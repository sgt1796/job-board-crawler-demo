"""
Finite state machine (FSM) for job processing.

This class manages the progression of each job through the pipeline states,
interacting with the agents and external helpers as necessary.  It uses a
SQLite database to persist state and decisions so that processing can resume
after interruptions.  The FSM is intentionally simple and synchronous to
facilitate comprehension and testing.
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import date, datetime
from typing import List, Dict, Optional, Any

from ..agents import (
    JobNormalizer,
    JobEvaluator,
    ApplicationPlanner,
    ResumeModifier,
    CoverLetterWriter,
    CandidateProfile,
    Job,
    Decision,
    ApplicationPlan,
)
from ..apply import fill_form, upload_resume, upload_cover_letter, take_screenshot, request_confirmation
from ..crawlers.base import BaseCrawler
from ..pipeline.states import JobState


class JobStateMachine:
    """
    A simple FSM that pulls jobs from the database and processes them step by
    step.  It relies on dependency injection for the profile and resume
    inventory so that tests can supply fixtures.
    """

    def __init__(
        self,
        profile: CandidateProfile,
        resume_inventory: Dict[str, Any],
        db_path: str = os.path.join(os.path.dirname(__file__), '..', 'data', 'jobs.db'),
        schema_path: str = os.path.join(os.path.dirname(__file__), '..', 'data', 'schema.sql'),
    ) -> None:
        self.profile = profile
        self.resume_inventory = resume_inventory
        # Use the provided database path as is for in‑memory databases.  When
        # `db_path` is exactly ':memory:' or begins with 'file:', SQLite
        # interprets it specially and the file system path should not be
        # normalised.  Otherwise construct an absolute path so that the
        # database resides in a predictable location.
        if db_path == ':memory:' or db_path.startswith('file:'):
            self.db_path = db_path
        else:
            self.db_path = os.path.abspath(db_path)
        self.schema_path = os.path.abspath(schema_path)

        # Ensure database directory exists unless using an in‑memory or URI path
        db_dir = os.path.dirname(self.db_path)
        # For special SQLite identifiers like ':memory:' the dirname is '' and we
        # should not attempt to create it.  Similarly, if `db_dir` is empty,
        # nothing needs to be created.  This avoids FileNotFoundError in tests.
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

        # Initialize agents
        self.normalizer = JobNormalizer()
        self.evaluator = JobEvaluator(profile)
        self.planner = ApplicationPlanner()
        self.resume_modifier = ResumeModifier()
        self.cover_letter_writer = CoverLetterWriter()

    @staticmethod
    def _json_default(value: Any) -> Any:
        """Convert common non‑serialisable types to JSON friendly values."""
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, set):
            return list(value)
        return str(value)

    def _json_dumps(self, payload: Any) -> str:
        return json.dumps(payload, default=self._json_default)

    def _init_db(self) -> None:
        """Create tables from the schema if they do not exist."""
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        self.conn.executescript(schema_sql)
        self.conn.commit()

    def close(self) -> None:
        """Close the underlying database connection."""
        self.conn.close()

    def add_jobs(self, raw_jobs: List[Dict[str, Any]]) -> None:
        """Insert new jobs into the database if they are not already present."""
        for raw in raw_jobs:
            # Derive job_id using normalizer helper
            tmp_job = self.normalizer.normalize(raw)
            cur = self.conn.cursor()
            cur.execute("SELECT job_id FROM jobs WHERE job_id = ?", (tmp_job.job_id,))
            if cur.fetchone() is None:
                cur.execute(
                    "INSERT INTO jobs (job_id, raw_data, state) VALUES (?, ?, ?)",
                    (tmp_job.job_id, self._json_dumps(raw), JobState.FETCHED.value),
                )
        self.conn.commit()

    def _get_next_row(self) -> Optional[sqlite3.Row]:
        """Retrieve the next job that is not finished (SUBMITTED or SKIPPED)."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM jobs WHERE state NOT IN (?, ?) ORDER BY rowid ASC LIMIT 1",
            (JobState.SUBMITTED.value, JobState.SKIPPED.value),
        )
        return cur.fetchone()

    def _update_job(self, job_id: str, **fields: Any) -> None:
        """Update arbitrary fields in the jobs table."""
        if not fields:
            return
        keys = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [job_id]
        sql = f"UPDATE jobs SET {keys} WHERE job_id = ?"
        cur = self.conn.cursor()
        cur.execute(sql, values)
        self.conn.commit()

    def step(self) -> bool:
        """Process one job through a single state transition.

        Returns:
            bool: True if a job was processed, False if there are no pending jobs.
        """
        row = self._get_next_row()
        if row is None:
            return False

        job_id = row["job_id"]
        state = JobState(row["state"])

        raw_data = json.loads(row["raw_data"])
        normalized_data = json.loads(row["normalized_data"]) if row["normalized_data"] else None
        decision_data = json.loads(row["decision_data"]) if row["decision_data"] else None
        plan_data = json.loads(row["plan_data"]) if row["plan_data"] else None

        if state == JobState.FETCHED:
            # Normalise
            job = self.normalizer.normalize(raw_data)
            self._update_job(job_id, normalized_data=self._json_dumps(job.asdict()), state=JobState.NORMALIZED.value)
            return True

        if state == JobState.NORMALIZED:
            job = Job(**normalized_data)  # type: ignore[arg-type]
            decision = self.evaluator.evaluate(job)
            self._update_job(job_id, decision_data=self._json_dumps(decision.__dict__), state=JobState.EVALUATED.value)
            return True

        if state == JobState.EVALUATED:
            decision = Decision(**decision_data)  # type: ignore[var-annotated]
            if decision.recommendation == "skip":
                self._update_job(job_id, state=JobState.SKIPPED.value)
            elif decision.recommendation == "human_review":
                self._update_job(job_id, state=JobState.HUMAN_REVIEW.value)
            else:
                self._update_job(job_id, state=JobState.PLANNED.value)
            return True

        if state == JobState.PLANNED:
            job = Job(**normalized_data)  # type: ignore[arg-type]
            decision = Decision(**decision_data)  # type: ignore[var-annotated]
            plan = self.planner.plan(job, decision, self.resume_inventory)
            self._update_job(job_id, plan_data=self._json_dumps(plan.__dict__), state=JobState.MATERIAL_READY.value)
            return True

        if state == JobState.MATERIAL_READY:
            job = Job(**normalized_data)  # type: ignore[arg-type]
            plan = ApplicationPlan(**plan_data)  # type: ignore[var-annotated]

            if not plan.apply:
                self._update_job(job_id, state=JobState.SKIPPED.value)
                return True

            # Prepare résumé
            core_resume = self.resume_inventory.get("core_resume", "")
            modules_dict = self.resume_inventory.get("modules_dict", {})
            highlight_names = plan.resume_strategy.get("highlight_modules", []) if plan.resume_strategy else []
            highlight_texts = [modules_dict.get(mod, "") for mod in highlight_names]
            final_resume = self.resume_modifier.modify(core_resume, highlight_texts, job.keywords)

            # Generate cover letter using candidate must‑have as facts
            candidate_facts = self.profile.must_have
            cover_letter = self.cover_letter_writer.write(job, candidate_facts)

            # Ask for confirmation (always yes in demo)
            if request_confirmation(job):
                # Fill the form and upload documents
                fill_form(job, plan, final_resume, cover_letter)
                upload_resume(job, final_resume)
                upload_cover_letter(job, cover_letter)
                take_screenshot(job)
                # Mark as submitted
                self._update_job(job_id, state=JobState.SUBMITTED.value)
            else:
                # If not confirmed, revert to human review
                self._update_job(job_id, state=JobState.HUMAN_REVIEW.value)
            return True

        # For other states we do nothing
        return False

    def run(self) -> None:
        """Process all pending jobs until completion."""
        while self.step():
            pass
