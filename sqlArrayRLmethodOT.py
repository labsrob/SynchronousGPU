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
Idx, dOT = [], []
st_id = 0                                               # SQL start index unless otherwise tracker!


def sqlexec(nGZ, grp_step, daq, rT1, fetch_no):
    """
    NOTE:
    """
    # idx = str(idx)                                    # convert Query Indexes to string concatenation

    group_step = int(grp_step)                          # group size/ sample sze
    fetch_no = int(fetch_no)                            # dbfreq = TODO look into any potential conflict
    print('\nSAMPLE SIZE:', nGZ, '| SLIDE STEP:', int(grp_step), '| FETCH CYCLE:', fetch_no)

    # ------------- Consistency Logic ensure list is filled with predetermined elements --------------
    if len(dOT) < (nGZ - 1):
        n2fetch = nGZ                                   # fetch initial specified number
        print('\nRows to Fetch:', n2fetch)
        print('Processing SQL Row #:', int(idx) + fetch_no + 1, 'to', (int(idx) + fetch_no + 1) + n2fetch)

    elif group_step == 1 and len(dOT) >= nGZ:
        print('\nSINGLE STEP SLIDE')
        print('=================')
        n2fetch = (nGZ + fetch_no)                      # fetch just one line to on top of previous fetch
        idxA = int(idx) + (((fetch_no + 1) - 2) * nGZ) + 1
        if len(Idx) > 1:
            del Idx[:1]
        Idx.append(idxA)
        print('Processing SQL Row #:', 'T1:', idxA)

    # ------------------------------------------------------------------------------------[]
    # data1 = daq1.execute('SELECT * FROM ' + rT1).fetchmany(n2fetch)
    data1 = daq.execute('SELECT * FROM ' + rT1).fetchmany(n2fetch)
    if len(data1) != 0:
        for result in data1:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dOT.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dOT) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dOT[0:(len(dOT) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dOT[0:(len(dOT) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dOT) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dOT[0:(len(dOT) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dOT[0:(len(dOT) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass
        # print("Step List1:", len(dL1), dL1)       FIXME:
    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    daq.close()

    return dOT
# -----------------------------------------------------------------------------------[Dr Labs]
