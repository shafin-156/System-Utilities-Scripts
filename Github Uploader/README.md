<p align="center">
  <img src="https://img.shields.io/badge/Python-3.7%2B-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey?style=for-the-badge&logo=windows" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

<h1 align="center">🚀 GitHub Batch Uploader GUI</h1>
<p align="center">
  A modern, multi-tabbed Python application that securely uploads entire folders and files to GitHub via the API.
</p>

<p align="center">
  <img src="assets/screenshot-GitHub-Uploader-1.png" alt="App Screenshot" width="50%"><img src="assets/screenshot-GitHub-Uploader-2.png" alt="App Screenshot" width="50%">
</p>

---

## 📚 Table of Contents
- [✨ Features](#-features)
- [📦 Prerequisites & Installation](#-prerequisites--installation)
- [🔑 Step-by-Step: How to Create a GitHub Token](#-step-by-step-how-to-create-a-github-token)
- [⚙️ Application Usage Guide](#️-application-usage-guide)
- [🧩 How to Compile to a standalone `.exe`](#-how-to-compile-to-a-standalone-exe)
- [👨‍💻 Creator](#-creator)

---

## ✨ Features
- **Batch & Recursive Uploads:** Upload an entire local directory including all subfolders and nested files in one click.
- **Smart Path Detection:** Select your local folder, and the app instantly auto-fills the remote directory name (e.g., selecting `D:/Projects/bill_calculator` auto-fills `bill_calculator` as the target folder). You can still edit it if needed.
- **Preserves Folder Structure:** The tool accurately recreates your local directory hierarchy on GitHub. *(Note: GitHub requires at least one file inside a folder to create it).*
- **Robust API Security:** Uses GitHub Personal Access Tokens (Classic) with a **"Save & Verify"** button to test your credentials before uploading.
- **Real-Time Activity Log:** A dedicated tab displays live timestamped logs (Success ✅ / Errors ❌) so you can track the process instantly.
- **Modern Dark UI:** Designed with a sleek, VSCode-inspired dark theme, complete with accent colors and an in-app "User Guide" tab.

---

## 📦 Prerequisites & Installation

Before running the uploader, please ensure you have the following installed:

1. **Git Bash / PortableGit**
   - Required to run the script and handle Git commands (if needed).
   - Download the Git Bash Portable here: [https://git-scm.com/install/windows](https://git-scm.com/install/windows)

2. **Python 3.7 or newer**
   - Make sure Python is installed and **added to your Windows PATH** during installation.
   - [Download Python](https://www.python.org/downloads/)

3. **Install the `requests` Library**
   - Open your terminal (or Command Prompt) and run:
   ```bash
   pip install requests
