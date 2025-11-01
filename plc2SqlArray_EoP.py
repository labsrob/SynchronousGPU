# This script is called in from Main program to load SQL execution syntax command and return a list in LisDat
 # Author: D Labs, R

# NOTE:
# data_gpu[:, :-1] → keeps all except the last column
# exclude_idx = 1  # the one you want to skip
# cols = [i for i in range(data_gpu.shape[1]) if i != exclude_idx]
# numeric_gpu = data_gpu[:, cols],
"""
This is a GPU-accelerated algorithm ----------------------------------------[]
Using a single convolution kernel, defined once
Each DB runs in its own thread — fully concurrent, no blocking
Prevents balloon effect by keeping the last 30 samples per DB
Uses a deque(maxlen=EXPORT_THRESHOLD)
Parallelisation technique to computes rolling mean & std dev on CuPy arrays
NOTE: Python automatically spawns a new background thread and calls your overridden run()
"""

import time
import snap7
import pandas as pd
import queue
import cupy as cp
import threading
from snap7.util import get_int
from collections import deque

# ----------------------------------------------------------------------------- #
# CONFIGURATION
# ----------------------------------------------------------------------------- #
PLC_IP = "192.168.100.100"
DBS = {
    "QRP": 235,   # Pressure data block
    "QTT": 233,   # Tape temperature data block
    "QST": 234    # Substrate temperature data block
}

ROLL_WINDOW = 30
SAMPLE_SIZE = 30
EXPORT_THRESHOLD = 40
POLL_INTERVAL = 0.1  # 10 Hz sampling rate
ALARM_THRESHOLD = 200

# ----------------------------------------------------------------------------- #
# PLC DATA COLLECTOR CLASS
# ----------------------------------------------------------------------------- #
class PLCCollector(threading.Thread):
    #  def __init__(self, ip, db_number, name, window=ROLL_WINDOW, sample_size=SAMPLE_SIZE):
    def __init__(self, ip, db_number, name, queue_out, window=ROLL_WINDOW, sample_size=SAMPLE_SIZE):
        super().__init__(daemon=True)
        self.ip = ip
        self.db_number = db_number
        self.name = name
        self.window = window
        self.sample_size = sample_size
        self.client = snap7.client.Client()
        self.cols = ["timestamp", "cLayer"] + [f"R{i}H{j}" for i in range(1, 5) for j in range(1, 5)]
        self.data = deque(maxlen=EXPORT_THRESHOLD)
        self.queue_out = queue_out
        self.running = True

    def connect(self):
        try:
            self.client.connect(self.ip, 0, 1)
        except Exception as e:
            print(f"[{self.name}] PLC connection error: {e}")

    def read_block(self):
        """Read one full PLC DB block"""
        try:
            size = 18 * 2
            raw = self.client.db_read(self.db_number, 0, size)
            vals = [get_int(raw, i * 2) for i in range(18)]
            return vals
        except Exception as e:
            print(f"[{self.name}] DB Read Error: {e}")
            return [0]*18

    def run(self):
        """Continuous sampling loop"""
        self.connect()
        kernel = cp.ones(self.window) / self.window  # Define kernel once (optimization)
        print(f"[{self.name}] Connected. Starting rolling acquisition...")

        while self.running:
            timestamp = time.time()
            vals = self.read_block()
            self.data.append([timestamp] + vals)
            time.sleep(POLL_INTERVAL)

            if len(self.data) >= self.window:
                # GPU processing (exclude timestamp)
                data_gpu = cp.asarray(self.data)
                numeric_gpu = data_gpu[:, 1:]  # Exclude first column
                roll_mean = cp.apply_along_axis(lambda col: cp.convolve(col, kernel, mode='valid'), 0, numeric_gpu)
                roll_std = cp.apply_along_axis(lambda col: cp.sqrt(cp.convolve(col**2, kernel, mode='valid') - cp.convolve(col, kernel, mode='valid')**2),0, numeric_gpu)

                # Send latest means to GUI thread
                mean_last = cp.asnumpy(roll_mean[-1])
                self.queue_out.put((self.name, mean_last))

                # Display last rolling stats (without ballooning)
                print(f"[{self.name}] Mean (last): {cp.asnumpy(roll_mean[-1])[:4]} ...")
                print(f"[{self.name}] Std (last):  {cp.asnumpy(roll_std[-1])[:4]} ...")
                print("-"*50)
            time.sleep(3)   # trip timer

    def stop(self):
        self.running = False
        try:
            self.client.disconnect()
            self.client.destroy()
        except Exception:
            pass
        print(f"[{self.name}] Collector stopped.")


def plcExec():
    queues = {name: queue.Queue() for name in DBS.keys()}
    collectors = [PLCCollector(PLC_IP, db, name, queues[name]) for name, db in DBS.items()]
    # collectors = [PLCCollector(PLC_IP, db, name) for name, db in DBS.items()]

    try:
        for c in collectors:
            c.start()       # dispatches to a new thread
        print("[INFO] All collectors running...\n")

        # Wait until user stops or CTRL+C
        while True:
            time.sleep(3)

    except KeyboardInterrupt:
        print("\n[INFO] Stopping collectors...")
        for c in collectors:
            c.stop()
        for c in collectors:
            c.join()
        print("[INFO] All collectors stopped.")



if __name__ == "__main__":
    plcExec()
