import time
import sys
import csv
import soundfile as sf
import sounddevice as sd

bodyScan_locations = [
    'left_chest',
    'right_chest',
    'left_abdomen',
    'right_abdomen',
    'left_shoulder',
    'right_shoulder',
    'left_lower_back',
    'right_lower_back',
]

participant_id = sys.argv[1] if len(sys.argv) > 1 else "test"
DATA_FILE = f"./data/audio/participant_{participant_id}_data.csv"
SAMPLE_RATE = 24000  # Sample rate for audio playback
AUDIO_PATH = "./audios/"  
def play_audio_blocking(file):
    try:
        data, fs = sf.read(AUDIO_PATH+file, dtype='float32')
        sd.play(data, fs)
        sd.wait()  # Wait until the sound has finished playing
    except Exception as e:
        print(f"Error playing audio file {AUDIO_PATH+file}: {e}")

def play_audio(file):
    try:
        data, fs = sf.read(AUDIO_PATH+file, dtype='float32')
        sd.play(data, fs)
    except Exception as e:
        print(f"Error playing audio file {AUDIO_PATH+file}: {e}")
        

def log_event(event):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    with open(DATA_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, event])
    print(f"[{timestamp}] {event}")

if __name__ == "__main__":

        log_event("Audio: welcome.wav")
        play_audio_blocking('welcome.wav')
        log_event("Audio: intro2")
        play_audio_blocking('intro2.wav')

        play_audio("inhale4.wav")
        log_event("Talk: inhale4")
        #log_event("Signal sent: inhale")
        time.sleep(5)

        log_event("Audio: hold4")
        play_audio_blocking("hold4.wav")
        play_audio("exhale4.wav")
        log_event("Talk: exhale4")
        #log_event("Signal sent: exhale")
        time.sleep(6)

        log_event("Audio: continue2")
        play_audio_blocking("continue2.wav")

        for i in range(4):
            log_event(f"Cycle {i+1}: Signal sent: inhale")
            play_audio("inhale2.wav")
            time.sleep(5)
            log_event("Audio: hold2")
            play_audio("hold2.wav")
            time.sleep(8)
            log_event("Audio: exhale2")
            play_audio("exhale3.wav")
            if i != 3:
                time.sleep(8)
                play_audio("repeat.wav")
                time.sleep(5)
            else:
                time.sleep(8)

        log_event("Audio: bodyScan")
        play_audio_blocking("bodyScan2.wav")

        for location in bodyScan_locations:
            log_event(f"Audio: {location}")
            play_audio(f"{location}2.wav")
            time.sleep(9)

        log_event("Audio: outro")
        play_audio_blocking('outro.wav')
        play_audio_blocking('proceed.wav')

        print("Finished.")
