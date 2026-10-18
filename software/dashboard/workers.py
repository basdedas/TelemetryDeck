import math
import random
import PyQt5.QtCore as QtCore
import sys
import serial

def parse_line(raw: bytes):
    """Turn one raw serial line into a dict, or None if it is not a data line."""
    line = raw.decode("ascii", errors="ignore").strip()
    if not line or line.startswith("#"):
        return None

    parts = line.split(",")
    if len(parts) != 6:
        return None
    
    try:
        return {
            "t": int(parts[0]) / 1000,      # ms -> seconds
            "temp": float(parts[1]),
            "pressure": float(parts[2]),
            "humidity": float(parts[3]),    # "nan" parses fine (BMP280)
            "pot": int(parts[4]),
            "enc": int(parts[5]),
        }
    except ValueError:
        return None

class FakeWorker(QtCore.QThread):
    data = QtCore.pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._running = True

    def run(self):
        ms = 0
        while self._running:
            self.msleep(100)
            ms += 100
            temp = 23 + 2 * math.sin(0.5 * ms / 1000) + random.uniform(-0.1, 0.1)           # Get some nice sine waves for random data generation.
            pressure = 1000 + 5  * math.sin(0.2 * ms / 1000) + random.uniform(-0.2, 0.2)
            humidity = 50   + 10 * math.sin(0.3 * ms / 1000) + random.uniform(-0.5, 0.5)
            pot      = int(512 + 511 * math.sin(0.5 * ms / 1000))
            enc      = int(ms / 1000 * 2)

            desired_line = f"{ms},{temp:.2f},{pressure:.2f},{humidity:.2f},{pot},{enc}"
            parsed_data = parse_line(desired_line.encode("ascii"))
            if parsed_data:
                self.data.emit(parsed_data)

    def stop(self):
        self._running = False
        self.wait()

class SerialWorker(QtCore.QThread):
    data = QtCore.pyqtSignal(dict)

    def __init__(self, port: str, baudrate: int = 115200):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self._running = True

    def run(self):
        import serial
        with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
            while self._running:
                line = ser.readline()
                parsed_data = parse_line(line)
                if parsed_data:
                    self.data.emit(parsed_data)

    def stop(self):
        self._running = False
        self.wait()