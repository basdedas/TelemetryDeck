import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QVBoxLayout, QWidget, QWidget
import pyqtgraph as pg
from collections import deque

from workers import FakeWorker, SerialWorker

class MainWindow(QMainWindow):        

    def __init__(self):
        super().__init__()

        # Initialize the UI
        KEYS = ["t", "temp", "pressure", "humidity", "pot", "enc"]      # All the keys we expect from the data, in order
        COLORS = ['r', 'g', 'b', 'c', 'm']                              # Colors for the plots
        
        self.buffers = {key: deque(maxlen=500) for key in KEYS}         # Store the last 500 samples for each key
        self.plots = {}
        self.curves = {}
        
        central = QWidget()
        layout = QVBoxLayout()

        for key, color in zip(KEYS[1:], COLORS):
            plot_widget = pg.PlotWidget(title=key)
            plot_widget.setLabel('left', key)
            plot_widget.setLabel('bottom', 'Time (s)')
            layout.addWidget(plot_widget)
            self.plots[key] = plot_widget
            self.curves[key] = plot_widget.plot(pen=color)
        
        central.setLayout(layout)
        self.setCentralWidget(central)

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
