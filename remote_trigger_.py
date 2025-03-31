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

# participant_id = sys.argv[1] if len(sys.argv) > 1 else "unknown"
# LOG_FILE = f"./data/participant_{participant_id}_trigger_log.txt"

HOST = ''         # Empty string means to listen on all available interfaces
PORT = 65432      # Choose an appropriate port that is open on your firewall




# Alternating Pattern (4 time steps)
import time




if __name__ == "__main__":
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            print(f"Server listening on port {PORT}...")

            while True:
                try:
                    server_socket.settimeout(1.0)
                    
                    conn, addr = server_socket.accept()  # Wait for a client connection
                    # conn.settimeout(1.0)
                    with conn:
                        print(f"Connected by {addr}")
                        while True:
                            data = conn.recv(1024)
                            if not data:
                                print(f"Client {addr} disconnected.")
                                break  # Exit inner loop and wait for next connection

                            trigger_event = data.decode().strip()
                            print(f"Received trigger: {trigger_event}")

                            if trigger_event == "inhale":
                                print("Running wave pattern...")
                                load_and_play_tact_file("inhale", "inhale.tact")
                                time.sleep(4)
                            elif trigger_event == "exhale":
                                print("Running wave pattern...")
                                load_and_play_tact_file("exhale", "exhale.tact")
                                time.sleep(8)
                            elif trigger_event == "left_shoulder":
                                print("Running left shoulder pattern...")
                                load_and_play_tact_file("left_shoulder", "left_shoulder2.tact")
                                time.sleep(8)
                            elif trigger_event == "left_abdomen":
                                print("Running left abdomen pattern...")
                                load_and_play_tact_file("left_abdomen", "left_abdomen2.tact")
                                time.sleep(9)
                            elif trigger_event == "right_shoulder":
                                print("Running right shoulder pattern...")
                                load_and_play_tact_file("right_shoulder", "right_shoulder2.tact")
                                time.sleep(8)
                            elif trigger_event == "right_abdomen":
                                print("Running right abdomen pattern...")
                                load_and_play_tact_file("right_abdomen", "right_abdomen2.tact")
                                time.sleep(9)
                            elif trigger_event == "left_chest":
                                print("Running left chest pattern...")
                                load_and_play_tact_file("left_chest", "left_chest2.tact")
                                time.sleep(9)
                            elif trigger_event == "right_chest":
                                print("Running right chest pattern...")
                                load_and_play_tact_file("right_chest", "right_chest2.tact")
                                time.sleep(9)
                            elif trigger_event == "left_lower_back":
                                print("Running left lower back pattern...")
                                load_and_play_tact_file("left_lower_back", "left_lower_back2.tact")
                                time.sleep(8)
                            elif trigger_event == "right_lower_back":
                                print("Running right lower back pattern...")
                                load_and_play_tact_file("right_lower_back", "right_lower_back2.tact")
                                time.sleep(8)
                            else:
                                print("Invalid trigger:", trigger_event)
                except socket.timeout:
                    continue 

    except KeyboardInterrupt:
        print("\nServer shutdown requested")
        exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("\nExecution complete.")
