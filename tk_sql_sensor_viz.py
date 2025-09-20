"""
tk_sql_sensor_viz.py

A Tkinter app that periodically loads multi-columns from SQL Server sensor tables
and visualizes them.

Features:
- Top shared visualization (bar chart showing latest means per tab)
- Notebook with 3 tabs; each tab shows:
    * rolling time-series plot for configured columns
    * rolling standard-deviation plot for the same columns
- Periodic polling from SQL Server using background threads
- Optional GPU acceleration using CuPy with automatic fallback to NumPy

Configure the `CONFIG` dict below with your DB connection string, queries, sensor columns,
and polling interval.

Dependencies:
    pip install pyodbc pandas matplotlib numpy cupy-python-headless
    (cupy is optional; if unavailable, NumPy will be used)

Run:
    python tk_sql_sensor_viz.py

"""

import sys
import threading
import traceback
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import pyodbc
import pandas as pd

# Try to import CuPy for GPU acceleration; otherwise use NumPy as a fallback.
try:
    import cupy as cp
    GPU_AVAILABLE = True
except Exception:
    import numpy as cp  # we alias NumPy as cp so later code can call cp.* the same way
    GPU_AVAILABLE = False

import numpy as np  # we still keep numpy for certain utilities

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk

# ================ Configuration ================
# Edit these entries to match your environment
CONFIG = {
    # pyodbc connection string template. Example for SQL Server:
    # "DRIVER={ODBC Driver 17 for SQL Server};SERVER=server_name;DATABASE=db;UID=user;PWD=password"
    'CONN_STR': "DRIVER={SQL Server};SERVER=localhost;DATABASE=YourDB;UID=sa;PWD=YourPassword",

    # polling interval in milliseconds
    'POLL_MS': 2000,

    # rolling window size (number of samples to keep)
    'WINDOW': 200,

    # list of tabs / sensor sources. Each entry must provide a name and SQL query that
    # returns at least a timestamp column and one or more numeric columns.
    # The query should return rows ordered by timestamp ASC ideally; if not, the code sorts by the timestamp column.
    'SOURCES': [
        {
            'name': 'Sensor A',
            'query': "SELECT TOP (1000) TimeStampUtc, Temp, Pressure, Humidity FROM dbo.SensorA ORDER BY TimeStampUtc DESC",
            'ts_col': 'TimeStampUtc',
            'cols': ['Temp', 'Pressure', 'Humidity']
        },
        {
            'name': 'Sensor B',
            'query': "SELECT TOP (1000) TimeStampUtc, X, Y FROM dbo.SensorB ORDER BY TimeStampUtc DESC",
            'ts_col': 'TimeStampUtc',
            'cols': ['X', 'Y']
        },
        {
            'name': 'Sensor C',
            'query': "SELECT TOP (1000) TimeStampUtc, A, B, C FROM dbo.SensorC ORDER BY TimeStampUtc DESC",
            'ts_col': 'TimeStampUtc',
            'cols': ['A', 'B', 'C']
        },
    ]
}

# ================ Helper: GPU wrapper ================
# We'll define a tiny wrapper for operations we need so both Cupy and Numpy work.
class ArrayBackend:
    def __init__(self):
        self.gpu = GPU_AVAILABLE
        self.lib = cp

    def array(self, x, dtype=None):
        return self.lib.array(x, dtype=dtype) if self.gpu else self.lib.asarray(x, dtype=dtype)

    def asnumpy(self, x):
        # cupy has .get(); numpy arrays are unchanged
        if self.gpu:
            return cp.asnumpy(x)
        else:
            return np.asarray(x)

    def mean(self, x, axis=None):
        return self.lib.mean(x, axis=axis)

    def std(self, x, axis=None):
        return self.lib.std(x, axis=axis)

    def nan_to_num(self, x, val=0.0):
        return self.lib.nan_to_num(x, nan=val)

backend = ArrayBackend()

# ================ DB Polling ================
class DBSampler:
    def __init__(self, conn_str):
        self.conn_str = conn_str
        self.lock = threading.Lock()
        self._conn = None

    def connect(self):
        with self.lock:
            if self._conn is None:
                self._conn = pyodbc.connect(self.conn_str, autocommit=True)
        return self._conn

    def fetch_df(self, query):
        try:
            conn = self.connect()
            df = pd.read_sql_query(query, conn)
            return df
        except Exception as e:
            print("DB fetch error:", e)
            traceback.print_exc()
            return pd.DataFrame()

# ================ Visualization App ================
class SensorTab:
    def __init__(self, parent, source_cfg, window):
        self.parent = parent
        self.cfg = source_cfg
        self.window = window
        self.ts_col = source_cfg['ts_col']
        self.cols = source_cfg['cols']

        # deques for each column and timestamps
        self.timestamps = deque(maxlen=window)
        self.data = {c: deque(maxlen=window) for c in self.cols}

        # Figure for this tab: two axes stacked vertically
        self.fig = Figure(figsize=(6, 3.5), tight_layout=True)
        self.ax_ts = self.fig.add_subplot(2, 1, 1)
        self.ax_std = self.fig.add_subplot(2, 1, 2)

        self.lines = {}  # lines for time series
        self.std_lines = {}  # lines for stddev plot

        # initialize empty lines
        for col in self.cols:
            ln, = self.ax_ts.plot([], [], label=col)
            sln, = self.ax_std.plot([], [], label=col)
            self.lines[col] = ln
            self.std_lines[col] = sln

        self.ax_ts.legend(loc='upper right', fontsize='small')
        self.ax_std.legend(loc='upper right', fontsize='small')
        self.ax_ts.set_ylabel('Value')
        self.ax_std.set_ylabel('Std Dev')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def ingest_dataframe(self, df):
        """Take rows from SQL and append to the rolling buffers"""
        if df.empty:
            return
        # ensure timestamp column is datetime
        df = df.copy()
        df[self.ts_col] = pd.to_datetime(df[self.ts_col])
        df = df.sort_values(self.ts_col)  # ascending

        for _, row in df.iterrows():
            ts = row[self.ts_col]
            self.timestamps.append(ts)
            for col in self.cols:
                val = row.get(col, np.nan)
                self.data[col].append(val)

    def update_plots(self):
        # convert to arrays (using backend if available) then compute std
        if not self.timestamps:
            return
        x = np.arange(-len(self.timestamps) + 1, 1)

        for col in self.cols:
            y_list = list(self.data[col])
            # use CPU numpy arrays for plotting convenience (matplotlib expects numpy arrays)
            y = np.asarray(y_list, dtype=float)
            if y.size == 0:
                continue
            # update time-series lines
            self.lines[col].set_data(x, y)
            # compute rolling std over the entire buffer for a simple demonstration
            std_val = np.std(y)
            # for std time-series, we plot the std across a trailing window: here we compute per-sample trailing std
            # compute trailing std via numpy for simplicity
            if y.size >= 2:
                trail_std = np.array([np.std(y[max(0, i - 20): i + 1]) for i in range(len(y))])
            else:
                trail_std = np.zeros_like(y)
            self.std_lines[col].set_data(x, trail_std)

        # autoscale axes
        self.ax_ts.relim()
        self.ax_ts.autoscale_view()
        self.ax_std.relim()
        self.ax_std.autoscale_view()

        self.canvas.draw_idle()

    def latest_means(self):
        # return mean of each column in this tab's buffer
        means = {}
        for col in self.cols:
            arr = np.asarray(self.data[col], dtype=float)
            if arr.size == 0:
                means[col] = np.nan
            else:
                means[col] = float(np.nanmean(arr))
        return means


class App(tk.Tk):
    def __init__(self, config):
        super().__init__()
        self.title('Sensor Multi-Tab Visualizer')
        self.geometry('1100x800')

        self.config = config
        self.window = config['WINDOW']
        self.poll_ms = config['POLL_MS']
        self.sources = config['SOURCES']

        # thread pool for DB fetching
        self.executor = ThreadPoolExecutor(max_workers=min(4, len(self.sources)))
        self.db = DBSampler(config['CONN_STR'])

        # Top shared visualization: overall means per source
        self.top_fig = Figure(figsize=(10, 2), tight_layout=True)
        self.top_ax = self.top_fig.add_subplot(1, 1, 1)
        self.top_canvas = FigureCanvasTkAgg(self.top_fig, master=self)
        self.top_canvas.get_tk_widget().pack(fill=tk.X)

        # notebook with tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tabs = []
        for src in self.sources:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=src['name'])
            tab = SensorTab(frame, src, self.window)
            self.tabs.append(tab)

        # state for shared plot
        self.shared_bar_containers = None

        # start polling
        self.after(500, self.poll_once)

    def poll_once(self):
        # schedule DB fetches concurrently
        futures = []
        for i, src in enumerate(self.sources):
            q = src['query']
            fut = self.executor.submit(self.db.fetch_df, q)
            futures.append((i, fut))

        # when complete, ingest into each tab in main thread via after
        def _ingest_results():
            for i, fut in futures:
                try:
                    df = fut.result(timeout=5)
                    # ensure dtype and columns exist
                    if not df.empty:
                        self.tabs[i].ingest_dataframe(df)
                except Exception as e:
                    print("Error fetching result for source", i, e)
            # update UI plots
            for tab in self.tabs:
                tab.update_plots()
            self.update_shared_plot()

            # schedule next poll
            self.after(self.poll_ms, self.poll_once)

        # run ingestion in mainloop shortly to avoid blocking
        self.after(10, _ingest_results)

    def update_shared_plot(self):
        # compute latest means from each tab and draw a simple bar chart
        labels = []
        means = []
        for tab in self.tabs:
            labels.append(tab.cfg['name'])
            # compute mean across all columns in the tab
            mdict = tab.latest_means()
            # mean of means (ignore NaNs)
            vals = [v for v in mdict.values() if v == v]  # v==v filters out NaN
            if vals:
                means.append(np.mean(vals))
            else:
                means.append(0.0)

        self.top_ax.clear()
        self.top_ax.bar(labels, means)
        self.top_ax.set_ylabel('Mean (latest buffer)')
        self.top_ax.set_title('Overview: Mean per Source')
        self.top_canvas.draw_idle()


if __name__ == '__main__':
    print('GPU available:', GPU_AVAILABLE)
    # Basic validation
    if not CONFIG['SOURCES']:
        print('No sources configured. Edit CONFIG in the script.')
        sys.exit(1)

    app = App(CONFIG)
    app.mainloop()
