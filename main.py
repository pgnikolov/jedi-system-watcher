import sys, os, psutil
from PyQt6.QtWidgets import (
    QApplication, QFrame, QLabel, QWidget, QVBoxLayout, QPushButton, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import QTimer, Qt, QSize, QPropertyAnimation
from PyQt6.QtGui import QMovie, QIcon, QColor
from pygame import mixer

# GPU support
try:
    import pynvml
    NVML_AVAILABLE = True
    pynvml.nvmlInit()
except:
    NVML_AVAILABLE = False

ASSETS_DIR = "assets"
IDLE_MAX = 70
ALERT_MAX = 90

class JediSystemWatcher(QWidget):
    def __init__(self):
        super().__init__()

        # Window settings
        self.setWindowTitle("Jedi System Watcher")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(80, 80, 360, 480)

        mixer.init(frequency=22050, size=-16, channels=1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Main core
        self.core_frame = QFrame()
        self.core_frame.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.core_frame.setFixedSize(320, 360)
        self.core_frame.setStyleSheet("background: transparent; border: none;")

        core_layout = QVBoxLayout(self.core_frame)
        core_layout.setContentsMargins(0, 0, 0, 0)

        # GIF
        self.gif_label = QLabel()
        self.gif_label.setFixedSize(300, 300)
        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        core_layout.addWidget(self.gif_label)

        # Overlay text inside circle
        self.overlay_label = QLabel("", alignment=Qt.AlignmentFlag.AlignCenter)
        self.overlay_label.setStyleSheet("color:white; font-size:14px; font-weight:bold; background:transparent;")
        self.overlay_label.setTextFormat(Qt.TextFormat.RichText)
        self.overlay_label.setWordWrap(True)
        core_layout.addWidget(self.overlay_label)

        layout.addWidget(self.core_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        # Glow effect
        glow = QGraphicsDropShadowEffect()
        glow.setOffset(0, 0)
        glow.setBlurRadius(85)
        glow.setColor(QColor(0, 255, 150, 200))
        self.core_frame.setGraphicsEffect(glow)
        self.glow_effect = glow

        # Toggle button
        self.switch_button = QPushButton("Join the Dark Side")
        self.switch_button.setFixedHeight(36)
        self.apply_button_style("#1BFD9C")  # Jedi color
        self.switch_button.clicked.connect(self.toggle_side)
        layout.addWidget(self.switch_button)

        self.side = "light"
        self.mode = "idle"
        self.apply_theme()

        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(2000)

        self.update_status()

    # --- Neon button styling ---
    def apply_button_style(self, color):
        self.switch_button.setStyleSheet(f"""
        QPushButton {{
            font-size: 15px;
            padding: 8px 28px;
            border-radius: 10px;
            border: 2px solid {color};
            color: {color};
            font-weight: bold;
            background: rgba(0,0,0,0.2);
        }}
        QPushButton:hover {{
            background: rgba(0,0,0,0.35);
        }}
        """)

        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(22)
        glow.setOffset(0, 0)
        glow.setColor(QColor(color))
        self.switch_button.setGraphicsEffect(glow)

    # --- Theme ---
    def apply_theme(self):
        if self.side == "light":
            icon = "icon.png"
            self.gif_idle = f"{ASSETS_DIR}/jedi_idle.gif"
            self.gif_alert = f"{ASSETS_DIR}/warrior_alert.gif"
            self.gif_crit = f"{ASSETS_DIR}/darklord_critical.gif"
            self.sound_idle = f"{ASSETS_DIR}/calm.wav"
            self.sound_alert = f"{ASSETS_DIR}/alert.wav"
            self.sound_crit = f"{ASSETS_DIR}/dark.wav"
            self.glow_effect.setColor(QColor(0,255,150))
            self.apply_button_style("#1BFD9C")
        else:
            self.gif_idle = f"{ASSETS_DIR}/darklord_critical.gif"
            self.gif_alert = f"{ASSETS_DIR}/warrior_alert.gif"
            self.gif_crit = f"{ASSETS_DIR}/jedi_idle.gif"
            self.sound_idle = f"{ASSETS_DIR}/dark.wav"
            self.sound_alert = f"{ASSETS_DIR}/alert.wav"
            self.sound_crit = f"{ASSETS_DIR}/calm.wav"
            self.glow_effect.setColor(QColor(255,60,60))
            self.apply_button_style("#FF4E4E")

    # Toggle light/dark
    def toggle_side(self):
        self.side = "dark" if self.side == "light" else "light"
        self.apply_theme()
        self.play_sound(f"{ASSETS_DIR}/alert.wav")
        self.switch_button.setText("Join the Light Side" if self.side=="dark" else "Join the Dark Side")
        self.update_status()

    # GPU usage
    def get_gpu_usage(self):
        try:
            import GPUtil
            g = GPUtil.getGPUs()
            if g:
                return g[0].load * 100, g[0].name
        except: pass

        if NVML_AVAILABLE:
            try:
                h = pynvml.nvmlDeviceGetHandleByIndex(0)
                util = pynvml.nvmlDeviceGetUtilizationRates(h).gpu
                name = pynvml.nvmlDeviceGetName(h)
                if isinstance(name, bytes): name = name.decode()
                return util, name
            except: pass

        return None, None

    # Set GIF
    def set_gif(self, path):
        movie = QMovie(path)
        movie.setScaledSize(QSize(300,300))
        self.gif_label.setMovie(movie)
        movie.start()

    # Sound
    def play_sound(self, path):
        try: mixer.music.load(path); mixer.music.play()
        except: pass

    # Update HUD
    def update_status(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        gpu, _ = self.get_gpu_usage()
        disk = psutil.disk_usage("/").percent

        orb = (
            "<span style='color:#00ff99;'>●</span>" if cpu<40 else
            "<span style='color:#00ffcc;'>●</span>" if cpu<70 else
            "<span style='color:#ffaa00;'>●</span>" if cpu<90 else
            "<span style='color:#ff4444;'>●</span>"
        )

        state = (
            "The Force is calm." if cpu<40 else
            "Energy stable." if cpu<70 else
            "Force tension rising..." if cpu<90 else
            "Dark surge detected!"
        )
        if self.side=="dark": state = state.replace("Force","Dark Force")

        self.overlay_label.setText(
            f"{self.side.title()} Side<br>"
            f"CPU: {cpu:.0f}% | RAM: {ram:.0f}%<br>"
            f"GPU: {'—' if gpu is None else f'{gpu:.0f}%'} | Disk: {disk:.0f}%<br>"
            f"{orb} {state}"
        )

        # glow pulse
        blur = 40 + min(45, (cpu*0.7+ram*0.3)/100*45)
        self.glow_effect.setBlurRadius(int(blur))

        # Mode GIF
        if cpu < IDLE_MAX: self.set_mode("idle")
        elif cpu < ALERT_MAX: self.set_mode("alert")
        else: self.set_mode("crit")

    def set_mode(self, m):
        if m==self.mode: return
        self.mode = m
        gif = self.gif_idle if m=="idle" else self.gif_alert if m=="alert" else self.gif_crit
        snd = self.sound_idle if m=="idle" else self.sound_alert if m=="alert" else self.sound_crit
        self.set_gif(gif); self.play_sound(snd)

    # Drag move window
    def mousePressEvent(self,e):
        if e.button()==Qt.MouseButton.LeftButton:
            self.drag = e.globalPosition().toPoint()-self.frameGeometry().topLeft()
            self.setWindowOpacity(0.85)
    def mouseMoveEvent(self,e):
        if e.buttons()==Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint()-self.drag)
    def mouseReleaseEvent(self,e): self.setWindowOpacity(1.0)

if __name__=="__main__":
    app = QApplication(sys.argv)
    w = JediSystemWatcher()
    w.show()
    app.exec()
