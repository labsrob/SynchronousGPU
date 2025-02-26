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



def dnv_sqlexec(nGZ, grp_step, daq1, daq2, daq3, daq4, T1, T2, T3, T4, fetch_no):
    """
    NOTE:
    """

    group_step = int(grp_step)                      # group size/ sample sze
    fetch_no = int(fetch_no)                        # dbfreq = TODO look into any potential conflict
    print('\nSAMPLE SIZE:', nGZ, '| SLIDE STEP:', int(grp_step), '| FETCH CYCLE:', fetch_no)

    # ------------- Consistency Logic ensure list is filled with predetermined elements --------------
    if len(dRP) < (nGZ - 1):
        n2fetch = nGZ                                       # fetch initial specified number
        print('\nRows to Fetch:', n2fetch)

    elif group_step == 1 and len(dRP) >= nGZ:
        print('\nSINGLE STEP SLIDE')
        print('=================')
        n2fetch = (nGZ + fetch_no)                          # fetch just one line to on top of previous fetch

    elif group_step > 1:                                    # and len(dL1) >= nGZ and len(dL2) >= nGZ:
        print('\nSAMPLE SIZE SLIDE')
        print('=================')
        if fetch_no != 0 and len(dRP) >= nGZ and len(dLA) >= nGZ:
            n2fetch = (nGZ * fetch_no)
        else:
            n2fetch = nGZ                                   # fetch twice

    # ------------------------------------------------------------------------------------[]

    # Roller Pressure procedure ----------------------------------[A]
    dataRP = daq1.execute('SELECT * FROM ' + T1).fetchmany(n2fetch)
    if len(dataRP) != 0:
        for result in dataRP:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dRP.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dRP) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dRP[0:(len(dRP) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dRP[0:(len(dRP) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dRP) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dRP[0:(len(dRP) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dRP[0:(len(dRP) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass
        # print("Step List1:", len(dL1), dL1)       FIXME:
    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    daq1.close()

    # Tape Winding procedure ----------------------------------[B]
    dataWS = daq2.execute('SELECT * FROM ' + T2).fetchmany(n2fetch)
    if len(dataWS) != 0:
        for result in dataWS:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dWS.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dWS) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dWS[0:(len(dWS) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dWS[0:(len(dWS) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dWS) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dWS[0:(len(dWS) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dWS[0:(len(dWS) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq2.close()

    # Cell Tension & Oven Temperature procedure ----------------------------[B]
    dataCT = daq3.execute('SELECT * FROM ' + T3).fetchmany(n2fetch)
    if len(dataCT) != 0:
        for result in dataCT:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dCT.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dCT) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dCT[0:(len(dCT) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dCT[0:(len(dCT) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dCT) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dCT[0:(len(dCT) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dCT[0:(len(dCT) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass
        # print("Step List1:", len(dL1), dL1)       FIXME:
    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq3.close()

    return dRP, dWS, dCT
# -------------------------------------------------------------------------------------------------------------[XXXXXXX]


def mgm_sqlexec(nGZ, grp_step, daq1, daq2, daq3, daq4, daq5, T1, T2, T3, T4, T5, fetch_no):
    """
    NOTE:
    """

    group_step = int(grp_step)                      # group size/ sample sze
    fetch_no = int(fetch_no)                        # dbfreq = TODO look into any potential conflict
    print('\nSAMPLE SIZE:', nGZ, '| SLIDE STEP:', int(grp_step), '| FETCH CYCLE:', fetch_no)

    # ------------- Consistency Logic ensure list is filled with predetermined elements --------------
    if len(dLP) < (nGZ - 1):
        n2fetch = nGZ                                       # fetch initial specified number
        print('\nRows to Fetch:', n2fetch)

    elif group_step == 1 and len(dLP) >= nGZ:
        print('\nSINGLE STEP SLIDE')
        print('=================')
        n2fetch = (nGZ + fetch_no)                          # fetch just one line to on top of previous fetch

    elif group_step > 1:                                    # and len(dL1) >= nGZ and len(dL2) >= nGZ:
        print('\nSAMPLE SIZE SLIDE')
        print('=================')
        if fetch_no != 0 and len(dLP) >= nGZ and len(dLA) >= nGZ:
            n2fetch = (nGZ * fetch_no)
        else:
            n2fetch = nGZ                                   # fetch twice

    # ------------------------------------------------------------------------------------[]

    # Roller Force procedure ----------------------------------[A]
    dataLP = daq1.execute('SELECT * FROM ' + T1).fetchmany(n2fetch)
    if len(dataLP) != 0:
        for result in dataLP:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dLP.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dLP) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dLP[0:(len(dLP) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dLP[0:(len(dLP) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dLP) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dLP[0:(len(dLP) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dLP[0:(len(dLP) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    daq1.close()

    # Laser Angle procedure ----------------------------------[B]
    dataLA = daq2.execute('SELECT * FROM ' + T2).fetchmany(n2fetch)
    if len(dataLA) != 0:
        for result in dataLA:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dLA.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dLA) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dLA[0:(len(dLA) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dLA[0:(len(dLA) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dLA) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dLA[0:(len(dLA) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dLA[0:(len(dLA) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq2.close()

    # Cell Tension Procedure ----------------------------------[D]
    dataCT = daq3.execute('SELECT * FROM ' + T3).fetchmany(n2fetch)
    if len(dataCT) != 0:
        for result in dataCT:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dCT.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dCT) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dCT[0:(len(dCT) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dCT[0:(len(dCT) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dCT) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dCT[0:(len(dCT) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dCT[0:(len(dCT) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq3.close()

    # Position Error Procedure ----------------------------------[E]
    dataRP = daq4.execute('SELECT * FROM ' + T4).fetchmany(n2fetch)
    if len(dataRP) != 0:
        for result in dataRP:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dRP.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dRP) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dRP[0:(len(dRP) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dRP[0:(len(dRP) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dRP) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dRP[0:(len(dRP) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dRP[0:(len(dRP) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq4.close()

    # Tape Speed Procedure ----------------------------------[F]
    dataWS = daq5.execute('SELECT * FROM ' + T5).fetchmany(n2fetch)
    if len(dataWS) != 0:
        for result in dataWS:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dWS.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dWS) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dWS[0:(len(dCT) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dWS[0:(len(dCT) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dWS) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dWS[0:(len(dWS) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dWS[0:(len(dWS) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq5.close()

    return dLP, dLA, dCT, dRP, dWS
