
# 🌌 Jedi System Watcher

> *"Your system resources… they surround you. They bind the galaxy — and your CPU cores — together."*

A real-time sci-fi desktop HUD built with **Python + PyQt6**.
It floats over your screen, reacts to system load, plays Star-Wars-style sounds, and glows with the Force.

## 🎭 Modes of the Force

| Mode                      | CPU State | Visual                           | Sound               |
| ------------------------- | --------- | -------------------------------- | ------------------- |
| 🟢 **Jedi Focus**         | CPU < 70% | Calm green aura, meditative core | Peaceful energy hum |
| 🟠 **Battle Tension**     | 70–90%    | Orange pulse, warrior energy     | Alert ping          |
| 🔴 **Dark Side Overload** | > 90%     | Violent red aura, chaos          | Ominous power surge |

The widget **breathes with your system load**, neon-glows, and shifts theme between **Light Side ↔ Dark Side** with one click.

## 🛠 Requirements

```bash
Python 3.10+
Windows 10/11 (transparent window optimized)
```

## 📦 Install

```bash
pip install PyQt6 psutil pygame GPUtil
```

> `requests`, `Pillow`, `numpy` only needed if you regenerate assets.

## 🚀 Run

```bash
python main.py
```

## 🎧 Assets

All hologram GIFs + sound effects are **procedurally generated** (CC0).
You can replace them with actual Star Wars assets — your project, your destiny. ✨

Directories:

```
assets/
  jedi_idle.gif
  warrior_alert.gif
  darklord_critical.gif
  calm.wav
  alert.wav
  dark.wav
  icon.png
```

---

## 🧠 Tech behind the Force

| Feature                  | Library                                  |
| ------------------------ | ---------------------------------------- |
| UI                       | PyQt6                                    |
| System stats             | psutil                                   |
| GPU detection            | GPUtil / NVIDIA NVML                     |
| Audio                    | pygame.mixer                             |
| Glow, transparency, neon | Qt effects / frameless transparent layer |

> No external images. No copyrighted content.
> Everything is legally clean. Yes, you can share it. ✅

---

## 📜 License

Source code: MIT
Generated assets: **CC0** — yours to keep, modify, share.
