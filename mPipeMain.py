"""
This Pipeline development demonstrates the implementation of an advanced Control Chart using
a real-time SQL connectivity to mPipe Tape laying Process PLC Server.
It aims at providing near real time data pool 20 data point (observation) per 2 seconds.
Included in the algorithm is the Intelligent procedure to identify current Process files, OEE Data
and Quality level control feedback into SIMOTION/ PLC alarms.

The SQL Server must be on the LAN/WAN and PLC server.

Title: Statistical Process Control Pipeline (CUSUM Method) **********

Author: Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
"""
# Import libraries ---------------------------------------------------------------------------[]
# import torch                             # CUDA - Compute Unified Device Architecture (NVIDIA)
import os
import time
from datetime import datetime
from itertools import count
from time import gmtime, strftime
import matplotlib.patches as patches
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation
from threading import *
import psutil
import matplotlib.pyplot as plt
from numba import jit, njit, cuda, prange
import matplotlib
matplotlib.use('TKAgg')                    # Interactive Backends class [.use('TkAgg'] | 'agg'
# import latexify

# Import Utility Modular functions ----------------------------------------------------------[]
import DailyProductionSQL as mP
import ProcessCapPerf as pp
import TriggerTripWire as sx
import loadSPCConfig as ty
# --------------------------#
rtUpdateCONNX = False               # import realTimeUpdate as pq | ALLOW CONNECTION ONCE
inUseAlready = False                # import realTPostProdUpdate as pq | ALLOW USAGE of CLASS ONCE
# --------------------------#
import rhAnalyzer as rh
import ringVarSQL as qv
import ringVarPLC as qw
import selPlcColumnsDNV as vq       # realtime columns
import selSqlColumnsTFM as qq       # post-processing columns
import selRingVarPlot as vd
import spcWatchDog as wd
from pydub import AudioSegment
from pydub.playback import play
from tkinter import messagebox

# ----------------------- Audible alert --------------------------------------------------[]
impath ='C:\\CuttingEdge\\SPC_ver12\\Media\\'
nudge = AudioSegment.from_wav(impath+'tada.wav')
error = AudioSegment.from_wav(impath+'error.wav')

# Define statistical operations ----------------------------------------------------------[]
WeldQualityProcess = True
paused = False

# Initialise process performance arrays ---
""""  
# -----------------------------------------
***     OTlayer => layer data from OEE Table'
***     HTlayr => layer data from Table RH01
# -----------------------------------------
"""
HTlayr, OTlayr, Ppka, Ppkb, Ppkc, Ppkd, Ppke, EPpos, pStatus = [], [], [], [], [], [], [], [], []
rfA, rfB, rfC, rfD = [], [], [], []     # Roller Fore
tsA, tsB, tsC, tsD = [], [], [], []     # Tape Speed
ttA, ttB, ttC, ttD = [], [], [], []     # Tape Temperature
dtA, dtB, dtC, dtD = [], [], [], []     # Delta Temp/Ratio
tgA, tgB, tgC, tgD = [], [], [], []     # Tape Gap


srchA, srchB = [], []
processWON = []

# Used to stores the samples of group mean in a subgroup ---
autoUCLA, autoLCLA, autoUSLA, autoLSLA = [], [], [], []
autoUCLB, autoLCLB, autoUSLB, autoLSLB = [], [], [], []
autoUCLC, autoLCLC, autoUSLC, autoLSLC = [], [], [], []
autoUCLD, autoLCLD, autoUSLD, autoLSLD = [], [], [], []

autoUCLE, autoLCLE, autoUSLE, autoLSLE = [], [], [], []
autoUCLF, autoLCLF, autoUSLF, autoLSLF = [], [], [], []

autoGpMeanA, autoGpMeanB, autoGpMeanC, autoGpMeanD, autoGpMeanE, autoGpMeanF = [], [], [], [], [], []
autoGpDevA, autoGpDevB, autoGpDevC, autoGpDevD, autoGpDevE, autoGpDevF = [], [], [], [], [], []

autosUCLA, autosLCLA, sClineA = [], [], []
autosUCLB, autosLCLB, sClineB = [], [], []
autosUCLC, autosLCLC, sClineC = [], [], []
autosUCLD, autosLCLD, sClineD = [], [], []
autosUCLE, autosLCLE, sClineE = [], [], []
autosUCLF, autosLCLF, sClineF = [], [], []


def differential_idx(layer, idx1, idx2, idx3, idx4, idx5, idx6, idx7, idx8, pPos):    # Record for offline SPC analysis
    rtitle = ('================================= TCP01 - Realtime Index Tracker =============================\n')
    rheader = ('Time'+'\t\t'+'Layer#'+'\t'+'T1Row'+'\t'+'T2Row'+'\t'+'T3Row'+'\t'+'T4Row'+'\t'+'T5Row'+'\t'+'T6Row'+'\t'+'T7Row'+'\t'+'T8Row'+'\t'+'EstPos'+'\n')
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


def reloadLimits(fname, N):
    # open and retrieve stats limits, convert to Historical Limits
    with open(fname) as file:
        for line in (file.readlines()[-N:]):
            histLim = line
    return histLim


def autoLimits(a, b, c, d, e, x, g, h, i, j, k, l):
    a = round(a, 2)
    b = round(b, 2)
    c = round(c, 2)
    d = round(d, 2)
    e = round(e, 2)
    x = round(x, 2)
    g = round(g, 2)
    h = round(h, 2)
    i = round(i, 2)
    j = round(j, 2)
    k = round(k, 2)
    l = round(l, 2)

    rtitle = ('============================================= TCP01 Shewharts Auto Generated Process Mean ===================================\n')
    rheader = ('Time'+'\t\t'+'WorkOrder#' + '\t' + 'Xrf' + '\t' + 'Srf' + '\t' + 'Xtt' + '\t' + 'Stt' + '\t' + 'Xdt' + '\t' + 'Sdt' + '\t' + 'Xtg' + '\t' + 'Stg' + '\t' + 'Xts' + '\t' + 'Sts' + '\t' + 'Xta' + '\t' + 'Sta' + '\n')
    rdemaca = ("----------------------------------------------------------------------------------------------------------------------------\n")
    event = datetime.now().strftime("%H:%M.%S")
    autoLimits = 'AutoLimLog_TCP01'                                 # processed SQL index Log

    filepath = '.\\ShewhartLim\\'+autoLimits+".txt"
    old_report = os.path.isfile(filepath)

    if not old_report:                                              # if doing a new report...
        f = open('.\\ShewhartLim\\'+autoLimits+".txt", "a")         # Open new file and ...
        f.write(rtitle)                                             # Insert a Title
        f.write(rheader)                                            # Insert new header
        f.write(rdemaca)                                            # Insert demarcator
    else:                                                           # if it's an existing report
        f = open('.\\ShewhartLim\\' + autoLimits + ".txt", "a")    # Just open the file for a write operations
    # initialise a tab delimited data and insert corresponding values in string format --------------------------[]
    f.write(event+'\t'+str(processWON)+'\t'+str(a)+'\t'+str(b)+'\t'+str(c)+'\t'+str(d)+'\t'+str(e)+'\t'+str(x)+'\t'+str(g)+'\t'+str(h)+'\t'+str(i)+'\t'+str(j)+'\t'+str(k)+'\t'+str(l)+'\n')
    f.close()


def errorLog(err):
    fileName = datetime.now().strftime('M2MLog '+"%Y-%m-%d")
    event = datetime.now().strftime("%Y-%m-%d %H:%M.%S")
    errorlogFile = str(fileName)
    f = open('.\\RuntimeLog\\'+errorlogFile+".txt", "a")
    f.write(event+' --- '+err+'\n')
    f.close()


def errorWON():
    messagebox.showerror('Local GUI', 'Invalid Work Order Number. Try again!')
    return


def callback():
    plt.close()
    print('Visualisation closed..')
    return plt


# Newly added Runtime Variables -----------------[]

def mainRun(conn, ret, stad, stpd, Sqlfmt, HeadA, HeadB, viewTFM, oEE, rp, ts, tt, tr, tgm, oParam, calr, sql1, sql2, sql3, sql4, sql5, sql6, sql7, sql8):
    global R1, R2, R3, R4, plt #,CTlayr
    """
    oParam: Owner of Process Parameter (TFM, DNV or DoE)
    """
    # Declare empty arrays ------------[]
    dL0, dX1, dX2, dX3 = [], [], [], []

    print('\nVisualisation PPID#:', os.getppid())
    print('Viz Child PID#:', os.getpid())
    print('Viz Plot Thread:', get_ident())
    print(f"CPU utilization: {psutil.cpu_percent()}%")
    print(f"Memory utilization: {psutil.virtual_memory().percent}%")
    print('-' * 34)
    print('Processing selection, please wait...\n')

    RetroReplay = ret       # Retrospective offline play
    StaSearchD = stad       # Retrospect Play: Date Lower Boundary or WON #
    EndSearchD = stpd       # Retrospect Play: Date Upper Boundary or 0
    UsePLC_DBS = Sqlfmt     # specify whether SQl Table Query or PLC DB Query is in use
    DNVspecify = int(oParam)
    apCalledby = calr
    rT1dx = sql1            # SQL data table index = 0 unless SPC stalled or relaunched.
    rT2dx = sql2            # SQL data table index = 0 unless SPC stalled or relaunched.
    rT3dx = sql3            # SQL data table index = 0 unless SPC stalled or relaunched.
    rT4dx = sql4            # SQL data table index = 0 unless SPC stalled or relaunched.
    rT5dx = sql5            # SQL data table index = 0 unless SPC stalled or relaunched.
    rT6dx = sql6            # SQL data table index = 0 unless SPC stalled or relaunched.
    rT7dx = sql7            # SQL data table index = 0 unless SPC stalled or relaunched.
    rT8dx = sql8            # SQL data table index = 0 unless SPC stalled or relaunched.

    # Visualization configuration menu options ===================================================[C]
    VarPerHeadA = HeadA     # Plots a chosen variable for all Rings-Head in one axis window
    VarPerHeadB = HeadB     # Plots a chosen variable for all Rings-Head in one alternative window
    VariProcess = viewTFM   # Display all variables per process into 4 axes windows
    # ----------------------#
    PerfProcess = oEE
    if VarPerHeadA or VarPerHeadB and not PerfProcess:
        # if DNVspecify:
        PerfProcess = True
    print('OEE Final State:', PerfProcess, 'Plot TFM/DNV (0/1):', DNVspecify, 'GrandView Type?:', VariProcess)

    # Control Process Parameters ------------------------[]
    pro_type = 'TFM Requirements: Visualise all Processes'
    RollerPressure = rp     # Roller Pressure/Roller Force
    Manu_TapeSpeed = ts     # Tape Feed speed
    TapeTemperatur = tt     # Tape Feed Temperature
    TSub_TempRatio = tr     # Tape/Sub temperature Ratio
    GapMeasurement = tgm    # Tape Gap Measurement

    print('Running' + pro_type + '...')
    # ---------------------------- Date Search Entry ---------------------------------------------[B]
    # load SPC run-time parameters
    (sd, fd, gpz, gps, uhl, usm, qmz, xuca, xlca, xma, suca, slca, sma, xucb, xlcb, xmb, sucb, slcb, smb, xucc, xlcc,
     xmc, succ, slcc, smc, xucd, xlcd, xmd, sucd, slcd, smd, xuce, xlce, xme, suce, slce, sme, asp, lpower, xuclp,
     xlclp, xmelp, suclp, slclp, smlp, langl, xucla, xlcla, xmela, sucla, slcla, smla) = ty.load_configSPC(
        'configSPCError.ini')
    # New possible variables: ht=hauloff tension --  ##
    # -- Define Process Control & Specification Limits for the Plots -----------------------------[D]
    smp_Sz = int(gpz)                               # Allow SCADA User to specify window sample size

    if UsePLC_DBS:
        import CommsPlc as q
        smp_SCADA = q.readString(89, 80, 0)
        if smp_SCADA == 'Discrete':
            smp_St = 2                              # Sample step of 2
            viz_cycle = 10
        else:                                       # Domino
            smp_St = 1
            viz_cycle = 150
        print('Step Number Type:', smp_St)
    else:
        smp_Sz = int(gpz)                           # Rolling Window Sample size
        smp_St = int(gps)                           # Rolling Window Sample step
        if smp_St == 1:
            viz_cycle = 100
        else:
            viz_cycle = 10
    optm2 = qmz                                     # using Dr Labs's Runtime Memory Optimization Method

    # Select RunTime memory management style --------------------------------------
    if optm2:
        import RT_MemDrLabs as lq                   # DrLabs optimization method per group processing
        print('DrLabs' + "' Runtime Optimisation is Enabled!")
    else:
        import RT_MemDefault as lq                  # rolling method only per step processing
        print('Pythonian Runtime Optimisation is Enabled!')

    if smp_St == 1:                                 # Domino group, single step slide
        type = 'Domino'
        smp_St = smp_St
    elif smp_St == 2:                               # Discrete group, discrete group slide
        type = 'Discrete'
        smp_St = smp_Sz
    else:
        print('Invalid group choice:', smp_St)
    print('\nSample Size:', smp_Sz, 'Group Type:', type)

    # -- Define Process Variation for Historical Limits -------------------------------------------[D]
    if uhl:                                     # Use Historical Data limits
        hUCLa = xuca                            # Upper Control Limit (UCL)
        hLCLa = xlca                            # Lower Control Limit (LCL)
        hUCLb = xucb                            # Upper Control Limit (UCL)
        hLCLb = xlcb                            # Lower Control Limit (LCL)
        hUCLc = xucc                            # Upper Control Limit (UCL)
        hLCLc = xlcc                            # Lower Control Limit (LCL)
        hUCLd = xucd                            # Upper Control Limit (UCL)
        hLCLd = xlcd                            # Lower Control Limit (LCL)
        hUCLe = xuce                            # Upper Control Limit (UCL)
        hLCLe = xlce                            # Lower Control Limit (LCL)
        hUCLf = xuclp                           # Upper Control Limit (UCL)
        hLCLf = xlclp                           # Lower Control Limit (LCL)
        hUCLg = xucla                           # Upper Control Limit (UCL)
        hLCLg = xlcla                           # Lower Control Limit (LCL)

        HistMeanA = xma                         # Sample Size group Mean of Xbar plot
        HistMeanB = xmb
        HistMeanC = xmc
        HistMeanD = xmd
        HistMeanE = xme
        HistMeanF = xmelp
        HistMeanG = xmela

        HistSDevA = sma                         # Sample size Group Mean of Sbar Plot
        HistSDevB = smb
        HistSDevC = smc
        HistSDevD = smd
        HistSDevE = sme
        HistSDevF = smlp
        HistSDevG = smla

        # Derive the XBar USLs -----------------------
        hUSLa = HistMeanA + (hUCLa - HistMeanA) /3 * 6     # Upper Specification Limit (USL= 6 sigma above the mean)
        hUSLb = HistMeanB + (hUCLb - HistMeanB) / 3 * 6
        hUSLc = HistMeanC + (hUCLc - HistMeanC) / 3 * 6
        hUSLd = HistMeanD + (hUCLd - HistMeanD) / 3 * 6
        hUSLe = HistMeanE + (hUCLe - HistMeanE) / 3 * 6
        hUSLf = HistMeanF + (hUCLf - HistMeanF) / 3 * 6
        hUSLg = HistMeanG + (hUCLg - HistMeanG) / 3 * 6
        # Derived units for S-Chart -------------------
        hLSLa = HistMeanA - (HistMeanA - hLCLa) / 3 * 6     # Lower Specification Limit (LSL = 6 sigma below the mean)
        hLSLb = HistMeanB - (HistMeanB - hLCLb) / 3 * 6
        hLSLc = HistMeanC - (HistMeanC - hLCLc) / 3 * 6
        hLSLd = HistMeanD - (HistMeanD - hLCLd) / 3 * 6
        hLSLe = HistMeanE - (HistMeanE - hLCLe) / 3 * 6
        hLSLf = HistMeanF - (HistMeanF - hLCLf) / 3 * 6
        hLSLg = HistMeanG - (HistMeanG - hLCLg) / 3 * 6

        # S-Plot Upper / Lower Control Limits
        dUCLa = suca
        dLCLa = slca
        dUCLb = sucb
        dLCLb = slcb
        dUCLc = succ
        dLCLc = slcc
        dUCLd = sucd
        dLCLd = slcd
        dUCLe = suce
        dLCLe = slce
        dUCLf = suclp
        dLCLf = slclp
        dUCLg = sucla
        dLCLg = slcla

        PPerf = '$Pp_{k' + str(smp_Sz) +'}$'               # Using estimated or historical Mean
        plabel = 'Pp'
        print('\nFixed XBar Mean:', HistMeanA)
    else:
        # Process performance label when using computed/automatic group Mean
        hUCL, hLCL, hUSL, hLSL, dUCL, dLCL  = 0, 0, 0, 0, 0, 0
        PPerf = '$Cp_{k' + str(smp_Sz) +'}$'               # Using Automatic group Mean
        plabel = 'Cp'
        print('Current Limits:', hUCL, hLCL, round(hUSL, 3), round(hLSL, 3), dUCL, dLCL)

    # Start Day Shift ----------------------------------------------------------------------------[E]
    Start_Day = sd
    FinishDay = fd

    # -- Monitoring Process Variables -----[Allow Dual plot on DNV]
    if DNVspecify and asp:
        if lpower and langl:
            monitorParamLP = lpower         # Laser Power
            monitorParamLA = 0              # Laser Angle
        elif lpower:
            monitorParamLP = lpower         # Laser Power
            monitorParamLA = 0
        elif langl:
            monitorParamLA = langl          # Laser Angle
            monitorParamLP = 0              # Laser Power
        else:
            monitorParamLP = 0
            monitorParamLA = 0

    elif DNVspecify:
        if lpower and langl:
            monitorParamLP = lpower
            monitorParamLA = langl
        elif lpower:
            monitorParamLP = lpower
            monitorParamLA = 0
        elif langl:
            monitorParamLA = langl
            monitorParamLP = 0
        else:
            monitorParamLP = 0
            monitorParamLA = 0
    else:
        print('\nTFMC processing....01')
        if lpower and langl:
            monitorParamLP = lpower         # Laser Power
            monitorParamLA = 0
        elif langl:
            monitorParamLA = langl          # Laser Angle
            monitorParamLP = 0
        elif lpower:
            monitorParamLP = lpower         # Laser Power
            monitorParamLA = 0
        else:
            monitorParamLP = 0              # Laser Power
            monitorParamLA = 0              # Laser Angle

    # Specify row index for database ------[]
    UseRowIndex = True
    idx = count()
    now = datetime.now()

    # Create figure for plotting -----------------------------------------------------------------[G]
    if DNVspecify:
        if VarPerHeadB or VarPerHeadA:
            fig = plt.figure("Process Characterization & Quality Assessment Program", figsize=(16, 9))
            ax = fig.add_subplot(3, 4, (1, 2))          # Aggregated data from all rings and heads
            axa = fig.add_subplot(3, 4, (3, 4))         # Aggregated data from all rings and heads
            # ax1 = fig.add_subplot(3, 4, 4)            # OEE data OEE Chart or Process Perfor
        else:
            fig = plt.figure("Process Characterization & Quality Assessment Program", figsize=(16, 9))
            ax = fig.add_subplot(3, 5, (1, 2))          # Aggregated values Laser Power
            axa = fig.add_subplot(3, 5, (3, 4))         # Aggregated values for Laser Angle
            ax1 = fig.add_subplot(3, 5, 5)              # OEE Chart or Process Performances Summary
    else:
        fig = plt.figure("Process Characterization & Quality Assessment Program", figsize=(16, 9))
        ax = fig.add_subplot(3, 4, (1, 3))              # Aggregated data from all rings and heads
        ax1 = fig.add_subplot(3, 4, 4)                  # OEE data OEE Chart or Process Performances Summary

    # Initial axial configuration for visualization --------------[1]
    if VariProcess:
        if DNVspecify:
            ax2 = fig.add_subplot(3, 5, 6)          # X_bar Ring 1/Laser Force Data
            ax3 = fig.add_subplot(3, 5, 7)          # X_bar Ring 2/Tape Speed Data
            ax4 = fig.add_subplot(3, 5, 8)          # X_bar Ring 3/Tape Temp Data
            ax5 = fig.add_subplot(3, 5, 9)          # X_bar Ring 4/Temp Ratio Data
            ax6 = fig.add_subplot(3, 5, 10)         # X_bar Ring 4/Tape Gap Data
            # --- Columns for S Plots --------------#
            ax7 = fig.add_subplot(3, 5, 11)         # S_bar Ring 1/LF Data
            ax8 = fig.add_subplot(3, 5, 12)         # S_bar Ring 2/TS Data
            ax9 = fig.add_subplot(3, 5, 13)         # S_bar Ring 3/TT Data
            ax10 = fig.add_subplot(3, 5, 14)        # S_bar Ring 4/TR Data
            ax11 = fig.add_subplot(3, 5, 15)        # S_bar Ring 4/TG Data
            # Initial axial configuration for visualization --------------[2]
        else:
            ax2 = fig.add_subplot(3, 4, 5)          # X_bar Ring 1 Data
            ax3 = fig.add_subplot(3, 4, 6)          # X_bar Ring 2 Data
            ax4 = fig.add_subplot(3, 4, 7)          # X_bar Ring 3 Data
            ax5 = fig.add_subplot(3, 4, 8)          # X_bar Ring 4 Data
            # --- Columns for S Plots --------------#
            ax6 = fig.add_subplot(3, 4, 9)          # S_bar Ring 1 Data
            ax7 = fig.add_subplot(3, 4, 10)         # S_bar Ring 2 Data
            ax8 = fig.add_subplot(3, 4, 11)         # S_bar Ring 3 Data
            ax9 = fig.add_subplot(3, 4, 12)         # S_bar Ring 4 Data

    if VarPerHeadB:
        ax2 = fig.add_subplot(3, 4, 5)              # X_bar Ring 1 Data
        ax3 = fig.add_subplot(3, 4, 6)              # X_bar Ring 2 Data
        ax4 = fig.add_subplot(3, 4, 7)              # X_bar Ring 3 Data
        ax5 = fig.add_subplot(3, 4, 8)              # X_bar Ring 4 Data

        ax6 = fig.add_subplot(3, 4, 9)              # S_bar Ring 1 Data
        ax7 = fig.add_subplot(3, 4, 10)             # S_bar Ring 2 Data
        ax8 = fig.add_subplot(3, 4, 11)             # S_bar Ring 3 Data
        ax9 = fig.add_subplot(3, 4, 12)             # S_bar Ring 4 Data

    # Initial axial configuration for visualization --------------[2]
    elif VarPerHeadA:                               # OptionA Axes format
        ax2 = fig.add_subplot(3, 4, (5, 7))         # X_bar Ring 1 Data
        ax3 = fig.add_subplot(3, 4, (8, 12))        # Summary for Pp-Ppk and Cp-Cpk
        ax6 = fig.add_subplot(3, 4, (9, 11))        # S_bar Ring 2 Data
        ax3.get_yaxis().set_visible(False)          # turn off axis for suary column
        ax3.get_xaxis().set_visible(False)
        # ax7 = fig.add_subplot(3, 4, 12)           # Stats merged in ax3

    plt.rcParams.update({'font.size': 7})           # Reduce fontsize to 7pt for all legends
    # --------------------------------------------------------------------------------------------[H]
    # Calibrate limits for X-moving Axis ----------
    window_Xmin, window_Xmax = 0, (smp_Sz + 3)      # windows view = visible data points
    """
    Adopting 0 as centre line when multiple variables are simultaneously considered 
    """
    # Calibrate Y Axis For monitoring Parameter ---------[Calibrate Axes for Monitoring Params]-
    if uhl:
        if DNVspecify and asp and monitorParamLP:
            winLP_y1min, winLP_y1max = hLSLf - 8, hUSLf + 8
            sBar_minLP, sBar_maxLP = dLCLf - 400, dUCLf + 400
            # ---------------------------------------------
        elif DNVspecify and asp and monitorParamLA:
            winLA_y1min, winLA_y1max = hLSLg - 8, hUSLg + 8
            sBar_minLA, sBar_maxLA = dLCLg - 8, dUCLg + 8

        elif DNVspecify and not asp:
            if monitorParamLP and monitorParamLA:
                winLP_y1min, winLP_y1max = hLSLf - 8, hUSLf + 8
                winLA_y1min, winLA_y1max = hLSLg - 8, hUSLg + 8
            elif monitorParamLA:
                winLA_y1min, winLA_y1max = hLSLg - 8, hUSLg + 8
            else:
                winLP_y1min, winLP_y1max = hLSLf - 8, hUSLf + 8

        # ------------- dealing with TFMC reqs -----------#
        else:
            if monitorParamLP:
                winLP_y1min, winLP_y1max = hLSLf - 8, hUSLf + 8
            if monitorParamLA:
                winLA_y1min, winLA_y1max = hLSLg - 8, hUSLg + 8

    else:
        winLP_y1min, winLP_y1max = 320, 2000
        sBar_minLP, sBar_maxLP = -2, 2
        # -------------------------------
        winLA_y1min, winLA_y1max = -2, 2
        sBar_minLA, sBar_maxLA = -1, 1

    # ---------------------------------------------------[Monitoring Parameter] ---------------#
    if DNVspecify and asp and monitorParamLP:
        ax.set_xlim(window_Xmin, window_Xmax)
        ax.set_ylim([winLP_y1min, winLP_y1max], auto=False)
        axa.set_xlim(window_Xmin, window_Xmax)
        axa.set_ylim([sBar_minLP, sBar_maxLP], auto=False)

    elif DNVspecify and asp and monitorParamLA:
        ax.set_xlim(window_Xmin, window_Xmax)
        ax.set_ylim([winLA_y1min, winLA_y1max], auto=False)
        axa.set_xlim(window_Xmin, window_Xmax)
        axa.set_ylim([sBar_minLA, sBar_maxLA], auto=False)

    elif DNVspecify and not asp:
        if monitorParamLP and monitorParamLA:
            ax.set_xlim(window_Xmin, window_Xmax)
            ax.set_ylim([winLP_y1min, winLP_y1max], auto=False)
            # ------------------------------------
            axa.set_xlim(window_Xmin, window_Xmax)
            axa.set_ylim([winLA_y1min, winLA_y1max], auto=False)
        elif monitorParamLA:
            ax.set_xlim(window_Xmin, window_Xmax)
            ax.set_ylim([winLA_y1min, winLA_y1max], auto=False)
        else:
            ax.set_xlim(window_Xmin, window_Xmax)
            ax.set_ylim([winLP_y1min, winLP_y1max], auto=False)
            # ------------------------------------------------
    else:
        # Set limits for axis 1 monitoring plot ------------[]
        if monitorParamLP:
            ax.set_xlim(window_Xmin, window_Xmax)
            ax.set_ylim([winLP_y1min, winLP_y1max], auto=False)
        if monitorParamLA:
            ax.set_xlim(window_Xmin, window_Xmax)
            ax.set_ylim([winLA_y1min, winLA_y1max], auto=False)

    # ---------------------------------------------------------[DO NOT ALTER] ------------------#
    # Calibrate Y Axis For Production Parameters ------------[Calibrate Axes for Process Params]-
    if VarPerHeadA or VarPerHeadB:
        if RollerPressure:
            if uhl:
                window_y2min, window_y2max = hLSLa - 8, hUSLa + 8
                sBar_min, sBar_max = dLCLa - 80, dUCLa + 80
            else:
                if type == 'Discrete':
                    window_y2min, window_y2max = 248, 321
                    sBar_min, sBar_max = 0, 40
                else:
                    window_y2min, window_y2max = 253, 278
                    sBar_min, sBar_max = 0, 55
        elif Manu_TapeSpeed:
            if uhl:
                window_y2min, window_y2max = hLSLb - 5, hUSLb + 5
                sBar_min, sBar_max = dLCLb - 39, dUCLb + 39
            else:
                if type == 'Discrete':
                    window_y2min, window_y2max = 264, 348
                    sBar_min, sBar_max = 0, 55
                else:
                    window_y2min, window_y2max = 264, 348
                    sBar_min, sBar_max = 0, 55
        elif TapeTemperatur:
            if uhl:
                window_y2min, window_y2max = hLSLc - 7, hUSLc + 7
                sBar_min, sBar_max = dLCLc - 39, dUCLc + 39
            else:
                if type == 'Discrete':
                    window_y2min, window_y2max = 264, 348
                    sBar_min, sBar_max = 0, 30
                else:
                    window_y2min, window_y2max = 167, 230
                    sBar_min, sBar_max = 0, 40
        elif TSub_TempRatio:
            if uhl:
                window_y2min, window_y2max = hLSLd - 8, hUSLd + 8
                sBar_min, sBar_max = dLCLd - 55, dUCLd + 55
            else:
                if type == 'Discrete':
                    window_y2min, window_y2max = -25, 25
                else:
                    window_y2min, window_y2max = -27, 20
                sBar_min, sBar_max = 0, 30
        elif GapMeasurement:
            if uhl:
                window_y2min, window_y2max = hLSLe - 0.3, hUSLe + 0.3
                sBar_min, sBar_max = dLCLe - 1.8,  dUCLe + 1.8
            else:
                if type == 'Discrete':
                    window_y2min, window_y2max = -1.5, 1.5
                else:
                    window_y2min, window_y2max = -2, 2
                sBar_min, sBar_max = -5, 5
        else:
            print('Invalid axial unit')
    # ------------------------------ End of Axial Config for Single Visualisation --------------[]
    # Turn off both x/y axes labels ----------[]
    if DNVspecify and VarPerHeadB or VarPerHeadA:
        pass
    else:
        ax1.get_yaxis().set_visible(False)
        ax1.get_xaxis().set_visible(False)

    # Visualisation Axes Definition ------------------------------------------------------------[1]
    if VarPerHeadA:                 # Visualise single parameter on a single axis plot --[1]
        window_y2minA, window_y2maxA = window_y2min, window_y2max
        window_y3min, window_y3max = sBar_min, sBar_max
        ax2.set_xlim([window_Xmin, window_Xmax])
        ax2.set_ylim([window_y2minA, window_y2maxA], auto=True)
        ax6.set_xlim([window_Xmin, window_Xmax])
        ax6.set_ylim([window_y3min, window_y3max], auto=True)

    elif VarPerHeadB:               # Visualise by single parameter on separate Ring Axes ------[3]
        # VariProcess Type B ------------------------------------------[]
        window_y2minE, window_y2maxE = window_y2min, window_y2max
        window_y3min, window_y3max = sBar_min, sBar_max
        # Initial window sizes configured for each axes -----[Ring 1]
        ax2.set_xlim([window_Xmin, window_Xmax])
        ax2.set_ylim([window_y2minE, window_y2maxE], auto=False)
        ax6.set_xlim([window_Xmin, window_Xmax])
        ax6.set_ylim([window_y3min, window_y3max], auto=False)
        # Initial window sizes configured for each axes -----[Ring 2]
        ax3.set_xlim([window_Xmin, window_Xmax])
        ax3.set_ylim([window_y2minE, window_y2maxE], auto=False)
        ax7.set_xlim([window_Xmin, window_Xmax])
        ax7.set_ylim([window_y3min, window_y3max], auto=False)
        # Initial window sizes configured for each axes -----[Ring 3]
        ax4.set_xlim([window_Xmin, window_Xmax])
        ax4.set_ylim([window_y2minE, window_y2maxE], auto=False)
        ax8.set_xlim([window_Xmin, window_Xmax])
        ax8.set_ylim([window_y3min, window_y3max], auto=False)
        # Initial window sizes configured for each axes -----[Ring 4]
        ax5.set_xlim([window_Xmin, window_Xmax])
        ax5.set_ylim([window_y2minE, window_y2maxE], auto=False)
        ax9.set_xlim([window_Xmin, window_Xmax])
        ax9.set_ylim([window_y3min, window_y3max], auto=False)

    elif VariProcess:           # Calibration for VariProcess Option [D] --[4]
        if uhl:
            YScale_minRF, YScale_maxRF = hLSLa - 8.5, hUSLa + 8.5       # Roller Pressure
            YScale_minTS, YScale_maxTS = hLSLb - 0.5, hUSLb + 0.5       # Tape Speed
            YScale_minTT, YScale_maxTT = hLSLc - 7, hUSLc + 7           # Tape Temperature
            YScale_minDT, YScale_maxDT = hLSLd - 0.1, hUSLd + 0.1       # Delta Temp or Temp
            YScale_minTG, YScale_maxTG = hLSLe - 0.3, hUSLe + 0.3       # Gap Measurement
            # # Clibrate Y-axis for S-Plot -----------------------------
            sBar_minRF, sBar_maxRF = dLCLa - 80, dUCLa + 80             # Splot
            sBar_minTS, sBar_maxTS = dLCLb - 5, dUCLb + 5               # Splot
            sBar_minTT, sBar_maxTT = dLCLc - 39, dUCLc + 39             # Splot
            sBar_minDT, sBar_maxDT = dLCLd - 1.5, dUCLd + 1.5           # Splot
            sBar_minTG, sBar_maxTG = dLCLe - 1.8,  dUCLe + 1.8          # Splot
        else:
            if type == 'Domino':
                # Cliberate Y-axis for XBar-Plot ----------------[]
                YScale_minRF, YScale_maxRF = 285, 347,                  # Roller Force 1Ring cAL
                YScale_minTS, YScale_maxTS = 57, 64.2                   # Tape Speed
                YScale_minTT, YScale_maxTT = 57, 64.2                   # Tape Temperature
                YScale_minDT, YScale_maxDT = -8, 5                      # Delta Temp or Temp Ratio (DNV)
                YScale_minTG, YScale_maxTG = -1.3, 1.3                  # Gap Measurement
                # # Clibrate Y-axis for S-Plot ------------------
                sBar_minRF, sBar_maxRF = 5, 35                          # Splot
                sBar_minTS, sBar_maxTS = 0, 4                           # Splot
                sBar_minTT, sBar_maxTT = 0, 4                           # Splot
                sBar_minDT, sBar_maxDT = 1, 6                           # Splot
                sBar_minTG, sBar_maxTG = 0.2, 1.2                       # Splot
            else:   # Discrete Group
                # Discrete Group -------------------------------
                YScale_minRF, YScale_maxRF = 249, 321                   # Roller Force 1Ring cAL
                YScale_minTS, YScale_maxTS = 57, 64.2                   # Tape Speed
                YScale_minTT, YScale_maxTT = 241, 299                   # Tape Temperature
                YScale_minDT, YScale_maxDT = -29, 24                    # Delta Temp
                YScale_minTG, YScale_maxTG = -0.35, 0.35                # Gap Measurement
                # # Clibrate Y-axis for S-Plot -----------------
                sBar_minRF, sBar_maxRF = 8, 40                          # Splot
                sBar_minTS, sBar_maxTS = 5, 30                          # DNV Req
                sBar_minTT, sBar_maxTT = 5, 30                          # Splot
                sBar_minDT, sBar_maxDT = 0, 35                          # Splot
                sBar_minTG, sBar_maxTG = -0.1, 0.1                      # Splot

        # Configure Axial Plot for each visualisation windows ----------------------------------------[B]
        # Requirement -------------------[Roller Force]
        if DNVspecify:
            ax2.set_xlim([window_Xmin, window_Xmax])
            ax2.set_ylim([YScale_minRF, YScale_maxRF], auto=False)
            ax7.set_xlim([window_Xmin, window_Xmax])
            ax7.set_ylim([sBar_minRF, sBar_maxRF])

            # Requirement -------------------[Tape Speed]
            ax3.set_xlim([window_Xmin, window_Xmax])
            ax3.set_ylim([YScale_minTS, YScale_maxTS], auto=False)
            ax8.set_xlim([window_Xmin, window_Xmax])
            ax8.set_ylim([sBar_minTS, sBar_maxTS], auto=False)

            # Requirement -------------[Tape Temperature]
            ax4.set_xlim([window_Xmin, window_Xmax])
            ax4.set_ylim([YScale_minTT, YScale_maxTT], auto=False)
            ax9.set_xlim([window_Xmin, window_Xmax])
            ax9.set_ylim([sBar_minTT, sBar_maxTT], auto=False)

            # Requirement -------------------[Temp Ratio]
            ax5.set_xlim([window_Xmin, window_Xmax])
            ax5.set_ylim([YScale_minDT, YScale_maxDT], auto=False)
            ax10.set_xlim([window_Xmin, window_Xmax])
            ax10.set_ylim([sBar_minDT, sBar_maxDT], auto=False)

            # Requirement -------------------[Tape Gap]
            ax6.set_xlim([window_Xmin, window_Xmax])
            ax6.set_ylim([YScale_minTG, YScale_maxTG])
            ax11.set_xlim([window_Xmin, window_Xmax])
            ax11.set_ylim([sBar_minTG, sBar_maxTG])
        else:
            # Initial window sizes configured for each axes -----[]
            ax2.set_xlim([window_Xmin, window_Xmax])
            ax2.set_ylim([YScale_minRF, YScale_maxRF], auto=False)
            ax6.set_xlim([window_Xmin, window_Xmax])
            ax6.set_ylim([sBar_minRF, sBar_maxRF], auto=False)

            ax3.set_xlim([window_Xmin, window_Xmax])
            ax3.set_ylim([YScale_minTT, YScale_maxTT], auto=False)
            ax7.set_xlim([window_Xmin, window_Xmax])
            ax7.set_ylim([sBar_minTT, sBar_maxTT], auto=False)

            ax4.set_xlim([window_Xmin, window_Xmax])
            ax4.set_ylim([YScale_minDT, YScale_maxDT], auto=False)
            ax8.set_xlim([window_Xmin, window_Xmax])
            ax8.set_ylim([sBar_minDT, sBar_maxDT], auto=False)

            ax5.set_xlim([window_Xmin, window_Xmax])
            ax5.set_ylim([YScale_minTG, YScale_maxTG], auto=False)
            ax9.set_xlim([window_Xmin, window_Xmax])
            ax9.set_ylim([sBar_minTG, sBar_maxTG], auto=False)

    # ======================================== TITLE & LEGEND =====================================[J]
    if RetroReplay:
        ax.set_title('SPC mPipe Solution (Asynchronous Mode - '+type+')  - ' + strftime("%a, %d %b %Y", gmtime()), fontsize=14,
                     fontweight='bold')
    else:
        ax.set_title('SPC mPipe Solution (Synchronous Mode - '+type+')  - ' + strftime("%a, %d %b %Y", gmtime()), fontsize=14,
                     fontweight='bold')

    # Define Title for aggregated value plot -----------------------------------------------------[2]
    if WeldQualityProcess:
        if VarPerHeadA:
            # Define Title for Column Axes ---[3]
            if RollerPressure:          # Roller Force XBar
                ax2.set_title('Roller Force: XBar - [Sample Size:' + str(smp_Sz) + ' ' + type + ']', fontsize=12,
                              fontweight='bold')
                ax6.set_title('[Roller Force: S-Plot]', fontsize=12, fontweight='bold')

            elif Manu_TapeSpeed and DNVspecify:        # Tape Speed XBar
                ax2.set_title('Tape Speed: XBar - [Sample Size:' + str(smp_Sz) + ' ' + type + ']', fontsize=12,
                              fontweight='bold')
                ax6.set_title('[Tape Speed: S-Plot]', fontsize=12, fontweight='bold')

            elif TapeTemperatur:                                                                # Tape Temperature XBar
                ax2.set_title('Tape Temperature: XBar - [Sample Size:' + str(smp_Sz) + ' ' + type + ']', fontsize=12,
                              fontweight='bold')
                ax6.set_title('[Tape Temperature: S-Plot]', fontsize=12, fontweight='bold')     # Std Dev Plot

            elif TSub_TempRatio:                                                                # Temperature Ratio XBar
                if DNVspecify:
                    label1 = 'Temperature Ratio'
                else:
                    label1 = 'Delta Temperature'
                ax2.set_title(label1+ ': XBar - [Sample Size:' + str(smp_Sz) + ' ' + type + ']', fontsize=12,
                              fontweight='bold')
                ax6.set_title('['+label1+': S-Plot]', fontsize=12, fontweight='bold')           # Std Dev Plot

            elif GapMeasurement:                                                                # Tape Gap Measurement
                ax2.set_title('Gap Measurement: XBar - [Sample Size:' + str(smp_Sz) + ' ' + type + ']', fontsize=12,
                              fontweight='bold')
                ax6.set_title('[Gap Measurement: S-Plot]', fontsize=12, fontweight='bold')      # Std Dev Plot
        else:
            if VarPerHeadB:     # Plot single process per ring-head ------[4]
                if RollerPressure:
                    varP = 'Roller Pressure'
                    segA = 'Ring'
                elif Manu_TapeSpeed:
                    varP = 'Tape Speed'
                    segA = 'Ring'
                elif TapeTemperatur:
                    varP = 'Tape Temperature'
                    segA = 'Ring'
                elif TSub_TempRatio:
                    if DNVspecify:
                        varP = 'Temperature Ratio'
                    else:
                        varP = 'Delta Temperature'
                    segA = 'Ring'
                else:   # Tape Gapeasurements
                    varP = 'Gap Measurement'
                    segA = 'Segment'
                # --------------------------------------------[]
                ax2.set_title(varP + ' - [' +segA+' #1]', fontsize=12, fontweight='bold')
                ax6.set_title('StdDev - [' +segA+' #1]', fontsize=12, fontweight='bold')

                ax3.set_title(varP + ' - [' +segA+' #2]', fontsize=12, fontweight='bold')
                ax7.set_title('StdDev - [' +segA+' #2]', fontsize=12, fontweight='bold')

                ax4.set_title(varP + ' - [' +segA+' #3]', fontsize=12, fontweight='bold')
                ax8.set_title('StdDev - [' +segA+' #3]', fontsize=12, fontweight='bold')

                ax5.set_title(varP + '  - [' +segA+' #4]', fontsize=12, fontweight='bold')
                ax9.set_title('StdDev - [' +segA+' #4]', fontsize=12, fontweight='bold')

            elif VariProcess:  # Plot all available variables per ring-head -------[5]
                if DNVspecify:
                    ax2.set_title('Roller Force XBar', fontsize=12, fontweight='bold')      # Roller Force XBar
                    ax7.set_title('Roller Force SDev', fontsize=12, fontweight='bold')

                    ax3.set_title('Tape Speed XBar', fontsize=12, fontweight='bold')        # Tape Speed
                    ax8.set_title('Tape Speed SDev', fontsize=12, fontweight='bold')

                    ax4.set_title('Tape Temp XBar', fontsize=12, fontweight='bold')         # Tape Temperature
                    ax9.set_title('Tape Temp SDev', fontsize=12, fontweight='bold')

                    ax5.set_title('Temp Ratio XBar', fontsize=12, fontweight='bold')        # Tape/Substrate Temp Ratio
                    ax10.set_title('Temp Ratio SDev', fontsize=12, fontweight='bold')

                    ax6.set_title('Tape Gap XBar', fontsize=12, fontweight='bold')          # Tape Gap
                    ax11.set_title('Tape Gap SDev', fontsize=12, fontweight='bold')
                else:
                    ax2.set_title('Roller Force XBar', fontsize=12, fontweight='bold')      # Roller Force XBar
                    ax6.set_title('Roller Force SDev', fontsize=12, fontweight='bold')      # Std Dev Plot

                    ax3.set_title('Tape Temp XBar', fontsize=12, fontweight='bold')         # Tape Temperature XBar
                    ax7.set_title('Tape Temp SDev', fontsize=12, fontweight='bold')         # Std Dev Plot

                    ax4.set_title('Delta Temp XBar', fontsize=12, fontweight='bold')        # Delta Temp XBar
                    ax8.set_title('Delta Temp SDev', fontsize=12, fontweight='bold')        # Std Dev Plot

                    ax5.set_title('Tape Gap XBar', fontsize=12, fontweight='bold')          # Tape Gap Measurement XBar
                    ax9.set_title('Tape Gap SDev', fontsize=12, fontweight='bold')          # Std Dev Plot

    # Define SQL Object connection ----------------------------------------------------------------[K]
    if RetroReplay:
        if stad != 0 and stpd == '0':                           # if WON is used in the search box
            gOEE = mP.seek_OEE_data(stad)
            print('\nWhats computed?', gOEE, stad)
        else:
            gOEE = mP.get_encodedFiles(StaSearchD)              # Computed OEE for specific date
    else:
        gOEE = mP.seek_OEE_data()                               # Computed OEE for current day real-time viz.
    gOEEStringed = "'"+gOEE+"'"                                 # Stringed for SQL syntax

    # To identify the current Process file on SQL server, the protocol loader is applied ----------[L]
    mPTablesID = conn.cursor()                                  # Get list of possible tables involved
    mProcessID = conn.cursor()
    mOEEDataID = conn.cursor()

    # Login to SQL server to confirm that OEE Table exist for current operations ------------------[M]
    print('\nVerifying the existence of OEE Data...')
    mOEE = mOEEDataID.execute('SELECT * FROM information_schema.Tables WHERE [Table_Name]=' + gOEEStringed).fetchone()
    time.sleep(5)                                               # Allow sQl refresh

    # Check if WON name sequence matches OEE table name ------------------------------[]
    if mOEE == None:
        print('No OEE Data generated. Machine in Off State..')
    else:
        dB_ShiftOEE = mOEE[2]
        print('\nFound OEE:', mOEE[2])  # Full OEE name ('DAQ', 'dbo', 'OEE_20240514', 'BASE TABLE')

    # Test for matching OEE Data ----------[]
    if mOEE != None and dB_ShiftOEE == gOEE:
        print('Loading Valid OEE Data...', dB_ShiftOEE)
        dB_ShiftOEEData = gOEE

    else:
        print('Sorry, no OEE Data found! Machine in Off State?')
        # exit('Exiting the program. Thanks for the Use')

    # ------------------------------- Load process Data from SQl View / Table ---------------------[N]
    if UsePLC_DBS:
        # Only use this option for real-time processing ---------------[]
        print('\nUsing PLC Data Source...')
        nTables = 'PLC dBlock'              # Table type
        # matchedOEE = dB_ShiftOEEData      # OEE TODO enable later
        matchedOEE = 'OEE_20240528'         # TODO disable later
        mTables = 16                        # Table count
        configH = 'R1R2R3R4'                # Default to real-time processing
        combo = configH
        rtWon = stad
        processWON.append(rtWon)
        print('\nLoading Available Ring Data..:', configH)
        print('=' * 27)

    else:       # Use SQL tables based on TCP1 configuration at manufacturing process -------------[O]
        # Compute numbers of process table by SQL Server Date or Work Order Number --[]
        print('\nUsing SQL Data Source...')
        if RetroReplay:  # for retrospective post-processing ------------------------[]
            print('\nSearching for valid record(s)...', stad)
            if stad != 0 and stpd == '0':  # WON is searched -------[]
                print('Work Order Number Search... True')
                DateSearch = False
                WonSearch = True  # OEE in the query list
                pTables = mPTablesID.execute('Select count(*) AS ValidTotal from Information_schema.Tables where '
                                             'TABLE_NAME like ' + "'" '%' + str(stad) + '%' "'").fetchone()
                time.sleep(4)                                             # allow SQL server response delay
                nTables = pTables[0]                                      # Pick total from sql column, add OEE table

                print('\nFound:', nTables, 'valid records..')
                if nTables == 0:
                    print('Invalid Work Order Number..')
                    errorWON()
                    exit()

                # List out all valid tables --------------------------[]
                mTables = mProcessID.execute(
                    'SELECT type_desc AS schema_name, name as table_name, create_date from '
                    'sys.tables where name LIKE ' + "'" '%' + str(stad) + '%' "'" + 'order by name asc').fetchmany(
                    nTables)
                # Check for Gap Data Table in SQL --------------------[]
                if 'R1H01_' + str(stad) == mTables[1][1]:
                    print('Gap Data exists..')
                else:
                    print('Cannot find Tape gap Data, are you dry running TCP01?')
                # print('\nTP01:', mTables)
                # print('TP02:', mTables[0][1])                 # Row 1, column 2 (OEE Table Name) | OEE_20240507
                # print('TP03:', mTables[1][1])                 # Row 2, column 2 (GapData 1st Table Name)
                processWON.append(str(stad))                    # Send details as work order for reference

                # Check if WON name sequence matches OEE table name ------------------------------[]
                if nTables != 0 and 'OEE_'+ str(stad) == mTables[0][1]:         # Check if OEE table name is included
                    matchedOEE = mTables[0][1]                                  # Include mTables[0][1]
                else:                                                           # Construct OEE name if not included
                    # reconstrue a valid name for OEE data, search and load into dynamic array
                    matchOEE = mTables[1][2]                                    # Obtain create date from date column
                    NewTable = str(matchOEE).split(' ', 1)          # split and remove time stamp string
                    matched = str(NewTable[0]).split('-', 2)        # Split date string into 3
                    OEEdata = 'OEE_' + matched[0] + matched[1] + matched[2]     # Use date to construct OEE table name
                    matchedOEE = OEEdata                                        # Constructed OEE Name to load
                print('Matched OEE Data:', matchedOEE)
            else:                                                               # Date search selected
                print('\nDate - WON Search... True')
                DateSearch = True
                WonSearch = False
                pTables = mPTablesID.execute('SELECT COUNT(create_date) AS ValidTotal from sys.tables where '
                                             'create_date BETWEEN ' + "'" + StaSearchD + "'" + ' AND ' + "'" + EndSearchD + "'").fetchone()
                time.sleep(10)                                                  # allow SQL server response delay
                nTables = pTables[0]                                            # pick values from sql column
                total_T = int(nTables)
                if not total_T % 2 == 0:                                        # Test value and add 1 if value is odd
                    nTables = pTables[0] + 1
                print('\nFound:', nTables, 'valid records..')
                # Search for tables created at specific dates ------------ TODO -----------------------------[]
                mTables = mProcessID.execute(
                    'SELECT schema_name(schema_id) as schema_name, name as table_name, create_date from '
                    'sys.tables where create_date BETWEEN ' + "'" + StaSearchD + "'" + ' AND '
                    + "'" + EndSearchD + "'" + 'order by table_name asc').fetchmany(nTables)

                # get the Work Order Name and keep for index-tracking ----
                print('\nList of Tables:', mTables)
                newWON = mTables[1][1]
                newWON = newWON.split('_')
                processWON.append(newWON[1])
                # Ensure compliance with 2 important header tables------------------------[]
                if newWON[1] == 'OEE_'+mTables[0][1]:                           # search for OEE compliant data
                    matchedOEE = mTables[0][1]
                else:
                    matchedOEE = 'OEE_' + newWON[1]                             # construe a valid OEE data and load
                if newWON[1] == 'R1H01_' + mTables[1][1]:
                    matchedPDATA = mTables[1][1]
                else:
                    matchedPDATA = 'R1H01_' + newWON[1]
                print('\nProcessing Job WON:', newWON[1])
        else:
            # Auto Synchroniser Using SQL Query ------------------------------------------------------------------[]
            print('\nSearching for valid live-data...')
            while True:
                    try:
                        pTables = mPTablesID.execute(
                            'SELECT COUNT(create_date) from sys.tables where create_date >= CAST(GETDATE() AS DATE)')\
                            .fetchone()
                        time.sleep(10)
                        nTables = pTables[0]                  # pick values and compare with length of loaded tables
                        print('RT-Synchroniser:', nTables, 'valid records found, rechecking...')
                        if nTables >= 4:                      # break wait search when SQL files are encountered
                            # Run query to identify each tables and load into SPC -------------------------------[A]
                            print('Found:', nTables, 'valid records')
                            mTables = mProcessID.execute(
                                'SELECT schema_name(schema_id) as schema_name, name as table_name, create_date'
                                ' from sys.tables where create_date >= CAST(GETDATE() AS DATE) order '
                                'by create_date asc').fetchmany(nTables)
                            break                                           # Stop loop and exit to next function

                        else:
                            # This scenario is valid only if try method fails or when re-processing live sql data--[B]
                            DateSearch = False
                            WonSearch = True
                            pTables = mPTablesID.execute(
                                'Select count(*) AS ValidTotal from Information_schema.Tables where '
                                'TABLE_NAME like ' + "'" '%' + str(stad) + '%' "'").fetchone()
                            time.sleep(10)                                      # allow SQL server response delay
                            nTables = pTables[0]                                # Pick total from sql column, add OEE
                            print('\nFound:', nTables, 'valid records..')
                            # List out all valid tables --------------------------[]
                            mTables = mProcessID.execute(
                                'SELECT type_desc AS schema_name, name as table_name, create_date from '
                                'sys.tables where name LIKE ' + "'" '%' + str(
                                    stad) + '%' "'" + 'order by name asc').fetchmany(nTables)

                            # print('\nTP01:', mTables[0])
                            # print('TP02:', mTables[0][1])                     # Row 1, column 2 (OEE Table Name)
                            # print('TP03:', mTables[1][1])                     # Row 2, column 2 (Table Name)
                            if 'R1H01_' + str(stad) != 'R1H01_' + mTables[1][1]:
                                print('Invalid SQL Table')
                                exit()
                            processWON.append(str(stad))  # Send details as work order for reference
                            # Compute and validate OEE data matches the WON ----[]
                            # Ensure compliance with 2 important header tables--[]
                            if 'OEE_' + str(stad) == 'OEE_' + mTables[0][1]:    # search for OEE compliant data
                                matchedOEE = mTables[0][1]
                            else:
                                matchedOEE = 'OEE_' + str(stad)  # construe a valid OEE data and load

                            # verify the headers gap measurement table ---------[]
                            if 'R1H01_' + str(stad) == 'R1H01_' + mTables[1][1]:
                                matchedPDATA = mTables[1][1]
                            else:
                                matchedPDATA = 'R1H01_' + str(stad)

                            break

                    except Exception as err:
                        print(f"Exception Error: '{err}'")

        # -------------- Detect TCP01 Process Data & RingHead Combinations ---------------------------------------[]
        mPTablesID.close()                              # Terminate connection briefly
        if nTables == 4:                                # 1 Active Ring in use
            if WonSearch:                               # If WON# is given instead of date
                oEE = matchedOEE                        # OEE Data
                gTM = mTables[0][1]                     # Gap tape Measurement
                rT1 = mTables[1][1]                     # RingXH12 Data
                rT2 = mTables[2][1]                     # RingXH34 Data
            elif DateSearch:                            # -------------------#
                oEE = matchedOEE                        # OEE Data
                gTM = matchedPDATA                      # Gap tape Measurement
                rT1 = mTables[1][1]                     # RingXH12 Data
                rT2 = mTables[2][1]                     # RingXH34 Data
            else:
                oEE = mTables[0][1]                     # OEE Data
                gTM = mTables[1][1]                     # Gap tape Measurement
                rT1 = mTables[2][1]                     # RingXH12 Data
                rT2 = mTables[3][1]                     # RingXH34 Data
            print('Loading Available Ring Data:', '\n', oEE, '\n', gTM, '\n', rT1, '\n', rT2)
            print('Sample Size:', smp_Sz, ' Slide Type', smp_St, oEE)
            print('=' * 27)
            # --- Strip the various ring head combo and combine for aggregated columns name---
            combo, N1, H1, H2 = rh.loadRHcombo(nTables, rT1, rT2, 0, 0, 0, 0, 0, 0)

        # Investigate and Acknowledge Ring Head Configuration --------------[CB]
        elif nTables == 6:                              # 2 Active Rings (4 SQL Tables)
            if WonSearch:                               # If WON# is given instead of date
                oEE = matchedOEE
                gTM = mTables[0][1]                     # Gap tape Measurement
                rT1 = mTables[1][1]                     # 1st Ring Head1-2
                rT2 = mTables[2][1]                     # 1st Ring Head3-4
                rT3 = mTables[3][1]                     # 2nd Ring Head1-2
                rT4 = mTables[4][1]                     # 2nd Ring Head 3-4
            elif DateSearch:
                oEE = matchedOEE                        # OEE Data
                gTM = matchedPDATA                      # Gap tape Measurement
                rT1 = mTables[1][1]                     # RingXH12 Data
                rT2 = mTables[2][1]                     # RingXH34 Data
                rT3 = mTables[3][1]                     # 2nd Ring Head1-2
                rT4 = mTables[4][1]                     # 2nd Ring Head 3-4
            else:
                oEE = mTables[0][1]                     # OEE Data
                gTM = mTables[1][1]                     # Gap tape Measurement
                rT1 = mTables[2][1]                     # 1st Ring Head1-2
                rT2 = mTables[3][1]                     # 1st Ring Head3-4
                rT3 = mTables[4][1]                     # 2nd Ring Head1-2
                rT4 = mTables[5][1]                     # 2nd Ring Head 3-4
            print('Loading Available Ring Data:', '\n', oEE, '\n', gTM, '\n', rT1, '\n', rT2, '\n', rT3, '\n', rT4)
            print('Sample Size:', smp_Sz, ' Slide Type', smp_St)
            print('=' * 27)
            # --- Strip the various ring head prefixes and combine to meet the formatted style
            combo, N1, N2, H1, H2, H3, H4 = rh.loadRHcombo(nTables, rT1, rT2, rT3, rT4, 0, 0, 0, 0)

        # Investigate and Acknowledge Ring Head Configuration --------------[CC]
        elif nTables == 8:                              # 3 Active Rings (6 SQL tables)
            if WonSearch:                               # If WON# is given instead of date
                print('\nSEARCH BY WON...')
                oEE = matchedOEE                        # OEE Data
                gTM = mTables[0][1]                     # Gap tape Measurement
                rT1 = mTables[1][1]                     # 1st Ring Head1-2
                rT2 = mTables[2][1]                     # 1st Ring Head3-4
                rT3 = mTables[3][1]                     # 2nd Ring Head1-2
                rT4 = mTables[4][1]                     # 2nd Ring Head3-4
                rT5 = mTables[5][1]                     # 3rd Ring Head1-2
                rT6 = mTables[6][1]                     # 3rd Ring Head3-4
            elif DateSearch:
                print('\nSEARCH BY DATE...')
                oEE = matchedOEE                        # OEE Data
                gTM = matchedPDATA                      # Gap tape Measurement
                rT1 = mTables[1][1]                     # 1st Ring Head1-2
                rT2 = mTables[2][1]                     # 1st Ring Head3-4
                rT3 = mTables[3][1]                     # 2nd Ring Head1-2
                rT4 = mTables[4][1]                     # 2nd Ring Head3-4
                rT5 = mTables[5][1]                     # 3rd Ring Head1-2
                rT6 = mTables[6][1]                     # 3rd Ring Head3-4
            else:
                oEE = mTables[0][1]                     # OEE Data
                gTM = mTables[1][1]                     # Gap tape Measurement
                rT1 = mTables[2][1]                     # 1st Ring Head1-2
                rT2 = mTables[3][1]                     # 2nd Ring Head1-2
                rT3 = mTables[4][1]                     # 2nd Ring Head1-2
                rT4 = mTables[5][1]                     # 2nd Ring Head3-4
                rT5 = mTables[6][1]                     # 3rd Ring Head1-2
                rT6 = mTables[7][1]                     # 3rd Ring Head3-4

            print('Loading Available Ring Data:', '\n', oEE, '\n', gTM, '\n', rT1, '\n', rT2, '\n', rT3, '\n', rT4, '\n', rT5, '\n', rT6)
            print('Sample Size:', smp_Sz, ' Slide Type', smp_St)
            print('=' * 27)
            # --- Strip the various ring head combo and combine for aggregated columns name---
            combo, N1, N2, N3, H1, H2, H3, H4, H5, H6 = rh.loadRHcombo(nTables, rT1, rT2, rT3, rT4, rT5, rT6, 0, 0)

        # Investigate and Acknowledge Ring Head Configuration --------------[CD] TODO ---- start!
        elif nTables >= 10:                             # 4 Active Rings (8 SQL Tables)
            if WonSearch:                               # If WON# is given instead of date
                print('\nSEARCH BY WON...')
                oEE = matchedOEE                        # OEE data
                gTM = mTables[1][1]                     # Tape Gap Measurement
                rT1 = mTables[2][1]                     # Ring 1 Head 1,2
                rT2 = mTables[3][1]                     # Ring 1 Head 3,4
                rT3 = mTables[4][1]                     # Ring 2 Head 1,2
                rT4 = mTables[5][1]                     # Ring 2 Head 3,4
                rT5 = mTables[6][1]                     # Ring 3 Head 1,2
                rT6 = mTables[7][1]                     # Ring 3 Head 3,4
                rT7 = mTables[8][1]                     # Ring 4 Head 1,2
                rT8 = mTables[9][1]                     # Ring 4 Head 3,4
            elif DateSearch:
                print('\nSEARCH BY DATE...')
                oEE = matchedOEE                        # OEE data
                gTM = matchedPDATA                      # Gap tape Measurement
                rT1 = mTables[2][1]                     # Ring 1 Head 1,2
                rT2 = mTables[3][1]                     # Ring 1 Head 3,4
                rT3 = mTables[4][1]                     # Ring 2 Head 1,2
                rT4 = mTables[5][1]                     # Ring 2 Head 3,4
                rT5 = mTables[6][1]                     # Ring 3 Head 1,2
                rT6 = mTables[7][1]                     # Ring 3 Head 3,4
                rT7 = mTables[8][1]                     # Ring 4 Head 1,2
                rT8 = mTables[9][1]                     # Ring 4 Head 3,4
            else:                                       # OEE found in query list
                oEE = mTables[0][1]                     # OEE Data
                gTM = mTables[1][1]                     # Gap tape Measurement
                rT1 = mTables[2][1]                     # 1st Ring Head1-2
                rT2 = mTables[3][1]                     # 2nd Ring Head1-2
                rT3 = mTables[4][1]                     # 2nd Ring Head1-2
                rT4 = mTables[5][1]                     # 2nd Ring Head3-4
                rT5 = mTables[6][1]                     # 3rd Ring Head1-2
                rT6 = mTables[7][1]                     # 3rd Ring Head3-4
                rT7 = mTables[8][1]                     # Ring 4 Head 1,2
                rT8 = mTables[9][1]                     # Ring 4 Head 3,4

            print('\nLoading Available Ring Data:', '\n', oEE, '\n', gTM, '\n', rT1, '\n', rT2, '\n', rT3, '\n', rT4, '\n', rT5, '\n', rT6, '\n',
                  rT7, '\n', rT8)
            print('Sample Size:', smp_Sz, ' Slide Type', smp_St)
            print('=' * 27)
            # --- Strip the various ring head combo and combine for aggregated columns name---
            # SQl Table Names encoded as H1, H2, etc. combo is the RingHead Combinations
            combo, H1, H2, H3, H4, H5, H6, H7, H8 = rh.loadRHcombo(nTables, rT1, rT2, rT3, rT4, rT5, rT6, rT7, rT8)

        else:
            print('\nSorry, expected minimum valid process record is 4!')
            exit()
    # =========================================END OF CONFIG =====================================END

    # Compute Ring Head Combinations for SQL or PLC Query ----------------------------------------[]
    R1, R2, R3, R4 = vd.validDrive(combo)  # Call function to determined valid Rings

    # ------ Plot Production Monitoring Parameters ----------------------------------------------[1]
    if monitorParamLP and DNVspecify and asp:  # Laser Power Cure
        # if R1 and R2 and R3 and R4:
        im1a, = ax.plot([], [], 'o-', label='R1 - Laser Power(W)')
        im1b, = ax.plot([], [], 'o-', label='R2 - Laser Power(W)')
        im1c, = ax.plot([], [], 'o-', label='R3 - Laser Power(W)')
        im1d, = ax.plot([], [], 'o-', label='R4 - Laser Power(W)')
        # -------------------- ASP Activated ----------------------#
        im2a, = axa.plot([], [], 'o-', label='R1 - LP')
        im2b, = axa.plot([], [], 'o-', label='R2 - LP')
        im2c, = axa.plot([], [], 'o-', label='R3 - LP')
        im2d, = axa.plot([], [], 'o-', label='R4 - LP')
    elif monitorParamLA and DNVspecify and asp:
        im1a, = ax.plot([], [], 'o-', label='R1 - Laser Angle(Deg)')
        im1b, = ax.plot([], [], 'o-', label='R2 - Laser Angle(Deg)')
        im1c, = ax.plot([], [], 'o-', label='R3 - Laser Angle(Deg)')
        im1d, = ax.plot([], [], 'o-', label='R4 - Laser Angle(Deg)')
        # --------------------ASP Activated -----------------------#
        im2a, = axa.plot([], [], 'o-', label='R1 - LA')
        im2b, = axa.plot([], [], 'o-', label='R2 - LA')
        im2c, = axa.plot([], [], 'o-', label='R3 - LA')
        im2d, = axa.plot([], [], 'o-', label='R4 - LA')
    # --------------------------- on DNV plot ---------------------#
    elif DNVspecify:
        if monitorParamLP and monitorParamLA:
            # ---------------[LP]
            im1a, = ax.plot([], [], 'o-', label='R1 - Laser Power(W)')
            im1b, = ax.plot([], [], 'o-', label='R2 - Laser Power(W)')
            im1c, = ax.plot([], [], 'o-', label='R3 - Laser Power(W)')
            im1d, = ax.plot([], [], 'o-', label='R4 - Laser Power(W)')
            # ---------------[LA]
            im2a, = axa.plot([], [], 'o-', label='R1 - Laser Angle(Deg)')
            im2b, = axa.plot([], [], 'o-', label='R2 - Laser Angle(Deg)')
            im2c, = axa.plot([], [], 'o-', label='R3 - Laser Angle(Deg)')
            im2d, = axa.plot([], [], 'o-', label='R4 - Laser Angle(Deg)')
        else:
            if monitorParamLP:
                # ------------Laser Power -------------------------#
                im1a, = ax.plot([], [], 'o-', label='R1 - Laser Power(W)')
                im1b, = ax.plot([], [], 'o-', label='R2 - Laser Power(W)')
                im1c, = ax.plot([], [], 'o-', label='R3 - Laser Power(W)')
                im1d, = ax.plot([], [], 'o-', label='R4 - Laser Power(W)')
            elif monitorParamLA:
                # ------------Laser Angle -------------------------#
                im2a, = ax.plot([], [], 'o-', label='R1 - Laser Angle(Deg)')
                im2b, = ax.plot([], [], 'o-', label='R2 - Laser Angle(Deg)')
                im2c, = ax.plot([], [], 'o-', label='R3 - Laser Angle(Deg)')
                im2d, = ax.plot([], [], 'o-', label='R4 - Laser Angle(Deg)')
    # -------------------------- on TFMC plot ---------------------------#
    else:
        print('\nTFMC processing....02')
        if monitorParamLP:      # Laser Angle Cure
            im1a, = ax.plot([], [], 'o-', label='R1 - Laser Power(W)')
            im1b, = ax.plot([], [], 'o-', label='R2 - Laser Power(W)')
            im1c, = ax.plot([], [], 'o-', label='R3 - Laser Power(W)')
            im1d, = ax.plot([], [], 'o-', label='R4 - Laser Power(W)')
        else:
            im1a, = ax.plot([], [], 'o-', label='R1 - Laser Angle(Deg)')
            im1b, = ax.plot([], [], 'o-', label='R2 - Laser Angle(Deg)')
            im1c, = ax.plot([], [], 'o-', label='R3 - Laser Angle(Deg)')
            im1d, = ax.plot([], [], 'o-', label='R4 - Laser Angle(Deg)')

    # DEFINE PLOTS' LEGEND Mean Plots & Std Dev Plots ===========================================[]
    # Define Procedure ---------------------------[TODO VARIABLES PER HEAD]
    if VarPerHeadA:
        if RollerPressure:
            print('\nRP Variable VarPerHeadA activated...')
            axp1 = ax2
            axp2 = ax6

            if R1:
                im6, = axp1.plot([], [], 'o-.', label='Roller Pressure(N) - (R1H1)')
                im7, = axp1.plot([], [], 'o-', label='Roller Pressure(N) - (R1H2)')
                im8, = axp1.plot([], [], 'o-', label='Roller Pressure(N) - (R1H3)')
                im9, = axp1.plot([], [], 'o-', label='Roller Pressure(N) - (R1H4)')
                im10, = axp2.plot([], [], 'o-', label='Roller Pressure(N)')
                im11, = axp2.plot([], [], 'o-', label='Roller Pressure(N)')
                im12, = axp2.plot([], [], 'o-', label='Roller Pressure(N)')
                im13, = axp2.plot([], [], 'o-', label='Roller Pressure(N)')

            if R2:
                im14, = axp1.plot([], [], 'o-.', label='Roller Pressure(N) - (R2H1)')
                im15, = axp1.plot([], [], 'o-', label='Roller Pressure(N) - (R2H2)')
                im16, = axp1.plot([], [], 'o-', label='Roller Pressure(N) - (R2H3)')
                im17, = axp1.plot([], [], 'o-', label='Roller Pressure(N) - (R2H4)')
                im18, = axp2.plot([], [], 'o-', label='Roller Pressure(N)')
                im19, = axp2.plot([], [], 'o-', label='Roller Pressure(N)')
                im20, = axp2.plot([], [], 'o-', label='Roller Pressure(N)')
                im21, = axp2.plot([], [], 'o-', label='Roller Pressure(N)')

            if R3:
                im22, = axp1.plot([], [], 'o-.', label='Roller Pressure(N) - (R3H1)')
                im23, = axp1.plot([], [], 'o-', label='Roller Pressure(N) - (R3H2)')
                im24, = axp1.plot([], [], 'o-', label='Roller Pressure(N) - (R3H3)')
                im25, = axp1.plot([], [], 'o-', label='Roller Pressure(N) - (R3H4)')
                im26, = axp2.plot([], [], 'o-', label='Roller Pressure(N)')
                im27, = axp2.plot([], [], 'o-', label='Roller Pressure(N)')
                im28, = axp2.plot([], [], 'o-', label='Roller Pressure(N)')
                im29, = axp2.plot([], [], 'o-', label='Roller Pressure(N)')

            if R4:
                im30, = axp1.plot([], [], 'o-.', label='Roller Pressure(N) - (R4H1)')
                im31, = axp1.plot([], [], 'o-', label='Roller Pressure(N) - (R4H2)')
                im32, = axp1.plot([], [], 'o-', label='Roller Pressure(N) - (R4H3)')
                im33, = axp1.plot([], [], 'o-', label='Roller Pressure(N) - (R4H4)')
                im34, = axp2.plot([], [], 'o-', label='Roller Pressure(N)')
                im35, = axp2.plot([], [], 'o-', label='Roller Pressure(N)')
                im36, = axp2.plot([], [], 'o-', label='Roller Pressure(N)')
                im37, = axp2.plot([], [], 'o-', label='Roller Pressure(N)')

        elif Manu_TapeSpeed:
            print('CT Variable VarPerHeadA activated...')
            axp1 = ax2
            axp2 = ax6

            if R1:
                im38, = axp1.plot([], [], 'o-.', label='Tape Speed(mm/s) - (R1H1)')
                im39, = axp1.plot([], [], 'o-', label='Tape Speed(mm/s)- (R1H2)')
                im40, = axp1.plot([], [], 'o-', label='Tape Speed(mm/s) - (R1H3)')
                im41, = axp1.plot([], [], 'o-', label='Tape Speed(mm/s) - (R1H4)')
                im42, = axp2.plot([], [], 'o-', label='Tape Speed')
                im43, = axp2.plot([], [], 'o-', label='Tape Speed')
                im44, = axp2.plot([], [], 'o-', label='Tape Speed')
                im45, = axp2.plot([], [], 'o-', label='Tape Speed')

            if R2:
                im46, = axp1.plot([], [], 'o-.', label='Tape Speed(mm/s) - (R2H1)')
                im47, = axp1.plot([], [], 'o-', label='Tape Speed(mm/s) - (R2H2)')
                im48, = axp1.plot([], [], 'o-', label='Tape Speed(mm/s) - (R2H3)')
                im49, = axp1.plot([], [], 'o-', label='Tape Speed(mm/s) - (R2H4)')
                im50, = axp2.plot([], [], 'o-', label='Tape Speed')
                im51, = axp2.plot([], [], 'o-', label='Tape Speed')
                im52, = axp2.plot([], [], 'o-', label='Tape Speed')
                im53, = axp2.plot([], [], 'o-', label='Tape Speed')

            if R3:
                im54, = axp1.plot([], [], 'o-.', label='Tape Speed(mm/s) - (R3H1)')
                im55, = axp1.plot([], [], 'o-', label='Tape Speed(mm/s) - (R3H2)')
                im56, = axp1.plot([], [], 'o-', label='Tape Speed(mm/s) - (R3H3)')
                im57, = axp1.plot([], [], 'o-', label='Tape Speed(mm/s) - (R3H4)')
                im58, = axp2.plot([], [], 'o-', label='Tape Speed')
                im59, = axp2.plot([], [], 'o-', label='Tape Speed')
                im60, = axp2.plot([], [], 'o-', label='Tape Speed')
                im61, = axp2.plot([], [], 'o-', label='Tape Speed')

            if R4:
                im62, = axp1.plot([], [], 'o-.', label='Tape Speed(mm/s) - (R4H1)')
                im63, = axp1.plot([], [], 'o-', label='Tape Speed(mm/s) - (R4H2)')
                im64, = axp1.plot([], [], 'o-', label='Tape Speed(mm/s) - (R4H3)')
                im65, = axp1.plot([], [], 'o-', label='Tape Speed(mm/s) - (R4H4)')
                im66, = axp2.plot([], [], 'o-', label='Tape Speed')
                im67, = axp2.plot([], [], 'o-', label='Tape Speed')
                im68, = axp2.plot([], [], 'o-', label='Tape Speed')
                im69, = axp2.plot([], [], 'o-', label='Tape Speed')

        elif TapeTemperatur:
            print('CT Variable VarPerHeadA activated...')
            axp1 = ax2
            axp2 = ax6

            if R1:
                im70, = axp1.plot([], [], 'o-.', label='Tape Temp(°C) - (R1H1)')
                im71, = axp1.plot([], [], 'o-', label='Tape Temp(°C) - (R1H2)')
                im72, = axp1.plot([], [], 'o-', label='Tape Temp(°C) - (R1H3)')
                im73, = axp1.plot([], [], 'o-', label='Tape Temp(°C) - (R1H4)')
                im74, = axp2.plot([], [], 'o-', label='Tape Temp(°C)')
                im75, = axp2.plot([], [], 'o-', label='Tape Temp(°C)')
                im76, = axp2.plot([], [], 'o-', label='Tape Temp(°C)')
                im77, = axp2.plot([], [], 'o-', label='Tape Temp(°C)')

            if R2:
                im78, = axp1.plot([], [], 'o-.', label='Tape Temp(°C) - (R2H1)')
                im79, = axp1.plot([], [], 'o-', label='Tape Temp(°C) - (R2H2)')
                im80, = axp1.plot([], [], 'o-', label='Tape Temp(°C) - (R2H3)')
                im81, = axp1.plot([], [], 'o-', label='Tape Temp(°C) - (R2H4)')
                im82, = axp2.plot([], [], 'o-', label='Tape Temp(°C)')
                im83, = axp2.plot([], [], 'o-', label='Tape Temp(°C)')
                im84, = axp2.plot([], [], 'o-', label='Tape Temp(°C)')
                im85, = axp2.plot([], [], 'o-', label='Tape Temp(°C)')

            if R3:
                im86, = axp1.plot([], [], 'o-.', label='Tape Temp(°C) - (R3H1)')
                im87, = axp1.plot([], [], 'o-', label='Tape Temp(°C) - (R3H2)')
                im88, = axp1.plot([], [], 'o-', label='Tape Temp(°C) - (R3H3)')
                im89, = axp1.plot([], [], 'o-', label='Tape Temp(°C) - (R3H4)')
                im90, = axp2.plot([], [], 'o-', label='Tape Temp(°C)')
                im91, = axp2.plot([], [], 'o-', label='Tape Temp(°C)')
                im92, = axp2.plot([], [], 'o-', label='Tape Temp(°C)')
                im93, = axp2.plot([], [], 'o-', label='Tape Temp(°C)')

            if R4:
                im94, = axp1.plot([], [], 'o-.', label='Tape Temp(°C) - (R4H1)')
                im95, = axp1.plot([], [], 'o-', label='Tape Temp(°C) - (R4H2)')
                im96, = axp1.plot([], [], 'o-', label='Tape Temp(°C) - (R4H3)')
                im97, = axp1.plot([], [], 'o-', label='Tape Temp(°C) - (R4H4)')
                im98, = axp2.plot([], [], 'o-', label='Tape Temp(°C)')
                im99, = axp2.plot([], [], 'o-', label='Tape Temp(°C)')
                im100, = axp2.plot([], [], 'o-', label='Tape Temp(°C)')
                im101, = axp2.plot([], [], 'o-', label='Tape Temp(°C)')

        elif TSub_TempRatio:
            print('DT Variable VarPerHeadA activated...')
            axp1 = ax2
            axp2 = ax6
            if DNVspecify:
                lbl = 'Temp Ratio'
            else:
                lbl = 'Delta Temp'
            if R1:
                im102, = axp1.plot([], [], 'o-.', label=lbl+' (°C) - (R1H1)')
                im103, = axp1.plot([], [], 'o-', label=lbl+' (°C) - (R1H2)')
                im104, = axp1.plot([], [], 'o-', label=lbl+' (°C) - (R1H3)')
                im105, = axp1.plot([], [], 'o-', label=lbl+' (°C) - (R1H4)')
                im106, = axp2.plot([], [], 'o-', label=lbl)
                im107, = axp2.plot([], [], 'o-', label=lbl)
                im108, = axp2.plot([], [], 'o-', label=lbl)
                im109, = axp2.plot([], [], 'o-', label=lbl)

            if R2:
                im110, = axp1.plot([], [], 'o-.', label=lbl+' (°C) - (R2H1)')
                im111, = axp1.plot([], [], 'o-', label=lbl+' (°C) - (R2H2)')
                im112, = axp1.plot([], [], 'o-', label=lbl+' (°C) - (R2H3)')
                im113, = axp1.plot([], [], 'o-', label=lbl+' (°C) - (R2H4)')
                im114, = axp2.plot([], [], 'o-', label=lbl)
                im115, = axp2.plot([], [], 'o-', label=lbl)
                im116, = axp2.plot([], [], 'o-', label=lbl)
                im117, = axp2.plot([], [], 'o-', label=lbl)

            if R3:
                im118, = axp1.plot([], [], 'o-.', label=lbl+' (°C) - (R3H1)')
                im119, = axp1.plot([], [], 'o-', label=lbl+' (°C) - (R3H2)')
                im120, = axp1.plot([], [], 'o-', label=lbl+' (°C) - (R3H13')
                im121, = axp1.plot([], [], 'o-', label=lbl+' (°C) - (R3H4)')
                im122, = axp2.plot([], [], 'o-', label=lbl)
                im123, = axp2.plot([], [], 'o-', label=lbl)
                im124, = axp2.plot([], [], 'o-', label=lbl)
                im125, = axp2.plot([], [], 'o-', label=lbl)

            if R4:
                im126, = axp1.plot([], [], 'o-.', label=lbl+' (°C) - (R4H1)')
                im127, = axp1.plot([], [], 'o-', label=lbl+' (°C) - (R4H2)')
                im128, = axp1.plot([], [], 'o-', label=lbl+' (°C) - (R4H3)')
                im129, = axp1.plot([], [], 'o-', label=lbl+' (°C) - (R4H4)')
                im130, = axp2.plot([], [], 'o-', label=lbl)
                im131, = axp2.plot([], [], 'o-', label=lbl)
                im132, = axp2.plot([], [], 'o-', label=lbl)
                im133, = axp2.plot([], [], 'o-', label=lbl)

        elif GapMeasurement:
            xa = ax6
            # if Segment #1 is enabled:
            im134, = ax2.plot([], [], 'o-.', label='Gap Measurement - (A1)')
            im135, = ax2.plot([], [], 'o-', label='Gap Measurement - (B1)')
            im136, = xa.plot([], [], 'o-', label='Tape Gap')
            im137, = xa.plot([], [], 'o-', label='Tape Gap')

            # if Segment #2 is enabled:
            im138, = ax2.plot([], [], 'o-.', label='Gap Measurement - (A2)')
            im139, = ax2.plot([], [], 'o-', label='Gap Measurement - (B2)')
            im140, = xa.plot([], [], 'o-', label='Tape Gap')
            im141, = xa.plot([], [], 'o-', label='Tape Gap')

            # if Segment #3 is enabled:
            im142, = ax2.plot([], [], 'o-.', label='Gap Measurement - (A3)')
            im143, = ax2.plot([], [], 'o-', label='Gap Measurement - (B3)')
            im144, = xa.plot([], [], 'o-', label='Tape Gap')
            im145, = xa.plot([], [], 'o-', label='Tape Gap')

            # if Segment #4 is enabled:
            im146, = ax2.plot([], [], 'o-.', label='Gap Measurement - (A4)')
            im147, = ax2.plot([], [], 'o-', label='Gap Measurement - (B4)')
            im148, = xa.plot([], [], 'o-', label='Tape Gap')
            im149, = xa.plot([], [], 'o-', label='Tape Gap')

    elif VarPerHeadB:
        # VariProcess & VarPerHeadB ----------- Yielding up to 16 variables plot per 4 window
        if RollerPressure:
            if R1:
                axb = ax2
                axB = ax6
                # Performed transposition on axes plot ------------------------#
                im6, = axb.plot([], [], 'o-', label='R1H1 - Roller Pressure(N)')
                im7, = axb.plot([], [], 'o-', label='R1H2 - Roller Pressure(N)')
                im8, = axb.plot([], [], 'o-', label='R1H3 - Roller Pressure(N)')
                im9, = axb.plot([], [], 'o-', label='R1H4 - Roller Pressure(N)')
                # ------------
                im10, = axB.plot([], [], 'o-', label='Roller Pressure(N)')
                im11, = axB.plot([], [], 'o-', label='Roller Pressure(N)')
                im12, = axB.plot([], [], 'o-', label='Roller Pressure(N)')
                im13, = axB.plot([], [], 'o-', label='Roller Pressure(N)')

            if R2:
                axesA = ax3
                axesB = ax7
                im14, = axesA.plot([], [], 'o-.', label='R2H1 - Roller Pressure(N)')
                im15, = axesA.plot([], [], 'o-', label='R2H2 - Roller Pressure(N)')
                im16, = axesA.plot([], [], 'o-', label='R2H3 - Roller Pressure(N)')
                im17, = axesA.plot([], [], 'o-', label='R2H4 - Roller Pressure(N)')
                # -------------
                im18, = axesB.plot([], [], 'o-', label='Roller Pressure(N)')
                im19, = axesB.plot([], [], 'o-', label='Roller Pressure(N)')
                im20, = axesB.plot([], [], 'o-', label='Roller Pressure(N)')
                im21, = axesB.plot([], [], 'o-', label='Roller Pressure(N)')

            if R3:
                axesC = ax4
                axesD = ax8
                im22, = axesC.plot([], [], 'o-.', label='R3H1 - Roller Pressure(N)')
                im23, = axesC.plot([], [], 'o-', label='R3H2 - Roller Pressure(N)')
                im24, = axesC.plot([], [], 'o-', label='R3H3 - Roller Pressure(N)')
                im25, = axesC.plot([], [], 'o-', label='R3H4 - Roller Pressure(N)')
                im26, = axesD.plot([], [], 'o-', label='Roller Pressure(N)')
                im27, = axesD.plot([], [], 'o-', label='Roller Pressure(N)')
                im28, = axesD.plot([], [], 'o-', label='Roller Pressure(N)')
                im29, = axesD.plot([], [], 'o-', label='Roller Pressure(N)')

            if R4:
                axesE = ax5
                axesF = ax9
                im30, = axesE.plot([], [], 'o-.', label='R4H1 - Roller Pressure(N)')
                im31, = axesE.plot([], [], 'o-', label='R4H2 - Roller Pressure(N)')
                im32, = axesE.plot([], [], 'o-', label='R4H3 - Roller Pressure(N)')
                im33, = axesE.plot([], [], 'o-', label='R4H4 - Roller Pressure(N)')
                im34, = axesF.plot([], [], 'o-', label='Roller Pressure(N)')
                im35, = axesF.plot([], [], 'o-', label='Roller Pressure(N)')
                im36, = axesF.plot([], [], 'o-', label='Roller Pressure(N)')
                im37, = axesF.plot([], [], 'o-', label='Roller Pressure(N)')

        elif Manu_TapeSpeed:
            if R1:
                # valid for VarPerHeadB only
                axT = ax2
                axt = ax6
                im38, = axT.plot([], [], 'o-', label='R1H1 - Tape Speed')
                im39, = axT.plot([], [], 'o-', label='R1H2 - Tape Speed')
                im40, = axT.plot([], [], 'o-', label='R1H3 - Tape Speed')
                im41, = axT.plot([], [], 'o-', label='R1H4 - Tape Speed')
                # ------------
                im42, = axt.plot([], [], 'o-', label='Tape Speed')
                im43, = axt.plot([], [], 'o-', label='Tape Speed')
                im44, = axt.plot([], [], 'o-', label='Tape Speed')
                im45, = axt.plot([], [], 'o-', label='Tape Speed')

            if R2:
                axesT2 = ax3
                axest2 = ax7
                im46, = axesT2.plot([], [], 'o-', label='R2H1 - Tape Speed')
                im47, = axesT2.plot([], [], 'o-', label='R2H2 - Tape Speed')
                im48, = axesT2.plot([], [], 'o-', label='R2H3 - Tape Speed')
                im49, = axesT2.plot([], [], 'o-', label='R2H4 - Tape Speed')
                # -------------
                im50, = axest2.plot([], [], 'o-', label='Tape Speed')
                im51, = axest2.plot([], [], 'o-', label='Tape Speed')
                im52, = axest2.plot([], [], 'o-', label='Tape Speed')
                im53, = axest2.plot([], [], 'o-', label='Tape Speed')

            if R3:
                axesT3 = ax4
                axest3 = ax8
                im54, = axesT3.plot([], [], 'o-.', label='R3H1 - Tape Speed')
                im55, = axesT3.plot([], [], 'o-', label='R3H2 - Tape Speed')
                im56, = axesT3.plot([], [], 'o-', label='R3H3 - Tape Speed')
                im57, = axesT3.plot([], [], 'o-', label='R3H4 - Tape Speed')
                im58, = axest3.plot([], [], 'o-', label='Tape Speed')
                im59, = axest3.plot([], [], 'o-', label='Tape Speed')
                im60, = axest3.plot([], [], 'o-', label='Tape Speed')
                im61, = axest3.plot([], [], 'o-', label='Tape Speed')

            if R4:
                axesT4 = ax5
                axest4 = ax9
                im62, = axesT4.plot([], [], 'o-.', label='R4H1 - Tape Speed')
                im63, = axesT4.plot([], [], 'o-', label='R4H2 - Tape Speed')
                im64, = axesT4.plot([], [], 'o-', label='R4H3 - Tape Speed')
                im65, = axesT4.plot([], [], 'o-', label='R4H4 - Tape Speed')
                im66, = axest4.plot([], [], 'o-', label='Tape Speed')
                im67, = axest4.plot([], [], 'o-', label='Tape Speed')
                im68, = axest4.plot([], [], 'o-', label='Tape Speed')
                im69, = axest4.plot([], [], 'o-', label='Tape Speed')

        elif TapeTemperatur:
            if R1:
                axH0 = ax2
                axH1 = ax6
                print('Tape Temp Plot Axis defined for Ring1...')
                im70, = axH0.plot([], [], 'o-.', label='R1H1 - Tape Temp(°C)')
                im71, = axH0.plot([], [], 'o-', label='R1H2 - Tape Temp(°C)')
                im72, = axH0.plot([], [], 'o-', label='R1H3 - Tape Temp(°C)')
                im73, = axH0.plot([], [], 'o-', label='R1H4 - Tape Temp(°C)')
                im74, = axH1.plot([], [], 'o-', label='Tape Temp(°C)')
                im75, = axH1.plot([], [], 'o-', label='Tape Temp(°C)')
                im76, = axH1.plot([], [], 'o-', label='Tape Temp(°C)')
                im77, = axH1.plot([], [], 'o-', label='Tape Temp(°C)')

            if R2:
                axG = ax3
                axH = ax7
                im78, = axG.plot([], [], 'o-', label='R2H1 - Tape Temp(°C)')
                im79, = axG.plot([], [], 'o-', label='R2H2 - Tape Temp(°C)')
                im80, = axG.plot([], [], 'o-', label='R2H3 - Tape Temp(°C)')
                im81, = axG.plot([], [], 'o-', label='R2H4 - Tape Temp(°C)')
                im82, = axH.plot([], [], 'o-', label='Tape Temp(°C)')
                im83, = axH.plot([], [], 'o-', label='Tape Temp(°C)')
                im84, = axH.plot([], [], 'o-', label='Tape Temp(°C)')
                im85, = axH.plot([], [], 'o-', label='Tape Temp(°C)')

            if R3:
                axesI = ax4
                axesJ = ax8
                im86, = axesI.plot([], [], 'o-', label='R3H1 - Tape Temp(°C)')
                im87, = axesI.plot([], [], 'o-', label='R3H2 - Tape Temp(°C)')
                im88, = axesI.plot([], [], 'o-', label='R3H3 - Tape Temp(°C)')
                im89, = axesI.plot([], [], 'o-', label='R3H4 - Tape Temp(°C)')
                im90, = axesJ.plot([], [], 'o-', label='Tape Temp(°C)')
                im91, = axesJ.plot([], [], 'o-', label='Tape Temp(°C)')
                im92, = axesJ.plot([], [], 'o-', label='Tape Temp(°C)')
                im93, = axesJ.plot([], [], 'o-', label='Tape Temp(°C)')

            if R4:
                axesK = ax5
                axesL = ax9
                im94, = axesK.plot([], [], 'o-', label='R4H1 - Tape Temp(°C)')
                im95, = axesK.plot([], [], 'o-', label='R4H2 - Tape Temp(°C)')
                im96, = axesK.plot([], [], 'o-', label='R4H3 - Tape Temp(°C)')
                im97, = axesK.plot([], [], 'o-', label='R4H4 - Tape Temp(°C)')
                im98, = axesL.plot([], [], 'o-', label='Tape Temp(°C)')
                im99, = axesL.plot([], [], 'o-', label='Tape Temp(°C)')
                im100, = axesL.plot([], [], 'o-', label='Tape Temp(°C)')
                im101, = axesL.plot([], [], 'o-', label='Tape Temp(°C)')

        # ---------------------- End of Addition DNV -------------------------------[]
        elif TSub_TempRatio:
            if R1:
                if DNVspecify:
                    if VarPerHeadB:
                        axN0 = ax2
                        axN1 = ax6
                    req = 'Temp Ratio (°C)'
                else:
                    axN0 = ax2
                    axN1 = ax6
                    req = 'Delta Temp (°C)'

                im102, = axN0.plot([], [], 'o-', label='R1H1 - ' + req)
                im103, = axN0.plot([], [], 'o-', label='R1H2 - ' + req)
                im104, = axN0.plot([], [], 'o-', label='R1H3 - ' + req)
                im105, = axN0.plot([], [], 'o-', label='R1H4 - ' + req)
                im106, = axN1.plot([], [], 'o-', label=req)
                im107, = axN1.plot([], [], 'o-', label=req)
                im108, = axN1.plot([], [], 'o-', label=req)
                im109, = axN1.plot([], [], 'o-', label=req)

            if R2:
                if DNVspecify:
                    if VarPerHeadB:
                        axesM = ax3
                        axesN = ax7
                    req = 'Temp Ratio (°C)'     # VarPerHeadB:  One variable per plot of 4 windows [R1, R2, R3, R4]
                else:
                    axesM = ax3
                    axesN = ax7
                    req = 'Delta Temp (°C)'
                im110, = axesM.plot([], [], 'o-', label='R2H1 - ' + req)
                im111, = axesM.plot([], [], 'o-', label='R2H2 - ' + req)
                im112, = axesM.plot([], [], 'o-', label='R2H3 - ' + req)
                im113, = axesM.plot([], [], 'o-', label='R2H4 - ' + req)
                im114, = axesN.plot([], [], 'o-', label=req)
                im115, = axesN.plot([], [], 'o-', label=req)
                im116, = axesN.plot([], [], 'o-', label=req)
                im117, = axesN.plot([], [], 'o-', label=req)

            if R3:
                if DNVspecify:
                    if VarPerHeadB:
                        axesO = ax4
                        axesP = ax8
                    req = 'Temp Ratio (°C)'     # VarPerHeadB:  One variable per plot of 4 windows [R1, R2, R3, R4]
                else:
                    axesO = ax4
                    axesP = ax8
                    req = 'Delta Temp (°C)'
                im118, = axesO.plot([], [], 'o-', label='R3H1 - ' + req)
                im119, = axesO.plot([], [], 'o-', label='R3H2 - ' + req)
                im120, = axesO.plot([], [], 'o-', label='R3H3 - ' + req)
                im121, = axesO.plot([], [], 'o-', label='R3H4 - ' + req)
                im122, = axesP.plot([], [], 'o-', label=req)
                im123, = axesP.plot([], [], 'o-', label=req)
                im124, = axesP.plot([], [], 'o-', label=req)
                im125, = axesP.plot([], [], 'o-', label=req)

            if R4:
                if DNVspecify:
                    if VarPerHeadB:
                        axesQ = ax5
                        axesR = ax9
                    req = 'Temp Ratio (°C)'        # VarPerHeadB:  One variable per plot of 4 windows [R1, R2, R3, R4]
                else:
                    axesQ = ax5
                    axesR = ax9
                    req = 'Delta Temp (°C)'
                im126, = axesQ.plot([], [], 'o-', label='R4H1 - ' + req)
                im127, = axesQ.plot([], [], 'o-', label='R4H2 - ' + req)
                im128, = axesQ.plot([], [], 'o-', label='R4H3 - ' + req)
                im129, = axesQ.plot([], [], 'o-', label='R4H4 - ' + req)
                im130, = axesR.plot([], [], 'o-', label=req)
                im131, = axesR.plot([], [], 'o-', label=req)
                im132, = axesR.plot([], [], 'o-', label=req)
                im133, = axesR.plot([], [], 'o-', label=req)

        elif GapMeasurement:
            axesV0 = ax2
            axesV1 = ax6
            im134, = axesV0.plot([], [], 'o-', label='Gap Measurement - (A1)')
            im135, = axesV0.plot([], [], 'o-', label='Gap Measurement - (B1)')
            im136, = axesV1.plot([], [], 'o-', label='Tape Gap')
            im137, = axesV1.plot([], [], 'o-', label='Tape Gap')

            # if on Segment #2 -----:
            axesU = ax3
            axesV = ax7
            im138, = axesU.plot([], [], 'o-', label='Gap Measurement - (A2)')
            im139, = axesU.plot([], [], 'o-', label='Gap Measurement - (B2)')
            im140, = axesV.plot([], [], 'o-', label='Tape Gap')
            im141, = axesV.plot([], [], 'o-', label='Tape Gap')

            # if on Segement #3 -----:
            axesW = ax4
            axesX = ax8
            im142, = axesW.plot([], [], 'o-', label='Gap Measurement - (A3)')
            im143, = axesW.plot([], [], 'o-', label='Gap Measurement - (B3)')
            im144, = axesX.plot([], [], 'o-', label='Tape Gap')
            im145, = axesX.plot([], [], 'o-', label='Tape Gap')

            # if on Segment #4 ----:
            axesY = ax5
            axesZ = ax9
            im146, = axesY.plot([], [], 'o-', label='Gap Measurement - (A4)')
            im147, = axesY.plot([], [], 'o-', label='Gap Measurement - (B4)')
            im148, = axesZ.plot([], [], 'o-', label='Tape Gap')
            im149, = axesZ.plot([], [], 'o-', label='Tape Gap')

    elif VariProcess:
        if RollerPressure:
            if DNVspecify:
                axb = ax2
                axB = ax7
                axesA = ax2
                axesB = ax7
                axesC = ax2
                axesD = ax7
                axesE = ax2
                axesF = ax7
            else:
                axb = ax2
                axB = ax6
                axesA = ax2
                axesB = ax6
                axesC = ax2
                axesD = ax6
                axesE = ax2
                axesF = ax6

            if R1:
                # Performed transposition on axes plot ------------------------#
                im6, = axb.plot([], [], 'o-', label='R1H1 - Roller Pressure(N)')
                im7, = axb.plot([], [], 'o-', label='R1H2 - Roller Pressure(N)')
                im8, = axb.plot([], [], 'o-', label='R1H3 - Roller Pressure(N)')
                im9, = axb.plot([], [], 'o-', label='R1H4 - Roller Pressure(N)')
                # ------------
                im10, = axB.plot([], [], 'o-', label='Roller Pressure(N)')
                im11, = axB.plot([], [], 'o-', label='Roller Pressure(N)')
                im12, = axB.plot([], [], 'o-', label='Roller Pressure(N)')
                im13, = axB.plot([], [], 'o-', label='Roller Pressure(N)')

            if R2:
                im14, = axesA.plot([], [], 'o-.', label='R2H1 - Roller Pressure(N)')
                im15, = axesA.plot([], [], 'o-', label='R2H2 - Roller Pressure(N)')
                im16, = axesA.plot([], [], 'o-', label='R2H3 - Roller Pressure(N)')
                im17, = axesA.plot([], [], 'o-', label='R2H4 - Roller Pressure(N)')
                # -------------
                im18, = axesB.plot([], [], 'o-', label='Roller Pressure(N)')
                im19, = axesB.plot([], [], 'o-', label='Roller Pressure(N)')
                im20, = axesB.plot([], [], 'o-', label='Roller Pressure(N)')
                im21, = axesB.plot([], [], 'o-', label='Roller Pressure(N)')

            if R3:
                im22, = axesC.plot([], [], 'o-.', label='R3H1 - Roller Pressure(N)')
                im23, = axesC.plot([], [], 'o-', label='R3H2 - Roller Pressure(N)')
                im24, = axesC.plot([], [], 'o-', label='R3H3 - Roller Pressure(N)')
                im25, = axesC.plot([], [], 'o-', label='R3H4 - Roller Pressure(N)')
                im26, = axesD.plot([], [], 'o-', label='Roller Pressure(N)')
                im27, = axesD.plot([], [], 'o-', label='Roller Pressure(N)')
                im28, = axesD.plot([], [], 'o-', label='Roller Pressure(N)')
                im29, = axesD.plot([], [], 'o-', label='Roller Pressure(N)')

            if R4:
                im30, = axesE.plot([], [], 'o-.', label='R4H1 - Roller Pressure(N)')
                im31, = axesE.plot([], [], 'o-', label='R4H2 - Roller Pressure(N)')
                im32, = axesE.plot([], [], 'o-', label='R4H3 - Roller Pressure(N)')
                im33, = axesE.plot([], [], 'o-', label='R4H4 - Roller Pressure(N)')
                im34, = axesF.plot([], [], 'o-', label='Roller Pressure(N)')
                im35, = axesF.plot([], [], 'o-', label='Roller Pressure(N)')
                im36, = axesF.plot([], [], 'o-', label='Roller Pressure(N)')
                im37, = axesF.plot([], [], 'o-', label='Roller Pressure(N)')

        if Manu_TapeSpeed and DNVspecify:   # Not available on TFMC View
            axT = ax3
            axt = ax8
            axesT2 = ax3
            axest2 = ax8
            axesT3 = ax3
            axest3 = ax8
            axesT4 = ax3
            axest4 = ax8

            if R1:
                im38, = axT.plot([], [], 'o-', label='R1H1 - Tape Speed')
                im39, = axT.plot([], [], 'o-', label='R1H2 - Tape Speed')
                im40, = axT.plot([], [], 'o-', label='R1H3 - Tape Speed')
                im41, = axT.plot([], [], 'o-', label='R1H4 - Tape Speed')
                # ------------
                im42, = axt.plot([], [], 'o-', label='Tape Speed')
                im43, = axt.plot([], [], 'o-', label='Tape Speed')
                im44, = axt.plot([], [], 'o-', label='Tape Speed')
                im45, = axt.plot([], [], 'o-', label='Tape Speed')

            if R2:
                im46, = axesT2.plot([], [], 'o-', label='R2H1 - Tape Speed')
                im47, = axesT2.plot([], [], 'o-', label='R2H2 - Tape Speed')
                im48, = axesT2.plot([], [], 'o-', label='R2H3 - Tape Speed')
                im49, = axesT2.plot([], [], 'o-', label='R2H4 - Tape Speed')
                # -------------
                im50, = axest2.plot([], [], 'o-', label='Tape Speed')
                im51, = axest2.plot([], [], 'o-', label='Tape Speed')
                im52, = axest2.plot([], [], 'o-', label='Tape Speed')
                im53, = axest2.plot([], [], 'o-', label='Tape Speed')

            if R3:
                im54, = axesT3.plot([], [], 'o-.', label='R3H1 - Tape Speed')
                im55, = axesT3.plot([], [], 'o-', label='R3H2 - Tape Speed')
                im56, = axesT3.plot([], [], 'o-', label='R3H3 - Tape Speed')
                im57, = axesT3.plot([], [], 'o-', label='R3H4 - Tape Speed')
                im58, = axest3.plot([], [], 'o-', label='Tape Speed')
                im59, = axest3.plot([], [], 'o-', label='Tape Speed')
                im60, = axest3.plot([], [], 'o-', label='Tape Speed')
                im61, = axest3.plot([], [], 'o-', label='Tape Speed')

            if R4:
                im62, = axesT4.plot([], [], 'o-.', label='R4H1 - Tape Speed')
                im63, = axesT4.plot([], [], 'o-', label='R4H2 - Tape Speed')
                im64, = axesT4.plot([], [], 'o-', label='R4H3 - Tape Speed')
                im65, = axesT4.plot([], [], 'o-', label='R4H4 - Tape Speed')
                im66, = axest4.plot([], [], 'o-', label='Tape Speed')
                im67, = axest4.plot([], [], 'o-', label='Tape Speed')
                im68, = axest4.plot([], [], 'o-', label='Tape Speed')
                im69, = axest4.plot([], [], 'o-', label='Tape Speed')

        if TapeTemperatur:
            if DNVspecify:
                axH0 = ax4
                axH1 = ax9
                axG = ax4
                axH = ax9
                axesI = ax4
                axesJ = ax9
                axesK = ax4
                axesL = ax9
            else:
                axH0 = ax3
                axH1 = ax7
                axG = ax3
                axH = ax7
                axesI = ax3
                axesJ = ax7
                axesK = ax3
                axesL = ax7

            if R1:
                print('Tape Temp Plot Axis defined for Ring1...')
                im70, = axH0.plot([], [], 'o-.', label='R1H1 - Tape Temp(°C)')
                im71, = axH0.plot([], [], 'o-', label='R1H2 - Tape Temp(°C)')
                im72, = axH0.plot([], [], 'o-', label='R1H3 - Tape Temp(°C)')
                im73, = axH0.plot([], [], 'o-', label='R1H4 - Tape Temp(°C)')
                im74, = axH1.plot([], [], 'o-', label='Tape Temp(°C)')
                im75, = axH1.plot([], [], 'o-', label='Tape Temp(°C)')
                im76, = axH1.plot([], [], 'o-', label='Tape Temp(°C)')
                im77, = axH1.plot([], [], 'o-', label='Tape Temp(°C)')

            if R2:
                im78, = axG.plot([], [], 'o-', label='R2H1 - Tape Temp(°C)')
                im79, = axG.plot([], [], 'o-', label='R2H2 - Tape Temp(°C)')
                im80, = axG.plot([], [], 'o-', label='R2H3 - Tape Temp(°C)')
                im81, = axG.plot([], [], 'o-', label='R2H4 - Tape Temp(°C)')
                im82, = axH.plot([], [], 'o-', label='Tape Temp(°C)')
                im83, = axH.plot([], [], 'o-', label='Tape Temp(°C)')
                im84, = axH.plot([], [], 'o-', label='Tape Temp(°C)')
                im85, = axH.plot([], [], 'o-', label='Tape Temp(°C)')

            if R3:
                im86, = axesI.plot([], [], 'o-', label='R3H1 - Tape Temp(°C)')
                im87, = axesI.plot([], [], 'o-', label='R3H2 - Tape Temp(°C)')
                im88, = axesI.plot([], [], 'o-', label='R3H3 - Tape Temp(°C)')
                im89, = axesI.plot([], [], 'o-', label='R3H4 - Tape Temp(°C)')
                im90, = axesJ.plot([], [], 'o-', label='Tape Temp(°C)')
                im91, = axesJ.plot([], [], 'o-', label='Tape Temp(°C)')
                im92, = axesJ.plot([], [], 'o-', label='Tape Temp(°C)')
                im93, = axesJ.plot([], [], 'o-', label='Tape Temp(°C)')

            if R4:
                im94, = axesK.plot([], [], 'o-', label='R4H1 - Tape Temp(°C)')
                im95, = axesK.plot([], [], 'o-', label='R4H2 - Tape Temp(°C)')
                im96, = axesK.plot([], [], 'o-', label='R4H3 - Tape Temp(°C)')
                im97, = axesK.plot([], [], 'o-', label='R4H4 - Tape Temp(°C)')
                im98, = axesL.plot([], [], 'o-', label='Tape Temp(°C)')
                im99, = axesL.plot([], [], 'o-', label='Tape Temp(°C)')
                im100, = axesL.plot([], [], 'o-', label='Tape Temp(°C)')
                im101, = axesL.plot([], [], 'o-', label='Tape Temp(°C)')

        if TSub_TempRatio:
            if DNVspecify:
                axN0 = ax5
                axN1 = ax10
                axesM = ax5
                axesN = ax10
                axesO = ax5
                axesP = ax10
                axesQ = ax5
                axesR = ax10
                req = 'Temp Ratio (°C)'
            else:
                axN0 = ax4
                axN1 = ax8
                axesM = ax4
                axesN = ax8
                axesO = ax4
                axesP = ax8
                axesQ = ax4
                axesR = ax8
                req = 'Delta Temp (°C)'
            if R1:
                im102, = axN0.plot([], [], 'o-', label='R1H1 - ' + req)
                im103, = axN0.plot([], [], 'o-', label='R1H2 - ' + req)
                im104, = axN0.plot([], [], 'o-', label='R1H3 - ' + req)
                im105, = axN0.plot([], [], 'o-', label='R1H4 - ' + req)
                im106, = axN1.plot([], [], 'o-', label=req)
                im107, = axN1.plot([], [], 'o-', label=req)
                im108, = axN1.plot([], [], 'o-', label=req)
                im109, = axN1.plot([], [], 'o-', label=req)

            if R2:
                im110, = axesM.plot([], [], 'o-', label='R2H1 - ' + req)
                im111, = axesM.plot([], [], 'o-', label='R2H2 - ' + req)
                im112, = axesM.plot([], [], 'o-', label='R2H3 - ' + req)
                im113, = axesM.plot([], [], 'o-', label='R2H4 - ' + req)
                im114, = axesN.plot([], [], 'o-', label=req)
                im115, = axesN.plot([], [], 'o-', label=req)
                im116, = axesN.plot([], [], 'o-', label=req)
                im117, = axesN.plot([], [], 'o-', label=req)

            if R3:
                im118, = axesO.plot([], [], 'o-', label='R3H1 - ' + req)
                im119, = axesO.plot([], [], 'o-', label='R3H2 - ' + req)
                im120, = axesO.plot([], [], 'o-', label='R3H3 - ' + req)
                im121, = axesO.plot([], [], 'o-', label='R3H4 - ' + req)
                im122, = axesP.plot([], [], 'o-', label=req)
                im123, = axesP.plot([], [], 'o-', label=req)
                im124, = axesP.plot([], [], 'o-', label=req)
                im125, = axesP.plot([], [], 'o-', label=req)

            if R4:
                im126, = axesQ.plot([], [], 'o-', label='R4H1 - ' + req)
                im127, = axesQ.plot([], [], 'o-', label='R4H2 - ' + req)
                im128, = axesQ.plot([], [], 'o-', label='R4H3 - ' + req)
                im129, = axesQ.plot([], [], 'o-', label='R4H4 - ' + req)
                im130, = axesR.plot([], [], 'o-', label=req)
                im131, = axesR.plot([], [], 'o-', label=req)
                im132, = axesR.plot([], [], 'o-', label=req)
                im133, = axesR.plot([], [], 'o-', label=req)

        if GapMeasurement:
            if DNVspecify:
                axesV0 = ax6
                axesV1 = ax11
                axesU = ax6
                axesV = ax11
                axesW = ax6
                axesX = ax11
                axesY = ax6
                axesZ = ax11
            else:
                axesV0 = ax5
                axesV1 = ax9
                axesU = ax5
                axesV = ax9
                axesW = ax5
                axesX = ax9
                axesY = ax5
                axesZ = ax9

            im134, = axesV0.plot([], [], 'o-', label='Gap Measurement - (A1)')
            im135, = axesV0.plot([], [], 'o-', label='Gap Measurement - (B1)')
            im136, = axesV1.plot([], [], 'o-', label='Tape Gap')
            im137, = axesV1.plot([], [], 'o-', label='Tape Gap')
            # if on Segment #2 -----:
            im138, = axesU.plot([], [], 'o-', label='Gap Measurement - (A2)')
            im139, = axesU.plot([], [], 'o-', label='Gap Measurement - (B2)')
            im140, = axesV.plot([], [], 'o-', label='Tape Gap')
            im141, = axesV.plot([], [], 'o-', label='Tape Gap')
            # if on Segement #3 -----:
            im142, = axesW.plot([], [], 'o-', label='Gap Measurement - (A3)')
            im143, = axesW.plot([], [], 'o-', label='Gap Measurement - (B3)')
            im144, = axesX.plot([], [], 'o-', label='Tape Gap')
            im145, = axesX.plot([], [], 'o-', label='Tape Gap')
            # if on Segment #4 ----:
            im146, = axesY.plot([], [], 'o-', label='Gap Measurement - (A4)')
            im147, = axesY.plot([], [], 'o-', label='Gap Measurement - (B4)')
            im148, = axesZ.plot([], [], 'o-', label='Tape Gap')
            im149, = axesZ.plot([], [], 'o-', label='Tape Gap')

    # ====================================== END OF PLOT LEGEND =====================================[]

    # TODO --- move body code to appropriate line ---------------------------------------------------#
    # ----------------------------- Algorithm for Synchronous SQL DATA -----------------------------[B]
    def synchronous(db_freq):

        fetch_no = str(db_freq)     # convert entry value to string for sql syntax
        # Initialise sql connection based on number of sql tables in use ------------------[D1]
        if UsePLC_DBS:
            # Establish connection with SQL server and PLC-Snap 7 server link
            daq10 = conn.cursor()   # Objective link to OEE Data

        else:
            # print('\nSwitching to SQL Tables...')
            if nTables == 4:  #
                daq1, daq2, daq9, daq10 = conn.cursor(), conn.cursor(), conn.cursor(), conn.cursor()

            elif nTables == 6:
                daq1, daq2, daq3, daq4 = conn.cursor(), conn.cursor(), conn.cursor(), conn.cursor()
                daq9, daq10 = conn.cursor(), conn.cursor()

            elif nTables == 8:
                daq1, daq2, daq3, daq4, daq5 = conn.cursor(), conn.cursor(), conn.cursor(), conn.cursor(), conn.cursor()
                daq6, daq9, daq10 = conn.cursor(), conn.cursor(), conn.cursor()

            elif nTables >= 10:
                daq1, daq2, daq3, daq4, daq5 = conn.cursor(), conn.cursor(), conn.cursor(), conn.cursor(), conn.cursor()
                daq6, daq7, daq8, daq9, daq10 = conn.cursor(), conn.cursor(), conn.cursor(), conn.cursor(), conn.cursor()

            else:
                print('Total number of SQL files not validated..')

        # Evaluate conditions for SQL Data Fetch -------------------------------[A]
        """
        Load watchdog function with synchronous function every seconds
        """
        # TODO: Add Play, Pause, Resume function here --------------------------TODO
        # Initialise RT variables -----------------------------------------------[]
        autoSpcRun = True
        autoSpcPause = False
        import keyboard                             # for temporary use until test passed.
        # TODO -----------------------------------------------------------------[]

        # import spcWatchDog as wd --------------------------------------[OBTAIN MSC]
        sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'       # Default state variables
        # Define PLC/SMC error state -----------------------------------------------
        # sysRun == False and msctcp == 100         # if an error occurs retrieving smc
        # ---------------------------------------------------------------------------
        while True:
            # print('Indefinite looping...')
            if apCalledby == 1 and not UsePLC_DBS:                      # caller Icon SCADA GUI or Primary GUI
                inProgress = True                                       # Always True state for RetroPlay mode
                print('\nAsynchronous controller activated...')
            else:
                inProgress = False                                      # Always True state for RetroPlay mode
                print('\nSynchronous controller activated...')

                if not sysRun:
                    sysRun, msctcp, msc_rt = wd.autoPausePlay()        # Retrieve M.State from Watchdog
                print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

            # Either of the 2 combo variables are assigned to trigger routine pause -------------[COMMON PROCEDURE]
            if RetroReplay and keyboard.is_pressed("ctrl") or not msctcp == 315 and not sysRun and not inProgress:
                print('\nProduction is pausing...')
                if not autoSpcPause:
                    autoSpcRun = not autoSpcRun
                    autoSpcPause = True
                    # play(error)             # Indicate pause mode with audible Alert
                    print("\nVisualization in Paused Mode...")
            else:
                autoSpcPause = False
                # Play visualization ----------------------------------------------[]
                print("Visualization in Play Mode...")
                # play(nudge)     # audible alert
                # Weld Quality Loop -----------------------------------------------[]
                if WeldQualityProcess:
                    if UsePLC_DBS:
                        if not inUseAlready:            # Load CommsPlc class once
                            import CommsPlc as q
                        # ---------------------------------------------------------------------------------------[]
                        if RollerPressure and Manu_TapeSpeed and TapeTemperatur and TSub_TempRatio and GapMeasurement:
                            sql1 = q.Req_RTparams(smp_Sz, smp_St, fetch_no)                       # 82 Column Data

                        elif RollerPressure:
                            sql1 = q.sel_RTparams(smp_Sz, smp_St, fetch_no, 'RF')           # 26 Column Data
                        elif Manu_TapeSpeed:
                            sql1 = q.sel_RTparams(smp_Sz, smp_St, fetch_no, 'TS')           # 26 Column Data
                        elif TapeTemperatur:
                            sql1 = q.sel_RTparams(smp_Sz, smp_St, fetch_no, 'TT')           # 26 Column Data
                        elif TSub_TempRatio:
                            sql1 = q.sel_RTparams(smp_Sz, smp_St, fetch_no, 'TR')           # 26 Column Data
                        elif GapMeasurement:
                            sql1 = q.sel_RTparams(smp_Sz, smp_St, fetch_no, 'TG')           # 18 Column Data
                        else:
                            pass

                        # Set condition for halting real-time plots ---------------[]
                        if len(sql1) < int(fetch_no):
                            print('End of Query, closing connection...')
                            time.sleep(0.2)
                            continue
                        else:
                            print('\nUpdating...')

                    else:   # import loadSQLExecs as lq [naturally dX2]
                        # Weld Quality Data CONNECT Functions ---------------------[D2]
                        if nTables == 4:
                            id1, id2, id3, id4, id5, id6, id7, id8, sql1, sql2, sql3, sql4, sql5, sql6, sql7, sql8 = lq.sqlexec(smp_Sz, nTables,
                                                                                        daq1, daq2, 0, 0, 0, 0, 0, 0,
                                                                                        smp_St, rT1, rT2, 0, 0, 0, 0,
                                                                                        0, 0, fetch_no, rT2dx, 0,
                                                                                                      0, 0, 0, 0, 0)
                            # print("\nSQL FEED TIMEpR:", timeit.timeit())
                        elif nTables == 6:
                            id1, id2, id3, id4, id5, id6, id7, id8, sql1, sql2, sql3, sql4, sql5, sql6, sql7, sql8 = lq.sqlexec(smp_Sz, nTables,
                                                                                        daq1, daq2, daq3, daq4, 0, 0,
                                                                                        0, 0, smp_St, rT1, rT2, rT3,
                                                                                        rT4, 0, 0, 0, 0, fetch_no,
                                                                                        rT1dx, rT2dx, rT3dx, rT4dx, 0,
                                                                                                      0, 0, 0)
                        elif nTables == 8:
                            id1, id2, id3, id4, id5, id6, id7, id8, sql1, sql2, sql3, sql4, sql5, sql6, sql7, sql8 = lq.sqlexec(smp_Sz, nTables,
                                                                                        daq1, daq2, daq3, daq4, daq5,
                                                                                        daq6, 0, 0, smp_St, rT1, rT2,
                                                                                        rT3, rT4, rT5, rT6, 0, 0,
                                                                                        fetch_no, rT1dx, rT2dx, rT3dx,
                                                                                        rT4dx, rT5dx, rT6dx, 0, 0)
                        elif nTables >= 10:
                            id1, id2, id3, id4, id5, id6, id7, id8, sql1, sql2, sql3, sql4, sql5, sql6, sql7, sql8 = lq.sqlexec(smp_Sz, nTables,
                                                                                        daq1, daq2, daq3, daq4, daq5,
                                                                                        daq6, daq7, daq8, smp_St, rT1,
                                                                                        rT2, rT3, rT4, rT5, rT6, rT7,
                                                                                        rT8, fetch_no, rT1dx, rT2dx,
                                                                                        rT3dx, rT4dx, rT5dx, rT6dx,
                                                                                        rT7dx, rT8dx)
                        # Added RL - 03/05/2024 ----------------------------------[+ 15/05/2023]
                        if RetroReplay and DNVspecify and not VarPerHeadB:
                            if VariProcess:
                                CTlayr = HTlayr
                            else:
                                CTlayr = OTlayr
                            # Prevent over flooding the arrays -------------------[START PURGE]
                            if db_freq > 2 and len(CTlayr) > 2 and len(EPpos) > 2:
                                del CTlayr[:1]
                                del EPpos[:1]
                            # -----------------------------------------------------[END of PURGE]
                            if nTables == 4:
                                if CTlayr[:1] and len(id1) > 1 or len(id2) > 1:
                                    del id1[:1]
                                    del id2[:1]
                                    differential_idx(CTlayr[-1], id1[0], id2[0], id3[0], id4[0], id5[0], id6[0], id7[0],
                                                   id8[0], EPpos[-1])
                                    # lastIdx = int(smp_Sz) + int(id1[0])
                            elif nTables == 6:
                                if CTlayr[:1] and len(id1) > 1 or len(id2) > 1 or len(id3) > 1 or len(id4) > 1:
                                    del id1[:1]
                                    del id2[:1]
                                    del id3[:1]
                                    del id4[:1]
                                    differential_idx(CTlayr[-1], id1[0], id2[0], id3[0], id4[0], id5[0], id6[0], id7[0],
                                                   id8[0], EPpos[-1])
                            elif nTables == 8:
                                if CTlayr[:1] and len(id1) > 1 or len(id2) > 1 or len(id3) > 1 or len(id4) > 1:
                                    del id1[:1]
                                    del id2[:1]
                                    del id3[:1]
                                    del id4[:1]
                                    del id5[:1]
                                    del id6[:1]
                                    differential_idx(CTlayr[-1], id1[0], id2[0], id3[0], id4[0], id5[0], id6[0], id7[0],
                                                   id8[0], EPpos[-1])
                            else:   # nTables == 10
                                # OTlayr = 1
                                if CTlayr[:1] and len(id1) > 1 or len(id2) > 1 or len(id3) > 1 or len(id4) > 1:
                                    del id1[:1]
                                    del id2[:1]
                                    del id3[:1]
                                    del id4[:1]
                                    del id5[:1]
                                    del id6[:1]
                                    del id7[:1]
                                    del id8[:1]
                                    differential_idx(CTlayr[0], id1[0], id2[0], id3[0], id4[0], id5[0], id6[0], id7[0],
                                                   id8[0], EPpos[-1])
                                    print('\nTP01 [Layer/Pos]:', CTlayr[0], EPpos[-1])
                            # Document every row index processed in a TXT file (RT_Index_Log Folder) ----[]
                        # ------ Inhibit iteration ----------------------------------------------------------[]
                        """
                        # Set condition for halting real-time plots in watchdog class ---------------------
                        """
                        # TODO --- values for inhibiting the SQL processing
                        if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                            daq1.close()
                            daq2.close()
                            print('SQL End of File, connection closes after 30 mins...')
                            time.sleep(60)
                            continue
                        else:
                            print('\nUpdating....')
                else:
                    print('\nQuality metrics not enabled...')

                # Tape Gap Measurement Loop ----------------------------------------------------------[D5]
                if GapMeasurement or RetroReplay:        # TGapMeasureProcess: on the variable is featured
                    if not UsePLC_DBS:
                        # Obtain gap data from SQL ---------[B] DX2
                        gdata = daq9.execute('SELECT * FROM ' + gTM).fetchmany(smp_Sz * db_freq)

                        # Loop through the fetched result and append into list -----[]
                        for result in gdata:
                            result = list(result)
                            if UseRowIndex:
                                dL0.append(next(idx))
                            else:
                                now = time.strftime("%H:%M:%S")
                                dL0.append(time.strftime(now))
                            dX2.append(result)

                    # Check the array, deduct old elements, ensure new entry data group only
                        if len(dX2) > (smp_Sz):
                            del dX2[0:(len(dX2) - (smp_Sz * db_freq))]  # Todo yields 50% shift register manipulations
                    if not UsePLC_DBS:
                        daq9.close()

                # OEE Performance Loop ----------------------------------------------[TODO - Add RetroPlay]
                if PerfProcess:     # This is OEE Data plot Stream. Not Available on HeadView TypeC
                    if not UsePLC_DBS:
                        data3 = daq10.execute('SELECT * FROM ' + dB_ShiftOEEData).fetchall()

                        # Loop through the fetched result and append into list ---------[1]
                        for result in data3:
                            result = list(result)
                            if UseRowIndex:
                                dL0.append(next(idx))
                            else:
                                now = time.strftime("%H:%M:%S")
                                dL0.append(time.strftime(now))
                            dX3.append(result)
                        if not UsePLC_DBS:
                            daq10.close()
                else:
                    ax1.cla()
                    # Process performance feed only exist for VariProcess View --------------[]
                    if DNVspecify:
                        ax1.text(0.100, 0.880, 'Process (' + PPerf + ') Performance Feed', fontsize=14, fontweight='bold')
                        ax1.text(0.100, 0.840, '-------------------------------------------------------------', fontsize=12)
                        if db_freq > 1:
                            if not VariProcess:
                                CTlayr = OTlayr                 # OEE layer data for offline processing
                                # pPos = 'Disabled'             # Currently disabled until SQL table update
                            else:
                                CTlayr = HTlayr[-1]             # RH01 layer data for real-time processing
                                pPos = round(EPpos[-1]/1000,4)  # Convert mm to meters scale
                        else:
                            CTlayr = 'Start'
                            pPos = '00.0'
                        ax1.text(0.288, 0.750, 'Current Tape Layer  : # ' + str(CTlayr), fontsize=12)
                        ax1.text(0.288, 0.650, 'Roller Force              :' + str(Ppka), fontsize=12)
                        ax1.text(0.288, 0.550, 'Tape Laying Speed   :' + str(Ppkb), fontsize=12)
                        ax1.text(0.288, 0.450, 'Tape Temperature    :' + str(Ppkc), fontsize=12)
                        ax1.text(0.288, 0.350, 'Delta Temperature   :' + str(Ppkd), fontsize=12)
                        ax1.text(0.288, 0.250, 'Gap Measurement    :' + str(Ppke), fontsize=12)
                        ax1.text(0.288, 0.150, 'Pipe Position Data     : ' + str(pPos)+' mtr', fontsize=12)
                    else:   # TFMC Requirements ---------#
                        ax1.text(0.150, 0.880, 'Process (' + PPerf + ') Performance Feed', fontsize=14, fontweight='bold')
                        ax1.text(0.150, 0.840, '-------------------------------------------------------------', fontsize=12)
                        if db_freq > 1:
                            if not VariProcess:
                                CTlayr = OTlayr                     # OEE layer data for offline processing
                                # pPos = 'Disabled'                 # Currently disabled until SQL table update
                            else:
                                CTlayr = HTlayr[-1]                 # RH01 layer data for real-time processing
                                pPos = round(EPpos[-1]/1000, 4)     # Convert mm to meters scale
                        else:
                            CTlayr = '1st'
                            pPos = '00.0'
                        ax1.text(0.288, 0.700, 'Current Tape Layer : # ' + str(CTlayr), fontsize=12)
                        ax1.text(0.288, 0.600, 'Compact Force       :' + str(Ppka), fontsize=12)
                        ax1.text(0.288, 0.500, 'Tape Temperature  :' + str(Ppkc), fontsize=12)
                        ax1.text(0.288, 0.400, 'Delta Temperature :' + str(Ppkd), fontsize=12)
                        ax1.text(0.288, 0.300, 'Gap Measurement  :' + str(Ppke), fontsize=12)
                        ax1.text(0.288, 0.200, 'Pipe Position Data   : ' + str(pPos) +' mtr', fontsize=12)
                    if RetroReplay:
                        if DNVspecify:
                            ax1.text(0.077, 0.048, 'SMC Status: Tape laying in progress...', fontsize=12)
                        else:
                            ax1.text(0.077, 0.048, 'Process Status: Tape laying in progress, please wait...', fontsize=12)
                    else:
                        # TODO ---- evaluate RT SMC codes and description -----------
                        ax1.text(0.077, 0.058, 'Process Status:'+ msc_rt + '.', fontsize=12)

                if UsePLC_DBS:    # TODO -------------------- [3]
                    return dL0, dX1, dX2, dX3, sql1
                else:
                    return dL0, dX1, dX2, dX3, sql1, sql2, sql3, sql4, sql5, sql6, sql7, sql8

    # -------------------------------------------------------------------------------------------|
    #                                   MAIN PROCEDURE
    # -------------------------------------------------------------------------------------------|

    def asynchronous(db_freq):
        timei = time.time()             # start timimg the entire loop

        # declare asynchronous variables -----[]
        tMean1, tMean2, tMean3, tMean4, tMean5, tMean6, tMean7, tMean8 = 0, 0, 0, 0, 0, 0, 0, 0
        tMean9, tMean10, tMean11, tMean12, tMean13, tMean14, tMean15, tMean16 = 0, 0, 0, 0, 0, 0, 0, 0
        tSDev1, tSDev2, tSDev3, tSDev4, tSDev5, tSDev6, tSDev7, tSDev8 = 0, 0, 0, 0, 0, 0, 0, 0
        tSDev9, tSDev10, tSDev11, tSDev12, tSDev13, tSDev14, tSDev15, tSDev16 = 0, 0, 0, 0, 0, 0, 0, 0
        TMean1, TMean2, TMean3, TMean4, TMean5, TMean6, TMean7, TMean8 = 0, 0, 0, 0, 0, 0, 0, 0

        Pp1, Pp2, Pp3, Pp4,Pp5, Pp6, Pp7, Pp8 = 0, 0, 0, 0, 0, 0, 0, 0
        Pp9, Pp10, Pp11, Pp12, Pp13, Pp14, Pp15, Pp16 = 0, 0, 0, 0, 0, 0, 0, 0

        PpkL1, PpkL2, PpkL3, PpkL4, PpkU1, PpkU2, PpkU3, PpkU4 = 0, 0, 0, 0, 0, 0, 0, 0
        PpkL5, PpkL6, PpkL7, PpkL8, PpkU5, PpkU6, PpkU7, PpkU8 = 0, 0, 0, 0, 0, 0, 0, 0
        PpkL9, PpkL10, PpkL11, PpkL12, PpkU9, PpkU10, PpkU11, PpkU12 = 0, 0, 0, 0, 0, 0, 0, 0

        if UsePLC_DBS:     # or GapMeasurement:
            dL0, dX1, dX2, dX3, sql1 = synchronous(db_freq)
        else:
            dL0, dX1, dX2, dX3, sql1, sql2, sql3, sql4, sql5, sql6, sql7, sql8 = synchronous(db_freq)

        # Ring Head Data ----------------------------------------------------------------[]
        if UsePLC_DBS:       # this applies nly to realtime play Mode -------------------[]
            print('Detected Config:', combo)
            # TODO ---- Verify Columns concatenation!
            columns = vq.validCols(combo, rp, ts, tt, tr, tgm)  # Load valid columns based on user se
            df1 = pd.DataFrame(sql1, columns=columns)           # Include table data into python Dataframe
            md = 1                                              # mode processing using PLC Query
            print('\nPLC Content', df1.head(10))
            print("Memory Usage:", df1.info(verbose=False))     # Check memory utilization

        else:
            md = 0                                              # mode processing using SQL Query
            if nTables == 4:                                    # Call [SelUColumns.py] class
                g1 = qq.validCols(H1)                           # Extract R1 SQl Table columns into dataframe
                d1 = pd.DataFrame(sql1, columns=g1)
                g2 = qq.validCols(H2)                           # Extract R2 SQL Tables columns into Dataframe
                d2 = pd.DataFrame(sql2, columns=g2)
                df1 = pd.concat([d1, d2], axis=1)          # concatenate tables
                print("\nMemory Usage:", df1.info(verbose=False))
                # print('SQL Content', df1.head(10))

            elif nTables == 6:
                g1 = qq.validCols(H1)
                d1 = pd.DataFrame(sql1, columns=g1)             # Import into python Dataframe
                g2 = qq.validCols(H2)
                d2 = pd.DataFrame(sql2, columns=g2)
                g3 = qq.validCols(H3)
                d3 = pd.DataFrame(sql3, columns=g3)             # Import into python Dataframe
                g4 = qq.validCols(H4)
                d4 = pd.DataFrame(sql4, columns=g4)
                # print('Performing SQL Concatenation...')
                df1 = pd.concat([d1, d2, d3, d4], axis=1)  # concatenate tables
                print("\nMemory Usage:", df1.info(verbose=False))
                # print('SQL Content', df1.head(10))

            elif nTables == 8:
                g1 = qq.validCols(H1)
                d1 = pd.DataFrame(sql1, columns=g1)             # Import into python Dataframe
                g2 = qq.validCols(H2)
                d2 = pd.DataFrame(sql2, columns=g2)
                g3 = qq.validCols(H3)
                d3 = pd.DataFrame(sql3, columns=g3)             # Import into python Dataframe
                g4 = qq.validCols(H4)
                d4 = pd.DataFrame(sql4, columns=g4)
                g5 = qq.validCols(H5)
                d5 = pd.DataFrame(sql5, columns=g5)
                g6 = qq.validCols(H6)
                d6 = pd.DataFrame(sql6, columns=g6)
                # print('Performing SQL Concatenation...')
                df1 = pd.concat([d1, d2, d3, d4, d5, d6], axis=1)  # concatenate table
                print("\nMemory Usage:", df1.info(verbose=False))
                # print('SQL Content', df1.head(10))

            elif nTables >= 10:
                g1 = qq.validCols(H1)
                d1 = pd.DataFrame(sql1, columns=g1)                 # Import into python Dataframe
                g2 = qq.validCols(H2)
                d2 = pd.DataFrame(sql2, columns=g2)
                g3 = qq.validCols(H3)
                d3 = pd.DataFrame(sql3, columns=g3)                 # Import into python Dataframe
                g4 = qq.validCols(H4)
                d4 = pd.DataFrame(sql4, columns=g4)
                g5 = qq.validCols(H5)
                d5 = pd.DataFrame(sql5, columns=g5)
                g6 = qq.validCols(H6)
                d6 = pd.DataFrame(sql6, columns=g6)
                g7 = qq.validCols(H7)
                d7 = pd.DataFrame(sql7, columns=g7)
                g8 = qq.validCols(H8)
                d8 = pd.DataFrame(sql8, columns=g8)
                # print('Performing SQL Concatenation...')
                df1 = pd.concat([d1, d2, d3, d4, d5, d6, d7, d8], axis=1)  # concatenate tables
                print("\nMemory Usage:", df1.info(verbose=False))
                # print('SQL Content', df1.head(10))

        # Plot Aggregated values for Process Monitoring -----------------------------------------------------------[]
        # --- X-Y-DATA POINTS -------------- Plot aggregated values ----[B]
        if WeldQualityProcess:
            # Load available Data variables based on filters RingCombo --[]
            if UsePLC_DBS:
                if RollerPressure:
                      tlpos, R1RF, R2RF, R3RF, R4RF, R1, R2, R3, R4, mPar = qw.loadRFvar(df1, 'PLC')
                elif Manu_TapeSpeed:
                    tlpos, R1TS, R2TS, R3TS, R4TS, R1, R2, R3, R4, mPar = qw.loadTSvar(df1, 'PLC')
                elif TapeTemperatur:
                    tlpos, R1TT, R2TT, R3TT, R4TT, R1, R2, R3, R4, mPar = qw.loadTTvar(df1, 'PLC')
                elif TSub_TempRatio:
                    tlpos, R1ST, R2ST, R3ST, R4ST, R1, R2, R3, R4, mPar = qw.loadSTvar(df1, 'PLC')
                elif GapMeasurement:
                    tlpos, TG1, TG2, TG3, TG4, R1, R2, R3, R4, mPar = qw.loadTGvar(df1, 'PLC')
                else:
                    tlpos, R1RF, R2RF, R3RF, R4RF, R1TS, R2TS, R3TS, R4TS, R1TT, R2TT, R3TT, R4TT, R1ST, R2ST, R3ST, R4ST, R1, R2, R3, R4, TG1, TG2, TG3, TG4, mPar = qw.loadRingsData(df1, 'PLC')
            else:
                # For SQL Tables --------------------------[]
                mParLP, mParLA, R1RF, R2RF, R3RF, R4RF, R1TS, R2TS, R3TS, R4TS, R1TT, R2TT, R3TT, R4TT, R1ST, R2ST, R3ST, R4ST, R1, R2, R3, R4 = qv.loadSQLringData(df1, combo)

            # Define Data source and scenario ----------------------------------------------------------------------[]
            if not UsePLC_DBS:      # Randomize if modelling for EoL and EoP with df.samples(n).rolling(2).man()
                if monitorParamLP:
                    DS1 = (mParLP[0] + mParLP[1] + mParLP[2] + mParLP[3]) / 4
                    DS2 = (mParLP[4] + mParLP[5] + mParLP[6] + mParLP[7]) / 4
                    DS3 = (mParLP[8] + mParLP[9] + mParLP[10] + mParLP[11]) / 4
                    DS4 = (mParLP[12] + mParLP[13] + mParLP[14] + mParLP[15]) / 4
                if monitorParamLA:
                    DS5 = (mParLA[0] + mParLA[1] + mParLA[2] + mParLA[3]) / 4
                    DS6 = (mParLA[4] + mParLA[5] + mParLA[6] + mParLA[7]) / 4
                    DS7 = (mParLA[8] + mParLA[9] + mParLA[10] + mParLA[11]) / 4
                    DS8 = (mParLA[12] + mParLA[13] + mParLA[14] + mParLA[15]) / 4

            else:       # If pooling data from PLC
                if monitorParamLP:
                    DS1 = mPar[0]
                    DS2 = mPar[1]
                    DS3 = mPar[2]
                    DS4 = mPar[3]
                if monitorParamLA:
                    DS5 = mPar[0]
                    DS6 = mPar[1]
                    DS7 = mPar[2]
                    DS8 = mPar[3]
            # -------------------------------------[]
            if monitorParamLP and DNVspecify and asp:
                # if (db_freq % 10 == 0):
                #     print('\nCondition met..', (db_freq % 10 == 0))
                # Ring 1 LP Data -------#
                AggLp1 = DS1
                print('Array Length:', len(AggLp1))
                im1a.set_xdata(np.arange(db_freq))
                im2a.set_xdata(np.arange(db_freq))
                im1a.set_ydata(AggLp1.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                im2a.set_ydata(AggLp1.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                # Ring 2 LP Data -------#
                AggLp2 = DS2
                im1b.set_xdata(np.arange(db_freq))
                im2b.set_xdata(np.arange(db_freq))
                im1b.set_ydata(AggLp2.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                im2b.set_ydata(AggLp2.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                # Ring 3 LP Data -------#
                AggLp3 = DS3
                im1c.set_xdata(np.arange(db_freq))
                im2c.set_xdata(np.arange(db_freq))
                im1c.set_ydata(AggLp3.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                im2c.set_ydata(AggLp3.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                # Ring 4 LP Data -------#
                AggLp4 = DS4
                im1d.set_xdata(np.arange(db_freq))
                im2d.set_xdata(np.arange(db_freq))
                im1d.set_ydata(AggLp4.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                im2d.set_ydata(AggLp4.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])

            elif monitorParamLA and DNVspecify and asp:
                # Ring 1 - Computed Aggregated Values from SQL -------#
                AggLa1 = DS5
                im1a.set_xdata(np.arange(db_freq))
                im2a.set_xdata(np.arange(db_freq))
                im1a.set_ydata(AggLa1.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                im2a.set_ydata(AggLa1.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                # Ring 2 LA Data -------#
                AggLa2 = DS6
                im1b.set_xdata(np.arange(db_freq))
                im2b.set_xdata(np.arange(db_freq))
                im1b.set_ydata(AggLa2.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                im2b.set_ydata(AggLa2.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                # Ring 3 LA Data -------#
                AggLa3 = DS7
                im1c.set_xdata(np.arange(db_freq))
                im2c.set_xdata(np.arange(db_freq))
                im1c.set_ydata(AggLa3.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                im2c.set_ydata(AggLa3.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                # Ring 4 LP Data -------#
                AggLa4 = DS8
                im1d.set_xdata(np.arange(db_freq))
                im2d.set_xdata(np.arange(db_freq))
                im1d.set_ydata(AggLa4.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                im2d.set_ydata(AggLa4.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])

            elif DNVspecify:
                if monitorParamLP and monitorParamLA:
                    # ----- [Laser Power ----------------------#
                    # Ring 1 LP Data -------#
                    AggLp1 = DS1
                    im1a.set_xdata(np.arange(db_freq))
                    im1a.set_ydata(AggLp1.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Ring 2 LP Data -------#
                    AggLp2 = DS2
                    im1b.set_xdata(np.arange(db_freq))
                    im1b.set_ydata(AggLp2.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Ring 3 LP Data -------#
                    AggLp3 = DS3
                    im1c.set_xdata(np.arange(db_freq))
                    im1c.set_ydata(AggLp3.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Ring 4 LP Data -------#
                    AggLp4 = DS4
                    im1d.set_xdata(np.arange(db_freq))
                    im1d.set_ydata(AggLp4[0:db_freq])
                    # ---- [Laser Angle] -------------------#
                    AggLa1 = DS5
                    im2a.set_xdata(np.arange(db_freq))
                    im2a.set_ydata(AggLa1.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Ring 2 LA Data -------#
                    AggLa2 = DS6
                    im2b.set_xdata(np.arange(db_freq))
                    im2b.set_ydata(AggLa2.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Ring 3 LA Data -------#
                    AggLa3 = DS7
                    im2c.set_xdata(np.arange(db_freq))
                    im2c.set_ydata(AggLa3.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Ring 4 LP Data -------#
                    AggLa4 = DS8
                    im2d.set_xdata(np.arange(db_freq))
                    im2d.set_ydata(AggLa4.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                else:
                    if monitorParamLP:
                        # Ring 1 LP Data -------#
                        AggLp1 = DS1
                        im1a.set_xdata(np.arange(db_freq))
                        im1a.set_ydata(AggLp1[0:db_freq])
                        # Ring 2 LP Data -------#
                        AggLp2 = DS2
                        im1b.set_xdata(np.arange(db_freq))
                        im1b.set_ydata(AggLp2[0:db_freq])
                        # Ring 3 LP Data -------#
                        AggLp3 = DS3
                        im1c.set_xdata(np.arange(db_freq))
                        im1c.set_ydata(AggLp3[0:db_freq])
                        # Ring 4 LP Data -------#
                        AggLp4 = DS4
                        im1d.set_xdata(np.arange(db_freq))
                        im1d.set_ydata(AggLp4[0:db_freq])
                    elif monitorParamLA:
                        # ----------------------- LA ----
                        AggLa1 = DS5
                        im2a.set_xdata(np.arange(db_freq))
                        im2a.set_ydata(AggLa1[0:db_freq])
                        # Ring 2 LA Data -------#
                        AggLa2 = DS6
                        im2b.set_xdata(np.arange(db_freq))
                        im2b.set_ydata(AggLa2[0:db_freq])
                        # Ring 3 LA Data -------#
                        AggLa3 = DS7
                        im2c.set_xdata(np.arange(db_freq))
                        im2c.set_ydata(AggLa3[0:db_freq])
                        # Ring 4 LP Data -------#
                        AggLa4 = DS8
                        im2d.set_xdata(np.arange(db_freq))
                        im2d.set_ydata(AggLa4[0:db_freq])

            else: # -- Computed Aggregated Values for non DNV Requirement -------#
                print('TFMC processing....03')
                if monitorParamLP:
                    # ------------------------ Laser Power ----------------------#
                    # Ring 1 LP Data -------#
                    AggLp1 = DS1
                    im1a.set_xdata(np.arange(db_freq))
                    im1a.set_ydata(AggLp1[0:db_freq])
                    # Ring 2 LP Data -------#
                    AggLp2 = DS2
                    im1b.set_xdata(np.arange(db_freq))
                    im1b.set_ydata(AggLp2[0:db_freq])
                    # Ring 3 LP Data -------#
                    AggLp3 = DS3
                    im1c.set_xdata(np.arange(db_freq))
                    im1c.set_ydata(AggLp3[0:db_freq])
                    # Ring 4 LP Data -------#
                    AggLp4 = DS4
                    im1d.set_xdata(np.arange(db_freq))
                    im1d.set_ydata(AggLp4[0:db_freq])

                # ------------------------ Laser Angle ----------------------#
                else: # if monitorParamLA:
                    # Ring 1 Data ---------#
                    AggLa1 = DS5
                    im1a.set_xdata(np.arange(db_freq))
                    im1a.set_ydata(AggLa1[0:db_freq])
                    # Ring 2 LA Data -------#
                    AggLa2 = DS6
                    im1b.set_xdata(np.arange(db_freq))
                    im1b.set_ydata(AggLa2[0:db_freq])
                    # Ring 3 LA Data -------#
                    AggLa3 = DS7
                    im1c.set_xdata(np.arange(db_freq))
                    im1c.set_ydata(AggLa3[0:db_freq])
                    # Ring 4 LP Data -------#
                    AggLa4 = DS8
                    im1d.set_xdata(np.arange(db_freq))
                    im1d.set_ydata(AggLa4[0:db_freq])

            # ------- Performance column ----------------------------------#
            if PerfProcess:  # Refresh plots for OEE Data -----------------[]
                if DNVspecify:
                    pass
                else:
                    ax1.cla()

        # Perform rolling window calculations. --------------------------------------------[]
        """
        The concept of rolling window calculation is most primarily used in signal processing and
        time-series data rolling(
        window, min_periods=None,
        center=False, win_type=None,
        on=None, axis=0, closed=None,
        step=None, method='single')
        """
        # Compute the mean and standard deviation of the sample subgroup of n=20 -----------
        # -------------------  CONTROL CHARTS PLOTS ---------------------------------------[]
        if RollerPressure:
            # print('\nRoller Pressure activated...')
            if R1:
                # Plot X-Axis data points -------- # if db_freq % grp_Size == 0:
                im6.set_xdata(np.arange(db_freq))
                im7.set_xdata(np.arange(db_freq))
                im8.set_xdata(np.arange(db_freq))
                im9.set_xdata(np.arange(db_freq))
                im10.set_xdata(np.arange(db_freq))
                im11.set_xdata(np.arange(db_freq))
                im12.set_xdata(np.arange(db_freq))
                im13.set_xdata(np.arange(db_freq))
                # Plot Y-Axis data points for XBar --------------------------------------------------[  # Ring 1 ]
                if optm2:
                    im6.set_ydata((R1RF[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])    # head 1
                    im7.set_ydata((R1RF[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])    # head 2
                    im8.set_ydata((R1RF[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])    # head 3
                    im9.set_ydata((R1RF[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])    # head 4
                    # Plot Y-Axis data points for StdDev --------------
                    im10.set_ydata((R1RF[0]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im11.set_ydata((R1RF[1]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im12.set_ydata((R1RF[2]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im13.set_ydata((R1RF[3]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                else:
                    # plot the mean of 20 data points as a single point---------- no of rows at a time
                    im6.set_ydata((R1RF[0]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im7.set_ydata((R1RF[1]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im8.set_ydata((R1RF[2]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im9.set_ydata((R1RF[3]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev ------------------------------------------[]
                    im10.set_ydata((R1RF[0]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im11.set_ydata((R1RF[1]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im12.set_ydata((R1RF[2]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im13.set_ydata((R1RF[3]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])

                # Compute the collective XBar & SChart for Ring 1 ---------------------------------[]
                if not uhl:  # if historical limits not available use automatic
                    if len(autoGpMeanA) == smp_Sz:
                        # filter out potential null and zero values from subgroup mean calculations
                        if (R1RF[0].any()) or (R1RF[1].any()) or (R1RF[2].any()) or (R1RF[3].any()):
                            pass
                        else:
                            # print('\n R1 - CHECK VALUES:', R1RF[0], R1RF[1], R1RF[2], R1RF[3])
                            tMean1 = ((R1RF[0]).mean() + (R1RF[1]).mean() + (R1RF[2]).mean() + (R1RF[3]).mean) / 4
                            tSDev1 = ((R1RF[0]).std() + (R1RF[1]).std() + (R1RF[2]).std() + (R1RF[3]).std()) / 4

                        if len(autoUSLA) != 0:
                            # Compute process capability using New Set limits -------
                            sUCL1, sLCL1, xUSL1, xLSL1, xUCL1, xLCL1 = autosUCLA[0], autosLCLA[0], autoUSLA[0], \
                            autoLSLA[0], autoUCLA[0], autoLCLA[0]
                            PpkL1, PpkU1, Pp1 = pp.hisCap(tMean1, tSDev1, xLSL1, xUSL1)
                            # print('\nUsing the Process MEAN:', tMean1)
                        else:
                            xUSL1, xLSL1, xUCL1, xLCL1, sUCL1, sLCL1, PpkL1, PpkU1, Pp1 = pp.processCap(tMean1, tSDev1, smp_Sz)
                    else:
                        tMean1 = ((R1RF[0]).mean() + (R1RF[1]).mean() + (R1RF[2]).mean() + (R1RF[3]).mean()) / 4
                        tSDev1 = ((R1RF[0]).std() + (R1RF[1]).std() + (R1RF[2]).std() + (R1RF[3]).std()) / 4
                        xUSL1, xLSL1, xUCL1, xLCL1, sUCL1, sLCL1, PpkL1, PpkU1, Pp1 = pp.processCap(tMean1, tSDev1, smp_Sz)
                        # print('\nUsing Ring 1 MEAN:', tMean1)
                else:
                    tMean1 = ((R1RF[0]).mean() + (R1RF[1]).mean() + (R1RF[2]).mean() + (R1RF[3]).mean()) / 4
                    xUCL1, xLCL1, xUSL1, xLSL1, sUCL1, sLCL1 = hUCLa, hLCLa, hUSLa, hLSLa, dUCLa, dLCLa

                    tSDev1 = ((R1RF[0]).std() + (R1RF[1]).std() + (R1RF[2]).std() + (R1RF[3]).std()) / 4
                    PpkL1, PpkU1, Pp1 = pp.hisCap(tMean1, tSDev1, xLSL1, xUSL1)
                    print('\nPPkLow/PpKHigh/PPk:', PpkL1, PpkU1, Pp1)
                # Compute process capability for Ring 1 Data --------------------------------------[]
                pkA = min(PpkL1, PpkU1)
                rfA.append(round(pkA, 4))
                # Free up some memory spaces -----
                if len(rfA) > 1:
                    del (rfA[:1])
                print('Head1-4 (RF) Dev:', round(tSDev1, 4))
                print('USL/LSL (RF):', xUSL1, xLSL1)
                print('UCL/LCL (RF):', xUCL1, xLCL1)
                print('Head1-4 (RF) Pp/Ppk:', round(Pp1, 4), '\t', rfA[-1])
                print('\nCalculated Values:', round(PpkL1, 4), round(PpkU1, 4), round(Pp1, 4))

            if R2:  # -----------------------------------------------------------------------[  # Ring 2 ]
                # Plot X-Axis data points --------
                im14.set_xdata(np.arange(db_freq))
                im15.set_xdata(np.arange(db_freq))
                im16.set_xdata(np.arange(db_freq))
                im17.set_xdata(np.arange(db_freq))
                im18.set_xdata(np.arange(db_freq))
                im19.set_xdata(np.arange(db_freq))
                im20.set_xdata(np.arange(db_freq))
                im21.set_xdata(np.arange(db_freq))
                if optm2:
                    im14.set_ydata((R2RF[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im15.set_ydata((R2RF[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im16.set_ydata((R2RF[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im17.set_ydata((R2RF[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------
                    im18.set_ydata((R2RF[0]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im19.set_ydata((R2RF[1]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im20.set_ydata((R2RF[2]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im21.set_ydata((R2RF[3]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                else:
                    # Plot Y-Axis data points for XBar ---------------
                    im14.set_ydata((R2RF[0]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im15.set_ydata((R2RF[1]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im16.set_ydata((R2RF[2]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im17.set_ydata((R2RF[3]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im18.set_ydata((R2RF[0]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im19.set_ydata((R2RF[1]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im20.set_ydata((R2RF[2]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im21.set_ydata((R2RF[3]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                # Compute the collective XBar & SChart for Ring 2 ---------[]
                if not uhl:
                    if len(autoGpMeanA) == smp_Sz:
                        # filter out potential null and zero values from subgroup mean deductions ----
                        if R2RF[0].any() or R2RF[1].any() or R2RF[2].any() or R2RF[3].any():
                            pass
                        else:
                            # print('\n R2 - CHECK VALUES:', R2RF[0], R2RF[1], R2RF[2], R2RF[3])
                            tMean2 = ((R2RF[0]).mean() + (R2RF[1]).mean() + (R2RF[2]).mean() + (R2RF[3]).mean()) / 4
                            tSDev2 = ((R2RF[0]).std() + (R2RF[1]).std() + (R2RF[2]).std() + (R2RF[3]).std()) / 4

                        if len(autoUSLA) != 0:
                            sUCL2, sLCL2, xUSL2, xLSL2, xUCL2, xLCL2 = autosUCLA[0], autosLCLA[0], autoUSLA[0], \
                                autoLSLA[0], autoUCLA[0], autoLCLA[0]
                            PpkL2, PpkU2, Pp2 = pp.hisCap(tMean2, tSDev2, xLSL2, xUSL2)
                        else:
                            xUSL2, xLSL2, xUCL2, xLCL2, sUCL2, sLCL2, PpkL2, PpkU2, Pp2 = pp.processCap(tMean2, tSDev2, smp_Sz)
                    else:
                        tMean2 = ((R2RF[0]).mean() + (R2RF[1]).mean() + (R2RF[2]).mean() + (R2RF[3]).mean()) / 4
                        tSDev2 = ((R2RF[0]).std() + (R2RF[1]).std() + (R2RF[2]).std() + (R2RF[3]).std()) / 4
                        xUSL2, xLSL2, xUCL2, xLCL2, sUCL2, sLCL2, PpkL2, PpkU2, Pp2 = pp.processCap(tMean2, tSDev2, smp_Sz)
                else:
                    tMean2 = ((R2RF[0]).mean() + (R2RF[1]).mean() + (R2RF[2]).mean() + (R2RF[3]).mean()) / 4
                    xUCL2, xLCL2, xUSL2, xLSL2, sUCL2, sLCL2 = hUCLa, hLCLa, hUSLa, hLSLa, dUCLa, dLCLa

                    tSDev2 = ((R2RF[0]).std() + (R2RF[1]).std() + (R2RF[2]).std() + (R2RF[3]).std()) / 4
                    PpkL2, PpkU2, Pp2 = pp.hisCap(tMean2, tSDev2, xLSL2, xUSL2)

                # Compute process capability for Ring 2 Data ----------------------------------------[]
                pkB = min(PpkL2, PpkU2)
                rfB.append(round(pkB, 4))
                # Free up some memory spaces -----
                if len(rfB) > 1:
                    del (rfB[:1])
                print('Head5-8 (RF) Dev:', round(tSDev2, 4))
                print('USL/LSL (RF):', xUSL2, xLSL2)
                print('UCL/LCL (RF):', xUCL2, xLCL2)
                print('Ring2-Head5-8 (RF) Pp/Ppk:', round(Pp2, 4), '\t', rfB[-1])

            if R3:
                # Plot X-Axis data points --------
                im22.set_xdata(np.arange(db_freq))
                im23.set_xdata(np.arange(db_freq))
                im24.set_xdata(np.arange(db_freq))
                im25.set_xdata(np.arange(db_freq))
                im26.set_xdata(np.arange(db_freq))
                im27.set_xdata(np.arange(db_freq))
                im28.set_xdata(np.arange(db_freq))
                im29.set_xdata(np.arange(db_freq))
                if optm2:
                    im22.set_ydata((R3RF[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im23.set_ydata((R3RF[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im24.set_ydata((R3RF[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im25.set_ydata((R3RF[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev -------------------------------------------
                    im26.set_ydata((R3RF[0]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im27.set_ydata((R3RF[1]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im28.set_ydata((R3RF[2]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im29.set_ydata((R3RF[3]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                else:
                    # Plot Y-Axis data points for XBar ---
                    im22.set_ydata((R3RF[0]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im23.set_ydata((R3RF[1]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im24.set_ydata((R3RF[2]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im25.set_ydata((R3RF[3]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev -----------------------------------------
                    im26.set_ydata((R3RF[0]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im27.set_ydata((R3RF[1]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im28.set_ydata((R3RF[2]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im29.set_ydata((R3RF[3]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                # Calculate XBar & SChart for Ring 3 ---------
                if not uhl:
                    if len(autoGpMeanA) == smp_Sz:
                        # filter out potential null and zero values from subgroup mean deductions ----
                        if R3RF[0].any() or R3RF[1].any() or R3RF[2].any() or R3RF[3].any():
                            pass
                        else:
                            tMean3 = ((R3RF[0]).mean() + (R3RF[1]).mean() + (R3RF[2]).mean() + (R3RF[3]).mean()) / 4
                            tSDev3 = ((R3RF[0]).std() + (R3RF[1]).std() + (R3RF[2]).std() + (R3RF[3]).std()) / 4

                        if len(autoUSLA) != 0:
                            # Compute process capability using New Set limits -------
                            sUCL3, sLCL3, xUSL3, xLSL3, xUCL3, xLCL3 = autosUCLA[0], autosLCLA[0], autoUSLA[0], \
                                autoLSLA[0], autoUCLA[0], autoLCLA[0]
                            PpkL3, PpkU3, Pp3 = pp.hisCap(tMean3, tSDev3, xLSL3, xUSL3)
                            # print('\nUsing the Process MEAN:', tMean3)
                        else:
                            xUSL3, xLSL3, xUCL3, xLCL3, sUCL3, sLCL3, PpkL3, PpkU3, Pp3 = pp.processCap(tMean3, tSDev3, smp_Sz)
                    else:
                        tMean3 = ((R3RF[0]).mean() + (R3RF[1]).mean() + (R3RF[2]).mean() + (R3RF[3]).mean()) / 4
                        tSDev3 = ((R3RF[0]).std() + (R3RF[1]).std() + (R3RF[2]).std() + (R3RF[3]).std()) / 4
                        xUSL3, xLSL3, xUCL3, xLCL3, sUCL3, sLCL3, PpkL3, PpkU3, Pp3 = pp.processCap(tMean3, tSDev3, smp_Sz)
                else:
                    tMean3 = ((R3RF[0]).mean() + (R3RF[1]).mean() + (R3RF[2]).mean() + (R3RF[3]).mean()) / 4
                    xUCL3, xLCL3, xUSL3, xLSL3, sUCL3, sLCL3 = hUCLa, hLCLa, hUSLa, hLSLa, dUCLa, dLCLa

                    tSDev3 = ((R3RF[0]).std() + (R3RF[1]).std() + (R3RF[2]).std() + (R3RF[3]).std()) / 4
                    PpkL3, PpkU3, Pp3 = pp.hisCap(tMean3, tSDev3, xLSL3, xUSL3)

                # Compute process capability for Ring 3 Data ----------------------------------------[]
                pkC = min(PpkL3, PpkU3)
                rfC.append(round(pkC, 4))
                # Free up some memory spaces -----
                if len(rfC) > 1:
                    del (rfC[:1])
                print('Head8-12 (RF) Dev:', round(tSDev3, 4))
                print('USL/LSL (RF):', xUSL3, xLSL3)
                print('UCL/LCL (RF):', xUCL3, xLCL3)
                print('Ring3-Head8-12 (RF) Pp/Ppk:', round(Pp3, 4), '\t', rfC[-1])

            if R4:
                # Plot X-Axis data points --------
                im30.set_xdata(np.arange(db_freq))
                im31.set_xdata(np.arange(db_freq))
                im32.set_xdata(np.arange(db_freq))
                im33.set_xdata(np.arange(db_freq))
                im34.set_xdata(np.arange(db_freq))
                im35.set_xdata(np.arange(db_freq))
                im36.set_xdata(np.arange(db_freq))
                im37.set_xdata(np.arange(db_freq))
                if optm2:
                    # Plot Y-Axis data points for XBar ---
                    im30.set_ydata((R4RF[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im31.set_ydata((R4RF[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im32.set_ydata((R4RF[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im33.set_ydata((R4RF[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im34.set_ydata((R4RF[0]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im35.set_ydata((R4RF[1]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im36.set_ydata((R4RF[2]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im37.set_ydata((R4RF[3]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                else:
                    # Plot Y-Axis data points for XBar ---
                    im30.set_ydata((R4RF[0]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im31.set_ydata((R4RF[1]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im32.set_ydata((R4RF[2]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im33.set_ydata((R4RF[3]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev ------------------------------------------
                    im34.set_ydata((R4RF[0]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im35.set_ydata((R4RF[1]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im36.set_ydata((R4RF[2]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im37.set_ydata((R4RF[3]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                # Calculate process capability for Ring 4 ---------
                if not uhl:
                    if len(autoGpMeanA) == smp_Sz:
                        # filter out potential null and zero values from subgroup mean deductions ----
                        if R4RF[0].any() or R4RF[1].any() or R4RF[2].any() or R4RF[3].any():
                            pass
                        else:
                            tMean4 = ((R4RF[0]).mean() + (R4RF[1]).mean() + (R4RF[2]).mean() + (R4RF[3]).mean()) / 4
                            tSDev4 = ((R4RF[0]).std() + (R4RF[1]).std() + (R4RF[2]).std() + (R4RF[3]).std()) / 4

                        if len(autoUSLA) != 0:
                            # Compute process capability using New Set limits -------
                            sUCL4, sLCL4, xUSL4, xLSL4, xUCL4, xLCL4 = autosUCLA[0], autosLCLA[0], autoUSLA[0], \
                                autoLSLA[0], autoUCLA[0], autoLCLA[0]
                            PpkL4, PpkU4, Pp4 = pp.hisCap(tMean4, tSDev4, xLSL4, xUSL4)
                        else:
                            xUSL4, xLSL4, xUCL4, xLCL4, sUCL4, sLCL4, PpkL4, PpkU4, Pp4 = pp.processCap(tMean4, tSDev4, smp_Sz)
                    else:
                        tMean4 = ((R4RF[0]).mean() + (R4RF[1]).mean() + (R4RF[2]).mean() + (R4RF[3]).mean()) / 4
                        tSDev4 = ((R4RF[0]).std() + (R4RF[1]).std() + (R4RF[2]).std() + (R4RF[3]).std()) / 4
                        xUSL4, xLSL4, xUCL4, xLCL4, sUCL4, sLCL4, PpkL4, PpkU4, Pp4 = pp.processCap(tMean4, tSDev4, smp_Sz)
                else:
                    tMean4 = ((R4RF[0]).mean() + (R4RF[1]).mean() + (R4RF[2]).mean() + (R4RF[3]).mean()) / 4
                    xUCL4, xLCL4, xUSL4, xLSL4, sUCL4, sLCL4 = hUCLa, hLCLa, hUSLa, hLSLa, dUCLa, dLCLa

                    tSDev4 = ((R4RF[0]).std() + (R4RF[1]).std() + (R4RF[2]).std() + (R4RF[3]).std()) / 4
                    PpkL4, PpkU4, Pp4 = pp.hisCap(tMean4, tSDev4, xLSL4, xUSL4)

                # Compute process capability for Ring 4 Data ---------------------------------------[]
                pkD = min(PpkL4, PpkU4)
                rfD.append(round(pkD, 4))
                # Free up some memory spaces -----
                if len(rfD) > 1:
                    del (rfD[:1])
                print('Head13-16 (RF) Dev:', round(tSDev4, 4))
                print('USL/LSL (RF):', xUSL4, xLSL4)
                print('UCL/LCL (RF):', xUCL4, xLCL4)
                print('Ring4-Head13-16 (RF) Pp/Ppk:', round(Pp4, 4), '\t', rfD[-1])

            # ----- Calculate Process Data ---------------------------------------------------------[]
            # For automatic derivatives: Only account for active rings with process data ----
            if not uhl:
                # Sample process group mean for 1st subgroup instance ----------------------------[TODO]
                if len(autoGpMeanA) <= smp_Sz:
                    if tMean1 != 0 or tMean2 != 0 or tMean3 != 0 or tMean4 != 0:
                        TMean1 = np.array([tMean1, tMean2, tMean3, tMean4])     # Ring data
                        TMean1 = (TMean1[np.nonzero(TMean1)]).mean()            # ignore defective head [.mean()]
                        TSdev1 = np.array([tSDev1, tSDev2, tSDev3, tSDev4])
                        TSdev1 = (TSdev1[np.nonzero(TSdev1)]).mean()            # total heads in the process

                    # Sample and Compute the subgroup Process Mean and subgroup Deviation
                    elif np.isnan(TMean1):
                        TMean1 = 0.0
                        TSdev1 = 0.68 * 2   # i.e 1 sigma DOF
                    else:
                        TMean1 = 0.0
                        TSdev1 = 0.68 * 2   # i.e 1 sigma DOF

                    sMeana = 0
                    xMeana = 0                          # Turn off center line until limits lock
                    autoGpMeanA.append(TMean1)          # record zero value
                    autoGpDevA.append(TSdev1)           # I sigma deviation
                    xUSLa, xLSLa, xUCLa, xLCLa, sUCLa, sLCLa, PpkLa, PpkUa, PpRa = pp.processCap(TMean1, TSdev1, smp_Sz)

                else:
                    TMean1 = sum(autoGpMeanA) / len(autoGpMeanA)    # compute & keep subgroup Center line
                    TSdev1 = sum(autoGpDevA) / len(autoGpDevA)      # Compute average dev for subgroup Center line
                    sMeana = 0
                    xMeana = 0                                      # Turn off center line until limits lock
                    if len(autoUSLA) < 2:
                        xUSLa, xLSLa, xUCLa, xLCLa, sUCLa, sLCLa, PpkLa, PpkUa, PpRa = pp.processCap(TMean1, TSdev1,
                                                                                                     smp_Sz)
                        sClineA.append(TSdev1)
                        autoUSLA.append(xUSLa)
                        autoLSLA.append(xLSLa)
                        autoUCLA.append(xUCLa)
                        autoLCLA.append(xLCLa)
                        autosUCLA.append(sUCLa)
                        autosLCLA.append(sLCLa)
                    else:
                        # Test static arrays for valid values --------------------[]
                        xUSLa = autoUSLA[0]
                        xLSLa = autoLSLA[0]
                        xUCLa = autoUCLA[0]
                        xLCLa = autoLCLA[0]
                        sUCLa = autosUCLA[0]
                        sLCLa = autosLCLA[0]
                        sMeana = sClineA[0]                                     # sPlot center line
                        xMeana = TMean1                                         # Turn off center line until limits lock
                        TSdev1 = np.array([tSDev1, tSDev2, tSDev3, tSDev4])     # Allow subgroup DOF on StdDev
                        TSdev1 = (TSdev1[np.nonzero(TSdev1)]).mean()            # Current Process's deviation
                        PpkLa, PpkUa, PpRa = pp.hisCap(TMean1, TSdev1, xLSLa, xUSLa)

            else:
                xMeana = HistMeanA                                              # X Bar Center Line
                sMeana = HistSDevA                                              # S Bar Center Line
                # ---- Compute Process Mean --------
                proM1 = (tMean1, tMean2, tMean3, tMean4)
                if sum(proM1) != 0:
                    TMean1 = np.array([tMean1, tMean2, tMean3, tMean4])             # Allow subgroup DOF on StdDev
                    TMean1 = (TMean1[np.nonzero(TMean1)]).mean()                    # Current Process's deviation
                else:
                    pass
                TSdev1 = np.array([tSDev1, tSDev2, tSDev3, tSDev4])             # Allow subgroup DOF on StdDev
                TSdev1 = (TSdev1[np.nonzero(TSdev1)]).mean()                    # Current Process's deviation

                xUSLa, xLSLa, xUCLa, xLCLa, sUCLa, sLCLa = hUSLa, hLSLa, hUCLa, hLCLa, dUCLa, dLCLa
                PpkLa, PpkUa, PpRa = pp.hisCap(TMean1, TSdev1, xLSLa, xUSLa)
            # Compute process capability for Process Data ------------------------[]
            procA = min(PpkLa, PpkUa)                               # Average Ppk per available rings combinations
            Ppka.append(round(procA, 4))                            # copy 2sig. result into a dynamic array
            # Free up some memory spaces -----
            if len(Ppka) > 1:
                del (Ppka[:1])
            print('-'*55)
            print('Process (RF) Mean/SDev:', round(TMean1, 4), round(TSdev1, 4))
            print('Process (RF) UCL/LCL:', xUCLa, xLCLa)
            print('Process (RF) USL/LSL:', xUSLa, xLSLa)
            print('Process (RF) Pp/Ppk:', round(PpRa, 4), '\t', Ppka[-1])        # 4 min to max 16 heads on 4 rings
            print('-' * 55)
        # ----------------------------------- DNV Parameter Requirements -----------------------------------------[]
        if Manu_TapeSpeed:
            # print('\nControl Temp variable activated...') ----------------------[]
            if R1:  # R1TS, R2TS, R3TS, R4TS
                im38.set_xdata(np.arange(db_freq))
                im39.set_xdata(np.arange(db_freq))
                im40.set_xdata(np.arange(db_freq))
                im41.set_xdata(np.arange(db_freq))
                im42.set_xdata(np.arange(db_freq))
                im43.set_xdata(np.arange(db_freq))
                im44.set_xdata(np.arange(db_freq))
                im45.set_xdata(np.arange(db_freq))
                if optm2:
                    # Plot Y-Axis data points for XEar --- # scaled down factor
                    im38.set_ydata((R1TS[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im39.set_ydata((R1TS[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im40.set_ydata((R1TS[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im41.set_ydata((R1TS[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im42.set_ydata((R1TS[0]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im43.set_ydata((R1TS[1]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im44.set_ydata((R1TS[2]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im45.set_ydata((R1TS[3]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    # Calculate process capability for Ring 1 ---------
                else:
                    # Plot Y-Axis data points for XEar --- # scaled down factor
                    im38.set_ydata((R1TS[0]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im39.set_ydata((R1TS[1]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im40.set_ydata((R1TS[2]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im41.set_ydata((R1TS[3]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im42.set_ydata((R1TS[0]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im43.set_ydata((R1TS[1]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im44.set_ydata((R1TS[2]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im45.set_ydata((R1TS[3]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    # Calculate process capability for Ring 1 ---------
                if not uhl:
                    if len(autoGpMeanB) == smp_Sz:
                        # filter out potential null and zero values from subgroup mean deductions ----
                        if R1TS[0].any() or R1TS[1].any() or R1TS[2].any() or R1TS[3].any():
                            pass
                        else:
                            tMean5 = ((R1TS[0]).mean() + (R1TS[1]).mean() + (R1TS[2]).mean() + (R1TS[3]).mean()) / 4
                            tSDev5 = ((R1TS[0]).std() + (R1TS[1]).std() + (R1TS[2]).std() + (R1TS[3]).std()) / 4

                        if len(autoUSLB) != 0:
                            # Compute process capability using New Set limits -------
                            sUCL5, sLCL5, xUSL5, xLSL5, xUCL5, xLCL5 = autosUCLB[0], autosLCLB[0], autoUSLB[0], \
                                autoLSLB[0], autoUCLB[0], autoLCLB[0]
                            PpkL5, PpkU5, Pp5 = pp.hisCap(tMean5, tSDev5, xLSL5, xUSL5)
                        else:
                            xUSL5, xLSL5, xUCL5, xLCL5, sUCL5, sLCL5, PpkL5, PpkU5, Pp5 = pp.processCap(
                                tMean5, tSDev5, smp_Sz)
                    else:
                        tMean5 = ((R1TS[0]).mean() + (R1TS[1]).mean() + (R1TS[2]).mean() + (R1TS[3]).mean()) / 4
                        tSDev5 = ((R1TS[0]).std() + (R1TS[1]).std() + (R1TS[2]).std() + (R1TS[3]).std()) / 4
                        xUSL5, xLSL5, xUCL5, xLCL5, sUCL5, sLCL5, PpkL5, PpkU5, Pp5 = pp.processCap(tMean5,
                                                                                                             tSDev5,
                                                                                                             smp_Sz)
                else:
                    tMean5 = ((R1TS[0]).mean() + (R1TS[1]).mean() + (R1TS[2]).mean() + (R1TS[3]).mean()) / 4
                    xUCL5, xLCL5, xUSL5, xLSL5, sUCL5, sLCL5 = hUCLb, hLCLb, hUSLb, hLSLb, dUCLb, dLCLb

                    tSDev5 = ((R1TS[0]).std() + (R1TS[1]).std() + (R1TS[2]).std() + (R1TS[3]).std()) / 4
                    PpkL5, PpkU5, Pp5 = pp.hisCap(tMean5, tSDev5, xLSL5, xUSL5)

                # Compute process capability for Ring 1 Data ----------------------------------------[]
                TsA = min(PpkL5, PpkU5)
                tsA.append(round(TsA, 4))
                # Free up some memory spaces -----
                if len(tsA) > 1:
                    del (tsA[:1])
                print('Head1-4 (TS) Dev:', round(tSDev5, 4))
                print('USL/LSL (TS):', round(xUSL5,4), round(xLSL5,4))
                print('UCL/LCL (TS):', xUCL5, xLCL5)
                print('Head1-4 (TS) Pp/Ppk:', round(Pp5, 4), '\t', tsA[-1])

            if R2:
                # Plot X-Axis data points --------
                im46.set_xdata(np.arange(db_freq))
                im47.set_xdata(np.arange(db_freq))
                im48.set_xdata(np.arange(db_freq))
                im49.set_xdata(np.arange(db_freq))
                im50.set_xdata(np.arange(db_freq))
                im51.set_xdata(np.arange(db_freq))
                im52.set_xdata(np.arange(db_freq))
                im53.set_xdata(np.arange(db_freq))
                if optm2:
                    # Plot Y-Axis data points for XEar ---
                    im46.set_ydata((R2TS[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im47.set_ydata((R2TS[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im48.set_ydata((R2TS[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im49.set_ydata((R2TS[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im50.set_ydata((R2TS[0]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im51.set_ydata((R2TS[1]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im52.set_ydata((R2TS[2]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im53.set_ydata((R2TS[3]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    # Calculate process capability for Ring 2 ---------
                else:
                    # Plot Y-Axis data points for XEar ---
                    im46.set_ydata((R2TS[0]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im47.set_ydata((R2TS[1]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im48.set_ydata((R2TS[2]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im49.set_ydata((R2TS[3]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im50.set_ydata((R2TS[0]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im51.set_ydata((R2TS[1]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im52.set_ydata((R2TS[2]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im53.set_ydata((R2TS[3]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    # Calculate process capability for Ring 2 ---------
                if not uhl:
                    if len(autoGpMeanB) == smp_Sz:
                        # filter out potential null and zero values from subgroup mean deductions ----[]
                        if R2TS[0].any() or R2TS[1].any() or R2TS[2].any() or R2TS[3].any():
                            pass
                        else:
                            tMean6 = ((R2TS[0]).mean() + (R2TS[1]).mean() + (R2TS[2]).mean() + (R2TS[3]).mean()) / 4
                            tSDev6 = ((R2TS[0]).std() + (R2TS[1]).std() + (R2TS[2]).std() + (R2TS[3]).std()) / 4

                        if len(autoUSLB) != 0:
                            # Compute process capability using New Set limits --------------------
                            sUCL6, sLCL6, xUSL6, xLSL6, xUCL6, xLCL6 = autosUCLB[0], autosLCLB[0], autoUSLB[0], \
                                autoLSLB[0], autoUCLB[0], autoLCLB[0]
                            PpkL6, PpkU6, Pp6 = pp.hisCap(tMean6, tSDev6, xLSL6, xUSL6)
                        else:
                            xUSL6, xLSL6, xUCL6, xLCL6, sUCL6, sLCL6, PpkL6, PpkU6, Pp6 = pp.processCap(
                                tMean6, tSDev6, smp_Sz)
                    else:
                        tMean6 = ((R2TS[0]).mean() + (R2TS[1]).mean() + (R2TS[2]).mean() + (R2TS[3]).mean()) / 4
                        tSDev6 = ((R2TS[0]).std() + (R2TS[1]).std() + (R2TS[2]).std() + (R2TS[3]).std()) / 4
                        xUSL6, xLSL6, xUCL6, xLCL6, sUCL6, sLCL6, PpkL6, PpkU6, Pp6 = pp.processCap(tMean6,
                                                                                                             tSDev6,
                                                                                                             smp_Sz)
                else:
                    tMean6 = ((R2TS[0]).mean() + (R2TS[1]).mean() + (R2TS[2]).mean() + (R2TS[3]).mean()) / 4
                    xUCL6, xLCL6, xUSL6, xLSL6, sUCL6, sLCL6 = hUCLb, hLCLb, hUSLb, hLSLb, dUCLb, dLCLb

                    tSDev6 = ((R2TS[0]).std() + (R2TS[1]).std() + (R2TS[2]).std() + (R2TS[3]).std()) / 4
                    PpkL6, PpkU6, Pp6 = pp.hisCap(tMean6, tSDev6, xLSL6, xUSL6)

                # Compute process capability for Ring 2 Data ----------------------------------------[]
                pkB = min(PpkL6, PpkU6)
                tsB.append(round(pkB, 4))
                # Free up some memory spaces -----
                if len(tsB) > 1:
                    del (tsB[:1])
                print('Head5-8 (TS) Dev:', round(tSDev6, 4))
                print('USL/LSL (TS):', round(xUSL6,4), round(xLSL6,4))
                print('UCL/LCL (TS):', xUCL6, xLCL6)
                print('Head5-8 (TS) Pp/Ppk:', round(Pp6, 4), '\t', tsB[-1])

            if R3:
                # Plot X-Axis data points --------
                im54.set_xdata(np.arange(db_freq))
                im55.set_xdata(np.arange(db_freq))
                im56.set_xdata(np.arange(db_freq))
                im57.set_xdata(np.arange(db_freq))
                im58.set_xdata(np.arange(db_freq))
                im59.set_xdata(np.arange(db_freq))
                im60.set_xdata(np.arange(db_freq))
                im61.set_xdata(np.arange(db_freq))
                if optm2:
                    # Plot Y-Axis data points for XEar ---
                    im54.set_ydata((R3TS[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im55.set_ydata((R3TS[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im56.set_ydata((R3TS[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im57.set_ydata((R3TS[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im58.set_ydata((R3TS[0]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im59.set_ydata((R3TS[1]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im60.set_ydata((R3TS[2]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im61.set_ydata((R3TS[3]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                else:
                    # Plot Y-Axis data points for XEar ---
                    im54.set_ydata((R3TS[0]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im55.set_ydata((R3TS[1]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im56.set_ydata((R3TS[2]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im57.set_ydata((R3TS[3]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im58.set_ydata((R3TS[0]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im59.set_ydata((R3TS[1]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im60.set_ydata((R3TS[2]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im61.set_ydata((R3TS[3]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    # Calculate process capability for Ring 3 ---------
                if not uhl:
                    if len(autoGpMeanB) == smp_Sz:
                        # filter out potential null and zero values from subgroup mean deductions ----[]
                        if R3TS[0].any() or R3TS[1].any() or R3TS[2].any() or R3TS[3].any():
                            pass
                        else:
                            tMean7 = ((R3TS[0]).mean() + (R3TS[1]).mean() + (R3TS[2]).mean() + (R3TS[3]).mean()) / 4
                            tSDev7 = ((R3TS[0]).std() + (R3TS[1]).std() + (R3TS[2]).std() + (R3TS[3]).std()) / 4

                        if len(autoUSLB) != 0:
                            # Compute process capability using New Set limits -------
                            sUCL7, sLCL7, xUSL7, xLSL7, xUCL7, xLCL7 = autosUCLB[0], autosLCLB[0], autoUSLB[0], \
                                autoLSLB[0], autoUCLB[0], autoLCLB[0]
                            PpkL7, PpkU7, Pp7 = pp.hisCap(tMean7, tSDev7, xLSL7, xUSL7)
                        else:
                            xUSL7, xLSL7, xUCL7, xLCL7, sUCL7, sLCL7, PpkL7, PpkU7, Pp7 = pp.processCap(
                                tMean7, tSDev7, smp_Sz)
                    else:
                        tMean7 = ((R3TS[0]).mean() + (R3TS[1]).mean() + (R3TS[2]).mean() + (R3TS[3]).mean()) / 4
                        tSDev7 = ((R3TS[0]).std() + (R3TS[1]).std() + (R3TS[2]).std() + (R3TS[3]).std()) / 4
                        xUSL7, xLSL7, xUCL7, xLCL7, sUCL7, sLCL7, PpkL7, PpkU7, Pp7 = pp.processCap(tMean7,
                                                                                                             tSDev7,
                                                                                                             smp_Sz)
                else:
                    tMean7 = ((R3TS[0]).mean() + (R3TS[1]).mean() + (R3TS[2]).mean() + (R3TS[3]).mean()) / 4
                    xUCL7, xLCL7, xUSL7, xLSL7, sUCL7, sLCL7 = hUCLb, hLCLb, hUSLb, hLSLb, dUCLb, dLCLb

                    tSDev7 = ((R3TS[0]).std() + (R3TS[1]).std() + (R3TS[2]).std() + (R3TS[3]).std()) / 4
                    PpkL7, PpkU7, Pp7 = pp.hisCap(tMean7, tSDev7, xLSL7, xUSL7)
                    # print('\nUsing Historical MEAN:', tMean7a)
                # Compute process capability for Ring 3 Data ----------------------------------------[]
                pkC = min(PpkL7, PpkU7)
                tsC.append(round(pkC, 4))
                # Free up some memory spaces -----
                if len(tsC) > 1:
                    del (tsC[:1])
                print('Head9-12 (TS) Dev:', round(tSDev7, 4))
                print('USL/LSL (TS):', round(xUSL7,4), round(xLSL7,4))
                print('UCL/LCL (TS):', xUCL7, xLCL7)
                print('Head9-12 (TS) Pp/Ppk:', round(Pp7, 4), '\t', tsC[-1])

            if R4:
                # Plot X-Axis data points --------
                im62.set_xdata(np.arange(db_freq))
                im63.set_xdata(np.arange(db_freq))
                im64.set_xdata(np.arange(db_freq))
                im65.set_xdata(np.arange(db_freq))
                im66.set_xdata(np.arange(db_freq))
                im67.set_xdata(np.arange(db_freq))
                im68.set_xdata(np.arange(db_freq))
                im69.set_xdata(np.arange(db_freq))
                if optm2:
                    # Plot Y-Axis data points for XEar ---
                    im62.set_ydata((R4TS[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im63.set_ydata((R4TS[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im64.set_ydata((R4TS[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im65.set_ydata((R4TS[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im66.set_ydata((R4TS[0]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im67.set_ydata((R4TS[1]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im68.set_ydata((R4TS[2]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im69.set_ydata((R4TS[3]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    # Calculate process capability for Ring 2 ---------
                else:
                    # Plot Y-Axis data points for XEar ---
                    im62.set_ydata((R4TS[0]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im63.set_ydata((R4TS[1]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im64.set_ydata((R4TS[2]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im65.set_ydata((R4TS[3]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im66.set_ydata((R4TS[0]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im67.set_ydata((R4TS[1]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im68.set_ydata((R4TS[2]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im69.set_ydata((R4TS[3]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                # Calculate process capability for Ring 2 ----------------------------------------
                if not uhl:
                    if len(autoGpMeanB) == smp_Sz:
                        # filter out potential null and zero values from subgroup mean deductions ----[]
                        if R4TS[0].any() or R4TS[1].any() or R4TS[2].any() or R4TS[3].any():
                            pass
                        else:
                            tMean8 = ((R4TS[0]).mean() + (R4TS[1]).mean() + (R4TS[2]).mean() + (R4TS[3]).mean()) / 4
                            tSDev8 = ((R4TS[0]).std() + (R4TS[1]).std() + (R4TS[2]).std() + (R4TS[3]).std()) / 4

                        if len(autoUSLE) != 0:
                            # Compute process capability using New Set limits -------------------------[]
                            sUCL8, sLCL8, xUSL8, xLSL8, xUCL8, xLCL8 = autosUCLB[0], autosLCLB[0], autoUSLB[0], \
                                autoLSLB[0], autoUCLB[0], autoLCLB[0]
                            PpkL8, PpkU8, Pp8 = pp.hisCap(tMean8, tSDev8, xLSL8, xUSL8)
                            # print('\nUsing the Process MEAN:', tMean8a)
                        else:
                            xUSL8, xLSL8, xUCL8, xLCL8, sUCL8, sLCL8, PpkL8, PpkU8, Pp8 = pp.processCap(
                                tMean8, tSDev8,
                                smp_Sz)
                    else:
                        tMean8 = ((R4TS[0]).mean() + (R4TS[1]).mean() + (R4TS[2]).mean() + (R4TS[3]).mean()) / 4
                        tSDev8 = ((R4TS[0]).std() + (R4TS[1]).std() + (R4TS[2]).std() + (R4TS[3]).std()) / 4
                        xUSL8, xLSL8, xUCL8, xLCL8, sUCL8, sLCL8, PpkL8, PpkU8, Pp8 = pp.processCap(tMean8,
                                                                                                             tSDev8,
                                                                                                             smp_Sz)
                        # print('\nUsing Ring 4 MEAN:', tMean8a)
                else:
                    tMean8 = ((R4TS[0]).mean() + (R4TS[1]).mean() + (R4TS[2]).mean() + (R4TS[3]).mean()) / 4
                    xUCL8, xLCL8, xUSL8, xLSL8, sUCL8, sLCL8 = hUCLb, hLCLb, hUSLb, hLSLb, dUCLb, dLCLb

                    tSDev8 = ((R4TS[0]).std() + (R4TS[1]).std() + (R4TS[2]).std() + (R4TS[3]).std()) / 4
                    PpkL8, PpkU8, Pp8 = pp.hisCap(tMean8, tSDev8, xLSL8, xUSL8)

                # Compute process capability for Ring 4 Data ----------------------------------------[]
                pkD = min(PpkL8, PpkU8)
                tsD.append(round(pkD, 4))
                # Free up some memory spaces -----
                if len(tsC) > 1:
                    del (tsC[:1])
                print('Head13-16 (TS) Dev:', round(tSDev8, 4))
                print('USL/LSL (TS):', round(xUSL8,4), round(xLSL8,4))
                print('UCL/LCL (TS):', xUCL8, xLCL8)
                print('Head13-16 (TS) Pp/Ppk:', round(Pp8, 4), '\t', tsD[-1])

            # ----- Calculate Process Data ----------------------------------------------------------[]
            # Only account for active rings with process data ----
            if not uhl:
                if len(autoGpMeanB) <= smp_Sz:
                    if tMean5 != 0 or tMean6 != 0 or tMean7 != 0 or tMean8 != 0:
                        TMean2 = np.array([tMean5, tMean6, tMean7, tMean8])
                        TMean2 = (TMean2[np.nonzero(TMean2)]).mean()  # compute for the mean of mean
                        TSdev2 = np.array([tSDev5, tSDev6, tSDev7, tSDev8])
                        TSdev2 = (TSdev2[np.nonzero(TSdev2)]).mean()

                    # Sample and Compute the subgroup Process Mean and subgroup Deviation
                    elif np.isnan(TMean2):
                        TMean2 = 0.0
                        TSdev2 = 0.68 * 2   # i.e 1sigma DOF
                    else:
                        TMean2 = 0.0
                        TSdev2 = 0.68 * 2   # i.e 1sigma DOF

                    sMeanb = 0
                    xMeanb = 0  # Turn off center line until limits lock
                    autoGpMeanB.append(TMean2)  # Sample subgroup Mean for Center Line auto-derivative
                    autoGpDevB.append(TSdev2)  # Sample subgroup Mean for Center Line auto-derivative
                    xUSLb, xLSLb, xUCLb, xLCLb, sUCLb, sLCLb, PpkLb, PpkUb, PpRb = pp.processCap(TMean2, TSdev2, smp_Sz)

                else:
                    TMean2 = sum(autoGpMeanB) / len(autoGpMeanB)    # compute & keep new Mean for the subgroup
                    TSdev2 = sum(autoGpDevB) / len(autoGpDevB)      # Compute average dev for subgroup Center line
                    sMeanb = 0
                    xMeanb = 0                                      # Turn off center line until limits lock
                    if len(autoUSLB) < 2:
                        xUSLb, xLSLb, xUCLb, xLCLb, sUCLb, sLCLb, PpkLb, PpkUb, PpRb = pp.processCap(TMean2, TSdev2,
                                                                                                     smp_Sz)
                        sClineB.append(TSdev2)
                        autoUSLB.append(xUSLb)
                        autoLSLB.append(xLSLb)
                        autoUCLB.append(xUCLb)
                        autoLCLB.append(xLCLb)
                        autosUCLB.append(sUCLb)
                        autosLCLB.append(sLCLb)
                    else:
                        # Test static arrays for valid values --------------------[]
                        xUSLb = autoUSLB[0]
                        xLSLb = autoLSLB[0]
                        xUCLb = autoUCLB[0]
                        xLCLb = autoLCLB[0]
                        sUCLb = autosUCLB[0]
                        sLCLb = autosLCLB[0]
                        sMeanb = sClineB[0]
                        xMeanb = TMean2                                             # Turn off center line until locks
                        TSdev2 = np.array([tSDev5, tSDev6, tSDev7, tSDev8])         # Allow subgroup DOF on StdDev
                        TSdev2 = (TSdev2[np.nonzero(TSdev2)]).mean()                # total heads in the process
                        PpkLb, PpkUb, PpRb = pp.hisCap(TMean2, TSdev2, xLSLb, xUSLb)
            else:
                xMeanb = HistMeanB                                                  # X Bar Center Line
                sMeanb = HistSDevB                                                  # S Bar Center Line
                # ---- Compute Process Mean --------
                proM2 = (tMean5, tMean6, tMean7, tMean8)
                if sum(proM2) != 0:
                    TMean2 = np.array([tMean5, tMean6, tMean7, tMean8])             # Allow subgroup DOF on StdDev
                    TMean2 = (TMean2[np.nonzero(TMean2)]).mean()                    # total heads in the process
                else:
                    pass
                TSdev2 = np.array([tSDev5, tSDev6, tSDev7, tSDev8])                 # Allow subgroup DOF on StdDev
                TSdev2 = (TSdev2[np.nonzero(TSdev2)]).mean()                        # total heads in the process

                xUSLb, xLSLb, xUCLb, xLCLb, sUCLb, sLCLb = hUSLb, hLSLb, hUCLb, hLCLb, dUCLb, dLCLb
                PpkLb, PpkUb, PpRb = pp.hisCap(TMean5, TSdev2, xLSLb, xUSLb)

            # Compute process capability for Process Data -------------------------------------------[]
            procB = min(PpkLb, PpkUb)       # Average Ppk per available rings combinations
            Ppkb.append(round(procB, 4))    # copy 2sig. result into a dynamic array
            # Free up some memory spaces -----
            if len(Ppkb) > 1:
                del (Ppkb[:1])
            print('-' * 55)
            print('Process (TS) Mean/SDev:', round(TMean2, 4), round(TSdev2, 4))
            print('Process (TS) UCL/LCL:', xUCLb, xLCLb)
            print('Process (TS) USL/LSL:', round(xUSLb, 4), round(xLSLb, 4))
            print('Process (TS) Pp/Ppk:', round(PpRb, 4), '\t', Ppkb[-1])
            print('-' * 55)
        # -------------------------------------------------------[]

        if TapeTemperatur:
            # print('\nControl Temp variable activated...')
            if R1:  # R1TS, R2TS, R3TS, R4TS
                im70.set_xdata(np.arange(db_freq))
                im71.set_xdata(np.arange(db_freq))
                im72.set_xdata(np.arange(db_freq))
                im73.set_xdata(np.arange(db_freq))
                im74.set_xdata(np.arange(db_freq))
                im75.set_xdata(np.arange(db_freq))
                im76.set_xdata(np.arange(db_freq))
                im77.set_xdata(np.arange(db_freq))
                if optm2:
                    # Plot Y-Axis data points for XFar --- # scaled down factor
                    im70.set_ydata((R1TT[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im71.set_ydata((R1TT[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im72.set_ydata((R1TT[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im73.set_ydata((R1TT[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im74.set_ydata((R1TT[0]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im75.set_ydata((R1TT[1]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im76.set_ydata((R1TT[2]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im77.set_ydata((R1TT[3]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    # Calculate process capability for Ring 1 ---------
                else:
                    # Plot Y-Axis data points for XFar --- # scaled down factor
                    im70.set_ydata((R1TT[0]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im71.set_ydata((R1TT[1]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im72.set_ydata((R1TT[2]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im73.set_ydata((R1TT[3]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im74.set_ydata((R1TT[0]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im75.set_ydata((R1TT[1]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im76.set_ydata((R1TT[2]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im77.set_ydata((R1TT[3]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    # Calculate process capability for Ring 1 ---------
                if not uhl:
                    if len(autoGpMeanC) == smp_Sz:
                        # filter out potential null and zero values from subgroup mean deductions ----
                        if R1TT[0].any() or R1TT[1].any() or R1TT[2].any() or R1TT[3].any():
                            pass
                        else:
                            tMean9 = ((R1TT[0]).mean() + (R1TT[1]).mean() + (R1TT[2]).mean() + (R1TT[3]).mean()) / 4
                            tSDev9 = ((R1TT[0]).std() + (R1TT[1]).std() + (R1TT[2]).std() + (R1TT[3]).std()) / 4

                        if len(autoUSLC) != 0:
                            # Compute process capability using New Set limits -------
                            sUCL9, sLCL9, xUSL9, xLSL9, xUCL9, xLCL9 = autosUCLC[0], autosLCLC[0], autoUSLC[0], \
                                autoLSLC[0], autoUCLC[0], autoLCLC[0]
                            PpkL9, PpkU9, Pp9 = pp.hisCap(tMean9, tSDev9, xLSL9, xUSL9)
                        else:
                            xUSL9, xLSL9, xUCL9, xLCL9, sUCL9, sLCL9, PpkL9, PpkU9, Pp9 = pp.processCap(
                                tMean9, tSDev9, smp_Sz)
                    else:
                        tMean9 = ((R1TT[0]).mean() + (R1TT[1]).mean() + (R1TT[2]).mean() + (R1TT[3]).mean()) / 4
                        tSDev9 = ((R1TT[0]).std() + (R1TT[1]).std() + (R1TT[2]).std() + (R1TT[3]).std()) / 4
                        xUSL9, xLSL9, xUCL9, xLCL9, sUCL9, sLCL9, PpkL9, PpkU9, Pp9 = pp.processCap(tMean9, tSDev9,
                                                                                                             smp_Sz)
                else:
                    tMean9 = ((R1TT[0]).mean() + (R1TT[1]).mean() + (R1TT[2]).mean() + (R1TT[3]).mean()) / 4
                    xUCL9, xLCL9, xUSL9, xLSL9, sUCL9, sLCL9 = hUCLc, hLCLc, hUSLc, hLSLc, dUCLc, dLCLc

                    tSDev9 = ((R1TT[0]).std() + (R1TT[1]).std() + (R1TT[2]).std() + (R1TT[3]).std()) / 4
                    PpkL9, PpkU9, Pp9 = pp.hisCap(tMean9, tSDev9, xLSL9, xUSL9)

                # Compute process capability for Ring 1 Data ----------------------------------------[]
                pkA = min(PpkL9, PpkU9)
                ttA.append(round(pkA, 4))
                # Free up some memory spaces -----
                if len(ttA) > 1:
                    del (ttA[:1])
                print('Head1-4 (TT) Dev:', round(tSDev9, 4))
                print('USL/LSL (TT):', round(xUSL9, 4), round(xLSL9, 4))
                print('UCL/LCL (TT):', xUCL9, xLCL9)
                print('Head1-4 (TT) Pp/Ppk:', round(Pp9, 4), '\t', ttA[-1])

            if R2:
                # Plot X-Axis data points --------
                im78.set_xdata(np.arange(db_freq))
                im79.set_xdata(np.arange(db_freq))
                im80.set_xdata(np.arange(db_freq))
                im81.set_xdata(np.arange(db_freq))
                im82.set_xdata(np.arange(db_freq))
                im83.set_xdata(np.arange(db_freq))
                im84.set_xdata(np.arange(db_freq))
                im85.set_xdata(np.arange(db_freq))
                if optm2:
                    # Plot Y-Axis data points for XFar ---
                    im78.set_ydata((R2TT[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im79.set_ydata((R2TT[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im80.set_ydata((R2TT[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im81.set_ydata((R2TT[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im82.set_ydata((R2TT[0]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im83.set_ydata((R2TT[1]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im84.set_ydata((R2TT[2]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im85.set_ydata((R2TT[3]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    # Calculate process capability for Ring 2 ---------
                else:
                    # Plot Y-Axis data points for XFar ---
                    im78.set_ydata((R2TT[0]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im79.set_ydata((R2TT[1]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im80.set_ydata((R2TT[2]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im81.set_ydata((R2TT[3]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im82.set_ydata((R2TT[0]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im83.set_ydata((R2TT[1]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im84.set_ydata((R2TT[2]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im85.set_ydata((R2TT[3]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    # Calculate process capability for Ring 2 ---------
                if not uhl:
                    if len(autoGpMeanC) == smp_Sz:
                        # filter out potential null and zero values from subgroup mean deductions ----[]
                        if R2TT[0].any() or R2TT[1].any() or R2TT[2].any() or R2TT[3].any():
                            pass
                        else:
                            tMean10 = ((R2TT[0]).mean() + (R2TT[1]).mean() + (R2TT[2]).mean() + (R2TT[3]).mean()) / 4
                            tSDev10 = ((R2TT[0]).std() + (R2TT[1]).std() + (R2TT[2]).std() + (R2TT[3]).std()) / 4

                        if len(autoUSLC) != 0:
                            # Compute process capability using New Set limits --------------------
                            sUCL10, sLCL10, xUSL10, xLSL10, xUCL10, xLCL10 = autosUCLC[0], autosLCLC[0], autoUSLC[0], \
                                autoLSLC[0], autoUCLC[0], autoLCLC[0]
                            PpkL10, PpkU10, Pp10 = pp.hisCap(tMean10, tSDev10, xLSL10, xUSL10)
                        else:
                            xUSL10, xLSL10, xUCL10, xLCL10, sUCL10, sLCL10, PpkL10, PpkU10, Pp10 = pp.processCap(
                                tMean10, tSDev10, smp_Sz)
                    else:
                        tMean10 = ((R2TT[0]).mean() + (R2TT[1]).mean() + (R2TT[2]).mean() + (R2TT[3]).mean()) / 4
                        tSDev10 = ((R2TT[0]).std() + (R2TT[1]).std() + (R2TT[2]).std() + (R2TT[3]).std()) / 4
                        xUSL10, xLSL10, xUCL10, xLCL10, sUCL10, sLCL10, PpkL10, PpkU10, Pp10 = pp.processCap(tMean10,
                                                                                                             tSDev10,
                                                                                                             smp_Sz)
                else:
                    tMean10 = ((R2TT[0]).mean() + (R2TT[1]).mean() + (R2TT[2]).mean() + (R2TT[3]).mean()) / 4
                    xUCL10, xLCL10, xUSL10, xLSL10, sUCL10, sLCL10 = hUCLc, hLCLc, hUSLc, hLSLc, dUCLc, dLCLc

                    tSDev10 = ((R2TT[0]).std() + (R2TT[1]).std() + (R2TT[2]).std() + (R2TT[3]).std()) / 4
                    PpkL10, PpkU10, Pp10 = pp.hisCap(tMean10, tSDev10, xLSL10, xUSL10)

                # Compute process capability for Ring 2 Data ----------------------------------------[]
                pkB = min(PpkL10, PpkU10)
                ttB.append(round(pkB, 4))
                # Free up some memory spaces -----
                if len(ttB) > 1:
                    del (ttB[:1])
                print('Head5-8 (TT) Dev:', round(tSDev10, 4))
                print('USL/LSL (TT):', round(xUSL10, 4), round(xLSL10, 4))
                print('UCL/LCL (TT):', xUCL10, xLCL10)
                print('Head5-8 (TT) Pp/Ppk:', round(Pp10, 4), '\t',  ttB[-1])

            if R3:
                # Plot X-Axis data points --------
                im86.set_xdata(np.arange(db_freq))
                im87.set_xdata(np.arange(db_freq))
                im88.set_xdata(np.arange(db_freq))
                im89.set_xdata(np.arange(db_freq))
                im90.set_xdata(np.arange(db_freq))
                im91.set_xdata(np.arange(db_freq))
                im92.set_xdata(np.arange(db_freq))
                im93.set_xdata(np.arange(db_freq))
                if optm2:
                    # Plot Y-Axis data points for XFar ---
                    im86.set_ydata((R3TT[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im87.set_ydata((R3TT[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im88.set_ydata((R3TT[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im89.set_ydata((R3TT[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im90.set_ydata((R3TT[0]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im91.set_ydata((R3TT[1]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im92.set_ydata((R3TT[2]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im93.set_ydata((R3TT[3]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                else:
                    # Plot Y-Axis data points for XFar ---
                    im86.set_ydata((R3TT[0]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im87.set_ydata((R3TT[1]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im88.set_ydata((R3TT[2]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im89.set_ydata((R3TT[3]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im90.set_ydata((R3TT[0]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im91.set_ydata((R3TT[1]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im92.set_ydata((R3TT[2]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im93.set_ydata((R3TT[3]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    # Calculate process capability for Ring 3 ---------
                if not uhl:
                    if len(autoGpMeanC) == smp_Sz:
                        # filter out potential null and zero values from subgroup mean deductions ----[]
                        if R3TT[0].any() or R3TT[1].any() or R3TT[2].any() or R3TT[3].any():
                            pass
                        else:
                            tMean11 = ((R3TT[0]).mean() + (R3TT[1]).mean() + (R3TT[2]).mean() + (R3TT[3]).mean()) / 4
                            tSDev11 = ((R3TT[0]).std() + (R3TT[1]).std() + (R3TT[2]).std() + (R3TT[3]).std()) / 4

                        if len(autoUSLC) != 0:
                            # Compute process capability using New Set limits -------
                            sUCL11, sLCL11, xUSL11, xLSL11, xUCL11, xLCL11 = autosUCLC[0], autosLCLC[0], autoUSLC[0], \
                                autoLSLC[0], autoUCLC[0], autoLCLC[0]
                            PpkL11, PpkU11, Pp11 = pp.hisCap(tMean11, tSDev11, xLSL11, xUSL11)
                        else:
                            xUSL11, xLSL11, xUCL11, xLCL11, sUCL11, sLCL11, PpkL11, PpkU11, Pp11 = pp.processCap(
                                tMean11, tSDev11, smp_Sz)
                    else:
                        tMean11 = ((R3TT[0]).mean() + (R3TT[1]).mean() + (R3TT[2]).mean() + (R3TT[3]).mean()) / 4
                        tSDev11 = ((R3TT[0]).std() + (R3TT[1]).std() + (R3TT[2]).std() + (R3TT[3]).std()) / 4
                        xUSL11, xLSL11, xUCL11, xLCL11, sUCL11, sLCL11, PpkL11, PpkU11, Pp11 = pp.processCap(tMean11,
                                                                                                             tSDev11,
                                                                                                             smp_Sz)
                else:
                    tMean11 = ((R3TT[0]).mean() + (R3TT[1]).mean() + (R3TT[2]).mean() + (R3TT[3]).mean()) / 4
                    xUCL11, xLCL11, xUSL11, xLSL11, sUCL11, sLCL11 = hUCLc, hLCLc, hUSLc, hLSLc, dUCLc, dLCLc

                    tSDev11 = ((R3TT[0]).std() + (R3TT[1]).std() + (R3TT[2]).std() + (R3TT[3]).std()) / 4
                    PpkL11, PpkU11, Pp11 = pp.hisCap(tMean11, tSDev11, xLSL11, xUSL11)

                # Compute process capability for Ring 3 Data ----------------------------------------[]
                pkC = min(PpkL11, PpkU11)
                ttC.append(round(pkC, 4))
                # Free up some memory spaces -----
                if len(ttC) > 1:
                    del (ttC[:1])
                print('Head9-12 (TT) Dev:', round(tSDev11, 4))
                print('USL/LSL (TT):', round(xUSL11, 4), round(xLSL11, 4))
                print('UCL/LCL (TT):', xUCL11, xLCL11)
                print('Head9-12 (TT) Pp/Ppk:', round(Pp11, 4), '\t', ttC[-1])

            if R4:
                # Plot X-Axis data points --------
                im94.set_xdata(np.arange(db_freq))
                im95.set_xdata(np.arange(db_freq))
                im96.set_xdata(np.arange(db_freq))
                im97.set_xdata(np.arange(db_freq))
                im98.set_xdata(np.arange(db_freq))
                im99.set_xdata(np.arange(db_freq))
                im100.set_xdata(np.arange(db_freq))
                im101.set_xdata(np.arange(db_freq))
                if optm2:
                    # Plot Y-Axis data points for XFar ---
                    im94.set_ydata((R4TT[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im95.set_ydata((R4TT[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im96.set_ydata((R4TT[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im97.set_ydata((R4TT[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im98.set_ydata((R4TT[0]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im99.set_ydata((R4TT[1]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im100.set_ydata((R4TT[2]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im101.set_ydata((R4TT[3]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    # Calculate process capability for Ring 2 ---------
                else:
                    # Plot Y-Axis data points for XFar ---
                    im94.set_ydata((R4TT[0]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im95.set_ydata((R4TT[1]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im96.set_ydata((R4TT[2]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im97.set_ydata((R4TT[3]).rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im98.set_ydata((R4TT[0]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im99.set_ydata((R4TT[1]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im100.set_ydata((R4TT[2]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im101.set_ydata((R4TT[3]).rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                # Calculate process capability for Ring 2 ----------------------------------------
                if not uhl:
                    if len(autoGpMeanC) == smp_Sz:
                        # filter out potential null and zero values from subgroup mean deductions ----[]
                        if R4TT[0].any() or R4TT[1].any() or R4TT[2].any() or R4TT[3].any():
                            pass
                        else:
                            tMean12 = ((R4TT[0]).mean() + (R4TT[1]).mean() + (R4TT[2]).mean() + (R4TT[3]).mean()) / 4
                            tSDev12 = ((R4TT[0]).std() + (R4TT[1]).std() + (R4TT[2]).std() + (R4TT[3]).std()) / 4

                        if len(autoUSLC) != 0:
                            # Compute process capability using New Set limits -------------------------[]
                            sUCL12, sLCL12, xUSL12, xLSL12, xUCL12, xLCL12 = autosUCLC[0], autosLCLC[0], autoUSLC[0], \
                                autoLSLC[0], autoUCLC[0], autoLCLC[0]
                            PpkL12, PpkU12, Pp12 = pp.hisCap(tMean12, tSDev12, xLSL12, xUSL12)
                            # print('\nUsing the Process MFAN:', tMean8a)
                        else:
                            xUSL12, xLSL12, xUCL12, xLCL12, sUCL12, sLCL12, PpkL12, PpkU12, Pp12 = pp.processCap(
                                tMean12, tSDev12,
                                smp_Sz)
                    else:
                        tMean12 = ((R4TT[0]).mean() + (R4TT[1]).mean() + (R4TT[2]).mean() + (R4TT[3]).mean()) / 4
                        tSDev12 = ((R4TT[0]).std() + (R4TT[1]).std() + (R4TT[2]).std() + (R4TT[3]).std()) / 4
                        xUSL12, xLSL12, xUCL12, xLCL12, sUCL12, sLCL12, PpkL12, PpkU12, Pp12 = pp.processCap(tMean12,
                                                                                                             tSDev12,
                                                                                                             smp_Sz)
                        # print('\nUsing Ring 4 MFAN:', tMean8a)
                else:
                    tMean12 = ((R4TT[0]).mean() + (R4TT[1]).mean() + (R4TT[2]).mean() + (R4TT[3]).mean()) / 4
                    xUCL12, xLCL12, xUSL12, xLSL12, sUCL12, sLCL12 = hUCLc, hLCLc, hUSLc, hLSLc, dUCLc, dLCLc

                    tSDev12 = ((R4TT[0]).std() + (R4TT[1]).std() + (R4TT[2]).std() + (R4TT[3]).std()) / 4
                    PpkL12, PpkU12, Pp12 = pp.hisCap(tMean12, tSDev12, xLSL12, xUSL12)

                # Compute process capability for Ring 4 Data ----------------------------------------[]
                pkD = min(PpkL12, PpkU12)
                ttD.append(round(pkD, 4))
                # Free up some memory spaces -----
                if len(ttD) > 1:
                    del (ttD[:1])
                print('Head13-16 (TT) Dev:', round(tSDev12, 4))
                print('USL/LSL (TT):', round(xUSL12, 4), round(xLSL12, 4))
                print('UCL/LCL (TT):', xUCL12, xLCL12)
                print('Head13-16 (TT) Pp/Ppk:', round(Pp12, 4), '\t', ttD[-1])

            # ----- Calculate Process Data ----------------------------------------------------------[]
            # Only account for active rings with process data ----
            if not uhl:
                if len(autoGpMeanC) <= smp_Sz:
                    if tMean9 != 0 or tMean10 != 0 or tMean11 != 0 or tMean12 != 0:
                        TMean3 = np.array([tMean9, tMean10, tMean11, tMean12])
                        TMean3 = (TMean3[np.nonzero(TMean3)]).mean()  # compute for the mean of mean
                        TSdev3 = np.array([tSDev9, tSDev10, tSDev11, tSDev12])
                        TSdev3 = (TSdev3[np.nonzero(TSdev3)]).mean()

                    # Sample and Compute the subgroup Process Mean and subgroup Deviation
                    elif np.isnan(TMean3):
                        TMean3 = 0.0
                        TSdev3 = 0.68 * 2   # i.e 1sigma DOF
                    else:
                        TMean3 = 0.0
                        TSdev3 = 0.68 * 2   # i.e 1sigma DOF

                    sMeanc = 0
                    xMeanc = 0  # Turn off center line until limits lock
                    autoGpMeanC.append(TMean3)  # Sample subgroup Mean for Center Line auto-derivative
                    autoGpDevC.append(TSdev3)   # Sample subgroup Mean for Center Line auto-derivative
                    xUSLc, xLSLc, xUCLc, xLCLc, sUCLc, sLCLc, PpkLc, PpkUc, PpRc = pp.processCap(TMean3, TSdev3, smp_Sz)

                else:
                    TMean3 = sum(autoGpMeanC) / len(autoGpMeanC)    # compute & keep new Mean for the subgroup
                    TSdev3 = sum(autoGpDevC) / len(autoGpDevC)      # Compute average dev for subgroup Center line
                    sMeanc = 0
                    xMeanc = 0  # Turn off center line until limits lock
                    if len(autoUSLC) < 2:
                        xUSLc, xLSLc, xUCLc, xLCLc, sUCLc, sLCLc, PpkLc, PpkUc, PpRe = pp.processCap(TMean3, TSdev3,
                                                                                                     smp_Sz)
                        sClineC.append(TSdev3)
                        autoUSLC.append(xUSLc)
                        autoLSLC.append(xLSLc)
                        autoUCLC.append(xUCLc)
                        autoLCLC.append(xLCLc)
                        autosUCLC.append(sUCLc)
                        autosLCLC.append(sLCLc)
                    else:
                        # Test static arrays for valid values --------------------[]
                        xUSLc = autoUSLC[0]
                        xLSLc = autoLSLC[0]
                        xUCLc = autoUCLC[0]
                        xLCLc = autoLCLC[0]
                        sUCLc = autosUCLC[0]
                        sLCLc = autosLCLC[0]
                        sMeanc = sClineC[0]
                        xMeanc = TMean3                                         # Turn off center line until limits lock
                        TSdev3 = np.array([tSDev9, tSDev10, tSDev11, tSDev12])  # Allow subgroup DOF on StdDev
                        TSdev3 = (TSdev3[np.nonzero(TSdev3)]).mean()  # total heads in the process
                        PpkLc, PpkUc, PpRc = pp.hisCap(TMean3, TSdev3, xLSLc, xUSLc)
            else:
                xMeanc = HistMeanC                                              # X Bar Center Line
                sMeanc = HistSDevC                                              # S Bar Center Line
                # ---- Compute Process Mean --------
                proM3 = (tMean9, tMean10, tMean11, tMean12)
                if sum(proM3) != 0:
                    TMean3 = np.array([tMean9, tMean10, tMean11, tMean12])     # Group process mean    -- (Cpk)
                    TMean3 = (TMean3[np.nonzero(TMean3)]).mean()
                else:
                    pass
                TSdev3 = np.array([tSDev9, tSDev10, tSDev11, tSDev12])         # Allow subgroup DOF on StdDev
                TSdev3 = (TSdev3[np.nonzero(TSdev3)]).mean()                   # total heads in the process

                xUSLc, xLSLc, xUCLc, xLCLc, sUCLc, sLCLc = hUSLc, hLSLc, hUCLc, hLCLc, dUCLc, dLCLc
                PpkLc, PpkUc, PpRc = pp.hisCap(TMean3, TSdev3, xLSLc, xUSLc)
            # Compute process capability for Process Data -------------------------------------------[]
            procC = min(PpkLc, PpkUc)  # Average Ppk per available rings combinations
            Ppkc.append(round(procC, 4))  # copy 2sig. result into a dynamic array
            # Free up some memory spaces -----
            if len(Ppkc) > 1:
                del (Ppkc[:1])
            print('-' * 55)
            print('Process (TT) Mean/SDev:', round(TMean3, 4), round(TSdev3, 4))
            print('Process (TT) UCL/LCL:', xUCLc, xLCLc)
            print('Process (TT) USL/LSL:', round(xUSLc, 4), round(xLSLc, 4))
            print('Process (TT) Pp/Ppk:', round(PpRc, 4), '\t', Ppkc[-1])
            print('-' * 55)

        # ------------------------------------ END OF DNV Params ---------------------------------------------------[]
        if TSub_TempRatio:
            # print('\nControl Temp variable activated...') ----------------------[]
            if R1:           # NOTE:  ΔT = T2 - T1 | ΔR = T1/T2
                if DNVspecify:
                    delta1 = (R1TT[0]/R1ST[0])
                    delta2 = (R1TT[1]/R1ST[1])
                    delta3 = (R1TT[2]/R1ST[2])
                    delta4 = (R1TT[3]/R1ST[3])
                else:
                    delta1 = (R1ST[0] - R1TT[0])
                    delta2 = (R1ST[1] - R1TT[1])
                    delta3 = (R1ST[2] - R1TT[2])
                    delta4 = (R1ST[3] - R1TT[3])
                im102.set_xdata(np.arange(db_freq))
                im103.set_xdata(np.arange(db_freq))
                im104.set_xdata(np.arange(db_freq))
                im105.set_xdata(np.arange(db_freq))
                im106.set_xdata(np.arange(db_freq))
                im107.set_xdata(np.arange(db_freq))
                im108.set_xdata(np.arange(db_freq))
                im109.set_xdata(np.arange(db_freq))
                if optm2:
                    # Plot Y-Axis data points for XBar --- # scaled down factor
                    im102.set_ydata(delta1.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im103.set_ydata(delta2.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im104.set_ydata(delta3.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im105.set_ydata(delta4.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im106.set_ydata(delta1.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im107.set_ydata(delta2.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im108.set_ydata(delta3.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im109.set_ydata(delta4.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    # Calculate process capability for Ring 1 ---------
                else:
                    # Plot Y-Axis data points for XBar --- # scaled down factor
                    im102.set_ydata(delta1.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im103.set_ydata(delta2.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im104.set_ydata(delta3.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im105.set_ydata(delta4.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im106.set_ydata(delta1.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im107.set_ydata(delta2.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im108.set_ydata(delta3.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im109.set_ydata(delta4.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    # Calculate process capability for Ring 1 ---------
                if not uhl:
                    if len(autoGpMeanD) == smp_Sz:
                        # filter out potential null and zero values from subgroup mean deductions ----
                        if delta1.any() or delta2.any() or delta3.any() or delta4.any():
                            pass
                        else:
                            tMean13 = (delta1.mean() + delta2.mean() + delta3.mean() + delta4.mean()) / 4
                            tSDev13 = (delta1.std() + delta2.std() + delta3.std() + delta4.std()) / 4

                        if len(autoUSLD) != 0:
                            # Compute process capability using New Set limits -------
                            sUCL13, sLCL13, xUSL13, xLSL13, xUCL13, xLCL13 = autosUCLD[0], autosLCLD[0], autoUSLD[0], \
                                autoLSLD[0], autoUCLD[0], autoLCLD[0]
                            PpkL13, PpkU13, Pp13 = pp.hisCap(tMean13, tSDev13, xLSL13, xUSL13)
                        else:
                            xUSL13, xLSL13, xUCL13, xLCL13, sUCL13, sLCL13, PpkL13, PpkU13, Pp13 = pp.processCap(tMean13, tSDev13, smp_Sz)
                    else:
                        tMean13 = (delta1.mean() + delta2.mean() + delta3.mean() + delta4.mean()) / 4
                        tSDev13 = (delta1.std() + delta2.std() + delta3.std() + delta4.std()) / 4
                        xUSL13, xLSL13, xUCL13, xLCL13, sUCL13, sLCL13, PpkL13, PpkU13, Pp13 = pp.processCap(tMean13, tSDev13, smp_Sz)
                else:
                    tMean13 = (delta1.mean() + delta2.mean() + delta3.mean() + delta4.mean()) / 4
                    xUCL13, xLCL13, xUSL13, xLSL13, sUCL13, sLCL13 = hUCLd, hLCLd, hUSLd, hLSLd, dUCLd, dLCLd

                    tSDev13 = (delta1.std() + delta2.std() + delta3.std() + delta4.std()) / 4
                    PpkL13, PpkU13, Pp13 = pp.hisCap(tMean13, tSDev13, xLSL13, xUSL13)

                # Compute process capability for Ring 1 Data ----------------------------------------[]
                pkA = min(PpkL13, PpkU13)
                dtA.append(round(pkA, 4))
                # Free up some memory spaces -----
                if len(dtA) > 1:
                    del (dtA[:1])
                if DNVspecify:
                    lbl = '(TR)'
                else:
                    lbl = '(DT)'
                print('Head1-4 '+lbl+' Dev:', round(tSDev13, 4))
                print('USL/LSL '+lbl+' :', round(xUSL13, 4), round(xLSL13, 4))
                print('UCL/LCL '+lbl+' : ', xUCL13, xLCL13)
                print('Head1-4 '+lbl+' Pp/Ppk:', round(Pp13, 4), '\t', dtA[-1])

            if R2:
                # Compute delta temperatures ----
                if DNVspecify:
                    delta5 = (R2TT[0]/R2ST[0])
                    delta6 = (R2TT[1]/R2ST[1])
                    delta7 = (R2TT[2]/R2ST[2])
                    delta8 = (R2TT[3]/R2ST[3])
                else:
                    delta5 = (R2ST[0] - R2TT[0])
                    delta6 = (R2ST[1] - R2TT[1])
                    delta7 = (R2ST[2] - R2TT[2])
                    delta8 = (R2ST[3] - R2TT[3])
                # Plot X-Axis data points --------
                im110.set_xdata(np.arange(db_freq))
                im111.set_xdata(np.arange(db_freq))
                im112.set_xdata(np.arange(db_freq))
                im113.set_xdata(np.arange(db_freq))
                im114.set_xdata(np.arange(db_freq))
                im115.set_xdata(np.arange(db_freq))
                im116.set_xdata(np.arange(db_freq))
                im117.set_xdata(np.arange(db_freq))
                if optm2:
                    # Plot Y-Axis data points for XBar ---
                    im110.set_ydata(delta5.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im111.set_ydata(delta6.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im112.set_ydata(delta7.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im113.set_ydata(delta8.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im114.set_ydata(delta5.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im115.set_ydata(delta6.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im116.set_ydata(delta7.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im117.set_ydata(delta8.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    # Calculate process capability for Ring 2 ---------
                else:
                    # Plot Y-Axis data points for XBar ---
                    im110.set_ydata(delta5.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im111.set_ydata(delta6.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im112.set_ydata(delta7.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im113.set_ydata(delta8.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im114.set_ydata(delta5.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im115.set_ydata(delta6.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im116.set_ydata(delta7.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im117.set_ydata(delta8.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    # Calculate process capability for Ring 2 ---------
                if not uhl:
                    if len(autoGpMeanD) == smp_Sz:
                        # filter out potential null and zero values from subgroup mean deductions ----[]
                        if delta5.any() or delta6.any() or delta7.any() or delta8.any():
                            pass
                        else:
                            tMean14 = (delta5.mean() + delta6.mean() + delta7.mean() + delta8.mean()) / 4
                            tSDev14 = (delta5.std() + delta6.std() + delta7.std() + delta8.std()) / 4

                        if len(autoUSLB) != 0:
                            # Compute process capability using New Set limits --------------------
                            sUCL14, sLCL14, xUSL14, xLSL14, xUCL14, xLCL14 = autosUCLD[0], autosLCLD[0], autoUSLD[0], \
                                autoLSLD[0], autoUCLD[0], autoLCLD[0]
                            PpkL14, PpkU14, Pp14 = pp.hisCap(tMean14, tSDev14, xLSL14, xUSL14)
                        else:
                            xUSL14, xLSL14, xUCL14, xLCL14, sUCL14, sLCL14, PpkL14, PpkU14, Pp14 = pp.processCap(tMean14, tSDev14, smp_Sz)
                    else:
                        tMean14 = (delta5.mean() + delta6.mean() + delta7.mean() + delta8.mean()) / 4
                        tSDev14 = (delta5.std() + delta6.std() + delta7.std() + delta8.std()) / 4
                        xUSL14, xLSL14, xUCL14, xLCL14, sUCL14, sLCL14, PpkL14, PpkU14, Pp14 = pp.processCap(tMean14, tSDev14, smp_Sz)
                else:
                    tMean14 = (delta5.mean() + delta6.mean() + delta7.mean() + delta8.mean()) / 4
                    xUCL14, xLCL14, xUSL14, xLSL14, sUCL14, sLCL14 = hUCLd, hLCLd, hUSLd, hLSLd, dUCLd, dLCLd

                    tSDev14 = (delta5.std() + delta6.std() + delta7.std() + delta8.std()) / 4
                    PpkL14, PpkU14, Pp14 = pp.hisCap(tMean14, tSDev14, xLSL14, xUSL14)

                # Compute process capability for Ring 2 Data ----------------------------------------[]
                pkB = min(PpkL14, PpkU14)
                dtB.append(round(pkB, 4))
                # Free up some memory spaces -----
                if len(dtB) > 1:
                    del (dtB[:1])
                if DNVspecify:
                    lbl = '(TR)'
                else:
                    lbl = '(DT)'
                print('Head5-8 '+lbl+' Dev:', round(tSDev14, 4))
                print('USL/LSL '+lbl+': ', round(xUSL14, 4), round(xLSL14, 4))
                print('UCL/LCL '+lbl+': ', xUCL14, xLCL14)
                print('Head5-8 '+lbl+' Pp/Ppk:', round(Pp14, 4), '\t', dtB[-1])

            if R3:
                # Compute delta temperatures ----
                if DNVspecify:
                    delta9 = (R3TT[0]/R3ST[0])
                    deltaA = (R3TT[1]/R3ST[1])
                    deltaB = (R3TT[2]/R3ST[2])
                    deltaC = (R3TT[3]/R3ST[3])
                else:
                    delta9 = (R3ST[0] - R3TT[0])
                    deltaA = (R3ST[1] - R3TT[1])
                    deltaB = (R3ST[2] - R3TT[2])
                    deltaC = (R3ST[3] - R3TT[3])
                # Plot X-Axis data points --------
                im118.set_xdata(np.arange(db_freq))
                im119.set_xdata(np.arange(db_freq))
                im120.set_xdata(np.arange(db_freq))
                im121.set_xdata(np.arange(db_freq))
                im122.set_xdata(np.arange(db_freq))
                im123.set_xdata(np.arange(db_freq))
                im124.set_xdata(np.arange(db_freq))
                im125.set_xdata(np.arange(db_freq))
                if optm2:
                    # Plot Y-Axis data points for XBar ---
                    im118.set_ydata(delta9.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im119.set_ydata(deltaA.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im120.set_ydata(deltaB.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im121.set_ydata(deltaC.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im122.set_ydata(delta9.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im123.set_ydata(deltaA.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im124.set_ydata(deltaB.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im125.set_ydata(deltaC.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                else:
                    # Plot Y-Axis data points for XBar ---
                    im118.set_ydata(delta9.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im119.set_ydata(deltaA.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im120.set_ydata(deltaB.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im121.set_ydata(deltaC.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev --------------------------------------------
                    im122.set_ydata(delta9.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im123.set_ydata(deltaA.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im124.set_ydata(deltaB.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im125.set_ydata(deltaC.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    # Calculate process capability for Ring 3 ---------
                if not uhl:
                    if len(autoGpMeanD) == smp_Sz:
                        # filter out potential null and zero values from subgroup mean deductions ----[]
                        if delta9.any() or deltaA.any() or deltaB.any() or deltaC.any():
                            pass
                        else:
                            tMean15 = (delta9.mean() + deltaA.mean() + deltaB.mean() + deltaC.mean()) / 4
                            tSDev15 = (delta9.std() + deltaA.std() + deltaB.std() + deltaC.std()) / 4

                        if len(autoUSLD) != 0:
                            # Compute process capability using New Set limits -------
                            sUCL15, sLCL15, xUSL15, xLSL15, xUCL15, xLCL15 = autosUCLD[0], autosLCLD[0], autoUSLD[0], \
                                autoLSLD[0], autoUCLD[0], autoLCLD[0]
                            PpkL15, PpkU15, Pp15 = pp.hisCap(tMean15, tSDev15, xLSL15, xUSL15)
                        else:
                            xUSL15, xLSL15, xUCL15, xLCL15, sUCL15, sLCL15, PpkL15, PpkU15, Pp15 = pp.processCap(tMean15, tSDev15, smp_Sz)
                    else:
                        tMean15 = (delta9.mean() + deltaA.mean() + deltaB.mean() + deltaC.mean()) / 4
                        tSDev15 = (delta9.std() + deltaA.std() + deltaB.std() + deltaC.std()) / 4
                        xUSL15, xLSL15, xUCL15, xLCL15, sUCL15, sLCL15, PpkL15, PpkU15, Pp15 = pp.processCap(tMean15, tSDev15, smp_Sz)
                else:
                    tMean15 = (delta9.mean() + deltaA.mean() + deltaB.mean() + deltaC.mean()) / 4
                    xUCL15, xLCL15, xUSL15, xLSL15, sUCL15, sLCL15 = hUCLd, hLCLd, hUSLd, hLSLd, dUCLd, dLCLd

                    tSDev15 = (delta9.std() + deltaA.std() + deltaB.std() + deltaC.std()) / 4
                    PpkL15, PpkU15, Pp15 = pp.hisCap(tMean15, tSDev15, xLSL15, xUSL15)
                    # print('\nUsing Historical MEAN:', tMean15)
                # Compute process capability for Ring 3 Data ----------------------------------------[]
                pkC = min(PpkL15, PpkU15)
                dtC.append(round(pkC, 4))
                # Free up some memory spaces -----
                if len(dtC) > 1:
                    del (dtC[:1])
                if DNVspecify:
                    lbl = '(TR)'
                else:
                    lbl = '(DT)'
                print('Head9-12 '+lbl+' Dev:', round(tSDev15, 4))
                print('USL/LSL '+lbl+': ', round(xUSL15, 4), round(xLSL15, 4))
                print('UCL/LCL '+lbl+': ', xUCL15, xLCL15)
                print('Head9-12 '+lbl+' Pp/Ppk:', round(Pp15, 4), '\t', dtC[-1])

            if R4:
                # Compute delta temperatures ----
                if DNVspecify:
                    deltaD = (R4TT[0]/R4ST[0])
                    deltaE = (R4TT[1]/R4ST[1])
                    deltaF = (R4TT[2]/R4ST[2])
                    deltaG = (R4TT[3]/R4ST[3])
                else:
                    deltaD = (R4ST[0] - R4TT[0])
                    deltaE = (R4ST[1] - R4TT[1])
                    deltaF = (R4ST[2] - R4TT[2])
                    deltaG = (R4ST[3] - R4TT[3])
                # Plot X-Axis data points --------
                im126.set_xdata(np.arange(db_freq))
                im127.set_xdata(np.arange(db_freq))
                im128.set_xdata(np.arange(db_freq))
                im129.set_xdata(np.arange(db_freq))
                im130.set_xdata(np.arange(db_freq))
                im131.set_xdata(np.arange(db_freq))
                im132.set_xdata(np.arange(db_freq))
                im133.set_xdata(np.arange(db_freq))
                if optm2:
                    # Plot Y-Axis data points for XBar ---
                    im126.set_ydata(deltaD.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im127.set_ydata(deltaE.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im128.set_ydata(deltaF.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    im129.set_ydata(deltaG.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev ----------------------------------------
                    im130.set_ydata(deltaD.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im131.set_ydata(deltaE.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im132.set_ydata(deltaF.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    im133.set_ydata(deltaG.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                    # Calculate process capability for Ring 2 ---------
                else:
                    # Plot Y-Axis data points for XBar ---
                    im126.set_ydata(deltaD.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im127.set_ydata(deltaE.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im128.set_ydata(deltaF.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    im129.set_ydata(deltaG.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                    # Plot Y-Axis data points for StdDev ---------------------------------------
                    im130.set_ydata(deltaD.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im131.set_ydata(deltaE.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im132.set_ydata(deltaF.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                    im133.set_ydata(deltaG.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                # Calculate process capability for Ring 2 --------------------------------------
                if not uhl:
                    if len(autoGpMeanD) == smp_Sz:
                        # filter out potential null and zero values from subgroup mean deductions ----[]
                        if deltaD.any() or deltaE.any() or deltaF.any() or deltaG.any():
                            pass
                        else:
                            tMean16 = (deltaD.mean() + deltaE.mean() + deltaF.mean() + deltaG.mean()) / 4
                            tSDev16 = (deltaD.std() + deltaE.std() + deltaF.std() + deltaG.std()) / 4

                        if len(autoUSLB) != 0:
                            # Compute process capability using New Set limits -----------------------[]
                            sUCL16, sLCL16, xUSL16, xLSL16, xUCL16, xLCL16 = autosUCLD[0], autosLCLD[0], autoUSLD[0], \
                                autoLSLD[0], autoUCLD[0], autoLCLD[0]
                            PpkL16, PpkU16, Pp16 = pp.hisCap(tMean16, tSDev16, xLSL16, xUSL16)
                            # print('\nUsing the Process MEAN:', tMean16)
                        else:
                            xUSL16, xLSL16, xUCL16, xLCL16, sUCL16, sLCL16, PpkL16, PpkU16, Pp16 = pp.processCap(tMean16, tSDev16,
                                                                                                        smp_Sz)
                    else:
                        tMean16 = (deltaD.mean() + deltaE.mean() + deltaF.mean() + deltaG.mean()) / 4
                        tSDev16 = (deltaD.std() + deltaE.std() + deltaF.std() + deltaG.std()) / 4
                        xUSL16, xLSL16, xUCL16, xLCL16, sUCL16, sLCL16, PpkL16, PpkU16, Pp16 = pp.processCap(tMean16, tSDev16, smp_Sz)
                        # print('\nUsing Ring 4 MEAN:', tMean16)
                else:
                    tMean16 = (deltaD.mean() + deltaE.mean() + deltaF.mean() + deltaG.mean()) / 4
                    xUCL16, xLCL16, xUSL16, xLSL16, sUCL16, sLCL16 = hUCLd, hLCLd, hUSLd, hLSLd, dUCLd, dLCLd

                    tSDev16 = (deltaD.std() + deltaE.std() + deltaF.std() + deltaG.std()) / 4
                    PpkL16, PpkU16, Pp16 = pp.hisCap(tMean16, tSDev16, xLSL16, xUSL16)
                    # print('\nUsing Historical MEAN:', tMean16)
                # Compute process capability for Ring 4 Data ----------------------------------------[]
                pkD = min(PpkL16, PpkU16)
                dtD.append(round(pkD, 4))
                # Free up some memory spaces -----
                if len(dtD) > 1:
                    del (dtD[:1])
                if DNVspecify:
                    lbl = '(TR)'
                else:
                    lbl = '(DT)'
                print('Head13-16 '+lbl+' Dev:', round(tSDev16, 4))
                print('USL/LSL '+lbl+': ', round(xUSL16, 4), round(xLSL16, 4))
                print('UCL/LCL '+lbl+': ', xUCL16, xLCL16)
                print('Head13-16 '+lbl+' Pp/Ppk:', round(Pp16, 4), '\t', dtD[-1])

            # ----- Calculate Process Data ----------------------------------------------------------[]
            # Only account for active rings with process data ----
            if not uhl:
                if len(autoGpMeanD) <= smp_Sz:
                    if tMean13 != 0 or tMean14 != 0 or tMean15 != 0 or tMean16 != 0:
                        TMean4 = np.array([tMean13, tMean14, tMean15, tMean16])
                        TMean4 = (TMean4[np.nonzero(TMean4)]).mean()            # compute for the mean of mean
                        TSdev4 = np.array([tSDev13, tSDev14, tSDev15, tSDev16])
                        TSdev4 = (TSdev4[np.nonzero(TSdev4)]).mean()

                    # Sample and Compute the subgroup Process Mean and subgroup Deviation
                    elif np.isnan(TMean4):
                        TMean4 = 0.0
                        TSdev4 = 0.68 * 2   # i.e 1sigma DOF
                    else:
                        TMean4 = 0.0
                        TSdev4 = 0.68 * 2   # i.e 1sigma DOF

                    sMeand = 0
                    xMeand = 0                      # Turn off center line until limits lock
                    autoGpMeanD.append(TMean4)      # Sample subgroup Mean for Center Line auto-derivative
                    autoGpDevD.append(TSdev4)       # Sample subgroup Mean for Center Line auto-derivative
                    xUSLd, xLSLd, xUCLd, xLCLd, sUCLd, sLCLd, PpkLd, PpkUd, PpRd = pp.processCap(TMean4, TSdev4, smp_Sz)

                else:
                    TMean4 = sum(autoGpMeanD) / len(autoGpMeanD)    # compute & keep new Mean for the subgroup
                    TSdev4 = sum(autoGpDevD) / len(autoGpDevD)      # Compute average dev for subgroup Center line
                    sMeand = 0
                    xMeand = 0                                      # Turn off center line until limits lock
                    if len(autoUSLB) < 2:
                        xUSLd, xLSLd, xUCLd, xLCLd, sUCLd, sLCLd, PpkLd, PpkUd, PpRd = pp.processCap(TMean4, TSdev4,
                                                                                                     smp_Sz)
                        sClineD.append(TSdev4)
                        autoUSLD.append(xUSLd)
                        autoLSLD.append(xLSLd)
                        autoUCLD.append(xUCLd)
                        autoLCLD.append(xLCLd)
                        autosUCLD.append(sUCLd)
                        autosLCLD.append(sLCLd)
                    else:
                        # Test static arrays for valid values --------------------[]
                        xUSLd = autoUSLD[0]
                        xLSLd = autoLSLD[0]
                        xUCLd = autoUCLD[0]
                        xLCLd = autoLCLD[0]
                        sUCLd = autosUCLD[0]
                        sLCLd = autosLCLD[0]
                        sMeand = sClineD[0]
                        xMeand = TMean4                                         # Turn off center line until limits lock
                        TSdev4 = np.array([tSDev5, tSDev6, tSDev7, tSDev8])     # Allow subgroup DOF on StdDev
                        TSdev4 = (TSdev4[np.nonzero(TSdev4)]).mean()            # total heads in the process
                        PpkLd, PpkUd, PpRd = pp.hisCap(TMean4, TSdev4, xLSLd, xUSLd)
            else:
                xMeand = HistMeanD                                              # X Bar Center Line
                sMeand = HistSDevD                                              # S Bar Center Line
                proM4 = (tMean5, tMean6, tMean7, tMean8)
                if sum(proM4) != 0:
                    TMean4 = np.array([tMean5, tMean6, tMean7, tMean8])         # Allow subgroup DOF on StdDev
                    TMean4 = (TMean4[np.nonzero(TMean4)]).mean()                # Allow deviation on its DOF
                else:
                    TMean4 = 0
                proMx = (tSDev5, tSDev6, tSDev7, tSDev8)
                if sum(proMx) != 0:
                    TSdev4 = np.array([tSDev5, tSDev6, tSDev7, tSDev8])             # Allow subgroup DOF on StdDev
                    TSdev4 = (TSdev4[np.nonzero(TSdev4)]).mean()                    # Allow deviation on its DOF
                else:
                    TSdev4 = 0.68 * 2
                xUSLd, xLSLd, xUCLd, xLCLd, sUCLd, sLCLd = hUSLd, hLSLd, hUCLd, hLCLd, dUCLd, dLCLd
                PpkLd, PpkUd, PpRd = pp.hisCap(TMean4, TSdev4, xLSLd, xUSLd)
            # Compute process capability for Process Data -------------------------------------------[]
            procD = min(PpkLd, PpkUd)               # Average Ppk per available rings combinations
            Ppkd.append(round(procD, 4))            # copy 2sig. result into a dynamic array
            # Free up some memory spaces -----
            if len(Ppkd) > 1:
                del (Ppkd[:1])
            print('-'*55)
            if DNVspecify:
                lbl = '(TR)'
            else:
                lbl = '(DT)'
            print('Process ' + lbl + ' Mean/SDev:', round(TMean4,4), round(TSdev4, 4))
            print('Process ' + lbl + ' UCL/LCL:', xUCLd, xLCLd)
            print('Process ' + lbl + ' USL/LSL:', round(xUSLd, 4), round(xLSLd, 4))
            print('Process ' + lbl + ' Pp/Ppk:', round(PpRd, 4), '\t', Ppkd[-1])
            print('-' * 55)

        # -----------------------------------------------------------------------------------------------------------[]
        if GapMeasurement:
            if not UsePLC_DBS:  # this applies to realtime/offline play modes ---------------[]
                # Define dataframe columns identities ---------------------------------------[]
                colum = ['IDX', 'TimeStamp', 'CurrentLayer', 'GapSampleCentre', 'PipePosition',
                         'GapAfterGaugeA1(mm)', 'GapAfterGaugeA2(mm)', 'GapAfterGaugeA3(mm)',
                         'GapAfterGaugeA4(mm)', 'GapAfterGaugeB1(mm)', 'GapAfterGaugeB2(mm)',
                         'GapAfterGaugeB3(mm)', 'GapAfterGaugeB4(mm)']

                df2 = pd.DataFrame(dX2, columns=colum)              # porte sql data into dataframe
                playrn = list(df2['CurrentLayer'].tail(1))          # perform filtering
                pipPos = list(df2['PipePosition'].tail(1))          # perform filtering

                # perform filtering -----------------#
                if len(playrn) != 0:
                    HTlayr.append(playrn[0])                        # report current layer to display array
                    EPpos.append(round(pipPos[0], 2))               # report current pipe pos to display array
                else:
                    HTlayr.append(1)
                    EPpos.append(0)
                # print('\nPipe Pos', EPpos)
                # -----------------------------------#
                # Load available Control variables on the df1's RingCombo -------------------------[]
                tGap1 = df2['GapAfterGaugeA1(mm)']
                tGap2 = df2['GapAfterGaugeA2(mm)']
                tGap3 = df2['GapAfterGaugeA3(mm)']
                tGap4 = df2['GapAfterGaugeA4(mm)']
                tGap5 = df2['GapAfterGaugeA1(mm)']
                tGap6 = df2['GapAfterGaugeA2(mm)']
                tGap7 = df2['GapAfterGaugeA3(mm)']
                tGap8 = df2['GapAfterGaugeA4(mm)']
                # ------------------------------#
            else:                               # this applies to realtime play mode only ---------[]
                playrn = tlpos[1]               # Real-time pipe layer reached
                pipPos = tlpos[0]               # real-time pipe position
                tGap1 = TG1[0]
                tGap2 = TG1[1]
                tGap3 = TG2[0]
                tGap4 = TG2[1]
                tGap5 = TG3[0]
                tGap6 = TG3[1]
                tGap7 = TG4[0]
                tGap8 = TG1[1]
                HTlayr.append(playrn)           # report current layer to display array
                EPpos.append(round(pipPos, 2))  # report current pipe pos to display array

            # Plot X-Axis data points --------
            im134.set_xdata(np.arange(db_freq))
            im135.set_xdata(np.arange(db_freq))
            im136.set_xdata(np.arange(db_freq))
            im137.set_xdata(np.arange(db_freq))

            im138.set_xdata(np.arange(db_freq))
            im139.set_xdata(np.arange(db_freq))
            im140.set_xdata(np.arange(db_freq))
            im141.set_xdata(np.arange(db_freq))

            im142.set_xdata(np.arange(db_freq))
            im143.set_xdata(np.arange(db_freq))
            im144.set_xdata(np.arange(db_freq))
            im145.set_xdata(np.arange(db_freq))

            im146.set_xdata(np.arange(db_freq))
            im147.set_xdata(np.arange(db_freq))
            im148.set_xdata(np.arange(db_freq))
            im149.set_xdata(np.arange(db_freq))
            # Plot Y-Axis data points for XBar
            if optm2:
                im134.set_ydata(tGap1.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im135.set_ydata(tGap2.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                # Plot Y-Axis data points for StdDev ---
                im136.set_ydata(tGap1.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im137.set_ydata(tGap2.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])

                # Plot Y-Axis data points for XBar ---
                im138.set_ydata(tGap3.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im139.set_ydata(tGap4.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                # Plot Y-Axis data points for StdDev ---
                im140.set_ydata(tGap3.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im141.set_ydata(tGap4.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])

                # Plot Y-Axis data points for XBar ---
                im142.set_ydata(tGap5.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im143.set_ydata(tGap6.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                # Plot Y-Axis data points for StdDev ---
                im144.set_ydata(tGap5.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im145.set_ydata(tGap6.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])

                # Plot Y-Axis data points for XBar ---
                im146.set_ydata(tGap7.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im147.set_ydata(tGap8.rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                # Plot Y-Axis data points for StdDev ---
                im148.set_ydata(tGap7.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im149.set_ydata(tGap8.rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
            else:
                im134.set_ydata(tGap1.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                im135.set_ydata(tGap2.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                # Plot Y-Axis data points for StdDev ---
                im136.set_ydata(tGap1.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                im137.set_ydata(tGap2.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])

                # Plot Y-Axis data points for XBar ---
                im138.set_ydata(tGap3.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                im139.set_ydata(tGap4.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                # Plot Y-Axis data points for StdDev ---
                im140.set_ydata(tGap3.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                im141.set_ydata(tGap4.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])

                # Plot Y-Axis data points for XBar ---
                im142.set_ydata(tGap5.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                im143.set_ydata(tGap6.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                # Plot Y-Axis data points for StdDev ---
                im144.set_ydata(tGap5.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                im145.set_ydata(tGap6.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])

                # Plot Y-Axis data points for XBar ---
                im146.set_ydata(tGap7.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                im147.set_ydata(tGap8.rolling(window=smp_Sz, step=smp_St).mean()[0:db_freq])
                # Plot Y-Axis data points for StdDev ---
                im148.set_ydata(tGap7.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])
                im149.set_ydata(tGap8.rolling(window=smp_Sz, step=smp_St).std()[0:db_freq])

            if not uhl:
                if len(autoGpMeanE) <= smp_Sz:
                    TMean5 = (tGap1.mean() + tGap2.mean() + tGap3.mean() + tGap4.mean() + tGap5.mean() +
                             tGap6.mean() + tGap7.mean() + tGap8.mean())/8
                    TSdev5 = (tGap1.std() + tGap2.std() + tGap3.std() + tGap4.std() + tGap5.std() +
                             tGap6.std() + tGap7.std() + tGap8.std())/8

                    if TMean5 != 0:
                        TMean5 = TMean5 / 8                 # Total ring mean data
                        TSdev5 = TSdev5 / 8                 # Total ring deviation
                    elif np.isnan(TMean5):
                        TMean5 = 0.0
                        TSdev5 = 0.68 * 2   # i.e 1sigma DOF
                    else:
                        TMean5 = 0.0
                        TSdev5 = 0.68 * 2   # i.e 1sigma DOF

                    sMeane = -5
                    xMeane = -5
                    autoGpMeanE.append(TMean5)
                    autoGpDevE.append(TSdev5)
                    xUSLe, xLSLe, xUCLe, xLCLe, sUCLe, sLCLe, PpkLe, PpkUe, PpRe = pp.processCap(TMean5, TSdev5, smp_Sz)

                else:
                    TMean5 = sum(autoGpMeanE) / len(autoGpMeanE)    # compute & keep new Mean for the subgroup
                    TSdev5 = sum(autoGpDevE) / len(autoGpDevE)
                    sMeane = -5      # Turn off mean line until limits lock (Above y_limits)
                    xMeane = -5      # Turn off mean line until limits lock
                    if len(autoUSLE) < 2:
                        xUSLe, xLSLe, xUCLe, xLCLe, sUCLe, sLCLe, PpkLe, PpkUe, PpRe = pp.processCap(TMean5, TSdev5,
                                                                                                     smp_Sz)
                        sClineE.append(TSdev5)
                        autoUSLE.append(xUSLe)
                        autoLSLE.append(xLSLe)
                        autoUCLE.append(xUCLe)
                        autoLCLE.append(xLCLe)
                        autosUCLE.append(sUCLe)
                        autosLCLE.append(sLCLe)
                    else:
                        # Test static arrays for valid values --------------------[]
                        xUSLe = autoUSLE[0]
                        xLSLe = autoLSLE[0]
                        xUCLe = autoUCLE[0]
                        xLCLe = autoLCLE[0]
                        sUCLe = autosUCLE[0]
                        sLCLe = autosLCLE[0]
                        sMeane = sClineE[0]  # sPlot center line
                        xMeane = TMean5
                        TSdev5 = (tGap1.std() + tGap2.std() + tGap3.std() + tGap4.std() + tGap5.std() + tGap6.std() + tGap7.std() + tGap8.std()) / 8
                        # print('\nTAPE Gap xMetrics - Mean/CL/USL/LSL:', TMean4, xMeand,  xUSLd, xLSLd)
                        # print('TAPE Gap sMetrics - Mean/CL/UCL/LCL:', TSdev4, sMeand, sUCLd, sLCLd)
                        PpkLe, PpkUe, PpRe = pp.hisCap(TMean5, TSdev5, xLSLe, xUSLe)

            else:
                xMeane = HistMeanE
                sMeane = HistSDevE
                TMean5 = (tGap1.mean() + tGap2.mean() + tGap3.mean() + tGap4.mean() + tGap5.mean() +
                          tGap6.mean() + tGap7.mean() + tGap8.mean()) / 8
                TSdev5 = (tGap1.std() + tGap2.std() + tGap3.std() + tGap4.std() + tGap5.std() +
                          tGap6.std() + tGap7.std() + tGap8.std()) / 8

                xUSLe, xLSLe, xUCLe, xLCLe, sUCLe, sLCLe = hUSLe, hLSLe, hUCLe, hLCLe, dUCLe, dLCLe
                PpkLe, PpkUe, PpRe = pp.hisCap(TMean5, TSdev5, xLSLe, xUSLe)
            # Compute process capability for Ring 1 Data --------------------------------------------[]
            procE = min(PpkLe, PpkUe)                           # Average Ppk per available rings combinations
            if procE == 0 or procE == 'inf':
                Ppke.append('Inf')
            else:
                Ppke.append(round(procE, 4))                    # insert current process values into axes title
            # Free up some memory spaces -----
            if len(Ppke) > 1:
                del (Ppke[:1])
            print('-' * 55)
            print('\nProcess (TG) Mean/SDev:', round(TMean5, 4), 'SDev:', round(TSdev5, 4))
            print('Process (TG) UCL/LCL:', xUCLe, xLCLe)
            print('Process (TG) USL/LSL:', round(xUSLe, 4), round(xLSLe, 4))
            print('Process (TG) Pp/Ppk:', round(PpRe, 4), '\t', Ppke[-1])
            print('-' * 55)

        # Capture statistical values from each chosen processes -------------------------------------[]
        WON = processWON[0]     # provide WON details
        # print('\nWork Order Number:', WON)
        # ----------------------#

        if RollerPressure:
            xUSL, xLSL, xUCL, xLCL, sUCL, sLCL = xUSLa, xLSLa, xUCLa, xLCLa, sUCLa, sLCLa
            PpR, PpkL, PpkU, Pp1, Pp2, Pp3, Pp4, PpkL1, PpkL2, PpkL3, PpkL4, PpkU1, PpkU2, PpkU3, PpkU4 = \
                PpRa, PpkLa, PpkUa, Pp1, Pp2, Pp3, Pp4, PpkL1, PpkL2, PpkL3, PpkL4, PpkU1, PpkU2, PpkU3, PpkU4
            TMean = xMeana
            TDev = sMeana
            # obtain values after 40 cycle to avoid ramp-up regions ----
            if db_freq == 40 and not uhl:
                autoLimits(xMeana, sMeana, 0, 0, 0, 0, 0, 0, 0, 0)

        elif Manu_TapeSpeed:
            xUSL, xLSL, xUCL, xLCL, sUCL, sLCL = xUSLb, xLSLb, xUCLb, xLCLb, sUCLb, sLCLb
            PpR, PpkL, PpkU, Pp1, Pp2, Pp3, Pp4, PpkL1, PpkL2, PpkL3, PpkL4, PpkU1, PpkU2, PpkU3, PpkU4 = \
            PpRb, PpkLb, PpkUb, Pp5, Pp6, Pp7, Pp8, PpkL5, PpkL6, PpkL7, PpkL8, PpkU5, PpkU6, PpkU7, PpkU8
            TMean = xMeanb
            TDev = sMeanb
            if db_freq == 40 and not uhl:
                autoLimits(0, 0, xMeanb, sMeanb, 0, 0,0, 0, 0, 0)

        elif TapeTemperatur:
            xUSL, xLSL, xUCL, xLCL, sUCL, sLCL = xUSLc, xLSLc, xUCLc, xLCLc, sUCLc, sLCLc
            PpR, PpkL, PpkU, Pp1, Pp2, Pp3, Pp4, PpkL1, PpkL2, PpkL3, PpkL4, PpkU1, PpkU2, PpkU3, PpkU4 = \
                PpRc, PpkLc, PpkUc, Pp9, Pp10, Pp11, Pp12, PpkL9, PpkL10, PpkL11, PpkL12, PpkU9, PpkU10, PpkU11, PpkU12
            TMean = xMeanc
            TDev = sMeanc
            if db_freq == 40 and not uhl:
                autoLimits(0, 0,  0, 0, xMeanc, sMeanc,0, 0, 0, 0)

        elif TSub_TempRatio:
            xUSL, xLSL, xUCL, xLCL, sUCL, sLCL = xUSLd, xLSLd, xUCLd, xLCLd, sUCLd, sLCLd
            PpR, PpkL, PpkU, Pp1, Pp2, Pp3, Pp4, PpkL1, PpkL2, PpkL3, PpkL4, PpkU1, PpkU2, PpkU3, PpkU4 = \
                PpRd, PpkLd, PpkUd, Pp13, Pp14, Pp15, Pp16, PpkL13, PpkL14, PpkL15, PpkL16, PpkU13, PpkU14, PpkU15, PpkU16
            TMean = xMeand
            TDev = sMeand
            if db_freq == 40 and not uhl:
                autoLimits(0, 0, 0, 0, 0, 0, xMeand, sMeand,0, 0)

        elif GapMeasurement:
            xUSL, xLSL, xUCL, xLCL, sUCL, sLCL = xUSLe, xLSLe, xUCLe, xLCLe, sUCLe, sLCLe
            PpR, PpkL, PpkU = PpRe, PpkLe, PpkUe
            TMean = xMeane
            TDev = sMeane
            if db_freq == 40 and not uhl:
                autoLimits(0, 0, 0, 0, 0, 0, xMeane, sMeane, 0, 0)

        # Define mean line for all plotted variables in Ring One ------------------------------------[G1]
        if DNVspecify:
            if asp and monitorParamLP:
                # Define Legend's Attributes  ----
                ax.legend(loc='upper left', title='Aggregated, XBar Plot')
                ax.grid(color="0.5", linestyle='-', linewidth=0.5)
                monLPx = HistMeanF  # XBar Mean Plot
                ax.axhline(y=monLPx, color="red", linestyle="--", linewidth=0.8)
                ax.axhspan(hLCLf, hUCLf, facecolor='#F9C0FD', edgecolor='#F9C0FD')          # 3 Sigma span (Purple)
                ax.axhspan(hUCLf, hUSLf, facecolor='#8d8794', edgecolor='#8d8794')          # grey area
                ax.axhspan(hLSLf, hLCLf, facecolor='#8d8794', edgecolor='#8d8794')
                # ----------------------
                # Define Legend's Attributes  ----
                axa.legend(loc='upper right', title='Aggregated, SDev Plot')
                axa.grid(color="0.5", linestyle='-', linewidth=0.5)
                monLPs = HistSDevF    # S Mean Plot
                axa.axhline(y=monLPs, color="blue", linestyle="--", linewidth=0.8)
                axa.axhspan(dLCLf, dUCLf, facecolor='#F9C0FD', edgecolor='#F9C0FD')         # 1 Sigma Span
                axa.axhspan(dUCLf, sBar_maxLP, facecolor='#CCCCFF', edgecolor='#CCCCFF')    # 1 Sigma above the Mean
                axa.axhspan(sBar_minLP, dLCLf, facecolor='#CCCCFF', edgecolor='#CCCCFF')
            elif asp and monitorParamLA:
                # Define Legend's Attributes  ----
                ax.legend(loc='upper left', title='Rings Aggregated Values')
                ax.grid(color="0.5", linestyle='-', linewidth=0.5)
                monLAx = HistMeanG
                ax.axhline(y=monLAx, color="red", linestyle="--", linewidth=0.8)
                ax.axhspan(hLCLg, hUCLg, facecolor='#A9EF91', edgecolor='#A9EF91')
                ax.axhspan(hUCLg, hUSLg, facecolor='#8d8794', edgecolor='#8d8794')          # grey area
                ax.axhspan(hLSLg, hLCLg, facecolor='#8d8794', edgecolor='#8d8794')
                # ----------------------
                # Define Legend's Attributes  ----
                axa.legend(loc='upper right', title='Aggregated, SDev Plot')
                axa.grid(color="0.5", linestyle='-', linewidth=0.5)
                monLAs = HistSDevG                                                          # S Mean Plot
                axa.axhline(y=monLAs, color="blue", linestyle="--", linewidth=0.8)
                axa.axhspan(dLCLg, dUCLg, facecolor='#A9EF91', edgecolor='#A9EF91')         # Sigma Span
                axa.axhspan(dUCLg, sBar_maxLA, facecolor='#98AFF9', edgecolor='#98AFF9')    # 1 Sigma above the Mean
                axa.axhspan(sBar_minLA, dLCLg, facecolor='#98AFF9', edgecolor='#98AFF9')

            elif not asp:
                if monitorParamLP and monitorParamLA:
                    monLPx = HistMeanF                                                          # XBar Mean Plot
                    ax.axhline(y=monLPx, color="red", linestyle="--", linewidth=0.8)
                    # Define Legend's Attributes  ----
                    ax.legend(loc='upper left', title='Rings Aggregated Values')
                    ax.grid(color="0.5", linestyle='-', linewidth=0.5)
                    # ------------------------------------
                    monLAx = HistMeanG                                                          # XBar Mean Plot
                    axa.axhline(y=monLAx, color="red", linestyle="--", linewidth=0.8)
                    # Define Legend's Attributes  ----
                    axa.legend(loc='upper right', title='Rings Aggregated Values')
                    axa.grid(color="0.5", linestyle='-', linewidth=0.5)
                elif monitorParamLP:
                    monLPx = HistMeanF  # XBar Mean Plot
                    ax.axhline(y=monLPx, color="red", linestyle="--", linewidth=0.8)
                    # Define Legend's Attributes  ----
                    ax.legend(loc='upper left', title='Rings Aggregated Values')
                    ax.grid(color="0.5", linestyle='-', linewidth=0.5)
                    axa.text(12.98, 0.490, 'Data Feed disabled..')
                else: # monitorParamLA
                    monLAx = HistMeanG  # XBar Mean Plot
                    ax.axhline(y=monLAx, color="red", linestyle="--", linewidth=0.8)
                    # Define Legend's Attributes  ----
                    ax.legend(loc='upper right', title='Rings Aggregated Values')
                    ax.grid(color="0.5", linestyle='-', linewidth=0.5)
                    axa.text(12.98, 0.490, 'Data Feed disabled..')
        else:
            # Plot a fixed Mean line values for TFMC Params ------------------------[]
            if monitorParamLP:
                monLPx = HistMeanF
                ax.axhline(y=monLPx, color="blue", linestyle="--", linewidth=0.8)
            else:
                monLAx = HistMeanG
                ax.axhline(y=monLAx, color="blue", linestyle="--", linewidth=0.8)
            ax.legend(loc='upper left', title='Value Curve: Rings Aggregates')
            ax.grid(color="0.5", linestyle='-', linewidth=0.5)
            ax.set_ylabel("Sample Data - Production Parameter")

        # Define mean line for all plotted variables in Ring One ------------------------------------[G1]
        if VarPerHeadA:
            # Plot a fixed Mean line --------------------------------[]
            ax2.axhline(y=TMean, color="green", linestyle="--", linewidth=0.8)
            # Sigma3: Span line -------------------------------------[]
            ax2.axhspan(xLCL, xUCL, facecolor='#A9EF91', edgecolor='#A9EF91')      # Light green: Span
            ax2.axhspan(xUCL, xUSL, facecolor='#8d8794', edgecolor='#8d8794')      # Grey: above mean line
            ax2.axhspan(xLSL, xLCL, facecolor='#8d8794', edgecolor='#8d8794')      # Grey: below mean line

            # clean up when Mean line changes ---
            # window_y2min, window_y2max = window_y2minA, window_y2maxA
            ax2.axhspan(xUSL, window_y2maxA, facecolor='#FFFFFF', edgecolor='#FFFFFF')  # White
            ax2.axhspan(window_y2minA, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')  # WHit

            # 1 Sigma line -------------------------------------------------------------------
            ax6.axhline(y=TDev, color="green", linestyle="--", linewidth=0.8)
            ax6.axhspan(sLCL, sUCL, facecolor='#A9EF91', edgecolor='#A9EF91')             # Std Dev Span
            ax6.axhspan(window_y3min, sLCL, facecolor='#98AFF9', edgecolor='#98AFF9')     # 1Sigma above Mean
            ax6.axhspan(sUCL, window_y3max, facecolor='#98AFF9', edgecolor='#98AFF9')     # 1Sigma below Mean
            # -------------------------------------------------------------------------------------
            ax3.cla()
            ax3.text(0.466, 0.945, 'Process Performance Feed', fontsize=16, fontweight='bold',
                     ha='center', va='center', transform=ax3.transAxes)
            # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
            rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
            rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
            ax3.add_patch(rect1)
            ax3.add_patch(rect2)
            # ------- Process Performance Pp (the spread)---------------------
            ax3.text(0.145, 0.804, plabel, fontsize=12, fontweight='bold', ha='center', transform=ax3.transAxes)
            ax3.text(0.328, 0.658, round(PpR, 3), fontsize=28, fontweight='bold', ha='center', transform=ax3.transAxes)

            ax3.text(0.650, 0.820, 'Ring '+plabel+' Data', fontsize=14, ha='left', transform=ax3.transAxes)
            if not GapMeasurement:
                ax3.text(0.755, 0.780, round(Pp1, 2), fontsize=12, ha='center', transform=ax3.transAxes)
                ax3.text(0.755, 0.702, round(Pp2, 2), fontsize=12, ha='center', transform=ax3.transAxes)
                ax3.text(0.755, 0.624, round(Pp3, 2), fontsize=12, ha='center', transform=ax3.transAxes)
                ax3.text(0.755, 0.546, round(Pp4, 2), fontsize=12, ha='center', transform=ax3.transAxes)
            else:
                ax3.text(0.755, 0.780, 'NA', fontsize=12, ha='center', transform=ax3.transAxes)
                ax3.text(0.755, 0.702, 'NA', fontsize=12, ha='center', transform=ax3.transAxes)
                ax3.text(0.755, 0.624, 'NA', fontsize=12, ha='center', transform=ax3.transAxes)
                ax3.text(0.755, 0.546, 'NA', fontsize=12, ha='center', transform=ax3.transAxes)
            # ------- Process Performance Ppk (Performance)---------------------
            ax3.text(0.145, 0.403, PPerf, fontsize=12, fontweight='bold', ha='center', transform=ax3.transAxes)
            ax3.text(0.328, 0.282, round(min(PpkL, PpkU), 3), fontsize=28, fontweight='bold', ha='center', transform=ax3.transAxes)
            ax3.text(0.640, 0.420, 'Ring '+PPerf+' Data', fontsize=14, ha='left', transform=ax3.transAxes)

            if not GapMeasurement:
                ax3.text(0.755, 0.380, round(min(PpkL1, PpkU1), 2), fontsize=12, ha='center', transform=ax3.transAxes)
                ax3.text(0.755, 0.302, round(min(PpkL2, PpkU2), 2), fontsize=12, ha='center', transform=ax3.transAxes)
                ax3.text(0.755, 0.224, round(min(PpkL3, PpkU3), 2), fontsize=12, ha='center', transform=ax3.transAxes)
                ax3.text(0.755, 0.146, round(min(PpkL4, PpkU4), 2), fontsize=12, ha='center', transform=ax3.transAxes)
            else:
                ax3.text(0.755, 0.380, 'NA', fontsize=12, ha='center', transform=ax3.transAxes)
                ax3.text(0.755, 0.302, 'NA', fontsize=12, ha='center', transform=ax3.transAxes)
                ax3.text(0.755, 0.224, 'NA', fontsize=12, ha='center', transform=ax3.transAxes)
                ax3.text(0.755, 0.146, 'NA', fontsize=12, ha='center', transform=ax3.transAxes)
            if RetroReplay:
                if len(OTlayr) > 2 and len(EPpos) > 2:
                    layr = OTlayr[-1]       # playrn
                    pPos = EPpos[-1]        # pipPos  TODO: Integrate Pipe position values from SQL table when ready
                else:
                    layr = 0
                    pPos = 0
                ax3.text(0.086, 0.070, 'Current Layer#:', fontsize=14, ha='left', transform=ax3.transAxes)
                ax3.text(0.364, 0.070, layr, fontsize=14, ha='left', transform=ax3.transAxes)
                ax3.text(0.464, 0.070, 'Status: Process in progress...', fontsize=14, ha='left', transform=ax3.transAxes)
                # ax3.text(0.765, 0.070, pPos, fontsize=14, ha='left', transform=ax3.transAxes)

        elif VarPerHeadB:
            if R1 or GapMeasurement:
                ax2.grid(color="0.5", linestyle='-', linewidth=0.5)
                ax2.legend(loc='upper left')
                ax6.grid(color="0.5", linestyle='-', linewidth=0.5)
                ax6.legend(loc='upper left')
                # Sigma 3 line (99.7% deviation) ------- times 3 above the mean value
                ax2.axhline(y=TMean, color="red", linestyle="--", linewidth=0.8)      # Plot a fixed Mean line
                ax2.axhspan(xLCL, xUCL, facecolor='#A9EF91', edgecolor='#A9EF91')     # Light Green

                # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
                ax2.axhspan(xUCL, xUSL, facecolor='#8d8794', edgecolor='#8d8794')     # grey area
                ax2.axhspan(xLSL, xLCL, facecolor='#8d8794', edgecolor='#8d8794')     # grey area
                # clean up when Mean line changes ---
                ax2.axhspan(xUSL, window_y2maxE, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                ax2.axhspan(window_y2minE, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')

                # SPlot 1 Sigma line -----------------------------------------------------------------
                ax6.axhline(y=TDev, color="red", linestyle="--", linewidth=0.8)
                ax6.axhspan(sLCL, sUCL, facecolor='#A9EF91', edgecolor='#A9EF91')             # Sigma Span
                ax6.axhspan(sUCL, window_y3max, facecolor='#98AFF9', edgecolor='#98AFF9')     # 1 Sigma above the Mean
                ax6.axhspan(window_y3min, sLCL, facecolor='#98AFF9', edgecolor='#98AFF9')     # 1 Sigma below the Mean
                # -------------------------------------------------------------------------------------
            else:
                ax2.text(84.95, 282.0, 'No DataFeed')
                ax6.text(84.95, 13.2, 'No DataFeed')

            if R2 or GapMeasurement:
                ax3.grid(color="0.5", linestyle='-', linewidth=0.5)
                ax3.legend(loc='upper left')
                ax7.grid(color="0.5", linestyle='-', linewidth=0.5)
                ax7.legend(loc='upper left')
                # Sigma 3 line (99.7% deviation) ------- times 3 above the mean value
                ax3.axhline(y=TMean, color="red", linestyle="--", linewidth=0.8)  # Plot a fixed Mean line
                ax3.axhspan(xLCL, xUCL, facecolor='#A9EF91', edgecolor='#A9EF91')  # TEak Green

                # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
                ax3.axhspan(xUCL, xUSL, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
                ax3.axhspan(xLSL, xLCL, facecolor='#8d8794', edgecolor='#8d8794')

                # clean up when Mean line changes ---
                ax3.axhspan(xUSL, window_y2maxE, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                ax3.axhspan(window_y2minE, xLSL,  facecolor='#FFFFFF', edgecolor='#FFFFFF')

                # 1 Sigma line ------------------------------------------------------------------------
                ax7.axhline(y=TDev, color="red", linestyle="--", linewidth=0.8)
                ax7.axhspan(sLCL, sUCL, facecolor='#A9EF91', edgecolor='#A9EF91')           # Sigma Span
                ax7.axhspan(sUCL, window_y3max, facecolor='#98AFF9', edgecolor='#98AFF9')   # 1 Sigma above the Mean
                ax7.axhspan(window_y3min, sLCL, facecolor='#98AFF9', edgecolor='#98AFF9')   # 1 Sigma below the Mean

                # -------------------------------------------------------------------------------------
            else:
                ax3.text(9.88, 282.0, 'No DataFeed')
                ax7.text(9.88, 13.2, 'No DataFeed')

            if R3 or GapMeasurement:
                ax4.grid(color="0.5", linestyle='-', linewidth=0.5)
                ax4.legend(loc='upper left')
                ax8.grid(color="0.5", linestyle='-', linewidth=0.5)
                ax8.legend(loc='upper left')
                # Sigma 3 line (99.7% deviation) ------- times 3 above the mean value
                ax4.axhline(y=TMean, color="red", linestyle="--", linewidth=0.8)  # Plot a fixed Mean line
                ax4.axhspan(xLCL, xUCL, facecolor='#A9EF91', edgecolor='#A9EF91')

                # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
                ax4.axhspan(xUCL, xUSL, facecolor='#8d8794', edgecolor='#8d8794')
                ax4.axhspan(xLSL, xLCL, facecolor='#8d8794', edgecolor='#8d8794')
                # clean up when Mean line changes ---
                ax4.axhspan(xUSL, window_y2maxE, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                ax4.axhspan(window_y2minE, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')

                # 1 Sigma line -----------------------------------------------------------------------
                ax8.axhline(y=TDev, color="red", linestyle="--", linewidth=0.8)
                ax8.axhspan(sLCL, sUCL, facecolor='#A9EF91', edgecolor='#A9EF91')             # Sigma Span
                ax8.axhspan(sUCL, window_y3max, facecolor='#98AFF9', edgecolor='#98AFF9')     # 1 Sigma above the Mean
                ax8.axhspan(window_y3min, sLCL, facecolor='#98AFF9', edgecolor='#98AFF9')     # 1 Sigma below the Mean
                # -------------------------------------------------------------------------------------
            else:
                ax4.text(9.27, 282.0, 'No DataFeed')
                ax8.text(9.27, 13.2, 'No DataFeed')

            if R4 or GapMeasurement:
                ax5.grid(color="0.5", linestyle='-', linewidth=0.5)
                ax5.legend(loc='upper left')
                ax9.grid(color="0.5", linestyle='-', linewidth=0.5)
                ax9.legend(loc='upper left')
                # Sigma 3 line (99.7% deviation) ------- times 3 above the mean value
                ax5.axhline(y=TMean, color="red", linestyle="--", linewidth=0.8)  # Plot a fixed Mean line
                ax5.axhspan(xLCL, xUCL, facecolor='#A9EF91', edgecolor='#A9EF91')

                # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
                ax5.axhspan(xUCL, xUSL, facecolor='#8d8794', edgecolor='#8d8794')
                ax5.axhspan(xLSL, xLCL, facecolor='#8d8794', edgecolor='#8d8794')
                # clean up when Mean line changes ---
                ax5.axhspan(xUSL, window_y2maxE, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                ax5.axhspan(window_y2minE, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')

                # 1 Sigma line ------------------------------------------------------------------------
                ax9.axhline(y=TDev, color="red", linestyle="--", linewidth=0.8)
                ax9.axhspan(sLCL, sUCL, facecolor='#A9EF91', edgecolor='#A9EF91')             # Sigma Span
                ax9.axhspan(sUCL, window_y3max, facecolor='#98AFF9', edgecolor='#98AFF9')     # 1 Sigma above the Mean
                ax9.axhspan(window_y3min, sLCL, facecolor='#98AFF9', edgecolor='#98AFF9')     # 1 Sigma below the Mean
                # -------------------------------------------------------------------------------------
            else:
                ax5.text(8.88, 282.0, 'No DataFeed')
                ax9.text(8.88, 13.2, 'No DataFeed')

        elif VariProcess:   # and not VarPerHeadB:
            if RollerPressure:
                if DNVspecify:
                    axs = ax2
                    axv = ax7
                else:
                    axs = ax2
                    axv = ax6
                # Plot a fixed Mean line --------------------------------------------[]
                axs.axhline(y=xMeana, color="green", linestyle="--", linewidth=0.8)
                # Sigma 3 line (99.7% deviation) ------- times 3 above the mean value
                axs.axhspan(xLCLa, xUCLa, facecolor='#A9EF91', edgecolor='#A9EF91')
                # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
                axs.axhspan(xUCLa, xUSLa, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
                axs.axhspan(xLSLa, xLCLa, facecolor='#8d8794', edgecolor='#8d8794')
                # clean up when Mean line changes -----------------------------------[]
                axs.axhspan(xUSLa, xUSLa, facecolor='#FFFFFF', edgecolor='#FFFFFF')  # YScale_maxRF
                axs.axhspan(xLSLa, xLSLa, facecolor='#FFFFFF', edgecolor='#FFFFFF')  # YScale_minRF

                # Plot Deviation Mean line ------------------------------------------[]
                axv.axhline(y=sMeana, color="green", linestyle="--", linewidth=0.8)
                # Plot Sigma 1 Span line --------------------------------------------[]
                axv.axhspan(sLCLa, sUCLa, facecolor='#A9EF91', edgecolor='#A9EF91')             # cornflowerblue
                axv.axhspan(sUCLa, sBar_maxRF, facecolor='#98AFF9', edgecolor='#98AFF9')       # 1 Sigma above the Mean
                axv.axhspan(sBar_minRF, sLCLa, facecolor='#98AFF9', edgecolor='#98AFF9')       # 1 Sigma below the Mean
                # ----------------------------------------------------------------------
            else:
                ax2.text(57.82, -0.15, 'No DataFeed')
                ax6.text(57.82, 0.02, 'No DataFeed')

            # -------------------------------------------------------------------------------------------[]
            if Manu_TapeSpeed and DNVspecify:
                # Plot a fixed Mean line --------------------------------------------
                ax3.axhline(y=xMeanb, color="green", linestyle="--", linewidth=0.8)
                # Sigma 3 line (99.7% deviation) ------- times 3 above the mean value
                ax3.axhspan(xLCLb, xUCLb, facecolor='#A9EF91', edgecolor='#A9EF91')

                # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
                ax3.axhspan(xUCLb, xUSLb, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
                ax3.axhspan(xLSLb, xLCLb, facecolor='#8d8794', edgecolor='#8d8794')
                # clean up when Mean line changes ---
                ax3.axhspan(xUSLb, xUSLb, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                ax3.axhspan(xLSLb, xLSLb, facecolor='#FFFFFF', edgecolor='#FFFFFF')

                # Plot Deviation Mean line -----------------------------------------
                ax8.axhline(y=sMeanb, color="green", linestyle="--", linewidth=0.8)
                # 1 Sigma line -----------------------------------------------------
                ax8.axhspan(sLCLb, sUCLb, facecolor='#A9EF91', edgecolor='#A9EF91')
                ax8.axhspan(sUCLb, sBar_maxTS, facecolor='#98AFF9', edgecolor='#98AFF9')
                ax8.axhspan(sBar_minTS, sLCLb, facecolor='#98AFF9', edgecolor='#98AFF9')
                # ------------------------------------------------------------------
            else:
                if DNVspecify:
                    ax3.text(9.88, -0.15, 'No DataFeed')
                    ax8.text(9.88, 0.02, 'No DataFeed')
            # ------------------------------------------------------------------------------------------[]
            if TapeTemperatur:
                if DNVspecify:
                    axQ = ax4
                    axR = ax9
                else:
                    axQ = ax3
                    axR = ax7
                # Plot a fixed Mean line -------------------------------------------
                axQ .axhline(y=xMeanc, color="green", linestyle="--", linewidth=0.8)
                # Sigma 3 line (99.7% deviation) ------- times 3 above the mean value
                axQ.axhspan(xLCLc, xUCLc, facecolor='#A9EF91', edgecolor='#A9EF91')

                # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
                axQ.axhspan(xUCLc, xUSLc, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
                axQ.axhspan(xLSLc, xLCLc, facecolor='#8d8794', edgecolor='#8d8794')
                # clean up when Mean line changes ---
                axQ.axhspan(xUSLc, xUSLc, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                axQ.axhspan(xLSLc, xLSLc, facecolor='#FFFFFF', edgecolor='#FFFFFF')

                # Plot Deviation Mean line -----------------------------------------
                axR.axhline(y=sMeanc, color="green", linestyle="--", linewidth=0.8)
                # 1 Sigma line -----------------------------------------------------
                axR.axhspan(sLCLc, sUCLc, facecolor='#A9EF91', edgecolor='#A9EF91')
                axR.axhspan(sUCLc, sBar_maxTT, facecolor='#98AFF9', edgecolor='#98AFF9')
                axR.axhspan(sBar_minTT, sLCLc, facecolor='#98AFF9', edgecolor='#98AFF9')
                # ------------------------------------------------------------------
            else:
                ax3.text(9.88, -0.15, 'No DataFeed')
                ax7.text(9.88, 0.02, 'No DataFeed')

            # ------------------------------------------------------------------------------------------[]
            if TSub_TempRatio:
                if DNVspecify:
                    acQ = ax5
                    acR = ax10
                else:
                    acQ = ax4
                    acR = ax8
                # Plot a fixed Mean line --------------------------------------------
                acQ.axhline(y=xMeand, color="green", linestyle="--", linewidth=0.8)
                # Sigma 3 line (99.7% deviation) ------- times 3 above the mean value
                acQ.axhspan(xLCLd, xUCLd, facecolor='#A9EF91', edgecolor='#A9EF91')

                # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
                acQ.axhspan(xUCLd, xUSLd, facecolor='#8d8794', edgecolor='#8d8794')
                acQ.axhspan(xLSLd, xLCLd, facecolor='#8d8794', edgecolor='#8d8794')
                # clean up when Mean line changes --- TODO -Solve alert limits
                acQ.axhspan(xUSLd, xUSLd, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                acQ.axhspan(xLSLd, xLSLd, facecolor='#FFFFFF', edgecolor='#FFFFFF')

                # Plot Deviation Mean line -----------------------------------------
                acR.axhline(y=sMeand, color="green", linestyle="--", linewidth=0.8)
                # 1 Sigma line -----------------------------------------------------
                acR.axhspan(sLCLd, sUCLd, facecolor='#A9EF91', edgecolor='#A9EF91')
                acR.axhspan(sUCLd, sBar_maxDT, facecolor='#98AFF9', edgecolor='#98AFF9')
                acR.axhspan(sBar_minDT, sLCLd, facecolor='#98AFF9', edgecolor='#98AFF9')
                # ------------------------------------------------------------------
            else:
                ax4.text(9.27, 0.44, 'No DataFeed')
                ax8.text(9.27, 0.012, 'No DataFeed')

            # -----------------------------------------------------------------------------------------[]
            if GapMeasurement:
                if DNVspecify:
                    xQ = ax6
                    xR = ax11
                else:
                    xQ = ax5
                    xR = ax9
                # Plot a fixed Mean line -----------------------------------------
                xQ.axhline(y=xMeane, color="green", linestyle="--", linewidth=0.8)
                # Sigma 3 line (99.7% deviation) ------- times 3 above the mean value
                xQ.axhspan(xLCLe, xUCLe, facecolor='#A9EF91', edgecolor='#A9EF91')

                # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
                xQ.axhspan(xUCLe, xUSLe, facecolor='#8d8794', edgecolor='#8d8794')
                xQ.axhspan(xLSLe, xLCLe, facecolor='#8d8794', edgecolor='#8d8794')
                # clean up when Mean line changes ---
                xQ.axhspan(xUSLe, xUSLe, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                xQ.axhspan(xLSLe, xLSLe, facecolor='#FFFFFF', edgecolor='#FFFFFF')

                # Plot Deviation Mean line ----------------------------------------
                xR.axhline(y=sMeane, color="green", linestyle="--", linewidth=0.8)
                # 1 Sigma line ----------------------------------------------------
                xR.axhspan(sLCLe, sUCLe, facecolor='#A9EF91', edgecolor='#A9EF91')
                xR.axhspan(sUCLe, sBar_maxTG, facecolor='#98AFF9', edgecolor='#98AFF9')
                xR.axhspan(sBar_minTG, sLCLe, facecolor='#98AFF9', edgecolor='#98AFF9')
                # -----------------------------------------------------------------
            else:
                ax5.text(8.88, 0.18, 'No DataFeed')
                ax9.text(8.88, 0.18, 'No DataFeed')

        # Setting up the parameters for moving windows Axes --------------------[]
        if db_freq > window_Xmax:
            ax.set_xlim(db_freq - window_Xmax, db_freq)
            if DNVspecify:
                axa.set_xlim(db_freq - window_Xmax, db_freq)

            if VarPerHeadA:
                # print('\nVariable per HeadA activated..')
                ax2.set_xlim(db_freq - window_Xmax, db_freq)
                ax6.set_xlim(db_freq - window_Xmax, db_freq)

            elif VarPerHeadB:   # -- VarPerHeadB or VariProcess
                # print('\nVariable per Ring Activated..')
                if R1:
                    ax2.set_xlim(db_freq - window_Xmax, db_freq)
                    ax6.set_xlim(db_freq - window_Xmax, db_freq)
                else:
                    ax2.set_xlim(0, window_Xmax)
                    ax6.set_xlim(0, window_Xmax)

                if R2:
                    ax3.set_xlim(db_freq - window_Xmax, db_freq)
                    ax7.set_xlim(db_freq - window_Xmax, db_freq)
                else:
                    ax3.set_xlim(0, window_Xmax)
                    ax7.set_xlim(0, window_Xmax)

                if R3:
                    ax4.set_xlim(db_freq - window_Xmax, db_freq)
                    ax8.set_xlim(db_freq - window_Xmax, db_freq)
                else:
                    ax4.set_xlim(0, window_Xmax)
                    ax8.set_xlim(0, window_Xmax)

                if R4:
                    ax5.set_xlim(db_freq - window_Xmax, db_freq)
                    ax9.set_xlim(db_freq - window_Xmax, db_freq)
                else:
                    ax5.set_xlim(0, window_Xmax)
                    ax9.set_xlim(0, window_Xmax)

            elif VariProcess:
                if DNVspecify:
                    ta = ax2
                    tb = ax7
                    tc = ax3
                    td = ax8
                    te = ax4
                    tf = ax9
                    tg = ax5
                    th = ax10
                    ti = ax6
                    tj = ax11
                else:
                    ta = ax2
                    tb = ax6
                    tc = 0
                    td = 0
                    te = ax3
                    tf = ax7
                    tg = ax4
                    th = ax8
                    ti = ax5
                    tj = ax9
                # -----------------------------------[A]
                if RollerPressure:
                    ta.set_xlim(db_freq - window_Xmax, db_freq)
                    tb.set_xlim(db_freq - window_Xmax, db_freq)
                else:
                    ta.set_xlim(0, window_Xmax)
                    tb.set_xlim(0, window_Xmax)
                # -----------------------------------[B]
                if Manu_TapeSpeed:
                    if DNVspecify:
                        tc.set_xlim(db_freq - window_Xmax, db_freq)
                        td.set_xlim(db_freq - window_Xmax, db_freq)
                    else:
                        tc.set_xlim(0, window_Xmax)
                        td.set_xlim(0, window_Xmax)
                else:
                    pass
                # -----------------------------------[C]
                if TapeTemperatur:
                    te.set_xlim(db_freq - window_Xmax, db_freq)
                    tf.set_xlim(db_freq - window_Xmax, db_freq)
                else:
                    te.set_xlim(0, window_Xmax)
                    tf.set_xlim(0, window_Xmax)
                # -----------------------------------[D]
                if TSub_TempRatio:
                    tg.set_xlim(db_freq - window_Xmax, db_freq)
                    th.set_xlim(db_freq - window_Xmax, db_freq)
                else:
                    tg.set_xlim(0, window_Xmax)
                    th.set_xlim(0, window_Xmax)
                # =---------------------------------[E]
                if GapMeasurement:
                    ti.set_xlim(db_freq - window_Xmax, db_freq)
                    tj.set_xlim(db_freq - window_Xmax, db_freq)
                else:
                    ti.set_xlim(0, window_Xmax)
                    tj.set_xlim(0, window_Xmax)

        else:
            ax.set_xlim(0, window_Xmax)

        # ---- Monitor Axis: Set properties  -------------------------------------------------------------------[]
        if DNVspecify:
            if VarPerHeadA or VarPerHeadB:
                axp = ax6
            else:
                axp = ax7
        else:
            axp = ax6
        # Insert model's identifier for XBar and SBar plots ----------------------------------[]
        ax2.grid(color="0.5", linestyle='-', linewidth=0.5)
        ax2.legend(loc='upper left')
        ax2.set_ylabel("Sample Mean " + "\n $ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $")
        # ----------------------
        axp.grid(color="0.5", linestyle='-', linewidth=0.5)
        axp.legend(loc='upper left')
        axp.set_ylabel("Sample SD " + "\n $ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$")

        # Evaluate the current Tape Layer if in RetroPlay Mode: -------------------------------[]
        if not UsePLC_DBS and GapMeasurement:
            lID = HTlayr[0]                                        # Static Values from SQL Tables
            pPos = EPpos[0]                                        # Pipe relative Position
        elif UsePLC_DBS:
            lID = tlpos[1]                                         # Layer No - Dynamic values from real-time PLC
            pPos = tlpos[0]                                        # Pipe Position - Dynamic values from PLC
        else:
            lID = 'N/A'                                            # Layer No - Dynamic values from real-time PLC
            pPos = 'N/A'
        # print('\nProcessing Current LAYER#:', lID, 'Pipe Pos:', pPos)
        # print('\nPipe Pos:', df2['PipePosition'][:20])

        # *************************************** VISUAL TRIGGER ALERTS ********************************[]
        # Capture trigg values above control/set limits --------------------------[]
        if not RetroReplay:                                         # Connect if realTime mode is activated
            import realTimePLCupdate as pq                          # Real Time PLC Query
            pq.recall_fromPLC_WON(WON)
        else:
            import realTPostSQLupdate as pq                         # Real Time SQL Query
            pq.recall_fromSQL_WON(WON)
        print('\nUpdating Statistical exceptions....')
        # =============================================================================================== #
        # Set Ring Head Triggers Using predefined edge colors --------------------------------[1-2]
        if RollerPressure:
            pID = 'RF'                                              # Required for FMEA report generation
            if VariProcess and DNVspecify:
                ax1T = ax2
                ax2T = ax2
                ax3T = ax2
                ax4T = ax2
                # ax5T = ax7
            elif VarPerHeadB and DNVspecify:
                ax1T = ax2
                ax2T = ax3
                ax3T = ax4
                ax4T = ax5
            elif VarPerHeadA and DNVspecify:
                ax1T = ax2
                ax2T = ax2
                ax3T = ax2
                ax4T = ax2
            # ----- on TFMC -----
            elif VarPerHeadA:
                ax1T = ax2
                ax2T = ax2
                ax3T = ax2
                ax4T = ax2
                ax5T = ax6
            elif VarPerHeadB:
                ax1T = ax2
                ax2T = ax3
                ax3T = ax4
                ax4T = ax5
            else:  # VariProcess on TFMC
                ax1T = ax2
                ax2T = ax2
                ax3T = ax2
                ax4T = ax2
                # ax5T = ax6

            # Set trip line for individual time-series plot -----------------------------------[R1]
            if R1:
                if VariProcess:
                    window_y2min, window_y2max = YScale_minRF, YScale_maxRF

                elif VarPerHeadB:  # Compute triger alert for perRing values
                    xUCL, xLCL, xUSL, xLSL = xUCL1, xLCL1, xUSL1, xLSL1
                    window_y2min, window_y2max = window_y2minE, window_y2maxE
                    TSdev1 = tSDev1
                else:
                    xUCL, xLCL, xUSL, xLSL = xUCL1, xLCL1, xUSL1, xLSL1
                    window_y2min, window_y2max = window_y2minA, window_y2maxA
                    TSdev1 = tSDev1

                Trig1 = (R1RF[0]).mean()      # Ring 1 Roller Pressure
                Trig2 = (R1RF[1]).mean()      # raRF[1].mean()
                Trig3 = (R1RF[2]).mean()
                Trig4 = (R1RF[3]).mean()
                # Provide visualisation: Evaluate trig values with Sigma Limits --------[]
                fcT1 = sx.trippWire(Trig1, xUCL, xLCL, xUSL, xLSL)  # Evaluate using process mean/dev values
                fcT2 = sx.trippWire(Trig2, xUCL, xLCL, xUSL, xLSL)
                fcT3 = sx.trippWire(Trig3, xUCL, xLCL, xUSL, xLSL)
                fcT4 = sx.trippWire(Trig4, xUCL, xLCL, xUSL, xLSL)

                if fcT1 == '#F7F5AB' or fcT2 == '#F7F5AB' or fcT3 == '#F7F5AB' or fcT4 == '#F7F5AB':
                    # Set the alert color to light Yellow -------[]
                    ax1T.axhspan(xUSL, window_y2max, facecolor='#f7f302', edgecolor='#f7f302')   # Yellow trip
                    ax1T.axhspan(window_y2min, xLSL, facecolor='#f7f302', edgecolor='#f7f302')   # Yellow trip

                    # write sigma values into PLC data block if RT is enabled -----------[TRIGGER]
                    U, L, X, D = round(xUCL, 2), round(xLCL, 2), round(TMean1, 2), round(TSdev1, 2)
                    pq.processR1_Sigma(U, L, X, D, round(Trig1, 2), round(Trig2, 2), round(Trig3, 2), round(Trig4, 2), lID, pPos, pID, md)
                    print('R1 Head1-4: 3Sigma', round(Trig1, 2), round(Trig2, 2), round(Trig3, 2), round(Trig4, 2))
                    print('-' * 55)

                elif fcT1 == '#FE9CC9' or fcT2 == '#FE9CC9' or fcT3 == '#FE9CC9' or fcT4 == '#FE9CC9':
                    # Set alert colors to light Brown -------[]
                    ax1T.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')   # Red trip
                    ax1T.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')   # Red trip

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUSL,2), round(xLSL, 2), round(TMean1, 2), round(TSdev1, 2)
                    pq.processR1_Sigma(U, L, X, D, round(Trig1, 2), round(Trig2, 2), round(Trig3, 2), round(Trig4, 2), lID, pPos, pID, md)
                    print('R1 Head1-4: 6Sigma', round(Trig1, 2), round(Trig2, 2), round(Trig3, 2), round(Trig4, 2))
                    print('-' * 55)
                else:
                    ax1T.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')     # white
                    ax1T.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')     # white

            if R2:
                if VariProcess:
                    window_y2min, window_y2max = YScale_minRF, YScale_maxRF
                elif VarPerHeadB:  # Computes trigger alerts for perRing values
                    xUCL, xLCL, xUSL, xLSL = xUCL2, xLCL2, xUSL2, xLSL2
                    window_y2min, window_y2max = window_y2minE, window_y2maxE
                    TSdev1 = tSDev2
                else:
                    xUCL, xLCL, xUSL, xLSL = xUCL2, xLCL2, xUSL2, xLSL2
                    window_y2min, window_y2max = window_y2minA, window_y2maxA
                    TSdev1 = tSDev2
                Trig5 = (R2RF[0]).mean()      # Ring 1 Roller Pressure TODO: 4 TRIGS PER RING
                Trig6 = (R2RF[1]).mean()      # raRF[1].mean()
                Trig7 = (R2RF[2]).mean()
                Trig8 = (R2RF[3]).mean()
                # Provide visualisation: Evaluate trig values with Sigma Limits -----[]
                fcT5 = sx.trippWire(Trig5, xUCL, xLCL, xUSL, xLSL)
                fcT6 = sx.trippWire(Trig6, xUCL, xLCL, xUSL, xLSL)
                fcT7 = sx.trippWire(Trig7, xUCL, xLCL, xUSL, xLSL)
                fcT8 = sx.trippWire(Trig8, xUCL, xLCL, xUSL, xLSL)

                # Capture trigg values above control/set limits -------------------------[]
                if fcT5 == '#F7F5AB' or fcT6 == '#F7F5AB' or fcT7 == '#F7F5AB' or fcT8 == '#F7F5AB':
                    # Set the alert color to light Yellow -------[]
                    ax2T.axhspan(xUSL, window_y2max, facecolor='#f7f302', edgecolor='#f7f302')
                    ax2T.axhspan(window_y2min, xLSL, facecolor='#f7f302', edgecolor='#f7f302')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUCL,2), round(xLCLa,2), round(TMean1,2), round(TSdev1,2)
                    pq.processR2_Sigma(U, L, X, D, round(Trig5, 2), round(Trig6, 2), round(Trig7, 2), round(Trig8, 2), lID, pPos, pID, md)
                    print('R2 Head1-4: 3Sigma', round(Trig5, 2), round(Trig6, 2), round(Trig7, 2), round(Trig8, 2))
                    print('-' * 55)

                elif fcT5 == '#FE9CC9' or fcT6 == '#FE9CC9' or fcT7 == '#FE9CC9' or fcT8 == '#FE9CC9':
                    # Set the alert color to light Yellow -------[]
                    ax2T.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')
                    ax2T.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUSL,2), round(xLSL,2), round(TMean1,2), round(TSdev1,2)
                    pq.processR2_Sigma(U, L, X, D, round(Trig5, 2), round(Trig6, 2), round(Trig7, 2), round(Trig8, 2), lID, pPos, pID, md)
                    print('R2 Head1-4: 6Sigma', round(Trig5, 2), round(Trig6, 2), round(Trig7, 2), round(Trig8, 2))
                    print('-' * 55)
                else:
                    ax2T.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')     # white
                    ax2T.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')     # white

            if R3:
                # Cases --------------------------------------------------[]
                if VariProcess:
                    window_y2min, window_y2max = YScale_minRF, YScale_maxRF
                elif VarPerHeadB:
                    xUCL, xLCL, xUSL, xLSL = xUCL3, xLCL3, xUSL3, xLSL3
                    window_y2min, window_y2max = window_y2minE, window_y2maxE
                    TSdev1 = tSDev3
                else:
                    xUCL, xLCL, xUSL, xLSL = xUCL3, xLCL3, xUSL3, xLSL3
                    window_y2min, window_y2max = window_y2minA, window_y2maxA
                    TSdev1 = tSDev3
                Trig9 = (R3RF[0]).mean()       # Ring 1 Roller Pressure TODO: 4 TRIGS PER RING
                Trig10 = (R3RF[1]).mean()      # raRF[1].mean()
                Trig11 = (R3RF[2]).mean()
                Trig12 = (R3RF[3]).mean()
                # Provide visualisation: Evaluate trig values with Sigma Limits -----[]
                fcT9 = sx.trippWire(Trig9, xUCL, xLCL, xUSL, xLSL)
                fcT10 = sx.trippWire(Trig10, xUCL, xLCL, xUSL, xLSL)
                fcT11 = sx.trippWire(Trig11, xUCL, xLCL, xUSL, xLSL)
                fcT12 = sx.trippWire(Trig12, xUCL, xLCL, xUSL, xLSL)

                # Capture trigg values above control/set limits ------------------------------------
                if fcT9 == '#F7F5AB' or fcT10 == '#F7F5AB' or fcT11 == '#F7F5AB' or fcT12 == '#F7F5AB':
                    ax3T.axhspan(xUSL, window_y2max, facecolor='#f7f302', edgecolor='#f7f302')
                    ax3T.axhspan(window_y2min, xLSL, facecolor='#f7f302', edgecolor='#f7f302')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUCL, 2), round(xLCL, 2), round(TMean1,2), round(TSdev1,2)
                    pq.processR3_Sigma(U, L, X, D, round(Trig9, 2), round(Trig10, 2), round(Trig11, 2), round(Trig12, 2), lID, pPos, pID, md)
                    print('R3 Head1-4: 3Sigma', round(Trig9, 2), round(Trig10, 2), round(Trig11, 2), round(Trig12, 2))
                    print('-' * 55)
                elif fcT9 == '#FE9CC9' or fcT10 == '#FE9CC9' or fcT11 == '#FE9CC9' or fcT12 == '#FE9CC9':
                    ax3T.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')
                    ax3T.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUSL, 2), round(xLSL, 2), round(TMean1,2), round(TSdev1,2)
                    pq.processR3_Sigma(U, L, X, D, round(Trig9, 2), round(Trig10, 2), round(Trig11, 2), round(Trig12, 2), lID, pPos, pID, md)
                    print('R3 Head1-4: 6Sigma', round(Trig9, 2), round(Trig10, 2), round(Trig11, 2), round(Trig12, 2))
                    print('-' * 55)
                else:
                    ax3T.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')     # white
                    ax3T.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')     # white

            if R4:
                if VariProcess:
                    window_y2min, window_y2max = YScale_minRF, YScale_maxRF
                elif VarPerHeadB:
                    xUCL, xLCL, xUSL, xLSL = xUCL4, xLCL4, xUSL4, xLSL4
                    window_y2min, window_y2max = window_y2minE, window_y2maxE
                    TSdev1 = tSDev4
                else:
                    xUCL, xLCL, xUSL, xLSLa = xUCL4, xLCL4, xUSL4, xLSL4
                    window_y2min, window_y2max = window_y2minA, window_y2maxA
                    TSdev1 = tSDev4
                Trig13 = (R4RF[0]).mean()      # Ring 1 Roller Pressure TODO: 4 TRIGS PER RING
                Trig14 = (R4RF[1]).mean()      # raRF[1].mean()
                Trig15 = (R4RF[2]).mean()
                Trig16 = (R4RF[3]).mean()
                # Provide visualisation: Evaluate trig values with Sigma Limits -----[]
                fcT13 = sx.trippWire(Trig13, xUCL, xLCL, xUSL, xLSL)
                fcT14 = sx.trippWire(Trig14, xUCL, xLCL, xUSL, xLSL)
                fcT15 = sx.trippWire(Trig15, xUCL, xLCL, xUSL, xLSL)
                fcT16 = sx.trippWire(Trig16, xUCL, xLCL, xUSL, xLSL)

                # Capture trigg values above control/set limits ------------------------------------
                if fcT13 == '#F7F5AB' or fcT14 == '#F7F5AB' or fcT15 == '#F7F5AB' or fcT16 == '#F7F5AB':
                    # ax2.set_facecolor('#f5f378')
                    ax4T.axhspan(xUSL, window_y2max, facecolor='#f7f302', edgecolor='#f7f302')  # Yellow alert
                    ax4T.axhspan(window_y2min, xLSL, facecolor='#f5f302', edgecolor='#f7f302')  # Yellow alert

                    # write rings' Sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUCL, 2), round(xLCL, 2), round(TMean1,2), round(TSdev1,2)
                    pq.processR4_Sigma(U, L, X, D, round(Trig13, 2), round(Trig14, 2), round(Trig15, 2), round(Trig16, 2), lID, pPos, pID, md)
                    print('Ring1-4 Trip Values: 3Sigma', round(Trig13, 2), round(Trig14, 2), round(Trig15, 2), round(Trig16, 2))
                    print('-' * 55)
                elif fcT13 == '#FE9CC9' or fcT14 == '#FE9CC9' or fcT15 == '#FE9CC9' or fcT16 == '#FE9CC9':
                    # ax2.set_facecolor('#f09605')
                    ax4T.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')     # Red alert
                    ax4T.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')     # Red alert

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUSL, 2), round(xLSL, 2), round(TMean1,2), round(TSdev1,2)
                    pq.processR4_Sigma(U, L, X, D, round(Trig13, 2), round(Trig14, 2), round(Trig15, 2), round(Trig16, 2), lID, pPos, pID, md)
                    print('Ring1-4 Trip Values: 6Sigma', round(Trig13, 2), round(Trig14, 2), round(Trig15, 2), round(Trig16, 2))
                    print('-' * 55)
                else:
                    ax4T.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')     # white
                    ax4T.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')     # white

        # Set trip-line for individual time-series plot ------------------------------------[TAPE SPEED]
        if Manu_TapeSpeed and DNVspecify:       # 02
            pID = 'TS'                          # Required for FMEA report generation
            if VariProcess and DNVspecify:
                axN1 = ax3
                axN2 = ax3
                axN3 = ax3
                axN4 = ax3
                axN5 = ax8
            elif VarPerHeadB and DNVspecify:
                axN1 = ax2
                axN2 = ax3
                axN3 = ax4
                axN4 = ax5
            elif VarPerHeadA and DNVspecify:
                axN1 = ax2
                axN2 = ax2
                axN3 = ax2
                axN4 = ax2
                axN5 = ax6
            # ----- on TFMC -----
            elif VarPerHeadA:
                axN1 = ax2
                axN2 = ax2
                axN3 = ax2
                axN4 = ax2
                axN5 = ax6
            elif VarPerHeadB:
                axN1 = ax2
                axN2 = ax3
                axN3 = ax4
                axN4 = ax5
            else:           # TS is not available on TFMC Grand View Type
                pass
            # ------------- End of trigger initialisation ---------
            if VariProcess:
                xUCL, xLCL, xUSL, xLSL = xUCL5, xLCL5, xUSL5, xLSL5
                window_y2min, window_y2max = YScale_minTS, YScale_maxTS
            # --- Axes plot 3 --------------------------------
            elif VarPerHeadB:
                xUCL, xLCL, xUSL, xLSL = xUCL5, xLCL5, xUSL5, xLSL5
                window_y2min, window_y2max = window_y2minE, window_y2maxE
                TSdev2 = tSDev5
            else:
                xUCL, xLCL, xUSL, xLSL = xUCL5, xLCL5, xUSL5, xLSL5
                window_y2min, window_y2max = window_y2minA, window_y2maxA
                TSdev2 = tSDev5
            axN1.grid(color="0.5", linestyle='-', linewidth=0.5)
            axN1.legend(loc='upper left')

            # TODO ----------------------- check for errors here
            if R1:
                Trig17 = R1TS[0].mean()
                Trig18 = R1TS[1].mean()
                Trig19 = R1TS[2].mean()
                Trig20 = R1TS[3].mean()
                # Provide visualisation: Evaluate trig values with Sigma Limits -----[]
                fcC17 = sx.trippWire(Trig17, xUCL, xLCL, xUSL, xLSL)
                fcC18 = sx.trippWire(Trig18, xUCL, xLCL, xUSL, xLSL)
                fcC19 = sx.trippWire(Trig19, xUCL, xLCL, xUSL, xLSL)
                fcC20 = sx.trippWire(Trig20, xUCL, xLCL, xUSL, xLSL)

                # Capture trigg values above control/set limits ------------------------------------
                if fcC17 == '#F7F5AB' or fcC18 == '#F7F5AB' or fcC19 == '#F7F5AB' or fcC20 == '#F7F5AB':
                    # Set the alert color to light Yellow -------[]
                    axN1.axhspan(xUSL, window_y2max, facecolor='#f5f378', edgecolor='#f5f378')
                    axN1.axhspan(window_y2min, xLSL, facecolor='#f5f378', edgecolor='#f5f378')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUCL,2), round(xLCL,2), round(TMean2,2), round(TSdev2,2)
                    pq.processR1_Sigma(U, L, X, D, round(Trig17, 2), round(Trig18, 2), round(Trig19, 2), round(Trig20, 2), lID, pPos, pID, md)
                    print('R1 Head1-4: 3Sigma', round(Trig17, 2), round(Trig18, 2), round(Trig19, 2), round(Trig20, 2))
                    print('-' * 55)
                elif fcC17 == '#FE9CC9' or fcC18 == '#FE9CC9' or fcC19 == '#FE9CC9' or fcC20 == '#FE9CC9':
                    # Set the alert color to light Yellow -------[]
                    axN1.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')
                    axN1.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUSL,2), round(xLSL,2), round(TMean2,2), round(TSdev2,2)
                    pq.processR1_Sigma(U, L, X, D, round(Trig17, 2), round(Trig18, 2), round(Trig19, 2), round(Trig20, 2), lID, pPos, pID, md)
                    print('R1 Head1-4: 6Sigma', round(Trig17, 2), round(Trig18, 2), round(Trig19, 2), round(Trig20, 2))
                    print('-' * 55)
                else:
                    axN1.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                    axN1.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')

            if R2:
                if VariProcess:
                    # xUCL, xLCL, xUSL, xLSL = xUCL6, xLCL6, xUSL6, xLSL6
                    window_y2min, window_y2max = YScale_minTS, YScale_maxTS
                # --- Axes plot 3 --------------------------------
                elif VarPerHeadB:
                    xUCLb, xLCL, xUSL, xLSL = xUCL6, xLCL6, xUSL6, xLSL6
                    window_y2min, window_y2max = window_y2minE, window_y2maxE
                    TSdev2 = tSDev6
                else:
                    xUCL, xLCL, xUSL, xLSL = xUCL6, xLCL6, xUSL6, xLSL6
                    window_y2min, window_y2max = window_y2minA, window_y2maxA
                    TSdev2 = tSDev6
                # Show grid and legend ------------------------------
                axN2.grid(color="0.5", linestyle='-', linewidth=0.5)
                axN2.legend(loc='upper left')

                Trig21 = R2TS[0].mean()
                Trig22 = R2TS[1].mean()
                Trig23 = R2TS[2].mean()
                Trig24 = R2TS[3].mean()
                # Provide visualisation: Evaluate trig values with Sigma Limits ----[]
                fcC21 = sx.trippWire(Trig21, xUCL, xLCL, xUSL, xLSL)
                fcC22 = sx.trippWire(Trig22, xUCL, xLCL, xUSL, xLSL)
                fcC23 = sx.trippWire(Trig23, xUCL, xLCL, xUSL, xLSL)
                fcC24 = sx.trippWire(Trig24, xUCL, xLCL, xUSL, xLSL)

                # Capture trigg values above control/set limits ------------------------------------
                if fcC21 == '#F7F5AB' or fcC22 == '#F7F5AB' or fcC23 == '#F7F5AB' or fcC24 == '#F7F5AB':
                    # Set the alert color to light Yellow -------[]
                    axN2.axhspan(xUSL, window_y2max, facecolor='#f5f378', edgecolor='#f5f378')
                    axN2.axhspan(window_y2min, xLSL, facecolor='#f5f378', edgecolor='#f5f378')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUCL,2), round(xLCL,2), round(TMean2,2), round(TSdev2,2)
                    pq.processR2_Sigma(U, L, X, D, round(Trig21, 2), round(Trig22, 2), round(Trig23, 2), round(Trig24, 2), lID, pPos, pID, md)
                    print('R2 Head1-4: 3Sigma', round(Trig21, 2), round(Trig22, 2), round(Trig23, 2), round(Trig24, 2))
                    print('-' * 55)
                elif fcC21 == '#FE9CC9' or fcC22 == '#FE9CC9' or fcC23 == '#FE9CC9' or fcC24 == '#FE9CC9':
                    # Set the alert color to light Yellow -------[]
                    axN2.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')
                    axN2.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUSL,2), round(xLSL,2), round(TMean2,2), round(TSdev2,2)
                    pq.processR2_Sigma(U, L, X, D, round(Trig21, 2), round(Trig22, 2), round(Trig23, 2), round(Trig24, 2), lID, pPos, pID, md)
                    print('R2 Head1-4: 6Sigma', round(Trig21, 2), round(Trig22, 2), round(Trig23, 2), round(Trig24, 2))
                    print('-' * 55)
                else:
                    axN2.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                    axN2.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')

            if R3:
                if VariProcess:
                    window_y2min, window_y2max = YScale_minTS, YScale_maxTS
                # --- Axes plot 3 --------------------------------
                elif VarPerHeadB:
                    xUCL, xLCL, xUSL, xLSL = xUCL7, xLCL7, xUSL7, xLSL7
                    window_y2min, window_y2max = window_y2minE, window_y2maxE
                    TSdev2 = tSDev7
                else:
                    xUCL, xLCL, xUSL, xLSL = xUCL7, xLCL7, xUSL7, xLSL7
                    window_y2min, window_y2max = window_y2minA, window_y2maxA
                    TSdev2 = tSDev7
                # Show grid and legend ------------------------------
                axN3.grid(color="0.5", linestyle='-', linewidth=0.5)
                axN3.legend(loc='upper left')
                Trig25 = R3TS[0].mean()
                Trig26 = R3TS[1].mean()
                Trig27 = R3TS[2].mean()
                Trig28 = R3TS[3].mean()
                # Provide visualisation: Evaluate trig values with Sigma Limits ----[]
                fcC25 = sx.trippWire(Trig25, xUCL, xLCL, xUSL, xLSL)
                fcC26 = sx.trippWire(Trig26, xUCL, xLCL, xUSL, xLSL)
                fcC27 = sx.trippWire(Trig27, xUCL, xLCL, xUSL, xLSL)
                fcC28 = sx.trippWire(Trig28, xUCL, xLCL, xUSL, xLSL)

                # Capture trigg values above control/set limits ------------------------------------
                if fcC25 == '#F7F5AB' or fcC26 == '#F7F5AB' or fcC27 == '#F7F5AB' or fcC28 == '#F7F5AB':
                    # Set the alert color to light Yellow -------[]
                    axN3.axhspan(xUSL, window_y2max, facecolor='#f5f378', edgecolor='#f5f378')
                    axN3.axhspan(window_y2min, xLSL, facecolor='#f5f378', edgecolor='#f5f378')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUCL,2), round(xLCL,2), round(TMean2,2), round(TSdev2,2)
                    pq.processR3_Sigma(U, L, X, D, round(Trig25, 2), round(Trig26, 2), round(Trig27, 2), round(Trig28, 2), lID, pPos, pID, md)
                    print('R3 Head1-4: 3Sigma:', round(Trig25, 2), round(Trig26, 2), round(Trig27, 2), round(Trig28, 2))
                    print('-' * 55)
                elif fcC25 == '#FE9CC9' or fcC26 == '#FE9CC9' or fcC27 == '#FE9CC9' or fcC28 == '#FE9CC9':
                    # Set the alert color to light Yellow -------[]
                    axN3.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')
                    axN3.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUSL,2), round(xLSL,2), round(TMean2,2), round(TSdev2,2)
                    pq.processR3_Sigma(U, L, X, D, round(Trig25, 2), round(Trig26, 2), round(Trig27, 2), round(Trig28, 2), lID, pPos, pID, md)
                    print('R3 Head1-4: 6Sigma', round(Trig25, 2), round(Trig26, 2), round(Trig27, 2), round(Trig28, 2))
                    print('-' * 55)
                else:
                    axN3.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                    axN3.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')

            if R4:
                if VariProcess:
                    # xUCL, xLCL, xUSL, xLSL = xUCLB, xLCLB, xUSLB, xLSLB
                    window_y2min, window_y2max = YScale_minTS, YScale_maxTS
                elif VarPerHeadB:
                    xUCL, xLCL, xUSL, xLSL = xUCL8, xLCL8, xUSL8, xLSL8
                    window_y2min, window_y2max = window_y2minE, window_y2maxE
                    TSdev2 = tSDev8
                else:
                    xUCL, xLCL, xUSL, xLSL = xUCL8, xLCL8, xUSL8, xLSL8
                    window_y2min, window_y2max = window_y2minA, window_y2maxA
                    TSdev2 = tSDev8
                # Show grid and legend ------------------------------
                axN4.grid(color="0.5", linestyle='-', linewidth=0.5)
                axN4.legend(loc='upper left')
                Trig29 = R4TS[0].mean()
                Trig30 = R4TS[1].mean()
                Trig31 = R4TS[2].mean()
                Trig32 = R4TS[3].mean()
                # Provide visualisation: Evaluate trig values with Sigma Limits ----[]
                fcC29 = sx.trippWire(Trig29, xUCL, xLCL, xUSL, xLSL)
                fcC30 = sx.trippWire(Trig30, xUCL, xLCL, xUSL, xLSL)
                fcC31 = sx.trippWire(Trig31, xUCL, xLCL, xUSL, xLSL)
                fcC32 = sx.trippWire(Trig32, xUCL, xLCL, xUSL, xLSL)

                # Capture trigg values above control/set limits ------------------------------------
                if fcC29 == '#F7F5AB' or fcC30 == '#F7F5AB' or fcC31 == '#F7F5AB' or fcC32 == '#F7F5AB':
                    # Set the alert color to light Yellow -------[]
                    axN4.axhspan(xUSL, window_y2max, facecolor='#f5f378', edgecolor='#f5f378')
                    axN4.axhspan(window_y2min, xLSL, facecolor='#f5f378', edgecolor='#f5f378')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUCL,2), round(xLCL,2), round(TMean2,2), round(TSdev2,2)
                    pq.processR4_Sigma(U, L, X, D, round(Trig29, 2), round(Trig30, 2), round(Trig31, 2), round(Trig32, 2), lID, pPos, pID, md)
                    print('R4 Head1-4: 3Sigma', round(Trig29, 2), round(Trig30, 2), round(Trig31, 2), round(Trig32, 2))
                    print('-' * 55)
                elif fcC29 == '#FE9CC9' or fcC30 == '#FE9CC9' or fcC31 == '#FE9CC9' or fcC32 == '#FE9CC9':
                    # Set the alert color to light Yellow -------[]
                    axN4.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')
                    axN4.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUSL,2), round(xLSL,2), round(TMean2,2), round(TSdev2,2)
                    pq.processR4_Sigma(U, L, X, D, round(Trig29, 2), round(Trig30, 2), round(Trig31, 2), round(Trig32, 2), lID, pPos, pID, md)
                    print('R4 Head1-4: 6Sigma', round(Trig29, 2), round(Trig30, 2), round(Trig31, 2), round(Trig32, 2))
                    print('-' * 55)
                else:
                    axN4.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                    axN4.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')

            # # FIXME --- Axes plot 7 --------------------------------------------------------[]
            # if not RollerPressure and not TSub_TempRatio and not GapMeasurement:    # TS only
            #     axeN = ax2
            # else:
            #     axeN = ax7
            if DNVspecify:
                if VarPerHeadB:
                    pass
                else:
                    axN5.grid(color="0.5", linestyle='-', linewidth=0.5)
                    axN5.legend(loc='upper left')

        # Set trip-line for individual time-series plot ------------------------------------[TAPE TEMP]
        if TapeTemperatur:
            pID = 'TT'                          # Required for FMEA report generation
            if VariProcess and DNVspecify:
                axk1 = ax4
                axk2 = ax4
                axk3 = ax4
                axk4 = ax4
                axk5 = ax9
            elif VarPerHeadB and DNVspecify:
                axk1 = ax2
                axk2 = ax3
                axk3 = ax4
                axk4 = ax5
                axk5 = ax6
            elif VarPerHeadA and DNVspecify:
                axk1 = ax2
                axk2 = ax2
                axk3 = ax2
                axk4 = ax2
                axk5 = ax6
            # ----- on TFMC -----
            elif VarPerHeadA:
                axk1 = ax2
                axk2 = ax2
                axk3 = ax2
                axk4 = ax2
                axk5 = ax6
            elif VarPerHeadB:
                axk1 = ax2
                axk2 = ax3
                axk3 = ax4
                axk4 = ax5
            else:       # VariProcess
                axk1 = ax3
                axk2 = ax3
                axk3 = ax3
                axk4 = ax3
                axk5 = ax7
        # -----------------------------------------------------------#
            if VariProcess:
                xUCL, xLCL, xUSL, xLSL = xUCL9, xLCL9, xUSL9, xLSL9
                window_y2min, window_y2max = YScale_minTT, YScale_maxTT
                axk1 = ax3
            # --- Axes plot 3 --------------------------------
            elif VarPerHeadB:
                xUCL, xLCL, xUSL, xLSL = xUCL9, xLCL9, xUSL9, xLSL9
                window_y2min, window_y2max = window_y2minE, window_y2maxE
                axk1 = ax2
                TSdev3 = tSDev9

            else:
                xUCL, xLCL, xUSL, xLSL = xUCL9, xLCL9, xUSL9, xLSL9
                window_y2min, window_y2max = window_y2minA, window_y2maxA
                axk1 = ax2
                TSdev3 = tSDev9

            if R1:
                # Show grid and legend ------------------------------
                axk1.grid(color="0.5", linestyle='-', linewidth=0.5)
                axk1.legend(loc='upper left')
                Trig17 = R1TT[0].mean()
                Trig18 = R1TT[1].mean()
                Trig19 = R1TT[2].mean()
                Trig20 = R1TT[3].mean()
                # Provide visualisation: Evaluate trig values with Sigma Limits -----[]
                fcC17 = sx.trippWire(Trig17, xUCL, xLCL, xUSL, xLSL)
                fcC18 = sx.trippWire(Trig18, xUCL, xLCL, xUSL, xLSL)
                fcC19 = sx.trippWire(Trig19, xUCL, xLCL, xUSL, xLSL)
                fcC20 = sx.trippWire(Trig20, xUCL, xLCL, xUSL, xLSL)

                # Capture trigg values above control/set limits ------------------------------------
                if fcC17 == '#F7F5AB' or fcC18 == '#F7F5AB' or fcC19 == '#F7F5AB' or fcC20 == '#F7F5AB':
                    # Set the alert color to light Yellow -------[]
                    axk1.axhspan(xUSL, window_y2max, facecolor='#f5f378', edgecolor='#f5f378')
                    axk1.axhspan(window_y2min, xLSL, facecolor='#f5f378', edgecolor='#f5f378')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUCL,2), round(xLCL,2), round(TMean3,2), round(TSdev3,2)
                    pq.processR1_Sigma(U, L, X, D, round(Trig17, 2), round(Trig18, 2), round(Trig19, 2), round(Trig20, 2), lID, pPos, pID, md)
                    print('R1 Head1-4: 3Sigma', round(Trig17, 2), round(Trig18, 2), round(Trig19, 2), round(Trig20, 2))
                    print('-' * 55)
                elif fcC17 == '#FE9CC9' or fcC18 == '#FE9CC9' or fcC19 == '#FE9CC9' or fcC20 == '#FE9CC9':
                    # Set the alert color to light Yellow -------[]
                    axk1.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')
                    axk1.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUSL, 2), round(xLSL,2), round(TMean3,2), round(TSdev3,2)
                    pq.processR1_Sigma(U, L, X, D, round(Trig17, 2), round(Trig18, 2), round(Trig19, 2), round(Trig20, 2), lID, pPos, pID, md)
                    print('R1 Head1-4: 6Sigma', round(Trig17, 2), round(Trig18, 2), round(Trig19, 2), round(Trig20, 2))
                    print('-' * 55)
                else:
                    axk1.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                    axk1.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')

            if R2:
                if VariProcess:
                    xUCL, xLCL, xUSL, xLSL = xUCL10, xLCL10, xUSL10, xLSL10
                    window_y2min, window_y2max = YScale_minTT, YScale_maxTT
                # --- Axes plot 3 --------------------------------
                elif VarPerHeadB:
                    xUCL, xLCL, xUSL, xLSL = xUCL10, xLCL10, xUSL10, xLSL10
                    window_y2min, window_y2max = window_y2minE, window_y2maxE
                    TSdev3 = tSDev10
                else:
                    xUCL, xLCL, xUSL, xLSL = xUCL10, xLCL10, xUSL10, xLSL10
                    window_y2min, window_y2max = window_y2minA, window_y2maxA
                    TSdev3 = tSDev10
                # Show grid and legend ------------------------------
                axk2.grid(color="0.5", linestyle='-', linewidth=0.5)
                axk2.legend(loc='upper left')
                Trig21 = R2TT[0].mean()
                Trig22 = R2TT[1].mean()
                Trig23 = R2TT[2].mean()
                Trig24 = R2TT[3].mean()
                # Provide visualisation: Evaluate trig values with Sigma Limits ----[]
                fcC21 = sx.trippWire(Trig21, xUCL, xLCL, xUSL, xLSL)
                fcC22 = sx.trippWire(Trig22, xUCL, xLCL, xUSL, xLSL)
                fcC23 = sx.trippWire(Trig23, xUCL, xLCL, xUSL, xLSL)
                fcC24 = sx.trippWire(Trig24, xUCL, xLCL, xUSL, xLSL)

                # Capture trigg values above control/set limits ------------------------------------
                if fcC21 == '#F7F5AB' or fcC22 == '#F7F5AB' or fcC23 == '#F7F5AB' or fcC24 == '#F7F5AB':
                    # Set the alert color to light Yellow -------[]
                    axk2.axhspan(xUSL, window_y2max, facecolor='#f5f378', edgecolor='#f5f378')
                    axk2.axhspan(window_y2min, xLSL, facecolor='#f5f378', edgecolor='#f5f378')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUCL,2), round(xLCL,2), round(TMean3,2), round(TSdev3,2)
                    pq.processR2_Sigma(U, L, X, D, round(Trig21, 2), round(Trig22, 2), round(Trig23, 2), round(Trig24, 2), lID, pPos, pID, md)
                    print('R2 Head1-4: 3Sigma', round(Trig21, 2), round(Trig22, 2), round(Trig23, 2), round(Trig24, 2))
                    print('-' * 55)
                elif fcC21 == '#FE9CC9' or fcC22 == '#FE9CC9' or fcC23 == '#FE9CC9' or fcC24 == '#FE9CC9':
                    # Set the alert color to light Yellow -------[]
                    axk2.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')
                    axk2.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUSL,2), round(xLSL, 2), round(TMean3, 2), round(TSdev3, 2)
                    pq.processR2_Sigma(U, L, X, D, round(Trig21, 2), round(Trig22, 2), round(Trig23, 2), round(Trig24, 2), lID, pPos, pID, md)
                    print('R2 Head1-4: 6Sigma', round(Trig21, 2), round(Trig22, 2), round(Trig23, 2), round(Trig24, 2))
                    print('-' * 55)
                else:
                    axk2.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                    axk2.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')

            if R3:
                if VariProcess:
                    window_y2min, window_y2max = YScale_minTT, YScale_maxTT
                # --- Axes plot 3 --------------------------------
                elif VarPerHeadB:
                    xUCL, xLCL, xUSL, xLSL = xUCL11, xLCL11, xUSL11, xLSL11
                    window_y2min, window_y2max = window_y2minE, window_y2maxE
                    TSdev3 = tSDev11
                else:
                    xUCL, xLCL, xUSL, xLSL = xUCL11, xLCL11, xUSL11, xLSL11
                    window_y2min, window_y2max = window_y2minA, window_y2maxA
                    TSdev3 = tSDev11
                # Show grid and legend ------------------------------
                axk3.grid(color="0.5", linestyle='-', linewidth=0.5)
                axk3.legend(loc='upper left')
                Trig25 = R3TT[0].mean()
                Trig26 = R3TT[1].mean()
                Trig27 = R3TT[2].mean()
                Trig28 = R3TT[3].mean()
                # Provide visualisation: Evaluate trig values with Sigma Limits ----[]
                fcC25 = sx.trippWire(Trig25, xUCL, xLCL, xUSL, xLSL)
                fcC26 = sx.trippWire(Trig26, xUCL, xLCL, xUSL, xLSL)
                fcC27 = sx.trippWire(Trig27, xUCL, xLCL, xUSL, xLSL)
                fcC28 = sx.trippWire(Trig28, xUCL, xLCL, xUSL, xLSL)

                # Capture trigg values above control/set limits ------------------------------------
                if fcC25 == '#F7F5AB' or fcC26 == '#F7F5AB' or fcC27 == '#F7F5AB' or fcC28 == '#F7F5AB':
                    # Set the alert color to light Yellow -------[]
                    axk3.axhspan(xUSL, window_y2max, facecolor='#f5f378', edgecolor='#f5f378')
                    axk3.axhspan(window_y2min, xLSL, facecolor='#f5f378', edgecolor='#f5f378')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUCL,2), round(xLCL,2), round(TMean3,2), round(TSdev3,2)
                    pq.processR3_Sigma(U, L, X, D, round(Trig25, 2), round(Trig26, 2), round(Trig27, 2), round(Trig28, 2), lID, pPos, pID, md)
                    print('R3 Head1-4: 3Sigma:', round(Trig25, 2), round(Trig26, 2), round(Trig27, 2), round(Trig28, 2))
                    print('-' * 55)
                elif fcC25 == '#FE9CC9' or fcC26 == '#FE9CC9' or fcC27 == '#FE9CC9' or fcC28 == '#FE9CC9':
                    # Set the alert color to light Yellow -------[]
                    axk3.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')
                    axk3.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUSL,2), round(xLSL,2), round(TMean3,2), round(TSdev3,2)
                    pq.processR3_Sigma(U, L, X, D, round(Trig25, 2), round(Trig26, 2), round(Trig27, 2), round(Trig28, 2), lID, pPos, pID, md)
                    print('R3 Head1-4: 6Sigma', round(Trig25, 2), round(Trig26, 2), round(Trig27, 2), round(Trig28, 2))
                    print('-' * 55)
                else:
                    axk3.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                    axk3.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')

            if R4:
                if VariProcess:
                    # xUCLb, xLCLb, xUSLb, xLSLb = xUCLB, xLCLB, xUSLB, xLSLB
                    window_y2min, window_y2max = YScale_minTT, YScale_maxTT
                elif VarPerHeadB:
                    xUCL, xLCL, xUSL, xLSL = xUCL12, xLCL12, xUSL12, xLSL12
                    window_y2min, window_y2max = window_y2minE, window_y2maxE
                    TSdev3 = tSDev12
                else:
                    xUCL, xLCL, xUSL, xLSL = xUCL12, xLCL12, xUSL12, xLSL12
                    window_y2min, window_y2max = window_y2minA, window_y2maxA
                    TSdev3 = tSDev12

                # Show grid and legend ------------------------------
                axk4.grid(color="0.5", linestyle='-', linewidth=0.5)
                axk4.legend(loc='upper left')
                Trig29 = R4TT[0].mean()
                Trig30 = R4TT[1].mean()
                Trig31 = R4TT[2].mean()
                Trig32 = R4TT[3].mean()
                # Provide visualisation: Evaluate trig values with Sigma Limits ----[]
                fcC29 = sx.trippWire(Trig29, xUCL, xLCL, xUSL, xLSL)
                fcC30 = sx.trippWire(Trig30, xUCL, xLCL, xUSL, xLSL)
                fcC31 = sx.trippWire(Trig31, xUCL, xLCL, xUSL, xLSL)
                fcC32 = sx.trippWire(Trig32, xUCL, xLCL, xUSL, xLSL)

                # Capture trigg values above control/set limits ------------------------------------
                if fcC29 == '#F7F5AB' or fcC30 == '#F7F5AB' or fcC31 == '#F7F5AB' or fcC32 == '#F7F5AB':
                    # Set the alert color to light Yellow -------[]
                    axk4.axhspan(xUSL, window_y2max, facecolor='#f5f378', edgecolor='#f5f378')
                    axk4.axhspan(window_y2min, xLSL, facecolor='#f5f378', edgecolor='#f5f378')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUCL,2), round(xLCL,2), round(TMean3,2), round(TSdev3,2)
                    pq.processR4_Sigma(U, L, X, D, round(Trig29, 2), round(Trig30, 2), round(Trig31, 2), round(Trig32, 2), lID, pPos, pID, md)
                    print('R4 Head1-4: 3Sigma', round(Trig29, 2), round(Trig30, 2), round(Trig31, 2), round(Trig32, 2))
                    print('-' * 55)
                elif fcC29 == '#FE9CC9' or fcC30 == '#FE9CC9' or fcC31 == '#FE9CC9' or fcC32 == '#FE9CC9':
                    # Set the alert color to light Yellow -------[]
                    axk4.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')
                    axk4.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    U, L, X, D = round(xUSL, 2), round(xLSL, 2), round(TMean3, 2), round(TSdev3, 2)
                    pq.processR4_Sigma(U, L, X, D, round(Trig29, 2), round(Trig30, 2), round(Trig31, 2), round(Trig32, 2), lID, pPos, pID, md)
                    print('R4 Head1-4: 6Sigma', round(Trig29, 2), round(Trig30, 2), round(Trig31, 2), round(Trig32, 2))
                    print('-' * 55)
                else:
                    axk4.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                    axk4.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')

            # FIXME --- Axes plot 7 --------------------------------------------------------[]
            # if not RollerPressure and not TSub_TempRatio and not GapMeasurement:    # TT
            #     axeN = ax7
            # else:
            #     axeN = ax9
            if DNVspecify:
                if VarPerHeadB:
                    pass
                else:
                    axk5.grid(color="0.5", linestyle='-', linewidth=0.5)
                    axk5.legend(loc='upper left')
            else:
                axk5.grid(color="0.5", linestyle='-', linewidth=0.5)
                axk5.legend(loc='upper left')
        # Set trigline for individual time-series plot ------------------------------------[R3]
        if TSub_TempRatio:
            pID = 'DT'                  # Required for FMEA report generation
            if VariProcess and DNVspecify:
                axs1 = ax5
                axs2 = ax5
                axs3 = ax5
                axs4 = ax5
                axs5 = ax10
            elif VarPerHeadB and DNVspecify:
                axs1 = ax2
                axs2 = ax3
                axs3 = ax4
                axs4 = ax5
            elif VarPerHeadA and DNVspecify:
                axs1 = ax2
                axs2 = ax2
                axs3 = ax2
                axs4 = ax2
                axs5 = ax6
            # ----- on TFMC -----
            elif VarPerHeadA:
                axs1 = ax2
                axs2 = ax2
                axs3 = ax2
                axs4 = ax2
                axs5 = ax6
            elif VarPerHeadB:
                axs1 = ax2
                axs2 = ax3
                axs3 = ax4
                axs4 = ax5
            else: # variprocess view
                axs1 = ax4
                axs2 = ax4
                axs3 = ax4
                axs4 = ax4
                axs5 = ax8
            # ---------------------------------------
            if VariProcess:
                xUCL, xLCL, xUSL, xLSL = xUCL13, xLCL13, xUSL13, xLSL13
                window_y2min, window_y2max = YScale_minDT, YScale_maxDT
            elif VarPerHeadB:
                xUCL, xLCL, xUSL, xLSL = xUCL13, xLCL13, xUSL13, xLSL13
                window_y2min, window_y2max = window_y2minE, window_y2maxE
                TSdev4 = tSDev13
            else:
                xUCL, xLCL, xUSL, xLSL = xUCL13, xLCL13, xUSL13, xLSL13
                window_y2min, window_y2max = window_y2minA, window_y2maxA
                TSdev4 = tSDev13

            if R1:
                # Show grid and legend ------------------------------
                axs1.grid(color="0.5", linestyle='-', linewidth=0.5)
                axs1.legend(loc='upper left')
                Trig33 = delta1.mean()
                Trig34 = delta2.mean()
                Trig35 = delta3.mean()
                Trig36 = delta4.mean()
                # Provide visualisation: Evaluate trig values with Sigma Limits ----[]
                fcC33 = sx.trippWire(Trig33, xUCL, xLCL, xUSL, xLSL)
                fcC34 = sx.trippWire(Trig34, xUCL, xLCL, xUSL, xLSL)
                fcC35 = sx.trippWire(Trig35, xUCL, xLCL, xUSL, xLSL)
                fcC36 = sx.trippWire(Trig36, xUCL, xLCL, xUSL, xLSL)

                # Capture trigg values above control/set limits ------------------------------------
                if fcC33 == '#F7F5AB' or fcC34 == '#F7F5AB' or fcC35 == '#F7F5AB' or fcC36 == '#F7F5AB':
                    # Set the alert color to light Yellow -------[]
                    axs1.axhspan(xUSL, window_y2max, facecolor='#f7f302', edgecolor='#f7f302')
                    axs1.axhspan(window_y2min, xLSL, facecolor='#f7f302', edgecolor='#f7f302')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    Q, L, X, D = round(xUCL, 2), round(xLCL, 2), round(TMean4, 2), round(TSdev4, 2)
                    pq.processR1_Sigma(Q, L, X, D, round(Trig33, 2), round(Trig34, 2), round(Trig35, 2), round(Trig36, 2), lID, pPos, pID, md)
                    print('R1 Head1-4: 3Sigma', round(Trig33, 2), round(Trig34, 2), round(Trig35, 2), round(Trig36, 2))
                    print('-' * 55)
                elif fcC33 == '#FE9CC9' or fcC34 == '#FE9CC9' or fcC35 == '#FE9CC9' or fcC36 == '#FE9CC9':
                    # Set the alert color to light Yellow -------[]
                    axs1.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')
                    axs1.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    Q, L, X, D = round(xUSL, 2), round(xLSL, 2), round(TMean4, 2), round(TSdev4, 2)
                    pq.processR1_Sigma(Q, L, X, D, round(Trig33, 2), round(Trig34, 2), round(Trig35, 2), round(Trig36, 2), lID, pPos, pID, md)
                    print('R1 Head1-4: 6Sigma', round(Trig33, 2), round(Trig34, 2), round(Trig35, 2), round(Trig36, 2))
                    print('-' * 55)
                else:
                    axs1.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                    axs1.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')

            if R2:
                if VarPerHeadA:
                    xUCL, xLCL, xUSL, xLSL = xUCL14, xLCL14, xUSL14, xLSL14
                    window_y2min, window_y2max = window_y2minA, window_y2maxA
                    TSdev4 = tSDev14
                elif VarPerHeadB:
                    xUCL, xLCL, xUSL, xLSL = xUCL14, xLCL14, xUSL14, xLSL14
                    window_y2min, window_y2max = window_y2minE, window_y2maxE
                    TSde4 = tSDev14
                elif VariProcess:
                    window_y2min, window_y2max = YScale_minDT, YScale_maxDT
                # Show grid and legend ------------------------------
                axs2.grid(color="0.5", linestyle='-', linewidth=0.5)
                axs2.legend(loc='upper left')
                Trig37 = delta5.mean()
                Trig38 = delta6.mean()
                Trig39 = delta7.mean()
                Trig40 = delta8.mean()
                # Provide visualisation: Evaluate trig values with Sigma Limits ----[]
                fcC37 = sx.trippWire(Trig37, xUCL, xLCL, xUSL, xLSL)
                fcC38 = sx.trippWire(Trig38, xUCL, xLCL, xUSL, xLSL)
                fcC39 = sx.trippWire(Trig39, xUCL, xLCL, xUSL, xLSL)
                fcC40 = sx.trippWire(Trig40, xUCL, xLCL, xUSL, xLSL)

                # Capture trigg values above control/set limits ------------------------------------
                if fcC37 == '#F7F5AB' or fcC38 == '#F7F5AB' or fcC39 == '#F7F5AB' or fcC40 == '#F7F5AB':
                    # Set the alert color to light Yellow -------[]
                    axs2.axhspan(xUSL, window_y2max, facecolor='#f7f302', edgecolor='#f7f302')
                    axs2.axhspan(window_y2min, xLSL, facecolor='#f7f302', edgecolor='#f7f302')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    Q, L, X, D = round(xUCL,2), round(xLCL,2), round(TMean, 2), round(TSdev4, 2)
                    pq.processR2_Sigma(Q, L, X, D, round(Trig37, 2), round(Trig38, 2), round(Trig39, 2), round(Trig40, 2), lID, pPos, pID, md)
                    print('R2 Head1-4: 3Sigma', round(Trig37, 2), round(Trig38, 2), round(Trig39, 2), round(Trig40, 2))
                    print('*' * 55)
                elif fcC37 == '#FE9CC9' or fcC38 == '#FE9CC9' or fcC39 == '#FE9CC9' or fcC40 == '#FE9CC9':
                    # Set the alert color to light Yellow -------[]
                    axs2.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')
                    axs2.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    Q, L, X, D = round(xUSL, 2), round(xLSL, 2), round(TMean4, 2), round(TSdev4, 2)
                    pq.processR2_Sigma(Q, L, X, D, round(Trig37, 2), round(Trig38, 2), round(Trig39, 2), round(Trig40, 2), lID, pPos, pID, md)
                    print('R2 Head1-4: 6Sigma', round(Trig37, 2), round(Trig38, 2), round(Trig39, 2), round(Trig40, 2))
                    print('*' * 55)
                else:
                    axs2.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                    axs2.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')

            if R3:
                if VariProcess:
                    window_y2min, window_y2max = YScale_minDT, YScale_maxDT
                elif VarPerHeadB:
                    xUCL, xLCL, xUSL, xLSL = xUCL15, xLCL15, xUSL15, xLSL15
                    window_y2min, window_y2max = window_y2minE, window_y2maxE
                    TSdev4 = tSDev15
                else:
                    xUCL, xLCL, xUSL, xLSL = xUCL15, xLCL15, xUSL15, xLSL15
                    window_y2min, window_y2max = window_y2minA, window_y2maxA
                    TSdev4 = tSDev15
                # Show grid and legend ------------------------------
                axs3.grid(color="0.5", linestyle='-', linewidth=0.5)
                axs3.legend(loc='upper left')
                Trig41 = delta9.mean()
                Trig42 = deltaA.mean()
                Trig43 = deltaB.mean()
                Trig44 = deltaC.mean()
                # Provide visualisation: Evaluate trig values with Sigma Limits ----[]
                fcC41 = sx.trippWire(Trig41, xUCL, xLCL, xUSL, xLSL)
                fcC42 = sx.trippWire(Trig42, xUCL, xLCL, xUSL, xLSL)
                fcC43 = sx.trippWire(Trig43, xUCL, xLCL, xUSL, xLSL)
                fcC44 = sx.trippWire(Trig44, xUCL, xLCL, xUSL, xLSL)

                # Capture trigg values above control/set limits ------------------------------------
                if fcC41 == '#F7F5AB' or fcC42 == '#F7F5AB' or fcC43 == '#F7F5AB' or fcC44 == '#F7F5AB':
                    # Set the alert color to light Yellow -------[]
                    axs3.axhspan(xUSL, window_y2max, facecolor='#f7f302', edgecolor='#f7f302')
                    axs3.axhspan(window_y2min, xLSL, facecolor='#f7f302', edgecolor='#f7f302')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    Q, L, X, D = round(xUCL, 2), round(xLCL, 2), round(TMean4, 2), round(TSdev4, 2)
                    pq.processR3_Sigma(Q, L, X, D, round(Trig41, 2), round(Trig42, 2), round(Trig43, 2), round(Trig44, 2), lID, pPos, pID, md)
                    print('R3 Head1-4: 3Sigma', round(Trig41, 2), round(Trig42, 2), round(Trig43, 2), round(Trig44, 2))
                    print('-' * 55)
                elif fcC41 == '#FE9CC9' or fcC42 == '#FE9CC9' or fcC43 == '#FE9CC9' or fcC44 == '#FE9CC9':
                    # Set the alert color to light Yellow -------[]
                    axs3.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')
                    axs3.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    Q, L, X, D = round(xUSL, 2), round(xLSL, 2), round(TMean4,2), round(TSdev4, 2)
                    pq.processR3_Sigma(Q, L, X, D, round(Trig41, 2), round(Trig42, 2), round(Trig43, 2), round(Trig44, 2), lID, pPos, pID, md)
                    print('R3 Head1-4: 6Sigma', round(Trig41, 2), round(Trig42, 2), round(Trig43, 2), round(Trig44, 2))
                    print('-' * 55)
                else:
                    axs3.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                    axs3.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')
            if R4:
                if VariProcess:
                    window_y2min, window_y2max = YScale_minDT, YScale_maxDT
                elif VarPerHeadB:
                    xUCL, xLCL, xUSL, xLSL = xUCL16, xLCL16, xUSL16, xLSL16
                    window_y2min, window_y2max = window_y2minE, window_y2maxE
                    TSdev4 = tSDev16
                else:
                    xUCL, xLCL, xUSL, xLSL = xUCL16, xLCL16, xUSL16, xLSL16
                    window_y2min, window_y2max = window_y2minA, window_y2maxA
                    TSdev4 = tSDev16
                # Show grid and legend ------------------------------
                axs4.grid(color="0.5", linestyle='-', linewidth=0.5)
                axs4.legend(loc='upper left')
                Trig45 = deltaD.mean()
                Trig46 = deltaE.mean()
                Trig47 = deltaF.mean()
                Trig48 = deltaG.mean()
                # Provide visualisation: Evaluate trig values with Sigma Limits ----[]
                fcC45 = sx.trippWire(Trig45, xUCL, xLCL, xUSL, xLSL)
                fcC46 = sx.trippWire(Trig46, xUCL, xLCL, xUSL, xLSL)
                fcC47 = sx.trippWire(Trig47, xUCL, xLCL, xUSL, xLSL)
                fcC48 = sx.trippWire(Trig48, xUCL, xLCL, xUSL, xLSL)

                # Capture trigg values above control/set limits ------------------------------------
                if fcC45 == '#F7F5AB' or fcC46 == '#F7F5AB' or fcC47 == '#F7F5AB' or fcC48 == '#F7F5AB':
                    # Set the alert color to light Yellow -------[]
                    axs4.axhspan(xUSL, window_y2max, facecolor='#f7f302', edgecolor='#f7f302')
                    axs4.axhspan(window_y2min, xLSL, facecolor='#f7f302', edgecolor='#f7f302')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    Q, L, X, D = round(xUCL,2), round(xLCL,2), round(TMean4, 2), round(TSdev4, 2)
                    pq.processR3_Sigma(Q, L, X, D, round(Trig45, 2), round(Trig46, 2), round(Trig47, 2), round(Trig48, 2), lID, pPos, pID, md)
                    print('R4 Head1-4: 3Sigma', round(Trig45, 2), round(Trig46, 2), round(Trig47, 2), round(Trig48, 2))
                    print('-' * 55)
                elif fcC45 == '#FE9CC9' or fcC46 == '#FE9CC9' or fcC47 == '#FE9CC9' or fcC48 == '#FE9CC9':
                    # Set the alert color to light Yellow -------[]
                    axs4.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')
                    axs4.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')

                    # write sigma values into PLC data block if RT is enabled -----------[]
                    Q, L, X, D = round(xUSL,2), round(xLSL, 2), round(TMean4, 2), round(TSdev4, 2)
                    pq.processR3_Sigma(Q, L, X, D, round(Trig45, 2), round(Trig46, 2), round(Trig47, 2), round(Trig48, 2), lID, pPos, pID, md)
                    print('R4 Head1-4: 6Sigma', round(Trig45, 2), round(Trig46, 2), round(Trig47, 2), round(Trig48, 2))
                    print('-' * 55)
                else:
                    axs4.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                    axs4.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')

            # FIXME ---------------------------------- Axes plot 8 ---------[]
            if DNVspecify:
                if VarPerHeadB:
                    pass
                else:
                    axs5.grid(color="0.5", linestyle='-', linewidth=0.5)
                    axs5.legend(loc='upper left')
            else:
                axs5.grid(color="0.5", linestyle='-', linewidth=0.5)
                axs5.legend(loc='upper left')
        # Set trigger line for individual time-series plot ------------------------------------[R4]
        if GapMeasurement:  # and TGapMeasureProcess:
            pID = 'TG'      # Required for FMEA report generation
            if VariProcess and DNVspecify:
                axz1 = ax6      # Segment #1
                axz2 = ax6      # Segment #2
                axz3 = ax6      # R3
                axz4 = ax6      # R4
                axz5 = ax11     # ref to s plot
            elif VarPerHeadB and DNVspecify:
                axz1 = ax2
                axz2 = ax3
                axz3 = ax4
                axz4 = ax5
            elif VarPerHeadA and DNVspecify:
                axz1 = ax2
                axz2 = ax2
                axz3 = ax2
                axz4 = ax2
                axz5 = ax6  # ref to s plot
            # ----- on TFMC -----
            elif VarPerHeadA:
                axz1 = ax2
                axz2 = ax2
                axz3 = ax2
                axz4 = ax2
                axz5 = ax6
            elif VarPerHeadB:
                axz1 = ax2
                axz2 = ax3
                axz3 = ax4
                axz4 = ax5
                axz5 = ax6
            else:  # variprocess view
                axz1 = ax5
                axz2 = ax5
                axz3 = ax5
                axz4 = ax5
                axz5 = ax9
            # ------------------------------------ #
            if VariProcess:
                xUCL, xLCL, xUSL, xLSL = xUCLe, xLCLe, xUSLe, xLSLe
                window_y2min, window_y2max = YScale_minTG, YScale_maxTG
            elif VarPerHeadB:
                xUCL, xLCL, xUSL, xLSL = xUCLe, xLCLe, xUSLe, xLSLe
                window_y2min, window_y2max = window_y2minE, window_y2maxE
                # TSdev5 = tSDev17
            else:
                xUCL, xLCL, xUSL, xLSL = xUCLe, xLCLe, xUSLe, xLSLe
                window_y2min, window_y2max = window_y2minA, window_y2maxA
                # TSdev5 = tSDev17

            # Show grid and legend ------------------------------
            axz1.grid(color="0.5", linestyle='-', linewidth=0.5)
            axz1.legend(loc='upper left')
            # if R1: -------------------- [A1A2]
            gTrig1 = tGap1.mean()
            gTrig2 = tGap2.mean()
            gTrig3 = tGap3.mean()
            gTrig4 = tGap4.mean()

            # Provide visualisation: Evaluate trig values with Sigma Limits ----[]
            fcG1 = sx.trippWire(gTrig1,  xUCL, xLCL, xUSL, xLSL)
            fcG2 = sx.trippWire(gTrig2,  xUCL, xLCL, xUSL, xLSL)
            # Capture trigg values above control/set limits --------------------[]
            if fcG1 == '#F7F5AB' or fcG2 == '#F7F5AB':
                # Set the alert color to light Yellow -------[]
                axz1.axhspan(xUSL, window_y2max, facecolor='#f7f302', edgecolor='#f7f302')
                axz1.axhspan(window_y2min, xLSL, facecolor='#f7f302', edgecolor='#f7f302')

                # write sigma values into PLC data block if RT is enabled ------[]
                U, L, X, D = round(xUCL, 2), round(xLCL, 2), round(TMean5, 2), round(TSdev5, 2)
                print('TP:', U, L, X, D, round(gTrig1, 2), round(gTrig2, 2), round(gTrig3, 2), round(gTrig4, 2), lID, pPos, pID, md, WON)
                pq.processR3_Sigma(U, L, X, D, round(gTrig1, 2), round(gTrig2, 2), round(gTrig3, 2), round(gTrig4, 2), lID, pPos, pID, md)
                print('Gap A1A2 3Sigma Trip:', round(gTrig1, 2), round(gTrig2, 2))
                print('-' * 55)
            elif fcG1 == '#FE9CC9' or fcG2 == '#FE9CC9':
                # Set the alert color to light Yellow -------[]
                axz1.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')
                axz1.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')

                # write sigma values into PLC data block if RT is enabled ------[]
                U, L, X, D = round(xUSL,2), round(xLSL,2), round(TMean4,2), round(TSdev4,2)
                pq.processR3_Sigma(U, L, X, D, round(gTrig1, 2), round(gTrig2, 2), round(gTrig3, 2), round(gTrig4, 2), lID, pPos, pID, md)
                print('Gap A1A2 6Sigma Trip:', round(gTrig1, 2), round(gTrig2, 2), round(gTrig3, 2), round(gTrig4, 2))
                print('-' * 55)
            else:
                axz1.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                axz1.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')

            # if #R2: --------------------------------------------------------------------[SEGMENT 3/4]
            # Show grid and legend ------------------------------
            axz2.grid(color="0.5", linestyle='-', linewidth=0.5)
            axz2.legend(loc='upper left')
            gTrig5 = tGap5.mean()
            gTrig6 = tGap6.mean()
            gTrig7 = tGap7.mean()
            gTrig8 = tGap8.mean()
            # Provide visualisation: Evaluate trig values with Sigma Limits ----[]
            fcG3 = sx.trippWire(gTrig3, xUCL, xLCL, xUSL, xLSL)
            fcG4 = sx.trippWire(gTrig4, xUCL, xLCL, xUSL, xLSL)

            # Capture trigg values above control/set limits --------------------[]
            if fcG3 == '#F7F5AB' or fcG4 == '#F7F5AB':
                # Set the alert color to light Yellow -------[]
                axz2.axhspan(xUSL, window_y2max, facecolor='#f7f302', edgecolor='#f7f302')
                axz2.axhspan(window_y2min, xLSL, facecolor='#f7f302', edgecolor='#f7f302')

                # write sigma values into PLC data block if RT is enabled ------[]
                U, L, X, D = round(xUCL, 2), round(xLCL, 2), round(TMean5, 2), round(TSdev5, 2)
                pq.processR3_Sigma(U, L, X, D, round(gTrig5, 2), round(gTrig6, 2), round(gTrig7, 2), round(gTrig8, 2), lID, pPos, pID, md)
                print('Gap A3A4 3Sigma Trip:', round(gTrig5, 2), round(gTrig6, 2), round(gTrig7, 2), round(gTrig8, 2))
                print('-' * 55)
            elif fcG3 == '#FE9CC9' or fcG4 == '#FE9CC9':
                # Set the alert color to light Yellow -------[]
                axz2.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')
                axz2.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')

                # write sigma values into PLC data block if RT is enabled ------[]
                U, L, X, D = round(xUSL, 2), round(xLSL,2), round(TMean5, 2), round(TSdev5, 2)
                pq.processR3_Sigma(U, L, X, D, round(gTrig5, 2), round(gTrig6, 2), round(gTrig7, 2), round(gTrig8, 2), lID, pPos, pID, md)
                print('Gap A3A4 6Sigma Trip:', round(gTrig5, 2), round(gTrig6, 2), round(gTrig7, 2), round(gTrig8, 2))
                print('-' * 55)
            else:
                axz2.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')
                axz2.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')

            # # if #Section 3: ------------------------------------------------------------[SEGMENT 3]
            # --- Axes plot 9 ---------
            if DNVspecify:
                if VarPerHeadB:
                    pass
                else:
                    axz5.grid(color="0.5", linestyle='-', linewidth=0.5)
                    axz5.legend(loc='upper left')

            else:
                axz5.grid(color="0.5", linestyle='-', linewidth=0.5)
                axz5.legend(loc='upper left')

        # Overall Equipment Effectiveness (OEE) Data -------------------------------------------[]
        if PerfProcess:
            # Define dataframe columns ---------------------------------------------------------[]
            colu = ['TimeLine', 'CurrentLayer', 'TransitionCode', 'Description', 'Duration(Sec)']
            df3 = pd.DataFrame(dX3, columns=colu)  # porte sql data into dataframe
            # --------------------------------
            # Allow the following code to run despite not on DNV condition ----------------#
            # TODO replace with process variable
            cLayer = df3['CurrentLayer']        # .tail(1)
            status = df3['Description'][1]      # .tail(1)
            curLayer = list(set(cLayer))        # shuffle list to obtain unique layer number at a time
            if len(curLayer) > 1:
                lastE = len(curLayer)
                curLayer = curLayer[lastE - 1]  # print the last index element
            # ---------------------------------
            # if VarPerHeadA or VarPerHeadB or VariProcess:
            OTlayr.append(curLayer[0])      # Post values into static array
            EPpos.append('N/A')             # Insert pipe position is available
            pStatus.append(status)
            print('\nTP05[Layer/Status]:', curLayer[0], status)
            # ----------------------------------------------------------------------------#
            # DNVspecify and VariProcess or not DNVspecify and VarPerHeadA or VarPerHeadB:
            if not DNVspecify and VarPerHeadA or not DNVspecify and VarPerHeadB or VariProcess and DNVspecify:
                print('\nTesting loop...')
                # Obtain current local time string ------------------------[]
                cTime = strftime("%H:%M:%S")

                # Convert current time string to datetime object ----------[]
                currentTime = str(datetime.strptime(cTime, "%H:%M:%S").time())
                print('\nCurrent Time:', currentTime)

                # Compute essential variables ------------------------------- TODO verify filter *****
                dayShiftTime = df3[(df3['TimeLine'] >= Start_Day) & (df3['TimeLine'] <= currentTime)]

                totalRun = dayShiftTime.copy()
                totalRun = totalRun.drop_duplicates(subset='TimeLine', keep='first')
                # print('Total Run:', totalRun)

                # Convert Shift start time to string format -----------------
                shiftStartTime = str(datetime.strptime(Start_Day, "%H:%M:%S").time())
                shiftEndTime = str(datetime.strptime(FinishDay, "%H:%M:%S").time())
                print("Shift Starts:", shiftStartTime)
                print("Shift Ends @:", shiftEndTime)

                # Compute production lapse time -----------------------------
                TShiftSec = datetime.strptime(FinishDay, '%H:%M:%S') - datetime.strptime(shiftStartTime, '%H:%M:%S')
                ShiftinSec = TShiftSec.total_seconds()      # Convert values into seconds
                print('=' * 22)
                print('Shift Hours:', ShiftinSec, '(Sec)')

                deltaT = datetime.strptime(str(currentTime), '%H:%M:%S') - datetime.strptime(shiftStartTime, '%H:%M:%S')
                opTime = deltaT.total_seconds()           # Convert values into seconds
                print('\n********* SUMMARY **********')
                print('Operation Time:', opTime, '(Sec)')

                # Compute downtime in seconds -------------------------------
                downtime = totalRun['Duration(Sec)'].sum()
                print('TCP1 Down Time:', float(downtime), '(Sec)')

                # Computer work time relative to total shift hours ----------
                prodTime = (opTime - downtime)
                print('Net Production:', prodTime, '(Sec)')
                print('-' * 28)

                endShiftHour = (ShiftinSec - prodTime)

                pieData = np.array([endShiftHour, prodTime, downtime])
                segexplode = [0, 0, 0.1]

                ind_metric = ['Current Shift', 'Production Time', 'OEE Time']

                # Pie Chart Plot ---------------------
                # add colors
                mycol = ['#4c72b0', 'green', 'orange']              # add colors
                ax1.pie(pieData, labels=ind_metric, startangle=90, explode=segexplode, shadow=True, autopct='%1.1f%%',
                        colors=mycol, textprops={'fontsize': 10})
                if RetroReplay:
                    ax1.set_title('Machine Progressive Status', fontsize=12, fontweight='bold')
                else:
                    ax1.set_title('Machine Live Status Analysis', fontsize=12, fontweight='bold')
                # -----------------------------------
                # TODO Recheck the line below...
                ax1.text(-1.559, -1.169, 'Processing Layer #: ' + str(curLayer), fontsize=12, fontweight='bold')
                if RetroReplay:
                    ax1.text(-1.659, -1.369, 'OEE Status: Pipe laying in Progress...', fontsize=12, fontweight='normal')
                else:
                    ax1.text(-1.659, -1.369, 'OEE Status: ' + str(status), fontsize=12, fontweight='normal')

        timef = time.time()
        lapsedT = timef - timei
        print(f"\nProcess Interval: {lapsedT} sec\n")
        # Calculate time lapses for all processing types and store in text file.
        if DNVspecify and asp:
            runtimeParams = '12 SPC Windows'
        else:
            if DNVspecify and monitorParamLP or monitorParamLA:
                runtimeParams = '10 + 2 VPlots' # DNV Reqs.: i.e 5 XBar + 5 SBar + 2 Monitoring params
            else:
                runtimeParams = '8 + 2 VPlot'   # TFMC Reqs.: i.e 4 XBar + 4 SBar + 1 Monitoring param + 1 OEE Plot

        timeProcessor(type, smp_Sz, runtimeParams, '05hz', round(lapsedT, 3))

    # Set up plot to call animate() function periodically [Animation, ArtistAnimation, FuncAnimation] ----------------
    """
    Blitting' is a standard technique in computer graphics. Save ('blit') one more artist on top of existing one.
    i.e re-draw the few artists that are changing at each frame and possibly save significant amounts of time
    """

    anim = FuncAnimation(fig, asynchronous, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle, blit=False)

    plt.tight_layout()
    plt.show()




