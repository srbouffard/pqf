# engine/drift_tracker.py
# Stub — full implementation in Task 6
from engine.models import Medal, DriftState


def compute_dimension_drift(
    product_id: str,
    dim_name: str,
    current_medal: Medal,
    target_medal: Medal,
    drift_history: dict,
) -> DriftState | None:
    # Stub — returns None when no history entry exists
    # Full implementation in Task 6
    return None


def update_drift_history(
    product_id: str,
    dim_name: str,
    current_medal: Medal,
    target_medal: Medal,
    drift_history: dict,
    now: object,
) -> None:
    raise NotImplementedError
