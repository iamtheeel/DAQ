'''
DAQ: reads from a National Instruments DAQ device and writes to a CSV file.
'''
import time
import tomllib


from simple_daq import SimpleDAQ
from data_out import WriteCSV


def load_config(path="daq_config.toml"):
    with open(path, "rb") as f:
        return tomllib.load(f)


def main():
    config = load_config()

    daq = SimpleDAQ(config)

    duration_s = config["daq"]["duration_s"]

    print("Enabled channels:")
    for ch in daq.channel_info():
        print(f"  {ch['name']}, physical channel: {ch['physical_channel']}, units: {ch['units']}")

    data_out = WriteCSV(daq.channel_info(), config)
    print(f"Writing data to {data_out.file_name}")

    print("Starting DAQ...")
    daq.start()

    start_time = time.time()

    try:
        while time.time() - start_time < duration_s:
            # Get a chunk of data from the DAQ with a timeout of 2 seconds
            # the number of samples in the chunk will be equal to samples_per_callback
            timestamp, data = daq.get_chunk(timeout=2.0)
            data_out.write_chunk(data)

            print(f"\n{timestamp}")

            for i, ch in enumerate(daq.channel_info()):
                ch_data = data[i, :]
                print(
                    f"  {ch['name']}: "
                    f"min={ch_data.min(): .4f} {ch['units']}, "
                    f"max={ch_data.max(): .4f} {ch['units']}, "
                    f"mean={ch_data.mean(): .4f} {ch['units']}"
                )

        data_out.close()

    except KeyboardInterrupt:
        print("Interrupted by user.")

    finally:
        print("Stopping DAQ...")
        daq.stop()
        print(f"Closing data file {data_out.file_name}")
        data_out.close()


if __name__ == "__main__":
    main()