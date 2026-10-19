import csv

class Recorder:
    FIELDS = ["t", "temp", "pressure", "humidity", "pot", "enc"]  # Define the fields for the CSV file

    def __init__(self):
        self.recording = False
        self.data = []  # Initialize an empty list to store data points

    def start_recording(self, path):
        self.recording = True
        self._file = open(path, 'w', newline='')  # Open the file for writing
        self._writer = csv.DictWriter(self._file, fieldnames=self.FIELDS)
        self._writer.writeheader()  # Write the header
        self.data = []  # Clear previous data

    def stop_recording(self):
        self.recording = False
        if hasattr(self, '_file'):
            self._file.close()
        if hasattr(self, '_writer'):
            self._writer = None

    def record_data(self, data_point):
        if self.recording:
            self._writer.writerow(data_point)
            self.data.append(data_point)

    def save_to_file(self, filename):
        if not self.data:
            print("No data to save.")
            return
        with open(filename, 'w') as f:
            for data_point in self.data:
                f.write(f"{data_point}\n")