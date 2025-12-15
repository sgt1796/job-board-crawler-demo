"""
Upload helpers.

These functions simulate uploading résumé and cover letter files to an ATS.
They simply print messages and return True.  Real implementations would
perform HTTP POSTs or interact with browser file inputs.
"""
from __future__ import annotations

from ..agents.job_normalizer import Job


def upload_resume(job: Job, resume_text: str) -> bool:
    """Simulate uploading a résumé file."""
    print(f"[upload] Uploading résumé for job {job.job_id}")
    return True


def upload_cover_letter(job: Job, cover_letter_text: str) -> bool:
    """Simulate uploading a cover letter file."""
    print(f"[upload] Uploading cover letter for job {job.job_id}")
    return True