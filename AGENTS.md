# AGENTS.md — rms-kodi

## Project Overview

Kodi video plugin for browsing and playing MotoGP 2026 race recordings from `https://cloud.strea.ru/2026/motogp`. Development environment: Fedora toolbx.

## Plugin File Structure

```
plugin.video.rmskodi/
├── addon.xml              # Metadata, dependencies, entry point ← CREATED
├── main.py                # Plugin entry point ← CREATED
├── icon.png               # Plugin icon (256x256) ← CREATED (placeholder)
├── fanart.jpg             # Plugin fanart (1280x720) ← CREATED (placeholder)
├── resources/
│   ├── language/
│   │   └── resource.language.en_gb/
│   │       └── strings.po  # Localized strings (optional)
│   └── settings.xml        # User-configurable settings ← CREATED
└── lib/                    # Third-party libraries (empty, not needed yet)
```

## Navigation Structure

```
Years
└── Championships (MotoGP, Moto2, Moto3, Дополнительно)
    └── Events / Race Weekends
        └── Sessions (FP1, Qualifying, Race, Warmup, Press, ...)
            └── Play HLS stream
```

## Discovered API

Base: `https://cloud.strea.ru/api/v1`

| Endpoint | Returns |
|---|---|
| `GET /events/years` | `{"data": [2025, 2026, ...]}` |
| `GET /events/championships` | `{"data": [{"id": 1, "name": "MotoGP", "code": "motogp", "colors": {...}}, ...]}` |
| `GET /events?year=&championship=&archive=1` | `{"data": [{slug, title, round, ...}]}` |
| `GET /events/{slug}` | Single event details |
| `GET /events/{slug}/videos` | `{"data": [{className, files: [{prefix, label, hasHls, hlsUrl, qualities}]}]}` |

### Video Response Structure

```json
{
  "data": [{
    "className": "MotoGP",
    "files": [{
      "prefix": "m",
      "label": "Гонка",
      "hasHls": true,
      "hlsUrl": "https://s1.strea.ru/files-hls/2026/MotoGP/R01/m/master.m3u8",
      "qualities": [
        {"quality": "1080", "downloadUrl": "/storage/files/2026/MotoGP/R01/m_1080.mp4"}
      ]
    }]
  }]
}
```

## Plugin Router (`main.py`)

| `action` param | Params | View |
|---|---|---|
| `years` (default) | — | Season list |
| `championships` | `year` | Championship list |
| `events` | `year`, `championship` | Race weekends |
| `sessions` | `slug` | Session recordings |
| `play` | `slug`, `prefix` | Plays HLS video |

Currently uses `urllib.request` (stdlib only — no external deps). Playback via `xbmcplugin.setResolvedUrl()` with HLS `.m3u8` URL.

## Critical Kodi Python API Facts

- **Entry point**: `main.py` (declared in addon.xml `library` attribute)
- **Plugin URL**: `sys.argv[0]` = `plugin://plugin.video.rmskodi/`
- **Handle**: `int(sys.argv[1])` — must pass to all `xbmcplugin.*` calls
- **Params**: `sys.argv[2]` — query string after `?` (e.g., `?action=play&url=xxx`)
- **Routing**: Parse `sys.argv[2]` with `urllib.parse.parse_qsl()`, dispatch to functions
- **Listings**: `xbmcplugin.addDirectoryItem()` + `endOfDirectory()`
- **Playback**: Set `list_item.setProperty('IsPlayable', 'true')`, then `xbmcplugin.setResolvedUrl()`
- **Content type**: `xbmcplugin.setContent(HANDLE, 'videos')` — enables appropriate skin views

## Fedora Toolbx Setup

Kodi is NOT in default Fedora repos. Enable RPM Fusion first:

```bash
# Enable RPM Fusion (required for Kodi on Fedora)
sudo dnf install \
  https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm \
  https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm

# Install Kodi
sudo dnf install kodi

# Install Python dev tools (for IDE autocompletion with Kodistubs)
pip install kodistubs
```

## Headless Testing

Kodi headless container for testing without display (Fedora toolbx has podman natively — use `podman-remote` or `podman` instead of `docker`):

```bash
# Run headless Kodi (Omega = Kodi 21)
# Use podman-remote if podman machine is configured, otherwise plain podman
podman run -d \
  --name kodi-headless \
  -v $(pwd)/plugin.video.rmskodi:/config/.kodi/addons/plugin.video.rmskodi \
  -p 8080:8080 \
  -p 9090:9090 \
  docker.io/matthuisman/kodi-headless:Omega

# Access web UI: http://localhost:8080
# Install addon via: podman exec kodi-headless install_addon "plugin.video.rmskodi"
```

Alternatively, run Kodi directly in toolbx with Xvfb:

```bash
# In Fedora toolbx
sudo dnf install xorg-x11-server-Xvfb
Xvfb :99 -screen 0 1280x720x24 &
DISPLAY=:99 kodi
```

## Packaging for Installation

```bash
# From project root (parent of plugin.video.rmskodi/)
zip -r plugin.video.rmskodi.zip plugin.video.rmskodi/
# Install in Kodi: Add-ons → Install from zip file → select the .zip
```

**Important**: ZIP structure must be `plugin.video.rmskodi/addon.xml`, NOT nested deeper.

## Development Workflow

1. Edit `main.py` and other files
2. Package: `zip -r plugin.video.rmskodi.zip plugin.video.rmskodi/`
3. Test in headless Kodi container or toolbx with Xvfb
4. Kodi logs: `~/.kodi/temp/kodi.log` or `podman logs kodi-headless`

## Reference

- Example plugin: https://github.com/romanvm/plugin.video.example
- Kodi Python API docs: https://xbmc.github.io/docs.kodi.tv/master/kodi-dev-kit/group__python.html
- Kodi addon.xml spec: https://kodi.wiki/view/Addon.xml
