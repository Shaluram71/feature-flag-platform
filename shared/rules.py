from typing import Dict, List

from shared.models import FlagVersion, TargetingRule, Variant


def _rule_matches(rule: TargetingRule, user_attributes: Dict[str, str]) -> bool:
    """
    Returns True if the given targeting rule matches the user attributes.

    Supported operators:
    - equals
    """
    user_value = user_attributes.get(rule.attribute)

    if user_value is None:
        return False

    if rule.operator == "equals":
        return user_value == rule.value

    raise ValueError(f"Unsupported operator: {rule.operator}")


def _select_variant(variants: List[Variant], bucket: float) -> Variant:
    """
    Selects a variant based on the user's bucket.

    Invariant:
    - Variant weights must sum to exactly 100.
    - bucket is in [0, 100).
    """
    total_weight = sum(v.weight for v in variants)
    if total_weight != 100:
        raise ValueError(
            f"Variant weights must sum to 100, got {total_weight}"
        )

    cumulative = 0.0
    for variant in variants:
        cumulative += variant.weight
        if bucket < cumulative:
            return variant

    # Defensive fallback — should be unreachable if invariants hold
    raise RuntimeError("Failed to select variant for bucket")


def evaluate_flag(
    flag_version: FlagVersion,
    user_attributes: Dict[str, str],
    bucket: float,
) -> Variant:
    """
    Evaluates a feature flag for a user and returns the selected variant.

    Evaluation order:
    1. If flag disabled -> default variant
    2. First matching rule wins
    3. If no rules match -> default variant
    """
    if not flag_version.enabled:
        return flag_version.default_variant

    for rule in flag_version.rules:
        if _rule_matches(rule, user_attributes):
            return _select_variant(rule.variants, bucket)

    return flag_version.default_variant
