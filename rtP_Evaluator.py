#
# MODULE ASYNCHRONOUS Data Frame (moduleAsynchronousData.py)
# Magma Global Ltd., TechnipFMC
# Author: Robert B. Labs, PhD
# -----------------------------------------------------
#
import numpy as np
import ProcessCapPerf as pp

# ------------ Initialise arrays ------------------------------#
autoGpMeanA, autoUSLA, autoLSLA, autoUCLA, autoLCLA, autosUCLA, autosLCLA, rfA,  = [], [], [], [], [], [], [], []
hUCLa, hLCLa, hUSLa, hLSLa, dUCLa, dLCLa = [], [], [], [], [], []
# -------------------------------------------
autoGpMeanB, autoUSLB, autoLSLB, autoUCLB, autoLCLB, autosUCLB, autosLCLB, rfB,  = [], [], [], [], [], [], [], []
hUCLb, hLCLb, hUSLb, hLSLb, dUCLb, dLCLb = [], [], [], [], [], []
# -------------------------------------------
autoGpMeanC, autoUSLC, autoLSLC, autoUCLC, autoLCLC, autosUCLC, autosLCLC, rfC,  = [], [], [], [], [], [], [], []
hUCLc, hLCLc, hUSLc, hLSLc, dUCLc, dLCLc = [], [], [], [], [], []
# -------------------------------------------
autoGpMeanD, autoUSLD, autoLSLD, autoUCLD, autoLCLD, autosUCLD, autosLCLD, rfD,  = [], [], [], [], [], [], [], []
hUCLd, hLCLd, hUSLd, hLSLd, dUCLd, dLCLd = [], [], [], [], [], []
# ---------------------------------------------------------------#
autoGpMeanT, autoGpDevT = [], []
TSdevT, sClineT, autoUSLT, autoLSLT, autoUCLT, autoLCLT, autosUCLT, autosLCLT, Ppkt = [], [], [], [], [], [], [], [], []

# ---- Ring 1 --------------#
def eProcessR1(uhl, smp_Sz, procID):
    if not uhl:
        if len(autoGpMeanA) == smp_Sz:
            
            # filter out potential null and zero values from subgroup mean deductions ----
            if procID[0].any() or procID[1].any() or procID[2].any() or procID[3].any():
                pass
            else:
                # print('\n R2 - CHECK VALUES:', R2RF[0], R2RF[1], R2RF[2], R2RF[3])
                tMean1 = ((procID[0]).mean() + (procID[1]).mean() + (procID[2]).mean() + (procID[3]).mean()) / 4
                tSDev1 = ((procID[0]).std() + (procID[1]).std() + (procID[2]).std() + (procID[3]).std()) / 4
    
            if len(autoUSLA) != 0:
                sUCL1, sLCL1, xUSL1, xLSL1, xUCL1, xLCL1 = autosUCLA[0], autosLCLA[0], autoUSLA[0], \
                    autoLSLA[0], autoUCLA[0], autoLCLA[0]
                PpkL1, PpkU1, Pp1 = pp.hisCap(tMean1, tSDev1, xLSL1, xUSL1)
            else:
                xUSL1, xLSL1, xUCL1, xLCL1, sUCL1, sLCL1, PpkL1, PpkU1, Pp1 = pp.processCap(tMean1, tSDev1, smp_Sz)
        else:
            tMean1 = ((procID[0]).mean() + (procID[1]).mean() + (procID[2]).mean() + (procID[3]).mean()) / 4
            tSDev1 = ((procID[0]).std() + (procID[1]).std() + (procID[2]).std() + (procID[3]).std()) / 4
            xUSL1, xLSL1, xUCL1, xLCL1, sUCL1, sLCL1, PpkL1, PpkU1, Pp1 = pp.processCap(tMean1, tSDev1, smp_Sz)
    else:
        tMean1 = ((procID[0]).mean() + (procID[1]).mean() + (procID[2]).mean() + (procID[3]).mean()) / 4
        xUCL1, xLCL1, xUSL1, xLSL1, sUCL1, sLCL1 = hUCLa, hLCLa, hUSLa, hLSLa, dUCLa, dLCLa
    
        tSDev1 = ((procID[0]).std() + (procID[1]).std() + (procID[2]).std() + (procID[3]).std()) / 4
        PpkL1, PpkU1, Pp1 = pp.hisCap(tMean1, tSDev1, xLSL1, xUSL1)
    
    # Compute process capability for Ring 2 Data ----------------------------------------[]
    pkA = min(PpkL1, PpkU1)
    rfA.append(round(pkA, 4))
    # Free up some memory spaces -----
    if len(rfA) > 1:
        del (rfA[:1])
    print('Head5-8 (RF) Dev:', round(tSDev1, 4))
    print('USL/LSL (RF):', xUSL1, xLSL1)
    print('UCL/LCL (RF):', xUCL1, xLCL1)
    print('Ring1-Head1-4 (RF) Pp/Ppk:', round(Pp1, 4), '\t', rfA[-1])

    return round(tMean1, 4), round(tSDev1, 4), xUSL1, xLSL1, xUCL1, xLCL1, round(Pp1, 4), rfA[-1]


# ---- Ring 2 --------------#
def eProcessR2(uhl, smp_Sz, procID):
    if not uhl:
        if len(autoGpMeanB) == smp_Sz:

            # filter out potential null and zero values from subgroup mean deductions ----
            if procID[4].any() or procID[5].any() or procID[6].any() or procID[7].any():
                pass
            else:
                # print('\n R2 - CHECK VALUES:', R2RF[0], R2RF[1], R2RF[2], R2RF[3])
                tMean2 = ((procID[4]).mean() + (procID[5]).mean() + (procID[6]).mean() + (procID[7]).mean()) / 4
                tSDev2 = ((procID[4]).std() + (procID[5]).std() + (procID[6]).std() + (procID[7]).std()) / 4

            if len(autoUSLB) != 0:
                sUCL2, sLCL2, xUSL2, xLSL2, xUCL2, xLCL2 = autosUCLB[0], autosLCLB[0], autoUSLB[0], \
                    autoLSLB[0], autoUCLB[0], autoLCLB[0]
                PpkL2, PpkU2, Pp2 = pp.hisCap(tMean2, tSDev2, xLSL2, xUSL2)
            else:
                xUSL2, xLSL2, xUCL2, xLCL2, sUCL2, sLCL2, PpkL2, PpkU2, Pp2 = pp.processCap(tMean2, tSDev2, smp_Sz)
        else:
            tMean2 = ((procID[4]).mean() + (procID[5]).mean() + (procID[6]).mean() + (procID[7]).mean()) / 4
            tSDev2 = ((procID[4]).std() + (procID[5]).std() + (procID[6]).std() + (procID[7]).std()) / 4
            xUSL2, xLSL2, xUCL2, xLCL2, sUCL2, sLCL2, PpkL2, PpkU2, Pp2 = pp.processCap(tMean2, tSDev2, smp_Sz)
    else:
        tMean2 = ((procID[0]).mean() + (procID[1]).mean() + (procID[2]).mean() + (procID[3]).mean()) / 4
        xUCL2, xLCL2, xUSL2, xLSL2, sUCL2, sLCL2 = hUCLb, hLCLb, hUSLb, hLSLb, dUCLb, dLCLb

        tSDev2 = ((procID[0]).std() + (procID[1]).std() + (procID[2]).std() + (procID[3]).std()) / 4
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

    return round(tMean2, 4), round(tSDev2, 4), xUSL2, xLSL2, xUCL2, xLCL2, round(Pp2, 4), rfB[-1]


# ---- Ring 3 --------------#
def eProcessR3(uhl, smp_Sz, procID):
    if not uhl:
        if len(autoGpMeanC) == smp_Sz:

            # filter out potential null and zero values from subgroup mean deductions ----
            if procID[8].any() or procID[9].any() or procID[10].any() or procID[11].any():
                pass
            else:
                # print('\n R2 - CHECK VALUES:', R2RF[0], R2RF[1], R2RF[2], R2RF[3])
                tMean3 = ((procID[8]).mean() + (procID[9]).mean() + (procID[10]).mean() + (procID[11]).mean()) / 4
                tSDev3 = ((procID[8]).std() + (procID[9]).std() + (procID[10]).std() + (procID[11]).std()) / 4

            if len(autoUSLC) != 0:
                sUCL3, sLCL3, xUSL3, xLSL3, xUCL3, xLCL3 = autosUCLC[0], autosLCLC[0], autoUSLC[0], \
                    autoLSLC[0], autoUCLC[0], autoLCLC[0]
                PpkL3, PpkU3, Pp3 = pp.hisCap(tMean3, tSDev3, xLSL3, xUSL3)
            else:
                xUSL3, xLSL3, xUCL3, xLCL3, sUCL3, sLCL3, PpkL3, PpkU3, Pp3 = pp.processCap(tMean3, tSDev3, smp_Sz)
        else:
            tMean3 = ((procID[8]).mean() + (procID[9]).mean() + (procID[10]).mean() + (procID[11]).mean()) / 4
            tSDev3 = ((procID[8]).std() + (procID[9]).std() + (procID[10]).std() + (procID[11]).std()) / 4
            xUSL3, xLSL3, xUCL3, xLCL3, sUCL3, sLCL3, PpkL3, PpkU3, Pp3 = pp.processCap(tMean3, tSDev3, smp_Sz)
    else:
        tMean3 = ((procID[8]).mean() + (procID[9]).mean() + (procID[10]).mean() + (procID[11]).mean()) / 4
        xUCL3, xLCL3, xUSL3, xLSL3, sUCL3, sLCL3 = hUCLc, hLCLc, hUSLc, hLSLc, dUCLc, dLCLc

        tSDev3 = ((procID[8]).std() + (procID[9]).std() + (procID[10]).std() + (procID[11]).std()) / 4
        PpkL3, PpkU3, Pp3 = pp.hisCap(tMean3, tSDev3, xLSL3, xUSL3)

    # Compute process capability for Ring 2 Data ----------------------------------------[]
    pkC = min(PpkL3, PpkU3)
    rfC.append(round(pkC, 4))
    # Free up some memory spaces -----
    if len(rfC) > 1:
        del (rfB[:1])
    print('Head5-8 (RF) Dev:', round(tSDev3, 4))
    print('USL/LSL (RF):', xUSL3, xLSL3)
    print('UCL/LCL (RF):', xUCL3, xLCL3)
    print('Ring3-Head9-12 (RF) Pp/Ppk:', round(Pp3, 4), '\t', rfC[-1])

    return round(tMean3, 4), round(tSDev3, 4), xUSL3, xLSL3, xUCL3, xLCL3, round(Pp3, 4), rfC[-1]


# ---- Ring 4 --------------#
def eProcessR4(uhl, smp_Sz, procID):
    if not uhl:
        if len(autoGpMeanD) == smp_Sz:

            # filter out potential null and zero values from subgroup mean deductions ----
            if procID[12].any() or procID[13].any() or procID[14].any() or procID[15].any():
                pass
            else:
                # print('\n R2 - CHECK VALUES:', R2RF[0], R2RF[1], R2RF[2], R2RF[3])
                tMean4 = ((procID[12]).mean() + (procID[13]).mean() + (procID[14]).mean() + (procID[15]).mean()) / 4
                tSDev4 = ((procID[12]).std() + (procID[13]).std() + (procID[14]).std() + (procID[15]).std()) / 4

            if len(autoUSLD) != 0:
                sUCL4, sLCL4, xUSL4, xLSL4, xUCL4, xLCL4 = autosUCLD[0], autosLCLD[0], autoUSLD[0], \
                    autoLSLD[0], autoUCLD[0], autoLCLD[0]
                PpkL4, PpkU4, Pp4 = pp.hisCap(tMean4, tSDev4, xLSL4, xUSL4)
            else:
                xUSL4, xLSL4, xUCL4, xLCL4, sUCL4, sLCL4, PpkL4, PpkU4, Pp4 = pp.processCap(tMean4, tSDev4, smp_Sz)
        else:
            tMean4 = ((procID[12]).mean() + (procID[13]).mean() + (procID[14]).mean() + (procID[15]).mean()) / 4
            tSDev4 = ((procID[12]).std() + (procID[13]).std() + (procID[14]).std() + (procID[15]).std()) / 4
            xUSL4, xLSL4, xUCL4, xLCL4, sUCL4, sLCL4, PpkL4, PpkU4, Pp4 = pp.processCap(tMean4, tSDev4, smp_Sz)
    else:
        tMean4 = ((procID[12]).mean() + (procID[13]).mean() + (procID[14]).mean() + (procID[15]).mean()) / 4
        xUCL4, xLCL4, xUSL4, xLSL4, sUCL4, sLCL4 = hUCLd, hLCLd, hUSLd, hLSLd, dUCLd, dLCLd

        tSDev4 = ((procID[12]).std() + (procID[13]).std() + (procID[14]).std() + (procID[15]).std()) / 4
        PpkL4, PpkU4, Pp4 = pp.hisCap(tMean4, tSDev4, xLSL4, xUSL4)

    # Compute process capability for Ring 2 Data ----------------------------------------[]
    pkD = min(PpkL4, PpkU4)
    rfD.append(round(pkD, 4))
    # Free up some memory spaces -----
    if len(rfD) > 1:
        del (rfD[:1])
    print('Head5-8 (RF) Dev:', round(tSDev4, 4))
    print('USL/LSL (RF):', xUSL4, xLSL4)
    print('UCL/LCL (RF):', xUCL4, xLCL4)
    print('Ring4-Head12-16 (RF) Pp/Ppk:', round(Pp4, 4), '\t', rfD[-1])

    return round(tMean4, 4), round(tSDev4, 4), xUSL4, xLSL4, xUCL4, xLCL4, round(Pp4, 4), rfD[-1]


#  Combined Process Performance  ------------------------------------------------------------[]
def tAutoPerf(smp_Sz, tMean1, tMean2, tMean3, tMean4, tSDev1, tSDev2, tSDev3, tSDev4):
    # ----- Compute Mean Line Using RT Date--------------------------------------------------[]
    # Sample process group mean for 1st subgroup instance ---[]
    if len(autoGpMeanT) <= smp_Sz:
        if tMean1 != 0 or tMean2 != 0 or tMean3 != 0 or tMean4 != 0:
            TMeanT = np.array([tMean1, tMean2, tMean3, tMean4])                 # Ring data
            TMeanT = (TMeanT[np.nonzero(TMeanT)]).mean()                        # ignore defective head [.mean()]
            TSdevT = np.array([tSDev1, tSDev2, tSDev3, tSDev4])
            TSdevT = (TSdevT[np.nonzero(TSdevT)]).mean()                        # total heads in the process
            # Sample and Compute the subgroup Process Mean and subgroup Deviation
        else:
            TMeanT = 0.0
            TSdevT = 0.68 * 2           # i.e 1 sigma DOF

        sMeant = 0
        xMeant = 0                      # Turn off center line until limits lock
        autoGpMeanT.append(TMeanT)      # record zero value
        autoGpDevT.append(TSdevT)       # I sigma deviation
        xUSLt, xLSLt, xUCLt, xLCLt, sUCLt, sLCLt, PpkLt, PpkUt, PpRt = pp.processCap(TMeanT, TSdevT, smp_Sz)

    else:
        TMeanT = sum(autoGpMeanT) / len(autoGpMeanT)        # compute & keep subgroup Center line
        TSdevT = sum(autoGpDevT) / len(autoGpDevT)          # Compute average dev for subgroup Center line
        sMeant = 0
        xMeant = 0                                          # Turn off center line until limits lock
        if len(autoUSLT) < 2:
            xUSLt, xLSLt, xUCLt, xLCLt, sUCLt, sLCLt, PpkLt, PpkUt, PpRt = pp.processCap(TMeanT, TSdevT, smp_Sz)
            sClineT.append(TSdevT)
            autoUSLT.append(xUSLt)
            autoLSLT.append(xLSLt)
            autoUCLT.append(xUCLt)
            autoLCLT.append(xLCLt)
            autosUCLT.append(sUCLt)
            autosLCLT.append(sLCLt)
        else:
            # Test static arrays for valid values --------------------[]
            xUSLt = autoUSLT[0]
            xLSLt = autoLSLT[0]
            xUCLt = autoUCLT[0]
            xLCLt = autoLCLT[0]
            sUCLt = autosUCLT[0]
            sLCLt = autosLCLT[0]
            sMeant = sClineT[0]                                     # sPlot centre line
            xMeant = TMeanT                                         # xPlot centre line until limits lock
            TSdevT = np.array([tSDev1, tSDev1, tSDev1, tSDev1])     # Allow subgroup DOF on StdDev
            TSdevT = (TSdevT[np.nonzero(TSdevT)]).mean()            # Current Process's deviation
            PpkLt, PpkUt, PpRt = pp.hisCap(TMeanT, TSdevT, xLSLt, xUSLt)

    # Compute process capability for Process Data ------------------------[]
    procT = min(PpkLt, PpkUt)           # Average Ppk per available rings combinations
    Ppkt.append(round(procT, 4))        # copy 2sig. result into a dynamic array
    # Free up some memory spaces
    if len(Ppkt) > 1:
        del (Ppkt[:1])
    print('-' * 55)
    print('Process (RF) Mean/SDev:', round(TMeanT, 4), round(TSdevT, 4))
    print('Process (RF) UCL/LCL:', xUCLt, xLCLt)
    print('Process (RF) USL/LSL:', xUSLt, xLSLt)
    print('Process (RF) Pp/Ppk:', round(PpRt, 4), '\t', Ppkt[-1])  # 4 min to max 16 heads on 4 rings
    print('-' * 55)

    return round(TMeanT, 4), round(TSdevT, 4), xUSLt, xLSLt, xUCLt, xLCLt, sUCLt, sLCLt, round(PpRt, 4), Ppkt[-1], xMeant, sMeant


def tManualPerf(tMean1, tMean2, tMean3, tMean4, tSDev1, tSDev2, tSDev3, tSDev4, hUSLx, hLSLx, hUCLx, hLCLx):

    # ---- Compute Process Mean --------
    proM1 = (tMean1, tMean2, tMean3, tMean4)

    if sum(proM1) != 0:
        TMeanT = np.array([tMean1, tMean2, tMean3, tMean4])     # Allow subgroup DOF on StdDev
        TMeanT = (TMeanT[np.nonzero(TMeanT)]).mean()            # Current Process's deviation
    else:
        pass
    TSdevT = np.array([tSDev1, tSDev2, tSDev3, tSDev4])         # Allow subgroup DOF on StdDev
    TSdevT = (TSdevT[np.nonzero(TSdevT)]).mean()                # Current Process's deviation

    xUSLt, xLSLt, xUCLt, xLCLt  = hUSLx, hLSLx, hUCLx, hLCLx
    PpkLt, PpkUt, PpRt = pp.hisCap(TMeanT, TSdevT, xUSLt, xLSLt)

    # Compute process capability for Process Data ------------------------[]
    procT = min(PpkLt, PpkUt)  # Average Ppk per available rings combinations
    Ppkt.append(round(procT, 4))  # copy 2sig. result into a dynamic array
    # Free up some memory spaces -----
    if len(Ppkt) > 1:
        del (Ppkt[:1])
    print('-' * 55)
    print('Process (RF) Mean/SDev:', round(TMeanT, 4), round(TSdevT, 4))
    print('Process (RF) UCL/LCL:', xUCLt, xLCLt)
    print('Process (RF) USL/LSL:', xUSLt, xLSLt)
    print('Process (RF) Pp/Ppk:', round(PpRt, 4), '\t', Ppkt[-1])  # 4 min to max 16 heads on 4 rings
    print('-' * 55)

    return round(TMeanT, 4), round(TSdevT, 4), xUSLt, xLSLt, xUCLt, xLCLt, round(PpRt, 4), Ppkt[-1]