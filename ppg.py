import time
import serial
import sys
from pyshimmer import ShimmerBluetooth, DEFAULT_BAUDRATE, DataPacket, EChannelType
from pyshimmer.dev.channels import ChDataTypeAssignment, ChannelDataType, EChannelType, ESensorGroup



participant_id = sys.argv[1] if len(sys.argv) > 1 else "test"
experiment_id = sys.argv[2] if len(sys.argv) > 2 else "test"
DATA_FILE = f"./data/{experiment_id}/participant_{participant_id}_ppg_data.csv"


def handler(pkt: DataPacket, file_handle, start_time_holder) -> None:
    try:
        cur_value = pkt[EChannelType.INTERNAL_ADC_13]
        packet_timestamp = pkt[EChannelType.TIMESTAMP]        
    except KeyError:
        print("Warning: PPG data not found in packet.")
        return

    if start_time_holder["start_time"] is None:
        start_time_holder["start_time"] = packet_timestamp


    # elapsed_time = (packet_timestamp - start_time_holder["start_time"])/32768.0
    print(f"Time: {packet_timestamp:.2f}s | PPG: {cur_value}")

    # Write data to disk immediately
    file_handle.write(f"{packet_timestamp:.4f},{cur_value}\n")
    file_handle.flush()  # ensures data is actually written

if __name__ == '__main__':
    # Open the file in write mode (or "a" if you want to append)
    with open(DATA_FILE, "w", buffering=1) as f:
        f.write("TimeStamp,PPG(mV)\n")  # header line

        try:
            
            serial_conn = serial.Serial('COM3', DEFAULT_BAUDRATE)
            shim_dev = ShimmerBluetooth(serial_conn)
            shim_dev.initialize()

            shim_dev.set_sampling_rate(512.0)

            print(f"Starting PPG data collection for Participant {participant_id}...")
            # We'll store the start time in a mutable dict so the handler can update it
            start_time_holder = {"start_time": None}
            
            # Add a lambda or partial so we can pass 'f' and 'start_time_holder' to the handler
            shim_dev.add_stream_callback(
                lambda pkt: handler(pkt, f, start_time_holder)
            )
            shim_dev.start_streaming()
            # status = shim_dev.get_status()
            # print(status)
            # sampling_rate = shim_dev.get_sampling_rate()
            # print(f"Sampling rate: {sampling_rate} Hz")
            # # shim_dev.set_rtc(time.time())
            # print(shim_dev.get_data_types())

            # main loop
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\nStopping PPG data collection...")
            shim_dev.stop_streaming()
            # shim_dev.shutdown()
        finally:
            print(f"\n✅ Data continuously saved to {DATA_FILE}.")


# if __name__ == '__main__':
#     serial = Serial('COM8', DEFAULT_BAUDRATE)
#     shim_dev = ShimmerBluetooth(serial)


#     # shim_dev.shutdown()
#     shim_dev.initialize()

    
#     shim_dev.set_sensors([
#         ESensorGroup.CH_A12,  # PPG 1
#         ESensorGroup.CH_A13,  # PPG 2
#         ESensorGroup.CH_A14,  # PPG 3
#          ESensorGroup.EXG1_16BIT
#     ])



#     dev_name = shim_dev.get_device_name()
#     print(f'My name is: {dev_name}')

#     shim_dev.add_stream_callback(handler)

#     shim_dev.start_streaming()
#     time.sleep(5.0)
#     shim_dev.stop_streaming()

#     shim_dev.shutdown()