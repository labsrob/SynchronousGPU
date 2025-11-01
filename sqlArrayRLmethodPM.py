# This script is called in from Main program to load SQL execution syntax command and return a list in LisDat
# Author: Dr Labs, RB
# -------------------------------------------------------------------------------------------------------------
from collections import deque
from itertools import count
from datetime import datetime, timedelta
import time
import timeit
import os
last_t1 = None
last_t2 = None
last_t3 = None

st_id = 0
dL1, dL2, dL3, dL4 = [], [], [], []                                              # SQL start index unless otherwise stated by the index tracker!
# ------------------------------------ MONITORING TAB VIZ -----------------------#

def dnv_sqlExec(daq, nGZ, grp_step, T1, T2, T3, fetch_no):
    global last_t1, last_t2, last_t3
    """
    NOTE:
    """
    # idx = str(idx)                                    # convert Query Indexes to string concatenation
    t1, t2, t3 = daq.cursor(), daq.cursor(), daq.cursor()

    n2fetch = int(nGZ)
    group_step = int(grp_step)
    fetch_no = int(fetch_no)                            # dbfreq = TODO look into any potential conflict
    print('\n[PM] SAMPLE SIZE:', nGZ, '| SLIDE STEP:', group_step, '| BATCH:', fetch_no)

    # ------------- Consistency Logic ensure list is filled with predetermined elements --------------
    try:
        if last_t1 is None:
            t1.execute('SELECT * FROM ' + str(T1) + ' ORDER BY cLayer ASC')         # GEN_
        else:
            t1.execute('SELECT * FROM ' + str(T1) + ' WHERE id_col > ? ORDER BY cLayer ASC', last_t1)

        data1 = t1.fetchmany(n2fetch)

        # --------------- Re-assemble into dynamic buffer -----
        if len(data1) != 0:
            for result in data1:
                result = list(result)
                dL1.append(result)
            last_t1 = data1[-1].id_col
        else:
            print('[GEN] Process EOF reached...')
            time.sleep(300)

    except Exception as e:
        print("[mGEN_] Data trickling...")  # , e)
        time.sleep(2)

    t1.close()

    # ------------------------------------------------------------------------------------[]
    try:
        if last_t2 is None:
            t2.execute('SELECT * FROM ' + str(T2) + ' ORDER BY cLayer ASC')     # RP_1
        else:
            t2.execute('SELECT * FROM ' + str(T2) + ' WHERE id_col > ? ORDER BY cLayer ASC', last_t2)

        data2 = t2.fetchmany(n2fetch)

        # --------------- Re-assemble into dynamic buffer -----
        if len(data2) != 0:
            for result in data2:
                result = list(result)
                dL2.append(result)
            last_t2 = data2[-1].id_col
        else:
            print('[mTT] Process EOF reached...')
            time.sleep(300)

    except Exception as e:
        print("[mRP1] Data trickling...")  # , e)
        time.sleep(2)

    t2.close()

    # ------------------------------------------------------------------------------------[]
    try:
        if last_t3 is None:
            t3.execute('SELECT * FROM ' + str(T3) + ' ORDER BY cLayer ASC')  # RP_2
        else:
            t3.execute('SELECT * FROM ' + str(T3) + ' WHERE id_col > ? ORDER BY cLayer ASC', last_t3)

        data3 = t3.fetchmany(n2fetch)

        # --------------- Re-assemble into dynamic buffer -----
        if len(data3) != 0:
            for result in data3:
                result = list(result)
                dL3.append(result)
            last_t3 = data3[-1].id_col
        else:
            print('[mRP2] Process EOF reached...')
            time.sleep(300)

    except Exception as e:
        print("[mRP2] Data trickling...")  # , e)
        time.sleep(2)

    t3.close()
    # ------------------------------------------------------------------------------------[]

    return dL1, dL2, dL3
# -------------------------------------------------------------------------------------------------------------[XXXXXXX]

