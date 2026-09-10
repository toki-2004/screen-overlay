[中文](README.md) | English

# Screen Sticker / Crosshair (screen-overlay)

Overlay a sticker or a crosshair on screen. The window is frameless, fully
transparent and always on top, it snaps to the four screen corners or the screen
center, and it can pass mouse events through to the window below. The overlay
approach follows [desktop-pet-ai](https://github.com/toki-2004/desktop-pet-ai).

## Features

- Load PNG / JPG / BMP / WebP stickers and display them at their original aspect
  ratio
- One-click reset to native size (1:1 — a 4x4 image covers 4x4 screen pixels)
- Built-in crosshair: red / green / cyan / white, with a center gap and dot
- Placement: top-left / top-right / bottom-left / bottom-right snapping
  (adjustable margin) and screen center
- Always-on-top, click-through, opacity 100 / 85 / 70 / 55 / 40%
- Show / hide can be bound to a customizable global hotkey (default Ctrl+Alt+H;
  leave it empty to disable)
- The loaded image and every setting are saved on exit and restored on the next
  launch; `overlay_config.json` sits in the same directory as the script or
  executable

## Run

Option 1: portable package. Download `screen-overlay-v1.0.5-win64.zip` from the
[Releases](../../releases) page and run `screen-overlay.exe`. All dependencies
sit in the same directory as the executable and must be kept together; the
license file and the configuration file are located there as well. Keeping the
whole directory in a fixed location is recommended.

Option 2: run from source. Python 3 and PyQt5 are required:

```
pip install PyQt5
python overlay.py              # crosshair by default
python overlay.py sticker.png  # open the given image
```

## Controls

| Control | Effect |
| --- | --- |
| Left drag | Move the sticker; the placement mode becomes free |
| Wheel | Zoom in / out |
| Right click | Menu: load image, built-in crosshair, corner, margin, zoom in / out, native size (1:1), crosshair color, opacity, always-on-top, click-through, show / hide, quit |
| Tray icon click | Show / hide the window |
| Global hotkey (default Ctrl+Alt+H) | Show / hide the window, also while it is unfocused |

- Snapping and centering are calculated from the full geometry of the screen the
  window currently sits on, taskbar area included: the center is the real screen
  center and the corners are the real screen corners, so the taskbar causes no
  offset. Because the window is always on top, it is drawn over the taskbar when
  placed near the bottom edge. On multi-monitor systems, drag the window to the
  target screen before choosing a placement.
- Once click-through is enabled the window no longer receives mouse events, so
  it can only be controlled from the tray icon menu.
- When used as an in-game crosshair, the game must run in borderless or windowed
  mode; exclusive fullscreen covers this window.
- The global hotkey can be changed under "设置显隐快捷键…" in the menu; clearing
  the input removes the hotkey. If registration is reported as failed, the
  combination is already taken by another program, so pick another one.
- The image path and all settings (margin, zoom, position, color, opacity,
  always-on-top, click-through, hotkey) are written to the configuration file on
  exit and restored on the next launch; deleting that file restores defaults.

## Self-check

```
python test_overlay.py
```

## Known limits

- Windows only (click-through uses Windows extended window styles)
- GIF shows the first frame only; no animation is played

## License

This project is licensed under the [PolyForm Noncommercial License 1.0.0](LICENSE):

- Noncommercial purposes are permitted, such as personal study, research,
  private entertainment and hobby projects
- Use by charitable organizations, educational institutions, public research
  organizations, public safety or health organizations, environmental protection
  organizations and government institutions is permitted
- **Any commercial use is prohibited**, including internal use at a
  for-profit company, distribution with a commercial product, and use in
  providing a commercial service
- For commercial licensing, please contact the author

This is not an OSI-approved open source license; it is a source-available
license. "No commercial use" conflicts with the Open Source Definition itself,
so no OSI-approved license can forbid commercial use.

## Version

- v1.0.5 added a customizable global show / hide hotkey and fixed the lost image
  path and settings: the image path was never stored, and quitting from the tray
  did not write the configuration file
- v1.0.4 adopted a noncommercial license (PolyForm Noncommercial 1.0.0); the
  full license text ships inside the release package
- v1.0.3 added "native size (1:1)": one click back to the image's real pixel size
- v1.0.2 placement now uses the full screen geometry (taskbar included), so the
  taskbar no longer shifts centering or corner snapping
- v1.0.1 packaging only: dropped unused Qt components (software OpenGL / ANGLE /
  Qml / Quick / non-Chinese translations), unpacked size 96.7MB -> 45.2MB, no
  functional change from v1.0.0
- v1.0.0 first release: sticker / crosshair, five placements, always-on-top and
  click-through, tray menu

## Related

- [desktop-pet-ai](https://github.com/toki-2004/desktop-pet-ai) — desktop pet;
  this project follows its transparent always-on-top overlay approach
