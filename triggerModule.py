#
#
# MODULE ASYNCHRONOUS Data Frame (moduleAsynchronousData.py)
# Magma Global Ltd., TechnipFMC
# Author: Robert B. Labs, PhD
# -----------------------------------------------------

import triggerWire as sx

# Set trip line for individual time-series plot -----------------------------------[R1]


def trigViolations(a1, md, procID, minYScale, maxYScale, xUCL, xLCL, xUSL, xLSL, pMean, pDev):
    window_y2min, window_y2max = minYScale, maxYScale       # limits for the process
    if md == 1:                                                 # using PLC query
        import realTimePLCupdate as pq
    else:
        import realTPostSQLupdate as pq                         # Using SQL Query

    ringValue = (procID[0], procID[1], procID[2], procID[3])    # check and avoid null values    
    if sum(ringValue) > 0:
        Trig1 = (procID[0]).mean()                              # Ring 1 Roller Pressure
        Trig2 = (procID[1]).mean()                              # raRF[1].mean()
        Trig3 = (procID[2]).mean()
        Trig4 = (procID[3]).mean()
        # Provide visualisation: Evaluate trig values with Sigma Limits --------[]
        fcT1 = sx.trippWire(Trig1, xUCL, xLCL, xUSL, xLSL)      # Evaluate using process mean/dev values
        fcT2 = sx.trippWire(Trig2, xUCL, xLCL, xUSL, xLSL)
        fcT3 = sx.trippWire(Trig3, xUCL, xLCL, xUSL, xLSL)
        fcT4 = sx.trippWire(Trig4, xUCL, xLCL, xUSL, xLSL)

        if fcT1 == '#F7F5AB' or fcT2 == '#F7F5AB' or fcT3 == '#F7F5AB' or fcT4 == '#F7F5AB':
            # Set the alert color to light Yellow -------[]
            a1.axhspan(xUSL, window_y2max, facecolor='#f7f302', edgecolor='#f7f302')   # Yellow trip
            a1.axhspan(window_y2min, xLSL, facecolor='#f7f302', edgecolor='#f7f302')   # Yellow trip

            # write sigma values into PLC data block if RT is enabled -----------[TRIGGER]
            U, L, X, D = round(xUCL, 2), round(xLCL, 2), round(pMean, 2), round(pDev, 2)
            pq.processR1_Sigma(U, L, X, D, round(Trig1, 2), round(Trig2, 2), round(Trig3, 2), round(Trig4, 2), str(procID))
            print('R1 Head1-4: 3Sigma', round(Trig1, 2), round(Trig2, 2), round(Trig3, 2), round(Trig4, 2))
            print('-' * 55)

        elif fcT1 == '#FE9CC9' or fcT2 == '#FE9CC9' or fcT3 == '#FE9CC9' or fcT4 == '#FE9CC9':
            # Set alert colors to light Brown -------[]
            a1.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')   # Red trip
            a1.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')   # Red trip

            # write sigma values into PLC data block if RT is enabled -----------[]
            U, L, X, D = round(xUSL,2), round(xLSL, 2), round(pMean, 2), round(pDev, 2)
            pq.processR1_Sigma(U, L, X, D, round(Trig1, 2), round(Trig2, 2), round(Trig3, 2), round(Trig4, 2), str(procID), md)
            print('R1 Head1-4: 6Sigma', round(Trig1, 2), round(Trig2, 2), round(Trig3, 2), round(Trig4, 2))
            print('-' * 55)
        else:
            a1.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')     # white
            a1.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')     # white

    ringValue = (procID[4], procID[5], procID[6], procID[7])  # check and avoid null values
    if sum(ringValue) > 0:
        Trig5 = (procID[4]).mean()      # Ring 1 Roller Pressure TODO: 4 TRIGS PER RING
        Trig6 = (procID[5]).mean()      # raRF[1].mean()
        Trig7 = (procID[6]).mean()
        Trig8 = (procID[7]).mean()
        # Provide visualisation: Evaluate trig values with Sigma Limits -----[]
        fcT5 = sx.trippWire(Trig5, xUCL, xLCL, xUSL, xLSL)
        fcT6 = sx.trippWire(Trig6, xUCL, xLCL, xUSL, xLSL)
        fcT7 = sx.trippWire(Trig7, xUCL, xLCL, xUSL, xLSL)
        fcT8 = sx.trippWire(Trig8, xUCL, xLCL, xUSL, xLSL)

        # Capture trigg values above control/set limits -------------------------[]
        if fcT5 == '#F7F5AB' or fcT6 == '#F7F5AB' or fcT7 == '#F7F5AB' or fcT8 == '#F7F5AB':
            # Set the alert color to light Yellow -------[]
            a1.axhspan(xUSL, window_y2max, facecolor='#f7f302', edgecolor='#f7f302')
            a1.axhspan(window_y2min, xLSL, facecolor='#f7f302', edgecolor='#f7f302')

            # write sigma values into PLC data block if RT is enabled -----------[]
            U, L, X, D = round(xUCL,2), round(xLCL,2), round(pMean,2), round(pDev,2)
            pq.processR2_Sigma(U, L, X, D, round(Trig5, 2), round(Trig6, 2), round(Trig7, 2), round(Trig8, 2), str(procID), md)
            print('R2 Head1-4: 3Sigma', round(Trig5, 2), round(Trig6, 2), round(Trig7, 2), round(Trig8, 2))
            print('-' * 55)

        elif fcT5 == '#FE9CC9' or fcT6 == '#FE9CC9' or fcT7 == '#FE9CC9' or fcT8 == '#FE9CC9':
            # Set the alert color to light Yellow -------[]
            a1.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')
            a1.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')

            # write sigma values into PLC data block if RT is enabled -----------[]
            U, L, X, D = round(xUSL,2), round(xLSL,2), round(pMean,2), round(pDev,2)
            pq.processR2_Sigma(U, L, X, D, round(Trig5, 2), round(Trig6, 2), round(Trig7, 2), round(Trig8, 2), str(procID), md)
            print('R2 Head1-4: 6Sigma', round(Trig5, 2), round(Trig6, 2), round(Trig7, 2), round(Trig8, 2))
            print('-' * 55)
        else:
            a1.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')     # white
            a1.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')     # white

    ringValue = (procID[8], procID[9], procID[10], procID[11])  # check and avoid null values
    if sum(ringValue) > 0:
        Trig9 = (procID[8]).mean()                            # Ring 1 Roller Pressure TODO: 4 TRIGS PER RING
        Trig10 = (procID[9]).mean()                           # raRF[1].mean()
        Trig11 = (procID[10]).mean()
        Trig12 = (procID[11]).mean()
        # Provide visualisation: Evaluate trig values with Sigma Limits -----[]
        fcT9 = sx.trippWire(Trig9, xUCL, xLCL, xUSL, xLSL)
        fcT10 = sx.trippWire(Trig10, xUCL, xLCL, xUSL, xLSL)
        fcT11 = sx.trippWire(Trig11, xUCL, xLCL, xUSL, xLSL)
        fcT12 = sx.trippWire(Trig12, xUCL, xLCL, xUSL, xLSL)

        # Capture trigg values above control/set limits ------------------------------------
        if fcT9 == '#F7F5AB' or fcT10 == '#F7F5AB' or fcT11 == '#F7F5AB' or fcT12 == '#F7F5AB':
            a1.axhspan(xUSL, window_y2max, facecolor='#f7f302', edgecolor='#f7f302')
            a1.axhspan(window_y2min, xLSL, facecolor='#f7f302', edgecolor='#f7f302')

            # write sigma values into PLC data block if RT is enabled -----------[]
            U, L, X, D = round(xUCL, 2), round(xLCL, 2), round(pMean,2), round(pDev,2)
            pq.processR3_Sigma(U, L, X, D, round(Trig9, 2), round(Trig10, 2), round(Trig11, 2), round(Trig12, 2), str(procID), md)
            print('R3 Head1-4: 3Sigma', round(Trig9, 2), round(Trig10, 2), round(Trig11, 2), round(Trig12, 2))
            print('-' * 55)
        elif fcT9 == '#FE9CC9' or fcT10 == '#FE9CC9' or fcT11 == '#FE9CC9' or fcT12 == '#FE9CC9':
            a1.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')
            a1.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')

            # write sigma values into PLC data block if RT is enabled -----------[]
            U, L, X, D = round(xUSL, 2), round(xLSL, 2), round(pMean,2), round(pDev,2)
            pq.processR3_Sigma(U, L, X, D, round(Trig9, 2), round(Trig10, 2), round(Trig11, 2), round(Trig12, 2), str(procID), md)
            print('R3 Head1-4: 6Sigma', round(Trig9, 2), round(Trig10, 2), round(Trig11, 2), round(Trig12, 2))
            print('-' * 55)
        else:
            a1.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')     # white
            a1.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')     # white

    ringValue = (procID[12], procID[13], procID[14], procID[15])  # check and avoid null values
    if sum(ringValue) > 0:
        Trig13 = (procID[12]).mean()      # Ring 1 Roller Pressure TODO: 4 TRIGS PER RING
        Trig14 = (procID[13]).mean()      # raRF[1].mean()
        Trig15 = (procID[14]).mean()
        Trig16 = (procID[15]).mean()
        # Provide visualisation: Evaluate trig values with Sigma Limits -----[]
        fcT13 = sx.trippWire(Trig13, xUCL, xLCL, xUSL, xLSL)
        fcT14 = sx.trippWire(Trig14, xUCL, xLCL, xUSL, xLSL)
        fcT15 = sx.trippWire(Trig15, xUCL, xLCL, xUSL, xLSL)
        fcT16 = sx.trippWire(Trig16, xUCL, xLCL, xUSL, xLSL)

        # Capture trigg values above control/set limits ------------------------------------
        if fcT13 == '#F7F5AB' or fcT14 == '#F7F5AB' or fcT15 == '#F7F5AB' or fcT16 == '#F7F5AB':
            # ax2.set_facecolor('#f5f378')
            a1.axhspan(xUSL, window_y2max, facecolor='#f7f302', edgecolor='#f7f302')  # Yellow alert
            a1.axhspan(window_y2min, xLSL, facecolor='#f5f302', edgecolor='#f7f302')  # Yellow alert

            # write rings' Sigma values into PLC data block if RT is enabled -----------[]
            U, L, X, D = round(xUCL, 2), round(xLCL, 2), round(pMean,2), round(pDev,2)
            pq.processR4_Sigma(U, L, X, D, round(Trig13, 2), round(Trig14, 2), round(Trig15, 2), round(Trig16, 2), str(procID), md)
            print('Ring1-4 Trip Values: 3Sigma', round(Trig13, 2), round(Trig14, 2), round(Trig15, 2), round(Trig16, 2))
            print('-' * 55)
        elif fcT13 == '#FE9CC9' or fcT14 == '#FE9CC9' or fcT15 == '#FE9CC9' or fcT16 == '#FE9CC9':
            # ax2.set_facecolor('#f09605')
            a1.axhspan(xUSL, window_y2max, facecolor='#f00505', edgecolor='#f00505')     # Red alert
            a1.axhspan(window_y2min, xLSL, facecolor='#f00505', edgecolor='#f00505')     # Red alert

            # write sigma values into PLC data block if RT is enabled -----------[]
            U, L, X, D = round(xUSL, 2), round(xLSL, 2), round(pMean,2), round(pDev,2)
            pq.processR4_Sigma(U, L, X, D, round(Trig13, 2), round(Trig14, 2), round(Trig15, 2), round(Trig16, 2), str(procID), md)
            print('Ring1-4 Trip Values: 6Sigma', round(Trig13, 2), round(Trig14, 2), round(Trig15, 2), round(Trig16, 2))
            print('-' * 55)
        else:
            a1.axhspan(xUSL, window_y2max, facecolor='#FFFFFF', edgecolor='#FFFFFF')     # white
            a1.axhspan(window_y2min, xLSL, facecolor='#FFFFFF', edgecolor='#FFFFFF')     # white
