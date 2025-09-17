# This script is called in from Main program to load SQL execution syntax command and return a list in LisDat
# Author: Dr Labs, RB
# -------------------------------------------------------------------------------------------------------------
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
st_id = 0
seqData = 0

# SQL start index unless otherwise stated by the index tracker!
cols = 'cLayer, Line1Temp, Line2Temp, Line3Temp, Line4Temp, Line5Temp, Line1Humi, Line2Humi, Line3Humi, Line4Humi, Line5Humi'

def sqlExec(daq, nGZ, grp_step, T1, fetch_no):
    """
    NOTE: Serialized processing enabled
    """
    t1 = daq.cursor()

    n2fetch = int(nGZ)
    group_step = int(grp_step)
    fetch_no = int(fetch_no)
    print('\nSAMPLE SIZE:', nGZ, '| SLIDE STEP:', int(grp_step), '| FETCH CYCLE:', fetch_no)

    # ------------- Consistency Logic ensure list is filled with predetermined elements --------------
    if group_step == 1:
        print('\nSINGLE SLIDE WINDOW')
        print('===================')

    elif group_step > 1:
        print('\nGROUP SLIDE WINDOW')
        print('==================')

    itr = len(dataList0)
    idxA = itr + nGZ
    print('\nRows to Fetch:', nGZ)
    print('Processing SQL Row #:', 'Idx:', itr, 'to Row #:', idxA)
    print('TP003', idxA)
    print('TP004 Data list Index', dataList0)
    # ------------------------------------------------------------------------------------[]
    # data1 = t1.execute(f'SELECT DISTINCT ' + cols + ' FROM ' + str(T1)) #.fetchmany(n2fetch)
    t1.execute(f'SELECT DISTINCT ' + cols + ' FROM ' + str(T1))
    # print('\nTotal SQL Column Fetched:', len(data1))
    # if len(data1) != 0:
        # for result, n in zip(data1, idx):
    for row in t1.fetchmany(n2fetch):
        print('row = %r' % (row,))
        dL = row
        # for result in data1:
        #     result = list(result)
        #     if UseRowIndex:
        #         dataList0.append(next(idx))
        #     else:
        #         now = time.strftime("%H:%M:%S")
        #         dataList0.append(time.strftime(now))
        #     dL.append(result)
        #     print('dL - Before Purge:', len(dL))
            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
        #     if len(dL) >= (nGZ + n2fetch):
        #         del dL[0:(len(dL) - nGZ)]
        #     else:
        #         del dL[0:len(dL) - (nGZ * fetch_no)]
        #     print('dL - After Purge:', len(dL))
        # print("cEV Buffer List:", len(dL), dL)

    # else:
    #     print('Process EOF reached...')
    #     print('SPC Halting for 5 Seconds...')
    #     time.sleep(5)


    t1.close()

    return dL
# -----------------------------------------------------------------------------------[Dr Labs]
