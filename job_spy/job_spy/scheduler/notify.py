"""
Notification script.

In a full implementation this script would send notifications to the user
whenever the FSM reaches a state that requires human intervention (e.g.,
`HUMAN_REVIEW`).  For demonstration it simply prints pending human reviews.
"""
from __future__ import annotations

import json
import os
import sqlite3

from ..pipeline.states import JobState


def main() -> None:
    # Locate the database
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_path = os.path.join(base_dir, 'data', 'jobs.db')
    if not os.path.exists(db_path):
        print("[notify] No database found.")
        return
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs WHERE state = ?", (JobState.HUMAN_REVIEW.value,))
    rows = cur.fetchall()
    if not rows:
        print("[notify] No jobs awaiting human review.")
    else:
        print(f"[notify] {len(rows)} job(s) awaiting human review:")
        for row in rows:
            raw = json.loads(row['raw_data'])
            print(f"- {raw.get('title')} at {raw.get('company')} ({row['job_id']})")
    conn.close()


if __name__ == '__main__':
    main()