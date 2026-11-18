"""The 2026-11-18 preliminary-results doc shows the committed numbers (DESIGN §5 rule 6).

The full recompute (`python analysis/prelim_2026_11_18.py --runs-root data/runs`) takes about an
hour. This check takes seconds: the tables in docs/results/2026-11-18-preliminary.md must be exactly
the ones rendered from analysis/out/prelim_2026_11_18.json, so no table is edited by hand or left
behind when the numbers change. It reads only those two files.
"""

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def test_prelim_doc_tables_match_the_committed_numbers():
    r = subprocess.run([sys.executable, str(REPO / "analysis" / "prelim_2026_11_18.py"), "--render-only", "--check"],
                       capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 0, r.stdout + r.stderr
