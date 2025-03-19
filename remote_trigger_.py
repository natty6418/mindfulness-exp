#!/usr/bin/env python3
"""
Module: array_example.py
Author: Pi Ko (pi.ko@nyu.edu)

This script demonstrates how to control two bHaptics vests using matrix representation.
The matrix layout represents two vests side by side, where each panel is represented
in its physical 4x5 layout (4 columns x 5 rows).

Front/Back Panel Physical Layout:
[0]  [1]  [2]  [3]
[4]  [5]  [6]  [7]
[8]  [9]  [10] [11]
[12] [13] [14] [15]
[16] [17] [18] [19]

Each row in the patterns represents a time step, and each motor position contains
an intensity value (0-100).
"""

from time import sleep
from haptics_motor_control import activate_discrete, player

from haptics_pattern_player import load_and_play_tact_file

# Play a .tact file pattern

import socket
import sys

participant_id = sys.argv[1] if len(sys.argv) > 1 else "unknown"
LOG_FILE = f"participant_{participant_id}_trigger_log.txt"

HOST = ''         # Empty string means to listen on all available interfaces
PORT = 65432      # Choose an appropriate port that is open on your firewall




# Alternating Pattern (4 time steps)
import time




if __name__ == "__main__":
    try:
        # example_wave_pattern()
        # while True:
        #     time.sleep(5)
        # body_scan_pattern("left_abdomen", 5000)
        # time.sleep(10)
        # body_scan_pattern("right_shoulder", 5000)
        # time.sleep(10)
        # body_scan_pattern("right_abdomen", 5000)
        # time.sleep(10)
        # body_scan_pattern("left_abdomen", 5000)
        # time.sleep(10)
        
        
        
        
        # body_scan_pattern("left_abdomen", 5000)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            print(f"Server listening on port {PORT}...")

            conn, addr = server_socket.accept()  # Wait for a client connection
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)  # Adjust buffer size as needed
                    if not data:
                        break  # Connection closed by the client
                        
                    trigger_event = data.decode()
                    print(f"Received trigger: {trigger_event}")

                    with open(LOG_FILE, "a") as log:
                        log.write(f"{time.time()},{trigger_event}\n")
                    # Here you can add the code to send the signal to your haptic jacket via Bluetooth
                    # print("Received trigger:", data.decode())
                    if data.decode() == "inhale":
                        print("Running wave pattern...")
                        load_and_play_tact_file("inhale", "inhale.tact")
                        time.sleep(4)
                    elif data.decode() == "exhale":
                        print("Running wave pattern...")
                        load_and_play_tact_file("exhale", "exhale.tact")
                        time.sleep(8)
                    elif data.decode() == "left_shoulder":
                        print("Running left shoulder pattern...")
                        load_and_play_tact_file("left_shoulder", "left_shoulder.tact")
                        time.sleep(8)
                    elif data.decode() == "left_abdomen":
                        print("Running left abdomen pattern...")
                        load_and_play_tact_file("left_abdomen", "left_abdomen.tact")
                        time.sleep(9)
                    elif data.decode() == "right_shoulder":
                        print("Running right shoulder pattern...")
                        load_and_play_tact_file("right_shoulder", "right_shoulder.tact")
                        time.sleep(8)
                    elif data.decode() == "right_abdomen":
                        print("Running right abdomen pattern...")
                        load_and_play_tact_file("right_abdomen", "right_abdomen.tact")
                        time.sleep(9)
                    elif data.decode() == "left_chest":
                        print("Running left chest pattern...")
                        load_and_play_tact_file("left_chest", "left_chest.tact")
                        time.sleep(9)
                    elif data.decode() == "right_chest":
                        print("Running right chest pattern...")
                        load_and_play_tact_file("right_chest", "right_chest.tact")
                        time.sleep(9)
                    elif data.decode() == "left_lower_back":
                        print("Running left lower back pattern...")
                        load_and_play_tact_file("left_lower_back", "left_lower_back.tact")
                        time.sleep(8)
                    elif data.decode() == "right_lower_back":
                        print("Running right lower back pattern...")
                        load_and_play_tact_file("right_lower_back", "right_lower_back.tact")
                        time.sleep(8)
                    else:
                        print("Invalid trigger:", data.decode())
        
    except KeyboardInterrupt:
        print("\nServer shutdown requested")
        exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("\nExecution complete.") 