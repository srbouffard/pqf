import pytest
import responses

from scorers.test_verification.logic import _uses_jubilant, _uses_ops_testing, compute_metrics

_SUMMARY = {
    "statistic": {"total": 100, "passed": 87, "failed": 3, "broken": 2, "skipped": 8, "unknown": 0}
}

_PASSING_SUMMARY = {
    "statistic": {"total": 50, "passed": 50, "failed": 0, "broken": 0, "skipped": 0, "unknown": 0}
}


@responses.activate
def test_returns_metrics_from_allure_summary():
    responses.add(
        responses.GET,
        "https://allure.example.com/reports/synapse/widgets/summary.json",
        json=_SUMMARY,
        status=200,
    )
    product = {"allure_report_url": "https://allure.example.com/reports/synapse"}
    result = compute_metrics(product)
    assert result["coverage_pct"] == 87
    assert result["stability_pct"] == 95  # (100 - 3 - 2) / 100 * 100
    assert result["latest_build_passing"] is False
    assert result["uses_ops_testing"] is False
    assert result["uses_jubilant"] is False


@responses.activate
def test_returns_passing_when_all_pass():
    responses.add(
        responses.GET,
        "https://allure.example.com/reports/synapse/widgets/summary.json",
        json=_PASSING_SUMMARY,
        status=200,
    )
    product = {"allure_report_url": "https://allure.example.com/reports/synapse"}
    result = compute_metrics(product)
    assert result["coverage_pct"] == 100
    assert result["stability_pct"] == 100
    assert result["latest_build_passing"] is True
    assert result["uses_ops_testing"] is False
    assert result["uses_jubilant"] is False


def test_returns_zeros_when_allure_url_empty():
    result = compute_metrics({"allure_report_url": ""})
    assert result == {
        "coverage_pct": 0,
        "stability_pct": 0,
        "latest_build_passing": False,
        "uses_ops_testing": False,
        "uses_jubilant": False,
    }


def test_returns_zeros_when_allure_url_missing():
    result = compute_metrics({})
    assert result == {
        "coverage_pct": 0,
        "stability_pct": 0,
        "latest_build_passing": False,
        "uses_ops_testing": False,
        "uses_jubilant": False,
    }


@responses.activate
def test_returns_zeros_when_total_is_zero():
    responses.add(
        responses.GET,
        "https://allure.example.com/reports/synapse/widgets/summary.json",
        json={"statistic": {"total": 0, "passed": 0, "failed": 0, "broken": 0}},
        status=200,
    )
    product = {"allure_report_url": "https://allure.example.com/reports/synapse"}
    result = compute_metrics(product)
    assert result == {
        "coverage_pct": 0,
        "stability_pct": 0,
        "latest_build_passing": False,
        "uses_ops_testing": False,
        "uses_jubilant": False,
    }


@responses.activate
def test_raises_on_http_error():
    responses.add(
        responses.GET,
        "https://allure.example.com/reports/synapse/widgets/summary.json",
        status=404,
    )
    product = {"allure_report_url": "https://allure.example.com/reports/synapse"}
    with pytest.raises(Exception):
        compute_metrics(product)


def test_uses_ops_testing_true_when_no_harness(mocker):
    mocker.patch("scorers.test_verification.logic._search_code", return_value=0)
    assert _uses_ops_testing(["canonical/synapse-operator"], "token") is True


def test_uses_jubilant_true_when_jubilant_found(mocker):
    mocker.patch("scorers.test_verification.logic._search_code", return_value=1)
    assert _uses_jubilant(["canonical/synapse-operator"], "token") is True
