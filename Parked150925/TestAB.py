from tkinter import *
from fpdf import FPDF
from PIL import Image, ImageTk
from tkinter import filedialog


# import tkinter as tk
# from tkinter import simpledialog
#
# def show_name_dialog():
#     name = simpledialog.askstring("Input", "Enter Layer Number:")
#     if name:
#         name_label.config(text=f"Hello, {name}!")
#
# parent = tk.Tk()
# parent.title("Input Dialog Example")
#
# get_name_button = tk.Button(parent, text="Get Name", command=show_name_dialog)
# get_name_button.pack(padx=20, pady=20)
#
# name_label = tk.Label(parent, text="", padx=20, pady=10)
# name_label.pack()
#
# parent.mainloop()
# --------------------------------

import tkinter as tk
from tkinter import ttk
from threading import Thread
from urllib.request import urlretrieve, urlcleanup


def connectSQLquery():
    url = "http://www.cnn.com"
    urlretrieve(url, "[dbo].[GEN_20250728]", eolProgressBar)
    urlcleanup()


def processEOL_button():
    # Download the file in a new thread.
    Thread(target=connectSQLquery).start()


def eolProgressBar(count, data_size, total_data):
    """
    This function is called by urlretrieve() every time
    a chunk of data is downloaded.
    """
    if count == 0:
        # Set the maximum value for the progress bar.
        progressbar.configure(maximum=total_data)
    else:
        # Increase the progress.
        progressbar.step(data_size)


# root = tk.Tk()
#
# root.title("Process EoL Summary")
# progressbar = ttk.Progressbar()
#
# progressbar.place(x=30, y=60, width=200)
# download_button = ttk.Button(text="Start EoL", command=processEOL_button)
# download_button.place(x=30, y=20)
#
# root.geometry("300x200")
#
# root.mainloop()
# --------------------------------------------------------------[]
# from threading import *
# import queue
# import time
# import tkinter as tk
# from tkinter import ttk
# import threading
# import queue
# import time
#
#
# class App(tk.Tk):
#
#     def __init__(self):
#         tk.Tk.__init__(self)
#         self.queue = queue.Queue()
#         self.listbox = tk.Listbox(self, width=20, height=5)
#         self.progressbar = ttk.Progressbar(self, orient='horizontal',
#                                            length=300, mode='determinate')
#         self.button = tk.Button(self, text="Start", command=self.spawnthread)
#         self.listbox.pack(padx=10, pady=10)
#         self.progressbar.pack(padx=10, pady=10)
#         self.button.pack(padx=10, pady=10)
#
#     def spawnthread(self):
#         self.button.config(state="disabled")
#         self.thread = ThreadedClient(self.queue)
#         self.thread.start()
#         self.periodiccall()
#
#     def periodiccall(self):
#         self.checkqueue()
#         if self.thread.is_alive():
#             self.after(100, self.periodiccall)
#         else:
#             self.button.config(state="active")
#
#     def checkqueue(self):
#         while self.queue.qsize():
#             try:
#                 msg = self.queue.get(0)
#                 self.listbox.insert('end', msg)
#                 self.progressbar.step(25)
#             except queue.Empty:
#                 pass
#
#
# class ThreadedClient(threading.Thread):
#
#     def __init__(self, queue):
#         threading.Thread.__init__(self)
#         self.queue = queue
#
#     def run(self):
#         for x in range(1, 5):
#             time.sleep(2)
#             msg = "Function %s finished..." % x
#             self.queue.put(msg)
#
#
# if __name__ == "__main__":
#     app = App()
#     app.mainloop()

# ------------------------------------------------------------

# import multiprocessing
# import tkinter as tk
#
#
# def make_window(index):
#     """Function to create a simple Tkinter window"""
#     root = tk.Tk()
#     root.title(f"Window {index + 1}")
#     root.geometry("300x150")
#
#     label = tk.Label(root, text=f"This is window {index + 1}", font=("Arial", 14))
#     label.pack(pady=30)
#
#     btn = tk.Button(root, text="Close", command=root.destroy)
#     btn.pack()
#
#     root.mainloop()
#
#
# if __name__ == "__main__":
#     processes = []
#     for i in range(5):  # Spawn 5 windows
#         p = multiprocessing.Process(target=make_window, args=(i,))
#         processes.append(p)
#         p.start()
#
#     for p in processes:
#         p.join()
# -----------------------------------------------------------------------
# import tkinter as tk
# from tkinter import ttk
# import threading
# import time
#
#
# class CounterTab:
#     def __init__(self, notebook, index):
#         self.frame = ttk.Frame(notebook)
#         notebook.add(self.frame, text=f"Tab {index+1}")
#
#         self.label = tk.Label(self.frame, text=f"Counter {index+1}: 0", font=("Arial", 14))
#         self.label.pack(pady=20)
#
#         self.running = False
#         self.counter = 0
#
#         self.start_btn = tk.Button(self.frame, text="Start", command=self.start)
#         self.start_btn.pack(side="left", padx=10, pady=10)
#
#         self.stop_btn = tk.Button(self.frame, text="Stop", command=self.stop)
#         self.stop_btn.pack(side="left", padx=10, pady=10)
#
#     def start(self):
#         if not self.running:
#             self.running = True
#             threading.Thread(target=self.run_counter, daemon=True).start()
#
#     def stop(self):
#         self.running = False
#
#     def run_counter(self):
#         while self.running:
#             self.counter += 1
#             # update GUI safely with after()
#             self.label.after(0, lambda: self.label.config(text=f"Counter: {self.counter}"))
#             time.sleep(1)
#
#
# def main():
#     root = tk.Tk()
#     root.title("Parallel Tabs GUI")
#     root.geometry("400x300")
#
#     notebook = ttk.Notebook(root)
#     notebook.pack(fill="both", expand=True)
#
#     # Create 5 tabs with counters
#     tabs = [CounterTab(notebook, i) for i in range(5)]
#
#     root.mainloop()
#
#
# if __name__ == "__main__":
#     main()

# --------------------------------------------------------
# import tkinter as tk
# from tkinter import ttk
# import threading
# import time
# import random
#
#
# class TaskTab:
#     def __init__(self, notebook, index, task_fn, task_name):
#         self.frame = ttk.Frame(notebook)
#         notebook.add(self.frame, text=f"Tab {index+1}")
#
#         self.label = tk.Label(self.frame, text=f"{task_name} not started", font=("Arial", 12))
#         self.label.pack(pady=20)
#
#         self.running = False
#         self.task_fn = task_fn
#         self.task_name = task_name
#
#         self.start_btn = tk.Button(self.frame, text="Start", command=self.start)
#         self.start_btn.pack(side="left", padx=10, pady=10)
#
#         self.stop_btn = tk.Button(self.frame, text="Stop", command=self.stop)
#         self.stop_btn.pack(side="left", padx=10, pady=10)
#
#     def start(self):
#         if not self.running:
#             self.running = True
#             threading.Thread(target=self.task_fn, args=(self,), daemon=True).start()
#
#     def stop(self):
#         self.running = False
#
#
# # Example background tasks for each tab
# def counter_task(tab):
#     count = 0
#     while tab.running:
#         count += 1
#         tab.label.after(0, lambda c=count: tab.label.config(text=f"Counter running: {c}"))
#         time.sleep(1)
#
#
# def random_number_task(tab):
#     while tab.running:
#         num = random.randint(1, 100)
#         tab.label.after(0, lambda n=num: tab.label.config(text=f"Random number: {n}"))
#         time.sleep(2)
#
#
# def clock_task(tab):
#     while tab.running:
#         now = time.strftime("%H:%M:%S")
#         tab.label.after(0, lambda t=now: tab.label.config(text=f"Clock: {t}"))
#         time.sleep(1)
#
#
# def dots_task(tab):
#     dots = ""
#     while tab.running:
#         dots += "."
#         if len(dots) > 10:
#             dots = ""
#         tab.label.after(0, lambda d=dots: tab.label.config(text=f"Loading{d}"))
#         time.sleep(0.5)
#
#
# def message_task(tab):
#     messages = ["Hello", "Welcome", "Tkinter is fun!", "Parallel tabs!", "Running smoothly"]
#     i = 0
#     while tab.running:
#         msg = messages[i % len(messages)]
#         tab.label.after(0, lambda m=msg: tab.label.config(text=f"Message: {m}"))
#         i += 1
#         time.sleep(3)
#
#
# def main():
#     root = tk.Tk()
#     root.title("Parallel Tabs GUI with Multiple Tasks")
#     root.geometry("400x300")
#
#     notebook = ttk.Notebook(root)
#     notebook.pack(fill="both", expand=True)
#
#     # Define different tasks for each tab
#     tasks = [
#         (counter_task, "Counter"),
#         (random_number_task, "Random Generator"),
#         (clock_task, "Clock"),
#         (dots_task, "Loading Dots"),
#         (message_task, "Messages"),
#     ]
#
#     # Create tabs
#     tabs = [TaskTab(notebook, i, task_fn, task_name) for i, (task_fn, task_name) in enumerate(tasks)]
#
#     root.mainloop()
#
#
# if __name__ == "__main__":
#     main()
# -------------------------------------------------------------------

import tkinter as tk
from tkinter import ttk
import threading
import time


class TaskTab:
    def __init__(self, notebook, index, task_fn, task_name="Task"):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text=f"Tab {index+1}")

        self.label = tk.Label(self.frame, text=f"{task_name} not started", font=("Arial", 12))
        self.label.pack(pady=20)

        self.running = False
        self.task_fn = task_fn
        self.task_name = task_name

        self.start_btn = tk.Button(self.frame, text="Start", command=self.start)
        self.start_btn.pack(side="left", padx=10, pady=10)

        self.stop_btn = tk.Button(self.frame, text="Stop", command=self.stop)
        self.stop_btn.pack(side="left", padx=10, pady=10)

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.task_fn, args=(self,), daemon=True).start()

    def stop(self):
        self.running = False


# --- Example Custom Tasks ---
def counter_task(tab):
    """Counts upward every second"""
    count = 0
    while tab.running:
        count += 1
        tab.label.after(0, lambda c=count: tab.label.config(text=f"Counter: {c}"))
        time.sleep(1)


def fibonacci_task(tab):
    """Generates Fibonacci numbers"""
    a, b = 0, 1
    while tab.running:
        tab.label.after(0, lambda n=a: tab.label.config(text=f"Fibonacci: {n}"))
        a, b = b, a + b
        time.sleep(1.5)


def text_cycle_task(tab):
    """Cycles through some custom messages"""
    messages = ["Hello!", "Custom tasks", "Run in parallel", "Tkinter Tabs!", "🚀"]
    i = 0
    while tab.running:
        msg = messages[i % len(messages)]
        tab.label.after(0, lambda m=msg: tab.label.config(text=f"Message: {m}"))
        i += 1
        time.sleep(2)


def clock_task(tab):
    """Shows live clock"""
    while tab.running:
        now = time.strftime("%H:%M:%S")
        tab.label.after(0, lambda t=now: tab.label.config(text=f"Clock: {t}"))
        time.sleep(1)


def loading_task(tab):
    """Loading dots animation"""
    dots = ""
    while tab.running:
        dots += "."
        if len(dots) > 10:
            dots = ""
        tab.label.after(0, lambda d=dots: tab.label.config(text=f"Loading{d}"))
        time.sleep(0.5)

def my_custom_task(tab):
    while tab.running:
        # Do some work...
        result = "Hello World"
        # Update the tab safely:
        tab.label.after(0, lambda r=result: tab.label.config(text=f"My Task: {r}"))
        time.sleep(1)

# --- Main Application ---
def main():
    root = tk.Tk()
    root.title("Parallel Tabs GUI (Custom Tasks)")
    root.geometry("450x300")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # Define your tasks here 👇 (You can plug in any function(tab) you like)
    tasks = [
        (counter_task, "Counter"),
        (fibonacci_task, "Fibonacci"),
        (text_cycle_task, "Messages"),
        (clock_task, "Clock"),
        (loading_task, "Loading Animation"),
        (my_custom_task, "Custom Task")
    ]

    # Create tabs for each task
    tabs = [TaskTab(notebook, i, task_fn, task_name) for i, (task_fn, task_name) in enumerate(tasks)]

    root.mainloop()


# if __name__ == "__main__":
#     main()

# --- detachable tabs (sometimes called tab tearing) --
import tkinter as tk
from tkinter import ttk
import threading
import time


class DetachableTab:
    def __init__(self, notebook, index, task_fn, task_name="Task"):
        self.notebook = notebook
        self.index = index
        self.task_fn = task_fn
        self.task_name = task_name

        # Create main frame for the tab
        self.frame = ttk.Frame(notebook)
        self.notebook.add(self.frame, text=f"{task_name}")

        # Label to show task info
        self.label = tk.Label(self.frame, text=f"{task_name} not started", font=("Arial", 12))
        self.label.pack(pady=20)

        # Start/Stop buttons
        self.running = False
        self.start_btn = tk.Button(self.frame, text="Start", command=self.start)
        self.start_btn.pack(side="left", padx=10, pady=10)
        self.stop_btn = tk.Button(self.frame, text="Stop", command=self.stop)
        self.stop_btn.pack(side="left", padx=10, pady=10)

        # Detach/Attach buttons
        self.detach_btn = tk.Button(self.frame, text="Detach", command=self.detach)
        self.detach_btn.pack(side="left", padx=10, pady=10)
        self.window = None  # external window reference

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.task_fn, args=(self,), daemon=True).start()

    def stop(self):
        self.running = False

    def detach(self):
        """Remove tab from notebook and put into a Toplevel window"""
        if self.window is not None:  # already detached
            return

        # Remove from notebook
        self.notebook.forget(self.frame)

        # Create new Toplevel window
        self.window = tk.Toplevel()
        self.window.title(self.task_name)

        # Repack the frame inside the window
        self.frame.pack(fill="both", expand=True)

        # Add "Reattach" button inside window
        reattach_btn = tk.Button(self.window, text="Reattach", command=self.attach)
        reattach_btn.pack(side="bottom", pady=5)

        # Handle close window -> reattach
        self.window.protocol("WM_DELETE_WINDOW", self.attach)

    def attach(self):
        """Put tab back into the notebook"""
        if self.window is None:
            return

        # Remove frame from window
        self.frame.pack_forget()

        # Add frame back to notebook
        self.notebook.add(self.frame, text=self.task_name)

        # Destroy the detached window
        self.window.destroy()
        self.window = None


# --- Example tasks ---
def counter_task(tab):
    count = 0
    while tab.running:
        count += 1
        tab.label.after(0, lambda c=count: tab.label.config(text=f"{tab.task_name}: {c}"))
        time.sleep(1)


def clock_task(tab):
    while tab.running:
        now = time.strftime("%H:%M:%S")
        tab.label.after(0, lambda t=now: tab.label.config(text=f"{tab.task_name}: {t}"))
        time.sleep(1)


def dots_task(tab):
    dots = ""
    while tab.running:
        dots += "."
        if len(dots) > 10:
            dots = ""
        tab.label.after(0, lambda d=dots: tab.label.config(text=f"{tab.task_name}: Loading{d}"))
        time.sleep(0.5)


def main():
    root = tk.Tk()
    root.title("Detachable Tabs with Parallel Tasks")
    root.geometry("500x300")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # Define tasks
    tasks = [
        (counter_task, "Counter"),
        (clock_task, "Clock"),
        (dots_task, "Loading"),
    ]

    tabs = [DetachableTab(notebook, i, fn, name) for i, (fn, name) in enumerate(tasks)]

    root.mainloop()

#
# if __name__ == "__main__":
#     main()

# -----------------------------------------------------------------
import tkinter as tk
from tkinter import ttk
import threading
import time


class DetachableNotebook(ttk.Notebook):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<ButtonPress-1>", self.on_tab_press, True)
        self.bind("<B1-Motion>", self.on_tab_motion, True)
        self.bind("<ButtonRelease-1>", self.on_tab_release, True)

        self._drag_data = {"tab_index": None, "start_x": 0, "start_y": 0, "detached": False}

    def on_tab_press(self, event):
        element = self.identify(event.x, event.y)
        if "label" in element:  # clicked on a tab label
            self._drag_data["tab_index"] = self.index(f"@{event.x},{event.y}")
            self._drag_data["start_x"] = event.x_root
            self._drag_data["start_y"] = event.y_root
            self._drag_data["detached"] = False

    def on_tab_motion(self, event):
        if self._drag_data["tab_index"] is None:
            return

        dx = event.x_root - self._drag_data["start_x"]
        dy = event.y_root - self._drag_data["start_y"]

        # --- Tab reordering (horizontal drag inside notebook) ---
        if abs(dx) > 20 and abs(dy) < 30 and not self._drag_data["detached"]:
            tab_index = self._drag_data["tab_index"]
            new_index = tab_index + (1 if dx > 0 else -1)

            if 0 <= new_index < len(self.tabs()):
                self.insert(new_index, self.tabs()[tab_index])
                self._drag_data["tab_index"] = new_index
                self._drag_data["start_x"] = event.x_root

        # --- Tab detachment (drag outside notebook) ---
        if (abs(dx) > 40 or abs(dy) > 40) and not self._drag_data["detached"]:
            idx = self._drag_data["tab_index"]
            self.detach_tab(idx)
            self._drag_data["detached"] = True

    def on_tab_release(self, event):
        self._drag_data = {"tab_index": None, "start_x": 0, "start_y": 0, "detached": False}

    def detach_tab(self, index):
        """Detach tab into a new Toplevel window"""
        tab_text = self.tab(index, "text")
        frame = self.nametowidget(self.tabs()[index])

        # Remove from notebook
        self.forget(index)

        # Create floating window
        win = tk.Toplevel(self)
        win.title(tab_text)
        frame.pack(fill="both", expand=True)
        frame.master = win

        # Handle close -> reattach
        def on_close():
            frame.pack_forget()
            self.add(frame, text=tab_text)
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)


# --- Parallel task tabs ---
class TaskTab:
    def __init__(self, notebook, task_fn, task_name="Task"):
        self.notebook = notebook
        self.task_fn = task_fn
        self.task_name = task_name

        # Frame for the tab
        self.frame = ttk.Frame(notebook)
        self.notebook.add(self.frame, text=task_name)

        # Label for output
        self.label = tk.Label(self.frame, text=f"{task_name} not started", font=("Arial", 12))
        self.label.pack(pady=20)

        self.running = False
        self.start_btn = tk.Button(self.frame, text="Start", command=self.start)
        self.start_btn.pack(side="left", padx=10, pady=10)
        self.stop_btn = tk.Button(self.frame, text="Stop", command=self.stop)
        self.stop_btn.pack(side="left", padx=10, pady=10)

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.task_fn, args=(self,), daemon=True).start()

    def stop(self):
        self.running = False


# --- Example tasks ---
def counter_task(tab):
    count = 0
    while tab.running:
        count += 1
        tab.label.after(0, lambda c=count: tab.label.config(text=f"{tab.task_name}: {c}"))
        time.sleep(1)


def clock_task(tab):
    while tab.running:
        now = time.strftime("%H:%M:%S")
        tab.label.after(0, lambda t=now: tab.label.config(text=f"{tab.task_name}: {t}"))
        time.sleep(1)


def dots_task(tab):
    dots = ""
    while tab.running:
        dots += "."
        if len(dots) > 10:
            dots = ""
        tab.label.after(0, lambda d=dots: tab.label.config(text=f"{tab.task_name}: Loading{d}"))
        time.sleep(0.5)


# --- Main ---
def main():
    root = tk.Tk()
    root.title("Drag-Reorder & Detachable Tabs")
    root.geometry("600x350")

    notebook = DetachableNotebook(root)
    notebook.pack(fill="both", expand=True)

    # Create parallel task tabs
    TaskTab(notebook, counter_task, "Counter")
    TaskTab(notebook, clock_task, "Clock")
    TaskTab(notebook, dots_task, "Loading")

    root.mainloop()


# if __name__ == "__main__":
#     main()

# --------------------------------------
import tkinter as tk
from tkinter import ttk
import threading
import time
import random
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

matplotlib.use("TkAgg")


# --- Notebook with detachable + reorderable tabs ---
class DetachableNotebook(ttk.Notebook):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<ButtonPress-1>", self.on_tab_press, True)
        self.bind("<B1-Motion>", self.on_tab_motion, True)
        self.bind("<ButtonRelease-1>", self.on_tab_release, True)

        self._drag_data = {"tab_index": None, "start_x": 0, "start_y": 0, "detached": False}

    def on_tab_press(self, event):
        element = self.identify(event.x, event.y)
        if "label" in element:
            self._drag_data["tab_index"] = self.index(f"@{event.x},{event.y}")
            self._drag_data["start_x"] = event.x_root
            self._drag_data["start_y"] = event.y_root
            self._drag_data["detached"] = False

    def on_tab_motion(self, event):
        if self._drag_data["tab_index"] is None:
            return

        dx = event.x_root - self._drag_data["start_x"]
        dy = event.y_root - self._drag_data["start_y"]

        # Reordering tabs
        if abs(dx) > 20 and abs(dy) < 30 and not self._drag_data["detached"]:
            tab_index = self._drag_data["tab_index"]
            new_index = tab_index + (1 if dx > 0 else -1)
            if 0 <= new_index < len(self.tabs()):
                self.insert(new_index, self.tabs()[tab_index])
                self._drag_data["tab_index"] = new_index
                self._drag_data["start_x"] = event.x_root

        # Detachment
        if (abs(dx) > 40 or abs(dy) > 40) and not self._drag_data["detached"]:
            idx = self._drag_data["tab_index"]
            self.detach_tab(idx)
            self._drag_data["detached"] = True

    def on_tab_release(self, event):
        self._drag_data = {"tab_index": None, "start_x": 0, "start_y": 0, "detached": False}

    def detach_tab(self, index):
        tab_text = self.tab(index, "text")
        frame = self.nametowidget(self.tabs()[index])
        self.forget(index)

        win = tk.Toplevel(self)
        win.title(tab_text)
        frame.pack(fill="both", expand=True)
        frame.master = win

        def on_close():
            frame.pack_forget()
            self.add(frame, text=tab_text)
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)


# --- TaskTab with rolling plot ---
class PlotTab:
    def __init__(self, notebook, task_name="Task", max_points=50):
        self.notebook = notebook
        self.task_name = task_name
        self.max_points = max_points
        self.running = False

        # Tab frame
        self.frame = ttk.Frame(notebook)
        self.notebook.add(self.frame, text=task_name)

        # Start/Stop buttons
        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(fill="x")
        tk.Button(btn_frame, text="Start", command=self.start).pack(side="left", padx=5, pady=5)
        tk.Button(btn_frame, text="Stop", command=self.stop).pack(side="left", padx=5, pady=5)

        # Matplotlib figure
        self.fig = Figure(figsize=(4, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(f"{task_name} - Rolling Data")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, 100)
        self.line, = self.ax.plot([], [], lw=2)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.data = []

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.generate_data, daemon=True).start()

    def stop(self):
        self.running = False

    def generate_data(self):
        while self.running:
            # Generate new random data point
            new_value = random.randint(0, 100)
            self.data.append(new_value)
            if len(self.data) > self.max_points:
                self.data.pop(0)

            # Update plot safely
            self.ax.clear()
            self.ax.set_title(f"{self.task_name} - Rolling Data")
            self.ax.set_xlim(0, self.max_points)
            self.ax.set_ylim(0, 100)
            self.ax.plot(range(len(self.data)), self.data, lw=2)

            self.canvas.draw_idle()
            time.sleep(0.5)


# --- Main ---
def main():
    root = tk.Tk()
    root.title("Detachable + Rolling Plots in Tabs")
    root.geometry("700x500")

    notebook = DetachableNotebook(root)
    notebook.pack(fill="both", expand=True)

    # Create tabs with rolling plots
    PlotTab(notebook, "Sensor A")
    PlotTab(notebook, "Sensor B")
    PlotTab(notebook, "Sensor C")
    PlotTab(notebook, "Sensor D")
    PlotTab(notebook, "Sensor E")

    root.mainloop()


# if __name__ == "__main__":
#     main()
# --------------------------------------------------------------------------
import tkinter as tk
from tkinter import ttk
import threading
import time
import random
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

matplotlib.use("TkAgg")


# --- Notebook with detachable + reorderable tabs ---
class DetachableNotebook(ttk.Notebook):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<ButtonPress-1>", self.on_tab_press, True)
        self.bind("<B1-Motion>", self.on_tab_motion, True)
        self.bind("<ButtonRelease-1>", self.on_tab_release, True)

        self._drag_data = {"tab_index": None, "start_x": 0, "start_y": 0, "detached": False}

    def on_tab_press(self, event):
        element = self.identify(event.x, event.y)
        if "label" in element:
            self._drag_data["tab_index"] = self.index(f"@{event.x},{event.y}")
            self._drag_data["start_x"] = event.x_root
            self._drag_data["start_y"] = event.y_root
            self._drag_data["detached"] = False

    def on_tab_motion(self, event):
        if self._drag_data["tab_index"] is None:
            return

        dx = event.x_root - self._drag_data["start_x"]
        dy = event.y_root - self._drag_data["start_y"]

        # Reordering tabs
        if abs(dx) > 20 and abs(dy) < 30 and not self._drag_data["detached"]:
            tab_index = self._drag_data["tab_index"]
            new_index = tab_index + (1 if dx > 0 else -1)
            if 0 <= new_index < len(self.tabs()):
                self.insert(new_index, self.tabs()[tab_index])
                self._drag_data["tab_index"] = new_index
                self._drag_data["start_x"] = event.x_root

        # Detachment
        if (abs(dx) > 40 or abs(dy) > 40) and not self._drag_data["detached"]:
            idx = self._drag_data["tab_index"]
            self.detach_tab(idx)
            self._drag_data["detached"] = True

    def on_tab_release(self, event):
        self._drag_data = {"tab_index": None, "start_x": 0, "start_y": 0, "detached": False}

    def detach_tab(self, index):
        tab_text = self.tab(index, "text")
        frame = self.nametowidget(self.tabs()[index])
        self.forget(index)

        win = tk.Toplevel(self)
        win.title(tab_text)
        frame.pack(fill="both", expand=True)
        frame.master = win

        def on_close():
            frame.pack_forget()
            self.add(frame, text=tab_text)
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)


# --- PlotTab with independent rolling data + alarm ---
class PlotTab:
    def __init__(self, notebook, task_name="Task", max_points=50, y_max=100):
        self.notebook = notebook
        self.task_name = task_name
        self.max_points = max_points
        self.y_max = y_max
        self.running = False

        # Frame for the tab
        self.frame = ttk.Frame(notebook)
        self.notebook.add(self.frame, text=task_name)

        # Start/Stop buttons
        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(fill="x")
        tk.Button(btn_frame, text="Start", command=self.start).pack(side="left", padx=5, pady=5)
        tk.Button(btn_frame, text="Stop", command=self.stop).pack(side="left", padx=5, pady=5)

        # Alarm label
        self.alarm_label = tk.Label(btn_frame, text="", fg="red", font=("Arial", 10, "bold"))
        self.alarm_label.pack(side="left", padx=10)

        # Matplotlib figure
        self.fig = Figure(figsize=(4, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(f"{task_name} - Rolling Data")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)
        self.line, = self.ax.plot([], [], lw=2)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.data = []

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.generate_data, daemon=True).start()

    def stop(self):
        self.running = False

    def generate_data(self):
        while self.running:
            new_value = random.randint(0, self.y_max)  # Simulated sensor value
            self.data.append(new_value)
            if len(self.data) > self.max_points:
                self.data.pop(0)

            # Clear and redraw plot
            self.ax.clear()
            self.ax.set_title(f"{self.task_name} - Rolling Data")
            self.ax.set_xlim(0, self.max_points)
            self.ax.set_ylim(0, self.y_max)
            self.ax.plot(range(len(self.data)), self.data, lw=2)

            # Alarm condition
            if new_value > 0.7 * self.y_max:
                self.ax.set_facecolor("#ffcccc")  # light red background
                self.alarm_label.config(text="⚠ High Value!")
            else:
                self.ax.set_facecolor("white")
                self.alarm_label.config(text="")

            self.canvas.draw_idle()
            time.sleep(0.5)


# --- Main ---
def main():
    root = tk.Tk()
    root.title("Independent Rolling Plots with Alarm")
    root.geometry("800x600")

    notebook = DetachableNotebook(root)
    notebook.pack(fill="both", expand=True)

    # Create 5 independent rolling-plot tabs
    PlotTab(notebook, "Sensor A")
    PlotTab(notebook, "Sensor B")
    PlotTab(notebook, "Sensor C")
    PlotTab(notebook, "Sensor D")
    PlotTab(notebook, "Sensor E")

    root.mainloop()


# if __name__ == "__main__":
#     main()
# ---------------------------------------------------------------
import tkinter as tk
from tkinter import ttk
import threading
import time
import random
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

matplotlib.use("TkAgg")


# --- Notebook with detachable + reorderable tabs ---
class DetachableNotebook(ttk.Notebook):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<ButtonPress-1>", self.on_tab_press, True)
        self.bind("<B1-Motion>", self.on_tab_motion, True)
        self.bind("<ButtonRelease-1>", self.on_tab_release, True)

        self._drag_data = {"tab_index": None, "start_x": 0, "start_y": 0, "detached": False}

        # Tab styles for alarm
        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=[10, 5])
        style.map(
            "Alarm.TNotebook.Tab",
            background=[("selected", "red"), ("!selected", "#ff9999")],
            foreground=[("selected", "white"), ("!selected", "black")],
        )

    def on_tab_press(self, event):
        element = self.identify(event.x, event.y)
        if "label" in element:
            self._drag_data["tab_index"] = self.index(f"@{event.x},{event.y}")
            self._drag_data["start_x"] = event.x_root
            self._drag_data["start_y"] = event.y_root
            self._drag_data["detached"] = False

    def on_tab_motion(self, event):
        if self._drag_data["tab_index"] is None:
            return

        dx = event.x_root - self._drag_data["start_x"]
        dy = event.y_root - self._drag_data["start_y"]

        # Reordering tabs
        if abs(dx) > 20 and abs(dy) < 30 and not self._drag_data["detached"]:
            tab_index = self._drag_data["tab_index"]
            new_index = tab_index + (1 if dx > 0 else -1)
            if 0 <= new_index < len(self.tabs()):
                self.insert(new_index, self.tabs()[tab_index])
                self._drag_data["tab_index"] = new_index
                self._drag_data["start_x"] = event.x_root

        # Detachment
        if (abs(dx) > 40 or abs(dy) > 40) and not self._drag_data["detached"]:
            idx = self._drag_data["tab_index"]
            self.detach_tab(idx)
            self._drag_data["detached"] = True

    def on_tab_release(self, event):
        self._drag_data = {"tab_index": None, "start_x": 0, "start_y": 0, "detached": False}

    def detach_tab(self, index):
        tab_text = self.tab(index, "text")
        frame = self.nametowidget(self.tabs()[index])
        self.forget(index)

        win = tk.Toplevel(self)
        win.title(tab_text)
        frame.pack(fill="both", expand=True)
        frame.master = win

        def on_close():
            frame.pack_forget()
            self.add(frame, text=tab_text)
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)


# --- PlotTab with alarm ---
class PlotTab:
    def __init__(self, notebook, task_name="Task", max_points=50, y_max=100):
        self.notebook = notebook
        self.task_name = task_name
        self.max_points = max_points
        self.y_max = y_max
        self.running = False

        # Frame for the tab
        self.frame = ttk.Frame(notebook)
        self.tab_id = notebook.add(self.frame, text=task_name)

        # Start/Stop buttons
        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(fill="x")
        tk.Button(btn_frame, text="Start", command=self.start).pack(side="left", padx=5, pady=5)
        tk.Button(btn_frame, text="Stop", command=self.stop).pack(side="left", padx=5, pady=5)

        # Alarm label
        self.alarm_label = tk.Label(btn_frame, text="", fg="red", font=("Arial", 10, "bold"))
        self.alarm_label.pack(side="left", padx=10)

        # Matplotlib figure
        self.fig = Figure(figsize=(4, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(f"{task_name} - Rolling Data")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)
        self.line, = self.ax.plot([], [], lw=2)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.data = []

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.generate_data, daemon=True).start()

    def stop(self):
        self.running = False

    def generate_data(self):
        while self.running:
            new_value = random.randint(0, self.y_max)  # Simulated sensor value
            self.data.append(new_value)
            if len(self.data) > self.max_points:
                self.data.pop(0)

            # Clear and redraw plot
            self.ax.clear()
            self.ax.set_title(f"{self.task_name} - Rolling Data")
            self.ax.set_xlim(0, self.max_points)
            self.ax.set_ylim(0, self.y_max)
            self.ax.plot(range(len(self.data)), self.data, lw=2)

            # Alarm condition
            if new_value > 0.7 * self.y_max:
                self.ax.set_facecolor("#ffcccc")  # light red background
                self.alarm_label.config(text="⚠ High Value!")
                self.notebook.tab(self.frame, style="Alarm.TNotebook.Tab")
                self.frame.bell()  # audible alert
            else:
                self.ax.set_facecolor("white")
                self.alarm_label.config(text="")
                self.notebook.tab(self.frame, style="TNotebook.Tab")

            self.canvas.draw_idle()
            time.sleep(0.5)


# --- Main ---
def main():
    root = tk.Tk()
    root.title("Independent Rolling Plots with Alarm")
    root.geometry("800x600")

    notebook = DetachableNotebook(root)
    notebook.pack(fill="both", expand=True)

    # Create 5 independent rolling-plot tabs
    PlotTab(notebook, "Sensor A")
    PlotTab(notebook, "Sensor B")
    PlotTab(notebook, "Sensor C")
    PlotTab(notebook, "Sensor D")
    PlotTab(notebook, "Sensor E")

    root.mainloop()


# if __name__ == "__main__":
#     main()
# --------------------------------------------------------------------------------
import tkinter as tk
from tkinter import ttk
import threading
import time
import random
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

matplotlib.use("TkAgg")


# --- Notebook with detachable + reorderable tabs ---
class DetachableNotebook(ttk.Notebook):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<ButtonPress-1>", self.on_tab_press, True)
        self.bind("<B1-Motion>", self.on_tab_motion, True)
        self.bind("<ButtonRelease-1>", self.on_tab_release, True)

        self._drag_data = {"tab_index": None, "start_x": 0, "start_y": 0, "detached": False}

        # Tab styles
        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=[10, 5])
        style.map(
            "Alarm.TNotebook.Tab",
            background=[("selected", "red"), ("!selected", "#ff9999")],
            foreground=[("selected", "white"), ("!selected", "black")],
        )

    def on_tab_press(self, event):
        element = self.identify(event.x, event.y)
        if "label" in element:
            self._drag_data["tab_index"] = self.index(f"@{event.x},{event.y}")
            self._drag_data["start_x"] = event.x_root
            self._drag_data["start_y"] = event.y_root
            self._drag_data["detached"] = False

    def on_tab_motion(self, event):
        if self._drag_data["tab_index"] is None:
            return

        dx = event.x_root - self._drag_data["start_x"]
        dy = event.y_root - self._drag_data["start_y"]

        # Reordering tabs
        if abs(dx) > 20 and abs(dy) < 30 and not self._drag_data["detached"]:
            tab_index = self._drag_data["tab_index"]
            new_index = tab_index + (1 if dx > 0 else -1)
            if 0 <= new_index < len(self.tabs()):
                self.insert(new_index, self.tabs()[tab_index])
                self._drag_data["tab_index"] = new_index
                self._drag_data["start_x"] = event.x_root

        # Detachment
        if (abs(dx) > 40 or abs(dy) > 40) and not self._drag_data["detached"]:
            idx = self._drag_data["tab_index"]
            self.detach_tab(idx)
            self._drag_data["detached"] = True

    def on_tab_release(self, event):
        self._drag_data = {"tab_index": None, "start_x": 0, "start_y": 0, "detached": False}

    def detach_tab(self, index):
        tab_text = self.tab(index, "text")
        frame = self.nametowidget(self.tabs()[index])
        self.forget(index)

        win = tk.Toplevel(self)
        win.title(tab_text)
        frame.pack(fill="both", expand=True)
        frame.master = win

        def on_close():
            frame.pack_forget()
            self.add(frame, text=tab_text)
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)


# --- PlotTab with latched alarm ---
class PlotTab:
    def __init__(self, notebook, task_name="Task", max_points=50, y_max=100):
        self.notebook = notebook
        self.task_name = task_name
        self.max_points = max_points
        self.y_max = y_max
        self.running = False
        self.alarm_active = False  # latched alarm state

        # Frame for the tab
        self.frame = ttk.Frame(notebook)
        self.tab_id = notebook.add(self.frame, text=task_name)

        # Buttons
        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(fill="x")
        tk.Button(btn_frame, text="Start", command=self.start).pack(side="left", padx=5, pady=5)
        tk.Button(btn_frame, text="Stop", command=self.stop).pack(side="left", padx=5, pady=5)
        tk.Button(btn_frame, text="Reset Alarm", command=self.reset_alarm).pack(side="left", padx=5, pady=5)

        # Alarm label
        self.alarm_label = tk.Label(btn_frame, text="", fg="red", font=("Arial", 10, "bold"))
        self.alarm_label.pack(side="left", padx=10)

        # Matplotlib figure
        self.fig = Figure(figsize=(4, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(f"{task_name} - Rolling Data")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)
        self.line, = self.ax.plot([], [], lw=2)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.data = []

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.generate_data, daemon=True).start()

    def stop(self):
        self.running = False

    def reset_alarm(self):
        """Reset latched alarm state manually"""
        self.alarm_active = False
        self.alarm_label.config(text="")
        self.notebook.tab(self.frame, style="TNotebook.Tab")
        self.ax.set_facecolor("white")
        self.canvas.draw_idle()

    def generate_data(self):
        while self.running:
            new_value = random.randint(0, self.y_max)  # Simulated sensor value
            self.data.append(new_value)
            if len(self.data) > self.max_points:
                self.data.pop(0)

            # Clear and redraw plot
            self.ax.clear()
            self.ax.set_title(f"{self.task_name} - Rolling Data")
            self.ax.set_xlim(0, self.max_points)
            self.ax.set_ylim(0, self.y_max)
            self.ax.plot(range(len(self.data)), self.data, lw=2)

            # Alarm condition (latches)
            if new_value > 0.7 * self.y_max:
                self.alarm_active = True

            if self.alarm_active:
                self.ax.set_facecolor("#ffcccc")
                self.alarm_label.config(text="⚠ HIGH VALUE - ALARM!")
                self.notebook.tab(self.frame, style="Alarm.TNotebook.Tab")
                self.frame.bell()  # audible alarm
            else:
                self.ax.set_facecolor("white")

            self.canvas.draw_idle()
            time.sleep(0.5)


# --- Main ---
def main():
    root = tk.Tk()
    root.title("Independent Rolling Plots with Latched Alarm")
    root.geometry("800x600")

    notebook = DetachableNotebook(root)
    notebook.pack(fill="both", expand=True)

    # Create 5 independent rolling-plot tabs
    PlotTab(notebook, "Sensor A")
    PlotTab(notebook, "Sensor B")
    PlotTab(notebook, "Sensor C")
    PlotTab(notebook, "Sensor D")
    PlotTab(notebook, "Sensor E")

    root.mainloop()


# if __name__ == "__main__":
#     main()
# -------------------------------------------------
import tkinter as tk
from tkinter import ttk
import threading
import time
import random
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

matplotlib.use("TkAgg")


# ---------- Detachable + Reorderable Notebook ----------
class DetachableNotebook(ttk.Notebook):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<ButtonPress-1>", self._on_tab_press, True)
        self.bind("<B1-Motion>", self._on_tab_motion, True)
        self.bind("<ButtonRelease-1>", self._on_tab_release, True)
        self._drag = {"index": None, "sx": 0, "sy": 0, "detached": False}

    def _on_tab_press(self, e):
        element = self.identify(e.x, e.y)
        if "label" in element:
            self._drag["index"] = self.index(f"@{e.x},{e.y}")
            self._drag["sx"] = e.x_root
            self._drag["sy"] = e.y_root
            self._drag["detached"] = False

    def _on_tab_motion(self, e):
        if self._drag["index"] is None:
            return
        dx = e.x_root - self._drag["sx"]
        dy = e.y_root - self._drag["sy"]

        # Reorder (horizontal move inside)
        if abs(dx) > 20 and abs(dy) < 30 and not self._drag["detached"]:
            i = self._drag["index"]
            j = i + (1 if dx > 0 else -1)
            if 0 <= j < len(self.tabs()):
                self.insert(j, self.tabs()[i])
                self._drag["index"] = j
                self._drag["sx"] = e.x_root

        # Detach (move out far enough)
        if (abs(dx) > 40 or abs(dy) > 40) and not self._drag["detached"]:
            self._detach_tab(self._drag["index"])
            self._drag["detached"] = True

    def _on_tab_release(self, _e):
        self._drag = {"index": None, "sx": 0, "sy": 0, "detached": False}

    def _detach_tab(self, index):
        text = self.tab(index, "text")
        frame = self.nametowidget(self.tabs()[index])
        self.forget(index)
        win = tk.Toplevel(self)
        win.title(text)
        frame.pack(fill="both", expand=True)
        frame.master = win

        def on_close():
            frame.pack_forget()
            self.add(frame, text=text)
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)


# ---------- Plot Tab with Latched Alarm + Rolling Plot ----------
class PlotTab:
    def __init__(self, notebook: DetachableNotebook, name="Sensor", max_points=50, y_max=100):
        self.nb = notebook
        self.name = name
        self.max_points = max_points
        self.y_max = y_max
        self.running = False
        self.alarm_latched = False

        # Tab frame
        self.frame = ttk.Frame(self.nb)
        # initial tab text (no badge)
        self.nb.add(self.frame, text=self.name)

        # Controls
        controls = tk.Frame(self.frame)
        controls.pack(fill="x")
        tk.Button(controls, text="Start", command=self.start).pack(side="left", padx=5, pady=5)
        tk.Button(controls, text="Stop", command=self.stop).pack(side="left", padx=5, pady=5)
        tk.Button(controls, text="Reset Alarm", command=self.reset_alarm).pack(side="left", padx=5, pady=5)
        self.alarm_lbl = tk.Label(controls, text="", fg="red", font=("Arial", 10, "bold"))
        self.alarm_lbl.pack(side="left", padx=10)

        # Matplotlib figure
        self.fig = Figure(figsize=(4, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(f"{self.name} - Rolling Data")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)
        self.line, = self.ax.plot([], [], lw=2)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.data = []

    # ----- Public controls -----
    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self._worker, daemon=True).start()

    def stop(self):
        self.running = False

    def reset_alarm(self):
        self.alarm_latched = False
        self.alarm_lbl.config(text="")
        # remove red background; clear badge
        self.ax.set_facecolor("white")
        self._set_tab_badge(False)
        self.canvas.draw_idle()

    # ----- Internal -----
    def _worker(self):
        while self.running:
            value = random.randint(0, self.y_max)  # simulate sensor reading
            self.data.append(value)
            if len(self.data) > self.max_points:
                self.data.pop(0)

            # Evaluate alarm (latching)
            if value > 0.7 * self.y_max:
                self.alarm_latched = True

            # Schedule safe GUI update
            self.frame.after(0, self._update_gui, value)
            time.sleep(0.5)

    def _update_gui(self, latest_value):
        # redraw plot
        self.ax.clear()
        self.ax.set_title(f"{self.name} - Rolling Data")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)
        self.ax.plot(range(len(self.data)), self.data, lw=2)

        if self.alarm_latched:
            self.ax.set_facecolor("#ffcccc")               # visual alarm on plot
            self.alarm_lbl.config(text="⚠ HIGH VALUE - ALARM (latched)")
            self._set_tab_badge(True)                      # show red badge on tab text
            self.frame.bell()                              # audible alarm (beeps repeatedly while latched)
        else:
            self.ax.set_facecolor("white")
            self.alarm_lbl.config(text="")
            self._set_tab_badge(False)

        self.canvas.draw_idle()

    def _set_tab_badge(self, alarming: bool):
        """Prefix tab text with a red badge when alarming (portable way)."""
        base = self.name
        current = self.nb.tab(self.frame, "text")
        want = f"🔴 {base}" if alarming else base
        if current != want:
            self.nb.tab(self.frame, text=want)


# ---------- App ----------
def main():
    root = tk.Tk()
    root.title("Independent Rolling Plots with Latched Alarm (Portable)")
    root.geometry("900x600")

    nb = DetachableNotebook(root)
    nb.pack(fill="both", expand=True)

    # Five independent tabs
    PlotTab(nb, "Sensor A")
    PlotTab(nb, "Sensor B")
    PlotTab(nb, "Sensor C")
    PlotTab(nb, "Sensor D")
    PlotTab(nb, "Sensor E")

    root.mainloop()


# if __name__ == "__main__":
#     main()
# ---------------------------------------------
# GPU auto fallback version ----
import tkinter as tk
from tkinter import ttk
import threading
import time
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Try GPU (CuPy). Fall back to CPU (NumPy) if not available.
try:
    import cupy as xp  # xp will be CuPy (GPU)
    GPU_ENABLED = True
except Exception:
    import numpy as xp  # xp will be NumPy (CPU)
    GPU_ENABLED = False

matplotlib.use("TkAgg")


# ---------- Detachable + Reorderable Notebook ----------
class DetachableNotebook(ttk.Notebook):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<ButtonPress-1>", self._on_tab_press, True)
        self.bind("<B1-Motion>", self._on_tab_motion, True)
        self.bind("<ButtonRelease-1>", self._on_tab_release, True)
        self._drag = {"index": None, "sx": 0, "sy": 0, "detached": False}

    def _on_tab_press(self, e):
        element = self.identify(e.x, e.y)
        if "label" in element:
            self._drag["index"] = self.index(f"@{e.x},{e.y}")
            self._drag["sx"] = e.x_root
            self._drag["sy"] = e.y_root
            self._drag["detached"] = False

    def _on_tab_motion(self, e):
        if self._drag["index"] is None:
            return
        dx = e.x_root - self._drag["sx"]
        dy = e.y_root - self._drag["sy"]

        # Reorder (horizontal move inside)
        if abs(dx) > 20 and abs(dy) < 30 and not self._drag["detached"]:
            i = self._drag["index"]
            j = i + (1 if dx > 0 else -1)
            if 0 <= j < len(self.tabs()):
                self.insert(j, self.tabs()[i])
                self._drag["index"] = j
                self._drag["sx"] = e.x_root

        # Detach (move out far enough)
        if (abs(dx) > 40 or abs(dy) > 40) and not self._drag["detached"]:
            self._detach_tab(self._drag["index"])
            self._drag["detached"] = True

    def _on_tab_release(self, _e):
        self._drag = {"index": None, "sx": 0, "sy": 0, "detached": False}

    def _detach_tab(self, index):
        text = self.tab(index, "text")
        frame = self.nametowidget(self.tabs()[index])
        self.forget(index)
        win = tk.Toplevel(self)
        win.title(text)
        frame.pack(fill="both", expand=True)
        frame.master = win

        def on_close():
            frame.pack_forget()
            self.add(frame, text=text)
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)


# ---------- Plot Tab with Latched Alarm + Rolling Plot (GPU-capable) ----------
class PlotTab:
    def __init__(self, notebook: DetachableNotebook, name="Sensor",
                 max_points=200, y_max=100, batch_size=64, rolling_window=25):
        """
        max_points: number of points shown in rolling plot
        batch_size: how many new samples to generate per update (amortize GPU overhead)
        rolling_window: size for rolling calculations (e.g., moving average)
        """
        self.nb = notebook
        self.name = name
        self.max_points = max_points
        self.y_max = y_max
        self.batch_size = batch_size
        self.rolling_window = rolling_window

        self.running = False
        self.alarm_latched = False

        # Tab frame
        self.frame = ttk.Frame(self.nb)
        self.nb.add(self.frame, text=self.name)

        # Controls
        controls = tk.Frame(self.frame)
        controls.pack(fill="x")
        tk.Button(controls, text="Start", command=self.start).pack(side="left", padx=5, pady=5)
        tk.Button(controls, text="Stop", command=self.stop).pack(side="left", padx=5, pady=5)
        tk.Button(controls, text="Reset Alarm", command=self.reset_alarm).pack(side="left", padx=5, pady=5)

        self.alarm_lbl = tk.Label(controls, text="", fg="red", font=("Arial", 10, "bold"))
        self.alarm_lbl.pack(side="left", padx=10)

        # GPU/CPU indicator
        engine = "GPU (CuPy)" if GPU_ENABLED else "CPU (NumPy)"
        self.engine_lbl = tk.Label(controls, text=f"Engine: {engine}", fg="gray")
        self.engine_lbl.pack(side="right", padx=10)

        # Matplotlib figure
        self.fig = Figure(figsize=(4.5, 3.2), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(f"{self.name} - Rolling Data")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)
        # Two series: raw signal and rolling mean
        (self.line_raw,) = self.ax.plot([], [], lw=1.5, label="Signal")
        (self.line_avg,) = self.ax.plot([], [], lw=2.0, linestyle="--", label=f"Mean({self.rolling_window})")
        self.ax.legend(loc="upper right")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Rolling buffers on CPU for plotting (lightweight)
        self.buf_raw = []
        self.buf_avg = []

        # Pre-allocate GPU/CPU arrays (for generation & rolling calc)
        self._rolling_kernel_ready = False
        self._prepare_rolling_kernel()

    # ----- Public controls -----
    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self._worker, daemon=True).start()

    def stop(self):
        self.running = False

    def reset_alarm(self):
        self.alarm_latched = False
        self.alarm_lbl.config(text="")
        self.ax.set_facecolor("white")
        self._set_tab_badge(False)
        self.canvas.draw_idle()

    # ----- Internal helpers -----
    def _prepare_rolling_kernel(self):
        """
        Prepare resources for rolling calculations.
        For GPU: nothing special needed; we use vectorized ops.
        """
        self._rolling_kernel_ready = True

    def _generate_batch(self, n):
        """
        Generate a batch of synthetic sensor samples on GPU if available,
        else CPU. Replace this with your real GPU compute as needed.
        """
        # Example: bounded random signal + slow drift (to exercise compute)
        # Using vectorized ops on xp (CuPy or NumPy)
        vals = (xp.random.rand(n) * self.y_max).astype(xp.float32)
        t = xp.arange(n, dtype=xp.float32)
        vals += (xp.sin(t / 10.0) + 1.0) * (0.1 * self.y_max)  # small periodic component
        # clip to [0, y_max]
        xp.clip(vals, 0, self.y_max, out=vals)
        return vals

    def _rolling_mean(self, arr, window):
        """
        Compute rolling mean on GPU if available, else CPU.
        Returns an array of same length, with NaN for first (window-1) entries.
        Implemented via cumulative sum (vectorized) for speed on both backends.
        """
        if window <= 1:
            return arr

        c = xp.cumsum(arr, dtype=xp.float64)
        c[window:] = c[window:] - c[:-window]
        out = c / window
        # shift to align with window end; pad first (window-1) as NaN
        pad = xp.full(window - 1, xp.nan, dtype=out.dtype)
        return xp.concatenate([pad, out[window - 1:]])

    def _worker(self):
        # local buffers on backend (GPU/CPU)
        backend_buf = xp.empty(0, dtype=xp.float32)
        backend_avg = xp.empty(0, dtype=xp.float32)

        while self.running:
            # 1) Generate a batch on GPU/CPU
            batch = self._generate_batch(self.batch_size)  # xp array

            # 2) Append to backend buffer and keep only max_points
            backend_buf = xp.concatenate([backend_buf, batch])
            if backend_buf.size > self.max_points:
                backend_buf = backend_buf[-self.max_points:]

            # 3) Rolling mean on backend
            backend_avg = self._rolling_mean(backend_buf, self.rolling_window)

            # 4) Decide alarm: based on the latest value
            latest = float(backend_buf[-1])
            if latest > 0.7 * self.y_max:
                self.alarm_latched = True

            # 5) Move minimal data to CPU for plotting
            if GPU_ENABLED:
                raw_cpu = backend_buf.get()
                avg_cpu = backend_avg.get()
            else:
                raw_cpu = backend_buf
                avg_cpu = backend_avg

            # 6) Schedule GUI update
            self.frame.after(0, self._update_gui, raw_cpu, avg_cpu, latest)

            # Update rate
            time.sleep(0.4)

    def _update_gui(self, raw_cpu, avg_cpu, latest_value):
        # Update CPU-side buffers for plotting
        self.buf_raw = raw_cpu.tolist()
        # Replace NaNs for display (matplotlib handles NaN, but we’ll fill for aesthetics)
        self.buf_avg = [float(x) if x == x else None for x in avg_cpu]  # NaN check: x == x is False for NaN

        # Redraw plot
        n = len(self.buf_raw)
        xs = list(range(max(0, n - self.max_points), n))  # independent timeline per tab
        # Keep x length equal to y length
        xs = list(range(len(self.buf_raw)))

        self.ax.clear()
        self.ax.set_title(f"{self.name} - Rolling Data ({'GPU' if GPU_ENABLED else 'CPU'})")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)
        self.ax.plot(xs, self.buf_raw, lw=1.5, label="Signal")
        self.ax.plot(xs, self.buf_avg, lw=2.0, linestyle="--", label=f"Mean({self.rolling_window})")
        self.ax.legend(loc="upper right")

        # Alarm visuals (latched)
        if self.alarm_latched:
            self.ax.set_facecolor("#ffcccc")
            self.alarm_lbl.config(text="⚠ HIGH VALUE - ALARM (latched)")
            self._set_tab_badge(True)
            self.frame.bell()  # keep audible while latched
        else:
            self.ax.set_facecolor("white")
            self.alarm_lbl.config(text="")
            self._set_tab_badge(False)

        self.canvas.draw_idle()

    def _set_tab_badge(self, alarming: bool):
        """Prefix tab text with a red badge when alarming (portable)."""
        base = self.name
        current = self.nb.tab(self.frame, "text")
        want = f"🔴 {base}" if alarming else base
        if current != want:
            self.nb.tab(self.frame, text=want)


# ---------- App ----------
def main():
    root = tk.Tk()
    root.title("GPU-Accelerated Rolling Plots with Latched Alarm")
    root.geometry("980x650")

    nb = DetachableNotebook(root)
    nb.pack(fill="both", expand=True)

    # Five independent GPU-capable tabs
    PlotTab(nb, "Sensor A", max_points=300, batch_size=64, rolling_window=25)
    PlotTab(nb, "Sensor B", max_points=300, batch_size=64, rolling_window=25)
    PlotTab(nb, "Sensor C", max_points=300, batch_size=64, rolling_window=25)
    PlotTab(nb, "Sensor D", max_points=300, batch_size=64, rolling_window=25)
    PlotTab(nb, "Sensor E", max_points=300, batch_size=64, rolling_window=25)

    root.mainloop()


# if __name__ == "__main__":
#     main()

# -------------------- with pytorch GPU -----------------------------
import tkinter as tk
from tkinter import ttk
import threading
import time
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Use PyTorch for GPU compute
import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
GPU_ENABLED = torch.cuda.is_available()

matplotlib.use("TkAgg")


# ---------- Detachable + Reorderable Notebook ----------
class DetachableNotebook(ttk.Notebook):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<ButtonPress-1>", self._on_tab_press, True)
        self.bind("<B1-Motion>", self._on_tab_motion, True)
        self.bind("<ButtonRelease-1>", self._on_tab_release, True)
        self._drag = {"index": None, "sx": 0, "sy": 0, "detached": False}

    def _on_tab_press(self, e):
        element = self.identify(e.x, e.y)
        if "label" in element:
            self._drag["index"] = self.index(f"@{e.x},{e.y}")
            self._drag["sx"] = e.x_root
            self._drag["sy"] = e.y_root
            self._drag["detached"] = False

    def _on_tab_motion(self, e):
        if self._drag["index"] is None:
            return
        dx = e.x_root - self._drag["sx"]
        dy = e.y_root - self._drag["sy"]

        if abs(dx) > 20 and abs(dy) < 30 and not self._drag["detached"]:
            i = self._drag["index"]
            j = i + (1 if dx > 0 else -1)
            if 0 <= j < len(self.tabs()):
                self.insert(j, self.tabs()[i])
                self._drag["index"] = j
                self._drag["sx"] = e.x_root

        if (abs(dx) > 40 or abs(dy) > 40) and not self._drag["detached"]:
            self._detach_tab(self._drag["index"])
            self._drag["detached"] = True

    def _on_tab_release(self, _e):
        self._drag = {"index": None, "sx": 0, "sy": 0, "detached": False}

    def _detach_tab(self, index):
        text = self.tab(index, "text")
        frame = self.nametowidget(self.tabs()[index])
        self.forget(index)
        win = tk.Toplevel(self)
        win.title(text)
        frame.pack(fill="both", expand=True)
        frame.master = win

        def on_close():
            frame.pack_forget()
            self.add(frame, text=text)
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)


# ---------- Plot Tab with Latched Alarm + Rolling Plot (Torch GPU-capable) ----------
class PlotTab:
    def __init__(self, notebook: DetachableNotebook, name="Sensor",
                 max_points=200, y_max=100, batch_size=64, rolling_window=25):
        self.nb = notebook
        self.name = name
        self.max_points = max_points
        self.y_max = y_max
        self.batch_size = batch_size
        self.rolling_window = rolling_window

        self.running = False
        self.alarm_latched = False

        # Tab frame
        self.frame = ttk.Frame(self.nb)
        self.nb.add(self.frame, text=self.name)

        # Controls
        controls = tk.Frame(self.frame)
        controls.pack(fill="x")
        tk.Button(controls, text="Start", command=self.start).pack(side="left", padx=5, pady=5)
        tk.Button(controls, text="Stop", command=self.stop).pack(side="left", padx=5, pady=5)
        tk.Button(controls, text="Reset Alarm", command=self.reset_alarm).pack(side="left", padx=5, pady=5)

        self.alarm_lbl = tk.Label(controls, text="", fg="red", font=("Arial", 10, "bold"))
        self.alarm_lbl.pack(side="left", padx=10)

        engine = "GPU (Torch CUDA)" if GPU_ENABLED else "CPU (Torch)"
        self.engine_lbl = tk.Label(controls, text=f"Engine: {engine}", fg="gray")
        self.engine_lbl.pack(side="right", padx=10)

        # Matplotlib figure
        self.fig = Figure(figsize=(4.5, 3.2), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(f"{self.name} - Rolling Data")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)
        (self.line_raw,) = self.ax.plot([], [], lw=1.5, label="Signal")
        (self.line_avg,) = self.ax.plot([], [], lw=2.0, linestyle="--", label=f"Mean({self.rolling_window})")
        self.ax.legend(loc="upper right")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.buf_raw = []
        self.buf_avg = []

    # ----- Public controls -----
    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self._worker, daemon=True).start()

    def stop(self):
        self.running = False

    def reset_alarm(self):
        self.alarm_latched = False
        self.alarm_lbl.config(text="")
        self.ax.set_facecolor("white")
        self._set_tab_badge(False)
        self.canvas.draw_idle()

    # ----- Internal -----
    def _generate_batch(self, n):
        # GPU/CPU tensor generation
        vals = torch.rand(n, device=DEVICE) * self.y_max
        t = torch.arange(n, device=DEVICE, dtype=torch.float32)
        vals += (torch.sin(t / 10.0) + 1.0) * (0.1 * self.y_max)
        return torch.clamp(vals, 0, self.y_max)

    def _rolling_mean(self, arr, window):
        if window <= 1:
            return arr
        cumsum = torch.cumsum(arr, dim=0)
        result = cumsum.clone()
        result[window:] = cumsum[window:] - cumsum[:-window]
        result = result / window
        pad = torch.full((window - 1,), float("nan"), device=DEVICE)
        return torch.cat([pad, result[window - 1:]])

    def _worker(self):
        buf = torch.empty(0, device=DEVICE)
        while self.running:
            batch = self._generate_batch(self.batch_size)
            buf = torch.cat([buf, batch])
            if buf.numel() > self.max_points:
                buf = buf[-self.max_points:]

            avg = self._rolling_mean(buf, self.rolling_window)

            latest = float(buf[-1].cpu())
            if latest > 0.7 * self.y_max:
                self.alarm_latched = True

            raw_cpu = buf.cpu().numpy()
            avg_cpu = avg.cpu().numpy()

            self.frame.after(0, self._update_gui, raw_cpu, avg_cpu, latest)
            time.sleep(0.4)

    def _update_gui(self, raw_cpu, avg_cpu, latest_value):
        self.buf_raw = raw_cpu.tolist()
        self.buf_avg = [float(x) if x == x else None for x in avg_cpu]

        xs = list(range(len(self.buf_raw)))
        self.ax.clear()
        self.ax.set_title(f"{self.name} - Rolling Data ({'GPU' if GPU_ENABLED else 'CPU'})")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)
        self.ax.plot(xs, self.buf_raw, lw=1.5, label="Signal")
        self.ax.plot(xs, self.buf_avg, lw=2.0, linestyle="--", label=f"Mean({self.rolling_window})")
        self.ax.legend(loc="upper right")

        if self.alarm_latched:
            self.ax.set_facecolor("#ffcccc")
            self.alarm_lbl.config(text="⚠ HIGH VALUE - ALARM (latched)")
            self._set_tab_badge(True)
            self.frame.bell()
        else:
            self.ax.set_facecolor("white")
            self.alarm_lbl.config(text="")
            self._set_tab_badge(False)

        self.canvas.draw_idle()

    def _set_tab_badge(self, alarming: bool):
        base = self.name
        current = self.nb.tab(self.frame, "text")
        want = f"🔴 {base}" if alarming else base
        if current != want:
            self.nb.tab(self.frame, text=want)


# ---------- App ----------
def main():
    root = tk.Tk()
    root.title("Torch GPU-Accelerated Rolling Plots with Latched Alarm")
    root.geometry("980x650")

    nb = DetachableNotebook(root)
    nb.pack(fill="both", expand=True)

    PlotTab(nb, "Sensor A", max_points=300, batch_size=64, rolling_window=25)
    PlotTab(nb, "Sensor B", max_points=300, batch_size=64, rolling_window=25)
    PlotTab(nb, "Sensor C", max_points=300, batch_size=64, rolling_window=25)
    PlotTab(nb, "Sensor D", max_points=300, batch_size=64, rolling_window=25)
    PlotTab(nb, "Sensor E", max_points=300, batch_size=64, rolling_window=25)

    root.mainloop()


# if __name__ == "__main__":
#     main()

# --------------- Non latchable alarms non detachable tabs ------------- GPU pytorch
import tkinter as tk
from tkinter import ttk
import threading
import time
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Torch for GPU/CPU compute
import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
GPU_ENABLED = torch.cuda.is_available()

matplotlib.use("TkAgg")


# ---------- Plot Tab with Rolling Plot + Real-Time Alarm ----------
class PlotTab:
    def __init__(self, notebook: ttk.Notebook, name="Sensor",
                 max_points=200, y_max=100, batch_size=64, rolling_window=25):
        self.nb = notebook
        self.name = name
        self.max_points = max_points
        self.y_max = y_max
        self.batch_size = batch_size
        self.rolling_window = rolling_window

        self.running = False

        # Tab frame
        self.frame = ttk.Frame(self.nb)
        self.nb.add(self.frame, text=self.name)

        # Controls
        controls = tk.Frame(self.frame)
        controls.pack(fill="x")
        tk.Button(controls, text="Start", command=self.start).pack(side="left", padx=5, pady=5)
        tk.Button(controls, text="Stop", command=self.stop).pack(side="left", padx=5, pady=5)

        self.alarm_lbl = tk.Label(controls, text="", fg="red", font=("Arial", 10, "bold"))
        self.alarm_lbl.pack(side="left", padx=10)

        engine = "GPU (Torch CUDA)" if GPU_ENABLED else "CPU (Torch)"
        self.engine_lbl = tk.Label(controls, text=f"Engine: {engine}", fg="gray")
        self.engine_lbl.pack(side="right", padx=10)

        # Matplotlib figure
        self.fig = Figure(figsize=(4.5, 3.2), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(f"{self.name} - Rolling Data")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)
        (self.line_raw,) = self.ax.plot([], [], lw=1.5, label="Signal")
        (self.line_avg,) = self.ax.plot([], [], lw=2.0, linestyle="--", label=f"Mean({self.rolling_window})")
        self.ax.legend(loc="upper right")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.buf_raw = []
        self.buf_avg = []

    # ----- Public controls -----
    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self._worker, daemon=True).start()

    def stop(self):
        self.running = False

    # ----- Internal -----
    def _generate_batch(self, n):
        vals = torch.rand(n, device=DEVICE) * self.y_max
        t = torch.arange(n, device=DEVICE, dtype=torch.float32)
        vals += (torch.sin(t / 10.0) + 1.0) * (0.1 * self.y_max)
        return torch.clamp(vals, 0, self.y_max)

    def _rolling_mean(self, arr, window):
        if window <= 1:
            return arr
        cumsum = torch.cumsum(arr, dim=0)
        result = cumsum.clone()
        result[window:] = cumsum[window:] - cumsum[:-window]
        result = result / window
        pad = torch.full((window - 1,), float("nan"), device=DEVICE)
        return torch.cat([pad, result[window - 1:]])

    def _worker(self):
        buf = torch.empty(0, device=DEVICE)
        while self.running:
            batch = self._generate_batch(self.batch_size)
            buf = torch.cat([buf, batch])
            if buf.numel() > self.max_points:
                buf = buf[-self.max_points:]

            avg = self._rolling_mean(buf, self.rolling_window)

            latest = float(buf[-1].cpu())
            raw_cpu = buf.cpu().numpy()
            avg_cpu = avg.cpu().numpy()

            self.frame.after(0, self._update_gui, raw_cpu, avg_cpu, latest)
            time.sleep(0.4)

    def _update_gui(self, raw_cpu, avg_cpu, latest_value):
        self.buf_raw = raw_cpu.tolist()
        self.buf_avg = [float(x) if x == x else None for x in avg_cpu]

        xs = list(range(len(self.buf_raw)))
        self.ax.clear()
        self.ax.set_title(f"{self.name} - Rolling Data ({'GPU' if GPU_ENABLED else 'CPU'})")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)
        self.ax.plot(xs, self.buf_raw, lw=1.5, label="Signal")
        self.ax.plot(xs, self.buf_avg, lw=2.0, linestyle="--", label=f"Mean({self.rolling_window})")
        self.ax.legend(loc="upper right")

        # Non-latching alarm (resets when value goes back below threshold)
        if latest_value > 0.7 * self.y_max:
            self.ax.set_facecolor("#ffcccc")
            self.alarm_lbl.config(text="⚠ HIGH VALUE")
            self._set_tab_badge(True)
            self.frame.bell()
        else:
            self.ax.set_facecolor("white")
            self.alarm_lbl.config(text="")
            self._set_tab_badge(False)

        self.canvas.draw_idle()

    def _set_tab_badge(self, alarming: bool):
        base = self.name
        current = self.nb.tab(self.frame, "text")
        want = f"🔴 {base}" if alarming else base
        if current != want:
            self.nb.tab(self.frame, text=want)


# ---------- App ----------
def main():
    root = tk.Tk()
    root.title("Torch GPU Rolling Plots with Real-Time Alarm")
    root.geometry("980x650")

    nb = ttk.Notebook(root)
    nb.pack(fill="both", expand=True)

    PlotTab(nb, "Sensor A", max_points=300, batch_size=64, rolling_window=25)
    PlotTab(nb, "Sensor B", max_points=300, batch_size=64, rolling_window=25)
    PlotTab(nb, "Sensor C", max_points=300, batch_size=64, rolling_window=25)
    PlotTab(nb, "Sensor D", max_points=300, batch_size=64, rolling_window=25)
    PlotTab(nb, "Sensor E", max_points=300, batch_size=64, rolling_window=25)

    root.mainloop()

#
# if __name__ == "__main__":
#     main()

# --------------------- with multiple sensors per Tab -------------
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"  # avoid OMP error
import torch
import tkinter as tk
from tkinter import ttk
import threading
import time
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# torch device (GPU if available)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
GPU_ENABLED = torch.cuda.is_available()

matplotlib.use("TkAgg")


# ---------- Plot Tab with 5 sensors ----------
class PlotTab:
    def __init__(self, notebook: ttk.Notebook, name="Sensor Group",
                 num_sensors=5, max_points=200, y_max=100, batch_size=32, rolling_window=20):
        self.nb = notebook
        self.name = name
        self.num_sensors = num_sensors
        self.max_points = max_points
        self.y_max = y_max
        self.batch_size = batch_size
        self.rolling_window = rolling_window
        self.running = False

        # Tab frame
        self.frame = ttk.Frame(self.nb)
        self.nb.add(self.frame, text=self.name)

        # Controls
        controls = tk.Frame(self.frame)
        controls.pack(fill="x")
        tk.Button(controls, text="Start", command=self.start).pack(side="left", padx=5, pady=5)
        tk.Button(controls, text="Stop", command=self.stop).pack(side="left", padx=5, pady=5)

        self.alarm_lbl = tk.Label(controls, text="", fg="red", font=("Arial", 10, "bold"))
        self.alarm_lbl.pack(side="left", padx=10)

        engine = "GPU (Torch CUDA)" if GPU_ENABLED else "CPU (Torch)"
        self.engine_lbl = tk.Label(controls, text=f"Engine: {engine}", fg="gray")
        self.engine_lbl.pack(side="right", padx=10)

        # Matplotlib figure
        self.fig = Figure(figsize=(5.5, 3.5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(f"{self.name} - Rolling Data ({'GPU' if GPU_ENABLED else 'CPU'})")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)

        # Colors and lines for sensors
        self.colors = ["blue", "green", "orange", "purple", "brown"]
        self.lines = []
        for i in range(self.num_sensors):
            (line,) = self.ax.plot([], [], lw=1.5, color=self.colors[i % len(self.colors)],
                                   label=f"Sensor {i+1}")
            self.lines.append(line)
        self.ax.legend(loc="upper right")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Buffers for data
        self.data_buffers = [torch.empty(0, device=DEVICE) for _ in range(self.num_sensors)]

    # ---------- Controls ----------
    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self._worker, daemon=True).start()

    def stop(self):
        self.running = False

    # ---------- Data Generation ----------
    def _generate_batch(self, n):
        # random + sine drift
        vals = torch.rand(self.num_sensors, n, device=DEVICE) * self.y_max
        t = torch.arange(n, device=DEVICE, dtype=torch.float32)
        vals += (torch.sin(t / 10.0) + 1.0) * (0.1 * self.y_max)
        return torch.clamp(vals, 0, self.y_max)  # shape: [num_sensors, n]

    def _rolling_mean(self, arr, window):
        if arr.numel() < window:
            return torch.full_like(arr, float("nan"))
        cumsum = torch.cumsum(arr, dim=0)
        result = cumsum.clone()
        result[window:] = cumsum[window:] - cumsum[:-window]
        result = result / window
        pad = torch.full((window - 1,), float("nan"), device=DEVICE)
        return torch.cat([pad, result[window - 1:]])

    def _worker(self):
        while self.running:
            batch = self._generate_batch(self.batch_size)  # [num_sensors, batch_size]

            for i in range(self.num_sensors):
                buf = torch.cat([self.data_buffers[i], batch[i]])
                if buf.numel() > self.max_points:
                    buf = buf[-self.max_points:]
                self.data_buffers[i] = buf

            # Push to GUI
            latest_vals = [float(buf[-1].cpu()) if buf.numel() > 0 else 0.0
                           for buf in self.data_buffers]
            buffers_cpu = [buf.cpu().numpy() for buf in self.data_buffers]

            self.frame.after(0, self._update_gui, buffers_cpu, latest_vals)
            time.sleep(0.4)

    # ---------- Update GUI ----------
    def _update_gui(self, buffers_cpu, latest_vals):
        self.ax.clear()
        self.ax.set_title(f"{self.name} - Rolling Data")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)

        alarming = False
        for i, buf in enumerate(buffers_cpu):
            xs = list(range(len(buf)))
            self.ax.plot(xs, buf, lw=1.5, color=self.colors[i % len(self.colors)], label=f"Sensor {i+1}")

            if len(buf) > 0 and buf[-1] > 0.7 * self.y_max:
                alarming = True

        self.ax.legend(loc="upper right")

        # Alarm display (non-latching)
        if alarming:
            self.ax.set_facecolor("#ffcccc")
            self.alarm_lbl.config(text="⚠ HIGH VALUE")
            self._set_tab_badge(True)
            self.frame.bell()
        else:
            self.ax.set_facecolor("white")
            self.alarm_lbl.config(text="")
            self._set_tab_badge(False)

        self.canvas.draw_idle()

    def _set_tab_badge(self, alarming: bool):
        base = self.name
        current = self.nb.tab(self.frame, "text")
        want = f"🔴 {base}" if alarming else base
        if current != want:
            self.nb.tab(self.frame, text=want)


# ---------- Main ----------
def main():
    root = tk.Tk()
    root.title("5 Sensors per Tab with Real-Time Alarm")
    root.geometry("1100x700")

    nb = ttk.Notebook(root)
    nb.pack(fill="both", expand=True)

    PlotTab(nb, "Group A")
    PlotTab(nb, "Group B")
    PlotTab(nb, "Group C")

    root.mainloop()


# if __name__ == "__main__":
#     main()

# ----------------------------------------------- with cupy ---------------------------
import tkinter as tk
from tkinter import ttk
import threading
import time
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Try GPU (CuPy), else fall back to NumPy
try:
    import cupy as xp
    GPU_ENABLED = True
except ImportError:
    import numpy as xp
    GPU_ENABLED = False
    # make numpy compatible with cupy API
    xp.asnumpy = lambda x: x

matplotlib.use("TkAgg")


class PlotTab:
    def __init__(self, notebook: ttk.Notebook, name="Sensor Group",
                 num_sensors=5, max_points=200, y_max=100, batch_size=32):
        self.nb = notebook
        self.name = name
        self.num_sensors = num_sensors
        self.max_points = max_points
        self.y_max = y_max
        self.batch_size = batch_size
        self.running = False

        # Frame for this tab
        self.frame = ttk.Frame(self.nb)
        self.nb.add(self.frame, text=self.name)

        # Controls
        controls = tk.Frame(self.frame)
        controls.pack(fill="x")
        tk.Button(controls, text="Start", command=self.start).pack(side="left", padx=5, pady=5)
        tk.Button(controls, text="Stop", command=self.stop).pack(side="left", padx=5, pady=5)

        # Alarm indicators per sensor
        self.sensor_labels = []
        for i in range(self.num_sensors):
            lbl = tk.Label(controls, text=f"S{i+1}: OK", fg="green", font=("Arial", 9, "bold"))
            lbl.pack(side="left", padx=5)
            self.sensor_labels.append(lbl)

        engine = "GPU (CuPy)" if GPU_ENABLED else "CPU (NumPy)"
        self.engine_lbl = tk.Label(controls, text=f"Engine: {engine}", fg="gray")
        self.engine_lbl.pack(side="right", padx=10)

        # Matplotlib figure
        self.fig = Figure(figsize=(6.5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(f"{self.name} - Rolling Data ({engine})")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)

        # Colors and lines for sensors
        self.colors = ["blue", "green", "orange", "purple", "brown"]
        self.lines = []
        for i in range(self.num_sensors):
            (line,) = self.ax.plot([], [], lw=1.5,
                                   color=self.colors[i % len(self.colors)],
                                   label=f"Sensor {i+1}")
            self.lines.append(line)
        self.ax.legend(loc="upper right")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Buffers for sensor data
        self.data_buffers = [xp.empty(0) for _ in range(self.num_sensors)]

    # -------- Controls --------
    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self._worker, daemon=True).start()

    def stop(self):
        self.running = False

    # -------- Data Generator --------
    def _generate_batch(self, n):
        # Random noise + slow sine drift
        vals = xp.random.rand(self.num_sensors, n) * self.y_max
        t = xp.arange(n, dtype=xp.float32)
        vals += (xp.sin(t / 10.0) + 1.0) * (0.1 * self.y_max)
        return xp.clip(vals, 0, self.y_max)  # shape: [num_sensors, n]

    def _worker(self):
        while self.running:
            batch = self._generate_batch(self.batch_size)

            for i in range(self.num_sensors):
                buf = xp.concatenate([self.data_buffers[i], batch[i]])
                if buf.size > self.max_points:
                    buf = buf[-self.max_points:]
                self.data_buffers[i] = buf

            # Copy to CPU for plotting
            buffers_cpu = [xp.asnumpy(buf) for buf in self.data_buffers]
            latest_vals = [buf[-1] if buf.size > 0 else 0.0 for buf in buffers_cpu]

            self.frame.after(0, self._update_gui, buffers_cpu, latest_vals)
            time.sleep(0.4)

    # -------- GUI Update --------
    def _update_gui(self, buffers_cpu, latest_vals):
        self.ax.clear()
        self.ax.set_title(f"{self.name} - Rolling Data")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)

        alarming = False
        for i, buf in enumerate(buffers_cpu):
            xs = list(range(len(buf)))
            self.ax.plot(xs, buf, lw=1.5,
                         color=self.colors[i % len(self.colors)],
                         label=f"Sensor {i+1}")

            # Alarm per sensor
            if len(buf) > 0 and buf[-1] > 0.7 * self.y_max:
                self.sensor_labels[i].config(text=f"S{i+1}: HIGH", fg="red")
                alarming = True
            else:
                self.sensor_labels[i].config(text=f"S{i+1}: OK", fg="green")

        self.ax.legend(loc="upper right")

        # Tab coloring (group alarm)
        self.ax.set_facecolor("#ffcccc" if alarming else "white")
        self._set_tab_badge(alarming)

        self.canvas.draw_idle()

    def _set_tab_badge(self, alarming: bool):
        base = self.name
        current = self.nb.tab(self.frame, "text")
        want = f"🔴 {base}" if alarming else base
        if current != want:
            self.nb.tab(self.frame, text=want)


# -------- Main --------
def main():
    root = tk.Tk()
    root.title("5 Sensors per Tab with GPU/CPU Support")
    root.geometry("1200x750")

    nb = ttk.Notebook(root)
    nb.pack(fill="both", expand=True)

    # Multiple tabs with 5 sensors each
    PlotTab(nb, "Group A")
    PlotTab(nb, "Group B")
    PlotTab(nb, "Group C")

    root.mainloop()


# if __name__ == "__main__":
#     main()

# ------------------------------------------- working when tab is selected  and others working in the background
import tkinter as tk
from tkinter import ttk
import threading
import time
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Try GPU (CuPy), else fall back to NumPy
try:
    import cupy as xp
    GPU_ENABLED = True
except ImportError:
    import numpy as xp
    GPU_ENABLED = False
    # make numpy compatible with cupy API
    xp.asnumpy = lambda x: x

matplotlib.use("TkAgg")


class PlotTab:
    def __init__(self, notebook: ttk.Notebook, name="Sensor Group",
                 num_sensors=5, max_points=200, y_max=100, batch_size=32):
        self.nb = notebook
        self.name = name
        self.num_sensors = num_sensors
        self.max_points = max_points
        self.y_max = y_max
        self.batch_size = batch_size
        self.running = False

        # Frame for this tab
        self.frame = ttk.Frame(self.nb)
        self.nb.add(self.frame, text=self.name)

        # Alarm indicators per sensor
        controls = tk.Frame(self.frame)
        controls.pack(fill="x")
        self.sensor_labels = []
        for i in range(self.num_sensors):
            lbl = tk.Label(controls, text=f"S{i+1}: OK", fg="green", font=("Arial", 9, "bold"))
            lbl.pack(side="left", padx=5)
            self.sensor_labels.append(lbl)

        engine = "GPU (CuPy)" if GPU_ENABLED else "CPU (NumPy)"
        self.engine_lbl = tk.Label(controls, text=f"Engine: {engine}", fg="gray")
        self.engine_lbl.pack(side="right", padx=10)

        # Matplotlib figure
        self.fig = Figure(figsize=(6.5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(f"{self.name} - Rolling Data ({engine})")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)

        # Colors and lines for sensors
        self.colors = ["blue", "green", "orange", "purple", "brown"]
        self.lines = []
        for i in range(self.num_sensors):
            (line,) = self.ax.plot([], [], lw=1.5,
                                   color=self.colors[i % len(self.colors)],
                                   label=f"Sensor {i+1}")
            self.lines.append(line)
        self.ax.legend(loc="upper right")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Buffers for sensor data
        self.data_buffers = [xp.empty(0) for _ in range(self.num_sensors)]

    # -------- Controls --------
    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self._worker, daemon=True).start()

    def stop(self):
        self.running = False

    # -------- Data Generator --------
    def _generate_batch(self, n):
        vals = xp.random.rand(self.num_sensors, n) * self.y_max
        t = xp.arange(n, dtype=xp.float32)
        vals += (xp.sin(t / 10.0) + 1.0) * (0.1 * self.y_max)
        return xp.clip(vals, 0, self.y_max)  # shape: [num_sensors, n]

    def _worker(self):
        while self.running:
            batch = self._generate_batch(self.batch_size)

            for i in range(self.num_sensors):
                buf = xp.concatenate([self.data_buffers[i], batch[i]])
                if buf.size > self.max_points:
                    buf = buf[-self.max_points:]
                self.data_buffers[i] = buf

            # Copy to CPU for plotting
            buffers_cpu = [xp.asnumpy(buf) for buf in self.data_buffers]

            self.frame.after(0, self._update_gui, buffers_cpu)
            time.sleep(0.4)

    # -------- GUI Update --------
    def _update_gui(self, buffers_cpu):
        self.ax.clear()
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)

        alarming = False
        for i, buf in enumerate(buffers_cpu):
            xs = list(range(len(buf)))
            self.ax.plot(xs, buf, lw=1.5,
                         color=self.colors[i % len(self.colors)],
                         label=f"Sensor {i+1}")

            # Alarm per sensor
            if len(buf) > 0 and buf[-1] > 0.7 * self.y_max:
                self.sensor_labels[i].config(text=f"S{i+1}: HIGH", fg="red")
                alarming = True
            else:
                self.sensor_labels[i].config(text=f"S{i+1}: OK", fg="green")

        self.ax.legend(loc="upper right")

        # Tab coloring (group alarm)
        self.ax.set_facecolor("#ffcccc" if alarming else "white")
        self._set_tab_badge(alarming)

        self.canvas.draw_idle()

    def _set_tab_badge(self, alarming: bool):
        base = self.name
        current = self.nb.tab(self.frame, "text")
        want = f"🔴 {base}" if alarming else base
        if current != want:
            self.nb.tab(self.frame, text=want)


# -------- Main --------
def main():
    root = tk.Tk()
    root.title("5 Sensors per Tab with GPU/CPU Support")
    root.geometry("1200x750")

    nb = ttk.Notebook(root)
    nb.pack(fill="both", expand=True)

    # Multiple tabs with 5 sensors each
    tabs = [
        PlotTab(nb, "Group A"),
        PlotTab(nb, "Group B"),
        PlotTab(nb, "Group C")
    ]

    # Start all tabs so they keep running in background
    for tab in tabs:
        tab.start()

    root.mainloop()


# if __name__ == "__main__":
#     main()
# --------------------------------------------------------------------------------
import tkinter as tk
from tkinter import ttk
import threading
import time
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Try GPU (CuPy), else fall back to NumPy
try:
    import cupy as xp
    GPU_ENABLED = True
except ImportError:
    import numpy as xp
    GPU_ENABLED = False
    # make numpy compatible with cupy API
    xp.asnumpy = lambda x: x

matplotlib.use("TkAgg")


class PlotTab:
    def __init__(self, notebook: ttk.Notebook, name="Sensor Group",
                 num_sensors=5, max_points=200, y_max=100, batch_size=32, seed=None):
        self.nb = notebook
        self.name = name
        self.num_sensors = num_sensors
        self.max_points = max_points
        self.y_max = y_max
        self.batch_size = batch_size
        self.running = False

        # Independent random generator (different per tab)
        if hasattr(xp.random, "default_rng"):
            self.rng = xp.random.default_rng(seed)
        else:  # fallback for old numpy
            self.rng = xp.random.RandomState(seed)

        # Frame for this tab
        self.frame = ttk.Frame(self.nb)
        self.nb.add(self.frame, text=self.name)

        # Alarm indicators per sensor
        controls = tk.Frame(self.frame)
        controls.pack(fill="x")
        self.sensor_labels = []
        for i in range(self.num_sensors):
            lbl = tk.Label(controls, text=f"S{i+1}: OK", fg="green", font=("Arial", 9, "bold"))
            lbl.pack(side="left", padx=5)
            self.sensor_labels.append(lbl)

        engine = "GPU (CuPy)" if GPU_ENABLED else "CPU (NumPy)"
        self.engine_lbl = tk.Label(controls, text=f"Engine: {engine}", fg="gray")
        self.engine_lbl.pack(side="right", padx=10)

        # Matplotlib figure
        self.fig = Figure(figsize=(6.5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(f"{self.name} - Rolling Data ({engine})")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)

        # Colors and lines for sensors
        self.colors = ["blue", "green", "orange", "purple", "brown"]
        self.lines = []
        for i in range(self.num_sensors):
            (line,) = self.ax.plot([], [], lw=1.5,
                                   color=self.colors[i % len(self.colors)],
                                   label=f"Sensor {i+1}")
            self.lines.append(line)
        self.ax.legend(loc="upper right")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Buffers for sensor data
        self.data_buffers = [xp.empty(0) for _ in range(self.num_sensors)]

    # -------- Controls --------
    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self._worker, daemon=True).start()

    def stop(self):
        self.running = False

    # -------- Data Generator --------
    def _generate_batch(self, n):
        vals = self.rng.random((self.num_sensors, n)) * self.y_max
        t = xp.arange(n, dtype=xp.float32)
        vals += (xp.sin(t / 10.0) + 1.0) * (0.1 * self.y_max)
        return xp.clip(vals, 0, self.y_max)  # shape: [num_sensors, n]

    def _worker(self):
        while self.running:
            batch = self._generate_batch(self.batch_size)

            for i in range(self.num_sensors):
                buf = xp.concatenate([self.data_buffers[i], batch[i]])
                if buf.size > self.max_points:
                    buf = buf[-self.max_points:]
                self.data_buffers[i] = buf

            # Copy to CPU for plotting
            buffers_cpu = [xp.asnumpy(buf) for buf in self.data_buffers]

            self.frame.after(0, self._update_gui, buffers_cpu)
            time.sleep(0.4)

    # -------- GUI Update --------
    def _update_gui(self, buffers_cpu):
        self.ax.clear()
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)

        alarming = False
        for i, buf in enumerate(buffers_cpu):
            xs = list(range(len(buf)))
            self.ax.plot(xs, buf, lw=1.5,
                         color=self.colors[i % len(self.colors)],
                         label=f"Sensor {i+1}")

            # Alarm per sensor
            if len(buf) > 0 and buf[-1] > 0.7 * self.y_max:
                self.sensor_labels[i].config(text=f"S{i+1}: HIGH", fg="red")
                alarming = True
            else:
                self.sensor_labels[i].config(text=f"S{i+1}: OK", fg="green")

        self.ax.legend(loc="upper right")

        # Tab coloring (group alarm)
        self.ax.set_facecolor("#ffcccc" if alarming else "white")
        self._set_tab_badge(alarming)

        self.canvas.draw_idle()

    def _set_tab_badge(self, alarming: bool):
        base = self.name
        current = self.nb.tab(self.frame, "text")
        want = f"🔴 {base}" if alarming else base
        if current != want:
            self.nb.tab(self.frame, text=want)


# -------- Main --------
def main():
    root = tk.Tk()
    root.title("Independent Sensors per Tab (GPU/CPU)")
    root.geometry("1200x750")

    nb = ttk.Notebook(root)
    nb.pack(fill="both", expand=True)

    # Each tab with a different RNG seed
    tabs = [
        PlotTab(nb, "Group A", seed=1),
        PlotTab(nb, "Group B", seed=2),
        PlotTab(nb, "Group C", seed=3)
    ]

    # Start all tabs so they keep running
    for tab in tabs:
        tab.start()

    root.mainloop()


# if __name__ == "__main__":
#     main()

# ---------------------------------------------------------------
import tkinter as tk
from tkinter import ttk
import threading
import time
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import random
import sys
import os

# Cross-platform simple beep
def beep():
    try:
        if sys.platform.startswith("win"):
            import winsound
            winsound.Beep(1000, 200)  # 1000 Hz for 200 ms
        else:
            os.system("printf '\\a'")  # Linux/macOS terminal bell
    except Exception:
        pass


matplotlib.use("TkAgg")


class PlotTab:
    def __init__(self, notebook: ttk.Notebook, name="Sensor Group",
                 num_sensors=5, max_points=200, y_max=100):
        self.nb = notebook
        self.name = name
        self.num_sensors = num_sensors
        self.max_points = max_points
        self.y_max = y_max
        self.running = False

        # Frame for this tab
        self.frame = ttk.Frame(self.nb)
        self.nb.add(self.frame, text=self.name)

        # Sensor indicators
        controls = tk.Frame(self.frame)
        controls.pack(fill="x")
        self.sensor_labels = []
        for i in range(self.num_sensors):
            lbl = tk.Label(controls, text=f"S{i+1}: OK", fg="green", font=("Arial", 9, "bold"))
            lbl.pack(side="left", padx=5)
            self.sensor_labels.append(lbl)

        # Matplotlib figure
        self.fig = Figure(figsize=(6.5, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(f"{self.name} - 5 Sensors")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)

        self.colors = ["blue", "green", "orange", "purple", "brown"]
        self.lines = []
        for i in range(self.num_sensors):
            (line,) = self.ax.plot([], [], lw=1.5,
                                   color=self.colors[i % len(self.colors)],
                                   label=f"Sensor {i+1}")
            self.lines.append(line)
        self.ax.legend(loc="upper right")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Buffers
        self.data_buffers = [[] for _ in range(self.num_sensors)]

    # -------- Controls --------
    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self._worker, daemon=True).start()

    def stop(self):
        self.running = False

    # -------- Worker --------
    def _worker(self):
        while self.running:
            new_vals = [random.uniform(0, self.y_max) for _ in range(self.num_sensors)]

            alarming = False
            for i in range(self.num_sensors):
                buf = self.data_buffers[i]
                buf.append(new_vals[i])
                if len(buf) > self.max_points:
                    buf.pop(0)
                self.data_buffers[i] = buf

                # Alarm check
                if new_vals[i] < 0.1 * self.y_max or new_vals[i] > 0.9 * self.y_max:
                    alarming = True
                    self.sensor_labels[i].config(text=f"S{i+1}: ALERT", fg="red")
                    beep()
                else:
                    self.sensor_labels[i].config(text=f"S{i+1}: OK", fg="green")

            # GUI update
            self.frame.after(0, self._update_gui, alarming)
            time.sleep(0.5)

    # -------- GUI Update --------
    def _update_gui(self, alarming: bool):
        self.ax.clear()
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)

        for i, buf in enumerate(self.data_buffers):
            xs = list(range(len(buf)))
            self.ax.plot(xs, buf, lw=1.5,
                         color=self.colors[i % len(self.colors)],
                         label=f"Sensor {i+1}")

        self.ax.legend(loc="upper right")
        self.ax.set_facecolor("#ffcccc" if alarming else "white")
        self._set_tab_badge(alarming)

        self.canvas.draw_idle()

    def _set_tab_badge(self, alarming: bool):
        base = self.name
        current = self.nb.tab(self.frame, "text")
        want = f"🔴 {base}" if alarming else base
        if current != want:
            self.nb.tab(self.frame, text=want)


class CommonPlot:
    """Shared plot at the bottom for overview or summary."""
    def __init__(self, root, num_sensors=5, max_points=200, y_max=100):
        self.num_sensors = num_sensors
        self.max_points = max_points
        self.y_max = y_max
        self.data_buffers = [[] for _ in range(self.num_sensors)]

        self.fig = Figure(figsize=(10, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Common Plot Area - Overview")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)

        self.colors = ["cyan", "magenta", "gold", "gray", "black"]
        self.lines = []
        for i in range(self.num_sensors):
            (line,) = self.ax.plot([], [], lw=1.2,
                                   color=self.colors[i % len(self.colors)],
                                   label=f"Common S{i+1}")
            self.lines.append(line)
        self.ax.legend(loc="upper right")

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        # ---- e.g data source -------
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        while True:
            new_vals = [random.uniform(0, self.y_max) for _ in range(self.num_sensors)]
            for i in range(self.num_sensors):
                buf = self.data_buffers[i]
                buf.append(new_vals[i])
                if len(buf) > self.max_points:
                    buf.pop(0)
                self.data_buffers[i] = buf
            self.canvas.get_tk_widget().after(0, self._update_plot)
            time.sleep(0.5)

    def _update_plot(self):
        self.ax.clear()
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)

        for i, buf in enumerate(self.data_buffers):
            xs = list(range(len(buf)))
            self.ax.plot(xs, buf, lw=1.2,
                         color=self.colors[i % len(self.colors)],
                         label=f"Common S{i+1}")

        self.ax.legend(loc="upper right")
        self.canvas.draw_idle()


# -------- Main --------
def main():
    root = tk.Tk()
    root.title("Tabbed Plots with Common Area")
    root.geometry("1200x800")

    # Split top and bottom
    top_frame = tk.Frame(root, height=400)
    top_frame.pack(fill="both", expand=True)
    bottom_frame = tk.Frame(root, height=400)
    bottom_frame.pack(fill="both", expand=True)

    # Top: 5 tabs
    nb = ttk.Notebook(top_frame)
    nb.pack(fill="both", expand=True)
    tabs = [PlotTab(nb, f"Group {i+1}") for i in range(5)]
    for tab in tabs:
        tab.start()

    # Bottom: shared plot
    CommonPlot(bottom_frame)

    root.mainloop()

#
# if __name__ == "__main__":
#     main()

# ----------------------------------------------
import tkinter as tk
from tkinter import ttk
import threading
import time
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import random
import sys
import os

# --------- Simple cross-platform beep ----------
def beep():
    try:
        if sys.platform.startswith("win"):
            import winsound
            winsound.Beep(1000, 200)  # 1000 Hz for 200 ms
        else:
            os.system("printf '\\a'")
    except Exception:
        pass


matplotlib.use("TkAgg")


class PlotTab:
    def __init__(self, notebook: ttk.Notebook, name="Sensor Group",
                 num_sensors=5, max_points=200, y_max=100):
        self.nb = notebook
        self.name = name
        self.num_sensors = num_sensors
        self.max_points = max_points
        self.y_max = y_max
        self.running = False

        # Frame for this tab
        self.frame = ttk.Frame(self.nb)
        self.nb.add(self.frame, text=self.name)

        # Sensor indicators
        controls = tk.Frame(self.frame)
        controls.pack(fill="x")
        self.sensor_labels = []
        for i in range(self.num_sensors):
            lbl = tk.Label(controls, text=f"S{i+1}: OK", fg="green", font=("Arial", 9, "bold"))
            lbl.pack(side="left", padx=5)
            self.sensor_labels.append(lbl)

        # Matplotlib figure for the tab
        self.fig = Figure(figsize=(6.5, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(f"{self.name} - 5 Sensors")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)

        self.colors = ["blue", "green", "orange", "purple", "brown"]
        self.lines = []
        for i in range(self.num_sensors):
            (line,) = self.ax.plot([], [], lw=1.5,
                                   color=self.colors[i % len(self.colors)],
                                   label=f"Sensor {i+1}")
            self.lines.append(line)
        self.ax.legend(loc="upper right")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Buffers
        self.data_buffers = [[] for _ in range(self.num_sensors)]

    # -------- Controls --------
    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self._worker, daemon=True).start()

    def stop(self):
        self.running = False

    # -------- Worker --------
    def _worker(self):
        while self.running:
            new_vals = [random.uniform(0, self.y_max) for _ in range(self.num_sensors)]

            alarming = False
            for i in range(self.num_sensors):
                buf = self.data_buffers[i]
                buf.append(new_vals[i])
                if len(buf) > self.max_points:
                    buf.pop(0)
                self.data_buffers[i] = buf

                # Alarm check
                if new_vals[i] < 0.1 * self.y_max or new_vals[i] > 0.9 * self.y_max:
                    alarming = True
                    self.sensor_labels[i].config(text=f"S{i+1}: ALERT", fg="red")
                    beep()
                else:
                    self.sensor_labels[i].config(text=f"S{i+1}: OK", fg="green")

            # GUI update
            self.frame.after(0, self._update_gui, alarming)
            time.sleep(0.5)

    # -------- GUI Update --------
    def _update_gui(self, alarming: bool):
        self.ax.clear()
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)

        for i, buf in enumerate(self.data_buffers):
            xs = list(range(len(buf)))
            self.ax.plot(xs, buf, lw=1.5,
                         color=self.colors[i % len(self.colors)],
                         label=f"Sensor {i+1}")

        self.ax.legend(loc="upper right")
        self.ax.set_facecolor("#ffcccc" if alarming else "white")
        self._set_tab_badge(alarming)

        self.canvas.draw_idle()

    def _set_tab_badge(self, alarming: bool):
        base = self.name
        current = self.nb.tab(self.frame, "text")
        want = f"🔴 {base}" if alarming else base
        if current != want:
            self.nb.tab(self.frame, text=want)


class CommonPlot:
    """Shared plot at the TOP for overview."""
    def __init__(self, root, num_sensors=5, max_points=200, y_max=100):
        self.num_sensors = num_sensors
        self.max_points = max_points
        self.y_max = y_max
        self.data_buffers = [[] for _ in range(self.num_sensors)]

        self.fig = Figure(figsize=(10, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Common Plot Area - Overview")
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)

        self.colors = ["cyan", "magenta", "gold", "gray", "black"]
        for i in range(self.num_sensors):
            self.ax.plot([], [], lw=1.2, color=self.colors[i % len(self.colors)], label=f"Common S{i+1}")
        self.ax.legend(loc="upper right")

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)


    def _worker(self):
        while True:
            new_vals = [random.uniform(0, self.y_max) for _ in range(self.num_sensors)]
            for i in range(self.num_sensors):
                buf = self.data_buffers[i]
                buf.append(new_vals[i])
                if len(buf) > self.max_points:
                    buf.pop(0)
                self.data_buffers[i] = buf
            self.canvas.get_tk_widget().after(0, self._update_plot)
            time.sleep(0.5)

    def _update_plot(self):
        self.ax.clear()
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(0, self.y_max)

        for i, buf in enumerate(self.data_buffers):
            xs = list(range(len(buf)))
            self.ax.plot(xs, buf, lw=1.2,
                         color=self.colors[i % len(self.colors)],
                         label=f"Common S{i+1}")

        self.ax.legend(loc="upper right")
        self.canvas.draw_idle()


# -------- Main --------
def main():
    root = tk.Tk()
    root.title("Common Plot on Top + Tabbed Plots Below")
    root.geometry("1200x800")

    # Top common plot
    top_frame = tk.Frame(root, height=400)
    top_frame.pack(fill="both", expand=True)
    CommonPlot(top_frame)

    # Bottom tabbed plots
    bottom_frame = tk.Frame(root, height=400)
    bottom_frame.pack(fill="both", expand=True)

    nb = ttk.Notebook(bottom_frame)
    nb.pack(fill="both", expand=True)
    tabs = [PlotTab(nb, f"Group {i+1}") for i in range(5)]
    for tab in tabs:
        tab.start()

    root.mainloop()

#
# if __name__ == "__main__":
#     main()

# -----------------------------------
import requests
import cfscrape
from bs4 import BeautifulSoup as bs

# header = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"}
# s = requests.session()
# scraper=cfscrape.create_scraper(sess=s) #i use cfscrape because the page uses cloudflare anti ddos page
# scraper.get("https://www.bstn.com/einloggen", headers=header)
# myacc={"login[email]": "labsrob@gmail.com", #obviously change
# "login[password]": "password123"}
# entry=scraper.post("https://www.bstn.com/einloggen", headers=header, data=myacc)
# soup=bs(entry.text, 'lxml')
# accnm=soup.find('meta',{'property':'og:title'})['content']
# print("Logged in as: " + accnm)
# aaaa=scraper.get("https://www.bstn.com/kundenkonto", headers=header)
# print(aaaa.cookies)


# Implementation of matplotlib function
from matplotlib.axis import Axis
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.widgets import Slider, Button, RadioButtons
#
# fig, ax1 = plt.subplots()
# plt.subplots_adjust(bottom=0.25)
# t = np.arange(0.0, 1.0, 0.001)
# a0 = 5
# f0 = 3
# delta_f = 5.0
# s = a0 * np.sin(2 * np.pi * f0 * t)
#
# ax1.plot(t, s, lw=2, color='green')
#
# ax1.xaxis.pan(-2)
#
# ax1.grid()
#
# fig.suptitle("""matplotlib.axis.Axis.pan()
# function Example\n""", fontweight="bold")
#
# plt.show()

# -------------------------------------------------------------------------[]
