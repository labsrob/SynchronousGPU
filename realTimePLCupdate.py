# ------------------------------------------------------------------------
# Author: Dr RB Labs
# Developed for Magma Global - TechnipFMC Industrialization
# Email: robbielabs@uwl.ac.uk
# Copyright (C) 2023-2025, Robbie Labs
# ------------------------------------------------------------------------
from pynput.keyboard import Key, Listener

import CommsPlc as pCon
from datetime import datetime
from time import sleep
import os

db_number = 89
start_offset = [900, 68, 18, 22, 26, 30, 2, 6, 10, 14, 34, 38, 42, 46, 50, 54, 58, 62, 902, 904, 906, 908, 910, 912,
                914, 916, 918, 920, 336]
bit_offset = [0, 1, 2, 3, 4, 5, 6, 7]

autoSTOP = False
autoCONN = False

# Perform connection with PLC in real time ------[]
if not autoCONN:
    pCon.connectM2M()
autoCONN = True


def sigmaErrorLog(layer, pID, pX, pD, pU, pL, rID, v1, v2, v3, v4, pPos):
    rtitle = ('============================ TCP01 FMEA Reports ======================================================\n')
    rheader = ('Time'+'\t\t'+'Layer#'+'\t'+'pID'+'\t'+'pMean'+'\t'+'pDev'+'\t'+'UCL'+'\t'+'LCL'+'\t'+'RingID'+'\t'+'Head1'+'\t'+'Head2'+'\t'+'Head3'+'\t'+'Head4'+'\t'+'EstPos'+'\n')
    rdemaca = ("------------------------------------------------------------------------------------------------------\n")
    fileName = datetime.now().strftime('FM_Repo '+"%Y-%m-%d")
    event = datetime.now().strftime("%H:%M.%S")
    SigmaLog = str(fileName)

    filepath = '.\\FMEA_Log\\'+SigmaLog+".txt"
    old_report = os.path.isfile(filepath)

    if not old_report:                                      # if doing a new report...
        f = open('.\\FMEA_Log\\'+SigmaLog+".txt", "a")      # Open new file and ...
        f.write(rtitle)                                     # Insert a Title
        f.write(rheader)                                    # Insert new header
        f.write(rdemaca)                                    # Insert demarcator
    else:                                                   # if it's an existing report
        f = open('.\\FMEA_Log\\' + SigmaLog + ".txt", "a")  # Just open the file for a write operations

    # initialise a tab delimited data and insert corresponding values in string format --------------------------[]
    f.write(event+'\t'+str(layer)+'\t'+pID+'\t'+pX+'\t'+pD+'\t'+pU+'\t'+pL+'\t'+rID+'\t'+str(v1)+'\t'+str(v2)+'\t'+str(v3)+'\t'+str(v4)+'\t'+str(pPos)+'\n')
    f.close()


def get_activeRings():

    try:  # TODO Please validate function and db offsets
        # Get details of the Active Rings only, OEE data is obtainiable from SQL Server Stream
        R1 = pCon.readInteger(db_number, start_offset[18], bit_offset[0])  # Sql Table 1 Ring-1 - 902.0
        R2 = pCon.readInteger(db_number, start_offset[19], bit_offset[0])  # Sql Table 2 Ring-1 - 904.0
        R3 = pCon.readInteger(db_number, start_offset[20], bit_offset[0])  # Sql Table 3 Ring-2 - 906.0
        R4 = pCon.readInteger(db_number, start_offset[21], bit_offset[0])  # Sql Table 4 Ring-2 - 908.0

    except Exception as err:
        print(f"Exception Error: '{err}'")

    return R1, R2, R3, R4


# SQL last processed index if Tables are individually tracked, index-wise ------[]
def recall_last_rt_idx():
    print('Checking Data Index readiness...')
    try:    # SPC processed SQL rows/ index
        idx1 = pCon.readInteger(db_number, start_offset[18], bit_offset[0])  # Sql Table 1 Ring-1 - 902.0
        idx2 = pCon.readInteger(db_number, start_offset[19], bit_offset[0])  # Sql Table 2 Ring-1 - 904.0
        idx3 = pCon.readInteger(db_number, start_offset[20], bit_offset[0])  # Sql Table 3 Ring-2 - 906.0
        idx4 = pCon.readInteger(db_number, start_offset[21], bit_offset[0])  # Sql Table 4 Ring-2 - 908.0
        idx5 = pCon.readInteger(db_number, start_offset[22], bit_offset[0])  # Sql Table 5 Ring-3 - 910.0
        idx6 = pCon.readInteger(db_number, start_offset[23], bit_offset[0])  # Sql Table 6 Ring-3 - 912.0
        idx7 = pCon.readInteger(db_number, start_offset[24], bit_offset[0])  # Sql Table 7 Ring-4 - 914.0
        idx8 = pCon.readInteger(db_number, start_offset[25], bit_offset[0])  # Sql Table 8 Ring-4 - 916.0
    except Exception as err_spcRec:
        print(f"Exception Error: '{err_spcRec}'")

    return idx1, idx2, idx3, idx4, idx5, idx6, idx7, idx8


# PLC current index row reference from SQL Data --------------------------[]
def recall_fromPLC_WON():
    try:
        getWON = pCon.readString(db_number, start_offset[1122], bit_offset[0])
    except Exception as err:
        print(f"Exception Error: '{err}'")

    return getWON


# Send sql index to PLC for recall in the process if needed
def update_procesed_idx(p_1dx, p_2dx, p_3dx, p_4dx, p_5dx, p_6dx, p_7dx, p_8dx):
    try:
        pCon.writeReal(db_number, start_offset[18], p_1dx)   # Sql Table 1 Ring-1 - 902.0
        pCon.writeReal(db_number, start_offset[19], p_2dx)   # Sql Table 2 Ring-1 - 904.0
        pCon.writeReal(db_number, start_offset[20], p_3dx)   # Sql Table 3 Ring-2 - 906.0
        pCon.writeReal(db_number, start_offset[21], p_4dx)   # Sql Table 4 Ring-2 - 908.0
        pCon.writeReal(db_number, start_offset[22], p_5dx)   # Sql Table 5 Ring-3 - 910.0
        pCon.writeReal(db_number, start_offset[23], p_6dx)   # Sql Table 6 Ring-3 - 912.0
        pCon.writeReal(db_number, start_offset[24], p_7dx)   # Sql Table 7 Ring-4 - 914.0
        pCon.writeReal(db_number, start_offset[25], p_8dx)   # Sql Table 8 Ring-4 - 916.0

    except Exception as err:
        print(f"Exception Error: '{err}'")

    return


def stopTCP_Ctrl():
    if not autoSTOP:
        auto_ACK = pCon.readBool(db_number, start_offset[4], bit_offset[2])
    try:
        autoStop = pCon.writeBool(db_number, start_offset[6], bit_offset[3], True)
        pipe_Pos = pCon.readReal(db_number, start_offset[8], bit_offset[0])
    except Exception as err:
        print(f"SPC Stop Read/Write Error: {err}")

    print('Checking machine state at interval...')
    sleep(5)

    return auto_ACK, autoStop, pipe_Pos


def processR1_Sigma(pU, pL, pX, pD, v1, v2, v3, v4, clayer, pPos, pID):
    """
    NOTE: This function must be loaded in a persistent fashion
    :param v1: RIng1 head 1 - result from XBar & S-Plot analysis
    :param v2: Ring1 head 2 - result from XBar & S-Plot analysis
    :param v3: Ring1 head 3 - result from XBar & S-Plot analysis
    :param v4: Ring1 head 4 - result from XBar & S-Plot analysis
    """

    # Obtain runtime settings for SPC take over ------------[]
    # auto_ACK, autoStop, pipe_Pos = stopTCP_Ctrl()
    # Copy discrete pipe position to ring position
    tbl = 'PLC Query'
    try:
        if pID == 'LP':
            SigPid = 3.0
        elif pID == 'LA':
            SigPid = 3.1
        elif pID == 'HT':
            SigPid = 3.2
        elif pID == 'DL':
            SigPid = 3.3

        elif pID == 'RP':
            SigPid = 3.4
        elif pID == 'TT':
            SigPid = 5.0
        elif pID == 'ST':
            SigPid = 7.0
        elif pID == 'TG':
            SigPid = 9.0

        # if md:
        # Write sigma values into PLC data blocks if PLC Query is true ---[]
        pCon.writeReal(db_number, start_offset[6], v1)
        pCon.writeReal(db_number, start_offset[7], v2)
        pCon.writeReal(db_number, start_offset[8], v3)
        pCon.writeReal(db_number, start_offset[9], v4)
        pCon.writeReal(db_number, start_offset[28], SigPid)

    except Exception as err:
        print(f"PLC Write Error: {err}")

    # Read Pipe Discrete Position --------------------------[]
    if clayer==None and pPos==None:
        try:
            layer = pCon.readInteger(db_number, start_offset[0], bit_offset[0])
            pPos = pCon.readReal(db_number, start_offset[1], bit_offset[0])
        except Exception as err:
            print(f"PLC Read Error: {err}")
    else:
        layer = clayer
        pPos = round(pPos, 2)
    ring = 'Ring#1'             # unidirectional convention
    prID = pID                  # String value of process identification

    # Write to FMEA report file ----------------------------[]
    sigmaErrorLog(tbl, layer, prID, str(pX), str(pD), str(pU), str(pL), ring, v1, v2, v3, v4, pPos)

    return


def processR2_Sigma(pU, pL, pX, pD, v1, v2, v3, v4, clayer, pPos, pID, md):
    """
    :param v1: Ring2 head 1 - result from XBar & S-Plot analysis
    :param v2: Ring2 head 2
    :param v3: Ring2 head 3
    :param v4: Ring2 head 4
    """
    # Obtain runtime settings for SPC take over ------------[]
    # auto_ACK, autoStop, pipe_Pos = stopTCP_Ctrl()
    # Copy discrete pipe position to ring position
    tbl = 'PLC Query'
    try:
        if pID == 'LP':
            SigPid = 3.0
        elif pID == 'LA':
            SigPid = 3.1
        elif pID == 'HT':
            SigPid = 3.2
        elif pID == 'DL':
            SigPid = 3.3

        elif pID == 'RP':
            SigPid = 3.4
        elif pID == 'TT':
            SigPid = 5.0
        elif pID == 'ST':
            SigPid = 7.0
        elif pID == 'TG':
            SigPid = 9.0

        if md:
            # Perform realtime update into PLC data blocks if PLC Query is true ---------[]
            pCon.writeReal(db_number, start_offset[2], v1)
            pCon.writeReal(db_number, start_offset[3], v2)
            pCon.writeReal(db_number, start_offset[4], v3)
            pCon.writeReal(db_number, start_offset[5], v4)
            pCon.writeReal(db_number, start_offset[28], SigPid)

    except Exception as err:
        print(f"PLC Write Error: {err}")

    # Read Pipe Discrete Position --------------------------[]
    if clayer==None and pPos==None and md:
        try:
            layer = pCon.readInteger(db_number, start_offset[0], bit_offset[0])
            pPos = pCon.readReal(db_number, start_offset[1], bit_offset[0])
        except Exception as err:
            print(f"PLC Read Error: {err}")
    else:
        layer = clayer
        pPos = round(pPos, 2)
    ring = 'Ring#2'             # unidirectional convention
    prID = pID                  # String value of process identification
    # Write to FMEA report file ----------------------------[]
    sigmaErrorLog(tbl, layer, prID, str(pX), str(pD), str(pU), str(pL), ring, v1, v2, v3, v4, pPos)

    return


def processR3_Sigma(pU, pL, pX, pD, v1, v2, v3, v4, clayer, pPos, pID, md):
    """
    :param v9: Ring3 head 1 - result from XBar & S-Plot analysis
    :param v10: Ring3 head 2
    :param v11: Ring3 head 3
    :param v12: Ring3 head 4
    """
    # Obtain runtime settings for SPC take over ------------[]
    # auto_ACK, autoStop, pipe_Pos = stopTCP_Ctrl()
    # Copy discrete pipe position to ring position
    tbl = 'PLC Query'

    try:
        if pID == 'LP':
            SigPid = 3.0
        elif pID == 'LA':
            SigPid = 3.1
        elif pID == 'HT':
            SigPid = 3.2
        elif pID == 'DL':
            SigPid = 3.3

        elif pID == 'RP':
            SigPid = 3.4
        elif pID == 'TT':
            SigPid = 5.0
        elif pID == 'ST':
            SigPid = 7.0
        elif pID == 'TG':
            SigPid = 9.0

        if md:
            # Perform realtime update into PLC data blocks if PLC Query is true ---------[]
            pCon.writeReal(db_number, start_offset[10], v1)
            pCon.writeReal(db_number, start_offset[11], v2)
            pCon.writeReal(db_number, start_offset[12], v3)
            pCon.writeReal(db_number, start_offset[13], v4)
            pCon.writeReal(db_number, start_offset[28], SigPid)

    except Exception as err:
        print(f"PLC Write Error: {err}")

    # Read Pipe Discrete Position --------------------------[]
    if clayer==None and pPos==None and md:
        try:
            layer = pCon.readInteger(db_number, start_offset[0], bit_offset[0])
            pPos = pCon.readReal(db_number, start_offset[1], bit_offset[0])
        except Exception as err:
            print(f"PLC Read Error: {err}")
    else:
        layer = clayer
        pPos = round(pPos, 2)
    ring = 'Ring#3'                 # unidirectional convention
    prID = pID                      # String value of process identification

    # Write to FMEA report file ----------------------------[]
    sigmaErrorLog(tbl, layer, prID, str(pX), str(pD), str(pU), str(pL), ring, v1, v2, v3, v4, pPos)

    return


def processR4_Sigma(pU, pL, pX, pD, v1, v2, v3, v4, clayer, pPos, pID, md):
    """
    :param v13: Ring4 head 1 - result from XBar & S-Plot analysis
    :param v14: Ring4 head 2 - result from XBar & S-Plot analysis
    :param v15: Ring4 head 3 - result from XBar & S-Plot analysis
    :param v16: Ring4 head 4 - result from XBar & S-Plot analysis
    """
    # Obtain runtime settings for SPC take over ------------[]
    # auto_ACK, autoStop, pipe_Pos = stopTCP_Ctrl()
    # Copy discrete pipe position to ring position
    tbl = 'PLC Query'

    try:
        if pID == 'LP':
            SigPid = 3.0
        elif pID == 'LA':
            SigPid = 3.1
        elif pID == 'HT':
            SigPid = 3.2
        elif pID == 'DL':
            SigPid = 3.3

        elif pID == 'RP':
            SigPid = 3.4
        elif pID == 'TT':
            SigPid = 5.0
        elif pID == 'ST':
            SigPid = 7.0
        elif pID == 'TG':
            SigPid = 9.0

        if md:
            # Perform realtime update into PLC data blocks if PLC Query is true ---------[]
            pCon.writeReal(db_number, start_offset[14], v1)
            pCon.writeReal(db_number, start_offset[15], v2)
            pCon.writeReal(db_number, start_offset[16], v3)
            pCon.writeReal(db_number, start_offset[17], v4)
            pCon.writeReal(db_number, start_offset[28], SigPid)

    except Exception as err:
        print(f"PLC Write Error: {err}")

    # Read Pipe Discrete Position --------------------------[]
    if clayer==None and pPos==None and md:
        try:
            layer = pCon.readInteger(db_number, start_offset[0], bit_offset[0])
            pPos = pCon.readReal(db_number, start_offset[1], bit_offset[0])
        except Exception as err:
            print(f"PLC Read Error: {err}")
    else:
        layer = clayer
        pPos = round(pPos, 2)
    ring = 'Ring#4'                 # unidirectional convention
    prID = pID                      # String value of process identification

    # Write to FMEA report file ----------------------------[]
    sigmaErrorLog(tbl, layer, prID, str(pX), str(pD), str(pU), str(pL), ring, v1, v2, v3, v4, pPos)

    return
