# This script is called in from Main program to load SQL execution syntax command and return a list in LisDat
# Author: Dr Labs, RB
from collections import deque
from itertools import count
from datetime import datetime, timedelta
import time
import timeit
import os


last_t1 = None
st_id = 0
dL1 = []                                              # SQL start index unless otherwise stated by the index tracker!


def sqlExec(daq, nGZ, grp_step, T1, fetch_no):
    global last_t1
    """
    NOTE:
    """
    # idx = str(idx)                                    # convert Query Indexes to string concatenation
    t1 = daq.cursor()

    n2fetch = int(nGZ)
    group_step = int(grp_step)
    fetch_no = int(fetch_no)
    if group_step == 1:
        slideType = 'Smooth Edge'
    else:
        slideType = 'Non-overlapping'

    print('\n[TG] SAMPLE SIZE:', nGZ, '| SLIDE MODE:', slideType, '| BATCH:', fetch_no)
    print('=' * 60)
    # --------------- Re-assemble into dynamic buffer -----
    if group_step == 1:
        if len(dL1) >= n2fetch:
            del dL1[:n2fetch - 1]
            n2fetch = int(nGZ) - 1

    elif group_step == 2:
        if len(dL1) == (n2fetch * 2):
            del dL1[:n2fetch]
            n2fetch = int(nGZ)
    else:
        print('Undefined Window Group Slide')
    # ------------- Consistency Logic ensure list is filled with predetermined elements --------------
    try:
        if last_t1 is None:
            t1.execute('SELECT * FROM ' + str(T1) + ' ORDER BY cLayer ASC')
        else:
            t1.execute('SELECT * FROM ' + str(T1) + ' WHERE id_col > ? ORDER BY LyIDc ASC', last_t1)
        data1 = t1.fetchmany(n2fetch)

        # --------------- Re-assemble into dynamic buffer -----
        if len(data1) != 0:
            for result in data1:
                result = list(result)
                dL1.append(result)
            last_t1 = data1[-1].id_col
        else:
            print('[TG] Process EOF reached...')
            time.sleep(30)

    except Exception as e:
        print("[TG] Data trickling on IDX#:", last_t1)  # , e)
        time.sleep(2)

    t1.close()

    return dL1
# -----------------------------------------------------------------------------------[Dr Labs]
