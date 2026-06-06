"""Read-only Looker adapter contract for future live L1 enrichment."""

from __future__ import annotations

from typing import Protocol

from strata.l1.types import ContentReference, ExploreUsage, PDTBuild


class LookerUsageAdapter(Protocol):
    """Adapter interface; implementations must be read-only."""

    def explore_usage(self) -> list[ExploreUsage]:
        ...

    def content_references(self) -> list[ContentReference]:
        ...

    def pdt_builds(self) -> list[PDTBuild]:
        ...


class LiveLookerNotConfigured(RuntimeError):
    pass


class DisabledLookerAdapter:
    """Placeholder that makes live access opt-in rather than accidental."""

    def explore_usage(self) -> list[ExploreUsage]:
        raise LiveLookerNotConfigured("live Looker L1 access is not configured")

    def content_references(self) -> list[ContentReference]:
        raise LiveLookerNotConfigured("live Looker L1 access is not configured")

    def pdt_builds(self) -> list[PDTBuild]:
        raise LiveLookerNotConfigured("live Looker L1 access is not configured")
