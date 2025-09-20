# ------------------------------------------------------------------------
# Author: Dr RB Labs
# Developed for Magma Global - TechnipFMC Industrialization
# Email: robbielabs@uwl.ac.uk
# Copyright (C) 2023-2025, Robbie Labs
# ------------------------------------------------------------------------
from datetime import datetime
import os
processWON = []

def sigmaExLP(md, layer, pID, pX, pD, pU, pL, rID, v1, v2, v3, v4, pPos):
    """
    md : SQL called | PLC called
    """
    Wkord = str(processWON[0])

    rtitle = ('============================ Sigma Exceptions ('+pID+') - ['+ md +'] - WO# '+ str(Wkord)+' ======================================\n')
    rheader = ('Time'+'\t\t'+'Layer#'+'\t'+'pMean'+'\t'+'pDev'+'\t'+'UCL'+'\t'+'LCL'+'\t'+'RingID'+'\t'+'Head1'+'\t'+'Head2'+'\t'+'Head3'+'\t'+'Head4'+'\t'+'EstPos'+'\n')
    rdemaca = ("--------------------------------------------------------------------------------------------------------------\n")
    fileName = datetime.now().strftime('RPT_'+pID+'_'+Wkord)
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
    f.write(event+'\t'+str(layer)+'\t'+pX+'\t'+pD+'\t'+pU+'\t'+pL+'\t'+rID+'\t'+str(v1)+'\t'+str(v2)+'\t'+str(v3)+'\t'+str(v4)+'\t'+str(pPos)+'\n')
    f.close()
# ------------------------------
def sigmaExLA(md, layer, pID, pX, pD, pU, pL, rID, v1, v2, v3, v4, pPos):
    """
    md : SQL called | PLC called
    """
    Wkord = str(processWON[0])

    rtitle = ('============================ Sigma Exceptions ('+pID+') - ['+ md +'] - WO# '+ str(Wkord)+' ======================================\n')
    rheader = ('Time'+'\t\t'+'Layer#'+'\t'+'pMean'+'\t'+'pDev'+'\t'+'UCL'+'\t'+'LCL'+'\t'+'RingID'+'\t'+'Head1'+'\t'+'Head2'+'\t'+'Head3'+'\t'+'Head4'+'\t'+'EstPos'+'\n')
    rdemaca = ("--------------------------------------------------------------------------------------------------------------\n")
    fileName = datetime.now().strftime('RPT_'+pID+'_'+Wkord)
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
    f.write(event+'\t'+str(layer)+'\t'+pX+'\t'+pD+'\t'+pU+'\t'+pL+'\t'+rID+'\t'+str(v1)+'\t'+str(v2)+'\t'+str(v3)+'\t'+str(v4)+'\t'+str(pPos)+'\n')
    f.close()
# --------------------------
def sigmaExRF(md, layer, pID, pX, pD, pU, pL, rID, v1, v2, v3, v4, pPos):
    """
    md : SQL called | PLC called
    """
    Wkord = str(processWON[0])

    rtitle = ('============================ Sigma Exceptions ('+pID+') - ['+ md +'] - WO# '+ str(Wkord)+' ======================================\n')
    rheader = ('Time'+'\t\t'+'Layer#'+'\t'+'pMean'+'\t'+'pDev'+'\t'+'UCL'+'\t'+'LCL'+'\t'+'RingID'+'\t'+'Head1'+'\t'+'Head2'+'\t'+'Head3'+'\t'+'Head4'+'\t'+'EstPos'+'\n')
    rdemaca = ("--------------------------------------------------------------------------------------------------------------\n")
    fileName = datetime.now().strftime('RPT_'+pID+'_'+Wkord)
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
    f.write(event+'\t'+str(layer)+'\t'+pX+'\t'+pD+'\t'+pU+'\t'+pL+'\t'+rID+'\t'+str(v1)+'\t'+str(v2)+'\t'+str(v3)+'\t'+str(v4)+'\t'+str(pPos)+'\n')
    f.close()
# ------------------------
def sigmaExTT(md, layer, pID, pX, pD, pU, pL, rID, v1, v2, v3, v4, pPos):
    """
    md : SQL called | PLC called
    """
    Wkord = str(processWON[0])

    rtitle = ('============================ Sigma Exceptions ('+pID+') - ['+ md +'] - WO# '+ str(Wkord)+' ======================================\n')
    rheader = ('Time'+'\t\t'+'Layer#'+'\t'+'pMean'+'\t'+'pDev'+'\t'+'UCL'+'\t'+'LCL'+'\t'+'RingID'+'\t'+'Head1'+'\t'+'Head2'+'\t'+'Head3'+'\t'+'Head4'+'\t'+'EstPos'+'\n')
    rdemaca = ("--------------------------------------------------------------------------------------------------------------\n")
    fileName = datetime.now().strftime('RPT_'+pID+'_'+Wkord)
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
    f.write(event+'\t'+str(layer)+'\t'+pX+'\t'+pD+'\t'+pU+'\t'+pL+'\t'+rID+'\t'+str(v1)+'\t'+str(v2)+'\t'+str(v3)+'\t'+str(v4)+'\t'+str(pPos)+'\n')
    f.close()
# ----------------------------
def sigmaExST(md, layer, pID, pX, pD, pU, pL, rID, v1, v2, v3, v4, pPos):
    """
    md : SQL called | PLC called
    """
    Wkord = str(processWON[0])

    rtitle = ('============================ Sigma Exceptions ('+pID+') - ['+ md +'] - WO# '+ str(Wkord)+' ======================================\n')
    rheader = ('Time'+'\t\t'+'Layer#'+'\t'+'pMean'+'\t'+'pDev'+'\t'+'UCL'+'\t'+'LCL'+'\t'+'RingID'+'\t'+'Head1'+'\t'+'Head2'+'\t'+'Head3'+'\t'+'Head4'+'\t'+'EstPos'+'\n')
    rdemaca = ("--------------------------------------------------------------------------------------------------------------\n")
    fileName = datetime.now().strftime('RPT_'+pID+'_'+Wkord)
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
    f.write(event+'\t'+str(layer)+'\t'+pX+'\t'+pD+'\t'+pU+'\t'+pL+'\t'+rID+'\t'+str(v1)+'\t'+str(v2)+'\t'+str(v3)+'\t'+str(v4)+'\t'+str(pPos)+'\n')
    f.close()
# ----------------------------
def sigmaExTG(md, layer, pID, pX, pD, pU, pL, rID, v1, v2, v3, v4, pPos):
    """
    md : SQL called | PLC called
    """
    Wkord = str(processWON[0])

    rtitle = ('============================ Sigma Exceptions ('+pID+') - ['+ md +'] - WO# '+ str(Wkord)+' ======================================\n')
    rheader = ('Time'+'\t\t'+'Layer#'+'\t'+'pMean'+'\t'+'pDev'+'\t'+'UCL'+'\t'+'LCL'+'\t'+'RingID'+'\t'+'Head1'+'\t'+'Head2'+'\t'+'Head3'+'\t'+'Head4'+'\t'+'EstPos'+'\n')
    rdemaca = ("--------------------------------------------------------------------------------------------------------------\n")
    fileName = datetime.now().strftime('RPT_'+pID+'_'+Wkord)
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
    f.write(event+'\t'+str(layer)+'\t'+pX+'\t'+pD+'\t'+pU+'\t'+pL+'\t'+rID+'\t'+str(v1)+'\t'+str(v2)+'\t'+str(v3)+'\t'+str(v4)+'\t'+str(pPos)+'\n')
    f.close()
# ----------------------------

def recall_fromSQL_WON(pWON):
    """
    This function is called on bu main program to receive t WON before updating FMEA report
    """
    getWON = pWON
    # prevent persistent call; i.e call once and get the WON updated into an array
    if not processWON:
        processWON.append(getWON)
        print('\nTPB', processWON)
    else:
        pass

    return


def LaserPowerSigma(pU, pL, pX, pD, v1, v2, v3, v4, clayer, pPos, pID, md):
    """
    md : Mode Processing (i.e SQL/PLC Query)
    """
    # Obtain runtime settings for SPC take over ------------[]
    try:
        if md == 1:
            tbl = 'PLC Query'
        else:
            tbl = 'SQL Query'

        layer = clayer
        pPos = round(pPos, 2)
        ring = 'Ring#1'                 # unidirectional convention
        prID = pID                      # String value of process identification

        # Write to FMEA report file ------------------------------------------------------------[]
        sigmaExLP(tbl, str(layer), str(prID), str(pX), str(pD), str(pU), str(pL), ring, v1, v2, v3, v4, pPos)

    except Exception as err:
        print(f"Update Data Write Error: {err}")

    return


def LaserAngleSigma(pU, pL, pX, pD, v1, v2, v3, v4, clayer, pPos, pID, md):
    """
       md : Mode Processing (i.e SQL/PLC Query)
       """
    # Obtain runtime settings for SPC take over ------------[]
    try:
        if md == 1:
            tbl = 'PLC Query'
        else:
            tbl = 'SQL Query'
        layer = clayer
        pPos = round(pPos, 2)
        ring = 'Ring#2'         # unidirectional convention
        prID = pID              # String value of process identification

        # Write to FMEA report file ------------------------------------------------------------[]
        sigmaExLA(tbl, layer, prID, str(pX), str(pD), str(pU), str(pL), ring, v1, v2, v3, v4, pPos)

    except Exception as err:
        print(f"Update Data Write Error: {err}")

    return


def RollerForceSigma(pU, pL, pX, pD, v1, v2, v3, v4, clayer, pPos, pID, md):
    """
       md : Mode Processing (i.e SQL/PLC Query)
       """
    # Obtain runtime settings for SPC take over ------------[]
    try:
        if md == 1:
            tbl = 'PLC Query'
        else:
            tbl = 'SQL Query'
        layer = clayer
        pPos = round(pPos, 2)
        ring = 'Ring#3'         # unidirectional convention
        prID = pID              # String value of process identification

        # Write to FMEA report file ------------------------------------------------------------[]
        sigmaExRF(tbl, layer, prID, str(pX), str(pD), str(pU), str(pL), ring, v1, v2, v3, v4, pPos)

    except Exception as err:
        print(f"Update Data Write Error: {err}")

    return


def TapeTempSigma(pU, pL, pX, pD, v1, v2, v3, v4, clayer, pPos, pID, md):
    """
       md : Mode Processing (i.e SQL/PLC Query)
       """
    # Obtain runtime settings for SPC take over ------------[]
    try:
        if md == 1:
            tbl = 'PLC Query'
        else:
            tbl = 'SQL Query'
        layer = clayer
        pPos = round(pPos, 2)
        ring = 'Ring#4'             # unidirectional convention
        prID = pID                  # String value of process identification

        # Write to FMEA report file ------------------------------------------------------------[]
        sigmaExTT(tbl, layer, prID, str(pX), str(pD), str(pU), str(pL), ring, v1, v2, v3, v4, pPos)

    except Exception as err:
        print(f"Update Data Write Error: {err}")

    return

def DeltaTempSigma(pU, pL, pX, pD, v1, v2, v3, v4, clayer, pPos, pID, md):
    """
       md : Mode Processing (i.e SQL/PLC Query)
       """
    # Obtain runtime settings for SPC take over ------------[]
    try:
        if md == 1:
            tbl = 'PLC Query'
        else:
            tbl = 'SQL Query'
        layer = clayer
        pPos = round(pPos, 2)
        ring = 'Ring#4'             # unidirectional convention
        prID = pID                  # String value of process identification

        # Write to FMEA report file ------------------------------------------------------------[]
        sigmaExST(tbl, layer, prID, str(pX), str(pD), str(pU), str(pL), ring, v1, v2, v3, v4, pPos)

    except Exception as err:
        print(f"Update Data Write Error: {err}")

    return

def TapeGapSigma(pU, pL, pX, pD, v1, v2, v3, v4, clayer, pPos, pID, md):
    """
       md : Mode Processing (i.e SQL/PLC Query)
       """
    # Obtain runtime settings for SPC take over ------------[]
    try:
        if md == 1:
            tbl = 'PLC Query'
        else:
            tbl = 'SQL Query'
        layer = clayer
        pPos = round(pPos, 2)
        ring = 'Ring#4'             # unidirectional convention
        prID = pID                  # String value of process identification

        # Write to FMEA report file ------------------------------------------------------------[]
        sigmaExTG(tbl, layer, prID, str(pX), str(pD), str(pU), str(pL), ring, v1, v2, v3, v4, pPos)

    except Exception as err:
        print(f"Update Data Write Error: {err}")

    return