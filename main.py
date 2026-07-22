import psutil
import tkinter as tk
import time
import hashlib
import os
import sys

# --- Configuration ---
TARGET_APP = "brave.exe"

# Sha256 hash (Password: ..)
PASSWORD_HASH = "5ec1f7e700f37c3d0b2981d04855fc34b94aaa15457b05ca571817442d228f81"


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class AppLocker:
    def __init__(self, target_app, pwd_hash):
        self.target_app = target_app.lower()
        self.pwd_hash = pwd_hash
        self.is_unlocked = False

    def get_target_processes(self):
        """Returns a list of all running processes matching the target app."""
        processes = []
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'] and proc.info['name'].lower() == self.target_app:
                    processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes

    def manage_processes(self, action='kill', procs=None):
        """Suspends, resumes, or kills a list of processes."""
        if procs is None:
            procs = self.get_target_processes()

        for proc in procs:
            try:
                if action == 'kill':
                    proc.kill()
                elif action == 'suspend':
                    proc.suspend()
                elif action == 'resume':
                    proc.resume()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def verify_password(self):
        """Displays a custom, Brave-themed tkinter dialog to verify the password."""
        root = tk.Tk()
        root.title("Brave")

        # Apply the icon to the window title bar gracefully
        try:
            root.iconbitmap(resource_path("icon.ico"))
        except Exception:
            pass

        root.geometry("380x240")
        root.configure(bg="#202324")  # Brave Dark Gray Background
        root.attributes("-topmost", True)  # Force window to the front
        root.focus_force()
        root.resizable(False, False)

        # Center the window on the screen
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (380 // 2)
        y = (root.winfo_screenheight() // 2) - (240 // 2)
        root.geometry(f"+{x}+{y}")

        result = []

        # Button / Enter key logic
        def submit(event=None):
            result.append(entry.get())
            root.quit()

        def on_closing():
            result.append("")  # Empty string if they close the window
            root.quit()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        # --- Custom UI Design ---
        tk.Label(root, text="Brave Security Guard", font=("Segoe UI", 20, "bold"),
                 bg="#202324", fg="#FB542B").pack(pady=(25, 0))

        tk.Label(root, text="Authentication required to proceed:", font=("Segoe UI", 10),
                 bg="#202324", fg="#E0E0E0").pack(pady=(0, 15))

        entry = tk.Entry(root, show="✵✵", font=("Segoe UI", 20), bg="#303436", fg="#FFFFFF",
                         insertbackground="#FB542B", relief="flat", justify="center")
        entry.pack(pady=5, padx=45, fill="x", ipady=5)
        entry.focus_set()

        root.bind('<Return>', submit)  # Let user press 'Enter' to submit

        btn = tk.Button(root, text="UNLOCK", font=("Segoe UI", 11, "bold"), bg="#FB542B", fg="#FFFFFF",
                        activebackground="#E0411B", activeforeground="#FFFFFF", relief="flat",
                        cursor="hand2", command=submit)
        btn.pack(pady=15, padx=45, fill="x", ipady=4)

        root.mainloop()

        try:
            root.destroy()
        except tk.TclError:
            pass

        # Extract the typed password
        pwd_input = result[0] if result else ""

        if not pwd_input:
            return False

        # Hash the input and compare it
        input_hash = hashlib.sha256(pwd_input.encode()).hexdigest()
        return input_hash == self.pwd_hash

    def run(self):
        while True:
            try:
                procs = self.get_target_processes()

                if procs and not self.is_unlocked:
                    # Freeze the browser instantly
                    self.manage_processes('suspend', procs)

                    if self.verify_password():
                        self.manage_processes('resume', procs)  # Unfreeze browser
                        self.is_unlocked = True
                    else:
                        self.manage_processes('kill', procs)

                elif not procs and self.is_unlocked:
                    # If Brave is completely closed by the user, re-arm the locker
                    self.is_unlocked = False

                time.sleep(1)  # Optimization check interval

            except Exception:
                time.sleep(2)


if __name__ == "__main__":
    locker = AppLocker(TARGET_APP, PASSWORD_HASH)
    locker.run()