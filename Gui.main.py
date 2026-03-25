import os
import hashlib
import json
import threading
import difflib
import tkinter as tk
from tkinter import filedialog, scrolledtext
from colorama import Fore, init
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

init(autoreset=True)

BASELINE_FILE = "baseline.json"
CONTENT_DIR = "baseline_content"

# ------------------- Helper Functions -------------------

def calculate_hash(file_path):
    hasher = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                hasher.update(chunk)
        return hasher.hexdigest()
    except:
        return None

def save_file_content(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.readlines()
        os.makedirs(CONTENT_DIR, exist_ok=True)
        file_name = path.replace("\\", "_").replace(":", "")
        with open(f"{CONTENT_DIR}/{file_name}.txt", "w", encoding="utf-8") as f:
            f.writelines(content)
    except:
        pass

def load_old_content(path):
    file_name = path.replace("\\", "_").replace(":", "")
    try:
        with open(f"{CONTENT_DIR}/{file_name}.txt", "r", encoding="utf-8") as f:
            return f.readlines()
    except:
        return []

def show_diff(old, new):
    diff = difflib.unified_diff(old, new, lineterm="")
    return [line for line in diff if not line.startswith(("+++", "---"))]

def scan_directory(folder):
    file_hashes = {}
    for root, dirs, files in os.walk(folder):
        for file in files:
            path = os.path.join(root, file)
            file_hash = calculate_hash(path)
            if file_hash:
                file_hashes[path] = file_hash
                save_file_content(path)
    return file_hashes

def save_baseline(data):
    with open(BASELINE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_baseline():
    if not os.path.exists(BASELINE_FILE):
        return {}
    with open(BASELINE_FILE, "r") as f:
        return json.load(f)

# ------------------- Watchdog Handler -------------------

class IntegrityHandler(FileSystemEventHandler):
    def __init__(self, baseline, panel):
        self.baseline = baseline
        self.panel = panel

    def log(self, message, color="white"):
        self.panel.configure(state='normal')
        self.panel.insert(tk.END, message + "\n")
        self.panel.configure(state='disabled')
        self.panel.see(tk.END)

    def on_created(self, event):
        if not event.is_directory:
            self.log(f"[NEW FILE] {event.src_path}", "yellow")
            save_file_content(event.src_path)
            self.baseline[event.src_path] = calculate_hash(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.log(f"[DELETED] {event.src_path}", "blue")
            old_content = load_old_content(event.src_path)
            if old_content:
                self.log("Deleted Content:", "red")
                for line in old_content[:10]:
                    self.log(line.strip(), "red")
            if event.src_path in self.baseline:
                del self.baseline[event.src_path]

    def on_modified(self, event):
        if not event.is_directory:
            new_hash = calculate_hash(event.src_path)
            old_hash = self.baseline.get(event.src_path)
            if old_hash and new_hash != old_hash:
                self.log(f"[MODIFIED] {event.src_path}", "red")
                old_content = load_old_content(event.src_path)
                try:
                    with open(event.src_path, "r", encoding="utf-8", errors="ignore") as f:
                        new_content = f.readlines()
                except:
                    new_content = []
                diff = show_diff(old_content, new_content)
                for line in diff[:20]:
                    self.log(line, "green" if line.startswith("+") else "red")
                save_file_content(event.src_path)
                self.baseline[event.src_path] = new_hash

# ------------------- GUI -------------------

class HackerFIC:
    def __init__(self, root):
        self.root = root
        self.root.title("CYBER HIMANSHU FIC")
        self.root.geometry("900x600")
        self.root.configure(bg="black")

        # Folder selection
        self.folder_path = tk.StringVar()
        tk.Label(root, text="Folder to Monitor:", bg="black", fg="lime", font=("Consolas", 12)).pack(pady=5)
        tk.Entry(root, textvariable=self.folder_path, width=80, bg="black", fg="lime", insertbackground="lime").pack()
        tk.Button(root, text="Browse", command=self.browse_folder, bg="gray20", fg="lime").pack(pady=5)

        # Control buttons
        tk.Button(root, text="Start Monitoring", command=self.start_monitoring, bg="red", fg="white").pack(pady=5)
        tk.Button(root, text="Stop Monitoring", command=self.stop_monitoring, bg="gray20", fg="white").pack(pady=5)

        # Live panel
        self.panel = scrolledtext.ScrolledText(root, width=110, height=25, bg="black", fg="lime", font=("Consolas", 10))
        self.panel.pack(pady=10)
        self.panel.configure(state='disabled')

        self.observer = None

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def start_monitoring(self):
        folder = self.folder_path.get()
        if not os.path.exists(folder):
            self.panel.configure(state='normal')
            self.panel.insert(tk.END, "[ERROR] Invalid folder path!\n")
            self.panel.configure(state='disabled')
            return
        baseline = load_baseline()
        if not baseline:
            self.panel.configure(state='normal')
            self.panel.insert(tk.END, "[INFO] Creating baseline...\n")
            self.panel.configure(state='disabled')
            baseline = scan_directory(folder)
            save_baseline(baseline)
            self.panel.configure(state='normal')
            self.panel.insert(tk.END, "[INFO] Baseline created!\n")
            self.panel.configure(state='disabled')

        event_handler = IntegrityHandler(baseline, self.panel)
        self.observer = Observer()
        self.observer.schedule(event_handler, folder, recursive=True)
        t = threading.Thread(target=self.observer.start)
        t.daemon = True
        t.start()
        self.panel.configure(state='normal')
        self.panel.insert(tk.END, f"[INFO] Monitoring started on {folder}\n")
        self.panel.configure(state='disabled')

    def stop_monitoring(self):
        if self.observer:
            self.observer.stop()
            save_baseline(load_baseline())
            self.panel.configure(state='normal')
            self.panel.insert(tk.END, "[INFO] Monitoring stopped and baseline saved.\n")
            self.panel.configure(state='disabled')

# ------------------- RUN -------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = HackerFIC(root)
    root.mainloop()
