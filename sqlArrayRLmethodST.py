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
    t1, t2 = daq.cursor(), daq.cursor()

    nGZ = int(nGZ) + 3
    group_step = int(grp_step)
    fetch_no = int(len(dataList0))  # int(nGZ) + 3
    print('\nIndex Counter:', fetch_no, group_step, '\n')

    # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
    # ------------- Consistency Logic ensure list is filled with predetermined elements --------------
    if group_step == 1:
        print('\nSINGLE STEP SLIDE')
        n2fetch = nGZ + 1
        print('Rows to Fetch:', nGZ)

    else:
        print('\nGROUP STEP SLIDE')
        print('=================')
        n2fetch = nGZ + (nGZ - 1)
        print('Rows to Fetch:', nGZ)
    # ------------------------------------------------------------------------------------[]
    data1 = t1.execute('SELECT TOP (' + str(n2fetch) + ') * FROM ' + str(T1)).fetchmany(n2fetch)
    # data1 = t1.execute('SELECT * FROM ' + str(T1)).fetchmany(n2fetch)
    print('\nTotal SQL Processed ST1:', data1)
    if len(data1) == n2fetch:
        for result in data1:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dL1.append(result)
            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            if group_step > 1:
                if len(dL1) >= nGZ and fetch_no <= 33:  # Retain group and step size
                    del dL1[0:(len(dL1) - nGZ)]
                elif (fetch_no + 1) >= 33:
                    del dL1[0:(len(dL1) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1:
                if len(dL1) >= nGZ and fetch_no <= 33:
                    del dL1[0:(len(dL1) - nGZ)]  # delete overflow data
                elif (fetch_no + 1) >= 33:  # moving windows
                    del dL1[0:(len(dL1) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass
        print('[ST1] Total Fetched:', len(dL1))

    else:
        dataList0.append(next(idx))
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    t1.close()  # close cursor

    # ------------------------------------------------------------------------------------[]
    # data2 = t2.execute('SELECT * FROM ' + str(T2)).fetchmany(n2fetch)
    data2 = t2.execute('SELECT TOP (' + str(n2fetch) + ') * FROM ' + str(T2)).fetchmany(n2fetch)
    print('Total SQL Fetched ST2:', data2)
    if len(data2) == n2fetch:
        for result in data2:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dL2.append(result)
            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            if group_step > 1:
                if len(dL2) >= nGZ and fetch_no <= 31:  # Retain group and step size
                    del dL2[0:(len(dL2) - nGZ)]
                elif (fetch_no + 1) >= 32:
                    del dL2[0:(len(dL2) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1:
                if len(dL2) >= nGZ and fetch_no <= 31:
                    del dL2[0:(len(dL2) - nGZ)]  # delete overflow data
                elif (fetch_no + 1) >= 32:  # moving windows
                    del dL2[0:(len(dL2) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass
        print('[ST2] Total Fetched:', len(dL2))

    else:
        dataList0.append(next(idx))
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    t2.close() # close cursor

    return dL1, dL2
# -----------------------------------------------------------------------------------[Dr Labs]
