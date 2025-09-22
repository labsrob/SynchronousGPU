# This script is called in from Main program to load SQL execution syntax command and return a list in LisDat
# Author: Dr Labs, RB
from collections import deque
from itertools import count
from datetime import datetime, timedelta
import time



UseRowIndex = True
idx = count()
now = datetime.now()

dataList0 = []
rTT, rST, rTG, rWS, rPP = [], [], [], [], []            # DNV
rLP, rLA, rTT, rST, rTG, rWA, rPP = [], [], [], [], [], [], []   # MGM


def dnv_sqlExec(sq_con, T1, T2, T3, T4, T5, layerNo):
    """
    NOTE:
    """
    t1, t2, t3, t4, t5 = sq_con.cursor(), sq_con.cursor(), sq_con.cursor(), sq_con.cursor(), sq_con.cursor()

    # ------------------ Load randomised samples --------------------------------------------------------------[A]
    if len(rTT) > 0:    # clean up accumulator
        del rTT[:]
    dataTT = t1.execute('Select * FROM ' + str(T1) + ' where [LyIDa] = ' + str(layerNo)).fetchall()
    # print('TP00', dataTT)
    if len(dataTT) != 0:
        for result in dataTT:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            rTT.append(result)
        # print("\nStep List1 @"+str(layerNo)+':', len(rTT), rTT, '\n')  # FIXME:

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    t1.close()

    # Substrate Temperature --------------------------------------------------------------------------------[B]
    if len(rST) > 0:    # clean up accumulator
        del rST[:]
    dataST = t2.execute('Select * FROM ' + str(T2) + ' where [LyIDb] = ' + str(layerNo)).fetchall()
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
    if len(rTG) > 0:    # clean up accumulator
        del rTG[:]
    dataTG = t3.execute('Select * FROM ' + str(T3) + ' where [LyIDc] = ' + str(layerNo)).fetchall()
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
    if len(rWS) > 0:    # clean up accumulator
        del rWS[:]
    if T4[0:4] == 'WS_':
        dataWS = t4.execute('Select * FROM ' + str(T4) + ' where [LyIDd] = ' + str(layerNo)).fetchall()
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

    # Pipe Profile ------------------------------------------------------------------------------------------[D]
    if len(rPP) > 0:    # clean up accumulator
        del rPP[:]
    dataPP = t5.execute('Select * FROM ' + str(T5) + ' where [LyID] = ' + str(layerNo)).fetchall()
    print('TP-SQL', len(dataPP), dataPP)
    if len(dataPP) != 0:
        for result in dataPP:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            rPP.append(result)

        # print("Step List1:", len(dL1), dL1)       FIXME:

    else:
        dataPP = 0, 0, 0, 0, 0, 0, 0, 0, 0
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    t5.close()


    return rTT, rST, rTG, rWS, rPP
# -------------------------------------------------------------------------------------------------------[XXXXXXX]


def mgm_sqlExec(sq_con, T1, T2, T3, T4, T5, T6, layerNo):
    """
    NOTE:
    """
    t1, t2, t3, t4, t5, t6 = sq_con.cursor(), sq_con.cursor(), sq_con.cursor(), sq_con.cursor(), sq_con.cursor(), sq_con.cursor()

    # ------------------ Load randomised samples --------------------------------------------------------------[A]
    if len(rLP) > 0:  # clean up accumulator
        del rLP[:]
    dataLP = t1.execute('Select * FROM ' + str(T1) + ' where [LyID] = ' + str(layerNo)).fetchall()
    # print('TP00', dataTT)
    if len(dataLP) != 0:
        for result in dataLP:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            rLP.append(result)
        # print("Step List1:", len(rTT), rTT)  #      FIXME:

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    t1.close()

    # Laser Angle  --------------------------------------------------------------------------------[B]
    if len(rLA) > 0:  # clean up accumulator
        del rLA[:]
    dataLA = t2.execute('Select * FROM ' + str(T2) + ' where [LyID] = ' + str(layerNo)).fetchall()
    if len(dataLA) != 0:
        for result in dataLA:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            rLA.append(result)

        # print("Step List1:", len(dL1), dL1)       FIXME:

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    t2.close()

    # Tape Temperature --------------------------------------------------------------------------------[B]
    if len(rTT) > 0:  # clean up accumulator
        del rTT[:]
    dataTT = t3.execute('Select * FROM ' + str(T3) + ' where [LyID] = ' + str(layerNo)).fetchall()
    if len(dataTT) != 0:
        for result in dataTT:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            rTT.append(result)

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    t3.close()

    # Substrate Temperature --------------------------------------------------------------------------[D]
    if len(rST) > 0:  # clean up accumulator
        del rST[:]
    dataST = t4.execute('Select * FROM ' + str(T4) + ' where [LyID] = ' + str(layerNo)).fetchall()
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

    # Tape Gap Procedure ------------------------------------------------------------------------------------[C]
    if len(rTG) > 0:  # clean up accumulator
        del rTG[:]
    dataTG = t5.execute('Select * FROM ' + str(T5) + ' where [LyID] = ' + str(layerNo)).fetchall()
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

    # Ramp Profile ------------------------------------------------------------------------------------------[D]
    if len(rWA) > 0:  # clean up accumulator
        del rWA[:]
    if T4[0:4] == 'ZWA_':
        dataWA = t6.execute('Select * FROM ' + str(T6) + ' where [LyID] = ' + str(layerNo)).fetchall()
        if len(dataWA) != 0:
            for result in dataWA:
                result = list(result)
                if UseRowIndex:
                    dataList0.append(next(idx))
                else:
                    now = time.strftime("%H:%M:%S")
                    dataList0.append(time.strftime(now))
                rWA.append(result)
            # print("Step List1:", len(dL1), dL1)       FIXME:

        else:
            print('Process EOF reached...')
            print('SPC Halting for 5 Minutes...')
            time.sleep(5)
        t6.close()

    return rLP, rLA, rTT, rST, rTG, rWA
# -------------------------------------------------------------------------------------------------------[XXXXXXX]
