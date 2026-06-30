from datetime import UTC, datetime

from engine.drift_tracker import compute_dimension_drift, update_drift_history
from engine.models import Medal


# Helper: UTC datetime factory
def utc(year, month, day):
    return datetime(year, month, day, tzinfo=UTC)


# ─── compute_dimension_drift ───────────────────────────────────────────────────


def test_no_drift_when_current_equals_target():
    assert compute_dimension_drift("matrix", "docs", Medal.GOLD, Medal.GOLD, {}) is None


def test_no_drift_when_current_exceeds_target():
    # Gold current, silver target → no drift
    assert compute_dimension_drift("matrix", "docs", Medal.GOLD, Medal.SILVER, {}) is None


def test_no_drift_when_bronze_target_and_above():
    assert compute_dimension_drift("matrix", "docs", Medal.BRONZE, Medal.BRONZE, {}) is None


def test_returns_none_when_drifting_but_no_history_entry():
    # First time we see this drift — history is empty, None returned
    # (update_drift_history must be called to record it)
    result = compute_dimension_drift("matrix", "docs", Medal.BRONZE, Medal.GOLD, {})
    assert result is None


def test_returns_remediating_when_within_deadline():
    history = {
        "matrix": {
            "docs": {
                "first_seen_at": "2026-06-01T00:00:00+00:00",
                "deadline": "2099-12-01T00:00:00+00:00",  # far future
            }
        }
    }
    result = compute_dimension_drift("matrix", "docs", Medal.BRONZE, Medal.GOLD, history)
    assert result is not None
    assert result.status == "remediating"
    assert result.first_seen_at == "2026-06-01T00:00:00+00:00"


def test_returns_overdue_when_past_deadline():
    history = {
        "matrix": {
            "docs": {
                "first_seen_at": "2020-01-01T00:00:00+00:00",
                "deadline": "2020-07-01T00:00:00+00:00",  # past
            }
        }
    }
    result = compute_dimension_drift("matrix", "docs", Medal.BRONZE, Medal.GOLD, history)
    assert result is not None
    assert result.status == "overdue"


# ─── update_drift_history ──────────────────────────────────────────────────────


def test_records_new_drift_gold_target_six_months():
    history = {}
    now = utc(2026, 6, 1)
    update_drift_history("matrix", "docs", Medal.BRONZE, Medal.GOLD, history, now)

    assert "matrix" in history
    assert "docs" in history["matrix"]
    assert history["matrix"]["docs"]["first_seen_at"] == "2026-06-01T00:00:00+00:00"
    # Gold target → 6 months → deadline December 1
    assert history["matrix"]["docs"]["deadline"] == "2026-12-01T00:00:00+00:00"


def test_records_new_drift_silver_target_twelve_months():
    history = {}
    now = utc(2026, 6, 1)
    update_drift_history("matrix", "docs", Medal.BRONZE, Medal.SILVER, history, now)

    assert history["matrix"]["docs"]["deadline"] == "2027-06-01T00:00:00+00:00"


def test_preserves_existing_clock_when_already_drifting():
    original_start = "2026-01-01T00:00:00+00:00"
    original_deadline = "2026-07-01T00:00:00+00:00"
    history = {
        "matrix": {
            "docs": {
                "first_seen_at": original_start,
                "deadline": original_deadline,
            }
        }
    }
    now = utc(2026, 6, 1)  # later time — should NOT reset the clock
    update_drift_history("matrix", "docs", Medal.BRONZE, Medal.GOLD, history, now)

    assert history["matrix"]["docs"]["first_seen_at"] == original_start
    assert history["matrix"]["docs"]["deadline"] == original_deadline


def test_clears_entry_when_compliant():
    history = {
        "matrix": {
            "docs": {
                "first_seen_at": "2026-01-01T00:00:00+00:00",
                "deadline": "2026-07-01T00:00:00+00:00",
            }
        }
    }
    now = utc(2026, 6, 1)
    # Now at gold, target is gold → compliant → clear
    update_drift_history("matrix", "docs", Medal.GOLD, Medal.GOLD, history, now)

    assert history.get("matrix", {}).get("docs") is None


def test_clears_entry_and_removes_empty_product_dict():
    history = {
        "matrix": {
            "docs": {
                "first_seen_at": "2026-01-01T00:00:00+00:00",
                "deadline": "2026-07-01T00:00:00+00:00",
            }
        }
    }
    now = utc(2026, 6, 1)
    update_drift_history("matrix", "docs", Medal.GOLD, Medal.GOLD, history, now)

    # "matrix" key removed entirely when no more drifting dimensions
    assert "matrix" not in history


def test_does_not_record_drift_for_bronze_target():
    # Bronze is the minimum — nothing below bronze to drift to
    history = {}
    now = utc(2026, 6, 1)
    update_drift_history("matrix", "docs", Medal.UNRATED, Medal.BRONZE, history, now)
    assert history == {}


def test_multiple_dimensions_tracked_independently():
    history = {}
    now = utc(2026, 6, 1)
    update_drift_history("matrix", "docs", Medal.BRONZE, Medal.GOLD, history, now)
    update_drift_history("matrix", "tests", Medal.SILVER, Medal.GOLD, history, now)

    assert "docs" in history["matrix"]
    assert "tests" in history["matrix"]
    # Fixing docs doesn't clear tests
    update_drift_history("matrix", "docs", Medal.GOLD, Medal.GOLD, history, now)
    assert "docs" not in history["matrix"]
    assert "tests" in history["matrix"]
