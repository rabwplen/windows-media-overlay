import pytest
import anyio
from types import SimpleNamespace
from datetime import datetime, timezone, timedelta

import media_info


@pytest.mark.anyio
async def test_get_media_info_with_mocked_session(monkeypatch):

    class DummyMediaProperties:
        title = "Test Song"
        artist = "Test Artist"
        album_title = "Test Album"
        album_artist = "Test Album Artist"
        thumbnail = None

    class DummyPlaybackInfo:
        playback_status = 4  # playing

    class DummyTimeline:
        position = timedelta(seconds=42)
        end_time = timedelta(seconds=180)
        last_updated_time = datetime.now(timezone.utc) - timedelta(seconds=2)

    class DummySession:
        async def try_get_media_properties_async(self):
            return DummyMediaProperties()

        def get_timeline_properties(self):
            return DummyTimeline()

        def get_playback_info(self):
            return DummyPlaybackInfo()

    class DummySessions:
        def get_current_session(self):
            return DummySession()

    async def fake_request_async():
        return DummySessions()

    monkeypatch.setattr(
        media_info.GlobalSystemMediaTransportControlsSessionManager,
        "request_async",
        fake_request_async,
    )

    data = await media_info.get_media_info()

    assert data is not None
    assert data["title"] == "Test Song"
    assert data["artist"] == "Test Artist"
    assert data["album"] == "Test Album"