import sys
import os
import psutil
from PyQt6.QtWidgets import (
    QApplication, QFrame, QLabel, QWidget, QVBoxLayout, QPushButton, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import QTimer, Qt, QSize, QPropertyAnimation
from PyQt6.QtGui import QMovie, QIcon, QColor
from pygame import mixer

# Optional GPU (NVIDIA) support
try:
    import pynvml
    NVML_AVAILABLE = True
    pynvml.nvmlInit()
except Exception:
    NVML_AVAILABLE = False

ASSETS_DIR = "assets"
IDLE_MAX = 70
ALERT_MAX = 90


class JediSystemWatcher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jedi System Watcher")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(80, 80, 360, 480)

        # Audio init
        mixer.init(frequency=22050, size=-16, channels=1)

        # --- Main layout ---
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # --- Energy Core Frame ---
        self.core_frame = QFrame()
        self.core_frame.setFixedSize(320, 360)
        self.core_frame.setStyleSheet("background-color: rgba(0,0,0,0); border-radius: 20px;")

        core_layout = QVBoxLayout()
        core_layout.setContentsMargins(0, 0, 0, 0)
        core_layout.setSpacing(0)

        # --- GIF Display ---
        self.gif_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.gif_label.setFixedSize(300, 300)
        core_layout.addWidget(self.gif_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- Overlay Info (text inside the core) ---
        self.overlay_label = QLabel("", alignment=Qt.AlignmentFlag.AlignCenter)
        self.overlay_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: bold;
            background-color: transparent;
            border: none;
        """)
        core_layout.addWidget(self.overlay_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.core_frame.setLayout(core_layout)
        layout.addWidget(self.core_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- Glow Effect (Force aura) ---
        shadow = QGraphicsDropShadowEffect()
        shadow.setOffset(0, 0)
        shadow.setBlurRadius(100)
        shadow.setColor(QColor(0, 255, 150, 200))
        self.core_frame.setGraphicsEffect(shadow)
        self.glow_effect = shadow

        # махаме рамката, за да няма двоен ръб
        self.core_frame.setStyleSheet("background-color: rgba(0,0,0,0); border: none; border-radius: 20px;")

        # --- Glow Animation (Force Breathing) ---
        from PyQt6.QtCore import QPropertyAnimation
        self.glow_anim = QPropertyAnimation(self.glow_effect, b"blurRadius")
        self.glow_anim.setDuration(3000)  # време за едно "вдишване"
        self.glow_anim.setStartValue(80)
        self.glow_anim.setEndValue(130)
        self.glow_anim.setLoopCount(-1)
        self.glow_anim.start()

        # --- Toggle Button ---
        self.switch_button = QPushButton("Join the Dark Side")
        self.switch_button.setFixedHeight(36)
        self.switch_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,30);
                color: white;
                font-weight: bold;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,60);
            }
        """)
        self.switch_button.clicked.connect(self.toggle_side)
        layout.addWidget(self.switch_button)

        self.setLayout(layout)

        # --- State ---
        self.mode = "idle"
        self.side = "light"
        self.current_gif = None

        # --- Theme ---
        self.apply_theme()

        # --- Update loop ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(2000)

        self.update_status()

    # ---------------- Theme Management ----------------
    def apply_theme(self):
        if self.side == "light":
            icon_path = os.path.join(ASSETS_DIR, "icon.png")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            self.bg_color = "rgba(0,150,80,150)"
            self.border_color = "rgba(0,255,120,220)"
            self.gif_idle = os.path.join(ASSETS_DIR, "jedi_idle.gif")
            self.gif_alert = os.path.join(ASSETS_DIR, "warrior_alert.gif")
            self.gif_crit = os.path.join(ASSETS_DIR, "darklord_critical.gif")
            self.sound_idle = os.path.join(ASSETS_DIR, "calm.wav")
            self.sound_alert = os.path.join(ASSETS_DIR, "alert.wav")
            self.sound_crit = os.path.join(ASSETS_DIR, "dark.wav")
        else:
            self.bg_color = "rgba(40,8,12,200)"
            self.border_color = "rgba(255,60,60,220)"
            self.gif_idle = os.path.join(ASSETS_DIR, "darklord_critical.gif")
            self.gif_alert = os.path.join(ASSETS_DIR, "warrior_alert.gif")
            self.gif_crit = os.path.join(ASSETS_DIR, "jedi_idle.gif")
            self.sound_idle = os.path.join(ASSETS_DIR, "dark.wav")
            self.sound_alert = os.path.join(ASSETS_DIR, "alert.wav")
            self.sound_crit = os.path.join(ASSETS_DIR, "calm.wav")

        self.setStyleSheet(
            f"background-color: {self.bg_color}; border: none; border-radius: 20px;"
        )

        color = QColor(0, 255, 180) if self.side == "light" else QColor(255, 60, 60)
        self.glow_effect.setColor(color)

    def toggle_side(self):
        self.side = "dark" if self.side == "light" else "light"
        self.apply_theme()
        alert_path = os.path.join(ASSETS_DIR, "alert.wav")
        self.play_sound(alert_path)
        self.switch_button.setText("Join the Light Side" if self.side == "dark" else "Join the Dark Side")
        self.update_status()

    # ---------------- system metrics ----------------
    def get_gpu_usage(self):
        """Return (gpu_percent, gpu_name) using GPUtil first, then NVML fallback."""
        # --- GPUtil first (универсален метод) ---
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                load = gpu.load * 100
                name = gpu.name
                return load, name
        except Exception as e:
            print("[GPUtil error]", e)

        # --- NVML fallback (NVIDIA specific) ---
        if NVML_AVAILABLE:
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes):
                    name = name.decode("utf-8")
                return util.gpu, name
            except Exception as e:
                print("[NVML error]", e)

        return None, None

    def get_cpu_temp(self):
        """Try psutil, then OpenHardwareMonitor (if running)."""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for key in ("coretemp", "cpu-thermal", "acpitz"):
                    if key in temps and temps[key]:
                        for v in temps[key]:
                            if v.current:
                                return v.current
                for sensor_vals in temps.values():
                    for v in sensor_vals:
                        if v.current:
                            return v.current
        except Exception:
            pass

        try:
            import requests
            data = requests.get("http://localhost:8085/data.json", timeout=0.5).json()
            for hw in data.get("Children", []):
                if hw.get("Text", "").lower().startswith("cpu"):
                    for sensor in hw.get("Children", []):
                        if "temperature" in sensor.get("Text", "").lower():
                            value = sensor.get("Value", "")
                            try:
                                return float(value.replace("°C", "").strip())
                            except Exception:
                                pass
        except Exception:
            pass

        return None
    # ---------------- UI Helpers ----------------
    def set_gif(self, path):
        if not os.path.exists(path):
            self.gif_label.setText("NO GIF")
            return
        movie = QMovie(path)
        movie.setScaledSize(QSize(300, 300))
        self.gif_label.setMovie(movie)
        movie.start()
        self.current_gif = movie

    def play_sound(self, path):
        if os.path.exists(path):
            try:
                mixer.music.load(path)
                mixer.music.play()
            except Exception as e:
                print("[sound error]", e)

    # ---------------- Update Core ----------------
    def update_status(self):
        # --- System metrics ---
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        gpu_percent, gpu_name = self.get_gpu_usage()
        temp = self.get_cpu_temp()

        # Temperature
        if temp is None:
            temp_str = "— °C"
        else:
            temp_str = f"{temp:.0f}°C"

        # GPU
        if gpu_percent is None:
            gpu_str = "— %"
        else:
            gpu_str = f"{gpu_percent:.0f}%"

        # Disk usage
        disk_usage = psutil.disk_usage("/").percent
        disk_str = f"{disk_usage:.0f}%"

        # Build overlay text (displayed inside the core)
        overlay_text = (
            f"{self.side.title()} Side\n"
            f"CPU: {cpu:.0f}% | RAM: {ram:.0f}% | Temp: {temp_str}\n"
            f"GPU: {gpu_str} | Disk: {disk_str}"
        )

        # Force state
        if cpu < 40:
            state = "🟢 The Force is calm."
        elif cpu < 70:
            state = "🟢 Energy stable."
        elif cpu < 90:
            state = "🟠 Force tension rising..."
        else:
            state = "🔴 Dark surge detected!"

        if self.side == "dark":
            state = state.replace("Force", "Dark Force")

        overlay_text += f"\n{state}"
        self.overlay_label.setText(overlay_text)

        # Glow intensity
        combined = cpu * 0.7 + ram * 0.3
        blur = 30 + min(80, combined / 100 * 80)
        self.glow_effect.setBlurRadius(blur)

        # Mode selection
        if cpu < IDLE_MAX:
            self.set_mode("idle")
        elif cpu < ALERT_MAX:
            self.set_mode("alert")
        else:
            self.set_mode("crit")

    def set_mode(self, mode):
        if mode == self.mode:
            return
        self.mode = mode
        if mode == "idle":
            self.set_gif(self.gif_idle)
            self.play_sound(self.sound_idle)
        elif mode == "alert":
            self.set_gif(self.gif_alert)
            self.play_sound(self.sound_alert)
        else:
            self.set_gif(self.gif_crit)
            self.play_sound(self.sound_crit)

    # ---------------- Mouse Drag Move ----------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.setWindowOpacity(0.85)
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setWindowOpacity(1.0)
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    watcher = JediSystemWatcher()
    watcher.show()
    sys.exit(app.exec())
