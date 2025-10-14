import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def select_source():
    folder = 'C:\\synchronousDOCS\\'
    if folder:
        source_var.set(folder)

def select_destination():
    folder = 'C:\\synchronousDOCS\\EoL Reports\\'
    if folder:
        dest_var.set(folder)

def move_files():
    src = source_var.get()
    dst = dest_var.get()

    if not os.path.isdir(src):
        messagebox.showerror("Error", "Invalid source folder.")
        return

    if not os.path.isdir(dst):
        messagebox.showerror("Error", "Invalid destination folder.")
        return

    all_files = [f for f in os.listdir(src) if os.path.isfile(os.path.join(src, f))]

    if not all_files:
        messagebox.showinfo("Info", "No files found in the source folder.")
        return

    progress_bar['maximum'] = len(all_files)
    progress_bar['value'] = 0
    status_label.config(text="Moving files...")

    move_next_file(src, dst, all_files, 0)

def move_next_file(src, dst, files, index):
    if index >= len(files):
        status_label.config(text="All files moved successfully.")
        messagebox.showinfo("Success", f"Moved {len(files)} file(s).")
        return

    file = files[index]
    try:
        shutil.move(os.path.join(src, file), os.path.join(dst, file))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to move {file}: {e}")
        return

    progress_bar['value'] = index + 1
    root.after(100, move_next_file, src, dst, files, index + 1)

# GUI setup
root = tk.Tk()
root.title("Archiving EoL Reports...")
root.geometry("500x250")
root.resizable(False, False)

source_var = tk.StringVar()
dest_var = tk.StringVar()

tk.Label(root, text="Source Folder:").pack(pady=5)
tk.Entry(root, textvariable=source_var, width=60).pack()
tk.Button(root, text="Browse", command=select_source).pack(pady=5)

tk.Label(root, text="Destination Folder:").pack(pady=5)
tk.Entry(root, textvariable=dest_var, width=60).pack()
tk.Button(root, text="Browse", command=select_destination).pack(pady=5)

tk.Button(root, text="Execute Now", command=move_files, bg="blue", fg="white").pack(pady=10)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()