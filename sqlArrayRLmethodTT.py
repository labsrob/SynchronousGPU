# This script is called in from Main program to load SQL execution syntax command and return a list in LisDat
# Author: Dr Labs, RB
from collections import deque
from itertools import count
from datetime import datetime, timedelta
import time
import timeit
import os

last_t1 = None
last_t2 = None
st_id = 0
dL1, dL2 = [], []                                              # SQL start index unless otherwise stated by the index tracker!


def sqlExec(daq, nGZ, grp_step, T1, T2, fetch_no):
    global last_t1, last_t2
    """
    NOTE:
    """
    # idx = str(idx)                                    # convert Query Indexes to string concatenation
    t1, t2 = daq.cursor(), daq.cursor()

    n2fetch = int(nGZ)
    group_step = int(grp_step)
    fetch_no = int(fetch_no)                            # dbfreq = TODO look into any potential conflict
    print('\nSAMPLE SIZE:', nGZ, '| SLIDE STEP:', group_step, '| BATCH:', fetch_no)

    # ------------- Consistency Logic ensure list is filled with predetermined elements --------------
    try:
        if last_t1 is None:
            t1.execute('SELECT * FROM ' + str(T1) + ' ORDER BY cLayer ASC')
        else:
            t1.execute('SELECT * FROM ' + str(T1) + ' WHERE tStamp > ? ORDER BY cLayer ASC', last_t1)

        data1 = t1.fetchmany(n2fetch)

        # --------------- Re-assemble into dynamic buffer -----
        if len(data1) != 0:
            for result in data1:
                result = list(result)
                dL1.append(result)
            last_t1 = data1[-1].tStamp
        else:
            print('[TT_1] Process EOF reached...')
            print('[TT_1] Halting for 5 Minutes...')
            time.sleep(300)

    except Exception as e:
        print("[TT_1] Ramp Count Data trickling...")  # , e)
        time.sleep(2)

    t1.close()

    # ------------------------------------------------------------------------------------[]
    try:
        if last_t2 is None:
            t2.execute('SELECT * FROM ' + str(T2) + ' ORDER BY cLayer ASC')
        else:
            t2.execute('SELECT * FROM ' + str(T2) + ' WHERE tStamp > ? ORDER BY cLayer ASC', last_t2)

        data2 = t2.fetchmany(n2fetch)

        # --------------- Re-assemble into dynamic buffer -----
        if len(data2) != 0:
            for result in data2:
                result = list(result)
                dL2.append(result)
            last_t2 = data2[-1].tStamp
        else:
            print('[TT_2] Process EOF reached...')
            print('[TT_2] Halting for 5 Minutes...')
            time.sleep(300)

    except Exception as e:
        print("[TT_2] Ramp Count Data trickling...")  # , e)
        time.sleep(2)

    t2.close()

    return dL1, dL2
    # -----------------------------------------------------------------------------------[Dr Labs]
