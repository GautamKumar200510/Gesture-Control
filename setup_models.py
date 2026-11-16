"""Download the MediaPipe Hand Landmarker task model."""

import shutil
import urllib.request
import zipfile
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
MODEL_DIR = PROJECT_DIR / "models"
MODEL_PATH = MODEL_DIR / "hand_landmarker.task"
TEMP_PATH = MODEL_PATH.with_suffix(".task.part")
MODEL_URL = "https://storage.googleapis.com/mediapipe-assets/hand_landmarker.task"


def download_model():
    MODEL_DIR.mkdir(exist_ok=True)

    if MODEL_PATH.is_file() and zipfile.is_zipfile(MODEL_PATH):
        print(f"Hand Landmarker model already exists: {MODEL_PATH}")
        return

    if MODEL_PATH.exists():
        print(f"Existing model is invalid; replacing it: {MODEL_PATH}")

    print(f"Downloading Hand Landmarker model from {MODEL_URL}...")
    try:
        with urllib.request.urlopen(MODEL_URL, timeout=30) as response:
            with TEMP_PATH.open("wb") as model_file:
                shutil.copyfileobj(response, model_file)

        if not zipfile.is_zipfile(TEMP_PATH):
            raise ValueError("The downloaded file is not a valid .task model archive.")

        TEMP_PATH.replace(MODEL_PATH)
    except Exception as error:
        TEMP_PATH.unlink(missing_ok=True)
        raise RuntimeError(
            f"Could not download a valid Hand Landmarker model to {MODEL_PATH}."
        ) from error

    print(f"Hand Landmarker model saved: {MODEL_PATH}")


if __name__ == "__main__":
    download_model()
