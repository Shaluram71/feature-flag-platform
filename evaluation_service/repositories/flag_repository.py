from abc import ABC, abstractmethod

from shared.models import FlagVersion, Variant, TargetingRule

class FlagRepository(ABC):
    @abstractmethod
    def get(self, flag_key: str) -> FlagVersion | None:
        """
        Return the current FlagVersion for the given key,
        or None if the flag does not exist.
        """
        raise NotImplementedError

class InMemoryFlagRepository(FlagRepository):
    def __init__(self):
        self._flags: dict[str, FlagVersion] = {
            "new_checkout": FlagVersion(
                flag_key="new_checkout",
                version=1,
                enabled=True,
                rules=[
                    TargetingRule(
                        attribute="country",
                        operator="equals",
                        value="US",
                        variants=[
                            Variant(name="on", value=True, weight=50),
                            Variant(name="off", value=False, weight=50),
                        ],
                    )
                ],
                default_variant=Variant(
                    name="off", value=False, weight=100
                ),
                created_at="2026-01-21T00:36:00Z",
            )
        }

    def get(self, flag_key: str) -> FlagVersion | None:
        return self._flags.get(flag_key)
