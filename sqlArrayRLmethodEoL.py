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
rTT, rST, rTG, rWS, rWA, rLP, rLA = [], [], [], [], [], [], []

st_id  = 0                                               # SQL start index unless otherwise tracker!
eol_sr = 0.5


def dnv_sqlexec(daq1, daq2, daq3, daq4, T1, T2, T3, T4, layerNo):
    """
    NOTE:
    """

    # Procedure -----------------------------------------------------------------------------------------------[X]
    # -- Find out total number of column record per Ring -----[]
    Ra = daq1.execute(
        'Select count([R1H1TT]) AS ValidTotal from ' + "'" '%' + str(T1) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    Rb = daq1.execute(
        'Select count([R1H1RP]) AS ValidTotal from ' + "'" '%' + str(T2) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    Rc = daq1.execute(
        'Select count([R1H1TP]) AS ValidTotal from ' + "'" '%' + str(T3) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    Rd = daq1.execute(
        'Select count([R1H1WS]) AS ValidTotal from ' + "'" '%' + str(T4) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()

    # --- Compute sampling regime based on data volume -------[]
    sp1 = Ra * eol_sr
    sp2 = Rb * eol_sr
    sp3 = Rc % 60            # Modulo evaluation for Tape Placement
    sp4 = Rd * eol_sr
    # ------------------ Load randomised samples --------------------------------------------------------------[A]
    dataTT = daq1.execute(
        'Select TOP ' + "'" '%' + str(sp1) + '%' "'" '* FROM ' + "'" '%' + str(T1) + '%' "'" ' where [cLayer] = '
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
        'Select TOP ' + "'" '%' + str(sp2) + '%' "'" '* FROM ' + "'" '%' + str(T2) + '%' "'" ' where [cLayer] = '
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
        'Select TOP ' + "'" '%' + str(sp3) + '%' "'" '* FROM ' + "'" '%' + str(T3) + '%' "'" ' where [cLayer] = '
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
        'Select TOP ' + "'" '%' + str(sp4) + '%' "'" '* FROM ' + "'" '%' + str(T4) + '%' "'" ' where [cLayer] = '
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

    return rTT, rST, rTG, rWS, Ra, Rb, Rc, Rd
# -------------------------------------------------------------------------------------------------------[XXXXXXX]


def mgm_sqlexec(daq1, daq2, daq3, daq4, daq5, daq6, T1, T2, T3, T4, T5, T6, layerNo):
    """
    NOTE:
    """

    # Procedure -----------------------------------------------------------------------------------------------[X]
    # -- Find out total number of column record per Ring -----[]
    Ra = daq1.execute(
        'Select count([R1H1TT]) AS ValidTotal from ' + "'" '%' + str(T1) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    Rb = daq2.execute(
        'Select count([R1H1ST]) AS ValidTotal from ' + "'" '%' + str(T2) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    Rc = daq3.execute(
        'Select count([R1H1TG]) AS ValidTotal from ' + "'" '%' + str(T3) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    Rd = daq4.execute(
        'Select count([R4H1WA]) AS ValidTotal from ' + "'" '%' + str(T4) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()
    Re = daq5.execute(
        'Select count([R4H1LP]) AS ValidTotal from ' + "'" '%' + str(T5) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()

    Rf = daq6.execute(
        'Select count([R4H1LA]) AS ValidTotal from ' + "'" '%' + str(T6) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
            layerNo) + '%' "'").fetchone()

    # --- Compute sampling regime based on data volume -------[]
    sp1 = Ra * eol_sr       # TT
    sp2 = Rb * eol_sr       # ST
    sp3 = Rc % 60           # TG
    sp4 = Rd * eol_sr       # WA
    sp5 = Re * eol_sr       # LP
    sp6 = Rf * eol_sr       # LA

    # ------------------ Load randomised samples ----------------------------------------------------------[A]
    dataTT = daq1.execute(
        'Select TOP ' + "'" '%' + str(sp1) + '%' "'" '* FROM ' + "'" '%' + str(T1) + '%' "'" ' where [cLayer] = '
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

    daq1.close()

    # Tape Winding procedure ----------------------------------[B]
    # ------------------ Load randomised samples ----------------------------------------------------------[A]
    dataST = daq2.execute(
        'Select TOP ' + "'" '%' + str(sp2) + '%' "'" '* FROM ' + "'" '%' + str(T2) + '%' "'" ' where [cLayer] = '
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

    daq2.close()

    # ------------------ Load randomised samples ----------------------------------------------------------[A]
    dataTG = daq3.execute(
        'Select TOP ' + "'" '%' + str(sp3) + '%' "'" '* FROM ' + "'" '%' + str(T3) + '%' "'" ' where [cLayer] = '
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
        # print("Step List1:", len(dL1), dL1)       FIXME:

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq3.close()

    # ------------------ Load randomised samples ----------------------------------------------------------[A]
    dataWS = daq4.execute(
        'Select TOP ' + "'" '%' + str(sp4) + '%' "'" '* FROM ' + "'" '%' + str(T4) + '%' "'" ' where [cLayer] = '
        + "'" '%' + str(layerNo) + '%' "'" + 'order by NEWID()').fetchone()
    # ------------------------------------------------------------------------------------------------------[]
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

    # ------------------ Load randomised samples ----------------------------------------------------------[A]
    dataLP = daq5.execute(
        'Select TOP ' + "'" '%' + str(sp5) + '%' "'" '* FROM ' + "'" '%' + str(T5) + '%' "'" ' where [cLayer] = '
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

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    daq5.close()

    # ------------------ Load randomised samples ----------------------------------------------------------[A]
    dataLA = daq6.execute(
        'Select TOP ' + "'" '%' + str(sp6) + '%' "'" '* FROM ' + "'" '%' + str(T6) + '%' "'" ' where [cLayer] = '
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

    daq6.close()

    return rTT, rST, rTG, rWS, rLP, rLA, Ra, Rb, Rc, Rd, Re, Rf
