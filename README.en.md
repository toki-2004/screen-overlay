[中文](README.md) | English

# Screen Sticker / Crosshair (screen-overlay)

Pin an image on screen, or use the built-in crosshair: a frameless, fully
transparent, always-on-top little window that snaps to the four screen corners
or the center, with optional click-through. The overlay approach follows
[desktop-pet-ai](https://github.com/toki-2004/desktop-pet-ai).

## Features

- Load PNG / JPG / BMP / WebP stickers, drawn at the original aspect ratio
- Built-in crosshair: red / green / cyan / white, with a center gap and dot
- Placement: top-left / top-right / bottom-left / bottom-right (adjustable
  margin), plus screen center
- Always-on-top, click-through, opacity 100/85/70/55/40%
- Settings are saved to `overlay_config.json` next to the script or exe

## Run

Option 1: portable exe. Download `screen-overlay-v1.0.1-win64.zip` from
[Releases](../../releases), unzip and run `screen-overlay.exe`. Keep the whole
folder — the dependencies sit next to the exe, and `overlay_config.json` is
written there too.

Option 2: from source, requires Python 3 + PyQt5:

```
pip install PyQt5
python overlay.py              # crosshair by default
python overlay.py sticker.png  # open an image directly
```

## Controls

| Action | Effect |
| --- | --- |
| Left drag | Move the sticker (switches to free position) |
| Wheel | Zoom in / out |
| Right click | Menu: load image, crosshair, corner, margin, color, opacity, top, click-through, quit |
| Tray icon click | Show / hide the window |

- Corners and center are computed from the full geometry of the screen the window
  currently sits on, taskbar area included: center means the real screen center
  and corners mean the real screen corners, so the taskbar never shifts them.
  Being always-on-top, the window is drawn over the taskbar when placed low.
  On multi-monitor setups, drag the window to the target screen first.
- With click-through enabled the window ignores the mouse; use the tray menu.
- As an in-game crosshair, the game must run in borderless/windowed mode;
  exclusive fullscreen covers the overlay.

## Self-check

```
python test_overlay.py
```

## Known limits

- Windows only (click-through uses Windows extended styles)
- GIF shows the first frame only, no animation

## Version

- v1.0.2 placement now uses the full screen geometry (taskbar included), so the
  taskbar no longer shifts centering / corner snapping
- v1.0.1 packaging only: dropped unused Qt components (software OpenGL / ANGLE /
  Qml / Quick / non-Chinese translations), unpacked size 96.7MB -> 45.2MB, no
  functional change from v1.0.0
- v1.0.0 first release: sticker / crosshair, five placements, always-on-top and
  click-through, tray menu

## Related

- [desktop-pet-ai](https://github.com/toki-2004/desktop-pet-ai) — desktop pet;
  this project reuses its transparent always-on-top overlay approach
