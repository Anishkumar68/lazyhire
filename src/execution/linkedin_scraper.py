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
            url = self._build_search_url(config)
            # For example, navigate to LinkedIn, perform the search, and scrape results
            await page.goto(url,wait_until="documentloaded")
            # Add your scraping logic here...
            return []  # Return a list of job postings as dictionaries
        finally:
            await self._close_browser()

    async def _build_search_url(self, config: JobSearchConfig) -> str:
        # Construct the LinkedIn job search URL based on the provided config
        keywords = "+".join(config.keywords)
        location = config.location.replace(" ", "+")
        easy_apply = "true" if config.easy_apply else "false"
        return f"{self.BASE_URL}?keywords={keywords}&location={location}&f_EA={easy_apply}&distance=49.709817725496514"
    
    # https://www.linkedin.com/jobs/search-results/?keywords=python%2Csoftware+engineer%2C+fastapi%2CAI+application%2C+jaipur%2C+gurugram&origin=JOBS_HOME_KEYWORD_HISTORY&geoId=106442238&distance=49.709817725496514