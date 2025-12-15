"""
Screenshot helper.

In a production system you might capture the final state of the application
form as an image for audit purposes.  This stub simply prints a message.
"""
from __future__ import annotations

from ..agents.job_normalizer import Job


def take_screenshot(job: Job) -> str:
    """Simulate taking a screenshot and return a file path."""
    path = f"screenshots/{job.job_id}.png"
    print(f"[screenshot] Would save screenshot to {path}")
    return path