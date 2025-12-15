import os
import json
import sqlite3
import sys
import unittest
from pathlib import Path

# Ensure the repository parent is on sys.path so discovery runs without install
REPO_PARENT = Path(__file__).resolve().parents[2]
if str(REPO_PARENT) not in sys.path:
    sys.path.insert(0, str(REPO_PARENT))

from job_spy.agents import CandidateProfile
from job_spy.crawlers.dummy_crawler import DummyCrawler
from job_spy.pipeline.fsm import JobStateMachine
from job_spy.pipeline.states import JobState


class TestFSM(unittest.TestCase):
    def setUp(self) -> None:
        # Create a candidate profile
        self.profile = CandidateProfile(
            target_titles=["Bioinformatics Scientist"],
            must_have=["python", "rna-seq", "cloud"],
            nice_to_have=[],
            hard_filters={"location": ["Boston, MA", "Remote"]},
            soft_preferences={},
        )
        # Create a simple resume inventory
        self.inventory = {
            "core_resume": "Core resume text with python and RNA-seq.",
            "modules": ["research_highlight"],
            "modules_dict": {
                "research_highlight": "Highlight: single-cell RNA-seq project."
            },
        }
        # Determine schema path
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.schema_path = os.path.join(base_dir, 'data', 'schema.sql')

        # Use an in-memory SQLite DB for tests
        self.fsm = JobStateMachine(
            self.profile,
            self.inventory,
            db_path=':memory:',
            schema_path=self.schema_path,
        )

    def tearDown(self) -> None:
        self.fsm.close()

    def test_full_pipeline(self):
        # Create dummy crawler and add jobs
        crawler = DummyCrawler()
        jobs = crawler.fetch()
        self.fsm.add_jobs(jobs)
        # Run the FSM until completion
        self.fsm.run()

        # Query final state
        cur = self.fsm.conn.cursor()
        cur.execute("SELECT state FROM jobs")
        states = [row[0] for row in cur.fetchall()]
        # Expect one job submitted
        self.assertEqual(states, [JobState.SUBMITTED.value])

    def test_skip_state(self):
        # Use a job that fails location filter
        bad_job = {
            "title": "Bioinformatics Scientist",
            "company": "BadCo",
            "location": "Nowhere, ZZ",
            "employment_type": "Full-time",
            "description": "Python and RNA-seq required.",
            "source_url": "https://example.com/job/bad"
        }
        self.fsm.add_jobs([bad_job])
        self.fsm.run()
        # After run the job should be skipped
        cur = self.fsm.conn.cursor()
        cur.execute("SELECT state FROM jobs WHERE job_id = (SELECT job_id FROM jobs LIMIT 1)")
        state = cur.fetchone()[0]
        self.assertEqual(state, JobState.SKIPPED.value)


if __name__ == '__main__':
    unittest.main()
