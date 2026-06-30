'''
    Writing the datafile.
    Output type: csv
'''
import csv
from datetime import datetime
from pathlib import Path

class WriteCSV:
    def __init__(self, channel_info, config):
        # Set our configuration parameters
        init_time_Stamp = datetime.now().strftime("%y%m%d-%H%M%S")
        base_name = Path(config["data"]["file_name"])
        self.file_name = f"{init_time_Stamp}_{base_name.stem}{base_name.suffix}"

        self.sample_rate_hz = config["daq"]["sample_rate_hz"]
        self.dt_ms = 1000.0 / self.sample_rate_hz
        self.sample_number = 0

        self.channel_info = channel_info

        # Open the CSV file for writing and write the header row
        header = ["Time (ms)"]
        for ch in channel_info: header.append(f"{ch['name']} ({ch['units']})")

        self.file = open(self.file_name, "w", newline="")
        self.writer = csv.writer(self.file)
        self.writer.writerow(header)
        #self.writer.writerow(["Time (ms)"] + self.channel_names)


    def write_chunk(self, data):
        num_channels, num_samples = data.shape

        for sample_index in range(num_samples):
            time_ms = self.sample_number * self.dt_ms

            row = [time_ms]

            for channel_index in range(num_channels):
                row.append(data[channel_index, sample_index])

            self.writer.writerow(row)

            self.sample_number += 1

    def close(self):
        self.file.close()