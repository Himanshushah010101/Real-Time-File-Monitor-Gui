# 🔐 Real Time File Integrity Checker GUI

A Python-based real-time file and folder monitoring tool with a user-friendly GUI. Detects file changes such as creation, modification, and deletion.

---

## 🚀 Features

- Real-time folder monitoring
- Detects file creations, modifications, and deletions
- SHA-256 hashing for file integrity verification
- Modern GUI interface for easy usage
- Logs all changes in a text file
- Lightweight and fast

---

## 🛠️ Tech Stack

- Python 3
- Tkinter (GUI)
- Watchdog (real-time monitoring)
- Hashlib (file integrity checking)
- Colorama (for colored console output/logging)

---

## 📦 Installation

```bash
git clone https://github.com/your-username/file-integrity-checker-gui.git
cd file-integrity-checker-gui
pip install -r requirements.txt

📦 Requirements.txt

watchdog==4.0.0
colorama==0.4.6
tk==0.1.0       # If using Tkinter (built-in usually, but good to mention)
pyinstaller==5.10.1  # Optional: if users want executable

⚠️ Disclaimer

This tool is for educational and defensive cybersecurity purposes only. Do not use it for unauthorized monitoring or malicious activities.
