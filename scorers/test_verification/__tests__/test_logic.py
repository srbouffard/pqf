import pytest
import responses

from scorers.test_verification.logic import compute_metrics

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


def test_returns_zeros_when_allure_url_empty():
    result = compute_metrics({"allure_report_url": ""})
    assert result == {"coverage_pct": 0, "stability_pct": 0, "latest_build_passing": False}


def test_returns_zeros_when_allure_url_missing():
    result = compute_metrics({})
    assert result == {"coverage_pct": 0, "stability_pct": 0, "latest_build_passing": False}


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
    assert result == {"coverage_pct": 0, "stability_pct": 0, "latest_build_passing": False}


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
