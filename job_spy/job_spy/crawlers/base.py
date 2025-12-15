"""
Base class for job crawlers.

Crawlers are responsible for retrieving job postings from external sources
and returning them in a raw dictionary format.  The core pipeline expects
the keys `title`, `company`, `location`, `employment_type`, `description`
and `source_url`.  Additional keys are passed through but ignored by the
normaliser.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseCrawler(ABC):
    """Abstract base class for all crawlers."""

    @abstractmethod
    def fetch(self) -> List[Dict[str, Any]]:
        """Fetch new job postings.

        Returns:
            List of raw job dictionaries.  Each dictionary must contain at
            least `title`, `company`, `location`, `description` and
            `source_url` keys.
        """
        raise NotImplementedError