from engine.badges import badge_state, generate_badge

_GOLD_PRODUCT = {
    "id": "matrix",
    "current_medal": "gold",
    "dimensions": {
        "test_verification": {"drift": None},
        "documentation": {"drift": None},
    },
}

_BRONZE_REMEDIATING = {
    "id": "indico",
    "current_medal": "bronze",
    "dimensions": {
        "test_verification": {"drift": None},
        "documentation": {
            "drift": {"status": "remediating", "first_seen_at": "...", "deadline": "..."}
        },
    },
}

_BRONZE_OVERDUE = {
    "id": "indico",
    "current_medal": "bronze",
    "dimensions": {
        "test_verification": {
            "drift": {"status": "overdue", "first_seen_at": "...", "deadline": "..."}
        },
        "documentation": {"drift": None},
    },
}


def test_badge_state_gold_when_no_drift():
    assert badge_state(_GOLD_PRODUCT) == "gold"


def test_badge_state_bronze_when_no_drift():
    product = {**_GOLD_PRODUCT, "current_medal": "bronze"}
    assert badge_state(product) == "bronze"


def test_badge_state_remediating_when_any_dimension_remediating():
    assert badge_state(_BRONZE_REMEDIATING) == "remediating"


def test_badge_state_overdue_when_any_dimension_overdue():
    assert badge_state(_BRONZE_OVERDUE) == "overdue"


def test_overdue_takes_priority_over_remediating():
    product = {
        "id": "test",
        "current_medal": "bronze",
        "dimensions": {
            "a": {"drift": {"status": "remediating", "first_seen_at": "...", "deadline": "..."}},
            "b": {"drift": {"status": "overdue", "first_seen_at": "...", "deadline": "..."}},
        },
    }
    assert badge_state(product) == "overdue"


def test_generate_badge_returns_svg_string():
    svg = generate_badge(_GOLD_PRODUCT)
    assert svg.strip().startswith("<svg")
    assert "quality" in svg
    assert "gold" in svg
    assert "#FFB700" in svg


def test_generate_badge_remediating_uses_orange():
    svg = generate_badge(_BRONZE_REMEDIATING)
    assert "remediating" in svg
    assert "#E98B06" in svg


def test_generate_badge_overdue_uses_red():
    svg = generate_badge(_BRONZE_OVERDUE)
    assert "overdue" in svg
    assert "#E05252" in svg
