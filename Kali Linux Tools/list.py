#!/usr/bin/env python3
import os
import subprocess
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

def banner():
    print(Fore.CYAN + Style.BRIGHT + """
========================================
        PYTHON FILE LAUNCHER
========================================
    """ + Style.RESET_ALL)

def list_py_files():
    # Get the absolute path of the directory where list.py is located
    script_dir = os.path.dirname(os.path.realpath(__file__))
    
    # List files in THAT specific directory
    files = [f for f in os.listdir(script_dir) 
             if f.endswith('.py') and f != os.path.basename(__file__)]
    return sorted(files), script_dir

def main():
    banner()
    py_files, script_dir = list_py_files()
    
    if not py_files:
        print(Fore.RED + f"No .py files found in: {script_dir}")
        return

    print(Fore.YELLOW + f"Files in {script_dir}:\n")
    for idx, file in enumerate(py_files, start=1):
        print(Fore.GREEN + f"{idx}. {file}")

    try:
        user_input = input(Fore.CYAN + "\nSelect a number to run (or 'q' to quit): " + Style.RESET_ALL)
        if user_input.lower() == 'q':
            return
            
        choice = int(user_input)
        if choice < 1 or choice > len(py_files):
            print(Fore.RED + "Invalid selection.")
            return
    except ValueError:
        print(Fore.RED + "Please enter a valid number.")
        return

    selected_file = py_files[choice - 1]
    # Join the directory path with the filename so subprocess can find it
    full_path = os.path.join(script_dir, selected_file)
    
    print(Fore.MAGENTA + f"\n[+] Running {selected_file}...\n")

    # Run the selected file using its full absolute path
    subprocess.run(["python3", full_path])

if __name__ == "__main__":
    main()
