# Media Overlay for Windows

A lightweight desktop overlay for Windows that shows the currently playing media
using the Windows Media Session API.

This project creates a small, always-on-top overlay that shows what you're currently listening to.

Built with Python and CustomTkinter.

## Features

- Displays track title and artist
- Shows album title and album artist
- Shows cover art when available
- Displays playback position and duration
- Always-on-top overlay window
- Draggable window
- Fade in / fade out on hover

## Requirements

- Windows 10 / 11
- Python 3.10 or newer
- Dependencies from `requirements.txt`

## Installation

```bash
git clone https://github.com/rabwplen/windows-media-overlay
cd windows-media-overlay
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## How it works

This project reads media data from Windows Media Session via WinRT.
It does not depend on Spotify Web API.

## Project structure

```text
.
├── assets/             # icons and UI images
├── main.py             # overlay window and app entry point
├── media_info.py       # media session data reader
├── settings.py         # settings window
├── requirements.txt
├── test_basic.py
```

## Notes

Some metadata may be unavailable depending on the player.
Cover art availability also depends on the active media app.

The project is Windows-only because it relies on WinRT media session APIs.

## Limitations

- Metadata depends on the active media application
- Some players may not provide full information
- Cover art is not always available

## Future improvements

- Improve UI performance (reduce unnecessary redraws)
- Cache album covers locally
- Add playback state indicators (playing / paused / closed)
- Improve metadata consistency across apps
- Custom themes and UI configuration
- Possible rewrite using C# WinUI (separate project)

## License
MIT License