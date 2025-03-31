import subprocess
import time
import os
from datetime import datetime
import signal

def log_marker(event):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {event}")

# Prompt for participant ID
participant_id = input("Enter Participant ID: ")

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Define log file paths
logs = {
    "stroop_out": f"./data/audio_robot_haptics/participant_{participant_id}_stroop_out.log",
    "stroop_err": f"./data/audio_robot_haptics/participant_{participant_id}_stroop_err.log",
    "video_out": f"./data/audio_robot_haptics/participant_{participant_id}_video_out.log",
    "video_err": f"./data/audio_robot_haptics/participant_{participant_id}_video_err.log",
    "ppg_out": f"./data/audio_robot_haptics/participant_{participant_id}_ppg_out.log",
    "ppg_err": f"./data/audio_robot_haptics/participant_{participant_id}_ppg_err.log",
    # "trigger_out": f"./data/participant_{participant_id}_trigger_out.log",
    # "trigger_err": f"./data/participant_{participant_id}_trigger_err.log",
    "qtrobot_out": f"./data/audio_robot_haptics/participant_{participant_id}_qtrobot_out.log",
    "qtrobot_err": f"./data/audio_robot_haptics/participant_{participant_id}_qtrobot_err.log",
}

log_marker(f"🧪 Starting experiment for Participant {participant_id}")

# --- STEP 1: Run Stroop Task ---
log_marker("▶ Running Stroop Task...")
stroop_proc = subprocess.run(
    ["python", "stroop.py", participant_id],
    stdout=open(logs["stroop_out"], "w"),
    stderr=open(logs["stroop_err"], "w")
)
log_marker("✅ Stroop Task Completed.")

# --- STEP 2: Break Time ---
break_seconds = 15  # Change back to 300 for 5 min
log_marker(f"🛋️ Break started. Duration: {break_seconds} seconds.")


# --- STEP 3: Start Remote Qtrobot Script via SSH ---
log_marker("🔁 Starting Qtrobot remote script via SSH...")
qtrobot_proc = subprocess.Popen(
    [
        "ssh", "qtrobot@192.168.1.34",
        "bash", "-c",
        f"'python3 /home/qtrobot/robot/code/natty/test_qt_speech/src/sendSignal_haptics.py {participant_id}'"
    ],
    stdout=open(logs["qtrobot_out"], "w"),
    stderr=open(logs["qtrobot_err"], "w"),
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
)
log_marker("✅ Qtrobot remote script started.")
# time.sleep(break_seconds)
log_marker("⏰ Break ended. Proceeding to main experiment.")

# --- STEP 4: Start Main Local Experiment Processes ---
def start_process(script_name, log_out, log_err):
    log_marker(f"▶ Starting {script_name}...")
    return subprocess.Popen(
        ["python", script_name, participant_id],
        stdout=open(log_out, "w"),
        stderr=open(log_err, "w"),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )

log_marker("▶ Starting video, and PPG recording...")
video_proc = start_process("recordVideo.py", logs["video_out"], logs["video_err"])
ppg_proc = start_process("ppg.py", logs["ppg_out"], logs["ppg_err"])
# trigger_proc = start_process("remote_trigger_.py", logs["trigger_out"], logs["trigger_err"])

log_marker("📡 All data collection processes started.")

# # --- STEP 5: Wait for user to end experiment ---
input("🧑‍🔬 Press ENTER to stop the experiment...\n")
log_marker("🛑 Experiment stop requested by user.")

# --- STEP 6: Terminate all processes ---
for proc, name in [(video_proc, "Video"), (qtrobot_proc, "Qtrobot")]:
    if proc.poll() is None:  # Still running
        proc.terminate()
        log_marker(f"🔻 {name} process terminated.")

if ppg_proc.poll() is None:
    ppg_proc.send_signal(signal.CTRL_BREAK_EVENT)
    ppg_proc.wait()
    log_marker("🔻 PPG process terminated gracefully.")

# --- Final log summary ---
log_marker("📁 Experiment completed. Data and logs saved:")
for key, path in logs.items():
    print(f" - {key}: {path}")
