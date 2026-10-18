import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QVBoxLayout, QWidget, QWidget
import pyqtgraph as pg
from collections import deque

from workers import FakeWorker, SerialWorker

class MainWindow(QMainWindow):        

    def __init__(self):
        super().__init__()
        uic.loadUi("dashboard.ui", self)                                # Load the UI from the .ui file

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

        self.worker = SerialWorker("COM3", 115200)
        self.worker.data.connect(self.on_sample)
        self.worker.start()

    def on_sample(self, data):
        for key in self.buffers:
            self.buffers[key].append(data[key])

        x = list(self.buffers["t"])                                     # take time seperately because it's shared
        for key, curve in self.curves.items():
            curve.setData(x, list(self.buffers[key]))
            
    def closeEvent(self, event):
        self.worker.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
