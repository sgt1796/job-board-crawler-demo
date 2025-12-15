"""
Job evaluation agent.

This module defines a small data structure representing the candidate's career
preferences and a class that scores jobs against these preferences.  The
implementation demonstrates how to integrate the `Embedder` class from the
POP library.  In this demonstration we instantiate the embedder but do not
invoke remote APIs to avoid network calls – tests patch the embedder to
return deterministic embeddings if needed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

try:
    # Attempt to import the Embedder from the POP package.  In this
    # environment the POP package may not be available on the Python path.
    from POP.Embedder import Embedder  # type: ignore
except ModuleNotFoundError:
    print("POP package not found; using stub Embedder.")
    # Provide a minimal fallback stub so that the evaluator can still be
    # instantiated in tests without network access or POP installation.
    class Embedder:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def get_embedding(self, texts: List[str]) -> list:
            return []
from .job_normalizer import Job


@dataclass
class CandidateProfile:
    """Representation of the job seeker's preferences and requirements."""

    target_titles: List[str] = field(default_factory=list)
    must_have: List[str] = field(default_factory=list)
    nice_to_have: List[str] = field(default_factory=list)
    hard_filters: Dict[str, Any] = field(default_factory=dict)
    soft_preferences: Dict[str, float] = field(default_factory=dict)


@dataclass
class Decision:
    """Structured decision returned by the evaluator."""

    match_score: float
    pass_hard_filter: bool
    strengths: List[str]
    gaps: List[str]
    risk_flags: List[str]
    recommendation: str  # one of "apply", "skip", "human_review"


class JobEvaluator:
    """
    Simple rule‑based evaluator that compares a job's keywords against a
    candidate's profile.  It demonstrates how the embedder could be
    incorporated; the embedder is instantiated but not called in the default
    implementation.
    """

    def __init__(self, profile: CandidateProfile, embedder: Optional[Embedder] = None):
        self.profile = profile
        # Instantiate embedder if not provided.  Use the default API (OpenAI) to
        # demonstrate integration.  In tests this can be patched to avoid
        # external calls.
        self.embedder = embedder or Embedder(use_api="openai")

    def evaluate(self, job: Job) -> Decision:
        """Compute a decision for a given job.

        The match score is a simple proportion of the candidate's `must_have`
        skills that appear in the job's keywords.  Hard filters check for
        location and other constraints specified in the candidate profile.  A
        real implementation might incorporate semantic similarity via the
        embedder; this method hints at where such logic could live.
        """

        must_have = [kw.lower() for kw in self.profile.must_have]
        job_keywords = [kw.lower() for kw in job.keywords]

        # Demonstrate the use of the embedder: obtain embeddings for the
        # candidate requirements and a subset of the job keywords.  In this
        # demonstration we ignore the returned vectors but making the call
        # shows how one would integrate semantic similarity.  When the
        # embedder is a stub it simply returns an empty list.
        try:
            _ = self.embedder.get_embedding(must_have + job_keywords[:3])
        except Exception:
            # If the embedder fails (e.g. due to missing API key), continue
            pass

        # Compute how many must-have keywords are present in the job.  Use
        # simple pattern matching but allow minor variations: a requirement
        # like "rna-seq" should match tokens like "rna" or "rnaseq" in the
        # description.  For each must-have term we generate a set of
        # candidate variations (original, without hyphens, and split on
        # hyphens) and consider it matched if any variation appears in the
        # job keywords.  This improves recall when the job description uses
        # different hyphenation.
        strengths: List[str] = []
        gaps: List[str] = []
        if not must_have:
            score = 1.0
        else:
            hits = 0
            for kw in must_have:
                variations = {kw}
                if '-' in kw:
                    variations.add(kw.replace('-', ''))
                    variations.update(kw.split('-'))
                # find if any variation appears in job keywords
                matched = False
                for v in variations:
                    if v and v in job_keywords:
                        matched = True
                        break
                if matched:
                    hits += 1
                    strengths.append(kw)
                else:
                    gaps.append(kw)
            score = hits / len(must_have)

        # Hard filters: location, visa, etc.
        passes = True
        hard_filters = self.profile.hard_filters or {}
        # Example: location filter can be a list of allowed locations
        allowed_locations = hard_filters.get("location")
        if allowed_locations:
            passes = job.location.lower() in [loc.lower() for loc in allowed_locations]

        # Risk flags – mark contract roles or missing keywords
        risk_flags: List[str] = []
        if job.employment_type and 'contract' in job.employment_type.lower():
            risk_flags.append('contract')
        if score < 0.5:
            risk_flags.append('low_match')

        # Determine recommendation
        recommendation: str
        if not passes or score == 0.0:
            recommendation = "skip"
        elif score >= 0.7:
            recommendation = "apply"
        elif 0.4 <= score < 0.7:
            recommendation = "human_review"
        else:
            recommendation = "skip"

        return Decision(
            match_score=round(score, 2),
            pass_hard_filter=passes,
            strengths=strengths,
            gaps=gaps,
            risk_flags=risk_flags,
            recommendation=recommendation,
        )