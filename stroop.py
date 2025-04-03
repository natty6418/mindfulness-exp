
import tkinter as tk
import random
import time
import csv
import sys
import os

# === Constants ===
DURATION = 120  # Total task time in seconds
ISI = 1500  # Inter-stimulus interval in ms
STIM_DURATION = 1000  # Stimulus duration in ms
MATCH_PROBABILITY = 0.3  # 30% match trials

WORDS = ["RED", "GREEN", "BLUE", "YELLOW", "PURPLE", "ORANGE"]
COLORS = {"RED": "red", "GREEN": "green", "BLUE": "blue", "YELLOW": "yellow", "PURPLE": "purple", "ORANGE": "orange"}

RESPONSE_KEY = "Return"  # Enter
QUIT_KEY = "q"

# === Setup participant ===
participant_id = sys.argv[1] if len(sys.argv) > 1 else "test"
experiment_id = sys.argv[2] if len(sys.argv) > 2 else "test"
before_after = sys.argv[3] if len(sys.argv) > 3 else "before"
os.makedirs(f"data/{experiment_id}", exist_ok=True)
log_file = f"./data/{experiment_id}/participant_{participant_id}_stroop_results_{before_after}.csv"
results = []

# === Tkinter GUI ===
root = tk.Tk()
root.title("Stroop Go/No-Go Task")
root.geometry("800x600")
root.configure(bg="#1e1e1e")
root.attributes("-fullscreen", True)

label = tk.Label(root, text="", font=("Arial", 64, "bold"), bg="#1e1e1e", fg="white")
label.pack(expand=True)

instructions_frame = tk.Frame(root, bg="#1e1e1e")
instructions_frame.pack(expand=True, fill="both")

instructions = tk.Label(
    instructions_frame,
    text="🧠 Welcome to the Stroop Task 🧠\n\n"
         "If the COLOR of the word matches the WORD, press ENTER.\n"
         "Do NOT press anything if they don't match.\n\n"
         "Press ENTER to begin.\n",
    font=("Arial", 20),
    bg="#1e1e1e",
    fg="white",
    justify="center",
    wraplength=800
)
instructions.pack(expand=True)

# === Global state ===
start_time = None
trial_start = None
current_word = None
current_color = None
response_received = False
task_running = False

# === Trial logic ===
def show_next_trial():
    global trial_start, current_word, current_color, response_received

    if not task_running:
        return

    if time.time() - start_time > DURATION:
        end_task()
        return

    response_received = False

    is_match = random.random() < MATCH_PROBABILITY
    current_word = random.choice(WORDS)
    correct_color = COLORS[current_word]

    if is_match:
        current_color = correct_color
    else:
        other_colors = [c for c in COLORS.values() if c != correct_color]
        current_color = random.choice(other_colors)

    label.config(text=current_word, fg=current_color)
    trial_start = time.time()

    root.after(STIM_DURATION, clear_stimulus)
    root.after(ISI, show_next_trial)

def clear_stimulus():
    global response_received
    label.config(text="")

    is_match = COLORS[current_word] == current_color

    if is_match and not response_received:
        results.append({
            "word": current_word,
            "color": current_color,
            "match": True,
            "response": False,
            "correct": False,
            "reaction_time": None
        })
    elif not is_match and not response_received:
        results.append({
            "word": current_word,
            "color": current_color,
            "match": False,
            "response": False,
            "correct": True,
            "reaction_time": None
        })

def on_key_press(event):
    global response_received, task_running

    key = event.keysym.lower()

    if not task_running:
        if key == "return":
            start_task()
        return

    if key == QUIT_KEY:
        end_task()
        return

    if label.cget("text") == "" or response_received:
        return

    rt = time.time() - trial_start
    response_received = True
    is_match = COLORS[current_word] == current_color
    correct = is_match

    results.append({
        "word": current_word,
        "color": current_color,
        "match": is_match,
        "response": True,
        "correct": correct,
        "reaction_time": round(rt, 3)
    })

def start_task():
    global start_time, task_running
    instructions_frame.pack_forget()
    start_time = time.time()
    task_running = True

    root.configure(bg="black")
    label.configure(bg="black")
    
    show_next_trial()

def end_task():
    global task_running
    task_running = False
    label.config(text="Done!", fg="white")
    root.unbind("<Key>")

    if results:
        with open(log_file, mode="w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["word", "color", "match", "response", "correct", "reaction_time"])
            writer.writeheader()
            writer.writerows(results)
        print(f"Stroop task completed. Data saved to {log_file}")
    else:
        print("⚠️ No responses recorded. Task was likely quit early.")

    root.after(3000, root.destroy)

root.bind("<Key>", on_key_press)
root.mainloop()
