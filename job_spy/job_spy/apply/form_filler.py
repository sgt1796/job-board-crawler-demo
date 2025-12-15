"""
Form filling stub.

In a real implementation this function would automate the process of filling
out an online job application form using browser automation libraries such as
Playwright or Selenium.  Here we simply log the action and return a
successful status.
"""
from __future__ import annotations

from typing import Any, Dict

from ..agents.job_normalizer import Job
from ..agents.application_planner import ApplicationPlan


def fill_form(job: Job, plan: ApplicationPlan, resume_text: str, cover_letter_text: str) -> bool:
    """Pretend to fill out a job application form.

    Args:
        job: The job being applied to.
        plan: The application plan specifying submission details.
        resume_text: The final résumé text.
        cover_letter_text: The cover letter text.

    Returns:
        True if the form was (supposedly) filled successfully.
    """
    print(f"[form_filler] Filling application form for job {job.job_id} at {job.company}")
    print(f"[form_filler] Resume length: {len(resume_text)} characters, cover letter length: {len(cover_letter_text)} characters")
    # Always succeed in this demo
    return True