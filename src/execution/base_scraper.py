from abc import ABC, abstractmethod
from typing import Any

from src.schemas.profile import JobSearchConfig


class BaseJobScraper(ABC):
    """Abstract base class for job discovery scrapers."""

    @abstractmethod
    async def search_jobs(
        self,
        config: JobSearchConfig,
    ) -> list[dict[str, Any]]:
        """Search for jobs using the provided search configuration."""
        pass