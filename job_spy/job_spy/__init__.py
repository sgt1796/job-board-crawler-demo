from __future__ import annotations

import sys
from pathlib import Path

# Add the parent of the repository (one level above the job_spy directory) to
# the import path.  This allows the `job_spy` package in the repo root to be
# importable regardless of the working directory used to run tests/scripts.
REPO_ROOT = Path(__file__).resolve().parent
PARENT = REPO_ROOT.parent

if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))
