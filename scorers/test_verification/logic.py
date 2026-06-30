from typing import Any

import requests


def compute_metrics(product: dict[str, Any]) -> dict[str, Any]:
    """
    Fetch test metrics from the product's Allure report.

    Reads allure_report_url from the product dict. Appends /widgets/summary.json
    to fetch the summary. Returns zeros if the URL is empty or missing.
    Raises requests.HTTPError on non-2xx responses.
    """
    url = product.get("allure_report_url", "").strip()
    if not url:
        return {"coverage_pct": 0, "stability_pct": 0, "latest_build_passing": False}

    summary_url = url.rstrip("/") + "/widgets/summary.json"
    resp = requests.get(summary_url, timeout=30)
    resp.raise_for_status()

    stat = resp.json().get("statistic", {})
    total = stat.get("total", 0)
    if total == 0:
        return {"coverage_pct": 0, "stability_pct": 0, "latest_build_passing": False}

    passed = stat.get("passed", 0)
    failed = stat.get("failed", 0)
    broken = stat.get("broken", 0)

    return {
        "coverage_pct": round(passed / total * 100),
        "stability_pct": round((total - failed - broken) / total * 100),
        "latest_build_passing": failed == 0 and broken == 0,
    }
