import cv2
import numpy as np

class FaceEncoder:
    def __init__(self):
        # CLAHE permet d'égaliser la lumière de manière locale et intelligente
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        
    def get_embedding(self, face_image):
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        # Application du filtre CLAHE pour une meilleure reconnaissance dans le noir
        gray = self.clahe.apply(gray)
        gray = cv2.resize(gray, (100, 100))
        return gray

