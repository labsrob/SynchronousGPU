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
def eProcessRn(xbar, sbar, xucl, xlcl, xusl, xlsl, sucl, slcl):

    # -----(Use Historical limits procedure ---------------[]
    tMean1 = xbar
    xUCL1, xLCL1, xUSL1, xLSL1, sUCL1, sLCL1 = xucl, xlcl, xusl, xlsl, sucl, slcl

    tSDev1 = sbar
    PkA, Pp1 = pp.hisCap(tMean1, tSDev1, xLSL1, xUSL1)

    # Free up some memory spaces --------------------------[]
    return PkA, Pp1


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

    return round(PpRt, 3), Ppkt[-1]