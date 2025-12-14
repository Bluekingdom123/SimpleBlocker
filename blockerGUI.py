import tkinter as tk
from tkinter import messagebox, simpledialog
import psutil
import threading
import time
import ctypes
import os
import shutil

# ------------------------------------------
# settings
# ------------------------------------------
BLOCKED_APPS = {"chrome.exe"} 
DRY_RUN = True
CHECK_INTERVAL = 2  # seconds

RUNNING = False

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
BACKUP_PATH = r"C:\Windows\System32\drivers\etc\hosts.backup"

# ------------------------------------------
# admin check thing
# ------------------------------------------


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# ------------------------------------------
# monitoring thread
# ------------------------------------------


def monitor_processes():
    global RUNNING
    while RUNNING:
        for proc in psutil.process_iter(["name"]):
            name = proc.info["name"]
            if not name:
                continue

            name = name.lower()

            
            if name in BLOCKED_APPS:
                if DRY_RUN:
                    print(f"[DRY RUN] Would close: {name}")
                else:
                    try:
                        print(f"Closing: {name}")
                        proc.terminate()
                    except:
                        pass

        time.sleep(CHECK_INTERVAL)

# ------------------------------------------
# GUI functions
# ------------------------------------------


def start_monitoring():
    global RUNNING
    if RUNNING:
        messagebox.showinfo("Already Running", "Monitoring is already active.")
        return

    RUNNING = True
    thread = threading.Thread(target=monitor_processes, daemon=True)
    thread.start()
    messagebox.showinfo("Started", "Monitoring started!")


def stop_monitoring():
    global RUNNING
    RUNNING = False
    messagebox.showinfo("Stopped", "Monitoring stopped.")


def add_blocked_app():
    app = simpledialog.askstring(
        "Add Blocked App", "Enter app name (example: chrome.exe):"
    )
    if app:
        BLOCKED_APPS.add(app.lower())
        blocked_list_var.set("\n".join(BLOCKED_APPS))


def toggle_dry_run():
    global DRY_RUN
    DRY_RUN = not DRY_RUN
    mode = "ON (safe)" if DRY_RUN else "OFF (will close apps)"
    dry_run_var.set(f"Dry Run Mode: {mode}")


def restore_hosts_file():
    if not is_admin():
        messagebox.showerror(
            "Admin Required", "Run the program as Administrator first."
        )
        return

    if os.path.exists(HOSTS_PATH):
        shutil.copy(HOSTS_PATH, BACKUP_PATH)

    default_hosts = """# Default Microsoft Windows HOSTS file
127.0.0.1 localhost
::1       localhost
"""

    with open(HOSTS_PATH, "w") as f:
        f.write(default_hosts)

    messagebox.showinfo("Restored", "Hosts file restored to default.")


# ------------------------------------------
# GUI setup
# ------------------------------------------
root = tk.Tk()
root.title("Simple Focus Blocker")
root.geometry("350x420")

title_label = tk.Label(root, text="Simple App Blocker", font=("Arial", 16))
title_label.pack(pady=10)

# Dry run indicator
dry_run_var = tk.StringVar()
dry_run_var.set("Dry Run Mode: ON (safe)")

dry_run_label = tk.Label(root, textvariable=dry_run_var, fg="blue")
dry_run_label.pack()

toggle_button = tk.Button(root, text="Toggle Dry Run", command=toggle_dry_run)
toggle_button.pack(pady=5)

# this list blocks stuff
blocked_list_var = tk.StringVar()
blocked_list_var.set("\n".join(BLOCKED_APPS))

blocked_label = tk.Label(root, text="Blocked Apps:")
blocked_label.pack()

blocked_box = tk.Label(
    root, textvariable=blocked_list_var,
    relief="solid", width=30, height=8
)
blocked_box.pack(pady=5)

add_button = tk.Button(
    root, text="Add Blocked App", command=add_blocked_app
)
add_button.pack(pady=5)

# Start / Stop
start_button = tk.Button(
    root, text="Start Monitoring", command=start_monitoring, bg="#90ee90"
)
start_button.pack(pady=10)

stop_button = tk.Button(
    root, text="Stop Monitoring", command=stop_monitoring, bg="#ffcccb"
)
stop_button.pack()

# Restore hosts
restore_button = tk.Button(
    root, text="Restore Hosts File", command=restore_hosts_file
)
restore_button.pack(pady=15)

root.mainloop()
