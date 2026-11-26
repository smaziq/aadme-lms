from typing import Any, Protocol


class LiveSessionProvider(Protocol):
    """B1 seam: Zoom-first adapter will implement this; Meet can follow."""

    def create_session(
        self, *, title: str, starts_at: str, metadata: dict[str, Any]
    ) -> dict[str, Any]:
        ...

    def fetch_attendance(self, *, provider_session_id: str) -> list[dict[str, Any]]:
        ...


class NotConfiguredLiveSessionProvider:
    """A1 placeholder — raises until B1 wires Zoom."""

    def create_session(
        self, *, title: str, starts_at: str, metadata: dict[str, Any]
    ) -> dict[str, Any]:
        raise NotImplementedError("Live sessions ship in B1 (Zoom first)")

    def fetch_attendance(self, *, provider_session_id: str) -> list[dict[str, Any]]:
        raise NotImplementedError("Live sessions ship in B1 (Zoom first)")