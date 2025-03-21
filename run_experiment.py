import subprocess
import time
import os
from datetime import datetime

# Prompt for participant ID
participant_id = input("Enter Participant ID: ")

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Timestamp for uniqueness (optional)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Define log file paths
logs = {
    "stroop_out": f"./data/participant_{participant_id}_stroop_out.log",
    "stroop_err": f"./data/participant_{participant_id}_stroop_err.log",
    "video_out": f"./data/participant_{participant_id}_video_out.log",
    "video_err": f"./data/participant_{participant_id}_video_err.log",
    "ppg_out": f"./data/participant_{participant_id}_ppg_out.log",
    "ppg_err": f"./data/participant_{participant_id}_ppg_err.log",
    "trigger_out": f"./data/participant_{participant_id}_trigger_out.log",
    "trigger_err": f"./data/participant_{participant_id}_trigger_err.log",
}

print(f"\n🧪 Starting experiment for Participant {participant_id}...\n")

# --- STEP 1: Run Stroop Task ---
print("▶ Running Stroop Task...")
stroop_proc = subprocess.run(
    ["python", "stroop.py", participant_id],
    stdout=open(logs["stroop_out"], "w"),
    stderr=open(logs["stroop_err"], "w")
)
print("✅ Stroop Task Completed.\n")

# --- STEP 2: Break Time ---
break_seconds = 60  # 5 minutes
print(f"🛋️ Break time: {break_seconds // 60} minute. Please relax...\n")
time.sleep(break_seconds)
print("⏰ Break over. Proceeding to main experiment...\n")

# --- STEP 3: Start Main Experiment Processes (video, ppg, trigger) ---
def start_process(script_name, log_out, log_err):
    return subprocess.Popen(
        ["python", script_name, participant_id],
        stdout=open(log_out, "w"),
        stderr=open(log_err, "w")
    )

print("▶ Starting video, PPG, and trigger recording...\n")

video_proc = start_process("recordVideo.py", logs["video_out"], logs["video_err"])
ppg_proc = start_process("ppg.py", logs["ppg_out"], logs["ppg_err"])
trigger_proc = start_process("remote_trigger_.py", logs["trigger_out"], logs["trigger_err"])

# --- STEP 4: Wait for user to end experiment ---
input("🧑‍🔬 Press ENTER to stop the experiment...\n")

# --- STEP 5: Terminate processes ---
for proc, name in [(video_proc, "Video"), (ppg_proc, "PPG"), (trigger_proc, "Trigger")]:
    if proc.poll() is None:  # Process still running
        proc.terminate()
        print(f"🛑 {name} process terminated.")

# --- Final log summary ---
print("\n📁 Experiment completed. Data and logs saved:")
for key, path in logs.items():
    print(f" - {key}: {path}")
