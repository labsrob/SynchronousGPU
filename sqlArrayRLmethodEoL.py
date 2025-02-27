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
dTT, dST, dTG, dRM, dLP, dLA, dTP, dRF = [], [], [], [], [], [], [], []

st_id = 0                                               # SQL start index unless otherwise tracker!



def dnv_sqlexec(nGZ, grp_step, daq1, daq2, daq3, daq4, T1, T2, T3, T4, fetch_no):
    """
    NOTE:
    """

    group_step = int(grp_step)                      # group size/ sample sze
    fetch_no = int(fetch_no)                        # dbfreq = TODO look into any potential conflict
    print('\nSAMPLE SIZE:', nGZ, '| SLIDE STEP:', int(grp_step), '| FETCH CYCLE:', fetch_no)

    # ------------- Consistency Logic ensure list is filled with predetermined elements --------------
    if len(dTT) < (nGZ - 1):
        n2fetch = nGZ                                       # fetch initial specified number
        print('\nRows to Fetch:', n2fetch)

    elif group_step == 1 and len(dTT) >= nGZ:
        print('\nSINGLE STEP SLIDE')
        print('=================')
        n2fetch = (nGZ + fetch_no)                          # fetch just one line to on top of previous fetch

    elif group_step > 1:                                    # and len(dL1) >= nGZ and len(dL2) >= nGZ:
        print('\nSAMPLE SIZE SLIDE')
        print('=================')
        if fetch_no != 0 and len(dTT) >= nGZ and len(dTT) >= nGZ:
            n2fetch = (nGZ * fetch_no)
        else:
            n2fetch = nGZ                                   # fetch twice

    # ------------------------------------------------------------------------------------[]

    # Procedure ----------------------------------[A]
    dataTT = daq1.execute('SELECT * FROM ' + T1).fetchmany(n2fetch)
    if len(dataTT) != 0:
        for result in dataTT:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dTT.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dTT) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dTT[0:(len(dTT) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dTT[0:(len(dTT) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dTT) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dTT[0:(len(dTT) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dTT[0:(len(dTT) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass
        # print("Step List1:", len(dL1), dL1)       FIXME:
    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    daq1.close()

    # Tape Winding procedure ----------------------------------[B]
    dataTS = daq2.execute('SELECT * FROM ' + T2).fetchmany(n2fetch)
    if len(dataTS) != 0:
        for result in dataTS:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dST.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dST) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dST[0:(len(dST) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dST[0:(len(dST) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dST) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dST[0:(len(dST) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dST[0:(len(dST) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq2.close()

    # Procedure ----------------------------------[A]
    dataTG = daq3.execute('SELECT * FROM ' + T3).fetchmany(n2fetch)
    if len(dataTG) != 0:
        for result in dataTG:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dTG.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dTG) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dTG[0:(len(dTG) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dTG[0:(len(dTG) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dTG) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dTG[0:(len(dTG) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dTG[0:(len(dTG) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass
        # print("Step List1:", len(dL1), dL1)       FIXME:
    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    daq1.close()

    # Cell Tension & Oven Temperature procedure ----------------------------[B]
    dataRM = daq4.execute('SELECT * FROM ' + T4).fetchmany(n2fetch)
    if len(dataRM) != 0:
        for result in dataRM:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dRM.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dRM) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dRM[0:(len(dRM) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dRM[0:(len(dRM) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dRM) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dRM[0:(len(dRM) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dRM[0:(len(dRM) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass
        # print("Step List1:", len(dL1), dL1)       FIXME:
    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq3.close()

    return dTT, dST, dTG, dRM
# -------------------------------------------------------------------------------------------------------------[XXXXXXX]


def mgm_sqlexec(nGZ, grp_step, daq1, daq2, daq3, daq4, daq5, daq6, daq7, daq8, T1, T2, T3, T4, T5, T6, T7, T8, fetch_no):
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
    # Procedure ----------------------------------[A]
    dataTT = daq1.execute('SELECT * FROM ' + T1).fetchmany(n2fetch)
    if len(dataTT) != 0:
        for result in dataTT:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dTT.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dTT) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dTT[0:(len(dTT) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dTT[0:(len(dTT) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dTT) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dTT[0:(len(dTT) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dTT[0:(len(dTT) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass
        # print("Step List1:", len(dL1), dL1)       FIXME:
    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    daq1.close()

    # Tape Winding procedure ----------------------------------[B]
    dataTS = daq2.execute('SELECT * FROM ' + T2).fetchmany(n2fetch)
    if len(dataTS) != 0:
        for result in dataTS:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dST.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dST) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dST[0:(len(dST) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dST[0:(len(dST) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dST) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dST[0:(len(dST) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dST[0:(len(dST) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    daq2.close()

    # Procedure ----------------------------------[A]
    dataTG = daq3.execute('SELECT * FROM ' + T3).fetchmany(n2fetch)
    if len(dataTG) != 0:
        for result in dataTG:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dTG.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dTG) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dTG[0:(len(dTG) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dTG[0:(len(dTG) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dTG) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dTG[0:(len(dTG) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dTG[0:(len(dTG) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass
        # print("Step List1:", len(dL1), dL1)       FIXME:
    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    daq1.close()

    # Cell Tension & Oven Temperature procedure ----------------------------[B]
    dataRM = daq4.execute('SELECT * FROM ' + T4).fetchmany(n2fetch)
    if len(dataRM) != 0:
        for result in dataRM:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dRM.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dRM) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dRM[0:(len(dRM) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dRM[0:(len(dRM) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dRM) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dRM[0:(len(dRM) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dRM[0:(len(dRM) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass
        # print("Step List1:", len(dL1), dL1)       FIXME:
    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    daq4.close()

    # Roller Force procedure ----------------------------------[A]
    dataLP = daq5.execute('SELECT * FROM ' + T5).fetchmany(n2fetch)
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
    daq5.close()

    # Laser Angle procedure ----------------------------------[B]
    dataLA = daq6.execute('SELECT * FROM ' + T6).fetchmany(n2fetch)
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
    daq6.close()

    # Cell Tension Procedure ----------------------------------[D]
    dataTP = daq7.execute('SELECT * FROM ' + T7).fetchmany(n2fetch)
    if len(dataTP) != 0:
        for result in dataTP:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dTP.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dTP) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dTP[0:(len(dTP) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dTP[0:(len(dTP) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dTP) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dTP[0:(len(dTP) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dTP[0:(len(dTP) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    daq7.close()

    # Position Error Procedure ----------------------------------[E]
    dataRF = daq8.execute('SELECT * FROM ' + T8).fetchmany(n2fetch)
    if len(dataRF) != 0:
        for result in dataRF:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dRF.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dRF) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dRF[0:(len(dRF) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dRF[0:(len(dRF) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dRF) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dRF[0:(len(dRF) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dRF[0:(len(dRF) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq4.close()

    return dTT, dST, dTG, dRM, dLP, dLA, dTP, dRF
