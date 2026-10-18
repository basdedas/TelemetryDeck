import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
import pyqtgraph as pg
from collections import deque

from workers import FakeWorker

class MainWindow(QMainWindow):        

    def __init__(self):
        super().__init__()
        self.t = deque(maxlen=500) # Store the last 500 data points
        self.temp_value = deque(maxlen=500)

        # Create a plot widget
        self.plot_widget = pg.PlotWidget()
        self.setCentralWidget(self.plot_widget)

        self.setWindowTitle("Real-time Data Plot")
        self.setGeometry(100, 100, 800, 600)
        self.curve = self.plot_widget.plot(pen='y')  # Yellow line for temperature
        self.update_plot()
        self.worker = FakeWorker()
        self.worker.data.connect(self.on_sample)
        self.worker.start()

    def update_plot(self):
        self.curve.setData(self.t, self.temp_value)

    def on_sample(self, data):
        self.t.append(data['t'])
        self.temp_value.append(data['temp'])  # Assuming you want to plot temperature
        self.update_plot()

    def closeEvent(self, event):
        self.worker.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
