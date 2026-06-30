import base64
from typing import Any

import requests

_GITHUB_API = "https://api.github.com"


def _make_github_session(github_token: str) -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    )
    return session


def _fetch_workflow_contents(owner_repo: str, github_token: str) -> list[str]:
    """Fetch text contents of all workflow YAML files in .github/workflows/."""
    session = _make_github_session(github_token)
    list_resp = session.get(
        f"{_GITHUB_API}/repos/{owner_repo}/contents/.github/workflows",
        timeout=15,
    )
    if not list_resp.ok:
        return []
    contents = []
    for entry in list_resp.json():
        if entry.get("type") != "file":
            continue
        name = entry.get("name", "")
        if not (name.endswith(".yml") or name.endswith(".yaml")):
            continue
        file_resp = session.get(entry["url"], timeout=15)
        if file_resp.ok:
            data = file_resp.json()
            raw = base64.b64decode(data.get("content", "")).decode("utf-8", errors="replace")
            contents.append(raw)
    return contents


def compute_metrics(product: dict[str, Any], github_token: str) -> dict[str, Any]:
    """
    Check GitHub Security features for all foundational component repos.

    dependabot_enabled: .github/dependabot.yml exists in any foundational repo
    codeql_enabled:     any workflow in any foundational repo references github/codeql-action
    """
    foundational = product.get("components", {}).get("foundational", [])
    repos = [c["github_repo"] for c in foundational if "github_repo" in c]

    dependabot_enabled = False
    codeql_enabled = False

    for repo in repos:
        session = _make_github_session(github_token)
        dependabot_resp = session.get(
            f"{_GITHUB_API}/repos/{repo}/contents/.github/dependabot.yml",
            timeout=15,
        )
        if dependabot_resp.status_code == 200:
            dependabot_enabled = True
        for content in _fetch_workflow_contents(repo, github_token):
            if "github/codeql-action" in content:
                codeql_enabled = True

    return {
        "dependabot_enabled": dependabot_enabled,
        "codeql_enabled": codeql_enabled,
    }
