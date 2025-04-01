import subprocess
import time
import sys
import os
import socket
import threading

HOST = '127.0.0.1'
PORT = 30001  # You can choose any free port

participant_id = sys.argv[1] if len(sys.argv) > 1 else "unknown"
experiment_id = sys.argv[2] if len(sys.argv) > 2 else "test"

output_dir = f"./data/{experiment_id}/"
os.makedirs(output_dir, exist_ok=True)
video_filename = os.path.join(output_dir, f"participant_{participant_id}_video.mp4")
log_filename = os.path.join(output_dir, f"ffmpeg_{participant_id}.log")


ffmpeg_cmd = [
    'ffmpeg',
    '-f', 'dshow',
    '-i', 'video=Microsoft® LifeCam HD-3000',
    '-vcodec', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-preset', 'ultrafast',
    '-crf', '23',
    '-f', 'mp4',
    '-y',
    video_filename
]

def socket_server():
    """Server to listen for STOP command"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Listening for STOP signal on {HOST}:{PORT}")
        conn, _ = s.accept()
        with conn:
            data = conn.recv(1024)
            if data.decode().strip() == "STOP":
                print("\nReceived STOP signal. Stopping recording...")
                try:
                    if process and process.poll() is None:
                        process.stdin.write('q\n')
                        process.stdin.flush()
                        process.wait()
                        print("FFmpeg stopped gracefully.")
                except Exception as e:
                    print(f"Error stopping FFmpeg: {e}")

print(f"Starting FFmpeg recording... Output: {video_filename}")
process = None
log_file = None

try:
    log_file = open(log_filename, 'w')
    process = subprocess.Popen(
        ffmpeg_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=log_file,
        text=True,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )

    # Start IPC server in a separate thread
    threading.Thread(target=socket_server, daemon=True).start()

    # Wait for FFmpeg to finish
    process.wait()

except Exception as e:
    print(f"Error: {e}")

finally:
    if process and process.poll() is None:
        process.terminate()
    if log_file:
        log_file.close()

    print(f"Recording finalized: {video_filename}")
    print(f"FFmpeg logs saved to: {log_filename}")
