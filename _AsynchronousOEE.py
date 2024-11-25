#
# MODULE ASYNCHRONOUS Data Frame (moduleAsynchronousData.py)
# Magma Global Ltd., TechnipFMC
# Author: Robert B. Labs, PhD
# -----------------------------------------------------

# import synchronous function to load data -----------[]
import time
import numpy as np
import pandas as pd
# ----------------------------------#
import rhAnalyzer as rh
import moduleSynchronousData as rt  # call class function
import selSqlColumnsTFM as qq       # Post processing columns
import selPlcColumnsTFM as vq       # Synchronous RT columns
import rtP_Evaluator as tq
from matplotlib.animation import FuncAnimation

UsePLC_DBS = False


def asynchronousDF(a1, a2, smp_Sz, optm, db_freq):
    timei = time.time()                 # start timing the entire loop

    # declare asynchronous variables -----[]
    tMean1, tMean2, tMean3, tMean4, tMean5, tMean6, tMean7, tMean8 = 0, 0, 0, 0, 0, 0, 0, 0
    Pp1, Pp2, Pp3, Pp4, Pp5, Pp6, Pp7, Pp8 = 0, 0, 0, 0, 0, 0, 0, 0
    PpkL1, PpkL2, PpkL3, PpkL4, PpkU1, PpkU2, PpkU3, PpkU4 = 0, 0, 0, 0, 0, 0, 0, 0
    # ----------------------------------------------------------------[]
    # Define Plot area and axes -
    # ----------------------------------------------------------------#
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

    if UsePLC_DBS:
        import ringVarPLC as qv                                     # load PLC variables column names

        # Call synchronous data function ------------------------[]
        sql_OEE, plcData = rt.synchronousPLC(conn, smp_Sz, smp_St, db_freq)

        columns = vq.validColsPLCData()                             # Load defined valid columns for PLC Data
        df1 = pd.DataFrame(sql1, columns=columns)                   # Include table data into python Dataframe
        tlpos, RF, mPar = qv.loadRingsData(df1, 'PLC')

        md = 1                                                      # mode processing using PLC Query
        procID = 'RF'
        print('\nPLC Content', df1.head(10))
        print("Memory Usage:", df1.info(verbose=False))             # Check memory utilization

    else:
        import ringVarSQL as qv     # load SQL variables column names
        sql1, sql2, sql3, sql4, sql5, sql6, sql7, sql8 = rt.synchronousSQL(conn, smp_Sz, smp_St, OTlayr, EPpos, db_freq)

        g1 = qq.validCols('RF')
        d1 = pd.DataFrame(sql1, columns=g1)  # Import into python Dataframe
        # g2 = qq.validCols('LA')
        # d2 = pd.DataFrame(sql2, columns=g2)
        # g3 = qq.validCols('HT')
        # d3 = pd.DataFrame(sql3, columns=g3)  # Import into python Dataframe
        # g4 = qq.validCols('DL')
        # d4 = pd.DataFrame(sql4, columns=g4)
        # g5 = qq.validCols('RF')
        # d5 = pd.DataFrame(sql5, columns=g5)
        # g6 = qq.validCols('TT')
        # d6 = pd.DataFrame(sql6, columns=g6)
        # g7 = qq.validCols('ST')
        # d7 = pd.DataFrame(sql7, columns=g7)
        # g8 = qq.validCols('TG')
        # d8 = pd.DataFrame(sql8, columns=g8)
        # Performing SQL Tables Concatenation... -----------------------#
        df1 = pd.concat([d1, d2, d3, d4, d5, d6, d7, d8], axis=1)  # concatenate table

        md = 0
        procID = 'RF'
        print('\nSQL Content', df1.head(10))
        print("Memory Usage:", df1.info(verbose=False))  # Check memory utilization
        RF = qv.loadSQLringData(df1, combo)

    # ----------------------------------------------------------------------[]
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
    # X Plot Y-Axis data points for XBar --------------------------------------------------[  # Ring 1 ]
    if optm:
        im10.set_ydata((RF[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
        im11.set_ydata((RF[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 2
        im12.set_ydata((RF[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 3
        im13.set_ydata((RF[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 1 ---------#
        mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(uhl, smp_Sz, 'RF')
        # ---------------------------------------#
        im14.set_ydata((RF[4]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
        im15.set_ydata((RF[5]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 2
        im16.set_ydata((RF[6]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 3
        im17.set_ydata((RF[7]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 2 ---------#
        mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(uhl, smp_Sz, 'RF')
        # ---------------------------------------#
        im18.set_ydata((RF[8]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
        im19.set_ydata((RF[9]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 2
        im20.set_ydata((RF[10]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 3
        im21.set_ydata((RF[11]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 3 ---------#
        mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(uhl, smp_Sz, 'RF')
        # ---------------------------------------#
        im22.set_ydata((RF[12]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
        im23.set_ydata((RF[13]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 2
        im24.set_ydata((RF[14]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 3
        im25.set_ydata((RF[15]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 4 ---------#
        mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(uhl, smp_Sz, 'RF')
        # ---------------------------------------#
        # S Plot Y-Axis data points for StdDev ----------------------------------------
        im26.set_ydata((RF[0]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im27.set_ydata((RF[1]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im28.set_ydata((RF[2]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im29.set_ydata((RF[3]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])

        im30.set_ydata((RF[4]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im31.set_ydata((RF[5]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im32.set_ydata((RF[6]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im33.set_ydata((RF[7]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])

        im34.set_ydata((RF[8]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im35.set_ydata((RF[9]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im36.set_ydata((RF[10]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im37.set_ydata((RF[11]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])

        im38.set_ydata((RF[12]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im39.set_ydata((RF[13]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im40.set_ydata((RF[14]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im41.set_ydata((RF[15]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
    else:
        # X Plot the mean of 20 data points as a single point---------- no of rows at a time
        im10.set_ydata((RF[0]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im11.set_ydata((RF[1]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im12.set_ydata((RF[2]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im13.set_ydata((RF[3]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        # ------ Evaluate Pp for Ring 4 ---------#
        mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(uhl, smp_Sz, 'RF')
        # ---------------------------------------#
        im14.set_ydata((RF[4]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im15.set_ydata((RF[5]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im16.set_ydata((RF[6]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im17.set_ydata((RF[7]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        # ------ Evaluate Pp for Ring 4 ---------#
        mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(uhl, smp_Sz, 'RF')
        # ---------------------------------------#
        im18.set_ydata((RF[8]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im19.set_ydata((RF[9]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im20.set_ydata((RF[10]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im21.set_ydata((RF[11]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        # ------ Evaluate Pp for Ring 4 ---------#
        mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(uhl, smp_Sz, 'RF')
        # ---------------------------------------#
        im22.set_ydata((RF[12]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im23.set_ydata((RF[13]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im24.set_ydata((RF[14]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im25.set_ydata((RF[15]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        # ------ Evaluate Pp for Ring 4 ---------#
        mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(uhl, smp_Sz, 'RF')
        # ---------------------------------------#

        # S Plot Y-Axis data points for StdDev ------------------------------------------[]
        im26.set_ydata((RF[0]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im27.set_ydata((RF[1]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im28.set_ydata((RF[2]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im29.set_ydata((RF[3]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im30.set_ydata((RF[4]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im31.set_ydata((RF[5]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im32.set_ydata((RF[6]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im33.set_ydata((RF[7]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im34.set_ydata((RF[8]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im35.set_ydata((RF[9]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im36.set_ydata((RF[10]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im37.set_ydata((RF[11]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im38.set_ydata((RF[12]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im39.set_ydata((RF[13]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im40.set_ydata((RF[14]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im41.set_ydata((RF[15]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
    # Compute entire Process Capability -----------#
    if not uhl:
        mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLa, slcT, ppT, pkT, xline, sline = tq.tAutoPerf(smp_Sz, mnA, mnB,
                                                                                             mnC, mnD, sdA,
                                                                                             sdB, sdC, sdD)
    else:
        xline, sline = hMeanA, hDevA
        mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLa, dLCLa, ppT, pkT = tq.tManualPerf(mnA, mnB, mnC, mnD, sdA, sdB,
                                                                                  sdC, sdD, hUSLa, hLSLa, hUCLa,
                                                                                  hLCLa)
    # Declare Plots attributes ------------------------------------------------------------[]
    a1.grid(color="0.5", linestyle='-', linewidth=0.5)
    a2.grid(color="0.5", linestyle='-', linewidth=0.5)
    # a1.legend(loc='upper left')
    a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
    a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")

    # Evaluate the current Tape Layer if in RetroPlay Mode: -------------------------------[]
    if not UsePLC_DBS:
        lID = HTlayr[0]  # Static Values from SQL Tables
        pPos = EPpos[0]  # Pipe relative Position
        # import realTPostSQLupdate as pq     # Real Time SQL Query
        # pq.recall_fromSQL_WON(WON)

    elif UsePLC_DBS:  # Use PLC Query (synchronous realtime)
        lID = tlpos[1]  # Layer No - Dynamic values from real-time PLC
        pPos = tlpos[0]  # Pipe Position - Dynamic values from PLC
        # import realTimePLCupdate as pq      # Real Time PLC Query
        # pq.recall_fromPLC_WON(WON)
    else:
        lID = 'N/A'  # Layer No - Dynamic values from real-time PLC
        pPos = 'N/A'
    print('\nUpdating Statistical exceptions....')

    # Capture statistical values from each chosen processes ----------------------------[]
    WON = processWON[0]  # provide WON details
    # print('\nWork Order Number:', WON)

    # Define limits for XB Plots ----------------------------------#
    a1.axhline(y=xline, color="green", linestyle="-", linewidth=1)
    a1.axhline(y=xucT, color="blue", linestyle="--", linewidth=0.95)
    a1.axhline(y=xlcT, color="blue", linestyle="--", linewidth=0.95)
    a1.axhline(y=xusT, color="red", linestyle="--", linewidth=0.99)
    a1.axhline(y=xlsT, color="red", linestyle="--", linewidth=0.99)
    # Define limits for S Plots -----------------------------------#
    a2.axhline(y=sline, color="green", linestyle="-", linewidth=1)
    a2.axhline(y=dUCLa, color="blue", linestyle="-", linewidth=0.95)
    a2.axhline(y=dLCLa, color="blue", linestyle="-", linewidth=0.95)
    # Define dynamic annotation ------------------------------------#
    f.text(0.75, 0.79, 'UCL', size=12, color='purple')  # X Bar
    f.text(0.75, 0.64, 'LCL', size=12, color='purple')  # X Bar
    # ---
    f.text(0.75, 0.43, 'UCL', size=12, color='purple')  # S Bar
    f.text(0.75, 0.20, 'LCL', size=12, color='purple')  # S Bar

    # Model data --------------------------------------------------[]
    # a1.plot([1, 2, 3, 4, 5, 6, 7, 8], [5, 6, 1, 3, 8, 9, 3, 5])
    # a2.plot([1, 2, 3, 4, 5, 6, 7, 8], [4, 5, 6, 1, 3, 0, 4, 2])

    a3.cla()
    a3.get_yaxis().set_visible(False)
    a3.get_xaxis().set_visible(False)

    # Statistical Feed ----------------------------------------------[]
    a3.text(0.466, 0.945, 'RF Performance Feed', fontsize=16, fontweight='bold', ha='center', va='center',
            transform=a3.transAxes)
    # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
    rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
    rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
    a3.add_patch(rect1)
    a3.add_patch(rect2)
    # ------- Process Performance Pp (the spread)---------------------
    a3.text(0.145, 0.804, plabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.328, 0.658, '#Pp Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.650, 0.820, 'Ring ' + plabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
    a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
    # ------- Process Performance Ppk (Performance)---------------------
    a3.text(0.145, 0.403, PPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.328, 0.282, '#Ppk Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
    a3.text(0.640, 0.420, 'Ring ' + PPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
    # -------------------------------------
    a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
    a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
    # ----- Pipe Position and SMC Status -----
    a3.text(0.080, 0.090, 'Pipe Position: ' + pPos + '    Processing Layer #' + layer, fontsize=12, ha='left',
            transform=a3.transAxes)
    a3.text(0.080, 0.036, 'SMC Status: ' + eSMC, fontsize=12, ha='left', transform=a3.transAxes)

    # Setting up the parameters for moving windows Axes ---------------------------------[]
    if db_freq > window_Xmax:
        a1.set_xlim(db_freq - window_Xmax, db_freq)
        a2.set_xlim(db_freq - window_Xmax, db_freq)
    else:
        a1.set_xlim(0, window_Xmax)
        a2.set_xlim(0, window_Xmax)

    # Set trip line for individual time-series plot -----------------------------------[R1]
    import triggerModule as sigma
    sigma.trigViolations(a1, md, procID, YScale_minRF, YScale_maxRF, xucT, xlcT, xusT, xlsT, mnT, sdT, lID, pPos)

    timef = time.time()
    lapsedT = timef - timei
    print(f"\nProcess Interval: {lapsedT} sec\n")


ani = FuncAnimation(f, asynchronous, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                    blit=False)
plt.tight_layout()
plt.show()
