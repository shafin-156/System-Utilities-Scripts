import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import json
import os
import base64
import threading
import webbrowser
import sys  # Added for PyInstaller resource path handling
from datetime import datetime

class ModernGitHubUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Batch Uploader v2.9.5")
        self.root.geometry("800x400")
        self.root.configure(bg="#1e1e1e")

        # ==========================================
        # COMPILED .EXE COMPATIBLE ICON LOADER
        # ==========================================
        try:
            # Handle PyInstaller .exe file paths (sys._MEIPASS)
            if getattr(sys, 'frozen', False):
                # Running as compiled .exe
                base_path = sys._MEIPASS
            else:
                # Running as normal Python script
                base_path = os.path.abspath(".")
            
            icon_path = os.path.join(base_path, 'icon.ico')
            self.root.iconbitmap(icon_path)
        except:
            pass  # Safe fallback if icon.ico is missing

        # State variables
        self.is_uploading = False
        self.current_file_index = 0
        self.total_files = 0

        # Config file path
        self.config_file = "github_config.json"
        self.config = self.load_config()

        # Modern Color Palette
        self.colors = {
            "bg": "#1e1e1e",
            "frame_bg": "#2d2d2d",
            "fg": "#d4d4d4",
            "accent": "#007acc",
            "success": "#2ecc71",
            "danger": "#e74c3c",
            "entry_bg": "#3c3c3c",
            "border": "#3e3e3e"
        }

        self.setup_styles()
        self.create_widgets()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_config(self):
        data = {
            "github_token": self.entry_token.get(),
            "owner": self.entry_owner.get(),
            "repo": self.entry_repo.get(),
            "branch": self.entry_branch.get()
        }
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=4)
        self.log("Settings saved successfully.")
        self.update_status("Settings Saved", "success")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        bg = self.colors["bg"]
        frame_bg = self.colors["frame_bg"]
        fg = self.colors["fg"]
        accent = self.colors["accent"]
        entry_bg = self.colors["entry_bg"]

        style.configure("TNotebook", background=bg, borderwidth=0)
        style.configure("TNotebook.Tab", background=frame_bg, foreground=fg, padding=[12, 4], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", accent)], foreground=[("selected", "#ffffff")])

        style.configure("Card.TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg, font=("Segoe UI", 10))
        style.configure("TEntry", fieldbackground=entry_bg, foreground=fg, bordercolor="#444", lightcolor="#444", darkcolor="#444")
        
        style.configure("Accent.TButton", background=accent, foreground="#ffffff", borderwidth=0, focuscolor="none", font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#005c99")])
        
        style.configure("TProgressbar", background=accent, troughcolor=entry_bg, thickness=12)
        style.configure("TCheckbutton", background=bg, foreground=fg)

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, expand=True, fill="both", padx=10)

        # 1. Settings Tab
        self.tab_config = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(self.tab_config, text=" ⚙️ Settings ")
        self.setup_config_tab()

        # 2. Uploader Tab
        self.tab_upload = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(self.tab_upload, text=" 📁 Multi-Uploader ")
        self.setup_upload_tab()

        # 3. Logs Tab
        self.tab_logs = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(self.tab_logs, text=" 📝 Activity Logs ")
        self.setup_logs_tab()

        # 4. Guide Tab
        self.tab_guide = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(self.tab_guide, text=" 📖 User Guide ")
        self.setup_guide_tab()

        # Status Bar
        self.status_frame = tk.Frame(self.root, bg=self.colors["frame_bg"], height=30)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_frame.pack_propagate(False)

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(self.status_frame, textvariable=self.status_var, bg=self.colors["frame_bg"], fg=self.colors["fg"], anchor="w", padx=15, font=("Segoe UI", 10))
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.status_indicator = tk.Label(self.status_frame, text="✔", bg=self.colors["frame_bg"], fg="#4CAF50", padx=15)
        self.status_indicator.pack(side=tk.RIGHT)

    # ==========================================
    # TAB 1: SETTINGS
    # ==========================================
    def setup_config_tab(self):
        self.tab_config.grid_columnconfigure(0, weight=1)
        self.tab_config.grid_rowconfigure(0, weight=1)
        
        left_frame = ttk.Frame(self.tab_config, style="Card.TFrame")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=50, pady=15)
        
        main_frame = ttk.LabelFrame(left_frame, text="🔐 GitHub Credentials", padding=15)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Token
        ttk.Label(main_frame, text="Personal Access Token:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_token = ttk.Entry(main_frame, width=50, show="*")
        self.entry_token.grid(row=0, column=1, padx=10, pady=5)
        self.entry_token.insert(0, self.config.get("github_token", "(e.g. ghp_xxxxxxxxxxxxxx)"))

        self.show_token = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="Show Token", variable=self.show_token, command=self.toggle_token_visibility).grid(row=0, column=2)

        # Owner, Repo, Branch
        ttk.Label(main_frame, text="Owner Username:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_owner = ttk.Entry(main_frame, width=50)
        self.entry_owner.grid(row=1, column=1, padx=10, pady=5)
        self.entry_owner.insert(0, self.config.get("owner", "(e.g. your_github_username)"))

        ttk.Label(main_frame, text="Repository:").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_repo = ttk.Entry(main_frame, width=50)
        self.entry_repo.grid(row=2, column=1, padx=10, pady=5)
        self.entry_repo.insert(0, self.config.get("repo", "(e.g. my_repository_name)"))

        ttk.Label(main_frame, text="Branch:").grid(row=3, column=0, sticky="w", pady=5)
        self.entry_branch = ttk.Entry(main_frame, width=50)
        self.entry_branch.grid(row=3, column=1, padx=10, pady=5)
        self.entry_branch.insert(0, self.config.get("branch", "main"))

        # Action Button
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=15)
        ttk.Button(btn_frame, text="🔒 Save & Verify", style="Accent.TButton", command=self.save_and_test).pack(ipadx=10, ipady=5)

        # ==========================================
        # CREATOR CREDIT & LINK
        # ==========================================
        credit_frame = ttk.Frame(left_frame, style="Card.TFrame")
        credit_frame.pack(side=tk.BOTTOM, anchor=tk.E, pady=10, padx=10)
        
        ttk.Label(credit_frame, text="Created by: ", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        
        link_label = tk.Label(credit_frame, text="SHAFIN (github.com/shafin-156)", 
                              font=("Segoe UI", 9, "underline"), 
                              fg=self.colors["accent"], 
                              bg=self.colors["bg"], 
                              cursor="hand2")
        link_label.pack(side=tk.LEFT)
        link_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/shafin-156"))

    # ==========================================
    # TAB 2: MULTI-UPLOADER
    # ==========================================
    def setup_upload_tab(self):
        wrapper = ttk.Frame(self.tab_upload, style="Card.TFrame")
        wrapper.pack(expand=True, fill="both", padx=20, pady=20)

        main_frame = ttk.LabelFrame(wrapper, text="Upload Batch or Folder", padding=20, style="Card.TFrame")
        main_frame.pack(expand=True, fill="both")

        # Local Path
        row = 0
        ttk.Label(main_frame, text="Local Path:").grid(row=row, column=0, sticky="w", pady=8)
        self.entry_local_path = ttk.Entry(main_frame, width=55)
        self.entry_local_path.grid(row=row, column=1, padx=10, pady=8, sticky="ew")
        self.entry_local_path.insert(0, "(e.g. C:\\Users\\Name\\Projects\\MyApp)")
        ttk.Button(main_frame, text="Browse Folder", style="Accent.TButton", command=self.browse_folder).grid(row=row, column=2, padx=5)

        # Remote Path
        row += 1
        ttk.Label(main_frame, text="Target Remote Dir:").grid(row=row, column=0, sticky="w", pady=8)
        self.entry_remote_base = ttk.Entry(main_frame, width=55)
        self.entry_remote_base.grid(row=row, column=1, padx=10, pady=8, sticky="ew")
        ttk.Label(main_frame, text="(Keep Blank for Root Directory)", background="#1e1e1e", foreground="#888888").grid(row=row, column=2)

        # Commit Message
        row += 1
        ttk.Label(main_frame, text="Commit Message:").grid(row=row, column=0, sticky="w", pady=8)
        self.entry_commit_msg = ttk.Entry(main_frame, width=55)
        self.entry_commit_msg.grid(row=row, column=1, padx=10, pady=8, sticky="ew")
        self.entry_commit_msg.insert(0, "Batch update via GitHub Script")

        # Progress
        row += 1
        progress_frame = ttk.Frame(main_frame, style="Card.TFrame")
        progress_frame.grid(row=row, column=0, columnspan=3, pady=15, sticky="ew")
        
        self.progress = ttk.Progressbar(progress_frame, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(side=tk.LEFT, padx=10, expand=True, fill="x")
        self.progress_label = ttk.Label(progress_frame, text="0 / 0 files")
        self.progress_label.pack(side=tk.LEFT, padx=10)

        # Action Button
        row += 1
        self.btn_upload = ttk.Button(main_frame, text="🚀 START UPLOAD", style="Accent.TButton", command=self.start_upload_process)
        self.btn_upload.grid(row=row, column=0, columnspan=3, pady=15, ipadx=20, ipady=8)

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.entry_local_path.delete(0, tk.END)
            self.entry_local_path.insert(0, folder_path)
            folder_name = os.path.basename(folder_path)
            self.entry_remote_base.delete(0, tk.END)
            self.entry_remote_base.insert(0, folder_name)

    # ==========================================
    # TAB 3: LOGS
    # ==========================================
    def setup_logs_tab(self):
        wrapper = ttk.Frame(self.tab_logs, style="Card.TFrame")
        wrapper.pack(expand=True, fill="both", padx=20, pady=20)

        frame = ttk.LabelFrame(wrapper, text="Real-time Logs", padding=10, style="Card.TFrame")
        frame.pack(expand=True, fill="both")

        self.logs_text = tk.Text(frame, height=12, width=100, bg=self.colors["entry_bg"], fg="#d4d4d4", font=("Consolas", 10), borderwidth=0, relief="flat")
        self.logs_text.pack(side=tk.LEFT, expand=True, fill="both")
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.logs_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.logs_text.config(yscrollcommand=scrollbar.set)
        
        self.log("Application started successfully.")

    # ==========================================
    # TAB 4: GUIDE
    # ==========================================
    def setup_guide_tab(self):
        wrapper = ttk.Frame(self.tab_guide, style="Card.TFrame")
        wrapper.pack(expand=True, fill="both", padx=20, pady=20)

        guide_frame = ttk.LabelFrame(wrapper, text="📋 Full Process Guide", padding=10)
        guide_frame.pack(fill=tk.BOTH, expand=True)
        
        self.guide_text = tk.Text(guide_frame, wrap=tk.WORD, bg=self.colors["entry_bg"], fg=self.colors["fg"], font=("Segoe UI", 10), borderwidth=0)
        self.guide_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        guide_scroll = ttk.Scrollbar(guide_frame, orient="vertical", command=self.guide_text.yview)
        guide_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.guide_text.config(yscrollcommand=guide_scroll.set)
        
        # Formatting Tags
        self.guide_text.tag_config("title", font=("Segoe UI", 12, "bold"), foreground=self.colors["accent"], spacing3=10)
        self.guide_text.tag_config("step", font=("Segoe UI", 10, "bold"), foreground="#d4d4d4", spacing1=5, spacing3=5)
        self.guide_text.tag_config("body", foreground="#b0b0b0", spacing3=3)

        # Guide Content
        self.guide_text.config(state='normal')
        self.guide_text.delete(1.0, tk.END)
        self.guide_text.insert(tk.END, "Step 1: Generate GitHub Token\n", "step")
        self.guide_text.insert(tk.END, "Go to GitHub > Settings > Developer settings > Personal access tokens > Tokens (classic). Create a new token and check the 'repo' scope (for writing permissions). Copy the generated token.\n\n", "body")
        
        self.guide_text.insert(tk.END, "Step 2: Connect Repository\n", "step")
        self.guide_text.insert(tk.END, "Paste the token into the 'Personal Access Token' field on the left. Enter your GitHub Username (Owner), Repository Name, and Target Branch (e.g., 'main'). Click 'Save & Verify' to confirm authentication.\n\n", "body")
        
        self.guide_text.insert(tk.END, "Step 3: Select Target Files\n", "step")
        self.guide_text.insert(tk.END, "Switch to the 'Multi-Uploader' tab. Click 'Browse Folder' to select a local directory or a single file to upload.\n\n", "body")
        
        self.guide_text.insert(tk.END, "Step 4: Remote Path & Commit\n", "step")
        self.guide_text.insert(tk.END, "Specify a 'Target Remote Dir' in GitHub (e.g., 'assets/images/'), or leave it blank to upload directly to the repository root. Type a meaningful Commit Message.\n\n", "body")
        
        self.guide_text.insert(tk.END, "Step 5: Execute Batch Upload\n", "step")
        self.guide_text.insert(tk.END, "Click the 'START UPLOAD' button. The tool will recursively process every file. Monitor real-time status and results in the 'Activity Logs' tab.\n\n", "body")
        
        self.guide_text.insert(tk.END, "⚠️ Important Notes\n", "step")
        self.guide_text.insert(tk.END, "- The tool automatically overwrites existing files on GitHub.\n- Large files may take longer due to GitHub API encoding limits.\n- Your local folder structure is perfectly preserved on the remote repository.\n", "body")
        
        self.guide_text.config(state='disabled')

    # ==========================================
    # LOGIC & HELPER FUNCTIONS
    # ==========================================
    def toggle_token_visibility(self):
        if self.show_token.get():
            self.entry_token.config(show="")
        else:
            self.entry_token.config(show="*")

    def update_status(self, message, state=None):
        self.status_var.set(message)
        color_map = {
            "success": self.colors["success"],
            "danger": self.colors["danger"],
            "info": self.colors["accent"]
        }
        self.status_indicator.config(fg=color_map.get(state, "#4CAF50"))

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs_text.config(state='normal')
        self.logs_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.logs_text.see(tk.END)
        self.logs_text.config(state='disabled')

    def save_and_test(self):
        self.save_config()
        self.test_connection()

    def test_connection(self):
        token = self.entry_token.get()
        if not token:
            messagebox.showerror("Error", "Token cannot be empty!")
            return
        
        self.update_status("Testing connection...", "info")
        self.log("Validating token...")
        
        def check():
            try:
                headers = {"Authorization": f"token {token}"}
                resp = requests.get("https://api.github.com/user", headers=headers)
                if resp.status_code == 200:
                    self.root.after(0, lambda: messagebox.showinfo("Success", f"Authenticated as: {resp.json()['login']}"))
                    self.root.after(0, lambda: self.update_status("Connected", "success"))
                    self.root.after(0, lambda: self.log("Connection test successful."))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Failed", f"Error {resp.status_code}"))
                    self.root.after(0, lambda: self.update_status("Connection failed", "danger"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.root.after(0, lambda: self.update_status("Connection error", "danger"))
        
        threading.Thread(target=check, daemon=True).start()

    # ==========================================
    # BATCH UPLOAD CORE
    # ==========================================
    def start_upload_process(self):
        if self.is_uploading:
            messagebox.showwarning("Busy", "An upload is currently in progress.")
            return

        token = self.entry_token.get()
        owner = self.entry_owner.get()
        repo = self.entry_repo.get()
        branch = self.entry_branch.get()
        local_base = self.entry_local_path.get()
        remote_base = self.entry_remote_base.get().strip()
        commit_msg = self.entry_commit_msg.get()

        if not os.path.exists(local_base):
            messagebox.showerror("Error", "Selected local path does not exist.")
            return

        file_list = []
        if os.path.isfile(local_base):
            file_list.append(local_base)
        elif os.path.isdir(local_base):
            for root, dirs, files in os.walk(local_base):
                for file in files:
                    file_list.append(os.path.join(root, file))
        
        if not file_list:
            messagebox.showerror("Error", "Selected directory is empty.")
            return

        self.total_files = len(file_list)
        self.current_file_index = 0
        self.is_uploading = True
        self.btn_upload.config(state="disabled", text="⏳ UPLOADING...")
        self.progress["value"] = 0
        self.progress_label.config(text=f"0 / {self.total_files}")
        self.update_status("Batch uploading...", "info")

        self.log(f"Starting batch upload of {self.total_files} files.")
        thread = threading.Thread(target=self.perform_batch_upload, args=(token, owner, repo, branch, local_base, remote_base, commit_msg, file_list))
        thread.daemon = True
        thread.start()

    def perform_batch_upload(self, token, owner, repo, branch, local_base, remote_base, commit_msg, file_list):
        headers = {"Authorization": f"token {token}"}
        
        for file_path in file_list:
            if not self.is_uploading:
                break

            if os.path.isfile(local_base):
                relative_path = os.path.basename(local_base)
            else:
                relative_path = os.path.relpath(file_path, local_base).replace("\\", "/")
            
            remote_path = relative_path if not remote_base else f"{remote_base.rstrip('/')}/{relative_path}"
            remote_path = remote_path.lstrip('/')
            
            self.current_file_index += 1
            progress_percent = int((self.current_file_index / self.total_files) * 100)
            
            self.root.after(0, lambda p=progress_percent, c=self.current_file_index: self.update_progress(p, c))
            self.root.after(0, lambda p=remote_path: self.log(f"Uploading [{self.current_file_index}]: {p}"))

            try:
                url = f"https://api.github.com/repos/{owner}/{repo}/contents/{remote_path}"
                
                get_resp = requests.get(url, headers=headers, params={"ref": branch})
                sha = None
                if get_resp.status_code == 200:
                    sha = get_resp.json()['sha']
                
                with open(file_path, 'rb') as f:
                    content_bytes = f.read()
                content_enc = base64.b64encode(content_bytes).decode('ascii')
                
                payload = {"message": commit_msg, "content": content_enc, "branch": branch}
                if sha:
                    payload["sha"] = sha
                
                upload_resp = requests.put(url, headers=headers, json=payload)
                
                if upload_resp.status_code in [200, 201]:
                    self.root.after(0, lambda p=remote_path: self.log(f"✅ OK: {p}"))
                else:
                    self.root.after(0, lambda p=remote_path, e=upload_resp.text: self.log(f"❌ ERROR {p}: {e}"))

            except Exception as e:
                self.root.after(0, lambda p=remote_path, e=str(e): self.log(f"⚠️ Exception {p}: {e}"))

        self.is_uploading = False
        self.root.after(0, lambda: self.btn_upload.config(state="normal", text="🚀 START UPLOAD"))
        self.root.after(0, lambda: self.log("Batch upload process completed."))
        self.root.after(0, lambda: self.update_status("Batch completed.", "success"))
        self.root.after(0, lambda: messagebox.showinfo("Complete", f"Processed {self.total_files} files."))

    def update_progress(self, percent, current_file):
        self.progress["value"] = percent
        self.progress_label.config(text=f"{current_file} / {self.total_files}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernGitHubUploaderApp(root)
    root.mainloop()