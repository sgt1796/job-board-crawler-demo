"""
Pipeline subpackage.

This package holds the finite state machine and related helpers.  The FSM is
responsible for orchestrating the job processing workflow.
"""

from .fsm import JobStateMachine
from .states import JobState

__all__ = ["JobStateMachine", "JobState"]