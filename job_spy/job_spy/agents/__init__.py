"""
Agent subpackage exposing the high level agent classes used by the job spy pipeline.

Modules:
    job_normalizer: Converts raw job postings into structured Job objects.
    job_evaluator: Evaluates the fit between a job and a candidate profile.
    application_planner: Decides whether and how to apply to a job.
    resume_modifier: Lightly modifies the résumé to emphasise relevant skills.
    cover_letter_writer: Generates simple cover letters.

Each agent has a single responsibility and is designed to be easy to unit test.  For
example, the evaluator class uses the `Embedder` from the POP library to
demonstrate integration points with semantic embedding services without making
external calls during tests.
"""

from .job_normalizer import JobNormalizer, Job
from .job_evaluator import JobEvaluator, CandidateProfile, Decision
from .application_planner import ApplicationPlanner, ApplicationPlan
from .resume_modifier import ResumeModifier
from .cover_letter_writer import CoverLetterWriter

__all__ = [
    "JobNormalizer",
    "Job",
    "JobEvaluator",
    "CandidateProfile",
    "Decision",
    "ApplicationPlanner",
    "ApplicationPlan",
    "ResumeModifier",
    "CoverLetterWriter",
]