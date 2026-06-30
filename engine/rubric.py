import operator as op_module
import re
from typing import Any


_OPS: dict[str, Any] = {
    ">=": op_module.ge,
    "<=": op_module.le,
    ">": op_module.gt,
    "<": op_module.lt,
    "==": op_module.eq,
    "!=": op_module.ne,
}

# Matches: <word> <operator> <value>
# Operators checked longest-first to avoid ">" matching ">="
_CONDITION_RE = re.compile(r"^(\w+)\s*(>=|<=|!=|>|<|==)\s*(.+)$")


def eval_condition(metrics: dict[str, Any], condition: str) -> bool:
    """
    Evaluate a single condition string against a metrics dict.

    Condition format: `<metric_key> <operator> <value>`
    Example: "coverage_pct >= 90", "latest_build_passing == true"

    Returns False (not raises) when the metric key is absent — missing
    data is treated as failing the condition conservatively.
    Raises ValueError for unparseable condition syntax.
    """
    match = _CONDITION_RE.match(condition.strip())
    if not match:
        raise ValueError(f"Invalid condition syntax: {condition!r}")

    key, op_str, raw_value = match.groups()
    raw_value = raw_value.strip()

    left = metrics.get(key)
    if left is None:
        return False

    # Parse right-hand side to a Python value
    if raw_value.lower() == "true":
        right: Any = True
    elif raw_value.lower() == "false":
        right = False
    else:
        try:
            # Parse as number; preserve int vs float based on left
            right = float(raw_value)
            if isinstance(left, int) and not isinstance(left, bool):
                right = int(right)
        except ValueError:
            right = raw_value

    return _OPS[op_str](left, right)
