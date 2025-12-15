"""
Résumé modifier agent.

In a real system this agent would reorder bullet points and emphasise relevant
skills without hallucinating new content.  For the purposes of this demo the
`modify` method simply inserts highlight modules at the top of the résumé and
uppercases matching keywords.
"""
from __future__ import annotations

from typing import List


class ResumeModifier:
    """Modify a résumé by emphasising modules and keywords."""

    def modify(self, core_resume: str, highlight_modules: List[str], job_keywords: List[str]) -> str:
        """
        Produce a modified résumé.

        Args:
            core_resume: The base résumé text.
            highlight_modules: Additional highlight paragraphs to insert at the top.
            job_keywords: Keywords from the job description used to emphasise.

        Returns:
            A new résumé string with the modules prepended and any job keywords
            appearing in the résumé uppercased.
        """
        # Insert highlight modules at the top separated by blank lines
        prefix = "\n\n".join(highlight_modules)

        # Emphasise keywords in the core résumé by uppercasing them
        modified_resume = core_resume
        for kw in job_keywords:
            if kw and kw.lower() in modified_resume.lower():
                # Replace case insensitively
                import re
                pattern = re.compile(re.escape(kw), re.IGNORECASE)
                modified_resume = pattern.sub(kw.upper(), modified_resume)

        if prefix:
            return prefix + "\n\n" + modified_resume
        return modified_resume