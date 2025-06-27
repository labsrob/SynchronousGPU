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
rLP, rLA, rRP, rTT, rST, rTG, rWA, rWS = [], [], [], [], [], [], [], []

st_id  = 0                                               # SQL start index unless otherwise tracker!
eol_sr = 0.5


def dnv_sqlExec(daq1, daq2, daq3, daq4, daq5, daq6, T1, T2, T3, T4, T5, T6, layerNo):
    """
    NOTE:
    """

    # Procedure to determine EOL sampling regime ---------------------------------------------------------------[X]
    # -- Find out total number of column record per Ring -----[]
    ttSR = daq1.execute(
        'Select count([R1H1TT]) AS ValidTotal from ' + "'" '%' + str(T1) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    # close sel link -------
    daq1.close()

    stSR = daq2.execute(
        'Select count([R1H1ST]) AS ValidTotal from ' + "'" '%' + str(T2) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    # close sel link -------
    daq2.close()

    tgSR = daq3.execute(
        'Select count([R1H1TG]) AS ValidTotal from ' + "'" '%' + str(T3) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    # close sel link -------
    daq3.close()

    wsSR = daq4.execute(
        'Select count([R1H1WS]) AS ValidTotal from ' + "'" '%' + str(T4) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    # close sel link -------
    daq4.close()

    # --- Compute sampling regime based on data volume -------[]
    regm1 = ttSR * eol_sr
    regm2 = stSR * eol_sr
    regm3 = tgSR * eol_sr       # % 60  # Modulo evaluation TG?
    regm4 = wsSR * eol_sr

    ############## RAMP COUNT ---------------------------------[]
    R1RC = daq5.execute(
        'Select count([RAMPosA]) AS ValidTotal from ' + "'" '%' + str(T5) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    R2RC = daq5.execute(
        'Select count([RAMPosB]) AS ValidTotal from ' + "'" '%' + str(T5) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    R3RC = daq5.execute(
        'Select count([RAMPosC]) AS ValidTotal from ' + "'" '%' + str(T5) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    R4RC = daq5.execute(
        'Select count([RAMPosD]) AS ValidTotal from ' + "'" '%' + str(T5) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    # close sel link -------
    daq5.close()

    ############## GAP COUNT ---------------------------------[]
    R1VC = daq6.execute(
        'Select count([VODPosA]) AS ValidTotal from ' + "'" '%' + str(
            T6) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    R2VC = daq6.execute(
        'Select count([VODPosB]) AS ValidTotal from ' + "'" '%' + str(
            T6) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    R3VC = daq6.execute(
        'Select count([VODPosC]) AS ValidTotal from ' + "'" '%' + str(
            T6) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    R4VC = daq6.execute(
        'Select count([VODPosD]) AS ValidTotal from ' + "'" '%' + str(
            T6) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()

    # close sel link ----------------------[]
    daq6.close()

    # ------------------ Load randomised samples --------------------------------------------------------------[A]
    dataTT = daq1.execute(
        'Select TOP ' + "'" '%' + str(regm1) + '%' "'" '* FROM ' + "'" '%' + str(T1) + '%' "'" ' where [cLayer] = '
                   + "'" '%' + str(layerNo) + '%' "'" + 'order by NEWID()').fetchone()
    if len(dataTT) != 0:
        for result in dataTT:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            rTT.append(result)
        # print("Step List1:", len(dL1), dL1)       FIXME:

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    daq1.close()

    # Substrate Temperature --------------------------------------------------------------------------------[B]
    dataST = daq2.execute(
        'Select TOP ' + "'" '%' + str(regm2) + '%' "'" '* FROM ' + "'" '%' + str(T2) + '%' "'" ' where [cLayer] = '
        + "'" '%' + str(layerNo) + '%' "'" + 'order by NEWID()').fetchone()

    if len(dataST) != 0:
        for result in dataST:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            rST.append(result)

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq2.close()

    # Tape Gap Procedure ------------------------------------------------------------------------------------[C]
    dataTG = daq3.execute(
        'Select TOP ' + "'" '%' + str(regm3) + '%' "'" '* FROM ' + "'" '%' + str(T3) + '%' "'" ' where [cLayer] = '
        + "'" '%' + str(layerNo) + '%' "'" + 'order by NEWID()').fetchone()
    if len(dataTG) != 0:
        for result in dataTG:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            rTG.append(result)

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    daq3.close()

    # Ramp Profile ------------------------------------------------------------------------------------------[D]
    dataWS = daq4.execute(
        'Select TOP ' + "'" '%' + str(regm4) + '%' "'" '* FROM ' + "'" '%' + str(T4) + '%' "'" ' where [cLayer] = '
        + "'" '%' + str(layerNo) + '%' "'" + 'order by NEWID()').fetchone()
    if len(dataWS) != 0:
        for result in dataWS:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            rWS.append(result)

        # print("Step List1:", len(dL1), dL1)       FIXME:

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq4.close()

    return rTT, rST, rTG, rWS, R1RC, R2RC, R3RC, R4RC, R1VC, R2VC, R3VC, R4VC
# -------------------------------------------------------------------------------------------------------[XXXXXXX]


def mgm_sqlExec(daq1, daq2, daq3, daq4, daq5, daq6, daq7, daq8, T1, T2, T3, T4, T5, T6, T7, T8, layerNo):
    """
    NOTE:
    """

    # Procedure -----------------------------------------------------------------------------------------------[X]
    # -- Find out total number of column record per Ring -----[]
    lpR = daq1.execute(
        'Select count([R1H1LP]) AS ValidTotal from ' + "'" '%' + str(T1) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    # close sel link -------[]
    daq1.close()

    laR = daq2.execute(
        'Select count([R1H1LA]) AS ValidTotal from ' + "'" '%' + str(T2) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    # close sel link -------[]
    daq2.close()

    ttR = daq3.execute(
        'Select count([R4H1TT]) AS ValidTotal from ' + "'" '%' + str(T4) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    # close sel link -------[]
    daq3.close()

    stR = daq4.execute(
        'Select count([R4H1ST]) AS ValidTotal from ' + "'" '%' + str(T5) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    # close sel link -------[]
    daq4.close()

    tgR = daq5.execute(
        'Select count([R4H1TG]) AS ValidTotal from ' + "'" '%' + str(T6) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    # close sel link -------[]
    daq5.close()

    waR = daq6.execute(
        'Select count([R4H1WA]) AS ValidTotal from ' + "'" '%' + str(T7) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    # close sel link -------[]
    daq6.close()

    # --- Compute sampling regime based on data volume -------[]
    sp1 = lpR * eol_sr       # LP
    sp2 = laR * eol_sr       # LA
    sp3 = ttR * eol_sr       # TT
    sp4 = stR * eol_sr       # ST
    sp5 = tgR * eol_sr       # TG
    sp6 = waR * eol_sr       # WS

    ############## RAMP COUNT ---------------------------------[]
    R1RC = daq7.execute(
        'Select count([RAMPosA]) AS ValidTotal from ' + "'" '%' + str(
            T7) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    R2RC = daq8.execute(
        'Select count([RAMPosB]) AS ValidTotal from ' + "'" '%' + str(
            T7) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    R3RC = daq7.execute(
        'Select count([RAMPosC]) AS ValidTotal from ' + "'" '%' + str(
            T7) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    R4RC = daq7.execute(
        'Select count([RAMPosD]) AS ValidTotal from ' + "'" '%' + str(
            T7) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    # close sel link -------
    daq7.close()

    ############## GAP COUNT ---------------------------------[]
    R1VC = daq8.execute(
        'Select count([VODPosA]) AS ValidTotal from ' + "'" '%' + str(
            T8) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    R2VC = daq8.execute(
        'Select count([VODPosB]) AS ValidTotal from ' + "'" '%' + str(
            T8) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    R3VC = daq8.execute(
        'Select count([VODPosC]) AS ValidTotal from ' + "'" '%' + str(
            T8) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    R4VC = daq8.execute(
        'Select count([VODPosD]) AS ValidTotal from ' + "'" '%' + str(
            T8) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()

    # close sel link ----------------------[]
    daq8.close()

    # ------------------ Load randomised samples ----------------------------------------------------------[A]
    dataLP = daq1.execute(
        'Select TOP ' + "'" '%' + str(sp1) + '%' "'" '* FROM ' + "'" '%' + str(T1) + '%' "'" ' where [cLayer] = '
        + "'" '%' + str(layerNo) + '%' "'" + 'order by NEWID()').fetchone()
    # ------------------------------------------------------------------------------------------------------[]
    if len(dataLP) != 0:
        for result in dataLP:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            rLP.append(result)
        # print("Step List1:", len(dL1), dL1)       FIXME:

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq1.close()

    # Tape Winding procedure ----------------------------------[B]
    # ------------------ Load randomised samples ----------------------------------------------------------[A]
    dataLA = daq2.execute(
        'Select TOP ' + "'" '%' + str(sp2) + '%' "'" '* FROM ' + "'" '%' + str(T2) + '%' "'" ' where [cLayer] = '
        + "'" '%' + str(layerNo) + '%' "'" + 'order by NEWID()').fetchone()
    # ------------------------------------------------------------------------------------------------------[]
    if len(dataLA) != 0:
        for result in dataLA:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            rLA.append(result)

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq2.close()

    # ------------------ Load randomised samples ----------------------------------------------------------[A]
    dataTT = daq3.execute(
        'Select TOP ' + "'" '%' + str(sp3) + '%' "'" '* FROM ' + "'" '%' + str(T3) + '%' "'" ' where [cLayer] = '
        + "'" '%' + str(layerNo) + '%' "'" + 'order by NEWID()').fetchone()
    # ------------------------------------------------------------------------------------------------------[]
    if len(dataTT) != 0:
        for result in dataTT:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            rTT.append(result)
        # print("Step List1:", len(dL1), dL1)       FIXME:

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq3.close()

    # ------------------ Load randomised samples ----------------------------------------------------------[A]
    dataST = daq4.execute(
        'Select TOP ' + "'" '%' + str(sp4) + '%' "'" '* FROM ' + "'" '%' + str(T4) + '%' "'" ' where [cLayer] = '
        + "'" '%' + str(layerNo) + '%' "'" + 'order by NEWID()').fetchone()
    # ------------------------------------------------------------------------------------------------------[]
    if len(dataST) != 0:
        for result in dataST:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            rST.append(result)

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq4.close()

    # ------------------ Load randomised samples ----------------------------------------------------------[A]
    dataTG = daq5.execute(
        'Select TOP ' + "'" '%' + str(sp5) + '%' "'" '* FROM ' + "'" '%' + str(T5) + '%' "'" ' where [cLayer] = '
        + "'" '%' + str(layerNo) + '%' "'" + 'order by NEWID()').fetchone()
    # ------------------------------------------------------------------------------------------------------[]
    if len(dataTG) != 0:
        for result in dataTG:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            rTG.append(result)

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq5.close()

    # ------------------ Load randomised samples ----------------------------------------------------------[A]
    dataWA = daq6.execute(
        'Select TOP ' + "'" '%' + str(sp6) + '%' "'" '* FROM ' + "'" '%' + str(T6) + '%' "'" ' where [cLayer] = '
        + "'" '%' + str(layerNo) + '%' "'" + 'order by NEWID()').fetchone()
    # ------------------------------------------------------------------------------------------------------[]
    if len(dataWA) != 0:
        for result in dataWA:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            rWA.append(result)

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq6.close()

    return rLP, rLA, rRP, rTT, rST, rTG, rWA, R1RC, R2RC, R3RC, R4RC, R1VC, R2VC, R3VC, R4VC
