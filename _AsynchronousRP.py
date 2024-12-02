#
# MODULE ASYNCHRONOUS Data Frame (moduleAsynchronousData.py)
# Magma Global Ltd., TechnipFMC
# Author: Robert B. Labs, PhD
# DNV Parameter - Roller Pressure
# -----------------------------------------------------

# import synchronous function to load data
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# ----------------------------------#
import SynchronousRPData as qrp      # call class function
import selSqlColumnsTFM as qq        # Post processing columns
import selPlcColumnsTFM as vq        # Synchronous RT columns
import rtP_Evaluator as tq
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation


def asynchronousRP(qType, fig, a1, a2, smp_Sz, stp_Sz, optm, uhl, tblID, minRP, maxRP, Xmax, sBar_minRP, sBar_maxRP, hMeanA, hDevA, hUSLa, hLSLa, hUCLa, hLCLa, db_freq):

    timei = time.time()                 # start timing the entire loop
    UsePLC_DBS = qType                  # Query Type

    # declare asynchronous variables -------------------------------------------------------[]
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

    if UsePLC_DBS == 1:
        import rpVarPLC as rp
        # Call synchronous data function ------------------------[]
        plcRP = qrp.syncRPdataPlc(smp_Sz, stp_Sz, db_freq)               # obtain list from data loading functions
        viz_cycle = 10

        columns = vq.validColsPLCData()                                 # Load defined valid columns for PLC Data
        df1 = pd.DataFrame(plcRP, columns=columns)                      # Include table data into python Dataframe
        RP = rp.loadProcesValues(df1)                                   # Join data values under dataframe

    else:
        import rpVarSQL as rp                                          # load SQL variables column names | rpVarSQL
        sqlRP = qrp.syncRPSql(None, smp_Sz, stp_Sz, optm, tblID, db_freq)    # obtain list from data loading functions

        viz_cycle = 150
        g1 = qq.validCols('RP')                                         # Construct Data Column selSqlColumnsTFM.py
        df1 = pd.DataFrame(sqlRP, columns=g1)                           # Import into python Dataframe
        RP = rp.loadProcesValues(df1)                                  # Join data values under dataframe
    print('\nSQL Content', df1.head(10))
    print("Memory Usage:", df1.info(verbose=False))                     # Check memory utilization

    # Declare Plots attributes ------------------------------------------------------------[]
    a1.grid(color="0.5", linestyle='-', linewidth=0.5)
    a2.grid(color="0.5", linestyle='-', linewidth=0.5)
    a1.legend(loc='upper left', title='XBar Plot')
    a2.legend(loc='upper right', title='SDev Plot')

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
    if optm:
        im10.set_ydata((RP[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
        im11.set_ydata((RP[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 2
        im12.set_ydata((RP[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 3
        im13.set_ydata((RP[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 1 ---------#
        mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(uhl, smp_Sz, 'RP')
        # ---------------------------------------#
        im14.set_ydata((RP[4]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
        im15.set_ydata((RP[5]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 2
        im16.set_ydata((RP[6]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 3
        im17.set_ydata((RP[7]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 2 ---------#
        mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(uhl, smp_Sz, 'RP')
        # ---------------------------------------#
        im18.set_ydata((RP[8]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
        im19.set_ydata((RP[9]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 2
        im20.set_ydata((RP[10]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 3
        im21.set_ydata((RP[11]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 3 ---------#
        mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(uhl, smp_Sz, 'RP')
        # ---------------------------------------#
        im22.set_ydata((RP[12]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
        im23.set_ydata((RP[13]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 2
        im24.set_ydata((RP[14]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 3
        im25.set_ydata((RP[15]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 4
        # ------ Evaluate Pp for Ring 4 ---------#
        mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(uhl, smp_Sz, 'RP')
        # ---------------------------------------#
        # S Plot Y-Axis data points for StdDev ----------------------------------------
        im26.set_ydata((RP[0]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im27.set_ydata((RP[1]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im28.set_ydata((RP[2]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im29.set_ydata((RP[3]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])

        im30.set_ydata((RP[4]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im31.set_ydata((RP[5]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im32.set_ydata((RP[6]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im33.set_ydata((RP[7]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])

        im34.set_ydata((RP[8]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im35.set_ydata((RP[9]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im36.set_ydata((RP[10]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im37.set_ydata((RP[11]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])

        im38.set_ydata((RP[12]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im39.set_ydata((RP[13]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im40.set_ydata((RP[14]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
        im41.set_ydata((RP[15]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
    else:
        # X Plot the mean of 20 data points as a single point---------- no of rows at a time
        im10.set_ydata((RP[0]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im11.set_ydata((RP[1]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im12.set_ydata((RP[2]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im13.set_ydata((RP[3]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        # ------ Evaluate Pp for Ring 4 ---------#
        mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(uhl, smp_Sz, 'RP')
        # ---------------------------------------#
        im14.set_ydata((RP[4]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im15.set_ydata((RP[5]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im16.set_ydata((RP[6]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im17.set_ydata((RP[7]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        # ------ Evaluate Pp for Ring 4 ---------#
        mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(uhl, smp_Sz, 'RP')
        # ---------------------------------------#
        im18.set_ydata((RP[8]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im19.set_ydata((RP[9]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im20.set_ydata((RP[10]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im21.set_ydata((RP[11]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        # ------ Evaluate Pp for Ring 4 ---------#
        mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(uhl, smp_Sz, 'RP')
        # ---------------------------------------#
        im22.set_ydata((RP[12]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im23.set_ydata((RP[13]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im24.set_ydata((RP[14]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        im25.set_ydata((RP[15]).rolling(window=smp_Sz, step=stp_Sz).mean()[0:db_freq])
        # ------ Evaluate Pp for Ring 4 ---------#
        mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(uhl, smp_Sz, 'RP')
        # ---------------------------------------#

        # S Plot Y-Axis data points for StdDev ------------------------------------------[]
        im26.set_ydata((RP[0]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im27.set_ydata((RP[1]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im28.set_ydata((RP[2]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im29.set_ydata((RP[3]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im30.set_ydata((RP[4]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im31.set_ydata((RP[5]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im32.set_ydata((RP[6]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im33.set_ydata((RP[7]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im34.set_ydata((RP[8]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im35.set_ydata((RP[9]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im36.set_ydata((RP[10]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im37.set_ydata((RP[11]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im38.set_ydata((RP[12]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im39.set_ydata((RP[13]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im40.set_ydata((RP[14]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
        im41.set_ydata((RP[15]).rolling(window=smp_Sz, step=stp_Sz).std()[0:db_freq])
    # Compute entire Process Capability -----------#
    if not uhl:
        mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLa, dLCLa, ppT, pkT, xline, sline = tq.tAutoPerf(smp_Sz, mnA, mnB,
                                                                                             mnC, mnD, sdA,
                                                                                             sdB, sdC, sdD)
    else:
        xline, sline = hMeanA, hDevA
        mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLa, dLCLa, ppT, pkT = tq.tManualPerf(mnA, mnB, mnC, mnD, sdA, sdB,
                                                                                  sdC, sdD, hUSLa, hLSLa, hUCLa,
                                                                                  hLCLa)
    # # Declare Plots attributes ------------------------------------------------------------[]
    # XBar Mean Plot
    a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
    a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')            # 3 Sigma span (Purple)
    a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')            # grey area
    a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
    # ---------------------- sBar_minRP, sBar_maxRP -------[]
    # Define Legend's Attributes  ----
    a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
    a2.axhspan(dLCLa, dUCLa, facecolor='#F9C0FD', edgecolor='#F9C0FD')          # 1 Sigma Span
    a2.axhspan(dUCLa, sBar_maxRP, facecolor='#CCCCFF', edgecolor='#CCCCFF')     # 1 Sigma above the Mean
    a2.axhspan(sBar_minRP, dLCLa, facecolor='#CCCCFF', edgecolor='#CCCCFF')

    # Setting up the parameters for moving windows Axes ---------------------------------[]
    if db_freq > Xmax:
        a1.set_xlim(db_freq - Xmax, db_freq)
        a2.set_xlim(db_freq - Xmax, db_freq)
    else:
        a1.set_xlim(0, Xmax)
        a2.set_xlim(0, Xmax)

    # Set trip line for individual time-series plot -----------------------------------[R1]
    import triggerModule as sigma
    sigma.trigViolations(a1, UsePLC_DBS, tblID, minRP, maxRP, xucT, xlcT, xusT, xlsT, mnT, sdT)

    timef = time.time()
    lapsedT = timef - timei
    print(f"\nProcess Interval: {lapsedT} sec\n")

    ani = FuncAnimation(fig, asynchronousRP, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                    blit=False)
    plt.tight_layout()
    plt.show()
