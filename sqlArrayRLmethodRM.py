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

    nGZ = int(nGZ)
    group_step = int(grp_step)
    fetch_no = int(len(dataList0))  # int(nGZ) + 3
    print('\nDefault Sample Size:', fetch_no, group_step, '\n')

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
    # data3 = t1.execute('SELECT TOP (' + str(n2fetch) + ') * FROM ' + str(T3)).fetchall()
    data3 = t1.execute('SELECT TOP (' + str(n2fetch) + ') * FROM ' + str(T3)+ ' ORDER BY cLayer').fetchall() #.fetchmany(n2fetch)
    # data3 = t1.execute('SELECT * FROM ' + str(T3)).fetchmany(n2fetch)
    print('Total SQL Processed RMP:', data3, '\n')
    if len(data3) != 0:
        for result in data3:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            # dL3.append(result)
            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            if group_step > 1:
                if len(dL3) >= nGZ and fetch_no <= 31:  # Retain group and step size
                    del dL3[0:(len(dL3) - nGZ)]
                elif (fetch_no + 1) >= 32:
                    del dL3[0:(len(dL3) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1:
                if len(dL3) >= nGZ and fetch_no <= 31:
                    del dL3[0:(len(dL3) - nGZ)]  # delete overflow data
                elif (fetch_no + 1) >= 32:  # moving windows
                    del dL3[0:(len(dL3) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass
            dL3.append(result)
            # print('ZIPPED', zip(fetch_no, dL1))
            print('[RMP] Total Fetched:', len(dL3))

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    t1.close()  # close cursor

    return dL3
# -----------------------------------------------------------------------------------[Dr Labs]
