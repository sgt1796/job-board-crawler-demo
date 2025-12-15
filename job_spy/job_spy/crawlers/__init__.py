"""
Crawler subpackage.

Each crawler implements a `fetch` method returning a list of raw job
postings.  Crawlers should inherit from `BaseCrawler` to provide a common
interface.  The dummy crawler supplies a static job for demonstration
p urposes.
"""

from .base import BaseCrawler
from .dummy_crawler import DummyCrawler

__all__ = ["BaseCrawler", "DummyCrawler"]

# JobSpyCrawler is optional to avoid forcing the jobspy dependency on tests.
try:  # pragma: no cover - availability depends on installed extras
    from .jobspy_crawler import JobSpyCrawler
except Exception:
    JobSpyCrawler = None  # type: ignore
else:
    __all__.append("JobSpyCrawler")
