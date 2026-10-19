import csv
from recorder import Recorder

def test_writes_rows(tmp_path):
    path = tmp_path / "out.csv"
    r = Recorder()
    r.start_recording(path)
    r.record_data({"t": 0.1, "temp": 24.0, "pressure": 970.0, "humidity": 45.0, "pot": 256, "enc": 0})
    r.record_data({"t": 0.2, "temp": 24.1, "pressure": 970.1, "humidity": 45.1, "pot": 257, "enc": -3})
    r.stop_recording()

    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert rows[1]["enc"] == "-3"