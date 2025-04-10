import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import socket
import os
from datetime import datetime

# ---- CONFIG ----
BREAK_DURATION = 15  # seconds
MEDITATION_DURATION = 330  # seconds
VIDEO_STOP_PORT = 65431
PARTICIPANTS_FILE = "participants.txt"

PRIMARY_COLOR = "#e0f7fa"  # light cyan
ACCENT_COLOR = "#0288d1"   # blue
FONT = ("Segoe UI", 14)
TITLE_FONT = ("Segoe UI", 22, "bold")

class ExperimentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mindfulness Experiment")
        self.root.state('zoomed')  # Maximized
        self.root.configure(bg=PRIMARY_COLOR)
        self.user_continue = threading.Event()
        self.participant_id = tk.StringVar()
        self.experiment_id = tk.StringVar()
        self.processes = {}
        self.logs = {}
        self.experiment = "test"

        self.build_start_screen()

    def show_continue_button(self):
        def on_click():
            self.user_continue.set()
            self.continue_button.destroy()  # Remove button after click

        self.continue_button = tk.Button(
            self.root, text="Proceed to Next Step", command=on_click,
            bg=ACCENT_COLOR, fg="white", font=FONT, padx=20, pady=10, relief="flat", borderwidth=0
        )
        self.continue_button.pack(pady=30)


    def build_start_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root, bg=PRIMARY_COLOR)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="Mindfulness Experiment", font=TITLE_FONT, bg=PRIMARY_COLOR).grid(row=0, column=0, columnspan=2, pady=20)

        tk.Label(frame, text="Participant ID:", font=FONT, bg=PRIMARY_COLOR).grid(row=1, column=0, sticky="e", padx=10, pady=10)
        tk.Entry(frame, textvariable=self.participant_id, font=FONT).grid(row=1, column=1, padx=10, pady=10)

        tk.Label(frame, text="Experiment Type:", font=FONT, bg=PRIMARY_COLOR).grid(row=2, column=0, sticky="e", padx=10, pady=10)
        ttk.Combobox(frame, textvariable=self.experiment_id, values=["1", "2", "3"], font=FONT, state="readonly").grid(row=2, column=1, padx=10, pady=10)

        tk.Button(frame, text="Start", command=self.validate_inputs,
                  bg=ACCENT_COLOR, fg="white", font=FONT, padx=20, pady=10, relief="flat", borderwidth=0).grid(row=3, column=0, columnspan=2, pady=20)

    def validate_inputs(self):
        pid = self.participant_id.get()
        exp_id = self.experiment_id.get()

        if not pid or not exp_id:
            messagebox.showerror("Error", "Please fill all fields.")
            return

        if os.path.exists(PARTICIPANTS_FILE):
            with open(PARTICIPANTS_FILE, "r") as f:
                existing = set(f.read().splitlines())
        else:
            existing = set()
        if pid != "0":
            if pid in existing:
                messagebox.showerror("Error", "Participant ID already exists!")
                return

            with open(PARTICIPANTS_FILE, "a") as f:
                f.write(pid + "\n")

        self.start_experiment(pid, exp_id)

    def start_experiment(self, pid, exp_id):
        self.participant_id = pid
        self.experiment_id = exp_id
        self.experiment = "audio" if exp_id == "1" else "audio_robot" if exp_id == "2" else "audio_robot_haptics"
        self.setup_log_paths()
        self.build_experiment_screen()
        threading.Thread(target=self.run_experiment, daemon=True).start()

    def setup_log_paths(self):
        logs_dir = f"./data/{self.experiment}/"
        os.makedirs(logs_dir, exist_ok=True)
        self.logs = {
            "video_out": f"{logs_dir}/participant_{self.participant_id}_video_out.log",
            "video_err": f"{logs_dir}/participant_{self.participant_id}_video_err.log",
            "ppg_out": f"{logs_dir}/participant_{self.participant_id}_ppg_out.log",
            "ppg_err": f"{logs_dir}/participant_{self.participant_id}_ppg_err.log",
            "qtrobot_out": f"{logs_dir}/participant_{self.participant_id}_qtrobot_out.log",
            "qtrobot_err": f"{logs_dir}/participant_{self.participant_id}_qtrobot_err.log",
            "stroop_out": f"{logs_dir}/participant_{self.participant_id}_stroop_out.log",
            "stroop_err": f"{logs_dir}/participant_{self.participant_id}_stroop_err.log",
            "experiment": f"{logs_dir}/participant_{self.participant_id}_experiment.log",
        }

    def build_experiment_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root, bg=PRIMARY_COLOR)
        frame.place(relx=0.5, rely=0.4, anchor="center")

        self.status_label = tk.Label(frame, text="Starting experiment...", font=FONT, bg=PRIMARY_COLOR)
        self.status_label.pack(pady=10)

        self.timer_label = tk.Label(frame, text="", font=("Segoe UI", 28), bg=PRIMARY_COLOR)
        self.timer_label.pack(pady=10)

        self.progress = ttk.Progressbar(frame, length=400, mode='determinate')
        style = ttk.Style()
        style.configure("TProgressbar", foreground=ACCENT_COLOR, background=ACCENT_COLOR)
        self.progress.pack(pady=10)

    def log(self, message):
        self.status_label.config(text=message)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        with open(self.logs["experiment"], "a") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")

    def run_subprocess(self, cmd, out_log, err_log):
        return subprocess.Popen(
            cmd,
            stdout=open(out_log, "w"),
            stderr=open(err_log, "w"),
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )

    def run_experiment(self):
        self.log("Starting Video & PPG...")
        self.processes["video"] = self.run_subprocess(
            ["python", "recordVideo.py", self.participant_id, self.experiment],
            self.logs["video_out"], self.logs["video_err"])

        self.processes["ppg"] = self.run_subprocess(
            ["python", "ppg.py", self.participant_id, self.experiment],
            self.logs["ppg_out"], self.logs["ppg_err"])

        time.sleep(2)

        self.log("Running Stroop Task...")
        with open(self.logs["stroop_out"], "a") as out, open(self.logs["stroop_err"], "a") as err:
            subprocess.run(
                ["python", "stroop.py", self.participant_id, self.experiment, "before"],
                stdout=out, stderr=err)

        self.log(f"Break Time: {BREAK_DURATION} sec")
        self.run_timer(BREAK_DURATION)

        self.log(f"Meditation Exercise {self.experiment_id}...")
        if self.experiment_id == "1":
            self.processes["qtrobot"] = self.run_subprocess(
                ["python", "audio.py", self.participant_id],
                self.logs["qtrobot_out"], self.logs["qtrobot_err"])
        else:
            self.processes["qtrobot"] = self.run_subprocess(
                ["ssh", "qtrobot@192.168.1.15", "bash", "-c",
                 f"'python3 /home/qtrobot/robot/code/natty/test_qt_speech/src/{self.experiment}.py {self.participant_id}'"],
                self.logs["qtrobot_out"], self.logs["qtrobot_err"])

        self.root.after(MEDITATION_DURATION * 1000, self.show_continue_button)
        self.user_continue.wait()

        self.log("Running Stroop Task (After)...")
        with open(self.logs["stroop_out"], "a") as out, open(self.logs["stroop_err"], "a") as err:
            subprocess.run(
                ["python", "stroop.py", self.participant_id, self.experiment, "after"],
                stdout=out, stderr=err)

        self.log("Stopping Video Recording...")
        self.stop_video()
        if self.experiment_id != "1":
            ps_script = ".\\download_data.ps1"
            try:
                result = subprocess.run(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_script, self.experiment, self.participant_id],
                    capture_output=True, text=True, check=True)
                print(result.stdout)
            except subprocess.CalledProcessError as e:
                print(f"❌ Script failed:\n{e.stderr}")


        self.log("Experiment Completed!")

    def run_timer(self, duration):
        for remaining in range(duration, 0, -1):
            self.timer_label.config(text=f"Break: {remaining} sec")
            time.sleep(1)
        self.timer_label.config(text="")

    def run_progress(self, duration):
        self.progress["maximum"] = duration
        for i in range(duration):
            self.progress["value"] = i + 1
            time.sleep(1)
        self.progress["value"] = 0

    def stop_video(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('127.0.0.1', VIDEO_STOP_PORT))
                s.sendall(b"STOP")
                self.log("Sent STOP to Video Recording.")
        except Exception as e:
            self.log(f"Video stop failed: {e}")

        for key in ["qtrobot", "ppg"]:
            proc = self.processes.get(key)
            if proc and proc.poll() is None:
                proc.terminate()
                self.log(f"{key} process terminated.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExperimentApp(root)
    root.mainloop()
