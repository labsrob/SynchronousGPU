# This script is called in from Main program to load SQL execution syntax command and return a list in LisDat
# Author: Dr Labs, RB
from collections import deque
from itertools import count
from datetime import datetime, timedelta
import time
import pyodbc

# ------------------------------
server_IP = '10.0.3.172'
db_ref = 'DAQ_sSPC'
isAtho = 'TCP01'
yekref = 'Testing27!'
Encrypt = 'no'                  # Added today 06/08/2024 [optional]
Certify = 'yes'
# -----------------------------

UseRowIndex = True
idx = count()
now = datetime.now()

dataList0 = []
rLP, rLA, rRP, rTT, rST, rTG, rWA, rWS, rPP = [], [], [], [], [], [], [], [], []

st_id  = 0                                               # SQL start index unless otherwise tracker!
eol_sr = 0.5
# ------------ PDF Generator Method ---------------------------------------------------------

def rpt_SQLconnect():
    """
    state: 1 connected, 0 Not connected
    agent: 1 indicate SCADA remote call, 0 indicating SPC local User Call
    """
    # print('\nDatasource Details:', server_IP, db_ref)
    # -------- Actual SQL Connection request -----------------#
    conn = None
    # ---------------------------------------------------------#
    if conn == None:
        print('\n[EoL] Connecting to SQL server...')

        try:
            conn = pyodbc.connect('Driver={SQL Server};'
                                  'Server=' + server_IP + ';'
                                  'Database=' + db_ref + ';'
                                  'Encrypt=' + Encrypt + ';'
                                  'TrustServerCertificate=' + Certify + ';'
                                  'uid=' + isAtho + ';'
                                  'pwd=' + yekref + ';'
                                  'MultipleActiveResultSets=True', timeout=5, autocommit=True)
            # conn = True
            print('\n[EoL] SQL Server connection active!\n')
            return conn

        except Exception as err:
            print('\n[EoL] Connection issue: SQL Server is inaccessible!')

    return None


def dnv_sqlExec(sq_con, T1, T2, T3, T4, T5, T6, layerNo):
    """
    NOTE:
    """
    # Provide critical and robust connection for End of Layer report
    if sq_con is None:
        tempo = rpt_SQLconnect()
        mainStream = True
        print('\nUsing a new param connection..')
    else:
        mainStream = False
        tempo = sq_con
        print('\nUsing mainstream connection..')
    # --------------------------------------
    t1, t2 = tempo.cursor(), tempo.cursor()
    t3, t4 = tempo.cursor(), tempo.cursor()
    t5, t6 = tempo.cursor(), tempo.cursor()

    # Enabling Table level sampling regime for performance level improvement ------------------------[X]
    """
    NOTE: SQL Server Regression Issues acknowledge by Microsoft.
    Table level resampling enabled. 
    """
    print('Processing Layer Number:', layerNo)
    lpSR = t1.execute('Select count([R1SP]) AS ValidTotal from ' + str(T1) +' where [cLyr] = ' + str(layerNo)).fetchone()
    # close sel link -------[ZLP_]
    ttSR = t2.execute('Select count([R1SP]) AS ValidTotal from ' + str(T2) +' where [cLyr] = ' + str(layerNo)).fetchone()
    # close sel link -------[ZTT_]
    stSR = t3.execute('Select count([R1SP]) AS ValidTotal from ' + str(T3) +' where [cLyr] = ' + str(layerNo)).fetchone()
    # close sel link -------[ZST_]
    tgSR = t4.execute('Select count([R1SP]) AS ValidTotal from ' + str(T4) +' where [cLyr] = ' + str(layerNo)).fetchone()
    # close sel link -------[ZTG_]
    wsSR = t4.execute('Select count([R1SP]) AS ValidTotal from ' + str(T5) + ' where [cLyr] = ' + str(layerNo)).fetchone()
    # close sel link -------[ZWS_]

    # --- Compute random sampling regime based on data volume -------[TODO: recheck the sampler method]
    regm1 = round(lpSR[0] * 0.3, )
    regm2 = round(ttSR[0] * 0.3, )
    regm3 = round(stSR[0] * 0.3, )      # % 60?  # Modulo evaluation TG?
    regm4 = round(tgSR[0] * 0.3, )
    regm5 = round(wsSR[0] * 0.3, )
    print('TP0002', regm1, regm2, regm3,regm4, regm5)

    # ------------------ Load randomised samples --------[TODO: Evaluate the impact oA]f these two methods on sys perf
    dataLP = t1.execute('Select TOP ' + str(regm1) + ' * FROM ' + str(T1) + ' where [cLyr] = '+ str(layerNo) + ' order by NEWID()').fetchall()
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

    if not mainStream:
        t1.close()

    # ----------------------------------------------------------------------------------------------------
    dataTT = t2.execute('Select TOP ' + str(regm2) + ' * FROM ' + str(T2) + ' where [cLyr] = ' + str(
        layerNo) + ' order by NEWID()').fetchall()
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

    if not mainStream:
        t2.close()

    # Substrate Temperature --------------------------------------------------------------------------------[B]
    dataST = t3.execute('Select TOP ' + str(regm3) + ' * FROM ' + str(T3) + ' where [cLyr] = '+ str(layerNo) + ' order by NEWID()').fetchall()
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

    if not mainStream:
        t3.close()

    # Tape Gap Procedure ------------------------------------------------------------------------------------[C]
    dataTG = t4.execute('Select TOP ' + str(regm4) + ' * FROM ' + str(T4) + ' where [cLyr] = '+ str(layerNo) + ' order by NEWID()').fetchall()
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

    if not mainStream:
        t4.close()

    # Ramp Profile ------------------------------------------------------------------------------------------[D]
    dataWS = t5.execute('Select TOP ' + str(regm5) + ' * FROM ' + str(T5) + ' where [cLyr] = '+ str(layerNo) + ' order by NEWID()').fetchall()
    if len(dataWS) != 0:
        for result in dataWS:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            rWS.append(result)

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    if not mainStream:
        t5.close()

    # Pipe Properties Profile ------------------------------------------------------------------------------------------[D]
    dataPP = t6.execute('Select * FROM ' + str(T6) + ' where [cLyr] = '+ str(layerNo)).fetchall()
    if len(dataPP) != 0:
        for result in dataPP:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            rPP.append(result)

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)

    if not mainStream:
        t6.close()

    return rLP, rTT, rST, rTG, rWS, rPP
# -------------------------------------------------------------------------------------------------------[XXXXXXX]
