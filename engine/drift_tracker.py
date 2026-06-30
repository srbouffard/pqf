# engine/drift_tracker.py
from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta

from engine.models import MEDAL_RANK, DriftState, Medal

# Remediation window per target medal tier
_REMEDIATION_MONTHS: dict[Medal, int] = {
    Medal.GOLD: 6,
    Medal.SILVER: 12,
}


def compute_dimension_drift(
    product_id: str,
    dim_name: str,
    current_medal: Medal,
    target_medal: Medal,
    drift_history: dict,
) -> DriftState | None:
    """
    Read-only. Returns the current drift state for a product+dimension.

    Returns None if:
    - Product is at or above its target for this dimension (no drift)
    - Product is drifting but no history entry exists yet (call
      update_drift_history to record it; it will appear on the next run)
    """
    if MEDAL_RANK[current_medal] >= MEDAL_RANK[target_medal]:
        return None

    entry = drift_history.get(product_id, {}).get(dim_name)
    if entry is None:
        return None

    deadline_dt = datetime.fromisoformat(entry["deadline"])
    if deadline_dt.tzinfo is None:
        deadline_dt = deadline_dt.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    status = "overdue" if now > deadline_dt else "remediating"

    return DriftState(
        status=status,
        first_seen_at=entry["first_seen_at"],
        deadline=entry["deadline"],
    )


def update_drift_history(
    product_id: str,
    dim_name: str,
    current_medal: Medal,
    target_medal: Medal,
    drift_history: dict,
    now: datetime,
) -> None:
    """
    Mutates drift_history in place.

    - Compliant (current ≥ target): clears any existing entry
    - Drifting, no entry: records first_seen_at + computes deadline
    - Drifting, entry exists: leaves untouched (original clock preserved)
    - Bronze target: never records drift (bronze is the minimum floor)
    """
    product_history = drift_history.setdefault(product_id, {})

    if MEDAL_RANK[current_medal] >= MEDAL_RANK[target_medal]:
        # Compliant — clear drift entry
        product_history.pop(dim_name, None)
        if not product_history:
            drift_history.pop(product_id, None)
        return

    if target_medal not in _REMEDIATION_MONTHS:
        # Bronze target has no remediation window
        # Clean up empty product dict if we created one via setdefault
        if not product_history:
            drift_history.pop(product_id, None)
        return

    if dim_name not in product_history:
        # First time seeing this drift — start the clock
        months = _REMEDIATION_MONTHS[target_medal]
        deadline = now + relativedelta(months=months)
        product_history[dim_name] = {
            "first_seen_at": now.isoformat(),
            "deadline": deadline.isoformat(),
        }
    # If entry already exists, leave it untouched (clock keeps running)
