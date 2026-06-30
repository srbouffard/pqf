# engine/__tests__/test_integration.py
"""
End-to-end test: run the CLI against the sample matrix.yaml + matrix.json
and verify the expected medals are computed.

Expected per-dimension medals for computed/matrix.json:
  test_verification: silver  (coverage 87 >= 80, stability 94 >= 85; 87 < 90 → not gold)
  documentation:     bronze  (has all files + links_passing, but diataxis 3 < 4 → not silver)
  substrate_compat:  silver  (supports_juju_3=true; juju_4+ck8s false → not gold)
  security_ssdlc:    silver  (dependabot_enabled=true; codeql_enabled=false → not gold)
  support_engagement: silver (triage 3 <= 5; pr_review 6 <= 7; both > gold threshold)

Overall current_medal: bronze (documentation pulls it down)
Target: gold → all dimensions drifting, but no history entries yet → drift=None
"""
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def test_cli_computes_expected_medals_for_matrix():
    result = subprocess.run(
        [
            sys.executable, "-m", "engine",
            "--product", str(REPO_ROOT / "products/matrix.yaml"),
            "--computed", str(REPO_ROOT / "computed/matrix.json"),
            "--dimensions", str(REPO_ROOT / "config/dimensions.yaml"),
            "--drift-history", str(REPO_ROOT / "drift-history.json"),
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, f"CLI failed:\n{result.stderr}"

    output = json.loads(result.stdout)

    assert output["id"] == "matrix"
    assert output["current_medal"] == "bronze"
    assert output["target_medal"] == "gold"

    dims = output["dimensions"]
    assert dims["test_verification"]["medal"] == "silver"
    assert dims["documentation"]["medal"] == "bronze"
    assert dims["substrate_compat"]["medal"] == "silver"
    assert dims["security_ssdlc"]["medal"] == "silver"
    assert dims["support_engagement"]["medal"] == "silver"

    # No drift history entries yet → drift is null for all
    for dim in dims.values():
        assert dim["drift"] is None
