"""
Gambito Chess Bot - Frutiger Aero UI
A Windows Vista/7 inspired glossy interface with glass effects.
"""
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QTextEdit, QFrame, QDoubleSpinBox,
    QCheckBox, QGraphicsDropShadowEffect, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QObject, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor, QPalette, QLinearGradient, QBrush, QPainter

# Frutiger Aero Color Palette
AERO_COLORS = {
    'sky_blue': '#4BA3C7',
    'sky_light': '#7FCCE5', 
    'glass_white': 'rgba(255, 255, 255, 0.85)',
    'glass_border': 'rgba(255, 255, 255, 0.6)',
    'green_fresh': '#7CB342',
    'green_light': '#9CCC65',
    'orange_warm': '#FFB74D',
    'red_soft': '#EF5350',
    'text_dark': '#1A3A4A',
    'text_light': '#FFFFFF',
    'shadow': 'rgba(0, 60, 90, 0.3)',
}

# Frutiger Aero Stylesheet
AERO_STYLESHEET = """
/* Main Window - Sky gradient background */
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #7FCCE5,
        stop:0.3 #4BA3C7,
        stop:0.7 #2E8EB3,
        stop:1 #1A6A8A);
}

QWidget#centralWidget {
    background: transparent;
}

/* Glass Panel Effect */
QFrame#glassPanel {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.95),
        stop:0.03 rgba(255, 255, 255, 0.85),
        stop:0.5 rgba(240, 248, 255, 0.75),
        stop:1 rgba(220, 240, 250, 0.85));
    border: 1px solid rgba(255, 255, 255, 0.8);
    border-radius: 12px;
}

/* Title Label */
QLabel#titleLabel {
    color: #1A3A4A;
    font-size: 28px;
    font-weight: bold;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    padding: 5px;
    background: transparent;
}

QLabel#subtitleLabel {
    color: #3A6A7A;
    font-size: 12px;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    background: transparent;
}

/* Status Indicator */
QLabel#statusLabel {
    font-size: 16px;
    font-weight: bold;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    padding: 8px 20px;
    border-radius: 20px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.9),
        stop:0.5 rgba(240, 240, 240, 0.8),
        stop:1 rgba(220, 220, 220, 0.9));
    border: 1px solid rgba(180, 180, 180, 0.5);
}

/* Glossy Buttons - Aero Style */
QPushButton {
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 13px;
    font-weight: bold;
    padding: 10px 24px;
    border-radius: 6px;
    border: 1px solid rgba(0, 0, 0, 0.2);
    color: white;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #8ED0E8,
        stop:0.45 #5BB5D5,
        stop:0.55 #4AA5C5,
        stop:1 #3A95B5);
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #A0E0F8,
        stop:0.45 #6CC5E5,
        stop:0.55 #5BB5D5,
        stop:1 #4AA5C5);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #3A85A5,
        stop:0.45 #4A95B5,
        stop:0.55 #5AA5C5,
        stop:1 #6AB5D5);
}

QPushButton:disabled {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #C0C0C0,
        stop:0.5 #A8A8A8,
        stop:1 #909090);
    color: #666666;
    border: 1px solid #888888;
}

/* Green Start Button */
QPushButton#btnStart {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #A5D66A,
        stop:0.45 #7CB342,
        stop:0.55 #6BA332,
        stop:1 #5A9322);
}

QPushButton#btnStart:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #B5E67A,
        stop:0.45 #8CC352,
        stop:0.55 #7BB342,
        stop:1 #6AA332);
}

/* Red Stop Button */
QPushButton#btnStop {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #EF7A7A,
        stop:0.45 #EF5350,
        stop:0.55 #DE4340,
        stop:1 #CD3330);
}

QPushButton#btnStop:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FF8A8A,
        stop:0.45 #FF6360,
        stop:0.55 #EE5350,
        stop:1 #DD4340);
}

/* Orange Pause Button */
QPushButton#btnPause {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFCC80,
        stop:0.45 #FFB74D,
        stop:0.55 #FFA63D,
        stop:1 #FF962D);
}

QPushButton#btnPause:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFDC90,
        stop:0.45 #FFC75D,
        stop:0.55 #FFB64D,
        stop:1 #FFA63D);
}

/* Section Labels */
QLabel#sectionLabel {
    color: #2A5A6A;
    font-size: 14px;
    font-weight: bold;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    background: transparent;
    padding: 4px 0;
}

QLabel {
    color: #1A4A5A;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    background: transparent;
}

/* Slider - Aero Style */
QSlider::groove:horizontal {
    border: 1px solid rgba(0, 80, 120, 0.3);
    height: 8px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #C0D8E8,
        stop:0.5 #A0C8D8,
        stop:1 #80B8C8);
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFFFFF,
        stop:0.45 #E8F4FA,
        stop:0.55 #D0E8F2,
        stop:1 #B8DCE8);
    border: 1px solid rgba(0, 80, 120, 0.4);
    width: 18px;
    margin: -6px 0;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFFFFF,
        stop:0.3 #F0F8FC,
        stop:1 #D8ECF4);
    border: 1px solid #4BA3C7;
}

/* SpinBox */
QDoubleSpinBox {
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 12px;
    padding: 6px 10px;
    border: 1px solid rgba(0, 80, 120, 0.3);
    border-radius: 6px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFFFFF,
        stop:1 #F0F8FA);
    color: #1A4A5A;
}

QDoubleSpinBox:focus {
    border: 2px solid #4BA3C7;
}

/* Checkbox - Aero Style */
QCheckBox {
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 12px;
    color: #1A4A5A;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid rgba(0, 80, 120, 0.4);
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFFFFF,
        stop:1 #E8F0F4);
}

QCheckBox::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #7CB342,
        stop:1 #5A9322);
    border: 1px solid #4A8312;
    image: none;
}

QCheckBox::indicator:checked::after {
    content: "✓";
}

/* Log Text Area */
QTextEdit#logArea {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(20, 40, 60, 0.95),
        stop:1 rgba(10, 30, 50, 0.98));
    color: #80E8B0;
    border: 1px solid rgba(80, 180, 220, 0.5);
    border-radius: 8px;
    padding: 8px;
    selection-background-color: #4BA3C7;
}

/* ELO Display */
QLabel#eloValue {
    font-size: 24px;
    font-weight: bold;
    color: #1A5A7A;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    background: transparent;
}

/* Progress/Status bar styling */
QProgressBar {
    border: 1px solid rgba(0, 80, 120, 0.3);
    border-radius: 6px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #E0E8EC,
        stop:1 #C0D0D8);
    text-align: center;
    color: #1A4A5A;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #7CB342,
        stop:0.5 #6BA332,
        stop:1 #5A9322);
    border-radius: 5px;
}
"""


class LogSignal(QObject):
    new_log = Signal(str)


class GlassPanel(QFrame):
    """A glass-effect panel with shadow."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("glassPanel")
        
        # Add drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 60, 100, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)


class MainWindow(QMainWindow):
    def __init__(self, bot_instance):
        super().__init__()
        self.bot = bot_instance
        self.setWindowTitle("♟ Gambito - Chess Bot")
        self.resize(520, 680)
        self.setMinimumSize(480, 600)
        
        # Signal for thread-safe logging
        self.log_signal = LogSignal()
        self.log_signal.new_log.connect(self.append_log)
        self.bot.set_log_callback(self.emit_log)

        # Central Widget
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # === HEADER ===
        header_layout = QVBoxLayout()
        header_layout.setSpacing(2)
        
        title = QLabel("♟ Gambito")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Advanced Chess Engine Controller")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)

        # === STATUS ===
        status_container = QHBoxLayout()
        status_container.addStretch()
        
        self.status_label = QLabel("● OFFLINE")
        self.status_label.setObjectName("statusLabel")
        self.update_status_style("stopped")
        
        status_container.addWidget(self.status_label)
        status_container.addStretch()
        main_layout.addLayout(status_container)

        # === MAIN GLASS PANEL ===
        glass_panel = GlassPanel()
        panel_layout = QVBoxLayout(glass_panel)
        panel_layout.setContentsMargins(20, 20, 20, 20)
        panel_layout.setSpacing(16)

        # --- Controls Section ---
        controls_label = QLabel("Controls")
        controls_label.setObjectName("sectionLabel")
        panel_layout.addWidget(controls_label)
        
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)
        
        self.btn_start = QPushButton("▶ Start")
        self.btn_start.setObjectName("btnStart")
        self.btn_start.clicked.connect(self.start_bot)
        self.btn_start.setCursor(Qt.PointingHandCursor)
        
        self.btn_pause = QPushButton("⏸ Pause")
        self.btn_pause.setObjectName("btnPause")
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setCursor(Qt.PointingHandCursor)
        
        self.btn_stop = QPushButton("■ Stop")
        self.btn_stop.setObjectName("btnStop")
        self.btn_stop.clicked.connect(self.stop_bot)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setCursor(Qt.PointingHandCursor)
        
        controls_layout.addWidget(self.btn_start)
        controls_layout.addWidget(self.btn_pause)
        controls_layout.addWidget(self.btn_stop)
        panel_layout.addLayout(controls_layout)

        # --- Separator ---
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setStyleSheet("background: rgba(0, 80, 120, 0.15); max-height: 1px;")
        panel_layout.addWidget(separator1)

        # --- ELO Section ---
        elo_section = QLabel("Engine Strength")
        elo_section.setObjectName("sectionLabel")
        panel_layout.addWidget(elo_section)
        
        elo_display_layout = QHBoxLayout()
        elo_display_layout.addWidget(QLabel("ELO Rating:"))
        elo_display_layout.addStretch()
        
        self.elo_label = QLabel("2850")
        self.elo_label.setObjectName("eloValue")
        elo_display_layout.addWidget(self.elo_label)
        panel_layout.addLayout(elo_display_layout)
        
        self.elo_slider = QSlider(Qt.Horizontal)
        self.elo_slider.setMinimum(1350)
        self.elo_slider.setMaximum(2850)
        self.elo_slider.setValue(2850)
        self.elo_slider.setTickPosition(QSlider.TicksBelow)
        self.elo_slider.setTickInterval(150)
        self.elo_slider.valueChanged.connect(self.update_elo)
        panel_layout.addWidget(self.elo_slider)
        
        # ELO Range labels
        elo_range = QHBoxLayout()
        elo_min = QLabel("1350")
        elo_min.setStyleSheet("font-size: 10px; color: #5A8A9A;")
        elo_max = QLabel("2850")
        elo_max.setStyleSheet("font-size: 10px; color: #5A8A9A;")
        elo_range.addWidget(elo_min)
        elo_range.addStretch()
        elo_range.addWidget(elo_max)
        panel_layout.addLayout(elo_range)

        # --- Separator ---
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setStyleSheet("background: rgba(0, 80, 120, 0.15); max-height: 1px;")
        panel_layout.addWidget(separator2)

        # --- Timing Section ---
        timing_label = QLabel("Human Behavior")
        timing_label.setObjectName("sectionLabel")
        panel_layout.addWidget(timing_label)
        
        delay_layout = QHBoxLayout()
        delay_layout.setSpacing(16)
        
        min_container = QVBoxLayout()
        min_container.addWidget(QLabel("Min Delay"))
        self.min_delay_spin = QDoubleSpinBox()
        self.min_delay_spin.setRange(0.0, 5.0)
        self.min_delay_spin.setSingleStep(0.1)
        self.min_delay_spin.setValue(0.1)
        self.min_delay_spin.setSuffix(" s")
        self.min_delay_spin.valueChanged.connect(self.update_delay)
        min_container.addWidget(self.min_delay_spin)
        
        max_container = QVBoxLayout()
        max_container.addWidget(QLabel("Max Delay"))
        self.max_delay_spin = QDoubleSpinBox()
        self.max_delay_spin.setRange(0.0, 10.0)
        self.max_delay_spin.setSingleStep(0.1)
        self.max_delay_spin.setValue(0.5)
        self.max_delay_spin.setSuffix(" s")
        self.max_delay_spin.valueChanged.connect(self.update_delay)
        max_container.addWidget(self.max_delay_spin)
        
        delay_layout.addLayout(min_container)
        delay_layout.addLayout(max_container)
        delay_layout.addStretch()
        panel_layout.addLayout(delay_layout)
        
        # Bullet Mode
        self.bullet_check = QCheckBox("⚡ Bullet Mode (Smart Timing)")
        self.bullet_check.setToolTip("Ultra-fast openings, variable midgame, occasional hesitations")
        self.bullet_check.stateChanged.connect(self.update_bullet_mode)
        panel_layout.addWidget(self.bullet_check)

        main_layout.addWidget(glass_panel)

        # === LOGS SECTION ===
        logs_label = QLabel("📋 Live Logs")
        logs_label.setObjectName("sectionLabel")
        logs_label.setStyleSheet("color: white; font-size: 13px;")
        main_layout.addWidget(logs_label)
        
        self.log_text = QTextEdit()
        self.log_text.setObjectName("logArea")
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(120)
        self.log_text.setMaximumHeight(180)
        main_layout.addWidget(self.log_text)

    def update_status_style(self, state):
        """Update status label appearance based on state."""
        styles = {
            "running": ("● RUNNING", "#2A6A32", "#C8F0C8"),
            "paused": ("● PAUSED", "#8A5A00", "#FFF0C0"),
            "stopped": ("● OFFLINE", "#6A2A2A", "#F0C8C8"),
        }
        text, color, bg = styles.get(state, styles["stopped"])
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"""
            QLabel#statusLabel {{
                color: {color};
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {bg},
                    stop:1 rgba(255, 255, 255, 0.9));
                padding: 8px 24px;
                border-radius: 16px;
                border: 1px solid rgba(0, 0, 0, 0.1);
                font-size: 14px;
                font-weight: bold;
            }}
        """)

    def emit_log(self, message):
        self.log_signal.new_log.emit(message)

    def append_log(self, message):
        self.log_text.append(f"› {message}")
        sb = self.log_text.verticalScrollBar()
        sb.setValue(sb.maximum())

    def start_bot(self):
        self.bot.start()
        self.update_ui_state(running=True)
        self.update_status_style("running")

    def stop_bot(self):
        self.bot.stop()
        self.update_ui_state(running=False)
        self.update_status_style("stopped")

    def toggle_pause(self):
        self.bot.toggle_pause()
        if self.bot.is_paused:
            self.btn_pause.setText("▶ Resume")
            self.update_status_style("paused")
        else:
            self.btn_pause.setText("⏸ Pause")
            self.update_status_style("running")

    def update_ui_state(self, running):
        self.btn_start.setEnabled(not running)
        self.btn_stop.setEnabled(running)
        self.btn_pause.setEnabled(running)
        if not running:
            self.btn_pause.setText("⏸ Pause")

    def update_elo(self):
        elo = self.elo_slider.value()
        self.elo_label.setText(str(elo))
        self.bot.set_elo(elo)

    def update_delay(self):
        min_d = self.min_delay_spin.value()
        max_d = self.max_delay_spin.value()
        if min_d > max_d:
            max_d = min_d
            self.max_delay_spin.setValue(max_d)
        self.bot.set_humanization_delay(min_d, max_d)

    def update_bullet_mode(self, state):
        enabled = state == Qt.CheckState.Checked.value
        self.bot.set_bullet_mode(enabled)
        self.min_delay_spin.setEnabled(not enabled)
        self.max_delay_spin.setEnabled(not enabled)


if __name__ == "__main__":
    import subprocess
    import os
    import atexit

    # Start the Flask server in the background
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(script_dir, "server.py")
    
    print(f"Starting server from: {server_path}")
    server_process = subprocess.Popen([sys.executable, server_path], cwd=script_dir)

    def cleanup():
        print("Stopping server...")
        server_process.terminate()
        server_process.wait()

    atexit.register(cleanup)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Apply Frutiger Aero stylesheet
    app.setStyleSheet(AERO_STYLESHEET)
    
    # Import bot AFTER QApplication to avoid DPI context conflict
    from bot_controller import bot
    
    window = MainWindow(bot)
    window.show()
    
    sys.exit(app.exec())
