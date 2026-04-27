import cv2
import numpy as np

class FaceEncoder:
    def __init__(self):
        # Utilisation du reconnaisseur LBPH d'OpenCV
        # Note: Sur certaines versions, il faut 'opencv-contrib-python'
        try:
            self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        except AttributeError:
            print("[FaceEncoder] Erreur: opencv-contrib-python est requis pour LBPH.")
            self.recognizer = None
        
    def get_embedding(self, face_image):
        """
        Pour OpenCV LBPH, l'embedding est l'image elle-même en gris.
        Le 'vrai' encodage se fait lors de l'entraînement ou de la comparaison.
        """
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (100, 100)) # Normalisation de la taille
        return gray
