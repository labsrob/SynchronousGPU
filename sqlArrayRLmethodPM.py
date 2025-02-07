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
dRF, dLA, dCT, dOT, dPE, dTS = [], [], [], [], [], []
idxRF, idxLA, idxCT, idxOT, idxPE, idxTS = [], [], [], [],[], []

st_id = 0                                           # SQL start index unless otherwise stated by the index tracker!


def dnv_sqlexec(nGZ, grp_step, daq1, daq2, daq3, daq4, T1, T2, T3, T4, q1, q2, q3, q4, fetch_no):
    """
    NOTE:
    """
    id1 = str(q1)                                   # convert Query Indexes to string concatenation
    id2 = str(q2)
    id3 = str(q3)
    id4 = str(q4)

    group_step = int(grp_step)                      # group size/ sample sze
    fetch_no = int(fetch_no)                        # dbfreq = TODO look into any potential conflict
    print('\nSAMPLE SIZE:', nGZ, '| SLIDE STEP:', int(grp_step), '| FETCH CYCLE:', fetch_no)

    # ------------- Consistency Logic ensure list is filled with predetermined elements --------------
    if len(dRF) < (nGZ - 1):
        n2fetch = nGZ                                       # fetch initial specified number
        print('\nRows to Fetch:', n2fetch)
        print('Processing SQL Row #:', int(id1) + fetch_no + 1, 'to', (int(id1) + fetch_no + 1) + n2fetch)

    elif group_step == 1 and len(dRF) >= nGZ:
        print('\nSINGLE STEP SLIDE')
        print('=================')
        n2fetch = (nGZ + fetch_no)                          # fetch just one line to on top of previous fetch

        idxA = int(id1) + (((fetch_no + 1) - 2) * nGZ) + 1
        idxB = int(id2) + (((fetch_no + 1) - 2) * nGZ) + 1
        idxC = int(id3) + (((fetch_no + 1) - 2) * nGZ) + 1
        idxD = int(id4) + (((fetch_no + 1) - 2) * nGZ) + 1
        if len(idxRF) > 1 or len(idxLA) > 1:
            del idxRF[:1]
            del idxLA[:1]
            del idxCT[:1]
            del idxOT[:1]
        # Add values after a systematic clean up
        idxRF.append(idxA)
        idxLA.append(idxB)
        idxCT.append(idxC)
        idxOT.append(idxD)
        print('Processing SQL Row #:', 'T1-4:', idxRF, idxLA, idxCT, idxOT)

    elif group_step > 1:                                    # and len(dL1) >= nGZ and len(dL2) >= nGZ:
        print('\nSAMPLE SIZE SLIDE')
        print('=================')
        if fetch_no != 0 and len(dRF) >= nGZ and len(dLA) >= nGZ:
            n2fetch = (nGZ * fetch_no)
        else:
            n2fetch = nGZ                                   # fetch twice
        # Evaluate rows in each tables ---------------------
        idxA = int(id1) + (((fetch_no + 1) - 2) * nGZ) + 1
        idxB = int(id2) + (((fetch_no + 1) - 2) * nGZ) + 1
        idxC = int(id3) + (((fetch_no + 1) - 2) * nGZ) + 1
        idxD = int(id4) + (((fetch_no + 1) - 2) * nGZ) + 1

        if len(idxRF) > 1 or len(idxLA) > 1:
            del idxRF[:1]
            del idxLA[:1]
            del idxCT[:1]
            del idxOT[:1]
        idxRF.append(idxA)
        idxLA.append(idxB)
        idxCT.append(idxC)
        idxOT.append(idxD)
    # ------------------------------------------------------------------------------------[]

    # Roller Force procedure ----------------------------------[A]
    dataRF = daq1.execute('SELECT * FROM ' + T1 + ' WHERE idxRF > ' + str(id1)).fetchmany(n2fetch)
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
        # print("Step List1:", len(dL1), dL1)       FIXME:
    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    daq1.close()

    # Laser Angle procedure ----------------------------------[B]
    dataLA = daq2.execute('SELECT * FROM ' + T2 + ' WHERE idxLA > ' + str(id2)).fetchmany(n2fetch)
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

    # Cell Tension procedure ----------------------------------[B]
    dataCT = daq3.execute('SELECT * FROM ' + T3 + ' WHERE idxCT > ' + str(id3)).fetchmany(n2fetch)
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

    # Oven Temperature procedure ----------------------------------[B]
    dataOT = daq4.execute('SELECT * FROM ' + T4 + ' WHERE idxOT > ' + str(id4)).fetchmany(n2fetch)
    if len(dataOT) != 0:
        for result in dataOT:
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

    daq4.close()

    return idxRF, idxLA, idxCT, idxOT, dRF, dLA, dCT, dOT
# -------------------------------------------------------------------------------------------------------------[XXXXXXX]


def mgm_sqlexec(nGZ, grp_step, daq1, daq2, daq3, daq4, daq5, daq6, q1, q2, q3, q4, q5, q6, T1, T2, T3, T4, T5, T6, fetch_no):
    """
    NOTE:
    """
    # convert Query Indexes to string concatenation
    id1 = str(q1)  # RF                            # convert query indexes to string concatenation
    id2 = str(q2)  # LA
    id3 = str(q3)  # OT
    id4 = str(q4)  # CT
    id5 = str(q5)  # PE
    id6 = str(q6)  # TS

    group_step = int(grp_step)                      # group size/ sample sze
    fetch_no = int(fetch_no)                        # dbfreq = TODO look into any potential conflict
    print('\nSAMPLE SIZE:', nGZ, '| SLIDE STEP:', int(grp_step), '| FETCH CYCLE:', fetch_no)

    # ------------- Consistency Logic ensure list is filled with predetermined elements --------------
    if len(dRF) < (nGZ - 1):
        n2fetch = nGZ                                       # fetch initial specified number
        print('\nRows to Fetch:', n2fetch)
        print('Processing SQL Row #:', int(id1) + fetch_no + 1, 'to', (int(id1) + fetch_no + 1) + n2fetch)

    elif group_step == 1 and len(dRF) >= nGZ:
        print('\nSINGLE STEP SLIDE')
        print('=================')
        n2fetch = (nGZ + fetch_no)                          # fetch just one line to on top of previous fetch

        idxA = int(id1) + (((fetch_no + 1) - 2) * nGZ) + 1
        idxB = int(id2) + (((fetch_no + 1) - 2) * nGZ) + 1
        idxC = int(id3) + (((fetch_no + 1) - 2) * nGZ) + 1
        idxD = int(id4) + (((fetch_no + 1) - 2) * nGZ) + 1
        idxE = int(id5) + (((fetch_no + 1) - 2) * nGZ) + 1
        idxF = int(id6) + (((fetch_no + 1) - 2) * nGZ) + 1
        if len(idxRF) > 1 or len(idxLA) > 1:
            del idxRF[:1]
            del idxLA[:1]
            del idxCT[:1]
            del idxOT[:1]
            del idxPE[:1]
            del idxTS[:1]
        # Add values after a systematic clean up
        idxRF.append(idxA)
        idxLA.append(idxB)
        idxOT.append(idxC)
        idxCT.append(idxD)
        idxPE.append(idxE)
        idxTS.append(idxF)
        print('Processing SQL Row #:', 'T1-6:', idxRF, idxLA, idxOT, idxCT, idxPE, idxTS)

    elif group_step > 1:                                    # and len(dL1) >= nGZ and len(dL2) >= nGZ:
        print('\nSAMPLE SIZE SLIDE')
        print('=================')
        if fetch_no != 0 and len(dRF) >= nGZ and len(dLA) >= nGZ:
            n2fetch = (nGZ * fetch_no)
        else:
            n2fetch = nGZ                                   # fetch twice
        # Evaluate rows in each tables ---------------------
        idxA = int(id1) + (((fetch_no + 1) - 2) * nGZ) + 1
        idxB = int(id2) + (((fetch_no + 1) - 2) * nGZ) + 1
        idxC = int(id3) + (((fetch_no + 1) - 2) * nGZ) + 1
        idxD = int(id4) + (((fetch_no + 1) - 2) * nGZ) + 1
        idxE = int(id4) + (((fetch_no + 1) - 2) * nGZ) + 1
        idxF = int(id4) + (((fetch_no + 1) - 2) * nGZ) + 1

        if len(idxRF) > 1 or len(idxLA) > 1:
            del idxRF[:1]
            del idxLA[:1]
            del idxOT[:1]
            del idxCT[:1]
            del idxPE[:1]
            del idxTS[:1]
        idxRF.append(idxA)
        idxLA.append(idxB)
        idxOT.append(idxC)
        idxCT.append(idxD)
        idxPE.append(idxE)
        idxTS.append(idxF)

    # ------------------------------------------------------------------------------------[]

    # Roller Force procedure ----------------------------------[A]
    dataRF = daq1.execute('SELECT * FROM ' + T1 + ' WHERE idxRF > ' + str(id1)).fetchmany(n2fetch)
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
    daq1.close()

    # Laser Angle procedure ----------------------------------[B]
    dataLA = daq2.execute('SELECT * FROM ' + T2 + ' WHERE idxLA > ' + str(id2)).fetchmany(n2fetch)
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

    # Oven Temperature procedure ----------------------------------[C]
    dataOT = daq3.execute('SELECT * FROM ' + T3 + ' WHERE idxOT > ' + str(id3)).fetchmany(n2fetch)
    if len(dataOT) != 0:
        for result in dataOT:
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
                del dOT[0:(len(dCT) - fetch_no)]

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

    daq3.close()

    # Cell Tension Procedure ----------------------------------[D]
    dataCT = daq4.execute('SELECT * FROM ' + T4 + ' WHERE idxCT > ' + str(id4)).fetchmany(n2fetch)
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

    daq4.close()

    # Position Error Procedure ----------------------------------[E]
    dataPE = daq5.execute('SELECT * FROM ' + T5 + ' WHERE idxPE > ' + str(id5)).fetchmany(n2fetch)
    if len(dataPE) != 0:
        for result in dataPE:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dPE.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dPE) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dPE[0:(len(dPE) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dPE[0:(len(dPE) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dPE) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dPE[0:(len(dPE) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dPE[0:(len(dPE) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq5.close()

    # Tape Speed Procedure ----------------------------------[F]
    dataTS = daq4.execute('SELECT * FROM ' + T6 + ' WHERE idxTS > ' + str(id4)).fetchmany(n2fetch)
    if len(dataTS) != 0:
        for result in dataTS:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dTS.append(result)

            # Purgatory logic to free up active buffer ----------------------[Dr labs Technique]
            # Step processing rate >1 ---[static window]
            if group_step > 1 and len(dTS) >= (nGZ + n2fetch) and fetch_no <= 21:  # Retain group and step size
                del dTS[0:(len(dCT) - nGZ)]

            # Step processing rate >1 ---[moving window]
            elif group_step > 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dTS[0:(len(dCT) - fetch_no)]

            # Step processing rate =1 ---[static window]
            elif group_step == 1 and len(dTS) >= (nGZ + n2fetch) and fetch_no <= 21:
                del dTS[0:(len(dTS) - nGZ)]  # delete overflow data

            # Step processing rate =1 ---[moving window]
            elif group_step == 1 and (fetch_no + 1) >= 22:  # After windows limit (move)
                del dTS[0:(len(dTS) - fetch_no)]

            else:  # len(dL1) < nGZ:
                pass

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq6.close()

    return idxRF, idxLA, idxOT, idxCT, idxPE, idxTS, dRF, dLA, dOT, dCT, dPE, dTS
