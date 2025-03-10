# --------------------------------------------------------------------------#
# Author: Dr RB Labs
# Developed for Magma Global - TechnipFMC Industrialization
# Email: robbielabs@uwl.ac.uk
# Copyright (C) 2023-2025, Robbie Labs
# Cascade (Multiple screen ) View
# --------------------------------------------------------------------------#

# -------PLC/SQL Query -------#
import time
from multiprocessing import Process
from time import gmtime, strftime
from tkinter import *
from tkinter import ttk

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

import spcWatchDog as wd

LARGE_FONT = ("Verdana", 12, 'bold')
import matplotlib.patches as patches
from mpl_interactions import zoom_factory

import rtP_Evaluator as tq
# -------PLC/SQL Query --------#
import selDataColsLA as qla     # Laser Angle
import selDataColsLP as qlp     # Laser Power
import selDataColsRF as qrf     # Roller Force
import selDataColsRM as qrm     # Ramp Mapping
import selDataColsST as qst     # Substrate Temperature
import selDataColsTG as qtg     # Tape Gap Void
import selDataColsTP as qtp     # Tape Placement error
import selDataColsTT as qtt     # Tape Temperature
import selDataColsVM as qvm     # Void mapping
# -----------------------------#
import pParamsHL as dd

import subprocess
try:
    subprocess.check_output('nvidia-smi')
    print('Nvidia GPU detected!')
except Exception:
    print('No Nvidia GPU in system!')

# -------------------------------#
pPos = str(3345)
layer = str(10)
# -------------------------------#
WON = "275044"
eSMC = 'Getting started...'
countA = '02'
countB = '03'
countC = '04'
countD = '05'
countE = '06'
countF = '07'
countG = '08'
countH = '09'
# --------------------------------------- Common to all Process Procedures -------------------------[]
cpTapeW, cpLayerNo, runType = [], [], []
UsePLC_DBS = True
hostConn = 0
runStatus = 0

# --------------
gap_vol = 0
ramp_vol = 0
vCount = 1000
pExLayer = 100
pLength = 10000
# ---------------

# XBar Constants ------------------------------[]
A3 = [0.975, 0.789, 0.680, 0.6327, 0.606, 0.5525]       # 10, 15, 20, 23, 25, 30  sample sizes respectively
B3 = [0.284, 0.428, 0.510, 0.5452, 0.565, 0.6044]       # 10, 15, 20, 23, 25, 30  sample sizes respectively
B4 = [1.716, 1.572, 1.490, 1.4548, 1.435, 1.3956]       # 10, 15, 20, 23, 25, 30

UsePLC_DBS = True                                       # specify SQl Query or PLC DB Query is in use
processWON = []

# ------------- Dummy values ----------------------[]
pPos = '6.2345'
layer = '03'
WON = "275044"
sel_SS = "30"
sel_gT = "S-Domino"
eSMC = 'Tape laying process in progress...'
# ------------------ Auto canvass configs -------[]
y_start = 110
y_incmt = 30
rtValues = []

# ---- Common to all Process Procedures ---[]
pRecipe = ""

# Call function and load WON specification -----[]
mLA, mLP, mCT, mOT, mRP, mWS, mSP, sStart, sStops, LP, LA, TP, RF, TT, ST, TG, SP = dd.decryptMetricsGeneral(WON)
print('\nDecrypted Prod Parameters:', mLA, mLP, mCT, mOT, mRP, mWS, mSP, sStart, sStops, LP, LA, TP, RF, TT, ST, TG, SP)

# ----------------------------------------------[A]
if int(TT) and int(ST) and int(TG) and not int(LP) and not int(LA) and not int(TP) and not int(RF):
    pRecipe = 'DNV'
    import qParamsHL_DNV as dnv
elif int(LP) and int(LA) and int(TP) and int(RF) and int(TT) and int(ST) and int(TG):
    pRecipe = 'MGM'
    import qParamsHL_MGM as mgm
else:
    pRecipe = 'USR'
# ----------------------------------------------[]


def rfProcessParam(vCounter, pType):

    root = Tk()
    root.title('mPipe Production: Synchronous SPC - Viz: ' + vCounter)
    root.geometry("1800x800")

    # Load Quality Historical Values ---------------[]
    if pRecipe == 'DNV':
        rfSize, rfgType, rfSEoL, rfSEoP, rfHL, rfAL, rfFO, rfParam1, rfParam2, dud3, dud4, dud5 = dnv.decryptpProcessLim(WON,
                                                                                                                   'RF')
    else:
        rfSize, rfgType, rfSEoL, rfSEoP, rfHL, rfAL, rfFO, rfParam1, rfParam2, dud3, dud4, dud5 = mgm.decryptpProcessLim(WON,
                                                                                                                   'RF')
    # Break down each element to useful list -------[Roller force]

    if rfHL and rfParam1 and rfParam2:  # Roller Pressure TODO - layer metrics to guide TCP01
        rfPerf = '$Pp_{k' + str(rfSize) + '}$'      # Using estimated or historical Mean
        rflabel = 'Pp'
        # -------------------------------
        rfOne = rfParam1.split(',')                 # split into list elements
        rfTwo = rfParam1.split(',')
        dTaperf = rfOne[1].strip("' ")              # defined Tape Width
        dLayer = rfOne[10].strip("' ")              # Defined Tape Layer
        # Load historical limits for the process----#
        if cpLayerNo == 40:                         # '22mm'|'18mm',  1-40 | 41+
            rfUCL = float(rfOne[2].strip("' "))     # Strip out the element of the list
            rfLCL = float(rfOne[3].strip("' "))
            rfMean = float(rfOne[4].strip("' "))
            rfDev = float(rfOne[5].strip("' "))
            # --------------------------------
            sUCLrf = float(rfOne[6].strip("' "))
            sLCLrf = float(rfOne[7].strip("' "))
            # --------------------------------
            rfUSL = (rfUCL - rfMean) / 3 * 6
            rfLSL = (rfMean - rfLCL) / 3 * 6
            # --------------------------------
        else:
            rfUCL = float(rfTwo[2].strip("' "))     # Strip out the element of the list
            rfLCL = float(rfTwo[3].strip("' "))
            rfMean = float(rfTwo[4].strip("' "))
            rfDev = float(rfTwo[5].strip("' "))
            # --------------------------------
            sUCLrf = float(rfTwo[6].strip("' "))
            sLCLrf = float(rfTwo[7].strip("' "))
            # -------------------------------
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
        rfPerf = '$Cp_{k' + str(rfSize) + '}$'  # Using Automatic group Mean
        rflabel = 'Cp'

    label = ttk.Label(root, text='Roller Force [RF] - [' + pType + ' Mode] - ' + strftime("%a, %d %b %Y", gmtime()), font=LARGE_FONT)
    label.pack(pady=10, padx=10)

    # Define Axes ---------------------#
    fig = Figure(figsize=(25, 13), dpi=100)

    # fig = Figure(figsize=(self.winfo_screenwidth(), self.winfo_screenheight()), dpi=100)
    fig.subplots_adjust(left=0.03, bottom=0.02, right=0.99, top=0.976, hspace=0.14, wspace=0.195)
    # -------------------------------------------------------[]
    a1 = fig.add_subplot(2, 3, (1, 2))                       # Roller Force X Bar plot
    a2 = fig.add_subplot(2, 3, (4, 5))                       # Roller angle S Bar plot
    a3 = fig.add_subplot(2, 3, (3, 6))                       # Process Feeds

    # Declare Plots attributes -----------------------------[]
    plt.rcParams.update({'font.size': 7})
    # Calibrate limits for X-moving Axis -------------------#
    YScale_minRF, YScale_maxRF = rfLSL - 8.5, rfUSL + 8.5   # Roller Force
    sBar_minRF, sBar_maxRF = sLCLrf - 80, sUCLrf + 80       # Calibrate Y-axis for S-Plot
    window_Xmin, window_Xmax = 0, (int(rfSize) + 3)         # windows view = visible data points

    # ----------------------------------------------------------#
    # Real-Time Parameter according to updated requirements ----# 28/Feb/2025
    T1 = WON + '_RF'  # Laser Power
    # ----------------------------------------------------------#

    # Declare Plots attributes --------------------------------#
    a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
    a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
    a1.set_title('Roller Pressure [XBar]', fontsize=12, fontweight='bold')
    a2.set_title('Roller Pressure [StDev]', fontsize=12, fontweight='bold')
    a1.grid(color="0.5", linestyle='-', linewidth=0.5)
    a2.grid(color="0.5", linestyle='-', linewidth=0.5)
    a1.legend(loc='upper right', title='Roller Force')
    a2.legend(loc='upper right', title='Sigma curve')

    # Initialise runtime limits --------------------------------#
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

    # Statistical Feed ---------------------------------------[]
    a3.text(0.466, 0.945, 'Performance Feed - RF', fontsize=16, fontweight='bold', ha='center', va='center',
            transform=a3.transAxes)
    # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
    rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
    rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
    a3.add_patch(rect1)
    a3.add_patch(rect2)
    # ------- Process Performance Pp (the spread)---------------------
    a3.text(0.145, 0.804, rflabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.328, 0.658, '#Pp', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.650, 0.820, 'Ring ' + rflabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
    a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
    # ------- Process Performance Ppk (Performance)--------------------#
    a3.text(0.145, 0.403, rfPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.328, 0.282, '#Ppk', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.640, 0.420, 'Ring ' + rfPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
    # -----------------------------------------------------------------#
    a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
    # ----- Pipe Position and SMC Status -----
    a3.text(0.080, 0.090, 'Pipe Position: ' + pPos + '    Processing Layer #' + layer, fontsize=12, ha='left',
            transform=a3.transAxes)
    a3.text(0.080, 0.036, 'SMC Status: ' + eSMC, fontsize=12, ha='left', transform=a3.transAxes)

    # ---------------- EXECUTE SYNCHRONOUS METHOD -----------------------------#
    def synchronousRP(rfSize, rfgType, fetchT):
        fetch_no = str(fetchT)          # entry value in string sql syntax

        # Obtain Volatile Data from PLC Host Server ---------------------------[]
        if not inUseAlready:            # Load Comms Plc class once
            import CommsPlc as q
            q.DAQ_connect(1, 0)
        else:
            con_rf = conn.cursor()

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
            if UsePLC_DBS:  # Not Using PLC Data
                import plcArrayRLmethodRF as srf                    # DrLabs optimization method

                inProgress = True                                   # True for RetroPlay mode
                print('\nSynchronous controller activated...')

                if not sysRun:
                    sysRun, msctcp, msc_rt = wd.autoPausePlay()     # Retrieve MSC from Watchdog
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

                # Allow selective runtime parameter selection on production critical process
                procID = 'RF'
                rfData = srf.paramDataRequest(procID, rfSize, rfgType, fetch_no)

            else:
                import sqlArrayRLmethodRF as srf     # DrLabs optimization method

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
                    rfData = srf.sqlexec(rfSize, rfgType, con_rf, T1, fetchT)

                # ------ Inhibit iteration ----------------------------------------------------------[]
                """
                # Set condition for halting real-time plots in watchdog class ---------------------
                """
                # TODO --- values for inhibiting the SQL processing
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    con_rf.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

        return rfData

    # ================== End of synchronous Method ==========================
    def asynchronousRF(db_freq):
        timei = time.time()  # start timing the entire loop

        # Call data loader Method---------------------------#
        rfData = synchronousRP(rfSize, rfgType, db_freq)    # data loading functions
        # --------------------------------------------------#

        if UsePLC_DBS == 1:
            import VarPLCrf as rf

            viz_cycle = 10
            # Call synchronous data function ---------------[]
            columns = qrf.validCols(T1)                    # Load defined valid columns for PLC Data
            df1 = pd.DataFrame(rfData, columns=columns)    # Include table data into python Dataframe
            RF = rf.loadProcesValues(df1)                  # Join data values under dataframe

        else:
            import rfVarSQL as rf                          # load SQL variables column names | rfVarSQL

            viz_cycle = 150
            g1 = qrf.validCols(T1)                         # Construct Data Column selSqlColumnsTFM.py
            df1 = pd.DataFrame(rfData, columns=g1)         # Import into python Dataframe
            RF = rf.loadProcesValues(df1)                  # Join data values under dataframe

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
        im10.set_ydata((RF[0]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 1
        im11.set_ydata((RF[1]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 2
        im12.set_ydata((RF[2]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 3
        im13.set_ydata((RF[3]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 1 ---------#
        mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(rfHL, rfSize, 'RF')
        # ---------------------------------------#
        im14.set_ydata((RF[4]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 1
        im15.set_ydata((RF[5]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 2
        im16.set_ydata((RF[6]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 3
        im17.set_ydata((RF[7]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 2 ---------#
        mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(rfHL, rfSize, 'RF')
        # ---------------------------------------#
        im18.set_ydata((RF[8]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 1
        im19.set_ydata((RF[9]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 2
        im20.set_ydata((RF[10]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 3
        im21.set_ydata((RF[11]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 3 ---------#
        mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(rfHL, rfSize, 'RF')
        # ---------------------------------------#
        im22.set_ydata((RF[12]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 1
        im23.set_ydata((RF[13]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 2
        im24.set_ydata((RF[14]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 3
        im25.set_ydata((RF[15]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 4 ---------#
        mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(rfHL, rfSize, 'RF')
        # ---------------------------------------#
        # S Plot Y-Axis data points for StdDev ----------------------------------------
        im26.set_ydata((RF[0]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
        im27.set_ydata((RF[1]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
        im28.set_ydata((RF[2]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
        im29.set_ydata((RF[3]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])

        im30.set_ydata((RF[4]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
        im31.set_ydata((RF[5]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
        im32.set_ydata((RF[6]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
        im33.set_ydata((RF[7]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])

        im34.set_ydata((RF[8]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
        im35.set_ydata((RF[9]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
        im36.set_ydata((RF[10]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
        im37.set_ydata((RF[11]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])

        im38.set_ydata((RF[12]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
        im39.set_ydata((RF[13]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
        im40.set_ydata((RF[14]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
        im41.set_ydata((RF[15]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
        # Compute entire Process Capability -----------#
        if not rfHL:
            mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLa, dLCLa, ppT, pkT, xline, sline = tq.tAutoPerf(rfSize, mnA, mnB,
                                                                                                  mnC, mnD, sdA,
                                                                                                  sdB, sdC, sdD)
        else:
            xline, sline = rfMean, rfDev
            mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLa, dLCLa, ppT, pkT = tq.tManualPerf(mnA, mnB, mnC, mnD, sdA, sdB,
                                                                                      sdC, sdD, rfUSL, rfLSL, rfUCL,
                                                                                       rfLCL)

        # # Declare Plots attributes --------------------------------------------------------[]
        # XBar Mean Plot
        a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
        a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')            # 3 Sigma span (Purple)
        a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')            # grey area
        a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
        # ---------------------- sBar_minTT, sBar_maxTT -------[]
        # Define Legend's Attributes  ----
        a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
        a2.axhspan(sLCLrf, sUCLrf, facecolor='#F9C0FD', edgecolor='#F9C0FD')        # 1 Sigma Span
        a2.axhspan(sUCLrf, sBar_maxRF, facecolor='#CCCCFF', edgecolor='#CCCCFF')    # 1 Sigma above the Mean
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
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack()

    root.mainloop()


# -----------------------------------------------------------------------------------------
def ttProcessParam(vCounter, pType):

    root = Tk()
    root.title('mPipe Production: Synchronous SPC - Viz: ' + vCounter)
    root.geometry("1800x800")

    # Load Quality Historical Values -----------[]
    if pRecipe == 'DNV':
        ttSize, ttgType, ttSEoL, ttSEoP, ttHL, ttAL, ttFO, ttParam1, ttParam2, ttParam3, ttParam4, ttParam5 = dnv.decryptpProcessLim(WON,
                                                                                                                   'TT')
    else:
        ttSize, ttgType, ttSEoL, ttSEoP, ttHL, ttAL, ttFO, ttParam1, ttParam2, ttParam3, ttParam4, ttParam5 = mgm.decryptpProcessLim(WON,
                                                                                                                   'TT')
    # Break down each element to useful list ---------------[Tape Temperature]

    if ttHL and ttParam1 and ttParam2 and ttParam3 and ttParam4 and ttParam5:  #
        ttPerf = '$Pp_{k' + str(ttSize) + '}$'          # Using estimated or historical Mean
        ttlabel = 'Pp'
        # -------------------------------
        One = ttParam1.split(',')                       # split into list elements
        Two = ttParam2.split(',')
        Thr = ttParam3.split(',')
        For = ttParam4.split(',')
        Fiv = ttParam5.split(',')
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
        # Load historical limits for the process------------#
        if cpTapeW == dTape1 and cpLayerNo <= 1:        # '22mm'|'18mm',  1-40 | 41+
            ttUCL = float(One[2].strip("' "))           # Strip out the element of the list
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
            ttUCL = float(Two[2].strip("' "))           # Strip out the element of the list
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
            ttUCL = float(Thr[2].strip("' "))           # Strip out the element of the list
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
            ttUCL = float(For[2].strip("' "))           # Strip out the element of the list
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
            ttUCL = float(Fiv[2].strip("' "))           # Strip out the element of the list
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
        ttPerf = '$Cp_{k' + str(ttSize) + '}$'          # Using Automatic group Mean
        ttlabel = 'Cp'

    # ------------------------------------[End of Tape Temperature Abstraction]
    label = ttk.Label(root,
                      text='Tape Temperature [TT] - [' + pType + ' Mode] - ' + strftime("%a, %d %b %Y", gmtime()),
                      font=LARGE_FONT)
    label.pack(pady=10, padx=10)

    # Define Axes ---------------------#
    fig = Figure(figsize=(25, 13), dpi=100)
    # fig = Figure(figsize=(self.winfo_screenwidth(), self.winfo_screenheight()), dpi=100)
    fig.subplots_adjust(left=0.03, bottom=0.02, right=0.99, top=0.976, hspace=0.14, wspace=0.195)
    a1 = fig.add_subplot(2, 6, (1, 3))                        # xbar plot
    a2 = fig.add_subplot(2, 6, (7, 9))                        # s bar plot
    a3 = fig.add_subplot(2, 6, (4, 12))                       # void mapping profile

    # Declare Plots attributes -----------------------------[]
    plt.rcParams.update({'font.size': 7})
    # Calibrate limits for X-moving Axis -------------------#
    YScale_minTT, YScale_maxTT = ttLSL - 8.5, ttUSL + 8.5   # Roller Force
    sBar_minTT, sBar_maxTT = sLCLtt - 80, sUCLtt + 80       # Calibrate Y-axis for S-Plot
    window_Xmin, window_Xmax = 0, (int(ttSize) + 3)         # windows view = visible data points
    # ----------------------------------------------------------#
    YScale_minRM, YScale_maxRM = 0, pExLayer                # Valid layer number
    window_XminRM, window_XmaxRM = 0, pLength               # Get details from SCADA PIpe Recipe TODO[1]

    # Real-Time Parameter according to updated requirements -# 07/Feb/2025
    T1 = WON + '_TT'  # Tape Temperature
    T2 = WON + '_RM'  # Ramp Profile Mapping
    # -------------------------------------------------------#
    # Declare Plots attributes ------------------------------#
    a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
    a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")

    a1.set_title('Tape Temperature [XBar]', fontsize=12, fontweight='bold')
    a2.set_title('Tape Temperature [StDev]', fontsize=12, fontweight='bold')
    a3.set_title('Ramp Mapping Profile - [RMP]', fontsize=12, fontweight='bold')
    a3.set_facecolor("blue")            # set background color to blue
    zoom_factory(a3)                    # Allow plot's image  zooming

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

    # ---------------------------------------------------------[]
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
    def synchronousTT(ttSize, ttgType, fetchT):
        fetch_no = str(fetchT)                                  # entry value in string sql syntax

        # Obtain Volatile Data from PLC Host Server ---------------------------[]
        if not inUseAlready:                                    # Load CommsPlc class once
            import CommsSql as q
            q.DAQ_connect(1, 0)
        else:
            con_tt = conn.cursor()
        # Evaluate conditions for SQL Data Fetch ------------------------------[A]
        """
        Load watchdog function with synchronous function every seconds
        """

        # Initialise RT variables ---[]
        autoSpcRun = True
        autoSpcPause = False
        import keyboard                                         # for temporary use

        # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
        sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
        # Define PLC/SMC error state -------------------------------------------#

        while True:
            # print('Indefinite looping...')
            if UsePLC_DBS:                                      # Not Using PLC Data
                import plcArrayRLmethodTT as pdA                # DrLabs optimization method

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
                    ttData = pdA.paramDataRequest(T1, ttSize, ttgType, fetch_no)

            else:
                import sqlArrayRLmethodTT as ptt

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
                    ttData = ptt.sqlexec(ttSize, ttgType, con_tt, T1, fetchT)
                    print("Visualization in Play Mode...")
                print('\nUpdating....')

                # ------ Inhibit iteration ----------------------------------------------------------[]
                """
                # Set condition for halting real-time plots in watchdog class -----------------------[]
                """
                # TODO --- values for inhibiting the SQL processing
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    con_tt.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

        return ttData

    # -------------------------------------[A]
    def synchronousRM(smp_Sz, smp_St, fetchT):
        fetch_no = str(fetchT)                                  # entry value in string sql syntax

        # Obtain Volatile Data from PLC Host Server ---------------------------[]
        con_rm = conn.cursor()

        # Evaluate conditions for SQL Data Fetch ------------------------------[A]
        """
        Load watchdog function with synchronous function every seconds
        """
        # Initialise RT variables ---[]
        autoSpcRun = True
        autoSpcPause = False
        import keyboard                                         # for temporary use

        # TODO ----------------------[]
        # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
        sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
        # Define PLC/SMC error state -------------------------------------------#

        while True:
            # Latch on SQL Query only a
            import sqlArrayRLmethodRM as srm                    # DrLabs optimization method

            inProgress = False                                  # True for RetroPlay mode
            print('\nAsynchronous controller activated...')

            if not sysRun:
                sysRun, msctcp, msc_rt = wd.autoPausePlay()     # Retrieve MSC from Watchdog
            print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

            # Get list of relevant SQL Tables using conn() --------------------[]
            if keyboard.is_pressed("Ctrl"):                     # Terminate file-fetch
                print('\nProduction is pausing...')
                if not autoSpcPause:
                    autoSpcRun = not autoSpcRun
                    autoSpcPause = True
                    print("\nVisualization in Paused Mode...")
                else:
                    autoSpcPause = False
                    con_rm.close()
                print('SQL End of File, connection closes after 30 mins...')
                time.sleep(60)
                continue

            else:
                RAMP = srm.sqlexec(smp_Sz, smp_St, con_rm, T2, fetchT)  # perform DB connections
                print('\nUpdating....')

            # ------ Inhibit iteration ----------------------------------------------------------[]
            """
            # Set condition for halting real-time plots in watchdog class ---------------------
            """
            # TODO --- values for inhibiting the SQL processing
            if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                con_rm.close()
                print('SQL End of File, connection closes after 30 mins...')
                time.sleep(60)
                continue
            else:
                print('\nUpdating....')

        return RAMP
    # ================== End of synchronous Method ==========================
    def asynchronousTT(db_freq):
        timei = time.time()  # start timing the entire loop

        # Bistream Data Pooling Method ---------------------#
        ttData = synchronousTT(ttSize, ttgType, db_freq)    # data loading functions
        rmData = synchronousRM(ttSize, ttgType, db_freq)

        # Initialise colum heads ---------------------------#
        df3 = pd.DataFrame(rmData, columns=['CumulativeRamp', 'SampleDistance'])
        RAMP = [df3['CumulativeRamp'], df3['SampleDistance']]
        # --------------------------------------------------#
        import VarSQLrm as rm  # load SQL variables column names |

        # viz_cycle = 150
        g1 = qrm.validCols('RM')                # Construct Data Column selSqlColumnsTFM.py
        df0 = pd.DataFrame(rmData, columns=g1)  # Import into python Dataframe
        RM = rm.loadProcesValues(df0)           # Join data values under dataframe

        if UsePLC_DBS == 1:
            import VarPLCtt as tt
            viz_cycle = 10

            # Call synchronous data function ---------------[]
            columns = qtt.validCols(T1)                    # Load defined valid columns for PLC Data
            df1 = pd.DataFrame(ttData, columns=columns)    # Include table data into python Dataframe
            TT = tt.loadProcesValues(df1)                  # Join data values under dataframe
        else:
            import VarSQLtt as tt                          # load SQL variables column names | rfVarSQL

            viz_cycle = 150
            g1 = qtt.validCols(T1)                          # Construct Data Column selSqlColumnsTFM.py
            df1 = pd.DataFrame(ttData, columns=g1)          # Import into python Dataframe
            TT = tt.loadProcesValues(df1)                  # Join data values under dataframe

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
        # --------- Ramp Profile ---------
        im42.set_xdata(np.arange(db_freq))  # TODO - cross check with freq counter
        im43.set_xdata(np.arange(db_freq))
        im44.set_xdata(np.arange(db_freq))
        im45.set_xdata(np.arange(db_freq))

        # X Plot Y-Axis data points for XBar --------------------------------------------[  # Ring 1 ]
        im10.set_ydata((TT[0]).rolling(window=ttSize, min_periods=1).mean()[0:db_freq])  # head 1
        im11.set_ydata((TT[1]).rolling(window=ttSize, min_periods=1).mean()[0:db_freq])  # head 2
        im12.set_ydata((TT[2]).rolling(window=ttSize, min_periods=1).mean()[0:db_freq])  # head 3
        im13.set_ydata((TT[3]).rolling(window=ttSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 1 ---------#
        mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(ttHL, ttSize, 'TT')
        # ---------------------------------------#
        im14.set_ydata((TT[4]).rolling(window=ttSize, min_periods=1).mean()[0:db_freq])  # head 1
        im15.set_ydata((TT[5]).rolling(window=ttSize, min_periods=1).mean()[0:db_freq])  # head 2
        im16.set_ydata((TT[6]).rolling(window=ttSize, min_periods=1).mean()[0:db_freq])  # head 3
        im17.set_ydata((TT[7]).rolling(window=ttSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 2 ---------#
        mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(ttHL, ttSize, 'TT')
        # ---------------------------------------#
        im18.set_ydata((TT[8]).rolling(window=ttSize, min_periods=1).mean()[0:db_freq])  # head 1
        im19.set_ydata((TT[9]).rolling(window=ttSize, min_periods=1).mean()[0:db_freq])  # head 2
        im20.set_ydata((TT[10]).rolling(window=ttSize, min_periods=1).mean()[0:db_freq])  # head 3
        im21.set_ydata((TT[11]).rolling(window=ttSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 3 ---------#
        mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(ttHL, ttSize, 'TT')
        # ---------------------------------------#
        im22.set_ydata((TT[12]).rolling(window=ttSize, min_periods=1).mean()[0:db_freq])  # head 1
        im23.set_ydata((TT[13]).rolling(window=ttSize, min_periods=1).mean()[0:db_freq])  # head 2
        im24.set_ydata((TT[14]).rolling(window=ttSize, min_periods=1).mean()[0:db_freq])  # head 3
        im25.set_ydata((TT[15]).rolling(window=ttSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 4 ---------#
        mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(ttHL, ttSize, 'TT')
        # ---------------------------------------#
        # S Plot Y-Axis data points for StdDev ----------------------------------------
        im26.set_ydata((TT[0]).rolling(window=ttSize, min_periods=1).std()[0:db_freq])
        im27.set_ydata((TT[1]).rolling(window=ttSize, min_periods=1).std()[0:db_freq])
        im28.set_ydata((TT[2]).rolling(window=ttSize, min_periods=1).std()[0:db_freq])
        im29.set_ydata((TT[3]).rolling(window=ttSize, min_periods=1).std()[0:db_freq])

        im30.set_ydata((TT[4]).rolling(window=ttSize, min_periods=1).std()[0:db_freq])
        im31.set_ydata((TT[5]).rolling(window=ttSize, min_periods=1).std()[0:db_freq])
        im32.set_ydata((TT[6]).rolling(window=ttSize, min_periods=1).std()[0:db_freq])
        im33.set_ydata((TT[7]).rolling(window=ttSize, min_periods=1).std()[0:db_freq])

        im34.set_ydata((TT[8]).rolling(window=ttSize, min_periods=1).std()[0:db_freq])
        im35.set_ydata((TT[9]).rolling(window=ttSize, min_periods=1).std()[0:db_freq])
        im36.set_ydata((TT[10]).rolling(window=ttSize, min_periods=1).std()[0:db_freq])
        im37.set_ydata((TT[11]).rolling(window=ttSize, min_periods=1).std()[0:db_freq])

        im38.set_ydata((TT[12]).rolling(window=ttSize, min_periods=1).std()[0:db_freq])
        im39.set_ydata((TT[13]).rolling(window=ttSize, min_periods=1).std()[0:db_freq])
        im40.set_ydata((TT[14]).rolling(window=ttSize, min_periods=1).std()[0:db_freq])
        im41.set_ydata((TT[15]).rolling(window=ttSize, min_periods=1).std()[0:db_freq])

        # Compute entire Process Capability -----------#
        if not ttHL:
            mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLb, ppT, pkT, xline, sline = tq.tAutoPerf(ttSize, mnA, mnB,
                                                                                                  mnC, mnD, sdA,
                                                                                                  sdB, sdC, sdD)
        else:
            xline, sline = ttMean, ttDev
            mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLba, ppT, pkT = tq.tManualPerf(mnA, mnB, mnC, mnD, sdA, sdB,
                                                                                       sdC, sdD, ttUSL, ttLSL, ttUCL,
                                                                                       ttLCL)

        # -------------- Ramp Data --------------------------------#
        im42.set_ydata((RM[0]).rolling(window=ttSize, min_periods=1).mean()[0:db_freq * 10 / db_freq])  # Cumulative
        im43.set_ydata((RM[1]).rolling(window=ttSize, min_periods=1).mean()[0:db_freq * 10 / db_freq])  # Nominal
        im44.set_ydata((RM[3])[0:db_freq])  # Ring 3
        im45.set_ydata((RM[4])[0:db_freq])  # Ring 4

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

        # Setting up the parameters for moving windows Axes ---------------------------------[]
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

        ani = FuncAnimation(fig, asynchronousTT, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                            blit=False)
        plt.tight_layout()
        plt.show()

    # Update Canvas -----------------------------------------------------[]
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack()

    root.mainloop()


# -------------------------------------------------------------------------[]
def stProcessParam(vCounter, pType):
    # def LaserPressure(hMeanC, hDevC, hLCLc, hUCLc, hUSLc, hLSLc, dLCLc, dUCLc, plabel, PPerf, pPos, layer, eSMC):
    root = Tk()
    root.title('mPipe Production: Synchronous SPC - Viz: ' + vCounter)
    root.geometry("1800x800")

    # Load Quality Historical Values ---------------------------------------[]
    if pRecipe == 'DNV':
        stSize, stgType, stSEoL, stSEoP, stHL, stAL, stFO, stParam1, stParam2, stParam3, stParam4, stParam5 = dnv.decryptpProcessLim(
            WON, 'ST')
    else:
        stSize, stgType, stSEoL, stSEoP, stHL, stAL, stFO, stParam1, stParam2, stParam3, stParam4, stParam5 = mgm.decryptpProcessLim(
            WON, 'ST')
    # Break down each element to useful list -----------[Substrate Temperature]

    if stHL and stParam1 and stParam2 and stParam3 and stParam4 and stParam5:
        stPerf = '$Pp_{k' + str(stSize) + '}$'  # Using estimated or historical Mean
        stlabel = 'Pp'
        # -------------------------------
        One = stParam1.split(',')  # split into list elements
        Two = stParam2.split(',')
        Thr = stParam3.split(',')
        For = stParam4.split(',')
        Fiv = stParam5.split(',')
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
        # Load historical limits for the process------------#
        if cpTapeW == dTape1 and cpLayerNo <= 1:  # '22mm'|'18mm',  1-40 | 41+
            stUCL = float(One[2].strip("' "))  # Strip out the element of the list
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
            stUCL = float(Two[2].strip("' "))  # Strip out the element of the list
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
            stUCL = float(Thr[2].strip("' "))  # Strip out the element of the list
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
            stUCL = float(For[2].strip("' "))  # Strip out the element of the list
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
            stUCL = float(Fiv[2].strip("' "))  # Strip out the element of the list
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
        stPerf = '$Cp_{k' + str(stSize) + '}$'  # Using Automatic group Mean
        stlabel = 'Cp'

    label = ttk.Label(root,
                      text='Substrate Temp [ST] - [' + pType + ' Mode] - ' + strftime("%a, %d %b %Y", gmtime()),
                      font=LARGE_FONT)
    label.pack(pady=10, padx=10)

    # Define Axes ---------------------#
    fig = Figure(figsize=(25, 13), dpi=100)

    # fig = Figure(figsize=(self.winfo_screenwidth(), self.winfo_screenheight()), dpi=100)
    fig.subplots_adjust(left=0.03, bottom=0.02, right=0.99, top=0.976, hspace=0.14, wspace=0.195)
    a1 = fig.add_subplot(2, 4, (1, 3))
    a2 = fig.add_subplot(2, 4, (5, 7))
    a3 = fig.add_subplot(2, 4, (4, 8))

    # Declare Plots attributes -----------------------------[]
    plt.rcParams.update({'font.size': 7})
    # Calibrate limits for X-moving Axis -------------------#
    YScale_minST, YScale_maxST = stLSL - 8.5, stUSL + 8.5       # Substrate Temp
    sBar_minST, sBar_maxST = sLCLst - 80, sUCLst + 80           # Calibrate Y-axis for S-Plot
    window_Xmin, window_Xmax = 0, (int(stSize) + 3)             # windows view = visible data points

    # Load SQL Query Table -------------------------------------#
    T1 = WON + '_ST'  # Identify Table
    # ----------------------------------------------------------#

    # Declare Plots attributes --------------------------------#
    a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
    a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
    a1.set_title('Substrate Temperature [XBar]', fontsize=12, fontweight='bold')
    a2.set_title('Substrate Temperature [StDev]', fontsize=12, fontweight='bold')
    a1.grid(color="0.5", linestyle='-', linewidth=0.5)
    a2.grid(color="0.5", linestyle='-', linewidth=0.5)
    a1.legend(loc='upper right', title='Substrate Temp')
    a2.legend(loc='upper right', title='Sigma curve')
    # Initialise runtime limits --------------------------------#
    a1.set_ylim([YScale_minST, YScale_maxST], auto=True)
    a1.set_xlim([window_Xmin, window_Xmax])
    # ----------------------------------------------------------#
    a2.set_ylim([sBar_minST, sBar_maxST], auto=True)
    a2.set_xlim([window_Xmin, window_Xmax])

    # ---------------------------------------------------------[]
    a3.cla()
    a3.get_yaxis().set_visible(False)
    a3.get_xaxis().set_visible(False)

    # ----------------------------------------------------------------[]
    # Define Plot area and axes -
    # ----------------------------------------------------------------#
    im10, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R1H1)')
    im11, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R1H2)')
    im12, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R1H3)')
    im13, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R1H4)')
    im14, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im15, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im16, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im17, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')

    im18, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R2H1)')
    im19, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R2H2)')
    im20, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R2H3)')
    im21, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R2H4)')
    im22, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im23, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im24, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im25, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')

    im26, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R3H1)')
    im27, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R3H2)')
    im28, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R3H3)')
    im29, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R3H4)')
    im30, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im31, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im32, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im33, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')

    im34, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R4H1)')
    im35, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R4H2)')
    im36, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R4H3)')
    im37, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R4H4)')
    im38, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im39, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im40, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im41, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')

    # Statistical Feed --------------------------------[]:
    a3.text(0.466, 0.945, 'Performance Feed - ST', fontsize=16, fontweight='bold', ha='center', va='center',
            transform=a3.transAxes)
    # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
    rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
    rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
    a3.add_patch(rect1)
    a3.add_patch(rect2)
    # ------- Process Performance Pp (the spread)---------------------
    a3.text(0.145, 0.804, stlabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.328, 0.658, '#Pp', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.650, 0.820, 'Ring ' + stlabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
    a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
    # ------- Process Performance Ppk (Performance)--------------------#
    a3.text(0.145, 0.403, stPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.328, 0.282, '#Ppk', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.640, 0.420, 'Ring ' + stPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
    # -----------------------------------------------------------------#
    a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
    # ----- Pipe Position and SMC Status -----
    a3.text(0.080, 0.090, 'Pipe Position: ' + pPos + '    Processing Layer #' + layer, fontsize=12, ha='left',
            transform=a3.transAxes)
    a3.text(0.080, 0.036, 'SMC Status: ' + eSMC, fontsize=12, ha='left', transform=a3.transAxes)

    # ---------------- EXECUTE SYNCHRONOUS METHOD -----------------------------#
    def synchronousST(stSize, stgType, fetchT):
        fetch_no = str(fetchT)  # entry value in string sql syntax

        # Obtain Volatile Data from PLC Host Server ---------------------------[]
        if not inUseAlready:                # Load CommsPlc class once
            import CommsSql as q
            q.DAQ_connect(1, 0)
        else:
            con_st = conn.cursor()

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
            if UsePLC_DBS:  # Using PLC Data
                import plcArrayRLmethodST as pdB  # DrLabs optimization method

                inProgress = True  # True for RetroPlay mode
                print('\nAsynchronous controller activated...')
                print('DrLabs' + "' Runtime Optimisation is Enabled!")

                if not sysRun:
                    sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve M.State from Watchdog
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
                    stData = pdB.paramDataRequest('ST', stSize, stgType, fetch_no)
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
                    stData = pst.sqlexec(stSize, stgType, con_st, T1, fetchT)
                    print("Visualization in Play Mode...")
                print('\nUpdating....')

                # ------ Inhibit iteration ----------------------------------------------------------[]
                """
                # Set condition for halting real-time plots in watchdog class -----------------------[]
                """
                # TODO --- values for inhibiting the SQL processing
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    con_st.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

        return stData

    # ================== End of synchronous Method ==========================
    def asynchronousST(db_freq):
        timei = time.time()  # start timing the entire loop

        # Call data loader Method---------------------------#
        rpData = synchronousST(stSize, stgType, db_freq)    # data loading functions
        # --------------------------------------------------#

        if UsePLC_DBS == 1:
            import VarPLCst as st

            viz_cycle = 10
            # Call synchronous data function ---------------[]
            columns = qst.validCols(T1)                    # Load defined valid columns for PLC Data
            df1 = pd.DataFrame(rpData, columns=columns)    # Include table data into python Dataframe
            ST = st.loadProcesValues(df1)                  # Join data values under dataframe

        else:
            import VarSQLst as st                          # load SQL variables column names | rfVarSQL

            viz_cycle = 150
            g1 = qst.validCols(T1)                         # Construct Data Column selSqlColumnsTFM.py
            df1 = pd.DataFrame(rpData, columns=g1)         # Import into python Dataframe
            ST = st.loadProcesValues(df1)                  # Join data values under dataframe

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
        im10.set_ydata((ST[0]).rolling(window=stSize, min_periods=1).mean()[0:db_freq])  # head 1
        im11.set_ydata((ST[1]).rolling(window=stSize, min_periods=1).mean()[0:db_freq])  # head 2
        im12.set_ydata((ST[2]).rolling(window=stSize, min_periods=1).mean()[0:db_freq])  # head 3
        im13.set_ydata((ST[3]).rolling(window=stSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 1 ---------#
        mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(stHL, stSize, 'ST')
        # ---------------------------------------#
        im14.set_ydata((ST[4]).rolling(window=stSize, min_periods=1).mean()[0:db_freq])  # head 1
        im15.set_ydata((ST[5]).rolling(window=stSize, min_periods=1).mean()[0:db_freq])  # head 2
        im16.set_ydata((ST[6]).rolling(window=stSize, min_periods=1).mean()[0:db_freq])  # head 3
        im17.set_ydata((ST[7]).rolling(window=stSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 2 ---------#
        mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(stHL, stSize, 'ST')
        # ---------------------------------------#
        im18.set_ydata((ST[8]).rolling(window=stSize, min_periods=1).mean()[0:db_freq])  # head 1
        im19.set_ydata((ST[9]).rolling(window=stSize, min_periods=1).mean()[0:db_freq])  # head 2
        im20.set_ydata((ST[10]).rolling(window=stSize, min_periods=1).mean()[0:db_freq])  # head 3
        im21.set_ydata((ST[11]).rolling(window=stSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 3 ---------#
        mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(stHL, stSize, 'ST')
        # ---------------------------------------#
        im22.set_ydata((ST[12]).rolling(window=stSize, min_periods=1).mean()[0:db_freq])  # head 1
        im23.set_ydata((ST[13]).rolling(window=stSize, min_periods=1).mean()[0:db_freq])  # head 2
        im24.set_ydata((ST[14]).rolling(window=stSize, min_periods=1).mean()[0:db_freq])  # head 3
        im25.set_ydata((ST[15]).rolling(window=stSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 4 ---------#
        mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(stHL, stSize, 'ST')
        # ---------------------------------------#
        # S Plot Y-Axis data points for StdDev ----------------------------------------
        im26.set_ydata((ST[0]).rolling(window=stSize, min_periods=1).std()[0:db_freq])
        im27.set_ydata((ST[1]).rolling(window=stSize, min_periods=1).std()[0:db_freq])
        im28.set_ydata((ST[2]).rolling(window=stSize, min_periods=1).std()[0:db_freq])
        im29.set_ydata((ST[3]).rolling(window=stSize, min_periods=1).std()[0:db_freq])

        im30.set_ydata((ST[4]).rolling(window=stSize, min_periods=1).std()[0:db_freq])
        im31.set_ydata((ST[5]).rolling(window=stSize, min_periods=1).std()[0:db_freq])
        im32.set_ydata((ST[6]).rolling(window=stSize, min_periods=1).std()[0:db_freq])
        im33.set_ydata((ST[7]).rolling(window=stSize, min_periods=1).std()[0:db_freq])

        im34.set_ydata((ST[8]).rolling(window=stSize, min_periods=1).std()[0:db_freq])
        im35.set_ydata((ST[9]).rolling(window=stSize, min_periods=1).std()[0:db_freq])
        im36.set_ydata((ST[10]).rolling(window=stSize, min_periods=1).std()[0:db_freq])
        im37.set_ydata((ST[11]).rolling(window=stSize, min_periods=1).std()[0:db_freq])

        im38.set_ydata((ST[12]).rolling(window=stSize, min_periods=1).std()[0:db_freq])
        im39.set_ydata((ST[13]).rolling(window=stSize, min_periods=1).std()[0:db_freq])
        im40.set_ydata((ST[14]).rolling(window=stSize, min_periods=1).std()[0:db_freq])
        im41.set_ydata((ST[15]).rolling(window=stSize, min_periods=1).std()[0:db_freq])
        # Compute entire Process Capability -----------#
        if not stHL:
            mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLc, dLCLc, ppT, pkT, xline, sline = tq.tAutoPerf(stSize, mnA, mnB,
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

        ani = FuncAnimation(fig, asynchronousST, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                            blit=False)
        plt.tight_layout()
        plt.show()

    # Update Canvas -----------------------------------------------------[]
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack()

    root.mainloop()


# -------------------------------------------------------------------------[]
def tgProcessParam(vCounter, pType):
    # def LaserPressure(hMeanC, hDevC, hLCLc, hUCLc, hUSLc, hLSLc, dLCLc, dUCLc, plabel, PPerf, pPos, layer, eSMC):
    root = Tk()
    root.title('mPipe Production: Synchronous SPC - Viz: ' + vCounter)
    root.geometry("1800x800")

    # Load Quality Historical Values ---------------------------------------[]
    if pRecipe == 'DNV':
        tgSize, tggType, tgSEoL, tgSEoP, tgHL, tgAL, tgtFO, tgParam1, dud2, dud3, dud4, dud5 = dnv.decryptpProcessLim(WON, 'TG')
    else:
        tgSize, tggType, tgSEoL, tgSEoP, tgHL, tgAL, tgtFO, tgParam1, dud2, dud3, dud4, dud5 = mgm.decryptpProcessLim(WON,
                                                                                                                'TG')
# Break down each element to useful list ----------------[Winding Speed]

    # Break down each element to useful list ---------------------[Tape Gap]
    if tgHL and tgParam1:
        tgPerf = '$Pp_{k' + str(tgSize) + '}$'  # Estimated or historical Mean
        tglabel = 'Pp'
        # -------------------------------
        tgOne = tgParam1.split(',')  # split into list elements
        dTapetg = tgOne[1].strip("' ")  # defined Tape Width
        dLayer = tgOne[10].strip("' ")  # Defined Tape Layer

        # Load historical limits for the process----#
        tgUCL = float(tgOne[2].strip("' "))  # Strip out the element of the list
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
    else:  # Computes Shewhart constants (Automatic Limits)
        tgUCL = 0
        tgLCL = 0
        tgMean = 0
        tgDev = 0
        sUCLtg = 0
        sLCLtg = 0
        tgUSL = 0
        tgLSL = 0
        tgPerf = '$Cp_{k' + str(tgSize) + '}$'  # Using Automatic group Mean
        tglabel = 'Cp'

    # ------------------------------------[End of Winding Speed Abstraction]
    label = ttk.Label(root,
                      text='Tape Gap Polarisation [TG] - [' + pType + ' Mode] - ' + strftime("%a, %d %b %Y", gmtime()),
                      font=LARGE_FONT)
    label.pack(pady=10, padx=10)

    # Define Axes ---------------------#
    fig = Figure(figsize=(25, 13), dpi=100)
    fig.subplots_adjust(left=0.03, bottom=0.02, right=0.99, top=0.976, hspace=0.14, wspace=0.195)
    # ----------------------------------[]
    a1 = fig.add_subplot(2, 6, (1, 3))                      # xbar plot
    a3 = fig.add_subplot(2, 6, (7, 9))                      # s bar plot
    a4 = fig.add_subplot(2, 6, (4, 12))                     # void mapping profile

    # Declare Plots attributes ----------------------------[]
    plt.rcParams.update({'font.size': 7})
    # Calibrate limits for X-moving Axis -------------------#
    YScale_minTG, YScale_maxTG = tgLSL - 8.5, tgUSL + 8.5   # Roller Force
    sBar_minTG, sBar_maxTG = sLCLtg - 80, sUCLtg + 80       # Calibrate Y-axis for S-Plot
    window_Xmin, window_Xmax = 0, 45              # windows view = visible data points
    # ------------------------------------------------------#
    YScale_minVM, YScale_maxVM = 0, 80                      # Valid Void Mapping
    window_XminVM, window_XmaxVM = 0, 100000                # Get details from SCADA PIpe Recipe TODO[1]

    # Real-Time Parameter according to updated requirements ----# 07/Feb/2025
    T1 = WON + '_TG'    # Tape Placement
    T2 = WON + '_RM'    # Void Mapping
    # ----------------------------------------------------------#

    # Initialise runtime limits --------------------------------#
    a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
    a3.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")

    a1.set_title('Tape Gap Polarisation [XBar]', fontsize=12, fontweight='bold')
    a3.set_title('Tape Gap Polarisation [SDev]', fontsize=12, fontweight='bold')
    a4.set_title('Tape Gap Mapping Profile', fontsize=12, fontweight='bold')

    a4.set_ylabel("2D - Staked Layer Void Mapping")
    a4.set_xlabel("Sample Distance (mt)")
    a4.set_facecolor("green")  # set face color for Ramp mapping volume
    zoom_factory(a4)  # allow zooming on image plot

    a1.grid(color="0.5", linestyle='-', linewidth=0.5)
    a3.grid(color="0.5", linestyle='-', linewidth=0.5)
    a4.grid(color="0.5", linestyle='-', linewidth=0.5)

    a1.legend(loc='upper right', title='Tape Gap Polarisation')
    a3.legend(loc='upper right', title='Sigma Plots')
    # a4.legend(loc='upper right', title='Void Map Profile')
    # ------------------------------------------------------[for Ramp Plot]
    colors = np.random.randint(50, 101, size=(367))  # TODO -- obtain length of element dynamically
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

    # ---------------- EXECUTE SYNCHRONOUS METHOD -----------------------------#
    def synchronousTG(tgSize, tggType, fetchT):
        fetch_no = str(fetchT)                  # entry value in string sql syntax

        # Obtain Volatile Data from PLC Host Server ---------------------------[]
        if not inUseAlready:                # Load CommsPlc class once
            import CommsSql as q
            con_tg = q.DAQ_connect(1, 0)
        else:
            con_tg = conn.cursor()

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
            if UsePLC_DBS:  # Not Using PLC Data
                import plcArrayRLmethodTG as pdC                # DrLabs optimization method

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
                    # Get list of relevant SQL Tables using conn() --------------------[]
                    # tgData = pdC.sqlexec(smp_Sz, smp_St, con_tg, T1, fetchT)  # get details from PLC array
                    tgData = q.paramDataRequest('TG', tgSize, tggType, fetch_no)

            else:
                import sqlArrayRLmethodTG as pdC

                inProgress = False                                  # False for Real-time mode
                print('\nSynchronous controller activated...')

                if not sysRun:
                    sysRun, msctcp, msc_rt = wd.autoPausePlay()     # Retrieve MSC from Watchdog
                print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

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
                    tgData = pdC.sqlexec(tgSize, tggType, con_tg, T1, fetchT)
                    print("Visualization in Play Mode...")
                print('\nUpdating....')

                # ------ Inhibit iteration ----------------------------------------------------------[]
                """
                # Set condition for halting real-time plots in watchdog class -----------------------[]
                """
                # TODO --- values for inhibiting the SQL processing
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    con_tg.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

        return tgData

    # ================== End of synchronous Method ==========================
    def synchronousMP(tgSize, tggType, fetchT):
        fetch_no = str(fetchT)                                 # start timing the entire loop

        # Obtain Data from SQL Repo ---------------------------[]
        con_vm = conn.cursor()  # Void mapping

        """
        Load watchdog function with synchronous function every seconds
        """
        # Initialise variables ---[]
        autoSpcRun = True
        autoSpcPause = False
        import keyboard  # for temporary use

        # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
        sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
        # Define PLC/SMC error state -------------------------------------------#

        while True:
            import sqlArrayRLmethodVM as svm                    # DrLabs optimization method

            inProgress = False                                  # True for RetroPlay mode
            print('\nAsynchronous controller activated...')

            if not sysRun:
                sysRun, msctcp, msc_rt = wd.autoPausePlay()     # Retrieve MSC from Watchdog

            if keyboard.is_pressed("Ctrl"):                     # Terminate file-fetch
                print('\nProduction is pausing...')
                if not autoSpcPause:
                    autoSpcRun = not autoSpcRun
                    autoSpcPause = True
                    # play(error)                                               # Pause mode with audible Alert
                    print("\nVisualization in Paused Mode...")
                else:
                    autoSpcPause = False
                    con_vm.close()
                print('SQL End of File, connection closes after 30 mins...')
                time.sleep(60)
                vm_profile = 0
                continue

            else:
                vm_profile = svm.sqlexec(tgSize, tggType, con_vm, T2, fetchT)  # perform DB connections
                print("Visualization in Play Mode...")
            print('\nUpdating....')

            # ------ Inhibit iteration ----------------------------------------------------------[]
            """
            # Set condition for halting real-time plots in watchdog class ---------------------
            """
            # TODO --- values for inhibiting the SQL processing
            if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                con_vm.close()
                print('SQL End of File, connection closes after 30 mins...')
                time.sleep(60)
                continue
            else:
                print('\nUpdating....')
        return vm_profile

    # ================== End of synchronous Method ==========================

    def asynchronousTG(db_freq):
        global gap_vol
        timei = time.time()  # start timing the entire loop

        # Bi-stream Data Pooling Method ----------------------#
        tgData = synchronousTG(tgSize, tggType, db_freq)  # PLC synchronous Data loading method1
        vmData = synchronousMP(tgSize, tggType, db_freq)  # Dr Labs Method for Void Mapping Profile
        # ----------------------------------------------------#

        if UsePLC_DBS == 1:
            import VarPLCtg as tg

            viz_cycle = 10
            columns = qtg.validCols('TG')           # Load defined valid columns for PLC Data
            df1 = pd.DataFrame(tgData, columns=columns)  # Include table data into python Dataframe
            TG = tg.loadProcesValues(df1)           # Join data values under dataframe

        else:
            import VarSQLtg as tg                   # load SQL variables column names | rfVarSQL

            viz_cycle = 150
            g1 = qtg.validCols('TG')                # Construct Data Column selSqlColumnsTFM.py
            df1 = pd.DataFrame(tgData, columns=g1)  # Import into python Dataframe
            TG = tg.loadProcesValues(df1)           # Join data values under dataframe

        # Compulsory VoidMap function call -- SQL loader -[B]
        import VarSQLvm as vm                       # load SQL variables column names | rfVarSQL

        viz_cycle = 150
        g1 = qvm.validCols('VM')                    # Construct Data Column selSqlColumnsTFM.py
        df1 = pd.DataFrame(vmData, columns=g1)      # Import into python Dataframe
        VM = vm.loadProcesValues(df1)               # Join data values under dataframe

        print('\nDataFrame Content', df1.head(10))  # Preview Data frame head
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
        # X Plot Y-Axis data points for XBar -------------------------------------------[# Channels]
        im10.set_ydata((TG[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
        im11.set_ydata((TG[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
        im12.set_ydata((TG[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
        im13.set_ydata((TG[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
        # ------ Evaluate Pp for Segments ---------#
        mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(tgHL, smp_Sz, 'TG')
        # ---------------------------------------#
        im14.set_ydata((TG[4]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
        im15.set_ydata((TG[5]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
        im16.set_ydata((TG[6]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
        im17.set_ydata((TG[7]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
        # ------ Evaluate Pp for Ring 2 ---------#
        mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(tgHL, smp_Sz, 'TG')

        # S Plot Y-Axis data points for StdDev ----------------------------------------[# S Bar Plot]
        im18.set_ydata((TG[0]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im19.set_ydata((TG[1]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im20.set_ydata((TG[2]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im21.set_ydata((TG[3]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])

        im22.set_ydata((TG[4]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im23.set_ydata((TG[5]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im24.set_ydata((TG[6]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im25.set_ydata((TG[7]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])

        if not tgHL:
            mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLd, dLCLd, ppT, pkT, xline, sline = tq.tAutoPerf(smp_Sz, mnA,
                                                                                                  mnB,
                                                                                                  0, 0, sdA,
                                                                                                  sdB, 0, 0)
        else:
            xline, sline = tgMean, tgDev
            mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLd, dLCLd, ppT, pkT = tq.tManualPerf(mnA, mnB, 0, 0, sdA, sdB,
                                                                                      0, 0, tgUSL, tgLSL, tgUCL,
                                                                                      tgLCL)
        # ---- Profile rolling Data Plot -------------
        pScount = VM[0]
        pCenter = VM[1]
        pAvgGap = VM[2]
        pMaxGap = VM[3]
        vLayerN = VM[4]
        sLength = VM[5]

        gap_vol = (pAvgGap / sLength) * 100  # Percentage Void

        # im26.set_ydata((vLayerN),(gap_vol) [0:db_freq])  # ------------------------------ Profile A
        a4.set_ydata((vLayerN), (gap_vol)[0:db_freq])

        # # Declare Plots attributes ------------------------------------------------------------[]
        # XBar Mean Plot
        a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
        a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 3 Sigma span (Purple)
        a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
        a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
        # ---------------------- sBar_minTG, sBar_maxTG -------[]
        # Define Legend's Attributes  ----
        a3.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
        a3.axhspan(dLCLd, dUCLd, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 1 Sigma Span
        a3.axhspan(dUCLd, sBar_maxTG, facecolor='#CCCCFF', edgecolor='#CCCCFF')  # 1 Sigma above the Mean
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

        ani = FuncAnimation(fig, asynchronousTG, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                            blit=False)
        plt.tight_layout()
        plt.show()

    # Update Canvas -----------------------------------------------------[]
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack()
    # Activate Matplot tools ------------------[Uncomment to activate]
    # toolbar = NavigationToolbar2Tk(canvas, self)
    # toolbar.update()
    # canvas._tkcanvas.pack(expand=True)

    root.mainloop()


def tpProcessParam(vCounter, pType):  # Tape Placement
    # def LaserPressure(hMeanC, hDevC, hLCLc, hUCLc, hUSLc, hLSLc, dLCLc, dUCLc, plabel, PPerf, pPos, layer, eSMC):
    root = Tk()
    root.title('mPipe Production: Synchronous SPC - Viz: ' + vCounter)
    root.geometry("1800x800")

    # Load metrics from config -----------------------------------[Tape Placement Error]
    if pRecipe == 'DNV':
        tpSize, tpgType, tpSEoL, tpSEoP, tpHL, tpAL, tptFO, tpParam1, dud2, dud3, dud4, dud5 = dnv.decryptpProcessLim(WON,
                                                                                                                'TP')
    else:
        tpSize, tpgType, tpSEoL, tpSEoP, tpHL, tpAL, tptFO, tpParam1, dud2, dud3, dud4, dud5 = mgm.decryptpProcessLim(WON,
                                                                                                                'TP')

    # Break down each element to useful list ---------------------[Tape Gap]

    if tpHL and tpParam1:
        tgPerf = '$Pp_{k' + str(tpSize) + '}$'                   # Estimated or historical Mean
        tglabel = 'Pp'
        # -------------------------------
        tpOne = tpParam1.split(',')                             # split into list elements
        dTapetp = tpOne[1].strip("' ")                          # defined Tape Width
        dLayer = tpOne[10].strip("' ")                          # Defined Tape Layer

        # Load historical limits for the process----------------#
        # if cpTapeW == dTapetg and cpLayerNo == range(1, 100):   # '*.*',  | *.*
        tpUCL = float(tpOne[2].strip("' "))                     # Strip out the element of the list
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
        tpPerf = '$Cp_{k' + str(tpSize) + '}$'  # Using Automatic group Mean
        tplabel = 'Cp'

    # -----------------------------------------------------[End of Tape Gap]
    label = ttk.Label(root,
                      text='Tape Placement Error [TP] - [' + pType + ' Mode] - ' + strftime("%a, %d %b %Y", gmtime()),
                      font=LARGE_FONT)
    label.pack(pady=10, padx=10)

    # Define Axes ---------------------#
    fig = Figure(figsize=(25, 13), dpi=100)
    fig.subplots_adjust(left=0.03, bottom=0.035, right=0.99, top=0.976, hspace=0.14, wspace=0.195)
    # ---------------------------------[]
    a1 = fig.add_subplot(2, 4, (1, 3))  # xbar plot
    a2 = fig.add_subplot(2, 4, (5, 7))  # s bar plot
    a3 = fig.add_subplot(2, 4, (4, 8))  # CPk/PPk Feed

    # Declare Plots attributes -----------------------------------------[]
    plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
    # Calibrate limits for X-moving Axis -----------------------#
    YScale_minTP, YScale_maxTP = tpLSL - 8.5, tpUSL + 8.5       # Roller Force
    sBar_minTP, sBar_maxTP = sLCLtp - 80, sUCLtp + 80           # Calibrate Y-axis for S-Plot
    window_Xmin, window_Xmax = 0, (int(tpSize) + 3)             # windows view = visible data points

    # ----------------------------------------------------------#
    # Real-Time Parameter according to updated requirements ----# 07/Feb/2025
    T1 = WON + '_TP'  # Tape Placement
    # ----------------------------------------------------------#

    # Declare Plots attributes --------------------------------#
    a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
    a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
    a1.set_title('Tape Placement [XBar]', fontsize=12, fontweight='bold')
    a2.set_title('Tape Placement [StDev]', fontsize=12, fontweight='bold')

    a2.yaxis.set_label_position("right")
    a2.set_ylabel("Cumulative & Average Tape Gap Measurement ")
    a2.set_xlabel("Progressive Layer")

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

    # Statistical Feed ------------------------------------------[]
    a3.text(0.466, 0.945, 'Performance Feed - TP', fontsize=15, fontweight='bold', ha='center', va='center',
            transform=a3.transAxes)
    # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
    rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
    rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
    a3.add_patch(rect1)
    a3.add_patch(rect2)
    # ------- Process Performance Pp (the spread)----------------[]
    a3.text(0.145, 0.804, tplabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.328, 0.658, '#Pp Value', fontsize=18, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.650, 0.820, 'Ring ' + tplabel, fontsize=12, ha='left', transform=a3.transAxes)
    a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
    # ------- Process Performance Ppk (Performance)--------------[]
    a3.text(0.145, 0.403, tpPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.328, 0.282, '#Ppk Value', fontsize=16, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.640, 0.420, 'Ring ' + tpPerf, fontsize=12, ha='left', transform=a3.transAxes)
    # -----------------------------------------------------------[]
    a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
    # ----- Pipe Position and SMC Status -----
    a3.text(0.080, 0.080, 'Pipe Position: ' + pPos + '\nProcessing Layer #' + layer, fontsize=12, ha='left',
            transform=a3.transAxes)
    a3.text(0.080, 0.036, 'SMC Status: ' + eSMC, fontsize=12, ha='left', transform=a3.transAxes)

    # ---------------- EXECUTE SYNCHRONOUS METHOD -----------------------------#
    def synchronousTP(tpSize, tpgType, fetchT):
        fetch_no = str(fetchT)          # entry value in string sql syntax

        # Obtain Volatile Data from PLC Host Server ---------------------------[]
        if not inUseAlready:            # Load CommsPlc class once
            import CommsSql as q
            q.DAQ_connect(1, 0)
        else:
            con_tp = conn.cursor()

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

                inProgress = True  # True for RetroPlay mode
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
                    # tgData = pdC.sqlexec(smp_Sz, smp_St, con_tg, T1, fetchT)  # get details from PLC array
                    tpData = stp.paramDataRequest('TP', tpSize, tpgType, fetch_no)

            else:
                import sqlArrayRLmethodTP as stp

                inProgress = False  # False for Real-time mode
                print('\nSynchronous controller activated...')

                if not sysRun:
                    sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve MSC from Watchdog
                print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

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
                    tpData = stp.sqlexec(tpSize, tpgType, con_tp, T1, fetchT)
                    print("Visualization in Play Mode...")
                print('\nUpdating....')

                # ------ Inhibit iteration ----------------------------------------------------------[]
                """
                # Set condition for halting real-time plots in watchdog class -----------------------[]
                """
                # TODO --- values for inhibiting the SQL processing
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    con_tp.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

        return tpData

    # ================== End of synchronous Method ==========================

    def asynchronousTP(db_freq):
        timei = time.time()  # start timing the entire loop

        # Call data loader Method---------------------------#
        tpData = synchronousTP(tpSize, tpgType, db_freq)  # data loading functions
        # --------------------------------------------------#

        if UsePLC_DBS == 1:
            import VarPLCtp as tp

            viz_cycle = 10
            # Call synchronous data function ---------------[]
            columns = qtp.validCols(T1)                     # Load defined valid columns for PLC Data
            df1 = pd.DataFrame(tpData, columns=columns)     # Include table data into python Dataframe
            TP = tp.loadProcesValues(df1)                   # Join data values under dataframe

        else:
            import VarSQLtp as tp                           # load SQL variables column names | rfVarSQL

            viz_cycle = 150
            g1 = qtp.validCols(T1)                          # Construct Data Column selSqlColumnsTFM.py
            df1 = pd.DataFrame(tpData, columns=g1)          # Import into python Dataframe
            TP = tp.loadProcesValues(df1)                   # Join data values under dataframe

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
        # ------------------------------- S Plot
        im18.set_xdata(np.arange(db_freq))
        im19.set_xdata(np.arange(db_freq))
        im20.set_xdata(np.arange(db_freq))
        im21.set_xdata(np.arange(db_freq))
        im22.set_xdata(np.arange(db_freq))
        im23.set_xdata(np.arange(db_freq))
        im24.set_xdata(np.arange(db_freq))
        im25.set_xdata(np.arange(db_freq))

        # X Plot Y-Axis data points for XBar -------------------------------------------[# Channels]
        im10.set_ydata((TP[0]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # Segment 1
        im11.set_ydata((TP[1]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # Segment 2
        im12.set_ydata((TP[2]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # Segment 3
        im13.set_ydata((TP[3]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # Segment 4
        # ------ Evaluate Pp for Segments ---------#
        mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(tpHL, tpSize, 'TP')
        # ---------------------------------------#
        im14.set_ydata((TP[4]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # Segment 1
        im15.set_ydata((TP[5]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # Segment 2
        im16.set_ydata((TP[6]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # Segment 3
        im17.set_ydata((TP[7]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # Segment 4
        # ------ Evaluate Pp for Ring 2 ---------#
        mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(tpHL, tpSize, 'TP')

        # S Plot Y-Axis data points for StdDev ----------------------------------------[# S Bar Plot]
        im18.set_ydata((TP[0]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
        im19.set_ydata((TP[1]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
        im20.set_ydata((TP[2]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
        im21.set_ydata((TP[3]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])

        im22.set_ydata((TP[4]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
        im23.set_ydata((TP[5]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
        im24.set_ydata((TP[6]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
        im25.set_ydata((TP[7]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])

        if not tpHL:
            mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLd, dLCLd, ppT, pkT, xline, sline = tq.tAutoPerf(tpSize, mnA,
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
        # ---------------------- sBar_minTG, sBar_maxTG -------[]
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

        ani = FuncAnimation(fig, asynchronousTP, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                            blit=False)
        plt.tight_layout()
        plt.show()

    # Update Canvas -----------------------------------------------------[]
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack()

    root.mainloop()


# ------------------------------------------------------------------------------------------------------[]

def lpProcessParam(vCounter, pType):  # Tape Placement
    # def LaserPressure(hMeanC, hDevC, hLCLc, hUCLc, hUSLc, hLSLc, dLCLc, dUCLc, plabel, PPerf, pPos, layer, eSMC):
    root = Tk()
    root.title('mPipe Production: Synchronous SPC - Viz: ' + vCounter)
    root.geometry("1800x800")

    # Load Quality Historical Values -----------[]
    if pRecipe == 'DNV':
        lpSize, lpgType, lpSEoL, lpSEoP, lpHL, lpAL, lpFO, lpParam1, lpParam2, lpParam3, lpParam4, lpParam5 = dnv.decryptpProcessLim(
        WON, 'LP')
    else:
        lpSize, lpgType, lpSEoL, lpSEoP, lpHL, lpAL, lpFO, lpParam1, lpParam2, lpParam3, lpParam4, lpParam5 = mgm.decryptpProcessLim(
            WON, 'LP')
    # Break down each element to useful list ---------------[Tape Temperature]

    if lpHL and lpParam1 and lpParam2 and lpParam3 and lpParam4 and lpParam5:  #
        lpPerf = '$Pp_{k' + str(lpSize) + '}$'  # Using estimated or historical Mean
        lplabel = 'Pp'
        # -------------------------------
        One = lpParam1.split(',')  # split into list elements
        Two = lpParam2.split(',')
        Thr = lpParam3.split(',')
        For = lpParam4.split(',')
        Fiv = lpParam5.split(',')
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
            lpUCL = float(One[2].strip("' "))  # Strip out the element of the list
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
            lpUCL = float(Two[2].strip("' "))  # Strip out the element of the list
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
            lpUCL = float(Thr[2].strip("' "))  # Strip out the element of the list
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
            lpUCL = float(For[2].strip("' "))  # Strip out the element of the list
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
            lpUCL = float(Fiv[2].strip("' "))  # Strip out the element of the list
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
        lpPerf = '$Cp_{k' + str(lpSize) + '}$'  # Using Automatic group Mean
        lplabel = 'Cp'

    # ------------------------------------[End of Tape Temperature Abstraction]
    label = ttk.Label(root,
                      text='Laser Power [LP] - [' + pType + ' Mode] - ' + strftime("%a, %d %b %Y", gmtime()),
                      font=LARGE_FONT)
    label.pack(padx=10, pady=5)

    # Define Axes ---------------------#
    f = Figure(figsize=(25, 8), dpi=100)
    f.subplots_adjust(left=0.022, bottom=0.05, right=0.993, top=0.967, wspace=0.18, hspace=0.174)
    # ---------------------------------[]
    a1 = f.add_subplot(2, 4, (1, 3))  # X Bar Plot
    a2 = f.add_subplot(2, 4, (5, 7))  # S Bar Plo
    a3 = f.add_subplot(2, 4, (4, 8))  # Performance Feeed
    # --------------- Former format -------------

    # Declare Plots attributes --------------------------------[H]
    plt.rcParams.update({'font.size': 7})  # Reduce font size to 7pt for all legends
    # Calibrate limits for X-moving Axis -----------------------#
    YScale_minLP, YScale_maxLP = lpLSL - 8.5, lpUSL + 8.5   # Roller Force
    sBar_minLP, sBar_maxLP = sLCLlp - 80, sUCLlp + 80       # Calibrate Y-axis for S-Plot
    window_Xmin, window_Xmax = 0, (int(lpSize) + 3)         # windows view = visible data points

    # ----------------------------------------------------------#
    # Real-Time Parameter according to updated requirements ----# 27/Feb/2025
    T1 = WON + '_LP'  # Laser Power
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
    def synchronousLP(lpSize, lpgType, fetchT):
        fetch_no = str(fetchT)              # entry value in string sql syntax

        # Obtain Volatile Data from PLC Host Server ---------------------------[]
        if not inUseAlready:                # Load CommsPlc class once
            import CommsSql as q
            q.DAQ_connect(1, 0)
        else:
            con_lp = conn.cursor()

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
            if UsePLC_DBS:
                import plcArrayRLmethodLP as slp  # DrLabs optimization method

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
                        print("\nVisualization in Paused Mode...")
                else:
                    autoSpcPause = False
                    print("Visualization in Play Mode...")
                # -----------------------------------------------------------------[]

                # Allow selective runtime parameter selection on production critical process
                lpData = slp.paramDataRequest('LP', lpSize, lpgType, fetch_no)

            else:
                import sqlArrayRLmethodLP as slp     # DrLabs optimization method

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
                    lpData = slp.sqlexec(lpSize, lpgType, con_lp, T1, fetchT)

                # ------ Inhibit iteration ----------------------------------------------------------[]
                """
                # Set condition for halting real-time plots in watchdog class ---------------------
                """
                # TODO --- values for inhibiting the SQL processing
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    con_lp.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

        return lpData

    # ================== End of synchronous Method ==========================
    def asynchronousLP(db_freq):
        timei = time.time()  # start timing the entire loop

        # Bistream Data Pooling Method ---------------------#
        lpData = synchronousLP(lpSize, lpgType, db_freq)  # data loading functions
        # --------------------------------------------------#

        if UsePLC_DBS == 1:
            import VarPLClp as lp

            viz_cycle = 10
            # Call synchronous data function ---------------[]
            columns = qlp.validCols(T1)  # Load defined valid columns for PLC Data
            df1 = pd.DataFrame(lpData, columns=columns)  # Include table data into python Dataframe
            LP = lp.loadProcesValues(df1)  # Join data values under dataframe

        else:
            import VarSQL_DFlp as lp  # load SQL variables column names | rfVarSQL

            viz_cycle = 150
            g1 = qlp.validCols(T1)  # Construct Data Column selSqlColumnsTFM.py
            df1 = pd.DataFrame(lpData, columns=g1)  # Import into python Dataframe
            LP = lp.loadProcesValues(df1)  # Join data values under dataframe

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
        im10.set_ydata((LP[0]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 1
        im11.set_ydata((LP[1]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 2
        im12.set_ydata((LP[2]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 3
        im13.set_ydata((LP[3]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 1 ---------#
        mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(lpHL, lpSize, 'LP')
        # ---------------------------------------#
        im14.set_ydata((LP[4]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 1
        im15.set_ydata((LP[5]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 2
        im16.set_ydata((LP[6]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 3
        im17.set_ydata((LP[7]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 2 ---------#
        mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(lpHL, lpSize, 'LP')
        # ---------------------------------------#
        im18.set_ydata((LP[8]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 1
        im19.set_ydata((LP[9]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 2
        im20.set_ydata((LP[10]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 3
        im21.set_ydata((LP[11]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 3 ---------#
        mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(lpHL, lpSize, 'LP')
        # ---------------------------------------#
        im22.set_ydata((LP[12]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 1
        im23.set_ydata((LP[13]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 2
        im24.set_ydata((LP[14]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 3
        im25.set_ydata((LP[15]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 4 ---------#
        mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(lpHL, lpSize, 'LP')
        # ---------------------------------------#
        # S Plot Y-Axis data points for StdDev ----------------------------------------
        im26.set_ydata((LP[0]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
        im27.set_ydata((LP[1]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
        im28.set_ydata((LP[2]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
        im29.set_ydata((LP[3]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])

        im30.set_ydata((LP[4]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
        im31.set_ydata((LP[5]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
        im32.set_ydata((LP[6]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
        im33.set_ydata((LP[7]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])

        im34.set_ydata((LP[8]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
        im35.set_ydata((LP[9]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
        im36.set_ydata((LP[10]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
        im37.set_ydata((LP[11]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])

        im38.set_ydata((LP[12]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
        im39.set_ydata((LP[13]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
        im40.set_ydata((LP[14]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
        im41.set_ydata((LP[15]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])

        # Compute entire Process Capability -----------#
        if not lpHL:
            mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLb, ppT, pkT, xline, sline = tq.tAutoPerf(lpSize, mnA, mnB,
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
    canvas = FigureCanvasTkAgg(f, master=root)
    canvas.get_tk_widget().pack(expand=False)

    # Activate Matplot tools ------------------[Uncomment to activate]
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    canvas._tkcanvas.pack(expand=True)


def laProcessParam(vCounter, pType):  # Tape Placement
    # def LaserPressure(hMeanC, hDevC, hLCLc, hUCLc, hUSLc, hLSLc, dLCLc, dUCLc, plabel, PPerf, pPos, layer, eSMC):
    root = Tk()
    root.title('mPipe Production: Synchronous SPC - Viz: ' + vCounter)
    root.geometry("1800x800")

    # Load metrics from config -----------------------------------[]
    if pRecipe == 'DNV':
        laSize, lagType, laSEoL, laSEoP, laHL, laAL, latFO, laParam1, dud2, dud3, dud4, dud5 = dnv.decryptpProcessLim(WON, 'LA')
    else:
        laSize, lagType, laSEoL, laSEoP, laHL, laAL, latFO, laParam1, dud2, dud3, dud4, dud5 = mgm.decryptpProcessLim(WON,
                                                                                                                'LA')
    # Break down each element to useful list ---------------------[Tape Gap]

    if laHL and laParam1:
        laPerf = '$Pp_{k' + str(laSize) + '}$'                   # Estimated or historical Mean
        lalabel = 'Pp'
        # -------------------------------
        laOne = laParam1.split(',')                             # split into list elements
        dTapela = laOne[1].strip("' ")                          # defined Tape Width
        dLayer = laOne[10].strip("' ")                          # Defined Tape Layer

        # Load historical limits for the process----------------#
        # if cpTapeW == dTapetg and cpLayerNo == range(1, 100):   # '*.*',  | *.*
        laUCL = float(laOne[2].strip("' "))                     # Strip out the element of the list
        laLCL = float(laOne[3].strip("' "))
        laMean = float(laOne[4].strip("' "))
        laDev = float(laOne[5].strip("' "))
        # --------------------------------
        sUCLla = float(laOne[6].strip("' "))
        sLCLla = float(laOne[7].strip("' "))
        # --------------------------------
        laUSL = (laUCL - laMean) / 3 * 6
        laLSL = (laMean - laLCL) / 3 * 6
        # --------------------------------
    else:  # Computes Shewhart constants (Automatic Limits)
        laUCL = 0
        laLCL = 0
        laMean = 0
        laDev = 0
        sUCLla = 0
        sLCLla = 0
        laUSL = 0
        laLSL = 0
        laPerf = '$Cp_{k' + str(laSize) + '}$'  # Using Automatic group Mean
        lalabel = 'Cp'

    # -----------------------------------------------------[End of Tape Gap]
    label = ttk.Label(root,
                      text='Laser Angle [LA] - [' + pType + ' Mode] - ' + strftime("%a, %d %b %Y", gmtime()),
                      font=LARGE_FONT)
    label.pack(pady=10, padx=10)

    # Define Axes ---------------------#
    fig = Figure(figsize=(25, 13), dpi=100)
    fig.subplots_adjust(left=0.03, bottom=0.035, right=0.99, top=0.976, hspace=0.14, wspace=0.195)
    # ---------------------------------[]
    a1 = fig.add_subplot(2, 4, (1, 3))  # xbar plot
    a2 = fig.add_subplot(2, 4, (5, 7))  # s bar plot
    a3 = fig.add_subplot(2, 4, (4, 8))  # CPk/PPk Feed

    # Declare Plots attributes -----------------------------------------[]
    plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
    # Calibrate limits for X-moving Axis -----------------------#
    YScale_minLA, YScale_maxLA = laLSL - 8.5, laUSL + 8.5       # Roller Force
    sBar_minLA, sBar_maxLA = sLCLla - 80, sUCLla + 80           # Calibrate Y-axis for S-Plot
    window_Xmin, window_Xmax = 0, (int(laSize) + 3)             # windows view = visible data points

    # ----------------------------------------------------------#
    # Real-Time Parameter according to updated requirements ----# 07/Feb/2025
    T1 = WON + '_LA'                                            # Laser Angle
    # ----------------------------------------------------------#

    # Declare Plots attributes ---------------------------------#
    a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
    a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
    a1.set_title('Laser Angle [XBar]', fontsize=12, fontweight='bold')
    a2.set_title('Laser Angle [StDev]', fontsize=12, fontweight='bold')

    a1.grid(color="0.5", linestyle='-', linewidth=0.5)
    a2.grid(color="0.5", linestyle='-', linewidth=0.5)
    a1.legend(loc='upper right', title='Laser Angle (Deg)')
    a2.legend(loc='upper right', title='Sigma curve')

    # Initialise runtime limits -------------------------------#
    a1.set_ylim([YScale_minLA, YScale_maxLA], auto=True)
    a1.set_xlim([window_Xmin, window_Xmax])
    # ----------------------------------------------------------#
    a3.set_ylim([sBar_minLA, sBar_maxLA], auto=True)
    a3.set_xlim([window_Xmin, window_Xmax])

    # ----------------------------------------------------------[]
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

    # Statistical Feed ------------------------------------------[]
    a3.text(0.466, 0.945, 'Performance Feed - LA', fontsize=15, fontweight='bold', ha='center', va='center',
            transform=a3.transAxes)
    # class malalotlib.patches.Rectangle(xy, width, height, angle=0.0)
    rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
    rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
    a3.add_patch(rect1)
    a3.add_patch(rect2)
    # ------- Process Performance Pp (the spread)----------------[]
    a3.text(0.145, 0.804, lalabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.328, 0.658, '#Pp Value', fontsize=18, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.650, 0.820, 'Ring ' + lalabel, fontsize=12, ha='left', transform=a3.transAxes)
    a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
    # ------- Process Performance Ppk (Performance)--------------[]
    a3.text(0.145, 0.403, laPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.328, 0.282, '#Ppk Value', fontsize=16, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.640, 0.420, 'Ring ' + laPerf, fontsize=12, ha='left', transform=a3.transAxes)
    # -----------------------------------------------------------[]
    a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
    # ----- Pipe Position and SMC Status -----
    a3.text(0.080, 0.080, 'Pipe Position: ' + pPos + '\nProcessing Layer #' + layer, fontsize=12, ha='left',
            transform=a3.transAxes)
    a3.text(0.080, 0.036, 'SMC Status: ' + eSMC, fontsize=12, ha='left', transform=a3.transAxes)

    # ---------------- EXECUTE SYNCHRONOUS METHOD -----------------------------#
    def synchronousLA(laSize, lagType, fetchT):
        fetch_no = str(fetchT)          # entry value in string sql syntax

        # Obtain Volatile Data from PLC Host Server ---------------------------[]
        if not inUseAlready:            # Load CommsPlc class once
            import CommsSql as q
            q.DAQ_connect(1, 0)
        else:
            con_la = conn.cursor()

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
                import plcArrayRLmethodA as sla                    # DrLabs optimization method

                inProgress = True  # True for RetroPlay mode
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
                    # tgData = pdC.sqlexec(smp_Sz, smp_St, con_tg, T1, fetchT)  # get details from PLC array
                    laData = sla.paramDataRequest(T1, laSize, lagType, fetch_no)

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
                        # play(error)                                               # Pause mode with audible Alert
                        print("\nVisualization in Paused Mode...")
                    else:
                        autoSpcPause = False
                    print("Visualization in Play Mode...")
                else:
                    laData = sla.sqlexec(laSize, lagType, con_la, T1, fetchT)
                    print("Visualization in Play Mode...")
                print('\nUpdating....')

                # ------ Inhibit iteration ----------------------------------------------------------[]
                """
                # Set condition for halting real-time plots in watchdog class -----------------------[]
                """
                # TODO --- values for inhibiting the SQL processing
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    con_la.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

        return laData

    # ================== End of synchronous Method ==========================

    def asynchronousLA(db_freq):
        timei = time.time()  # start timing the entire loop

        # declare asynchronous variables ------------------[]

        # Call data loader Method---------------------------#
        laData = synchronousLA(laSize, lagType, db_freq)  # data loading functions
        # --------------------------------------------------#

        if UsePLC_DBS == 1:
            import VarPLCla as la

            viz_cycle = 10
            # Call synchronous data function ---------------[]
            columns = qla.validCols(T1)                     # Load defined valid columns for PLC Data
            df1 = pd.DataFrame(laData, columns=columns)     # Include table data into python Dataframe
            LA = la.loadProcesValues(df1)                   # Join data values under dataframe

        else:
            import VarSQLla as la                           # load SQL variables column names | rfVarSQL

            viz_cycle = 150
            g1 = qla.validCols(T1)                          # Construct Data Column selSqlColumnsTFM.py
            df1 = pd.DataFrame(laData, columns=g1)          # Import into python Dataframe
            LA = la.loadProcesValues(df1)                   # Join data values under dataframe

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
        im10.set_ydata((LA[0]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 1
        im11.set_ydata((LA[1]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 2
        im12.set_ydata((LA[2]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 3
        im13.set_ydata((LA[3]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 1 ---------#
        mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(laHL, laSize, 'LA')
        # ---------------------------------------#
        im14.set_ydata((LA[4]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 1
        im15.set_ydata((LA[5]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 2
        im16.set_ydata((LA[6]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 3
        im17.set_ydata((LA[7]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 2 ---------#
        mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(laHL, laSize, 'LA')
        # ---------------------------------------#
        im18.set_ydata((LA[8]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 1
        im19.set_ydata((LA[9]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 2
        im20.set_ydata((LA[10]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 3
        im21.set_ydata((LA[11]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 3 ---------#
        mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(laHL, laSize, 'LA')
        # ---------------------------------------#
        im22.set_ydata((LA[12]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 1
        im23.set_ydata((LA[13]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 2
        im24.set_ydata((LA[14]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 3
        im25.set_ydata((LA[15]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 4 ---------#
        mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(laHL, laSize, 'LA')
        # ---------------------------------------#
        im18.set_ydata((TG[0]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
        im19.set_ydata((TG[1]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
        im20.set_ydata((TG[2]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
        im21.set_ydata((TG[3]).rolling(window=laSize, min_periods=1).std()[0:db_freq])

        im22.set_ydata((TG[4]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
        im23.set_ydata((TG[5]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
        im24.set_ydata((TG[6]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
        im25.set_ydata((TG[7]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
        # S Plot Y-Axis data points for StdDev ----------------------------------------
        im26.set_ydata((LA[0]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
        im27.set_ydata((LA[1]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
        im28.set_ydata((LA[2]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
        im29.set_ydata((LA[3]).rolling(window=laSize, min_periods=1).std()[0:db_freq])

        im30.set_ydata((LA[4]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
        im31.set_ydata((LA[5]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
        im32.set_ydata((LA[6]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
        im33.set_ydata((LA[7]).rolling(window=laSize, min_periods=1).std()[0:db_freq])

        im34.set_ydata((LA[8]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
        im35.set_ydata((LA[9]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
        im36.set_ydata((LA[10]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
        im37.set_ydata((LA[11]).rolling(window=laSize, min_periods=1).std()[0:db_freq])

        im38.set_ydata((LA[12]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
        im39.set_ydata((LA[13]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
        im40.set_ydata((LA[14]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
        im41.set_ydata((LA[15]).rolling(window=laSize, min_periods=1).std()[0:db_freq])

        if not laHL:
            mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLd, dLCLd, ppT, pkT, xline, sline = tq.tAutoPerf(laSize, mnA,
                                                                                                  mnB,
                                                                                                  0, 0, sdA,
                                                                                                  sdB, 0, 0)
        else:
            xline, sline = laMean, laDev
            mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLd, dLCLd, ppT, pkT = tq.tManualPerf(mnA, mnB, 0, 0, sdA, sdB,
                                                                                      0, 0, laUSL, laLSL, laUCL,
                                                                                      laLCL)

        # # Declare Plots attributes ------------------------------------------------------------[]
        # XBar Mean Plot
        a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
        a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 3 Sigma span (Purple)
        a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
        a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
        # ---------------------- sBar_minTG, sBar_maxTG -------[]
        # Define Legend's Attributes  ----
        a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
        a2.axhspan(sLCLla, sUCLla, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 1 Sigma Span
        a2.axhspan(sUCLla, sBar_maxLA, facecolor='#CCCCFF', edgecolor='#CCCCFF')  # 1 Sigma above the Mean
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
        sigma.trigViolations(a1, UsePLC_DBS, 'TG', YScale_minLA, YScale_maxLA, xucT, xlcT, xusT, xlsT, mnT, sdT)

        timef = time.time()
        lapsedT = timef - timei
        print(f"\nProcess Interval: {lapsedT} sec\n")

        ani = FuncAnimation(fig, asynchronousLA, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                            blit=False)
        plt.tight_layout()
        plt.show()

    # Update Canvas -----------------------------------------------------[]
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack()

    root.mainloop()

# ---------------------- Port windows into parallel processing ----------[]

def myMain(qType, ProcID):
    global pType, pParam, smp_Sz, stp_Sz # , p1, p2, p3, p4, p5, p6, p7

    pType = qType
    pParam = ProcID

    # print('\nP-Type..:', pType)
    if ProcID == 'DNV':
        # if GPU -------------------------------------------------#
        p1 = Process(target=ttProcessParam, args=(countA, pType))          # name="CascadeTT")
        p2 = Process(target=stProcessParam, args=(countB, pType))          # name="CascadeST")
        p3 = Process(target=tgProcessParam, args=(countC, pType))          # name="CascadeTG")
        p4 = 0
        p5 = 0
        p6 = 0
        p7 = 0
        # --------------------------------------------------------#
        p1.start()                                                          # Quality parameter 1
        p2.start()                                                          # Quality parameter 2
        p3.start()                                                          # Quality parameter 3

    elif ProcID == 'MGM':
        # if GPU -------------------------------------------------#
        p1 = Process(target=lpProcessParam, args=(countA, pType))           # name="CascadeRF")
        p2 = Process(target=laProcessParam, args=(countB, pType))           # name="CascadeTT")
        p3 = Process(target=tpProcessParam, args=(countC, pType))           # name="CascadeST")
        p4 = Process(target=rfProcessParam, args=(countD, pType))           # name="CascadeTS")
        p5 = Process(target=ttProcessParam, args=(countE, pType))           # name="CascadeTG")
        p6 = Process(target=stProcessParam, args=(countF, pType))           # name="CascadeTG")
        p7 = Process(target=tgProcessParam, args=(countG, pType))           # name="CascadeTG")

        p1.start()                                                          # Quality parameter 1
        p2.start()                                                          # Quality parameter 2
        p3.start()                                                          # Quality parameter 3
        p4.start()                                                          # Quality parameter 4
        p5.start()                                                          # Quality parameter 5
        p6.start()                                                          # Quality parameter 4
        p7.start()

    else:
        pass

    # --------------------- Join the threads -------------------#
    # print('\nP1 #:', p1)
    # print('P2 #:', p2)
    # print('P3 #:', p3)
    # print('Proces 1', p1.pid)   # display only the process number(int)
    # print('Proces 2', p2.pid)
    # print('Proces 3', p3.pid)
    # print('Proces 1', p4.pid)
    # --------------------- Join the threads -----------------#
    # returned values for evaluation and closing out of the process

    return p1, p2, p3, p4, p5, p6, p7

# -------------------------------------------------------------------------------------------------------- [if on GPU]
"""
# NOTE: Parallel programing is beautiful when you observe the rule of Best Practice:
https://docs.python.org/3/library/multiprocessing.html#multiprocessing-programming
R. Labs
"""
# 1. In parallel programming, avoid shared state for multiple objects
# 2. Stick to using queues or pipes for communication between processes
# 3. Ensure that the arguments to the methods of proxies are picklable
# 4. Do not use a proxy object from more than one thread unless you protect it with a lock
# 5. It is probably good practice to explicitly join all the processes that you start
# 6. Arrange the program so that a process can inherit access to a shared resource created elsewhere from an ancestor
# 7. Using the Process.terminate method to stop a process is liable to cause any shared resources broken or unavailable
# 8. Best to only consider using Process.terminate on processes which never use any shared resources
# 9. Process engages Queue function will wait before terminating until all the buffered items are fed by the “feeder”
# 10. However, global variables which are just module level constants cause no problems
# 11. Safe importing of main module - Protect the “entry point” of the program by using if __name__ == '__main__':
# -------------------------------------------------------------------------------------[]

# if __name__ == '__main__':
#     freeze_support()            # omitted if the program will be run normally instead of frozen
#     set_start_method('spawn')   # This enables the newly spawned Python interpreter to safely import the module
#     myMain()

# ------ END OF PIPELINE --------------------------------------------------------------[]

