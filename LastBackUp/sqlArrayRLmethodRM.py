# This script is called in from Main program to load SQL execution syntax command and return a list in LisDat
# Author: Dr Labs, RB
from collections import deque
from itertools import count
from datetime import datetime, timedelta
import time
import timeit
import os


last_ts = None
st_id = 0
dL = []                                              # SQL start index unless otherwise stated by the index tracker!


def sqlExec(daq, nGZ, grp_step, T1, fetch_no):
    global last_ts
    """
    NOTE:
    """
    t1 = daq.cursor()

    n2fetch = int(nGZ)
    group_step = int(grp_step)
    fetch_no = int(fetch_no)
    if group_step == 1:
        slideType = 'Smooth Edge'
    else:
        slideType = 'Non-overlapping'

    print('\n[cRC] SAMPLE SIZE:', nGZ, '| SLIDE MODE:', slideType, '| BATCH:', fetch_no)
    print('=' * 60, '\n')
    # ------------- Consistency Logic ensure list is filled with predetermined elements --------------
    try:
        if last_ts is None:
            t1.execute('SELECT * FROM ' + str(T1) + ' ORDER BY cLayer ASC')
        else:
            t1.execute('SELECT * FROM ' + str(T1) + ' WHERE id_col > ? ORDER BY cLayer ASC', last_ts)
        data1 = t1.fetchmany(n2fetch)
        # ---- Re-assemble into dynamic buffer -----[]
        if len(data1) != 0:
            for result in data1:
                result = list(result)
                dL.append(result)
            last_ts = data1[-1].id_col
        else:
            print('[cRC] Process EOF reached...')
            print('[cRC] Halting for 30 sec...')
            time.sleep(30)

    except Exception as e:
        print("[cRC] Data trickling on IDX#:", last_ts)  # , e)
        time.sleep(2)

    t1.close()

    return dL
# -----------------------------------------------------------------------------------[Dr Labs]

