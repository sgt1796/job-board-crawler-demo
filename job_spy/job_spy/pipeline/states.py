"""
State definitions for the job processing FSM.

Each job in the pipeline progresses through these states.  The state
machine ensures that every job follows the same path and avoids repeated
actions when a script is restarted.
"""
from __future__ import annotations

from enum import Enum


class JobState(str, Enum):
    """Enumeration of processing states for a job."""

    FETCHED = "FETCHED"
    NORMALIZED = "NORMALIZED"
    EVALUATED = "EVALUATED"
    SKIPPED = "SKIPPED"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    PLANNED = "PLANNED"
    MATERIAL_READY = "MATERIAL_READY"
    SUBMITTED = "SUBMITTED"