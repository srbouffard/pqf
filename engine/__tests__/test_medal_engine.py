# engine/__tests__/test_medal_engine.py
from engine.medal_engine import compute_product
from engine.models import Medal

# Minimal two-dimension config for testing
_DIMENSIONS = {
    "dimensions": {
        "test_verification": {
            "medals": {
                "bronze": ["coverage_pct >= 70", "latest_build_passing == true"],
                "silver": ["coverage_pct >= 80"],
                "gold": ["coverage_pct >= 90"],
            }
        },
        "documentation": {
            "medals": {
                "bronze": ["has_readme == true"],
                "silver": ["diataxis_coverage >= 4"],
                "gold": ["style_linter_passing == true", "diataxis_coverage == 4"],
            }
        },
    }
}

_PRODUCT = {"id": "test-product", "target_medal": "gold"}


def test_current_medal_is_lowest_across_dimensions():
    computed = {
        "metrics": {
            "test_verification": {"coverage_pct": 95, "latest_build_passing": True},
            # documentation only meets bronze
            "documentation": {
                "has_readme": True,
                "diataxis_coverage": 2,
                "style_linter_passing": False,
            },
        }
    }
    result = compute_product(_PRODUCT, computed, _DIMENSIONS, {})
    assert result.current_medal == Medal.BRONZE
    assert result.dimensions["test_verification"].medal == Medal.GOLD
    assert result.dimensions["documentation"].medal == Medal.BRONZE


def test_all_gold_dimensions_gives_gold_product():
    computed = {
        "metrics": {
            "test_verification": {"coverage_pct": 95, "latest_build_passing": True},
            "documentation": {
                "has_readme": True,
                "diataxis_coverage": 4,
                "style_linter_passing": True,
            },
        }
    }
    result = compute_product(_PRODUCT, computed, _DIMENSIONS, {})
    assert result.current_medal == Medal.GOLD


def test_all_silver_gives_silver_product():
    computed = {
        "metrics": {
            "test_verification": {"coverage_pct": 85, "latest_build_passing": True},
            "documentation": {
                "has_readme": True,
                "diataxis_coverage": 4,
                "style_linter_passing": False,
            },
        }
    }
    result = compute_product(_PRODUCT, computed, _DIMENSIONS, {})
    assert result.current_medal == Medal.SILVER


def test_missing_dimension_in_computed_treated_as_empty_metrics():
    # test_verification metrics missing entirely
    computed = {
        "metrics": {
            "documentation": {
                "has_readme": True,
                "diataxis_coverage": 4,
                "style_linter_passing": True,
            },
        }
    }
    result = compute_product(_PRODUCT, computed, _DIMENSIONS, {})
    # test_verification gets empty metrics → bronze conditions fail → unrated
    assert result.dimensions["test_verification"].medal == Medal.UNRATED
    assert result.current_medal == Medal.UNRATED


def test_entirely_empty_computed_gives_unrated():
    result = compute_product(_PRODUCT, {}, _DIMENSIONS, {})
    assert result.current_medal == Medal.UNRATED


def test_dimension_results_contain_target_medal():
    computed = {"metrics": {"test_verification": {"coverage_pct": 85, "latest_build_passing": True},
                             "documentation": {"has_readme": True, "diataxis_coverage": 2}}}
    result = compute_product(_PRODUCT, computed, _DIMENSIONS, {})
    for dim in result.dimensions.values():
        assert dim.target == Medal.GOLD


def test_product_id_and_target_medal_in_result():
    result = compute_product(_PRODUCT, {}, _DIMENSIONS, {})
    assert result.product_id == "test-product"
    assert result.target_medal == Medal.GOLD


def test_drift_is_none_for_dimension_when_no_history():
    # With empty drift_history, compute_dimension_drift returns None
    computed = {"metrics": {"test_verification": {"coverage_pct": 85, "latest_build_passing": True},
                             "documentation": {"has_readme": True, "diataxis_coverage": 2}}}
    result = compute_product(_PRODUCT, computed, _DIMENSIONS, {})
    # Documentation is bronze, target is gold → drifting, but no history entry yet → None
    assert result.dimensions["documentation"].drift is None
