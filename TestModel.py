# import multiprocessing
#
# # can also be a dictionary
# gpu_id_list = [3, 5, 7, 10]
#
#
# def function(x):
#     cpu_name = multiprocessing.current_process().name
#     cpu_id = int(cpu_name[cpu_name.find('-') + 1:]) - 1
#     gpu_id = gpu_id_list[cpu_id]
#
#     return x * gpu_id
#
#
# if __name__ == '__main__':
#     pool = multiprocessing.Pool(4)
#     input_list = [1, 1, 1, 1]
#     print(pool.map(function, input_list))
# -------------------------------------------------------------
#
import logging
import multiprocessing
import os
import time
#
# # logging just to get not mangled outputs
# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)
#
# def get_process_index(process) -> int:
#     proc_name = multiprocessing.current_process().name
#     # eg. "ForkPoolWorker-10", can be numbered not from zero upon multiple Pool invocations,
#     # be the numbering should be contiguous
#     return int(proc_name.split("-")[1])
#
# def initialize(gpus: list[str]):
#     if gpus:
#         proc_index = get_process_index(multiprocessing.current_process())
#         selected_gpu = gpus[proc_index % len(gpus)]
#         os.environ["CUDA_VISIBLE_DEVICES"] = str(selected_gpu)
#         logger.info(f"process id: {proc_index} -> GPU id: {selected_gpu}")
#
# def work(i):
#     time.sleep(0.1)
#     logger.info(f"work item {i} on GPU {os.environ['CUDA_VISIBLE_DEVICES']}")
#
# available_gpu_ids = [3, 5, 7]
# with multiprocessing.Pool(processes=4, initializer=initialize, initargs=(available_gpu_ids,)) as pool:
#     pool.map(work, range(12))
#
# -----------------------------------------------------------------
#
# from multiprocessing import Pool, current_process, Queue
#
# NUM_GPUS = 4
# PROC_PER_GPU = 2
#
# queue = Queue()
#
# def foo(filename):
#     gpu_id = queue.get()
#     try:
#         # run processing on GPU <gpu_id>
#         ident = current_process().ident
#         print('{}: starting process on GPU {}'.format(ident, gpu_id))
#         # ... process filename
#         print('{}: finished'.format(ident))
#     finally:
#         queue.put(gpu_id)
#
# # initialize the queue with the GPU ids
# for gpu_ids in range(NUM_GPUS):
#     for _ in range(PROC_PER_GPU):
#         queue.put(gpu_ids)
#
# pool = Pool(processes=PROC_PER_GPU * NUM_GPUS)
# files = ['file{}.xyz'.format(x) for x in range(1000)]
# for _ in pool.imap_unordered(foo, files):
#     pass
# pool.close()
# pool.join()

# ----------------------------------------------------------
# import pycuda
# from pycuda import compiler
# import pycuda.driver as drv
#
# drv.init()
# print("%d device(s) found." % drv.Device.count())
#
# for ordinal in range(drv.Device.count()):
#     dev = drv.Device(ordinal)
#     print(ordinal, dev.name())

# --------------------------------------------------------
from tkinter import *
import subprocess
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

try:
    subprocess.check_output('nvidia-smi')
    print('Nvidia GPU detected!')
except Exception: # this command not being found can raise quite a few different errors depending on the configuration
    print('No Nvidia GPU in system!')

import tkinter as tk

# class ResizableCanvas(tk.Canvas):
#     def __init__(self, master=None, **kwargs):
#         super().__init__(master, **kwargs)
#         self.bind("<Configure>", self.resize)
#
#     def resize(self, event):
#         self.config(width=event.width, height=event.height)
#
# root = tk.Tk()
# root.geometry("600x400")  # Set an initial size for the window
# canvas = ResizableCanvas(root)
# canvas.pack(fill=tk.BOTH, expand=True)
# root.mainloop()
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

class ResizableCanvas(tk.Canvas):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<Configure>", self.resize)

    def resize(self, event):
        self.config(width=event.width, height=event.height)

root = tk.Tk()
# root.geometry("600x400")  # Set an initial size for the window
canvas = ResizableCanvas(root)
Label(root, text='Size', width=8, state='normal', font=("bold", 10)).place(x=20, y=80)


# Define Axes ---------------------#
fig = Figure(figsize=(10, 5), dpi=100)


canvas = FigureCanvasTkAgg(fig, )
canvas.get_tk_widget().pack(expand=False)

# tes.pack()
# canvas.pack(fill=tk.BOTH, expand=True)
root.mainloop()
