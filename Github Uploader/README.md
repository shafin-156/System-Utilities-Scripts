# GitHub Batch Uploader GUI

A modern, multi-tabbed Python GUI application designed to batch-upload files and entire folder structures to GitHub repositories using Personal Access Tokens. Features automatic folder creation, real-time logging, and a sleek dark-themed interface.

![App Screenshot](https://via.placeholder.com/800x400?text=GitHub+Uploader+GUI+Preview) *(Replace with actual screenshot)*

---

## 🚀 Features
- **Batch & Recursive Uploads**: Upload an entire local folder with all its subfolders and files in one click.
- **Smart Path Detection**: When you browse for a local folder, the app automatically extracts the folder name and pre-fills it as the `Target Remote Dir`. You can still edit it manually.
- **Folder Creation**: Automatically preserves your local folder structure on GitHub (Note: GitHub requires at least one file in a folder to create it).
- **Tabbed Interface**: Easy-to-use tabs for **Settings**, **Multi-Uploader**, **Activity Logs**, and **User Guide**.
- **Robust Authentication**: Uses GitHub Personal Access Tokens (Classic) with a `Save & Verify` feature to test your connection before uploading.
- **Real-time Logging**: View a live, timestamped log of your upload process in the Activity Logs tab.
- **Modern Dark Theme**: Styled with a high-contrast dark theme (VSCode-style) for a professional look.
- **One-Click EXE Compilation**: Fully tested to compile into a single portable `.exe` file using PyInstaller.

---

## 📋 Prerequisites
Before running the application, make sure you have the following installed:

1. **Python 3.7+** 
   *Download from [python.org](https://www.python.org/downloads/)*. (Ensure you check **"Add Python to PATH"** during installation).
2. **Git Bash / PortableGit**
   *Download Git for Windows: [https://git-scm.com/install/windows](https://git-scm.com/install/windows)* (Standard installer includes Git Bash). 
   *Alternatively, use Portable Git if you prefer a standalone folder (like in your setup).
3. **Python `requests` Library**
   Open your Git Bash terminal and run:
   ```bash
   pip install requests
