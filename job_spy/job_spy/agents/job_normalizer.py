"""
Job normalisation agent.

The normaliser converts a raw job dictionary (as produced by a crawler) into a
structured `Job` dataclass.  This step does not interpret or evaluate the job; it
simply enforces a common schema and derives a stable identifier.  If new
attributes are desired, extend the `Job` dataclass and update the `normalize`
method accordingly.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any


@dataclass
class Job:
    """Structured representation of a job posting.

    Attributes:
        job_id: Stable hash for de‑duplication (company + title + location).
        title: Job title.
        company: Hiring company name.
        location: Location string (may be "remote").
        employment_type: Full‑time, contract, etc., or None if not provided.
        seniority: Broad seniority level if extractable, otherwise "unknown".
        keywords: Extracted keyword list from the description.
        responsibilities: List of bullet points describing duties.
        requirements: List of bullet points describing requirements.
        source_url: Original listing URL.
    """

    job_id: str
    title: str
    company: str
    location: str
    employment_type: Optional[str]
    seniority: str
    keywords: List[str]
    responsibilities: List[str]
    requirements: List[str]
    source_url: str

    def asdict(self) -> Dict[str, Any]:
        """Return a serialisable dictionary representation of the job."""
        return asdict(self)


class JobNormalizer:
    """
    A lightweight agent that converts raw crawled job data into the `Job`
    dataclass.  It performs only basic parsing and is free of any LLM logic.
    """

    @staticmethod
    def _derive_job_id(title: str, company: str, location: str) -> str:
        """Compute a stable hash for deduplication.

        A SHA1 of the concatenated company, title and location is used.  If
        additional fields are important for uniqueness they can be added
        here.
        """
        identity = f"{company}|{title}|{location}".lower().encode("utf-8")
        return hashlib.sha1(identity).hexdigest()

    @staticmethod
    def _extract_keywords(description: str) -> List[str]:
        """
        Naively extract keywords from the description.

        The extractor splits on non‑word characters (anything other than
        letters, digits or underscores) and retains tokens that have at
        least **three** characters.  A lower length threshold allows
        domain‑specific acronyms (e.g. "rna") to be captured.  In a
        production system you should replace this with a more
        sophisticated keyword extractor or embedding based approach.
        """
        import re

        tokens = re.split(r"\W+", description.lower())
        # Keep words with at least three characters to include short acronyms like "rna".
        keywords = [t for t in tokens if len(t) >= 3]
        # Deduplicate while preserving order
        return list(dict.fromkeys(keywords))

    def normalize(self, raw_job: Dict[str, Any]) -> Job:
        """Normalise a raw job dictionary.

        Args:
            raw_job: Dictionary with keys like `title`, `company`, `location`,
                `employment_type`, `description` and `source_url`.

        Returns:
            `Job` dataclass instance with derived fields.
        """
        title = raw_job.get("title", "").strip()
        company = raw_job.get("company", "").strip()
        location = raw_job.get("location", "").strip()
        employment_type: Optional[str] = raw_job.get("employment_type")
        description = raw_job.get("description", "")

        job_id = self._derive_job_id(title, company, location)
        keywords = self._extract_keywords(description)

        # For simplicity, responsibilities and requirements are not parsed
        # separately in this demonstration.  They mirror the keywords list.
        responsibilities: List[str] = keywords
        requirements: List[str] = keywords

        # Attempt to infer seniority from the title
        seniority = "unknown"
        lower_title = title.lower()
        if any(kw in lower_title for kw in ["intern", "junior"]):
            seniority = "junior"
        elif any(kw in lower_title for kw in ["senior", "lead", "principal"]):
            seniority = "senior"
        elif any(kw in lower_title for kw in ["manager", "director"]):
            seniority = "mid"

        return Job(
            job_id=job_id,
            title=title,
            company=company,
            location=location or "remote",
            employment_type=employment_type,
            seniority=seniority,
            keywords=keywords,
            responsibilities=responsibilities,
            requirements=requirements,
            source_url=raw_job.get("source_url", "") or "",
        )