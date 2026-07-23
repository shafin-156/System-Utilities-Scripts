"""
Lite EXE Builder - Minimal resource usage
"""

import os
import subprocess
import sys


def build_exe():
    """Build the EXE file with minimal settings"""

    # Files to check
    script_file = "play_ishti_kutum_silent.py"
    icon_file = "KMP Icon.ico"

    # Check if script exists
    if not os.path.exists(script_file):
        print(f"Error: {script_file} not found!")
        return False

    # Build command
    cmd = [
        "pyinstaller",
        "--onefile",  # Single file
        "--noconsole",  # No console window
        "--clean",  # Clean build
        "--name=PlayIshtiKutum",  # Output name
    ]

    # Add icon if exists
    if os.path.exists(icon_file):
        cmd.append(f"--icon={icon_file}")

    # Add script
    cmd.append(script_file)

    print("Building EXE... (This may take a few minutes)")

    try:
        # Run pyinstaller
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("\n✓ Build successful!")
            print(f"\nEXE created at: dist\\PlayIshtiKutum.exe")
            print("\nFeatures:")
            print("- No console window appears")
            print("- Opens Ishti Kutum video from recent list")
            print("- If not found, opens default video")
            print("- Minimal resource usage")
            return True
        else:
            print(f"\n✗ Build failed: {result.stderr}")
            return False

    except FileNotFoundError:
        print("\n✗ PyInstaller not found!")
        print("Install it with: pip install pyinstaller")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def main():
    """Main function"""
    print("=" * 50)
    print("Lite EXE Builder for Ishti Kutum Player")
    print("=" * 50)

    # Check if pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("\nPyInstaller not found.")
        print("Installing PyInstaller...")

        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller installed")
        except:
            print("✗ Failed to install PyInstaller")
            input("Press Enter to exit...")
            return

    # Build the EXE
    success = build_exe()

    if success:
        print("\n✓ Done! You can run 'PlayIshtiKutum.exe'")
    else:
        print("\n✗ Build failed")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()