import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QSlider, 
                               QTextEdit, QGroupBox, QDoubleSpinBox)
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QFont

# Defer import to avoid DPI context conflict
# from bot_controller import bot 

class LogSignal(QObject):
    new_log = Signal(str)

class MainWindow(QMainWindow):
    def __init__(self, bot_instance):
        super().__init__()
        self.bot = bot_instance # Store bot instance
        self.setWindowTitle("Chess Bot Controller")
        self.resize(500, 600)
        
        # Signal for thread-safe logging
        self.log_signal = LogSignal()
        self.log_signal.new_log.connect(self.append_log)
        self.bot.set_log_callback(self.emit_log)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # --- Status Section ---
        self.status_label = QLabel("Status: STOPPED")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.status_label.setStyleSheet("color: red;")
        layout.addWidget(self.status_label)

        # --- Controls Section ---
        controls_group = QGroupBox("Controls")
        controls_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("Start")
        self.btn_start.clicked.connect(self.start_bot)
        self.btn_start.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        
        self.btn_pause = QPushButton("Pause")
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setStyleSheet("padding: 10px;")
        
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.clicked.connect(self.stop_bot)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 10px;")

        controls_layout.addWidget(self.btn_start)
        controls_layout.addWidget(self.btn_pause)
        controls_layout.addWidget(self.btn_stop)
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)

        # --- Settings Section ---
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout()

        # ELO Slider
        elo_layout = QHBoxLayout()
        elo_layout.addWidget(QLabel("ELO Rating:"))
        self.elo_label = QLabel("2850")
        elo_layout.addWidget(self.elo_label)
        settings_layout.addLayout(elo_layout)

        self.elo_slider = QSlider(Qt.Horizontal)
        self.elo_slider.setMinimum(1350)
        self.elo_slider.setMaximum(2850)
        self.elo_slider.setTickPosition(QSlider.TicksBelow)
        self.elo_slider.setTickInterval(100)
        
        # Set initial value BEFORE connecting signal to avoid premature log calls
        self.elo_slider.setValue(2850)
        
        # Now connect the signal after initial value is set
        self.elo_slider.valueChanged.connect(self.update_elo)
        settings_layout.addWidget(self.elo_slider)

        # Humanization Delay
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("Humanization Delay (s):"))
        
        self.min_delay_spin = QDoubleSpinBox()
        self.min_delay_spin.setRange(0.0, 5.0)
        self.min_delay_spin.setSingleStep(0.1)
        self.min_delay_spin.setValue(0.1)
        self.min_delay_spin.setPrefix("Min: ")
        self.min_delay_spin.valueChanged.connect(self.update_delay)
        
        self.max_delay_spin = QDoubleSpinBox()
        self.max_delay_spin.setRange(0.0, 10.0)
        self.max_delay_spin.setSingleStep(0.1)
        self.max_delay_spin.setValue(0.5)
        self.max_delay_spin.setPrefix("Max: ")
        self.max_delay_spin.valueChanged.connect(self.update_delay)

        delay_layout.addWidget(self.min_delay_spin)
        delay_layout.addWidget(self.max_delay_spin)
        settings_layout.addLayout(delay_layout)

        # Bullet Mode Checkbox
        from PySide6.QtWidgets import QCheckBox
        self.bullet_check = QCheckBox("Bullet Mode (Smart Timing)")
        self.bullet_check.setToolTip("Optimized for Bullet games: Ultra fast openings, variable midgame delays.")
        self.bullet_check.stateChanged.connect(self.update_bullet_mode)
        settings_layout.addWidget(self.bullet_check)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # --- Logs Section ---
        log_group = QGroupBox("Logs")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #222; color: #0f0; font-family: Consolas;")
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

    def emit_log(self, message):
        self.log_signal.new_log.emit(message)

    def append_log(self, message):
        self.log_text.append(message)
        # Auto scroll
        sb = self.log_text.verticalScrollBar()
        sb.setValue(sb.maximum())

    def start_bot(self):
        self.bot.start()
        self.update_ui_state(running=True)
        self.status_label.setText("Status: RUNNING")
        self.status_label.setStyleSheet("color: green;")

    def stop_bot(self):
        self.bot.stop()
        self.update_ui_state(running=False)
        self.status_label.setText("Status: STOPPED")
        self.status_label.setStyleSheet("color: red;")

    def toggle_pause(self):
        self.bot.toggle_pause()
        if self.bot.is_paused:
            self.btn_pause.setText("Resume")
            self.status_label.setText("Status: PAUSED")
            self.status_label.setStyleSheet("color: orange;")
        else:
            self.btn_pause.setText("Pause")
            self.status_label.setText("Status: RUNNING")
            self.status_label.setStyleSheet("color: green;")

    def update_ui_state(self, running):
        self.btn_start.setEnabled(not running)
        self.btn_stop.setEnabled(running)
        self.btn_pause.setEnabled(running)
        self.elo_slider.setEnabled(True) # Always allow changing ELO

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
        enabled = state == 2 # Qt.Checked is 2
        self.bot.set_bullet_mode(enabled)
        
        # Disable manual delay spinners if Bullet Mode is on
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
    
    # Import bot AFTER QApplication to avoid DPI context conflict
    from bot_controller import bot
    
    # Dark Mode Style
    app.setStyle("Fusion")
    
    window = MainWindow(bot)
    window.show()
    
    sys.exit(app.exec())
