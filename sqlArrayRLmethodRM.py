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
dataList0, dL = [], []


def sqlExec(daq, nGZ, grp_step, T3):
    """
    NOTE:
    """
    t1 = daq.cursor()
    group_step = int(grp_step)                      # group size/ sample sze
    n2fetch = int(nGZ) # + 2
    print('\nDefault Sample Size:', n2fetch, group_step, '\n')

    # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
    if group_step == 1:
        print('\nTTA:', len(dL), dL)
        if len(dL) < int(nGZ):
            n2fetch = int(nGZ)  # fetch initial specified number

        elif len(dL) == int(nGZ):
            n2fetch = int(nGZ)  # - len(dL1)

        else:
            # dL.pop(0)
            n2fetch = 10
            print('\nTTB:', len(dL), dL)

    elif group_step == 2:
        if len(dL) <= int(nGZ):
            n2fetch = int(nGZ)
        else:
            n2fetch = int(nGZ) - 1
        print('\nRows to Fetch on Discrete:', n2fetch)
    else:
        n2fetch = int(nGZ)
    print('Fetch RMP samples:', n2fetch)
    # ------------------------------------------------------------------------------------[]
    # data3 = t1.execute('SELECT TOP ('+ str(n2fetch) +') * FROM ' + str(T3)).fetchall()
    data3 = t1.execute('SELECT * FROM ' + str(T3) + ' ORDER BY cLayer').fetchmany(n2fetch)
    print('RMP', len(data3), data3)
    if len(data3) != 0:
        for result in data3:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            # if len(dL) > n2fetch:
            #     dL.pop(0)
            dL.append(result)
            # print('Round Trip:', idx)

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    # t1.close()

    return dL
# -----------------------------------------------------------------------------------[Dr Labs]
