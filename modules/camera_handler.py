import cv2

class CameraHandler:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        return self.cap.isOpened()

    def get_frame(self):
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None

    def stop(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
