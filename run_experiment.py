import subprocess
import time
import os
from datetime import datetime
import signal
import socket

def log_marker(event):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {event}")

# Prompt for participant ID
filename = "participants.txt"

# Read existing IDs
if os.path.exists(filename):
    with open(filename, "r") as f:
        participant_ids = set(f.read().splitlines())
else:
    participant_ids = set()

# Get new participant ID
participant_id = (input("Enter Participant ID: "))



while participant_id !="0" and participant_id in participant_ids:
    print("Participant ID already exists! Please enter a unique ID.")
    participant_id = (input("Enter Participant ID: "))

if participant_id !="0":
    participant_ids.add(participant_id)
    with open(filename, "a") as f:
        f.write(participant_id + "\n")
    print(f"Participant ID {participant_id} saved.")

experiment_id = (input("Enter Experiment ID: "))

while experiment_id not in set(["0","1","2","3"]):
    print("Experiment ID should be either 1, 2 or 3.")
    experiment_id = (input("Enter Experiment ID: "))

experiment = "test"
if experiment_id == "1": 
    experiment = "audio"
elif experiment_id == "2":
    experiment = "audio_robot"
else:
    experiment = "audio_robot_haptics"
# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Define log file paths
logs = {
    "stroop_out": f"./data/{experiment}/participant_{participant_id}_stroop_out.log",
    "stroop_err": f"./data/{experiment}/participant_{participant_id}_stroop_err.log",
    "video_out": f"./data/{experiment}/participant_{participant_id}_video_out.log",
    "video_err": f"./data/{experiment}/participant_{participant_id}_video_err.log",
    "ppg_out": f"./data/{experiment}/participant_{participant_id}_ppg_out.log",
    "ppg_err": f"./data/{experiment}/participant_{participant_id}_ppg_err.log",
    # "trigger_out": f"./data/participant_{participant_id}_trigger_out.log",
    # "trigger_err": f"./data/participant_{participant_id}_trigger_err.log",
    "qtrobot_out": f"./data/{experiment}/participant_{participant_id}_qtrobot_out.log",
    "qtrobot_err": f"./data/{experiment}/participant_{participant_id}_qtrobot_err.log",
}

log_marker(f"🧪 Starting experiment for Participant {participant_id}")
log_marker("▶ Starting video, and PPG recording...")

def start_process(script_name, log_out, log_err):
    log_marker(f"▶ Starting {script_name}...")
    return subprocess.Popen(
        ["python", script_name, participant_id, experiment],
        stdout=open(log_out, "w"),
        stderr=open(log_err, "w"),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
def stop_video():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', 65432))
            s.sendall(b"STOP")
            print("📩 Sent STOP signal to Video Recording.")
    except Exception as e:
        print(f"Failed to stop video: {e}")

video_proc = start_process("recordVideo.py", logs["video_out"], logs["video_err"])
ppg_proc = start_process("ppg.py", logs["ppg_out"], logs["ppg_err"])

log_marker("▶ Running Stroop Task...")
stroop_proc = subprocess.run(
    ["python", "stroop.py", participant_id, experiment, "before"],
    stdout=open(logs["stroop_out"], "w"),
    stderr=open(logs["stroop_err"], "w")
)
log_marker("✅ Stroop Task Completed.")

break_seconds = 15  # Change back to 300 for 5 min
log_marker(f"🛋️ Break started. Duration: {break_seconds} seconds.")
time.sleep(15)
log_marker("⏰ Break ended. Proceeding to main experiment.")

  

if experiment_id == "1":
    log_marker("🔁 Starting audio only experiment...")

    qtrobot_proc = start_process("audio.py", logs["qtrobot_out"], logs["qtrobot_err"])
else:
    log_marker("🔁 Starting Qtrobot remote script via SSH...")
    qtrobot_proc = subprocess.Popen(
        [
            "ssh", "qtrobot@192.168.1.34",
            "bash", "-c",
            f"'python3 /home/qtrobot/robot/code/natty/test_qt_speech/src/{experiment}.py {participant_id}'"
        ],
        stdout=open(logs["qtrobot_out"], "w"),
        stderr=open(logs["qtrobot_err"], "w"),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
    log_marker("✅ Qtrobot remote script started.")

# --- STEP 5: Wait for user to end experiment ---
input("Once you are done with the meditation excercise press ENTER to continue...\n")
log_marker("▶ Running Stroop Task...")
stroop_proc = subprocess.run(
    ["python", "stroop.py", participant_id, experiment, "after"],
    stdout=open(logs["stroop_out"], "w"),
    stderr=open(logs["stroop_err"], "w")
)
log_marker("✅ Stroop Task Completed.")
log_marker("🛑 Experiment stop requested by user.")

input("🧑‍🔬 Press ENTER to finish the experiment...\n")

# --- STEP 6: Terminate all processes ---
#

stop_video()
if qtrobot_proc.poll() is None:  # Still running
    qtrobot_proc.terminate()
    log_marker(f"🔻 Qtrobot process terminated.")

if ppg_proc.poll() is None:
    ppg_proc.send_signal(signal.CTRL_BREAK_EVENT)
    ppg_proc.wait()
    log_marker("🔻 PPG process terminated gracefully.")

# --- Final log summary ---
log_marker("📁 Experiment completed. Data and logs saved:")
for key, path in logs.items():
    print(f" - {key}: {path}")
