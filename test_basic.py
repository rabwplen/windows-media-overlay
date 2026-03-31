import pytest
import anyio
from types import SimpleNamespace

import media_info


@pytest.mark.anyio
async def test_get_media_info_with_mocked_session(monkeypatch):
    class DummyReader:
        async def load_async(self, size):
            return size

        def read_bytes(self, data):
            pass

    class DummyThumbnail:
        async def open_read_async(self):
            return SimpleNamespace(size=0)

    class DummyMediaProperties:
        title = "Test Song"
        artist = "Test Artist"
        album_title = "Test Album"
        album_artist = "Test Album Artist"
        thumbnail = None

    class DummyPlaybackInfo:
        playback_status = 4

    class DummyTimeline:
        position = SimpleNamespace(total_seconds=lambda: 42)
        end_time = SimpleNamespace(total_seconds=lambda: 180)
        last_updated_time = None

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

    assert data["title"] == "Test Song"
    assert data["artist"] == "Test Artist"
    assert data["album"] == "Test Album"