import time
from pathlib import Path

import cv2
import mediapipe as mp
import pyautogui
from mediapipe.tasks.python import vision


MODEL_PATH = Path(__file__).resolve().parent / "models" / "hand_landmarker.task"


def fingers_up(hand_landmarks):
    """Detect which fingers are up based on landmarks"""
    tips = [8, 12, 16, 20]   # Fingertip indices
    pips = [6, 10, 14, 18]   # PIP joint indices

    fingers = []

    for tip, pip in zip(tips, pips):
        # If tip is above pip, finger is up
        if hand_landmarks[tip].y < hand_landmarks[pip].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers


def main():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"Hand Landmarker model not found: {MODEL_PATH}\n"
            "Run setup_models.py with this project's Python environment first."
        )

    base_options = mp.tasks.BaseOptions(model_asset_path=str(MODEL_PATH))
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_hand_presence_confidence=0.7,
        min_tracking_confidence=0.7,
    )
    hand_landmarker = vision.HandLandmarker.create_from_options(options)
    cap = cv2.VideoCapture(0)
    last_time = 0.0
    cooldown = 1.5

    try:
        if not cap.isOpened():
            raise RuntimeError(
                "Could not open webcam 0. Check that a camera is connected, "
                "not in use by another application, and allowed in Windows "
                "Settings > Privacy & security > Camera."
            )

        while True:
            success, frame = cap.read()
            if not success:
                raise RuntimeError(
                    "The webcam opened but failed to provide a video frame."
                )

            frame = cv2.flip(frame, 1)
            height, width, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            detection_result = hand_landmarker.detect(mp_image)
            gesture = "Waiting..."

            if detection_result.hand_landmarks:
                for hand_landmarks in detection_result.hand_landmarks:
                    for landmark in hand_landmarks:
                        x = int(landmark.x * width)
                        y = int(landmark.y * height)
                        cv2.circle(frame, (x, y), 2, (0, 255, 0), 1)

                    connections = [
                        (0, 1), (1, 2), (2, 3), (3, 4),
                        (5, 6), (6, 7), (7, 8),
                        (9, 10), (10, 11), (11, 12),
                        (13, 14), (14, 15), (15, 16),
                        (17, 18), (18, 19), (19, 20),
                        (0, 5), (5, 9), (9, 13), (13, 17), (0, 17),
                    ]
                    for start_idx, end_idx in connections:
                        start = hand_landmarks[start_idx]
                        end = hand_landmarks[end_idx]
                        x1, y1 = int(start.x * width), int(start.y * height)
                        x2, y2 = int(end.x * width), int(end.y * height)
                        cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)

                    total = fingers_up(hand_landmarks).count(1)
                    current_time = time.monotonic()
                    if current_time - last_time > cooldown:
                        if total == 4:
                            pyautogui.press("right")
                            gesture = "Next Slide"
                            last_time = current_time
                        elif total == 3:
                            pyautogui.press("left")
                            gesture = "Previous Slide"
                            last_time = current_time
                        elif total == 2:
                            pyautogui.hotkey("ctrl", "f5")
                            gesture = "Start Slideshow"
                            last_time = current_time
                        elif total == 0:
                            pyautogui.press("esc")
                            gesture = "Exit Slideshow"
                            last_time = current_time

            cv2.putText(
                frame,
                gesture,
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )
            cv2.imshow("Google Slides Gesture Control", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        hand_landmarker.close()


if __name__ == "__main__":
    main()