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
dGEN, dRPa, dRPb, dLPa, dLPb, dLAa,  dLAb = [], [], [], [], [], [], []

st_id = 0                                           # SQL start index unless otherwise stated by the index tracker!


def dnv_sqlexec(nGZ, grp_step, daq1, daq2, daq3, T1, T2, T3, fetch_no):
    """
    NOTE:
    """

    group_step = int(grp_step)                      # group size/ sample sze
    fetch_no = int(fetch_no)                        # dbfreq = TODO look into any potential conflict
    print('\nSAMPLE SIZE:', nGZ, '| SLIDE STEP:', int(grp_step), '| FETCH CYCLE:', fetch_no)

    # ------------- Consistency Logic ensure list is filled with predetermined elements --------------
    if len(dRPa) < (nGZ - 1):
        n2fetch = nGZ                                       # fetch initial specified number
        print('\nRows to Fetch:', n2fetch)

    elif group_step == 1 and len(dRPa) >= nGZ:
        print('\nSINGLE STEP SLIDE')
        print('=================')
        n2fetch = (nGZ + fetch_no)                          # fetch just one line to on top of previous fetch

    elif group_step > 1:                                    # and len(dL1) >= nGZ and len(dL2) >= nGZ:
        print('\nSAMPLE SIZE SLIDE')
        print('=================')
        if fetch_no != 0 and len(dRPa) >= nGZ and len(dLAa) >= nGZ:
            n2fetch = (nGZ * fetch_no)
        else:
            n2fetch = nGZ                                   # fetch twice

    # ------------------------------------------------------------------------------------[]

    # Roller Pressure procedure ----------------------------------[A]
    dataGEN = daq1.execute('SELECT * FROM ' + T1).fetchmany(n2fetch)
    if len(dataGEN) != 0:
        for result in dataGEN:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dGEN.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dGEN) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dGEN[0:(len(dGEN) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dGEN[0:(len(dGEN) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dGEN) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dGEN[0:(len(dGEN) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dGEN[0:(len(dGEN) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass
        # print("Step List1:", len(dL1), dL1)       FIXME:
    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    daq1.close()

    # Tape Winding procedure ----------------------------------[B]
    dataRPa = daq2.execute('SELECT * FROM ' + T2).fetchmany(n2fetch)
    if len(dataRPa) != 0:
        for result in dataRPa:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dRPa.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dRPa) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dRPa[0:(len(dRPa) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dRPa[0:(len(dRPa) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dRPa) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dRPa[0:(len(dRPa) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dRPa[0:(len(dRPa) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq2.close()

    # Tape Winding procedure ----------------------------------[B]
    dataRPb = daq3.execute('SELECT * FROM ' + T3).fetchmany(n2fetch)
    if len(dataRPb) != 0:
        for result in dataRPb:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dRPb.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dRPb) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dRPb[0:(len(dRPb) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dRPb[0:(len(dRPb) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dRPb) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dRPb[0:(len(dRPb) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dRPb[0:(len(dRPb) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq3.close()

    return dGEN, dRPa, dRPb
# -------------------------------------------------------------------------------------------------------------[XXXXXXX]


def mgm_sqlexec(nGZ, grp_step, daq1, daq2, daq3, daq4, daq5, daq6, daq7, T1, T2, T3, T4, T5, T6, T7, fetch_no):
    """
    NOTE:
    """

    group_step = int(grp_step)                      # group size/ sample sze
    fetch_no = int(fetch_no)                        # dbfreq = TODO look into any potential conflict
    print('\nSAMPLE SIZE:', nGZ, '| SLIDE STEP:', int(grp_step), '| FETCH CYCLE:', fetch_no)

    # ------------- Consistency Logic ensure list is filled with predetermined elements --------------
    if len(dLPa) < (nGZ - 1):
        n2fetch = nGZ                                       # fetch initial specified number
        print('\nRows to Fetch:', n2fetch)

    elif group_step == 1 and len(dLPa) >= nGZ:
        print('\nSINGLE STEP SLIDE')
        print('=================')
        n2fetch = (nGZ + fetch_no)                          # fetch just one line to on top of previous fetch

    elif group_step > 1:                                    # and len(dL1) >= nGZ and len(dL2) >= nGZ:
        print('\nSAMPLE SIZE SLIDE')
        print('=================')
        if fetch_no != 0 and len(dLPa) >= nGZ and len(dLAa) >= nGZ:
            n2fetch = (nGZ * fetch_no)
        else:
            n2fetch = nGZ                                   # fetch twice

    # ------------------------------------------------------------------------------------[]
    dataGEN = daq1.execute('SELECT * FROM ' + T1).fetchmany(n2fetch)
    if len(dataGEN) != 0:
        for result in dataGEN:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dGEN.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dGEN) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dGEN[0:(len(dGEN) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dGEN[0:(len(dGEN) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dGEN) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dGEN[0:(len(dGEN) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dGEN[0:(len(dGEN) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass
        # print("Step List1:", len(dL1), dL1)       FIXME:
    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    daq1.close()

    # Position Error Procedure ----------------------------------[E]
    dataRPa = daq2.execute('SELECT * FROM ' + T2).fetchmany(n2fetch)
    if len(dataRPa) != 0:
        for result in dataRPa:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dRPa.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dRPa) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dRPa[0:(len(dRPa) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dRPa[0:(len(dRPa) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dRPa) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dRPa[0:(len(dRPa) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dRPa[0:(len(dRPa) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq2.close()

    # Position Error Procedure ----------------------------------[E]
    dataRPb = daq3.execute('SELECT * FROM ' + T3).fetchmany(n2fetch)
    if len(dataRPb) != 0:
        for result in dataRPb:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dRPb.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dRPb) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dRPb[0:(len(dRPb) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dRPb[0:(len(dRPb) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dRPb) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dRPb[0:(len(dRPb) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dRPb[0:(len(dRPb) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq3.close()

    # Roller Force procedure ----------------------------------[A]
    dataLPa = daq4.execute('SELECT * FROM ' + T4).fetchmany(n2fetch)
    if len(dataLPa) != 0:
        for result in dataLPa:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dLPa.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dLPa) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dLPa[0:(len(dLPa) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dLPa[0:(len(dLPa) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dLPa) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dLPa[0:(len(dLPa) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dLPa[0:(len(dLPa) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    daq4.close()

    # Roller Force procedure ----------------------------------[A]
    dataLPb = daq5.execute('SELECT * FROM ' + T5).fetchmany(n2fetch)
    if len(dataLPb) != 0:
        for result in dataLPb:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dLPb.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dLPb) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dLPb[0:(len(dLPb) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dLPb[0:(len(dLPb) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dLPb) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dLPb[0:(len(dLPb) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dLPb[0:(len(dLPb) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    daq5.close()

    # Laser Angle procedure ----------------------------------[B]
    dataLAa = daq6.execute('SELECT * FROM ' + T6).fetchmany(n2fetch)
    if len(dataLAa) != 0:
        for result in dataLAa:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dLAa.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dLAa) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dLAa[0:(len(dLAa) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dLAa[0:(len(dLAa) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dLAa) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dLAa[0:(len(dLAa) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dLAa[0:(len(dLAa) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq6.close()

    # Laser Angle procedure ----------------------------------[B]
    dataLAb = daq7.execute('SELECT * FROM ' + T7).fetchmany(n2fetch)
    if len(dataLAb) != 0:
        for result in dataLAb:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dLAb.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dLAb) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dLAb[0:(len(dLAb) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dLAb[0:(len(dLAb) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dLAa) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dLAb[0:(len(dLAb) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dLAb[0:(len(dLAb) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq7.close()

    return dGEN, dRPa, dRPb, dLPa, dLPb, dLAa, dLAb
