# This script is called in from Main program to load SQL execution syntax command and return a liRP in LisDat
# Author: Dr Labs, RB
# --------------------------------------------------------------------------------------------------------------------[]
import time
import snap7
import cupy as cp
from snap7.util import get_int
from collections import deque
import OPC_UA_settings as ld

configP = 'C:\\synchronousGPU\\INI_Files\\checksumError.ini'
ip, name, User, Pswd = ld.load_configPLC(configP)
ip = '192.168.100.100'

# ---------------------------------------------------------------------------------------------------[]
# Obtain PLC volatile data and computes mean/std per channel (column)
# prevent memory ballooning (due to deque(maxlen=...), runs efficiently on GPU, real-time performance.
""" PERFORMANCE PROFILE
| Operation        | GPU load    | CPU load   | Memory growth | Comment           |
| ---------------- | ----------- | ---------- | ------------- | ----------------- |
| PLC reads        | low         | low        | constant      | bounded by deque  |
| Rolling mean/std | small burst | negligible | constant      | safe for 10 Hz    |
| Printing         | moderate    | moderate   | none          | batching on deque |
| Author: Robert Labs
"""

# ---------------------------------------------------------------------------------------------------[]

def connect_plc(ip, rack=0, slot=1):
    client = snap7.client.Client()
    client.connect(ip, rack, slot)
    return client


def read_block(client, db_number, num_ints=17):
    size = num_ints * 2
    raw = client.db_read(db_number, 0, size)
    return [get_int(raw, i * 2) for i in range(num_ints)]


def plcExec(ip, db_number, sample_size, batch_No, rate_hz=10, window=5):
    delay = 1.0 / rate_hz
    client = connect_plc(ip)

    # Using deque with maxlen to prevent balloon effect
    data = deque(maxlen=sample_size)  # discard old samples

    print(f"[Live RP] Collecting {sample_size} samples from DB{db_number}, Batch #{batch_No}")

    # Precompute rolling kernel once
    kernel = cp.ones(window) / window

    try:
        for i in range(sample_size):
            vals = read_block(client, db_number)
            timestamp = time.time()
            data.append([timestamp] + vals)
            print(f"Sample {i + 1}/{sample_size}: {vals}")
            time.sleep(delay)

            # Compute rolling mean/std on GPU once window is full
            if len(data) >= window:
                data_gpu = cp.asarray(data)
                numeric_gpu = data_gpu[:, 2:]  # exclude timestamp & Layer column

                roll_mean = cp.apply_along_axis(
                    lambda col: cp.convolve(col, kernel, mode='valid'),
                    0, numeric_gpu
                )
                roll_std = cp.apply_along_axis(
                    lambda col: cp.sqrt(
                        cp.convolve(col ** 2, kernel, mode='valid')
                        - cp.convolve(col, kernel, mode='valid') ** 2
                    ),
                    0, numeric_gpu
                )

                # convert entire row instead of forcing float()
                mean_last = cp.asnumpy(roll_mean[-1])
                std_last = cp.asnumpy(roll_std[-1])
                print(f"[GPU Rolling Stats @Sample {i + 1}]")
                print(f"  Mean: {mean_last}")
                print(f"  Std : {std_last}")


    except Exception as e:
        print(f"[Error] {e}")

    finally:
        client.disconnect()
        client.destroy()
        print("[Live RP] Done.")
        print('\nTP01-Mean', list(mean_last))
        print('\nTP01-Std', list(std_last))

    return list(mean_last), list(std_last)


# plcExec(ip, 151, 30, 1, 10, 30)