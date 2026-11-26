import pytest

from providers.live_session import LiveSessionProvider, NotConfiguredLiveSessionProvider


def test_protocol_importable():
    assert LiveSessionProvider is not None


def test_placeholder_raises():
    p = NotConfiguredLiveSessionProvider()
    with pytest.raises(NotImplementedError):
        p.create_session(title="Class", starts_at="2027-01-01T10:00:00+05:30", metadata={})