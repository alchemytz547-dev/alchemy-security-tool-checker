import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import shutil
from datetime import datetime


APP_NAME = "ALCHEMY SECURITY TOOL CHECKER"


def adb_command(args):
    adb = shutil.which("adb")

    if not adb:
        return None, "ADB_NOT_FOUND"

    try:
        result = subprocess.run(
            [adb] + args,
            capture_output=True,
            text=True,
            timeout=15
        )

        return result.stdout.strip(), result.stderr.strip()

    except Exception as e:
        return None, str(e)


def run_check():
    output.delete("1.0", tk.END)

    output.insert(tk.END, f"{APP_NAME}\n")
    output.insert(tk.END, "=" * 60 + "\n\n")

    devices, error = adb_command(["devices"])

    if error == "ADB_NOT_FOUND":
        output.insert(
            tk.END,
            "ERROR: ADB haijapatikana.\n\n"
            "Install Android Platform-Tools kisha ongeza adb kwenye PATH.\n"
        )
        return

    if not devices:
        output.insert(tk.END, "Hakuna taarifa kutoka ADB.\n")
        return

    lines = devices.splitlines()
    connected = [
        line for line in lines[1:]
        if line.strip() and "device" in line
    ]

    if not connected:
        output.insert(
            tk.END,
            "Hakuna Android device iliyounganishwa.\n\n"
            "1. Unganisha simu kwa USB.\n"
            "2. Enable USB debugging.\n"
            "3. Kubali RSA prompt kwenye simu.\n"
        )
        return

    output.insert(tk.END, "DEVICE STATUS: CONNECTED\n\n")

    checks = {
        "Model": ["shell", "getprop", "ro.product.model"],
        "Manufacturer": ["shell", "getprop", "ro.product.manufacturer"],
        "Android Version": ["shell", "getprop", "ro.build.version.release"],
        "Security Patch": ["shell", "getprop", "ro.build.version.security_patch"],
        "Build": ["shell", "getprop", "ro.build.display.id"],
    }

    for name, command in checks.items():
        value, err = adb_command(command)

        if value:
            output.insert(tk.END, f"{name}: {value}\n")
        else:
            output.insert(tk.END, f"{name}: UNAVAILABLE\n")

    output.insert(tk.END, "\n" + "-" * 60 + "\n")
    output.insert(tk.END, "DEVICE ADMIN / MDM AUDIT\n\n")

    commands = [
        (
            "Device Policy Manager",
            ["shell", "dumpsys", "device_policy"]
        ),
        (
            "Device Owner",
            ["shell", "dpm", "list-owners"]
        ),
    ]

    for title, command in commands:
        value, err = adb_command(command)

        output.insert(tk.END, f"\n[{title}]\n")

        if value:
            output.insert(tk.END, value + "\n")
        else:
            output.insert(tk.END, "UNAVAILABLE / RESTRICTED\n")

    output.insert(tk.END, "\n" + "=" * 60 + "\n")
    output.insert(
        tk.END,
        "Audit completed: "
        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + "\n"
    )


def save_report():
    content = output.get("1.0", tk.END).strip()

    if not content:
        messagebox.showwarning(
            "No Report",
            "Run CHECK DEVICE kwanza."
        )
        return

    filename = filedialog.asksaveasfilename(
        title="Save Audit Report",
        defaultextension=".txt",
        filetypes=[
            ("Text file", "*.txt"),
            ("All files", ".")
        ]
    )

    if filename:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)

        messagebox.showinfo(
            "Saved",
            "Audit report imehifadhiwa."
        )


def clear_report():
    output.delete("1.0", tk.END)


# -------------------------
# GUI
# -------------------------

root = tk.Tk()
root.title(APP_NAME)
root.geometry("900x650")
root.minsize(750, 500)

style = ttk.Style()

try:
    style.theme_use("clam")
except:
    pass

header = ttk.Label(
    root,
    text=APP_NAME,
    font=("Segoe UI", 22, "bold")
)

header.pack(pady=(20, 5))

subtitle = ttk.Label(
    root,
    text="Android / MDM Security Audit & Reporting Tool",
    font=("Segoe UI", 11)
)

subtitle.pack(pady=(0, 15))

button_frame = ttk.Frame(root)
button_frame.pack(pady=5)

check_button = ttk.Button(
    button_frame,
    text="CHECK DEVICE",
    command=run_check
)

check_button.grid(row=0, column=0, padx=6)

save_button = ttk.Button(
    button_frame,
    text="SAVE REPORT",
    command=save_report
)

save_button.grid(row=0, column=1, padx=6)

clear_button = ttk.Button(
    button_frame,
    text="CLEAR",
    command=clear_report
)

clear_button.grid(row=0, column=2, padx=6)

output = tk.Text(
    root,
    wrap=tk.WORD,
    font=("Consolas", 10),
    bg="#101820",
    fg="#00ff88",
    insertbackground="white"
)

output.pack(
    fill=tk.BOTH,
    expand=True,
    padx=20,
    pady=20
)

output.insert(
    tk.END,
    "ALCHEMY SECURITY TOOL CHECKER\n\n"
    "Connect Android device via USB, then click CHECK DEVICE.\n\n"
    "This tool performs security/MDM auditing only.\n"
    "It does not disable or bypass device security.\n"
)

root.mainloop()
