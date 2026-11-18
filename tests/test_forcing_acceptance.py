"""analysis/out/forcing_acceptance.json must be what analysis/forcing_acceptance.py computes from the committed
force-2 passes (data/runs/forced-2/)."""

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def test_forcing_acceptance_matches_the_committed_json():
    r = subprocess.run([sys.executable, str(REPO / "analysis" / "forcing_acceptance.py"), "--check"],
                       capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 0, r.stderr
