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
Idx, dL = [], []
st_id = 0                                           # SQL start index unless otherwise stated by the index tracker!


def sqlExec(conn, nGZ, grp_step, T1):
    """
    NOTE:
    """
    t1 = conn.cursor()                        # convert Query Indexes to string concatenation

    group_step = int(grp_step)                # group size/ sample sze
    n2fetch = int(nGZ)                        # dbfreq = TODO look into any potential conflict

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
            # dL.pop(0)
            fetch = n2fetch + 1
    else:
        fetch = n2fetch
    print('\nCumulative VMP:', len(dL), dL)

    # ------------------------------------------------------------------------------------[]
    data1 = t1.execute('SELECT * FROM ' + str(T1) + ' ORDER BY cLayer').fetcall()
    # data1 = t1.execute('SELECT * FROM ' + str(T1)).fetchmany(fetch)
    if len(data1) != 0:
        for result in data1:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dL.append(result)
        # print("Step List1:", len(dL1), dL1)       FIXME:

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    t1.close()

    return dL
# -----------------------------------------------------------------------------------[Dr Labs]
