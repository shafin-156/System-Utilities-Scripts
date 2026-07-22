import PyInstaller.__main__
import os
import sys

# --- Configuration ---
SCRIPT_NAME = "main.py"
EXE_NAME = "BraveService"
ICON_FILE = "icon.ico"

def build_executable():
    if not os.path.exists(SCRIPT_NAME):
        print(f"[ERROR] {SCRIPT_NAME} not found in the current directory.")
        sys.exit(1)

    print(f"[INFO] Initializing build for {EXE_NAME}...")

    # Define build parameters clearly
    build_args = [
        SCRIPT_NAME,
        f'--name={EXE_NAME}',
        '--onefile',                   # Output a single .exe
        '--noconsole',                 # Hides the console window
        '--add-data=icon.ico;.',       # Bundle the icon inside the executable
        '--clean',                     # Clears PyInstaller cache
        '--log-level=WARN'             # Reduces terminal spam during build
    ]

    # Dynamically handle the system file icon application
    if os.path.exists(ICON_FILE):
        print(f"[INFO] Found {ICON_FILE}. Attaching as application icon...")
        build_args.append(f'--icon={ICON_FILE}')
    else:
        print(f"[WARNING] '{ICON_FILE}' not found in directory. Building with default system icon.")

    try:
        PyInstaller.__main__.run(build_args)
        print("\n" + "="*50)
        print(f"[SUCCESS] Build Complete! Executable is located in the 'dist' folder.")
        print("="*50)
    except Exception as e:
        print(f"\n[ERROR] Build process failed: {e}")

if __name__ == "__main__":
    build_executable()