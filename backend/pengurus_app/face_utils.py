import face_recognition
import numpy as np
from PIL import Image
from io import BytesIO
import base64
from .models import Santri

def decode_base64_image(data_url):
    """Decode base64 dataURL jadi PIL image (RGB)."""
    header, encoded = data_url.split(',', 1)
    data = base64.b64decode(encoded)
    return Image.open(BytesIO(data)).convert('RGB')

def get_all_encodings():
    """Ambil semua face_encoding santri dari DB."""
    enc_dict = {}
    for s in Santri.objects.exclude(face_encoding__isnull=True):
        try:
            enc = np.array(s.face_encoding, dtype=float)
            enc_dict[s.id] = enc
        except Exception:
            continue
    return enc_dict

def recognize_from_image_pil(pil_image, tolerance=0.5):
    """Cocokin wajah dari gambar PIL dengan database santri."""
    img = np.array(pil_image)

    # pastiin RGB
    if img.ndim == 3 and img.shape[2] == 4:
        img = img[:, :, :3]

    face_locations = face_recognition.face_locations(img)
    if not face_locations:
        return None, "no_face"

    face_encodings = face_recognition.face_encodings(img, face_locations)
    if not face_encodings:
        return None, "no_face"

    db_encs = get_all_encodings()
    if not db_encs:
        return None, "no_dataset"

    face_enc = face_encodings[0]
    ids = list(db_encs.keys())
    encs = np.stack([db_encs[i] for i in ids])

    matches = face_recognition.compare_faces(encs, face_enc, tolerance=tolerance)
    distances = face_recognition.face_distance(encs, face_enc)

    matched_indices = [i for i, m in enumerate(matches) if m]
    if matched_indices:
        best_idx = min(matched_indices, key=lambda i: distances[i])
        santri_pk = ids[best_idx]
        santri = Santri.objects.get(pk=santri_pk)
        return santri, float(distances[best_idx])
    else:
        return None, "no_match"
    
def prepare_image_for_face_recognition(path, max_size=1000, force_gray=False):
    """
    Baca gambar dari path, resize biar ga kegedean, convert ke RGB/grayscale,
    lalu return numpy array uint8 C-contiguous siap untuk face_recognition.
    """
    pil_img = Image.open(path).convert("RGB")
    pil_img.thumbnail((max_size, max_size))

    if force_gray:
        pil_img = pil_img.convert("L")  # 🔥 fallback grayscale

    img_np = np.array(pil_img, dtype=np.uint8)
    img_np = np.ascontiguousarray(img_np)

    print("DEBUG final >>", pil_img.mode, img_np.dtype, img_np.shape, img_np.flags)
    return img_np