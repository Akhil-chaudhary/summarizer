import re


class SummarizerService:
    def summarize(self, content: str, *, max_chars: int = 200) -> str:
        """Author: Akhil Chaudhary

        Generate a minimal summary for the given content (first sentence, truncated).
        """
        content = content.strip()
        if not content:
            return ""

        sentences = re.split(r"(?<=[.!?])\s+", content)
        summary = sentences[0] if sentences else content
        summary = summary.strip()

        if len(summary) > max_chars:
            summary = summary[: max_chars - 1].rstrip() + "…"

        return summary
