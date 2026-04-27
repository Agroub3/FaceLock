import cv2
import numpy as np

class FaceAuthenticator:
    def __init__(self, database, threshold=80.0):
        self.db = database
        self.threshold = threshold # Pour LBPH, plus bas = plus proche

    def authenticate(self, current_face_gray):
        """Compare le visage actuel avec la base via template matching ou LBPH."""
        users = self.db.get_all_users()
        if not users:
            return None, 100.0
        
        best_match = None
        min_dist = 1000.0
        
        for user in users:
            known_face = np.array(user['embedding'], dtype=np.uint8)
            # Comparaison simple par corrélation (Template Matching)
            res = cv2.matchTemplate(current_face_gray, known_face, cv2.TM_SQDIFF_NORMED)
            dist = cv2.minMaxLoc(res)[0] * 100 # Score de 0 à 100
            
            if dist < min_dist:
                min_dist = dist
                best_match = user['name']
        
        if min_dist < self.threshold:
            return best_match, min_dist
        return None, min_dist
