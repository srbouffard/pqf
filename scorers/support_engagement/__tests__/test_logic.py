import responses
import pytest
from scorers.support_engagement.logic import compute_metrics, _compute_avg_triage_days

_GITHUB_API = "https://api.github.com"

_PRODUCT = {
    "components": {
        "foundational": [{"github_repo": "canonical/synapse-operator"}]
    }
}

_ISSUES = [
    {
        "number": 1,
        "user": {"login": "reporter"},
        "created_at": "2026-06-01T00:00:00Z",
        "pull_request": None,  # not a PR
    },
    {
        "number": 2,
        "user": {"login": "reporter"},
        "created_at": "2026-06-01T00:00:00Z",
        "pull_request": None,
    },
]

_COMMENTS_ISSUE_1 = [
    {"user": {"login": "maintainer"}, "created_at": "2026-06-03T00:00:00Z"}
]  # 2 days to triage

_COMMENTS_ISSUE_2 = [
    {"user": {"login": "reporter"}, "created_at": "2026-06-01T12:00:00Z"},  # skip — same author
    {"user": {"login": "maintainer"}, "created_at": "2026-06-05T00:00:00Z"},  # 4 days
]

_PULLS = [
    {"number": 10, "created_at": "2026-06-01T00:00:00Z"},
]

_REVIEWS_PR_10 = [
    {"submitted_at": "2026-06-02T00:00:00Z", "state": "COMMENTED"},  # 1 day
]


@responses.activate
def test_avg_triage_days_computed_correctly():
    since = "2026-03-01T00:00:00Z"  # value doesn't matter for mock
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/canonical/synapse-operator/issues",
        json=_ISSUES,
        status=200,
        match_querystring=False,
    )
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/canonical/synapse-operator/issues/1/comments",
        json=_COMMENTS_ISSUE_1,
        status=200,
    )
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/canonical/synapse-operator/issues/2/comments",
        json=_COMMENTS_ISSUE_2,
        status=200,
    )
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/canonical/synapse-operator/pulls",
        json=_PULLS,
        status=200,
        match_querystring=False,
    )
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/canonical/synapse-operator/pulls/10/reviews",
        json=_REVIEWS_PR_10,
        status=200,
    )
    result = compute_metrics(_PRODUCT, "token")
    assert result["avg_triage_days"] == 3.0   # (2 + 4) / 2
    assert result["avg_pr_review_days"] == 1.0


@responses.activate
def test_returns_zero_when_no_issues():
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/canonical/synapse-operator/issues",
        json=[],
        status=200,
        match_querystring=False,
    )
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/canonical/synapse-operator/pulls",
        json=[],
        status=200,
        match_querystring=False,
    )
    result = compute_metrics(_PRODUCT, "token")
    assert result["avg_triage_days"] == 0.0
    assert result["avg_pr_review_days"] == 0.0


@responses.activate
def test_skips_pr_issues_in_issue_list():
    """Issues that are actually PRs (have pull_request key) are excluded."""
    issues = [{"number": 5, "user": {"login": "a"}, "created_at": "2026-06-01T00:00:00Z",
               "pull_request": {"url": "https://..."}}]
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/canonical/synapse-operator/issues",
        json=issues,
        status=200,
        match_querystring=False,
    )
    responses.add(
        responses.GET,
        f"{_GITHUB_API}/repos/canonical/synapse-operator/pulls",
        json=[],
        status=200,
        match_querystring=False,
    )
    result = compute_metrics(_PRODUCT, "token")
    assert result["avg_triage_days"] == 0.0


@responses.activate
def test_zero_when_issue_has_no_comments():
    issues = [{"number": 3, "user": {"login": "reporter"}, "created_at": "2026-06-01T00:00:00Z",
               "pull_request": None}]
    responses.add(
        responses.GET, f"{_GITHUB_API}/repos/canonical/synapse-operator/issues",
        json=issues, status=200, match_querystring=False,
    )
    responses.add(
        responses.GET, f"{_GITHUB_API}/repos/canonical/synapse-operator/issues/3/comments",
        json=[], status=200,
    )
    responses.add(
        responses.GET, f"{_GITHUB_API}/repos/canonical/synapse-operator/pulls",
        json=[], status=200, match_querystring=False,
    )
    result = compute_metrics(_PRODUCT, "token")
    assert result["avg_triage_days"] == 0.0


def test_returns_zeros_when_no_components():
    result = compute_metrics({}, "token")
    assert result == {"avg_triage_days": 0.0, "avg_pr_review_days": 0.0}


@responses.activate
def test_pr_review_zero_when_no_reviews():
    responses.add(
        responses.GET, f"{_GITHUB_API}/repos/canonical/synapse-operator/issues",
        json=[], status=200, match_querystring=False,
    )
    responses.add(
        responses.GET, f"{_GITHUB_API}/repos/canonical/synapse-operator/pulls",
        json=[{"number": 20, "created_at": "2026-06-01T00:00:00Z"}], status=200,
        match_querystring=False,
    )
    responses.add(
        responses.GET, f"{_GITHUB_API}/repos/canonical/synapse-operator/pulls/20/reviews",
        json=[], status=200,
    )
    result = compute_metrics(_PRODUCT, "token")
    assert result["avg_pr_review_days"] == 0.0


@responses.activate
def test_aggregates_multiple_repos():
    """Two foundational repos — both contribute to averages."""
    product = {
        "components": {
            "foundational": [
                {"github_repo": "canonical/synapse-operator"},
                {"github_repo": "canonical/postgresql-k8s-operator"},
            ]
        }
    }
    for repo in ("canonical/synapse-operator", "canonical/postgresql-k8s-operator"):
        responses.add(
            responses.GET, f"{_GITHUB_API}/repos/{repo}/issues",
            json=[{"number": 1, "user": {"login": "a"}, "created_at": "2026-06-01T00:00:00Z",
                   "pull_request": None}],
            status=200, match_querystring=False,
        )
        responses.add(
            responses.GET, f"{_GITHUB_API}/repos/{repo}/issues/1/comments",
            json=[{"user": {"login": "b"}, "created_at": "2026-06-03T00:00:00Z"}],
            status=200,
        )
        responses.add(
            responses.GET, f"{_GITHUB_API}/repos/{repo}/pulls",
            json=[], status=200, match_querystring=False,
        )
    result = compute_metrics(product, "token")
    assert result["avg_triage_days"] == 2.0   # both repos have 2-day triage


@responses.activate
def test_excludes_prs_outside_90day_window():
    """PRs created more than 90 days ago are excluded from the metric."""
    # One old PR (created ~180 days ago), one recent PR (created recently)
    pulls = [
        {"number": 1, "created_at": "2025-12-01T00:00:00Z"},  # ~180 days ago
        {"number": 2, "created_at": "2026-06-01T00:00:00Z"},  # recent
    ]
    responses.add(
        responses.GET, f"{_GITHUB_API}/repos/canonical/synapse-operator/issues",
        json=[], status=200, match_querystring=False,
    )
    responses.add(
        responses.GET, f"{_GITHUB_API}/repos/canonical/synapse-operator/pulls",
        json=pulls, status=200, match_querystring=False,
    )
    responses.add(
        responses.GET, f"{_GITHUB_API}/repos/canonical/synapse-operator/pulls/2/reviews",
        json=[{"submitted_at": "2026-06-02T00:00:00Z"}], status=200,
    )
    result = compute_metrics(_PRODUCT, "token")
    # Only PR #2 should be considered (PR #1 is outside 90-day window)
    assert result["avg_pr_review_days"] == 1.0
