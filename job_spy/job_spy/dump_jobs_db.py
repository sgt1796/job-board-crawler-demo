"""
Utility script to inspect (and optionally clear) the pipeline jobs database.

Usage examples:
    python -m job_spy.dump_jobs_db
    python -m job_spy.dump_jobs_db --db-path /path/to/jobs.db --limit 5 --show-raw
    python -m job_spy.dump_jobs_db --truncate
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from typing import Any, Iterable

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "data", "jobs.db")


def _pretty_json(text: str) -> str:
    """Best effort pretty printer for JSON fields."""
    try:
        parsed = json.loads(text)
        return json.dumps(parsed, indent=2)
    except Exception:
        return text


def _iter_jobs(conn: sqlite3.Connection) -> Iterable[sqlite3.Row]:
    cur = conn.execute(
        "SELECT job_id, state, raw_data, normalized_data, decision_data, plan_data "
        "FROM jobs ORDER BY rowid ASC"
    )
    yield from cur


def dump_jobs(
    db_path: str = DEFAULT_DB_PATH,
    limit: int | None = None,
    show_raw: bool = False,
    truncate: bool = False,
) -> None:
    if not os.path.exists(db_path):
        sys.exit(f"No database found at: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        printed = 0
        for idx, row in enumerate(_iter_jobs(conn), start=1):
            if limit and printed >= limit:
                break

            job_id = row["job_id"]
            state = row["state"]
            header = f"[{idx}] {job_id} | state={state}"

            title = company = None
            if row["normalized_data"]:
                try:
                    norm = json.loads(row["normalized_data"])
                    title = norm.get("title")
                    company = norm.get("company")
                except Exception:
                    norm = None
            if title or company:
                header += f" | {title or '?'} @ {company or '?'}"

            print(header)

            for label in ("normalized_data", "decision_data", "plan_data"):
                data = row[label]
                if not data:
                    continue
                print(f"{label}:")
                print(_pretty_json(data))

            if show_raw and row["raw_data"]:
                print("raw_data:")
                print(_pretty_json(row["raw_data"]))

            print("-" * 60)
            printed += 1

        print(f"Printed {printed} row(s) from {db_path}")

        if truncate:
            conn.execute("DELETE FROM jobs")
            conn.commit()
            print("jobs table truncated.")
    finally:
        conn.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dump (and optionally clear) the jobs.db contents.")
    parser.add_argument("--db-path", default=DEFAULT_DB_PATH, help="Path to jobs.db file.")
    parser.add_argument("--limit", type=int, help="Maximum number of rows to print.")
    parser.add_argument("--show-raw", action="store_true", help="Include raw_data column in output.")
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Delete all rows after dumping. Useful to reset state.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    dump_jobs(
        db_path=args.db_path,
        limit=args.limit,
        show_raw=args.show_raw,
        truncate=args.truncate,
    )


if __name__ == "__main__":
    main()
