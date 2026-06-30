from dataclasses import dataclass
from enum import StrEnum


class Medal(StrEnum):
    UNRATED = "unrated"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


MEDAL_RANK: dict[Medal, int] = {
    Medal.UNRATED: 0,
    Medal.BRONZE: 1,
    Medal.SILVER: 2,
    Medal.GOLD: 3,
}


@dataclass
class DriftState:
    status: str  # "remediating" | "overdue"
    first_seen_at: str  # ISO 8601 with UTC timezone
    deadline: str  # ISO 8601 with UTC timezone


@dataclass
class DimensionResult:
    medal: Medal
    target: Medal
    metrics: dict
    drift: DriftState | None


@dataclass
class ProductResult:
    product_id: str
    current_medal: Medal
    target_medal: Medal
    dimensions: dict[str, DimensionResult]
