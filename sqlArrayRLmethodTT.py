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

dataList0, dL1, dL2, dL3 = [], [], [], []


def sqlExec(daq, nGZ, grp_step, T1, T2, T3, dbfreq):

    """
    NOTE:
    """
    t1, t2, t3 = daq.cursor(), daq.cursor(), daq.cursor()

    nGZ = int(nGZ)
    group_step = int(grp_step)
    fetch_no = dbfreq
    print('\nIndex Counter:', fetch_no, 'To Fetch', nGZ, '\n')

    # ------------- Consistency Logic ensure list is filled with predetermined elements --------------
    if group_step == 1:
        print('\nSINGLE STEP SLIDE')
        # if len(dL1) < (nGZ -1):
        #     n2fetch = nGZ
        # elif len(dL1) >= nGZ:
        #     n2fetch = 1
        # else:
        #     n2fetch = nGZ
        n2fetch = nGZ
        print('Processing SQL Row #:', fetch_no, 'to', (fetch_no + nGZ))

    else:
        print('\nGROUP STEP SLIDE')
        print('=================')
        n2fetch = nGZ + (nGZ - 1)
        print('Rows to Fetch:', nGZ)

    # -------------------------------Assuming a very large dataset -------------------------[]
    # data1 = t1.execute('SELECT TOP (' + str(n2fetch) +') * FROM ' + str(T1)).fetchmany(n2fetch)
    data1 = t1.execute('SELECT * FROM ' + str(T1)).fetchmany(n2fetch)
    print('\nTotal SQL Processed TT1:', data1)
    if len(data1) != 0:
        for result in data1:
            result = list(result)

            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dL1.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate =1 ---[static window]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dL1) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dL1[0:(len(dL1) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dL1[0:(len(dL1) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dL1) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dL1[0:(len(dL1) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dL1[0:(len(dL1) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass
            print('[TT1] Total Fetched:', len(dL1))
    else:
        dataList0.append(next(idx))
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    t1.close()  # close cursor

    # ------------------------------------------------------------------------------------[]
    # data2 = t2.execute('SELECT TOP ('+ str(n2fetch) +') * FROM ' + str(T2)).fetchmany(n2fetch)
    data2 = t2.execute('SELECT * FROM ' + str(T2)).fetchmany(n2fetch)
    print('Total SQL Fetched TT2:', data2)
    if len(data2) == n2fetch:
        for result in data2:
            result = list(result)
            dL2.append(result)

            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
                # Step processing rate >1 ---[static window]
                if group_step > 1 and len(dL2) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                    del dL2[0:(len(dL2) - nGZ)]

                # Step processing rate >1 ---[moving window]
                elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                    del dL2[0:(len(dL2) - fetch_no)]

                # Step processing rate =1 ---[static window]
                elif group_step == 1 and len(dL2) >= (nGZ + n2fetch) and fetch_no <= 21:
                    del dL2[0:(len(dL2) - nGZ)]  # delete overflow data

                # Step processing rate =1 ---[moving window]
                elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                    del dL2[0:(len(dL2) - fetch_no)]

                else:  # len(dL1) < nGZ:
                    pass

            print('[TT2] Total Fetched:', len(dL2))
    else:
        dataList0.append(next(idx))
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    t2.close()  # close cursor

    # ------------------------------------------------------------------------------------[]
    # data3 = t1.execute('SELECT TOP ('+ str(n2fetch) +') * FROM ' + str(T3)).fetchall()
    data3 = t3.execute('SELECT * FROM ' + str(T3)).fetchmany(n2fetch)
    print('Total SQL Fetched RMP:', data3)
    if len(data3) == n2fetch:
        for result in data3:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dL3.append(result)
            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dL3) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dL3[0:(len(dL3) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dL3[0:(len(dL3) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dL3) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dL3[0:(len(dL3) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dL3[0:(len(dL3) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass
            print('[RMP] Total Fetched:', len(dL3))

    else:
        dataList0.append(next(idx))
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    t3.close()  # close cursor

    return dL1, dL2, dL3
    # -----------------------------------------------------------------------------------[Dr Labs]
