# --------------------------------------------------------------------------
# Author: Dr RB Labs
# Developed for Magma Global - TechnipFMC Industrialization
# Email: robbielabs@uwl.ac.uk
# Copyright (C) 2023-2025, Robbie Labs
# Cascade (Multiple screen ) View
# --------------------------------------------------------------------------
import time
import os
import sys
from datetime import datetime

from time import gmtime, strftime
import numpy as np
import pandas as pd
from tkinter import *
from tkinter import ttk
import matplotlib.pyplot as plt
from multiprocessing import Process, freeze_support, set_start_method
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
LARGE_FONT = ("Verdana", 12, 'bold')
import matplotlib.patches as patches
import loadSPCConfig as ty
import qParamsHL as mq

# -------PLC/SQL Query -------#
import selDataColsOEE as qo
import selDataColsCT as qc
import selDataColsRF as qf
# ----- DNV Params ------
import selDataColsTG as qg
import selDataColsWS as qw
import selDataColsST as qs
import selDataColsTT as qt
import selDataColsRP as qp
# -----------------------------#

import subprocess
try:
    subprocess.check_output('nvidia-smi')
    print('Nvidia GPU detected!')
except Exception:
    print('No Nvidia GPU in system!')


pPos = str(3345)
layer = str(10)

WON = "275044"
eSMC = 'Getting started...'
countA = '01'
countB = '02'
countC = '03'
countD = '04'
countE = '05'
# ---------------------------------------------- Common to all Process Procedures -------------------------[]
cpTapeW, cpLayerNo, runType = [], [], []
UsePLC_DBS = True
runStatus = 0
hostConn = 0
# ---------------------------------------------------------------------------------------------------------[]


class common_OEE(ttk.Frame):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=2010, y=20)
        self.createWidgets()

    def createWidgets(self):
        # -----------------------------------
        f = Figure(figsize=(5, 4), dpi=100)
        f.subplots_adjust(left=0.045, bottom=0, right=0.988, top=0.929, wspace=0.202)
        a3 = f.add_subplot(1, 1, 1)

        # Model data --------------------------------------------------[]
        a3.cla()
        a3.get_yaxis().set_visible(False)
        a3.get_xaxis().set_visible(False)
        if not runStatus:
            a3.pie([1, 7, 0, 5, 9, 6], shadow=True)

        # ---------------- EXECUTE SYNCHRONOUS METHOD ---------------#
        def synchronousOEE(smp_Sz, smp_St, fetchT):
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
                import sqlArrayRLmethodOE as oe                             # DrLabs optimization method
                inProgress = True                                           # True for RetroPlay mode
                print('\nAsynchronous controller activated...')
                print('DrLabs' + "' Runtime Optimisation is Enabled!")

                # Get list of relevant SQL Tables using conn() ---------[TODO] Data fetch only at unique stoppages
                oeData = oe.sqlexec(smp_Sz, smp_St, qRP, tblID, fetchT)     # perform DB connections
                if keyboard.is_pressed("Alt+Q"):                            # Terminate file-fetch
                    qRP.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

            return oeData

        # ================== End of synchronous Method ==========================
        def asynchronousOEE(db_freq):

            timei = time.time()                                 # start timing the entire loop
            # Call data loader Method---------------------------#
            oeSQL = synchronousOEE(smp_Sz, stp_Sz, db_freq)     # data loading functions

            import oeVarSQL as qoe                              # load SQL variables column names | rfVarSQL
            viz_cycle = 150
            g1 = qo.validCols('OEE')                            # Construct Data Column selSqlColumnsTFM.py
            df3 = pd.DataFrame(oeSQL, columns=g1)               # Import into python Dataframe
            OE = qoe.loadProcesValues(df3)                      # Join data values under dataframe
            print('\nDataFrame Content', df3.head(10))          # Preview Data frame head
            print("Memory Usage:", df3.info(verbose=False))     # Check memory utilization

            # --------------------------------
            # Allow the following code to run despite not on DNV condition ----------------#
            # TODO replace with process variable
            cLayer = OE[1]
            status = OE[3]
            curLayer = list(set(cLayer))            # shuffle list to obtain unique layer number at a time
            if len(curLayer) > 1:
                lastE = len(curLayer)
                curLayer = curLayer[lastE - 1]      # print the last index element
            # ---------------------------------
            # if VarPerHeadA or VarPerHeadB or VariProcess:
            OTlayr.append(curLayer[0])              # Post values into static array
            EPpos.append('N/A')                     # Insert pipe position is available
            pStatus.append(status)
            print('\nTP05[Layer/Status]:', curLayer[0], status)
            # ----------------------------------------------------------------------------#
            print('\nTesting loop...')
            # Obtain current local time string ------------------------[]
            cTime = strftime("%H:%M:%S")

            # Convert current time string to datetime object ----------[]
            currentTime = str(datetime.strptime(cTime, "%H:%M:%S").time())
            print('\nCurrent Time:', currentTime)

            # Compute essential variables ------------------------------- TODO verify filter *****
            dayShiftTime = df3[(df3['TimeLine'] >= sStart) & (df3['TimeLine'] <= currentTime)]

            totalRun = dayShiftTime.copy()
            totalRun = totalRun.drop_duplicates(subset='TimeLine', keep='first')
            # print('Total Run:', totalRun)

            # Convert Shift start time to string format -----------------
            shiftStartTime = str(datetime.strptime(sStart, "%H:%M:%S").time())
            shiftEndTime = str(datetime.strptime(sStops, "%H:%M:%S").time())
            print("Shift Starts:", shiftStartTime)
            print("Shift Ends @:", shiftEndTime)

            # Compute production lapse time -----------------------------
            TShiftSec = datetime.strptime(sStops, '%H:%M:%S') - datetime.strptime(shiftStartTime, '%H:%M:%S')
            ShiftinSec = TShiftSec.total_seconds()  # Convert values into seconds
            print('=' * 22)
            print('Shift Hours:', ShiftinSec, '(Sec)')

            deltaT = datetime.strptime(str(currentTime), '%H:%M:%S') - datetime.strptime(shiftStartTime, '%H:%M:%S')
            opTime = deltaT.total_seconds()  # Convert values into seconds
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
            mycol = ['#4c72b0', 'green', 'orange']          # add colors
            a3.pie(pieData, labels=ind_metric, startangle=90, explode=segexplode, shadow=True, autopct='%1.1f%%',
                    colors=mycol, textprops={'fontsize': 10})
            if not HeadA:   # if HeadA (synchronous)
                a3.set_title('Post Production Status', fontsize=12, fontweight='bold')
            else:
                a3.set_title('Machine Live Status Analysis', fontsize=12, fontweight='bold')

            # No trigger module processing - Production parameter is for monitoring purposes only.
            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousOEE, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -------------------------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)

        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True)


def RollerPressure(vCounter, pType):

    root = Tk()
    root.title('mPipe Production: Synchronous SPC - Viz: ' + vCounter)
    root.geometry("1800x800")

    # Load Quality Historical Values ---------------[]
    rpSize, rpgType, rpSspace, rpHL, rpAL, rpFO, rpParam1, rpParam2, dud3, dud4, dud5 = mq.decryptpProcessLim(WON, 'RP')
    # Break down each element to useful list -------[Roller Pressure]

    if rpHL and rpParam1 and rpParam2:  # Roller Pressure TODO - layer metrics to guide TCP01
        rpPerf = '$Pp_{k' + str(rpSize) + '}$'      # Using estimated or historical Mean
        rplabel = 'Pp'
        # -------------------------------
        rpOne = rpParam1.split(',')                 # split into list elements
        rpTwo = rpParam1.split(',')
        dTaperp = rpOne[1].strip("' ")              # defined Tape Width
        dLayer = rpOne[10].strip("' ")              # Defined Tape Layer
        # Load historical limits for the process----#
        if cpLayerNo == 40:                         # '22mm'|'18mm',  1-40 | 41+
            rpUCL = float(rpOne[2].strip("' "))     # Strip out the element of the list
            rpLCL = float(rpOne[3].strip("' "))
            rpMean = float(rpOne[4].strip("' "))
            rpDev = float(rpOne[5].strip("' "))
            # --------------------------------
            sUCLrp = float(rpOne[6].strip("' "))
            sLCLrp = float(rpOne[7].strip("' "))
            # --------------------------------
            rpUSL = (rpUCL - rpMean) / 3 * 6
            rpLSL = (rpMean - rpLCL) / 3 * 6
            # --------------------------------
        else:
            rpUCL = float(rpTwo[2].strip("' "))     # Strip out the element of the list
            rpLCL = float(rpTwo[3].strip("' "))
            rpMean = float(rpTwo[4].strip("' "))
            rpDev = float(rpTwo[5].strip("' "))
            # --------------------------------
            sUCLrp = float(rpTwo[6].strip("' "))
            sLCLrp = float(rpTwo[7].strip("' "))
            # -------------------------------
            rpUSL = (rpUCL - rpMean) / 3 * 6
            rpLSL = (rpMean - rpLCL) / 3 * 6
            # -------------------------------
    else:  # Computes Shewhart constants (Automatic Limits)
        rpUCL = 0
        rpLCL = 0
        rpMean = 0
        rpDev = 0
        sUCLrp = 0
        sLCLrp = 0
        rpUSL = 0
        rpLSL = 0
        rpPerf = '$Cp_{k' + str(rpSize) + '}$'  # Using Automatic group Mean
        rplabel = 'Cp'

    label = ttk.Label(root, text='DNV Quality Parameter [RP] - [' + pType + ' Mode] - ' + strftime("%a, %d %b %Y", gmtime()), font=LARGE_FONT)
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
    YScale_minRP, YScale_maxRP = rpLSL - 8.5, rpUSL + 8.5   # Roller Force
    sBar_minRP, sBar_maxRP = sLCLrp - 80, sUCLrp + 80       # Calibrate Y-axis for S-Plot
    window_Xmin, window_Xmax = 0, (int(rpSize) + 3)         # windows view = visible data points

    # Declare Plots attributes --------------------------------#
    a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
    a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
    a1.set_title('Roller Pressure [XBar Plot]', fontsize=12, fontweight='bold')
    a2.set_title('Roller Pressure [S Plot]', fontsize=12, fontweight='bold')
    a1.grid(color="0.5", linestyle='-', linewidth=0.5)
    a2.grid(color="0.5", linestyle='-', linewidth=0.5)
    a1.legend(loc='upper left', title='XBar Plot')
    a2.legend(loc='upper right', title='SDev Plot')
    # Initialise runtime limits --------------------------------#
    a1.set_ylim([YScale_minRP, YScale_maxRP], auto=True)
    a1.set_xlim([window_Xmin, window_Xmax])
    # ----------------------------------------------------------#
    a2.set_ylim([sBar_minRP, sBar_maxRP], auto=True)
    a2.set_xlim([window_Xmin, window_Xmax])

    # ---------------------------------------------------------[]
    a3.cla()
    a3.get_yaxis().set_visible(False)
    a3.get_xaxis().set_visible(False)

    # # Model data ----------------------------------------------[]
    # a1.plot([1857, 848, 1984, 529, 1740, 1136, 1012, 723, 1791, 600])
    # a2.plot([-1.78, -1.0, -0.8, -1.3, -0.89, -0.92, -1.2, -1.5, -1.6, -0.85])
    # # Calibrate the rest of the Plots -------------------------#

    # ---------------------------------------------------------[]
    # Define Plot area and axes -
    # ---------------------------------------------------------#
    im10, = a1.plot([], [], 'o-.', label='Roller Pressure(N) - (R1H1)')
    im11, = a1.plot([], [], 'o-', label='Roller Pressure(N) - (R1H2)')
    im12, = a1.plot([], [], 'o-', label='Roller Pressure(N) - (R1H3)')
    im13, = a1.plot([], [], 'o-', label='Roller Pressure(N) - (R1H4)')
    im14, = a2.plot([], [], 'o-', label='Roller Pressure(N)')
    im15, = a2.plot([], [], 'o-', label='Roller Pressure(N)')
    im16, = a2.plot([], [], 'o-', label='Roller Pressure(N)')
    im17, = a2.plot([], [], 'o-', label='Roller Pressure(N)')

    im18, = a1.plot([], [], 'o-.', label='Roller Pressure(N) - (R2H1)')
    im19, = a1.plot([], [], 'o-', label='Roller Pressure(N) - (R2H2)')
    im20, = a1.plot([], [], 'o-', label='Roller Pressure(N) - (R2H3)')
    im21, = a1.plot([], [], 'o-', label='Roller Pressure(N) - (R2H4)')
    im22, = a2.plot([], [], 'o-', label='Roller Pressure(N)')
    im23, = a2.plot([], [], 'o-', label='Roller Pressure(N)')
    im24, = a2.plot([], [], 'o-', label='Roller Pressure(N)')
    im25, = a2.plot([], [], 'o-', label='Roller Pressure(N)')

    im26, = a1.plot([], [], 'o-.', label='Roller Pressure(N) - (R3H1)')
    im27, = a1.plot([], [], 'o-', label='Roller Pressure(N) - (R3H2)')
    im28, = a1.plot([], [], 'o-', label='Roller Pressure(N) - (R3H3)')
    im29, = a1.plot([], [], 'o-', label='Roller Pressure(N) - (R3H4)')
    im30, = a2.plot([], [], 'o-', label='Roller Pressure(N)')
    im31, = a2.plot([], [], 'o-', label='Roller Pressure(N)')
    im32, = a2.plot([], [], 'o-', label='Roller Pressure(N)')
    im33, = a2.plot([], [], 'o-', label='Roller Pressure(N)')

    im34, = a1.plot([], [], 'o-.', label='Roller Pressure(N) - (R4H1)')
    im35, = a1.plot([], [], 'o-', label='Roller Pressure(N) - (R4H2)')
    im36, = a1.plot([], [], 'o-', label='Roller Pressure(N) - (R4H3)')
    im37, = a1.plot([], [], 'o-', label='Roller Pressure(N) - (R4H4)')
    im38, = a2.plot([], [], 'o-', label='Roller Pressure(N)')
    im39, = a2.plot([], [], 'o-', label='Roller Pressure(N)')
    im40, = a2.plot([], [], 'o-', label='Roller Pressure(N)')
    im41, = a2.plot([], [], 'o-', label='Roller Pressure(N)')

    # Statistical Feed ---------------------------------------[]
    a3.text(0.466, 0.945, 'Performance Feed - RP', fontsize=16, fontweight='bold', ha='center', va='center',
            transform=a3.transAxes)
    # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
    rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
    rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
    a3.add_patch(rect1)
    a3.add_patch(rect2)
    # ------- Process Performance Pp (the spread)---------------------
    a3.text(0.145, 0.804, rplabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.328, 0.658, '#Pp', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.650, 0.820, 'Ring ' + rplabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
    a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
    # ------- Process Performance Ppk (Performance)--------------------#
    a3.text(0.145, 0.403, rpPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.328, 0.282, '#Ppk', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.640, 0.420, 'Ring ' + rpPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
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
    def synchronousRP(wsSize, wsgType, fetchT):
        fetch_no = str(fetchT)  # entry value in string sql syntax

        # Obtain Volatile Data from PLC Host Server ---------------------------[]
        if not inUseAlready:  # Load CommsPlc class once
            import CommsSql as q
            q.DAQ_connect(1, 0)
        else:
            qRP = conn.cursor()
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
            if not UsePLC_DBS:                                  # Not Using PLC Data
                import ArrayRP_sqlRLmethod as lq                # DrLabs optimization method
                inProgress = True                               # True for RetroPlay mode
                print('\nAsynchronous controller activated...')
                print('DrLabs' + "' Runtime Optimisation is Enabled!")

                # Get list of relevant SQL Tables using conn() --------------------[]
                rpData = lq.sqlexec(rpSize, rpgType, qRP, tblID, fetchT)
                if keyboard.is_pressed("Alt+Q"):                # Terminate file-fetch
                    qRP.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

            else:
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

                # Play visualization ----------------------------------------------[]
                print("Visualization in Play Mode...")
                # play(nudge)     # audible alert

                # -----------------------------------------------------------------[]
                # Allow selective runtime parameter selection on production critical process
                procID = 'RP'
                rpData = q.paramDataRequest(procID, rpSize, rpgType, fetch_no)

        return rpData

    # ================== End of synchronous Method ==========================
    def asynchronousRP(db_freq):

        timei = time.time()  # start timing the entire loop
        UsePLC_DBS = pType  # Query Type

        # Call data loader Method---------------------------#
        rpData = synchronousRP(rpSize, rpgType, db_freq)  # data loading functions
        if UsePLC_DBS == 1:
            import rfVarPLC as qrf
            viz_cycle = 10
            # Call synchronous data function ---------------[]
            columns = vq.validColsPLCData()                 # Load defined valid columns for PLC Data
            df1 = pd.DataFrame(rpData, columns=columns)     # Include table data into python Dataframe
            RP = qrf.loadProcesValues(df1)                  # Join data values under dataframe

        else:
            import rfVarSQL as qrf                          # load SQL variables column names | rfVarSQL
            viz_cycle = 150
            g1 = qq.validCols('WS')                         # Construct Data Column selSqlColumnsTFM.py
            df1 = pd.DataFrame(rpData, columns=g1)          # Import into python Dataframe
            RP = qrf.loadProcesValues(df1)                  # Join data values under dataframe
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
        im10.set_ydata((RP[0]).rolling(window=rpSize, min_periods=1).mean()[0:db_freq])  # head 1
        im11.set_ydata((RP[1]).rolling(window=rpSize, min_periods=1).mean()[0:db_freq])  # head 2
        im12.set_ydata((RP[2]).rolling(window=rpSize, min_periods=1).mean()[0:db_freq])  # head 3
        im13.set_ydata((RP[3]).rolling(window=rpSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 1 ---------#
        mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(rpHL, rpSize, 'RP')
        # ---------------------------------------#
        im14.set_ydata((RP[4]).rolling(window=rpSize, min_periods=1).mean()[0:db_freq])  # head 1
        im15.set_ydata((RP[5]).rolling(window=rpSize, min_periods=1).mean()[0:db_freq])  # head 2
        im16.set_ydata((RP[6]).rolling(window=rpSize, min_periods=1).mean()[0:db_freq])  # head 3
        im17.set_ydata((RP[7]).rolling(window=rpSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 2 ---------#
        mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(rpHL, rpSize, 'RP')
        # ---------------------------------------#
        im18.set_ydata((RP[8]).rolling(window=rpSize, min_periods=1).mean()[0:db_freq])  # head 1
        im19.set_ydata((RP[9]).rolling(window=rpSize, min_periods=1).mean()[0:db_freq])  # head 2
        im20.set_ydata((RP[10]).rolling(window=rpSize, min_periods=1).mean()[0:db_freq])  # head 3
        im21.set_ydata((RP[11]).rolling(window=rpSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 3 ---------#
        mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(rpHL, rpSize, 'RP')
        # ---------------------------------------#
        im22.set_ydata((RP[12]).rolling(window=rpSize, min_periods=1).mean()[0:db_freq])  # head 1
        im23.set_ydata((RP[13]).rolling(window=rpSize, min_periods=1).mean()[0:db_freq])  # head 2
        im24.set_ydata((RP[14]).rolling(window=rpSize, min_periods=1).mean()[0:db_freq])  # head 3
        im25.set_ydata((RP[15]).rolling(window=rpSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 4 ---------#
        mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(rpHL, rpSize, 'RP')
        # ---------------------------------------#
        # S Plot Y-Axis data points for StdDev ----------------------------------------
        im26.set_ydata((RP[0]).rolling(window=rpSize, min_periods=1).std()[0:db_freq])
        im27.set_ydata((RP[1]).rolling(window=rpSize, min_periods=1).std()[0:db_freq])
        im28.set_ydata((RP[2]).rolling(window=rpSize, min_periods=1).std()[0:db_freq])
        im29.set_ydata((RP[3]).rolling(window=rpSize, min_periods=1).std()[0:db_freq])

        im30.set_ydata((RP[4]).rolling(window=rpSize, min_periods=1).std()[0:db_freq])
        im31.set_ydata((RP[5]).rolling(window=rpSize, min_periods=1).std()[0:db_freq])
        im32.set_ydata((RP[6]).rolling(window=rpSize, min_periods=1).std()[0:db_freq])
        im33.set_ydata((RP[7]).rolling(window=rpSize, min_periods=1).std()[0:db_freq])

        im34.set_ydata((RP[8]).rolling(window=rpSize, min_periods=1).std()[0:db_freq])
        im35.set_ydata((RP[9]).rolling(window=rpSize, min_periods=1).std()[0:db_freq])
        im36.set_ydata((RP[10]).rolling(window=rpSize, min_periods=1).std()[0:db_freq])
        im37.set_ydata((RP[11]).rolling(window=rpSize, min_periods=1).std()[0:db_freq])

        im38.set_ydata((RP[12]).rolling(window=rpSize, min_periods=1).std()[0:db_freq])
        im39.set_ydata((RP[13]).rolling(window=rpSize, min_periods=1).std()[0:db_freq])
        im40.set_ydata((RP[14]).rolling(window=rpSize, min_periods=1).std()[0:db_freq])
        im41.set_ydata((RP[15]).rolling(window=rpSize, min_periods=1).std()[0:db_freq])
        # Compute entire Process Capability -----------#
        if not rpHL:
            mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLa, dLCLa, ppT, pkT, xline, sline = tq.tAutoPerf(rpSize, mnA, mnB,
                                                                                                  mnC, mnD, sdA,
                                                                                                  sdB, sdC, sdD)
        else:
            xline, sline = rpMean, rpDev
            mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLa, dLCLa, ppT, pkT = tq.tManualPerf(mnA, mnB, mnC, mnD, sdA, sdB,
                                                                                      sdC, sdD, rpUSL, rpLSL, rpUCL,
                                                                                       rpLCL)

        # # Declare Plots attributes --------------------------------------------------------[]
        # XBar Mean Plot
        a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
        a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')            # 3 Sigma span (Purple)
        a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')            # grey area
        a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
        # ---------------------- sBar_minTT, sBar_maxTT -------[]
        # Define Legend's Attributes  ----
        a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
        a2.axhspan(sLCLrp, sUCLrp, facecolor='#F9C0FD', edgecolor='#F9C0FD')        # 1 Sigma Span
        a2.axhspan(sUCLrp, sBar_maxRP, facecolor='#CCCCFF', edgecolor='#CCCCFF')    # 1 Sigma above the Mean
        a2.axhspan(sBar_minRP, sLCLrp, facecolor='#CCCCFF', edgecolor='#CCCCFF')

        # Setting up the parameters for moving windows Axes ---------------------------------[]
        if db_freq > window_Xmax:
            a1.set_xlim(db_freq - window_Xmax, db_freq)
            a2.set_xlim(db_freq - window_Xmax, db_freq)
        else:
            a1.set_xlim(0, window_Xmax)
            a2.set_xlim(0, window_Xmax)

        # Set trip line for individual time-series plot -----------------------------------[R1]
        import triggerModule as sigma
        sigma.trigViolations(a1, UsePLC_DBS, 'RP', YScale_minRP, YScale_maxRP, xucT, xlcT, xusT, xlsT, mnT, sdT)

        timef = time.time()
        lapsedT = timef - timei
        print(f"\nProcess Interval: {lapsedT} sec\n")

        ani = FuncAnimation(fig, asynchronousRP, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                            blit=False)
        plt.tight_layout()
        plt.show()

    # Update Canvas -----------------------------------------------------[]
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack()

    root.mainloop()


# -----------------------------------------------------------------------------------------
def TapeTemperature(vCounter, pType):
    # def LaserPressure(hMeanC, hDevC, hLCLc, hUCLc, hUSLc, hLSLc, dLCLc, dUCLc, plabel, PPerf, pPos, layer, eSMC):
    root = Tk()
    root.title('mPipe Production: Synchronous SPC - Viz: ' + vCounter)
    root.geometry("1800x800")

    # Load Quality Historical Values -----------[]
    ttSize, ttgType, ttSspace, ttHL, ttAL, ttFO, ttParam1, ttParam2, ttParam3, ttParam4, ttParam5 = mq.decryptpProcessLim(
        WON, 'TT')
    # Break down each element to useful list ---------------[Tape Temperature]
    if ttHL and ttParam1 and ttParam2 and ttParam3 and ttParam4 and ttParam5:  #
        ttPerf = '$Pp_{k' + str(ttSize) + '}$'  # Using estimated or historical Mean
        ttlabel = 'Pp'
        # -------------------------------
        One = ttParam1.split(',')  # split into list elements
        Two = ttParam2.split(',')
        Thr = ttParam3.split(',')
        For = ttParam4.split(',')
        Fiv = ttParam5.split(',')
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
            ttUCL = float(One[2].strip("' "))  # Strip out the element of the list
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
            ttUCL = float(Two[2].strip("' "))  # Strip out the element of the list
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
            ttUCL = float(Thr[2].strip("' "))  # Strip out the element of the list
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
            ttUCL = float(For[2].strip("' "))  # Strip out the element of the list
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
            ttUCL = float(Fiv[2].strip("' "))  # Strip out the element of the list
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
        ttPerf = '$Cp_{k' + str(ttSize) + '}$'  # Using Automatic group Mean
        ttlabel = 'Cp'

    # ------------------------------------[End of Tape Temperature Abstraction]
    label = ttk.Label(root,
                      text='DNV Quality Parameter [TT] - [' + pType + ' Mode] - ' + strftime("%a, %d %b %Y", gmtime()),
                      font=LARGE_FONT)
    label.pack(pady=10, padx=10)

    # Define Axes ---------------------#
    fig = Figure(figsize=(25, 13), dpi=100)

    # fig = Figure(figsize=(self.winfo_screenwidth(), self.winfo_screenheight()), dpi=100)
    fig.subplots_adjust(left=0.03, bottom=0.02, right=0.99, top=0.976, hspace=0.14, wspace=0.195)
    a1 = fig.add_subplot(2, 3, (1, 2))  # Laser Power X plot
    a2 = fig.add_subplot(2, 3, (4, 5))  # Laser angle X plot
    a3 = fig.add_subplot(2, 3, (3, 6))  # Process Feeds

    # Declare Plots attributes -----------------------------[]
    plt.rcParams.update({'font.size': 7})
    # Calibrate limits for X-moving Axis -------------------#
    YScale_minTT, YScale_maxTT = ttLSL - 8.5, ttUSL + 8.5   # Roller Force
    sBar_minTT, sBar_maxTT = sLCLtt - 80, sUCLtt + 80       # Calibrate Y-axis for S-Plot
    window_Xmin, window_Xmax = 0, (int(ttSize) + 3)         # windows view = visible data points

    # Declare Plots attributes --------------------------------#
    a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
    a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
    a1.set_title('Roller Pressure [XBar Plot]', fontsize=12, fontweight='bold')
    a2.set_title('Roller Pressure [S Plot]', fontsize=12, fontweight='bold')
    a1.grid(color="0.5", linestyle='-', linewidth=0.5)
    a2.grid(color="0.5", linestyle='-', linewidth=0.5)
    a1.legend(loc='upper left', title='XBar Plot')
    a2.legend(loc='upper right', title='SDev Plot')
    # Initialise runtime limits --------------------------------#
    a1.set_ylim([YScale_minTT, YScale_maxTT], auto=True)
    a1.set_xlim([window_Xmin, window_Xmax])
    # ----------------------------------------------------------#
    a2.set_ylim([sBar_minTT, sBar_maxTT], auto=True)
    a2.set_xlim([window_Xmin, window_Xmax])

    # ---------------------------------------------------------[]
    a3.cla()
    a3.get_yaxis().set_visible(False)
    a3.get_xaxis().set_visible(False)

    # ---------------------------------------------------------[]
    # Define Plot area and axes -
    # ---------------------------------------------------------#
    im10, = a1.plot([], [], 'o-.', label='Tape Temp(°C) - (R1H1)')
    im11, = a1.plot([], [], 'o-', label='Tape Temp(°C) - (R1H2)')
    im12, = a1.plot([], [], 'o-', label='Tape Temp(°C) - (R1H3)')
    im13, = a1.plot([], [], 'o-', label='Tape Temp(°C) - (R1H4)')
    im14, = a2.plot([], [], 'o-', label='Tape Temp(°C)')
    im15, = a2.plot([], [], 'o-', label='Tape Temp(°C)')
    im16, = a2.plot([], [], 'o-', label='Tape Temp(°C)')
    im17, = a2.plot([], [], 'o-', label='Tape Temp(°C)')

    im18, = a1.plot([], [], 'o-.', label='Tape Temp(°C) - (R2H1)')
    im19, = a1.plot([], [], 'o-', label='Tape Temp(°C) - (R2H2)')
    im20, = a1.plot([], [], 'o-', label='Tape Temp(°C) - (R2H3)')
    im21, = a1.plot([], [], 'o-', label='Tape Temp(°C) - (R2H4)')
    im22, = a2.plot([], [], 'o-', label='Tape Temp(°C)')
    im23, = a2.plot([], [], 'o-', label='Tape Temp(°C)')
    im24, = a2.plot([], [], 'o-', label='Tape Temp(°C)')
    im25, = a2.plot([], [], 'o-', label='Tape Temp(°C)')

    im26, = a1.plot([], [], 'o-.', label='Tape Temp(°C) - (R3H1)')
    im27, = a1.plot([], [], 'o-', label='Tape Temp(°C) - (R3H2)')
    im28, = a1.plot([], [], 'o-', label='Tape Temp(°C) - (R3H3)')
    im29, = a1.plot([], [], 'o-', label='Tape Temp(°C) - (R3H4)')
    im30, = a2.plot([], [], 'o-', label='Tape Temp(°C)')
    im31, = a2.plot([], [], 'o-', label='Tape Temp(°C)')
    im32, = a2.plot([], [], 'o-', label='Tape Temp(°C)')
    im33, = a2.plot([], [], 'o-', label='Tape Temp(°C)')

    im34, = a1.plot([], [], 'o-.', label='Tape Temp(°C) - (R4H1)')
    im35, = a1.plot([], [], 'o-', label='Tape Temp(°C) - (R4H2)')
    im36, = a1.plot([], [], 'o-', label='Tape Temp(°C) - (R4H3)')
    im37, = a1.plot([], [], 'o-', label='Tape Temp(°C) - (R4H4)')
    im38, = a2.plot([], [], 'o-', label='Tape Temp(°C)')
    im39, = a2.plot([], [], 'o-', label='Tape Temp(°C)')
    im40, = a2.plot([], [], 'o-', label='Tape Temp(°C)')
    im41, = a2.plot([], [], 'o-', label='Tape Temp(°C)')

    # Statistical Feed ------------------------------------[]
    a3.text(0.466, 0.945, 'Performance Feed - TT', fontsize=16, fontweight='bold', ha='center', va='center',
            transform=a3.transAxes)
    # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
    rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
    rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
    a3.add_patch(rect1)
    a3.add_patch(rect2)
    # ------- Process Performance Pp (the spread)---------------------
    a3.text(0.145, 0.804, ttlabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.328, 0.658, '#Pp', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.650, 0.820, 'Ring ' + ttlabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
    a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
    # ------- Process Performance Ppk (Performance)--------------------#
    a3.text(0.145, 0.403, ttPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.328, 0.282, '#Ppk', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.640, 0.420, 'Ring ' + ttPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
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
    def synchronousTT(ttSize, ttgType, fetchT):
        fetch_no = str(fetchT)  # entry value in string sql syntax

        # Obtain Volatile Data from PLC Host Server ---------------------------[]
        if not inUseAlready:  # Load CommsPlc class once
            import CommsSql as q
            q.DAQ_connect(1, 0)
        else:
            qRP = conn.cursor()
        # Evaluate conditions for SQL Data Fetch ------------------------------[A]
        """
        Load watchdog function with synchronous function every seconds
        """
        # Initialise RT variables ---[]
        autoSpcRun = True
        autoSpcPause = False
        import keyboard                             # for temporary use

        # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
        sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
        # Define PLC/SMC error state -------------------------------------------#

        while True:
            # print('Indefinite looping...')
            if not UsePLC_DBS:                                  # Not Using PLC Data
                import ArrayRP_sqlRLmethod as lq                # DrLabs optimization method
                inProgress = True                               # True for RetroPlay mode
                print('\nAsynchronous controller activated...')
                print('DrLabs' + "' Runtime Optimisation is Enabled!")

                # Get list of relevant SQL Tables using conn() --------------------[]
                ttData = lq.sqlexec(ttSize, ttgType, qRP, tblID, fetchT)
                if keyboard.is_pressed("Alt+Q"):                # Terminate file-fetch
                    qRP.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

            else:
                inProgress = False                              # False for Real-time mode
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
                # play(nudge)     # audible alert

                # -----------------------------------------------------------------[]
                # Allow selective runtime parameter selection on production critical process
                procID = 'RP'
                ttData = q.paramDataRequest(procID, ttSize, ttgType, fetch_no)

        return ttData

    # ================== End of synchronous Method ==========================
    def asynchronousTT(db_freq):

        timei = time.time()  # start timing the entire loop
        UsePLC_DBS = pType  # Query Type

        # Call data loader Method---------------------------#
        rpData = synchronousTT(ttSize, ttgType, db_freq)    # data loading functions
        if UsePLC_DBS == 1:
            import rfVarPLC as qrf
            viz_cycle = 10
            # Call synchronous data function ---------------[]
            columns = vq.validColsPLCData()                 # Load defined valid columns for PLC Data
            df1 = pd.DataFrame(rpData, columns=columns)     # Include table data into python Dataframe
            TT = qrf.loadProcesValues(df1)                  # Join data values under dataframe

        else:
            import rfVarSQL as qrf                          # load SQL variables column names | rfVarSQL
            viz_cycle = 150
            g1 = qq.validCols('WS')                         # Construct Data Column selSqlColumnsTFM.py
            df1 = pd.DataFrame(rpData, columns=g1)          # Import into python Dataframe
            TT = qrf.loadProcesValues(df1)                  # Join data values under dataframe
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
        sigma.trigViolations(a1, UsePLC_DBS, 'RP', YScale_minTT, YScale_maxTT, xucT, xlcT, xusT, xlsT, mnT, sdT)

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
def SubstrateTemp(vCounter, pType):
    # def LaserPressure(hMeanC, hDevC, hLCLc, hUCLc, hUSLc, hLSLc, dLCLc, dUCLc, plabel, PPerf, pPos, layer, eSMC):
    root = Tk()
    root.title('mPipe Production: Synchronous SPC - Viz: ' + vCounter)
    root.geometry("1800x800")
    # Load Quality Historical Values -----------[]
    stSize, stgType, stSspace, stHL, stAL, stFO, stParam1, stParam2, stParam3, stParam4, stParam5 = mq.decryptpProcessLim(
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
                      text='DNV Quality Parameter [ST] - [' + pType + ' Mode] - ' + strftime("%a, %d %b %Y", gmtime()),
                      font=LARGE_FONT)
    label.pack(pady=10, padx=10)

    # Define Axes ---------------------#
    fig = Figure(figsize=(25, 13), dpi=100)

    # fig = Figure(figsize=(self.winfo_screenwidth(), self.winfo_screenheight()), dpi=100)
    fig.subplots_adjust(left=0.03, bottom=0.02, right=0.99, top=0.976, hspace=0.14, wspace=0.195)
    a1 = fig.add_subplot(2, 3, (1, 2))  # Laser Power X plot
    a2 = fig.add_subplot(2, 3, (4, 5))  # Laser angle X plot
    a3 = fig.add_subplot(2, 3, (3, 6))  # Process Feeds

    # Declare Plots attributes -----------------------------[]
    plt.rcParams.update({'font.size': 7})
    # Calibrate limits for X-moving Axis -------------------#
    YScale_minST, YScale_maxST = stLSL - 8.5, stUSL + 8.5       # Substrate Temp
    sBar_minST, sBar_maxST = sLCLst - 80, sUCLst + 80           # Calibrate Y-axis for S-Plot
    window_Xmin, window_Xmax = 0, (int(stSize) + 3)             # windows view = visible data points

    # Declare Plots attributes --------------------------------#
    a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
    a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
    a1.set_title('Substrate Temperature [XBar Plot]', fontsize=12, fontweight='bold')
    a2.set_title('Substrate Temperature [S Plot]', fontsize=12, fontweight='bold')
    a1.grid(color="0.5", linestyle='-', linewidth=0.5)
    a2.grid(color="0.5", linestyle='-', linewidth=0.5)
    a1.legend(loc='upper left', title='XBar Plot')
    a2.legend(loc='upper right', title='SDev Plot')
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
    im10, = a1.plot([], [], 'o-.', label='Substrate Temp(°C) - (R1H1)')
    im11, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R1H2)')
    im12, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R1H3)')
    im13, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R1H4)')
    im14, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im15, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im16, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im17, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')

    im18, = a1.plot([], [], 'o-.', label='Substrate Temp(°C) - (R2H1)')
    im19, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R2H2)')
    im20, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R2H3)')
    im21, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R2H4)')
    im22, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im23, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im24, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im25, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')

    im26, = a1.plot([], [], 'o-.', label='Substrate Temp(°C) - (R3H1)')
    im27, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R3H2)')
    im28, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R3H3)')
    im29, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R3H4)')
    im30, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im31, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im32, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im33, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')

    im34, = a1.plot([], [], 'o-.', label='Substrate Temp(°C) - (R4H1)')
    im35, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R4H2)')
    im36, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R4H3)')
    im37, = a1.plot([], [], 'o-', label='Substrate Temp(°C) - (R4H4)')
    im38, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im39, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im40, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')
    im41, = a2.plot([], [], 'o-', label='Substrate Temp(°C)')

    # Statistical Feed --------------------------------[]:
    a3.text(0.466, 0.945, 'Process Performance Feed', fontsize=16, fontweight='bold', ha='center', va='center',
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
        if not inUseAlready:  # Load CommsPlc class once
            import CommsSql as q
            q.DAQ_connect(1, 0)
        else:
            qRP = conn.cursor()
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
            if not UsePLC_DBS:  # Not Using PLC Data
                import ArrayRP_sqlRLmethod as lq  # DrLabs optimization method
                inProgress = True  # True for RetroPlay mode
                print('\nAsynchronous controller activated...')
                print('DrLabs' + "' Runtime Optimisation is Enabled!")

                # Get list of relevant SQL Tables using conn() --------------------[]
                stData = lq.sqlexec(stSize, stgType, qRP, tblID, fetchT)
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    qRP.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

            else:
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

                # Play visualization ----------------------------------------------[]
                print("Visualization in Play Mode...")
                # play(nudge)     # audible alert

                # -----------------------------------------------------------------[]
                # Allow selective runtime parameter selection on production critical process
                procID = 'ST'
                stData = q.paramDataRequest(procID, stSize, stgType, fetch_no)

        return stData

    # ================== End of synchronous Method ==========================
    def asynchronousST(db_freq):

        timei = time.time()  # start timing the entire loop
        UsePLC_DBS = pType  # Query Type

        # Call data loader Method---------------------------#
        rpData = synchronousST(stSize, stgType, db_freq)  # data loading functions
        if UsePLC_DBS == 1:
            import rfVarPLC as qrf
            viz_cycle = 10
            # Call synchronous data function ---------------[]
            columns = vq.validColsPLCData()                 # Load defined valid columns for PLC Data
            df1 = pd.DataFrame(rpData, columns=columns)     # Include table data into python Dataframe
            ST = qrf.loadProcesValues(df1)                  # Join data values under dataframe

        else:
            import rfVarSQL as qrf                          # load SQL variables column names | rfVarSQL
            viz_cycle = 150
            g1 = qq.validCols('WS')                         # Construct Data Column selSqlColumnsTFM.py
            df1 = pd.DataFrame(rpData, columns=g1)          # Import into python Dataframe
            ST = qrf.loadProcesValues(df1)                  # Join data values under dataframe
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
def WindingSpeed(vCounter, pType):
    # def LaserPressure(hMeanC, hDevC, hLCLc, hUCLc, hUSLc, hLSLc, dLCLc, dUCLc, plabel, PPerf, pPos, layer, eSMC):
    root = Tk()
    root.title('mPipe Production: Synchronous SPC - Viz: ' + vCounter)
    root.geometry("1800x800")

    # dimensions of the main window --------------------------------------[]
    wsSize, wsgType, wsSspace, wsHL, wsAL, wstFO, wsParam1, dud2, dud3, dud4, dud5 = mq.decryptpProcessLim(WON, 'WS')
    # Break down each element to useful list ----------------[Winding Speed]

    if wsHL and wsParam1:  # Roller Pressure TODO - layer metrics to guide TCP01
        wsPerf = '$Pp_{k' + str(wsSize) + '}$'  # Using estimated or historical Mean
        wslabel = 'Pp'
        # -------------------------------
        wsOne = wsParam1.split(',')             # split into list elements
        dTapews = wsOne[1].strip("' ")          # defined Tape Width
        dLayer = wsOne[10].strip("' ")          # Defined Tape Layer

        # Load historical limits for the process------------#
        # if cpTapeW == dTapews and cpLayerNo == range(1, 100):
        wsUCL = float(wsOne[2].strip("' "))     # Strip out the element of the list
        wsLCL = float(wsOne[3].strip("' "))
        wsMean = float(wsOne[4].strip("' "))
        wsDev = float(wsOne[5].strip("' "))
        # --------------------------------
        sUCLws = float(wsOne[6].strip("' "))
        sLCLws = float(wsOne[7].strip("' "))
        # --------------------------------
        wsUSL = (wsUCL - wsMean) / 3 * 6
        wsLSL = (wsMean - wsLCL) / 3 * 6
        # --------------------------------
    else:  # Computes Shewhart constants (Automatic Limits)
        wsUCL = 0
        wsLCL = 0
        wsMean = 0
        wsDev = 0
        sUCLws = 0
        sLCLws = 0
        wsUSL = 0
        wsLSL = 0
        wsPerf = '$Cp_{k' + str(wsSize) + '}$'  # Using Automatic group Mean
        wslabel = 'Cp'

    # ------------------------------------[End of Winding Speed Abstraction]
    label = ttk.Label(root,
                      text='DNV Quality Parameter [WS] - [' + pType + ' Mode] - ' + strftime("%a, %d %b %Y", gmtime()),
                      font=LARGE_FONT)
    label.pack(pady=10, padx=10)

    # Define Axes ---------------------#
    fig = Figure(figsize=(25, 13), dpi=100)
    fig.subplots_adjust(left=0.03, bottom=0.02, right=0.99, top=0.976, hspace=0.14, wspace=0.195)
    # ----------------------------------[]
    a1 = fig.add_subplot(2, 3, (1, 2))  # X Bar plot
    a2 = fig.add_subplot(2, 3, (4, 5))  # S Bar Plot
    a3 = fig.add_subplot(2, 3, (3, 6))  # Process Feeds

    # Declare Plots attributes ---------------------------------[]
    plt.rcParams.update({'font.size': 7})
    # Calibrate limits for X-moving Axis -----------------------#
    YScale_minWS, YScale_maxWS = wsLSL - 8.5, wsUSL + 8.5       # Roller Force
    sBar_minWS, sBar_maxWS = sLCLws - 80, sUCLws + 80           # Calibrate Y-axis for S-Plot
    window_Xmin, window_Xmax = 0, (int(wsSize) + 3)             # windows view = visible data points

    # Declare Plots attributes --------------------------------#
    a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
    a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
    a1.set_title('Winding Speed [XBar Plot]', fontsize=12, fontweight='bold')
    a2.set_title('Winding Speed [S Plot]', fontsize=12, fontweight='bold')
    a1.grid(color="0.5", linestyle='-', linewidth=0.5)
    a2.grid(color="0.5", linestyle='-', linewidth=0.5)
    a1.legend(loc='upper left', title='XBar Plot')
    a2.legend(loc='upper right', title='SDev Plot')
    # Initialise runtime limits --------------------------------#
    a1.set_ylim([YScale_minWS, YScale_maxWS], auto=True)
    a1.set_xlim([window_Xmin, window_Xmax])
    # ----------------------------------------------------------#
    a2.set_ylim([sBar_minWS, sBar_maxWS], auto=True)
    a2.set_xlim([window_Xmin, window_Xmax])

    # ----------------------------------------------------------[]
    a3.cla()
    a3.get_yaxis().set_visible(False)
    a3.get_xaxis().set_visible(False)

    # --------------------------------------------------------------[]
    # Define Plot area and axes -
    # ----------------------------------------------------------------#
    im10, = a1.plot([], [], 'o-.', label='Winding Speed (m/s) - (R1H1)')
    im11, = a1.plot([], [], 'o-', label='Winding Speed (m/s) - (R1H2)')
    im12, = a1.plot([], [], 'o-', label='Winding Speed (m/s) - (R1H3)')
    im13, = a1.plot([], [], 'o-', label='Winding Speed (m/s) - (R1H4)')
    im14, = a2.plot([], [], 'o-', label='Winding Speed (m/s)')
    im15, = a2.plot([], [], 'o-', label='Winding Speed (m/s)')
    im16, = a2.plot([], [], 'o-', label='Winding Speed (m/s)')
    im17, = a2.plot([], [], 'o-', label='Winding Speed (m/s)')

    im18, = a1.plot([], [], 'o-.', label='Winding Speed (m/s) - (R2H1)')
    im19, = a1.plot([], [], 'o-', label='Winding Speed (m/s) - (R2H2)')
    im20, = a1.plot([], [], 'o-', label='Winding Speed (m/s) - (R2H3)')
    im21, = a1.plot([], [], 'o-', label='Winding Speed (m/s) - (R2H4)')
    im22, = a2.plot([], [], 'o-', label='Winding Speed (m/s)')
    im23, = a2.plot([], [], 'o-', label='Winding Speed (m/s)')
    im24, = a2.plot([], [], 'o-', label='Winding Speed (m/s)')
    im25, = a2.plot([], [], 'o-', label='Winding Speed (m/s)')

    im26, = a1.plot([], [], 'o-.', label='Winding Speed (m/s) - (R3H1)')
    im27, = a1.plot([], [], 'o-', label='Winding Speed (m/s) - (R3H2)')
    im28, = a1.plot([], [], 'o-', label='Winding Speed (m/s) - (R3H3)')
    im29, = a1.plot([], [], 'o-', label='Winding Speed (m/s) - (R3H4)')
    im30, = a2.plot([], [], 'o-', label='Winding Speed (m/s)')
    im31, = a2.plot([], [], 'o-', label='Winding Speed (m/s)')
    im32, = a2.plot([], [], 'o-', label='Winding Speed (m/s)')
    im33, = a2.plot([], [], 'o-', label='Winding Speed (m/s)')

    im34, = a1.plot([], [], 'o-.', label='Winding Speed (m/s) - (R4H1)')
    im35, = a1.plot([], [], 'o-', label='Winding Speed (m/s) - (R4H2)')
    im36, = a1.plot([], [], 'o-', label='Winding Speed (m/s) - (R4H3)')
    im37, = a1.plot([], [], 'o-', label='Winding Speed (m/s) - (R4H4)')
    im38, = a2.plot([], [], 'o-', label='Winding Speed (m/s)')
    im39, = a2.plot([], [], 'o-', label='Winding Speed (m/s)')
    im40, = a2.plot([], [], 'o-', label='Winding Speed (m/s)')
    im41, = a2.plot([], [], 'o-', label='Winding Speed (m/s)')

    # Statistical Feed --------------------------------[]:
    a3.text(0.466, 0.945, 'Performance Feed - WS', fontsize=15, fontweight='bold', ha='center', va='center',
            transform=a3.transAxes)
    # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
    rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
    rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
    a3.add_patch(rect1)
    a3.add_patch(rect2)
    # ------- Process Performance Pp (the spread)---------------------
    a3.text(0.145, 0.804, wslabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.328, 0.658, '#Pp', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.650, 0.820, 'Ring ' + wslabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
    a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
    # ------- Process Performance Ppk (Performance)--------------------#
    a3.text(0.145, 0.403, wsPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.328, 0.282, '#Ppk Value', fontsize=16, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.640, 0.420, 'Ring ' + wsPerf, fontsize=14, ha='left', transform=a3.transAxes)
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
    def synchronousWS(wsSize, wsgType, fetchT):
        fetch_no = str(fetchT)      # entry value in string sql syntax

        # Obtain Volatile Data from PLC Host Server ---------------------------[]
        if not inUseAlready:        # Load CommsPlc class once
            import CommsSql as q
            q.DAQ_connect(1, 0)
        else:
            qRP = conn.cursor()
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
            if not UsePLC_DBS:                      # Not Using PLC Data
                import ArrayRP_sqlRLmethod as lq    # DrLabs optimization method
                inProgress = True                   # True for RetroPlay mode
                print('\nAsynchronous controller activated...')
                print('DrLabs' + "' Runtime Optimisation is Enabled!")

                # Get list of relevant SQL Tables using conn() --------------------[]
                tgData = lq.sqlexec(wsSize, wsgType, qRP, tblID, fetchT)
                if keyboard.is_pressed("Alt+Q"):    # Terminate file-fetch
                    qRP.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

            else:
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

                # Play visualization ----------------------------------------------[]
                print("Visualization in Play Mode...")
                # play(nudge)     # audible alert

                # -----------------------------------------------------------------[]
                # Allow selective runtime parameter selection on production critical process
                procID = 'WS'
                wsData = q.paramDataRequest(procID, wsSize, wsgType, fetch_no)

        return wsData

    # ================== End of synchronous Method ==========================
    def asynchronousWS(db_freq):

        timei = time.time()                                 # start timing the entire loop
        UsePLC_DBS = pType                                  # Query Type

        # Call data loader Method---------------------------#
        wsData = synchronousWS(wsSize, wsgType, db_freq)  # data loading functions
        if UsePLC_DBS == 1:
            import rfVarPLC as qrf
            viz_cycle = 10
            # Call synchronous data function ---------------[]
            columns = vq.validColsPLCData()                 # Load defined valid columns for PLC Data
            df1 = pd.DataFrame(wsData, columns=columns)     # Include table data into python Dataframe
            WS = qrf.loadProcesValues(df1)                  # Join data values under dataframe

        else:
            import rfVarSQL as qrf                          # load SQL variables column names | rfVarSQL
            viz_cycle = 150
            g1 = qq.validCols('WS')                         # Construct Data Column selSqlColumnsTFM.py
            df1 = pd.DataFrame(wsData, columns=g1)          # Import into python Dataframe
            WS = qrf.loadProcesValues(df1)                  # Join data values under dataframe
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
        im10.set_ydata((WS[0]).rolling(window=wsSize, min_periods=1).mean()[0:db_freq])  # head 1
        im11.set_ydata((WS[1]).rolling(window=wsSize, min_periods=1).mean()[0:db_freq])  # head 2
        im12.set_ydata((WS[2]).rolling(window=wsSize, min_periods=1).mean()[0:db_freq])  # head 3
        im13.set_ydata((WS[3]).rolling(window=wsSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 1 ---------#
        mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(wsHL, wsSize, 'WS')
        # ---------------------------------------#
        im14.set_ydata((WS[4]).rolling(window=wsSize, min_periods=1).mean()[0:db_freq])  # head 1
        im15.set_ydata((WS[5]).rolling(window=wsSize, min_periods=1).mean()[0:db_freq])  # head 2
        im16.set_ydata((WS[6]).rolling(window=wsSize, min_periods=1).mean()[0:db_freq])  # head 3
        im17.set_ydata((WS[7]).rolling(window=wsSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 2 ---------#
        mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(wsHL, wsSize, 'WS')
        # ---------------------------------------#
        im18.set_ydata((WS[8]).rolling(window=wsSize, min_periods=1).mean()[0:db_freq])  # head 1
        im19.set_ydata((WS[9]).rolling(window=wsSize, min_periods=1).mean()[0:db_freq])  # head 2
        im20.set_ydata((WS[10]).rolling(window=wsSize, min_periods=1).mean()[0:db_freq])  # head 3
        im21.set_ydata((WS[11]).rolling(window=wsSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 3 ---------#
        mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(wsHL, wsSize, 'WS')
        # ---------------------------------------#
        im22.set_ydata((WS[12]).rolling(window=wsSize, min_periods=1).mean()[0:db_freq])  # head 1
        im23.set_ydata((WS[13]).rolling(window=wsSize, min_periods=1).mean()[0:db_freq])  # head 2
        im24.set_ydata((WS[14]).rolling(window=wsSize, min_periods=1).mean()[0:db_freq])  # head 3
        im25.set_ydata((WS[15]).rolling(window=wsSize, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 4 ---------#
        mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(wsHL, wsSize, 'WS')
        # ---------------------------------------#
        # S Plot Y-Axis data points for StdDev ----------------------------------------
        im26.set_ydata((WS[0]).rolling(window=wsSize, min_periods=1).std()[0:db_freq])
        im27.set_ydata((WS[1]).rolling(window=wsSize, min_periods=1).std()[0:db_freq])
        im28.set_ydata((WS[2]).rolling(window=wsSize, min_periods=1).std()[0:db_freq])
        im29.set_ydata((WS[3]).rolling(window=wsSize, min_periods=1).std()[0:db_freq])

        im30.set_ydata((WS[4]).rolling(window=wsSize, min_periods=1).std()[0:db_freq])
        im31.set_ydata((WS[5]).rolling(window=wsSize, min_periods=1).std()[0:db_freq])
        im32.set_ydata((WS[6]).rolling(window=wsSize, min_periods=1).std()[0:db_freq])
        im33.set_ydata((WS[7]).rolling(window=wsSize, min_periods=1).std()[0:db_freq])

        im34.set_ydata((WS[8]).rolling(window=wsSize, min_periods=1).std()[0:db_freq])
        im35.set_ydata((WS[9]).rolling(window=wsSize, min_periods=1).std()[0:db_freq])
        im36.set_ydata((WS[10]).rolling(window=wsSize, min_periods=1).std()[0:db_freq])
        im37.set_ydata((WS[11]).rolling(window=wsSize, min_periods=1).std()[0:db_freq])

        im38.set_ydata((WS[12]).rolling(window=wsSize, min_periods=1).std()[0:db_freq])
        im39.set_ydata((WS[13]).rolling(window=wsSize, min_periods=1).std()[0:db_freq])
        im40.set_ydata((WS[14]).rolling(window=wsSize, min_periods=1).std()[0:db_freq])
        im41.set_ydata((WS[15]).rolling(window=wsSize, min_periods=1).std()[0:db_freq])

        # Compute entire Process Capability -----------#
        if not wsHL:
            mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLa, dLCLa, ppT, pkT, xline, sline = tq.tAutoPerf(wsSize, mnA, mnB,
                                                                                                  mnC, mnD, sdA,
                                                                                                  sdB, sdC, sdD)
        else:
            xline, sline = wsMean, wsDev
            mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLa, dLCLa, ppT, pkT = tq.tManualPerf(mnA, mnB, mnC, mnD, sdA, sdB,
                                                                                      sdC, sdD, wsUSL, wsLSL, wsUCL,
                                                                                      wsLCL)
        # # Declare Plots attributes ------------------------------------------------------------[]
        # XBar Mean Plot
        a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
        a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')            # 3 Sigma span (Purple)
        a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')            # grey area
        a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
        # ---------------------- sBar_minTT, sBar_maxTT -------[]
        # Define Legend's Attributes  ----
        a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
        a2.axhspan(sLCLws, sUCLws, facecolor='#F9C0FD', edgecolor='#F9C0FD')        # 1 Sigma Span
        a2.axhspan(sUCLws, sBar_maxWS, facecolor='#CCCCFF', edgecolor='#CCCCFF')    # 1 Sigma above the Mean
        a2.axhspan(sBar_minWS, sLCLws, facecolor='#CCCCFF', edgecolor='#CCCCFF')

        # Setting up the parameters for moving windows Axes ---------------------------------[]
        if db_freq > window_Xmax:
            a1.set_xlim(db_freq - window_Xmax, db_freq)
            a2.set_xlim(db_freq - window_Xmax, db_freq)
        else:
            a1.set_xlim(0, window_Xmax)
            a2.set_xlim(0, window_Xmax)

        # Set trip line for individual time-series plot -----------------------------------[R1]
        import triggerModule as sigma
        sigma.trigViolations(a1, UsePLC_DBS, 'WS', YScale_minWS, YScale_maxWS, xucT, xlcT, xusT, xlsT, mnT, sdT)

        timef = time.time()
        lapsedT = timef - timei
        print(f"\nProcess Interval: {lapsedT} sec\n")

        ani = FuncAnimation(fig, asynchronousWS, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                            blit=False)
        plt.tight_layout()
        plt.show()

    # Update Canvas -----------------------------------------------------[]
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack()

    root.mainloop()


def tapeGap(vCounter, pType):
    # def LaserPressure(hMeanC, hDevC, hLCLc, hUCLc, hUSLc, hLSLc, dLCLc, dUCLc, plabel, PPerf, pPos, layer, eSMC):
    root = Tk()
    root.title('mPipe Production: Synchronous SPC - Viz: ' + vCounter)
    root.geometry("1800x800")

    # Load metrics from config -----------------------------------[Tape Gap]
    tgSize, tggType, tgSspace, tgHL, tgAL, tgtFO, tgParam1, dud2, dud3, dud4, dud5 = mq.decryptpProcessLim(WON, 'TG')

    # Break down each element to useful list ---------------------[Tape Gap]
    if tgHL and tgParam1:
        tgPerf = '$Pp_{k' + str(tgSize) + '}$'                   # Estimated or historical Mean
        tglabel = 'Pp'
        # -------------------------------
        tgOne = tgParam1.split(',')                             # split into list elements
        dTapetg = tgOne[1].strip("' ")                          # defined Tape Width
        dLayer = tgOne[10].strip("' ")                          # Defined Tape Layer

        # Load historical limits for the process----------------#
        # if cpTapeW == dTapetg and cpLayerNo == range(1, 100):   # '*.*',  | *.*
        tgUCL = float(tgOne[2].strip("' "))                     # Strip out the element of the list
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

    # -----------------------------------------------------[End of Tape Gap]
    label = ttk.Label(root,
                      text='DNV Quality Parameter [TG] - [' + pType + ' Mode] - ' + strftime("%a, %d %b %Y", gmtime()),
                      font=LARGE_FONT)
    label.pack(pady=10, padx=10)

    # Define Axes ---------------------#
    fig = Figure(figsize=(25, 13), dpi=100)
    fig.subplots_adjust(left=0.03, bottom=0.02, right=0.99, top=0.976, hspace=0.14, wspace=0.195)
    # ---------------------------------[]
    a1 = fig.add_subplot(2, 5, (1, 2))    # xbar plot
    a2 = fig.add_subplot(2, 5, (3, 4))    # cumulative plot
    a3 = fig.add_subplot(2, 5, (6, 7))    # s bar plot
    a4 = fig.add_subplot(2, 5, (8, 9))    # cumulative contours
    a5 = fig.add_subplot(2, 5, (5, 10))   # CPk/PPk Feed

    # Declare Plots attributes -----------------------------------------[]
    plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends

    # Calibrate limits for X-moving Axis -----------------------#
    YScale_minTG, YScale_maxTG = tgLSL - 8.5, tgUSL + 8.5       # Roller Force
    sBar_minTG, sBar_maxTG = sLCLtg - 80, sUCLtg + 80           # Calibrate Y-axis for S-Plot
    window_Xmin, window_Xmax = 0, (int(tgSize) + 3)             # windows view = visible data points
    # ----------------------------------------------------------#

    # Declare Plots attributes --------------------------------#
    a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
    a3.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
    a1.set_title('Tape Gap [XBar Plot]', fontsize=12, fontweight='bold')
    a3.set_title('Tape Gap [S Plot]', fontsize=12, fontweight='bold')
    a1.grid(color="0.5", linestyle='-', linewidth=0.5)
    a3.grid(color="0.5", linestyle='-', linewidth=0.5)
    a1.legend(loc='upper left', title='XBar Plot')
    a3.legend(loc='upper right', title='SDev Plot')
    # Initialise runtime limits -------------------------------#
    a1.set_ylim([YScale_minTG, YScale_maxTG], auto=True)
    a1.set_xlim([window_Xmin, window_Xmax])
    # ----------------------------------------------------------#
    a3.set_ylim([sBar_minTG, sBar_maxTG], auto=True)
    a3.set_xlim([window_Xmin, window_Xmax])

    # ----------------------------------------------------------[]
    a5.cla()
    a5.get_yaxis().set_visible(False)
    a5.get_xaxis().set_visible(False)

    # ----------------------------------------------------------[]
    # Define Plot area and axes -
    # ----------------------------------------------------------#
    im10, = a1.plot([], [], 'o-', label='Tape Gap(mm) - (A1)')
    im11, = a1.plot([], [], 'o-', label='Tape Gap(mm) - (B1)')
    im12, = a1.plot([], [], 'o-', label='Tape Gap(mm) - (A2)')
    im13, = a1.plot([], [], 'o-', label='Tape Gap(mm) - (B2)')
    im14, = a1.plot([], [], 'o-', label='Tape Gap(°C) - (A3)')
    im15, = a1.plot([], [], 'o-', label='Tape Gap(°C) - (B3)')
    im16, = a1.plot([], [], 'o-', label='Tape Gap(°C) - (A4)')
    im17, = a1.plot([], [], 'o-', label='Tape Gap(°C) - (B4)')
    # ------------ S Bar Plot ------------------------------
    im18, = a2.plot([], [], 'o-', label='Tape Gap(mm)')
    im19, = a2.plot([], [], 'o-', label='Tape Gap(mm)')
    im20, = a2.plot([], [], 'o-', label='Tape Gap(mm)')
    im21, = a2.plot([], [], 'o-', label='Tape Gap(mm)')
    im22, = a2.plot([], [], 'o-', label='Tape Gap(mm)')
    im23, = a2.plot([], [], 'o-', label='Tape Gap(mm)')
    im24, = a2.plot([], [], 'o-', label='Tape Gap(mm)')
    im25, = a2.plot([], [], 'o-', label='Tape Gap(mm)')

    # Statistical Feed ------------------------------------------[]
    a5.text(0.466, 0.945, 'Performance Feed - TS', fontsize=15, fontweight='bold', ha='center', va='center',
            transform=a5.transAxes)
    # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
    rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
    rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
    a5.add_patch(rect1)
    a5.add_patch(rect2)
    # ------- Process Performance Pp (the spread)----------------[]
    a5.text(0.145, 0.804, tglabel, fontsize=12, fontweight='bold', ha='center', transform=a5.transAxes)
    a5.text(0.328, 0.658, '#Pp Value', fontsize=18, fontweight='bold', ha='center', transform=a5.transAxes)
    a5.text(0.650, 0.820, 'Ring ' + tglabel, fontsize=12, ha='left', transform=a5.transAxes)
    a5.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a5.transAxes)
    a5.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a5.transAxes)
    a5.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a5.transAxes)
    a5.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a5.transAxes)
    # ------- Process Performance Ppk (Performance)--------------[]
    a5.text(0.145, 0.403, tgPerf, fontsize=12, fontweight='bold', ha='center', transform=a5.transAxes)
    a5.text(0.328, 0.282, '#Ppk Value', fontsize=16, fontweight='bold', ha='center', transform=a5.transAxes)
    a5.text(0.640, 0.420, 'Ring ' + tgPerf, fontsize=12, ha='left', transform=a5.transAxes)
    # -----------------------------------------------------------[]
    a5.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=a5.transAxes)
    a5.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=a5.transAxes)
    a5.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=a5.transAxes)
    a5.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=a5.transAxes)
    # ----- Pipe Position and SMC Status -----
    a5.text(0.080, 0.080, 'Pipe Position: ' + pPos + '\nProcessing Layer #' + layer, fontsize=12, ha='left',
            transform=a5.transAxes)
    a5.text(0.080, 0.036, 'SMC Status: ' + eSMC, fontsize=12, ha='left', transform=a5.transAxes)

    # ---------------- EXECUTE SYNCHRONOUS METHOD -----------------------------#
    def synchronousTG(tgSize, tggType, fetchT):
        fetch_no = str(fetchT)  # entry value in string sql syntax

        # Obtain Volatile Data from PLC Host Server ---------------------------[]
        if not inUseAlready:  # Load CommsPlc class once
            import CommsSql as q
            q.DAQ_connect(1, 0)
        else:
            qRP = conn.cursor()
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
            if not UsePLC_DBS:                                      # Not Using PLC Data
                import ArrayRP_sqlRLmethod as lq                    # DrLabs optimization method
                inProgress = True                                   # True for RetroPlay mode
                print('\nAsynchronous controller activated...')
                print('DrLabs' + "' Runtime Optimisation is Enabled!")

                # Get list of relevant SQL Tables using conn() --------------------[]
                tgData = lq.sqlexec(tgSize, tggType, qRP, tblID, fetchT)
                if keyboard.is_pressed("Alt+Q"):                    # Terminate file-fetch
                    qRP.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

            else:
                inProgress = False                                  # False for Real-time mode
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
                        # play(error)                                               # Pause mode with audible Alert
                        print("\nVisualization in Paused Mode...")
                else:
                    autoSpcPause = False

                # Play visualization ----------------------------------------------[]
                print("Visualization in Play Mode...")
                # play(nudge)     # audible alert

                # -----------------------------------------------------------------[]
                # Allow selective runtime parameter selection on production critical process
                procID = 'TG'
                tgData = q.paramDataRequest(procID, tgSize, tggType, fetch_no)

        return tgData

    # ================== End of synchronous Method ==========================

    def asynchronousTG(db_freq):

        timei = time.time()  # start timing the entire loop
        UsePLC_DBS = pType   # Query Type
        # declare asynchronous variables ------------------[]

        # Call data loader Method--------------------------[]
        tgData = synchronousTG(tgSize, tggType, db_freq)     # data loading functions
        if UsePLC_DBS == 1:
            import rfVarPLC as qrf
            viz_cycle = 10
            columns = vq.validColsPLCData()                 # Load defined valid columns for PLC Data
            df1 = pd.DataFrame(tgData, columns=columns)     # Include table data into python Dataframe
            TG = qrf.loadProcesValues(df1)                  # Join data values under dataframe

        else:
            import rfVarSQL as qrf                          # load SQL variables column names | rfVarSQL
            viz_cycle = 150
            g1 = qq.validCols('TG')                         # Construct Data Column selSqlColumnsTFM.py
            df1 = pd.DataFrame(tgData, columns=g1)          # Import into python Dataframe
            TG = qrf.loadProcesValues(df1)                  # Join data values under dataframe
        print('\nDataFrame Content', df1.head(10))          # Preview Data frame head
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
        im10.set_ydata((TG[0]).rolling(window=tgSize, min_periods=1).mean()[0:db_freq])  # Segment 1
        im11.set_ydata((TG[1]).rolling(window=tgSize, min_periods=1).mean()[0:db_freq])  # Segment 2
        im12.set_ydata((TG[2]).rolling(window=tgSize, min_periods=1).mean()[0:db_freq])  # Segment 3
        im13.set_ydata((TG[3]).rolling(window=tgSize, min_periods=1).mean()[0:db_freq])  # Segment 4
        # ------ Evaluate Pp for Segments ---------#
        mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(tgHL, tgSize, 'TG')
        # ---------------------------------------#
        im14.set_ydata((TG[4]).rolling(window=tgSize, min_periods=1).mean()[0:db_freq])  # Segment 1
        im15.set_ydata((TG[5]).rolling(window=tgSize, min_periods=1).mean()[0:db_freq])  # Segment 2
        im16.set_ydata((TG[6]).rolling(window=tgSize, min_periods=1).mean()[0:db_freq])  # Segment 3
        im17.set_ydata((TG[7]).rolling(window=tgSize, min_periods=1).mean()[0:db_freq])  # Segment 4
        # ------ Evaluate Pp for Ring 2 ---------#
        mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(tgHL, tgSize, 'TG')

        # S Plot Y-Axis data points for StdDev ----------------------------------------[# S Bar Plot]
        im18.set_ydata((TG[0]).rolling(window=tgSize, min_periods=1).std()[0:db_freq])
        im19.set_ydata((TG[1]).rolling(window=tgSize, min_periods=1).std()[0:db_freq])
        im20.set_ydata((TG[2]).rolling(window=tgSize, min_periods=1).std()[0:db_freq])
        im21.set_ydata((TG[3]).rolling(window=tgSize, min_periods=1).std()[0:db_freq])

        im22.set_ydata((TG[4]).rolling(window=tgSize, min_periods=1).std()[0:db_freq])
        im23.set_ydata((TG[5]).rolling(window=tgSize, min_periods=1).std()[0:db_freq])
        im24.set_ydata((TG[6]).rolling(window=tgSize, min_periods=1).std()[0:db_freq])
        im25.set_ydata((TG[7]).rolling(window=tgSize, min_periods=1).std()[0:db_freq])

        if not tgHL:
            mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLd, dLCLd, ppT, pkT, xline, sline = tq.tAutoPerf(tgSize, mnA,
                                                                                                  mnB,
                                                                                                  0, 0, sdA,
                                                                                                  sdB, 0, 0)
        else:
            xline, sline = tgMean, tgDev
            mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLd, dLCLd, ppT, pkT = tq.tManualPerf(mnA, mnB, 0, 0, sdA, sdB,
                                                                                      0, 0, tgUSL, tgLSL, tgUCL,
                                                                                      tgLCL)
        # # Declare Plots attributes ------------------------------------------------------------[]
        # XBar Mean Plot
        a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
        a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 3 Sigma span (Purple)
        a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
        a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
        # ---------------------- sBar_minTG, sBar_maxTG -------[]
        # Define Legend's Attributes  ----
        a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
        a2.axhspan(sLCLtg, sUCLtg, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 1 Sigma Span
        a2.axhspan(sUCLtg, sBar_maxTG, facecolor='#CCCCFF', edgecolor='#CCCCFF')  # 1 Sigma above the Mean
        a2.axhspan(sBar_minTG, sLCLtg, facecolor='#CCCCFF', edgecolor='#CCCCFF')

        # Setting up the parameters for moving windows Axes ---------------------------------[]
        if db_freq > window_Xmax:
            a1.set_xlim(db_freq - window_Xmax, db_freq)
            a2.set_xlim(db_freq - window_Xmax, db_freq)
        else:
            a1.set_xlim(0, window_Xmax)
            a2.set_xlim(0, window_Xmax)

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

    root.mainloop()


# ---------------------- Port windows into parallel processing ----------[]

def myMain(qType):
    # global pType
    pType = qType
    # runType.append(pType)
    print('\nP-Type..:', pType)
    # if GPU -------------------------------------------------#
    p1 = Process(target=RollerPressure, args=(countA, pType))           #, name="CascadeRF")
    p2 = Process(target=TapeTemperature, args=(countB, pType))          #, name="CascadeTT")
    p3 = Process(target=SubstrateTemp, args=(countC, pType))            #, name="CascadeST")
    p4 = Process(target=WindingSpeed, args=(countD, pType))             # , name="CascadeTS")
    p5 = Process(target=tapeGap, args=(countE, pType))                  #, name="CascadeTG")

    p1.start()                                                          # Quality parameter 1
    p2.start()                                                          # Quality parameter 2
    p3.start()                                                          # Quality parameter 3
    p4.start()                                                          # Quality parameter 4
    p5.start()                                                          # Quality parameter 5
    # --------------------- Join the threads -------------------#
    print('\nP1 #:', p1)
    print('P2 #:', p2)
    print('P3 #:', p3)
    print('P4 #:', p4)
    print('P5 #:', p5)
    # print('Proces 1', p1.pid) # display only the process number(int)
    # print('Proces 2', p2.pid)
    # print('Proces 3', p3.pid)
    # print('Proces 1', p4.pid)
    # # --------------------- Join the threads -----------------#
    # p1.join()
    # p2.join()
    # p3.join()
    # p4.join()
    # returned values for evaluation and closing out of the process

    return p1, p2, p3, p4, p5

# -------------------------------------------------------------------------------------------------------- [if on GPU]
# https://docs.python.org/3/library/multiprocessing.html#multiprocessing-programming
# 1. Avoid shared state
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
# Main construct provides a standard entry point to stand alone app; best practice

# if __name__ == '__main__':
#     freeze_support()            # omitted if the program will be run normally instead of frozen
#     set_start_method('spawn')   # This enables the newly spawned Python interpreter to safely import the module
#     myMain()

# ------ END OF PIPELINE --------------------------------------------------------------[]

