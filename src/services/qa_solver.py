import re
from typing import Optional, Dict, Any


class QASolverService:
    """
    Hybrid Question Answering Engine:
    - Tier 1: Offline Regex / Heuristic rule lookup (from personals/questions config)
    - Tier 2: Exact/Fuzzy match in candidate's QABank memory
    - Tier 3: LLM Dynamic Prompt Solver
    """

    HEURISTIC_RULES = {
        r"years of experience": "5",
        r"work authorization|authorized to work": "Yes",
        r"require sponsorship|sponsorship": "No",
        r"desired salary|expected salary": "120000",
        r"notice period": "30",
    }

    @classmethod
    def solve_heuristic(cls, question_text: str) -> Optional[str]:
        cleaned_text = question_text.lower().strip()
        for pattern, answer in cls.HEURISTIC_RULES.items():
            if re.search(pattern, cleaned_text):
                return answer
        return None

    @classmethod
    async def solve_question(cls, question_text: str, context: Optional[Dict[str, Any]] = None) -> str:
        # Tier 1: Try heuristic regex lookup
        heuristic_answer = cls.solve_heuristic(question_text)
        if heuristic_answer is not None:
            return heuristic_answer

        # Tier 2 & Tier 3 fallbacks will connect to QA Bank and LLM providers
        return "Yes"
