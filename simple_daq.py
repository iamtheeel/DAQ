import datetime
import queue
import numpy as np
import nidaqmx

from nidaqmx.constants import AcquisitionType
from nidaqmx.stream_readers import AnalogMultiChannelReader


class SimpleDAQ:
    def __init__(self, config):
        self.config = config
        self.task = None
        self.reader = None
        self.data_queue = queue.Queue()

        self.device = config["daq"]["device"]
        self.sample_rate_hz = config["daq"]["sample_rate_hz"]
        self.samples_per_callback = config["daq"]["samples_per_callback"]
        self.buffer_seconds = config["daq"].get("buffer_seconds", 5)

        self.channels = [
            ch for ch in config["channels"]
            if ch.get("enabled", True)
        ]

        self.num_channels = len(self.channels)

        if self.num_channels == 0:
            raise ValueError("No enabled channels in config file.")

    def setup(self):
        self.task = nidaqmx.Task()

        for ch in self.channels:
            physical_name = f"{self.device}/{ch['physical_channel']}"

            self.task.ai_channels.add_ai_voltage_chan(
                physical_name,
                name_to_assign_to_channel=ch["name"],
                min_val=ch.get("min_v", -10.0),
                max_val=ch.get("max_v", 10.0),
            )

        samples_per_buffer = int(
            self.sample_rate_hz * self.buffer_seconds
        )

        self.task.timing.cfg_samp_clk_timing(
            rate=self.sample_rate_hz,
            sample_mode=AcquisitionType.CONTINUOUS,
            samps_per_chan=samples_per_buffer,
        )

        self.reader = AnalogMultiChannelReader(
            self.task.in_stream
        )

        self.task.register_every_n_samples_acquired_into_buffer_event(
            self.samples_per_callback,
            self.daq_callback,
        )

    def daq_callback(
        self,
        task_handle,
        every_n_samples_event_type,
        number_of_samples,
        callback_data,
    ):
        timestamp = datetime.datetime.now()

        data = np.zeros(
            (self.num_channels, number_of_samples),
            dtype=np.float64,
        )

        self.reader.read_many_sample(
            data,
            number_of_samples_per_channel=number_of_samples,
        )

        try:
            self.data_queue.put_nowait((timestamp, data))
        except queue.Full:
            pass

        return 0

    def start(self):
        if self.task is None:
            self.setup()

        self.task.start()

    def stop(self):
        if self.task is not None:
            self.task.stop()
            self.task.close()
            self.task = None

    def get_chunk(self, timeout=1.0):
        return self.data_queue.get(timeout=timeout)

    def channel_names(self):
        return [ch["name"] for ch in self.channels]