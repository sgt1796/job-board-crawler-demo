-- SQLite schema for the job spy pipeline.

CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    raw_data TEXT NOT NULL,
    normalized_data TEXT,
    decision_data TEXT,
    plan_data TEXT,
    state TEXT NOT NULL
);