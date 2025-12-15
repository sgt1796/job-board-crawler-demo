"""
Cover letter writer agent.

This simplified writer constructs a three‑paragraph cover letter based on the
job and candidate profile.  In a production system one could integrate
`PromptFunction` from the POP library to leverage an LLM for more natural
language generation.  The writer remains deterministic and easy to test.
"""
from __future__ import annotations

from typing import List

from .job_normalizer import Job

try:
    # Attempt to import PromptFunction from the POP package.  In this
    # environment the POP library may not be available.  If the import
    # fails a simple fallback stub is defined below.
    from POP.PromptFunction import PromptFunction  # type: ignore
except ModuleNotFoundError:
    class PromptFunction:  # type: ignore
        """Minimal stub for the POP PromptFunction.

        The real POP.PromptFunction enables LLM calls based on a system
        prompt and optional templates.  This stub simply formats a
        provided template string using keyword arguments.
        """

        def __init__(self, template: str) -> None:
            self.template = template

        def __call__(self, **kwargs: str) -> str:
            return self.template.format(**kwargs)


class CoverLetterWriter:
    """Generate a basic cover letter for a given job and candidate."""

    @staticmethod
    def write(job: Job, candidate_facts: List[str]) -> str:
        """Assemble a cover letter from static templates.

        Args:
            job: The structured job posting.
            candidate_facts: A list of short bullet points about the candidate
                relevant to the role.

        Returns:
            A three paragraph cover letter string.
        """
        paragraphs: List[str] = []

        # Build a comma‑separated facts string once
        facts_str = ", ".join(candidate_facts)

        # Define templates for each paragraph.  These templates use Python
        # format fields that will be substituted via the PromptFunction.
        template1 = (
            "Dear Hiring Committee,\n\n"
            "I am writing to express my strong interest in the {title} position at {company}. "
            "With a background in {facts} I am excited about the opportunity to contribute to your team.\n"
        )
        template2 = (
            "My experience aligns closely with the key requirements of this role. "
            "In particular, I have demonstrated proficiency in {facts} which directly match the qualifications you are seeking.\n"
        )
        template3 = (
            "I am particularly drawn to {company}'s mission and the impact it has in the industry. "
            "I believe my skills and values make me a great fit for your team. "
            "Thank you for considering my application.\n\nSincerely,\nCandidate"
        )

        # Instantiate prompt functions (or stubs) and generate paragraphs
        pf1 = PromptFunction(template1)
        pf2 = PromptFunction(template2)
        pf3 = PromptFunction(template3)

        paragraphs.append(pf1(title=job.title, company=job.company, facts=facts_str))
        paragraphs.append(pf2(facts=facts_str))
        paragraphs.append(pf3(company=job.company))

        return "\n".join(paragraphs)