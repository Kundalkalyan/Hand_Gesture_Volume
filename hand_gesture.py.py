import cv2
import mediapipe as mp
import math
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import time

last_vol = 0.5  # initial volume (50%)

# Initialize timers
pinch_thumb_pinky_start = None
pinch_thumb_index_start = None
GESTURE_HOLD_TIME = 4  # seconds

# -----------------------------
# MediaPipe setup
# -----------------------------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8)

# -----------------------------
# Windows volume control (modern PyCaw)
# -----------------------------
# Get default audio device
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Volume range
vol_range = volume.GetVolumeRange()  # (min, max, increment)
min_vol, max_vol = vol_range[0], vol_range[1]

# -----------------------------
# Helper
# -----------------------------


def distance(p1, p2):
    return math.hypot(p2[0]-p1[0], p2[1]-p1[1])


# -----------------------------
# Start webcam
# -----------------------------
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:

        for handLms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            h, w, _ = frame.shape
            # Thumb tip
            x1, y1 = int(handLms.landmark[4].x *
                         w), int(handLms.landmark[4].y * h)
            # Index tip
            x2, y2 = int(handLms.landmark[8].x *
                         w), int(handLms.landmark[8].y * h)

            cv2.circle(frame, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
            cv2.circle(frame, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

           # Map thumb-index distance to volume
            length = distance((x1, y1), (x2, y2))
            min_len, max_len = 20, 200
            raw_vol = (length - min_len) / (max_len - min_len)
            raw_vol = max(0.0, min(1.0, raw_vol))

            # Smooth transition
            vol = 0.9 * last_vol + 0.1 * raw_vol  # smooth sudden changes
            last_vol = vol

            # Set volume
            volume.SetMasterVolumeLevelScalar(vol, None)

            cv2.putText(frame, f'Vol: {int(vol*100)}%', (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.putText(frame, f'Vol: {int(vol*100)}%', (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            # Thumb tip
            x_thumb, y_thumb = int(
                handLms.landmark[4].x * w), int(handLms.landmark[4].y * h)
            # Pinky tip
            x_pinky, y_pinky = int(
                handLms.landmark[20].x * w), int(handLms.landmark[20].y * h)

            # Distance between thumb and pinky
            pinch_distance = distance((x_thumb, y_thumb), (x_pinky, y_pinky))

            # Detect pinch gesture
            if pinch_distance < 40:  # tweak based on hand size
                # Example action: mute/unmute
                volume.SetMasterVolumeLevelScalar(0, None)
                cv2.putText(frame, "Pinch Thumb+Pinky Detected!", (10, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.circle(frame, (x_thumb, y_thumb),
                       10, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (x_pinky, y_pinky),
                       10, (255, 0, 255), cv2.FILLED)

            # Thumb + Pinky pinch
            pinch_distance = distance((x_thumb, y_thumb), (x_pinky, y_pinky))

            if pinch_distance < 40:
                if pinch_thumb_pinky_start is None:
                    pinch_thumb_pinky_start = time.time()  # start timer
                elif time.time() - pinch_thumb_pinky_start >= GESTURE_HOLD_TIME:
                    # Trigger action after 2 seconds
                    volume.SetMasterVolumeLevelScalar(0, None)
                    cv2.putText(frame, "Thumb+Pinky Pinch Active!", (10, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                pinch_thumb_pinky_start = None  # reset timer if gesture released

    cv2.imshow("Hand Gesture Volume Control", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key to quit
        break

cap.release()
cv2.destroyAllWindows()
