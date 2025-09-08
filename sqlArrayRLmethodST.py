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
dL1, dL2 = [], []
st_id = 0                                           # SQL start index unless otherwise stated by the index tracker!


def sqlExec(daq, nGZ, grp_step, T1, T2):
    """
    NOTE:
    """
    t1 = daq.cursor()
    group_step = int(grp_step)                      # group size/ sample sze
    n2fetch = int(nGZ) # + 2

    # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
    if group_step == 1:
        if len(dL1) < int(nGZ) or len(dL2) < int(nGZ):
            n2fetch = int(nGZ)  # fetch initial specified number
            print('1st Trip:', n2fetch)

        elif len(dL1) == int(nGZ):
            n2fetch = int(nGZ)  # - len(dL1)
            print('2nd Trip:', n2fetch)

        else:
            dL1.pop(0)
            dL2.pop(0)
            n2fetch = 1

    elif group_step == 2:
        if len(dL1) <= int(nGZ) or len(dL2) <= int(nGZ):
            n2fetch = int(nGZ)
        else:
            del dL1[:(len(dL1) - 1)]
            del dL2[:(len(dL2) - 1)]
            n2fetch = int(nGZ) - 1
        print('\nRows to Fetch on Discrete:', n2fetch)
    else:
        n2fetch = int(nGZ)
    print('\nTTA:', n2fetch, len(dL1), dL1)
    print('TTB:', n2fetch, len(dL2), dL2)

    # ------------------------------------------------------------------------------------[]
    # data1 = daq1.execute('SELECT * FROM ' + rT1).fetchmany(n2fetch)
    data1 = t1.execute('SELECT * FROM ' + str(T1) + ' ORDER BY tStamp').fetchmany(n2fetch)
    if len(data1) != 0:
        for result in data1:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dL1.append(result)

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    # t1.close()

    # ------------------------------------------------------------------------------------[]
    # data2 = t1.execute('SELECT TOP ('+ str(n2fetch) +') * FROM ' + str(T2)).fetchall()
    data2 = t1.execute('SELECT * FROM ' + str(T2) + ' ORDER BY tStamp').fetchmany(n2fetch)
    print('TT2', len(data2), data2)
    if len(data2) != 0:
        for result in data2:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            # if len(dL2) > n2fetch:  # purgatory
            #     dL2.pop(0)
            dL2.append(result)

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    # t1.close()

    return dL1, dL2
# -----------------------------------------------------------------------------------[Dr Labs]
