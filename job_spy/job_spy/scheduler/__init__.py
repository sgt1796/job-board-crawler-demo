"""
Scheduler entry points.

This package contains small scripts that can be scheduled via cron or
APScheduler.  They simply invoke the crawler or pipeline runner and have
minimal logic of their own.  The runner in `pipeline/runner.py` performs
all heavy lifting.
"""

__all__ = []