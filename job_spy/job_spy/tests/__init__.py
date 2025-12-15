# This package contains unit tests for the job spy project.

import sys
from pathlib import Path

# Make the repository parent discoverable so `import job_spy...` works when
# running tests directly from the project root.
REPO_PARENT = Path(__file__).resolve().parent.parent.parent
if str(REPO_PARENT) not in sys.path:
    sys.path.insert(0, str(REPO_PARENT))
