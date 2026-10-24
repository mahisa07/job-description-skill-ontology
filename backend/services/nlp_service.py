import re
from typing import List, Dict

class NLPService:
    @staticmethod
    def segment_sentences(text: str) -> List[str]:
        """Split clean text into sentences."""
        # Simple robust sentence splitter supporting bullet points
        raw_sentences = re.split(r'(?<=[.!?])\s+|\n+|- |\* ', text)
        sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 3]
        return sentences

    @staticmethod
    def identify_sections(text: str) -> Dict[str, List[str]]:
        """Identify major sections in Job Description."""
        sections = {
            "summary": [],
            "requirements": [],
            "responsibilities": [],
            "preferred": [],
            "other": []
        }

        current_sec = "summary"
        lines = text.split('\n')

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            lower_line = line_str.lower()
            if any(k in lower_line for k in ["requirement", "qualification", "skills required", "what you need"]):
                current_sec = "requirements"
            elif any(k in lower_line for k in ["responsibility", "duties", "what you'll do", "role overview"]):
                current_sec = "responsibilities"
            elif any(k in lower_line for k in ["preferred", "nice to have", "good to have", "bonus"]):
                current_sec = "preferred"

            sections[current_sec].append(line_str)

        return sections
