# today = date.today()
import time
import pyodbc
import loadSQLConfig as tx

# Initialise relevant variables and load configuration settings ----------[]
# server_IP, db_ref, isAtho, yekref = tx.load_configSQL('checksumError.ini')
# print('ServerUse Details:', server_IP, db_ref, isAtho, yekref)
#
# server_IP = '10.0.3.172'
# db_ref = 'DAQ_sSPC'
# isAtho = 'TCP01'
# yekref = 'Testing27!'
# Encrypt = 'no'                  # Added today 06/08/2024 [optional]
# Certify = 'yes'                 # DITTO
#
# def EOLrpt_connect():
#     """
#     state: 1 connected, 0 Not connected
#     agent: 1 indicate SCADA remote call, 0 indicating SPC local User Call
#     """
#     # print('\nDatasource Details:', server_IP, db_ref)
#     # -------- Actual SQL Connection request -----------------#
#     conn = None
#     # ---------------------------------------------------------#
#     if conn == None:
#         print('\n[EoL] Connecting to SQL server...')
#
#         try:
#             conn = pyodbc.connect('Driver={SQL Server};'
#                                   'Server=' + server_IP + ';'
#                                   'Database=' + db_ref + ';'
#                                   'Encrypt=' + Encrypt + ';'
#                                   'TrustServerCertificate=' + Certify + ';'
#                                   'uid=' + isAtho + ';'
#                                   'pwd=' + yekref + ';'
#                                   'MultipleActiveResultSets=True', timeout=5, autocommit=True)
#             # conn = True
#             print('\n[EoL] SQL Server connection active!\n')
#             return conn
#
#         except Exception as err:
#             print('\n[EoL] Connection issue: SQL Server is inaccessible!')
#
#     return None
#
# # # Determine EOL Random sampling regime ---------------------------------------------------------------[X]
# tempo = EOLrpt_connect()
# t1 = tempo.cursor()
# t2 = tempo.cursor()
#
# T1 = 'ZTT_20250923'
# T2 = 'ZST_20250923'
# layerNo = 1

# Query = 'Select count([R1SP]) AS ValidTotal from [' + str(T1) + '] where [cLyr] = ' + str(layerNo)
# t1.execute(Query)
# data1 = t1.fetchone()

# ttSR = t1.execute('Select count([R1SP]) AS ValidTotal from [' + str(T1) + '] where [cLyr] = ' + str(layerNo)).fetchone()
# stSR = t2.execute('Select count([R1SP]) AS ValidTotal from [' + str(T2) + '] where [cLyr] = ' + str(layerNo)).fetchone()
#
#
# print('TP01', ttSR[0])
# Data1 = round(ttSR[0] * 0.5, )
# print('TP02', Data1)
#
# print('\nTP03', stSR[0])
# Data2 = round(stSR[0] * 0.5, )
# print('TP04', Data2)
#
# t1.close()
# t2.close()
# -----------------------------------------------------------------------------#
last_t1 = None
dL1 = []
n2fetch = 100

# try:
#     if last_t1 is None:
#         t1.execute('SELECT * FROM ' + str(T1) + ' ORDER BY cLyr ASC')
#     else:
#         t1.execute('SELECT * FROM ' + str(T1) + ' WHERE id_col > ? ORDER BY cLyr ASC', last_t1)
#     data1 = t1.fetchmany(n2fetch)
#     print('\nDT01', len(data1))
#     # --------------- Re-assemble into dynamic buffer -----
#     if len(data1) != 0:
#         for result in data1:
#             result = list(result)
#             dL1.append(result)
#         last_t1 = data1[-1].id_col
#         print('\nDT02', dL1)
#     else:
#         print('[vTT] Process EOF reached...')
#         print('[vTT] Halting for 5 Minutes...')
#         time.sleep(3)
#
# except Exception as e:
#     print("[vTT Error] Tape Temp Data trickling...")  # , e)
#     time.sleep(2)
# t1.close()

# ---------------------------- Testing PLC Communication -----------------------------------#
# import snap7
#
# _Plc= snap7.client.Client()
# pCon = _Plc.connect('192.168.100.100', 0, 1)
# db_number, start_offset, bit_offset = 89, 0, 0
#
# start_offset1, bit_offset1 = 2, 0
# value, data = True, False  			# 1 = true | 0 = false
#
# start_address = 0  					# starting address
# r_length = 4  						# double word (4 Bytes)
# b_length = 1  						# boolean size = 1 Byte
# r_data = 52.4
# initialise = 0
#
#
# def readBool(db_number, start_offset, bit_offset):
# 	reading = pCon.db_read(db_number, start_offset, b_length)
# 	a = snap7.util.get_bool(reading, 0, bit_offset)
# 	print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
# 	return a
#
#
# def readReal(db_number, start_offset, bit_offset):
# 	reading = pCon.db_read(db_number, start_offset, r_length)
# 	a = snap7.util.get_real(reading, 0)
# 	# print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
# 	return a
#
#
# def readInteger(db_number, start_offset, bit_offset):
# 	reading = pCon.db_read(db_number, start_offset, r_length)
# 	a = snap7.util.get_int(reading, 0)
# 	print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
# 	return a
#
#
# def readString(db_number, start_offset, bit_offset):
# 	r_length = 2 # 16
# 	reading = pCon.db_read(db_number, start_offset, r_length)
# 	a = snap7.util.get_string(reading, 0)
# 	print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
# 	return a

# -----------------------------------------------------------
#
# def liveProductionRdy():
# 	# Allow connection once unless connection drops out -----
#     try:
#         sysRun = readBool(db_number,0, 0)  # System is runing
#         sysidl = readBool(db_number, 0, 1)  # System idling
#         sysrdy = readBool(db_number, 0, 2)  # System Ready
#         msctcp = readInteger(db_number, 2, 0)  # Machine State Code (msc)
#         won_NO = readString(db_number, 4, 0)  # Work Order Number
#
#
#     except Exception as err:
#         print(f"Exception Error: '{err}'")
#         sysidl = False
#         sysrdy = False
#
#         print('Sorry, PLC Host not responding, retry within seconds..')
#     return sysRun, sysidl, sysrdy, msctcp, won_NO

# sysRun, sysidl, sysrdy, msctcp, won_NO = liveProductionRdy()

# print('WON:', won_NO)

# ---------------------------------------
# # import packages
# import pandas as pd
#
# # reading csv file
# result = pd.read_csv('C:\\synchronousDOCS\\fossilfuels.csv')
# pd.set_option('display.max_columns', None)
# print('TP01',result.head(5))
# print()
#
# # randomly selecting columns
# sampled = result.sample(frac=0.3, axis='rows', random_state=9)
# print('TP02', sampled.head(5))
# from statistics import mean
#
# def sum_nestedlist(l):
#     total = 0
#     for j in range(len(l)):
#         if type(l[j]) == list:
#             total += sum_nestedlist(l[j])
#         else:
#             total += l[j]
#     return total
#
#
# l = [[2,5,3],[4,7,6,4],[3,4,6,7]]
# # total = sum_nestedlist(l)
# # print(total)
#
# for list_ in l:   # nested list iteration
#     if isinstance(list_[0], int):   # checking integer list type within nested list
#         print(mean(list_))          # printing integer list mean
#     else:                           # pass the list which is not integer type
#          pass

#
# import matplotlib.pyplot as plt
#
# def pan_factory(ax):
#     def on_press(event):
#         if event.inaxes != ax:
#             return
#         ax._pan_start = event.x, event.y, ax.get_xlim(), ax.get_ylim()
#
#     def on_release(event):
#         ax._pan_start = None
#         ax.figure.canvas.draw()
#
#     def on_motion(event):
#         if ax._pan_start is None or event.inaxes != ax:
#             return
#
#         x_press, y_press, xlim_start, ylim_start = ax._pan_start
#         dx = event.x - x_press
#         dy = event.y - y_press
#
#         # Transform the mouse movement into data coordinates
#         scale_x = (xlim_start[1] - xlim_start[0]) / ax.bbox.width
#         scale_y = (ylim_start[1] - ylim_start[0]) / ax.bbox.height
#
#         dx_data = dx * scale_x
#         dy_data = dy * scale_y
#
#         ax.set_xlim(xlim_start[0] - dx_data, xlim_start[1] - dx_data)
#         ax.set_ylim(ylim_start[0] - dy_data, ylim_start[1] - dy_data)
#         ax.figure.canvas.draw_idle()
#
#     ax.figure.canvas.mpl_connect('button_press_event', on_press)
#     ax.figure.canvas.mpl_connect('button_release_event', on_release)
#     ax.figure.canvas.mpl_connect('motion_notify_event', on_motion)
#     ax._pan_start = None
#
# # Example usage
# fig, ax = plt.subplots()
# ax.plot(range(10))
#
# # Assuming you already have zoom_factory(ax)
# # zoom_factory(ax)   # <== Already defined elsewhere
#
# # Enable pan:
# pan_factory(ax)
#
# plt.show()
# -----------------------------------------------------------------
import numpy as np
import numpy as np

# def align_arrays(arrs, mode="truncate", pad_value=0):
#     if mode == "truncate":
#         min_len = min(len(arr) for arr in arrs)
#         return [arr[:min_len] for arr in arrs]
#
#     elif mode == "pad":
#         max_len = max(len(arr) for arr in arrs)
#         return [np.pad(arr, (0, max_len - len(arr)),
#                        constant_values=pad_value) for arr in arrs]
#
#     else:
#         raise ValueError("mode must be 'truncate' or 'pad'")
#
#
# def truncate_to_shortest(x, *ys):
#     """
#     Truncate x and all y arrays to the shortest length.
#     """
#     min_len = min([len(x)] + [len(y) for y in ys])
#     x_trunc = x[:min_len]
#     # y_trunc = np.vstack[y[:min_len] for y in ys]
#     y_trunc = np.vstack([y[:min_len] for y in ys])
#     return x_trunc, y_trunc


# x =  np.arange(4)
# y1 = [[4, 6, 5, 7, 7], [6, 8, 3, 4, 6, 5], [5, 4, 2, 7, 7]]
# x, y = truncate_to_shortest(x, y1)
# print('X-Axis', x)
# print('Y-Axis', y)

# aligned = align_arrays([x, y1], mode="pad", pad_value=0)
#
# print([a.shape for a in aligned])  # → [(5,), (5,)]
# print(aligned[0] + aligned[1])

import numpy as np


# def padDT(x, ys, pad_value=0):
#     max_len = max(len(x), max(len(y) for y in ys))
#     # Pad x if shorter
#     x_padded = np.pad(x, (0, max_len - len(x)), constant_values=pad_value)
#     # Pad each y-series
#     ys_padded = np.vstack([np.pad(y, (0, max_len - len(y)), constant_values=pad_value) for y in ys])
#     return x_padded, ys_padded
# #
#
# x = np.arange(32)
# y1 = np.arange(28)      # shorter
# y2 = np.arange(32)      # full length
# y3 = np.arange(30)      # shorter
# ys = [y1, y2, y3]
#
# x_pad, ys_pad = padDT(x, ys, pad_value=0)
# print(x_pad.shape)  # (32,)
# print(ys_pad.shape) # (3, 32)
# print(ys_pad)
# print('\nTP1', ys_pad[0])
# print('\nTP2', ys_pad[1])

# layerN = range(0, 70)
# for layer in layerN:
#     time.sleep(3)
#     print(layer)
#     # layerN = layer
# import pandas as pd
# import matplotlib.pyplot as plt
#
# # Example DataFrame
# df = pd.DataFrame({
#     "valueA": ["X", "X", "Y", "Y", "Z", "X", "Y", "Z"],
#     "layerNo": [1, 2, 1, 2, 1, 1, 2, 2]
# })
#
# # Count occurrences of valueA per layer
# counts = pd.crosstab(df["layerNo"], df["valueA"])
#
# # Plot as line chart (one line per valueA)
# counts.plot(kind="line", marker="o")
#
# plt.title("Distribution of valueA across layerNo")
# plt.xlabel("Layer Number")
# plt.ylabel("Counts")
# plt.grid(True)
# plt.legend(title="valueA")
# plt.show()

mlis =[] # [2, 3, 8]
# mlis.append(5)
mlis.insert(0,8)
print('New List', mlis)

# Example 2: Using the pop() method
my_list = [1, 2, 3, 4, 5]
last_element = my_list.pop()
print(last_element)

try:
    import cupy as np
    GPU_ENABLED = True
except ImportError:
    import numpy as np
    GPU_ENABLED = False
# make numpy compatible with cupy API
np.asnumpy = lambda x: x
# import cudf

try:
    import cupy as cp
    import numpy as np
    GPU_ENABLED = False

    # Check if a CUDA device is available and usable
    try:
        num_gpus = cp.cuda.runtime.getDeviceCount()
        if num_gpus > 0:
            free_mem, total_mem = cp.cuda.runtime.memGetInfo()
            if free_mem / total_mem > 0.1:  # at least 10% free memory
                np = cp                # ✅ use CuPy as NumPy
                GPU_ENABLED = True
                print(f"✅ Using GPU (CuPy) | Free memory: {free_mem / 1e9:.2f} GB")
            else:
                print("⚠️ GPU memory low — falling back to CPU (NumPy).")
        else:
            print("⚠️ No GPU found — using CPU (NumPy).")
    except cp.cuda.runtime.CUDARuntimeError:
        print("⚠️ CUDA not available — using CPU (NumPy).")

except ImportError:
    import numpy as np
    GPU_ENABLED = False
    print("⚠️ CuPy not installed — using CPU (NumPy).")

# Always ensure np.asnumpy() is defined (for cross-compatibility)
if not hasattr(np, "asnumpy"):
    np.asnumpy = lambda x: x

# # NumPy array on CPU
# np_arr = np.arange(5)
# print("NumPy:", type(np_arr))
#
# # Convert to CuPy array (on GPU)
# cp_arr = np.asarray(np_arr)
# print("CuPy:", type(cp_arr))
#
# # Convert back to NumPy
# np_arr2 = cp_arr.get()
# print("Back to NumPy:", type(np_arr2))
#
# # works on GPU if available, otherwise CPU
# x = np.arange(10)
# y = np.sin(x)
#
# # convert back to CPU safely
# y_cpu = np.asnumpy(y)
# print(type(y_cpu))

# --------------------------------------------------------------------------[]
#
# import cupy
# print(cupy.Series([1, 2, 3]))

# # Rolling mean with min_periods=1
# gdf_rolling = gdf.rolling(window=s_fetch, min_periods=1).mean()
#
# # Optionally convert back to pandas
# pdf_rolling = gdf_rolling.to_pandas()

# -------------------------------------------------------------------Test @ Jit Numba --------#
# import numpy as np
# import matplotlib.pyplot as plt
# from numba import cuda
# NUMBA_CUDA_USE_NVIDIA_BINDING = 0
# print(cuda.is_available())
#
# # Generate synthetic time series data
# N = 1000
# np.random.seed(0)
# signal = np.sin(np.linspace(0, 20, N)) + np.random.normal(0, 0.3, N).astype(np.float32)
#
# # Rolling window size
# window = 25
# half_window = window // 2
#
# # Output arrays
# rolling_mean = np.zeros_like(signal)
# rolling_std = np.zeros_like(signal)
#
# # CUDA kernel
# @cuda.jit
# def rolling_stats_kernel(data, mean_out, std_out, window):
#     i = cuda.grid(1)
#     N = data.shape[0]
#     half_w = window // 2
#
#     if i < N:
#         sum_ = 0.0
#         count = 0
#         for j in range(i - half_w, i + half_w + 1):
#             if 0 <= j < N:
#                 sum_ += data[j]
#                 count += 1
#
#         mean = sum_ / count
#         mean_out[i] = mean
#
#         # Compute standard deviation
#         sum_sq = 0.0
#         for j in range(i - half_w, i + half_w + 1):
#             if 0 <= j < N:
#                 sum_sq += (data[j] - mean) ** 2
#
#         std_out[i] = (sum_sq / count) ** 0.5
#
# # Move data to device
# d_signal = cuda.to_device(signal)
# d_mean = cuda.device_array_like(signal)
# d_std = cuda.device_array_like(signal)
#
# # Launch kernel
# threads_per_block = 128
# blocks = (N + threads_per_block - 1) // threads_per_block
#
# rolling_stats_kernel[blocks, threads_per_block](d_signal, d_mean, d_std, window)
#
# # Copy back to host
# d_mean.copy_to_host(rolling_mean)
# d_std.copy_to_host(rolling_std)
#
# # Plotting
# x = np.arange(N)
# plt.figure(figsize=(12, 6))
# plt.plot(x, signal, label='Original Signal', alpha=0.5)
# plt.plot(x, rolling_mean, label='Rolling Mean', color='orange')
# plt.fill_between(x, rolling_mean - rolling_std, rolling_mean + rolling_std,
#                  color='orange', alpha=0.2, label='Rolling Std Dev')
# plt.title("Rolling Mean and Standard Deviation (Window = {})".format(window))
# plt.legend()
# plt.grid(True)
# plt.xlabel("Time")
# plt.ylabel("Signal")
# plt.tight_layout()
# plt.show()

# ------------------------------------------------------------------------------------------
#
# import pandas as pd
# import numpy as np
#
# import cupy as cp
# from cupyx.scipy.ndimage import uniform_filter1d
#
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import tkinter as tk
#
# # ----- Step 1: Simulate SQL data as a DataFrame -----
# # Simulated data: 300 rows, 10 columns
# np.random.seed(42)
# df = pd.DataFrame(np.random.randn(300, 10), columns=[f'col{i}' for i in range(10)])
#
# # ----- Step 2: Convert to CuPy -----
# data_np = df.to_numpy().astype(np.float32)   # NumPy first
# data_cp = cp.asarray(data_np)                # Then to CuPy
#
# window = 30
#
# # ----- Step 3: Compute rolling mean & std (centered window) -----
# # Using uniform_filter1d for efficient rolling mean
# mean_cp = uniform_filter1d(data_cp, size=window, axis=0, mode='reflect')
# # Compute rolling std: std(x) = sqrt(mean(x^2) - mean(x)^2)
# squared_cp = uniform_filter1d(data_cp ** 2, size=window, axis=0, mode='reflect')
# std_cp = cp.sqrt(squared_cp - mean_cp ** 2)
#
# # Transfer results back to CPU
# mean_np = cp.asnumpy(mean_cp)
# std_np = cp.asnumpy(std_cp)
#
# # ----- Step 4: Plot in Tkinter -----
# def plot_in_tkinter():
#     root = tk.Tk()
#     root.title("CuPy Rolling Mean/Std Plot (10 Columns)")
#
#     fig, axs = plt.subplots(5, 2, figsize=(10, 8), constrained_layout=True)
#     axs = axs.flatten()
#
#     x = np.arange(len(mean_np))
#
#     for i in range(10):
#         axs[i].plot(x, mean_np[:, i], label=f'Mean col{i}', color='blue')
#         axs[i].fill_between(x,
#                             mean_np[:, i] - std_np[:, i],
#                             mean_np[:, i] + std_np[:, i],
#                             alpha=0.3,
#                             color='blue',
#                             label='±1 Std Dev')
#         axs[i].set_title(f'Column {i}')
#         axs[i].legend()
#         axs[i].grid(True)
#
#     # Embed the plot into Tkinter
#     canvas = FigureCanvasTkAgg(fig, master=root)
#     canvas.draw()
#     canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
#
#     root.mainloop()
#
# # ----- Run the app -----
# plot_in_tkinter()
import numpy as np
import statistics as st
# ------------------------------------------------
list1 = [3.2,2.1,5.0,6.2]
list2 = [4,2,6,5]
list3 = [3,5,4,7]
list4 = [4,5,2,3]
print('R1:', np.mean(list1))
print('R2:', np.mean(list2))
print('R3:', np.mean(list3))
print('R4:', np.mean(list4))
print('Total X:', np.mean(list1) + np.mean(list2) + np.mean(list3) + np.mean(list4))
print('Total Mean of Means:', np.mean([np.mean(list1), np.mean(list2), np.mean(list3), np.mean(list4)]))

print('Total Mean of_Means:', np.mean([list1, list2, list3, list4]))
print('Total Mean of_Stds:', np.std([list1, list2, list3, list4]))


list = [420.2, 425.13333, 415.73334, 422.60004]
print('TP01', np.mean(list))
print('TP01', st.mean(list))
