from shared.models import Variant, TargetingRule, FlagVersion
from shared.rules import evaluate_flag
from shared.hashing import compute_bucket

def make_test_flag():
    return FlagVersion(
        flag_key="test_flag",
        version=1,
        enabled=True,
        rules=[
            TargetingRule(
                attribute="country",
                operator="equals",
                value="US",
                variants=[
                    Variant(name="on", value=True, weight=30),
                    Variant(name="off", value=False, weight=70),
                ],
            )
        ],
        default_variant=Variant(name="off", value=False, weight=100),
        created_at="2026-01-21T00:36:00Z",
    )

def test_deterministic_evaluation():
    flag = make_test_flag()

    user_id = "user_123"
    attrs = {"country": "US"}

    bucket1 = compute_bucket(flag.flag_key, user_id)
    bucket2 = compute_bucket(flag.flag_key, user_id)

    assert bucket1 == bucket2

    variant1 = evaluate_flag(flag, attrs, bucket1)
    variant2 = evaluate_flag(flag, attrs, bucket2)

    assert variant1 == variant2

def test_variant_weight_mapping():
    flag = make_test_flag()
    attrs = {"country": "US"}

    # Buckets that should land in each range
    on_bucket = 10.0    # ∈ [0, 30)
    off_bucket = 90.0   # ∈ [30, 100)

    on_variant = evaluate_flag(flag, attrs, on_bucket)
    off_variant = evaluate_flag(flag, attrs, off_bucket)

    assert on_variant.name == "on"
    assert off_variant.name == "off"

def test_default_variant_when_rule_does_not_match():
    flag = make_test_flag()

    attrs = {"country": "CA"}  # does not match rule
    bucket = 10.0

    variant = evaluate_flag(flag, attrs, bucket)

    assert variant.name == "off"
    assert variant.value is False

def test_flag_disabled_returns_default():
    flag = make_test_flag()
    flag = FlagVersion(
        **{**flag.__dict__, "enabled": False}
    )

    attrs = {"country": "US"}
    bucket = 10.0

    variant = evaluate_flag(flag, attrs, bucket)

    assert variant.name == "off"
