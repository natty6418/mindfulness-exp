import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks

# 🔹 Configuration Parameters
SAMPLING_RATE = 128  # Hz
TIME_WINDOW = 2  # Seconds for initial processing
LOWCUT = 0.5  # Hz (Low cutoff for band-pass filter)
HIGHCUT = 3.0  # Hz (High cutoff for band-pass filter)

# 🔹 Simulated Raw PPG Data (Replace with actual Shimmer PPG readings)
ppg_signal = np.loadtxt("ppg_data.txt", delimiter=",", skiprows=1, usecols=1)
time = np.loadtxt("ppg_data.txt", delimiter=",", skiprows=1, usecols=0)
    

# 🔹 1. Apply Band-Pass Filter
def bandpass_filter(signal, lowcut, highcut, fs, order=3):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, signal)

filtered_ppg = bandpass_filter(ppg_signal, LOWCUT, HIGHCUT, SAMPLING_RATE)

# 🔹 2. Detect Peaks (Heartbeats)
peaks, _ = find_peaks(filtered_ppg, distance=SAMPLING_RATE//2, prominence=0.3)

# 🔹 3. Compute Heart Rate (BPM)
peak_times = time[peaks]
peak_intervals = np.diff(peak_times)  # Time difference between beats

if len(peak_intervals) > 0:
    avg_beat_interval = np.mean(peak_intervals)  # Average interval between peaks
    heart_rate = 60 / avg_beat_interval  # Convert to BPM
    print(f"\n❤️ Estimated Heart Rate: {heart_rate:.2f} BPM")
else:
    print("\n⚠️ Not enough data to calculate heart rate.")

# 🔹 4. Plot PPG Signal & Detected Heartbeats
plt.figure(figsize=(10, 5))
plt.plot(time, filtered_ppg, label="Filtered PPG Signal", color="blue")
plt.plot(time[peaks], filtered_ppg[peaks], "ro", label="Detected Heartbeats")  # Mark peaks
plt.axvline(x=60, color="g", linestyle="--", label="Walking Begins")  # Walking starts at 60s
plt.xlabel("Time (s)")
plt.ylabel("PPG Value (mV)")
plt.title("PPG Signal with Heart Rate Detection")
plt.legend()
plt.grid()
plt.show()
