
# 🌌 Jedi System Watcher

> "Feel the Force of your CPU."

A sci-fi desktop overlay built with Python + PyQt6.
The widget floats above other windows and reacts to system load in real time.

## Modes

| Mode | Trigger | Visual | Sound |
|------|---------|--------|-------|
| 🟢 Jedi Idle | CPU < 70% | `jedi_idle.gif` (calm green aura) | `calm.wav` (deep hum) |
| 🟠 Warrior Alert | 70% ≤ CPU < 90% | `warrior_alert.gif` (orange pulse) | `alert.wav` (sci-fi ping) |
| 🔴 Dark Lord Critical | CPU ≥ 90% | `darklord_critical.gif` (red violent energy) | `dark.wav` (low ominous pulse) |

## How to run

1. Create venv (done already).
2. Install deps:

```powershell
pip install PyQt6 psutil pygame requests pillow numpy
````

3. Generate assets (GIFs / sounds / icon):

```powershell
python generate_assets.py
```

4. Launch the watcher:

```powershell
python main.py
```

## Tech stack

* PyQt6 for UI
* psutil for system stats
* pygame.mixer for audio playback
* Pillow for procedural animated GIF generation
* pure Python audio synthesis (wave module)

## License for assets

All generated assets are original procedural graphics/sound.
You own them. CC0-style: do whatever you want.
