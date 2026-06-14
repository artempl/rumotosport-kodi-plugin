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

1. Package the addon:
   ```bash
   zip -r plugin.video.rmskodi.zip plugin.video.rmskodi/
   ```
2. In Kodi: **Add-ons** → **Install from zip file** → select `plugin.video.rmskodi.zip`

## Development

Requires Python 3.x and Kodi 21 (Omega). See [AGENTS.md](AGENTS.md) for full development workflow, headless testing, and API reference.

## Source

https://rumotosport.ru/
