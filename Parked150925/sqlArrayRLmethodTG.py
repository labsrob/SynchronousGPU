# This script is called in from Main program to load SQL execution syntax command and return a list in LisDat
# Author: Dr Labs, RB
from collections import deque
from itertools import count
from datetime import datetime, timedelta
import time
import timeit
import os

UseRowIndex = True
idx = count()
now = datetime.now()

dataList0 = []
Idx, Idx, dL = [], [], []
st_id = 0                                           # SQL start index unless otherwise stated by the index tracker!


def sqlExec(conn, nGZ, grp_step, sCentr, T1):
    """
    NOTE:
    """
    t1 = conn.cursor()                              # convert Query Indexes to string concatenation

    group_step = int(grp_step)                      # group size/ sample sze
    n2fetch = int(nGZ)                             # dbfreq = TODO look into any potential conflict
    print('\nDefault Sample Size:', n2fetch, group_step, '\n')

    # ------------- Consistency Logic ensure list is filled with predetermined elements --------------
    if group_step == 1:
        if len(dL) < n2fetch:
            fetch = n2fetch  # fetch initial specified number

        elif len(dL) == int(nGZ):
            fetch = n2fetch  # - len(dL1)
        else:
            dL.pop(0)
            fetch = 10

    elif group_step == 2:
        if len(dL) <= n2fetch:
            fetch = n2fetch
        elif len(dL) == n2fetch:
            fetch = n2fetch - 1
        else:
            dL.pop(0)
            fetch = n2fetch + 1
    else:
        fetch = n2fetch
    print('\nCumulative RM:', len(dL), dL)

    # ------------------------------------------------------------------------------------[]
    # data1 = daq1.execute('SELECT * FROM ' + rT1).fetchmany(n2fetch)
    data = t1.execute('SELECT * FROM ' + str(T1) + ' WHERE sCentre = ' + str(sCentr)).fetchmany(fetch)
    if len(data) != 0:
        for result in data:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dL.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dL) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dL[0:(len(dL) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dL[0:(len(dL) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dL) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dL[0:(len(dL) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dL[0:(len(dL) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass
        # print("Step List1:", len(dL1), dL1)       FIXME:
    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    daq.close()

    return dL
# -----------------------------------------------------------------------------------[Dr Labs]
