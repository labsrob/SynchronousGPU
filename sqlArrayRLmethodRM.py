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
dataList0, dL3 = [], []


def sqlExec(daq, nGZ, grp_step, T3):
    """
    NOTE:
    """
    t1 = daq.cursor()

    group_step = int(grp_step)
    fetch_no = int(len(dataList0))  # int(nGZ) + 3
    print('\nDefault Sample Size:', fetch_no, group_step, '\n')

    # ------------- Consistency Logic ensure list is filled with predetermined elements --------------
    if len(dL3) < (int(nGZ) - 1):
        n2fetch = int(nGZ)  # fetch initial specified number
        print('\nRows to Fetch:', n2fetch)

    elif group_step == 1 and len(dL3) >= int(nGZ):
        print('\nSINGLE STEP SLIDE')
        print('=================')
        n2fetch = (int(nGZ) + fetch_no)  # fetch just one line to on top of previous fetch
        print('\nRows to Fetch:', n2fetch)

    # ------------------------------------------------------------------------------------[]
    tot = int(nGZ) + fetch_no
    print('\nTotal to Fetch:', tot)
    # ------------------------------------------------------------------------------------[]

    data3 = t1.execute('SELECT TOP (' + str(n2fetch) + ') * FROM ' + str(T3)).fetchall()
    # data3 = t1.execute('SELECT TOP (' + str(fetch) + ') * FROM ' + str(T3)+ ' ORDER BY cLayer').fetchmany(fetch)
    # data3 = t1.execute('SELECT * FROM ' + str(T3)).fetchmany(n2fetch)
    print('Cumulative RMB:', len(dL3), '\n')
    if len(data3) != 0:
        for result in data3:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dL3.append(result)
            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            if group_step > 1 and len(dL3) >= tot and fetch_no <= 31:  # Retain group and step size
                del dL3[0:(len(dL3) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 32:  # After windows limit (move)
                del dL3[0:(len(dL3) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dL3) >= tot and fetch_no <= 31:
                del dL3[0:(len(dL3) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 32:  # After windows limit (move)
                del dL3[0:(len(dL3) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass
            # print('RMP Data Length:', len(dL3))

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    t1.close()  # close cursor

    return dL3
# -----------------------------------------------------------------------------------[Dr Labs]
