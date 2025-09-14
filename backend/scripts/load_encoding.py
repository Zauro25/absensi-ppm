import os
import face_recognition
import pickle
from django.conf import settings

DATASET_DIR = os.path.join(settings.MEDIA_ROOT, "santri_faces")
ENCODINGS_FILE = os.path.join(settings.MEDIA_ROOT, "encodings.pkl")

def update_encodings():
    known_encodings = []
    known_ids = []

    for file in os.listdir(DATASET_DIR):
        if file.endswith((".jpg", ".png", ".jpeg")):
            santri_id = file.split(".")[0]
            img_path = os.path.join(DATASET_DIR, file)
            image = face_recognition.load_image_file(img_path)
            encs = face_recognition.face_encodings(image)
            if encs:
                known_encodings.append(encs[0])
                known_ids.append(santri_id)

    data = {"encodings": known_encodings, "ids": known_ids}
    with open(ENCODINGS_FILE, "wb") as f:
        pickle.dump(data, f)

    print("✅ Dataset encodings updated.")
