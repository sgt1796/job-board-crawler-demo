"""
Convenience script to run the entire job spy pipeline.

Use this script as the main entry point in a scheduler to execute both
crawling and state machine processing.  It delegates to the runner in
`pipeline/runner.py`.
"""
from __future__ import annotations

from ..pipeline.runner import main as run


if __name__ == '__main__':
    run()