"""
Dummy crawler that yields a single hard‑coded job.

This crawler is useful for tests and demonstrations where external
connectivity is unavailable.  Feel free to replace this with a real crawler
that scrapes a job board or reads from an RSS feed.
"""
from __future__ import annotations

from typing import List, Dict, Any

from .base import BaseCrawler


class DummyCrawler(BaseCrawler):
    """Return one or more hard coded job postings."""

    def fetch(self) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Senior Bioinformatics Scientist",
                "company": "Acme Genomics",
                "location": "Boston, MA",
                "employment_type": "Full‑time",
                "description": (
                    "We are seeking a senior bioinformatics scientist with strong Python skills,"
                    " experience in RNA‑seq data analysis, and familiarity with cloud computing."
                ),
                "source_url": "https://example.com/jobs/123",
            }
        ]