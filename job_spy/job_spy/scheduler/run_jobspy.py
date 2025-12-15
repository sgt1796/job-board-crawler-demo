"""
Run the pipeline using the JobSpy crawler.

This script mirrors `run_pipeline.py` but pulls live jobs via the optional
`jobspy` dependency.  It is safe to run without `jobspy` installed; a clear
error message is emitted in that case.
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import List, Optional

from ..crawlers import JobSpyCrawler
from ..pipeline.fsm import JobStateMachine
from ..pipeline.runner import load_profile, load_resume_inventory


def _parse_csv(text: str) -> List[str]:
    return [part.strip() for part in text.split(",") if part.strip()]


def _parse_proxies(proxy_arg: str) -> Optional[List[str]]:
    proxies = _parse_csv(proxy_arg)
    return proxies or None


def build_arg_parser(base_dir: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch jobs via jobspy and run the pipeline.")
    parser.add_argument("--search-term", default="UI UX -PhD -Master -Head", help="Search query.")
    parser.add_argument("--location", default="MA, USA", help="Location filter.")
    parser.add_argument(
        "--platforms",
        default="indeed,linkedin",
        help="Comma-separated list of job boards supported by jobspy.",
    )
    parser.add_argument("--hours-old", type=int, default=144, help="Maximum age of listings in hours.")
    parser.add_argument("--results", type=int, default=50, help="Maximum number of results to request.")
    parser.add_argument("--country-indeed", default="USA", help="Country code passed to Indeed searches.")
    parser.add_argument(
        "--proxies",
        default=os.environ.get("JOBSPY_PROXIES", ""),
        help="Comma-separated proxy list or set JOBSPY_PROXIES env var.",
    )
    parser.add_argument(
        "--profile",
        default=os.path.join(base_dir, "profiles", "candidate_profile.json"),
        help="Path to candidate profile JSON.",
    )
    parser.add_argument(
        "--resume-core",
        default=os.path.join(base_dir, "profiles", "resume_core.md"),
        help="Core resume markdown path.",
    )
    parser.add_argument(
        "--modules-dir",
        default=os.path.join(base_dir, "profiles", "resume_modules"),
        help="Directory of optional resume modules.",
    )
    parser.add_argument(
        "--db-path",
        default=os.path.join(base_dir, "data", "jobs.db"),
        help="SQLite database path for job state.",
    )
    parser.add_argument(
        "--schema-path",
        default=os.path.join(base_dir, "data", "schema.sql"),
        help="SQL schema file path.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> None:
    if JobSpyCrawler is None:
        sys.exit("JobSpyCrawler requires the `jobspy` package. Install it with `pip install python-jobspy`.")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    parser = build_arg_parser(base_dir)
    args = parser.parse_args(argv)

    platforms = _parse_csv(args.platforms) or ["indeed", "linkedin"]
    proxies = _parse_proxies(args.proxies)

    profile = load_profile(args.profile)
    inventory = load_resume_inventory(args.resume_core, args.modules_dir)

    fsm = JobStateMachine(profile, inventory, db_path=args.db_path, schema_path=args.schema_path)
    crawler = JobSpyCrawler(
        search_term=args.search_term,
        location=args.location,
        platforms=platforms,
        hours_old=args.hours_old,
        results_wanted=args.results,
        country_indeed=args.country_indeed,
        proxies=proxies,
    )

    jobs = crawler.fetch()
    fsm.add_jobs(jobs)
    fsm.run()
    fsm.close()

    print(f"Processed {len(jobs)} jobs from {', '.join(platforms)}")


if __name__ == "__main__":
    main()
