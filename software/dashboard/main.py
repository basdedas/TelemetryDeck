import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QComboBox, QLabel, QMainWindow, QPushButton, QSpinBox, QVBoxLayout, QVBoxLayout, QWidget, QWidget
import pyqtgraph as pg
from collections import deque
import serial.tools.list_ports
from datetime import datetime
from pathlib import Path

from recorder import Recorder
from workers import FakeWorker, SerialWorker

class MainWindow(QMainWindow):        
    LOG_DIR = Path(__file__).parent / "logs"                            # Define the logs directory

    def __init__(self):
        super().__init__()

        # Connect the UI elements to their respective slots
        uic.loadUi("dashboard.ui", self)                                # Load the UI from the .ui file
        self.worker = None
        refresh_button = self.findChild(QPushButton, "refresh_button")
        port_combo = self.findChild(QComboBox, "port_combo")
        connect_button = self.findChild(QPushButton, "connect_button")
        interval_spin = self.findChild(QSpinBox, "interval_spin")
        clear_button = self.findChild(QPushButton, "clear_button")
        pause_button = self.findChild(QPushButton, "pause_button")
        status_label = self.findChild(QLabel, "status_label")
        record_button = self.findChild(QPushButton, "record_button")
        
        refresh_button.clicked.connect(self.refresh_ports)
        port_combo.clear()
        connect_button.clicked.connect(self.connect)
        status_label.setText("Disconnected")

        clear_button.clicked.connect(self.clear_buffers)                # Connect the clear button to the clear_buffers
        pause_button.toggled.connect(self.pause_resume)                 # Connect the toggle state to the pause_resume method
        self.paused = False

        self.refresh_ports()                                            # Refresh the ports when the application starts
        self.interval_spin.setKeyboardTracking(False)                   # Disable keyboard tracking to avoid rapid updates
        self.interval_spin.valueChanged.connect(self.set_interval)      # Connect the interval spin box to the set_interval method        

        self.recorder = Recorder()                                         # Initialize the Recorder instance
        record_button.toggled.connect(self.toggle_recording)                # Connect the record button toggle to the toggle_recording method
        self.LOG_DIR.mkdir(exist_ok=True)                                    # Create the logs directory if it doesn't exist

        # Initialize the UI
        KEYS = ["t", "temp", "pressure", "humidity", "pot", "enc"]      # All the keys we expect from the data, in order
        COLORS = ['r', 'g', 'b', 'orange', 'm']                         # Colors for the plots
        
        self.buffers = {key: deque(maxlen=100) for key in KEYS}         # Store the last 500 samples for each key
        self.plots = {}
        self.curves = {}

        for key, color in zip(KEYS[1:], COLORS):
            plot = getattr(self, f"plot_{key}")
            plot.setTitle(key)
            plot.setLabel("left", key)
            plot.setLabel("bottom", "Time (s)")

            plot.setMouseEnabled(x=False, y=True)  # Enable mouse interaction for panning only
            plot.showGrid(x=True, y=True)  # Show grid lines for better readability
            plot.setBackground(None)  # Set background color to white

            self.plots[key] = plot
            self.curves[key] = plot.plot(pen=color)

    def clear_buffers(self):
        for key in self.buffers:
            self.buffers[key].clear()
        for curve in self.curves.values():
            curve.setData([], [])                                       # Clear the plot data

    def on_sample(self, data):

        if self.sender() is not self.worker:
            return                                                      # Ignore data from any worker that is not the current one
        for key in self.buffers:
            self.buffers[key].append(data[key])
        self.recorder.record_data(data)
        if not self.paused:
            self.redraw()

    def refresh_ports(self):
        port_combo = self.findChild(QComboBox, "port_combo")
        port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            port_combo.addItem(port.device)
        port_combo.addItem("Fake")                                     # Add the Fake option for testing without hardware

    def connect(self):
        port_combo = self.findChild(QComboBox, "port_combo")
        selected_port = port_combo.currentText()
        if selected_port:
            self.record_button.setChecked(False)
            if self.worker is not None:
                self.worker.data.disconnect(self.on_sample)
                self.worker.stop()
            if selected_port == "Fake":
                self.worker = FakeWorker()
            else:
                self.worker = SerialWorker(selected_port, 115200)            
            self.interval_spin.blockSignals(True)
            self.interval_spin.setValue(100)
            self.interval_spin.blockSignals(False)
            self.worker.data.connect(self.on_sample)
            self.clear_buffers()                                       # Clear buffers when connecting to a new port
            self.worker.start()
            self.status_label.setText(f"Connected to {selected_port}")

    def set_interval(self, value):
        if self.worker is not None:
            self.worker.set_interval(value)

    def redraw(self):
       x = list(self.buffers["t"])
       for key, curve in self.curves.items():
           curve.setData(x, list(self.buffers[key]))

    def pause_resume(self, checked):
       self.paused = checked
       self.pause_button.setText("Resume" if checked else "Pause")
       if not checked:
           self.redraw()

    def closeEvent(self, event):
        self.recorder.stop_recording()
        if self.worker:
            self.worker.stop()
        event.accept()

    def toggle_recording(self, checked):
        if checked:
            self.LOG_DIR.mkdir(exist_ok=True)
            name = datetime.now().strftime("telemetry_%Y-%m-%d_%H-%M-%S.csv")
            self.recorder.start_recording(self.LOG_DIR / name)
            self.record_button.setText("Stop")
            self.record_label.setText(f"Recording: {name}")
        else:
            self.recorder.stop_recording()
            self.record_button.setText("Record")
            self.record_label.setText("Not recording")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())