import time
import serial
import sys
import numpy as np
from pyshimmer import ShimmerBluetooth, DEFAULT_BAUDRATE, DataPacket, EChannelType

# Get participant ID from command-line argument
participant_id = sys.argv[1] if len(sys.argv) > 1 else "unknown"

# Define output filename
DATA_FILE = f"./data/participant_{participant_id}_ppg_data.txt"

timestamps = []
ppg_values = []
start_time = None

def handler(pkt: DataPacket) -> None:
    global start_time
    try:
        cur_value = pkt[EChannelType.INTERNAL_ADC_13]

        if start_time is None:
            start_time = time.time()

        elapsed_time = time.time() - start_time
        timestamps.append(elapsed_time)
        ppg_values.append(cur_value)

        print(f'Time: {elapsed_time:.2f}s | PPG: {cur_value}')

    except KeyError:
        print("Warning: PPG data not found in packet.")

if __name__ == '__main__':
    serial_conn = None
    try:
        serial_conn = serial.Serial('COM8', DEFAULT_BAUDRATE, timeout=1)
        shim_dev = ShimmerBluetooth(serial_conn)
        shim_dev.initialize()

        print(f"Starting PPG data collection for Participant {participant_id}...")
        shim_dev.add_stream_callback(handler)
        shim_dev.start_streaming()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping PPG data collection...")
    finally:
        if timestamps and ppg_values:
            with open(DATA_FILE, "w") as file:
                file.write("Time(s),PPG(mV)\n")
                for t, p in zip(timestamps, ppg_values):
                    file.write(f"{t:.4f},{p}\n")

            print(f"✅ PPG data saved to {DATA_FILE}.")
