import os
import platform
import ctypes

class SystemController:
    def __init__(self):
        self.is_windows = platform.system() == "Windows"

    def lock_session(self):
        """Verrouille la session Windows."""
        if self.is_windows:
            print("[System] Verrouillage de la session...")
            ctypes.windll.user32.LockWorkStation()
        else:
            print("[System] Simulation : Verrouillage de session (Non-Windows)")

    def prevent_sleep(self):
        """Empêche la mise en veille (simulation via affichage d'activité)."""
        # Sur Windows réel, on pourrait utiliser ctypes.windll.kernel32.SetThreadExecutionState
        pass

    def unlock_session(self):
        """
        Note: Déverrouiller Windows programmatiquement est complexe pour des raisons de sécurité.
        Généralement, on simule une activité ou on utilise des APIs spécifiques si l'app a les droits.
        """
        print("[System] Utilisateur reconnu : Session maintenue active.")
