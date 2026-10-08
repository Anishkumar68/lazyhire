from __future__ import annotations

import html
import logging
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlencode


from playwright.async_api import (
    BrowserContext,
    Page,
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)

from src.execution.base_scraper import BaseJobScraper
from src.schemas.profile import JobSearchConfig

logger = logging.getLogger("lazyhire.execution.linkedin")

LINKEDIN_BASE = "https://www.linkedin.com"
LINKEDIN_JOBS_SEARCH = "https://www.linkedin.com/jobs/search/"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)

# Selectors for job search results page matching LinkedIn DOM variations
SELECTORS = {
    "job_card": (
        '[componentkey^="job-card-component-ref-"], '
        "div.job-card-container, "
        "li.jobs-search-results__list-item, "
        "li.scaffold-layout__list-item, "
        "div.base-card, "
        "div.base-search-card, "
        "div.job-search-card"
    ),
    "job_title": (
        "a.job-card-list__title, "
        "a.job-card-list__title--link, "
        "a.job-card-container__link, "
        ".artdeco-entity-lockup__title a, "
        "h3.base-search-card__title, "
        ".jobs-search-card__title, "
        "h3"
    ),
    "job_company": (
        "span.job-card-container__primary-description, "
        "span.job-card-container__company-name, "
        "div.artdeco-entity-lockup__subtitle, "
        "div.artdeco-entity-lockup__subtitle span, "
        "a.job-card-container__company-name, "
        "h4.base-search-card__subtitle, "
        "h4"
    ),
    "job_location": (
        "li.job-card-container__metadata-item, "
        "span.job-card-container__metadata-wrapper, "
        "ul.job-card-container__metadata-wrapper li, "
        ".artdeco-entity-lockup__caption, "
        ".artdeco-entity-lockup__caption li, "
        "span.job-search-card__location, "
        ".jobs-search-card__location"
    ),
    "easy_apply": (
        ".job-card-container__apply-method, "
        ".job-search-card__easy-apply-label, "
        "[aria-label*='Easy Apply']"
    ),
}

PUBLIC_JOB_CARD_RE = re.compile(
    r'<li>\s*<div[^>]*class="[^"]*base-card[^"]*base-search-card[^"]*job-search-card[^"]*"'
    r"(?P<attrs>[^>]*)>(?P<body>.*?)</div>\s*</li>",
    re.IGNORECASE | re.DOTALL,
)
PUBLIC_JOB_ID_RE = re.compile(r'data-entity-urn="urn:li:jobPosting:(\d+)"', re.IGNORECASE)
PUBLIC_JOB_LINK_RE = re.compile(
    r'href="(?P<value>https://www\.linkedin\.com/jobs/view/[^"]+)"',
    re.IGNORECASE,
)
PUBLIC_JOB_TITLE_RE = re.compile(
    r'<h3[^>]*class="[^"]*base-search-card__title[^"]*"[^>]*>(?P<value>.*?)</h3>',
    re.IGNORECASE | re.DOTALL,
)
PUBLIC_JOB_COMPANY_RE = re.compile(
    r'<h4[^>]*class="[^"]*base-search-card__subtitle[^"]*"[^>]*>(?P<value>.*?)</h4>',
    re.IGNORECASE | re.DOTALL,
)
PUBLIC_JOB_LOCATION_RE = re.compile(
    r'<span[^>]*class="[^"]*job-search-card__location[^"]*"[^>]*>(?P<value>.*?)</span>',
    re.IGNORECASE | re.DOTALL,
)


def _extract_job_id_from_url(href: str | None) -> str | None:
    """Extract LinkedIn job ID from a job URL.

    Examples:
        /jobs/view/1234567890/ -> "1234567890"
        /jobs/view/1234567890?refId=... -> "1234567890"
        software-engineer-1234567890 -> "1234567890"
    """
    if not href:
        return None
    match = re.search(r"/jobs/view/(?:[^/?]+-)?(\d+)", href)
    if match:
        return match.group(1)

    match = re.search(r"-(\d+)(?:\?|/|$)", href)
    if match:
        return match.group(1)

    match = re.search(r"currentJobId=(\d+)", href)
    if match:
        return match.group(1)

    match = re.search(r"jobPosting:(\d+)", href)
    if match:
        return match.group(1)

    return None


def _canonical_linkedin_job_url(source_id: str | None, href: str | None) -> str:
    """Return canonical job URL using source_id or normalized href."""
    source_id = (source_id or "").strip()
    raw_href = (href or "").strip()

    if source_id:
        return f"{LINKEDIN_BASE}/jobs/view/{source_id}/"

    if not raw_href:
        return ""

    if raw_href.startswith("http"):
        return raw_href.split("?")[0]
    if raw_href.startswith("/"):
        return f"{LINKEDIN_BASE}{raw_href.split('?')[0]}"
    return raw_href.split("?")[0]


def _clean_html_text(value: str | None) -> str:
    """Strip HTML tags, decode entities, and normalize whitespace."""
    if not value:
        return ""
    text = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _normalize_linkedin_title_text(value: str | None) -> str:
    """Clean job title string by stripping verification badges and repeated phrases."""
    cleaned = _clean_html_text(value)
    cleaned = re.sub(r"\s+with verification(?:\s+at\s+.+)?$", "", cleaned, flags=re.IGNORECASE)
    parts = cleaned.split()
    if len(parts) >= 6 and len(parts) % 2 == 0:
        midpoint = len(parts) // 2
        if parts[:midpoint] == parts[midpoint:]:
            cleaned = " ".join(parts[:midpoint])
    return cleaned.strip(" -")


def _dedupe_jobs(jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate job dictionaries by external_id / link."""
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()

    for job in jobs:
        key = job.get("external_id") or job.get("link") or job.get("url")
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(job)

    return unique


class LinkedInScraper(BaseJobScraper):

    BASE_URL = "https://www.linkedin.com/jobs/search-results/"

    def __init__(self, user_data_dir: str = "./playwright/linkedin", headless: bool = False):
        self.user_data_dir = Path(user_data_dir)
        self.headless = headless
        self._playwright = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    async def __aenter__(self) -> LinkedInScraper:
        await self._start_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self._close_browser()

    async def _start_browser(self) -> Page:
        if self._page and not self._page.is_closed():
            return self._page

        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        if not self._playwright:
            self._playwright = await async_playwright().start()

        if not self._context:
            self._context = await self._playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.user_data_dir),
                headless=self.headless,
                viewport={"width": 1280, "height": 900},
                user_agent=DEFAULT_USER_AGENT,
                args=["--disable-blink-features=AutomationControlled"],
            )

        self._page = (
            self._context.pages[0]
            if self._context.pages
            else await self._context.new_page()
        )
        return self._page

    async def _close_browser(self):
        if self._context:
            try:
                await self._context.close()
            except Exception:
                pass
            self._context = None
            self._page = None

        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception:
                pass
            self._playwright = None

    async def is_authenticated(self) -> bool:
        """Check if browser profile has active LinkedIn login session."""
        if not self._context:
            return False
        try:
            cookies = await self._context.cookies([LINKEDIN_BASE])
            return any(c.get("name") == "li_at" and c.get("value") for c in cookies)
        except Exception:
            return False

    async def search_jobs(
        self,
        config: JobSearchConfig,
        max_pages: int = 5,
    ) -> list[dict[str, Any]]:
        page = await self._start_browser()
        all_jobs: list[dict[str, Any]] = []

        try:
            for page_num in range(max_pages):
                url = await self._build_search_url(config, page_index=page_num)
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2000)

                # Scroll to load dynamically rendered job cards
                await self._scroll_results(page)

                page_jobs = await self._extract_job_cards(page)
                if not page_jobs:
                    try:
                        html_text = await page.content()
                        page_jobs = self._extract_html_job_cards(html_text)
                    except Exception:
                        pass

                if not page_jobs:
                    try:
                        page_jobs = await self._extract_jobs_from_links(page)
                    except Exception:
                        pass

                prev_len = len(all_jobs)
                all_jobs = _dedupe_jobs([*all_jobs, *page_jobs])
                new_count = len(all_jobs) - prev_len

                if new_count == 0 and page_num > 0:
                    break

            return all_jobs
        finally:
            if not self._context:
                await self._close_browser()

    async def _build_search_url(
        self,
        config: JobSearchConfig,
        page_index: int = 0,
    ) -> str:
        keywords = "+".join(config.keywords) if isinstance(config.keywords, list) else str(config.keywords)
        location = config.location.replace(" ", "+")
        easy_apply = "true" if config.easy_apply else "false"
        url = f"{self.BASE_URL}?keywords={keywords}&location={location}&f_EA={easy_apply}&distance=49.709817725496514"
        if page_index > 0:
            url += f"&start={page_index * 25}"
        return url

    # https://www.linkedin.com/jobs/search-results/?keywords=python%2Csoftware+engineer%2C+fastapi%2CAI+application%2C+jaipur%2C+gurugram&origin=JOBS_HOME_KEYWORD_HISTORY&geoId=106442238&distance=49.709817725496514

    async def _scroll_results(self, page: Page) -> None:
        try:
            container = page.locator(
                "div.jobs-search-results-list, div.scaffold-layout__list > div, section.jobs-search-results-list"
            ).first
            if await container.count() > 0:
                for _ in range(5):
                    await container.evaluate("el => el.scrollBy(0, 500)")
                    await page.wait_for_timeout(500)
            else:
                for _ in range(3):
                    await page.evaluate("window.scrollBy(0, 500)")
                    await page.wait_for_timeout(500)
        except Exception:
            pass

    async def _extract_job_cards(self, page: Page) -> list[dict[str, Any]]:
        """Extract job cards dynamically using multiple fallback strategies."""
        job_cards = await page.locator(SELECTORS["job_card"]).all()
        jobs: list[dict[str, Any]] = []

        for card in job_cards:
            try:
                job = await self._extract_job_details(card)
                if job and (job.get("title") or job.get("link")):
                    jobs.append(job)
            except Exception:
                continue

        return _dedupe_jobs(jobs)

    async def _extract_job_details(self, card) -> dict[str, Any]:
        """Extract job details from a single job card with full fallbacks and normalization."""
        try:
            title = ""
            company = ""
            location = ""
            raw_href = ""

            # 1. Parse structured <p> elements if present in modern LinkedIn DOM
            paragraphs = await card.locator("p").all_inner_texts()
            cleaned_paragraphs = [
                re.sub(r"\s+", " ", text).strip()
                for text in paragraphs
                if text.strip()
            ]

            for text in cleaned_paragraphs:
                if text.startswith("Selected, "):
                    title = text.removeprefix("Selected, ").strip()
                    break

            if title:
                title_idx = cleaned_paragraphs.index(f"Selected, {title}") if f"Selected, {title}" in cleaned_paragraphs else -1
                if title_idx >= 0:
                    remaining = cleaned_paragraphs[title_idx + 1:]
                    for value in remaining:
                        if value in {"Viewed", "Promoted"}:
                            continue
                        if not company:
                            company = value
                        elif not location:
                            location = value
                            break

            # 2. Extract link / href
            link_el = card.locator("a[href*='/jobs/view/']").first
            if await link_el.count() > 0:
                raw_href = await link_el.get_attribute("href") or ""

            # 3. Fallback for title, company, location, link using standard selectors
            if not title:
                title_el = await card.query_selector(SELECTORS["job_title"])
                if title_el:
                    title = _normalize_linkedin_title_text(await title_el.inner_text())

            if not company:
                company_el = await card.query_selector(SELECTORS["job_company"])
                if company_el:
                    company = _clean_html_text(await company_el.inner_text()) or "Unknown"

            if not location:
                location_el = await card.query_selector(SELECTORS["job_location"])
                if location_el:
                    location = _clean_html_text(await location_el.inner_text()) or None

            if not raw_href:
                link_el = await card.query_selector(SELECTORS["job_title"]) or await card.query_selector("a")
                if link_el:
                    raw_href = await link_el.get_attribute("href") or ""

            source_id = _extract_job_id_from_url(raw_href)
            link = _canonical_linkedin_job_url(source_id, raw_href)
            external_id = source_id or link

            easy_apply_loc = card.locator(SELECTORS["easy_apply"]).first
            is_easy_apply = await easy_apply_loc.count() > 0

            return {
                "external_id": external_id,
                "platform": "linkedin",
                "title": title,
                "company": company or "Unknown",
                "location": location,
                "url": link,
                "link": link,
                "description": "",
                "is_easy_apply": is_easy_apply,
                "raw_data": {
                    "linkedin_href": raw_href,
                    "detail_url": link,
                    "manual_apply_url": link,
                    "source_id": source_id,
                },
            }

        except Exception:
            return {
                "external_id": "",
                "platform": "linkedin",
                "title": "",
                "company": "Unknown",
                "location": None,
                "url": "",
                "link": "",
                "description": "",
                "is_easy_apply": False,
                "raw_data": {},
            }

    def _extract_html_job_cards(self, html_text: str) -> list[dict[str, Any]]:
        """Dynamic HTML regex fallback for guest / public search results."""
        jobs: list[dict[str, Any]] = []

        for match in PUBLIC_JOB_CARD_RE.finditer(html_text):
            attrs = match.group("attrs")
            body = match.group("body")

            source_id_match = PUBLIC_JOB_ID_RE.search(attrs)
            href_match = PUBLIC_JOB_LINK_RE.search(body)
            title_match = PUBLIC_JOB_TITLE_RE.search(body)
            company_match = PUBLIC_JOB_COMPANY_RE.search(body)
            location_match = PUBLIC_JOB_LOCATION_RE.search(body)

            href = html.unescape(href_match.group("value")) if href_match else ""
            source_id = (
                source_id_match.group(1)
                if source_id_match
                else _extract_job_id_from_url(href)
            )
            title = (
                _normalize_linkedin_title_text(title_match.group("value"))
                if title_match
                else ""
            )
            company = (
                _clean_html_text(company_match.group("value"))
                if company_match
                else "Unknown"
            )
            location = (
                _clean_html_text(location_match.group("value"))
                if location_match
                else None
            )

            if not title and not href:
                continue

            link = _canonical_linkedin_job_url(source_id, href)
            external_id = source_id or link

            jobs.append({
                "external_id": external_id,
                "platform": "linkedin",
                "title": title,
                "company": company,
                "location": location,
                "url": link,
                "link": link,
                "description": "",
                "is_easy_apply": False,
                "raw_data": {
                    "linkedin_href": href,
                    "detail_url": link,
                    "manual_apply_url": link,
                    "source_id": source_id,
                    "search_mode": "public_guest",
                },
            })

        return _dedupe_jobs(jobs)

    async def _extract_jobs_from_links(self, page: Page) -> list[dict[str, Any]]:
        """Fallback to extract jobs directly from all job view link anchors on the page."""
        links = await page.locator("a[href*='/jobs/view/']").all()
        jobs: list[dict[str, Any]] = []

        for link_loc in links:
            try:
                href = await link_loc.get_attribute("href")
                if not href:
                    continue
                source_id = _extract_job_id_from_url(href)
                link = _canonical_linkedin_job_url(source_id, href)
                external_id = source_id or link

                raw_title = await link_loc.inner_text()
                title = _normalize_linkedin_title_text(raw_title)

                jobs.append({
                    "external_id": external_id,
                    "platform": "linkedin",
                    "title": title,
                    "company": "Unknown",
                    "location": None,
                    "url": link,
                    "link": link,
                    "description": "",
                    "is_easy_apply": False,
                    "raw_data": {
                        "linkedin_href": href,
                        "detail_url": link,
                        "source_id": source_id,
                    },
                })
            except Exception:
                continue

        return _dedupe_jobs(jobs)