"""
Application planner agent.

The planner consumes the evaluator's `Decision` and produces a
high‑level application plan specifying whether to apply, which résumé
modules to emphasise, whether a cover letter is required, and the
degree of automation for submission.  The goal is to centralise
application logic separate from the evaluator and submission layers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any

from .job_normalizer import Job
from .job_evaluator import Decision


@dataclass
class ApplicationPlan:
    """Plan describing how to apply to a job."""

    apply: bool
    resume_strategy: Dict[str, Any] = field(default_factory=dict)
    cover_letter: Dict[str, Any] = field(default_factory=dict)
    automation_level: str = "manual"


class ApplicationPlanner:
    """Decide whether and how to apply to a job based on the evaluator's decision."""

    def __init__(self, threshold: float = 0.5) -> None:
        self.threshold = threshold

    def plan(self, job: Job, decision: Decision, resume_inventory: Dict[str, Any]) -> ApplicationPlan:
        """Generate an application plan.

        Args:
            job: The structured job description.
            decision: The evaluator's structured decision.
            resume_inventory: Dictionary with `core_resume` (string) and
                `modules` (list of module names) entries.

        Returns:
            ApplicationPlan: The plan including whether to apply and any
                modifications required.
        """

        plan = ApplicationPlan(apply=False)

        if not decision.pass_hard_filter:
            return plan

        if decision.recommendation != "apply":
            return plan

        # Basic threshold: require match_score >= configured threshold
        if decision.match_score < self.threshold:
            return plan

        # Decide which résumé modules to highlight – select modules that
        # correspond to at least one strength keyword.  In this demo the
        # module names are arbitrary and can be mapped to keywords outside
        # this method.
        modules_to_highlight: List[str] = []
        available_modules: List[str] = resume_inventory.get("modules", [])
        for mod in available_modules:
            # If the module name appears in the job keywords or strengths, pick it
            if mod.lower() in (kw.lower() for kw in job.keywords + decision.strengths):
                modules_to_highlight.append(mod)

        plan.apply = True
        plan.resume_strategy = {
            "use_core": True,
            "highlight_modules": modules_to_highlight,
        }
        plan.cover_letter = {
            "required": True,
            "style": "formal",
        }
        plan.automation_level = "manual"  # always manual in this demo

        return plan