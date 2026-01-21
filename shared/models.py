from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class Variant:
    name: str
    value: bool
    weight: int  # percentage, must sum to 100 within a rule


@dataclass(frozen=True)
class TargetingRule:
    attribute: str          # e.g. "country"
    operator: str           # e.g. "equals"
    value: str              # e.g. "US"
    variants: List[Variant]


@dataclass(frozen=True)
class FlagVersion:
    flag_key: str
    version: int
    enabled: bool
    rules: List[TargetingRule]
    default_variant: Variant
    created_at: str
