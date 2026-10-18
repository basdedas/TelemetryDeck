import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QComboBox, QMainWindow, QPushButton, QVBoxLayout, QVBoxLayout, QWidget, QWidget
import pyqtgraph as pg
from collections import deque
import serial.tools.list_ports

from workers import FakeWorker, SerialWorker

class MainWindow(QMainWindow):        

    def __init__(self):
        super().__init__()
        uic.loadUi("dashboard.ui", self)                                # Load the UI from the .ui file
        self.worker = None
        refresh_button = self.findChild(QPushButton, "refresh_button")
        refresh_button.clicked.connect(self.refresh_ports)
        port_combo = self.findChild(QComboBox, "port_combo")
        connect_button = self.findChild(QPushButton, "connect_button")
        connect_button.clicked.connect(self.connect)
        port_combo.clear()

        self.refresh_ports()                                            # Refresh the ports when the application starts
        
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

        x = list(self.buffers["t"])                                     # take time seperately because it's shared
        for key, curve in self.curves.items():
            curve.setData(x, list(self.buffers[key]))

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
            if self.worker is not None:
                self.worker.data.disconnect(self.on_sample)
                self.worker.stop()
            if selected_port == "Fake":
                self.worker = FakeWorker()
            else:
                self.worker = SerialWorker(selected_port, 115200)
            self.worker.data.connect(self.on_sample)
            self.clear_buffers()                                       # Clear buffers when connecting to a new port
            self.worker.start()
            
    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
