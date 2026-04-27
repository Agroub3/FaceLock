import cv2
import os

class FaceDetector:
    def __init__(self):
        # Utilisation du classificateur Haar Cascade intégré à OpenCV
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.detector = cv2.CascadeClassifier(cascade_path)

    def detect_faces(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Détection des visages
        faces_rects = self.detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        faces = []
        for (x, y, w, h) in faces_rects:
            faces.append((x, y, w, h))
        return faces

    def crop_face(self, image, bbox):
        x, y, w, h = bbox
        return image[y:y+h, x:x+w]
