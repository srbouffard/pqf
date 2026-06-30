# engine/medal_engine.py
from engine.drift_tracker import compute_dimension_drift
from engine.models import MEDAL_RANK, DimensionResult, Medal, ProductResult
from engine.rubric import evaluate_rubric


def compute_product(
    product: dict,
    computed: dict,
    dimensions_config: dict,
    drift_history: dict,
) -> ProductResult:
    """
    Compute the current medal and per-dimension results for a product.

    Pure function — reads drift_history but never mutates it.
    Call engine.drift_tracker.update_drift_history() separately to persist
    drift state changes.
    """
    target_medal = Medal(product["target_medal"])
    dimension_results: dict[str, DimensionResult] = {}

    for dim_name, dim_config in dimensions_config.get("dimensions", {}).items():
        metrics = computed.get("metrics", {}).get(dim_name, {})
        dim_medal = evaluate_rubric(metrics, dim_config["medals"])
        drift = compute_dimension_drift(
            product["id"], dim_name, dim_medal, target_medal, drift_history
        )
        dimension_results[dim_name] = DimensionResult(
            medal=dim_medal,
            target=target_medal,
            metrics=metrics,
            drift=drift,
        )

    if dimension_results:
        current_medal = min(
            dimension_results.values(),
            key=lambda r: MEDAL_RANK[r.medal],
        ).medal
    else:
        current_medal = Medal.UNRATED

    return ProductResult(
        product_id=product["id"],
        current_medal=current_medal,
        target_medal=target_medal,
        dimensions=dimension_results,
    )
