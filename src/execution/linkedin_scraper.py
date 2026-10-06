import html
import re
from pathlib import Path
from typing import Any

from playwright.async_api import BrowserContext, Page, async_playwright

from src.execution.base_scraper import BaseJobScraper
from src.schemas.profile import JobSearchConfig


class LinkedInScraper(BaseJobScraper):

    BASE_URL = "https://www.linkedin.com/jobs/search-results/"

    def __init__(self, user_data_dir : str ="./playwright/linkedin"):
        self.user_data_dir = Path(user_data_dir)
        self._playwright =None
        self._context : BrowserContext | None = None
        self._page : Page | None =None

    async def _start_browser(self)-> Page:

        self.user_data_dir.mkdir(parents=True,  exist_ok=True)

        self._playwright = await async_playwright().start()

        self._context = await self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=False,
        )

        self._page = self._context.pages[0] if self._context.pages else await self._context.new_page()

        return self._page

    async def _close_browser(self):
        if self._context:
            await self._context.close()
        if self._playwright:
            await self._playwright.stop()

    async def search_jobs(
        self,
        config: JobSearchConfig,
    ) -> list[dict[str, Any]]:
        page = await self._start_browser()
        try:
            # Implement the job search logic here using the provided config
            url = await self._build_search_url(config)
            # For example, navigate to LinkedIn, perform the search, and scrape results
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)

            # Scroll to load dynamically rendered job cards
            await page.evaluate("window.scrollBy(0, 500)")
            await page.wait_for_timeout(1000)

            return await self._extract_job_cards(page)
        finally:
            await self._close_browser()

    async def _build_search_url(self, config: JobSearchConfig) -> str:
        # Construct the LinkedIn job search URL based on the provided config
        keywords = "+".join(config.keywords)
        location = config.location.replace(" ", "+")
        easy_apply = "true" if config.easy_apply else "false"
        return f"{self.BASE_URL}?keywords={keywords}&location={location}&f_EA={easy_apply}&distance=49.709817725496514"
    
    # https://www.linkedin.com/jobs/search-results/?keywords=python%2Csoftware+engineer%2C+fastapi%2CAI+application%2C+jaipur%2C+gurugram&origin=JOBS_HOME_KEYWORD_HISTORY&geoId=106442238&distance=49.709817725496514

    async def _extract_job_cards(self, page: Page) -> list[dict[str, Any]]:
        """Extract job cards dynamically using multiple fallback strategies (DOM locators, HTML regex, Link parsing)."""
        # 1. Try DOM selector extraction first
        job_cards = await page.locator(
            '[componentkey^="job-card-component-ref-"], '
            "div.job-card-container, "
            "li.jobs-search-results__list-item, "
            "li.scaffold-layout__list-item, "
            "div.base-card, "
            "div.base-search-card, "
            "div.job-search-card"
        ).all()
        
        jobs: list[dict[str, Any]] = []
        seen_links: set[str] = set()

        for card in job_cards:
            try:
                job = await self._extract_job_details(card)
                if job and (job.get("title") or job.get("link")):
                    link = job.get("link", "")
                    if link and link in seen_links:
                        continue
                    if link:
                        seen_links.add(link)
                    jobs.append(job)
            except Exception:
                continue

        # 2. Fallback: Parse HTML content dynamically using Regex if DOM selectors return empty
        if not jobs:
            try:
                html_text = await page.content()
                jobs = self._extract_html_job_cards(html_text)
            except Exception:
                pass

        # 3. Fallback: Extract from all job view links on page
        if not jobs:
            try:
                jobs = await self._extract_jobs_from_links(page)
            except Exception:
                pass

        return jobs

    async def _extract_job_details(self, card) -> dict[str, Any]:
        """Extract job details from a LinkedIn job card."""
        try:
            title = ""
            company = ""
            location = ""
            link = ""

            # Current LinkedIn card structure
            paragraphs = await card.locator("p").all_inner_texts()

            cleaned = [
                re.sub(r"\s+", " ", text).strip()
                for text in paragraphs
                if text.strip()
            ]

            for text in cleaned:
                if text.startswith("Selected, "):
                    title = text.removeprefix("Selected, ").strip()
                    break

            # Current card has company and location as subsequent <p> elements.
            if title:
                title_index = cleaned.index(
                    f"Selected, {title}"
                ) if f"Selected, {title}" in cleaned else -1

                if title_index >= 0:
                    remaining = cleaned[title_index + 1:]

                    for value in remaining:
                        if value == "Viewed":
                            continue

                        if not company:
                            company = value
                        elif not location:
                            location = value
                            break

            # Prefer a real LinkedIn job-view URL if present.
            link_el = card.locator("a[href*='/jobs/view/']").first

            if await link_el.count():
                link = await link_el.get_attribute("href") or ""

            # Existing/legacy fallback selectors
            if not title:
                title_el = await card.query_selector(
                    "a.job-card-list__title, "
                    "a.job-card-list__title--link, "
                    "a.job-card-container__link, "
                    ".artdeco-entity-lockup__title a, "
                    "h3.base-search-card__title, "
                    ".jobs-search-card__title, "
                    "h3"
                )
                if title_el:
                    title = re.sub(
                        r"\s+",
                        " ",
                        await title_el.inner_text(),
                    ).strip()

            if not company:
                company_el = await card.query_selector(
                    "span.job-card-container__primary-description, "
                    "span.job-card-container__company-name, "
                    "div.artdeco-entity-lockup__subtitle, "
                    "div.artdeco-entity-lockup__subtitle span, "
                    "a.job-card-container__company-name, "
                    "h4.base-search-card__subtitle, "
                    "h4"
                )
                if company_el:
                    company = re.sub(
                        r"\s+",
                        " ",
                        await company_el.inner_text(),
                    ).strip()

            if not location:
                location_el = await card.query_selector(
                    "li.job-card-container__metadata-item, "
                    "span.job-card-container__metadata-wrapper, "
                    "ul.job-card-container__metadata-wrapper li, "
                    ".artdeco-entity-lockup__caption, "
                    ".artdeco-entity-lockup__caption li, "
                    "span.job-search-card__location, "
                    ".jobs-search-card__location"
                )
                if location_el:
                    location = re.sub(
                        r"\s+",
                        " ",
                        await location_el.inner_text(),
                    ).strip()

            # Final URL fallback.
            if not link:
                link_el = await card.query_selector(
                    "a.job-card-list__title, "
                    "a.job-card-list__title--link, "
                    "a.job-card-container__link, "
                    ".artdeco-entity-lockup__title a, "
                    "a.base-card__full-link, "
                    "a[href*='/jobs/view/'], "
                    "a"
                )
                if link_el:
                    link = await link_el.get_attribute("href") or ""

            if link.startswith("/"):
                link = f"https://www.linkedin.com{link}"

            link = link.split("?")[0]

            return {
                "title": title,
                "company": company,
                "location": location,
                "link": link,
            }

        except Exception:
            return {
                "title": "",
                "company": "",
                "location": "",
                "link": "",
            }

 
    def _extract_html_job_cards(self, html_text: str) -> list[dict[str, Any]]:
        """Dynamic HTML regex fallback for guest / public search results."""
        card_re = re.compile(
            r'<li[^>]*>\s*<div[^>]*class="[^"]*base-search-card[^"]*"[^>]*>(?P<body>.*?)</div>\s*</li>',
            re.IGNORECASE | re.DOTALL,
        )
        link_re = re.compile(
            r'href="(?P<value>https://www\.linkedin\.com/jobs/view/[^"?]+)',
            re.IGNORECASE,
        )
        title_re = re.compile(
            r'<h3[^>]*class="[^"]*base-search-card__title[^"]*"[^>]*>(?P<value>.*?)</h3>',
            re.IGNORECASE | re.DOTALL,
        )
        company_re = re.compile(
            r'<h4[^>]*class="[^"]*base-search-card__subtitle[^"]*"[^>]*>(?P<value>.*?)</h4>',
            re.IGNORECASE | re.DOTALL,
        )
        location_re = re.compile(
            r'<span[^>]*class="[^"]*job-search-card__location[^"]*"[^>]*>(?P<value>.*?)</span>',
            re.IGNORECASE | re.DOTALL,
        )

        jobs: list[dict[str, Any]] = []
        seen: set[str] = set()

        for match in card_re.finditer(html_text):
            body = match.group("body")
            link_m = link_re.search(body)
            title_m = title_re.search(body)
            company_m = company_re.search(body)
            location_m = location_re.search(body)

            link = link_m.group("value") if link_m else ""
            if not link or link in seen:
                continue
            seen.add(link)

            def clean(val: str) -> str:
                return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html.unescape(val))).strip()

            title = clean(title_m.group("value")) if title_m else ""
            company = clean(company_m.group("value")) if company_m else ""
            location = clean(location_m.group("value")) if location_m else ""

            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "link": link,
            })

        return jobs

    async def _extract_jobs_from_links(self, page: Page) -> list[dict[str, Any]]:
        """Fallback to extract jobs directly from all job view link anchors on the page."""
        links = await page.locator("a[href*='/jobs/view/']").all()
        jobs: list[dict[str, Any]] = []
        seen: set[str] = set()

        for link_loc in links:
            try:
                href = await link_loc.get_attribute("href")
                if not href:
                    continue
                clean_href = href.split("?")[0]
                if clean_href.startswith("/"):
                    clean_href = f"https://www.linkedin.com{clean_href}"

                if clean_href in seen:
                    continue
                seen.add(clean_href)

                raw_title = await link_loc.inner_text()
                title = re.sub(r"\s+", " ", raw_title).strip()

                jobs.append({
                    "title": title,
                    "company": "",
                    "location": "",
                    "link": clean_href,
                })
            except Exception:
                continue

        return jobs