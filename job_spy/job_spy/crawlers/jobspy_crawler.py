"""
JobSpy-backed crawler.

This crawler wraps the `jobspy` package to fetch live job postings from
multiple job boards and map them into the simple dictionary format expected
by the rest of the pipeline.  The dependency is optional so that tests and
offline environments keep working with the bundled dummy crawler.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from .base import BaseCrawler


class JobSpyCrawler(BaseCrawler):
    """
    Fetch jobs using the `jobspy` library.

    Args:
        search_term: Query string passed to jobspy.
        location: Location filter string.
        platforms: List of job boards to query (e.g. ["indeed", "linkedin"]).
        hours_old: Maximum age of listings in hours.
        results_wanted: Maximum number of rows to request.
        country_indeed: Country code for Indeed results.
        proxies: Optional list of proxy strings supported by jobspy.
        scrape_kwargs: Extra keyword arguments forwarded to `scrape_jobs`.
    """

    def __init__(
        self,
        search_term: str,
        location: str,
        platforms: Optional[List[str]] = None,
        hours_old: int = 72,
        results_wanted: int = 50,
        country_indeed: str = "USA",
        proxies: Optional[List[str]] = None,
        scrape_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.search_term = search_term
        self.location = location
        self.platforms = platforms or ["indeed", "linkedin"]
        self.hours_old = hours_old
        self.results_wanted = results_wanted
        self.country_indeed = country_indeed
        self.proxies = proxies
        self.scrape_kwargs = scrape_kwargs or {}

    @staticmethod
    def _import_scraper():
        """Lazy import jobspy so environments without it still work."""
        try:
            from jobspy import scrape_jobs
        except Exception as exc:  # pragma: no cover - exercised only when missing
            raise ImportError(
                "JobSpyCrawler requires the `jobspy` package. "
                "Install it with `pip install python-jobspy` before use."
            ) from exc
        return scrape_jobs

    @staticmethod
    def _clean_value(value: Any, default: str = "") -> str:
        """Return a trimmed string unless the value is missing or NaN."""
        if value is None:
            return default
        if isinstance(value, float) and math.isnan(value):
            return default
        text = str(value).strip()
        return text or default

    def _map_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a jobspy record into the raw job dict expected by the FSM."""
        title = self._clean_value(record.get("title") or record.get("job_title"))
        company = self._clean_value(record.get("company") or record.get("company_name"))
        location = self._clean_value(
            record.get("location")
            or record.get("formatted_location")
            or record.get("job_location"),
            default="Remote",
        )
        employment_type = self._clean_value(
            record.get("employment_type") or record.get("job_type") or record.get("type")
        )
        if not employment_type:
            employment_type = None

        description = self._clean_value(
            record.get("description")
            or record.get("job_description")
            or record.get("body")
            or record.get("snippet")
        )
        source_url = self._clean_value(
            record.get("job_url") or record.get("url") or record.get("source_url")
        )

        return {
            "title": title,
            "company": company,
            "location": location,
            "employment_type": employment_type,
            "description": description,
            "source_url": source_url,
            "source_site": self._clean_value(
                record.get("site_name") or record.get("source") or record.get("job_board")
            ),
            # Keep the original row in case downstream needs richer metadata.
            "raw_record": record,
        }

    def fetch(self) -> List[Dict[str, Any]]:
        scrape_jobs = self._import_scraper()
        kwargs: Dict[str, Any] = {
            "site_name": self.platforms,
            "search_term": self.search_term,
            "location": self.location,
            "hours_old": self.hours_old,
            "results_wanted": self.results_wanted,
            "country_indeed": self.country_indeed,
        }
        if self.proxies:
            kwargs["proxies"] = self.proxies
        kwargs.update(self.scrape_kwargs)

        df = scrape_jobs(**kwargs)
        try:
            df = df.fillna("")
        except Exception:
            # If fillna is unavailable for some reason, proceed with raw data.
            pass
        records = df.to_dict("records")
        return [self._map_record(rec) for rec in records]
