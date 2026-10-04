from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseExecutionRunner(ABC):
    """Abstract Base Class for Browser Automation Form Fillers"""

    @abstractmethod
    async def apply_job(self, job_url: str, candidate_data: Dict[str, Any], resume_path: str) -> Dict[str, Any]:
        """Automate applying to a job posting."""
        pass
