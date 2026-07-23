"""
Lite KMPlayer Launcher - Opens Ishti Kutum videos silently
No console window, minimal resource usage
"""

import winreg
import os
import subprocess
import sys

def find_kmplayer():
    """Find KMPlayer executable - minimal check"""
    paths = [
        r"C:\Program Files\KMPlayer\KMPlayer64.exe",
        r"C:\Program Files (x86)\KMPlayer\KMPlayer.exe",
        r"C:\Program Files\KMPlayer\KMPlayer.exe",
    ]
    
    for path in paths:
        if os.path.exists(path):
            return path
    return None

def get_recent_file():
    """Get the most recent 'Ishti Kutum' file from the full registry list"""
    registry_keys = [
        r"SOFTWARE\KMPlayer 64X\KMPlayer 64X\Recent File List",
        r"SOFTWARE\KMPlayer\KMPlayer\Recent File List",
    ]

    for key_path in registry_keys:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)

            # Iterate through all possible entries (File1, File2, File3...)
            # Registry lists usually start at 1 and go up to 10, 20, or 100
            i = 1
            while True:
                try:
                    value_name = f"File{i}"
                    value_data, _ = winreg.QueryValueEx(key, value_name)

                    # Check if file contains "Ishti Kutum"
                    # Since we start at File1, the first match found is the most recent
                    if "Ishti Kutum".lower() in value_data.lower() and os.path.exists(value_data):
                        winreg.CloseKey(key)
                        return value_data
                    i += 1
                except OSError:
                    # Reached the end of the entries for this registry key
                    break

            winreg.CloseKey(key)
        except:
            continue

    return None

def open_file(file_path, kmplayer_path):
    """Open file with KMPlayer - silent execution"""
    try:
        # Use CREATE_NO_WINDOW flag to hide console window
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        subprocess.Popen(
            [kmplayer_path, file_path],
            startupinfo=startupinfo,
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except:
        # If that fails, try simple method
        try:
            os.startfile(file_path)
            return True
        except:
            return False

def main():
    """Main function - completely silent"""
    # Find KMPlayer
    kmplayer = find_kmplayer()

    # Try to find recent Ishti Kutum file (now checks full list)
    recent_file = get_recent_file()

    # If not found in registry, use default file
    if not recent_file:
        recent_file = r"D:\Disk E\Ishti Kutum S1\Ishti Kutum - S01 E01.ts"

    # Open the file
    if os.path.exists(recent_file):
        if kmplayer:
            open_file(recent_file, kmplayer)
        else:
            # KMPlayer not found, try to open with default system player
            try:
                os.startfile(recent_file)
            except:
                pass
    else:
        # If default file doesn't exist, do nothing
        pass

if __name__ == "__main__":
    # Run silently - no console window
    main()
    sys.exit(0)