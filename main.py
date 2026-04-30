import cv2
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import time
import numpy as np
import os
from datetime import datetime

# Importation des modules locaux
from modules.database import Database
from modules.camera_handler import CameraHandler
from modules.face_detector import FaceDetector
from modules.face_encoder import FaceEncoder
from modules.face_authenticator import FaceAuthenticator
from modules.system_controller import SystemController

class FaceLockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FaceLock Ultra Security")
        self.root.geometry("1100x700")
        ctk.set_appearance_mode("dark")
        
        # Initialisation des composants
        self.db = Database()
        self.camera = CameraHandler()
        self.detector = FaceDetector()
        self.encoder = FaceEncoder()
        self.authenticator = FaceAuthenticator(self.db)
        self.system = SystemController()
        
        # Variables d'état
        self.is_running = False
        self.is_monitoring = False
        self.guest_mode = False
        self.guest_end_time = 0
        self.last_seen_time = time.time()
        self.default_timeout = 10 
        self.intruder_timeout = 5 # Verrouillage rapide si inconnu
        
        self.admin_password = "1234"
        self.has_blinked = False
        self.eyes_closed_frames = 0
        
        # Création du dossier intrus s'il n'existe pas
        if not os.path.exists("intrus"):
            os.makedirs("intrus")
        
        self.setup_ui()

    def setup_ui(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self.root, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="FACELOCK ULTRA", font=("Impact", 28), text_color="#3498db").pack(pady=30)

        self.btn_enroll = ctk.CTkButton(self.sidebar, text="ENRÔLER", height=45, command=self.enroll_user)
        self.btn_enroll.pack(pady=10, padx=20)
        
        self.btn_monitor = ctk.CTkButton(self.sidebar, text="ACTIVER PROTECTION", height=45, fg_color="#2ecc71", command=self.toggle_monitoring)
        self.btn_monitor.pack(pady=10, padx=20)

        self.btn_guest = ctk.CTkButton(self.sidebar, text="MODE INVITÉ", height=45, fg_color="#9b59b6", command=self.toggle_guest)
        self.btn_guest.pack(pady=10, padx=20)
        
        self.status_label = ctk.CTkLabel(self.sidebar, text="SYSTÈME PRÊT", text_color="#95a5a6")
        self.status_label.pack(side="bottom", pady=30)

        # Zone Vidéo
        self.video_frame = ctk.CTkFrame(self.root, fg_color="black")
        self.video_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.video_label = tk.Label(self.video_frame, bg="black")
        self.video_label.pack(expand=True, fill="both")

    def toggle_guest(self):
        password = ctk.CTkInputDialog(text="Entrez le code de sécurité :", title="Sécurité").get_input()
        if password == self.admin_password:
            if not self.guest_mode:
                duration_str = ctk.CTkInputDialog(text="Durée (minutes) :", title="Durée").get_input()
                try:
                    duration = int(duration_str)
                    self.guest_mode = True
                    self.guest_end_time = time.time() + (duration * 60)
                    self.btn_guest.configure(text=f"INVITÉ ({duration}m)", fg_color="#8e44ad")
                except:
                    messagebox.showerror("Erreur", "Veuillez entrer un nombre valide.")
            else:
                self.guest_mode = False
                self.btn_guest.configure(text="MODE INVITÉ", fg_color="#9b59b6")
        elif password is not None:
            messagebox.showerror("Erreur", "Code incorrect !")

    def toggle_monitoring(self):
        if not self.is_monitoring:
            if self.camera.start():
                self.is_monitoring = self.is_running = True
                self.has_blinked = False
                self.btn_monitor.configure(text="DÉSACTIVER", fg_color="#e74c3c")
                self.status_label.configure(text="PROTECTION ACTIVE", text_color="#2ecc71")
                threading.Thread(target=self.update_frame, daemon=True).start()
        else:
            self.is_monitoring = self.is_running = False
            self.camera.stop()
            self.btn_monitor.configure(text="ACTIVER PROTECTION", fg_color="#2ecc71")
            self.status_label.configure(text="SYSTÈME PRÊT", text_color="#95a5a6")

    def update_frame(self):
        unknown_presence_start = None
        
        while self.is_running:
            frame = self.camera.get_frame()
            if frame is not None:
                if self.guest_mode and time.time() > self.guest_end_time:
                    self.guest_mode = False
                    self.btn_guest.configure(text="MODE INVITÉ", fg_color="#9b59b6")

                if self.guest_mode:
                    cv2.putText(frame, "MODE INVITE ACTIF", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (155, 89, 182), 2)
                else:
                    faces = self.detector.detect_faces(frame)
                    if len(faces) > 0:
                        self.last_seen_time = time.time()
                        for bbox in faces:
                            x, y, w, h = bbox
                            face_img = self.detector.crop_face(frame, bbox)
                            face_gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
                            
                            eyes_count = self.detector.get_eyes_count(face_gray)
                            if eyes_count == 0: self.eyes_closed_frames += 1
                            else:
                                if self.eyes_closed_frames >= 1: self.has_blinked = True
                                self.eyes_closed_frames = 0

                            embedding = self.encoder.get_embedding(face_img)
                            name, dist = self.authenticator.authenticate(embedding)
                            
                            if name:
                                unknown_presence_start = None
                                if self.has_blinked:
                                    label, color = f"{name}", (46, 204, 113)
                                else:
                                    label, color = "CLIGNEZ DES YEUX", (0, 165, 255)
                            else:
                                if unknown_presence_start is None:
                                    unknown_presence_start = time.time()
                                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    cv2.imwrite(f"intrus/intrus_{ts}.jpg", frame)
                                
                                elapsed = time.time() - unknown_presence_start
                                countdown = int(self.intruder_timeout - elapsed)
                                label, color = f"INCONNU - LOCK {max(0, countdown)}s", (231, 76, 60)
                                
                                if countdown <= 0:
                                    self.system.lock_session()
                                    unknown_presence_start = None
                            
                            cv2.rectangle(frame, (x, y), (x+w, y+h), color[::-1], 2)
                            cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_DUPLEX, 0.7, color[::-1], 2)
                    else:
                        unknown_presence_start = None
                        self.has_blinked = False
                        countdown = int(self.default_timeout - (time.time() - self.last_seen_time))
                        if 0 < countdown < self.default_timeout:
                            cv2.putText(frame, f"ABSENCE - LOCK {countdown}s", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
                        elif countdown <= 0:
                            self.system.lock_session()
                            self.last_seen_time = time.time()

                img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                self.video_label.after(10, lambda: self.video_label.config(image=img))
                self.video_label.image = img
            time.sleep(0.03)

    def enroll_user(self):
        name = ctk.CTkInputDialog(text="Nom :", title="Enrôlement").get_input()
        if name:
            self.camera.start()
            time.sleep(2)
            frame = self.camera.get_frame()
            faces = self.detector.detect_faces(frame)
            if len(faces) > 0:
                face_img = self.detector.crop_face(frame, faces[0])
                embedding = self.encoder.get_embedding(face_img)
                self.db.add_user(name, embedding)
                messagebox.showinfo("Succès", f"Utilisateur {name} ajouté.")
            if not self.is_monitoring: self.camera.stop()

if __name__ == "__main__":
    root = ctk.CTk()
    app = FaceLockApp(root)
    root.mainloop()
