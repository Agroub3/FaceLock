import cv2
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import time
import numpy as np

from modules.database import Database
from modules.camera_handler import CameraHandler
from modules.face_detector import FaceDetector
from modules.face_encoder import FaceEncoder
from modules.face_authenticator import FaceAuthenticator
from modules.system_controller import SystemController

class FaceLockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FaceLock - Version Stable")
        self.root.geometry("900x600")
        ctk.set_appearance_mode("dark")
        
        self.db = Database()
        self.camera = CameraHandler()
        self.detector = FaceDetector()
        self.encoder = FaceEncoder()
        self.authenticator = FaceAuthenticator(self.db)
        self.system = SystemController()
        
        self.is_running = False
        self.is_monitoring = False
        self.last_seen_time = time.time()
        self.lock_timeout = 10 
        
        self.setup_ui()

    def setup_ui(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="FaceLock", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        self.btn_enroll = ctk.CTkButton(self.sidebar, text="Enrôler Utilisateur", command=self.enroll_user)
        self.btn_enroll.pack(pady=10, padx=20)
        self.btn_monitor = ctk.CTkButton(self.sidebar, text="Démarrer Surveillance", command=self.toggle_monitoring)
        self.btn_monitor.pack(pady=10, padx=20)
        self.status_label = ctk.CTkLabel(self.sidebar, text="Statut: Inactif", text_color="gray")
        self.status_label.pack(side="bottom", pady=20)
        self.video_frame = ctk.CTkFrame(self.root)
        self.video_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.video_label = tk.Label(self.video_frame, bg="black")
        self.video_label.pack(expand=True, fill="both")

    def toggle_monitoring(self):
        if not self.is_monitoring:
            if self.camera.start():
                self.is_monitoring = True
                self.is_running = True
                self.btn_monitor.configure(text="Arrêter Surveillance", fg_color="red")
                self.status_label.configure(text="Statut: Actif", text_color="green")
                self.last_seen_time = time.time()
                threading.Thread(target=self.update_frame, daemon=True).start()
        else:
            self.is_monitoring = False
            self.is_running = False
            self.camera.stop()
            self.btn_monitor.configure(text="Démarrer Surveillance", fg_color=["#3a7ebf", "#1f538d"])
            self.status_label.configure(text="Statut: Inactif", text_color="gray")

    def update_frame(self):
        while self.is_running:
            frame = self.camera.get_frame()
            if frame is not None:
                faces = self.detector.detect_faces(frame)
                if faces:
                    self.last_seen_time = time.time()
                    for bbox in faces:
                        x, y, w, h = bbox
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        face_img = self.detector.crop_face(frame, bbox)
                        embedding = self.encoder.get_embedding(face_img)
                        name, dist = self.authenticator.authenticate(embedding)
                        label = f"{name}" if name else "Inconnu"
                        cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                else:
                    if time.time() - self.last_seen_time > self.lock_timeout:
                        self.system.lock_session()
                        self.last_seen_time = time.time()

                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                img_tk = ImageTk.PhotoImage(image=img)
                self.video_label.after(10, lambda: self.video_label.config(image=img_tk))
                self.video_label.image = img_tk
            time.sleep(0.03)

    def enroll_user(self):
        dialog = ctk.CTkInputDialog(text="Nom de l'utilisateur:", title="Enrôlement")
        name = dialog.get_input()
        if name:
            self.camera.start()
            time.sleep(1)
            frame = self.camera.get_frame()
            faces = self.detector.detect_faces(frame)
            if faces:
                face_img = self.detector.crop_face(frame, faces[0])
                embedding = self.encoder.get_embedding(face_img)
                self.db.add_user(name, embedding)
                messagebox.showinfo("Succès", f"Utilisateur {name} ajouté.")
            self.camera.stop()

if __name__ == "__main__":
    root = ctk.CTk()
    app = FaceLockApp(root)
    root.mainloop()
