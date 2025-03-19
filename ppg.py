import time
import serial
import numpy as np
from pyshimmer import ShimmerBluetooth, DEFAULT_BAUDRATE, DataPacket, EChannelType

# File to save PPG data
DATA_FILE = "ppg_data.txt"

# Data storage
timestamps = []
ppg_values = []
start_time = None

# Callback function to handle incoming PPG data
def handler(pkt: DataPacket) -> None:
    global start_time
    try:
        cur_value = pkt[EChannelType.INTERNAL_ADC_13]  # Try PPG_A12 if needed

        # Initialize start time
        if start_time is None:
            start_time = time.time()

        # Record elapsed time
        elapsed_time = time.time() - start_time
        timestamps.append(elapsed_time)
        ppg_values.append(cur_value)

        print(f'Time: {elapsed_time:.2f}s | PPG: {cur_value}')

    except KeyError:
        print("Warning: PPG data not found in packet")

if __name__ == '__main__':
    serial_conn = None
    try:
        serial_conn = serial.Serial('COM9', DEFAULT_BAUDRATE, timeout=1)

        shim_dev = ShimmerBluetooth(serial_conn)
        shim_dev.initialize()

        dev_name = shim_dev.get_device_name()
        print(f'My name is: {dev_name}')

        shim_dev.add_stream_callback(handler)
        print("Starting PPG data stream... Press Ctrl+C to stop.")
        shim_dev.start_streaming()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected! Stopping PPG data stream...")
    except serial.SerialException as e:
        print(f"Serial connection error: {e}")
    except Exception as ex:
        print(f"Unexpected error: {ex}")
    finally:
        if 'shim_dev' in locals():
            try:
                shim_dev.stop_streaming()
                shim_dev.shutdown()
                print("Shimmer device disconnected.")
            except Exception as e:
                print(f"Error while stopping shimmer: {e}")

        if serial_conn:
            try:
                serial_conn.close()
                print("Serial connection closed.")
            except Exception as e:
                print(f"Error while closing serial connection: {e}")

        print("Exiting program.")

        # ✅ Save Data to File
        if timestamps and ppg_values:
            with open(DATA_FILE, "w") as file:
                file.write("Time(s),PPG(mV)\n")  # Header
                for t, p in zip(timestamps, ppg_values):
                    file.write(f"{t:.4f},{p}\n")

            print(f"\n✅ PPG data saved to {DATA_FILE}. You can now import it for analysis.")
