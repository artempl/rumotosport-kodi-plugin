# RuMotoSport Kodi Plugin

Kodi video addon for browsing and streaming MotoGP race recordings from [RuMotoSport](https://rumotosport.ru/).

## Features

- Browse seasons by year
- Filter by championship (MotoGP, Moto2, Moto3, Дополнительно)
- Navigate race weekends and individual sessions (FP1, Qualifying, Race, Warmup, etc.)
- Stream via HLS directly in Kodi
- Zero external dependencies — uses only Python stdlib

## Navigation

```
Years
└── Championships
    └── Events / Race Weekends
        └── Sessions
            └── Play HLS stream
```

## Installation

### Via repository (recommended — auto-updates)

Each [release](https://gitlab.com/artempl/rumotosport-kodi-plugin/-/releases) includes two files:

| File | Purpose |
|---|---|
| `repository.rmskodi.zip` | Repository addon — install this first |
| `plugin.video.rmskodi.zip` | Plugin itself — for manual install |

**Setup:**

1. In Kodi: **Settings → System → Add-ons** → enable **Unknown sources**
2. Download `repository.rmskodi.zip` from the [Releases page](https://gitlab.com/artempl/rumotosport-kodi-plugin/-/releases)
3. **Settings → Add-ons → Install from zip file** → select `repository.rmskodi.zip`
4. **Install from repository → RuMotoSport Repository → Video add-ons → RuMotoSport Kodi → Install**

The plugin will update automatically when new versions are released.

### Direct ZIP (no auto-updates)

Download `plugin.video.rmskodi.zip` from the [Releases page](https://gitlab.com/artempl/rumotosport-kodi-plugin/-/releases) and install via **Add-ons → Install from zip file**.

## Development

Requires Python 3.x and Kodi 21 (Omega). See [AGENTS.md](AGENTS.md) for full development workflow, headless testing, and API reference.

## Source

https://rumotosport.ru/
