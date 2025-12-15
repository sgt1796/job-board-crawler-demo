"""
Pipeline runner.

This script ties together the crawler, the candidate profile and the FSM.  It
fetches jobs using the dummy crawler, inserts them into the database and runs
the state machine until all jobs are processed.  You can replace the
`DummyCrawler` with a real crawler implementation.
"""
from __future__ import annotations

import json
import os

from ..agents import CandidateProfile
from ..crawlers import DummyCrawler
from ..pipeline.fsm import JobStateMachine


def load_profile(profile_path: str) -> CandidateProfile:
    with open(profile_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return CandidateProfile(
        target_titles=data.get('target_titles', []),
        must_have=data.get('must_have', []),
        nice_to_have=data.get('nice_to_have', []),
        hard_filters=data.get('hard_filters', {}),
        soft_preferences=data.get('soft_preferences', {}),
    )


def load_resume_inventory(core_path: str, modules_dir: str) -> dict:
    with open(core_path, 'r', encoding='utf-8') as f:
        core_resume = f.read()
    modules = []
    modules_dict = {}
    if os.path.isdir(modules_dir):
        for fname in os.listdir(modules_dir):
            if not fname.lower().endswith(('.md', '.txt')):
                continue
            name = os.path.splitext(fname)[0]
            path = os.path.join(modules_dir, fname)
            with open(path, 'r', encoding='utf-8') as mf:
                text = mf.read().strip()
                modules.append(name)
                modules_dict[name] = text
    return {
        'core_resume': core_resume,
        'modules': modules,
        'modules_dict': modules_dict,
    }


def main() -> None:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    profile_path = os.path.join(base_dir, 'profiles', 'candidate_profile.json')
    resume_core = os.path.join(base_dir, 'profiles', 'resume_core.md')
    modules_dir = os.path.join(base_dir, 'profiles', 'resume_modules')

    profile = load_profile(profile_path)
    inventory = load_resume_inventory(resume_core, modules_dir)

    fsm = JobStateMachine(profile, inventory)
    crawler = DummyCrawler()
    fsm.add_jobs(crawler.fetch())
    fsm.run()
    fsm.close()


if __name__ == '__main__':
    main()