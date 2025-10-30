import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import wave, struct

ASSETS_DIR = "assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

def plasma_frame(size, base_color, phase, intensity=0.8):
    """генерира кадър от енергийна плазма"""
    w, h = size
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    cx, cy = w / 2, h / 2

    for y in range(h):
        for x in range(w):
            dx, dy = x - cx, y - cy
            dist = math.sqrt(dx*dx + dy*dy)
            angle = math.atan2(dy, dx)
            v = math.sin(dist * 0.05 - phase*3) + math.cos(angle*3 + phase*2)
            glow = (1 - min(dist / (w/2), 1))**2
            pulse = (math.sin(phase*6) + 1) / 2
            intensity_val = (v * 0.3 + 0.7) * glow * (0.5 + 0.5*pulse)
            r = int(base_color[0] * intensity_val * intensity)
            g = int(base_color[1] * intensity_val * intensity)
            b = int(base_color[2] * intensity_val * intensity)
            arr[y, x] = (r, g, b)
    img = Image.fromarray(arr, "RGB")
    img = img.filter(ImageFilter.GaussianBlur(radius=3))
    return img

def generate_gif(filename, base_color):
    frames = []
    for i in range(24):
        phase = i / 24.0 * 2 * math.pi
        frame = plasma_frame((300, 300), base_color, phase)
        frames.append(frame)
    frames[0].save(
        filename,
        save_all=True,
        append_images=frames[1:],
        duration=80,
        loop=0,
        optimize=False,
        disposal=2
    )
    print(f"[✓] {filename} готов.")

def make_tone_wav(path, freq_main, seconds, volume=0.4, dark=False):
    rate = 44100
    data = []
    for n in range(int(rate * seconds)):
        t = n / rate
        val = math.sin(2 * math.pi * freq_main * t)
        if dark:
            val += 0.4 * math.sin(2 * math.pi * (freq_main/2) * t)
        env = 0.5 * (1 - math.cos(2 * math.pi * t / seconds))
        sample = val * volume * env
        data.append(int(max(-1, min(1, sample)) * 32767))
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(b"".join(struct.pack("<h", s) for s in data))
    print(f"[✓] {path} готов.")

def generate_icon():
    size = 256
    img = Image.new("RGBA", (size, size), (0,0,0,0))
    d = ImageDraw.Draw(img)
    for r in range(100, 120):
        alpha = 255 - (r - 100) * 12
        d.ellipse((128-r,128-r,128+r,128+r), outline=(0,255,180,alpha), width=3)
    d.ellipse((116,116,140,140), fill=(0,255,180,180))
    img.save(os.path.join(ASSETS_DIR, "icon.png"))
    print("[✓] icon.png готов.")

def main():
    print("[*] Генерирам sci-fi енергийни ефекти...")

    generate_gif(os.path.join(ASSETS_DIR, "jedi_idle.gif"), (0, 255, 100))
    generate_gif(os.path.join(ASSETS_DIR, "warrior_alert.gif"), (255, 180, 0))
    generate_gif(os.path.join(ASSETS_DIR, "darklord_critical.gif"), (255, 40, 40))

    print("[*] Генерирам звуци...")
    make_tone_wav(os.path.join(ASSETS_DIR, "calm.wav"), 130, 2.5, 0.4)
    make_tone_wav(os.path.join(ASSETS_DIR, "alert.wav"), 600, 1.0, 0.5)
    make_tone_wav(os.path.join(ASSETS_DIR, "dark.wav"), 60, 2.0, 0.5, dark=True)

    generate_icon()

    print("\n[✅] Всички assets са готови в ./assets/ !")

if __name__ == "__main__":
    main()
