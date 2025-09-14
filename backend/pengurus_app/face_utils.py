import face_recognition
import numpy as np
from PIL import Image
from io import BytesIO
import base64
from .models import Santri

def decode_base64_image(data_url):
    header, encoded = data_url.split(',', 1)
    data = base64.b64decode(encoded)
    return Image.open(BytesIO(data)).convert('RGB')

def get_all_encodings():
    enc_dict = {}
    for s in Santri.objects.exclude(face_encoding__isnull=True):
        try:
            enc = np.array(s.face_encoding, dtype=float)
            enc_dict[s.id] = enc
        except:
            continue
    return enc_dict

def recognize_from_image_pil(pil_image, tolerance=0.5):
    img = np.array(pil_image)
    # ensure RGB
    if img.shape[2] == 4:
        img = img[:, :, :3]
    face_locations = face_recognition.face_locations(img)
    if not face_locations:
        return None, "no_face"
    face_encodings = face_recognition.face_encodings(img, face_locations)
    db_encs = get_all_encodings()
    if not db_encs:
        return None, "no_dataset"
    face_enc = face_encodings[0]
    ids = list(db_encs.keys())
    encs = np.stack([db_encs[i] for i in ids])
    matches = face_recognition.compare_faces(encs, face_enc, tolerance=tolerance)
    distances = face_recognition.face_distance(encs, face_enc)
    matched_indices = [i for i,m in enumerate(matches) if m]
    if matched_indices:
        best_idx = min(matched_indices, key=lambda i: distances[i])
        santri_pk = ids[best_idx]
        santri = Santri.objects.get(pk=santri_pk)
        return santri, float(distances[best_idx])
    else:
        best_overall = int(np.argmin(distances))
        santri_pk = ids[best_overall]
        return None, float(distances[best_overall])
