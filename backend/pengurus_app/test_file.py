import face_recognition

img = face_recognition.load_image_file("tes.png")

try:
    locs = face_recognition.face_locations(img)
    print("Face locations:", locs)
except Exception as e:
    print("Error detector:", e)
