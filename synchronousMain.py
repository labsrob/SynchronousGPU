# --------------------------------------------------------------------------#
# Author: Dr RB Labs
# Developed for Magma Global - TechnipFMC Industrialization
# Email: robbielabs@uwl.ac.uk
# Copyright (C) 2023-2025, Robbie Labs
#
# -------------------- Primary User Graphic Interface ----------------------#

import numpy as np
import pandas as pd
import spcWatchDog as wd
import ctypes

# ----- PLC/SQL Query ---#
import selDataColsGEN as gv     # General Table
import selDataCols_EV as qev     # Environmental Values
import selDataColsLA as qla     # Laser Angle
import selDataColsLP as qlp     # Laser Power
import selDataColsRC as qrc     # Ramp Count
import selDataColsRF as qrf     # Roller Force
import selDataColsRM as qrm     # Ramp Mapping
import selDataColsST as qst     # Substrate Temperature
import selDataColsTG as qtg     # Tape Gap Void
import selDataColsTP as qtp     # Tape Placement error
import selDataColsTT as qtt     # Tape Temperature
import selDataColsVC as qvc     # void (gap) count
import selDataColsVM as qvm     # Void mapping
# ------------ EoL Report ------#
# import selDataColsEoLTS as xts
# ------------------------------#
import selDataColsEoLLP as olp  # EoL Laser Power (on DNV)
import selDataColsEoLLA as ola  # EoL Laser Angle (on DNV)
# import selDataColsEoLRP as orp  # EoL Roller Pressure (on MGM)
# ------------------------------#
import selDataColsEoLTT as ott  # EoL Tape Temperature (Control Temperature)
import selDataColsEoLST as ost  # EoL Substrate Temperature (on DNV)
import selDataColsEoLTG as otg  # EoL Tape Gape (on DNV)
import selDataColsEoLWS as ows  # EoL Winding Speed (on DNV)
import selDataColsEoLWA as owa  # EoL Winding Angle (on MGM)


# ----- DNV/MGM Params ---#
import selDataColsPM as qpm        # Production Monitors
import selDataColsWA as qwa                 # winding angle
# import selDataColsOE as qoe               # OEE TechnipFMC
# -------------------------#
import GPUtil as gp
import screeninfo as m
from random import randint

import pdfkit
from fpdf import FPDF
import time
import os
import sys
import math
from datetime import datetime, date
from time import gmtime, strftime
from pynput.keyboard import Key, Listener
import signal
import tkinter as tk
from tkinter import *
from threading import *
from multiprocessing import Process
from tkinter import messagebox, ttk
from tkinter.simpledialog import askstring
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
LARGE_FONT = ("Verdana", 10, 'bold')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import loadSPCConfig as ty
import rtP_Evaluator as tq
from pydub import AudioSegment
from matplotlib.animation import FuncAnimation
from mpl_interactions import ioff, panhandler, zoom_factory
# --------------------------
import pParamsHL as dd
import pWON_finder as wo
# -------------------------
import qParametersDNV as hla
import qParametersMGM as hlb
import Screen_Calibration as cal
# ------------------------------------------------------------------------[]
tabConfig = []
cpTapeW, cpLayerNo, runType = [], [], []
OTlayr, EPpos, pStatus = [], [], []
HeadA, HeadB, vTFM = 0, 0, 0
hostConn = 0
runStatus = 0
qMarker_rpt = 0.1
# -------------
gap_vol = 0
ramp_vol = 0
vCount = 1000
pExLayer = 100          # Pipe Expected/Predicted final Layer
pLength = 10000         # Pipe expected Length
# --------------
optm = True
inUseAlready = []
# ------------------------------------------#
# Storing the list of PLC data Block        #
#                                           #
# Load PLC DB address once -----------------#
SPC_LP = 112 #
SPC_LA = 103 #
SPC_TP = 111
SPC_RF = 71 #
SPC_TT = 98 #
SPC_ST = 99 #
SPC_TG = 101
SPC_EV = 109
SPC_GEN = 104
SPC_RC = 116
SPC_VC = 117
SPC_RM = 114
SCP_VM = 115
SPC_RP = 97 #
SPC_WS = 100 # not Tape speed
SPC_WA = 113 #
# ------------------------------------------#

import subprocess
try:
    subprocess.check_output('nvidia-smi')
    print('Nvidia GPU detected!')
except Exception:
    print('No Nvidia GPU in system!')

# -----[Detect attached Screen, Extract details to Set GUI Canvas ------[]
aSCR, scrW1, scrW2, scrW3, scrW4, scrW5, scrW6, scrW7, scrW8 = cal.getSCRdetails()

if scrW1 == 2560:   # Digital monitor
    scrW = 2535     # Set GUI Canvas size
    scrX = 8.5      # Set GUI Figure size
    pEvX = 860      # Environmental Values
    pTgX = 1700     # TapeGap Count
    pMtX = 25.5     # Canvas for Monitoring Tab

elif scrW1 == 3840: # Digital Screen/TV
    scrW = 3810     # Set GUI Canvas size
    scrX = 9        # Set GUI Figure size
    pEvX = 860      # Environmental Values
    pTgX = 1700     # TapeGap Count
    pMtX = 27       # Canvas for Monitoring Tab

else:               # Digital Screen # 4864
    print('Chosen.....')
    scrW = 2535     # Set GUI Canvas size
    scrX = 8.5      # Set GUI Figure size
    pEvX = 860      # Environmental Values
    pTgX = 1700     # TapeGap Count
    pMtX = 25.5     # Canvas for monitoring Tab
# -----------------------------------------------------------------------[]
# ----------------------- Audible alert ---------------------------------[]
impath ='C:\\SynchronousGPU\\Media\\'
nudge = AudioSegment.from_wav(impath+'tada.wav')
error = AudioSegment.from_wav(impath+'error.wav')

# -----------------------------------------------------#
path = ('C:\\TapeGapDocs\\testFile.csv')
csv_file = (path)
df = pd.read_csv(csv_file)

# Define statistical operations -----------------------[]
WeldQualityProcess = True
paused = False

url = 'http://www.magmaglobal.com'
localArray = []                                         # raising the bit for GUI canvas
exit_bit = []                                           # enable the close out of all cascade windows

# XBar Constants ------------------------------[]
A3 = [0.975, 0.789, 0.680, 0.6327, 0.606, 0.5525]       # 10, 15, 20, 23, 25, 30  sample sizes respectively
B3 = [0.284, 0.428, 0.510, 0.5452, 0.565, 0.6044]       # 10, 15, 20, 23, 25, 30  sample sizes respectively
B4 = [1.716, 1.572, 1.490, 1.4548, 1.435, 1.3956]       # 10, 15, 20, 23, 25, 30
# ----------------------------------------------[]

today = date.today()
pWON = today.strftime("%Y%m%d")

plcConnex = []
UsePLC_DBS = True                                       # specify SQl Query or PLC DB Query is in use
processWON = [pWON, "20240507", "20240508"]             # Dynamically obtain WON from sysDate or Host PLC
# print('Computed Work Order #:', pWON)

# ------------- Dummy values -------------------[]
pPos = '6.2345'
layer = '03'
sel_SS = "30"
sel_gT = "S-Domino"
eSMC = 'Tape laying process in progress...'
# ------------------ Auto canvass configs ------[]
y_start = 110
y_incmt = 30
rtValues = []

# ---- Common to all Process Procedures --------[]

# Call function and load WON specifications per Parameter -----[]
cDM, cSS, cGS, mLA, mLP, mCT, mOT, mRP, mWS, sStart, sStops, LP, LA, TP, RF, TT, ST, TG = dd.decryptMetricsGeneral(pWON)
print('\nDecrypted MGM Parameters:', mLA, mLP, LP, LA, TP, RF, TT, ST, TG)
print('Decrypted DNV Parameters:', mCT, mOT, mRP, mWS, TT, ST, TG)
print('Work Order Number #:', processWON[0], 'Default Mode:', cDM)
print('Monitors:', cDM, cSS, cGS, mLA, mLP, mCT, mOT, mRP, mWS, '\n')
if cGS == 'SS-Domino':
    cGS = 1
elif cGS == 'GS-Discrete':
    cGS = 2
else:
    cGS = 0
# ----------------------------------------------[A]
if int(TT) and int(ST) and int(TG) and not int(LP) and not int(LA):
    pRecipe = 'DNV'
    import qParamsHL_DNV as dnv
    print('processing DNV parameters...\n')

elif int(LP) and int(LA) and int(TP) and int(RF) and int(TT) and int(ST) and int(TG):
    pRecipe = 'MGM'
    import qParamsHL_MGM as mgm
    print('processing MGM parameters...\n')

else:
    pRecipe = 'New Process'
    import qParamsHL_DNV as dnv
    print('processing DNV parameters...\n')
    # exit()
# ----------------------------------------------[]

def generate_pdf(rptID, cPipe, cProc, custm, layrN, ringA, ringB, ringC, ringD, SetPt, Value, Stdev, Tvalu, usrID):
    # --------------------------------------[]
    from pylab import title, figure, xlabel, ylabel, xticks, bar, legend, axis, savefig

    # Initialise dataframe from Tables ----------[]
    if rptID == 'EoL':
        rpID = ' Layer (EoL)'       # Report ID/Description
    else:
        rpID = ' Layer (EoP)'       # Report ID/Description

    proj = custm                    # Project ID
    pID = cPipe                     # Pipe ID
    oID = usrID                     # User ID
    dID = datetime.datetime.now()   # Date ID
    lID = layrN                     # Layer ID
    # ------------------------------------------[]
    proID = cProc                   # Process ID
    # ------------------------------------------[]

    df = pd.DataFrame()
    df['RingID'] = [ringA, ringB, ringC, ringD]
    df["Actual"] = [SetPt[0], SetPt[1], SetPt[2], SetPt[3]]
    df["Nominal"] = [Value[0], Value[1], Value[2], Value[3]]
    df["StdDev"] = [Stdev[0], Stdev[1], Stdev[2], Stdev[3]]
    df["Tolerance"] = [Tvalu[0], Tvalu[1], Tvalu[2], Tvalu[3]]

    if df['Tolerance'][0] > qMarker_rpt:
        A = 'CHECK'
    else:
        A = 'OK'
    # -----------------
    if df['Tolerance'][1] > qMarker_rpt:
        B = 'CHECK'
    else:
        B = 'OK'
    # -----------------
    if df['Tolerance'][2] > qMarker_rpt:
        C = 'CHECK'
    else:
        C = 'OK'
    # -----------------
    if df['Tolerance'][3] > qMarker_rpt:
        D = 'CHECK'
    else:
        D = 'OK'

    # -- Construct new validation method ----
    df["Status"] = [A, B, C, D]

    title(rpID + " Report")     # Report ID + 'Report'
    xlabel('Ring Analytics')
    ylabel('Rated Quality')

    a = [1.0, 2.0, 3.0, 4.0]
    # a = a.sort()
    n = [x - 0.5 for x in a]
    s = [x - 0.3 for x in a]

    xticks(a, df['RingID'])
    bar(a, df['Actual'], width=0.3, color="blue", label="Actual")
    bar(n, df['Nominal'], width=0.3, color="#51eb87", label="Nominal")
    bar(s, df["StdDev"], width=0.3, color="#eb379c", label="StDev")

    legend()
    axis([0, 4, 0, 5])
    savefig('barchart.png')

    pdf = FPDF()
    pdf.add_page()
    pdf.set_xy(0, 0)
    pdf.set_font('arial', 'B', 14)
    pdf.cell(60)
    pdf.cell(75, 10, rpID + " Report", 0, 2, 'C')
    pdf.cell(90, 10, " ", 0, 2, 'C')

    pdf.cell(-40)
    pdf.cell(5, 10, "Customer Project ID: " + (str(proj)), 0, 2, 'L')
    pdf.cell(5, 10, "Pipe ID                      : " + (str(pID)), 0, 2, 'L')
    pdf.cell(5, 10, "Operators ID            : " + (str(oID)), 0, 2, 'L')
    pdf.cell(5, 10, "Date Time                : " + (str(dID)), 0, 2, 'L')
    pdf.cell(5, 10, "Layer Number         : " + (str(lID)), 0, 2, 'L')
    pdf.cell(5, 10, "Process Name         : " + (str(proID)), 0, 2, 'L')

    pdf.cell(40)
    pdf.cell(90, 10, " ", 0, 2, 'C')
    # draw a rectangle over the text area for Report header ----
    pdf.rect(x=20.0, y=20.5, w=150.0, h=50, style='')
    # construct report header r1RC, r2RC, r3RC, r4RC, rR1VC, r2VC, r3VC, r4VC,
    pdf.cell(-40)
    pdf.cell(5, 10, (str(proID)), 0, 2, 'L')
    pdf.cell(35, 8, 'RingID', 1, 0, 'C')
    pdf.cell(25, 8, 'Actual', 1, 0, 'C')
    pdf.cell(25, 8, 'Nominal', 1, 0, 'C')
    pdf.cell(25, 8, "StdDev", 1, 0, 'C')
    pdf.cell(20, 8, "Tol(±)", 1, 0, 'C')
    pdf.cell(20, 8, "Status", 1, 2, 'C')
    pdf.set_font('arial', '', 12)
    pdf.cell(-130)

    for i in range(0, len(df)):
        print('Iteration ...')   # Instead of ln=2 use new_x=XPos.LEFT, new_y=YPos.NEXT.
        pdf.cell(35, 8, '%s' % (str(df.RingID.iloc[i])), 1, 0, 'C')  # 1: Next line under
        pdf.cell(25, 8, '%s' % (str(df.Actual.iloc[i])), 1, 0, 'C')  # 0: to the right
        pdf.cell(25, 8, '%s' % (str(df.Nominal.iloc[i])), 1, 0, 'C')
        pdf.cell(25, 8, '%s' % (str(df.StdDev.iloc[i])), 1, 0, 'C')
        pdf.cell(20, 8, '%s' % (str(df.Tolerance.iloc[i])), 1, 0, 'C')
        if str(df["Status"].iloc[i]) == "OK":
            pdf.set_fill_color(0, 255, 0)
            pdf.cell(20, 8, '%s' % (str(df["Status"].iloc[i])), 1, 2, 'C', 1)
        else:
            pdf.set_fill_color(255, 255, 0)
            pdf.cell(20, 8, '%s' % (str(df["Status"].iloc[i])), 1, 2, 'C', 1)
        pdf.cell(-130)  # newly added for testing
    pdf.cell(90, 20, " ", 0, 2, 'C')  # 2: place new line below

    pdf.cell(-30)
    pdf.image('barchart.png', x=10, y=135, w=0, h=130, type='', link='')

    # pdf.set_font('arial', '', 8)
    pdf.set_font('helvetica', '', 7)
    with pdf.rotation(angle=90, x=3, y=280):
        pdf.text(10, 280, "Statistical Process Control generated report - " + (str(dID)))

    pdf.output("QualityEOL.pdf")

# -------------------------------------------------------------------------------------------------[]

def random_with_N_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1

    return randint(range_start, range_end)

def get_data():
    sptDat, valuDat, stdDat, tolDat = [], [], [], []

    # Split Process & Map SQL data columns into Dataframe -------------------------------------------[]
    coluA = ['tStamp', 'LyIDa', 'R1SPa', 'R1NVa', 'R2SPa', 'R2NVa', 'R3SPa', 'R3NVa', 'R4SPa', 'R4NVa']
    coluB = ['tStamp', 'LyIDb', 'R1SPb', 'R1NVb', 'R2SPb', 'R2NVb', 'R3SPb', 'R3NVb', 'R4SPb', 'R4NVb']
    coluC = ['tStamp', 'LyIDc', 'R1SPc', 'R1NVc', 'R2SPc', 'R2NVc', 'R3SPc', 'R3NVc', 'R4SPc', 'R4NVc']
    if pRecipe == 'MGM':                                    # Winding Angle Parameter
        coluD = ['tStamp', 'LyIDe', 'R1SPe', 'R1NVe', 'R2SPe', 'R2NVe', 'R3SPe', 'R3NVe', 'R4SPe', 'R4NVe']
    else:                                                   # Winding Speed Parameter
        coluD = ['tStamp', 'LyIDd', 'R1SPd', 'R1NVd', 'R2SPd', 'R2NVd', 'R3SPd', 'R3NVd', 'R4SPd', 'R4NVd']
    # ------------------------------------
    df1 = pd.DataFrame(zTT, columns=coluA)                  # Inherited from global variable EoL/EoP Process
    df2 = pd.DataFrame(zST, columns=coluB)
    df3 = pd.DataFrame(zTG, columns=coluC)
    if pRecipe == 'MGM':
        df4 = pd.DataFrame(zWA, columns=coluD)
    else:
        df4 = pd.DataFrame(zWS, columns=coluD)
    # ------------------------------
    pRPT = [df1, df2, df3, df4]                             # Dynamic aggregated List
    # ------------------------------

    # Constants per Pipe -----------
    cPipe = 'Pipe XXXX'                     # Pipe ID TODO -- Automate varibles
    custm = 'Customer cID'                  # Customer ID
    usrID = 'Operator ID'                   # User ID

    for proP in pRPT:
        if proP[0]:
            cProc = 'Tape Temperature'       # Process ID
        elif proP[1]:
            cProc = 'Substrate Temperature'  # Process ID
        elif proP[2]:
            cProc = 'Gap Measurement'       # Process ID
        elif proP[3] and pRecipe == 'MGM':
            cProc = 'Winding Angle'         # Process ID
        else:
            cProc = 'Winding Speed'         # Process ID
        # --------------------------#       # From SQL Data
        layrNO = proP['LyID']               # Layer ID
        ring1A = proP['R1SP']               # Head 1
        ring1B = proP['R1NV']               # Head 2
        ring2A = proP['R2SP']               # Head 1
        ring2B = proP['R2NV']               # Head 2
        ring3A = proP['R3SP']               # Head 1
        ring3B = proP['R3NV']               # Head 2
        ring4A = proP['R4SP']               # Head 1
        ring4B = proP['R4NV']               # Head 2
        # --------------------------#
        SetPt = proP['pSP']                 # Process Set Point values (Average all the ring values)
        Value = proP['pRV']                 # Process Measured values (ringValue/Average total ring0
        Stdev = proP['pDV']                 # Standard Deviation
        Tvalu = proP['pTo']                 # Tolerance
        # ---------------------------#
        sptDat.append(SetPt)
        valuDat.append(Value)
        stdDat.append(Stdev)
        tolDat.append(Tvalu)
        # Send values to PDG generator and repeat until last process --------------------[]
        generate_pdf(rptID, cPipe, cProc, custm, usrID, layrNO, ring1A, ring1B, ring2A, ring2B, ring3A, ring3B, ring4A,
                     ring4B, sptDat[0], valuDat[0], stdDat[0], tolDat[0])
    else:
        print('\nEnd of Report')

    # -------------------------------------------------[]

class autoResizableCanvas(tk.Canvas):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<Configure>", self.resize)

    def resize(self, event):
        self.config(width=event.width, height=event.height)


def diff_idx_Tracker(layer, idx1, idx2, idx3, idx4, idx5, idx6, pPos):    # Record for offline SPC analysis
    rtitle = ('================================= TCP01 - Realtime Index Tracker =============================\n')
    rheader = ('Time'+'\t\t'+'Layer#'+'\t'+'T1Row'+'\t'+'T2Row'+'\t'+'T3Row'+'\t'+'T4Row'+'\t'+'T5Row'+'\t'+'T6Row'+'\t'+'EstPos'+'\n')
    rdemaca = ("----------------------------------------------------------------------------------------------\n")
    event = datetime.now().strftime("%H:%M.%S")                 # WON as name for easy retrieval method
    PidxLog = 'IDXLog_' + str(processWON[0])                    # processed SQL index Log

    filepath = '.\\RT_Index_Log\\'+PidxLog+".txt"
    old_report = os.path.isfile(filepath)

    if not old_report:                                          # if doing a new report...
        f = open('.\\RT_Index_Log\\'+PidxLog+".txt", "a")       # Open new file and ...
        f.write(rtitle)                                         # Insert a Title
        f.write(rheader)                                        # Insert new header
        f.write(rdemaca)                                        # Insert demarcator
    else:                                                       # if it's an existing report
        f = open('.\\RT_Index_Log\\' + PidxLog + ".txt", "a")   # Just open the file for a write operations
    # initialise a tab delimited data and insert corresponding values in string format ------------------------[]
    f.write(event+'\t'+str(layer)+'\t'+str(idx1)+'\t'+str(idx2)+'\t'+str(idx3)+'\t'+str(idx4)+ '\t'+str(idx5)+'\t'+str(idx6)+'\t'+str(pPos)+'\n')
    f.close()


def timeProcessor(runtimeType, smp_Sz, runtimeParams, regime, lapsedT):    # Record for offline SPC analysis

    rtitle = ('=== TCP1 - Processing Speed Tracker - '+runtimeType+ ' Samples ===\n')
    rheader = ('Rolling Type'+'\t'+'Sample'+'\t'+'Parameters#'+'\t'+'Regime'+'\t'+'LapsedTime'+'\n')
    rdemaca = ("----------------------------------------------------------\n")
    PidxLog = 'TXLog_' + str(processWON[0])                           # processed SQL index Log

    filepath = '.\\ProcessTime_Log\\'+PidxLog+".txt"
    old_report = os.path.isfile(filepath)

    if not old_report:                                              # if doing a new report...
        f = open('.\\ProcessTime_Log\\'+PidxLog+".txt", "a")        # Open new file and ...
        f.write(rtitle)                                             # Insert a Title
        f.write(rheader)                                            # Insert new header
        f.write(rdemaca)                                            # Insert demarcator
    else:                                                           # if it's an existing report
        f = open('.\\ProcessTime_Log\\' + PidxLog + ".txt", "a")    # Just open the file for a write operations
    # initialise a tab delimited data and insert corresponding values in string format --------------------------[]
    f.write(str(runtimeType)+'\t'+str(smp_Sz)+'\t'+str(runtimeParams)+'\t'+str(regime)+'\t'+str(lapsedT) +'\n')
    f.close()

def errorLog(err):
    fileName = datetime.now().strftime('SQLM2MLog '+"%Y-%m-%d")
    event = datetime.now().strftime("%Y-%m-%d %H:%M.%S")
    errorlogFile = str(fileName)
    f = open('.\\RuntimeLog\\'+errorlogFile+".txt", "a")
    f.write(event+' --- '+err+'\n')
    f.close()


# This function runs only once! When SPC stalls and replayed
def bufferEOF(fname, N):
    # open index tracker file, and load the values in the end of file
    with open(fname) as file:
        for line in (file.readlines()[-N:]):    # N = number of lines to read
            oem = line
        # print('\nEND OF FILE:', oem)
        # print(line, end='')
    return oem


def checkhistDev(xUCL, MeanP, sampSiz):
    # Evaluate SPC constants with chosen sample size --
    print('SAMPLE:', sampSiz)
    if sampSiz == '10':
        const1 = A3[0]
        const2 = B3[0]
        const3 = B4[0]
    elif sampSiz == '15':
        const1 = A3[1]
        const2 = B3[1]
        const3 = B4[1]
    elif sampSiz == '20':
        const1 = A3[2]
        const2 = B3[2]
        const3 = B4[2]
    elif sampSiz == '23':
        const1 = A3[3]
        const2 = B3[3]
        const3 = B4[3]
    elif sampSiz == '25':
        const1 = A3[4]
        const2 = B3[4]
        const3 = B4[4]
    elif sampSiz == '30':
        const1 = A3[5]
        const2 = B3[5]
        const3 = B4[5]
    else:
        print('Sample Size undefined!, Exiting...')
    # Compute for stdDev  in  [xUCL = meanP + (const1 * stdDev)]
    stdDev = (xUCL - MeanP)/const1

    UCL = (const3 * stdDev)  # Upper control limits of 1 std dev
    LCL = (const2 * stdDev)  # Lower control limits of 1 Std dev

    return UCL, LCL, stdDev


def canvasOn(bitHigh=None):
    if bitHigh:
        localArray.append(True)     # Update local array with bit from GUI when active
    else:
        localArray.append(False)
    return


def callback():
    if messagebox.askokcancel("Quit", "Do you really wish to quit?"):
        # root.protocol('WM_DELETE_WINDOW', lambda: quit())
        import magmaSPC as en
        en.move_window(True)
        print('\nAfter Menu closes, check timer is alive...')
        root.destroy()
        localArray.clear()      # clear array held for GUI

    return


def check_pid(pid):
    PROCESS_QUERY_INFROMATION = 0x1000
    processHandle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFROMATION, 0, pid)
    if processHandle == 0:
        return False
    else:
        ctypes.windll.kernel32.CloseHandle(processHandle)
    return True

def menuExit():
    # print('ExitBit H/L:', exit_bit)
    inUse = os.getpid()

    if not exit_bit:                                # Check exit_bit for unitary value
        print('\nExiting Local GUI, bye for now...')
        root.quit()                                 # Exit Apps if exit_bit is empty
        os._exit(0)                                 # Close out all process

    elif len(exit_bit) >= 4:
        print('\nExiting Local GUI, bye for now...')

        # Evaluate active process before exiting -------#
        proc_list = [p1.pid, p2.pid, p3.pid, p4.pid]  # Evaluate exit_bit as true if all active
        for p in proc_list:
            try:
                os.kill(p, signal.SIGTERM)
                print('Process:', p, ' terminated by the User')
            except Exception:
                print(f'Process {p} failed to terminate, attempting force termination!')

    elif len(exit_bit) < 4 and inUse:
        print('Exiting...')
        root.quit()
        os._exit(0)

    else:
        root.quit()
        os._exit(0)

# ------------------------------------------------------------------------------------[ MAIN PROGRAM ]

def tabbed_cascadeMode(cMode, pType):
    global p1, p2, p3, p4, p5, p6, p7, hostConn, pRecipe, pMode
    """
    https://stackoverflow.com/questions/73088304/styling-a-single-tkinter-notebook-tab
    :return:
    """
    pMode = cMode               # Copy variable to new var

    if cMode == 1:
        print('Connecting to PLC Host...')
    elif cMode == 2:
        print('Connecting to SQL Server...')
    else:
        print('Standby/Maintenance Mode...')

    # Specify production type -----------[DNV/MGM]
    pRecipe = pType
    print('Loading ' + pRecipe + ' Production Data...\n')

    s = ttk.Style()
    s.theme_use('default')  # Options: ('clam', 'alt', 'default', 'classic')
    s.configure('TNotebook.Tab', background="green3", foreground="black")

    # s.map("TNotebook", background=[("selected", "red3")]) ------------------------------------------#
    s.map("TNotebook.Tab", background=[("selected", "lightblue")], foreground=[("selected", "red")])
    # Hover color if needed....-----------------------------------------------------------------------#

    # Insert 3 runtime objects [1] Ramp Profile [2] Location Based Climate [3] Tape Gap Profile ------[]
    common_rampCount()                                          # Ramp cumulative curve
    common_climateProfile()                                     # environmental factors
    common_gapCount()                                           # Void gap count curve

    # Load class object from Cascade Switcher Method -----------[x]
    import CascadeSwitcher as cs
    p1, p2, p3, p4, p5, p6, p7, p8 = cs.myMain(cMode, pRecipe)      # runtimeType, process RecipeType
    # ----------------------------------------------------------[]

    # Set up embedding notebook (tabs) ------------------------[B]
    notebook = ttk.Notebook(root, width=scrW, height=850)       # Declare Tab overall Screen size [2500]
    notebook.grid(column=0, row=0, padx=10, pady=450)           # Tab's spatial position on the Parent [10]
    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)
    tab3 = ttk.Frame(notebook)

    # Define common Tabb for DNV/MGM Procedure  ----------------#
    notebook.add(tab1, text="[Runtime Monitoring]")             # Default Min/Max x1
    notebook.add(tab2, text="EoL Report System")                # Report
    notebook.add(tab3, text="EoP Report System")                # Report
    notebook.grid()

    # ------------------------------------------[]
    app1 = MonitorTabb(master=tab1)
    app1.grid(column=0, row=0, padx=10, pady=10)
    # ------------------------------------------[]
    app2 = collectiveEoL(master=tab2)
    app2.grid(column=0, row=0, padx=10, pady=10)

    app3 = collectiveEoP(master=tab3)
    app3.grid(column=0, row=0, padx=10, pady=10)

    root.mainloop()


def tabbed_canvas(cMode, pType):   # Tabbed Common Classes -------------------[TABBED ]
    global hostConn, pRecipe
    """
    https://stackoverflow.com/questions/73088304/styling-a-single-tkinter-notebook-tab
    :return:
    """
    if cMode == 1:
        print('Connecting to PLC Host...')
    elif cMode == 2:
        print('Connecting to SQL Server...')
    else:
        print('Standby/Maintenance Mode')

    # Specify production type --------[]
    pRecipe = pType
    print('Loading ' + pRecipe + ' Production Data...\n')

    s = ttk.Style()
    s.theme_use('default')
    s.configure('TNotebook.Tab', background="green3", foreground="black")

    # s.map("TNotebook", background=[("selected", "red3")]) ------------------------------------------#
    s.map("TNotebook.Tab", background=[("selected", "lightblue")], foreground=[("selected", "red")])
    # Hover color if needed  -------------------------------------------------------------------------#

    common_rampCount()                                      # called function
    common_climateProfile()                                 # called function
    common_gapCount()                                       # called function
    # Load from CFG fine and parse the variables ------[x]

    # Set up embedding notebook (tabs) ----------------[B]
    notebook = ttk.Notebook(root, width=scrW, height=850)      # Declare Tab overall Screen size[2500, 2540,]
    notebook.grid(column=0, row=0, padx=10, pady=450)           # Tab's spatial position on the Parent [450]
    if pRecipe == 'DNV':
        tab1 = ttk.Frame(notebook)
        tab2 = ttk.Frame(notebook)
        tab3 = ttk.Frame(notebook)
        tab4 = ttk.Frame(notebook)
        tab5 = ttk.Frame(notebook)
        tab6 = ttk.Frame(notebook)
    else:
        tab1 = ttk.Frame(notebook)
        tab2 = ttk.Frame(notebook)
        tab3 = ttk.Frame(notebook)
        tab4 = ttk.Frame(notebook)
        tab5 = ttk.Frame(notebook)
        tab6 = ttk.Frame(notebook)
        tab7 = ttk.Frame(notebook)
        tab8 = ttk.Frame(notebook)
        tab9 = ttk.Frame(notebook)
        tab10 = ttk.Frame(notebook)

    # ------------------------------------------ DNV Statistical Process Parameters -----[]
    if pRecipe == 'DNV': # and int(TT) and int(ST) and int(TG) and not int(LP) and not int(LA):
        print('Loading DNV Algorithm...\n')
        notebook.add(tab1, text="Tape Temperature")         # Stats x16
        notebook.add(tab2, text="Substrate Temperature")    # Stats x16
        notebook.add(tab3, text="Tape Gap Polarisation")    # Stats x4 per Ring
        # ----------------------------------------------#
        notebook.add(tab4, text="[Runtime Monitoring]")     # Default Min/Max x16
        # ----------------------------------------------#
        notebook.add(tab5, text="EoL Report System")        # Report
        notebook.add(tab6, text="EoP Report System")        # Report

    elif pRecipe == 'MGM': # and int(LP) and int(LA) and int(TP) and int(RF) and int(TT) and int(ST) and int(TG):
        print('Loading Commercial Algorithm...\n')
        notebook.add(tab1, text="Laser Power")              # Stats
        notebook.add(tab2, text="Laser Angle")              # Stats
        notebook.add(tab3, text="Roller Force")             # Stats
        # --------------------------------------------------#
        notebook.add(tab4, text="Tape Temperature")         # Stats x16
        notebook.add(tab5, text="Subs Temperature")         # Stats x16
        notebook.add(tab6, text="Tape Placement Error")     # Stats x8 (2 per Ring)
        notebook.add(tab7, text="Tape Gap Polarisation")    # Stats x4 (1 per Ring)
        # --------------------------------------------------#
        notebook.add(tab8, text="[Runtime Monitoring]")     # Commercial - LP, LA, RP, WS, TG, RP
        # --------------------------------------------------#
        notebook.add(tab9, text="EoL Report System")
        notebook.add(tab10, text="EoP Report System")

    else:  # Bespoke selection only affects Runtime Monitoring Reports
        pass
        print('Loading Bespoke User Selection Algorithm...')

    notebook.grid()

    # Create DNV tab frames properties -------------[]
    if pRecipe == 'DNV':
        app1 = tapeTempTabb(master=tab1)
        app1.grid(column=0, row=0, padx=10, pady=10)

        app2 = substTempTabb(master=tab2)
        app2.grid(column=0, row=0, padx=10, pady=10)

        app3 = tapeGapPolTabb(master=tab3)
        app3.grid(column=0, row=0, padx=10, pady=10)
        # ------------------------------------------[]
        app4 = MonitorTabb(master=tab4)
        app4.grid(column=0, row=0, padx=10, pady=10)
        # ------------------------------------------[]
        app5 = collectiveEoL(master=tab5)
        app5.grid(column=0, row=0, padx=10, pady=10)

        app6 = collectiveEoP(master=tab6)
        app6.grid(column=0, row=0, padx=10, pady=10)

    elif pRecipe == 'MGM':
        app1 = laserPowerTabb(master=tab1)
        app1.grid(column=0, row=0, padx=10, pady=10)

        app2 = laserAngleTabb(master=tab2)
        app2.grid(column=0, row=0, padx=10, pady=10)

        app3 = rollerForceTabb(master=tab3)
        app3.grid(column=0, row=0, padx=10, pady=10)

        app4 = tapeTempTabb(master=tab4)
        app4.grid(column=0, row=0, padx=10, pady=10)

        app5 = substTempTabb(master=tab5)
        app5.grid(column=0, row=0, padx=10, pady=10)

        app6 = tapePlacementTabb(master=tab6)
        app6.grid(column=0, row=0, padx=10, pady=10)    # Tape Placement Error

        app7 = tapeGapPolTabb(master=tab7)
        app7.grid(column=0, row=0, padx=10, pady=10)    # Tape Gap Polarisation
        # --------------------------------------------[]
        app8 = MonitorTabb(master=tab8)
        app8.grid(column=0, row=0, padx=10, pady=10)
        # --------------------------------------------[]
        app9 = collectiveEoL(master=tab9)
        app9.grid(column=0, row=0, padx=10, pady=10)

        app10 = collectiveEoP(master=tab10)
        app10.grid(column=0, row=0, padx=10, pady=10)
        # ------------------------------------------[]
    else:       # USR Selection
        print('Details not found!')

    root.mainloop()


def plotView(titleMean):
    # Define Axes ----------------------------------#
    fig = Figure(figsize=(27, 7), dpi=100)  # 12.5, 7
    fig.subplots_adjust(left=0.04, bottom=0.033, right=0.988, top=0.957, hspace=0.14, wspace=0.033)
    # ---------------------------------[]
    a1 = fig.add_subplot(2, 3, (1, 2))  # X Bar Plot
    a2 = fig.add_subplot(2, 3, (4, 5))  # S Bar Plot
    a3 = fig.add_subplot(2, 3, (3, 6))  # Combo Ref

    # Declare Plots attributes ---------------------[]
    plt.rcParams.update({'font.size': 7})  # Reduce font size to 7pt for all legends

    # Calibrate limits for X-moving Axis -----------#
    YScale_minRF, YScale_maxRF = 10, 500
    sBar_minRF, sBar_maxRF = 10, 250  # Calibrate Y-axis for S-Plot
    window_Xmin, window_Xmax = 0, 30  # windows view = visible data points
    # Common properties ------------------------#
    a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
    a2.set_ylabel("Sample Deviation [" + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
    a1.set_title(titleMean + '[XBar Plot]', fontsize=12, fontweight='bold')
    a2.set_title(titleMean + '[SDev Plot]', fontsize=12, fontweight='bold')

    # Apply grid lines ------------------------------
    a1.grid(color="0.5", linestyle='-', linewidth=0.5)
    a2.grid(color="0.5", linestyle='-', linewidth=0.5)
    a1.legend(loc='upper right', title='Mean curve')
    a2.legend(loc='upper right', title='Sigma curve')

    # ----------------------------------------------------------#
    a1.set_ylim([YScale_minRF, YScale_maxRF], auto=True)
    a1.set_xlim([window_Xmin, window_Xmax])
    # ----------------------------------------------------------#
    a2.set_ylim([sBar_minRF, sBar_maxRF], auto=True)
    a2.set_xlim([window_Xmin, window_Xmax])
    # ----------------------------------------------------------#
    a3.cla()
    a3.get_yaxis().set_visible(False)
    a3.get_xaxis().set_visible(False)

    # ----------------------------------------------------------[]
    # Define Plot area and axes -
    # ----------------------------------------------------------#
    im10, = a1.plot([], [], 'o-', label='Roller Force - (R1H1)')
    im11, = a1.plot([], [], 'o-', label='Roller Force - (R1H2)')
    im12, = a1.plot([], [], 'o-', label='Roller Force - (R1H3)')
    im13, = a1.plot([], [], 'o-', label='Roller Force - (R1H4)')
    im14, = a2.plot([], [], 'o-', label='Roller Force')
    im15, = a2.plot([], [], 'o-', label='Roller Force')
    im16, = a2.plot([], [], 'o-', label='Roller Force')
    im17, = a2.plot([], [], 'o-', label='Roller Force')


def readEoP(text_widget, rptID):        # End of Pipe Report
    # file_path = filedialog.askopenfilename(title='Select a Text File', filetypes=[('Text files&quot', '*.txt')])

    file_path = 'C:\\SynchronousGPU\\FMEA_Log\\'+ rptID +'.txt'
    rpfMissing = 'C:\\SynchronousGPU\\FMEA_Log\\RPT_NOTFOUND.txt'
    conc_RPT = ["RPT_LP_", "RPT_LA_", "RPT_TP_", "RPT_RF_", "RPT_TT_", "RPT_ST_", "RPT_TG_"]
    # -----------------------------------------------------------------

    if rptID == "RPT_AL_":
        counter = 1
        file_path = 'C:\\SynchronousGPU\\FMEA_Log\\' + conc_RPT +'.txt'
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                content = file.read()
                text_widget.delete(1.0, tk.END)         # Clear previous content
                text_widget.insert(tk.END, content)
        counter += 1

        if counter == len(conc_RPT):
            pass

        else:
            with open(rpfMissing, 'r') as file:
                content = file.read()
                text_widget.delete(1.0, tk.END)         # Clear previous content
                text_widget.insert(tk.END, content)

    elif os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            text_widget.delete(1.0, tk.END)            # Clear previous content
            text_widget.insert(tk.END, content)
    else:
        with open(rpfMissing, 'r') as file:
            content = file.read()
            text_widget.delete(1.0, tk.END)            # Clear previous content
            text_widget.insert(tk.END, content)


# -------- Defines the collective screen structure -----------------------[EOL Reports]


class collectiveEoL(ttk.Frame):
    # End of Layer Progress Report Tabb. Plot Mean/stdev for each parameter, generate QA-EoL nominal values per process
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.createWidgets()

    def createWidgets(self):
        # Load settings -------
        # pWON = processWON[0]
        # Load metrics from config -----------------------------------[TG, TT, ST]
        if pRecipe == 'DNV':
            import qParamsHL_DNV as dnv
            ttS, ttTy, ttSoL, ttSoP, ttHL, ttAL, ttFO, A, B, C, D, E = dnv.decryptpProcessLim(pWON, 'TT')
            stS, stTy, stSoL, stSoP, stHL, stAL, stFO, A, B, C, D, E = dnv.decryptpProcessLim(pWON, 'ST')
            tgS, tgTy, tgSoL, tgSoP, tgHL, tgAL, tgFO, A, B, C, D, E = dnv.decryptpProcessLim(pWON, 'TG')
            wsS, wsTy, wsSoL, wsSoP, wsHL, wsAL, wsFO, A, B, C, D, E = dnv.decryptpProcessLim(pWON, 'WS')
            # ----
            rcS, rcTy, rcSoL, rcSoP, rcHL, rcAL, rcFO, A, B, C, D, E = dnv.decryptpProcessLim(pWON, 'RC')
            vcS, vcTy, vcSoL, vcSoP, vcHL, vcAL, vcFO, A, B, C, D, E = dnv.decryptpProcessLim(pWON, 'VC')
        else:
            import qParamsHL_MGM as mgm
            lpS, lpTy, lpSoL, lpSoP, lpHL, lpAL, lpFO, A, B, C, D, E = mgm.decryptpProcessLim(pWON, 'LP')
            laS, laTy, laSoL, laSoP, laHL, laAL, laFO, A, B, C, D, E = mgm.decryptpProcessLim(pWON, 'LA')
            ttS, ttTy, ttSoL, ttSoP, ttHL, ttAL, ttFO, A, B, C, D, E = mgm.decryptpProcessLim(pWON, 'TT')
            stS, stTy, stSoL, stSoP, stHL, stAL, stFO, A, B, C, D, E = mgm.decryptpProcessLim(pWON, 'ST')
            tgS, tgTy, tgSoL, tgSoP, tgHL, tgAL, tgFO, A, B, C, D, E = mgm.decryptpProcessLim(pWON, 'TG')
            waS, waTy, waSoL, waSoP, waHL, waAL, waFO, A, B, C, D, E = mgm.decryptpProcessLim(pWON, 'WA')
            # ------
            rcS, rcTy, rcSoL, rcSoP, rcHL, rcAL, rcFO, A, B, C, D, E = mgm.decryptpProcessLim(pWON, 'RC')
            vcS, vcTy, vcSoL, vcSoP, vcHL, vcAL, vcFO, A, B, C, D, E = mgm.decryptpProcessLim(pWON, 'VC')
        # ----------------------
        label = ttk.Label(self, text='[End of Layer Summary - ' + rType + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)
        # ----------------------------------#
        gen_report = ttk.Button(self, text="Generate PDF Reports", command=get_data)
        gen_report.place(x=1920, y=1)
        # ---------------------------------#
        upload_report = ttk.Button(self, text="Upload Reports", command=get_data)
        upload_report.place(x=2380, y=1)

        # Define Axes ---------------------#
        f = Figure(figsize=(pMtX, 8), dpi=100)
        f.subplots_adjust(left=0.022, bottom=0.05, right=0.983, top=0.936, wspace=0.1, hspace=0.17)
        # ---------------------------------[]
        if pRecipe == 'DNV':
            a1 = f.add_subplot(2, 5, 1)         # xbar plot
            a2 = f.add_subplot(2, 5, 2)         # s bar plot
            a3 = f.add_subplot(2, 5, 3)         # s bar plot
            a4 = f.add_subplot(2, 5, 4)
            a5 = f.add_subplot(2, 5, (5, 10))   # PDF Report Space
            a6 = f.add_subplot(2, 5, 6)         # s bar plot
            a7 = f.add_subplot(2, 5, 7)         # s bar plot
            a8 = f.add_subplot(2, 5, 8)         # s bar plot
            a9 = f.add_subplot(2, 5, 9)
        else:
            a1 = f.add_subplot(2, 7, 1)         # xbar plot
            a2 = f.add_subplot(2, 7, 2)         # s bar plot
            a3 = f.add_subplot(2, 7, 3)         # s bar plot
            a4 = f.add_subplot(2, 7, 4)
            a5 = f.add_subplot(2, 7, 5)         # PDF Report Space
            a6 = f.add_subplot(2, 7, 6)         # s bar plot
            a7 = f.add_subplot(2, 7, (7, 14))   # s bar plot
            a8 = f.add_subplot(2, 7, 8)         # xbar plot
            a9 = f.add_subplot(2, 7, 9)         # xbar plot
            a10 = f.add_subplot(2, 7, 10)       # s bar plot
            a11 = f.add_subplot(2, 7, 11)
            a12 = f.add_subplot(2, 7, 12)       # PDF Report Space
            a13 = f.add_subplot(2, 7, 13)       # s bar plot

        # Declare Plots attributes ----------------------------[H]
        plt.rcParams.update({'font.size': 7})                   # Reduce font size to 7pt for all legends

        # Calibrate limits for X-moving Axis -------------------#
        YScale_minEOL, YScale_maxEOL = 0, pExLayer              # Roller Force
        sBar_minEOL, sBar_maxEOL = 0, pLength                   # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, pLength                   # windows view = visible data points

        # Load SQL Query Table [Important] ---------------------#
        if pRecipe == 'DNV':
            EoLRep = 'DNV'
            # ---------- Based on Group's URS ------------------#
            T1 = 'ZTT_' + pWON          # Identify EOL_TT Table
            T2 = 'ZST_' + pWON          # Identify EOL_ST Table
            T3 = 'ZTG_' + pWON          # Identify EOL_TG Table
            T4 = 'ZWS' + pWON           # Winding Speed
            T5 = 'RC_' + pWON           # Identify RampCount Table - not visualised but reckoned on pdf report
            T6 = 'VC_' + pWON           # Identify Void count table - not visualised but reckoned on pdf report

        elif pRecipe == 'MGM':
            EoLRep = 'MGM'
            # --------- Based on Group's URS -------------------#
            T1 = 'ZLP_' + pWON          # Identify Laser Power EOL Table
            T2 = 'ZLA_' + pWON          # Identify Laser Angle EOL Table
            T3 = 'ZTT_' + pWON          # Identify Tape Temperature EOL Table
            T4 = 'ZST_' + pWON          # Identify Substrate Temperature EOL Table
            T5 = 'ZTG_' + pWON          # Identify Tape Gap EOL Table
            T6 = 'ZWA_' + pWON          # Identify Winding Angle EOL Table
            T7 = 'RC_' + pWON           # Identify RampCount Table
            T8 = 'VC_' + pWON           # Identify Void count table

        else:
            pass
        # ----------------------------------------------------------#

        # Initialise runtime limits
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        if pRecipe == 'DNV':
            a6.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
            # -----------------------------
            a1.set_title('EoL - Tape Temperature [XBar]', fontsize=12, fontweight='bold')
            a6.set_title('EoL - Tape Temperature [SDev]', fontsize=12, fontweight='bold')
            # ------
            a2.set_title('EoL - Substrate Temperature [XBar]', fontsize=12, fontweight='bold')
            a7.set_title('EoL - Substrate Temperature [SDev]', fontsize=12, fontweight='bold')
            # -------------------
            a3.set_title('EoL - Tape Gap Measurement [XBar]', fontsize=12, fontweight='bold')
            a8.set_title('EoL - Tape Gap Measurement [SDev]', fontsize=12, fontweight='bold')
            # -------------------
            a4.set_title('EoL - Tape Winding Speed [XBar]', fontsize=12, fontweight='bold')
            a9.set_title('EoL - Tape Winding Speed [SDev]', fontsize=12, fontweight='bold')

            a1.grid(color="0.5", linestyle='-', linewidth=0.5)
            a2.grid(color="0.5", linestyle='-', linewidth=0.5)
            a3.grid(color="0.5", linestyle='-', linewidth=0.5)
            a4.grid(color="0.5", linestyle='-', linewidth=0.5)
            a6.grid(color="0.5", linestyle='-', linewidth=0.5)
            a7.grid(color="0.5", linestyle='-', linewidth=0.5)
            a8.grid(color="0.5", linestyle='-', linewidth=0.5)
            a9.grid(color="0.5", linestyle='-', linewidth=0.5)

            a1.legend(loc='upper right', title='EoL - Tape Temperature')
            a2.legend(loc='upper right', title='EoL - Substrate Temperature')
            a3.legend(loc='upper right', title='EoL - Tape Gap Measurement')
            a4.legend(loc='upper right', title='EoL - Winding Speed')
            # ----------------------------------------------------------#
            a1.set_ylim([YScale_minEOL, YScale_maxEOL], auto=True)
            a1.set_xlim([window_Xmin, window_Xmax])

            a6.set_ylim([0, 10], auto=True)
            a6.set_xlim([window_Xmin, window_Xmax])

            # ----------------------------------------------------------#
            a2.set_ylim([YScale_minEOL, YScale_maxEOL], auto=True)
            a2.set_xlim([window_Xmin, window_Xmax])

            a7.set_ylim([0, 10], auto=True)
            a7.set_xlim([window_Xmin, window_Xmax])

            a3.set_ylim([YScale_minEOL, YScale_maxEOL], auto=True)
            a3.set_xlim([window_Xmin, window_Xmax])

            a8.set_ylim([0, 10], auto=True)
            a8.set_xlim([window_Xmin, window_Xmax])

            a4.set_ylim([YScale_minEOL, YScale_maxEOL], auto=True)
            a4.set_xlim([window_Xmin, window_Xmax])

            a9.set_ylim([0, 10], auto=True)
            a9.set_xlim([window_Xmin, window_Xmax])

            a5.cla()
            a5.get_yaxis().set_visible(False)
            a5.get_xaxis().set_visible(False)

        else:
            a8.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
            # -----------------------------
            a1.set_title('EoL - Laser Power [XBar]', fontsize=12, fontweight='bold')
            a8.set_title('EoL - Laser Power [SDev]', fontsize=12, fontweight='bold')
            # ------
            a2.set_title('EoL - Laser Angle [XBar]', fontsize=12, fontweight='bold')
            a9.set_title('EoL - Laser Angle [SDev]', fontsize=12, fontweight='bold')
            # -------------------
            a3.set_title('EoL - Tape Temperature [XBar]', fontsize=12, fontweight='bold')
            a10.set_title('EoL - Tape Temperature [SDev]', fontsize=12, fontweight='bold')
            # ------
            a4.set_title('EoL - Substrate Temperature [XBar]', fontsize=12, fontweight='bold')
            a11.set_title('EoL - Substrate Temperature [SDev]', fontsize=12, fontweight='bold')
            # -------------------
            a5.set_title('EoL - Tape Gap Measurement [XBar]', fontsize=12, fontweight='bold')
            a12.set_title('EoL - Tape Gap Measurement [SDev]', fontsize=12, fontweight='bold')
            # -------------------
            a6.set_title('EoL - Tape Winding Angle [XBar]', fontsize=12, fontweight='bold')
            a13.set_title('EoL - Tape Winding Angle [SDev]', fontsize=12, fontweight='bold')
            # ------
            # -----------------------------------------------------
            a1.grid(color="0.5", linestyle='-', linewidth=0.5)
            a2.grid(color="0.5", linestyle='-', linewidth=0.5)
            a3.grid(color="0.5", linestyle='-', linewidth=0.5)
            a4.grid(color="0.5", linestyle='-', linewidth=0.5)
            a5.grid(color="0.5", linestyle='-', linewidth=0.5)
            a6.grid(color="0.5", linestyle='-', linewidth=0.5)

            a8.grid(color="0.5", linestyle='-', linewidth=0.5)
            a9.grid(color="0.5", linestyle='-', linewidth=0.5)
            a10.grid(color="0.5", linestyle='-', linewidth=0.5)
            a11.grid(color="0.5", linestyle='-', linewidth=0.5)
            a12.grid(color="0.5", linestyle='-', linewidth=0.5)
            a13.grid(color="0.5", linestyle='-', linewidth=0.5)

            a1.legend(loc='upper right', title='EoL - Laser Power')
            a2.legend(loc='upper right', title='EoL - Laser Angle')
            a3.legend(loc='upper right', title='EoL - Tape Temperature')
            a4.legend(loc='upper right', title='EoL - Substrate Temperature')
            a5.legend(loc='upper right', title='EoL - Tape Gap Measurement')
            a6.legend(loc='upper right', title='EoL - Tape Winding Speed')

            # ----------------------------------------------------------#
            a1.set_ylim([YScale_minEOL, YScale_maxEOL], auto=True)
            a1.set_xlim([window_Xmin, window_Xmax])

            a8.set_ylim([0, 10], auto=True)
            a8.set_xlim([window_Xmin, window_Xmax])

            a2.set_ylim([YScale_minEOL, YScale_maxEOL], auto=True)
            a2.set_xlim([window_Xmin, window_Xmax])

            a9.set_ylim([0, 10], auto=True)
            a9.set_xlim([window_Xmin, window_Xmax])

            a3.set_ylim([YScale_minEOL, YScale_maxEOL], auto=True)
            a3.set_xlim([window_Xmin, window_Xmax])

            a10.set_ylim([0, 10], auto=True)
            a10.set_xlim([window_Xmin, window_Xmax])

            a4.set_ylim([YScale_minEOL, YScale_maxEOL], auto=True)
            a4.set_xlim([window_Xmin, window_Xmax])

            a11.set_ylim([0, 10], auto=True)
            a11.set_xlim([window_Xmin, window_Xmax])

            a5.set_ylim([YScale_minEOL, YScale_maxEOL], auto=True)
            a5.set_xlim([window_Xmin, window_Xmax])

            a12.set_ylim([0, 10], auto=True)
            a12.set_xlim([window_Xmin, window_Xmax])

            a6.set_ylim([YScale_minEOL, YScale_maxEOL], auto=True)
            a6.set_xlim([window_Xmin, window_Xmax])

            a13.set_ylim([0, 10], auto=True)
            a13.set_xlim([window_Xmin, window_Xmax])
            # ---- Report window for RC and VC ----
            a7.cla()
            a7.get_yaxis().set_visible(False)
            a7.get_xaxis().set_visible(False)

        # ---------------------------------------------------------[]
        # Define Plot area and axes -
        # ---------------------------------------------------------[1-5]
        if EoLRep == 'DNV':
            im10, = a1.plot([], [], 'o-', label='Tape Temp - (R1H1)')
            im11, = a1.plot([], [], 'o-', label='Tape Temp - (R1H2)')
            im12, = a1.plot([], [], 'o-', label='Tape Temp - (R1H3)')
            im13, = a1.plot([], [], 'o-', label='Tape Temp - (R1H4)')
            im14, = a1.plot([], [], 'o-', label='Tape Temp - (R2H1)')
            im15, = a1.plot([], [], 'o-', label='Tape Temp - (R2H2)')
            im16, = a1.plot([], [], 'o-', label='Tape Temp - (R2H3)')
            im17, = a1.plot([], [], 'o-', label='Tape Temp - (R2H4)')
            im18, = a1.plot([], [], 'o-', label='Tape Temp - (R3H1)')
            im19, = a1.plot([], [], 'o-', label='Tape Temp - (R3H2)')
            im20, = a1.plot([], [], 'o-', label='Tape Temp - (R3H3)')
            im21, = a1.plot([], [], 'o-', label='Tape Temp - (R3H4)')
            im22, = a1.plot([], [], 'o-', label='Tape Temp - (R4H1)')
            im23, = a1.plot([], [], 'o-', label='Tape Temp - (R4H2)')
            im24, = a1.plot([], [], 'o-', label='Tape Temp - (R4H3)')
            im25, = a1.plot([], [], 'o-', label='Tape Temp - (R4H4)')
            # -------------------------------------------------------
            im26, = a6.plot([], [], 'o-', label='Tape Temp')
            im27, = a6.plot([], [], 'o-', label='Tape Temp')
            im28, = a6.plot([], [], 'o-', label='Tape Temp')
            im29, = a6.plot([], [], 'o-', label='Tape Temp')
            im30, = a6.plot([], [], 'o-', label='Tape Temp')
            im31, = a6.plot([], [], 'o-', label='Tape Temp')
            im32, = a6.plot([], [], 'o-', label='Tape Temp')
            im33, = a6.plot([], [], 'o-', label='Tape Temp')
            im34, = a6.plot([], [], 'o-', label='Tape Temp')
            im35, = a6.plot([], [], 'o-', label='Tape Temp')
            im36, = a6.plot([], [], 'o-', label='Tape Temp')
            im37, = a6.plot([], [], 'o-', label='Tape Temp')
            im38, = a6.plot([], [], 'o-', label='Tape Temp')
            im39, = a6.plot([], [], 'o-', label='Tape Temp')
            im40, = a6.plot([], [], 'o-', label='Tape Temp')
            im41, = a6.plot([], [], 'o-', label='Tape Temp')
            # ---------------------------------------------------------[2-6]
            im42, = a2.plot([], [], 'o-', label='Substrate Temp - (R1H1)')
            im43, = a2.plot([], [], 'o-', label='Substrate Temp - (R1H2)')
            im44, = a2.plot([], [], 'o-', label='Substrate Temp - (R1H3)')
            im45, = a2.plot([], [], 'o-', label='Substrate Temp - (R1H4)')
            im46, = a2.plot([], [], 'o-', label='Substrate Temp - (R2H1)')
            im47, = a2.plot([], [], 'o-', label='Substrate Temp - (R2H2)')
            im48, = a2.plot([], [], 'o-', label='Substrate Temp - (R2H3)')
            im49, = a2.plot([], [], 'o-', label='Substrate Temp - (R2H4)')
            im50, = a2.plot([], [], 'o-', label='Substrate Temp - (R3H1)')
            im51, = a2.plot([], [], 'o-', label='Substrate Temp - (R3H2)')
            im52, = a2.plot([], [], 'o-', label='Substrate Temp - (R3H3)')
            im53, = a2.plot([], [], 'o-', label='Substrate Temp - (R3H4)')
            im54, = a2.plot([], [], 'o-', label='Substrate Temp - (R4H1)')
            im55, = a2.plot([], [], 'o-', label='Substrate Temp - (R4H2)')
            im56, = a2.plot([], [], 'o-', label='Substrate Temp - (R4H3)')
            im57, = a2.plot([], [], 'o-', label='Substrate Temp - (R4H4)')
            # -----------------------------------------------------------------
            im58, = a7.plot([], [], 'o-', label='Substrate Temp')
            im59, = a7.plot([], [], 'o-', label='Substrate Temp')
            im60, = a7.plot([], [], 'o-', label='Substrate Temp')
            im61, = a7.plot([], [], 'o-', label='Substrate Temp')
            im62, = a7.plot([], [], 'o-', label='Substrate Temp')
            im63, = a7.plot([], [], 'o-', label='Substrate Temp')
            im64, = a7.plot([], [], 'o-', label='Substrate Temp')
            im65, = a7.plot([], [], 'o-', label='Substrate Temp')
            im66, = a7.plot([], [], 'o-', label='Substrate Temp')
            im67, = a7.plot([], [], 'o-', label='Substrate Temp')
            im68, = a7.plot([], [], 'o-', label='Substrate Temp')
            im69, = a7.plot([], [], 'o-', label='Substrate Temp')
            im70, = a7.plot([], [], 'o-', label='Substrate Temp')
            im71, = a7.plot([], [], 'o-', label='Substrate Temp')
            im72, = a7.plot([], [], 'o-', label='Substrate Temp')
            im73, = a7.plot([], [], 'o-', label='Substrate Temp')
            # --------------------------------------------------[Tape Gap x8]
            im74, = a3.plot([], [], 'o-', label='Tape Gap - (A1)')
            im75, = a3.plot([], [], 'o-', label='Tape Gap - (A2)')
            im76, = a3.plot([], [], 'o-', label='Tape Gap - (A3)')
            im77, = a3.plot([], [], 'o-', label='Tape Gap - (A4)')
            im78, = a3.plot([], [], 'o-', label='Tape Gap - (B1)')
            im79, = a3.plot([], [], 'o-', label='Tape Gap - (B2)')
            im80, = a3.plot([], [], 'o-', label='Tape Gap - (B3)')
            im81, = a3.plot([], [], 'o-', label='Tape Gap - (B4)')
            # ------------
            im82, = a8.plot([], [], 'o-', label='Tape Gap')
            im83, = a8.plot([], [], 'o-', label='Tape Gap')
            im84, = a8.plot([], [], 'o-', label='Tape Gap')
            im85, = a8.plot([], [], 'o-', label='Tape Gap')
            im86, = a8.plot([], [], 'o-', label='Tape Gap')
            im87, = a8.plot([], [], 'o-', label='Tape Gap')
            im88, = a8.plot([], [], 'o-', label='Tape Gap')
            im89, = a8.plot([], [], 'o-', label='Tape Gap')
            # -------------------------------------------------------[Ramp Data]
            im90, = a4.plot([], [], 'o-', label='Winding Speed - (R1)')     # Ring 1 value
            im91, = a4.plot([], [], 'o-', label='Winding Speed - (R2)')     # Ring 2 value
            im92, = a4.plot([], [], 'o-', label='Winding Speed - (R3)')     # Ring 3 value
            im93, = a4.plot([], [], 'o-', label='Winding Speed - (R4)')     # Ring 4 value
            im94, = a9.plot([], [], 'o-', label='Winding Speed')
            im95, = a9.plot([], [], 'o-', label='Winding Speed')
            im96, = a9.plot([], [], 'o-', label='Winding Speed')
            im97, = a9.plot([], [], 'o-', label='Winding Speed')
        else:
            EoLRep = 'MGM'
            # ---------------------------------------------------[Laser Power T5 x16]
            im10, = a1.plot([], [], 'o-', label='Laser Power - (R1H1)')
            im11, = a1.plot([], [], 'o-', label='Laser Power - (R1H2)')
            im12, = a1.plot([], [], 'o-', label='Laser Power - (R1H3)')
            im13, = a1.plot([], [], 'o-', label='Laser Power - (R1H4)')
            im14, = a1.plot([], [], 'o-', label='Laser Power - (R2H1)')
            im15, = a1.plot([], [], 'o-', label='Laser Power - (R2H2)')
            im16, = a1.plot([], [], 'o-', label='Laser Power - (R2H3)')
            im17, = a1.plot([], [], 'o-', label='Laser Power - (R2H4)')
            im18, = a1.plot([], [], 'o-', label='Laser Power - (R3H1)')
            im19, = a1.plot([], [], 'o-', label='Laser Power - (R3H2)')
            im20, = a1.plot([], [], 'o-', label='Laser Power - (R3H3)')
            im21, = a1.plot([], [], 'o-', label='Laser Power - (R3H4)')
            im22, = a1.plot([], [], 'o-', label='Laser Power - (R4H1)')
            im23, = a1.plot([], [], 'o-', label='Laser Power - (R4H2)')
            im24, = a1.plot([], [], 'o-', label='Laser Power - (R4H3)')
            im25, = a1.plot([], [], 'o-', label='Laser Power - (R4H4)')

            im26, = a8.plot([], [], 'o-', label='Laser Power')
            im27, = a8.plot([], [], 'o-', label='Laser Power')
            im28, = a8.plot([], [], 'o-', label='Laser Power')
            im29, = a8.plot([], [], 'o-', label='Laser Power')
            im30, = a8.plot([], [], 'o-', label='Laser Power')
            im31, = a8.plot([], [], 'o-', label='Laser Power')
            im32, = a8.plot([], [], 'o-', label='Laser Power')
            im33, = a8.plot([], [], 'o-', label='Laser Power')
            im34, = a8.plot([], [], 'o-', label='Laser Power')
            im35, = a8.plot([], [], 'o-', label='Laser Power')
            im36, = a8.plot([], [], 'o-', label='Laser Power')
            im37, = a8.plot([], [], 'o-', label='Laser Power')
            im38, = a8.plot([], [], 'o-', label='Laser Power')
            im39, = a8.plot([], [], 'o-', label='Laser Power')
            im40, = a8.plot([], [], 'o-', label='Laser Power')
            im41, = a8.plot([], [], 'o-', label='Laser Power')
            # ---------------------------------------------------[Laser Angle x16]
            im42, = a2.plot([], [], 'o-', label='Laser Angle - (R1H1)')
            im43, = a2.plot([], [], 'o-', label='Laser Angle - (R1H2)')
            im44, = a2.plot([], [], 'o-', label='Laser Angle - (R1H3)')
            im45, = a2.plot([], [], 'o-', label='Laser Angle - (R1H4)')
            im46, = a2.plot([], [], 'o-', label='Laser Angle - (R2H1)')
            im47, = a2.plot([], [], 'o-', label='Laser Angle - (R2H2)')
            im48, = a2.plot([], [], 'o-', label='Laser Angle - (R2H3)')
            im49, = a2.plot([], [], 'o-', label='Laser Angle - (R2H4)')
            im50, = a2.plot([], [], 'o-', label='Laser Angle - (R3H1)')
            im51, = a2.plot([], [], 'o-', label='Laser Angle - (R3H2)')
            im52, = a2.plot([], [], 'o-', label='Laser Angle - (R3H3)')
            im53, = a2.plot([], [], 'o-', label='Laser Angle - (R3H4)')
            im54, = a2.plot([], [], 'o-', label='Laser Angle - (R4H1)')
            im55, = a2.plot([], [], 'o-', label='Laser Angle - (R4H2)')
            im56, = a2.plot([], [], 'o-', label='Laser Angle - (R4H3)')
            im57, = a2.plot([], [], 'o-', label='Laser Angle - (R4H4)')
            # -----------------------------------------------------------------
            im58, = a9.plot([], [], 'o-', label='Laser Angle')
            im59, = a9.plot([], [], 'o-', label='Laser Angle')
            im60, = a9.plot([], [], 'o-', label='Laser Angle')
            im61, = a9.plot([], [], 'o-', label='Laser Angle')
            im62, = a9.plot([], [], 'o-', label='Laser Angle')
            im63, = a9.plot([], [], 'o-', label='Laser Angle')
            im64, = a9.plot([], [], 'o-', label='Laser Angle')
            im65, = a9.plot([], [], 'o-', label='Laser Angle')
            im66, = a9.plot([], [], 'o-', label='Laser Angle')
            im67, = a9.plot([], [], 'o-', label='Laser Angle')
            im68, = a9.plot([], [], 'o-', label='Laser Angle')
            im69, = a9.plot([], [], 'o-', label='Laser Angle')
            im70, = a9.plot([], [], 'o-', label='Laser Angle')
            im71, = a9.plot([], [], 'o-', label='Laser Angle')
            im72, = a9.plot([], [], 'o-', label='Laser Angle')
            im73, = a9.plot([], [], 'o-', label='Laser Angle')

            # ----------------------------------------[Tape Temperature x16]
            im74, = a3.plot([], [], 'o-', label='Tape Temp - (R1H1)')
            im75, = a3.plot([], [], 'o-', label='Tape Temp - (R1H2)')
            im76, = a3.plot([], [], 'o-', label='Tape Temp - (R1H3)')
            im77, = a3.plot([], [], 'o-', label='Tape Temp - (R1H4)')
            im78, = a3.plot([], [], 'o-', label='Tape Temp - (R2H1)')
            im79, = a3.plot([], [], 'o-', label='Tape Temp - (R2H2)')
            im80, = a3.plot([], [], 'o-', label='Tape Temp - (R2H3)')
            im81, = a3.plot([], [], 'o-', label='Tape Temp - (R2H4)')
            im82, = a3.plot([], [], 'o-', label='Tape Temp - (R3H1)')
            im83, = a3.plot([], [], 'o-', label='Tape Temp - (R3H2)')
            im84, = a3.plot([], [], 'o-', label='Tape Temp - (R3H3)')
            im85, = a3.plot([], [], 'o-', label='Tape Temp - (R3H4)')
            im86, = a3.plot([], [], 'o-', label='Tape Temp - (R4H1)')
            im87, = a3.plot([], [], 'o-', label='Tape Temp - (R4H2)')
            im88, = a3.plot([], [], 'o-', label='Tape Temp - (R4H3)')
            im89, = a3.plot([], [], 'o-', label='Tape Temp - (R4H4)')

            im90, = a10.plot([], [], 'o-', label='Tape Temp')
            im91, = a10.plot([], [], 'o-', label='Tape Temp')
            im92, = a10.plot([], [], 'o-', label='Tape Temp')
            im93, = a10.plot([], [], 'o-', label='Tape Temp')
            im94, = a10.plot([], [], 'o-', label='Tape Temp')
            im95, = a10.plot([], [], 'o-', label='Tape Temp')
            im96, = a10.plot([], [], 'o-', label='Tape Temp')
            im97, = a10.plot([], [], 'o-', label='Tape Temp')
            im98, = a10.plot([], [], 'o-', label='Tape Temp')
            im99, = a10.plot([], [], 'o-', label='Tape Temp')
            im100, = a10.plot([], [], 'o-', label='Tape Temp')
            im101, = a10.plot([], [], 'o-', label='Tape Temp')
            im102, = a10.plot([], [], 'o-', label='Tape Temp')
            im103, = a10.plot([], [], 'o-', label='Tape Temp')
            im104, = a10.plot([], [], 'o-', label='Tape Temp')
            im105, = a10.plot([], [], 'o-', label='Tape Temp')
            # ----------------------------------------[Substrate Temperature x16]
            im106, = a4.plot([], [], 'o-', label='Substrate Temp - (R1H1)')
            im107, = a4.plot([], [], 'o-', label='Substrate Temp - (R1H2)')
            im108, = a4.plot([], [], 'o-', label='Substrate Temp - (R1H3)')
            im109, = a4.plot([], [], 'o-', label='Substrate Temp - (R1H4)')
            im110, = a4.plot([], [], 'o-', label='Substrate Temp - (R2H1)')
            im111, = a4.plot([], [], 'o-', label='Substrate Temp - (R2H2)')
            im112, = a4.plot([], [], 'o-', label='Substrate Temp - (R2H3)')
            im113, = a4.plot([], [], 'o-', label='Substrate Temp - (R2H4)')
            im114, = a4.plot([], [], 'o-', label='Substrate Temp - (R3H1)')
            im115, = a4.plot([], [], 'o-', label='Substrate Temp - (R3H2)')
            im116, = a4.plot([], [], 'o-', label='Substrate Temp - (R3H3)')
            im117, = a4.plot([], [], 'o-', label='Substrate Temp - (R3H4)')
            im118, = a4.plot([], [], 'o-', label='Substrate Temp - (R4H1)')
            im119, = a4.plot([], [], 'o-', label='Substrate Temp - (R4H2)')
            im120, = a4.plot([], [], 'o-', label='Substrate Temp - (R4H3)')
            im121, = a4.plot([], [], 'o-', label='Substrate Temp - (R4H4)')
            # ------
            im122, = a11.plot([], [], 'o-', label='Substrate Temp')
            im123, = a11.plot([], [], 'o-', label='Substrate Temp')
            im124, = a11.plot([], [], 'o-', label='Substrate Temp')
            im125, = a11.plot([], [], 'o-', label='Substrate Temp')
            im126, = a11.plot([], [], 'o-', label='Substrate Temp')
            im127, = a11.plot([], [], 'o-', label='Substrate Temp')
            im128, = a11.plot([], [], 'o-', label='Substrate Temp')
            im129, = a11.plot([], [], 'o-', label='Substrate Temp')
            im130, = a11.plot([], [], 'o-', label='Substrate Temp')
            im131, = a11.plot([], [], 'o-', label='Substrate Temp')
            im132, = a11.plot([], [], 'o-', label='Substrate Temp')
            im133, = a11.plot([], [], 'o-', label='Substrate Temp')
            im134, = a11.plot([], [], 'o-', label='Substrate Temp')
            im135, = a11.plot([], [], 'o-', label='Substrate Temp')
            im136, = a11.plot([], [], 'o-', label='Substrate Temp')
            im137, = a11.plot([], [], 'o-', label='Substrate Temp')
            # --------------------------------------------------[Tape Gap x8]
            im138, = a5.plot([], [], 'o-', label='Tape Gap - (A1)')
            im139, = a5.plot([], [], 'o-', label='Tape Gap - (A2)')
            im140, = a5.plot([], [], 'o-', label='Tape Gap - (A3)')
            im141, = a5.plot([], [], 'o-', label='Tape Gap - (A4)')
            im142, = a5.plot([], [], 'o-', label='Tape Gap - (B1)')
            im143, = a5.plot([], [], 'o-', label='Tape Gap - (B2)')
            im144, = a5.plot([], [], 'o-', label='Tape Gap - (B3)')
            im145, = a5.plot([], [], 'o-', label='Tape Gap - (B4)')

            im146, = a12.plot([], [], 'o-', label='Tape Gap')
            im147, = a12.plot([], [], 'o-', label='Tape Gap')
            im148, = a12.plot([], [], 'o-', label='Tape Gap')
            im149, = a12.plot([], [], 'o-', label='Tape Gap')
            im150, = a12.plot([], [], 'o-', label='Tape Gap')
            im151, = a12.plot([], [], 'o-', label='Tape Gap')
            im152, = a12.plot([], [], 'o-', label='Tape Gap')
            im153, = a12.plot([], [], 'o-', label='Tape Gap')

            # -------------------------------------------------------[Ramp Data T4]
            im154, = a6.plot([], [], 'o-', label='Winding Angle - (R1H1)')  # Ring 1 value count per layer
            im155, = a6.plot([], [], 'o-', label='Winding Angle - (R1H2)')  # Ring 2 value count per layer
            im156, = a6.plot([], [], 'o-', label='Winding Angle - (R1H3)')  # Ring 3 value count per layer
            im157, = a6.plot([], [], 'o-', label='Winding Angle - (R1H4)')  # Ring 4 value count per layer
            # ---
            im158, = a6.plot([], [], 'o-', label='Winding Angle - (R2H1)')  # Ring 1 value count per layer
            im159, = a6.plot([], [], 'o-', label='Winding Angle - (R2H2)')  # Ring 2 value count per layer
            im160, = a6.plot([], [], 'o-', label='Winding Angle - (R2H3)')  # Ring 3 value count per layer
            im161, = a6.plot([], [], 'o-', label='Winding Angle - (R2H4)')
            #-----
            im162, = a6.plot([], [], 'o-', label='Winding Angle - (R2H1)')  # Ring 1 value count per layer
            im163, = a6.plot([], [], 'o-', label='Winding Angle - (R2H2)')  # Ring 2 value count per layer
            im164, = a6.plot([], [], 'o-', label='Winding Angle - (R2H3)')  # Ring 3 value count per layer
            im165, = a6.plot([], [], 'o-', label='Winding Angle - (R2H4)')
            # ------
            im166, = a6.plot([], [], 'o-', label='Winding Angle - (R2H1)')  # Ring 1 value count per layer
            im167, = a6.plot([], [], 'o-', label='Winding Angle - (R2H2)')  # Ring 2 value count per layer
            im168, = a6.plot([], [], 'o-', label='Winding Angle - (R2H3)')  # Ring 3 value count per layer
            im169, = a6.plot([], [], 'o-', label='Winding Angle - (R2H4)')
            # ------ -----------------------------------------------Std Dev
            im170, = a13.plot([], [], 'o-', label='Winding Angle')  # Ring 1 value count per layer
            im171, = a13.plot([], [], 'o-', label='Winding Angle')  # Ring 2 value count per layer
            im172, = a13.plot([], [], 'o-', label='Winding Angle')  # Ring 3 value count per layer
            im173, = a13.plot([], [], 'o-', label='Winding Angle)')
            im174, = a13.plot([], [], 'o-', label='Winding Angle')  # Ring 1 value count per layer
            im175, = a13.plot([], [], 'o-', label='Winding Angle')  # Ring 2 value count per layer
            im176, = a13.plot([], [], 'o-', label='Winding Angle')  # Ring 3 value count per layer
            im177, = a13.plot([], [], 'o-', label='Winding Angle)')
            im178, = a13.plot([], [], 'o-', label='Winding Angle')  # Ring 1 value count per layer
            im179, = a13.plot([], [], 'o-', label='Winding Angle')  # Ring 2 value count per layer
            im180, = a13.plot([], [], 'o-', label='Winding Angle')  # Ring 3 value count per layer
            im181, = a13.plot([], [], 'o-', label='Winding Angle)')
            im182, = a13.plot([], [], 'o-', label='Winding Angle')  # Ring 1 value count per layer
            im183, = a13.plot([], [], 'o-', label='Winding Angle')  # Ring 2 value count per layer
            im184, = a13.plot([], [], 'o-', label='Winding Angle')  # Ring 3 value count per layer
            im185, = a13.plot([], [], 'o-', label='Winding Angle)')

            # ---------------- EXECUTE SYNCHRONOUS METHOD -----------------------------#

        def synchronousEoL(layerNo):

            # Initialise SQL Data connection per listed Table --------------------[]
            if EoLRep == 'DNV':
                l1, l2, l3, l4, l5, l6 = conn.cursor(), conn.cursor(), conn.cursor(), conn.cursor(), conn.cursor(), conn.cursor()
            else: # EoLRep == 'MGM':
                l1, l2, l3, l4, l5, l6, l7, l8 = (conn.cursor(), conn.cursor(), conn.cursor(), conn.cursor(),
                                                  conn.cursor(), conn.cursor(), conn.cursor(), conn.cursor())

            """
            Load watchdog function with synchronous function every seconds
            """
            # Initialise variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard                                         # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                import sqlArrayRLmethodEoL as sel                   # DrLabs optimization method

                # ------ Process data fetch sequences pData, Void Count + Ramp Count ----------------------#
                if EoLRep == 'DNV': # [+ RampCount & VoidCount]
                    rpTT, rpST, rpTG, rpWS, r1RC, r2RC, r3RC, r4RC, rR1VC, r2VC, r3VC, r4VC = sel.dnv_sqlExec(
                        l1, l2, l3, l4, l5, l6, T1, T2, T3, T4, T5, T6, layerNo)
                else:
                    rpLP, rpLA, rpTT, rpST, rpTG, rpWA, r1RC, r2RC, r3RC, r4RC, rR1VC, r2VC, r3VC, r4VC = sel.mgm_sqlExec(
                        l1, l2, l3, l4, l5, l6, l7, l8, T1, T2, T3, T4, T5, T6, T7, T8, layerNo)

                # --- Conditional break when ----- Assuming all data were pooled at once ---
                if rpTT > 0 and rpST > 0 and rpTG > 0 and rpLA > 0:
                    break

            if EoLRep == 'DNV':
                 return rpTT, rpST, rpTG, rpWS, r1RC, r2RC, r3RC, r4RC, rR1VC, r2VC, r3VC, r4VC
            else:
                return rpLP, rpLA, rpTT, rpST, rpTG, rpWA, r1RC, r2RC, r3RC, r4RC, rR1VC, r2VC, r3VC, r4VC

        # ================== End of synchronous Method =======================================================[]

        def asynchronousEoL(layerNo):
            global zTT, zST, zTG, zWS, zWA, r1RC, r2RC, r3RC, r4RC, rR1VC, r2VC, r3VC, r4VC, rptID

            timei = time.time()  # start timing the entire loop
            # --------- Generate Unique ID for pdf report ------#
            rptID = random_with_N_digits(10)
            # Obtain fetch SQl data from respective Tables -----#

            if EoLRep == 'DNV':
                zTT, zST, zTG, zWS, r1RC, r2RC, r3RC, r4RC, rR1VC, r2VC, r3VC, r4VC = synchronousEoL(layerNo)
            else:
                zLP, zLA, zTT, zST, zTG, zWA, r1RC, r2RC, r3RC, r4RC, rR1VC, r2VC, r3VC, r4VC = synchronousEoL(layerNo)

            # --------------------------------------------------#

            import VarSQL_EOLRPT as el                          # load SQL variables column names | rfVarSQL

            if EoLRep == 'DNV':
                g1 = ott.validCols(T1)                          # Construct Table Column (Tape Temp)
                d1 = pd.DataFrame(zTT, columns=g1)
                g2 = ost.validCols(T2)                          # Construct Table Column (Sub Temp)
                d2 = pd.DataFrame(zST, columns=g2)
                g3 = otg.validCols(T3)                          # Construct Table Column (Tape Gap)
                d3 = pd.DataFrame(zTG, columns=g3)
                g4 = ows.validCols(T4)                          # Construct Table Column (Tape Gap)
                d4 = pd.DataFrame(zWS, columns=g4)
                # Concatenate all columns ----------------------[]
                df1 = pd.concat([d1, d2, d3, d4], axis=1)

            elif EoLRep == 'MGM':
                g1 = olp.validCols(T1)                          # Laser Power - Construct Table Column (Tape Temp)
                d1 = pd.DataFrame(zLP, columns=g1)
                g2 = ola.validCols(T2)                          # Laser Angle - Construct Table Column (Sub Temp)
                d2 = pd.DataFrame(zLA, columns=g2)
                g3 = olp.validCols(T3)                          # Construct Table Column (Tape Gap)
                d3 = pd.DataFrame(zTT, columns=g3)
                g4 = ott.validCols(T4)                          # Construct Table Column (Tape Temp)
                d4 = pd.DataFrame(zST, columns=g4)
                g5 = ost.validCols(T5)                          # Construct Table Column (Sub Temp)
                d5 = pd.DataFrame(zTG, columns=g5)
                g6 = otg.validCols(T6)                          # Construct Table Column (Tape Gap)
                d6 = pd.DataFrame(zWA, columns=g6)
                # Concatenate all columns ----------------------[]
                df1 = pd.concat([d1, d2, d3, d4, d5, d6], axis=1)

            else:
                df1 = 0
                pass

            # ----- Access data element within the concatenated columns -------------------------[A]
            ZX = el.loadProcesValues(df1, EoLRep)
            print('\nSQL Content', df1.head(10))
            print("Memory Usage:", df1.info(verbose=False))     # Check memory utilization
            # -------------------------------------------------------------------------------------[]
            # Plot X-Axis data points -------- X Plot TT
            # im10.set_xdata(np.arange(db_freq))
            im10.set_xdata(range(0, pLength))
            im11.set_xdata(range(0, pLength))
            im12.set_xdata(range(0, pLength))
            im13.set_xdata(range(0, pLength))
            im14.set_xdata(range(0, pLength))
            im15.set_xdata(range(0, pLength))
            im16.set_xdata(range(0, pLength))
            im17.set_xdata(range(0, pLength))
            im18.set_xdata(range(0, pLength))
            im19.set_xdata(range(0, pLength))
            im20.set_xdata(range(0, pLength))
            im21.set_xdata(range(0, pLength))
            im22.set_xdata(range(0, pLength))
            im23.set_xdata(range(0, pLength))
            im24.set_xdata(range(0, pLength))
            im25.set_xdata(range(0, pLength))
            # ------------------------------- S Plot TT
            im26.set_xdata(range(0, pLength))
            im27.set_xdata(range(0, pLength))
            im28.set_xdata(range(0, pLength))
            im29.set_xdata(range(0, pLength))
            im30.set_xdata(range(0, pLength))
            im31.set_xdata(range(0, pLength))
            im32.set_xdata(range(0, pLength))
            im33.set_xdata(range(0, pLength))
            im34.set_xdata(range(0, pLength))
            im35.set_xdata(range(0, pLength))
            im36.set_xdata(range(0, pLength))
            im37.set_xdata(range(0, pLength))
            im38.set_xdata(range(0, pLength))
            im39.set_xdata(range(0, pLength))
            im40.set_xdata(range(0, pLength))
            im41.set_xdata(range(0, pLength))
            # ------------------------------- X Plot ST
            im42.set_xdata(range(0, pLength))
            im43.set_xdata(range(0, pLength))
            im44.set_xdata(range(0, pLength))
            im45.set_xdata(range(0, pLength))
            im46.set_xdata(range(0, pLength))
            im47.set_xdata(range(0, pLength))
            im49.set_xdata(range(0, pLength))
            im50.set_xdata(range(0, pLength))
            im51.set_xdata(range(0, pLength))
            im52.set_xdata(range(0, pLength))
            im53.set_xdata(range(0, pLength))
            im54.set_xdata(range(0, pLength))
            im55.set_xdata(range(0, pLength))
            im56.set_xdata(range(0, pLength))
            im56.set_xdata(range(0, pLength))
            im57.set_xdata(range(0, pLength))
            # ------------------------------- S Plot ST
            im58.set_xdata(range(0, pLength))
            im59.set_xdata(range(0, pLength))
            im60.set_xdata(range(0, pLength))
            im61.set_xdata(range(0, pLength))
            im62.set_xdata(range(0, pLength))
            im63.set_xdata(range(0, pLength))
            im64.set_xdata(range(0, pLength))
            im65.set_xdata(range(0, pLength))
            im66.set_xdata(range(0, pLength))
            im67.set_xdata(range(0, pLength))
            im68.set_xdata(range(0, pLength))
            im69.set_xdata(range(0, pLength))
            im70.set_xdata(range(0, pLength))
            im71.set_xdata(range(0, pLength))
            im72.set_xdata(range(0, pLength))
            im73.set_xdata(range(0, pLength))
            # ------------------------------- X Plot TG
            im74.set_xdata(range(0, pLength))
            im75.set_xdata(range(0, pLength))
            im76.set_xdata(range(0, pLength))
            im77.set_xdata(range(0, pLength))
            im78.set_xdata(range(0, pLength))
            im79.set_xdata(range(0, pLength))
            im80.set_xdata(range(0, pLength))
            im81.set_xdata(range(0, pLength))
            # --------------------------- S Plot TG
            im82.set_xdata(range(0, pLength))
            im83.set_xdata(range(0, pLength))
            im84.set_xdata(range(0, pLength))
            im85.set_xdata(range(0, pLength))
            im86.set_xdata(range(0, pLength))
            im87.set_xdata(range(0, pLength))
            im88.set_xdata(range(0, pLength))
            im89.set_xdata(range(0, pLength))
            # ------------------------------ Value Plot RM, No X/S Plots -
            im90.set_xdata(range(0, pLength))
            im91.set_xdata(range(0, pLength))
            im92.set_xdata(range(0, pLength))
            im93.set_xdata(range(0, pLength))
            im94.set_xdata(range(0, pLength))
            im95.set_xdata(range(0, pLength))
            im96.set_xdata(range(0, pLength))
            im97.set_xdata(range(0, pLength))
            # --------------------------- X Plot for LP

            im98.set_xdata(range(0, pLength))
            im99.set_xdata(range(0, pLength))
            im100.set_xdata(range(0, pLength))
            im101.set_xdata(range(0, pLength))
            im102.set_xdata(range(0, pLength))
            im103.set_xdata(range(0, pLength))
            im104.set_xdata(range(0, pLength))
            im105.set_xdata(range(0, pLength))
            im106.set_xdata(range(0, pLength))
            im107.set_xdata(range(0, pLength))
            im108.set_xdata(range(0, pLength))
            im109.set_xdata(range(0, pLength))
            # ---------------------------- S Plot
            im110.set_xdata(range(0, pLength))
            im111.set_xdata(range(0, pLength))
            im112.set_xdata(range(0, pLength))
            im113.set_xdata(range(0, pLength))
            im114.set_xdata(range(0, pLength))
            im115.set_xdata(range(0, pLength))
            im116.set_xdata(range(0, pLength))
            im117.set_xdata(range(0, pLength))
            im118.set_xdata(range(0, pLength))
            im119.set_xdata(range(0, pLength))
            im120.set_xdata(range(0, pLength))
            im121.set_xdata(range(0, pLength))
            im122.set_xdata(range(0, pLength))
            im123.set_xdata(range(0, pLength))
            im124.set_xdata(range(0, pLength))
            im125.set_xdata(range(0, pLength))
            # ---------------------------- S Plot
            im126.set_xdata(range(0, pLength))
            im127.set_xdata(range(0, pLength))
            im128.set_xdata(range(0, pLength))
            im129.set_xdata(range(0, pLength))
            im130.set_xdata(range(0, pLength))
            im131.set_xdata(range(0, pLength))
            im132.set_xdata(range(0, pLength))
            im133.set_xdata(range(0, pLength))
            im134.set_xdata(range(0, pLength))
            im135.set_xdata(range(0, pLength))
            im136.set_xdata(range(0, pLength))
            im137.set_xdata(range(0, pLength))
            im138.set_xdata(range(0, pLength))
            im139.set_xdata(range(0, pLength))
            im140.set_xdata(range(0, pLength))
            im141.set_xdata(range(0, pLength))
            # ---------------------------- XS Plot
            im142.set_xdata(range(0, pLength))
            im143.set_xdata(range(0, pLength))
            im144.set_xdata(range(0, pLength))
            im145.set_xdata(range(0, pLength))
            im146.set_xdata(range(0, pLength))
            im147.set_xdata(range(0, pLength))
            im148.set_xdata(range(0, pLength))
            im149.set_xdata(range(0, pLength))
            im150.set_xdata(range(0, pLength))
            im151.set_xdata(range(0, pLength))
            im152.set_xdata(range(0, pLength))
            im153.set_xdata(range(0, pLength))
            im154.set_xdata(range(0, pLength))
            im155.set_xdata(range(0, pLength))
            im156.set_xdata(range(0, pLength))
            im157.set_xdata(range(0, pLength))
            # ---------------------------- XS Plot
            im158.set_xdata(range(0, pLength))
            im159.set_xdata(range(0, pLength))
            im160.set_xdata(range(0, pLength))
            im161.set_xdata(range(0, pLength))
            im162.set_xdata(range(0, pLength))
            im163.set_xdata(range(0, pLength))
            im164.set_xdata(range(0, pLength))
            im165.set_xdata(range(0, pLength))
            im166.set_xdata(range(0, pLength))
            im167.set_xdata(range(0, pLength))
            im168.set_xdata(range(0, pLength))
            im169.set_xdata(range(0, pLength))
            im170.set_xdata(range(0, pLength))
            im171.set_xdata(range(0, pLength))
            im172.set_xdata(range(0, pLength))
            im173.set_xdata(range(0, pLength))
            # ---------------------------- XS Plot
            im174.set_xdata(range(0, pLength))
            im175.set_xdata(range(0, pLength))
            im176.set_xdata(range(0, pLength))
            im177.set_xdata(range(0, pLength))
            im178.set_xdata(range(0, pLength))
            im179.set_xdata(range(0, pLength))
            im180.set_xdata(range(0, pLength))
            im181.set_xdata(range(0, pLength))
            im182.set_xdata(range(0, pLength))
            im183.set_xdata(range(0, pLength))
            im184.set_xdata(range(0, pLength))
            im185.set_xdata(range(0, pLength))

            if EoLRep == 'DNV':
                # X Plot Y-Axis data points for XBar ---------------------------------------------[ Mean TT ]
                im10.set_ydata((ZX[0]).rolling(window=ttS, min_periods=1).mean())  # head 1
                im11.set_ydata((ZX[1]).rolling(window=ttS, min_periods=1).mean())  # head 2
                im12.set_ydata((ZX[2]).rolling(window=ttS, min_periods=1).mean())  # head 3
                im13.set_ydata((ZX[3]).rolling(window=ttS, min_periods=1).mean())  # head 4
                im14.set_ydata((ZX[4]).rolling(window=ttS, min_periods=1).mean())  # head 1
                im15.set_ydata((ZX[5]).rolling(window=ttS, min_periods=1).mean())  # head 2
                im16.set_ydata((ZX[6]).rolling(window=ttS, min_periods=1).mean())  # head 3
                im17.set_ydata((ZX[7]).rolling(window=ttS, min_periods=1).mean())  # head 4
                im18.set_ydata((ZX[8]).rolling(window=ttS, min_periods=1).mean())  # head 1
                im19.set_ydata((ZX[9]).rolling(window=ttS, min_periods=1).mean())  # head 2
                im20.set_ydata((ZX[10]).rolling(window=ttS, min_periods=1).mean())  # head 3
                im21.set_ydata((ZX[11]).rolling(window=ttS, min_periods=1).mean())  # head 4
                im22.set_ydata((ZX[12]).rolling(window=ttS, min_periods=1).mean())  # head 1
                im23.set_ydata((ZX[13]).rolling(window=ttS, min_periods=1).mean())  # head 2
                im24.set_ydata((ZX[14]).rolling(window=ttS, min_periods=1).mean())  # head 3
                im25.set_ydata((ZX[15]).rolling(window=ttS, min_periods=1).mean())  # head 4
                # ---------------------------------------[T1 std Dev]
                im26.set_ydata((ZX[0]).rolling(window=ttS, min_periods=1).std())
                im27.set_ydata((ZX[1]).rolling(window=ttS, min_periods=1).std())
                im28.set_ydata((ZX[2]).rolling(window=ttS, min_periods=1).std())
                im29.set_ydata((ZX[3]).rolling(window=ttS, min_periods=1).std())
                im30.set_ydata((ZX[4]).rolling(window=ttS, min_periods=1).std())
                im31.set_ydata((ZX[5]).rolling(window=ttS, min_periods=1).std())
                im32.set_ydata((ZX[6]).rolling(window=ttS, min_periods=1).std())
                im33.set_ydata((ZX[7]).rolling(window=ttS, min_periods=1).std())
                im34.set_ydata((ZX[8]).rolling(window=ttS, min_periods=1).std())
                im35.set_ydata((ZX[9]).rolling(window=ttS, min_periods=1).std())
                im36.set_ydata((ZX[10]).rolling(window=ttS, min_periods=1).std())
                im37.set_ydata((ZX[11]).rolling(window=ttS, min_periods=1).std())
                im38.set_ydata((ZX[12]).rolling(window=ttS, min_periods=1).std())
                im39.set_ydata((ZX[13]).rolling(window=ttS, min_periods=1).std())
                im40.set_ydata((ZX[14]).rolling(window=ttS, min_periods=1).std())
                im41.set_ydata((ZX[15]).rolling(window=ttS, min_periods=1).std())
                # ----------------------------------------------------------------------[Mean ST]
                im42.set_ydata((ZX[16]).rolling(window=stS, min_periods=1).mean())
                im43.set_ydata((ZX[17]).rolling(window=stS, min_periods=1).mean())
                im44.set_ydata((ZX[18]).rolling(window=stS, min_periods=1).mean())
                im45.set_ydata((ZX[19]).rolling(window=stS, min_periods=1).mean())
                im46.set_ydata((ZX[20]).rolling(window=stS, min_periods=1).mean())
                im47.set_ydata((ZX[21]).rolling(window=stS, min_periods=1).mean())
                im48.set_ydata((ZX[22]).rolling(window=stS, min_periods=1).mean())
                im49.set_ydata((ZX[23]).rolling(window=stS, min_periods=1).mean())
                im50.set_ydata((ZX[24]).rolling(window=stS, min_periods=1).mean())
                im51.set_ydata((ZX[25]).rolling(window=stS, min_periods=1).mean())
                im52.set_ydata((ZX[26]).rolling(window=stS, min_periods=1).mean())
                im53.set_ydata((ZX[27]).rolling(window=stS, min_periods=1).mean())
                im54.set_ydata((ZX[28]).rolling(window=stS, min_periods=1).mean())
                im55.set_ydata((ZX[29]).rolling(window=stS, min_periods=1).mean())
                im56.set_ydata((ZX[30]).rolling(window=stS, min_periods=1).mean())
                im57.set_ydata((ZX[31]).rolling(window=stS, min_periods=1).mean())
                # ---------------------------------------[T2 std Dev]
                im58.set_ydata((ZX[16]).rolling(window=stS, min_periods=1).std())
                im59.set_ydata((ZX[17]).rolling(window=stS, min_periods=1).std())
                im60.set_ydata((ZX[18]).rolling(window=stS, min_periods=1).std())
                im61.set_ydata((ZX[19]).rolling(window=stS, min_periods=1).std())
                im62.set_ydata((ZX[20]).rolling(window=stS, min_periods=1).std())
                im63.set_ydata((ZX[21]).rolling(window=stS, min_periods=1).std())
                im64.set_ydata((ZX[22]).rolling(window=stS, min_periods=1).std())
                im65.set_ydata((ZX[23]).rolling(window=stS, min_periods=1).std())
                im66.set_ydata((ZX[24]).rolling(window=stS, min_periods=1).std())
                im67.set_ydata((ZX[25]).rolling(window=stS, min_periods=1).std())
                im68.set_ydata((ZX[26]).rolling(window=stS, min_periods=1).std())
                im69.set_ydata((ZX[27]).rolling(window=stS, min_periods=1).std())
                im70.set_ydata((ZX[28]).rolling(window=stS, min_periods=1).std())
                im71.set_ydata((ZX[29]).rolling(window=stS, min_periods=1).std())
                im72.set_ydata((ZX[30]).rolling(window=stS, min_periods=1).std())
                im73.set_ydata((ZX[31]).rolling(window=stS, min_periods=1).std())
                # ------------------------------------------------------------------[Mean TG]
                im74.set_ydata((ZX[32]).rolling(window=tgS, min_periods=1).mean())
                im75.set_ydata((ZX[33]).rolling(window=tgS, min_periods=1).mean())
                im76.set_ydata((ZX[34]).rolling(window=tgS, min_periods=1).mean())
                im77.set_ydata((ZX[35]).rolling(window=tgS, min_periods=1).mean())
                im78.set_ydata((ZX[36]).rolling(window=tgS, min_periods=1).mean())
                im79.set_ydata((ZX[37]).rolling(window=tgS, min_periods=1).mean())
                im80.set_ydata((ZX[38]).rolling(window=tgS, min_periods=1).mean())
                im81.set_ydata((ZX[39]).rolling(window=tgS, min_periods=1).mean())
                # ---------------------------------------[TG std Dev]
                im82.set_ydata((ZX[32]).rolling(window=tgS, min_periods=1).std())
                im83.set_ydata((ZX[33]).rolling(window=tgS, min_periods=1).std())
                im84.set_ydata((ZX[34]).rolling(window=tgS, min_periods=1).std())
                im85.set_ydata((ZX[35]).rolling(window=tgS, min_periods=1).std())
                im86.set_ydata((ZX[36]).rolling(window=tgS, min_periods=1).std())
                im87.set_ydata((ZX[37]).rolling(window=tgS, min_periods=1).std())
                im88.set_ydata((ZX[38]).rolling(window=tgS, min_periods=1).std())
                im89.set_ydata((ZX[39]).rolling(window=tgS, min_periods=1).std())
                # --------------------------------------------------------------------------- [Mean WS]
                im74.set_ydata((ZX[32]).rolling(window=wsS, min_periods=1).mean())
                im75.set_ydata((ZX[33]).rolling(window=wsS, min_periods=1).mean())
                im76.set_ydata((ZX[34]).rolling(window=wsS, min_periods=1).mean())
                im77.set_ydata((ZX[35]).rolling(window=wsS, min_periods=1).mean())
                # ---------------------------------------[Std Dev]
                im78.set_ydata((ZX[36]).rolling(window=wsS, min_periods=1).std())
                im79.set_ydata((ZX[37]).rolling(window=wsS, min_periods=1).std())
                im80.set_ydata((ZX[38]).rolling(window=wsS, min_periods=1).std())
                im81.set_ydata((ZX[39]).rolling(window=stS, min_periods=1).std())
                # --------------------------------------[Void Count]
                im90.set_ydata((ZX[41]).sum())              # Sum up the values for Ring 1
                im91.set_ydata((ZX[42]).sum())              # Sum up the values for Ring 2
                im92.set_ydata((ZX[43]).sum())              # Sum up the values for Ring 3
                im93.set_ydata((ZX[44]).sum())              # Sum up the values for Ring 4
                # Compute entire Process Capability -----[Ramp Count]
                im94.set_ydata((ZX[41]).sum())              # Sum up the values for Ring 1
                im95.set_ydata((ZX[42]).sum())              # Sum up the values for Ring 2
                im96.set_ydata((ZX[43]).sum())
                im97.set_ydata((ZX[44]).sum())

            elif EoLRep == 'MGM':
                # X Plot Y-Axis data points for XBar ------------------------------[Laser Power]
                im10.set_ydata((ZX[0]).rolling(window=lpS, min_periods=1).mean())  # head 1
                im11.set_ydata((ZX[1]).rolling(window=lpS, min_periods=1).mean())  # head 2
                im12.set_ydata((ZX[2]).rolling(window=lpS, min_periods=1).mean())  # head 3
                im13.set_ydata((ZX[3]).rolling(window=lpS, min_periods=1).mean())  # head 4
                im14.set_ydata((ZX[4]).rolling(window=lpS, min_periods=1).mean())  # head 1
                im15.set_ydata((ZX[5]).rolling(window=lpS, min_periods=1).mean())  # head 2
                im16.set_ydata((ZX[6]).rolling(window=lpS, min_periods=1).mean())  # head 3
                im17.set_ydata((ZX[7]).rolling(window=lpS, min_periods=1).mean())  # head 4
                im18.set_ydata((ZX[8]).rolling(window=lpS, min_periods=1).mean())  # head 1
                im19.set_ydata((ZX[9]).rolling(window=lpS, min_periods=1).mean())  # head 2
                im20.set_ydata((ZX[10]).rolling(window=lpS, min_periods=1).mean())  # head 3
                im21.set_ydata((ZX[11]).rolling(window=lpS, min_periods=1).mean())  # head 4
                im22.set_ydata((ZX[12]).rolling(window=lpS, min_periods=1).mean())  # head 1
                im23.set_ydata((ZX[13]).rolling(window=lpS, min_periods=1).mean())  # head 2
                im24.set_ydata((ZX[14]).rolling(window=lpS, min_periods=1).mean())  # head 3
                im25.set_ydata((ZX[15]).rolling(window=lpS, min_periods=1).mean())  # head 4
                # ---------------------------------------[T1 std Dev]
                im26.set_ydata((ZX[0]).rolling(window=lpS, min_periods=1).std())
                im27.set_ydata((ZX[1]).rolling(window=lpS, min_periods=1).std())
                im28.set_ydata((ZX[2]).rolling(window=lpS, min_periods=1).std())
                im29.set_ydata((ZX[3]).rolling(window=lpS, min_periods=1).std())
                im30.set_ydata((ZX[4]).rolling(window=lpS, min_periods=1).std())
                im31.set_ydata((ZX[5]).rolling(window=lpS, min_periods=1).std())
                im32.set_ydata((ZX[6]).rolling(window=lpS, min_periods=1).std())
                im33.set_ydata((ZX[7]).rolling(window=lpS, min_periods=1).std())
                im34.set_ydata((ZX[8]).rolling(window=lpS, min_periods=1).std())
                im35.set_ydata((ZX[9]).rolling(window=lpS, min_periods=1).std())
                im36.set_ydata((ZX[10]).rolling(window=lpS, min_periods=1).std())
                im37.set_ydata((ZX[11]).rolling(window=lpS, min_periods=1).std())
                im38.set_ydata((ZX[12]).rolling(window=lpS, min_periods=1).std())
                im39.set_ydata((ZX[13]).rolling(window=lpS, min_periods=1).std())
                im40.set_ydata((ZX[14]).rolling(window=lpS, min_periods=1).std())
                im41.set_ydata((ZX[15]).rolling(window=lpS, min_periods=1).std())
                # ---------------------------------------------------------------[Laser Angle T2]
                im42.set_ydata((ZX[16]).rolling(window=laS, min_periods=1).mean())
                im43.set_ydata((ZX[17]).rolling(window=laS, min_periods=1).mean())
                im44.set_ydata((ZX[18]).rolling(window=laS, min_periods=1).mean())
                im45.set_ydata((ZX[19]).rolling(window=laS, min_periods=1).mean())
                im46.set_ydata((ZX[20]).rolling(window=laS, min_periods=1).mean())
                im47.set_ydata((ZX[21]).rolling(window=laS, min_periods=1).mean())
                im48.set_ydata((ZX[22]).rolling(window=laS, min_periods=1).mean())
                im49.set_ydata((ZX[23]).rolling(window=laS, min_periods=1).mean())
                im50.set_ydata((ZX[24]).rolling(window=laS, min_periods=1).mean())
                im51.set_ydata((ZX[25]).rolling(window=laS, min_periods=1).mean())
                im52.set_ydata((ZX[26]).rolling(window=laS, min_periods=1).mean())
                im53.set_ydata((ZX[27]).rolling(window=laS, min_periods=1).mean())
                im54.set_ydata((ZX[28]).rolling(window=laS, min_periods=1).mean())
                im55.set_ydata((ZX[29]).rolling(window=laS, min_periods=1).mean())
                im56.set_ydata((ZX[30]).rolling(window=laS, min_periods=1).mean())
                im57.set_ydata((ZX[31]).rolling(window=laS, min_periods=1).mean())
                # ---------------------------------------[T2 std Dev]
                im58.set_ydata((ZX[16]).rolling(window=laS, min_periods=1).std())
                im59.set_ydata((ZX[17]).rolling(window=laS, min_periods=1).std())
                im60.set_ydata((ZX[18]).rolling(window=laS, min_periods=1).std())
                im61.set_ydata((ZX[19]).rolling(window=laS, min_periods=1).std())
                im62.set_ydata((ZX[20]).rolling(window=laS, min_periods=1).std())
                im63.set_ydata((ZX[21]).rolling(window=laS, min_periods=1).std())
                im64.set_ydata((ZX[22]).rolling(window=laS, min_periods=1).std())
                im65.set_ydata((ZX[23]).rolling(window=laS, min_periods=1).std())
                im66.set_ydata((ZX[24]).rolling(window=laS, min_periods=1).std())
                im67.set_ydata((ZX[25]).rolling(window=laS, min_periods=1).std())
                im68.set_ydata((ZX[26]).rolling(window=laS, min_periods=1).std())
                im69.set_ydata((ZX[27]).rolling(window=laS, min_periods=1).std())
                im70.set_ydata((ZX[28]).rolling(window=laS, min_periods=1).std())
                im71.set_ydata((ZX[29]).rolling(window=laS, min_periods=1).std())
                im72.set_ydata((ZX[30]).rolling(window=laS, min_periods=1).std())
                im73.set_ydata((ZX[31]).rolling(window=laS, min_periods=1).std())
                # ----------------------------------------------------------------------[Tape Temp]
                im74.set_ydata((ZX[32]).rolling(window=ttS, min_periods=1).mean())
                im75.set_ydata((ZX[33]).rolling(window=ttS, min_periods=1).mean())
                im76.set_ydata((ZX[34]).rolling(window=ttS, min_periods=1).mean())
                im77.set_ydata((ZX[35]).rolling(window=ttS, min_periods=1).mean())
                im78.set_ydata((ZX[36]).rolling(window=ttS, min_periods=1).mean())
                im79.set_ydata((ZX[37]).rolling(window=ttS, min_periods=1).mean())
                im80.set_ydata((ZX[38]).rolling(window=ttS, min_periods=1).mean())
                im81.set_ydata((ZX[39]).rolling(window=ttS, min_periods=1).mean())
                im82.set_ydata((ZX[32]).rolling(window=ttS, min_periods=1).mean())
                im83.set_ydata((ZX[33]).rolling(window=ttS, min_periods=1).mean())
                im84.set_ydata((ZX[34]).rolling(window=ttS, min_periods=1).mean())
                im85.set_ydata((ZX[35]).rolling(window=ttS, min_periods=1).mean())
                im86.set_ydata((ZX[36]).rolling(window=ttS, min_periods=1).mean())
                im87.set_ydata((ZX[37]).rolling(window=ttS, min_periods=1).mean())
                im88.set_ydata((ZX[38]).rolling(window=ttS, min_periods=1).mean())
                im89.set_ydata((ZX[39]).rolling(window=ttS, min_periods=1).mean())
                # ---------
                im90.set_ydata((ZX[32]).rolling(window=ttS, min_periods=1).std())
                im91.set_ydata((ZX[33]).rolling(window=ttS, min_periods=1).std())
                im92.set_ydata((ZX[34]).rolling(window=ttS, min_periods=1).std())
                im93.set_ydata((ZX[35]).rolling(window=ttS, min_periods=1).std())
                im94.set_ydata((ZX[36]).rolling(window=ttS, min_periods=1).std())
                im95.set_ydata((ZX[37]).rolling(window=ttS, min_periods=1).std())
                im96.set_ydata((ZX[38]).rolling(window=ttS, min_periods=1).std())
                im97.set_ydata((ZX[39]).rolling(window=ttS, min_periods=1).std())
                im98.set_ydata((ZX[32]).rolling(window=ttS, min_periods=1).std())
                im99.set_ydata((ZX[33]).rolling(window=ttS, min_periods=1).std())
                im100.set_ydata((ZX[34]).rolling(window=ttS, min_periods=1).std())
                im101.set_ydata((ZX[35]).rolling(window=ttS, min_periods=1).std())
                im102.set_ydata((ZX[36]).rolling(window=ttS, min_periods=1).std())
                im103.set_ydata((ZX[37]).rolling(window=ttS, min_periods=1).std())
                im104.set_ydata((ZX[38]).rolling(window=ttS, min_periods=1).std())
                im105.set_ydata((ZX[39]).rolling(window=ttS, min_periods=1).std())
                # ----------------------------------------------------------------------- [Substrate Tape]
                im106.set_ydata((ZX[47]).rolling(window=stS, min_periods=1).mean())  # head 1
                im107.set_ydata((ZX[48]).rolling(window=stS, min_periods=1).mean())  # head 2
                im108.set_ydata((ZX[49]).rolling(window=stS, min_periods=1).mean())  # head 3
                im109.set_ydata((ZX[50]).rolling(window=stS, min_periods=1).mean())  # head 4
                im110.set_ydata((ZX[51]).rolling(window=stS, min_periods=1).mean())  # head 1
                im111.set_ydata((ZX[52]).rolling(window=stS, min_periods=1).mean())  # head 2
                im112.set_ydata((ZX[53]).rolling(window=stS, min_periods=1).mean())  # head 3
                im113.set_ydata((ZX[54]).rolling(window=stS, min_periods=1).mean())  # head 4
                im114.set_ydata((ZX[55]).rolling(window=stS, min_periods=1).mean())  # head 1
                im115.set_ydata((ZX[56]).rolling(window=stS, min_periods=1).mean())  # head 2
                im116.set_ydata((ZX[57]).rolling(window=stS, min_periods=1).mean())  # head 3
                im117.set_ydata((ZX[58]).rolling(window=stS, min_periods=1).mean())  # head 4
                im118.set_ydata((ZX[59]).rolling(window=stS, min_periods=1).mean())
                im119.set_ydata((ZX[60]).rolling(window=stS, min_periods=1).mean())
                im120.set_ydata((ZX[61]).rolling(window=stS, min_periods=1).mean())
                im121.set_ydata((ZX[62]).rolling(window=stS, min_periods=1).mean())
                # ---------------------------------------#[Stddev]
                im122.set_ydata((ZX[47]).rolling(window=stS, min_periods=1).std())
                im123.set_ydata((ZX[48]).rolling(window=stS, min_periods=1).std())
                im124.set_ydata((ZX[49]).rolling(window=stS, min_periods=1).std())
                im125.set_ydata((ZX[50]).rolling(window=stS, min_periods=1).std())
                im126.set_ydata((ZX[51]).rolling(window=stS, min_periods=1).std())
                im127.set_ydata((ZX[52]).rolling(window=stS, min_periods=1).std())
                im128.set_ydata((ZX[53]).rolling(window=stS, min_periods=1).std())
                im129.set_ydata((ZX[54]).rolling(window=stS, min_periods=1).std())
                im130.set_ydata((ZX[55]).rolling(window=stS, min_periods=1).std())
                im131.set_ydata((ZX[56]).rolling(window=stS, min_periods=1).std())
                im132.set_ydata((ZX[57]).rolling(window=stS, min_periods=1).std())
                im133.set_ydata((ZX[58]).rolling(window=stS, min_periods=1).std())
                im134.set_ydata((ZX[59]).rolling(window=stS, min_periods=1).std())
                im135.set_ydata((ZX[60]).rolling(window=stS, min_periods=1).std())
                im136.set_ydata((ZX[61]).rolling(window=stS, min_periods=1).std())
                im137.set_ydata((ZX[62]).rolling(window=stS, min_periods=1).std())
                # -----------------------------------------------------------------[Tape Gap T6]
                im138.set_ydata((ZX[63]).rolling(window=tgS, min_periods=1).mean())
                im139.set_ydata((ZX[64]).rolling(window=tgS, min_periods=1).mean())
                im140.set_ydata((ZX[65]).rolling(window=tgS, min_periods=1).mean())
                im141.set_ydata((ZX[66]).rolling(window=tgS, min_periods=1).mean())
                im142.set_ydata((ZX[67]).rolling(window=tgS, min_periods=1).mean())
                im143.set_ydata((ZX[68]).rolling(window=tgS, min_periods=1).mean())
                im144.set_ydata((ZX[69]).rolling(window=tgS, min_periods=1).mean())
                im145.set_ydata((ZX[70]).rolling(window=tgS, min_periods=1).mean())
                # ----------- Std
                im146.set_ydata((ZX[71]).rolling(window=tgS, min_periods=1).std())
                im147.set_ydata((ZX[72]).rolling(window=tgS, min_periods=1).std())
                im148.set_ydata((ZX[73]).rolling(window=tgS, min_periods=1).std())
                im149.set_ydata((ZX[74]).rolling(window=tgS, min_periods=1).std())
                im150.set_ydata((ZX[75]).rolling(window=tgS, min_periods=1).std())
                im151.set_ydata((ZX[76]).rolling(window=tgS, min_periods=1).std())
                im152.set_ydata((ZX[77]).rolling(window=tgS, min_periods=1).std())
                im153.set_ydata((ZX[78]).rolling(window=tgS, min_periods=1).std())
                # --------------------------------------------------------------[ Winding Angle]
                im154.set_ydata((ZX[63]).rolling(window=waS, min_periods=1).mean())
                im155.set_ydata((ZX[64]).rolling(window=waS, min_periods=1).mean())
                im156.set_ydata((ZX[65]).rolling(window=waS, min_periods=1).mean())
                im157.set_ydata((ZX[66]).rolling(window=waS, min_periods=1).mean())
                im158.set_ydata((ZX[67]).rolling(window=waS, min_periods=1).mean())
                im159.set_ydata((ZX[68]).rolling(window=waS, min_periods=1).mean())
                im160.set_ydata((ZX[69]).rolling(window=waS, min_periods=1).mean())
                im161.set_ydata((ZX[70]).rolling(window=waS, min_periods=1).mean())
                im162.set_ydata((ZX[71]).rolling(window=waS, min_periods=1).mean())
                im163.set_ydata((ZX[72]).rolling(window=waS, min_periods=1).mean())
                im164.set_ydata((ZX[73]).rolling(window=waS, min_periods=1).mean())
                im165.set_ydata((ZX[74]).rolling(window=waS, min_periods=1).mean())
                im166.set_ydata((ZX[75]).rolling(window=waS, min_periods=1).mean())
                im167.set_ydata((ZX[76]).rolling(window=waS, min_periods=1).mean())
                im168.set_ydata((ZX[77]).rolling(window=waS, min_periods=1).mean())
                im169.set_ydata((ZX[78]).rolling(window=waS, min_periods=1).mean())
                # -----------------------------------------------------------------[Tape Placement Mean T7]
                im170.set_ydata((ZX[79]).rolling(window=waS, min_periods=1).std())
                im171.set_ydata((ZX[80]).rolling(window=waS, min_periods=1).std())
                im172.set_ydata((ZX[81]).rolling(window=waS, min_periods=1).std())
                im173.set_ydata((ZX[82]).rolling(window=waS, min_periods=1).std())
                im174.set_ydata((ZX[83]).rolling(window=waS, min_periods=1).std())
                im175.set_ydata((ZX[84]).rolling(window=waS, min_periods=1).std())
                im176.set_ydata((ZX[85]).rolling(window=waS, min_periods=1).std())
                im177.set_ydata((ZX[86]).rolling(window=waS, min_periods=1).std())
                im178.set_ydata((ZX[79]).rolling(window=waS, min_periods=1).std())
                im179.set_ydata((ZX[80]).rolling(window=waS, min_periods=1).std())
                im180.set_ydata((ZX[81]).rolling(window=waS, min_periods=1).std())
                im181.set_ydata((ZX[82]).rolling(window=waS, min_periods=1).std())
                im182.set_ydata((ZX[83]).rolling(window=waS, min_periods=1).std())
                im183.set_ydata((ZX[84]).rolling(window=waS, min_periods=1).std())
                im184.set_ydata((ZX[85]).rolling(window=waS, min_periods=1).std())
                im185.set_ydata((ZX[86]).rolling(window=waS, min_periods=1).std())
                # ------------------------------------------------------ Std Dev
                # Compute entire Process Capability ------------------------------------------#

            # Setting up the parameters for non-moving windows Axes ------------------------[]
            a1.set_xlim(0, window_Xmax)
            a2.set_xlim(0, window_Xmax)

            # Set trip line for individual time-series plot -------------------------------[R1]

            # -------------------------------------------------------------------------------[]

            plt.tight_layout()
            plt.show()
        # --------------------------- QA REPORT ------------------------[]
        # ring1SP = avg(head1 + head2 + head3 + head4)
        # ring2SP = avg(head1 + head2 + head3 + head4)
        # ring3SP = avg(head1 + head2 + head3 + head4)
        # ring4SP = avg(head1 + head2 + head3 + head4)
        # tRingSP = ring1SP + ring2SP + ring3SP + ring4SP
        # # -------------------------------------------
        # ring1NV = ring1SP / tRingSP
        # ring2NV = ring2SP / tRingSP
        # ring3NV = ring3SP / tRingSP
        # ring4NV = ring4SP / tRingSP
        # ---------------- Call objective function -----
        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)


# ------- Defines the collective screen structure ------------------------[EOP Reports]
class collectiveEoP(ttk.Frame):                                # End of Layer Progressive Report Tabb
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        # self.grid(column=0, row=0, padx=10, pady=10)
        self.place(x=10, y=10)
        self.createWidgets()

    def createWidgets(self):
        label = ttk.Label(self, text="End of Pipe Report", font=LARGE_FONT)
        # label.pack(padx=10, pady=10, side=tk.RIGHT)
        # label.grid(column=0, row=0, padx=10, pady=10)
        label.place(x=400, y=10)

        # Define Axes ----------------------------------#
        fig = Figure(figsize=(pMtX - 9.5, 7.21), dpi=100)        # 12.5, 7.22, 18
        fig.subplots_adjust(left=0.04, bottom=0.033, right=0.983, top=0.957, hspace=0.14, wspace=0.033)
        # ---------------------------------[]
        a1 = fig.add_subplot(2, 3, (1, 3))              # X Bar Plot
        a2 = fig.add_subplot(2, 3, (4, 6))              # S Bar Plot

        # Declare Plots attributes ---------------------[]
        plt.rcParams.update({'font.size': 7})           # Reduce font size to 7pt for all legends

        # Calibrate limits for X-moving Axis -----------#
        YScale_minRF, YScale_maxRF = 10, 500
        sBar_minRF, sBar_maxRF = 10, 250                # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, 30                # windows view = visible data points

        # Common properties ------------------------#
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [" + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        a1.set_title('[XBar Plot]', fontsize=12, fontweight='bold')
        a2.set_title('[SDev Plot]', fontsize=12, fontweight='bold')

        # Apply grid lines ------------------------------
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a1.legend(loc='upper right', title='Mean curve')
        a2.legend(loc='upper right', title='Sigma curve')

        # ----------------------------------------------------------#
        a1.set_ylim([YScale_minRF, YScale_maxRF], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        a2.set_ylim([sBar_minRF, sBar_maxRF], auto=True)
        a2.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------[]
        # Define Plot area and axes -
        # ----------------------------------------------------------#
        im10, = a1.plot([], [], 'o-', label='Roller Force - (R1H1)')
        im11, = a1.plot([], [], 'o-', label='Roller Force - (R1H2)')
        im12, = a1.plot([], [], 'o-', label='Roller Force - (R1H3)')
        im13, = a1.plot([], [], 'o-', label='Roller Force - (R1H4)')
        im14, = a2.plot([], [], 'o-', label='Roller Force')
        im15, = a2.plot([], [], 'o-', label='Roller Force')
        im16, = a2.plot([], [], 'o-', label='Roller Force')
        im17, = a2.plot([], [], 'o-', label='Roller Force')

        # Define dropdown List ---------------------#
        combo = ttk.Combobox(self, values=["= Select Process Parameter =", "Roller Force",
                                           "Tape Temperature", "Subs Temperature", "Laser Power",
                                           "Laser Angle", "Tape Placement Error",
                                           "Tape Gap Polarisation"], width=25)
        combo.place(x=385, y=30)
        combo.current(0)

        # Create empty Text Space -----------------------------------
        text_widget = tk.Text(self, wrap='word', width=110, height=47)  # 110 | 70
        text_widget.pack(padx=10, pady=50, side=tk.LEFT)
        # text_widget.place(x=10, y=10)

        # ---------------------------------------------------------[]
        def option_selected(event):
            selected_option = combo.get()
            if selected_option == "Roller Force":
                label = ttk.Label(self, text='Roller Force', width=16, font=14, background='#fff') #, justify='center')
                label.place(x=1540, y=54)

                rpt = "RPT_RF_" + str(processWON[0])
                readEoP(text_widget, rpt)                              # Open txt file from FMEA folder

            elif selected_option == "Tape Temperature":
                label = ttk.Label(self, text='Tape Temperature', width=16, background='#fff', font=14)
                label.place(x=1540, y=54)

                rpt = "RPT_TT_" + str(processWON[0])
                readEoP(text_widget, rpt)                              # Open txt file from FMEA folder

            elif selected_option == "Subs Temperature":
                label = ttk.Label(self, text='Subs Temperature', width=16, background='#fff', font=14)
                label.place(x=1540, y=54)

                rpt = "RPT_ST_" + str(processWON[0])
                readEoP(text_widget, rpt)                               # Open txt file from FMEA folder

            elif selected_option == "Laser Power":
                label = ttk.Label(self, text='Laser Power', width=16, background='#fff', font=14)
                label.place(x=1540, y=54)

                rpt = "RPT_LP_" + str(processWON[0])
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder

            elif selected_option == "Laser Angle":
                label = ttk.Label(self, text='Laser Angle', width=16, background='#fff', font=14)
                label.place(x=1540, y=54)

                rpt = "RPT_LA_" + str(processWON[0])
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder

            elif selected_option == "Tape Placement Error":
                label = ttk.Label(self, text='Tape Placement', width=16, background='#fff', font=14)
                label.place(x=1540, y=54)

                rpt = "RPT_TP_" + str(processWON[0])
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder

            elif selected_option == "Tape Gap Polarisation":
                label = ttk.Label(self, text='Gap Measurement', width=16, background='#fff', font=14)
                label.place(x=1540, y=54)

                rpt = "RPT_TG_" + str(processWON[0])
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder

            else:
                label = ttk.Label(self, text=' ')
                label.place(x=1540, y=54)

                rpt = "VOID_REPORT"
                readEoP(text_widget, rpt)

            print("You selected:", selected_option)
        combo.bind("<<ComboboxSelected>>", option_selected)

        # Update Canvas -----------------------------------------------------[NO FIGURE YET]
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().pack(expand=False)

        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

# ---------------------------- End of Collective Reporting Functions ----------------------------[]

#     ********   These set of functions defines the common canvas Area  *******************
# ---------------------------------- COMMON VIEW CLASS OBJECTS ---------[Ramp Count Plot]
class common_rampCount(ttk.Frame):
    # compute ram Count against cumulative layers ramp count --------[A]
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=20)
        self.createWidgets()

    def createWidgets(self):
        mtS, mtTy = cSS, cGS                    # Copy variable and use
        # ---------------------------------------------------------[]

        f = Figure(figsize=(scrX, 4), dpi=100)
        f.subplots_adjust(left=0.083, bottom=0.11, right=0.976, top=0.99, wspace=0.202)
        a1 = f.add_subplot(1, 1, 1)

        # Model data -----------------------------------------------[]
        # a3.cla()
        a1.get_yaxis().set_visible(True)
        a1.get_xaxis().set_visible(True)

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends

        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minRP, YScale_maxRP = 0, vCount                      # Ramp Count Profile (Per segment)
        window_Xmin, window_Xmax = 0, pExLayer                      # windows view = visible data points

        # Load SQL Query Table -------------------------------------#
        if rType == 1:
            rcDT = SPC_RC
        else:
            rcDT = 'RC_'+ pWON                                        # Ramp Count
        # ----------------------------------------------------------#

        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a1.legend(loc='upper right', title='Cumulative Ramp Count')
        a1.set_ylabel("Cumulative Ramp Count / Segment")
        a1.set_xlabel("Pipe Nominal Layer")
        # ----------------------------------------------------------#

        a1.set_ylim([YScale_minRP, YScale_maxRP], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])

        # ------- plot ramp count ------------[]
        im10, = a1.plot([], [], 'o-', label='Ramp Count - Ring 1')                  # ramp count all layers
        im11, = a1.plot([], [], 'o-', label='Ramp Count - Ring 2')                  # ramp count all layers
        im12, = a1.plot([], [], 'o-', label='Ramp Count - Ring 3')                  # ramp count all layers
        im13, = a1.plot([], [], 'o-', label='Ramp Count - Ring 4')                  # ramp count all layers
        im14, = a1.plot([], [], 'o-', label='Cumulative Ramp Count - All Rings')    # ramp count all layers

        # ---------------- EXECUTE SYNCHRONOUS METHOD --------------#

        def synchronousRampC(fetchT):
            fetch_no = str(fetchT)              # entry value in string sql syntax
            smp_Sz, stp_Sz = 30, 1              # Static Plot

            # Obtain Volatile Data from sql Host Server ---------------------------[]
            if not inUseAlready:  # Load CommsPlc class once
                import CommsSql as q
                q.DAQ_connect(1, 0)
            else:
                con_ramp = conn.cursor()

            # Evaluate conditions for SQL Data Fetch ------------------------------[A]
            """
            Load watchdog function with synchronous function every seconds
            """
            # Initialise RT variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard                     # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                # Latch on SQL Query only a
                if UsePLC_DBS:                                      # Not Using PLC Data
                    import plcArrayRLmethodRC as rC                 # DrLabs optimization method

                    inProgress = False  # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()     # Retrieve MSC from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    # Get list of relevant SQL Tables using conn() --------------------[]
                    if keyboard.is_pressed(
                            "Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:    # Terminate file-fetch
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            print("\nVisualization in Paused Mode...")

                        else:
                            autoSpcPause = False
                        print("Visualization in Play Mode...")

                    else:
                        dLRC = rC.plcExec(rcDT, mtS, mtTy, fetchT)        # perform DB connections

                else:
                    import sqlArrayRLmethodRC as rC

                    inProgress = True  # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve M.State from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    if keyboard.is_pressed("Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            print("\nVisualization in Paused Mode...")
                        else:
                            autoSpcPause = False
                            print("Visualization in Real-time Mode...")
                    else:
                        # Get list of relevant SQL Tables using conn() --------------------[]
                        gcDta = rC.sqlExec(mtS, mtTy, con_ramp, rcDT, fetchT)
                    # ------ Inhibit iteration ----------------------------------------------------------[]
                    """
                    # Set condition for halting real-time plots in watchdog class ---------------------
                    """
                    # TODO --- values for inhibiting the SQL processing
                    if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                        con_ramp.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

            return dLRC

        # ================== End of synchronous Method ==========================obal

        def asynchronous_rc(db_freq):

            timei = time.time()                                 # start timing the entire loop

            # Call data loader Method---------------------------#
            dXrc = synchronousRampC(db_freq)                    # data loading functions
            if UsePLC_DBS == 1:
                import VarPLC_RC as rc
            else:
                # ----------------------------------------------#
                import VarSQL_RC as rc                          # load SQL variables column names | rfVarSQL

            viz_cycle = 150
            g1 = qrc.validCols(rcDT)                            # Construct Data Column selSqlColumnsTFM.py
            df1 = pd.DataFrame(dXrc, columns=g1)                # Import into python Dataframe
            RC = rc.loadProcesValues(df1)                       # Join data values under dataframe
            print('\nSQL Content', df1.head(10))
            print("Memory Usage:", df1.info(verbose=False))     # Check memory utilization
            total_cum = RC[2] + RC[3] + RC[4] + RC[5]           # sCentre[0] | RMCount[1] | PipeDir[6] | cLayer[7]

            # ----------------------------------------------------------------------------------[]
            # Plot X-Axis data points -------- X Plot
            im10.set_xdata(np.arange(db_freq))
            im11.set_xdata(np.arange(db_freq))
            im12.set_xdata(np.arange(db_freq))
            im13.set_xdata(np.arange(db_freq))
            im14.set_xdata(np.arange(db_freq))

            # X Plot Y-Axis data points for XBar --------------------------------------------[Ring 1]
            im10.set_ydata((RC[2]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # head 1
            im11.set_ydata((RC[3]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # head 1
            im12.set_ydata((RC[4]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # head 1
            im13.set_ydata((RC[5]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # head 1
            im14.set_ydata((total_cum).rolling(window=mtS, min_periods=1)[0:db_freq])     # Cumulative count

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
                # a2.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a1.set_xlim(0, window_Xmax)
                # a2.set_xlim(0, window_Xmax)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronous_rc, frames=None, save_count=100, repeat_delay=None,
                                interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)

        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

# ---------------------------------- COMMON VIEW CLASS OBJECTS ------[Climatic Variables]
class common_climateProfile(ttk.Frame):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=pEvX, y=20)     # 915
        self.createWidgets()

    def createWidgets(self):
        mtS, mtTy = cSS, cGS                    # Copy variable and use

        # -----------------------------------
        f = Figure(figsize=(scrX, 4), dpi=100)
        f.subplots_adjust(left=0.076, bottom=0.098, right=0.91, top=0.99, wspace=0.202)
        a2 = f.add_subplot(1, 1, 1)
        a3 = a2.twinx()

        # --------------------------------------- Dump Data ----------[]
        # x = np.arange(0, 100, 0.1)
        # y1 = - 0.01 * x ** 2
        # y2 = -1 * y1
        #
        # # configure plot curves -----
        # a2.plot(x, y1, 'r-')
        # a3.plot(x, y2, 'b-')

        # Model data --------------------------------------------------[]
        a2.get_yaxis().set_visible(True)
        a2.get_xaxis().set_visible(True)

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 9})                       # Reduce font size to 7pt for all legends

        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minCP, YScale_maxCP = -10, 80                        # Climate Data
        window_Xmin, window_Xmax = 0, 30                            # windows view = visible data points

        # Load SQL Query Table -------------------------------------#
        if rType == 1:
            evDT = SPC_EV
        else:
            evDT = 'EV_' + pWON                                       # Environmental Values Reprocessed from SQL
        # ----------------------------------------------------------#

        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.legend(loc='upper left', title='PO64PX Climate Profile')
        a3.legend(loc='upper right', title="UV-Index:" + str(3.2))
        a2.set_ylabel("Temperature [°C]", color='r')
        a3.set_ylabel("Relative Humidity", color='b')
        a2.set_xlabel("Time Series")

        # ----------------------------------------------------------#
        a2.set_ylim([YScale_minCP, YScale_maxCP], auto=True)
        a2.set_xlim([window_Xmin, window_Xmax])

        # ------- plot ramp count ----------------------------------#
        im10, = a2.plot([], [], 'o-', label='TCP-Cell Temperature')
        im11, = a2.plot([], [], 'o-', label='Factory Temperature')
        im12, = a2.plot([], [], 'o-', label='Cell DP Temperature')
        im13, = a3.plot([], [], 'o-', label='TCP-Cell Humidity')
        im14, = a3.plot([], [], 'o-', label='Factory Humidity')
        im15, = a3.plot([], [], 'o-', label='Cell DP Humidity')
        # ---------------- EXECUTE SYNCHRONOUS METHOD --------------#

        def synchronousClimate(fetchT):
            fetch_no = str(fetchT)  # entry value in string sql syntax

            # Obtain SQL Data Host Server ---------------------------[]
            if not inUseAlready:  # Load CommsPlc class once
                import CommsSql as q
                q.DAQ_connect(1, 0)
            else:
                # pass
                con_ev = conn.cursor()

            # Evaluate conditions for SQL Data Fetch ---------------[A]
            """
            Load watchdog function with synchronous function every seconds
            """
            # Initialise RT variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard  # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                if UsePLC_DBS:  # Not Using PLC Data
                    import plcArrayRLmethodEV as sev                            # DrLabs optimization method

                    inProgress = True                                           # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve MSC from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    # Get list of relevant SQL Tables using conn() --------------------[]
                    if keyboard.is_pressed(
                            "Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:  # Terminate file-fetch
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            print("\nVisualization in Paused Mode...")

                        else:
                            autoSpcPause = False
                            print("Visualization in Play Mode...")

                    else:
                        evDta = sev.plcExec(evDT, mtS, mtTy, fetchT)                  # perform DB connections

                else:
                    import sqlArrayRLmethodEV as sev

                    inProgress = True  # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve M.State from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    if keyboard.is_pressed("Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            print("\nVisualization in Paused Mode...")
                        else:
                            autoSpcPause = False
                            print("Visualization in Real-time Mode...")
                    else:
                        # Get list of relevant SQL Tables using conn() --------------------[]
                        evDta = sev.sqlExec(mtS, mtTy, con_ev, evDT, fetchT)
                        # ------ Inhibit iteration ----------------------------------------------------------[]
                    """
                    # Set condition for halting real-time plots in watchdog class ---------------------
                    """
                    # TODO --- values for inhibiting the SQL processing
                    if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                        con_ev.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

                return evDta

        # ================== End of synchronous Method ===========================================================[]
        def asynchronousClimate(db_freq):
            timei = time.time()                                 # start timing the entire loop

            # Call data loader Method---------------------------#
            evDta = synchronousClimate(db_freq)                 # data loading functions
            if UsePLC_DBS == 1:
                import VarPLC_EV as ev
            else:
                import VarSQL_EV as ev                           # load SQL variables column names | rfVarSQL

            viz_cycle = 150
            g1 = qev.validCols(evDT)                            # Construct Data Column selSqlColumnsTFM.py
            df1 = pd.DataFrame(evDta, columns=g1)               # Import into python Dataframe
            EV = ev.loadProcesValues(df1)                       # Join data values under dataframe
            print('\nDataFrame Content', df1.head(10))          # Preview Data frame head
            print("Memory Usage:", df1.info(verbose=False))     # Check memory utilization

            # a2.text(2.25, 43.9, 'UV-Index: ' + str(uvIndex), fontsize=12, fontweight='normal')
            # a2.text(4.25, 43.9, 'UV-Index:', transform=plt.gca().transAxes)
            # a2.annotate('UV-Index:', xy=(4.25, 43.9), xytext=(5, 70))
            # a2.annotate("UV-Index:", xy=(10, 50), xycoords="axes fraction")
            # a2.annotate("Test 2", xy=(2, 6), xycoords=a2.get_window_extent)
            t_freq = EV[0]
            uvIndex = 3.0
            a3.legend(loc='upper right', title="UV-Index:" + str(uvIndex))

            # --------------------------------
            # Plot X-Axis data points -------- X Plot
            im10.set_xdata(np.arange(t_freq))
            im11.set_xdata(np.arange(t_freq))
            im12.set_xdata(np.arange(t_freq))
            im13.set_xdata(np.arange(t_freq))
            im14.set_xdata(np.arange(t_freq))
            im15.set_xdata(np.arange(t_freq))

            # X Plot Y-Axis data points for XBar --------------------------------------------[Ring 1]
            # im10.set_ydata((EV[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])   # time stamp
            im10.set_ydata((EV[2])[0:t_freq])           # oven tempA
            im11.set_ydata((EV[3])[0:t_freq])           # oven temp B
            im12.set_ydata((EV[4])[0:t_freq])           # Cell Rel Temperature
            im13.set_ydata((EV[5])[0:t_freq])           # Cell Rel Humidity
            im14.set_ydata((EV[6])[0:t_freq])           # Factory Dew Point Temp
            im15.set_ydata((EV[7])[0:t_freq])           # Factory Humidity
            # im11.set_ydata((CT[12]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # UVIndex

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if t_freq > window_Xmax:
                a2.set_xlim(t_freq - window_Xmax, t_freq)
                a3.set_xlim(t_freq - window_Xmax, t_freq)
            else:
                a2.set_xlim(0, window_Xmax)
                a3.set_xlim(0, window_Xmax)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousClimate, frames=None, save_count=100, repeat_delay=None,
                                interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -------------------------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)

        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

# ---------------------------------- COMMON VIEW CLASS OBJECTS -----------[Gap Count Plot]
class common_gapCount(ttk.Frame):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=pTgX, y=20)    #[1600, 1820]
        self.createWidgets()

    def createWidgets(self):
        mtS, mtTy = cSS, cGS  # Copy variable and use
        # -----------------------------------
        f = Figure(figsize=(scrX, 4), dpi=100)   #w.h
        f.subplots_adjust(left=0.076, bottom=0.1, right=0.971, top=0.99, wspace=0.202)
        a3 = f.add_subplot(1, 1, 1)

        # Model data --------------------------------------------------[]
        a3.get_yaxis().set_visible(True)
        a3.get_xaxis().set_visible(True)

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 9})  # Reduce font size to 7pt for all legends

        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minGP, YScale_maxGP = 0, vCount
        window_Xmin, window_Xmax = 0, pExLayer                      # windows view = visible data points

        # Load SQL Query Table -------------------------------------#
        if rType == 1:
            vDT = SPC_VC
        else:
            vDT = 'VC_' + pWON                                       # Void Count
        # ----------------------------------------------------------#

        a3.grid(color="0.5", linestyle='-', linewidth=0.5)
        a3.legend(loc='upper right', title='Cumulative Gap Count')
        a3.set_ylabel("Cumulative Tape Gap Count / Segment")
        a3.set_xlabel("Pipe Nominal Layer")

        # ----------------------------------------------------------#
        a3.set_ylim([YScale_minGP, YScale_maxGP], auto=True)
        a3.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        im10, = a3.plot([], [], 'o-', label='Void Count Segment A')
        im11, = a3.plot([], [], 'o-', label='Void Count Segment B')
        im12, = a3.plot([], [], 'o-', label='Void Count Segment C')
        im13, = a3.plot([], [], 'o-', label='Void Count Segment D')
        im14, = a3.plot([], [], 'o-', label='Cumulative Gap Count')

        # ---------------- EXECUTE SYNCHRONOUS METHOD ---------------#
        def synchronousGapC(fetchT):
            fetch_no = str(fetchT)  # entry value in string sql syntax

            # Obtain SQL Data Host Server ---------------------------[]
            if not inUseAlready:  # Load CommsPlc class once
                import CommsSql as q
                q.DAQ_connect(1, 0)
            else:
                con_vc = conn.cursor()

            # Evaluate conditions for SQL Data Fetch ---------------[A]
            """
            Load watchdog function with synchronous function every seconds
            """
            # Initialise RT variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard  # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                # print('Indefinite looping...')
                if UsePLC_DBS:  # Not Using PLC Data
                    import plcArrayRLmethodVC as svc                            # DrLabs optimized Loader

                    inProgress = True                                           # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()             # Retrieve MSC from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    # Get list of relevant SQL Tables using conn() ------------[]
                    if keyboard.is_pressed(
                            "Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:  # Terminate file-fetch
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            print("\nVisualization in Paused Mode...")

                        else:
                            autoSpcPause = False
                            print("Visualization in Play Mode...")
                    else:
                        gcDta = svc.plcExec(vDT, mtS, mtTy, fetchT)           # perform DB connections

                else:
                    import sqlArrayRLmethodVC as svc                              # DrLabs optimization method

                    inProgress = True  # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve M.State from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    if keyboard.is_pressed("Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            print("\nVisualization in Paused Mode...")
                        else:
                            autoSpcPause = False
                            print("Visualization in Real-time Mode...")
                    else:
                        # Get list of relevant SQL Tables using conn() --------------------[]
                        gcDta = svc.sqlExec(mtS, mtTy, con_vc, vDT, fetchT)
                    # ------ Inhibit iteration ----------------------------------------------------------[]
                    """
                    # Set condition for halting real-time plots in watchdog class ---------------------
                    """
                    # TODO --- values for inhibiting the SQL processing
                    if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                        con_vc.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

            return gcDta

        # ================== End of synchronous Method ==========================
        def asynchronousGapC(db_freq):

            timei = time.time()                                # start timing the entire loop

            # Call data loader Method--------------------------#
            gcData = synchronousGapC(db_freq)                   # data loading functions
            if UsePLC_DBS == 1:
                import VarPLC_VC as vc
            else:
                import VarSQL_VC as vc                          # load SQL variables column names | rfVarSQL

            viz_cycle = 150
            g1 = qvc.validCols(vDT)
            df1 = pd.DataFrame(gcData, columns=g1)             # Import into python Dataframe vData
            VC = vc.loadProcesValues(df1)                      # Join data values under dataframe
            print('\nDataFrame Content', df1.head(10))         # Preview Data frame head
            print("Memory Usage:", df1.info(verbose=False))    # Check memory utilization

            # Plot X-Axis data points -------- X Plot
            im10.set_xdata(np.arange(db_freq))
            im11.set_xdata(np.arange(db_freq))
            im12.set_xdata(np.arange(db_freq))
            im13.set_xdata(np.arange(db_freq))
            im14.set_xdata(np.arange(db_freq))

            # X Plot Y-Axis data points for XBar --------------------------------------------[Ring 1]
            im10.set_ydata(VC[2].rolling(window=mtS, min_periods=1).mean()[0:db_freq])   # Count under Ring 1
            im11.set_ydata(VC[3].rolling(window=mtS, min_periods=1).mean()[0:db_freq])   # Count under Ring 2
            im12.set_ydata(VC[4].rolling(window=mtS, min_periods=1).mean()[0:db_freq])   # Count under Ring 3
            im13.set_ydata(VC[5].rolling(window=mtS, min_periods=1).mean()[0:db_freq])   # Count under Ring 4
            im14.set_ydata(VC[1].rolling(window=mtS, min_periods=1)[0:db_freq])          # Cumulative

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if db_freq > window_Xmax:
                a3.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a3.set_xlim(0, window_Xmax)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousGapC, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -------------------------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)

        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

# ***************************************** END  OF COMMON CANVAS ************************************

# ------------------------- Additional Tabb for Monitoring Parameters -------------[Monitoring Tabs]
class MonitorTabb(ttk.Frame):

    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=20)
        self.createWidgets()

    def createWidgets(self):
        # Load metrics from config -----------------------------------[TG, TT, ST]
        mtS, mtTy = cSS, cGS        # Copy variable and use

        # Load Quality Historical Values -----------[]
        label = ttk.Label(self, text='[' + rType + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)
        f = Figure(figsize=(pMtX, 8), dpi=100)    # 27

        if pRecipe == 'DNV':
            print('\n 4 params condition met....')
            f.subplots_adjust(left=0.029, bottom=0.057, right=0.983, top=0.979, wspace=0.167, hspace=0.164)
            a1 = f.add_subplot(2, 4, (1, 2))        # Roller Pressure
            a2 = f.add_subplot(2, 4, (3, 4))        # Winding Speed
            a3 = f.add_subplot(2, 4, (5, 6))        # Cell Tension
            a4 = f.add_subplot(2, 4, (7, 8))        # Oven Temperature

            # Load Query Tables --------------------#
            # if runType == 2:
            T1 = 'GEN_' + pWON                      # Tape Winding Speed, Cell Tension & Oven Temp
            T2 = 'RP1_' + pWON                      # Roller Pressure
            T3 = 'RP2_' + pWON                      # Table 2 to be concatenated
            T4 = 'WS_' + pWON                       # Winding Speed Table
            # --------------------------------------#

        elif pRecipe == 'MGM':
            print('\n6 Param condition met....')
            f.subplots_adjust(left=0.029, bottom=0.057, right=0.99, top=0.979, wspace=0.245, hspace=0.164)
            a1 = f.add_subplot(2, 6, (1, 2))        # Laser power
            a2 = f.add_subplot(2, 6, (3, 4))        # Cell Tension
            a3 = f.add_subplot(2, 6, (5, 6))        # Roller Pressure
            a4 = f.add_subplot(2, 6, (7, 8))        # Laser Angle
            a5 = f.add_subplot(2, 6, (9, 10))       # Oven Temperature
            a6 = f.add_subplot(2, 6, (11, 12))      # Winding Speed

            # Load SQL Query Tables ----------------#
            # if runType == 2:
            T1 = 'GEN_' + pWON                      # Tape Winding Speed, Cell Tension & Oven Temp
            T2 = 'RP1_' + pWON                      # Roller Pressure Table 1
            T3 = 'RP2_' + pWON                      # Roller Pressure T2
            # --------------------------------------#
            T4 = 'LP1_' + pWON                      # Laser Power Table 1
            T5 = 'LP2_' + pWON                      # Laser Power Table 2
            T6 = 'LA1_' + pWON                      # Laser Angle Table 1
            T7 = 'LA2_' + pWON                      # Laser Angle Table 2

            # --------------------------------------#
        else:
            print('\n Users params condition met....')
            f.subplots_adjust(left=0.029, bottom=0.057, right=0.99, top=0.979, wspace=0.245, hspace=0.164)
            print('Bespoke Selection Not allowed in this Version...')
            # ----------------------------------#

        # Declare Plots attributes -----------------[]
        plt.rcParams.update({'font.size': 7})        # Reduce font size to 7pt for all legends

        # Calibrate limits for X-moving Axis --------#
        YScale_minMT, YScale_maxMT = 20, 400
        window_Xmin, window_Xmax = 0, 35             # windows view = visible data points
        # -------------------------------------------#

        # Monitoring Parameters --------------------------------------------#
        if pRecipe == 'DNV': # int(mCT) and int(mOT) and int(mRP) and int(mWS):
            a1.grid(color="0.5", linestyle='-', linewidth=0.5)
            a2.grid(color="0.5", linestyle='-', linewidth=0.5)
            a3.grid(color="0.5", linestyle='-', linewidth=0.5)
            a4.grid(color="0.5", linestyle='-', linewidth=0.5)

            # --------- Monitoring Legend Label -------------#
            a1.legend(loc='upper right', title='Roller Pressure - MPa')
            a2.legend(loc='upper right', title='Winding Speed - m/s')
            a3.legend(loc='upper right', title='Cell Tension - N.m')
            a4.legend(loc='upper right', title='Oven Temperature - °C')

            # Initialise runtime limits --------------------#
            a1.set_ylabel("Roller Pressure - MPa")          # Pressure measured in Pascal
            a2.set_ylabel("Tape Winding Speed - m/s")       # Angle measured in Degrees
            a3.set_ylabel("Cell Tension Force - N.m")       # Tension measured in Newton
            a4.set_ylabel("Oven Temperature - °C")          # Oven Temperature in Degrees Celsius

        elif pRecipe == 'MGM': # int(mLP) and int(mLA) and int(mCT) and int(mOT) and int(mRP):
            # monitorP = 'MGM'
            a1.grid(color="0.5", linestyle='-', linewidth=0.5)
            a2.grid(color="0.5", linestyle='-', linewidth=0.5)
            a3.grid(color="0.5", linestyle='-', linewidth=0.5)
            a4.grid(color="0.5", linestyle='-', linewidth=0.5)
            a5.grid(color="0.5", linestyle='-', linewidth=0.5)
            a6.grid(color="0.5", linestyle='-', linewidth=0.5)
            # ---------------- Legend Label -----------------#
            a1.legend(loc='upper right', title='Laser Power - Watt')
            a2.legend(loc='upper right', title='Cell Tension - N.m')
            a3.legend(loc='upper right', title='Roller Pressure - MPa')
            a4.legend(loc='upper right', title='Laser Angle - Deg')
            a5.legend(loc='upper right', title='Oven Temperature - °C')
            a6.legend(loc='upper right', title='Winding Speed - m/s')
            # Initialise runtime limits --------------------#
            a1.set_ylabel("Laser Power")            # Force measured in Newton
            a2.set_ylabel("Cell Tension")           # Angle measured in Degrees
            a3.set_ylabel("Roller Pressure")        # Oven Temperature in Degree Celsius
            a4.set_ylabel("Laser Angle")            # Oven Temperature in Degrees Celsius
            a5.set_ylabel("Oven Temperature")       # Oven Temperature in Degrees Celsius
            a6.set_ylabel("Winding Speed")          # Oven Temperature in Degrees Celsius
        else:
            monitorP = 'USR'
            print('\n Bespoke Selection NOT allowed....')

        # Initialise runtime limits --------------------------------#
        a1.set_ylim([YScale_minMT, YScale_maxMT], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])

        # Model data -----------------------------------------------[]
        a1.plot([172, 48, 64, 59, 50, 136, 112, 223, 91, 320])
        # ----------------------------------------------------------[]

        # Define Plot area and axes -
        if pRecipe == 'DNV':
            # -----------------------------------------------------[Roller Force]
            im10, = a1.plot([], [], 'o-', label='Roller Pressure - (R1H1)')
            im11, = a1.plot([], [], 'o-', label='Roller Pressure - (R1H2)')
            im12, = a1.plot([], [], 'o-', label='Roller Pressure - (R1H3)')
            im13, = a1.plot([], [], 'o-', label='Roller Pressure - (R1H4)')
            im14, = a1.plot([], [], 'o-', label='Roller Pressure - (R2H1)')
            im15, = a1.plot([], [], 'o-', label='Roller Pressure - (R2H2)')
            im16, = a1.plot([], [], 'o-', label='Roller Pressure - (R2H3)')
            im17, = a1.plot([], [], 'o-', label='Roller Pressure - (R2H4)')
            im18, = a1.plot([], [], 'o-', label='Roller Pressure - (R3H1)')
            im19, = a1.plot([], [], 'o-', label='Roller Pressure - (R3H2)')
            im20, = a1.plot([], [], 'o-', label='Roller Pressure - (R3H3)')
            im21, = a1.plot([], [], 'o-', label='Roller Pressure - (R3H4)')
            im22, = a1.plot([], [], 'o-', label='Roller Pressure - (R4H1)')
            im23, = a1.plot([], [], 'o-', label='Roller Pressure - (R4H2)')
            im24, = a1.plot([], [], 'o-', label='Roller Pressure - (R4H3)')
            im25, = a1.plot([], [], 'o-', label='Roller Pressure - (R4H4)')
            # ------------------------------------------------------[Winding Speed]
            im26, = a2.plot([], [], 'o-', label='Winding Speed - (Ring 1)')
            im27, = a2.plot([], [], 'o-', label='Winding Speed - (Ring 2)')
            im28, = a2.plot([], [], 'o-', label='Winding Speed - (Ring 3)')
            im29, = a2.plot([], [], 'o-', label='Winding Speed - (Ring 4)')
            # ------------------------------------------------------[Cell Tension]
            im30, = a3.plot([], [], 'o-', label='Active Cell Tension')
            # -------------------------------------------------[Oven Temperature]
            im31, = a4.plot([], [], 'o-', label='RTD Oven Temperature (Lower Segment)')
            im32, = a4.plot([], [], 'o-', label='RTD Oven Temperature (Upper Segment)')
            im33, = a4.plot([], [], 'o-', label='IR Oven Temperature (Lower Segment)')
            im34, = a4.plot([], [], 'o-', label='IR Oven Temperature (Upper Segment)')

        elif pRecipe == 'MGM':
            # --------------------------------------------------[Laser Power]
            im10, = a1.plot([], [], 'o-', label='Laser Power - (R1H1)')
            im11, = a1.plot([], [], 'o-', label='Laser Power - (R1H2)')
            im12, = a1.plot([], [], 'o-', label='Laser Power - (R1H3)')
            im13, = a1.plot([], [], 'o-', label='Laser Power - (R1H4)')
            im14, = a1.plot([], [], 'o-', label='Laser Power - (R2H1)')
            im15, = a1.plot([], [], 'o-', label='Laser Power - (R2H2)')
            im16, = a1.plot([], [], 'o-', label='Laser Power - (R2H3)')
            im17, = a1.plot([], [], 'o-', label='Laser Power - (R2H4)')
            im18, = a1.plot([], [], 'o-', label='Laser Power - (R3H1)')
            im19, = a1.plot([], [], 'o-', label='Laser Power - (R3H2)')
            im20, = a1.plot([], [], 'o-', label='Laser Power - (R3H3)')
            im21, = a1.plot([], [], 'o-', label='Laser Power - (R3H4)')
            im22, = a1.plot([], [], 'o-', label='Laser Power - (R4H1)')
            im23, = a1.plot([], [], 'o-', label='Laser Power - (R4H2)')
            im24, = a1.plot([], [], 'o-', label='Laser Power - (R4H3)')
            im25, = a1.plot([], [], 'o-', label='Laser Power - (R4H4)')
            # ---------------------------------------- [Cell Tension  & Oven Temp]
            im26, = a2.plot([], [], 'o-', label='Active Cell Tension')
            # --------------------------------------------------[Roller Pressure]
            im27, = a3.plot([], [], 'o-', label='Roller Pressure - (R1H1)')
            im28, = a3.plot([], [], 'o-', label='Roller Pressure - (R1H2)')
            im29, = a3.plot([], [], 'o-', label='Roller Pressure - (R1H3)')
            im30, = a3.plot([], [], 'o-', label='Roller Pressure - (R1H4)')
            im31, = a3.plot([], [], 'o-', label='Roller Pressure - (R2H1)')
            im32, = a3.plot([], [], 'o-', label='Roller Pressure - (R2H2)')
            im33, = a3.plot([], [], 'o-', label='Roller Pressure - (R2H3)')
            im34, = a3.plot([], [], 'o-', label='Roller Pressure - (R2H4)')
            im35, = a3.plot([], [], 'o-', label='Roller Pressure - (R3H1)')
            im36, = a3.plot([], [], 'o-', label='Roller Pressure - (R3H2)')
            im37, = a3.plot([], [], 'o-', label='Roller Pressure - (R3H3)')
            im38, = a3.plot([], [], 'o-', label='Roller Pressure - (R3H4)')
            im39, = a3.plot([], [], 'o-', label='Roller Pressure - (R4H1)')
            im40, = a3.plot([], [], 'o-', label='Roller Pressure - (R4H2)')
            im41, = a3.plot([], [], 'o-', label='Roller Pressure - (R4H3)')
            im42, = a3.plot([], [], 'o-', label='Roller Pressure - (R4H4)')
            # --------------------------------------------------[Laser Angle]
            im43, = a4.plot([], [], 'o-', label='Laser Angle - (R1H1)')
            im44, = a4.plot([], [], 'o-', label='Laser Angle - (R1H2)')
            im45, = a4.plot([], [], 'o-', label='Laser Angle - (R1H3)')
            im46, = a4.plot([], [], 'o-', label='Laser Angle - (R1H4)')
            im47, = a4.plot([], [], 'o-', label='Laser Angle - (R2H1)')
            im48, = a4.plot([], [], 'o-', label='Laser Angle - (R2H2)')
            im49, = a4.plot([], [], 'o-', label='Laser Angle - (R2H3)')
            im50, = a4.plot([], [], 'o-', label='Laser Angle - (R2H4)')
            im51, = a4.plot([], [], 'o-', label='Laser Angle - (R3H1)')
            im52, = a4.plot([], [], 'o-', label='Laser Angle - (R3H2)')
            im53, = a4.plot([], [], 'o-', label='Laser Angle - (R3H3)')
            im54, = a4.plot([], [], 'o-', label='Laser Angle - (R3H4)')
            im55, = a4.plot([], [], 'o-', label='Laser Angle - (R4H1)')
            im56, = a4.plot([], [], 'o-', label='Laser Angle - (R4H2)')
            im57, = a4.plot([], [], 'o-', label='Laser Angle - (R4H3)')
            im58, = a4.plot([], [], 'o-', label='Laser Angle - (R4H4)')
            # -----------------------------------------------[ Oven Temperature]
            im59, = a5.plot([], [], 'o-', label='RTD Oven Temperature (Lower Segment)')
            im60, = a5.plot([], [], 'o-', label='RTD Oven Temperature (Upper Segment)')
            im61, = a6.plot([], [], 'o-', label='IR Oven Temperature (Lower Segment)')
            im62, = a6.plot([], [], 'o-', label='IR Oven Temperature (Upper Segment)')
            # ----------------------------------------------[Winding Speed x16]
            im63, = a6.plot([], [], 'o-', label='Winding Speed - (Ring 1)')
            im64, = a6.plot([], [], 'o-', label='Winding Speed - (Ring 2)')
            im65, = a6.plot([], [], 'o-', label='Winding Speed - (Ring 3)')
            im66, = a6.plot([], [], 'o-', label='Winding Speed - (Ring 4)')

        else:
            print('Ilegal requiest. Bespoke user selection not enabled')

            # ---------------- EXECUTE SYNCHRONOUS METHOD ---------------#

        def synchronousP(fetchT):
            fetch_no = str(fetchT)      # entry value in string sql syntax

            # Obtain SQL Data Host Server ---------------------------[GEN, RP, LP, LA]
            if pRecipe == 'DNV':
                conA, conB, conC, conD  = conn.cursor(),  conn.cursor(), conn.cursor(), conn.cursor()     # SQL stream
            elif pRecipe == 'MGM':
                conA, conB, conC, conD, conE, conF, conG  = (conn.cursor(), conn.cursor(), conn.cursor(),
                                                             conn.cursor(), conn.cursor(), conn.cursor(), conn.cursor())

            else:
                pass                                        # reserved for bespoke configuration

            # Evaluate conditions for SQL Data Fetch ---------------[A]
            """
            Load watchdog function with synchronous function every seconds
            """

            # Initialise RT variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard                     # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                # print('Indefinite looping...')
                import sqlArrayRLmethodPM as spm                             # Process Monitoring method

                inProgress = True                                            # True for RetroPlay mode
                print('\nAsynchronous controller activated...')
                print('DrLabs' + "' Runtime Optimisation is Enabled!")

                if not sysRun:
                    sysRun, msctcp, msc_rt = wd.autoPausePlay()             # Retrieve M.State from Watchdog
                print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                if keyboard.is_pressed("Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:
                    print('\nProduction is pausing...')
                    if not autoSpcPause:
                        autoSpcRun = not autoSpcRun
                        autoSpcPause = True
                        print("\nVisualization in Paused Mode...")
                    else:
                        autoSpcPause = False
                        print("Visualization in Real-time Mode...")

                else:
                    # Get list of relevant SQL Tables using conn() and execute real-time query --------------------[]
                    if pRecipe == 'DNV':
                        dGEN, dRPa, dRPb, dRPc = spm.dnv_sqlExec(mtS, mtTy, conA, conB, conC, conD, T1, T2, T3, T4, fetch_no)

                    elif pRecipe == 'MGM':
                        dGEN, dRPa, dRPb, dLPa, dLPb, dLAa, dLAb = spm.mgm_sqlExec(mtS, mtTy, conA, conB, conC,
                                                                                   conD, conE, conF, conG, T1, T2, T3,
                                                                                   T4, T5, T6, T7, fetch_no)
                    else:
                        dGEN, dRP, dLP, dLA = 0, 0, 0, 0            # Assigned to Bespoke User Selection.

                # ------ Inhibit iteration ----------------------------------------------------------[]
                """
                # Set condition for halting real-time plots in watchdog class ---------------------
                """
                # TODO --- values for inhibiting the SQL processing
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    conA.close()
                    conB.close()
                    if monitorP == 'MGM':
                        conC.close()
                        conD.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

            if monitorP == 'DNV':
                return dGEN, dRPa, dRPb, dRPc
            else:
                return dGEN, dRPa, dRPb, dLPa, dLPb, dLAa, dLAb

        # ================== End of synchronous Method ==========================================================[]

        def asynchronousP(db_freq):
            timei = time.time()                                                             # start timing the entire loop

            # declare asynchronous variables ------------------[]
            if monitorP == 'DNV':
                dGEN, dRPa, dRPb, dRPc = synchronousP(db_freq)                                    # data loading functions
            else:
                dGEN, dRPa, dRPb, dLPa, dLPb, dLAa, dLAb = synchronousP(db_freq)            # data loading functions

            import VarSQL_PM as pm                                                          # Construct new data frame columns

            viz_cycle = 150
            if monitorP == 'DNV':
                g1 = qpm.validCols(T1)                          # General Table (OT/CT)
                d1 = pd.DataFrame(dGEN, columns=g1)
                g2 = qpm.validCols(T2)                          # Roller Pressure Table 1
                d2 = pd.DataFrame(dRPa, columns=g2)
                g3 = qpm.validCols(T3)                          # Roller Pressure Table 2
                d3 = pd.DataFrame(dRPb, columns=g3)
                g4 = qpm.validCols(T4)                          # Winding Speed
                d4 = pd.DataFrame(dRPc, columns=g4)

                # Concatenate all columns -----------------------[]
                df1 = pd.concat([d1, d2, d3, d4], axis=1)

            elif monitorP == 'MGM':
                g1 = qpm.validCols(T1)                          # General Table
                d1 = pd.DataFrame(dGEN, columns=g1)

                g2 = qpm.validCols(T2)                          # Roller Pressure Table 1
                d2 = pd.DataFrame(dRPa, columns=g2)

                g3 = qpm.validCols(T3)                          # Roller Pressure Table 2
                d3 = pd.DataFrame(dRPb, columns=g3)

                g4 = qpm.validCols(T4)                          # Laser Power Table 1
                d4 = pd.DataFrame(dLPa, columns=g4)

                g5 = qpm.validCols(T5)                          # Laser Power Table 2
                d5 = pd.DataFrame(dLPb, columns=g5)

                g6 = qpm.validCols(T6)                          # Laser Angle
                d6 = pd.DataFrame(dLAa, columns=g6)

                g7 = qpm.validCols(T7)                          # Laser Angle
                d7 = pd.DataFrame(dLAb, columns=g7)

                # Concatenate all columns -----------[]
                df1 = pd.concat([d1, d2, d3, d4, d5, d6, d7], axis=1)
            else:
                df1 = 0
                pass                                            # Reserve for process scaling -- RBL.

            # ----- Access data element within the concatenated columns -------------------------[A]
            PM = pm.loadProcesValues(df1, monitorP)             # Join data values under dataframe
            print('\nDataFrame Content', df1.head(10))          # Preview Data frame head
            print("Memory Usage:", df1.info(verbose=False))     # Check memory utilization

            # Declare Plots attributes ------------------------------------------------------------[]
            im10.set_xdata(np.arange(db_freq))
            im11.set_xdata(np.arange(db_freq))
            im12.set_xdata(np.arange(db_freq))
            im13.set_xdata(np.arange(db_freq))
            im14.set_xdata(np.arange(db_freq))
            im15.set_xdata(np.arange(db_freq))
            im16.set_xdata(np.arange(db_freq))
            im17.set_xdata(np.arange(db_freq))
            im18.set_xdata(np.arange(db_freq))
            im19.set_xdata(np.arange(db_freq))
            im20.set_xdata(np.arange(db_freq))
            im21.set_xdata(np.arange(db_freq))
            im22.set_xdata(np.arange(db_freq))
            im23.set_xdata(np.arange(db_freq))
            im24.set_xdata(np.arange(db_freq))
            im25.set_xdata(np.arange(db_freq))

            im26.set_xdata(np.arange(db_freq))
            im27.set_xdata(np.arange(db_freq))
            im28.set_xdata(np.arange(db_freq))
            im29.set_xdata(np.arange(db_freq))
            im30.set_xdata(np.arange(db_freq))
            im31.set_xdata(np.arange(db_freq))
            im32.set_xdata(np.arange(db_freq))
            im33.set_xdata(np.arange(db_freq))
            im34.set_xdata(np.arange(db_freq))
            im35.set_xdata(np.arange(db_freq))
            im36.set_xdata(np.arange(db_freq))
            im37.set_xdata(np.arange(db_freq))
            im38.set_xdata(np.arange(db_freq))
            im39.set_xdata(np.arange(db_freq))
            im40.set_xdata(np.arange(db_freq))
            im41.set_xdata(np.arange(db_freq))

            im42.set_xdata(np.arange(db_freq))
            im43.set_xdata(np.arange(db_freq))
            im44.set_xdata(np.arange(db_freq))
            im45.set_xdata(np.arange(db_freq))

            im46.set_xdata(np.arange(db_freq))
            im47.set_xdata(np.arange(db_freq))
            im48.set_xdata(np.arange(db_freq))
            im49.set_xdata(np.arange(db_freq))
            im50.set_xdata(np.arange(db_freq))
            im51.set_xdata(np.arange(db_freq))
            im52.set_xdata(np.arange(db_freq))
            im53.set_xdata(np.arange(db_freq))
            im54.set_xdata(np.arange(db_freq))
            im55.set_xdata(np.arange(db_freq))
            im56.set_xdata(np.arange(db_freq))
            im57.set_xdata(np.arange(db_freq))
            im58.set_xdata(np.arange(db_freq))
            im59.set_xdata(np.arange(db_freq))
            im60.set_xdata(np.arange(db_freq))
            im61.set_xdata(np.arange(db_freq))

            im62.set_xdata(np.arange(db_freq))
            im63.set_xdata(np.arange(db_freq))
            im64.set_xdata(np.arange(db_freq))
            im65.set_xdata(np.arange(db_freq))
            im66.set_xdata(np.arange(db_freq))

            if monitorP == 'DNV':
                # X Plot Y-Axis data points for XBar ----------[Roller Pressure x16, A1]
                im10.set_ydata((PM[13]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # R1H1
                im11.set_ydata((PM[14]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # R1H2
                im12.set_ydata((PM[15]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # R1H3
                im13.set_ydata((PM[16]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # R1H4
                im14.set_ydata((PM[17]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # R2H1
                im15.set_ydata((PM[18]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # R2H2
                im16.set_ydata((PM[19]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # R2H3
                im17.set_ydata((PM[20]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # R2H4
                im18.set_ydata((PM[21]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 1
                im19.set_ydata((PM[22]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 2
                im20.set_ydata((PM[23]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 3
                im21.set_ydata((PM[24]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 4
                im22.set_ydata((PM[25]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 1
                im23.set_ydata((PM[26]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 2
                im24.set_ydata((PM[27]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 3
                im25.set_ydata((PM[28]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 4
                # ------------------------------------- Tape Winding Speed x16, A2
                im26.set_ydata((PM[6]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 1
                im27.set_ydata((PM[7]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 2
                im28.set_ydata((PM[8]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 3
                im29.set_ydata((PM[9]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 4
                # --------------------------------------Active Cell Tension x1
                im30.set_ydata((PM[1]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 1
                # ----------------------------------------Oven Temperature x4 (RTD & IR Temp)
                im31.set_ydata((PM[2]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 2
                im32.set_ydata((PM[3]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 3
                im33.set_ydata((PM[4]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 4
                im34.set_ydata((PM[5]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 1

            elif monitorP == 'MGM':
                # -------------------------------------------------------------------------------[Laser Power]
                im10.set_ydata((PM[30]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 1
                im11.set_ydata((PM[31]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 2
                im12.set_ydata((PM[32]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 3
                im13.set_ydata((PM[33]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 4
                im14.set_ydata((PM[34]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 1
                im15.set_ydata((PM[35]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 2
                im16.set_ydata((PM[36]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 3
                im17.set_ydata((PM[37]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 4
                im18.set_ydata((PM[38]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 1
                im19.set_ydata((PM[39]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 2
                im20.set_ydata((PM[40]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 3
                im21.set_ydata((PM[41]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 4
                im22.set_ydata((PM[42]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 1
                im23.set_ydata((PM[43]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 2
                im24.set_ydata((PM[44]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 3
                im25.set_ydata((PM[45]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 4
                # -----------------------------------------------------[Cell Tension]
                im26.set_ydata((PM[1]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])   # Segment 1
                # --------------------------------------------------[Roller Pressure]
                im27.set_ydata((PM[13]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 2
                im28.set_ydata((PM[14]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 3
                im29.set_ydata((PM[15]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 4
                im30.set_ydata((PM[16]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 1
                im31.set_ydata((PM[17]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 2
                im32.set_ydata((PM[18]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 3
                im33.set_ydata((PM[19]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 4
                im34.set_ydata((PM[20]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 1
                im35.set_ydata((PM[21]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 2
                im36.set_ydata((PM[22]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 3
                im37.set_ydata((PM[23]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 4
                im38.set_ydata((PM[24]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 1
                im39.set_ydata((PM[25]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 2
                im40.set_ydata((PM[26]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 3
                im41.set_ydata((PM[27]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 4
                im42.set_ydata((PM[28]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 1
                # -------------------------------------------------------[Laser Angle]
                im43.set_ydata((PM[47]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 2
                im44.set_ydata((PM[48]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 1
                im45.set_ydata((PM[49]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 2
                im46.set_ydata((PM[50]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 1
                im47.set_ydata((PM[51]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 2
                im48.set_ydata((PM[52]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 3
                im49.set_ydata((PM[53]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 4
                im50.set_ydata((PM[54]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 1
                im51.set_ydata((PM[55]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 2
                im52.set_ydata((PM[56]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 3
                im53.set_ydata((PM[57]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 4
                im54.set_ydata((PM[58]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 1
                im55.set_ydata((PM[59]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 2
                im56.set_ydata((PM[60]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 3
                im57.set_ydata((PM[61]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 4
                im58.set_ydata((PM[62]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 1
                # -------------------------------------------------[Oven Temperature]
                im59.set_ydata((PM[2]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 2
                im60.set_ydata((PM[3]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 3
                im61.set_ydata((PM[4]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 4
                im62.set_ydata((PM[5]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 1
                # ----------------------------------------------[Winding Speed x16]
                im63.set_ydata((PM[6]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 2
                im64.set_ydata((PM[7]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 3
                im65.set_ydata((PM[8]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 4
                im66.set_ydata((PM[9]).rolling(window=mtS, min_periods=1).mean()[0:db_freq])  # Segment 1

            else:
                # X Plot Y-Axis data points for XBar -------------------------------------------[# Channels]
                print('No data to plot...')

            # --------------------
            xline, sline = 10, 2.2
            # Declare Plots attributes ----------------------------[]
            a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
            # ---------------------- sBar_minTG, sBar_maxTG -------[]

            # Setting up the parameters for moving windows Axes ---[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a1.set_xlim(0, window_Xmax)

            # No trigger module processing - Production parameter is for monitoring purposes only.
            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousP, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)

        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

# ------------------------------------------------------------------------------------------[Laser Power Tab]
class laserPowerTabb(ttk.Frame):
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        # Load Quality Historical Values -----------[]
        if pRecipe == 'DNV':
            import qParamsHL_DNV as dnv
            lpS, lpTy, olS, opS, pHL, pAL, pFO, pP1, pP2, pP3, pP4, pP5 = dnv.decryptpProcessLim(pWON, 'LP')
        else:
            import qParamsHL_MGM as mgm
            lpS, lpTy, olS, opS, pHL, pAL, pFO, pP1, pP2, pP3, pP4, pP5 = mgm.decryptpProcessLim(pWON, 'LP')
        # Break down each element to useful list ---------------[Tape Temperature]

        if pHL and pP1 and pP2 and pP3 and pP4 and pP5:  #
            lpPerf = '$Pp_{k' + str(lpS) + '}$'  # Using estimated or historical Mean
            lplabel = 'Pp'
            # -------------------------------
            One = pP1.split(',')                   # split into list elements
            Two = pP2.split(',')
            Thr = pP3.split(',')
            For = pP4.split(',')
            Fiv = pP5.split(',')
            # -------------------------------
            dTape1 = One[1].strip("' ")                 # defined Tape Width
            dTape2 = Two[1].strip("' ")                 # defined Tape Width
            dTape3 = Thr[1].strip("' ")                 # defined Tape Width
            dTape4 = For[1].strip("' ")                 # defined Tape Width
            dTape5 = Fiv[1].strip("' ")                 # defined Tape Width
            # --------------------------------
            dLayer1 = One[10].strip("' ")               # Defined Tape Layer
            dLayer2 = Two[10].strip("' ")
            dLayer3 = Thr[10].strip("' ")
            dLayer4 = For[10].strip("' ")
            dLayer5 = Fiv[10].strip("' ")
            # Load historical limits for the process----#
            if cpLayerNo == 1:                          # '22mm'|'18mm',  1-40 | 41+ TODO
                lpUCL = float(One[2].strip("' "))       # Strip out the element of the list
                lpLCL = float(One[3].strip("' "))
                lpMean = float(One[4].strip("' "))
                lpDev = float(One[5].strip("' "))
                # --------------------------------
                sUCLlp = float(One[6].strip("' "))
                sLCLlp = float(One[7].strip("' "))
                # --------------------------------
                lpUSL = (lpUCL - lpMean) / 3 * 6
                lpLSL = (lpMean - lpLCL) / 3 * 6
                # --------------------------------
            elif cpTapeW == dTape2 and cpLayerNo == 2:
                lpUCL = float(Two[2].strip("' "))       # Strip out the element of the list
                lpLCL = float(Two[3].strip("' "))
                lpMean = float(Two[4].strip("' "))
                lpDev = float(Two[5].strip("' "))
                # --------------------------------
                sUCLlp = float(Two[6].strip("' "))
                sLCLlp = float(Two[7].strip("' "))
                # --------------------------------
                lpUSL = (lpUCL - lpMean) / 3 * 6
                lpLSL = (lpMean - lpLCL) / 3 * 6
            elif cpTapeW == dTape3 and cpLayerNo == range(3, 40):
                lpUCL = float(Thr[2].strip("' "))       # Strip out the element of the list
                lpLCL = float(Thr[3].strip("' "))
                lpMean = float(Thr[4].strip("' "))
                lpDev = float(Thr[5].strip("' "))
                # --------------------------------
                sUCLlp = float(Thr[6].strip("' "))
                sLCLlp = float(Thr[7].strip("' "))
                # --------------------------------
                lpUSL = (lpUCL - lpMean) / 3 * 6
                lpLSL = (lpMean - lpLCL) / 3 * 6
            elif cpTapeW == dTape4 and cpLayerNo == 41:
                lpUCL = float(For[2].strip("' "))       # Strip out the element of the list
                lpLCL = float(For[3].strip("' "))
                lpMean = float(For[4].strip("' "))
                lpDev = float(For[5].strip("' "))
                # --------------------------------
                sUCLlp = float(For[6].strip("' "))
                sLCLlp = float(For[7].strip("' "))
                # --------------------------------
                lpUSL = (lpUCL - lpMean) / 3 * 6
                lpLSL = (lpMean - lpLCL) / 3 * 6
            else:
                lpUCL = float(Fiv[2].strip("' "))       # Strip out the element of the list
                lpLCL = float(Fiv[3].strip("' "))
                lpMean = float(Fiv[4].strip("' "))
                lpDev = float(Fiv[5].strip("' "))
                # --------------------------------
                sUCLlp = float(Fiv[6].strip("' "))
                sLCLlp = float(Fiv[7].strip("' "))
                # --------------------------------
                lpUSL = (lpUCL - lpMean) / 3 * 6
                lpLSL = (lpMean - lpLCL) / 3 * 6
                # -------------------------------
        else:  # Computes Shewhart constants (Automatic Limits)
            lpUCL = 0
            lpLCL = 0
            lpMean = 0
            lpDev = 0
            sUCLlp = 0
            sLCLlp = 0
            lpUSL = 0
            lpLSL = 0
            lpPerf = '$Cp_{k' + str(lpS) + '}$'  # Using Automatic group Mean
            lplabel = 'Cp'

        # ------------------------------------[End of Tape Temperature Abstraction]
        label = ttk.Label(self, text='[' + rType + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Define Axes ---------------------#
        f = Figure(figsize=(pMtX, 8), dpi=100)  #[25 on 1920 x 1200 resolution screen, 27 on 4096 x2160]
        f.subplots_adjust(left=0.022, bottom=0.05, right=0.993, top=0.967, wspace=0.18, hspace=0.174)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 4, (1, 3))   # X Bar Plot
        a2 = f.add_subplot(2, 4, (5, 7))   # S Bar Plo
        a3 = f.add_subplot(2, 4, (4, 8))   # Performance Feeed
        # --------------- Former format -------------

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minLP, YScale_maxLP = lpLSL - 8.5, lpUSL + 8.5       # Roller Force
        sBar_minLP, sBar_maxLP = sLCLlp - 80, sUCLlp + 80           # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (int(lpS) + 3)                # windows view = visible data points

        # Select betweeen straem -----------------------------------#
        if rType == 1:
            T1 = SPC_LP
        else:
            T1 = 'LP1_' + pWON                                          # Laser Power
            T2 = 'LP2_' + pWON
        # ----------------------------------------------------------#

        # Initialise runtime limits
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        a1.set_title('Laser Power [XBar]', fontsize=12, fontweight='bold')
        a2.set_title('Laser Power [StDev]', fontsize=12, fontweight='bold')

        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a1.legend(loc='upper right', title='Laser Power (Watt)')
        a2.legend(loc='upper right', title='Sigma curve')

        # ----------------------------------------------------------#
        a1.set_ylim([YScale_minLP, YScale_maxLP], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        a2.set_ylim([sBar_minLP, sBar_maxLP], auto=True)
        a2.set_xlim([window_Xmin, window_Xmax])

        # ---------------------------------------------------------[]
        a3.cla()
        a3.get_yaxis().set_visible(False)
        a3.get_xaxis().set_visible(False)

        # ---------------------------------------------------------[]
        # Define Plot area and axes -
        # ---------------------------------------------------------#
        im10, = a1.plot([], [], 'o-', label='Laser Power - (R1H1)')
        im11, = a1.plot([], [], 'o-', label='Laser Power - (R1H2)')
        im12, = a1.plot([], [], 'o-', label='Laser Power - (R1H3)')
        im13, = a1.plot([], [], 'o-', label='Laser Power - (R1H4)')
        im14, = a2.plot([], [], 'o-', label='Laser Power')
        im15, = a2.plot([], [], 'o-', label='Laser Power')
        im16, = a2.plot([], [], 'o-', label='Laser Power')
        im17, = a2.plot([], [], 'o-', label='Laser Power')

        im18, = a1.plot([], [], 'o-', label='Laser Power - (R2H1)')
        im19, = a1.plot([], [], 'o-', label='Laser Power - (R2H2)')
        im20, = a1.plot([], [], 'o-', label='Laser Power - (R2H3)')
        im21, = a1.plot([], [], 'o-', label='Laser Power - (R2H4)')
        im22, = a2.plot([], [], 'o-', label='Laser Power')
        im23, = a2.plot([], [], 'o-', label='Laser Power')
        im24, = a2.plot([], [], 'o-', label='Laser Power')
        im25, = a2.plot([], [], 'o-', label='Laser Power')

        im26, = a1.plot([], [], 'o-', label='Laser Power - (R3H1)')
        im27, = a1.plot([], [], 'o-', label='Laser Power - (R3H2)')
        im28, = a1.plot([], [], 'o-', label='Laser Power - (R3H3)')
        im29, = a1.plot([], [], 'o-', label='Laser Power - (R3H4)')
        im30, = a2.plot([], [], 'o-', label='Laser Power')
        im31, = a2.plot([], [], 'o-', label='Laser Power')
        im32, = a2.plot([], [], 'o-', label='Laser Power')
        im33, = a2.plot([], [], 'o-', label='Laser Power')

        im34, = a1.plot([], [], 'o-', label='Laser Power - (R4H1)')
        im35, = a1.plot([], [], 'o-', label='Laser Power - (R4H2)')
        im36, = a1.plot([], [], 'o-', label='Laser Power - (R4H3)')
        im37, = a1.plot([], [], 'o-', label='Laser Power - (R4H4)')
        im38, = a2.plot([], [], 'o-', label='Laser Power')
        im39, = a2.plot([], [], 'o-', label='Laser Power')
        im40, = a2.plot([], [], 'o-', label='Laser Power')
        im41, = a2.plot([], [], 'o-', label='Laser Power')

        # Statistical Feed -----------------------------------------[]
        a3.text(0.466, 0.945, 'Performance Feed - LP', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        a3.add_patch(rect1)
        a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)---------------------
        a3.text(0.145, 0.804, lplabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.658, '#Pp Value', fontsize=24, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.650, 0.820, 'Ring ' + lplabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        a3.text(0.145, 0.403, lpPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=22, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring ' + lpPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        # -------------------------------------
        a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ----- Pipe Position and SMC Status -----
        a3.text(0.080, 0.090, 'Pipe Position: ' + pPos + '    Processing Layer #' + layer, fontsize=12, ha='left',
                transform=a3.transAxes)
        a3.text(0.080, 0.036, 'SMC Status: ' + eSMC, fontsize=12, ha='left', transform=a3.transAxes)

        # ---------------- EXECUTE SYNCHRONOUS METHOD -----------------------------#
        def synchronousLP(lpS, lpTy, fetchT):
            fetch_no = str(fetchT)                  # entry value in string sql syntax

            # Obtain Volatile Data from PLC Host Server ---------------------------[]
            if not inUseAlready:                    # Load CommsPlc class once
                import CommsSql as q
                q.DAQ_connect(1, 0)
            else:
                con_a, con_b = conn.cursor(), conn.cursor()

            # Evaluate conditions for SQL Data Fetch ------------------------------[A]
            """
            Load watchdog function with synchronous function every seconds
            """
            # Initialise RT variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard                         # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                if UsePLC_DBS:                               # Not Using PLC Data
                    import plcArrayRLmethodLP as slp         # DrLabs optimization method

                    inProgress = False                       # False for Real-time mode
                    print('\nSynchronous controller activated...')

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve MSC from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    # Either of the 2 combo variables are assigned to trigger routine pause
                    if keyboard.is_pressed("ctrl") or not msctcp == 315 and not sysRun and not inProgress:
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            # play(error)                            # Pause mode with audible Alert
                            print("\nVisualization in Paused Mode...")

                    else:
                        autoSpcPause = False

                    # Play visualization ----------------------------------------------[]
                    print("Visualization in Play Mode...")
                    # -----------------------------------------------------------------[]
                    lpDta = slp.plcExec(T1, lpS, lpTy, fetch_no)
                    lpDtb = 0

                else:
                    import sqlArrayRLmethodLP as slp        # DrLabs optimization method

                    inProgress = True                       # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve M.State from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    if keyboard.is_pressed("Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            print("\nVisualization in Paused Mode...")
                        else:
                            autoSpcPause = False
                            print("Visualization in Real-time Mode...")
                    else:
                        # Get list of relevant SQL Tables using conn() --------------------[]
                        lpDta, lpDtb = slp.sqlExec(lpS, lpTy, con_a, con_b, T1, T2, fetchT)

                    # ------ Inhibit iteration ----------------------------------------------------------[]
                    """
                    # Set condition for halting real-time plots in watchdog class ---------------------
                    """
                    # TODO --- values for inhibiting the SQL processing
                    if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                        con_a.close()
                        con_b.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

            return lpDta, lpDtb

        # ================== End of synchronous Method ==========================
        def asynchronousLP(db_freq):
            timei = time.time()                                 # start timing the entire loop

            # Bistream Data Pooling Method ---------------------#
            lpDta, lpDtb = synchronousLP(lpS, lpTy, db_freq)                     # data loading functions
            # --------------------------------------------------#

            if UsePLC_DBS == 1:
                import VarPLC_LP as lp

                viz_cycle = 10
                # Call synchronous data function ---------------[]
                columns = qlp.validCols(T1)                     # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(lpDta, columns=columns)      # Include table data into python Dataframe
                LP = lp.loadProcesValues(df1)                   # Join data values under dataframe

            else:
                import VarSQL_LP as lp                        # load SQL variables column names | rfVarSQL

                viz_cycle = 150
                g1 = qlp.validCols(T1)                          # Construct Data Column selSqlColumnsTFM.py
                d1 = pd.DataFrame(lpDta, columns=g1)
                g2 = qlp.validCols(T2)
                d2 = pd.DataFrame(lpDtb, columns=g2)          # Import into python Dataframe

                # Concatenate all columns -----------[]
                df1 = pd.concat([d1, d2], axis=1)          # Join data values under dataframe
                LP = lp.loadProcesValues(df1)
            print('\nSQL Content', df1.head(10))
            print("Memory Usage:", df1.info(verbose=False))     # Check memory utilization

            # -------------------------------------------------------------------------------------[]
            # Plot X-Axis data points -------- X Plot
            im10.set_xdata(np.arange(db_freq))
            im11.set_xdata(np.arange(db_freq))
            im12.set_xdata(np.arange(db_freq))
            im13.set_xdata(np.arange(db_freq))
            im14.set_xdata(np.arange(db_freq))
            im15.set_xdata(np.arange(db_freq))
            im16.set_xdata(np.arange(db_freq))
            im17.set_xdata(np.arange(db_freq))
            im18.set_xdata(np.arange(db_freq))
            im19.set_xdata(np.arange(db_freq))
            im20.set_xdata(np.arange(db_freq))
            im21.set_xdata(np.arange(db_freq))
            im22.set_xdata(np.arange(db_freq))
            im23.set_xdata(np.arange(db_freq))
            im24.set_xdata(np.arange(db_freq))
            im25.set_xdata(np.arange(db_freq))
            # ------------------------------- S Plot
            im26.set_xdata(np.arange(db_freq))
            im27.set_xdata(np.arange(db_freq))
            im28.set_xdata(np.arange(db_freq))
            im29.set_xdata(np.arange(db_freq))
            im30.set_xdata(np.arange(db_freq))
            im31.set_xdata(np.arange(db_freq))
            im32.set_xdata(np.arange(db_freq))
            im33.set_xdata(np.arange(db_freq))
            im34.set_xdata(np.arange(db_freq))
            im35.set_xdata(np.arange(db_freq))
            im36.set_xdata(np.arange(db_freq))
            im37.set_xdata(np.arange(db_freq))
            im38.set_xdata(np.arange(db_freq))
            im39.set_xdata(np.arange(db_freq))
            im40.set_xdata(np.arange(db_freq))
            im41.set_xdata(np.arange(db_freq))      # lpS, lTy

            # X Plot Y-Axis data points for XBar --------------------------------------------[  # Ring 1 ]
            im10.set_ydata((LP[0]).rolling(window=lpS, min_periods=1).mean()[0:db_freq])  # head 1
            im11.set_ydata((LP[1]).rolling(window=lpS, min_periods=1).mean()[0:db_freq])  # head 2
            im12.set_ydata((LP[2]).rolling(window=lpS, min_periods=1).mean()[0:db_freq])  # head 3
            im13.set_ydata((LP[3]).rolling(window=lpS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 1 ---------#
            mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(pAL, lpS, 'LP')
            # ---------------------------------------#
            im14.set_ydata((LP[4]).rolling(window=lpS, min_periods=1).mean()[0:db_freq])  # head 1
            im15.set_ydata((LP[5]).rolling(window=lpS, min_periods=1).mean()[0:db_freq])  # head 2
            im16.set_ydata((LP[6]).rolling(window=lpS, min_periods=1).mean()[0:db_freq])  # head 3
            im17.set_ydata((LP[7]).rolling(window=lpS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 2 ---------#
            mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(pAL, lpS, 'LP')
            # ---------------------------------------#
            im18.set_ydata((LP[8]).rolling(window=lpS, min_periods=1).mean()[0:db_freq])  # head 1
            im19.set_ydata((LP[9]).rolling(window=lpS, min_periods=1).mean()[0:db_freq])  # head 2
            im20.set_ydata((LP[10]).rolling(window=lpS, min_periods=1).mean()[0:db_freq])  # head 3
            im21.set_ydata((LP[11]).rolling(window=lpS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 3 ---------#
            mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(pAL, lpS, 'LP')
            # ---------------------------------------#
            im22.set_ydata((LP[12]).rolling(window=lpS, min_periods=1).mean()[0:db_freq])  # head 1
            im23.set_ydata((LP[13]).rolling(window=lpS, min_periods=1).mean()[0:db_freq])  # head 2
            im24.set_ydata((LP[14]).rolling(window=lpS, min_periods=1).mean()[0:db_freq])  # head 3
            im25.set_ydata((LP[15]).rolling(window=lpS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 4 ---------#
            mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(pAL, lpS, 'LP')
            # ---------------------------------------#
            # S Plot Y-Axis data points for StdDev ----------------------------------------
            im26.set_ydata((LP[0]).rolling(window=lpS, min_periods=1).std()[0:db_freq])
            im27.set_ydata((LP[1]).rolling(window=lpS, min_periods=1).std()[0:db_freq])
            im28.set_ydata((LP[2]).rolling(window=lpS, min_periods=1).std()[0:db_freq])
            im29.set_ydata((LP[3]).rolling(window=lpS, min_periods=1).std()[0:db_freq])

            im30.set_ydata((LP[4]).rolling(window=lpS, min_periods=1).std()[0:db_freq])
            im31.set_ydata((LP[5]).rolling(window=lpS, min_periods=1).std()[0:db_freq])
            im32.set_ydata((LP[6]).rolling(window=lpS, min_periods=1).std()[0:db_freq])
            im33.set_ydata((LP[7]).rolling(window=lpS, min_periods=1).std()[0:db_freq])

            im34.set_ydata((LP[8]).rolling(window=lpS, min_periods=1).std()[0:db_freq])
            im35.set_ydata((LP[9]).rolling(window=lpS, min_periods=1).std()[0:db_freq])
            im36.set_ydata((LP[10]).rolling(window=lpS, min_periods=1).std()[0:db_freq])
            im37.set_ydata((LP[11]).rolling(window=lpS, min_periods=1).std()[0:db_freq])

            im38.set_ydata((LP[12]).rolling(window=lpS, min_periods=1).std()[0:db_freq])
            im39.set_ydata((LP[13]).rolling(window=lpS, min_periods=1).std()[0:db_freq])
            im40.set_ydata((LP[14]).rolling(window=lpS, min_periods=1).std()[0:db_freq])
            im41.set_ydata((LP[15]).rolling(window=lpS, min_periods=1).std()[0:db_freq])

            # Compute entire Process Capability -----------#
            if not pAL:
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLb, ppT, pkT, xline, sline = tq.tAutoPerf(lpS, mnA, mnB,
                                                                                                      mnC, mnD, sdA,
                                                                                                      sdB, sdC, sdD)
            else:
                xline, sline = lpMean, lpDev
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLba, ppT, pkT = tq.tManualPerf(mnA, mnB, mnC, mnD, sdA, sdB,
                                                                                           sdC, sdD, lpUSL, lpLSL,
                                                                                           lpUCL,
                                                                                           lpLCL)

            # # Declare Plots attributes --------------------------------------------------------[]
            # XBar Mean Plot
            a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
            a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 3 Sigma span (Purple)
            a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minLP, sBar_maxLP -------[]
            # Define Legend's Attributes  ----
            a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
            a2.axhspan(sLCLlp, sUCLlp, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 1 Sigma Span
            a2.axhspan(sUCLlp, sBar_maxLP, facecolor='#CCCCFF', edgecolor='#CCCCFF')  # 1 Sigma above the Mean
            a2.axhspan(sBar_minLP, sLCLlp, facecolor='#CCCCFF', edgecolor='#CCCCFF')

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
                a2.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a1.set_xlim(0, window_Xmax)
                a2.set_xlim(0, window_Xmax)

            # Set trip line for individual time-series plot -----------------------------------[R1]
            import triggerModule as sigma
            sigma.trigViolations(a1, UsePLC_DBS, 'LP', YScale_minLP, YScale_maxLP, xucT, xlcT, xusT, xlsT, mnT, sdT)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousLP, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)

        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

# ------------------------------------------------------------------------------------------[Laser Angle Tab]
class laserAngleTabb(ttk.Frame):      # -- Defines the tabbed region for QA param - Tape Temperature --[]
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        # Load Quality Historical Values -----------[]
        laS, laTy, eolS, eopS, laHL, laAL, laFO, laP1, laP2, laP3, laP4, laP5 = mgm.decryptpProcessLim(pWON, 'LA')

        # Break down each element to useful list ---------------[Tape Temperature]
        if laHL and laP1 and laP2 and laP3 and laP4 and laP5:  #
            laPerf = '$Pp_{k' + str(laS) + '}$'  # Using estimated or historical Mean
            lalabel = 'Pp'
            # -------------------------------
            One = laP1.split(',')                   # split into list elements
            Two = laP2.split(',')
            Thr = laP3.split(',')
            For = laP4.split(',')
            Fiv = laP5.split(',')
            # -------------------------------
            dTape1 = One[1].strip("' ")                 # defined Tape Width
            dTape2 = Two[1].strip("' ")                 # defined Tape Width
            dTape3 = Thr[1].strip("' ")                 # defined Tape Width
            dTape4 = For[1].strip("' ")                 # defined Tape Width
            dTape5 = Fiv[1].strip("' ")                 # defined Tape Width
            # --------------------------------
            dLayer1 = One[10].strip("' ")               # Defined Tape Layer
            dLayer2 = Two[10].strip("' ")
            dLayer3 = Thr[10].strip("' ")
            dLayer4 = For[10].strip("' ")
            dLayer5 = Fiv[10].strip("' ")
            # Load historical limits for the process----#
            if cpLayerNo == 1:                          # '22mm'|'18mm',  1-40 | 41+ TODO
                laUCL = float(One[2].strip("' "))       # Strip out the element of the list
                laLCL = float(One[3].strip("' "))
                laMean = float(One[4].strip("' "))
                laDev = float(One[5].strip("' "))
                # --------------------------------
                sUCLla = float(One[6].strip("' "))
                sLCLla = float(One[7].strip("' "))
                # --------------------------------
                laUSL = (laUCL - laMean) / 3 * 6
                laLSL = (laMean - laLCL) / 3 * 6
                # --------------------------------
            elif cpTapeW == dTape2 and cpLayerNo == 2:
                laUCL = float(Two[2].strip("' "))       # Strip out the element of the list
                laLCL = float(Two[3].strip("' "))
                laMean = float(Two[4].strip("' "))
                laDev = float(Two[5].strip("' "))
                # --------------------------------
                sUCLla = float(Two[6].strip("' "))
                sLCLla = float(Two[7].strip("' "))
                # --------------------------------
                laUSL = (laUCL - laMean) / 3 * 6
                laLSL = (laMean - laLCL) / 3 * 6
            elif cpTapeW == dTape3 and cpLayerNo == range(3, 40):
                laUCL = float(Thr[2].strip("' "))       # Strip out the element of the list
                laLCL = float(Thr[3].strip("' "))
                laMean = float(Thr[4].strip("' "))
                laDev = float(Thr[5].strip("' "))
                # --------------------------------
                sUCLla = float(Thr[6].strip("' "))
                sLCLla = float(Thr[7].strip("' "))
                # --------------------------------
                laUSL = (laUCL - laMean) / 3 * 6
                laLSL = (laMean - laLCL) / 3 * 6
            elif cpTapeW == dTape4 and cpLayerNo == 41:
                laUCL = float(For[2].strip("' "))       # Strip out the element of the list
                laLCL = float(For[3].strip("' "))
                laMean = float(For[4].strip("' "))
                laDev = float(For[5].strip("' "))
                # --------------------------------
                sUCLla = float(For[6].strip("' "))
                sLCLla = float(For[7].strip("' "))
                # --------------------------------
                laUSL = (laUCL - laMean) / 3 * 6
                laLSL = (laMean - laLCL) / 3 * 6
            else:
                laUCL = float(Fiv[2].strip("' "))       # Strip out the element of the list
                laLCL = float(Fiv[3].strip("' "))
                laMean = float(Fiv[4].strip("' "))
                laDev = float(Fiv[5].strip("' "))
                # --------------------------------
                sUCLla = float(Fiv[6].strip("' "))
                sLCLla = float(Fiv[7].strip("' "))
                # --------------------------------
                laUSL = (laUCL - laMean) / 3 * 6
                laLSL = (laMean - laLCL) / 3 * 6
                # -------------------------------
        else:  # Computes Shewhart constants (Automatic Limits)
            laUCL = 0
            laLCL = 0
            laMean = 0
            laDev = 0
            sUCLla = 0
            sLCLla = 0
            laUSL = 0
            laLSL = 0
            laPerf = '$Cp_{k' + str(laS) + '}$'  # Using Automatic group Mean
            lalabel = 'Cp'

        # ------------------------------------[End of Tape Temperature Abstraction]

        label = ttk.Label(self, text='[' + rType + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Define Axes ---------------------#
        f = Figure(figsize=(pMtX, 8), dpi=100)
        f.subplots_adjust(left=0.022, bottom=0.05, right=0.993, top=0.967, wspace=0.18, hspace=0.174)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 4, (1, 3))   # X Bar Plot
        a2 = f.add_subplot(2, 4, (5, 7))   # S Bar Plo
        a3 = f.add_subplot(2, 4, (4, 8))   # Performance Feeed
        # --------------- Former format -------------

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minLA, YScale_maxLA = laLSL - 8.5, laUSL + 8.5       # Roller Force
        sBar_minLA, sBar_maxLA = sLCLla - 80, sUCLla + 80           # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (int(laS) + 3)             # windows view = visible data points

        # ----------------------------------------------------------#
        # Real-Time Parameter according to updated requirements ----# 07/Feb/2025
        # Select betweeen straem -----------------------------------#
        if rType == 1:
            T1 = SPC_LA
        else:
            T1 = 'LA1_' + pWON          # Laser Power table 1
            T2 = 'LA2_' + pWON          # Laser Power table 2
        # ----------------------------------------------------------#

        # Initialise runtime limits
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        a1.set_title('Laser Angle [XBar Plot]', fontsize=12, fontweight='bold')
        a2.set_title('Laser Angle [S Plot]', fontsize=12, fontweight='bold')

        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a1.legend(loc='upper right', title='Laser Angle (Deg)')
        a2.legend(loc='upper right', title='Sigma curve')

        # ----------------------------------------------------------#
        a1.set_ylim([YScale_minLA, YScale_maxLA], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        a2.set_ylim([sBar_minLA, sBar_maxLA], auto=True)
        a2.set_xlim([window_Xmin, window_Xmax])

        # ---------------------------------------------------------[]
        a3.cla()
        a3.get_yaxis().set_visible(False)
        a3.get_xaxis().set_visible(False)

        # ---------------------------------------------------------[]
        # Define Plot area and axes -
        # ---------------------------------------------------------#
        im10, = a1.plot([], [], 'o-.', label='Laser Angle - (R1H1)')
        im11, = a1.plot([], [], 'o-', label='Laser Angle - (R1H2)')
        im12, = a1.plot([], [], 'o-', label='Laser Angle - (R1H3)')
        im13, = a1.plot([], [], 'o-', label='Laser Angle - (R1H4)')
        im14, = a2.plot([], [], 'o-', label='Laser Angle')
        im15, = a2.plot([], [], 'o-', label='Laser Angle')
        im16, = a2.plot([], [], 'o-', label='Laser Angle')
        im17, = a2.plot([], [], 'o-', label='Laser Angle')

        im18, = a1.plot([], [], 'o-.', label='Laser Angle - (R2H1)')
        im19, = a1.plot([], [], 'o-', label='Laser Angle - (R2H2)')
        im20, = a1.plot([], [], 'o-', label='Laser Angle - (R2H3)')
        im21, = a1.plot([], [], 'o-', label='Laser Angle - (R2H4)')
        im22, = a2.plot([], [], 'o-', label='Laser Angle')
        im23, = a2.plot([], [], 'o-', label='Laser Angle')
        im24, = a2.plot([], [], 'o-', label='Laser Angle')
        im25, = a2.plot([], [], 'o-', label='Laser Angle')

        im26, = a1.plot([], [], 'o-.', label='Laser Angle - (R3H1)')
        im27, = a1.plot([], [], 'o-', label='Laser Angle - (R3H2)')
        im28, = a1.plot([], [], 'o-', label='Laser Angle - (R3H3)')
        im29, = a1.plot([], [], 'o-', label='Laser Angle - (R3H4)')
        im30, = a2.plot([], [], 'o-', label='Laser Angle')
        im31, = a2.plot([], [], 'o-', label='Laser Angle')
        im32, = a2.plot([], [], 'o-', label='Laser Angle')
        im33, = a2.plot([], [], 'o-', label='Laser Angle')

        im34, = a1.plot([], [], 'o-.', label='Laser Angle - (R4H1)')
        im35, = a1.plot([], [], 'o-', label='Laser Angle - (R4H2)')
        im36, = a1.plot([], [], 'o-', label='Laser Angle - (R4H3)')
        im37, = a1.plot([], [], 'o-', label='Laser Angle - (R4H4)')
        im38, = a2.plot([], [], 'o-', label='Laser Angle')
        im39, = a2.plot([], [], 'o-', label='Laser Angle')
        im40, = a2.plot([], [], 'o-', label='Laser Angle')
        im41, = a2.plot([], [], 'o-', label='Laser Angle')

        # Statistical Feed -----------------------------------------[]
        a3.text(0.466, 0.945, 'Performance Feed - LA', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        a3.add_patch(rect1)
        a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)---------------------
        a3.text(0.145, 0.804, lalabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.658, '#Pp Value', fontsize=24, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.650, 0.820, 'Ring ' + lalabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        a3.text(0.145, 0.403, laPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=22, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring ' + laPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        # -------------------------------------
        a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ----- Pipe Position and SMC Status -----
        a3.text(0.080, 0.090, 'Pipe Position: ' + pPos + '    Processing Layer #' + layer, fontsize=12, ha='left',
                transform=a3.transAxes)
        a3.text(0.080, 0.036, 'SMC Status: ' + eSMC, fontsize=12, ha='left', transform=a3.transAxes)

        # ---------------- EXECUTE SYNCHRONOUS METHOD -----------------------------#
        def synchronousLA(laS, laTy, fetchT):
            fetch_no = str(fetchT)  # entry value in string sql syntax

            # Obtain Volatile Data from PLC Host Server ---------------------------[]
            if not inUseAlready:  # Load CommsPlc class once
                import CommsSql as q
                q.DAQ_connect(1, 0)
            else:
                con_a, con_b = conn.cursor(), conn.cursor()

            # Evaluate conditions for SQL Data Fetch ------------------------------[A]
            """
            Load watchdog function with synchronous function every seconds
            """
            # Initialise RT variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard  # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                if UsePLC_DBS:                               # Not Using PLC Data
                    import plcArrayRLmethodLA as sla         # DrLabs optimization method

                    inProgress = True                        # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve MSC from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    # Either of the 2 combo variables are assigned to trigger routine pause
                    if keyboard.is_pressed("ctrl") or not msctcp == 315 and not sysRun and not inProgress:
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            # play(error)                            # Pause mode with audible Alert
                            print("\nVisualization in Paused Mode...")

                    else:
                        autoSpcPause = False
                        print("Visualization in Real-time Mode...")
                        # Allow selective runtime parameter selection on production critical process
                        laDta = sla.plcExec(T1, laS, laTy, fetch_no)
                        laDtb = 0

                else:
                    import sqlArrayRLmethodLA as sla

                    inProgress = False  # False for Real-time mode
                    print('\nSynchronous controller activated...')

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve MSC from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    # Either of the 2 combo variables are assigned to trigger routine pause
                    if keyboard.is_pressed("ctrl") or not msctcp == 315 and not sysRun and not inProgress:
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            # play(error)                            # Pause mode with audible Alert
                            print("\nVisualization in Paused Mode...")
                        else:
                            autoSpcPause = False
                            print("Visualization in Real-time Mode...")
                    else:
                        # Get list of relevant SQL Tables using conn() ----------------[]
                        laDta, laDtb = sla.sqlExec(laS, laTy, con_a, con_b, T1, T2, fetchT)

                    # ------ Inhibit iteration ----------------------------------------------------------[]
                    """
                    # Set condition for halting real-time plots in watchdog class ---------------------
                    """
                    # TODO --- values for inhibiting the SQL processing
                    if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                        con_a.close()
                        con_b.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

            return laDta, laDtb

        # ================== End of synchronous Method ==========================
        def asynchronousLA(db_freq):
            timei = time.time()                                 # start timing the entire loop

            # Bistream Data Pooling Method ---------------------#
            laDta, laDtb = synchronousLA(laS, laTy, db_freq)    # data loading functions
            # --------------------------------------------------#

            if UsePLC_DBS == 1:
                import VarPLC_LA as la

                viz_cycle = 10
                # Call synchronous data function ---------------[]
                columns = qla.validCols(T1)                         # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(laDta, columns=columns)          # Include table data into python Dataframe
                LA = la.loadProcesValues(df1)                       # Join data values under dataframe

            else:
                import VarSQL_LA as la                              # load SQL variables column names | rfVarSQL

                viz_cycle = 150
                g1 = qla.validCols(T1)                              # Construct Data Column selSqlColumnsTFM.py
                d1 = pd.DataFrame(laDta, columns=g1)                # Import into python Dataframe

                g2 = qla.validCols(T2)
                d2 = pd.DataFrame(laDtb, columns=g2)

                # Concatenate all columns -----------[]
                df1 = pd.concat([d1, d2], axis=1)
                LA = la.loadProcesValues(df1)                       # Join data values under dataframe
            print('\nSQL Content', df1.head(10))
            print("Memory Usage:", df1.info(verbose=False))         # Check memory utilization

            # -------------------------------------------------------------------------------------[]
            # Plot X-Axis data points -------- X Plot
            im10.set_xdata(np.arange(db_freq))
            im11.set_xdata(np.arange(db_freq))
            im12.set_xdata(np.arange(db_freq))
            im13.set_xdata(np.arange(db_freq))
            im14.set_xdata(np.arange(db_freq))
            im15.set_xdata(np.arange(db_freq))
            im16.set_xdata(np.arange(db_freq))
            im17.set_xdata(np.arange(db_freq))
            im18.set_xdata(np.arange(db_freq))
            im19.set_xdata(np.arange(db_freq))
            im20.set_xdata(np.arange(db_freq))
            im21.set_xdata(np.arange(db_freq))
            im22.set_xdata(np.arange(db_freq))
            im23.set_xdata(np.arange(db_freq))
            im24.set_xdata(np.arange(db_freq))
            im25.set_xdata(np.arange(db_freq))
            # ------------------------------- S Plot
            im26.set_xdata(np.arange(db_freq))
            im27.set_xdata(np.arange(db_freq))
            im28.set_xdata(np.arange(db_freq))
            im29.set_xdata(np.arange(db_freq))
            im30.set_xdata(np.arange(db_freq))
            im31.set_xdata(np.arange(db_freq))
            im32.set_xdata(np.arange(db_freq))
            im33.set_xdata(np.arange(db_freq))
            im34.set_xdata(np.arange(db_freq))
            im35.set_xdata(np.arange(db_freq))
            im36.set_xdata(np.arange(db_freq))
            im37.set_xdata(np.arange(db_freq))
            im38.set_xdata(np.arange(db_freq))
            im39.set_xdata(np.arange(db_freq))
            im40.set_xdata(np.arange(db_freq))
            im41.set_xdata(np.arange(db_freq))

            # X Plot Y-Axis data points for XBar --------------------------------------------[  # Ring 1 ]
            im10.set_ydata((LA[0]).rolling(window=laS, min_periods=1).mean()[0:db_freq])  # head 1
            im11.set_ydata((LA[1]).rolling(window=laS, min_periods=1).mean()[0:db_freq])  # head 2
            im12.set_ydata((LA[2]).rolling(window=laS, min_periods=1).mean()[0:db_freq])  # head 3
            im13.set_ydata((LA[3]).rolling(window=laS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 1 ---------#
            mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(laHL, laS, 'LA')
            # ---------------------------------------#
            im14.set_ydata((LA[4]).rolling(window=laS, min_periods=1).mean()[0:db_freq])  # head 1
            im15.set_ydata((LA[5]).rolling(window=laS, min_periods=1).mean()[0:db_freq])  # head 2
            im16.set_ydata((LA[6]).rolling(window=laS, min_periods=1).mean()[0:db_freq])  # head 3
            im17.set_ydata((LA[7]).rolling(window=laS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 2 ---------#
            mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(laHL, laS, 'LA')
            # ---------------------------------------#
            im18.set_ydata((LA[8]).rolling(window=laS, min_periods=1).mean()[0:db_freq])  # head 1
            im19.set_ydata((LA[9]).rolling(window=laS, min_periods=1).mean()[0:db_freq])  # head 2
            im20.set_ydata((LA[10]).rolling(window=laS, min_periods=1).mean()[0:db_freq])  # head 3
            im21.set_ydata((LA[11]).rolling(window=laS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 3 ---------#
            mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(laHL, laS, 'LA')
            # ---------------------------------------#
            im22.set_ydata((LA[12]).rolling(window=laS, min_periods=1).mean()[0:db_freq])  # head 1
            im23.set_ydata((LA[13]).rolling(window=laS, min_periods=1).mean()[0:db_freq])  # head 2
            im24.set_ydata((LA[14]).rolling(window=laS, min_periods=1).mean()[0:db_freq])  # head 3
            im25.set_ydata((LA[15]).rolling(window=laS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 4 ---------#
            mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(laHL, laS, 'LA')
            # ---------------------------------------#
            # S Plot Y-Axis data points for StdDev ----------------------------------------
            im26.set_ydata((LA[0]).rolling(window=laS, min_periods=1).std()[0:db_freq])
            im27.set_ydata((LA[1]).rolling(window=laS, min_periods=1).std()[0:db_freq])
            im28.set_ydata((LA[2]).rolling(window=laS, min_periods=1).std()[0:db_freq])
            im29.set_ydata((LA[3]).rolling(window=laS, min_periods=1).std()[0:db_freq])

            im30.set_ydata((LA[4]).rolling(window=laS, min_periods=1).std()[0:db_freq])
            im31.set_ydata((LA[5]).rolling(window=laS, min_periods=1).std()[0:db_freq])
            im32.set_ydata((LA[6]).rolling(window=laS, min_periods=1).std()[0:db_freq])
            im33.set_ydata((LA[7]).rolling(window=laS, min_periods=1).std()[0:db_freq])

            im34.set_ydata((LA[8]).rolling(window=laS, min_periods=1).std()[0:db_freq])
            im35.set_ydata((LA[9]).rolling(window=laS, min_periods=1).std()[0:db_freq])
            im36.set_ydata((LA[10]).rolling(window=laS, min_periods=1).std()[0:db_freq])
            im37.set_ydata((LA[11]).rolling(window=laS, min_periods=1).std()[0:db_freq])

            im38.set_ydata((LA[12]).rolling(window=laS, min_periods=1).std()[0:db_freq])
            im39.set_ydata((LA[13]).rolling(window=laS, min_periods=1).std()[0:db_freq])
            im40.set_ydata((LA[14]).rolling(window=laS, min_periods=1).std()[0:db_freq])
            im41.set_ydata((LA[15]).rolling(window=laS, min_periods=1).std()[0:db_freq])

            # Compute entire Process Capability -----------#
            if not laHL:
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLb, ppT, pkT, xline, sline = tq.tAutoPerf(laS, mnA, mnB,
                                                                                                      mnC, mnD, sdA,
                                                                                                      sdB, sdC, sdD)
            else:
                xline, sline = laMean, laDev
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLba, ppT, pkT = tq.tManualPerf(mnA, mnB, mnC, mnD, sdA, sdB,
                                                                                           sdC, sdD, laUSL, laLSL,
                                                                                           laUCL,
                                                                                           laLCL)

            # # Declare Plots alaributes --------------------------------------------------------[]
            # XBar Mean Plot
            a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
            a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')            # 3 Sigma span (Purple)
            a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')            # grey area
            a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minLP, sBar_maxLP -------[]
            # Define Legend's Alaributes  ----
            a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
            a2.axhspan(sLCLla, sUCLla, facecolor='#F9C0FD', edgecolor='#F9C0FD')        # 1 Sigma Span
            a2.axhspan(sUCLla, sBar_maxLA, facecolor='#CCCCFF', edgecolor='#CCCCFF')    # 1 Sigma above the Mean
            a2.axhspan(sBar_minLA, sLCLla, facecolor='#CCCCFF', edgecolor='#CCCCFF')

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
                a2.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a1.set_xlim(0, window_Xmax)
                a2.set_xlim(0, window_Xmax)

            # Set trip line for individual time-series plot -----------------------------------[R1]
            import triggerModule as sigma
            sigma.trigViolations(a1, UsePLC_DBS, 'LA', YScale_minLA, YScale_maxLA, xucT, xlcT, xusT, xlsT, mnT, sdT)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousLA, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

# ---------------------------------------------------------------------------------------------[Roller Force]
class rollerForceTabb(ttk.Frame):
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        # Load Quality Historical Values -----------[]
        if pRecipe == 'DNV':
            rfS, rfTy, eolS, eopS, rfHL, rfAL, rfFO, rfP1, rfP2, rfP3, rfP4, rfP5 = dnv.decryptpProcessLim(pWON, 'RF')
        else:
            rfS, rfTy, eolS, eopS, rfHL, rfAL, rfFO, rfP1, rfP2, rfP3, rfP4, rfP5 = mgm.decryptpProcessLim(pWON, 'RF')
        # Break down each element to useful list ---------------[Tape Temperature]

        if rfHL and rfP1 and rfP2 and rfP3 and rfP4 and rfP5:  #
            rfPerf = '$Pp_{k' + str(rfS) + '}$'  # Using estimated or historical Mean
            rflabel = 'Pp'
            # -------------------------------
            One = rfP1.split(',')                   # split into list elements
            Two = rfP2.split(',')
            Thr = rfP3.split(',')
            For = rfP4.split(',')
            Fiv = rfP5.split(',')
            # -------------------------------
            dTape1 = One[1].strip("' ")                 # defined Tape Width
            dTape2 = Two[1].strip("' ")                 # defined Tape Width
            dTape3 = Thr[1].strip("' ")                 # defined Tape Width
            dTape4 = For[1].strip("' ")                 # defined Tape Width
            dTape5 = Fiv[1].strip("' ")                 # defined Tape Width
            # --------------------------------
            dLayer1 = One[10].strip("' ")               # Defined Tape Layer
            dLayer2 = Two[10].strip("' ")
            dLayer3 = Thr[10].strip("' ")
            dLayer4 = For[10].strip("' ")
            dLayer5 = Fiv[10].strip("' ")
            # Load historical limits for the process----#
            if cpLayerNo == 1:                          # '22mm'|'18mm',  1-40 | 41+ TODO
                rfUCL = float(One[2].strip("' "))       # Strip out the element of the list
                rfLCL = float(One[3].strip("' "))
                rfMean = float(One[4].strip("' "))
                rfDev = float(One[5].strip("' "))
                # --------------------------------
                sUCLrf = float(One[6].strip("' "))
                sLCLrf = float(One[7].strip("' "))
                # --------------------------------
                rfUSL = (rfUCL - rfMean) / 3 * 6
                rfLSL = (rfMean - rfLCL) / 3 * 6
                # --------------------------------
            elif cpTapeW == dTape2 and cpLayerNo == 2:
                rfUCL = float(Two[2].strip("' "))       # Strip out the element of the list
                rfLCL = float(Two[3].strip("' "))
                rfMean = float(Two[4].strip("' "))
                rfDev = float(Two[5].strip("' "))
                # --------------------------------
                sUCLrf = float(Two[6].strip("' "))
                sLCLrf = float(Two[7].strip("' "))
                # --------------------------------
                rfUSL = (rfUCL - rfMean) / 3 * 6
                rfLSL = (rfMean - rfLCL) / 3 * 6
            elif cpTapeW == dTape3 and cpLayerNo == range(3, 40):
                rfUCL = float(Thr[2].strip("' "))       # Strip out the element of the list
                rfLCL = float(Thr[3].strip("' "))
                rfMean = float(Thr[4].strip("' "))
                rfDev = float(Thr[5].strip("' "))
                # --------------------------------
                sUCLrf = float(Thr[6].strip("' "))
                sLCLrf = float(Thr[7].strip("' "))
                # --------------------------------
                rfUSL = (rfUCL - rfMean) / 3 * 6
                rfLSL = (rfMean - rfLCL) / 3 * 6
            elif cpTapeW == dTape4 and cpLayerNo == 41:
                rfUCL = float(For[2].strip("' "))       # Strip out the element of the list
                rfLCL = float(For[3].strip("' "))
                rfMean = float(For[4].strip("' "))
                rfDev = float(For[5].strip("' "))
                # --------------------------------
                sUCLrf = float(For[6].strip("' "))
                sLCLrf = float(For[7].strip("' "))
                # --------------------------------
                rfUSL = (rfUCL - rfMean) / 3 * 6
                rfLSL = (rfMean - rfLCL) / 3 * 6
            else:
                rfUCL = float(Fiv[2].strip("' "))       # Strip out the element of the list
                rfLCL = float(Fiv[3].strip("' "))
                rfMean = float(Fiv[4].strip("' "))
                rfDev = float(Fiv[5].strip("' "))
                # --------------------------------
                sUCLrf = float(Fiv[6].strip("' "))
                sLCLrf = float(Fiv[7].strip("' "))
                # --------------------------------
                rfUSL = (rfUCL - rfMean) / 3 * 6
                rfLSL = (rfMean - rfLCL) / 3 * 6
                # -------------------------------
        else:  # Computes Shewhart constants (Automatic Limits)
            rfUCL = 0
            rfLCL = 0
            rfMean = 0
            rfDev = 0
            sUCLrf = 0
            sLCLrf = 0
            rfUSL = 0
            rfLSL = 0
            rfPerf = '$Cp_{k' + str(rfS) + '}$'  # Using Automatic group Mean
            rflabel = 'Cp'

        # ------ [End of Historical abstraction -------]

        label = ttk.Label(self, text='[' + rType + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Define Axes ---------------------#
        f = Figure(figsize=(pMtX, 8), dpi=100)
        f.subplots_adjust(left=0.022, bottom=0.05, right=0.993, top=0.967, wspace=0.18, hspace=0.174)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 4, (1, 3))   # X Bar Plot
        a2 = f.add_subplot(2, 4, (5, 7))   # S Bar Plo
        a3 = f.add_subplot(2, 4, (4, 8))   # Performance Feeed

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minRF, YScale_maxRF = 10, 500                        # Roller Force
        sBar_minRF, sBar_maxRF = 10, 250                            # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (int(rfS) + 3)             # windows view = visible data points

        # ----------------------------------------------------------#
        # Real-Time Parameter according to updated requirements ----# 28/Feb/2025
        if rType == 1:
            T1 = SPC_RF
        else:
            T1 = 'RF1_' + pWON        # Laser Power
            T2 = 'RF2_' + pWON
        # ----------------------------------------------------------#

        # Initialise runtime limits
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        a1.set_title('Roller Force [XBar Plot]', fontsize=12, fontweight='bold')
        a2.set_title('Roller Force [S Plot]', fontsize=12, fontweight='bold')
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a1.legend(loc='upper right', title='Roller Force (N.m)')
        a2.legend(loc='upper right', title='Sigma curve')

        # ----------------------------------------------------------#
        a1.set_ylim([YScale_minRF, YScale_maxRF], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        a2.set_ylim([sBar_minRF, sBar_maxRF], auto=True)
        a2.set_xlim([window_Xmin, window_Xmax])

        # ---------------------------------------------------------[]
        a3.cla()
        a3.get_yaxis().set_visible(False)
        a3.get_xaxis().set_visible(False)

        # ---------------------------------------------------------[]
        # Define Plot area and axes -
        # ---------------------------------------------------------#
        im10, = a1.plot([], [], 'o-', label='Roller Force - (R1H1)')
        im11, = a1.plot([], [], 'o-', label='Roller Force - (R1H2)')
        im12, = a1.plot([], [], 'o-', label='Roller Force - (R1H3)')
        im13, = a1.plot([], [], 'o-', label='Roller Force - (R1H4)')
        im14, = a2.plot([], [], 'o-', label='Roller Force')
        im15, = a2.plot([], [], 'o-', label='Roller Force')
        im16, = a2.plot([], [], 'o-', label='Roller Force')
        im17, = a2.plot([], [], 'o-', label='Roller Force')

        im18, = a1.plot([], [], 'o-', label='Roller Force - (R2H1)')
        im19, = a1.plot([], [], 'o-', label='Roller Force - (R2H2)')
        im20, = a1.plot([], [], 'o-', label='Roller Force - (R2H3)')
        im21, = a1.plot([], [], 'o-', label='Roller Force - (R2H4)')
        im22, = a2.plot([], [], 'o-', label='Roller Force')
        im23, = a2.plot([], [], 'o-', label='Roller Force')
        im24, = a2.plot([], [], 'o-', label='Roller Force')
        im25, = a2.plot([], [], 'o-', label='Roller Force')

        im26, = a1.plot([], [], 'o-', label='Roller Force - (R3H1)')
        im27, = a1.plot([], [], 'o-', label='Roller Force - (R3H2)')
        im28, = a1.plot([], [], 'o-', label='Roller Force - (R3H3)')
        im29, = a1.plot([], [], 'o-', label='Roller Force - (R3H4)')
        im30, = a2.plot([], [], 'o-', label='Roller Force')
        im31, = a2.plot([], [], 'o-', label='Roller Force')
        im32, = a2.plot([], [], 'o-', label='Roller Force')
        im33, = a2.plot([], [], 'o-', label='Roller Force')

        im34, = a1.plot([], [], 'o-', label='Roller Force - (R4H1)')
        im35, = a1.plot([], [], 'o-', label='Roller Force - (R4H2)')
        im36, = a1.plot([], [], 'o-', label='Roller Force - (R4H3)')
        im37, = a1.plot([], [], 'o-', label='Roller Force - (R4H4)')
        im38, = a2.plot([], [], 'o-', label='Roller Force')
        im39, = a2.plot([], [], 'o-', label='Roller Force')
        im40, = a2.plot([], [], 'o-', label='Roller Force')
        im41, = a2.plot([], [], 'o-', label='Roller Force')
        # --------------- Ramp Profile ---------------------------[ Important ]
        # im42, = a2.plot([], [], 'o-', label='Cumulated Ramp')
        # im43, = a2.plot([], [], 'o-', label='Nominal Ramp')

        # Statistical Feed -----------------------------------------[]
        a3.text(0.466, 0.945, 'Performance Feed - RF', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        a3.add_patch(rect1)
        a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)---------------------
        a3.text(0.145, 0.804, rflabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.658, '#Pp Value', fontsize=24, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.650, 0.820, 'Ring ' + rflabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        a3.text(0.145, 0.403, rfPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=22, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring ' + rfPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        # -------------------------------------
        a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ----- Pipe Position and SMC Status -----
        a3.text(0.080, 0.090, 'Pipe Position: ' + pPos + '    Processing Layer #' + layer, fontsize=12, ha='left',
                transform=a3.transAxes)
        a3.text(0.080, 0.036, 'SMC Status: ' + eSMC, fontsize=12, ha='left', transform=a3.transAxes)

        # ---------------- EXECUTE SYNCHRONOUS METHOD -----------------------------#
        def synchronousRF(rfS, rfTy, fetchT):
            fetch_no = str(fetchT)  # entry value in string sql syntax

            # Obtain Volatile Data from PLC Host Server ---------------------------[]
            if not inUseAlready:  # Load CommsPlc class once
                import CommsPlc as q
                q.DAQ_connect(1, 0)
            else:
                con_a, con_b = conn.cursor(), conn.cursor()

            # Evaluate conditions for SQL Data Fetch ------------------------------[A]
            """
            Load watchdog function with synchronous function every seconds
            """
            # Initialise RT variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard                                 # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                if UsePLC_DBS:                              # Not Using PLC Data
                    import plcArrayRLmethodRF as srf         # DrLabs optimization method

                    inProgress = True                       # True for RetroPlay mode
                    print('\nSynchronous controller activated...')

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve MSC from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    # Either of the 2 combo variables are assigned to trigger routine pause
                    if keyboard.is_pressed("ctrl") or not msctcp == 315 and not sysRun and not inProgress:
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            # play(error)                            # Pause mode with audible Alert
                            print("\nVisualization in Paused Mode...")
                    else:
                        autoSpcPause = False
                        procID = 'RF'
                        print("Visualization in Play Mode...")
                        rfDta = srf.plcExec(procID, rfS, rfTy, fetch_no)
                        rfDtb = 0

                else:
                    import sqlArrayRLmethodRF as srf  # DrLabs optimization method

                    inProgress = True  # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve M.State from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    if keyboard.is_pressed("Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            print("\nVisualization in Paused Mode...")
                        else:
                            autoSpcPause = False
                            print("Visualization in Real-time Mode...")
                    else:
                        # Get list of relevant SQL Tables using conn() --------------------[]
                        rfDta, rfDtb = srf.sqlExec(rfS, rfTy, con_a, con_b, T1, T2, fetchT)

                    # ------ Inhibit iteration ----------------------------------------------------------[]
                    """
                    # Set condition for halting real-time plots in watchdog class ---------------------
                    """
                    # TODO --- values for inhibiting the SQL processing
                    if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                        con_a.close()
                        con_b.close()

                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

            return rfDta, rfDtb

        # -------------------------------------[A]

        # ================== End of synchronous Method ==========================
        def asynchronousRF(db_freq):
            timei = time.time()         # start timing the entire loop

            # Bistream Data Pooling Method ---------------------#
            rfDta, rfDtb = synchronousRF(rfS, rfTy, db_freq)    # data loading functions
            # --------------------------------------------------#

            if UsePLC_DBS == 1:
                import VarPLCrf as rf

                viz_cycle = 10
                # Call synchronous data function ---------------[]
                columns = qrf.validCols(T1)                     # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(rfDta, columns=columns)      # Include table data into python Dataframe
                RF = rf.loadProcesValues(df1)                   # Join data values under dataframe

            else:
                import VarSQL_RF as rf                           # load SQL variables column names | rfVarSQL

                viz_cycle = 150
                g1 = qrf.validCols(T1)                           # Construct Data Column selSqlColumnsTFM.py
                d1 = pd.DataFrame(rfDta, columns=g1)             # Import into python Dataframe
                g2 = qrf.validCols(T1)                           # Construct Data Column selSqlColumnsTFM.py
                d2 = pd.DataFrame(rfDtb, columns=g2)

                # Concatenate all columns -----------------------[]
                df1 = pd.concat([d1, d2], axis=1)
                RF = rf.loadProcesValues(df1)                       # Join data values under dataframe
            print('\nSQL Content', df1.head(10))
            print("Memory Usage:", df1.info(verbose=False))         # Check memory utilization

            # -------------------------------------------------------------------------------------[]
            # Plot X-Axis data points -------- X Plot
            im10.set_xdata(np.arange(db_freq))
            im11.set_xdata(np.arange(db_freq))
            im12.set_xdata(np.arange(db_freq))
            im13.set_xdata(np.arange(db_freq))
            im14.set_xdata(np.arange(db_freq))
            im15.set_xdata(np.arange(db_freq))
            im16.set_xdata(np.arange(db_freq))
            im17.set_xdata(np.arange(db_freq))
            im18.set_xdata(np.arange(db_freq))
            im19.set_xdata(np.arange(db_freq))
            im20.set_xdata(np.arange(db_freq))
            im21.set_xdata(np.arange(db_freq))
            im22.set_xdata(np.arange(db_freq))
            im23.set_xdata(np.arange(db_freq))
            im24.set_xdata(np.arange(db_freq))
            im25.set_xdata(np.arange(db_freq))
            # ------------------------------- S Plot
            im26.set_xdata(np.arange(db_freq))
            im27.set_xdata(np.arange(db_freq))
            im28.set_xdata(np.arange(db_freq))
            im29.set_xdata(np.arange(db_freq))
            im30.set_xdata(np.arange(db_freq))
            im31.set_xdata(np.arange(db_freq))
            im32.set_xdata(np.arange(db_freq))
            im33.set_xdata(np.arange(db_freq))
            im34.set_xdata(np.arange(db_freq))
            im35.set_xdata(np.arange(db_freq))
            im36.set_xdata(np.arange(db_freq))
            im37.set_xdata(np.arange(db_freq))
            im38.set_xdata(np.arange(db_freq))
            im39.set_xdata(np.arange(db_freq))
            im40.set_xdata(np.arange(db_freq))
            im41.set_xdata(np.arange(db_freq))

            # X Plot Y-Axis data points for XBar --------------------------------------------[  # Ring 1 ]
            im10.set_ydata((RF[0]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 1
            im11.set_ydata((RF[1]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 2
            im12.set_ydata((RF[2]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 3
            im13.set_ydata((RF[3]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 1 ---------#
            mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(rfHL, rfS, 'RF')
            # ---------------------------------------#
            im14.set_ydata((RF[4]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 1
            im15.set_ydata((RF[5]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 2
            im16.set_ydata((RF[6]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 3
            im17.set_ydata((RF[7]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 2 ---------#
            mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(rfHL, rfS, 'RF')
            # ---------------------------------------#
            im18.set_ydata((RF[8]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 1
            im19.set_ydata((RF[9]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 2
            im20.set_ydata((RF[10]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 3
            im21.set_ydata((RF[11]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 3 ---------#
            mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(rfHL, rfS, 'RF')
            # ---------------------------------------#
            im22.set_ydata((RF[12]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 1
            im23.set_ydata((RF[13]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 2
            im24.set_ydata((RF[14]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 3
            im25.set_ydata((RF[15]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 4 ---------#
            mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(rfHL, rfS, 'RF')
            # ---------------------------------------#
            # S Plot Y-Axis data points for StdDev ----------------------------------------
            im26.set_ydata((RF[0]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im27.set_ydata((RF[1]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im28.set_ydata((RF[2]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im29.set_ydata((RF[3]).rolling(window=rfS, min_periods=1).std()[0:db_freq])

            im30.set_ydata((RF[4]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im31.set_ydata((RF[5]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im32.set_ydata((RF[6]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im33.set_ydata((RF[7]).rolling(window=rfS, min_periods=1).std()[0:db_freq])

            im34.set_ydata((RF[8]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im35.set_ydata((RF[9]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im36.set_ydata((RF[10]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im37.set_ydata((RF[11]).rolling(window=rfS, min_periods=1).std()[0:db_freq])

            im38.set_ydata((RF[12]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im39.set_ydata((RF[13]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im40.set_ydata((RF[14]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im41.set_ydata((RF[15]).rolling(window=rfS, min_periods=1).std()[0:db_freq])

            # Compute entire Process Capability -----------#
            if not rfHL:
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLb, ppT, pkT, xline, sline = tq.tAutoPerf(rfS, mnA, mnB,
                                                                                                      mnC, mnD, sdA,
                                                                                                      sdB, sdC, sdD)
            else:
                xline, sline = rfMean, rfDev
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLba, ppT, pkT = tq.tManualPerf(mnA, mnB, mnC, mnD, sdA, sdB,
                                                                                           sdC, sdD, rfUSL, rfLSL,
                                                                                           rfUCL,
                                                                                           rfLCL)

            # # Declare Plots attributes --------------------------------------------------------[]
            # XBar Mean Plot
            a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
            a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 3 Sigma span (Purple)
            a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minRF, sBar_maxRF -------[]
            # Define Legend's Attributes  ----
            a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
            a2.axhspan(sLCLrf, sUCLrf, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 1 Sigma Span
            a2.axhspan(sUCLrf, sBar_maxRF, facecolor='#CCCCFF', edgecolor='#CCCCFF')  # 1 Sigma above the Mean
            a2.axhspan(sBar_minRF, sLCLrf, facecolor='#CCCCFF', edgecolor='#CCCCFF')

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
                a2.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a1.set_xlim(0, window_Xmax)
                a2.set_xlim(0, window_Xmax)

            # Set trip line for individual time-series plot -----------------------------------[R1]
            import triggerModule as sigma
            sigma.trigViolations(a1, UsePLC_DBS, 'RF', YScale_minRF, YScale_maxRF, xucT, xlcT, xusT, xlsT, mnT, sdT)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousRF, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

# -----------------------------------------------------------------------------------------[Tape Temperature]
class tapeTempTabb(ttk.Frame):  # -- Defines the tabbed region for QA param - Tape Temperature --[]
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""

        # Load Quality Historical Values -----------[]
        if pRecipe == 'DNV':
            import qParamsHL_DNV as qp
        else:
            import qParamsHL_MGM as qp
        # ------------------------------------------[]
        ttS, ttTy, eolS, eopS, ttHL, ttAL, ttFO, ttP1, ttP2, ttP3, ttP4, ttP5 = qp.decryptpProcessLim(pWON, 'TT')
        # Break down each element to useful list ---------------[Tape Temperature]

        if ttHL and ttP1 and ttP2 and ttP3 and ttP4 and ttP5:  #
            ttPerf = '$Pp_{k' + str(ttS) + '}$'      # Using estimated or historical Mean
            ttlabel = 'Pp'
            # -------------------------------
            One = ttP1.split(',')                   # split into list elements
            Two = ttP2.split(',')
            Thr = ttP3.split(',')
            For = ttP4.split(',')
            Fiv = ttP5.split(',')
            # -------------------------------
            dTape1 = One[1].strip("' ")                 # defined Tape Width
            dTape2 = Two[1].strip("' ")                 # defined Tape Width
            dTape3 = Thr[1].strip("' ")                 # defined Tape Width
            dTape4 = For[1].strip("' ")                 # defined Tape Width
            dTape5 = Fiv[1].strip("' ")                 # defined Tape Width
            # --------------------------------
            dLayer1 = One[10].strip("' ")               # Defined Tape Layer
            dLayer2 = Two[10].strip("' ")
            dLayer3 = Thr[10].strip("' ")
            dLayer4 = For[10].strip("' ")
            dLayer5 = Fiv[10].strip("' ")
            # Load historical limits for the process----#
            if cpLayerNo == 1:                          # '22mm'|'18mm',  1-40 | 41+ TODO
                ttUCL = float(One[2].strip("' "))       # Strip out the element of the list
                ttLCL = float(One[3].strip("' "))
                ttMean = float(One[4].strip("' "))
                ttDev = float(One[5].strip("' "))
                # --------------------------------
                sUCLtt = float(One[6].strip("' "))
                sLCLtt = float(One[7].strip("' "))
                # --------------------------------
                ttUSL = (ttUCL - ttMean) / 3 * 6
                ttLSL = (ttMean - ttLCL) / 3 * 6
                # --------------------------------
            elif cpTapeW == dTape2 and cpLayerNo == 2:
                ttUCL = float(Two[2].strip("' "))       # Strip out the element of the list
                ttLCL = float(Two[3].strip("' "))
                ttMean = float(Two[4].strip("' "))
                ttDev = float(Two[5].strip("' "))
                # --------------------------------
                sUCLtt = float(Two[6].strip("' "))
                sLCLtt = float(Two[7].strip("' "))
                # --------------------------------
                ttUSL = (ttUCL - ttMean) / 3 * 6
                ttLSL = (ttMean - ttLCL) / 3 * 6
            elif cpTapeW == dTape3 and cpLayerNo == range(3, 40):
                ttUCL = float(Thr[2].strip("' "))       # Strip out the element of the list
                ttLCL = float(Thr[3].strip("' "))
                ttMean = float(Thr[4].strip("' "))
                ttDev = float(Thr[5].strip("' "))
                # --------------------------------
                sUCLtt = float(Thr[6].strip("' "))
                sLCLtt = float(Thr[7].strip("' "))
                # --------------------------------
                ttUSL = (ttUCL - ttMean) / 3 * 6
                ttLSL = (ttMean - ttLCL) / 3 * 6
            elif cpTapeW == dTape4 and cpLayerNo == 41:
                ttUCL = float(For[2].strip("' "))       # Strip out the element of the list
                ttLCL = float(For[3].strip("' "))
                ttMean = float(For[4].strip("' "))
                ttDev = float(For[5].strip("' "))
                # --------------------------------
                sUCLtt = float(For[6].strip("' "))
                sLCLtt = float(For[7].strip("' "))
                # --------------------------------
                ttUSL = (ttUCL - ttMean) / 3 * 6
                ttLSL = (ttMean - ttLCL) / 3 * 6
            else:
                ttUCL = float(Fiv[2].strip("' "))       # Strip out the element of the list
                ttLCL = float(Fiv[3].strip("' "))
                ttMean = float(Fiv[4].strip("' "))
                ttDev = float(Fiv[5].strip("' "))
                # --------------------------------
                sUCLtt = float(Fiv[6].strip("' "))
                sLCLtt = float(Fiv[7].strip("' "))
                # --------------------------------
                ttUSL = (ttUCL - ttMean) / 3 * 6
                ttLSL = (ttMean - ttLCL) / 3 * 6
                # -------------------------------
        else:  # Computes Shewhart constants (Automatic Limits)
            ttUCL = 0
            ttLCL = 0
            ttMean = 0
            ttDev = 0
            sUCLtt = 0
            sLCLtt = 0
            ttUSL = 0
            ttLSL = 0
            ttPerf = '$Cp_{k' + str(ttS) + '}$'  # Using Automatic group Mean
            ttlabel = 'Cp'

        # ------------------------------------[End of Tape Temperature Abstraction]

        label = ttk.Label(self, text='[' + rType + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Define Axes ---------------------#
        f = Figure(figsize=(pMtX, 8), dpi=100)    # 27
        f.subplots_adjust(left=0.029, bottom=0.05, right=0.983, top=0.967, wspace=0.18, hspace=0.174)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 6, (1, 3))                            # xbar plot
        a2 = f.add_subplot(2, 6, (7, 9))                            # s bar plot
        a3 = f.add_subplot(2, 6, (4, 12))                           # void mapping profile

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends

        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minTT, YScale_maxTT = ttLSL - 8.5, ttUSL + 8.5       # Tape Temperature
        sBar_minTT, sBar_maxTT = sLCLtt - 80, sUCLtt + 80           # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (int(ttS) + 3)             # windows view = visible data points
        # ----------------------------------------------------------#
        YScale_minRM, YScale_maxRM = 0, pExLayer                    # Valid layer number
        window_XminRM, window_XmaxRM = 0, pLength                   # Get details from SCADA PIpe Recipe TODO[1]

        # Real-Time Parameter according to updated requirements ----# 07/Feb/2025
        if rType == 1:
            # PLC Data - for Live Production Analysis
            T1 = SPC_TT
        else:
            # SQL Data --------------------#
            T1 = 'TT1_' + pWON             # Tape Temperature
            T2 = 'TT2_' + pWON
        T3 = 'RM_' + pWON                  # Ramp Profile Mapping from SQL table Only
        # ----------------------------------------------------------#

        # Initialise runtime limits --------------------------------#
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")

        a1.set_title('Tape Temperature [XBar]', fontsize=12, fontweight='bold')
        a2.set_title('Tape Temperature [SDev]', fontsize=12, fontweight='bold')
        a3.set_title('Ramp Mapping Profile - [RMP]', fontsize=12, fontweight='bold')
        a3.set_facecolor("blue")        # set background color to blue
        zoom_factory(a3)                # Allow plot's image  zooming

        a3.set_ylabel("2D - Staked Layer Ramp Mapping")
        a3.set_xlabel("Sample Distance (mt)")

        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a3.grid(color="0.5", linestyle='-', linewidth=0.5)

        a1.legend(loc='upper right', title='Tape Temperature')
        a2.legend(loc='upper right', title='Sigma Plot')
        a3.legend(loc='upper right', title='Temp Ramp Profile')
        # ----------------------------------------------------------#
        a1.set_ylim([YScale_minTT, YScale_maxTT], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        a2.set_ylim([sBar_minTT, sBar_maxTT], auto=True)
        a2.set_xlim([window_Xmin, window_Xmax])
        # --------------------------------------------------------[]
        a3.set_ylim([YScale_minRM, YScale_maxRM], auto=True)
        a3.set_xlim([window_XminRM, window_XmaxRM])

        # --------------------------------------------------------[]
        # Define Plot area and axes -
        # ---------------------------------------------------------#
        im10, = a1.plot([], [], 'o-', label='Tape Temp - (R1H1)')
        im11, = a1.plot([], [], 'o-', label='Tape Temp - (R1H2)')
        im12, = a1.plot([], [], 'o-', label='Tape Temp - (R1H3)')
        im13, = a1.plot([], [], 'o-', label='Tape Temp - (R1H4)')
        im14, = a2.plot([], [], 'o-', label='Tape Temp')
        im15, = a2.plot([], [], 'o-', label='Tape Temp')
        im16, = a2.plot([], [], 'o-', label='Tape Temp')
        im17, = a2.plot([], [], 'o-', label='Tape Temp')

        im18, = a1.plot([], [], 'o-', label='Tape Temp - (R2H1)')
        im19, = a1.plot([], [], 'o-', label='Tape Temp - (R2H2)')
        im20, = a1.plot([], [], 'o-', label='Tape Temp - (R2H3)')
        im21, = a1.plot([], [], 'o-', label='Tape Temp - (R2H4)')
        im22, = a2.plot([], [], 'o-', label='Tape Temp')
        im23, = a2.plot([], [], 'o-', label='Tape Temp')
        im24, = a2.plot([], [], 'o-', label='Tape Temp')
        im25, = a2.plot([], [], 'o-', label='Tape Temp')

        im26, = a1.plot([], [], 'o-', label='Tape Temp - (R3H1)')
        im27, = a1.plot([], [], 'o-', label='Tape Temp - (R3H2)')
        im28, = a1.plot([], [], 'o-', label='Tape Temp - (R3H3)')
        im29, = a1.plot([], [], 'o-', label='Tape Temp - (R3H4)')
        im30, = a2.plot([], [], 'o-', label='Tape Temp')
        im31, = a2.plot([], [], 'o-', label='Tape Temp')
        im32, = a2.plot([], [], 'o-', label='Tape Temp')
        im33, = a2.plot([], [], 'o-', label='Tape Temp')

        im34, = a1.plot([], [], 'o-', label='Tape Temp - (R4H1)')
        im35, = a1.plot([], [], 'o-', label='Tape Temp - (R4H2)')
        im36, = a1.plot([], [], 'o-', label='Tape Temp - (R4H3)')
        im37, = a1.plot([], [], 'o-', label='Tape Temp - (R4H4)')
        im38, = a2.plot([], [], 'o-', label='Tape Temp')
        im39, = a2.plot([], [], 'o-', label='Tape Temp')
        im40, = a2.plot([], [], 'o-', label='Tape Temp')
        im41, = a2.plot([], [], 'o-', label='Tape Temp')
        # --------------- Temperature Ramp Profile -------------------[ Important ]
        im42 = a3.plot([], [], marker='|', color='w', linestyle='', label='Ring 1 Ramp')
        im43 = a3.plot([], [], marker='|', color='w', linestyle='', label='Ring 2 Ramp')
        im44 = a3.plot([], [], marker='|', color='w', linestyle='', label='Ring 3 Ramp')
        im45 = a3.plot([], [], marker='|', color='w', linestyle='', label='Ring 4 Ramp')

        # ---------------- EXECUTE SYNCHRONOUS METHOD -----------------------------#

        def synchronousTT(ttS, ttTy, fetchT):
            fetch_no = str(fetchT)                        # entry value in string sql syntax

            # Obtain Volatile Data from PLC Host Server ---------------------------[]
            if not inUseAlready:                         # Load Comm Plc class once
                import CommsSql as q
                cont_A = q.DAQ_connect(1, 0)             # Connect PLC for real-time data
            else:
                con_A, con_B = conn.cursor()

            # Evaluate conditions for SQL Data Fetch ------------------------------[A]
            """
            Load watchdog function with synchronous function every seconds
            """

            # Initialise RT variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard  # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                # print('Indefinite looping...')
                # Using PLC Data ----------------#
                if UsePLC_DBS:
                    import plcArrayRLmethodTT as pdA
                    import sqlArrayRLmethodRM as srm

                    inProgress = True                               # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve M.State from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    if keyboard.is_pressed(
                            "Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:  # Terminate file-fetch
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            print("\nVisualization in Paused Mode...")
                    else:
                        autoSpcPause = False
                        print("Visualization in Real-time Mode...")
                        # Get list of relevant PLC Tables using conn() --------------------[]
                        ttDta = pdA.plcExec(T1, ttS, ttTy, fetch_no)
                        ttDtb = 0
                        rmDta = srm.sqlExec(ttS, ttTy, con_B, T3, fetchT)

                else:
                    import sqlArrayRLmethodTT as ptt
                    import sqlArrayRLmethodRM as srm

                    inProgress = False  # False for Real-time mode
                    print('\nSynchronous controller activated...')
                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve MSC from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    # Either of the 2 combo variables are assigned to trigger routine pause
                    if keyboard.is_pressed("ctrl") or not msctcp == 315 and not sysRun and not inProgress:
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            # play(error)                                               # Pause mode with audible Alert
                            print("\nVisualization in Paused Mode...")
                        else:
                            autoSpcPause = False
                        print("Visualization in Play Mode...")

                    else:

                        ttDta, ttDtb = ptt.sqlExec(ttS, ttTy, con_A, con_B, T1, T2, fetchT)
                        rmDta = srm.sqlExec(ttS, ttTy, con_B, T3, fetchT)
                        print("Visualization in Play Mode...")
                    print('\nUpdating....')

                    # ------ Inhibit iteration ----------------------------------------------------------[]
                    """
                    # Set condition for halting real-time plots in watchdog class -----------------------[]
                    """
                    # TODO --- values for inhibiting the SQL processing
                    if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                        con_A.close()
                        con_B.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

            return ttDta, ttDtb, rmDta


        # ================== End of synchronous Method ==========================--------------------[]
        def asynchronousTT(db_freq):
            timei = time.time()         # start timing the entire loop

            # Bi-stream Data Pooling Method ----------------#
            ttDta, ttDtb, rmDta = synchronousTT(ttS, ttTy, db_freq)              # data loading functions
            # ----------------------------------------------#

            if UsePLC_DBS == 1:
                import VarPLC_TT as tt

                viz_cycle = 10
                stream = 1                                  # PLC Stream
                # Call synchronous data PLC function ------[A]
                g1 = qtt.validCols(T1, pWON)                # Load PLC-dB [SPC_TT]
                df1 = pd.DataFrame(ttDta, columns=g1)       # Include table data into python Dataframe
                # ------------------------------------------#
                TT = tt.loadProcesValues(df1, stream)       # Join data values under dataframe

            else:
                import VarSQL_TT as tt
                viz_cycle = 150
                stream = 2                                 # SQL Stream
                g1 = qtt.validCols(T1, pWON)               # Load TT1_
                d1 = pd.DataFrame(ttDta, columns=g1)       # Include table data into python Dataframe
                g2 = qtt.validCols(T2, pWON)               # Load TT2
                d2 = pd.DataFrame(ttDtb, columns=g2)

                # Concatenate all columns -----------[]
                df1 = pd.concat([d1, d2], axis=1)
                TT = tt.loadProcesValues(df1, stream)       # Join data values under dataframe
            # ----------------------------------------------#
            import VarSQL_RM as rm                          # load SQL variables column names | rfVarSQL

            viz_cycle = 150
            g1 = qrm.validCols(T3)                          # Construct Data Column selSqlColumnsTFM.py
            df1 = pd.DataFrame(rmDta, columns=g1)           # Import into python Dataframe
            RM = rm.loadProcesValues(df1)                   # Join data values under dataframe
            print('\nSQL Content', df1.head(10))
            print("Memory Usage:", df1.info(verbose=False)) # Check memory utilization

            # -------------------------------------------------------------------------------------[]
            # Plot X-Axis data points -------- X Plot
            im10.set_xdata(np.arange(db_freq))
            im11.set_xdata(np.arange(db_freq))
            im12.set_xdata(np.arange(db_freq))
            im13.set_xdata(np.arange(db_freq))
            im14.set_xdata(np.arange(db_freq))
            im15.set_xdata(np.arange(db_freq))
            im16.set_xdata(np.arange(db_freq))
            im17.set_xdata(np.arange(db_freq))
            im18.set_xdata(np.arange(db_freq))
            im19.set_xdata(np.arange(db_freq))
            im20.set_xdata(np.arange(db_freq))
            im21.set_xdata(np.arange(db_freq))
            im22.set_xdata(np.arange(db_freq))
            im23.set_xdata(np.arange(db_freq))
            im24.set_xdata(np.arange(db_freq))
            im25.set_xdata(np.arange(db_freq))
            # ------------------------------- S Plot
            im26.set_xdata(np.arange(db_freq))
            im27.set_xdata(np.arange(db_freq))
            im28.set_xdata(np.arange(db_freq))
            im29.set_xdata(np.arange(db_freq))
            im30.set_xdata(np.arange(db_freq))
            im31.set_xdata(np.arange(db_freq))
            im32.set_xdata(np.arange(db_freq))
            im33.set_xdata(np.arange(db_freq))
            im34.set_xdata(np.arange(db_freq))
            im35.set_xdata(np.arange(db_freq))
            im36.set_xdata(np.arange(db_freq))
            im37.set_xdata(np.arange(db_freq))
            im38.set_xdata(np.arange(db_freq))
            im39.set_xdata(np.arange(db_freq))
            im40.set_xdata(np.arange(db_freq))
            im41.set_xdata(np.arange(db_freq))
            # X Plot Y-Axis data points for XBar --------------------------------------------[  # Ring 1 ]
            im42.set_xdata(np.arange(db_freq))  # TODO - cross check with freq counter
            im43.set_xdata(np.arange(db_freq))
            im44.set_xdata(np.arange(db_freq))
            im45.set_xdata(np.arange(db_freq))

            # X Plot Y-Axis data points for XBar --------------------------------------------[  # Ring 1 ]
            im10.set_ydata((TT[0]).rolling(window=ttS, min_periods=1).mean()[0:db_freq])  # head 1
            im11.set_ydata((TT[1]).rolling(window=ttS, min_periods=1).mean()[0:db_freq])  # head 2
            im12.set_ydata((TT[2]).rolling(window=ttS, min_periods=1).mean()[0:db_freq])  # head 3
            im13.set_ydata((TT[3]).rolling(window=ttS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 1 ---------#
            mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(ttHL, ttS, 'TT')
            # ---------------------------------------#
            im14.set_ydata((TT[4]).rolling(window=ttS, min_periods=1).mean()[0:db_freq])  # head 1
            im15.set_ydata((TT[5]).rolling(window=ttS, min_periods=1).mean()[0:db_freq])  # head 2
            im16.set_ydata((TT[6]).rolling(window=ttS, min_periods=1).mean()[0:db_freq])  # head 3
            im17.set_ydata((TT[7]).rolling(window=ttS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 2 ---------#
            mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(ttHL, ttS, 'TT')
            # ---------------------------------------#
            im18.set_ydata((TT[8]).rolling(window=ttS, min_periods=1).mean()[0:db_freq])  # head 1
            im19.set_ydata((TT[9]).rolling(window=ttS, min_periods=1).mean()[0:db_freq])  # head 2
            im20.set_ydata((TT[10]).rolling(window=ttS, min_periods=1).mean()[0:db_freq])  # head 3
            im21.set_ydata((TT[11]).rolling(window=ttS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 3 ---------#
            mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(ttHL, ttS, 'TT')
            # ---------------------------------------#
            im22.set_ydata((TT[12]).rolling(window=ttS, min_periods=1).mean()[0:db_freq])  # head 1
            im23.set_ydata((TT[13]).rolling(window=ttS, min_periods=1).mean()[0:db_freq])  # head 2
            im24.set_ydata((TT[14]).rolling(window=ttS, min_periods=1).mean()[0:db_freq])  # head 3
            im25.set_ydata((TT[15]).rolling(window=ttS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 4 ---------#
            mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(ttHL, ttS, 'TT')
            # ---------------------------------------#
            # S Plot Y-Axis data points for StdDev ----------------------------------------
            im26.set_ydata((TT[0]).rolling(window=ttS, min_periods=1).std()[0:db_freq])
            im27.set_ydata((TT[1]).rolling(window=ttS, min_periods=1).std()[0:db_freq])
            im28.set_ydata((TT[2]).rolling(window=ttS, min_periods=1).std()[0:db_freq])
            im29.set_ydata((TT[3]).rolling(window=ttS, min_periods=1).std()[0:db_freq])

            im30.set_ydata((TT[4]).rolling(window=ttS, min_periods=1).std()[0:db_freq])
            im31.set_ydata((TT[5]).rolling(window=ttS, min_periods=1).std()[0:db_freq])
            im32.set_ydata((TT[6]).rolling(window=ttS, min_periods=1).std()[0:db_freq])
            im33.set_ydata((TT[7]).rolling(window=ttS, min_periods=1).std()[0:db_freq])

            im34.set_ydata((TT[8]).rolling(window=ttS, min_periods=1).std()[0:db_freq])
            im35.set_ydata((TT[9]).rolling(window=ttS, min_periods=1).std()[0:db_freq])
            im36.set_ydata((TT[10]).rolling(window=ttS, min_periods=1).std()[0:db_freq])
            im37.set_ydata((TT[11]).rolling(window=ttS, min_periods=1).std()[0:db_freq])

            im38.set_ydata((TT[12]).rolling(window=ttS, min_periods=1).std()[0:db_freq])
            im39.set_ydata((TT[13]).rolling(window=ttS, min_periods=1).std()[0:db_freq])
            im40.set_ydata((TT[14]).rolling(window=ttS, min_periods=1).std()[0:db_freq])
            im41.set_ydata((TT[15]).rolling(window=ttS, min_periods=1).std()[0:db_freq])

            # Compute entire Process Capability -----------#
            if not ttHL:
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLb, ppT, pkT, xline, sline = tq.tAutoPerf(ttS, mnA, mnB,
                                                                                                      mnC, mnD, sdA,
                                                                                                      sdB, sdC, sdD)
            else:
                xline, sline = ttMean, ttDev
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLba, ppT, pkT = tq.tManualPerf(mnA, mnB, mnC, mnD, sdA, sdB,
                                                                                           sdC, sdD, ttUSL, ttLSL,
                                                                                           ttUCL,
                                                                                           ttLCL)
            # ---------------------------------------------------------------------------------------[RAMP]
            # TODO ----
            # im42.set_ydata((RM[1]).rolling(window=ttSize, min_periods=1).mean()[0:db_freq])  # tStamp
            im42.set_ydata((RM[1])[0:db_freq])              # Ring 1
            im43.set_ydata((RM[2])[0:db_freq])              # Ring 2
            im44.set_ydata((RM[3])[0:db_freq])              # Ring 3
            im45.set_ydata((RM[4])[0:db_freq])              # Ring 4

            # # Declare Plots attributes --------------------------------------------------------[]
            # XBar Mean Plot
            a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
            a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 3 Sigma span (Purple)
            a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minTT, sBar_maxTT -------[]
            # Define Legend's Attributes  ----
            a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
            a2.axhspan(sLCLtt, sUCLtt, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 1 Sigma Span
            a2.axhspan(sUCLtt, sBar_maxTT, facecolor='#CCCCFF', edgecolor='#CCCCFF')  # 1 Sigma above the Mean
            a2.axhspan(sBar_minTT, sLCLtt, facecolor='#CCCCFF', edgecolor='#CCCCFF')

            # Setting up the parameters for windows moving Axes on Tape Temp only ---------------[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
                a2.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a1.set_xlim(0, window_Xmax)
                a2.set_xlim(0, window_Xmax)

            # Set trip line for individual time-series plot -----------------------------------[R1]
            import triggerModule as sigma
            sigma.trigViolations(a1, UsePLC_DBS, 'TT', YScale_minTT, YScale_maxTT, xucT, xlcT, xusT, xlsT, mnT, sdT)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousTT, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

# ------------------------------------------------------------------------------------[Substrate Temperature]
class substTempTabb(ttk.Frame):
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        # Load Quality Historical Values -----------[]
        if pRecipe == 'DNV':
            import qParamsHL_DNV as qp
        else:
            import qParamsHL_MGM as qp
        # -----------------------------------------
        stS, stTy, eolS, eopS, stHL, stAL, stFO, stP1, stP2, stP3, stP4, stP5 = qp.decryptpProcessLim(pWON, 'ST')
        # -----------------------------------------
        # Break down each element to useful list -----------[Substrate Temperature]
        if stHL and stP1 and stP2 and stP3 and stP4 and stP5:
            stPerf = '$Pp_{k' + str(stS) + '}$'  # Using estimated or historical Mean
            stlabel = 'Pp'
            # -------------------------------
            One = stP1.split(',')                       # split into list elements
            Two = stP2.split(',')
            Thr = stP3.split(',')
            For = stP4.split(',')
            Fiv = stP5.split(',')
            # -------------------------------
            dTape1 = One[1].strip("' ")                     # defined Tape Width
            dTape2 = Two[1].strip("' ")                     # defined Tape Width
            dTape3 = Thr[1].strip("' ")                     # defined Tape Width
            dTape4 = For[1].strip("' ")                     # defined Tape Width
            dTape5 = Fiv[1].strip("' ")                     # defined Tape Width
            # --------------------------------
            dLayer1 = One[10].strip("' ")                   # Defined Tape Layer
            dLayer2 = Two[10].strip("' ")
            dLayer3 = Thr[10].strip("' ")
            dLayer4 = For[10].strip("' ")
            dLayer5 = Fiv[10].strip("' ")
            # Load historical limits for the process--------#
            if cpTapeW == dTape1 and cpLayerNo <= 1:        # '22mm'|'18mm',  1-40 | 41+
                stUCL = float(One[2].strip("' "))           # Strip out the element of the list
                stLCL = float(One[3].strip("' "))
                stMean = float(One[4].strip("' "))
                stDev = float(One[5].strip("' "))
                # --------------------------------
                sUCLst = float(One[6].strip("' "))
                sLCLst = float(One[7].strip("' "))
                # --------------------------------
                stUSL = (stUCL - stMean) / 3 * 6
                stLSL = (stMean - stLCL) / 3 * 6
                # --------------------------------
            elif cpTapeW == dTape2 and cpLayerNo == 2:
                stUCL = float(Two[2].strip("' "))           # Strip out the element of the list
                stLCL = float(Two[3].strip("' "))
                stMean = float(Two[4].strip("' "))
                stDev = float(Two[5].strip("' "))
                # --------------------------------
                sUCLst = float(Two[6].strip("' "))
                sLCLst = float(Two[7].strip("' "))
                # --------------------------------
                stUSL = (stUCL - stMean) / 3 * 6
                stLSL = (stMean - stLCL) / 3 * 6
            elif cpTapeW == dTape3 and cpLayerNo == range(3, 40):
                stUCL = float(Thr[2].strip("' "))           # Strip out the element of the list
                stLCL = float(Thr[3].strip("' "))
                stMean = float(Thr[4].strip("' "))
                stDev = float(Thr[5].strip("' "))
                # --------------------------------
                sUCLst = float(Thr[6].strip("' "))
                sLCLst = float(Thr[7].strip("' "))
                # --------------------------------
                stUSL = (stUCL - stMean) / 3 * 6
                stLSL = (stMean - stLCL) / 3 * 6
            elif cpTapeW == dTape4 and cpLayerNo == 41:
                stUCL = float(For[2].strip("' "))           # Strip out the element of the list
                stLCL = float(For[3].strip("' "))
                stMean = float(For[4].strip("' "))
                stDev = float(For[5].strip("' "))
                # --------------------------------
                sUCLst = float(For[6].strip("' "))
                sLCLst = float(For[7].strip("' "))
                # --------------------------------
                stUSL = (stUCL - stMean) / 3 * 6
                stLSL = (stMean - stLCL) / 3 * 6
            else:
                stUCL = float(Fiv[2].strip("' "))           # Strip out the element of the list
                stLCL = float(Fiv[3].strip("' "))
                stMean = float(Fiv[4].strip("' "))
                stDev = float(Fiv[5].strip("' "))
                # --------------------------------
                sUCLst = float(Fiv[6].strip("' "))
                sLCLst = float(Fiv[7].strip("' "))
                # --------------------------------
                stUSL = (stUCL - stMean) / 3 * 6
                stLSL = (stMean - stLCL) / 3 * 6
                # -------------------------------
        else:  # Computes Shewhart constants (Automatic Limits)
            stUCL = 0
            stLCL = 0
            stMean = 0
            stDev = 0
            sUCLst = 0
            sLCLst = 0
            stUSL = 0
            stLSL = 0
            stPerf = '$Cp_{k' + str(stS) + '}$'           # Using Automatic group Mean
            stlabel = 'Cp'

        label = ttk.Label(self, text='[' + rType + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Define Axes ---------------------#
        f = Figure(figsize=(pMtX, 8), dpi=100)    # 27
        f.subplots_adjust(left=0.029, bottom=0.05, right=0.983, top=0.955, wspace=0.117, hspace=0.157)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 4, (1, 3))
        a2 = f.add_subplot(2, 4, (5, 7))
        a3 = f.add_subplot(2, 4, (4, 8))

        # Declare Plots attributes --------------------------------[]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minST, YScale_maxST = stLSL - 8.5, stUSL + 8.5
        sBar_minST, sBar_maxST = sLCLst - 80, sUCLst + 80           # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (int(stS) + 3)             # windows view = visible data points

        # Load SQL Query Table -------------------------------------#
        if rType == 1:
            T1 = SPC_ST
        else:
            T1 = 'ST1_' + pWON  # Identify Table
            T2 = 'ST2_' + pWON
        # ----------------------------------------------------------#

        # Initialise runtime limits
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")

        a1.set_title('Substrate Temperature [XBar]', fontsize=12, fontweight='bold')
        a2.set_title('Substrate Temperature [StDev]', fontsize=12, fontweight='bold')
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)

        a1.legend(loc='upper right', title='Substrate Temp')
        a2.legend(loc='upper right', title='Sigma curve')
        # ----------------------------------------------------------#
        a1.set_ylim([YScale_minST, YScale_maxST], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        a2.set_ylim([sBar_minST, sBar_maxST], auto=True)
        a2.set_xlim([window_Xmin, window_Xmax])

        # ----------------------------------------------------------[]
        a3.cla()
        a3.get_yaxis().set_visible(False)
        a3.get_xaxis().set_visible(False)

        # ----------------------------------------------------------------[]
        # Define Plot area and axes -
        # ----------------------------------------------------------------#
        im10, = a1.plot([], [], 'o-', label='Substrate Temp - (R1H1)')
        im11, = a1.plot([], [], 'o-', label='Substrate Temp - (R1H2)')
        im12, = a1.plot([], [], 'o-', label='Substrate Temp - (R1H3)')
        im13, = a1.plot([], [], 'o-', label='Substrate Temp - (R1H4)')
        im14, = a2.plot([], [], 'o-', label='Substrate Temp')
        im15, = a2.plot([], [], 'o-', label='Substrate Temp')
        im16, = a2.plot([], [], 'o-', label='Substrate Temp')
        im17, = a2.plot([], [], 'o-', label='Substrate Temp')

        im18, = a1.plot([], [], 'o-', label='Substrate Temp - (R2H1)')
        im19, = a1.plot([], [], 'o-', label='Substrate Temp - (R2H2)')
        im20, = a1.plot([], [], 'o-', label='Substrate Temp - (R2H3)')
        im21, = a1.plot([], [], 'o-', label='Substrate Temp - (R2H4)')
        im22, = a2.plot([], [], 'o-', label='Substrate Temp')
        im23, = a2.plot([], [], 'o-', label='Substrate Temp')
        im24, = a2.plot([], [], 'o-', label='Substrate Temp')
        im25, = a2.plot([], [], 'o-', label='Substrate Temp')

        im26, = a1.plot([], [], 'o-', label='Substrate Temp - (R3H1)')
        im27, = a1.plot([], [], 'o-', label='Substrate Temp - (R3H2)')
        im28, = a1.plot([], [], 'o-', label='Substrate Temp - (R3H3)')
        im29, = a1.plot([], [], 'o-', label='Substrate Temp - (R3H4)')
        im30, = a2.plot([], [], 'o-', label='Substrate Temp')
        im31, = a2.plot([], [], 'o-', label='Substrate Temp')
        im32, = a2.plot([], [], 'o-', label='Substrate Temp')
        im33, = a2.plot([], [], 'o-', label='Substrate Temp')

        im34, = a1.plot([], [], 'o-', label='Substrate Temp - (R4H1)')
        im35, = a1.plot([], [], 'o-', label='Substrate Temp - (R4H2)')
        im36, = a1.plot([], [], 'o-', label='Substrate Temp - (R4H3)')
        im37, = a1.plot([], [], 'o-', label='Substrate Temp - (R4H4)')
        im38, = a2.plot([], [], 'o-', label='Substrate Temp')
        im39, = a2.plot([], [], 'o-', label='Substrate Temp')
        im40, = a2.plot([], [], 'o-', label='Substrate Temp')
        im41, = a2.plot([], [], 'o-', label='Substrate Temp')

        # Statistical Feed -----------------------------------------[]
        a3.text(0.466, 0.945, 'Performance Feed - ST', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        a3.add_patch(rect1)
        a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)---------------------
        a3.text(0.145, 0.804, stlabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.658, '#Pp Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.650, 0.820, 'Ring ' + stlabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        a3.text(0.145, 0.403, stPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring ' + stPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        # -------------------------------------
        a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ----- Pipe Position and SMC Status -----
        a3.text(0.080, 0.090, 'Pipe Position: ' + pPos + '    Processing Layer #' + layer, fontsize=12, ha='left',
                transform=a3.transAxes)
        a3.text(0.080, 0.036, 'SMC Status: ' + eSMC, fontsize=12, ha='left', transform=a3.transAxes)

        # ---------------- EXECUTE SYNCHRONOUS METHOD -----------------------------#
        def synchronousST(stS, stTy, fetchT):
            fetch_no = str(fetchT)                          # entry value in string sql syntax

            # Obtain Volatile Data from PLC Host Server ---------------------------[]
            if not inUseAlready:                            # Load Coms Plc class once
                import CommsSql as q
                con_st = q.DAQ_connect(1, 0)
            else:
                con_a, con_b = conn.cursor(), conn.cursor()

            # Evaluate conditions for SQL Data Fetch ------------------------------[A]
            """
            Load watchdog function with synchronous function every seconds
            """
            # Initialise RT variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard  # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                # print('Indefinite looping...')
                if UsePLC_DBS:                                      # Using PLC Data
                    import plcArrayRLmethodST as pdB                # DrLabs optimization method

                    inProgress = True                                   # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()     # Retrieve M.State from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    # Either of the 2 combo variables are assigned to trigger routine pause
                    if keyboard.is_pressed(
                            "Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:  # Terminate file-fetch
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            print("\nVisualization in Paused Mode...")
                    else:
                        autoSpcPause = False
                        print("Visualization in Real-time Mode...")
                        # -----------------------------------------------------------------[]
                        stDta = pdB.plcExec(T1, stS, stTy, fetch_no)
                else:
                    import sqlArrayRLmethodST as pst

                    inProgress = False  # False for Real-time mode
                    print('\nSynchronous controller activated...')
                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve MSC from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    # Either of the 2 combo variables are assigned to trigger routine pause
                    if keyboard.is_pressed("ctrl") or not msctcp == 315 and not sysRun and not inProgress:
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            # play(error)                                               # Pause mode with audible Alert
                            print("\nVisualization in Paused Mode...")
                        else:
                            autoSpcPause = False
                        print("Visualization in Play Mode...")

                    else:
                        stDta, stDtb = pst.sqlExec(stS, stTy, con_a, con_b, T1, T2, fetchT)
                        print("Visualization in Play Mode...")
                    print('\nUpdating....')

                    # ------ Inhibit iteration ----------------------------------------------------------[]
                    """
                    # Set condition for halting real-time plots in watchdog class -----------------------[]
                    """
                    # TODO --- values for inhibiting the SQL processing
                    if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                        con_a.close()
                        con_b.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

            return stDta, stDtb

        # ================== End of synchronous Method ==========================
        def asynchronousST(db_freq):
            timei = time.time()  # start timing the entire loop

            # Call data loader Method---------------------------#
            stDta, stDtb = synchronousST(stS, stTy, db_freq)     # data loading functions
            # --------------------------------------------------#

            if UsePLC_DBS == 1:
                import VarPLC_ST as st

                viz_cycle = 10
                # Call synchronous data function ---------------[]
                g1 = qst.validCols(T1)                          # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(stDta, columns=g1)           # Include table data into python Dataframe
                ST = st.loadProcesValues(df1)                   # Join data values under dataframe

            else:
                import VarSQL_ST as st                           # load SQL variables column names | rfVarSQL

                viz_cycle = 150
                g1 = qst.validCols(T1)                          # Construct Data Column selSqlColumnsTFM.py
                d1 = pd.DataFrame(stDta, columns=g1)            # Import into python Dataframe

                g2 = qla.validCols(T2)
                d2 = pd.DataFrame(stDtb, columns=g2)

                # Concatenate all columns -----------[]
                df1 = pd.concat([d1, d2], axis=1)
                ST = st.loadProcesValues(df1)                   # Join data values under dataframe
            print('\nSQL Content', df1.head(10))
            print("Memory Usage:", df1.info(verbose=False))     # Check memory utilization

            # -------------------------------------------------------------------------------------[]
            # Plot X-Axis data points -------- X Plot
            im10.set_xdata(np.arange(db_freq))
            im11.set_xdata(np.arange(db_freq))
            im12.set_xdata(np.arange(db_freq))
            im13.set_xdata(np.arange(db_freq))
            im14.set_xdata(np.arange(db_freq))
            im15.set_xdata(np.arange(db_freq))
            im16.set_xdata(np.arange(db_freq))
            im17.set_xdata(np.arange(db_freq))
            im18.set_xdata(np.arange(db_freq))
            im19.set_xdata(np.arange(db_freq))
            im20.set_xdata(np.arange(db_freq))
            im21.set_xdata(np.arange(db_freq))
            im22.set_xdata(np.arange(db_freq))
            im23.set_xdata(np.arange(db_freq))
            im24.set_xdata(np.arange(db_freq))
            im25.set_xdata(np.arange(db_freq))
            # ------------------------------- S Plot
            im26.set_xdata(np.arange(db_freq))
            im27.set_xdata(np.arange(db_freq))
            im28.set_xdata(np.arange(db_freq))
            im29.set_xdata(np.arange(db_freq))
            im30.set_xdata(np.arange(db_freq))
            im31.set_xdata(np.arange(db_freq))
            im32.set_xdata(np.arange(db_freq))
            im33.set_xdata(np.arange(db_freq))
            im34.set_xdata(np.arange(db_freq))
            im35.set_xdata(np.arange(db_freq))
            im36.set_xdata(np.arange(db_freq))
            im37.set_xdata(np.arange(db_freq))
            im38.set_xdata(np.arange(db_freq))
            im39.set_xdata(np.arange(db_freq))
            im40.set_xdata(np.arange(db_freq))
            im41.set_xdata(np.arange(db_freq))
            # X Plot Y-Axis data points for XBar --------------------------------------------[  # Ring 1 ]
            im10.set_ydata((ST[0]).rolling(window=stS, min_periods=1).mean()[0:db_freq])  # head 1
            im11.set_ydata((ST[1]).rolling(window=stS, min_periods=1).mean()[0:db_freq])  # head 2
            im12.set_ydata((ST[2]).rolling(window=stS, min_periods=1).mean()[0:db_freq])  # head 3
            im13.set_ydata((ST[3]).rolling(window=stS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 1 ---------#
            mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(stHL, stS, 'ST')
            # ---------------------------------------#
            im14.set_ydata((ST[4]).rolling(window=stS, min_periods=1).mean()[0:db_freq])  # head 1
            im15.set_ydata((ST[5]).rolling(window=stS, min_periods=1).mean()[0:db_freq])  # head 2
            im16.set_ydata((ST[6]).rolling(window=stS, min_periods=1).mean()[0:db_freq])  # head 3
            im17.set_ydata((ST[7]).rolling(window=stS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 2 ---------#
            mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(stHL, stS, 'ST')
            # ---------------------------------------#
            im18.set_ydata((ST[8]).rolling(window=stS, min_periods=1).mean()[0:db_freq])  # head 1
            im19.set_ydata((ST[9]).rolling(window=stS, min_periods=1).mean()[0:db_freq])  # head 2
            im20.set_ydata((ST[10]).rolling(window=stS, min_periods=1).mean()[0:db_freq])  # head 3
            im21.set_ydata((ST[11]).rolling(window=stS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 3 ---------#
            mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(stHL, stS, 'ST')
            # ---------------------------------------#
            im22.set_ydata((ST[12]).rolling(window=stS, min_periods=1).mean()[0:db_freq])  # head 1
            im23.set_ydata((ST[13]).rolling(window=stS, min_periods=1).mean()[0:db_freq])  # head 2
            im24.set_ydata((ST[14]).rolling(window=stS, min_periods=1).mean()[0:db_freq])  # head 3
            im25.set_ydata((ST[15]).rolling(window=stS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 4 ---------#
            mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(stHL, stS, 'ST')
            # ---------------------------------------#
            # S Plot Y-Axis data points for StdDev ----------------------------------------
            im26.set_ydata((ST[0]).rolling(window=stS, min_periods=1).std()[0:db_freq])
            im27.set_ydata((ST[1]).rolling(window=stS, min_periods=1).std()[0:db_freq])
            im28.set_ydata((ST[2]).rolling(window=stS, min_periods=1).std()[0:db_freq])
            im29.set_ydata((ST[3]).rolling(window=stS, min_periods=1).std()[0:db_freq])

            im30.set_ydata((ST[4]).rolling(window=stS, min_periods=1).std()[0:db_freq])
            im31.set_ydata((ST[5]).rolling(window=stS, min_periods=1).std()[0:db_freq])
            im32.set_ydata((ST[6]).rolling(window=stS, min_periods=1).std()[0:db_freq])
            im33.set_ydata((ST[7]).rolling(window=stS, min_periods=1).std()[0:db_freq])

            im34.set_ydata((ST[8]).rolling(window=stS, min_periods=1).std()[0:db_freq])
            im35.set_ydata((ST[9]).rolling(window=stS, min_periods=1).std()[0:db_freq])
            im36.set_ydata((ST[10]).rolling(window=stS, min_periods=1).std()[0:db_freq])
            im37.set_ydata((ST[11]).rolling(window=stS, min_periods=1).std()[0:db_freq])

            im38.set_ydata((ST[12]).rolling(window=stS, min_periods=1).std()[0:db_freq])
            im39.set_ydata((ST[13]).rolling(window=stS, min_periods=1).std()[0:db_freq])
            im40.set_ydata((ST[14]).rolling(window=stS, min_periods=1).std()[0:db_freq])
            im41.set_ydata((ST[15]).rolling(window=stS, min_periods=1).std()[0:db_freq])
            # Compute entire Process Capability -----------#
            if not stHL:
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLc, dLCLc, ppT, pkT, xline, sline = tq.tAutoPerf(stS, mnA, mnB,
                                                                                                      mnC, mnD, sdA,
                                                                                                      sdB, sdC, sdD)
            else:
                xline, sline = stMean, stDev
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLc, dLCLc, ppT, pkT = tq.tManualPerf(mnA, mnB, mnC, mnD, sdA, sdB,
                                                                                          sdC, sdD, stUSL, stLSL, stUCL,
                                                                                          stLCL)
            # # Declare Plots attributes ------------------------------------------------------------[]
            # XBar Mean Plot
            a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
            a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 3 Sigma span (Purple)
            a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minST, sBar_maxST -------[]
            # Define Legend's Attributes  ----
            a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
            a2.axhspan(dLCLc, dUCLc, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 1 Sigma Span
            a2.axhspan(dUCLc, sBar_maxST, facecolor='#CCCCFF', edgecolor='#CCCCFF')  # 1 Sigma above the Mean
            a2.axhspan(sBar_minST, dLCLc, facecolor='#CCCCFF', edgecolor='#CCCCFF')

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
                a2.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a1.set_xlim(0, window_Xmax)
                a2.set_xlim(0, window_Xmax)

            # Set trip line for individual time-series plot -----------------------------------[R1]
            import triggerModule as sigma
            sigma.trigViolations(a1, UsePLC_DBS, 'ST', YScale_minST, YScale_maxST, xucT, xlcT, xusT, xlsT, mnT, sdT)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousST, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

# ---------------------------------------------------------------------------------------------[Tape Gap Tab]
class tapeGapPolTabb(ttk.Frame):

    """ Application to convert feet to meters or vice versa. """

    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        # define region ------
        self.display_rtStats()

    def display_rtStats(self):
        global a2, a4, gap_vol       # allow axial inheritance on new class method

        """Create the widgets for the GUI"""
        if pRecipe == 'DNV':
            import qParamsHL_DNV as qp
        else:
            import qParamsHL_MGM as qp
        # Load metrics from config -----------------------------------[Tape Gap]
        tgS, tgTy, eolS, eopS, tgHL, tgAL, tgtFO, tgP1, dud2, dud3, dud4, dud5 = qp.decryptpProcessLim(pWON, 'TG')

        # Break down each element to useful list ---------------------[Tape Gap]
        if tgHL and tgP1:
            tgPerf = '$Pp_{k' + str(tgS) + '}$'       # Estimated or historical Mean
            tglabel = 'Pp'
            # -------------------------------
            tgOne = tgP1.split(',')                 # split into list elements
            dTapetg = tgOne[1].strip("' ")              # defined Tape Width
            dLayer = tgOne[10].strip("' ")              # Defined Tape Layer

            # Load historical limits for the process----#
            tgUCL = float(tgOne[2].strip("' "))         # Strip out the element of the list
            tgLCL = float(tgOne[3].strip("' "))
            tgMean = float(tgOne[4].strip("' "))
            tgDev = float(tgOne[5].strip("' "))
            # --------------------------------
            sUCLtg = float(tgOne[6].strip("' "))
            sLCLtg = float(tgOne[7].strip("' "))
            # --------------------------------
            tgUSL = (tgUCL - tgMean) / 3 * 6
            tgLSL = (tgMean - tgLCL) / 3 * 6
            # --------------------------------
        else:   # Computes Shewhart constants (Automatic Limits)
            tgUCL = 0
            tgLCL = 0
            tgMean = 0
            tgDev = 0
            sUCLtg = 0
            sLCLtg = 0
            tgUSL = 0
            tgLSL = 0
            tgPerf = '$Cp_{k' + str(tgS) + '}$'                   # Using Automatic group Mean
            tglabel = 'Cp'

        # -------------------------------------------[End of Tape Gap]

        label = ttk.Label(self, text='[' + rType + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)     # 10 | 5

        # Define Axes ---------------------#
        f = Figure(figsize=(pMtX, 8), dpi=100)                        # 25, 27 = 12 | 8
        f.subplots_adjust(left=0.026, bottom=0.045, right=0.983, top=0.967, wspace=0.217, hspace=0.162)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 6, (1, 3))                            # xbar plot
        a3 = f.add_subplot(2, 6, (7, 9))                            # s bar plot
        a4 = f.add_subplot(2, 6, (4, 12))                           # void mapping profile

        # ----------------------------------------------------------[H]
        plt.rcParams.update({'font.size': 9})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minTG, YScale_maxTG = tgLSL - 8.5, tgUSL + 8.5       # Roller Force
        sBar_minTG, sBar_maxTG = sLCLtg - 80, sUCLtg + 80           # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (int(tgS) + 3)             # windows view = visible data points
        # ----------------------------------------------------------#
        YScale_minVM, YScale_maxVM = 0, pExLayer                    # Valid Void Mapping
        window_XminVM, window_XmaxVM = 0, pLength                   # Get details from SCADA PIpe Recipe TODO[1]

        # Real-Time Parameter according to updated requirements ----# 07/Feb/2025
        if rType == 1:
            T1 = SPC_TG                 # SPC Datablock
        else:
            T1 = 'TG_' + pWON           # Tape Gap
        T2 = 'VM_' + pWON               # Void Mapping - Must be loaded from SQL repository
        # ----------------------------------------------------------#

        # Initialise runtime limits --------------------------------#
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a3.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")

        a1.set_title('Tape Gap Polarisation [XBar]', fontsize=12, fontweight='bold')
        a3.set_title('Tape Gap Polarisation [SDev]', fontsize=12, fontweight='bold')
        a4.set_title('Tape Gap Mapping Profile', fontsize=12, fontweight='bold')

        a4.set_ylabel("2D - Staked Layer Void Mapping")
        a4.set_xlabel("Sample Distance (mt)")
        a4.set_facecolor("green")                           # set face color for Ramp mapping volume
        zoom_factory(a4)                                    # allow zooming on image plot

        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a3.grid(color="0.5", linestyle='-', linewidth=0.5)
        a4.grid(color="0.5", linestyle='-', linewidth=0.5)

        a1.legend(loc='upper right', title='Tape Gap Polarisation')
        a3.legend(loc='upper right', title='Sigma Plots')
        # a4.legend(loc='upper right', title='Void Map Profile')
        # ------------------------------------------------------[for Ramp Plot]
        colors = np.random.randint(50, 101, size=(367))     # TODO -- obtain length of element dynamically
        rlabel = ['< 0', '0 - 2', '2 - 4', '4 - 6', '6 - 8', '8 - 9', '9 - 10', 'above']

        # Initialise runtime limits -------------------------------#
        a1.set_ylim([YScale_minTG, YScale_maxTG], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        a3.set_ylim([sBar_minTG, sBar_maxTG], auto=True)
        a3.set_xlim([window_Xmin, window_Xmax])
        # --------------------------------------------------------[]
        a4.set_ylim([YScale_minVM, YScale_maxVM], auto=True)
        a4.set_xlim([window_XminVM, window_XmaxVM])

        # ----------------------------------------------------------[]
        # Define Plot area and axes -
        # ----------------------------------------------------------[8 into 4]
        im10, = a1.plot([], [], 'o-', label='Tape Gap Pol - (A1)')
        im11, = a1.plot([], [], 'o-', label='Tape Gap Pol - (B1)')
        im12, = a1.plot([], [], 'o-', label='Tape Gap Pol - (A2)')
        im13, = a1.plot([], [], 'o-', label='Tape Gap Pol - (B2)')
        im14, = a1.plot([], [], 'o-', label='Tape Gap Pol - (A3)')
        im15, = a1.plot([], [], 'o-', label='Tape Gap Pol - (B3)')
        im16, = a1.plot([], [], 'o-', label='Tape Gap Pol - (A4)')
        im17, = a1.plot([], [], 'o-', label='Tape Gap Pol - (B4)')
        # ------------ S Bar Plot ------------------------------
        im18, = a3.plot([], [], 'o-', label='Tape Gap Pol')
        im19, = a3.plot([], [], 'o-', label='Tape Gap Pol')
        im20, = a3.plot([], [], 'o-', label='Tape Gap Pol')
        im21, = a3.plot([], [], 'o-', label='Tape Gap Pol')
        im22, = a3.plot([], [], 'o-', label='Tape Gap Pol')
        im23, = a3.plot([], [], 'o-', label='Tape Gap Pol')
        im24, = a3.plot([], [], 'o-', label='Tape Gap Pol')
        im25, = a3.plot([], [], 'o-', label='Tape Gap Pol')
        # ------------------------------------------------------
        im26, = a4.plot([], [], 'o-', label='Tape Gap Pol')
        # im26 = a4.plot([], [], s=gap_vol, marker='s', c=colors, cmap='rainbow')
        # a4.legend(handles=im26.legend_elements()[0], labels=rlabel, title='Void Map (%)')
        # -------------------------------------------------------------------------#
        # loadSqlCumProfile(ttk.Frame)
        # loadSqlVoidMapping()
        # ---------------- EXECUTE SYNCHRONOUS TG METHOD --------------------------#

        def synchronousTG(tgS, tgTy, fetchT):
            # fetch_no = str(fetchT)                                                 # entry value in string sql syntax

            # Obtain Volatile Data from PLC Host Server ---------------------------[]
            if not inUseAlready:                                                   # Load CommsPlc class once
                import CommsSql as q
                con_tg = q.DAQ_connect(1, 0)                                        # Load TG and VM data from PLC
                con_vm = conn.cursor()                                              # SQL Stream for cummulative plot
            else:
                con_tg = conn.cursor()                                               # TapeGap Stream

            # Evaluate conditions for SQL Data Fetch ------------------------------[A]
            """
            Load watchdog function with synchronous function every seconds
            """
            # Initialise RT variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard                                                        # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                # print('Indefinite looping...')
                if UsePLC_DBS:                                                      # Not Using PLC Data
                    import plcArrayRLmethodTG as pdC                                # DrLabs optimization method
                    import sqlArrayRLmethodVM as pdD                                # Important to load from SQL Repo

                    inProgress = True                                               # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve M.State from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    if keyboard.is_pressed(
                            "Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:  # Terminate file-fetch
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            print("\nVisualization in Paused Mode...")
                    else:
                        sampC = 0           # TODO: pooling from SPC_VM sCentre
                        autoSpcPause = False
                        print("Visualization in Real-time Mode...")
                        # Open RT dual stream connections and obtain relevant Table --------------------[]
                        tgDta = pdC.plcExec(T1, tgS, tgTy, fetchT)                          # get data from PLC array
                        vmDta = pdD.sqlExec(tgS, tgTy, con_vm, T2, sampC, fetchT)           # get data from SQl Repo

                else:
                    import sqlArrayRLmethodTG as pdC
                    import sqlArrayRLmethodVM as pdD

                    inProgress = False                                                  # False for Real-time mode
                    print('\nSynchronous controller activated...')
                    if not sysRun:
                       sysRun, msctcp, msc_rt = wd.autoPausePlay()                      # Retrieve MSC from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    # Either of the 2 combo variables are assigned to trigger routine pause
                    if keyboard.is_pressed("ctrl") or not msctcp == 315 and not sysRun and not inProgress:
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            # play(error)                                               # Pause mode with audible Alert
                            print("\nVisualization in Paused Mode...")
                        else:
                            autoSpcPause = False
                            print("Visualization in Play Mode...")
                    else:
                        sampC = 0                   # TODO: pooling from SPC_VM sCentre
                        tgDta = pdC.sqlExec(tgS, tgTy, con_tg, T1, sampC, fetchT)
                        vmDta = pdD.sqlExec(tgS, tgTy, con_vm, T2, sampC, fetchT)
                        print("Visualization in Play Mode...")
                    print('\nUpdating....')

                    # ------ Inhibit iteration ----------------------------------------------------------[]
                    """
                    # Set condition for halting real-time plots in watchdog class -----------------------[]
                    """
                    # TODO --- values for inhibiting the SQL processing
                    if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                        con_tg.close()
                        con_vm.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

            return tgDta, vmDta


        # ================== End of synchronous Method ==========================

        def asynchronousTG(db_freq):
            global gap_vol
            timei = time.time()                                   # start timing the entire loop

            # Bi-stream Data Pooling Method ----------------------#
            tgDta, vmDta = synchronousTG(tgS, tgTy, db_freq)       # PLC synchronous Data loading method1
            # ----------------------------------------------------#

            if UsePLC_DBS == 1:
                import VarPLC_TG as tg

                viz_cycle = 10
                dcA = qtg.validCols(T1)                         # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(tgDta, columns=dcA)          # Include table data into python Dataframe
                # ----------------------------------------------#
                TG = tg.loadProcesValues(df1)                   # Join data values under dataframe

            else:
                import VarSQL_TG as tg                           # load SQL variables column names | rfVarSQL

                viz_cycle = 150
                g1 = qtg.validCols(T1)                          # Construct Data Column selSqlColumnsTFM.py
                df1 = pd.DataFrame(tgDta, columns=g1)           # Import into python Dataframe
                TG = tg.loadProcesValues(df1)                   # Join data values under dataframe
            # Compulsory VoidMap function call -- SQL loader --[B]
            import VarSQL_VM as vm                              # load SQL variables column names | rfVarSQL

            viz_cycle = 150
            g1 = qvm.validCols(T2)                              # Construct Data Column selSqlColumnsTFM.py
            df1 = pd.DataFrame(vmDta, columns=g1)               # Import into python Dataframe
            VM = vm.loadProcesValues(df1)                       # Join data values under dataframe
            print('\nDataFrame Content', df1.head(10))          # Preview Data frame head
            print("Memory Usage:", df1.info(verbose=False))     # Check memory utilization

            # Plot X-Axis data points -------- X Plot
            im10.set_xdata(np.arange(db_freq))
            im11.set_xdata(np.arange(db_freq))
            im12.set_xdata(np.arange(db_freq))
            im13.set_xdata(np.arange(db_freq))
            im14.set_xdata(np.arange(db_freq))
            im15.set_xdata(np.arange(db_freq))
            im16.set_xdata(np.arange(db_freq))
            im17.set_xdata(np.arange(db_freq))
            # ------------------------------- S Plot
            im18.set_xdata(np.arange(db_freq))
            im19.set_xdata(np.arange(db_freq))
            im20.set_xdata(np.arange(db_freq))
            im21.set_xdata(np.arange(db_freq))
            im22.set_xdata(np.arange(db_freq))
            im23.set_xdata(np.arange(db_freq))
            im24.set_xdata(np.arange(db_freq))
            im25.set_xdata(np.arange(db_freq))
            # -------------------------------- Profile Axes
            # im26.set_xdata(np.arange(db_freq))
            a4.set_xdata(np.arange(db_freq))

            # X Plot Y-Axis data points for XBar -------------------------------------------[# Channels]
            im10.set_ydata((TG[0]).rolling(window=tgS, min_periods=1).mean()[0:db_freq])  # Segment 1
            im11.set_ydata((TG[1]).rolling(window=tgS, min_periods=1).mean()[0:db_freq])  # Segment 2
            im12.set_ydata((TG[2]).rolling(window=tgS, min_periods=1).mean()[0:db_freq])  # Segment 3
            im13.set_ydata((TG[3]).rolling(window=tgS, min_periods=1).mean()[0:db_freq])  # Segment 4
            # ------ Evaluate Pp for Segments ---------#
            mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(tgHL, tgS, 'TG')
            # ---------------------------------------#
            im14.set_ydata((TG[4]).rolling(window=tgS, min_periods=1).mean()[0:db_freq])  # Segment 1
            im15.set_ydata((TG[5]).rolling(window=tgS, min_periods=1).mean()[0:db_freq])  # Segment 2
            im16.set_ydata((TG[6]).rolling(window=tgS, min_periods=1).mean()[0:db_freq])  # Segment 3
            im17.set_ydata((TG[7]).rolling(window=tgS, min_periods=1).mean()[0:db_freq])  # Segment 4
            # ------ Evaluate Pp for Ring 2 ---------#
            mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(tgHL, tgS, 'TG')

            # S Plot Y-Axis data points for StdDev ----------------------------------------[# S Bar Plot]
            im18.set_ydata((TG[0]).rolling(window=tgS, min_periods=1).std()[0:db_freq])
            im19.set_ydata((TG[1]).rolling(window=tgS, min_periods=1).std()[0:db_freq])
            im20.set_ydata((TG[2]).rolling(window=tgS, min_periods=1).std()[0:db_freq])
            im21.set_ydata((TG[3]).rolling(window=tgS, min_periods=1).std()[0:db_freq])

            im22.set_ydata((TG[4]).rolling(window=tgS, min_periods=1).std()[0:db_freq])
            im23.set_ydata((TG[5]).rolling(window=tgS, min_periods=1).std()[0:db_freq])
            im24.set_ydata((TG[6]).rolling(window=tgS, min_periods=1).std()[0:db_freq])
            im25.set_ydata((TG[7]).rolling(window=tgS, min_periods=1).std()[0:db_freq])

            if not tgHL:
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLd, dLCLd, ppT, pkT, xline, sline = tq.tAutoPerf(tgS, mnA, mnB,
                                                                                                      0, 0, sdA,
                                                                                                      sdB, 0, 0)
            else:
                xline, sline = tgMean, tgDev
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLd, dLCLd, ppT, pkT = tq.tManualPerf(mnA, mnB, 0, 0, sdA, sdB,
                                                                                          0, 0, tgUSL, tgLSL, tgUCL,
                                                                                          tgLCL)
            # ---- Profile rolling Data Plot ------------------------------------------------------------------------[]
            pScount = VM[0]
            pCenter = VM[1]
            pAvgGap = VM[2]
            pMaxGap = VM[3]
            vLayerN = VM[4]
            sLength = VM[5]
            gap_vol = (pAvgGap / sLength) * 100  # Percentage Void

            # im26.set_ydata((vLayerN),(gap_vol) [0:db_freq])  # --------------------------- Profile A
            a4.set_ydata((vLayerN),(gap_vol) [0:db_freq])

            # # Declare Plots attributes ------------------------------------------------------------[]
            # XBar Mean Plot
            a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
            a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')            # 3 Sigma span (Purple)
            a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')            # grey area
            a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minTG, sBar_maxTG -------[]
            # Define Legend's Attributes  ----
            a3.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
            a3.axhspan(dLCLd, dUCLd, facecolor='#F9C0FD', edgecolor='#F9C0FD')          # 1 Sigma Span
            a3.axhspan(dUCLd, sBar_maxTG, facecolor='#CCCCFF', edgecolor='#CCCCFF')     # 1 Sigma above the Mean
            a3.axhspan(sBar_minTG, dLCLd, facecolor='#CCCCFF', edgecolor='#CCCCFF')

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
                a3.set_xlim(db_freq - window_Xmax, db_freq)
                # a4.set_xlim(db_freq - window_Xmax, db_freq)   # Non moving axis on profile B
            else:
                a1.set_xlim(0, window_Xmax)
                a3.set_xlim(0, window_Xmax)

            # Set trip line for individual time-series plot -----------------------------------[R1]
            import triggerModule as sigma
            sigma.trigViolations(a1, UsePLC_DBS, 'TG', YScale_minTG, YScale_maxTG, xucT, xlcT, xusT, xlsT, mnT, sdT)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousTG, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

# -------------------------------------------------------------------------------------------[Tape Placement]
class tapePlacementTabb(ttk.Frame):     # -- Defines the tabbed region for QA param - Substrate Temperature --[]
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        # --------------------------------------------------------------------[]
        if pRecipe == 'DNV':
            import qParamsHL_DNV as qp
        else:
            import qParamsHL_MGM as qp
        # Load metrics from config -----------------------------------[Tape Gap]
        tpS, tpTy, eolS, eopS, tpHL, tpAL, tptFO, tpP1, dud2, dud3, dud4, dud5 = qp.decryptpProcessLim(pWON, 'TP')

        # Break down each element to useful list ----------------[Tape Placement]

        if tpHL and tpP1:
            tpPerf = '$Pp_{k' + str(tpS) + '}$'  # Estimated or historical Mean
            tplabel = 'Pp'
            # -------------------------------
            tpOne = tpP1.split(',')  # split into list elements
            dTapetp = tpOne[1].strip("' ")  # defined Tape Width
            dLayer = tpOne[10].strip("' ")  # Defined Tape Layer

            # Load historical limits for the process----------------#
            # if cpTapeW == dTapetg and cpLayerNo == range(1, 100):   # '*.*',  | *.*
            tpUCL = float(tpOne[2].strip("' "))  # Strip out the element of the list
            tpLCL = float(tpOne[3].strip("' "))
            tpMean = float(tpOne[4].strip("' "))
            tpDev = float(tpOne[5].strip("' "))
            # --------------------------------
            sUCLtp = float(tpOne[6].strip("' "))
            sLCLtp = float(tpOne[7].strip("' "))
            # --------------------------------
            tpUSL = (tpUCL - tpMean) / 3 * 6
            tpLSL = (tpMean - tpLCL) / 3 * 6
            # --------------------------------
        else:  # Computes Shewhart constants (Automatic Limits)
            tpUCL = 0
            tpLCL = 0
            tpMean = 0
            tpDev = 0
            sUCLtp = 0
            sLCLtp = 0
            tpUSL = 0
            tpLSL = 0
            tpPerf = '$Cp_{k' + str(tpS) + '}$'  # Using Automatic group Mean
            tplabel = 'Cp'

        # ------------------------------------[End of Winding Speed Abstraction]

        label = ttk.Label(self, text='[' + rType + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Set subplot embedded properties ----------------------------------[]
        f = Figure(figsize=(pMtX, 8), dpi=100)      # 25, 27
        f.subplots_adjust(left=0.029, bottom=0.05, right=0.983, top=0.955, wspace=0.117, hspace=0.157)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 4, (1, 3))        # xbar plot
        a2 = f.add_subplot(2, 4, (5, 7))        # s bar plot
        a3 = f.add_subplot(2, 4, (4, 8))        # CPk/PPk Feed

        # Declare Plots attributes ---------------------------------[]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minTP, YScale_maxTP = tpLSL - 8.5, tpUSL + 8.5       # Roller Force
        sBar_minTP, sBar_maxTP = sLCLtp - 80, sUCLtp + 80           # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (int(tpS) + 3)             # windows view = visible data points

        # ----------------------------------------------------------#
        # Real-Time Parameter according to updated requirements ----# 07/Feb/2025
        if rType == 1:
            T1 = SPC_TP
        else:
            T1 = 'TP1_' + pWON  # Tape Placement
            T2 = 'TP2_' + pWON
        # ----------------------------------------------------------#

        # Initialise runtime limits
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        a1.set_title('Tape Placement [XBar]', fontsize=12, fontweight='bold')
        a2.set_title('Tape Placement [StDev]', fontsize=12, fontweight='bold')

        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a1.legend(loc='upper right', title='Tape Placement')
        a2.legend(loc='upper right', title='Sigma curve')

        # Initialise runtime limits -------------------------------#
        a1.set_ylim([YScale_minTP, YScale_maxTP], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        a3.set_ylim([sBar_minTP, sBar_maxTP], auto=True)
        a3.set_xlim([window_Xmin, window_Xmax])

        # ----------------------------------------------------------[]
        a3.cla()
        a3.get_yaxis().set_visible(False)
        a3.get_xaxis().set_visible(False)

        # ----------------------------------------------------------[]
        # Define Plot area and axes -
        # ----------------------------------------------------------#
        im10, = a1.plot([], [], 'o-', label='Tape Placement - (A1)')
        im11, = a1.plot([], [], 'o-', label='Tape Placement - (B1)')
        im12, = a1.plot([], [], 'o-', label='Tape Placement - (A2)')
        im13, = a1.plot([], [], 'o-', label='Tape Placement - (B2)')
        im14, = a1.plot([], [], 'o-', label='Tape Placement - (A3)')
        im15, = a1.plot([], [], 'o-', label='Tape Placement - (B3)')
        im16, = a1.plot([], [], 'o-', label='Tape Placement - (A4)')
        im17, = a1.plot([], [], 'o-', label='Tape Placement - (B4)')
        # ------------ S Bar Plot ------------------------------
        im18, = a2.plot([], [], 'o-', label='Tape Placement')
        im19, = a2.plot([], [], 'o-', label='Tape Placement')
        im20, = a2.plot([], [], 'o-', label='Tape Placement')
        im21, = a2.plot([], [], 'o-', label='Tape Placement')
        im22, = a2.plot([], [], 'o-', label='Tape Placement')
        im23, = a2.plot([], [], 'o-', label='Tape Placement')
        im24, = a2.plot([], [], 'o-', label='Tape Placement')
        im25, = a2.plot([], [], 'o-', label='Tape Placement')

        # Statistical Feed -----------------------------------------[]
        a3.text(0.466, 0.945, 'Performance Feed - WP', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        a3.add_patch(rect1)
        a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)---------------------
        a3.text(0.145, 0.804, tplabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.658, '#Pp Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.650, 0.820, 'Ring ' + tplabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        a3.text(0.145, 0.403, tpPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring ' + tpPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        # -------------------------------------
        a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ----- Pipe Position and SMC Status -----
        a3.text(0.080, 0.090, 'Pipe Position: ' + pPos + '    Processing Layer #' + layer, fontsize=12, ha='left',
                transform=a3.transAxes)
        a3.text(0.080, 0.036, 'SMC Status: ' + eSMC, fontsize=12, ha='left', transform=a3.transAxes)

        # ---------------- EXECUTE SYNCHRONOUS METHOD -----------------------------#
        def synchronousTP(tpS, tpTy, fetchT):
            fetch_no = str(fetchT)                  # entry value in string sql syntax

            # Obtain Volatile Data from PLC Host Server ---------------------------[]
            if not inUseAlready:  # Load CommsPlc class once
                import CommsSql as q
                q.DAQ_connect(1, 0)
            else:
                con_a, con_b = conn.cursor(), conn.cursor()
            # Evaluate conditions for SQL Data Fetch ------------------------------[A]
            """
            Load watchdog function with synchronous function every seconds
            """
            # Initialise RT variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard  # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                # print('Indefinite looping...')
                if UsePLC_DBS:                                          # Not Using PLC Data
                    import plcArrayRLmethodTP as stp                    # DrLabs optimization method

                    inProgress = True                                   # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve M.State from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    if keyboard.is_pressed(
                            "Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:  # Terminate file-fetch
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            print("\nVisualization in Paused Mode...")

                    else:
                        autoSpcPause = False
                        print("Visualization in Real-time Mode...")
                        # Get list of relevant SQL Tables using conn() --------------------[]
                        tpDta = stp.plcExec(T1, tpS, tpTy, fetch_no)
                        tpDtb = 0

                else:
                    import sqlArrayRLmethodTP as stp

                    inProgress = False  # False for Real-time mode
                    print('\nSynchronous controller activated...')
                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve MSC from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    # Either of the 2 combo variables are assigned to trigger routine pause
                    if keyboard.is_pressed("ctrl") or not msctcp == 315 and not sysRun and not inProgress:
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            # play(error)                                               # Pause mode with audible Alert
                            print("\nVisualization in Paused Mode...")
                        else:
                            autoSpcPause = False
                        print("Visualization in Play Mode...")
                    else:
                        tpDta, tpDtb = stp.sqlExec(tpS, tpTy, con_a, con_b, T1, T2, fetchT)
                        print("Visualization in Play Mode...")
                    print('\nUpdating....')
                    # ------ Inhibit iteration ----------------------------------------------------------[]
                    """
                    # Set condition for halting real-time plots in watchdog class -----------------------[]
                    """
                    # TODO --- values for inhibiting the SQL processing
                    if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                        con_a.close()
                        con_b.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

            return tpDta, tpDtb

        # ================== End of synchronous Method ==========================
        def asynchronousTP(db_freq):
            timei = time.time()                                 # start timing the entire loop

            # Call data loader Method---------------------------#
            tpDta, tpDtb = synchronousTP(tpS, tpTy, db_freq)    # data loading functions
            # --------------------------------------------------#

            if UsePLC_DBS == 1:
                import VarPLCtp as tp

                viz_cycle = 10
                # Call synchronous data function ---------------[]
                columns = qtp.validCols(T1)                    # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(tpDta, columns=columns)    # Include table data into python Dataframe
                TP = tp.loadProcesValues(df1)                  # Join data values under dataframe

            else:
                import VarSQLtp as tp                          # load SQL variables column names | rfVarSQL

                viz_cycle = 150
                g1 = qtp.validCols(T1)                         # Construct Data Column selSqlColumnsTFM.py
                d1 = pd.DataFrame(tpDta, columns=g1)         # Import into python Dataframe

                g2 = qla.validCols(T2)
                d2 = pd.DataFrame(tpDtb, columns=g2)

                # Concatenate all columns -----------[]
                df1 = pd.concat([d1, d2], axis=1)
                TP = tp.loadProcesValues(df1)                  # Join data values under dataframe
            print('\nSQL Content', df1.head(10))
            print("Memory Usage:", df1.info(verbose=False))    # Check memory utilization

            # -------------------------------------------------------------------------------------[]
            # Plot X-Axis data points -------- X Plot
            im10.set_xdata(np.arange(db_freq))
            im11.set_xdata(np.arange(db_freq))
            im12.set_xdata(np.arange(db_freq))
            im13.set_xdata(np.arange(db_freq))
            im14.set_xdata(np.arange(db_freq))
            im15.set_xdata(np.arange(db_freq))
            im16.set_xdata(np.arange(db_freq))
            im17.set_xdata(np.arange(db_freq))
            im18.set_xdata(np.arange(db_freq))
            im19.set_xdata(np.arange(db_freq))
            im20.set_xdata(np.arange(db_freq))
            im21.set_xdata(np.arange(db_freq))
            im22.set_xdata(np.arange(db_freq))
            im23.set_xdata(np.arange(db_freq))
            im24.set_xdata(np.arange(db_freq))
            im25.set_xdata(np.arange(db_freq))

            # X Plot Y-Axis data points for XBar -------------------------------------------[# Channels]
            im10.set_ydata((TP[0]).rolling(window=tpS, min_periods=1).mean()[0:db_freq])  # Segment 1
            im11.set_ydata((TP[1]).rolling(window=tpS, min_periods=1).mean()[0:db_freq])  # Segment 2
            im12.set_ydata((TP[2]).rolling(window=tpS, min_periods=1).mean()[0:db_freq])  # Segment 3
            im13.set_ydata((TP[3]).rolling(window=tpS, min_periods=1).mean()[0:db_freq])  # Segment 4
            # ------ Evaluate Pp for Segments ---------#
            mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(tpHL, tpS, 'TP')
            # ---------------------------------------#
            im14.set_ydata((TP[4]).rolling(window=tpS, min_periods=1).mean()[0:db_freq])  # Segment 1
            im15.set_ydata((TP[5]).rolling(window=tpS, min_periods=1).mean()[0:db_freq])  # Segment 2
            im16.set_ydata((TP[6]).rolling(window=tpS, min_periods=1).mean()[0:db_freq])  # Segment 3
            im17.set_ydata((TP[7]).rolling(window=tpS, min_periods=1).mean()[0:db_freq])  # Segment 4
            # ------ Evaluate Pp for Ring 2 ---------#
            mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(tpHL, tpS, 'TP')

            # S Plot Y-Axis data points for StdDev ----------------------------------------[# S Bar Plot]
            im18.set_ydata((TP[0]).rolling(window=tpS, min_periods=1).std()[0:db_freq])
            im19.set_ydata((TP[1]).rolling(window=tpS, min_periods=1).std()[0:db_freq])
            im20.set_ydata((TP[2]).rolling(window=tpS, min_periods=1).std()[0:db_freq])
            im21.set_ydata((TP[3]).rolling(window=tpS, min_periods=1).std()[0:db_freq])

            im22.set_ydata((TP[4]).rolling(window=tpS, min_periods=1).std()[0:db_freq])
            im23.set_ydata((TP[5]).rolling(window=tpS, min_periods=1).std()[0:db_freq])
            im24.set_ydata((TP[6]).rolling(window=tpS, min_periods=1).std()[0:db_freq])
            im25.set_ydata((TP[7]).rolling(window=tpS, min_periods=1).std()[0:db_freq])


            # Compute entire Process Capability -----------#
            if not tpHL:
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLd, dLCLd, ppT, pkT, xline, sline = tq.tAutoPerf(tpS, mnA,
                                                                                                      mnB,
                                                                                                      0, 0, sdA,
                                                                                                      sdB, 0, 0)
            else:
                xline, sline = tpMean, tpDev
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLd, dLCLd, ppT, pkT = tq.tManualPerf(mnA, mnB, 0, 0, sdA, sdB,
                                                                                          0, 0, tpUSL, tpLSL, tpUCL,
                                                                                          tpLCL)
            # # Declare Plots attributes ------------------------------------------------------------[]
            # XBar Mean Plot
            a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
            a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 3 Sigma span (Purple)
            a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minTT, sBar_maxTT -------[]
            # Define Legend's Attributes  ----
            a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
            a2.axhspan(sLCLtp, sUCLtp, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 1 Sigma Span
            a2.axhspan(sUCLtp, sBar_maxTP, facecolor='#CCCCFF', edgecolor='#CCCCFF')  # 1 Sigma above the Mean
            a2.axhspan(sBar_minTP, sLCLtp, facecolor='#CCCCFF', edgecolor='#CCCCFF')

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
                a2.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a1.set_xlim(0, window_Xmax)
                a2.set_xlim(0, window_Xmax)

            # Set trip line for individual time-series plot -----------------------------------[R1]
            import triggerModule as sigma
            sigma.trigViolations(a1, UsePLC_DBS, 'TP', YScale_minTP, YScale_maxTP, xucT, xlcT, xusT, xlsT, mnT, sdT)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousTP, frames=None, save_count=100, repeat_delay=None,
                                interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

# ============================================= CASCADE CLASS METHODS ===============================================#
#                                                                                                                    #
# This class procedure allows SCADA operator to split the screen into respective runtime process                     #
#                                                                                                                    #
# ===================================================================================================================#

class cascadeCommonViewsRF(ttk.Frame):          # Load common Cascade and all object in cascadeSwitcher() class
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.createWidgetsRF()

    def createWidgetsRF(self):

        # Load metrics from config -----------------------------------[]
        if pRecipe == 'DNV':
            import qParamsHL_DNV as qp
        else:
            import qParamsHL_MGM as qp
        # ------------------------------------------------------------[]
        rfS, rfTy, rfSoL, rfSoP, rfHL, rfAL, rfFO, rfP1, rfP2, rfP3, rfP4, rfP5 = qp.decryptpProcessLim(pWON, 'RF')
        # Break down each element to useful list -----[Tape Temperature]

        if rfHL and rfP1 and rfP2 and rfP3 and rfP4 and rfP5:  #
            rfPerf = '$Pp_{k' + str(rfS) + '}$'  # Using estimated or historical Mean
            rflabel = 'Pp'
            # -------------------------------------[]
            One = rfP1.split(',')  # split into list elements
            Two = rfP2.split(',')
            Thr = rfP3.split(',')
            For = rfP4.split(',')
            Fiv = rfP5.split(',')
            # -------------------------------
            dTape1 = One[1].strip("' ")  # defined Tape Width
            dTape2 = Two[1].strip("' ")  # defined Tape Width
            dTape3 = Thr[1].strip("' ")  # defined Tape Width
            dTape4 = For[1].strip("' ")  # defined Tape Width
            dTape5 = Fiv[1].strip("' ")  # defined Tape Width
            # --------------------------------
            dLayer1 = One[10].strip("' ")  # Defined Tape Layer
            dLayer2 = Two[10].strip("' ")
            dLayer3 = Thr[10].strip("' ")
            dLayer4 = For[10].strip("' ")
            dLayer5 = Fiv[10].strip("' ")
            # Load historical limits for the process----#
            if cpLayerNo == 1:  # '22mm'|'18mm',  1-40 | 41+ TODO
                rfUCL = float(One[2].strip("' "))  # Strip out the element of the list
                rfLCL = float(One[3].strip("' "))
                rfMean = float(One[4].strip("' "))
                rfDev = float(One[5].strip("' "))
                # --------------------------------
                sUCLrf = float(One[6].strip("' "))
                sLCLrf = float(One[7].strip("' "))
                # --------------------------------
                rfUSL = (rfUCL - rfMean) / 3 * 6
                rfLSL = (rfMean - rfLCL) / 3 * 6
                # --------------------------------
            elif cpTapeW == dTape2 and cpLayerNo == 2:
                rfUCL = float(Two[2].strip("' "))  # Strip out the element of the list
                rfLCL = float(Two[3].strip("' "))
                rfMean = float(Two[4].strip("' "))
                rfDev = float(Two[5].strip("' "))
                # --------------------------------
                sUCLrf = float(Two[6].strip("' "))
                sLCLrf = float(Two[7].strip("' "))
                # --------------------------------
                rfUSL = (rfUCL - rfMean) / 3 * 6
                rfLSL = (rfMean - rfLCL) / 3 * 6
            elif cpTapeW == dTape3 and cpLayerNo == range(3, 40):
                rfUCL = float(Thr[2].strip("' "))  # Strip out the element of the list
                rfLCL = float(Thr[3].strip("' "))
                rfMean = float(Thr[4].strip("' "))
                rfDev = float(Thr[5].strip("' "))
                # --------------------------------
                sUCLrf = float(Thr[6].strip("' "))
                sLCLrf = float(Thr[7].strip("' "))
                # --------------------------------
                rfUSL = (rfUCL - rfMean) / 3 * 6
                rfLSL = (rfMean - rfLCL) / 3 * 6
            elif cpTapeW == dTape4 and cpLayerNo == 41:
                rfUCL = float(For[2].strip("' "))  # Strip out the element of the list
                rfLCL = float(For[3].strip("' "))
                rfMean = float(For[4].strip("' "))
                rfDev = float(For[5].strip("' "))
                # --------------------------------
                sUCLrf = float(For[6].strip("' "))
                sLCLrf = float(For[7].strip("' "))
                # --------------------------------
                rfUSL = (rfUCL - rfMean) / 3 * 6
                rfLSL = (rfMean - rfLCL) / 3 * 6
            else:
                rfUCL = float(Fiv[2].strip("' "))  # Strip out the element of the list
                rfLCL = float(Fiv[3].strip("' "))
                rfMean = float(Fiv[4].strip("' "))
                rfDev = float(Fiv[5].strip("' "))
                # --------------------------------
                sUCLrf = float(Fiv[6].strip("' "))
                sLCLrf = float(Fiv[7].strip("' "))
                # --------------------------------
                rfUSL = (rfUCL - rfMean) / 3 * 6
                rfLSL = (rfMean - rfLCL) / 3 * 6
                # -------------------------------
        else:  # Computes Shewhart constants (Automatic Limits)
            rfUCL = 0
            rfLCL = 0
            rfMean = 0
            rfDev = 0
            sUCLrf = 0
            sLCLrf = 0
            rfUSL = 0
            rfLSL = 0
            rfPerf = '$Cp_{k' + str(rfS) + '}$'  # Using Automatic group Mean
            rflabel = 'Cp'

        # ------ [End of Historical abstraction -------]
        label = ttk.Label(self, text='[' + rType + ' Mode - RF]', font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        # Define Axes ---------------------#
        fig = Figure(figsize=(12.5, 7), dpi=100)
        fig.subplots_adjust(left=0.04, bottom=0.033, right=0.988, top=0.957, hspace=0.14, wspace=0.195)
        # ---------------------------------[]
        a1 = fig.add_subplot(2, 4, (1, 3))  # X Bar Plot
        a2 = fig.add_subplot(2, 4, (5, 7))  # S Bar Plo
        a3 = fig.add_subplot(2, 4, (4, 8))  # Performance Feeed

        # Declare Plots attributes --------------------------------[]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minRF, YScale_maxRF = 10, 500
        sBar_minRF, sBar_maxRF = 10, 250                            # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (int(rfS) + 3)                # windows view = visible data points

        # ----------------------------------------------------------#
        # Real-Time Parameter according to updated requirements ----# 28/Feb/2025
        if rType == 1:
            T1 = SPC_RF
        else:
            T1 = 'RF1_' + pWON                                            # Roller Force
            T2 = 'RF2_' + pWON
        # ----------------------------------------------------------#

        # Common properties -------------------------------------------------#
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [" + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        a1.set_title('Roller Force [XBar Plot]', fontsize=12, fontweight='bold')
        a2.set_title('Roller Force [S Plot]', fontsize=12, fontweight='bold')
        # Apply grid lines -----
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a1.legend(loc='upper right', title='Roller Force (N.m)')
        a2.legend(loc='upper right', title='Sigma curve')

        # ----------------------------------------------------------#
        a1.set_ylim([YScale_minRF, YScale_maxRF], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        a2.set_ylim([sBar_minRF, sBar_maxRF], auto=True)
        a2.set_xlim([window_Xmin, window_Xmax])

        # ---------------------------------------------------------[]
        a3.cla()
        a3.get_yaxis().set_visible(False)
        a3.get_xaxis().set_visible(False)

        # ----------------------------------------------------------[]
        # Define Plot area and axes -
        # ----------------------------------------------------------#
        im10, = a1.plot([], [], 'o-', label='Roller Force - (R1H1)')
        im11, = a1.plot([], [], 'o-', label='Roller Force - (R1H2)')
        im12, = a1.plot([], [], 'o-', label='Roller Force - (R1H3)')
        im13, = a1.plot([], [], 'o-', label='Roller Force - (R1H4)')
        im14, = a2.plot([], [], 'o-', label='Roller Force')
        im15, = a2.plot([], [], 'o-', label='Roller Force')
        im16, = a2.plot([], [], 'o-', label='Roller Force')
        im17, = a2.plot([], [], 'o-', label='Roller Force')

        im18, = a1.plot([], [], 'o-', label='Roller Force - (R2H1)')
        im19, = a1.plot([], [], 'o-', label='Roller Force - (R2H2)')
        im20, = a1.plot([], [], 'o-', label='Roller Force - (R2H3)')
        im21, = a1.plot([], [], 'o-', label='Roller Force - (R2H4)')
        im22, = a2.plot([], [], 'o-', label='Roller Force')
        im23, = a2.plot([], [], 'o-', label='Roller Force')
        im24, = a2.plot([], [], 'o-', label='Roller Force')
        im25, = a2.plot([], [], 'o-', label='Roller Force')

        im26, = a1.plot([], [], 'o-', label='Roller Force - (R3H1)')
        im27, = a1.plot([], [], 'o-', label='Roller Force - (R3H2)')
        im28, = a1.plot([], [], 'o-', label='Roller Force - (R3H3)')
        im29, = a1.plot([], [], 'o-', label='Roller Force - (R3H4)')
        im30, = a2.plot([], [], 'o-', label='Roller Force')
        im31, = a2.plot([], [], 'o-', label='Roller Force')
        im32, = a2.plot([], [], 'o-', label='Roller Force')
        im33, = a2.plot([], [], 'o-', label='Roller Force')

        im34, = a1.plot([], [], 'o-', label='Roller Force - (R4H1)')
        im35, = a1.plot([], [], 'o-', label='Roller Force - (R4H2)')
        im36, = a1.plot([], [], 'o-', label='Roller Force - (R4H3)')
        im37, = a1.plot([], [], 'o-', label='Roller Force - (R4H4)')
        im38, = a2.plot([], [], 'o-', label='Roller Force')
        im39, = a2.plot([], [], 'o-', label='Roller Force')
        im40, = a2.plot([], [], 'o-', label='Roller Force')
        im41, = a2.plot([], [], 'o-', label='Roller Force')
        # -----------------------------------------------------------#
        # Statistical Feed -----------------------------------------[]
        a3.text(0.466, 0.945, 'Performance Feed - RF', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        a3.add_patch(rect1)
        a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)---------------------
        a3.text(0.145, 0.804, rflabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.658, '#Pp Value', fontsize=24, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.650, 0.820, 'Ring ' + rflabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        a3.text(0.145, 0.403, rfPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=22, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring ' + rfPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        # -------------------------------------
        a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ----- Pipe Position and SMC Status -----
        a3.text(0.080, 0.090, 'Pipe Position: ' + pPos + '    Processing Layer #' + layer, fontsize=12, ha='left',
                transform=a3.transAxes)
        a3.text(0.080, 0.036, 'SMC Status: ' + eSMC, fontsize=12, ha='left', transform=a3.transAxes)

        # ---------------- EXECUTE SYNCHRONOUS METHOD ---------------#
        def synchronousRF(rfS, rfTy, fetchT):
            fetch_no = str(fetchT)      # entry value in string sql syntax

            # Obtain Volatile Data from PLC Host Server ---------------------------[]
            if not inUseAlready:                    # Load CommsPlc class once
                import CommsSql as q
                q.DAQ_connect(1, 0)
            else:
                con_a, con_b = conn.cursor(), conn.cursor()

            # Evaluate conditions for SQL Data Fetch ------------------------------[A]
            """
            Load watchdog function with synchronous function every seconds
            """
            # Initialise RT variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard                         # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                if UsePLC_DBS:  # Not Using PLC Data
                    import plcArrayRLmethodRF as crf                    # DrLabs optimization method

                    inProgress = True  # True for RetroPlay mode
                    print('\nSynchronous controller activated...')

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve MSC from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    # Either of the 2 combo variables are assigned to trigger routine pause
                    if keyboard.is_pressed("ctrl") or not msctcp == 315 and not sysRun and not inProgress:
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            # play(error)                            # Pause mode with audible Alert
                            print("\nVisualization in Paused Mode...")
                    else:
                        autoSpcPause = False

                    # Play visualization ----------------------------------------------[]
                    print("Visualization in Play Mode...")
                    # -----------------------------------------------------------------[]

                    # Allow selective runtime parameter selection on production-critical process
                    rfMta = crf.plcExec(T1, rfS, rfTy, fetch_no)
                    rfMtb = 0

                else:
                    import sqlArrayRLmethodRF as crf  # DrLabs optimization method

                    inProgress = True  # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve M.State from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    if keyboard.is_pressed("Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            print("\nVisualization in Paused Mode...")
                        else:
                            autoSpcPause = False
                        print("Visualization in Real-time Mode...")
                    else:
                        # Get list of relevant SQL Tables using conn() --------------------[]
                        rfMta, rfMtb = crf.sqlExec(rfS, rfTy, con_a, con_b, T1, T2, fetchT)
                        print("Visualization in Play Mode...")
                    print('\nUpdating....')
                    # ------ Inhibit iteration ----------------------------------------------------------[]
                    """
                    # Set condition for halting real-time plots in watchdog class ---------------------
                    """
                    # TODO --- values for inhibiting the SQL processing
                    if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                        con_a.close()
                        con_b.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

            return rfMta, rfMtb

        # ================== End of synchronous Method ==========================

        def asynchronousRF(db_freq):
            timei = time.time()  # start timing the entire loop

            # Bistream Data Pooling Method ---------------------#
            rfMta, rfMtb = synchronousRF(rfS, rfTy, db_freq)    # data loading functions
            # --------------------------------------------------#

            if UsePLC_DBS == 1:
                import VarPLClp as rf

                viz_cycle = 10
                # Call synchronous data function ---------------[]
                columns = qrf.validCols(T1)  # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(rfMta, columns=columns)  # Include table data into python Dataframe
                cRF = rf.loadProcesValues(df1)  # Join data values under dataframe

            else:
                import VarSQLlp as rf                   # load SQL variables column names | rfVarSQL

                viz_cycle = 150
                g1 = qrf.validCols(T1)                  # Construct Data Column selSqlColumnsTFM.py
                d1 = pd.DataFrame(rfMta, columns=g1)    # Import into python Dataframe

                g2 = qla.validCols(T2)
                d2 = pd.DataFrame(rfMtb, columns=g2)

                # Concatenate all columns -----------[]
                df1 = pd.concat([d1, d2], axis=1)

                cRF = rf.loadProcesValues(df1)          # Join data values under dataframe
            print('\nSQL Content', df1.head(10))
            print("Memory Usage:", df1.info(verbose=False))  # Check memory utilization

            # -------------------------------------------------------------------------------------[]
            # Plot X-Axis data points -------- X Plot
            im10.set_xdata(np.arange(db_freq))
            im11.set_xdata(np.arange(db_freq))
            im12.set_xdata(np.arange(db_freq))
            im13.set_xdata(np.arange(db_freq))
            im14.set_xdata(np.arange(db_freq))
            im15.set_xdata(np.arange(db_freq))
            im16.set_xdata(np.arange(db_freq))
            im17.set_xdata(np.arange(db_freq))
            im18.set_xdata(np.arange(db_freq))
            im19.set_xdata(np.arange(db_freq))
            im20.set_xdata(np.arange(db_freq))
            im21.set_xdata(np.arange(db_freq))
            im22.set_xdata(np.arange(db_freq))
            im23.set_xdata(np.arange(db_freq))
            im24.set_xdata(np.arange(db_freq))
            im25.set_xdata(np.arange(db_freq))
            # ------------------------------- S Plot
            # ------------------------------- S Plot
            im26.set_xdata(np.arange(db_freq))
            im27.set_xdata(np.arange(db_freq))
            im28.set_xdata(np.arange(db_freq))
            im29.set_xdata(np.arange(db_freq))
            im30.set_xdata(np.arange(db_freq))
            im31.set_xdata(np.arange(db_freq))
            im32.set_xdata(np.arange(db_freq))
            im33.set_xdata(np.arange(db_freq))
            im34.set_xdata(np.arange(db_freq))
            im35.set_xdata(np.arange(db_freq))
            im36.set_xdata(np.arange(db_freq))
            im37.set_xdata(np.arange(db_freq))
            im38.set_xdata(np.arange(db_freq))
            im39.set_xdata(np.arange(db_freq))
            im40.set_xdata(np.arange(db_freq))
            im41.set_xdata(np.arange(db_freq))

            # X Plot Y-Axis data points for XBar --------------------------------------------[  # Ring 1 ]
            im10.set_ydata((cRF[0]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 1
            im11.set_ydata((cRF[1]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 2
            im12.set_ydata((cRF[2]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 3
            im13.set_ydata((cRF[3]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 1 ---------#
            mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(rfHL, rfS, 'RF')
            # ---------------------------------------#
            im14.set_ydata((cRF[4]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 1
            im15.set_ydata((cRF[5]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 2
            im16.set_ydata((cRF[6]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 3
            im17.set_ydata((cRF[7]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 2 ---------#
            mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(rfHL, rfS, 'RF')
            # ---------------------------------------#
            im18.set_ydata((cRF[8]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 1
            im19.set_ydata((cRF[9]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 2
            im20.set_ydata((cRF[10]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 3
            im21.set_ydata((cRF[11]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 3 ---------#
            mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(rfHL, rfS, 'RF')
            # ---------------------------------------#
            im22.set_ydata((cRF[12]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 1
            im23.set_ydata((cRF[13]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 2
            im24.set_ydata((cRF[14]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 3
            im25.set_ydata((cRF[15]).rolling(window=rfS, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 4 ---------#
            mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(rfHL, rfS, 'RF')
            # ---------------------------------------#
            # S Plot Y-Axis data points for StdDev ----------------------------------------
            im26.set_ydata((cRF[0]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im27.set_ydata((cRF[1]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im28.set_ydata((cRF[2]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im29.set_ydata((cRF[3]).rolling(window=rfS, min_periods=1).std()[0:db_freq])

            im30.set_ydata((cRF[4]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im31.set_ydata((cRF[5]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im32.set_ydata((cRF[6]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im33.set_ydata((cRF[7]).rolling(window=rfS, min_periods=1).std()[0:db_freq])

            im34.set_ydata((cRF[8]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im35.set_ydata((cRF[9]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im36.set_ydata((cRF[10]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im37.set_ydata((cRF[11]).rolling(window=rfS, min_periods=1).std()[0:db_freq])

            im38.set_ydata((cRF[12]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im39.set_ydata((cRF[13]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im40.set_ydata((cRF[14]).rolling(window=rfS, min_periods=1).std()[0:db_freq])
            im41.set_ydata((cRF[15]).rolling(window=rfS, min_periods=1).std()[0:db_freq])

            # Compute entire Process Capability -----------#
            if not rfHL:
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLb, ppT, pkT, xline, sline = tq.tAutoPerf(rfS, mnA, mnB,
                                                                                                      mnC, mnD, sdA,
                                                                                                      sdB, sdC, sdD)
            else:
                xline, sline = rfMean, rfDev
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLba, ppT, pkT = tq.tManualPerf(mnA, mnB, mnC, mnD, sdA, sdB,
                                                                                           sdC, sdD, rfUSL, rfLSL,
                                                                                           rfUCL,
                                                                                           rfLCL)

            # # Declare Plots attributes --------------------------------------------------------[]
            # XBar Mean Plot
            a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
            a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 3 Sigma span (Purple)
            a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minRF, sBar_maxRF -------[]
            # Define Legend's Attributes  ----
            a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
            a2.axhspan(sLCLrf, sUCLrf, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 1 Sigma Span
            a2.axhspan(sUCLrf, sBar_maxRF, facecolor='#CCCCFF', edgecolor='#CCCCFF')  # 1 Sigma above the Mean
            a2.axhspan(sBar_minRF, sLCLrf, facecolor='#CCCCFF', edgecolor='#CCCCFF')

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
                a2.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a1.set_xlim(0, window_Xmax)
                a2.set_xlim(0, window_Xmax)

            # Set trip line for individual time-series plot -----------------------------------[R1]
            import triggerModule as sigma
            sigma.trigViolations(a1, UsePLC_DBS, 'RF', YScale_minRF, YScale_maxRF, xucT, xlcT, xusT, xlsT, mnT, sdT)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(fig, asynchronousRF, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # Update Canvas -----------------------------------------------------[]
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)


class cascadeCommonViewsEoL(ttk.Frame):          # Load common Cascade and all object in cascadeSwitcher() class
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=1300, y=750)
        self.createWidgetsCT()

    def createWidgetsCT(self):
        oLS, oLTy = cDM, cSS
        # Load metrics from config -----------------------------------[]
        if pRecipe == 'DNV':
            import qParamsHL_DNV as qp
        else:
            import qParamsHL_MGM as qp
        # ------------------------------------------------------------[]

        label = ttk.Label(self, text="JIT - End of Layer Processing", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        # Define Axes ---------------------#
        fig = Figure(figsize=(12.5, 5.5), dpi=100)

        # Attempt to auto screen size ---
        fig.subplots_adjust(left=0.043, bottom=0.043, right=0.986, top=0.96, hspace=0.14, wspace=0.195)
        # ----------------------------------
        a1 = fig.add_subplot(2, 2, (1, 2))                          # Cell Tension X Bar Plot
        a2 = fig.add_subplot(2, 2, (3, 4))                          # Cell Tension s Plot

        # Declare Plots attributes --------------------------------[]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minEOL, YScale_maxEOL = 18.5, 38.5
        sBar_minEOL, sBar_maxEOL = 10, 250                          # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (int(oLS) + 3)                # windows view = visible data points

        # ----------------------------------------------------------#
        # Real-Time Parameter according to updated requirements ----# 28/Feb/2025
        T1 = 'RF1_' + pWON                                          # Roller Force
        T2 = 'RF2_' + pWON
        # ----------------------------------------------------------#

        # Common properties ----------------------------------------#
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [" + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        a1.set_title('Cell Tension [XBar Plot]', fontsize=12, fontweight='bold')
        a2.set_title('Cell Tension [SBar Plot]', fontsize=12, fontweight='bold')
        # Apply grid lines -----
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a1.legend(loc='upper right', title='Cell Tension Control Plot')
        a2.legend(loc='upper right', title='Sigma curve')

        # ---------------------------------------------------------#
        a1.set_ylim([YScale_minEOL, YScale_maxEOL], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ---------------------------------------------------------#
        a2.set_ylim([sBar_minEOL, sBar_maxEOL], auto=True)
        a2.set_xlim([window_Xmin, window_Xmax])

        # ---------------------------------------------------------[]
        # Define Plot area and axes -
        # ----------------------------------------------------------#
        im10, = a1.plot([], [], 'o-', label='Roller Force - (R1H1)')
        im11, = a1.plot([], [], 'o-', label='Roller Force - (R1H2)')
        im12, = a1.plot([], [], 'o-', label='Roller Force - (R1H3)')
        im13, = a1.plot([], [], 'o-', label='Roller Force - (R1H4)')
        im14, = a2.plot([], [], 'o-', label='Roller Force')
        im15, = a2.plot([], [], 'o-', label='Roller Force')
        im16, = a2.plot([], [], 'o-', label='Roller Force')
        im17, = a2.plot([], [], 'o-', label='Roller Force')


        # Define limits for X Bar Plots -----------------------#
        a1.axhline(y=hMeanB, color="green", linestyle="-", linewidth=1)
        a1.axhspan(hLCLb, hUCLb, facecolor='#A9EF91', edgecolor='#A9EF91')  # Light Green
        # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
        a1.axhspan(hUCLb, hUSLb, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
        a1.axhspan(hLSLb, hLCLb, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
        # clean up when Mean line changes ---
        a1.axhspan(hUSLb, hUSLb + 10, facecolor='#FFFFFF', edgecolor='#FFFFFF')
        a1.axhspan(hLSLb - 10, hLSLb, facecolor='#FFFFFF', edgecolor='#FFFFFF')

        # Define limits for S Bar Plot -----------------------#
        a2.axhline(y=hDevB, color="green", linestyle="-", linewidth=1)
        a2.axhspan(dLCLb, dUCLb, facecolor='#A9EF91', edgecolor='#A9EF91')  # Light Green

        # clean up when Mean line changes ---
        a2.axhspan(dUCLb, dUCLb + 0.005, facecolor='#FFFFFF', edgecolor='#FFFFFF')
        a2.axhspan(dLCLb - 0.05, dLCLb, facecolor='#FFFFFF', edgecolor='#FFFFFF')

        # Model data --------------------------------------------------[]
        a1.plot([105, 120, 114, 109, 110, 86, 102, 103, 101, 100])
        # -------------------------------------------------------------[]
        # Calibrate the rest of the Plots -----------------------------#
        # ----------------------------------------------------------[]
        # Define Plot area and axes -
        # ----------------------------------------------------------#
        im10, = a1.plot([], [], 'o-', label='Cell Tension A (N/mm2)')
        im11, = a1.plot([], [], 'o-', label='Cell tension B (N/mm2)')


        # ---------------- EXECUTE SYNCHRONOUS METHOD ---------------#
        def synchronousEoL(smp_Sz, smp_St, fetchT):
            fetch_no = str(fetchT)  # entry value in string sql syntax
            # Obtain SQL Data Host Server ---------------------------[]
            qRP = conn.cursor()

            # Evaluate conditions for SQL Data Fetch ---------------[A]
            """
            Load watchdog function with synchronous function every seconds
            """
            # Initialise RT variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard  # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                # print('Indefinite looping...')
                import sqlArrayRLmethodCT as ct  # DrLabs optimization method
                inProgress = True  # True for RetroPlay mode
                print('\nAsynchronous controller activated...')
                print('DrLabs' + "' Runtime Optimisation is Enabled!")

                # Get list of relevant SQL Tables using conn() --------------------[]
                ctData = ct.sqlexec(smp_Sz, smp_St, qRP, tblID, fetchT)  # perform DB connections
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    qRP.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

            return ctData

        # ================== End of synchronous Method ==========================

        def asynchronousEoL(db_freq):

            timei = time.time()  # start timing the entire loop

            # Call data loader Method---------------------------#
            ctSQL = synchronousEoL(smp_Sz, stp_Sz, db_freq)      # data loading functions

            import VarSQLct as qct                              # load SQL variables column names | rfVarSQL
            viz_cycle = 150
            g1 = qc.validCols('CT')                             # Construct Data Column selSqlColumnsTFM.py
            df1 = pd.DataFrame(ctSQL, columns=g1)               # Import into python Dataframe
            RF = qct.loadProcesValues(df1)                      # Join data values under dataframe
            print('\nDataFrame Content', df1.head(10))          # Preview Data frame head
            print("Memory Usage:", df1.info(verbose=False))     # Check memory utilization

            # Declare Plots attributes ------------------------------------------------------------[]
            a1.grid(color="0.5", linestyle='-', linewidth=0.5)
            a1.legend(loc='upper left', title='XBar Plot')
            # -------------------------------------------------------------------------------------[]
            # Plot X-Axis data points -------- X Plot
            im10.set_xdata(np.arange(db_freq))
            im11.set_xdata(np.arange(db_freq))
            # X Plot Y-Axis data points for XBar -------------------------------------------[# Channels]
            im10.set_ydata((RF[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
            im11.set_ydata((RF[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
            if not useHL and not pMinMax:  # switch to control plot on shewhart model
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLd, dLCLd, ppT, pkT, xline, sline = tq.tAutoPerf(smp_Sz, mnA,
                                                                                                      mnB,
                                                                                                      0, 0, sdA,
                                                                                                      sdB, 0, 0)
            else:  # switch to historical limits
                xline, sline = hMeanA, hDevA

            # # Declare Plots attributes ------------------------------------------------------------[]
            # XBar Mean Plot
            a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
            a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 3 Sigma span (Purple)
            a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minTG, sBar_maxTG -------[]
            # Setting up the parameters for moving windows Axes ---[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a1.set_xlim(0, window_Xmax)

            # Set trip line for individual time-series plot -----[R1]
            # No trigger module processing - Production parameter is for monitoring purposes only.
            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousEoL, frames=None, save_count=100, repeat_delay=None,
                                interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # Update Canvas ---------------------------------------------------[]
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)


class cascadeCommonViewsRPT(ttk.Frame):                                # End of Layer Progressive Report Tabb
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        # self.grid(column=0, row=0, padx=10, pady=10)
        self.place(x=10, y=750)
        self.createWidgets()

    def createWidgets(self):
        label = ttk.Label(self, text="End of Layer - Progressive Summary:                                          ", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        # label.place(x=100, y=50)
        # Define Axes ---------------------#
        combo = ttk.Combobox(self, values=["= Select Progressive Report =", "View EoL Curve", "Roller Pressure",
                                           "Tape Temperature", "Subs Temperature", "Winding Speed", "Gap Measurement",
                                           "Generate EoL Report", "Generate EoP Report"], width=25)
        combo.place(x=520, y=10)
        combo.current(0)

        # Create empty Text Space -----------------------------------
        text_widget = tk.Text(self, wrap='word', width=155, height=80)
        text_widget.pack(padx=10, pady=10)

        def option_selected(event):
            selected_option = combo.get()
            if selected_option == "View EoL Curve":
                # rpt = "RPT_EL_" + str(processWON[0])
                cascadeCommonViewsEoL()
            elif selected_option == "Roller Pressure":
                rpt = "RPT_RP_" + str(processWON[0])
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder
            elif selected_option == "Tape Temperature":
                rpt = "RPT_TT_" + str(processWON[0])
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder
            elif selected_option == "Subs Temperature":
                rpt = "RPT_ST_" + str(processWON[0])
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder
            elif selected_option == "Winding Speed":
                rpt = "RPT_WS_" + str(processWON[0])
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder
            elif selected_option == "Gap Measurement":
                rpt = "RPT_TG_" + str(processWON[0])
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder
            else:
                rpt = "VOID_REPORT"
                readEoP(text_widget, rpt)                                 # Clean up the matt instead

            print("You selected:", selected_option)
        combo.bind("<<ComboboxSelected>>", option_selected)

        # Update Canvas -----------------------------------------------------[NO FIGURE YET]
        # canvas = FigureCanvasTkAgg(fig, self)
        # canvas.get_tk_widget().pack(expand=False)

        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True)


# ====================================================== MAIN PIPELINE ===========================================[]
# qType = 0   # default play mode


def userMenu():     # listener, myplash
    print('Welcome to RL Synchronous SPC....')
    global sqlRO, metRO, root, HeadA, HeadB, vTFM, comboL, comboR, qType

    # splash = myplash
    # del splash Turn off Splash timer -----[]

    print('Timer Paused for GUI...')

    # inherit PID from Splash Screen and transfer back when Object closes
    print('\nUser Menu: Inherited PARENT ID#:', os.getppid())
    print('User Menu: Inherited CHILD ID#:', os.getpid())
    print('User Menu: New Object THREAD:', get_native_id())
    time.sleep(2)

    # for windows centralizing ---------[]
    window_height = 580     #1080
    window_width = 950      #1920

    root.title('Synchronous SPC - ' + strftime("%a, %d %b %Y", gmtime()))
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Coordinates of the upper left corner of the window to make the window appear in the center
    x_cordinate = int((screen_width / 2) - (window_width / 2))
    y_cordinate = int((screen_height / 2) - (window_height / 2))
    root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
    # root.geometry("%dx%d" % (screen_width, screen_height))

    # canvas = autoResizableCanvas(root)
    # filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))
    icon1 = 'C:\\CuttingEdge\\SPC_ver12\\crb.png'
    # --------------------------------------------------------------------------------------[]

    # Define volatile runtime variables -------------------[]
    svar1 = IntVar()

    sqlRO = False       # SQL server filed is read only
    metRO = False

    def clearFields():  # for SQL server credentials -------
        # clear the content of text entry box
        if sub_menu.entrycget(0, 'state') == 'disabled' and sub_menu.entrycget(1, 'state') == 'normal':
            seripSql.set('')
            sqlid.set('')
            uname.set('')
            autho.set('')
            Entry(pop, state='normal', textvariable=seripSql).place(x=86, y=60)
            Entry(pop, state='normal', textvariable=sqlid).place(x=86, y=100)
            Entry(pop, state='normal', textvariable=uname).place(x=330, y=60)
            Entry(pop, state='normal', textvariable=autho, show="*").place(x=330, y=100)

        elif sub_menu.entrycget(1, 'state') == 'disabled' and sub_menu.entrycget(0, 'state') == 'normal':
            hostIPv4.set('')
            hostName.set('')
            deviceNm.set('')
            authopwd.set('')
            Entry(pop, state='normal', width=15, textvariable=hostIPv4).place(x=105, y=60)
            Entry(pop, state='normal', width=15, textvariable=hostName).place(x=105, y=100)
            Entry(pop, state='normal', width=15, textvariable=deviceNm).place(x=330, y=60)
            Entry(pop, state='normal', width=15, textvariable=authopwd, show="*").place(x=330, y=100)
        else:
            pass
        sqlRO = True
        print('Read Only Field State:', sqlRO)

        return sqlRO

    # function to allow historical limits entry---------------------------------------------[]
    def errorConfig():
        messagebox.showerror("Configuration:", "Enable Statistic on Two Parameters")

    def errorNote():
        messagebox.showerror('Error', 'Empty field(s)')
        return

    def successNote():
        messagebox.showinfo('Saved', 'Config Saved')
        return

    def save_pMetrics():                    # Save historical Limits for Production Parameters
        print("\nSaving Production Constants..")
        grayOut = [button2, e7, e8, m1, m2, m3, m4, m5, m6]             # set value entry field to read only
        e5.config(state='readonly')                                     # applicable to combo drop down
        e6.config(state='readonly')                                     # combo box property

        for fld in grayOut:
            fld.config(state="disabled")                                # for text fields
        if hLmtA.get() == 1:                                            # check condition of edit button
            hLmtA.set(0)                                                # uncheck the button
        s_butt.config(state="disabled")                                 # disable Save button

        print('\nStacked Values:', rtValues)
        print('Array Length', len(rtValues))

        # print('Switch Values', rtValues[-1])
        if len(rtValues) > 1:                                           # Compute the length for dynamic arrays
            x = len(rtValues) - 1                                       # Use the last index
            print('\nTest Vars:', m1, m2, m3, m4, m5, m6)

            # Encrypt configuration on production params ---------------#
            dd.saveMetricspP(processWON[0],  rMode, sel_SS, sel_gT, LA, LP, CT, OT, RP, WS, sSta, sEnd, rtValues[x][0], rtValues[x][1], rtValues[x][2],
                             rtValues[x][3], rtValues[x][4], rtValues[x][5], rtValues[x][6])
        else:
            print('\nTest Vars:', m1, m2, m3, m4, m5, m6)
            dd.saveMetricspP(processWON[0], rMode, sel_SS, sel_gT, LA, LP, CT, OT, RP, WS, sSta, sEnd, xlp, xla, xtp, xrf, xtt, xst, xtg)

        return


    def clearMetrics():
        # clear the content of chart parameter using change settings button ---
        global e5, e6, e7, e8, m1, m2, m3, m4, m5, m6, metRO, clearM

        # pop = Toplevel(root)
        # pop.wm_attributes('-topmost', True)
        clearM = 1
        if clearM:
            sSta.set('07:00:00')
            sEnd.set('17:00:00')
            e5 = Entry(pop, width=8, state='normal', textvariable=sSta)
            e5.place(x=290, y=10)  # Shift starts
            e6 = Entry(pop, width=8, state='normal', textvariable=sEnd)
            e6.place(x=290, y=40)  # Shift ends

            e7 = ttk.Combobox(pop, width=10, values=[" Select", "10", "15", "20", "23", "25", "30"], state="normal")
            e7.bind("<<ComboboxSelected>>", display_sel)
            e7.place(x=100, y=10)

            e8 = ttk.Combobox(pop, width=10, values=["SS-Domino", "GS-Discrete"], state="normal")
            e8.bind("<<ComboboxSelected>>", display_selection)
            e8.place(x=100, y=40)

            s_butt.config(state="normal")  # enable edit button (Sve Details) on entry
            # mp.ppHLderivation(pop, gSize1, gSize2, xUCLLP, xLCLLP, xUCLLA, xLCLLA)

            metRO = True
        else:
            clearM = 0
            metRO = False
        print('SQL Field State:', metRO, clearM)  # metric fields set to read only

        return
    # ------------------------------

    def display_selection(event):
        global sel_gT

        # Get the selected value.
        sel_gT = e8.get()
        if sel_gT == "S-Domino":  # butterfly effect/small change
            messagebox.showinfo(message="Combines the rising/falling edges of previous subgroup",
                                title=f"{sel_gT} Group")
        elif sel_gT == "F-Discrete":
            messagebox.showinfo(message="Evaluates new subgroup samples in the order of index", title=f"{sel_gT} Group")
        else:
            pass
        # print("The drop-down has been opened!")
        print('Selected Group Type:', sel_gT)
        return

    def display_sel(event):
        global sel_SS

        # Get the selected value ------#
        sel_SS = e7.get()
        if sel_SS == "10":
            messagebox.showinfo(message="Computed Mean with A3=0.975, B3=0.284, B4=1.716",
                                title=f"{sel_SS} Sample Size")
        elif sel_SS == "15":  # Unstable Domino
            messagebox.showinfo(message="Computed Mean with A3=0.789, B3=0.428, B4=1.572",
                                title=f"{sel_SS} Sample Size")
        elif sel_SS == "20":
            messagebox.showinfo(message="Computed Mean with A3=0.680, B3=0.510, B4=1.490",
                                title=f"{sel_SS} Sample Size")
        elif sel_SS == "23":
            messagebox.showinfo(message="Computed Mean with A3=0.633, B3=0.545, B4=1.455",
                                title=f"{sel_SS} Sample Size")
        elif sel_SS == "25":
            messagebox.showinfo(message="Computed Mean with A3=0.606, B3=0.565, B4=1.435",
                                title=f"{sel_SS} Sample Size")
        elif sel_SS == "30":
            messagebox.showinfo(message="Computed Mean with A3=0.553, B3=0.604, B4=1.396",
                                title=f"{sel_SS} Sample Size")
        else:
            pass
        print('\nSelected Sample Size:', sel_SS)

        return


    def dMinMaxPlot():
        global pStat, dMax, mMax, oMax, OT, CT, RP, WS, LP, LA, m1, m2, m3, m4, m5, m6, xlp, xla, xtp, xrf, xtt, xst, xtg
        if dnvMinMax.get():
            print('\nMonitoring Parameters for DNV Production..')
            dMax = 1
            mMax = 0
            oMax = 0
            pStat = 1
            dnvMinMax.set(dMax)
            mgmMinMax.set(mMax)
            othMinMax.set(oMax)

            # Set Production Parameter on DNV Params Monitor
            mOT.set(1)      # Oven Temperature
            mCT.set(1)      # Cell Tension
            mRP.set(1)      # Roller Pressure
            mWS.set(1)      # Tape Winding Speed
            # --------
            mLA.set(0)      # Laser Angle
            mLP.set(0)      # Laser Power
            # ----------------------------------------------------
            if metRO:
                # repopulate with default values -----------#
                m1 = Checkbutton(pop, text="Oven Temperature", font=("bold", 10), variable=mOT, state="disabled")
                m1.place(x=10, y=y_start)

                m2 = Checkbutton(pop, text="Active Cell Tension", font=("bold", 10), variable=mCT, state="disabled")
                m2.place(x=150, y=y_start)

                m3 = Checkbutton(pop, text="Tape Winding Spd", font=("bold", 10), variable=mWS, state="disabled")
                m3.place(x=10, y=y_start + y_incmt * 1)

                m4 = Checkbutton(pop, text="Reinforced Pressure", font=("bold", 10), variable=mRP, state="disabled")
                m4.place(x=150, y=y_start + y_incmt * 1)

                # -------------------------------------------- Not included in DNV/MGM requirements
                m5 = Checkbutton(pop, text="Laser Power", font=("bold", 10), variable=mLP, state="disabled")
                m5.place(x=305, y=y_start)

                m6 = Checkbutton(pop, text="Laser Angle", font=("bold", 10), variable=mLA, state="disabled")
                m6.place(x=305, y=y_start + y_incmt * 1)
                # -----------------------------------
            OT, CT, WS, RP, LP, LA = 1, 1, 1, 1, 0, 0
            xlp, xla, xtp, xrf, xtt, xst, xtg = 0, 0, 0, 0, 1, 1, 1
        # -----------End of Parameters ---------------
        else:
            dMax = 0
            mMax = 0        # Defaulted to Commercial Production
            oMax = 0
            pStat = 0
            dnvMinMax.set(dMax)
            mgmMinMax.set(mMax)
            othMinMax.set(oMax)
            mOT.set(0)
            mCT.set(0)
            mRP.set(0)
            mWS.set(0)
            OT, CT, WS, RP, LP, LA = 0, 0, 0, 0, 0, 0
            xlp, xla, xtp, xrf, xtt, xst, xtg = 0, 0, 0, 0, 0, 0, 0

        print('Monitoring DNV Params:', OT, CT, WS, RP, LP, LA, 'Plot Stats:', pStat)
        return OT, CT, WS, RP, LP, LA

    def mMinMaxPlot():
        global pStat, dMax, mMax, oMax, OT, CT, WS, RP, LP, LA, xlp, xla, xtp, xrf, xtt, xst, xtg, m1, m2, m3, m4, m5, m6
        if mgmMinMax.get():
            print('\nMonitoring Parameters for Commercial Production..')
            dMax = 0
            mMax = 1
            oMax = 0
            pStat = 1
            dnvMinMax.set(dMax)
            mgmMinMax.set(mMax)
            othMinMax.set(oMax)
            # Set default Monitoring params for MGM
            mOT.set(1)  # Oven Temperature
            mCT.set(1)  # Cell Tension
            mRP.set(1)  # Roller Pressure
            mWS.set(1)  # Tape Winding Speed
            # --------
            mLA.set(1)  # Laser Angle
            mLP.set(1)  # Laser Power
            # ----------------------------------------------------[]
            if metRO:
                # repopulate with default values -----------#
                m1 = Checkbutton(pop, text="Oven Temperature", font=("bold", 10), variable=mOT, state="disabled")
                m1.place(x=10, y=y_start)
                mOT.set(1)

                m2 = Checkbutton(pop, text="Active Cell Tension", font=("bold", 10), variable=mCT, state="disabled")
                m2.place(x=150, y=y_start)  # x=160
                mCT.set(1)

                m3 = Checkbutton(pop, text="Tape Winding Spd", font=("bold", 10), variable=mWS, state="disabled")
                m3.place(x=10, y=y_start + y_incmt * 1)
                mWS.set(1)

                m4 = Checkbutton(pop, text="Reinforced Pressure", font=("bold", 10), variable=mRP, state="disabled")
                m4.place(x=150, y=y_start + y_incmt * 1)
                mRP.set(1)
                # -------------------------------------------- Not included in DNV/MGM requirements
                m5 = Checkbutton(pop, text="Laser Power", font=("bold", 10), variable=mLP, state="disabled")
                m5.place(x=305, y=y_start)

                m6 = Checkbutton(pop, text="Laser Angle", font=("bold", 10), variable=mLA, state="disabled")
                m6.place(x=305, y=y_start + y_incmt * 1)
            # --------Summary of Monitors -----------
            OT, CT, WS, RP, LP, LA = 1, 1, 1, 1, 1, 1
            xlp, xla, xtp, xrf, xtt, xst, xtg = 1, 1, 1, 1, 1, 1, 1
            # -----------End of Parameters ----------
        else:
            dMax = 0
            mMax = 0                # Defaulted to Commercial Production
            oMax = 0
            pStat = 0
            dnvMinMax.set(dMax)
            mgmMinMax.set(mMax)
            othMinMax.set(oMax)
            mLA.set(0)
            mLP.set(0)
            mCT.set(0)
            mOT.set(0)
            mRP.set(0)
            mWS.set(0)
            # ---------
            OT, CT, WS, RP, LP, LA = 0, 0, 0, 0, 0, 0
            xlp, xla, xtp, xrf, xtt, xst, xtg = 0, 0, 0, 0, 0, 0, 0

        print('Monitoring MGM Params:', OT, CT, WS, RP, LP, LA, 'Plot Stats:', pStat)
        return OT, CT, WS, RP, LP, LA


    def runChecksPQ():
        global usepHL
        # Do a toggle from Historical limits checkbutton to enforce one choice --------[]
        if hLmtA.get():
            button2.config(state="normal")
            hLmtA.set(1)
            usepHL = True  # Use production parameter historical limits
        else:
            button2.config(state="disabled")
            hLmtA.set(0)
            usepHL = False

        return usepHL

    def mgmChecksA():
        if pLP.get():
            pLP.set(1)
            pLA.set(0)
            pTP.set(0)
            pRF.set(0)
            pTT.set(0)
            pST.set(0)
            pTG.set(0)
            hlb.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pLP, pLA, pTP, pRF, pTT, pST, pTG)
        else:
            pLP.set(0)

    # ------------------------
    def mgmChecksB():
        if pLA.get():
            pLP.set(0)
            pLA.set(1)
            pTP.set(0)
            pRF.set(0)
            pTT.set(0)
            pST.set(0)
            pTG.set(0)
            hlb.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pLP, pLA, pTP, pRF, pTT, pST, pTG)
        else:
            pLA.set(0)

    # ------------------------
    def mgmChecksC():
        if pTP.get():
            pLP.set(0)
            pLA.set(0)
            pTP.set(1)
            pRF.set(0)
            pTT.set(0)
            pST.set(0)
            pTG.set(0)
            hlb.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pLP, pLA, pTP, pRF, pTT, pST, pTG)
        else:
            pTP.set(0)

    # ------------------------
    def mgmChecksD():
        if pRF.get():
            pLP.set(0)
            pLA.set(0)
            pTP.set(0)
            pRF.set(1)
            pTT.set(0)
            pST.set(0)
            pTG.set(0)
            hlb.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pLP, pLA, pTP, pRF, pTT, pST, pTG)
        else:
            pRF.set(0)

    # ------------------------
    def mgmChecksE():
        if pTT.get():
            pLP.set(0)
            pLA.set(0)
            pTP.set(0)
            pRF.set(0)
            pTT.set(1)
            pST.set(0)
            pTG.set(0)
            hlb.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pLP, pLA, pTP, pRF, pTT, pST, pTG)
        else:
            pTT.set(0)

    # ------------------------
    def mgmChecksF():
        if pST.get():
            pLP.set(0)
            pLA.set(0)
            pTP.set(0)
            pRF.set(0)
            pTT.set(0)
            pST.set(1)
            pTG.set(0)
            hlb.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pLP, pLA, pTP, pRF, pTT, pST, pTG)
        else:
            pST.set(0)

    # ------------------------
    def mgmChecksG():
        if pTG.get():
            pLP.set(0)
            pLA.set(0)
            pTP.set(0)
            pRF.set(0)
            pTT.set(0)
            pST.set(0)
            pTG.set(1)
            hlb.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pLP, pLA, pTP, pRF, pTT, pST, pTG)
        else:
            pLA.set(0)

    def runChecksB():
        if pTT.get():
            pTT.set(1)
            pRP.set(0)
            pST.set(0)
            pWS.set(0)
            pTG.set(0)
            hla.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pRP, pTT, pST, pWS, pTG)
        else:
            pTT.set(0)

    def runChecksC():
        if pST.get():
            pST.set(1)
            pRP.set(0)
            pTT.set(0)
            pWS.set(0)
            pTG.set(0)
            hla.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pRP, pTT, pST, pWS, pTG)
        else:
            pST.set(0)

    def runChecksD():
        if pWS.get():
            pWS.set(1)
            pRP.set(0)
            pTT.set(0)
            pST.set(0)
            pTG.set(0)
            hla.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pRP, pTT, pST, pWS, pTG)
        else:
            pWS.set(0)

    def runChecksE():
        if pTG.get():
            pTG.set(1)
            pRP.set(0)
            pTT.set(0)
            pST.set(0)
            pWS.set(0)
            hla.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pRP, pTT, pST, pWS, pTG)
        else:
            pTG.set(0)


    def dnvConfigs():
        global modal, pRP, pTT, pST, pWS, pTG

        # prevent parent window closure until 'Save settings' ---[]
        root.protocol("WM_DELETE_WINDOW", preventClose)  # prevent closure even when using (ALT + F4)
        # -------------------------------------------------------[]

        modal = Toplevel(root)
        modal.wm_attributes('-topmost', True)

        pRP, pTT, pST, pWS, pTG = IntVar(), IntVar(), IntVar(), IntVar(), IntVar()

        # ----------------------------------------------------------------------------------[]
        modal.resizable(False, False)

        w, h = 615, 250
        modal.title('Lookup Table: Define Historical Limits')
        screen_w = modal.winfo_screenwidth()
        screen_h = modal.winfo_screenheight()
        x_c = int((screen_w / 2) - (w / 2))
        y_c = int((screen_h / 2) - (h / 2))
        modal.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))

        # ----------------------------------------------------------------------------------[]
        # a1 = Checkbutton(modal, text="RollerPressure", font=("bold", 10), variable=pRP, command=runChecksA)
        # a1.place(x=20, y=10)
        a2 = Checkbutton(modal, text="TapeTemp", font=("bold", 10), variable=pTT, command=runChecksB)
        # a2.place(x=145, y=10)
        a2.place(x=20, y=10)

        a3 = Checkbutton(modal, text="SubstrateTemp", font=("bold", 10), variable=pST, command=runChecksC)
        a3.place(x=250, y=10)

        # a4 = Checkbutton(modal, text="WindingSpeed", font=("bold", 10), variable=pWS, command=runChecksD)
        # a4.place(x=380, y=10)

        a5 = Checkbutton(modal, text="TapeGaps", font=("bold", 10), variable=pTG, command=runChecksE)
        a5.place(x=500, y=10)

        separator = ttk.Separator(modal, orient='horizontal')
        separator.place(relx=0.01, rely=0.17, relwidth=0.98, relheight=0.02)

        # ----------------------------------------[Laser Power]
        Label(modal, text='Tape Size').place(x=10, y=50)
        Label(modal, text='x̄UCL').place(x=80, y=50)
        Label(modal, text='x̄LCL').place(x=140, y=50)
        Label(modal, text='ŝUCL').place(x=200, y=50)
        Label(modal, text='ŝLCL').place(x=260, y=50)

        Label(modal, text='x̄Mean').place(x=320, y=50)
        Label(modal, text='ŝMean').place(x=380, y=50)
        Label(modal, text='x̄USL').place(x=440, y=50)
        Label(modal, text='x̄LSL').place(x=500, y=50)

        Label(modal, text='Layer(s)').place(x=550, y=50)

        # # Add Button for making selection -----------------------------------------------------[]
        # rf = Button(modal, text="Save " + pTy + " Metrics", command=saveMetricRP, bg="green", fg="white")
        # rf.place(x=254, y=200)
        return

# ------------------------------------------------------------------------------------------------[]
    def mgmConfigs():
        global modal, pLP, pLA, pTP, pRF, pTT, pST, pTG

        # prevent parent window closure until 'Save settings' ---[]
        root.protocol("WM_DELETE_WINDOW", preventClose)  # prevent closure even when using (ALT + F4)
        # -------------------------------------------------------[]

        modal = Toplevel(root)
        modal.wm_attributes('-topmost', True)

        pLP, pLA, pTP, pRF, pTT, pST, pTG = IntVar(), IntVar(), IntVar(), IntVar(), IntVar(), IntVar(), IntVar()

        # ----------------------------------------------------------------------------------------[]
        modal.resizable(False, False)

        w, h = 750, 250
        modal.title('Lookup Table: Define Historical Limits')
        screen_w = modal.winfo_screenwidth()
        screen_h = modal.winfo_screenheight()
        x_c = int((screen_w / 2) - (w / 2))
        y_c = int((screen_h / 2) - (h / 2))
        modal.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))

        # --------------------------------------------------------[]
        a1 = Checkbutton(modal, text="Laser Power", font=("bold", 10), variable=pLP, command=mgmChecksA)
        a1.place(x=20, y=10)

        a2 = Checkbutton(modal, text="Laser Angle", font=("bold", 10), variable=pLA, command=mgmChecksB)
        a2.place(x=120, y=10)

        a3 = Checkbutton(modal, text="Tape Error", font=("bold", 10), variable=pTP, command=mgmChecksC)
        a3.place(x=220, y=10)

        a4 = Checkbutton(modal, text="Roller Force", font=("bold", 10), variable=pRF, command=mgmChecksD)
        a4.place(x=320, y=10)

        a5 = Checkbutton(modal, text="Tape Temp", font=("bold", 10), variable=pTT, command=mgmChecksE)
        a5.place(x=420, y=10)

        a6 = Checkbutton(modal, text="Substrate Temp", font=("bold", 10), variable=pST, command=mgmChecksF)
        a6.place(x=520, y=10)

        a7 = Checkbutton(modal, text="Tape Gaps", font=("bold", 10), variable=pTG, command=mgmChecksG)
        a7.place(x=650, y=10)

        separator = ttk.Separator(modal, orient='horizontal')
        separator.place(relx=0.01, rely=0.17, relwidth=0.98, relheight=0.02)

        # --------------------------------------------[LP]
        Label(modal, text='Tape Size').place(x=10, y=50)
        Label(modal, text='x̄UCL').place(x=80, y=50)
        Label(modal, text='x̄LCL').place(x=140, y=50)
        Label(modal, text='ŝUCL').place(x=200, y=50)
        Label(modal, text='ŝLCL').place(x=260, y=50)

        Label(modal, text='x̄Mean').place(x=380, y=50)
        Label(modal, text='ŝMean').place(x=440, y=50)
        Label(modal, text='x̄USL').place(x=500, y=50)
        Label(modal, text='x̄LSL').place(x=560, y=50)

        Label(modal, text='Tape Layer(s)').place(x=660, y=50)
        # 550, 670
        # # Add Button for making selection -----------------------------------------------------[]
        # rf = Button(modal, text="Save " + pTy + " Metrics", command=saveMetricRP, bg="green", fg="white")
        # rf.place(x=254, y=200)
        return

    def enDNV():
        global dnv, mgm, aut
        if pLmtA.get():
            dnv = 1
            mgm = 0
            aut = 0
            dnv_butt.config(state="normal")
            mgm_butt.config(state="disabled")
            pLmtA.set(dnv)
            shewhart.set(aut)
            pLmtB.set(mgm)
        else:
            dnv = 1
            mgm = 0
            aut = 0
            dnv_butt.config(state="disabled")
            mgm_butt.config(state="disabled")
            pLmtA.set(dnv)
            shewhart.set(aut)
            pLmtB.set(mgm)

        return dnv, mgm, aut

    def enAUTO():
        global dnv, mgm, aut
        if shewhart.get():
            dnv = 0
            mgm = 0
            aut = 1
            dnv_butt.config(state="disabled")
            mgm_butt.config(state="disabled")
            pLmtA.set(dnv)
            shewhart.set(aut)
            pLmtB.set(mgm)
        else:
            dnv = 0
            mgm = 0
            aut = 1
            dnv_butt.config(state="disabled")
            mgm_butt.config(state="disabled")
            pLmtA.set(dnv)
            shewhart.set(aut)
            pLmtB.set(mgm)

        return dnv, mgm, aut

    def enMGM():
        global dnv, mgm, aut
        if pLmtB.get():
            dnv = 0
            mgm = 1
            aut = 0
            mgm_butt.config(state="normal")
            dnv_butt.config(state="disabled")
            pLmtA.set(dnv)
            shewhart.set(aut)
            pLmtB.set(mgm)
        else:
            dnv = 0
            mgm = 1
            aut = 0
            mgm_butt.config(state="disabled")
            dnv_butt.config(state="disabled")
            pLmtA.set(dnv)
            shewhart.set(aut)
            pLmtB.set(mgm)

        return dnv, mgm, aut

    def watchDG():
        global rMode, HeadA, HeadB, closeV
        if pWDG.get():
            rMode = 1                   # set auto synchronous mode
            process.entryconfig(0, state='disabled')
            process.entryconfig(1, state='disabled')
            process.entryconfig(3, state='disabled')
            # -------------------------------------------
            analysis.entryconfig(0, state='normal')
            analysis.entryconfig(1, state='disabled')
            analysis.entryconfig(3, state='disabled')
            pWDG.set(rMode)
            HeadA, HeadB, closeV = 0, 1, 0  # call embedded functions

        else:
            rMode = 0                       # clear auto synchronous mode
            process.entryconfig(0, state='normal')
            process.entryconfig(1, state='normal')
            process.entryconfig(3, state='normal')
            # -------------------------------------------
            analysis.entryconfig(0, state='normal')
            analysis.entryconfig(1, state='normal')
            analysis.entryconfig(3, state='normal')
            pWDG.set(rMode)
            HeadA, HeadB, closeV = 0, 1, 0  # call embedded functions

        return # rMode, HeadA, HeadB, closeV

    def preventClose():
        print('Variable State:', pLmtA.get())
        pass

    def newMetricsConfig():  # This is a DNV Metric Configuration Lookup Table ------[]

        global pLmtA, sSta, sEnd, eStat, gSize1, gSize2, xUCLLP, xLCLLP, xUCLLA, xLCLLA, xUCLHT, xLCLHT, xUCLDL, \
            xLCLDL, xUCLDD, xLCLDD, xUCLOT, xLCLOT, hLmtA, shewhart, pLmtB, dnvMinMax, mgmMinMax, othMinMax, pWDG, \
            s_butt, sSta, sEnd, e5, e6, dnv_butt, mgm_butt, button2, pop, mLA, mLP, mCT, mOT, mRP, mWS, m1, m2, m3, \
            m4, m5, m6, pWDG

        pop = Toplevel(root)
        pop.wm_attributes('-topmost', True)

        # center root window ------------------------[]
        pop.tk.eval(f'tk::PlaceWindow {pop._w} center')
        # pop.withdraw()

        # Define volatile runtime variables ---------[]
        metRO = False
        # Define and initialise essential popup variables -----------------------------------------
        xUCLLP, xLCLLP, sUCLLP, sLCLLP = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
        xUCLLA, xLCLLA, sUCLLA, sLCLLA = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
        xUCLHT, xLCLHT, sUCLHT, sLCLHT = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
        xUCLDL, xLCLDL, sUCLDL, sLCLDL = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
        xUCLDD, xLCLDD, sUCLDD, sLCLDD = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
        xUCLOT, xLCLOT, sUCLOT, sLCLOT = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
        # -----------------------------------------------

        sSta, sEnd, gSize1, gSize2 = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
        lPwr, lAng, eStat, optm1, optm2 = IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop)

        pLmtA, pLmtB, pLmtC, pLmtD, pLmtE, pLmtF = (IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop),
                                                    IntVar(pop), IntVar(pop))

        hLmtA, hLmtB, shewhart, Sample = IntVar(pop), IntVar(pop), IntVar(pop), StringVar(pop)

        dnvMinMax, mgmMinMax, othMinMax, mLA, mLP, mCT, mOT, mRP, mWS = (IntVar(pop), IntVar(pop), IntVar(pop),
                                                                         IntVar(pop), IntVar(pop), IntVar(pop),
                                                                         IntVar(pop), IntVar(pop), IntVar(pop))
        pWDG = IntVar(pop)

        # global pop, screen_h, screen_w, x_c, y_c
        # center object on the screen---
        pop.resizable(False, False)
        height = (95 + y_start + (y_incmt * 5))
        w, h = 520, height  # 450

        pop.title('Configure Samples & Parameters')
        screen_w = pop.winfo_screenwidth()
        screen_h = pop.winfo_screenheight()
        x_c = int((screen_w / 2) - (w / 2))
        y_c = int((screen_h / 2) - (h / 2))
        pop.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))

        # creating labels and positioning them on the grid --------[]
        Label(pop, text='Sample Size').place(x=10, y=10)
        Label(pop, text='Group Type').place(x=10, y=40)
        Label(pop, text='Shift Begins @').place(x=200, y=10)
        Label(pop, text='Shift Closes @').place(x=200, y=40)

        # --------------------------------------------------------[]
        Label(pop, text='[Configure Monitoring Parameters]  -  ', font=("bold", 10)).place(x=10, y=80)

        p4 = Checkbutton(pop, text="DNV Pipe", font=("bold", 10), variable=dnvMinMax, command=dMinMaxPlot)
        p4.place(x=230, y=y_start - y_incmt * 1)    # 6

        p5 = Checkbutton(pop, text="MGM Pipe", font=("bold", 10), variable=mgmMinMax, command=mMinMaxPlot)
        p5.place(x=325, y=y_start - y_incmt * 1)    # 6

        p6 = Checkbutton(pop, text="AutoMode", font=("bold", 10), variable=pWDG, command=watchDG)
        p6.place(x=415, y=124)                      # 6
        if int(cDM):
            pWDG.set(1)
        else:
            pWDG.set(0)
        # -------------------------------------------------------------------------[]
        m1 = Checkbutton(pop, text="Oven Temperature", font=("bold", 10), variable=mOT, state="disabled")
        m1.place(x=10, y=y_start)
        mOT.set(1)

        m2 = Checkbutton(pop, text="Active Cell Tension", font=("bold", 10), variable=mCT, state="disabled")
        m2.place(x=150, y=y_start)  #x=160
        mCT.set(1)

        m3 = Checkbutton(pop, text="Tape Winding Spd", font=("bold", 10), variable=mWS, state="disabled")
        m3.place(x=10, y=y_start + y_incmt * 1)
        mWS.set(1)

        m4 = Checkbutton(pop, text="Reinforced Pressure", font=("bold", 10), variable=mRP, state="disabled")
        m4.place(x=150, y=y_start + y_incmt * 1)
        mRP.set(1)
        # -------------------------------------------- Not included in DNV/MGM requirements
        m5 = Checkbutton(pop, text="Laser Power", font=("bold", 10), variable=mLP, state="disabled")
        m5.place(x=305, y=y_start)

        m6 = Checkbutton(pop, text="Laser Angle", font=("bold", 10), variable=mLA, state="disabled")
        m6.place(x=305, y=y_start + y_incmt * 1)

        # ---------------------------------------------------------------------#
        # load variables directly from ini files --[TODO]
        sbutton = 'disabled'  # disable Save button on entry state
        cState = 'disabled'

        separatorU = ttk.Separator(pop, orient='horizontal')
        separatorU.place(relx=0.01, rely=0.53, relwidth=0.75, relheight=0.01)  # y=7.3

        # ---------------------------------------------------------------------#
        Label(pop, text='[Configure Statistical Limits]', font=("bold", 10)).place(x=10,
                                                                             y=(y_start + 5) + (y_incmt * 3))  # 320 | 7

        # --------------------------------------------------------------------------------------------#
        dnv_butt = Button(pop, text="DNV Key Parameters", wraplength=90, justify=CENTER, width=12,
                          height=3, font=("bold", 12), command=dnvConfigs, state=cState)
        dnv_butt.place(x=240, y=3 + y_start + y_incmt * 4)  # 350 | 8
        # --------------------------------------------------------------------------------------------#
        # EoLP_butt = Button(pop, text=" EoL/EoP Sampling ", width=15, command=eolpConfigs, state='normal')
        # EoLP_butt.place(x=240, y=3 + y_start + y_incmt * 6.6)
        # p4 = Checkbutton(pop, text="AutoSynchronous", font=("bold", 10), variable=pWDG, command=watchDG)
        # p4.place(x=240, y=3 + y_start + y_incmt * 6.6)  # 393 |10
        # --------------------------------------------------------------------------------------------#
        mgm_butt = Button(pop, text="MGM Key Parameters", wraplength=90, justify=CENTER, width=12,
                              height=3, font=("bold", 12), command=mgmConfigs, state=cState)
        mgm_butt.place(x=380, y=3 + y_start + y_incmt * 4)  # 350 | 8
        # --------------------------------------------------------------------------------------------#

        p1 = Checkbutton(pop, text="Set DNV Limits", font=("bold", 10), variable=pLmtA, command=enDNV)
        p1.place(x=10, y=3 + y_start + y_incmt * 4)         # 353

        p2 = Checkbutton(pop, text="Use Auto Limits", font=("bold", 10), variable=shewhart, command=enAUTO)
        p2.place(x=10, y=y_start + y_incmt * 5)             # 373 | 9
        shewhart.set(1)

        p3 = Checkbutton(pop, text="Set MGM Limits", font=("bold", 10), variable=pLmtB, command=enMGM)
        p3.place(x=10, y=y_start + y_incmt * 6)             # 393 |10

        def display_selection(event):
            # Get the selected value.
            selection = e8.get()
            if selection == "S-Domino":  # butterfly effect/small change
                messagebox.showinfo(message="Combines the rising/falling edges of previous subgroup",
                                    title=f"{selection} Group")
            elif selection == "F-Discrete":
                messagebox.showinfo(message="Evaluates new subgroup samples in the order of index",
                                    title=f"{selection} Group")
            # print("The drop-down has been opened!")
            return

        def display_sel(event):
            # Get the selected value.
            selection = e7.get()
            if selection == "10":
                messagebox.showinfo(message="Computed Mean with A3=0.975, B3=0.284, B4=1.716",
                                    title=f"{selection} Sample Size")
            elif selection == "15":  # Unstable Domino
                messagebox.showinfo(message="Computed Mean with A3=0.789, B3=0.428, B4=1.572",
                                    title=f"{selection} Sample Size")
            elif selection == "20":
                messagebox.showinfo(message="Computed Mean with A3=0.680, B3=0.510, B4=1.490",
                                    title=f"{selection} Sample Size")
            elif selection == "23":
                messagebox.showinfo(message="Computed Mean with A3=0.633, B3=0.545, B4=1.455",
                                    title=f"{selection} Sample Size")
            elif selection == "25":
                messagebox.showinfo(message="Computed Mean with A3=0.606, B3=0.565, B4=1.435",
                                    title=f"{selection} Sample Size")
            elif selection == "30":
                messagebox.showinfo(message="Computed Mean with A3=0.553, B3=0.604, B4=1.396",
                                    title=f"{selection} Sample Size")
            else:
                pass

            return

        # ------------------------------------[Multiple options: Laser Power (M)]
        # TODO ---- command=saveMetricRP)

        # Set default values - Break down each element and show to users
        gSize1.set('30')
        gSize2.set('GS-Discrete')  # Group Type (1=Domino, 2=SemiDomino, 3=Discrete)
        sSta.set('07:00:00 ')
        sEnd.set('01:00:00 ')

        # TODO ------------------------------------- [Include command=klr ] ---------------------------------------[]
        c1 = Checkbutton(pop, text="Historical Limits", font=("bold", 10), variable=hLmtA, command=runChecksPQ)
        c1.place(x=370, y=6)  # x=290, y=80, width=20,
        # ------------------

        if not metRO:
            # TODO --------------------------------------------------------[]

            e7 = ttk.Combobox(pop, width=10, values=[" Select Size", "10", "15", "20", "23", "25", "30"],
                              state="disabled")
            e7.bind("<<ComboboxSelected>>", display_sel)
            e7.current(0)           # set default choice
            e7.place(x=100, y=10)

            e8 = ttk.Combobox(pop, width=10, values=["SS-Domino", "GS-Discrete"], state="disabled")
            e8.bind("<<ComboboxSelected>>", display_selection)
            e8.current(0)           # set default choice to first index
            e8.place(x=100, y=40)
            # --------------------------------------------------- [Shift information]
            e5 = Entry(pop, width=8, textvariable=sSta, state="readonly")
            e5.place(x=290, y=10)
            e6 = Entry(pop, width=8, textvariable=sEnd, state="readonly")
            e6.place(x=290, y=40)

            # # Add isolation button
            button2 = Button(pop, text="Edit Stats Properties", bg="red", fg="white", state="disabled", command=clearMetrics)
            button2.place(x=370, y=35)  # place(x=520, y=47)

        else:
            e7 = ttk.Combobox(pop, width=8, values=[" Select", "10", "15", "20", "23", "25", "25"], state="normal")
            e7.bind("<<ComboboxSelected>>", display_sel)
            e7.current(0)  # set default choice
            e7.place(x=40, y=50)

            e8 = ttk.Combobox(pop, width=10, values=["SS-Domino", "GS-Discrete"], state="normal")
            e8.bind("<<ComboboxSelected>>", display_selection)
            e8.current(0)  # set default choice to first index
            e8.place(x=172, y=50)
            # -------------------------------------------------[ Shift duration ]
            e5 = Entry(pop, width=8, textvariable=sSta, state="normal")
            e5.place(x=290, y=10)
            e6 = Entry(pop, width=8, textvariable=sEnd, state="normal")
            e6.place(x=290, y=40)

        # ------------------------------ # TODO ---- command=saveMetricRP)
        s_butt = Button(pop, text="Save Config Details", fg="black", state=sbutton, command=save_pMetrics)
        s_butt.place(x=385, y=5 + y_start + y_incmt * 2)  # 295 now 2
        # --------------------------------
        button5 = Button(pop, text="Exit Configuration", command=pop.destroy)
        button5.place(x=391, y=22 + y_start + y_incmt * 6)  # 400 nowe 2
        # pop.mainloop()
    # ------------------------ Line 2604

    def errorNoServer():
        messagebox.showerror('dB Server', 'Server offline or No connection')
        return

    def pingError():
        messagebox.showerror('OSI layer Error', 'Network Error or Server offline..')
        return

    def errorChoice():
        messagebox.showerror('Warning - Display Modes', 'Invalid request, no active Visualisation found.')
        return

    def errorSelection():
        messagebox.showerror('Warning - Runtime', 'No active Runtime Process')
        return

    def runtimeChange():
        messagebox.showerror('Invalid Change', 'Stop the active Runtime before new selection')
        return

    def errorNoconnect():
        messagebox.showerror("Warning - Data Disconnect", "Invalid request, no active connection(s) found.")

    def hostConnect():
        messagebox.showinfo('Host Connection', 'Connection is successful!')
        return

    def saveSQLconfig():
        import loadSQLConfig as to
        if sub_menu.entrycget(0, 'state') == 'normal':
            ct1 = seripSql.get()
        else:
            ct1 = seripSql.get()
        ct2 = sqlid.get()
        ct3 = uname.get()
        ct4 = autho.get()
        print('Variables:', ct1, ct2, ct3, ct4)
        if ct1 == "" or ct2 == "" or ct3 == "" or ct4 == "":
            errorNote()  # response to save button when entry field is empty
            print('Empty field...')

        else:
            to.writeSQLconfig(ct1, ct2, ct3, ct4)  # save into text file
            successNote()
        # Condition for saving entries ---------------[]
        Entry(pop, state='disabled').place(x=86, y=60)
        Entry(pop, state='disabled').place(x=86, y=100)
        Entry(pop, state='disabled').place(x=330, y=60)
        Entry(pop, state='disabled').place(x=330, y=100)
        pop.destroy()
        # pop.grab_release()
        return

    def savePLCconfig():
        import OPC_UA_settings as to

        if sub_menu.entrycget(0, 'state') == 'normal':
            ct1 = hostName.get()
        else:
            ct1 = hostName.get()
        ct2 = hostIPv4.get()
        ct3 = deviceNm.get()
        ct4 = authopwd.get()
        print('Variables:', ct1, ct2, ct3, ct4)
        if ct1 == "" or ct2 == "" or ct3 == "" or ct4 == "":
            errorNote()  # response to save button when entry field is empty
            print('Empty field...')

        else:
            to.writePLCconfig(ct1, ct2, ct3, ct4)  # save into text file
            successNote()
        # Condition for saving entries ---------------[]
        Entry(pop, state='disabled').place(x=86, y=60)
        Entry(pop, state='disabled').place(x=86, y=100)
        Entry(pop, state='disabled').place(x=330, y=60)
        Entry(pop, state='disabled').place(x=330, y=100)
        pop.destroy()
        # pop.grab_release()
        return

    def serverSQLConfig():
        global pop, sqlRO, seripSql, sqlid, uname, autho, e4

        import loadSQLConfig as ls
        pop = Toplevel(root)
        # pop.wm_attributes('-topmost', True)
        pop.wm_attributes('-alpha', 0.9)

        # Define and initialise essential popup variables -------------------------------------------
        seripSql, sqlid, uname, autho = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
        print('State:', sqlRO)

        # center object on the screen---
        w, h = 480, 210
        pop.resizable(False, False)
        pop.title('Modify SQL Server Connection')
        screen_w = pop.winfo_screenwidth()
        screen_h = pop.winfo_screenheight()
        x_c = int((screen_w / 2) - (w / 2))
        y_c = int((screen_h / 2) - (h / 2))
        pop.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))

        labl_0 = Label(pop, text="SQL Credentials", width=20, font=("bold", 14))
        labl_0.place(x=130, y=10)

        # creating labels and positioning them on the grid --------[]
        sub_menu.entryconfig(0, label='SQL Connectivity', state='disabled')  # disable submenu
        Label(pop, text='Server IP').place(x=10, y=60)
        Label(pop, text='Database').place(x=10, y=100)
        Label(pop, text="Access ID").place(x=250, y=60)
        Label(pop, text="Authorize").place(x=250, y=100)

        # set initial variables or last known variables
        configFile = 'checksumError.ini'
        if os.path.isfile('C:\\SynchronousGPU\\' + configFile):
            IP, name, User, Pswd = ls.load_configSQL(configFile)
            seripSql.set(IP)
            sqlid.set(name)
            uname.set(User)
            autho.set(Pswd)
            print('Using decrypted details...')
        else:
            seripSql.set('Server ID')
            sqlid.set('dBase Repository')
            uname.set('User Name')
            autho.set('Authorization Code')

        # creating entries and positioning them on the grid -----
        if not sqlRO:
            e1 = Entry(pop, textvariable=seripSql, state='readonly')
            e1.place(x=86, y=60)
            e2 = Entry(pop, textvariable=sqlid, state='readonly')
            e2.place(x=86, y=100)
            e3 = Entry(pop, textvariable=uname, state='readonly')
            e3.place(x=330, y=60)
            e4 = Entry(pop, textvariable=autho, state='readonly', show="*")
            e4.place(x=330, y=100)
        else:
            e1 = Entry(pop, textvariable=seripSql, state='normal')
            e1.place(x=86, y=60)
            e2 = Entry(pop, textvariable=sqlid, state='normal')
            e2.place(x=86, y=100)
            e3 = Entry(pop, textvariable=uname, state='normal')
            e3.place(x=330, y=60)
            e4 = Entry(pop, textvariable=autho, state='normal', show="*")
            e4.place(x=330, y=100)

        Button(pop, text="Change Details", bg="red", fg="white", command=clearFields).place(x=160, y=150)
        Button(pop, text="Test Connection", command=testConnSQL).place(x=270, y=150)
        Button(pop, text="Save Details", bg="green", fg="white", command=saveSQLconfig).place(x=380, y=150)

        return

    # ------------------------------------------------------------------[]
    def serverPLCConfig():
        global pop, sqlRO, hostName, hostIPv4, deviceNm, authopwd, e4

        import OPC_UA_settings as ld

        pop = Toplevel(root)
        # pop.wm_attributes('-topmost', True)
        pop.wm_attributes('-alpha', 0.9)

        # Define and initialise essential popup variables --------------[]
        hostName, hostIPv4, deviceNm, authopwd = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
        print('State:', sqlRO)

        # center object on the screen---
        w, h = 470, 210
        pop.resizable(False, False)
        pop.title('Modify PLC Connection')
        screen_w = pop.winfo_screenwidth()
        screen_h = pop.winfo_screenheight()
        x_c = int((screen_w / 2) - (w / 2))
        y_c = int((screen_h / 2) - (h / 2))
        pop.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))

        labl_0 = Label(pop, text="OPC UA Credentials", width=20, font=("bold", 14))
        labl_0.place(x=130, y=10)

        # creating labels and positioning them on the grid --------[]
        sub_menu.entryconfig(1, label='PLC Connectivity', state='disabled') # disable submenu
        Label(pop, text='Host PLC Name:').place(x=10, y=60)
        Label(pop, text="Device Access:").place(x=238, y=60)
        Label(pop, text='TCPV4 Address:').place(x=10, y=100)
        Label(pop, text="AccessID Code:").place(x=238, y=100)

        # set initial variables or last known variables
        configFile = 'ISO62264_ISA95.ini'
        if os.path.isfile('C:\\SynchronousGPU\\'+configFile):
            IP, name, User, Pswd = ld.load_configPLC(configFile)
            hostName.set(name)
            hostIPv4.set(IP)
            deviceNm.set(User)
            authopwd.set(Pswd)
            print('Using decrypted details:', name, IP, User, Pswd)
        else:
            hostName.set('DefaultHost')
            hostIPv4.set('192.168.100.XXX')
            deviceNm.set('TCP01_SPC')
            authopwd.set('*********')

        # creating entries and positioning them on the grid -----
        if not sqlRO:
            e1 = Entry(pop, textvariable=hostName, width=15, state='readonly')
            e1.place(x=105, y=60)
            e2 = Entry(pop, textvariable=hostIPv4, width=15, state='readonly')
            e2.place(x=105, y=100)
            e3 = Entry(pop, textvariable=deviceNm, width=15, state='readonly')
            e3.place(x=330, y=60)
            e4 = Entry(pop, textvariable=authopwd, width=15, state='readonly')   #, show="*")
            e4.place(x=330, y=100)
        else:
            e1 = Entry(pop, textvariable=hostName, width=15, state='normal')
            e1.place(x=105, y=60)
            e2 = Entry(pop, textvariable=hostIPv4, width=15, state='normal')
            e2.place(x=105, y=100)
            e3 = Entry(pop, textvariable=deviceNm, width=15, state='normal')
            e3.place(x=330, y=60)
            e4 = Entry(pop, textvariable=authopwd, width=15, state='normal', show="*")
            e4.place(x=330, y=100)

        Button(pop, text="Modify OPC-UA", bg="red", fg="white", command=clearFields).place(x=245, y=140)
        Button(pop, text="Test Connection",  bg="green", fg="white", command=testConnPLC).place(x=350, y=140)
        Button(pop, text="Save OPC-UA Details & Exit", command=savePLCconfig).place(x=295, y=175)

        return

    def oclicked():
        if svar1.get() == 1:
            oEE = 1
            print("OEE Data Disabled", oEE)
            svar1.set(0)
        else:
            oEE = 0
            print("OEE Data Enabled", not oEE)
            svar1.set(1)
        return oEE

    def aboutSPC():        # TODO configure menu item to functon
        pop = Toplevel(root)

        pop.wm_attributes('-topmost', True)
        # center object on the screen---
        pop.resizable(False, False)
        w, h = 430, 250
        pop.title('About MagmaSPC')
        screen_w = pop.winfo_screenwidth()
        screen_h = pop.winfo_screenheight()
        x_c = int((screen_w / 2) - (w / 2))
        y_c = int((screen_h / 2) - (h / 2))
        pop.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))

        labl_0 = Label(pop, text="The Synchronous SPC (GPU Edition 2.0)", font=("bold", 14))
        labl_0.place(x=60, y=30)

        # creating labels and positioning them on the grid --------[]
        Label(pop, text='Real-Time Statistical Process Control System').place(x=90, y=80)
        Label(pop, text='Built Ver: 12.0, Built on: November 2024').place(x=110, y=100)
        Label(pop, text='Sole Author: Robert B. Labs').place(x=140, y=120)
        Label(pop, text='Copyright (C) 2023-2025 Group Industrialisation, United Kingdom.').place(x=30, y=180)
       # filewin = Toplevel(pop)

    def onlinehelp():        # TODO configure menu item to functon
        import webbrowser
        webbrowser.open(url, new=1)
        return

    def testConnSQL():
        import Test_PING as sq
        agent = 0
        server_IP = seripSql.get()  # PLC Server IP

        try:
            # Test server connection over TCP/IP ---------------------[]
            netTX = sq.testNetworkConn([server_IP], 1)
            # if ICMP ping response is allowed on the server
            if netTX:
                hostConnect()       # acknowledgement
                conn = 'true'
            else:
                pingError()         # Ping error failed -------
                conn = 'none'

        except Exception as err:
            errorLog(f"{err}")
            errorNoServer()         # errorNoServer()
            conn = 'none'

        return conn

    def testConnPLC():
        import Test_PING as sq

        agent = 0
        server_IP = hostIPv4.get()  # PLC Server IP

        try:
            # Test server connection over TCP/IP ---------------------[]
            netTX = sq.testNetworkConn([server_IP], 1)  # if ICMP ping response is allowed on the server
            if netTX:
                hostConnect()                                          # acknowledgement
                conn = 'true'
            else:
                pingError()                                            # Ping error failed -------
                conn = 'none'

        except Exception as err:
            errorLog(f"{err}")
            errorNoServer()                                            # errorNoServer()
            conn = 'none'

        return conn

    def sCloseConnSQL():
        global conn
        # ------------------------------------------------------------------ Start
        import CommsSql as mCon
        conn = mCon.DAQ_connect(1, 0)  # 1 = connection is active to be .closed()
        if conn == 'true':
            conn.close()
            print('SQL Data is disconnected')
        else:
            conn = 'none'
            print('No active connections!')
            errorNoconnect()
        return conn

    # ---------------------------------------------------------------------------[]

    def sCloseConnPLC():
        global conn
        # plc_stop() - beware not to halt PLC
        # ------------------------------------------------------------------ Start
        import CommsPlc as mCon
        conn_active = mCon.disconnct_PLC()                    # TODO: Check PLC server link
        if conn_active == 'true':
            print('Host PLC is disconnected')
        else:
            print('No active connections!')
            conn_active = 'false'

        return conn_active

    # ---------------------------------------------------------------------------[]
    def discALL():
        if filemenu.entrycget(3, 'state') == 'disabled':
            filemenu.entryconfig(3, label='Disconnect SQL Data', state='normal')
            filemenu.entryconfig(4, label="Disconnect PLC Data", state='normal')
            filemenu.entryconfig(5, label='Terminate Connections', state='disabled')
            connect = True
            sCloseConnSQL()
            # ---- acknowledgement f(x) ----

        elif filemenu.entrycget(4, 'state') == 'disabled':
            filemenu.entryconfig(3, label='Disconnect SQL Data', state='normal')
            filemenu.entryconfig(4, label="Disconnect PLC Data", state='normal')
            filemenu.entryconfig(5, label='Terminate Connections', state='disabled')
            connect = True
            sCloseConnPLC()
            # ---- acknowledgement f(x) ----

        else:
            connect = False
            errorNoconnect()
            print('\nNo active connection found..')

        return connect
    # One of the challenging object to configure both checkbox and state --------[]

    def retroPlay():
        # Declare global variable available to all processes
        global stpd, pWON, pID, OeeID, hostConn

        # ------------------------------[ Check valid number of attached Monitors]
        # myMon = m.get_monitors()                    # Automatically detect attached monitors
        # print('\nAttached Monitors:', len(myMon))

        if process.entrycget(0, 'state') == 'disabled' or process.entrycget(1, 'state') == 'disabled':
            print('\nSelection Condition met...')
            # import signal
            # os.kill(sid, signal.SIGTERM)
            # Cascade View Date String Search ------------------------[]
            if (process.entrycget(0, 'state') == 'disabled'
                    and process.entrycget(1, 'state') == 'normal'
                    and process.entrycget(3, 'state') == 'normal'):

                # ----- Calling essential functions -----------[]
                process.entryconfig(0, state='disabled')                     # turn command off
                analysis.entryconfig(0, state='normal')
                analysis.entryconfig(1, state='normal')
                analysis.entryconfig(3, state='normal')

                # ------- Indicate Record Date or WON ---------[TODO...]
                sDate1, sDate2, uWON = searchBox()                                  # Popup dialogue
                print('\nCascade Date String - Between:', sDate1, 'and:', sDate2, 'WON_#:', uWON)
                # ---------------------------------------------[2]
                if sDate1 == '?' and sDate2 == '?' and uWON == '?':
                    print('Search Aborted!')
                    process.entryconfig(0, state='normal')
                else:
                    print('Attempting connection with SQL Server...')
                    cMode = 2
                    runType.append(cMode)

                    # Connect to SQL Server -----------------------[]
                    oeeValid, organicID, pType = wo.srcTable(sDate1, sDate2, uWON)     # Query record [pType=DnV/MGM]
                    print('\nSearch Return:', oeeValid, organicID)
                    # ---------------------------------------------[]
                    if organicID != 'G' and aSCR >= 4 and pRecipe == 'DNV':
                        print('\nSelecting Cascade View....')
                        tabbed_cascadeMode(cMode, pType)                        # Cascade View

                    elif organicID != 'G' and aSCR >= 8 and pRecipe == 'MGM':
                        print('\nSelecting Cascade View....')
                        tabbed_cascadeMode(cMode, pType)                        # Cascade View

                    elif organicID != 'G' and aSCR >= 1 or aSCR <= 4:
                        print('\nSorry, multiple Screen display is required for Cascade View!')
                        print('Attached Monitor(s):', aSCR)
                        print('Switching back to Tabbed View...')
                        tabbed_canvas(cMode, pType)                             # Tabbed View
                    else:
                        process.entryconfig(0, state='normal')
                        print('Invalid post processing data or Production record not found..')

            # Tabbed View Date String Search -------------------------------[]
            elif (process.entrycget(1, 'state') == 'disabled'
                  and process.entrycget(0, 'state') == 'normal'
                  and process.entrycget(3, 'state') == 'normal'):

                # ----- Calling essential functions ---------#
                process.entryconfig(1, state='disabled')
                analysis.entryconfig(0, state='normal')
                analysis.entryconfig(1, state='normal')
                analysis.entryconfig(3, state='normal')

                # ------- Indicate Record Date or WON ---------[]
                sDate1, sDate2, uWON = searchBox()                                   # Search for Production data
                print('Tabbed Date String - Between:', sDate1, '&', sDate2, ':WON_# -', uWON)

                if sDate1 == '?' and sDate2 == '?' and uWON == '?':
                    print('Search Aborted!')
                    process.entryconfig(1, state='normal')
                else:
                    print('\nAttempting connection with SQL Server...')
                    cMode = 2
                    runType.append(cMode)

                    # connect SQL Server and obtain Process ID ----#
                    oeeValid, organicID, pType = wo.srcTable(sDate1, sDate2, uWON)    # Query SQL record
                    print('\nSearch Return:', oeeValid, organicID)

                    # ---------------------------------------------[]
                    if organicID != 'G':
                        print('\nSelecting Tabbed View....')
                        tabbed_canvas(cMode, pType)        # Tabbed View
                    else:
                        process.entryconfig(1, state='normal')
                        print('Invalid post processing data or Production record not found..')

            else:
                runtimeChange()
                cMode = 0
                runType.append(cMode)
                print('Invalid SQL Query connection...')

        else:
            print('Invalid selection. Please, enable a visualisation mode')

        return


    def realTimePlay():
        # Declare global variable available to all processes
        global stpd, pWON, pID, OeeID, hostConn

        # ------------------------------[ Check valid number of attached Monitors]
        import screeninfo as m
        # myMon = m.get_monitors()            # Automatically detect attached monitors
        # print('Attached Monitors:', len(myMon))

        if analysis.entrycget(0, 'state') == 'disabled' or analysis.entrycget(1, 'state') == 'disabled':
            print('\nSelection A Condition met....')
            # import dataRepository as sqld
            # Test condition for CASCADE VIEW -----------------#
            if (analysis.entrycget(0, 'state') == 'disabled'
                    and analysis.entrycget(1, 'state') == 'normal'
                    and analysis.entrycget(3, 'state') == 'normal'):

                # ----- Calling essential functions -----------[]
                analysis.entryconfig(0, state='disabled')
                process.entryconfig(0, state='normal')
                process.entryconfig(1, state='normal')
                process.entryconfig(3, state='normal')

                cMode = 1
                runType.append(cMode)
                print('\nSelecting Cascade View....')

                if aSCR >= 4 and pRecipe == 'DNV':
                    print('\nSelecting Cascade View....')
                    tabbed_cascadeMode(cMode, pRecipe)                  # Cascade View

                elif aSCR >= 8 and pRecipe == 'MGM':
                    print('\nSelecting Cascade View....')
                    tabbed_cascadeMode(cMode, pRecipe)                  # Cascade View

                elif aSCR >= 1 or aSCR <= 4:
                    print('\nSorry, multiple screen function is NOT available, attach 4 or 8 Monitors!')
                    print('Attached Monitors', aSCR)
                    print('Selecting Tabbed View....')
                    tabbed_canvas(cMode, pRecipe)                       # Tabbed View
                else:
                    print('Invalid post processing data or Production record not found..')

            # Test condition for TABBED VIEW -----------------#
            elif (analysis.entrycget(1, 'state') == 'disabled'
                  and analysis.entrycget(0, 'state') == 'normal'
                  and analysis.entrycget(3, 'state') == 'normal'):

                # ----- Calling essential functions ----------#
                analysis.entryconfig(1, state='disabled')
                process.entryconfig(0, state='normal')
                process.entryconfig(1, state='normal')
                process.entryconfig(3, state='normal')

                cMode = 1
                runType.append(cMode)
                print('\nSelecting Tabbed View....')
                tabbed_canvas(cMode, pRecipe)                         # Call tabbed canvas functions

            else:
                runtimeChange()
                cMode = 0
                runType.append(cMode)
        else:
            print('Invalid selection. Please, enable visualisation mode')

        return

    def terminateVis(typeV):
        if messagebox.askokcancel("STOP: Visualisation", "Terminating Visualisation?"):
            if typeV == 1:
                casc_clearOut()
            else:
                tabb_clearOut()
        else:
            if typeV == 1:
                process.entryconfig(0, state='disabled')  # return to previous state
            else:
                process.entryconfig(1, state='disabled')  # return to previous state
            process.entryconfig(3, state='normal')        # return calling menu command to initial dstate

    def stopSPCrun():                   # reset analysis menu command
        if (analysis.entrycget(0, 'state') == 'disabled'
                or analysis.entrycget(1, 'state') == 'disabled'):
            analysis.entryconfig(3, state='disabled')
            analysis.entryconfig(0, state='normal')
            analysis.entryconfig(1, state='normal')
        else:
            errorSelection()
        # clearSPCrun()
        # terminateVis()  # TODO - this should close existing SPC window

    # ---------------------- CALL SPC FUNCTIONAL PROCEDURES ---------------------------------------------[]
    def validQueryObj():
        # Check SQL connection and selected option on SQL data Types ----------------------[]
        if filemenu.entrycget(5, 'state') == 'disabled' and filemenu.entrycget(2, 'state') == 'disabled':
            plcTbls, sqlTbls = 1, 0
            print('Using PLC Query System...')

        elif filemenu.entrycget(6, 'state') == 'disabled' and filemenu.entrycget(2, 'state') == 'disabled':
            plcTbls, sqlTbls = 0, 1
            print('Using SQL Query System...')

        else:
            plcTbls, sqlTbls = 0, 0
            print('Valid Query Object not found...')
            errorNoServer()
        return plcTbls, sqlTbls

    def searchBox():       # Indicate DATE/WON Search for production data
        pop = Toplevel(root)
        pop.wm_attributes('-topmost', True)

        # center root window --------------
        pop.tk.eval(f'tk::PlaceWindow {pop._w} center')
        pop.withdraw()
        uWON = askstring(title="Search Records", prompt="By WON / (YYYY-MM-DD)", initialvalue="20240507", parent=root)

        # -----------------------############---------------------------[]
        validWON = 8

        # Test for null entry -------------
        if uWON is None or uWON == '':
            fmDATE, toDATE, uWON = '?', '?', '?'  # Date was not used
            print('Search was aborted by User action')

        # elif isinstance(uWON, str):                # Search data rec by date
        elif '\\' in uWON or '-' in uWON or '/' in uWON:

            # calculate the next boundary date
            print('SearchBox Production by date...')
            if '-' in uWON:
                # print('Dash found...')
                rangeD = uWON.split('-', 2)
                # print('DT1:', rangeD)

            elif '\\' in uWON:
                # print('Slash found...\\')
                rangeD = uWON.split('\\', 2)
                # print('DT2', rangeD)

            else:
                # print('Slash found.../')
                rangeD = uWON.split('/', 2)
                # print('DT3', rangeD)

            # ----------------------------------------------#
            begMO = int(rangeD[1])
            begDA = int(rangeD[2])                          # The current Month
            nextMnth = int(rangeD[1]) + 1                   # New Month interval
            nextDate = int(rangeD[2]) + 1                   # New date interval

            # treat calendar special cases ----------------[]
            if rangeD[1] == '02':                           # Find February Month (28)
                if nextDate > 28:                           # February
                    endMO = nextMnth                        # Spilling into next Month
                    endDA = nextDate - 28                   # keep current date
                else:
                    endMO = int(rangeD[1])                  # The current Day
                    endDA = nextDate                        # Current date + 1

            # -----------------------------------   # Jan, March, May, July, August, October, December
            elif (rangeD[1] == '01' or rangeD[1] == '03' or rangeD[1] == '05' or rangeD[1] == '07'
                        or rangeD[1] == '08' or rangeD[1] == '10' or rangeD[1] == '12'):
                # ------------------------------------------#
                if nextDate > 31:                           # end search interval
                   endMO = nextMnth                         # Spilling into next Month
                   endDA = nextDate - 31                    # keep current date
                else:
                    endMO = int(rangeD[1])                  # The current Day
                    endDA = nextDate                        # Current date + 1

            elif rangeD[1] == '04' or rangeD[1] == '06' or rangeD[1] == '09' or rangeD[1] == '11': #rangeD[2] == '30':                         # April, June, September, November

                if nextDate > 30:                           # Month and date search interval
                    endMO = nextMnth                        # Spilling into next Month
                    endDA = nextDate - 30                   # keep current date
                else:
                    endMO = int(rangeD[1])                  # The current Day
                    endDA = nextDate                        # Current date + 1
            else:
                # print('AM HERE 4')
                endMO = int(rangeD[1])                      # The current Day
                endDA = nextDate                            # Current date + 1

            # Convert to Work Order Number--- YYYY-MM-DD -----------
            fmDATE = rangeD[0] + '-' + str(begMO) + '-' + str(begDA)    # Date was used in search query
            toDATE = rangeD[0] + '-' + str(endMO) + '-' + str(endDA)    # Date was used in search query

            uWON = rangeD[0] + rangeD[1] + rangeD[2]
            # print('WON:', uWON)

        elif validWON == len(uWON):
            print('\nSearch by Work Order Number...')
            ret = 1
            stad = str(uWON)
            fmDATE, toDATE, uWON = '0', '0', stad        # Date was not used
            print('WON:', uWON)
        else:
            print('Search was aborted by Operator...')
            return

        return fmDATE, toDATE, uWON

    # -------------------------------- APP MENU PROCEDURE START ------------------------------------------------[]
    def viewTypeA():    # enforce selection integrity ------------------[Cascade Tabb View]
        global HeadA, rType                 # declare as global variables

        # Define run Type -------------[]
        if runType == 1:
            rType = 'Synchro'
        elif runType == 2:
            rType = 'PostPro'
        else:
            rType = 'Standby'
        # -----------------------------[]
        if process.entrycget(1, 'state') == 'disabled':      # If Tabbed View was in disabled state
            # if Tabbed view is active
            process.entryconfig(0, state='disabled')                # select cascade View becomes an option
            process.entryconfig(1, state='normal')                  # set Tabb View to normal
            process.entryconfig(3, state='normal')                  # set Close Display to normal

            if messagebox.askokcancel("Warning!!!", "Current Visualisation will be lost!"):
                tabb_clearOut()                                           # Clear out existing Tabbed View
                tabbed_cascadeMode()                                      # Default limited tabbed common screen
                print('\nStarting new GPU thread...')
                exit_bit.append(1)

            else:
                process.entryconfig(1, state='disabled')            # revert to original state
                process.entryconfig(0, state='normal')              # revert to original state

            HeadA, HeadB, closeV = 1, 0, 0
            retroPlay()                                                  # Call objective function

        elif process.entrycget(3, 'state') == 'disabled':    # If Closed Display state is disabled
            process.entryconfig(0, state='disabled')                # select and disable Cascade View command
            process.entryconfig(1, state='normal')                  # set tabb view command to normal
            process.entryconfig(3, state='normal')                  # set close display to normal

            # --- start parallel thread ----------------------------------#
            # cascadeViews()                                              # Critical Production Params
            retroPlay()                                                   # Call objective function
            # tabbed_cascadeMode()                                        # Default limited tabbed common screen + Casc
            exit_bit.append(1)
            HeadA, HeadB, closeV = 1, 0, 0

        elif (process.entrycget(0, 'state') == 'normal'
              and process.entrycget(1, 'state') == 'normal'
              and process.entrycget(3, 'state') == 'normal'):
            process.entryconfig(0, state='disabled')
            process.entryconfig(1, state='normal')
            process.entryconfig(3, state='normal')

            # --- start parallel thread --------------------------------#
            # cascadeViews()                                            # Critical Production Params
            retroPlay()                                                 # Call objective function
            # tabbed_cascadeMode()                                      # Provide limited Tabb and multiple screen
            exit_bit.append(1)
            HeadA, HeadB, closeV = 1, 0, 0

        else:
            process.entryconfig(0, state='normal')
            HeadA, HeadB, closeV = 0, 0, 1
            errorChoice()                               # pop up error
            print('Invalid! View selection before process parameter..')

        return HeadA, HeadB, closeV

    def viewTypeB():        # Tabbed View (This is configured for remote users)
        global HeadA, HeadB, closeV, rType
        # Define run Type ---------------------[TODO]
        if runType == 1:
            rType = 'Synchro'
        elif runType == 2:
            rType = 'PostPro'
        else:
            rType = 'Standby'
        # -------------------------------------[]
        # enforce category selection integrity ---------------------#
        if process.entrycget(0,'state') == 'disabled':
            process.entryconfig(1, state='disabled')
            process.entryconfig(0, state='normal')
            process.entryconfig(3, state='normal')

            if messagebox.askokcancel("Warning!!!", "Current Visualisation will be lost!"):
                casc_clearOut()                                           # clear out visualisation frame
                tabbed_canvas()                                           # Call Canvas binding function
                exit_bit.append(0)                                        # Keep a byte into empty list
            else:
                process.entryconfig(0, state='disabled')            # revert to original state
                process.entryconfig(1, state='normal')              # revert to original state

            HeadA, HeadB, closeV = 0, 1, 0                                # call embedded functions
            retroPlay()                                                   # Call objective function

        elif process.entrycget(3, 'state') == 'disabled':
            process.entryconfig(1, state='disabled')
            process.entryconfig(0, state='normal')
            process.entryconfig(3, state='normal')

            retroPlay()                                                     # Call objective function
            # tabbed_canvas()                                               # Tabbed Visualisation
            exit_bit.append(0)

            HeadA, HeadB, closeV = 0, 1, 0                                  # call embedded functions

        elif (process.entrycget(0, 'state') == 'normal'
                  and process.entrycget(1, 'state') == 'normal'
                  and process.entrycget(3, 'state') == 'normal'):
                process.entryconfig(1, state='disabled')
                process.entryconfig(0, state='normal')
                process.entryconfig(3, state='normal')

                retroPlay()                     # Call objective function
                # tabbed_canvas()               # Tabbed Visualisation
                exit_bit.append(0)
                HeadA, HeadB, closeV = 0, 1, 0

        else:
            process.entryconfig(1, state='normal')
            HeadA, HeadB, closeV = 0, 0, 1
            errorChoice()                                   # raise user exception
            print('Invalid! View selection before process parameter..')

        return HeadA, HeadB, closeV

# -----------------------------------------[ For Spalsh Control]
    def abortKey(key):
        # you can terminate the program with 'End' button ----
        if key == Key.end:
            print('\nTotal Number of Core-CPU#:', os.cpu_count())
            print('Killing Parent PID:', os.getppid())
            print('Killing Child PID:', os.getpid())
            print('SPC terminated by Local User...')
            # mySplash.withdraw()
            # lt.timer.cancel()
            os._exit(0)
            return True
# --------------------------------------------------------------------------------#
    def viewTypeC():
        global HeadA, rType  # declare as global variables

        # Define run Type -------------[]
        if runType == 1:
            rType = 'Synchro'
        elif runType == 2:
            rType = 'PostPro'
        else:
            rType = 'Standby'
        # -----------------------------[]
        if analysis.entrycget(1, 'state') == 'disabled':  # If Tabbed View was in disabled state
            # if Tabbed view is active
            analysis.entryconfig(0, state='disabled')   # select cascade View becomes an option
            analysis.entryconfig(1, state='normal')     # set Tabb View to normal
            analysis.entryconfig(3, state='normal')     # set Close Display to normal

            if messagebox.askokcancel("Warning!!!", "Current Visualisation will be lost!"):
                tabb_clearOut()                                             # Clear out existing Tabbed View

                # --- start parallel thread --------------------------------#
                import autoSPCGUI as lt
                conPLC = lt.splashT(root)
                # call realtime method -----------[]
                if conPLC:
                    realTimePlay()                                          # Call objective function (tabbed_cascade)
                else:
                    print('Failed connection...')
                # ----------------------------------------------------------[]
                print('\nStarting new GPU thread...')
                exit_bit.append(1)

            else:
                analysis.entryconfig(1, state='disabled')   # revert to original state
                analysis.entryconfig(0, state='normal')     # revert to original state
            HeadA, HeadB, closeV = 1, 0, 0

        elif analysis.entrycget(3, 'state') == 'disabled':    # If Closed Display state is disabled
            analysis.entryconfig(0, state='disabled')               # select and disable Cascade View command
            analysis.entryconfig(1, state='normal')                 # set tabb view command to normal
            analysis.entryconfig(3, state='normal')                 # set close display to normal

            # --- start parallel thread ---------------------------------#
            # cascadeViews()                                             # Critical Production Params
            import autoSPCGUI as lt
            conPLC = lt.splashT(root)

            # call realtime method -----------[]
            if conPLC:
                inUseAlready.append(True)
                realTimePlay()                                           # Call objective function (tabbed_cascade)
            else:
                print('Failed connection...')
            # ----------------------------------------------------------[]
            exit_bit.append(1)
            HeadA, HeadB, closeV = 1, 0, 0

        # ---------------- Fresh selection ------------------------------#
        elif (analysis.entrycget(0, 'state') == 'normal'
              and analysis.entrycget(1, 'state') == 'normal'
              and analysis.entrycget(3, 'state') == 'normal'):
            analysis.entryconfig(0, state='disabled')               # Disable selected command
            analysis.entryconfig(1, state='normal')                 # Keep command Enabled
            analysis.entryconfig(3, state='normal')                 # Keep command enabled
            # Prevent Post Production analysis Menu object
            process.entryconfig(0, state='normal')
            process.entryconfig(1, state='normal')
            process.entryconfig(3, state='normal')

            # --- start parallel thread ---------------------------------#
            import autoSPCGUI as lt
            conPLC = lt.splashT(root)
            # call realtime method -----------[]
            if conPLC:
                inUseAlready.append(True)
                realTimePlay()                                           # Call objective function (tabbed_cascade)
            else:
                print('Failed connection...')
            # ----------------------------------------------------------[]
            exit_bit.append(1)
            HeadA, HeadB, closeV = 1, 0, 0

        else:
            analysis.entryconfig(0, state='normal')
            HeadA, HeadB, closeV = 0, 0, 1
            errorChoice()                                               # pop up error
            print('Invalid! View selection before process parameter..')

        return HeadA, HeadB, closeV

    def viewTypeD():  # Tabbed View (This is configured for remote users)
        global HeadA, HeadB, closeV, rType
        # Define run Type -----------------------------------------[]
        if runType == 1:
            rType = 'Synchro'
        elif runType == 2:
            rType = 'PostPro'
        else:
            rType = 'Standby'
        # ---------------------------------------------------------[]
        # enforce category selection integrity ---------------------#
        if analysis.entrycget(0, 'state') == 'disabled':
            analysis.entryconfig(1, state='disabled')
            analysis.entryconfig(0, state='normal')
            analysis.entryconfig(3, state='normal')

            if messagebox.askokcancel("Warning!!!", "Current Visualisation will be lost!"):
                casc_clearOut()                                     # clear out visualisation frame
                # tabbed_canvas()                                   # Call Canvas binding function
                # --- start parallel thread ------------------------#
                import autoSPCGUI as lt
                conPLC = lt.splashT(root)
                # call realtime method -----------[]
                if conPLC:
                    inUseAlready.append(True)
                    realTimePlay()  # Call objective function (tabbed_cascade)
                else:
                    print('Failed connection...')
                # --------------------------------------------------[]
                exit_bit.append(0)                                  # Keep a byte into empty list
            else:
                analysis.entryconfig(0, state='disabled')     # revert to original state
                analysis.entryconfig(1, state='normal')       # revert to original state

            HeadA, HeadB, closeV = 0, 1, 0                          # call embedded functions
            realTimePlay()                                          # Call objective function

        elif analysis.entrycget(3, 'state') == 'disabled':
            analysis.entryconfig(1, state='disabled')
            analysis.entryconfig(0, state='normal')
            analysis.entryconfig(3, state='normal')

            # --- start parallel thread ---------------------------------#
            import autoSPCGUI as lt
            conPLC = lt.splashT(root)
            # call realtime method -----------[]
            if conPLC:
                inUseAlready.append(True)
                realTimePlay()  # Call objective function (tabbed_cascade)
            else:
                print('Failed connection...')
            # ----------------------------------------------------------[]
            exit_bit.append(0)
            HeadA, HeadB, closeV = 0, 1, 0  # call embedded functions

        elif (analysis.entrycget(0, 'state') == 'normal'
              and analysis.entrycget(1, 'state') == 'normal'
              and analysis.entrycget(3, 'state') == 'normal'):
            analysis.entryconfig(1, state='disabled')
            analysis.entryconfig(0, state='normal')
            analysis.entryconfig(3, state='normal')

            # --- start parallel thread ---------------------------------#
            import autoSPCGUI as lt
            conPLC = lt.splashT(root)
            # call realtime method -----------[]
            if conPLC:
                inUseAlready.append(True)
                realTimePlay()  # Call objective function (tabbed_cascade)
            else:
                print('Failed connection...')
            # ----------------------------------------------------------[]
            exit_bit.append(0)
            HeadA, HeadB, closeV = 0, 1, 0

        else:
            analysis.entryconfig(1, state='normal')
            HeadA, HeadB, closeV = 0, 0, 1
            errorChoice()  # raise user exception
            print('Invalid! View selection before process parameter..')

        return HeadA, HeadB, closeV

    def tabb_clearOut():
        # evaluate how many widget is in use and clear accordingly
        inUse = len(root.winfo_children())

        if inUse == 9:
            # root.winfo_children()[9].destroy()
            root.winfo_children()[8].destroy()
            root.winfo_children()[7].destroy()
            root.winfo_children()[6].destroy()
        elif inUse == 7:
            root.winfo_children()[6].destroy()
            root.winfo_children()[5].destroy()
        # ---------------------------------
        root.winfo_children()[4].destroy()
        root.winfo_children()[3].destroy()
        root.winfo_children()[2].destroy()
        root.winfo_children()[1].destroy()

    # ------------------------------------------#
    def kill_process(pid):
        # SIGKILL = terminate the process forcefully | SIGINT = interrupt ( equivalent to CONTROL-C)
        os.kill(pid, signal.SIGTERM)
    # ------------------------------------------#

    def casc_clearOut():
        # https://www.geeksforgeeks.org/python-different-ways-to-kill-a-thread/
        inUse = len(root.winfo_children())
        # -------------
        print('\n******************************')
        print('Whats in Use', inUse)
        print('Get PPID', os.getppid())                         # Parent ID 37248
        print('Get PID', os.getpid())                           # Child ID 52692
        print('Get CWDB', os.getcwdb())                         # b'C:\\CuttingEdge\\BETA_ver3.6'
        print('Get CWD', os.getcwd())                           # C:\CuttingEdge\BETA_ver3.6
        print('Get INDENT', get_ident())                        # 32356
        print('Get Native ID', get_native_id())                 # 32356
        print('Current Thread Name', current_thread().name)     # MainThread
        print('Current Thread Ident', current_thread().ident)   # Current Thread 32356

        try:
            if pRecipe == 'DNV':
                kill_process(p3.pid)
                kill_process(p2.pid)
                kill_process(p1.pid)
            else:
                kill_process(p7.pid)  # convert process into pid number
                kill_process(p6.pid)
                kill_process(p5.pid)                                  # convert process into pid number
                kill_process(p4.pid)
                kill_process(p3.pid)
                kill_process(p2.pid)
                kill_process(p1.pid)
        except OSError:
            print(f'Process {p7} failed to terminate!')
            print(f'Process {p6} failed to terminate!')
            print(f'Process {p5} failed to terminate!')
            print(f'Process {p4} failed to terminate!')
            print(f'Process {p3} failed to terminate!')
            print(f'Process {p2} failed to terminate!')
            print(f'Process {p1} failed to terminate!')
        # clear out all children process --[]
        if pRecipe == 'DNV':
            root.winfo_children()[3].destroy()
            root.winfo_children()[2].destroy()
            root.winfo_children()[1].destroy()
        else:
            root.winfo_children()[7].destroy()
            root.winfo_children()[6].destroy()
            root.winfo_children()[5].destroy()
            root.winfo_children()[4].destroy()
            root.winfo_children()[3].destroy()
            root.winfo_children()[2].destroy()
            root.winfo_children()[1].destroy()

    def closeViews():
        # enforce category selection integrity ---------------------#
        if process.entrycget(0, 'state') == 'disabled':

            process.entryconfig(0, state='normal')
            process.entryconfig(1, state='normal')
            process.entryconfig(3, state='disabled')

            viewA = 1
            terminateVis(viewA)
            # casc_clearOut()
            HeadA, HeadB, closeV = 0, 0, 1

        elif process.entrycget(1, 'state') == 'disabled':
            process.entryconfig(0, state='normal')
            process.entryconfig(1, state='normal')
            process.entryconfig(3, state='disabled')

            viewB = 2
            terminateVis(viewB)
            # tabb_clearOut()                               # Call Canvas binding function
            HeadA, HeadB, closeV = 0, 0, 1                  # call embedded functions

        else:
            process.entryconfig(3, state='normal')
            HeadA, HeadB, closeV = 0, 0, 1
            errorChoice()                                   # raise user exception
            print('Invalid! View selection before process parameter..')

        return HeadA, HeadB, closeV

    # Menu Bar --------------------------------------------------------------------------------[]
    if int(cDM):
        inautoMode = 'disabled' # disable Synchronous and PostProd Menu if in AutoMode
    else:
        inautoMode = 'normal'   # enable Synchronous and PostProd Menu if in AutoMode

    # ---------------------------------------------------------------[Menu GUI Canvas Begins Here]
    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    sub_menu = tk.Menu(menubar, tearoff=0)

    filemenu.add_cascade(label="Server Credentials", menu=sub_menu)
    sub_menu.add_command(label="SQL Connectivity", command=serverSQLConfig, accelerator="Ctrl+S")
    sub_menu.add_command(label="PLC Connectivity", command=serverPLCConfig, accelerator="Ctrl+P")

    filemenu.add_command(label="Statistical Process", command=newMetricsConfig, accelerator="Ctrl+L")

    filemenu.add_separator()
    filemenu.add_command(label="Disconnect SQL Data", command=sCloseConnSQL, accelerator="Alt+S")  # enabled on connection
    filemenu.add_command(label="Disconnect PLC Data", command=sCloseConnPLC, accelerator="Alt+P")  # disable no connection
    filemenu.add_command(label="Terminate Connections", command=discALL, accelerator="Ctrl+Q")

    filemenu.add_separator()
    filemenu.add_command(label="Close", command=callback)           # root.destroy via callback func
    filemenu.add_command(label="Exit", command=menuExit)
    menubar.add_cascade(label="System Setup", menu=filemenu)

    # Analysis Menu -----------------------------------------[]
    analysis = Menu(menubar, tearoff=0)

    analysis.add_command(label="Set Cascade View", command=viewTypeC)
    analysis.add_command(label="Set Tabbed View", state=inautoMode, command=viewTypeD)

    analysis.add_separator()
    analysis.add_command(label="Stop SPC Process", command=stopSPCrun)
    menubar.add_cascade(label="Synchronous Live Mode", menu=analysis)

    # Process Menu ----------------------------------------[]
    process = Menu(menubar, tearoff=0)

    process.add_command(label="Use Cascade View", state=inautoMode, command=viewTypeA)
    process.add_command(label="Use Tabbed View", state=inautoMode, command=viewTypeB)

    process.add_separator()
    process.add_command(label="Close Display", command=closeViews)
    menubar.add_cascade(label="PostProd Analysis", menu=process)

    # Help Menu ------------------------------------------------[]
    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Help Index", command=onlinehelp)
    helpmenu.add_command(label="About...", command=aboutSPC)
    menubar.add_cascade(label="SPC Help", menu=helpmenu)

    root.config(menu=menubar)
    # ----------------------------------------------------------------------[]
    canvasOn(1)  # Update canvas on when GUI is active
    # ----------------------------------------------------------------------[]
    # tabbed_canvas()

    # capture closing events and activate snooze mode -------------[]
    root.protocol("WM_DELETE_WINDOW", callback)

    # root.mainloop()


if __name__ == '__main__':
    # This code will only be executed if the script is run as the main program
    root = Tk()

    # # Create table -----------------------------[]
    # entries = []
    # for i in range(5):              # Example: 5 rows
    #     row_entries = []
    #     for j in range(6):          # 6 columns
    #         entry = tk.Entry(root)
    #         entry.grid(row=i, column=j)
    #         row_entries.append(entry)
    #     entries.append(row_entries)
    # -------------------------------------------[]
    # Load menu functions
    userMenu()

    root.mainloop()
