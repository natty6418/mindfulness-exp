import cv2
import sys

# Get participant ID from command-line argument
participant_id = sys.argv[1] if len(sys.argv) > 1 else "unknown"

# Define video filename with participant ID
video_filename = f"./data/participant_{participant_id}_video.avi"

# Open the webcam (0 = default camera)
cap = cv2.VideoCapture(1)

# Define video codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))

print(f"Recording... Saving as {video_filename}. Press 'q' to stop.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    out.write(frame)
    cv2.imshow('Recording', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

print(f"Recording saved as '{video_filename}'")
