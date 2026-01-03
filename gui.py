"""
Gambito Chess Bot - Fixed Size Professional UI with Global Hotkeys
"""
import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QTextEdit, QFrame, QDoubleSpinBox,
    QCheckBox, QGraphicsDropShadowEffect, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QColor, QPixmap
from pynput import keyboard


STYLESHEET = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #87CEEB, stop:0.5 #5DADE2, stop:1 #2980B9);
}

QFrame#glassPanel {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.96), stop:1 rgba(248,252,255,0.94));
    border: 2px solid rgba(255,255,255,0.9);
    border-radius: 10px;
}

QLabel { color: #2c3e50; font-size: 11px; }
QLabel#titleLabel { color: #1a5276; font-size: 28px; font-weight: bold; }
QLabel#subtitleLabel { color: #5d6d7e; font-size: 11px; }
QLabel#sectionLabel { color: #2c3e50; font-size: 12px; font-weight: bold; margin-top: 6px; }
QLabel#eloValue { color: #1A5276; font-size: 24px; font-weight: bold; }
QLabel#statusLabel { font-size: 13px; font-weight: bold; padding: 6px 20px; border-radius: 14px; }
QLabel#logsHeader { color: white; font-size: 12px; font-weight: bold; }
QLabel#hotkeyLabel { color: rgba(255,255,255,0.8); font-size: 10px; }

QPushButton {
    font-size: 12px; font-weight: bold; padding: 8px 16px;
    border-radius: 5px; border: none; color: white; min-height: 32px;
}
QPushButton#btnStart { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #58D68D, stop:1 #27AE60); }
QPushButton#btnStart:hover { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #7DCEA0, stop:1 #2ECC71); }
QPushButton#btnStart:disabled { background: #AAB7B8; color: #F0F0F0; }

QPushButton#btnPause { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #F8C471, stop:1 #F39C12); color: #6E4600; }
QPushButton#btnPause:hover { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #FAD7A0, stop:1 #F5B041); }
QPushButton#btnPause:disabled { background: #AAB7B8; color: #F0F0F0; }

QPushButton#btnStop { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #EC7063, stop:1 #CB4335); }
QPushButton#btnStop:hover { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #F1948A, stop:1 #E74C3C); }
QPushButton#btnStop:disabled { background: #AAB7B8; color: #F0F0F0; }

QSlider::groove:horizontal { border: 1px solid #BDC3C7; height: 6px; background: #ECF0F1; border-radius: 3px; }
QSlider::handle:horizontal {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #FFFFFF, stop:1 #D5D8DC);
    border: 2px solid #5DADE2; width: 16px; margin: -6px 0; border-radius: 8px;
}

QDoubleSpinBox {
    font-size: 11px; padding: 4px 6px; border: 1px solid #BDC3C7;
    border-radius: 4px; background: white; color: #2C3E50; min-width: 80px;
}

QCheckBox { font-size: 11px; color: #2C3E50; spacing: 6px; }
QCheckBox::indicator { width: 16px; height: 16px; border-radius: 3px; border: 1px solid #ABB2B9; background: white; }
QCheckBox::indicator:checked { background: #27AE60; border: 1px solid #1E8449; }

QTextEdit#logArea {
    font-family: Consolas, monospace; font-size: 10px;
    background: #1C2833; color: #58D68D; border: 1px solid #34495E;
    border-radius: 6px; padding: 6px;
}

QFrame#separator { background: #D5DBDB; max-height: 1px; min-height: 1px; }
"""


class LogSignal(QObject):
    new_log = Signal(str)


class HotkeySignal(QObject):
    start = Signal()
    pause = Signal()
    stop = Signal()


class GlassPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("glassPanel")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 50, 80, 60))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)


class MainWindow(QMainWindow):
    def __init__(self, bot_instance):
        super().__init__()
        self.bot = bot_instance
        self.setWindowTitle("Gambito - Chess Bot")
        
        self.setFixedSize(480, 680)
        
        self.log_signal = LogSignal()
        self.log_signal.new_log.connect(self.append_log)
        self.bot.set_log_callback(self.emit_log)

        # Hotkey signals (for thread-safe GUI updates)
        self.hotkey_signal = HotkeySignal()
        self.hotkey_signal.start.connect(self.start_bot)
        self.hotkey_signal.pause.connect(self.toggle_pause)
        self.hotkey_signal.stop.connect(self.stop_bot)

        central = QWidget()
        self.setCentralWidget(central)
        
        main = QVBoxLayout(central)
        main.setContentsMargins(16, 12, 16, 12)
        main.setSpacing(8)

        # Logo PNG
        logo_container = QHBoxLayout()
        logo_container.addStretch()
        
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        logo_label = QLabel()
        pixmap = QPixmap(logo_path)
        scaled_pixmap = pixmap.scaledToWidth(280, Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_container.addWidget(logo_label)
        
        logo_container.addStretch()
        main.addLayout(logo_container)
        
        subtitle = QLabel("Advanced Chess Engine Controller")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        main.addWidget(subtitle)
        
        main.addSpacing(10)

        # Glass Panel
        panel = GlassPanel()
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(14, 12, 14, 12)
        panel_layout.setSpacing(8)

        # Controls
        lbl = QLabel("Controls")
        lbl.setObjectName("sectionLabel")
        panel_layout.addWidget(lbl)
        
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        
        self.btn_start = QPushButton("Start (F6)")
        self.btn_start.setObjectName("btnStart")
        self.btn_start.clicked.connect(self.start_bot)
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.btn_pause = QPushButton("Pause (F7)")
        self.btn_pause.setObjectName("btnPause")
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setCursor(Qt.PointingHandCursor)
        self.btn_pause.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.btn_stop = QPushButton("Stop (F8)")
        self.btn_stop.setObjectName("btnStop")
        self.btn_stop.clicked.connect(self.stop_bot)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setCursor(Qt.PointingHandCursor)
        self.btn_stop.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_pause)
        btn_row.addWidget(self.btn_stop)
        panel_layout.addLayout(btn_row)

        # Separator
        sep1 = QFrame()
        sep1.setObjectName("separator")
        sep1.setFrameShape(QFrame.HLine)
        panel_layout.addWidget(sep1)

        # ELO
        lbl2 = QLabel("Engine Strength")
        lbl2.setObjectName("sectionLabel")
        panel_layout.addWidget(lbl2)
        
        elo_row = QHBoxLayout()
        elo_row.addWidget(QLabel("ELO Rating:"))
        elo_row.addStretch()
        self.elo_value = QLabel("2850")
        self.elo_value.setObjectName("eloValue")
        elo_row.addWidget(self.elo_value)
        panel_layout.addLayout(elo_row)
        
        self.elo_slider = QSlider(Qt.Horizontal)
        self.elo_slider.setMinimum(1350)
        self.elo_slider.setMaximum(2850)
        self.elo_slider.setValue(2850)
        self.elo_slider.valueChanged.connect(self.update_elo)
        panel_layout.addWidget(self.elo_slider)
        
        range_row = QHBoxLayout()
        lbl_min = QLabel("1350")
        lbl_min.setStyleSheet("font-size: 9px; color: #7F8C8D;")
        lbl_max = QLabel("2850")
        lbl_max.setStyleSheet("font-size: 9px; color: #7F8C8D;")
        range_row.addWidget(lbl_min)
        range_row.addStretch()
        range_row.addWidget(lbl_max)
        panel_layout.addLayout(range_row)

        # Separator
        sep2 = QFrame()
        sep2.setObjectName("separator")
        sep2.setFrameShape(QFrame.HLine)
        panel_layout.addWidget(sep2)

        # Human Behavior
        lbl3 = QLabel("Human Behavior")
        lbl3.setObjectName("sectionLabel")
        panel_layout.addWidget(lbl3)
        
        delay_row = QHBoxLayout()
        delay_row.setSpacing(16)
        
        delay_row.addWidget(QLabel("Min Delay:"))
        self.min_delay_spin = QDoubleSpinBox()
        self.min_delay_spin.setRange(0.0, 5.0)
        self.min_delay_spin.setSingleStep(0.1)
        self.min_delay_spin.setValue(0.1)
        self.min_delay_spin.setSuffix(" s")
        self.min_delay_spin.valueChanged.connect(self.update_delay)
        delay_row.addWidget(self.min_delay_spin)
        
        delay_row.addSpacing(8)
        
        delay_row.addWidget(QLabel("Max Delay:"))
        self.max_delay_spin = QDoubleSpinBox()
        self.max_delay_spin.setRange(0.0, 10.0)
        self.max_delay_spin.setSingleStep(0.1)
        self.max_delay_spin.setValue(0.5)
        self.max_delay_spin.setSuffix(" s")
        self.max_delay_spin.valueChanged.connect(self.update_delay)
        delay_row.addWidget(self.max_delay_spin)
        
        delay_row.addStretch()
        panel_layout.addLayout(delay_row)
        
        self.bullet_check = QCheckBox("Bullet Mode (Smart Timing)")
        self.bullet_check.stateChanged.connect(self.update_bullet_mode)
        panel_layout.addWidget(self.bullet_check)

        main.addWidget(panel)

        # Hotkey hint
        hotkey_lbl = QLabel("Global Hotkeys: F6 = Start | F7 = Pause/Resume | F8 = Stop")
        hotkey_lbl.setObjectName("hotkeyLabel")
        hotkey_lbl.setAlignment(Qt.AlignCenter)
        main.addWidget(hotkey_lbl)

        # Logs
        logs_lbl = QLabel("Live Logs")
        logs_lbl.setObjectName("logsHeader")
        main.addWidget(logs_lbl)
        
        self.log_text = QTextEdit()
        self.log_text.setObjectName("logArea")
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(100)
        main.addWidget(self.log_text)

        # Start global hotkey listener
        self.setup_hotkeys()

    def setup_hotkeys(self):
        """Setup global hotkeys using pynput"""
        def on_press(key):
            try:
                if key == keyboard.Key.f6:
                    self.hotkey_signal.start.emit()
                elif key == keyboard.Key.f7:
                    self.hotkey_signal.pause.emit()
                elif key == keyboard.Key.f8:
                    self.hotkey_signal.stop.emit()
            except:
                pass

        self.hotkey_listener = keyboard.Listener(on_press=on_press)
        self.hotkey_listener.daemon = True
        self.hotkey_listener.start()

    def emit_log(self, msg):
        self.log_signal.new_log.emit(msg)

    def append_log(self, msg):
        self.log_text.append(msg)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def start_bot(self):
        if not self.bot.is_running:
            self.bot.start()
            self.update_ui_state(True)

    def stop_bot(self):
        if self.bot.is_running:
            self.bot.stop()
            self.update_ui_state(False)

    def toggle_pause(self):
        if self.bot.is_running:
            self.bot.toggle_pause()
            if self.bot.is_paused:
                self.btn_pause.setText("Resume (F7)")
            else:
                self.btn_pause.setText("Pause (F7)")

    def update_ui_state(self, running):
        self.btn_start.setEnabled(not running)
        self.btn_stop.setEnabled(running)
        self.btn_pause.setEnabled(running)
        if not running:
            self.btn_pause.setText("Pause (F7)")

    def update_elo(self):
        elo = self.elo_slider.value()
        self.elo_value.setText(str(elo))
        self.bot.set_elo(elo)

    def update_delay(self):
        min_d = self.min_delay_spin.value()
        max_d = self.max_delay_spin.value()
        if min_d > max_d:
            self.max_delay_spin.setValue(min_d)
        self.bot.set_humanization_delay(min_d, max_d)

    def update_bullet_mode(self, state):
        enabled = state == Qt.CheckState.Checked.value
        self.bot.set_bullet_mode(enabled)
        self.min_delay_spin.setEnabled(not enabled)
        self.max_delay_spin.setEnabled(not enabled)

    def closeEvent(self, event):
        """Stop hotkey listener on close"""
        if hasattr(self, 'hotkey_listener'):
            self.hotkey_listener.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    import subprocess
    import os
    import atexit

    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(script_dir, "server.py")
    
    server_process = subprocess.Popen(
        [sys.executable, server_path], 
        cwd=script_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    def cleanup():
        server_process.terminate()
        server_process.wait()

    atexit.register(cleanup)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)
    
    from bot_controller import bot
    
    window = MainWindow(bot)
    window.show()
    
    sys.exit(app.exec())
