"""
Crawler invocation script.

This script can be scheduled to run periodically and populate the jobs
database with new postings.  It uses the dummy crawler in this demo.  When
integrating a real crawler, replace `DummyCrawler` with your implementation.
"""
from __future__ import annotations

import json
import os

from ..agents import CandidateProfile
from ..crawlers import DummyCrawler
from ..pipeline.fsm import JobStateMachine
from ..pipeline.runner import load_profile, load_resume_inventory


def main() -> None:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    profile_path = os.path.join(base_dir, 'profiles', 'candidate_profile.json')
    resume_core = os.path.join(base_dir, 'profiles', 'resume_core.md')
    modules_dir = os.path.join(base_dir, 'profiles', 'resume_modules')

    profile = load_profile(profile_path)
    inventory = load_resume_inventory(resume_core, modules_dir)

    fsm = JobStateMachine(profile, inventory)
    crawler = DummyCrawler()
    jobs = crawler.fetch()
    fsm.add_jobs(jobs)
    fsm.close()


if __name__ == '__main__':
    main()