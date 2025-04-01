import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import socket
import os
import threading
import time
from datetime import datetime
import signal

class ExperimentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Experiment Controller")
        self.participant_id = tk.StringVar()
        self.experiment_id = tk.StringVar()
        self.log_text = tk.StringVar()
        self.processes = {}

        # UI Layout
        tk.Label(root, text="Participant ID:").grid(row=0, column=0, sticky="w")
        tk.Entry(root, textvariable=self.participant_id).grid(row=0, column=1)

        tk.Label(root, text="Experiment:").grid(row=1, column=0, sticky="w")
        ttk.Combobox(root, textvariable=self.experiment_id, values=["1", "2", "3"]).grid(row=1, column=1)

        tk.Button(root, text="Start Experiment", command=self.start_experiment).grid(row=2, column=0, pady=10)
        tk.Button(root, text="Finish Experiment", command=self.stop_experiment).grid(row=2, column=1, pady=10)

        self.log_area = tk.Text(root, height=15, width=50)
        self.log_area.grid(row=3, column=0, columnspan=2)

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)

    def start_experiment(self):
        pid = self.participant_id.get()
        exp_id = self.experiment_id.get()
        if not pid or not exp_id:
            messagebox.showerror("Error", "Enter Participant ID and Experiment")
            return

        # Save participant ID
        filename = "participants.txt"
        if os.path.exists(filename):
            with open(filename, "r") as f:
                participant_ids = set(f.read().splitlines())
        else:
            participant_ids = set()

        if pid in participant_ids and pid !="0":
            messagebox.showerror("Error", "Participant ID already exists!")
            return

        participant_ids.add(pid)
        with open(filename, "a") as f:
            f.write(pid + "\n")

        experiment = "audio" if exp_id == "1" else "audio_robot" if exp_id == "2" else "audio_robot_haptics"
        self.log(f"🧪 Starting experiment for Participant {pid}")

        # Start processes in background thread
        threading.Thread(target=self.run_experiment, args=(pid, experiment, exp_id)).start()

    def run_experiment(self, pid, experiment, exp_id):
        logs_dir = f"./data/{experiment}/"
        os.makedirs(logs_dir, exist_ok=True)

        logs = {
            "video_out": f"{logs_dir}/participant_{pid}_video_out.log",
            "video_err": f"{logs_dir}/participant_{pid}_video_err.log",
            "ppg_out": f"{logs_dir}/participant_{pid}_ppg_out.log",
            "ppg_err": f"{logs_dir}/participant_{pid}_ppg_err.log",
            "qtrobot_out": f"{logs_dir}/participant_{pid}_qtrobot_out.log",
            "qtrobot_err": f"{logs_dir}/participant_{pid}_qtrobot_err.log",
        }

        def start_process(script, out, err):
            return subprocess.Popen(
                ["python", script, pid, experiment],
                stdout=open(out, "w"),
                stderr=open(err, "w"),
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )

        # Start video & PPG
        self.log("▶ Starting video and PPG recording...")
        self.processes["video"] = start_process("recordVideo.py", logs["video_out"], logs["video_err"])
        self.processes["ppg"] = start_process("ppg.py", logs["ppg_out"], logs["ppg_err"])

        # Run Stroop task
        self.log("▶ Running Stroop Task...")
        subprocess.run(
            ["python", "stroop.py", pid, experiment, "before"],
            stdout=open(logs["video_out"], "a"),
            stderr=open(logs["video_err"], "a")
        )
        self.log("✅ Stroop Task Completed")

        # Break
        self.log("🛋️ Break started for 15 seconds...")
        time.sleep(15)
        self.log("⏰ Break ended. Starting main experiment.")

        # Qtrobot / Audio
        if exp_id == "1":
            self.processes["qtrobot"] = start_process("audio.py", logs["qtrobot_out"], logs["qtrobot_err"])
        else:
            self.processes["qtrobot"] = subprocess.Popen(
                [
                    "ssh", "qtrobot@192.168.1.34",
                    "bash", "-c",
                    f"'python3 /home/qtrobot/robot/code/natty/test_qt_speech/src/{experiment}.py {pid}'"
                ],
                stdout=open(logs["qtrobot_out"], "w"),
                stderr=open(logs["qtrobot_err"], "w"),
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        self.log("✅ Main experiment running...")

        # Stroop after
        self.log("▶ Waiting for user to finish...")
        self.root.after(100, self.wait_for_finish)

    def wait_for_finish(self):
        if "finished" in self.processes:
            return
        # Wait until user clicks Finish
        self.root.after(100, self.wait_for_finish)

    def stop_experiment(self):
        self.log("🛑 Stopping experiment...")
        self.processes["finished"] = True

        # Stop video
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('127.0.0.1', 65432))
                s.sendall(b"STOP")
                self.log("📩 Sent STOP to Video Recording.")
        except Exception as e:
            self.log(f"⚠️ Failed to stop video: {e}")

        # Terminate others
        for key in ["qtrobot", "ppg"]:
            proc = self.processes.get(key)
            if proc and proc.poll() is None:
                proc.terminate()
                self.log(f"🔻 {key} process terminated.")

        self.log("✅ Experiment finished.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExperimentApp(root)
    root.mainloop()
