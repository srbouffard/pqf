import base64
import responses
from scorers.security_ssdlc.logic import compute_metrics

_GITHUB_API = "https://api.github.com"

_CODEQL_WORKFLOW = """\
name: CodeQL
on: [push]
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: github/codeql-action/init@v3
"""

_NO_CODEQL_WORKFLOW = """\
name: CI
on: [push]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: echo lint
"""


def _b64(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


def _mock_dependabot(owner_repo: str, exists: bool):
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/{owner_repo}/contents/.github/dependabot.yml",
        json={"name": "dependabot.yml"} if exists else {},
        status=200 if exists else 404,
    )


def _mock_workflows_dir(owner_repo: str, filenames: list[str]):
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/{owner_repo}/contents/.github/workflows",
        json=[
            {
                "name": name,
                "type": "file",
                "url": f"{_GITHUB_API}/repos/{owner_repo}/contents/.github/workflows/{name}",
            }
            for name in filenames
        ],
        status=200,
    )


def _mock_workflow_file(owner_repo: str, filename: str, content: str):
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/{owner_repo}/contents/.github/workflows/{filename}",
        json={"content": _b64(content), "encoding": "base64"},
        status=200,
    )


_PRODUCT = {
    "components": {
        "foundational": [{"github_repo": "canonical/synapse-operator"}]
    }
}

_PRODUCT_TWO_REPOS = {
    "components": {
        "foundational": [
            {"github_repo": "canonical/synapse-operator"},
            {"github_repo": "canonical/postgresql-k8s-operator"},
        ]
    }
}


@responses.activate
def test_dependabot_enabled_when_file_exists():
    _mock_dependabot("canonical/synapse-operator", exists=True)
    _mock_workflows_dir("canonical/synapse-operator", ["ci.yaml"])
    _mock_workflow_file("canonical/synapse-operator", "ci.yaml", _NO_CODEQL_WORKFLOW)
    result = compute_metrics(_PRODUCT, "token")
    assert result["dependabot_enabled"] is True


@responses.activate
def test_dependabot_disabled_on_404():
    _mock_dependabot("canonical/synapse-operator", exists=False)
    _mock_workflows_dir("canonical/synapse-operator", ["ci.yaml"])
    _mock_workflow_file("canonical/synapse-operator", "ci.yaml", _NO_CODEQL_WORKFLOW)
    result = compute_metrics(_PRODUCT, "token")
    assert result["dependabot_enabled"] is False


@responses.activate
def test_codeql_enabled_when_workflow_contains_action():
    _mock_dependabot("canonical/synapse-operator", exists=False)
    _mock_workflows_dir("canonical/synapse-operator", ["codeql.yaml"])
    _mock_workflow_file("canonical/synapse-operator", "codeql.yaml", _CODEQL_WORKFLOW)
    result = compute_metrics(_PRODUCT, "token")
    assert result["codeql_enabled"] is True


@responses.activate
def test_codeql_disabled_when_action_absent():
    _mock_dependabot("canonical/synapse-operator", exists=False)
    _mock_workflows_dir("canonical/synapse-operator", ["ci.yaml"])
    _mock_workflow_file("canonical/synapse-operator", "ci.yaml", _NO_CODEQL_WORKFLOW)
    result = compute_metrics(_PRODUCT, "token")
    assert result["codeql_enabled"] is False


@responses.activate
def test_scans_all_foundational_repos():
    _mock_dependabot("canonical/synapse-operator", exists=True)
    _mock_workflows_dir("canonical/synapse-operator", ["ci.yaml"])
    _mock_workflow_file("canonical/synapse-operator", "ci.yaml", _NO_CODEQL_WORKFLOW)
    _mock_dependabot("canonical/postgresql-k8s-operator", exists=False)
    _mock_workflows_dir("canonical/postgresql-k8s-operator", ["codeql.yaml"])
    _mock_workflow_file("canonical/postgresql-k8s-operator", "codeql.yaml", _CODEQL_WORKFLOW)
    result = compute_metrics(_PRODUCT_TWO_REPOS, "token")
    assert result["dependabot_enabled"] is True
    assert result["codeql_enabled"] is True


def test_no_foundational_components_returns_false():
    result = compute_metrics({}, "token")
    assert result == {"dependabot_enabled": False, "codeql_enabled": False}
