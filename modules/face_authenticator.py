import cv2
import numpy as np

class FaceAuthenticator:
    def __init__(self, database, threshold=50.0):
        self.db = database
        self.threshold = threshold 

    def authenticate(self, current_face_gray):
        """Compare le visage actuel avec la base via Template Matching."""
        users = self.db.get_all_users()
        if not users or current_face_gray is None:
            return None, 100.0
        
        best_match = None
        min_dist = 1000.0
        
        # S'assurer du bon format pour NumPy
        current_face_gray = np.array(current_face_gray, dtype=np.uint8)
        
        for user in users:
            known_face = np.array(user['embedding'], dtype=np.uint8).reshape(100, 100)
            
            # Comparaison par corrélation (Template Matching)
            res = cv2.matchTemplate(current_face_gray, known_face, cv2.TM_SQDIFF_NORMED)
            dist = cv2.minMaxLoc(res)[0] * 100 
            
            if dist < min_dist:
                min_dist = dist
                best_match = user['name']
        
        if min_dist < self.threshold:
            return best_match, min_dist
        return None, min_dist
