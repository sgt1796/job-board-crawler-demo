"""
Confirmation helper.

During semi‑automated submission the system may pause and ask the user for
confirmation before actually submitting the application.  This stub always
returns True in tests.
"""
from __future__ import annotations

from ..agents.job_normalizer import Job


def request_confirmation(job: Job) -> bool:
    """Prompt the user to confirm application submission.

    In a real system this would send a notification or wait for a manual
    approval.  In this demonstration it always confirms automatically.
    """
    print(f"[confirm] Automatically confirming application for job {job.job_id}")
    return True