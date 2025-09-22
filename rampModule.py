

import tkinter as tk
from tkinter import ttk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# --- Helper Functions ---
def compute_running_stats(signal, window=20):
    """Compute running mean and std with a moving window."""
    cumsum = np.cumsum(np.insert(signal, 0, 0))
    running_mean = (cumsum[window:] - cumsum[:-window]) / window

    running_std = np.array([
        np.std(signal[i:i+window]) for i in range(len(signal) - window + 1)
    ])
    return running_mean, running_std

# --- Main App Class ---
class SensorPlotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sensor Signal Viewer with Running Stats")
        self.geometry("1000x800")

        # Simulated sensor data
        self.time = np.linspace(0, 10, 1000)
        self.sensors = {
            "Sensor A": np.sin(self.time) + np.random.normal(0, 0.2, len(self.time)),
            "Sensor B": np.cos(self.time) + np.random.normal(0, 0.3, len(self.time)),
            "Sensor C": np.sin(2 * self.time) + np.random.normal(0, 0.1, len(self.time)),
        }

        self.create_widgets()

    def create_widgets(self):
        # --- Top Plot: Common Raw Signal (first sensor) ---
        top_frame = ttk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        fig_top = Figure(figsize=(10, 2.5), dpi=100)
        ax_top = fig_top.add_subplot(111)
        ax_top.plot(self.time, self.sensors["Sensor A"], label="Sensor A Raw")
        ax_top.set_title("Top Plot: Raw Sensor A Signal")
        ax_top.set_xlabel("Time (s)")
        ax_top.set_ylabel("Amplitude")
        ax_top.grid(True)
        ax_top.legend()

        canvas_top = FigureCanvasTkAgg(fig_top, master=top_frame)
        canvas_top.draw()
        canvas_top.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # --- Notebook Tabs ---
        notebook = ttk.Notebook(self)
        notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        for name, signal in self.sensors.items():
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=name)

            self.populate_tab(tab, signal, sensor_name=name)

    def populate_tab(self, parent, signal, sensor_name):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)

        fig = Figure(figsize=(10, 6), dpi=100)

        # Running stats
        window_size = 50
        mean, std = compute_running_stats(signal, window=window_size)
        time_stats = self.time[:len(mean)]

        # Mean Plot
        ax1 = fig.add_subplot(211)
        ax1.plot(time_stats, mean, color='blue', label=f'{sensor_name} Running Mean')
        ax1.set_title(f"{sensor_name} - Running Mean (window={window_size})")
        ax1.set_xlabel("Time (s)")
        ax1.set_ylabel("Mean")
        ax1.grid(True)
        ax1.legend()

        # Std Deviation Plot
        ax2 = fig.add_subplot(212)
        ax2.plot(time_stats, std, color='green', label=f'{sensor_name} Running Std Dev')
        ax2.set_title(f"{sensor_name} - Running Standard Deviation (window={window_size})")
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Std Dev")
        ax2.grid(True)
        ax2.legend()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# --- Run App ---
if __name__ == "__main__":
    app = SensorPlotApp()
    app.mainloop()
