# engine/__tests__/test_assemble.py
import json

from engine.assemble import _build_dimensions_meta, assemble_portfolio

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
                "gold": ["style_linter_passing == true"],
            }
        },
    }
}

_PRODUCT = {"id": "matrix", "name": "Matrix", "description": "Chat", "lifecycle": "stable",
            "target_medal": "gold", "ownership": {"squad": "americas"}, "documentation_url": "",
            "components": {}}

_COMPUTED = {
    "product_id": "matrix",
    "computed_at": "2026-06-29T20:00:00+00:00",
    "metrics": {
        "test_verification": {
            "coverage_pct": 90,
            "latest_build_passing": True,
        },
        "documentation": {
            "has_readme": True,
            "diataxis_coverage": 2,
            "style_linter_passing": False,
        },
    },
}


def test_assemble_portfolio_returns_products_list(tmp_path):
    products_dir = tmp_path / "products"
    products_dir.mkdir()
    computed_dir = tmp_path / "computed"
    computed_dir.mkdir()
    (products_dir / "matrix.yaml").write_text(
        "id: matrix\nname: Matrix\ndescription: Chat\nlifecycle: stable\ntarget_medal: gold\n"
        "ownership:\n  squad: americas\ndocumentation_url: ''\ncomponents: {}\n"
    )
    (computed_dir / "matrix.json").write_text(json.dumps(_COMPUTED))
    result = assemble_portfolio(
        products_dir=products_dir,
        computed_dir=computed_dir,
        dimensions_config=_DIMENSIONS,
        drift_history={},
        update_drift=False,
    )
    assert "generated_at" in result
    assert len(result["products"]) == 1
    assert result["products"][0]["id"] == "matrix"
    assert "dimensions_meta" in result


def test_assemble_portfolio_medal_computed_correctly(tmp_path):
    products_dir = tmp_path / "products"
    products_dir.mkdir()
    computed_dir = tmp_path / "computed"
    computed_dir.mkdir()
    (products_dir / "matrix.yaml").write_text(
        "id: matrix\nname: Matrix\ndescription: Chat\nlifecycle: stable\ntarget_medal: gold\n"
        "ownership:\n  squad: americas\ndocumentation_url: ''\ncomponents: {}\n"
    )
    (computed_dir / "matrix.json").write_text(json.dumps(_COMPUTED))
    result = assemble_portfolio(
        products_dir=products_dir, computed_dir=computed_dir,
        dimensions_config=_DIMENSIONS, drift_history={}, update_drift=False,
    )
    product = result["products"][0]
    # test_verification: coverage 90 → gold
    # documentation: has_readme=True bronze, diataxis 2 < 4 → bronze
    # overall current_medal = min(gold, bronze) = bronze
    assert product["current_medal"] == "bronze"


def test_dimensions_meta_structure():
    meta = _build_dimensions_meta(_DIMENSIONS)
    assert "test_verification" in meta
    assert "documentation" in meta
    tv = meta["test_verification"]
    assert "medals" in tv
    assert "bronze" in tv["medals"]
    assert "criteria" in tv["medals"]["bronze"]
    assert "coverage_pct >= 70" in tv["medals"]["bronze"]["criteria"]


def test_assemble_portfolio_missing_computed_gives_unrated(tmp_path):
    products_dir = tmp_path / "products"
    products_dir.mkdir()
    computed_dir = tmp_path / "computed"
    computed_dir.mkdir()
    (products_dir / "matrix.yaml").write_text(
        "id: matrix\nname: Matrix\ndescription: Chat\nlifecycle: stable\ntarget_medal: gold\n"
        "ownership:\n  squad: americas\ndocumentation_url: ''\ncomponents: {}\n"
    )
    # No computed/matrix.json — should treat as empty metrics
    result = assemble_portfolio(
        products_dir=products_dir, computed_dir=computed_dir,
        dimensions_config=_DIMENSIONS, drift_history={}, update_drift=False,
    )
    assert result["products"][0]["current_medal"] == "unrated"


def test_assemble_portfolio_updates_drift_when_flag_set(tmp_path):
    products_dir = tmp_path / "products"
    products_dir.mkdir()
    computed_dir = tmp_path / "computed"
    computed_dir.mkdir()
    (products_dir / "matrix.yaml").write_text(
        "id: matrix\nname: Matrix\ndescription: Chat\nlifecycle: stable\ntarget_medal: gold\n"
        "ownership:\n  squad: americas\ndocumentation_url: ''\ncomponents: {}\n"
    )
    # documentation is bronze, target gold → drifting
    (computed_dir / "matrix.json").write_text(json.dumps(_COMPUTED))
    drift_history: dict = {}
    assemble_portfolio(
        products_dir=products_dir, computed_dir=computed_dir,
        dimensions_config=_DIMENSIONS, drift_history=drift_history, update_drift=True,
    )
    # After update_drift=True, matrix/documentation drift should be recorded
    assert "matrix" in drift_history
    assert "documentation" in drift_history["matrix"]
