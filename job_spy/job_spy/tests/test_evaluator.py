import sys
import unittest
from pathlib import Path

# Ensure the repository parent is on sys.path so discovery runs without install
REPO_PARENT = Path(__file__).resolve().parents[2]
if str(REPO_PARENT) not in sys.path:
    sys.path.insert(0, str(REPO_PARENT))

from job_spy.agents import CandidateProfile, JobEvaluator, Job


class TestJobEvaluator(unittest.TestCase):
    def setUp(self) -> None:
        profile_data = {
            "target_titles": ["Bioinformatics Scientist"],
            "must_have": ["python", "rna-seq", "cloud"],
            "nice_to_have": [],
            "hard_filters": {"location": ["Boston, MA", "Remote"]},
            "soft_preferences": {},
        }
        self.profile = CandidateProfile(
            target_titles=profile_data["target_titles"],
            must_have=profile_data["must_have"],
            nice_to_have=profile_data["nice_to_have"],
            hard_filters=profile_data["hard_filters"],
            soft_preferences=profile_data["soft_preferences"],
        )
        self.evaluator = JobEvaluator(self.profile)

    def test_evaluator_matches_must_have(self):
        job = Job(
            job_id="1",
            title="Senior Bioinformatics Scientist",
            company="Acme",
            location="Boston, MA",
            employment_type="Full-time",
            seniority="senior",
            keywords=["python", "rna-seq", "cloud", "other"],
            responsibilities=[],
            requirements=[],
            source_url="",
        )
        decision = self.evaluator.evaluate(job)
        # All three must_have keywords appear
        self.assertEqual(decision.match_score, 1.0)
        self.assertTrue(decision.pass_hard_filter)
        self.assertEqual(set(decision.strengths), {"python", "rna-seq", "cloud"})
        self.assertEqual(decision.gaps, [])
        self.assertEqual(decision.recommendation, "apply")

    def test_evaluator_partial_match(self):
        job = Job(
            job_id="2",
            title="Bioinformatics Analyst",
            company="Beta",
            location="Boston, MA",
            employment_type="Contract",
            seniority="junior",
            keywords=["python"],
            responsibilities=[],
            requirements=[],
            source_url="",
        )
        decision = self.evaluator.evaluate(job)
        # Only one of three must_have keywords appears
        self.assertEqual(decision.match_score, round(1/3, 2))
        self.assertIn('low_match', decision.risk_flags)
        # Employment type is contract
        self.assertIn('contract', decision.risk_flags)
        # Recommendation should be skip (below 0.4)
        self.assertEqual(decision.recommendation, "skip")

    def test_evaluator_location_filter(self):
        job = Job(
            job_id="3",
            title="Bioinformatics Scientist",
            company="Gamma",
            location="New York, NY",
            employment_type="Full-time",
            seniority="mid",
            keywords=["python", "rna-seq", "cloud"],
            responsibilities=[],
            requirements=[],
            source_url="",
        )
        decision = self.evaluator.evaluate(job)
        # Location does not match allowed list
        self.assertFalse(decision.pass_hard_filter)
        self.assertEqual(decision.recommendation, "skip")


if __name__ == '__main__':
    unittest.main()
