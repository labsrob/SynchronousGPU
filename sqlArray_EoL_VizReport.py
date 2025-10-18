# This script is called in from Main program to load SQL execution syntax command and return a list in LisDat
# Author: Dr Labs, RB
from collections import deque
from itertools import count
from datetime import datetime, timedelta
import time

last_t1 = None
last_t2 = None
last_t3 = None
last_t4 = None

st_id = 0
dL1, dL2, dL3, dL4 = [], [], [], []                                              # SQL start index unless otherwise stated by the index tracker!
# Plot visualisation for EoL Report only-------

def dnv_sqlExec(daq, nGZ, grp_step, T1, T2, T3, T4, fetch_no):
    global last_t1, last_t2, last_t3, last_t4
    """
    NOTE:
    """
    # idx = str(idx)                                    # convert Query Indexes to string concatenation
    t1, t2, t3, t4 = daq.cursor(), daq.cursor(), daq.cursor(), daq.cursor()

    n2fetch = int(nGZ)
    group_step = int(grp_step)
    fetch_no = int(fetch_no)                            # dbfreq = TODO look into any potential conflict
    if group_step == 1:
        slideType = 'Smooth Edge'
    else:
        slideType = 'Non-overlapping'

    print('\n[EoL Viz] SAMPLE SIZE:', nGZ, '| SLIDE Mode:', slideType, '| BATCH:', fetch_no)
    print('='*60)

    # ------------- Consistency Logic ensure list is filled with predetermined elements --------------
    try:
        if last_t1 is None:
            t1.execute('SELECT * FROM ' + str(T1))
        else:
            t1.execute('SELECT * FROM ' + str(T1) + ' WHERE id_col > ? ORDER BY cLyr ASC', last_t1)
        data1 = t1.fetchmany(n2fetch)

        # --------------- Re-assemble into dynamic buffer -----
        if len(data1) != 0:
            for result in data1:
                result = list(result)
                dL1.append(result)
            if last_t1 is None:
                pass
            else:
                last_t1 = data1[-1].id_col

        else:
            print('[vTT] Process EOF reached...')
            print('[vTT] Halting for 5 Minutes...')
            time.sleep(3)

    except Exception as e:
        print("[vTT Error] Data is trickling...")  # , e)
        time.sleep(2)
    t1.close()

    # # ------------------------------------------------------------------------------------[]
    try:
        if last_t2 is None:
            t2.execute('SELECT * FROM ' + str(T2))
        else:
            t2.execute('SELECT * FROM ' + str(T2) + ' WHERE id_col > ? ORDER BY cLyr ASC', last_t2)
        data2 = t2.fetchmany(n2fetch)

        # --------------- Re-assemble into dynamic buffer -----
        if len(data2) != 0:
            for result in data2:
                result = list(result)
                dL2.append(result)
            if last_t2 is None:
                pass
            else:
                last_t2 = data2[-1].id_col
        else:
            print('[vST] Process EOF reached...')
            print('[vST] Halting for 5 Minutes...')
            time.sleep(3)

    except Exception as e:
        print("[vST Error] Data is trickling...")  # , e)
        time.sleep(2)
    t2.close()

    # ------------------------------------------------------------------------------------[]
    try:
        if last_t3 is None:
            t3.execute('SELECT * FROM ' + str(T3))
        else:
            t3.execute('SELECT * FROM ' + str(T3) + ' WHERE id_col > ? ORDER BY cLyr ASC', last_t3)
        data3 = t3.fetchmany(n2fetch)

        # --------------- Re-assemble into dynamic buffer -----
        if len(data3) != 0:
            for result in data3:
                result = list(result)
                dL3.append(result)
            if last_t3 is None:
                pass
            else:
                last_t3 = data3[-1].id_col
        else:
            print('[vTG] Process EOF reached...')
            print('[vTG] Halting for 5 Minutes...')
            time.sleep(3)

    except Exception as e:
        print("[vTG Error] Data is trickling...")  # , e)
        time.sleep(2)
    t3.close()

    # ------------------------------------------------------------------------------------[]
    try:
        if last_t4 is None:
            t4.execute('SELECT * FROM ' + str(T4))
        else:
            t4.execute('SELECT * FROM ' + str(T4) + ' WHERE id_col > ? ORDER BY cLyr ASC', last_t4)
        data4 = t4.fetchmany(n2fetch)

        # --------------- Re-assemble into dynamic buffer -----
        if len(data4) != 0:
            for result in data4:
                result = list(result)
                dL4.append(result)
            if last_t4 is None:
                pass
            else:
                last_t4 = data4[-1].id_col
        else:
            print('[vWS] Process EOF reached...')
            print('[vWS] Halting for 5 Minutes...')
            time.sleep(3)

    except Exception as e:
        print("[vWS Error] Data is trickling...")  # , e)
        time.sleep(2)

    t4.close()

    return dL1, dL2, dL3, dL4


# -------------------------------------------------------------------------------------------------------[XXXXXXX]
