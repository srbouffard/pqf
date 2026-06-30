from unittest.mock import MagicMock

import responses

from scorers.documentation.logic import (
    _check_file_exists,
    _check_url_alive,
    _primary_repo,
    compute_metrics,
)

_PRODUCT = {
    "id": "matrix",
    "documentation_url": "https://charmhub.io/synapse",
    "components": {
        "foundational": [
            {"id": "synapse", "type": "charm", "github_repo": "canonical/synapse-operator"}
        ]
    },
}

_README = "# Synapse\n\n## Getting started\n\nThis tutorial shows you how to deploy...\n"


def test_primary_repo_returns_first_foundational():
    assert _primary_repo(_PRODUCT) == "canonical/synapse-operator"


def test_primary_repo_falls_back_to_feature():
    product = {"components": {"feature": [{"github_repo": "canonical/foo"}]}}
    assert _primary_repo(product) == "canonical/foo"


def test_primary_repo_returns_none_when_no_components():
    assert _primary_repo({}) is None


@responses.activate
def test_check_file_exists_true():
    responses.add(
        responses.GET,
        "https://api.github.com/repos/canonical/synapse-operator/contents/README.md",
        json={"name": "README.md"},
        status=200,
    )
    assert _check_file_exists("canonical/synapse-operator", "README.md", "token") is True


@responses.activate
def test_check_file_exists_false_on_404():
    responses.add(
        responses.GET,
        "https://api.github.com/repos/canonical/synapse-operator/contents/CONTRIBUTING.md",
        status=404,
    )
    assert _check_file_exists("canonical/synapse-operator", "CONTRIBUTING.md", "token") is False


@responses.activate
def test_check_url_alive_true():
    responses.add(responses.GET, "https://charmhub.io/synapse", status=200)
    assert _check_url_alive("https://charmhub.io/synapse") is True


@responses.activate
def test_check_url_alive_false_on_404():
    responses.add(responses.GET, "https://charmhub.io/synapse", status=404)
    assert _check_url_alive("https://charmhub.io/synapse") is False


def test_compute_metrics_happy_path(mocker):
    mocker.patch(
        "scorers.documentation.logic._check_file_exists",
        side_effect=lambda repo, fname, token: fname
        in {"README.md", "CONTRIBUTING.md", "SECURITY.md"},
    )
    mocker.patch("scorers.documentation.logic._check_url_alive", return_value=True)
    mocker.patch(
        "scorers.documentation.logic._fetch_readme",
        return_value=_README,
    )
    mock_client = MagicMock()
    mocker.patch("scorers.documentation.logic._make_openrouter_client", return_value=mock_client)
    # Patch style call separately on second invocation
    mock_client.chat.completions.create.side_effect = [
        MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content='{"diataxis_coverage": 2, "reasoning": "ok"}'
                    )
                )
            ]
        ),
        MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content='{"style_linter_passing": false, "reasoning": "ok"}'
                    )
                )
            ]
        ),
    ]

    result = compute_metrics(_PRODUCT, "gh-token", "or-key")
    assert result["has_readme"] is True
    assert result["has_contributing"] is True
    assert result["has_security"] is True
    assert result["links_passing"] is True
    assert result["diataxis_coverage"] == 2
    assert result["style_linter_passing"] is False
