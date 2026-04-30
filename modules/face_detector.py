import cv2

class FaceDetector:
    def __init__(self):
        # Chargement des deux modèles : Visage et Yeux
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    def detect_faces(self, image):
        """Détecte les visages dans l'image."""
        if image is None: return []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # On utilise des paramètres stables pour la détection
        return self.face_cascade.detectMultiScale(gray, 1.3, 5)

    def get_eyes_count(self, face_gray):
        """Détecte et compte les yeux ouverts dans un visage."""
        # On cherche les yeux uniquement dans la zone du visage pour plus de précision
        eyes = self.eye_cascade.detectMultiScale(face_gray, 1.1, 10, minSize=(15, 15))
        return len(eyes)

    def crop_face(self, image, bbox):
        """Découpe la zone du visage."""
        x, y, w, h = bbox
        return image[y:y+h, x:x+w]



