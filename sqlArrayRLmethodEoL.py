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


def dnv_sqlExec(sq_con, layerNo, ttSoL, stSoL, tgSoL, wsSoL, T1, T2, T3, T4):
    """
    NOTE:
    """
    t1, t2, t3, t4 = sq_con.cursor(), sq_con.cursor(), sq_con.cursor(), sq_con.cursor()

    # Determine EOL sampling regime ---------------------------------------------------------------[X]
    # -- Find out total number of column record per Ring -----[]
    ttSR = t1.execute('Select count([R1SPa]) AS ValidTotal from ' + str(T1) + ' where [LyIDa] = ' + str(layerNo)).fetchone()
    # close sel link -------[ZTT_]
    t1.close()

    stSR = t2.execute('Select count([R1SPb]) AS ValidTotal from ' + str(T2) + ' where [LyIDb] = ' + str(layerNo)).fetchone()
    # close sel link -------[ZST_]
    t2.close()

    tgSR = t3.execute('Select count([R1SPc]) AS ValidTotal from ' + str(T3) + ' where [LyIDc] = ' + str(layerNo)).fetchone()
    # close sel link -------[ZTG_]
    t3.close()

    wsSR = t4.execute('Select count([R1SPd]) AS ValidTotal from ' + str(T4) + ' where [LyIDd] = ' + str(layerNo)).fetchone()
    # close sel link -------[ZWS_]
    t4.close()

    # --- Compute random sampling regime based on data volume -------[TODO: recheck the sampler method]
    regm1 = ttSR * ttSoL
    regm2 = stSR * stSoL
    regm3 = tgSR * tgSoL      # % 60  # Modulo evaluation TG?
    regm4 = wsSR * wsSoL

    # ------------------ Load randomised samples --------------------------------------------------------------[A]
    dataTT = t1.execute('Select TOP ' + str(regm1) + ' * FROM ' + str(T1) + ' where [cLayer] = '+ str(layerNo) + ' order by NEWID()').fetchall()
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
    t1.close()

    # Substrate Temperature --------------------------------------------------------------------------------[B]
    dataST = t2.execute('Select TOP ' + str(regm2) + ' * FROM ' + str(T2) + ' where [cLayer] = '+ str(layerNo) + ' order by NEWID()').fetchall()

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

    t2.close()

    # Tape Gap Procedure ------------------------------------------------------------------------------------[C]
    dataTG = t3.execute('Select TOP ' + str(regm3) + ' * FROM ' + str(T3) + ' where [cLayer] = '+ str(layerNo) + ' order by NEWID()').fetchall()
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
    t3.close()

    # Ramp Profile ------------------------------------------------------------------------------------------[D]
    dataWS = t4.execute('Select TOP ' + str(regm4) + ' * FROM ' + str(T4) + ' where [cLayer] = '+ str(layerNo) + ' order by NEWID()').fetchall()
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

    t4.close()

    return rTT, rST, rTG, rWS
# -------------------------------------------------------------------------------------------------------[XXXXXXX]


def mgm_sqlExec(sq_con, lpSoL, laSoL, ttSoL, stSoL, tgSoL, waSoL, T1, T2, T3, T4, T5, T6, layerNo):
    """
    NOTE:
    """
    t1, t2, t3, t4, t5, t6 = sq_con.cursor(), sq_con.cursor(), sq_con.cursor(), sq_con.cursor(), sq_con.cursor(), sq_con.cursor()

    # Procedure -----------------------------------------------------------------------------------------------[X]
    # -- Find out total number of column record per Ring -----[]
    lpR = t1.execute(
        'Select count([R1H1LP]) AS ValidTotal from '+ str(T1) + '%' "'" ' where [cLayer] = ' + str(layerNo)).fetchone()
    # close sel link -------[]
    t1.close()

    laR = t2.execute(
        'Select count([R1H1LA]) AS ValidTotal from ' + str(T2) + ' where [cLayer] = ' + str(layerNo)).fetchone()
    # close sel link -------[]
    t2.close()

    ttR = t3.execute(
        'Select count([R4H1TT]) AS ValidTotal from ' + str(T3) + ' where [cLayer] = ' + str(layerNo)).fetchone()
    # close sel link -------[]
    t3.close()

    stR = t4.execute(
        'Select count([R4H1ST]) AS ValidTotal from ' + str(T4) + ' where [cLayer] = ' + str(layerNo)).fetchone()
    # close sel link -------[]
    t4.close()

    tgR = t5.execute(
        'Select count([R4H1TG]) AS ValidTotal from ' + str(T5) + ' where [cLayer] = ' + str(layerNo)).fetchone()
    # close sel link -------[]
    t5.close()

    waR = t6.execute(
        'Select count([R4H1WA]) AS ValidTotal from ' + str(T6) +  ' where [cLayer] = ' + str(layerNo)).fetchone()
    # close sel link -------[]
    t6.close()

    # --- Compute sampling regime based on data volume -------[]
    sp1 = lpR * lpSoL       # LP
    sp2 = laR * laSoL       # LA
    sp3 = ttR * ttSoL       # TT
    sp4 = stR * stSoL       # ST
    sp5 = tgR * tgSoL       # TG
    sp6 = waR * waSoL       # WS

    ############## RAMP COUNT ---------------------------------[]
    # R1RC = daq7.execute(
    #     'Select count([RAMPosA]) AS ValidTotal from ' + str(T7) + ' where [cLayer] = ' + str(layerNo)).fetchone()
    # R2RC = daq8.execute(
    #     'Select count([RAMPosB]) AS ValidTotal from ' + str(T7) + ' where [cLayer] = ' + str(layerNo)).fetchone()
    # R3RC = daq7.execute(
    #     'Select count([RAMPosC]) AS ValidTotal from ' + str(T7) + ' where [cLayer] = ' + str(layerNo)).fetchone()
    # R4RC = daq7.execute(
    #     'Select count([RAMPosD]) AS ValidTotal from ' + str(T7) + ' where [cLayer] = ' + str(layerNo)).fetchone()
    # # close sel link -------
    # daq7.close()
    #
    # ############## GAP COUNT ---------------------------------[]
    # R1VC = daq8.execute(
    #     'Select count([VODPosA]) AS ValidTotal from ' + "'" '%' + str(
    #         T8) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
    #         layerNo) + '%' "'").fetchone()
    # R2VC = daq8.execute(
    #     'Select count([VODPosB]) AS ValidTotal from ' + "'" '%' + str(
    #         T8) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
    #         layerNo) + '%' "'").fetchone()
    # R3VC = daq8.execute(
    #     'Select count([VODPosC]) AS ValidTotal from ' + "'" '%' + str(
    #         T8) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
    #         layerNo) + '%' "'").fetchone()
    # R4VC = daq8.execute(
    #     'Select count([VODPosD]) AS ValidTotal from ' + "'" '%' + str(
    #         T8) + '%' "'" ' where [cLayer] = ' + "'" '%' + str(
    #         layerNo) + '%' "'").fetchone()
    #
    # # close sel link ----------------------[]
    # daq8.close()

    # ------------------ Load randomised samples ----------------------------------------------------------[A]
    dataLP = t1.execute(
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

    t1.close()

    # Tape Winding procedure ----------------------------------[B]
    # ------------------ Load randomised samples ----------------------------------------------------------[A]
    dataLA = t2.execute(
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

    t2.close()

    # ------------------ Load randomised samples ----------------------------------------------------------[A]
    dataTT = t3.execute(
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

    t3.close()

    # ------------------ Load randomised samples ----------------------------------------------------------[A]
    dataST = t4.execute(
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

    t4.close()

    # ------------------ Load randomised samples ----------------------------------------------------------[A]
    dataTG = t5.execute(
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

    t5.close()

    # ------------------ Load randomised samples ----------------------------------------------------------[A]
    dataWA = t6.execute(
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

    t6.close()

    return rLP, rLA, rTT, rST, rTG, rWA
