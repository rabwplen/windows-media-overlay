import asyncio
from io import BytesIO

from PIL import Image

from datetime import datetime, timezone

try:
    from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager
    from winrt.windows.storage.streams import DataReader
    WINRT_AVAILABLE = True
except ImportError:
    WINRT_AVAILABLE = False

def format_time(timespan):
    total_seconds = int(timespan.total_seconds())
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02}"

async def get_media_info():
    if not WINRT_AVAILABLE:
        print("winrt modules not available. media info functionality will be disabled.")
        return None
    
    sessions = await GlobalSystemMediaTransportControlsSessionManager.request_async()
    session = sessions.get_current_session()

    # if theres no active media session, return None
    if not session:
        return None

    # get media properties and timeline properties
    info = await session.try_get_media_properties_async()
    timeline = session.get_timeline_properties()
    actual_position = timeline.position
    
    if session.get_playback_info().playback_status == 4: # check if track is playing (4 - playing, 3 or 5 - paused)
        # calculate the time that has passed since the last update and add it to the position
        time_diff = datetime.now(timezone.utc) - timeline.last_updated_time
        actual_position += time_diff
    
    if actual_position > timeline.end_time: # set limit for position so it does not go beyond the track
        actual_position = timeline.end_time

    # get track cover if available
    cover_image = None
    if info.thumbnail:
        stream = await info.thumbnail.open_read_async()
        reader = DataReader(stream)
        await reader.load_async(stream.size)

        data = bytearray(stream.size)
        reader.read_bytes(data)

        cover_image = Image.open(BytesIO(data)).convert("RGBA")

    return {
        "title": info.title or "-",
        "artist": info.artist or "-",
        "album": info.album_title or "-",
        "position": format_time(actual_position) or "0:00 -",
        "duration": format_time(timeline.end_time) or "0:00 -",
        "freezed position": format_time(timeline.position) or "0:00 -",
        "last updated": timeline.last_updated_time.isoformat() if timeline.last_updated_time else "-",
        "playback_status": session.get_playback_info().playback_status,
        "cover_image": cover_image,
    }

def load_media_info(app, callback_func):
    try:
        # run the async function in the event loop and get the result
        data = asyncio.run(get_media_info())
        
        if data:
            print(" - - - Current Media - - - ")
            for key, value in data.items():
                if key != "cover_image":
                    print(f"{key}: {value}")
        
        app.after(0, callback_func, data)
    except Exception as e:
        print(f"Error loading media: {e}")
        app.after(0, callback_func, None)
    

def print_media_info():
    data = asyncio.run(get_media_info())

    if not data:
        print("No active media session (main)")
        return

    print(" - - - Current Media - - - ")
    for key, value in data.items():
        print(f"{key}: {value}")