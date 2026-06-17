import time
import tomllib

from simple_daq import SimpleDAQ


def load_config(path="daq_config.toml"):
    with open(path, "rb") as f:
        return tomllib.load(f)


def main():
    config = load_config()

    daq = SimpleDAQ(config)

    duration_s = config["daq"]["duration_s"]

    print("Enabled channels:")
    for name in daq.channel_names():
        print(f"  {name}")

    print("Starting DAQ...")
    daq.start()

    start_time = time.time()

    try:
        while time.time() - start_time < duration_s:
            # Get a chunk of data from the DAQ with a timeout of 2 seconds
            # the number of samples in the chunk will be equal to samples_per_callback
            timestamp, data = daq.get_chunk(timeout=2.0)

            print(f"\n{timestamp}")

            for i, name in enumerate(daq.channel_names()):
                ch_data = data[i, :]
                print(
                    f"  {name}: "
                    f"min={ch_data.min(): .4f} V, "
                    f"max={ch_data.max(): .4f} V, "
                    f"mean={ch_data.mean(): .4f} V"
                )

    except KeyboardInterrupt:
        print("Interrupted by user.")

    finally:
        print("Stopping DAQ...")
        daq.stop()


if __name__ == "__main__":
    main()