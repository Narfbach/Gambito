"""
Gambito Chess Bot - Matrix Style UI with Global Hotkeys
"""
import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QTextEdit, QFrame, QDoubleSpinBox,
    QCheckBox, QGraphicsDropShadowEffect, QSizePolicy, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QObject, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QColor, QPixmap, QFont
from pynput import keyboard


STYLESHEET = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #000000, stop:0.5 #001100, stop:1 #000000);
}

QFrame#glassPanel {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(0, 30, 0, 0.95), stop:0.5 rgba(0, 20, 0, 0.98), stop:1 rgba(0, 30, 0, 0.95));
    border: 3px solid #00FF41;
    border-radius: 10px;
}

QFrame#innerPanel {
    background: rgba(0, 0, 0, 0.7);
    border: 2px solid #00AA33;
    border-radius: 6px;
    padding: 10px;
}

QLabel { 
    color: #00FF41; 
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 11px; 
}
QLabel#titleLabel { 
    color: #00FF41; 
    font-size: 28px; 
    font-weight: bold;
    font-family: 'Consolas', 'Monaco', monospace;
}
QLabel#subtitleLabel { 
    color: #00DD44; 
    font-size: 11px;
    font-family: 'Consolas', 'Monaco', monospace;
    letter-spacing: 3px;
}
QLabel#sectionLabel { 
    color: #00FF41; 
    font-size: 12px; 
    font-weight: bold; 
    margin-top: 4px;
    margin-bottom: 6px;
    font-family: 'Consolas', 'Monaco', monospace;
    letter-spacing: 2px;
    padding: 6px 10px;
    background: rgba(0, 255, 65, 0.15);
    border-left: 4px solid #00FF41;
    border-radius: 3px;
}
QLabel#eloValue { 
    color: #00FF41; 
    font-size: 36px; 
    font-weight: bold;
    font-family: 'Consolas', 'Monaco', monospace;
}
QLabel#statusLabel { 
    font-size: 13px; 
    font-weight: bold; 
    padding: 6px 20px; 
    border-radius: 14px;
    font-family: 'Consolas', 'Monaco', monospace;
}
QLabel#logsHeader { 
    color: #00FF41; 
    font-size: 12px; 
    font-weight: bold;
    font-family: 'Consolas', 'Monaco', monospace;
    letter-spacing: 2px;
    padding: 6px 10px;
    background: rgba(0, 255, 65, 0.15);
    border-left: 4px solid #00FF41;
    border-radius: 3px;
}
QLabel#hotkeyLabel { 
    color: #00DD44; 
    font-size: 10px;
    font-family: 'Consolas', 'Monaco', monospace;
    letter-spacing: 1px;
}
QLabel#metricLabel {
    color: #00DD44;
    font-size: 10px;
    font-family: 'Consolas', 'Monaco', monospace;
}

QPushButton {
    font-size: 13px; 
    font-weight: bold; 
    padding: 10px 18px;
    border-radius: 6px; 
    border: 2px solid #00FF41;
    color: #00FF41; 
    min-height: 36px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(0, 255, 65, 0.15), stop:1 rgba(0, 255, 65, 0.05));
    font-family: 'Consolas', 'Monaco', monospace;
    letter-spacing: 2px;
}
QPushButton:hover { 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(0, 255, 65, 0.25), stop:1 rgba(0, 255, 65, 0.15));
    border: 2px solid #00FF88;
}
QPushButton:pressed {
    background: rgba(0, 255, 65, 0.3);
    border: 2px solid #00FFAA;
}
QPushButton:disabled { 
    background: rgba(30, 30, 30, 0.3); 
    color: #444444;
    border: 2px solid #222222;
}

QPushButton#btnStart { 
    border-color: #00FF41;
    color: #00FF41;
}
QPushButton#btnStart:hover { 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(0, 255, 65, 0.3), stop:1 rgba(0, 255, 65, 0.2));
}

QPushButton#btnPause { 
    border-color: #FFAA00;
    color: #FFAA00;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 170, 0, 0.15), stop:1 rgba(255, 170, 0, 0.05));
}
QPushButton#btnPause:hover { 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 170, 0, 0.25), stop:1 rgba(255, 170, 0, 0.15));
}

QPushButton#btnStop { 
    border-color: #FF0000;
    color: #FF0000;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 0, 0, 0.15), stop:1 rgba(255, 0, 0, 0.05));
}
QPushButton#btnStop:hover { 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 0, 0, 0.25), stop:1 rgba(255, 0, 0, 0.15));
}

QSlider::groove:horizontal { 
    border: 2px solid #00FF41; 
    height: 8px; 
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #001100, stop:0.5 #002200, stop:1 #001100);
    border-radius: 4px; 
}
QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #00FF88, stop:1 #00DD44);
    border: 2px solid #00FF41; 
    width: 20px; 
    margin: -7px 0; 
    border-radius: 10px;
}
QSlider::handle:horizontal:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #00FFAA, stop:1 #00FF66);
}

QDoubleSpinBox {
    font-size: 12px; 
    padding: 6px 8px; 
    border: 2px solid #00FF41;
    border-radius: 5px; 
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #001100, stop:1 #000800);
    color: #00FF41; 
    min-width: 90px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-weight: bold;
}
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background: rgba(0, 255, 65, 0.2);
    border: 1px solid #00FF41;
    width: 20px;
}
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background: rgba(0, 255, 65, 0.3);
}

QCheckBox { 
    font-size: 12px; 
    color: #00FF41; 
    spacing: 8px;
    font-family: 'Consolas', 'Monaco', monospace;
    padding: 4px;
}
QCheckBox::indicator { 
    width: 18px; 
    height: 18px; 
    border-radius: 4px; 
    border: 2px solid #00FF41; 
    background: #001100; 
}
QCheckBox::indicator:checked { 
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #00FF41, stop:1 #00DD33);
    border: 2px solid #00FF88; 
}
QCheckBox::indicator:hover {
    background: rgba(0, 255, 65, 0.2);
}

QTextEdit#logArea {
    font-family: 'Consolas', 'Monaco', monospace; 
    font-size: 11px;
    background: #000000; 
    color: #00FF41; 
    border: 3px solid #00FF41;
    border-radius: 8px; 
    padding: 8px;
    selection-background-color: #00AA33;
    line-height: 1.4;
}

QFrame#separator { 
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(0, 255, 65, 0), stop:0.5 #00FF41, stop:1 rgba(0, 255, 65, 0));
    max-height: 2px; 
    min-height: 2px;
    margin: 6px 0px;
}

QProgressBar {
    border: 2px solid #00FF41;
    border-radius: 5px;
    background: #001100;
    height: 8px;
    text-align: center;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #00DD33, stop:1 #00FF41);
}
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
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 255, 65, 120))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)


class MainWindow(QMainWindow):
    def __init__(self, bot_instance):
        super().__init__()
        self.bot = bot_instance
        self.setWindowTitle("GAMBITO")
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            from PySide6.QtGui import QIcon
            self.setWindowIcon(QIcon(icon_path))
        
        self.setFixedSize(540, 720)
        
        self.log_signal = LogSignal()
        self.log_signal.new_log.connect(self.append_log)
        self.bot.set_log_callback(self.emit_log)

        self.hotkey_signal = HotkeySignal()
        self.hotkey_signal.start.connect(self.start_bot)
        self.hotkey_signal.pause.connect(self.toggle_pause)
        self.hotkey_signal.stop.connect(self.stop_bot)

        central = QWidget()
        self.setCentralWidget(central)
        
        main = QVBoxLayout(central)
        main.setContentsMargins(18, 14, 18, 14)
        main.setSpacing(10)

        # Logo text
        logo_label = QLabel("GAMBITO")
        logo_label.setStyleSheet("""
            font-size: 48px;
            font-weight: bold;
            color: #00FF41;
            font-family: 'Consolas', 'Monaco', monospace;
            letter-spacing: 8px;
            padding: 10px;
        """)
        logo_label.setAlignment(Qt.AlignCenter)
        main.addWidget(logo_label)
        
        subtitle = QLabel("// CHESS NEURAL INTERFACE //")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        main.addWidget(subtitle)
        
        main.addSpacing(8)

        # Glass Panel
        panel = GlassPanel()
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(16, 14, 16, 14)
        panel_layout.setSpacing(14)

        # Controls
        lbl = QLabel("[ SYSTEM CONTROLS ]")
        lbl.setObjectName("sectionLabel")
        panel_layout.addWidget(lbl)
        
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        
        self.btn_start = QPushButton("INIT (F6)")
        self.btn_start.setObjectName("btnStart")
        self.btn_start.clicked.connect(self.start_bot)
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.btn_pause = QPushButton("PAUSE (F7)")
        self.btn_pause.setObjectName("btnPause")
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setCursor(Qt.PointingHandCursor)
        self.btn_pause.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.btn_stop = QPushButton("TERM (F8)")
        self.btn_stop.setObjectName("btnStop")
        self.btn_stop.clicked.connect(self.stop_bot)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setCursor(Qt.PointingHandCursor)
        self.btn_stop.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_pause)
        btn_row.addWidget(self.btn_stop)
        panel_layout.addLayout(btn_row)
        
        panel_layout.addSpacing(24)

        # ELO Section
        lbl2 = QLabel("[ ENGINE POWER ]")
        lbl2.setObjectName("sectionLabel")
        panel_layout.addWidget(lbl2)
        
        elo_row = QHBoxLayout()
        elo_label = QLabel("ELO RATING:")
        elo_label.setStyleSheet("font-size: 12px; margin-left: 8px;")
        elo_row.addWidget(elo_label)
        elo_row.addStretch()
        self.elo_value = QLabel("2850")
        self.elo_value.setObjectName("eloValue")
        elo_row.addWidget(self.elo_value)
        panel_layout.addLayout(elo_row)
        
        slider_container = QHBoxLayout()
        slider_container.addSpacing(8)
        self.elo_slider = QSlider(Qt.Horizontal)
        self.elo_slider.setMinimum(1350)
        self.elo_slider.setMaximum(2850)
        self.elo_slider.setValue(2850)
        self.elo_slider.valueChanged.connect(self.update_elo)
        slider_container.addWidget(self.elo_slider)
        slider_container.addSpacing(8)
        panel_layout.addLayout(slider_container)
        
        range_row = QHBoxLayout()
        range_row.addSpacing(8)
        lbl_min = QLabel("1350 [NOVICE]")
        lbl_min.setStyleSheet("font-size: 9px; color: #00AA33;")
        lbl_max = QLabel("[MASTER] 2850")
        lbl_max.setStyleSheet("font-size: 9px; color: #00AA33;")
        range_row.addWidget(lbl_min)
        range_row.addStretch()
        range_row.addWidget(lbl_max)
        range_row.addSpacing(8)
        panel_layout.addLayout(range_row)

        # Humanization
        panel_layout.addSpacing(6)
        lbl3 = QLabel("[ HUMANIZATION ]")
        lbl3.setObjectName("sectionLabel")
        panel_layout.addWidget(lbl3)
        
        delay_row = QHBoxLayout()
        delay_row.setSpacing(12)
        delay_row.addSpacing(8)
        
        min_label = QLabel("MIN DELAY:")
        min_label.setStyleSheet("font-size: 11px;")
        delay_row.addWidget(min_label)
        self.min_delay_spin = QDoubleSpinBox()
        self.min_delay_spin.setRange(0.0, 5.0)
        self.min_delay_spin.setSingleStep(0.1)
        self.min_delay_spin.setValue(0.1)
        self.min_delay_spin.setSuffix(" s")
        self.min_delay_spin.valueChanged.connect(self.update_delay)
        delay_row.addWidget(self.min_delay_spin)
        
        delay_row.addSpacing(10)
        
        max_label = QLabel("MAX DELAY:")
        max_label.setStyleSheet("font-size: 11px;")
        delay_row.addWidget(max_label)
        self.max_delay_spin = QDoubleSpinBox()
        self.max_delay_spin.setRange(0.0, 10.0)
        self.max_delay_spin.setSingleStep(0.1)
        self.max_delay_spin.setValue(0.5)
        self.max_delay_spin.setSuffix(" s")
        self.max_delay_spin.valueChanged.connect(self.update_delay)
        delay_row.addWidget(self.max_delay_spin)
        
        delay_row.addStretch()
        delay_row.addSpacing(8)
        panel_layout.addLayout(delay_row)
        
        bullet_container = QHBoxLayout()
        bullet_container.addSpacing(8)
        self.bullet_check = QCheckBox("BULLET MODE (NEURAL TIMING)")
        self.bullet_check.stateChanged.connect(self.update_bullet_mode)
        bullet_container.addWidget(self.bullet_check)
        bullet_container.addStretch()
        panel_layout.addLayout(bullet_container)

        main.addWidget(panel)

        # Logs
        logs_lbl = QLabel("[ SYSTEM LOG ]")
        logs_lbl.setObjectName("logsHeader")
        main.addWidget(logs_lbl)
        
        self.log_text = QTextEdit()
        self.log_text.setObjectName("logArea")
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(110)
        main.addWidget(self.log_text)

        # Matrix rain effect simulation
        self.setup_matrix_effect()
        
        # Setup hotkeys
        self.setup_hotkeys()

    def setup_matrix_effect(self):
        """Add subtle pulsing effect to simulate matrix aesthetic"""
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.pulse_effect)
        self.pulse_timer.start(2000)
        self.pulse_state = 0

    def pulse_effect(self):
        """Subtle glow pulse on the panel border"""
        self.pulse_state = (self.pulse_state + 1) % 2

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
        self.log_text.append(f">> {msg}")
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
                self.btn_pause.setText("RESUME (F7)")
            else:
                self.btn_pause.setText("PAUSE (F7)")

    def update_ui_state(self, running):
        self.btn_start.setEnabled(not running)
        self.btn_stop.setEnabled(running)
        self.btn_pause.setEnabled(running)
        if not running:
            self.btn_pause.setText("PAUSE (F7)")

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
        if hasattr(self, 'pulse_timer'):
            self.pulse_timer.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    import subprocess
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
