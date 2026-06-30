import pytest
from engine.rubric import eval_condition


# --- Numeric comparisons ---

def test_gte_true():
    assert eval_condition({"coverage_pct": 90}, "coverage_pct >= 90") is True


def test_gte_false():
    assert eval_condition({"coverage_pct": 89}, "coverage_pct >= 90") is False


def test_gt_true():
    assert eval_condition({"coverage_pct": 91}, "coverage_pct > 90") is True


def test_gt_boundary_false():
    assert eval_condition({"coverage_pct": 90}, "coverage_pct > 90") is False


def test_lte_true():
    assert eval_condition({"avg_triage_days": 3}, "avg_triage_days <= 5") is True


def test_lte_false():
    assert eval_condition({"avg_triage_days": 6}, "avg_triage_days <= 5") is False


def test_lt_true():
    assert eval_condition({"avg_triage_days": 2}, "avg_triage_days < 5") is True


def test_lt_boundary_false():
    assert eval_condition({"avg_triage_days": 5}, "avg_triage_days < 5") is False


def test_eq_numeric():
    assert eval_condition({"diataxis_coverage": 4}, "diataxis_coverage == 4") is True


def test_neq_numeric():
    assert eval_condition({"diataxis_coverage": 3}, "diataxis_coverage != 4") is True


# --- Boolean comparisons ---

def test_bool_eq_true_passes():
    assert eval_condition({"latest_build_passing": True}, "latest_build_passing == true") is True


def test_bool_eq_true_fails_when_false():
    assert eval_condition({"latest_build_passing": False}, "latest_build_passing == true") is False


def test_bool_eq_false_passes():
    assert eval_condition({"has_readme": False}, "has_readme == false") is True


def test_bool_neq():
    assert eval_condition({"ssdlc_onboarded": False}, "ssdlc_onboarded != true") is True


# --- Missing key ---

def test_missing_key_returns_false():
    assert eval_condition({}, "coverage_pct >= 70") is False


def test_missing_key_bool_returns_false():
    assert eval_condition({}, "latest_build_passing == true") is False


# --- Invalid condition ---

def test_invalid_condition_raises_value_error():
    with pytest.raises(ValueError, match="Invalid condition"):
        eval_condition({}, "this is not valid")


def test_condition_with_extra_spaces_is_valid():
    assert eval_condition({"coverage_pct": 90}, "  coverage_pct  >=  90  ") is True
