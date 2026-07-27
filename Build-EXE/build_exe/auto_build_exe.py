#!/usr/bin/env python3
"""
build_exe.py - Advanced GUI for PyInstaller
- Browse .py script, .ico icon, output folder
- One-file / One-folder, console/windowed, clean, debug, custom name
- Icon is automatically embedded AND added as runtime data (no extra files needed)
- Add any other data files/folders
- Progress bar during build
- Automatically deletes build/ and .spec files after successful build
- Shows "All Complete" message with the final .exe location
"""
import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import shutil

class PyInstallerGUI:
    def __init__(self, root):
        self.root = root
        root.title("Build EXE - PyInstaller GUI")
        root.geometry("720x520")  # reduced height for compactness
        root.resizable(False, False)

        # Variables
        self.script_path = tk.StringVar(value=os.getcwd())
        self.icon_path = tk.StringVar()
        self.output_dir = tk.StringVar(value="OUTPUT")
        self.onefile = tk.BooleanVar(value=True)
        self.noconsole = tk.BooleanVar(value=True)
        self.clean = tk.BooleanVar(value=True)
        self.debug = tk.BooleanVar(value=False)
        self.name = tk.StringVar()
        self.data_files = []   # list of (source, dest) tuples

        self.build_frame(root)
        self.options_frame(root)
        self.data_frame(root)
        self.command_frame(root)
        self.progress_frame(root)
        self.run_button(root)

    def build_frame(self, parent):
        frame = tk.LabelFrame(parent, text="Main Script & Output", padx=8, pady=8)
        frame.pack(fill="x", padx=10, pady=3)

        tk.Label(frame, text="Python Script:").grid(row=0, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.script_path, width=50).grid(row=0, column=1, padx=5)
        tk.Button(frame, text="Browse", command=self.browse_script).grid(row=0, column=2)

        tk.Label(frame, text="Icon (.ico):").grid(row=1, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.icon_path, width=50).grid(row=1, column=1, padx=5)
        tk.Button(frame, text="Browse", command=self.browse_icon).grid(row=1, column=2)
        tk.Label(frame, text="(auto‑added as data)", fg="gray", font=("Arial", 8)).grid(row=1, column=3, padx=5)

        tk.Label(frame, text="Output Dir:").grid(row=2, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.output_dir, width=50).grid(row=2, column=1, padx=5)
        tk.Button(frame, text="Browse", command=self.browse_output).grid(row=2, column=2)

    def options_frame(self, parent):
        frame = tk.LabelFrame(parent, text="PyInstaller Options", padx=8, pady=8)
        frame.pack(fill="x", padx=10, pady=3)

        tk.Checkbutton(frame, text="One-file (--onefile)", variable=self.onefile).grid(row=0, column=0, sticky="w")
        tk.Checkbutton(frame, text="No console (--windowed)", variable=self.noconsole).grid(row=0, column=1, sticky="w")
        tk.Checkbutton(frame, text="Clean (--clean)", variable=self.clean).grid(row=0, column=2, sticky="w")
        tk.Checkbutton(frame, text="Debug (--debug)", variable=self.debug).grid(row=0, column=3, sticky="w")

        tk.Label(frame, text="Custom EXE name:").grid(row=1, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.name, width=20).grid(row=1, column=1, sticky="w", padx=5)

    def data_frame(self, parent):
        frame = tk.LabelFrame(parent, text="Additional Data Files (--add-data)", padx=8, pady=8)
        frame.pack(fill="x", padx=10, pady=3)

        self.data_listbox = tk.Listbox(frame, height=2)  # reduced height
        self.data_listbox.pack(fill="x", padx=5, pady=3)

        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill="x", padx=5, pady=3)

        tk.Button(btn_frame, text="Add File(s)", command=self.add_data_files).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Add Folder", command=self.add_data_folder).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Remove Selected", command=self.remove_data).pack(side="left", padx=2)

        self.icon_data_label = tk.Label(frame, text="", fg="blue", font=("Arial", 8, "italic"))
        self.icon_data_label.pack(anchor="w", padx=5)

    def command_frame(self, parent):
        frame = tk.LabelFrame(parent, text="Generated Command (preview)", padx=8, pady=8)
        frame.pack(fill="x", padx=10, pady=3)

        self.cmd_text = tk.Text(frame, height=2, state="disabled", wrap="word")  # reduced height
        self.cmd_text.pack(fill="x", padx=5, pady=3)

    def progress_frame(self, parent):
        frame = tk.Frame(parent)
        frame.pack(fill="x", padx=10, pady=3)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(frame, variable=self.progress_var, mode='indeterminate')
        self.progress_bar.pack(fill="x", padx=5, pady=3)

        self.status_label = tk.Label(frame, text="Ready", anchor="w")
        self.status_label.pack(fill="x", padx=5)

    def run_button(self, parent):
        frame = tk.Frame(parent)
        frame.pack(pady=8)

        tk.Button(frame, text="Build EXE", command=self.run_pyinstaller,
                  bg="lightgreen", font=("Arial", 12, "bold"), width=15).pack(side="left", padx=5)
        tk.Button(frame, text="Clear Log", command=self.clear_log,
                  bg="lightgray", width=10).pack(side="left", padx=5)

        self.log_text = tk.Text(parent, height=6, state="disabled", wrap="word", bg="#f0f0f0")  # reduced height
        self.log_text.pack(fill="both", padx=10, pady=5, expand=True)

    # ---------- Browse methods ----------
    def browse_script(self):
        f = filedialog.askopenfilename(
            title="Select Python Script",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
            initialdir=os.path.dirname(self.script_path.get()) or os.getcwd()
        )
        if f:
            self.script_path.set(f)

    def browse_icon(self):
        f = filedialog.askopenfilename(
            title="Select Icon (.ico)",
            filetypes=[("Icon files", "*.ico"), ("All files", "*.*")],
            initialdir=os.path.dirname(self.icon_path.get()) or os.getcwd()
        )
        if f:
            self.icon_path.set(f)
            self.add_icon_as_data()

    def browse_output(self):
        d = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir.get() or os.getcwd()
        )
        if d:
            self.output_dir.set(d)

    # ---------- Icon as data ----------
    def add_icon_as_data(self):
        icon = self.icon_path.get().strip()
        if not icon or not os.path.isfile(icon):
            return
        for src, dest in self.data_files:
            if os.path.abspath(src) == os.path.abspath(icon) and dest == ".":
                return
        self.data_files.append((icon, "."))
        self.data_listbox.insert(tk.END, f"{icon} -> .  (icon)")
        self.icon_data_label.config(text="✓ Icon is included as runtime data.")

    # ---------- Data files (manual) ----------
    def add_data_files(self):
        files = filedialog.askopenfilenames(
            title="Select files to bundle",
            initialdir=os.getcwd()
        )
        for f in files:
            dest = os.path.basename(f)
            self.data_files.append((f, dest))
            self.data_listbox.insert(tk.END, f"{f} -> {dest}")

    def add_data_folder(self):
        folder = filedialog.askdirectory(
            title="Select folder to bundle",
            initialdir=os.getcwd()
        )
        if folder:
            dest = os.path.basename(folder)
            self.data_files.append((folder, dest))
            self.data_listbox.insert(tk.END, f"{folder} -> {dest}")

    def remove_data(self):
        sel = self.data_listbox.curselection()
        if sel:
            idx = sel[0]
            item = self.data_listbox.get(idx)
            if " (icon)" in item:
                del self.data_files[idx]
                self.data_listbox.delete(idx)
                self.icon_data_label.config(text="")
                return
            del self.data_files[idx]
            self.data_listbox.delete(idx)

    # ---------- Cleanup ----------
    def cleanup_build_artifacts(self):
        """Delete build/ folder and .spec file created by PyInstaller."""
        # Determine spec file name
        name = self.name.get().strip()
        if not name:
            base = os.path.basename(self.script_path.get())
            name = os.path.splitext(base)[0]
        spec_path = os.path.join(os.getcwd(), name + ".spec")
        if os.path.exists(spec_path):
            try:
                os.remove(spec_path)
                self.log(f"Removed spec file: {spec_path}\n")
            except Exception as e:
                self.log(f"Could not remove spec file: {e}\n")

        build_dir = os.path.join(os.getcwd(), "build")
        if os.path.exists(build_dir) and os.path.isdir(build_dir):
            try:
                shutil.rmtree(build_dir)
                self.log(f"Removed build directory: {build_dir}\n")
            except Exception as e:
                self.log(f"Could not remove build directory: {e}\n")

    # ---------- Run PyInstaller ----------
    def run_pyinstaller(self):
        script = self.script_path.get().strip()
        if not script or not os.path.isfile(script):
            messagebox.showerror("Error", "Please select a valid Python script.")
            return

        # Build command
        cmd = ["pyinstaller"]

        if self.onefile.get():
            cmd.append("--onefile")
        else:
            cmd.append("--onedir")

        if self.noconsole.get():
            cmd.append("--windowed")

        if self.clean.get():
            cmd.append("--clean")

        if self.debug.get():
            cmd.append("--debug")

        # Icon handling
        icon = self.icon_path.get().strip()
        if icon:
            icon_abs = os.path.abspath(icon)
            if os.path.isfile(icon_abs):
                cmd.append(f"--icon={icon_abs}")
                self.add_icon_as_data()
            else:
                messagebox.showwarning("Icon Warning",
                    f"Icon file not found:\n{icon_abs}\n\nBuild will continue without embedding an icon.")

        # Name, output, data files
        name = self.name.get().strip()
        if name:
            cmd.append(f"--name={name}")

        out = self.output_dir.get().strip()
        if out:
            cmd.append(f"--distpath={out}")

        for src, dest in self.data_files:
            src_abs = os.path.abspath(src)
            cmd.append(f"--add-data={src_abs}{os.pathsep}{dest}")

        cmd.append(script)

        self.update_command(" ".join(cmd))

        if not messagebox.askyesno("Confirm", f"Execute:\n{' '.join(cmd)}\n\nProceed?"):
            return

        # Progress bar
        self.progress_bar.start(10)
        self.status_label.config(text="Building...")

        self.log("Starting PyInstaller ...\n")
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in process.stdout:
                self.log(line)
            process.wait()
            if process.returncode == 0:
                self.log("\n✅ Build completed successfully.\n")
                self.log("💡 The icon is embedded in the .exe and also available as a data file.\n")
                self.log("   You can now move the .exe anywhere – no extra files needed.\n")
                # Clean up temporary build artifacts
                self.log("Cleaning up build artifacts...\n")
                self.cleanup_build_artifacts()
                # Show confirmation
                exe_name = name if name else os.path.splitext(os.path.basename(script))[0] + ".exe"
                exe_path = os.path.join(out, exe_name) if out else os.path.join(os.getcwd(), exe_name)
                messagebox.showinfo("All Complete", f"Build succeeded!\n\nOutput executable:\n{exe_path}")
            else:
                self.log(f"\n❌ Build failed with return code {process.returncode}\n")
        except Exception as e:
            self.log(f"Error: {e}\n")
            messagebox.showerror("Error", f"Failed to run PyInstaller:\n{e}")
        finally:
            self.progress_bar.stop()
            self.progress_var.set(0)
            self.status_label.config(text="Ready")

    # ---------- UI helpers ----------
    def update_command(self, cmd_str):
        self.cmd_text.config(state="normal")
        self.cmd_text.delete(1.0, tk.END)
        self.cmd_text.insert(tk.END, cmd_str)
        self.cmd_text.config(state="disabled")

    def log(self, text):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        self.root.update()

    def clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = PyInstallerGUI(root)
    root.mainloop()