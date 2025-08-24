#
from tkinter import *
import tkinter as tk
from tkinter.simpledialog import Dialog
import qParamsHL_MGM as mx
pa1, pa2 = 0, 0

# Initialise example FIXME -- Work order number must be obtained from SQL or PLC
WON = "275044"


def save_mMetrics():
    print("\nCalling Function is:", pTy, WON)
    mx.saveMetricsQP(pTy, WON, sSize, gType, enHL, enAL, enMG)          # Set limits for Quality parameters
    s_data.config(state="disabled")                                     # disable safe button on entry
    e_data.config(state="normal")                                       # enable edit button on entry
    return


def editPHL():
    if pTy == 'RF':
        s_data.config(state="normal")                   # enable safe button on entry
        sRegime.config(state="normal")                  # enable data entry
        mx.qpHL_RF(popmodal, sSize, xUCL, xLCL, sUCL, sLCL, xUCL1, xLCL1,  sUCL1, sLCL1, WON)
        e_data.config(state="disabled")                 # prevent accidental entry clearance
    elif pTy == 'LP':
        s_data.config(state="normal")                   # enable safe button on entry
        sRegime.config(state="normal")                  # enable data entry
        mx.qpHL_LP(popmodal, sSize, xUCL, xLCL, sUCL, sLCL, xUCL1, xLCL1,  sUCL1, sLCL1, WON)
        e_data.config(state="disabled")                 # prevent accidental entry clearance
    elif pTy == 'TT':                                   # Tape Temp
        print('\nSelecting TT')
        s_data.config(state="normal")
        sRegime.config(state="normal")                  # enable data entry
        mx.qpHL_TT(popmodal, sSize, xUCL, xLCL, sUCL, sLCL, xUCL1, xLCL1,  sUCL1, sLCL1, xUCL2, xLCL2,  sUCL2, sLCL2, xUCL3, xLCL3,  sUCL3, sLCL3, xUCL4, xLCL4, sUCL4, sLCL4, WON)
        e_data.config(state="disabled")
    elif pTy == 'ST':                                   # Substrate Temp
        s_data.config(state="normal")
        sRegime.config(state="normal")                  # enable data entry
        mx.qpHL_ST(popmodal, sSize, xUCL, xLCL, sUCL, sLCL, xUCL1, xLCL1,  sUCL1, sLCL1, xUCL2, xLCL2,  sUCL2, sLCL2, xUCL3, xLCL3,  sUCL3, sLCL3, xUCL4, xLCL4, sUCL4, sLCL4, WON)
        e_data.config(state="disabled")
    elif pTy == 'TP':                                   # Tape Placement Error
        s_data.config(state="normal")
        sRegime.config(state="normal")                  # enable data entry
        mx.qpHL_TP(popmodal, sSize, xUCL, xLCL, sUCL, sLCL, WON)
        e_data.config(state="disabled")
    elif pTy == 'TG':                                   # Tape Ga
        s_data.config(state="normal")
        sRegime.config(state="normal")                  # enable data entry
        mx.qpHL_TG(popmodal, sSize, xUCL, xLCL, sUCL, sLCL, WON)
        e_data.config(state="disabled")
    elif pTy == 'LA':                                   # Tape Placement Error
        s_data.config(state="normal")
        sRegime.config(state="normal")                  # enable data entry
        mx.qpHL_LA(popmodal, sSize, xUCL, xLCL, sUCL, sLCL, WON)
        e_data.config(state="disabled")
    else:
        pass


def paramsEntry(modal, gSize, gMode, defHL, defAL, defMG, pLP, pLA, pTP, pRF, pTT, pST, pTG):
    global pTy, xUCL, xUCL1, xUCL2, xUCL3, xUCL4, xLCL, xLCL1, xLCL2, xLCL3, xLCL4, \
           xMean, xMean1, xMean2, xMean3, xMean4, sMean, sMean1, sMean2, sMean3, sMean4,\
           xUSL, xUSL1, xUSL2, xUSL3, xUSL4, xLSL, xLSL1, xLSL2, xLSL3, xLSL4, \
           sUCL, sUCL1, sUCL2, sUCL3, sUCL4, sLCL, sLCL1, sLCL2, sLCL3, sLCL4,\
           pa1, pb1, pc1, pd1, pe1, pf1, pg1, ph1, pi1, pj1, pa2, pb2, pc2, pd2, pe2, pf2, pg2, ph2, pi2, pj2, \
           pa3, pb3, pc3, pd3, pe3, pf3, pg3, ph3, pi3, pj3, pa4, pb4, pc4, pd4, pe4, pf4, pg4, ph4, pi4, pj4, \
           pf, pg, ph, pi, pf1, pg1, ph1, pi1, sSize, popmodal, s_data, e_data, gType, enHL, enAL, enMG, sel_SS, \
           sRegime, sReg

    # defHL = DNV' Historical Limits | defAL = Shewhart Automatic Limits | Auth = Automatic Fail Over
    # Define and initialise essential popup variables -------[RP  2 entries for hist limits]------------- [Roller Force]
    Taperf, TLyrf, xclrf, sclrf = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLrf, xLCLrf, sUCLrf, sLCLrf = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLrf, xLSLrf = StringVar(modal), StringVar(modal)
    # -----------------------
    Taperf1, TLyrf1, xclrf1, sclrf1 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLrf1, xLCLrf1, sUCLrf1, sLCLrf1 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLrf1, xLSLrf1 = StringVar(modal), StringVar(modal)
    # ------------------------
    Taperf2, TLyrf2, xclrf2, sclrf2 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLrf2, xLCLrf2, sUCLrf2, sLCLrf2 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLrf2, xLSLrf2 = StringVar(modal), StringVar(modal)
    # ------------------------
    Taperf3, TLyrf3, xclrf3, sclrf3 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLrf3, xLCLrf3, sUCLrf3, sLCLrf3 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLrf3, xLSLrf3 = StringVar(modal), StringVar(modal)
    # -----------------------
    Taperf4, TLyrf4, xclrf4, sclrf4 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLrf4, xLCLrf4, sUCLrf4, sLCLrf4 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLrf4, xLSLrf4 = StringVar(modal), StringVar(modal)

    # -------------------------------------------------------[TT 5 entries for hist limits] ---------------- [Tape Temp]
    Tapett, TLytt, xcltt, scltt = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLtt, xLCLtt, sUCLtt, sLCLtt = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLtt, xLSLtt = StringVar(modal), StringVar(modal)
    # -----------------------
    Tapett1, TLytt1, xcltt1, scltt1 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLtt1, xLCLtt1, sUCLtt1, sLCLtt1 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLtt1, xLSLtt1 = StringVar(modal), StringVar(modal)
    # ------------------------
    Tapett2, TLytt2, xcltt2, scltt2 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLtt2, xLCLtt2, sUCLtt2, sLCLtt2 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLtt2, xLSLtt2 = StringVar(modal), StringVar(modal)
    # ------------------------
    Tapett3, TLytt3, xcltt3, scltt3 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLtt3, xLCLtt3, sUCLtt3, sLCLtt3 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLtt3, xLSLtt3 = StringVar(modal), StringVar(modal)
    # -----------------------
    Tapett4, TLytt4, xcltt4, scltt4 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLtt4, xLCLtt4, sUCLtt4, sLCLtt4 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLtt4, xLSLtt4 = StringVar(modal), StringVar(modal)

    # -------------------------------------------------------[ST 5 entries for hist limits] ------------[Substrate Temp]
    Tapest, TLyst, xclst, sclst = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLst, xLCLst, sUCLst, sLCLst = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLst, xLSLst = StringVar(modal), StringVar(modal)
    # -----------------------
    Tapest1, TLyst1, xclst1, sclst1 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLst1, xLCLst1, sUCLst1, sLCLst1 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLst1, xLSLst1 = StringVar(modal), StringVar(modal)
    # ------------------------
    Tapest2, TLyst2, xclst2, sclst2 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLst2, xLCLst2, sUCLst2, sLCLst2 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLst2, xLSLst2 = StringVar(modal), StringVar(modal)
    # ------------------------
    Tapest3, TLyst3, xclst3, sclst3 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLst3, xLCLst3, sUCLst3, sLCLst3 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLst3, xLSLst3 = StringVar(modal), StringVar(modal)
    # -----------------------
    Tapest4, TLyst4, xclst4, sclst4 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLst4, xLCLst4, sUCLst4, sLCLst4 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLst4, xLSLst4 = StringVar(modal), StringVar(modal)

    # -------------------------------------------------------[TP] ------------------------------- [Tape Placement Error]
    Tapetp, TLytp, xcltp, scltp = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLtp, xLCLtp, sUCLtp, sLCLtp = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLtp, xLSLtp = StringVar(modal), StringVar(modal)
    # -----------------------
    Tapetp1, TLytp1, xcltp1, scltp1 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLtp1, xLCLtp1, sUCLtp1, sLCLtp1 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLtp1, xLSLtp1 = StringVar(modal), StringVar(modal)
    # ------------------------
    Tapetp2, TLytp2, xcltp2, scltp2 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLtp2, xLCLtp2, sUCLtp2, sLCLtp2 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLtp2, xLSLtp2 = StringVar(modal), StringVar(modal)
    # ------------------------
    Tapetp3, TLytp3, xcltp3, scltp3 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLtp3, xLCLtp3, sUCLtp3, sLCLtp3 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLtp3, xLSLtp3 = StringVar(modal), StringVar(modal)
    # -----------------------
    Tapetp4, TLytp4, xcltp4, scltp4 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLtp4, xLCLtp4, sUCLtp4, sLCLtp4 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLtp4, xLSLtp4 = StringVar(modal), StringVar(modal)

    # -------------------------------------------------------[LP] ---------------------------------------- [Laser Power]
    Tapelp, TLylp, xcllp, scllp = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLlp, xLCLlp, sUCLlp, sLCLlp = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLlp, xLSLlp = StringVar(modal), StringVar(modal)
    # -----------------------
    Tapelp1, TLylp1, xcllp1, scllp1 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLlp1, xLCLlp1, sUCLlp1, sLCLlp1 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLlp1, xLSLlp1 = StringVar(modal), StringVar(modal)
    # ------------------------
    Tapelp2, TLylp2, xcllp2, scllp2 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLlp2, xLCLlp2, sUCLlp2, sLCLlp2 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLlp2, xLSLlp2 = StringVar(modal), StringVar(modal)
    # ------------------------
    Tapelp3, TLylp3, xcllp3, scllp3 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLlp3, xLCLlp3, sUCLlp3, sLCLlp3 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLlp3, xLSLlp3 = StringVar(modal), StringVar(modal)
    # -----------------------
    Tapelp4, TLylp4, xcllp4, scllp4 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLlp4, xLCLlp4, sUCLlp4, sLCLlp4 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLlp4, xLSLlp4 = StringVar(modal), StringVar(modal)

    # -------------------------------------------------------[LA] ---------------------------------------- [Laser Angle]
    Tapela, TLyla, xclla, sclla = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLla, xLCLla, sUCLla, sLCLla = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLla, xLSLla = StringVar(modal), StringVar(modal)
    # -----------------------
    Tapela1, TLyla1, xclla1, sclla1 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLla1, xLCLla1, sUCLla1, sLCLla1 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLla1, xLSLla1 = StringVar(modal), StringVar(modal)
    # ------------------------
    Tapela2, TLyla2, xclla2, sclla2 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLla2, xLCLla2, sUCLla2, sLCLla2 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLla2, xLSLla2 = StringVar(modal), StringVar(modal)
    # ------------------------
    Tapela3, TLyla3, xclla3, sclla3 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLla3, xLCLla3, sUCLla3, sLCLla3 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLla3, xLSLla3 = StringVar(modal), StringVar(modal)
    # -----------------------
    Tapela4, TLyla4, xclla4, sclla4 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLla4, xLCLla4, sUCLla4, sLCLla4 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLla4, xLSLla4 = StringVar(modal), StringVar(modal)

    # -------------------------------------------------------[TG] ------------------------------------------- [Tape Gap]
    Tapetg, TLytg, xcltg, scltg = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLtg, xLCLtg, sUCLtg, sLCLtg = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLtg, xLSLtg = StringVar(modal), StringVar(modal)
    # -----------------------
    Tapetg1, TLytg1, xcltg1, scltg1 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLtg1, xLCLtg1, sUCLtg1, sLCLtg1 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLtg1, xLSLtg1 = StringVar(modal), StringVar(modal)
    # ------------------------
    Tapetg2, TLytg2, xcltg2, scltg2 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLtg2, xLCLtg2, sUCLtg2, sLCLtg2 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLtg2, xLSLtg2 = StringVar(modal), StringVar(modal)
    # ------------------------
    Tapetg3, TLytg3, xcltg3, scltg3 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLtg3, xLCLtg3, sUCLtg3, sLCLtg3 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLtg3, xLSLtg3 = StringVar(modal), StringVar(modal)
    # -----------------------
    Tapetg4, TLytg4, xcltg4, scltg4 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLtg4, xLCLtg4, sUCLtg4, sLCLtg4 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLtg4, xLSLtg4, sReg = StringVar(modal), StringVar(modal), StringVar(modal)

    sSize = gSize           # copy into new var
    gType = gMode           # Samples Subgroup Type
    enHL = defHL            # DNV Historical Limits
    enAL = defAL            # Shewhart Automatic Limits
    enMG = defMG            # Magma Commercial Pipe Historical Limits
    popmodal = modal        # copy into new var

    if pRF.get():
        print("\nRoller Force Parameter Checked...")
        pTy = 'RF'
        pState = 'normal'
        pbutton = 'disabled'
        tape0 = Taperf
        xUCL = xUCLrf
        xLCL = xLCLrf
        sUCL = sUCLrf
        sLCL = sLCLrf
        xMean = xclrf
        sMean = sclrf
        xUSL = xUSLrf
        xLSL = xLSLrf
        tLyr = TLyrf
        # TODO Set selection to readonly then allow next entry of other params value
        # ---------- Line 1
        tape1 = Taperf1
        xUCL1 = xUCLrf1
        xLCL1 = xLCLrf1
        sUCL1 = sUCLrf1
        sLCL1 = sLCLrf1
        xMean1 = xclrf1
        sMean1 = sclrf1
        xUSL1 = xUSLrf1
        xLSL1 = xLSLrf1
        tLyr1 = TLyrf1
        # ----------- Line 2
        tape2 = Taperf2
        xUCL2 = xUCLrf2
        xLCL2 = xLCLrf2
        sUCL2 = sUCLrf2
        sLCL2 = sLCLrf2
        xMean2 = xclrf2
        sMean2 = sclrf2
        xUSL2 = xUSLrf2
        xLSL2 = xLSLrf2
        tLyr2 = TLyrf2
        # ------------ Line 3
        tape3 = Taperf3
        xUCL3 = xUCLrf3
        xLCL3 = xLCLrf3
        sUCL3 = sUCLrf3
        sLCL3 = sLCLrf3
        xMean3 = xclrf3
        sMean3 = sclrf3
        xUSL3 = xUSLrf3
        xLSL3 = xLSLrf3
        tLyr3 = TLyrf3
        # ------------ Line 4
        tape4 = Taperf4
        xUCL4 = xUCLrf4
        xLCL4 = xLCLrf4
        sUCL4 = sUCLrf4
        sLCL4 = sLCLrf4
        xMean4 = xclrf4
        sMean4 = sclrf4
        xUSL4 = xUSLrf4
        xLSL4 = xLSLrf4
        tLyr4 = TLyrf4
        # ------------- Line 5
        # TODO -- Load last used parameters ----------------[]
        gen10, gen20, gen25, gen26, gen30, gen40, gen50, tupa, tupb, c, d, e = mx.decryptpProcessLim(WON, pTy)
        # ---------------------[Require to load DNV HL Page]
        # Set static Values -----------------------------[]
        if tupa:
            histA = tupa.split(',')  # split into list elements
            tape0.set('22mm')
            xUCL.set(float(histA[2].strip("' ")))
            xLCL.set(float(histA[3].strip("' ")))
            sUCL.set(float(histA[4].strip("' ")))
            sLCL.set(float(histA[5].strip("' ")))
            tLyr.set('1+')
        else:
            tape0.set('22mm')
            xUCL.set('0')
            xLCL.set('0')
            sUCL.set('0')
            sLCL.set('0')
            tLyr.set('1+')
        # -------------------------
        if tupb:
            histB = tupb.split(',')  # split into list elements
            tape1.set('18mm')
            xUCL1.set(float(histB[2].strip("' ")))
            xLCL1.set(float(histB[3].strip("' ")))
            sUCL1.set(float(histB[4].strip("' ")))
            sLCL1.set(float(histB[5].strip("' ")))
            tLyr1.set('41+')
            sReg.set(gen25)
        else:
            tape1.set('18mm')
            xUCL1.set('0')
            xLCL1.set('0')
            sUCL1.set('0')
            sLCL1.set('0')
            tLyr1.set('41+')
            sReg.set(3)

    elif pLP.get():
        print("\nLaser Power Parameter Checked...")
        pTy = 'LP'
        pState = 'normal'
        pbutton = 'disabled'
        tape0 = Tapelp
        xUCL = xUCLlp
        xLCL = xLCLlp
        sUCL = sUCLlp
        sLCL = sLCLlp
        xMean = xcllp
        sMean = scllp
        xUSL = xUSLlp
        xLSL = xLSLlp
        tLyr = TLylp
        # TODO Set selection to readonly then allow next entry of other params value
        # ---------- Line 1
        tape1 = Tapelp1
        xUCL1 = xUCLlp1
        xLCL1 = xLCLlp1
        sUCL1 = sUCLlp1
        sLCL1 = sLCLlp1
        xMean1 = xcllp1
        sMean1 = scllp1
        xUSL1 = xUSLlp1
        xLSL1 = xLSLlp1
        tLyr1 = TLylp1
        # ----------- Line 2
        tape2 = Tapelp2
        xUCL2 = xUCLlp2
        xLCL2 = xLCLlp2
        sUCL2 = sUCLlp2
        sLCL2 = sLCLlp2
        xMean2 = xcllp2
        sMean2 = scllp2
        xUSL2 = xUSLlp2
        xLSL2 = xLSLlp2
        tLyr2 = TLylp2
        # ------------ Line 3
        tape3 = Tapelp3
        xUCL3 = xUCLlp3
        xLCL3 = xLCLlp3
        sUCL3 = sUCLlp3
        sLCL3 = sLCLlp3
        xMean3 = xcllp3
        sMean3 = scllp3
        xUSL3 = xUSLlp3
        xLSL3 = xLSLlp3
        tLyr3 = TLylp3
        # ------------ Line 4
        tape4 = Tapelp4
        xUCL4 = xUCLlp4
        xLCL4 = xLCLlp4
        sUCL4 = sUCLlp4
        sLCL4 = sLCLlp4
        xMean4 = xcllp4
        sMean4 = scllp4
        xUSL4 = xUSLlp4
        xLSL4 = xLSLlp4
        tLyr4 = TLylp4
        # ------------- Line 5
        # TODO -- Load last used parameters ----------------[]
        gen10, gen20, gen25, gen26, gen30, gen40, gen50, tupa, tupb, c, d, e = mx.decryptpProcessLim(WON, pTy)
        # ---------------------[Require to load DNV HL Page]
        # Set static Values -----------------------------[]
        if tupa:
            histA = tupa.split(',')  # split into list elements
            tape0.set('22mm')
            xUCL.set(float(histA[2].strip("' ")))
            xLCL.set(float(histA[3].strip("' ")))
            sUCL.set(float(histA[4].strip("' ")))
            sLCL.set(float(histA[5].strip("' ")))
            tLyr.set('1+')
        else:
            tape0.set('22mm')
            xUCL.set('0')
            xLCL.set('0')
            sUCL.set('0')
            sLCL.set('0')
            tLyr.set('1+')
        # -------------------------
        if tupb:
            histB = tupb.split(',')  # split into list elements
            tape1.set('18mm')
            xUCL1.set(float(histB[2].strip("' ")))
            xLCL1.set(float(histB[3].strip("' ")))
            sUCL1.set(float(histB[4].strip("' ")))
            sLCL1.set(float(histB[5].strip("' ")))
            tLyr1.set('41+')
            sReg.set(gen25)
        else:
            tape1.set('18mm')
            xUCL1.set('0')
            xLCL1.set('0')
            sUCL1.set('0')
            sLCL1.set('0')
            tLyr1.set('41+')
            sReg.set(3)
    # -------------------------------------------------
    elif pLA.get():
        print("\nLaser Angle Parameter Checked...")
        pTy = 'LA'
        pState = 'normal'
        pbutton = 'disabled'
        tape0 = Tapela
        xUCL = xUCLla
        xLCL = xLCLla
        sUCL = sUCLla
        sLCL = sLCLla
        xMean = xclla
        sMean = sclla
        xUSL = xUSLla
        xLSL = xLSLla
        tLyr = TLyla
        # ----------
        tape1 = Tapela1
        xUCL1 = xUCLla1
        xLCL1 = xLCLla1
        sUCL1 = sUCLla1
        sLCL1 = sLCLla1
        xMean1 = xclla1
        sMean1 = sclla1
        xUSL1 = xUSLla1
        xLSL1 = xLSLla1
        tLyr1 = TLyla1
        # -----------
        tape2 = Tapela2
        xUCL2 = xUCLla2
        xLCL2 = xLCLla2
        sUCL2 = sUCLla2
        sLCL2 = sLCLla2
        xMean2 = xclla2
        sMean2 = sclla2
        xUSL2 = xUSLla2
        xLSL2 = xLSLla2
        tLyr2 = TLyla2
        # ------------
        tape3 = Tapela3
        xUCL3 = xUCLla3
        xLCL3 = xLCLla3
        sUCL3 = sUCLla3
        sLCL3 = sLCLla3
        xMean3 = xclla3
        sMean3 = sclla3
        xUSL3 = xUSLla3
        xLSL3 = xLSLla3
        tLyr3 = TLyla3
        # ------------
        tape4 = Tapela4
        xUCL4 = xUCLla4
        xLCL4 = xLCLla4
        sUCL4 = sUCLla4
        sLCL4 = sLCLla4
        xMean4 = xclla4
        sMean4 = sclla4
        xUSL4 = xUSLla4
        xLSL4 = xLSLla4
        tLyr4 = TLyla4
        # Set static Values ---[l1, l2, l3]
        # TODO -- Load last used parameters ----------------[]
        gen10, gen20, gen25, gen26, gen30, gen40, gen50, tupa, tupb, c, d, e = mx.decryptpProcessLim(WON, pTy)
        # ---------------------[Require to load DNV HL Page]
        print('\nTP Sample space Value:', gen25)
        # Set static Values -----------------------------[]
        if tupa:
            histA = tupa.split(',')  # split into list elements
            tape0.set('**mm')
            xUCL.set(float(histA[2].strip("' ")))
            xLCL.set(float(histA[3].strip("' ")))
            sUCL.set(float(histA[4].strip("' ")))
            sLCL.set(float(histA[5].strip("' ")))
            tLyr.set('1+')
            sReg.set(gen25)
        else:
            tape0.set('**mm')
            xUCL.set('0')
            xLCL.set('0')
            sUCL.set('0')
            sLCL.set('0')
            tLyr.set('1+')
            sReg.set(3)

    elif pTT.get():
        print("\nTape Temp Parameter Checked...")
        pTy = 'TT'
        pState = 'normal'
        pbutton = 'disabled'
        tape0 = Tapett
        xUCL = xUCLtt
        xLCL = xLCLtt
        sUCL = sUCLtt
        sLCL = sLCLtt
        xMean = xcltt
        sMean = scltt
        xUSL = xUSLtt
        xLSL = xLSLtt
        tLyr = TLytt
        # ----------
        tape1 = Tapett1
        xUCL1 = xUCLtt1
        xLCL1 = xLCLtt1
        sUCL1 = sUCLtt1
        sLCL1 = sLCLtt1
        xMean1 = xcltt1
        sMean1 = scltt1
        xUSL1 = xUSLtt1
        xLSL1 = xLSLtt1
        tLyr1 = TLytt1
        # -----------
        tape2 = Tapett2
        xUCL2 = xUCLtt2
        xLCL2 = xLCLtt2
        sUCL2 = sUCLtt2
        sLCL2 = sLCLtt2
        xMean2 = xcltt2
        sMean2 = scltt2
        xUSL2 = xUSLtt2
        xLSL2 = xLSLtt2
        tLyr2 = TLytt2
        # ------------
        tape3 = Tapett3
        xUCL3 = xUCLtt3
        xLCL3 = xLCLtt3
        sUCL3 = sUCLtt3
        sLCL3 = sLCLtt3
        xMean3 = xcltt3
        sMean3 = scltt3
        xUSL3 = xUSLtt3
        xLSL3 = xLSLtt3
        tLyr3 = TLytt3
        # ------------
        tape4 = Tapett4
        xUCL4 = xUCLtt4
        xLCL4 = xLCLtt4
        sUCL4 = sUCLtt4
        sLCL4 = sLCLtt4
        xMean4 = xcltt4
        sMean4 = scltt4
        xUSL4 = xUSLtt4
        xLSL4 = xLSLtt4
        tLyr4 = TLytt4
        # Set static Values ---[l1, l2, l3]
        # TODO -- Load last used parameters ----------------[]
        gen10, gen20, gen25, gen26, gen30, gen40, gen50, tupa, tupb, tupc, tupd, tupe = mx.decryptpProcessLim(WON, pTy)
        # ---------------------[Require to load DNV HL Page]
        # Set static Values -----------------------------[]
        if tupa:
            histA = tupa.split(',')  # split into list elements
            tape0.set('22mm')
            xUCL.set(float(histA[2].strip("' ")))
            xLCL.set(float(histA[3].strip("' ")))
            sUCL.set(float(histA[4].strip("' ")))
            sLCL.set(float(histA[5].strip("' ")))
            tLyr.set('1')
        else:
            tape0.set('22mm')
            xUCL.set('0')
            xLCL.set('0')
            sUCL.set('0')
            sLCL.set('0')
            tLyr.set('1')
        # -------------------------
        if tupb:
            histB = tupb.split(',')  # split into list elements
            tape1.set('22mm')
            xUCL1.set(float(histB[2].strip("' ")))
            xLCL1.set(float(histB[3].strip("' ")))
            sUCL1.set(float(histB[4].strip("' ")))
            sLCL1.set(float(histB[5].strip("' ")))
            tLyr1.set('2')
        else:
            tape1.set('22mm')
            xUCL1.set('0')
            xLCL1.set('0')
            sUCL1.set('0')
            sLCL1.set('0')
            tLyr1.set('2')

        # -------------------------
        if tupc:
            histC = tupc.split(',')  # split into list elements
            tape2.set('22mm')
            xUCL2.set(float(histC[2].strip("' ")))
            xLCL2.set(float(histC[3].strip("' ")))
            sUCL2.set(float(histC[4].strip("' ")))
            sLCL2.set(float(histC[5].strip("' ")))
            tLyr2.set('3-40')
        else:
            tape2.set('22mm')
            xUCL2.set('0')
            xLCL2.set('0')
            sUCL2.set('0')
            sLCL2.set('0')
            tLyr2.set('3-40')
        # -------------------------
        if tupd:
            histD = tupd.split(',')  # split into list elements
            tape3.set('18mm')
            xUCL3.set(float(histD[2].strip("' ")))
            xLCL3.set(float(histD[3].strip("' ")))
            sUCL3.set(float(histD[4].strip("' ")))
            sLCL3.set(float(histD[5].strip("' ")))
            tLyr3.set('41')
        else:
            tape3.set('18mm')
            xUCL3.set('0')
            xLCL3.set('0')
            sUCL3.set('0')
            sLCL3.set('0')
            tLyr3.set('41')

        # -------------------------
        if tupe:
            histE = tupe.split(',')  # split into list elements
            tape4.set('18mm')
            xUCL4.set(float(histE[2].strip("' ")))
            xLCL4.set(float(histE[3].strip("' ")))
            sUCL4.set(float(histE[4].strip("' ")))
            sLCL4.set(float(histE[5].strip("' ")))
            tLyr4.set('42+')
            sReg.set(gen25)

        else:
            tape4.set('18mm')
            xUCL4.set('0')
            xLCL4.set('0')
            sUCL4.set('0')
            sLCL4.set('0')
            tLyr4.set('42+')
            sReg.set(3)

    elif pST.get():
        print("\nSubstrate Temp Parameter Checked...")
        pTy = 'ST'
        pState = 'normal'
        pbutton = 'disabled'
        tape0 = Tapest
        xUCL = xUCLst
        xLCL = xLCLst
        sUCL = sUCLst
        sLCL = sLCLst
        xMean = xclst
        sMean = sclst
        xUSL = xUSLst
        xLSL = xLSLst
        tLyr = TLyst
        # ----------
        tape1 = Tapest1
        xUCL1 = xUCLst1
        xLCL1 = xLCLst1
        sUCL1 = sUCLst1
        sLCL1 = sLCLst1
        xMean1 = xclst1
        sMean1 = sclst1
        xUSL1 = xUSLst1
        xLSL1 = xLSLst1
        tLyr1 = TLyst1
        # -----------
        tape2 = Tapest2
        xUCL2 = xUCLst2
        xLCL2 = xLCLst2
        sUCL2 = sUCLst2
        sLCL2 = sLCLst2
        xMean2 = xclst2
        sMean2 = sclst2
        xUSL2 = xUSLst2
        xLSL2 = xLSLst2
        tLyr2 = TLyst2
        # ------------
        tape3 = Tapest3
        xUCL3 = xUCLst3
        xLCL3 = xLCLst3
        sUCL3 = sUCLst3
        sLCL3 = sLCLst3
        xMean3 = xclst3
        sMean3 = sclst3
        xUSL3 = xUSLst3
        xLSL3 = xLSLst3
        tLyr3 = TLyst3
        # ------------
        tape4 = Tapest4
        xUCL4 = xUCLst4
        xLCL4 = xLCLst4
        sUCL4 = sUCLst4
        sLCL4 = sLCLst4
        xMean4 = xclst4
        sMean4 = sclst4
        xUSL4 = xUSLst4
        xLSL4 = xLSLst4
        tLyr4 = TLyst4
        # Set static Values --[l1, l2, l3]
        # TODO -- Load last used parameters ----------------[]
        gen10, gen20, gen25, gen26, gen30, gen40, gen50, tupa, tupb, tupc, tupd, tupe = mx.decryptpProcessLim(WON, pTy)
        # ---------------------[Require to load DNV HL Page]
        # Set static Values -----------------------------[]
        if tupa:
            histA = tupa.split(',')  # split into list elements
            tape0.set('22mm')
            xUCL.set(float(histA[2].strip("' ")))
            xLCL.set(float(histA[3].strip("' ")))
            sUCL.set(float(histA[4].strip("' ")))
            sLCL.set(float(histA[5].strip("' ")))
            tLyr.set('1')
        else:
            tape0.set('22mm')
            xUCL.set('0')
            xLCL.set('0')
            sUCL.set('0')
            sLCL.set('0')
            tLyr.set('1')
        # -------------------------
        if tupb:
            histB = tupb.split(',')  # split into list elements
            tape1.set('22mm')
            xUCL1.set(float(histB[2].strip("' ")))
            xLCL1.set(float(histB[3].strip("' ")))
            sUCL1.set(float(histB[4].strip("' ")))
            sLCL1.set(float(histB[5].strip("' ")))
            tLyr1.set('2')
        else:
            tape1.set('22mm')
            xUCL1.set('0')
            xLCL1.set('0')
            sUCL1.set('0')
            sLCL1.set('0')
            tLyr1.set('2')

        # -------------------------
        if tupc:
            histC = tupc.split(',')  # split into list elements
            tape2.set('22mm')
            xUCL2.set(float(histC[2].strip("' ")))
            xLCL2.set(float(histC[3].strip("' ")))
            sUCL2.set(float(histC[4].strip("' ")))
            sLCL2.set(float(histC[5].strip("' ")))
            tLyr2.set('3-40')
        else:
            tape2.set('22mm')
            xUCL2.set('0')
            xLCL2.set('0')
            sUCL2.set('0')
            sLCL2.set('0')
            tLyr2.set('3-40')
        # -------------------------
        if tupd:
            histD = tupd.split(',')  # split into list elements
            tape3.set('18mm')
            xUCL3.set(float(histD[2].strip("' ")))
            xLCL3.set(float(histD[3].strip("' ")))
            sUCL3.set(float(histD[4].strip("' ")))
            sLCL3.set(float(histD[5].strip("' ")))
            tLyr3.set('41')
        else:
            tape3.set('18mm')
            xUCL3.set('0')
            xLCL3.set('0')
            sUCL3.set('0')
            sLCL3.set('0')
            tLyr3.set('41')

        # -------------------------
        if tupe:
            histE = tupe.split(',')  # split into list elements
            tape4.set('18mm')
            xUCL4.set(float(histE[2].strip("' ")))
            xLCL4.set(float(histE[3].strip("' ")))
            sUCL4.set(float(histE[4].strip("' ")))
            sLCL4.set(float(histE[5].strip("' ")))
            tLyr4.set('42+')
            sReg.set(gen25)
        else:
            tape4.set('18mm')
            xUCL4.set('0')
            xLCL4.set('0')
            sUCL4.set('0')
            sLCL4.set('0')
            tLyr4.set('42+')
            sReg.set(3)

    elif pTP.get():
        print("\nKeyance Tape Placement Error Checked...")
        pTy = 'TP'
        pState = 'normal'
        pbutton = 'disabled'
        tape0 = Tapetp
        xUCL = xUCLtp
        xLCL = xLCLtp
        sUCL = sUCLtp
        sLCL = sLCLtp
        xMean = xcltp
        sMean = scltp
        xUSL = xUSLtp
        xLSL = xLSLtp
        tLyr = TLytp
        # ----------
        tape1 = Tapetp1
        xUCL1 = xUCLtp1
        xLCL1 = xLCLtp1
        sUCL1 = sUCLtp1
        sLCL1 = sLCLtp1
        xMean1 = xcltp1
        sMean1 = scltp1
        xUSL1 = xUSLtp1
        xLSL1 = xLSLtp1
        tLyr1 = TLytp1
        # -----------
        tape2 = Tapetp2
        xUCL2 = xUCLtp2
        xLCL2 = xLCLtp2
        sUCL2 = sUCLtp2
        sLCL2 = sLCLtp2
        xMean2 = xcltp2
        sMean2 = scltp2
        xUSL2 = xUSLtp2
        xLSL2 = xLSLtp2
        tLyr2 = TLytp2
        # ------------
        tape3 = Tapetp3
        xUCL3 = xUCLtp3
        xLCL3 = xLCLtp3
        sUCL3 = sUCLtp3
        sLCL3 = sLCLtp3
        xMean3 = xcltp3
        sMean3 = scltp3
        xUSL3 = xUSLtp3
        xLSL3 = xLSLtp3
        tLyr3 = TLytp3
        # ------------
        tape4 = Tapetp4
        xUCL4 = xUCLtp4
        xLCL4 = xLCLtp4
        sUCL4 = sUCLtp4
        sLCL4 = sLCLtp4
        xMean4 = xcltp4
        sMean4 = scltp4
        xUSL4 = xUSLtp4
        xLSL4 = xLSLtp4
        tLyr4 = TLytp4
        # Set static Values ---[l1, l2, l3]
        # TODO -- Load last used parameters ----------------[]
        gen10, gen20, gen25, gen26, gen30, gen40, gen50, tupa, tupb, c, d, e = mx.decryptpProcessLim(WON, pTy)
        # ---------------------[Require to load DNV HL Page]
        print('\nTP Sample space Value:', gen25)
        # Set static Values -----------------------------[]
        if tupa:
            histA = tupa.split(',')  # split into list elements
            tape0.set('**mm')
            xUCL.set(float(histA[2].strip("' ")))
            xLCL.set(float(histA[3].strip("' ")))
            sUCL.set(float(histA[4].strip("' ")))
            sLCL.set(float(histA[5].strip("' ")))
            tLyr.set('1+')
            sReg.set(gen25)
        else:
            tape0.set('**mm')
            xUCL.set('0')
            xLCL.set('0')
            sUCL.set('0')
            sLCL.set('0')
            tLyr.set('1+')
            sReg.set(3)

    elif pTG.get():
        print("\nTape Gap Parameter Checked...")
        pTy = 'TG'
        pState = 'normal'
        pbutton = 'disabled'    # on entry state

        tape0 = Tapetg
        xUCL = xUCLtg
        xLCL = xLCLtg
        sUCL = sUCLtg
        sLCL = sLCLtg
        xMean = xcltg
        sMean = scltg
        xUSL = xUSLtg
        xLSL = xLSLtg
        tLyr = TLytg
        # ----------
        tape1 = Tapetg1
        xUCL1 = xUCLtg1
        xLCL1 = xLCLtg1
        sUCL1 = sUCLtg1
        sLCL1 = sLCLtg1
        xMean1 = xcltg1
        sMean1 = scltg1
        xUSL1 = xUSLtg1
        xLSL1 = xLSLtg1
        tLyr1 = TLytg1
        # -----------
        tape2 = Tapetg2
        xUCL2 = xUCLtg2
        xLCL2 = xLCLtg2
        sUCL2 = sUCLtg2
        sLCL2 = sLCLtg2
        xMean2 = xcltg2
        sMean2 = scltg2
        xUSL2 = xUSLtg2
        xLSL2 = xLSLtg2
        tLyr2 = TLytg2
        # ------------
        tape3 = Tapetg3
        xUCL3 = xUCLtg3
        xLCL3 = xLCLtg3
        sUCL3 = sUCLtg3
        sLCL3 = sLCLtg3
        xMean3 = xcltg3
        sMean3 = scltg3
        xUSL3 = xUSLtg3
        xLSL3 = xLSLtg3
        tLyr3 = TLytg3
        # ------------
        tape4 = Tapetg4
        xUCL4 = xUCLtg4
        xLCL4 = xLCLtg4
        sUCL4 = sUCLtg4
        sLCL4 = sLCLtg4
        xMean4 = xcltg4
        sMean4 = scltg4
        xUSL4 = xUSLtg4
        xLSL4 = xLSLtg4
        tLyr4 = TLytg4

        # Set static Values ---[l1, l2, l3]
        # TODO -- Load last used parameters ----------------[]
        gen10, gen20, gen25, gen26, gen30, gen40, gen50, tupa, tupb, c, d, e = mx.decryptpProcessLim(WON, pTy)
        # ---------------------[Require to load DNV HL Page]
        print('\nTP Sample space Value:', gen25)
        # Set static Values -----------------------------[]
        if tupa:
            histA = tupa.split(',')  # split into list elements
            tape0.set('**mm')
            xUCL.set(float(histA[2].strip("' ")))
            xLCL.set(float(histA[3].strip("' ")))
            sUCL.set(float(histA[4].strip("' ")))
            sLCL.set(float(histA[5].strip("' ")))
            tLyr.set('1+')
            sReg.set(gen25)
        else:
            tape0.set('**mm')
            xUCL.set('0')
            xLCL.set('0')
            sUCL.set('0')
            sLCL.set('0')
            tLyr.set('1+')
            sReg.set(3)         # 3 seconds sampling cycle
    else:
        pass
    # # TODO --------------------------------- Insert dynamic calculations for Mean, SD & USL []

    # hd.calculationF(xUCLa, xLCLa, xUCLb, xLCLb, gSize1, pf, pf1, pg, pg1, ph, ph1, pi, pi1,)
    # # call calculation functions ---- []

    # --------------- Line 1 (Lookup Rows) -------------------------------[]
    pa = Entry(modal, width=8, textvariable=tape0, state=pState)
    pa.place(x=10, y=80)
    pb = Entry(modal, width=8, textvariable=xUCL, state=pState)
    pb.place(x=70, y=80)
    pc = Entry(modal, width=8, textvariable=xLCL, state=pState)
    pc.place(x=130, y=80)
    pd = Entry(modal, width=8, textvariable=sUCL, state=pState)             # Upper Control Limit
    pd.place(x=190, y=80)
    pe = Entry(modal, width=8, textvariable=sLCL, state=pState)             # Lower control limit
    pe.place(x=250, y=80)
    # ----------------------------------------------------------------------#
    pf = Entry(modal, width=8, state="readonly", textvariable=xMean)        # xMean Centre line
    pf.place(x=375, y=80)
    pg = Entry(modal, width=8, state="readonly", textvariable=sMean)        # sMean Centre line
    pg.place(x=435, y=80)
    ph = Entry(modal, width=8,  state="readonly", textvariable=xUSL)         # Upper Set Limit
    ph.place(x=495, y=80)
    pi = Entry(modal, width=8, state="readonly", textvariable=xLSL)         # Lower Set Limit
    pi.place(x=555, y=80)
    # ----------------------------------------------------------------------#
    pj = Entry(modal, width=8, textvariable=tLyr, state=pState)
    pj.place(x=675, y=80)
    pk = Entry(modal, width=8, state="readonly", textvariable=sReg)

    # ----------------- set entry field to read only ---------[]
    readonlyA = [pa, pb, pc, pd, pe]
    for txtA in readonlyA:
        txtA.config(state='readonly')
    # --------------------------------------------------------[]
    if pa1 and pTG.get() or pa1 and pTP.get() or pa1 and pLA.get():
        # Blank out irrelevant rows & its transient values in the Lookup Table
        canvasBlank = [pa1, pb1, pc1, pd1, pe1, pf1, pg1, ph1, pi1, pj1,
                       pa2, pb2, pc2, pd2, pe2, pf2, pg2, ph2, pi2, pj2,
                       pa3, pb3, pc3, pd3, pe3, pf3, pg3, ph3, pi3, pj3,
                       pa4, pb4, pc4, pd4, pe4, pf4, pg4, ph4, pi4, pj4]

        for line in canvasBlank:
            line.config(state="normal")
            line.delete(0, 'end')
            line.config(state="disabled")
            # pa.config(state='readonly')
    # # --------------------------------------------------------[]

    if not pTP.get() and not pTG.get() and not pLA.get():
        # --------------- Line 2
        pa1 = Entry(modal, width=8, textvariable=tape1, state=pState)
        pa1.place(x=10, y=102)
        pb1 = Entry(modal, width=8, textvariable=xUCL1, state=pState)
        pb1.place(x=70, y=102)
        pc1 = Entry(modal, width=8, textvariable=xLCL1, state=pState)
        pc1.place(x=130, y=102)
        pd1 = Entry(modal, width=8, textvariable=sUCL1, state=pState)           # Upper Control Limit
        pd1.place(x=190, y=102)
        pe1 = Entry(modal, width=8, textvariable=sLCL1, state=pState)           # Lower control limit
        pe1.place(x=250, y=102)
        # ------------------------------------------------------------[]
        pf1 = Entry(modal, width=8, textvariable=xMean1, state="readonly")      # xMean Centre line
        pf1.place(x=375, y=102)
        pg1 = Entry(modal, width=8, textvariable=sMean1, state="readonly")      # sMean Centre line
        pg1.place(x=435, y=102)
        ph1 = Entry(modal, width=8, textvariable=xUSL1, state="readonly")       # Upper Set Limit
        ph1.place(x=495, y=102)
        pi1 = Entry(modal, width=8, textvariable=xLSL1, state="readonly")       # Lower Set Limit
        pi1.place(x=555, y=102)
        pj1 = Entry(modal, width=8, textvariable=tLyr1, state=pState)
        pj1.place(x=675, y=102)
        # ----------------- set entry field to read only ---------[]
        readonlyB = [pa1, pb1, pc1, pd1, pe1]
        for txtB in readonlyB:
            txtB.config(state='readonly')
        # --------------------------------------------------------[]
        if pRF.get() and pa2:
            # Blank out irrelevant rows & its transient values in the Lookup Table
            canvasBlank = [pa2, pb2, pc2, pd2, pe2, pf2, pg2, ph2, pi2, pj2,
                           pa3, pb3, pc3, pd3, pe3, pf3, pg3, ph3, pi3, pj3,
                           pa4, pb4, pc4, pd4, pe4, pf4, pg4, ph4, pi4, pj4]
            for line in canvasBlank:
                line.config(state="normal")
                line.delete(0, 'end')
                line. config(state="disabled")
            # perform derived calculations ----[]

    if not pRF.get() and not pTP.get() and not pTG.get() and not pLA.get():
        # ----------------Line 3
        pa2 = Entry(modal, width=8, textvariable=tape2, state=pState)
        pa2.place(x=10, y=124)
        pb2 = Entry(modal, width=8, textvariable=xUCL2, state=pState)
        pb2.place(x=70, y=124)
        pc2 = Entry(modal, width=8, textvariable=xLCL2, state=pState)
        pc2.place(x=130, y=124)
        pd2 = Entry(modal, width=8, textvariable=sUCL2, state=pState)                # Upper Control Limit
        pd2.place(x=190, y=124)
        pe2 = Entry(modal, width=8, textvariable=sLCL2, state=pState)               # Lower control limit
        pe2.place(x=250, y=124)
        pf2 = Entry(modal, width=8, textvariable=xMean2, state="readonly")          # xMean Centre line
        pf2.place(x=375, y=124)
        pg2 = Entry(modal, width=8, textvariable=sMean2, state="readonly")          # sMean Centre line
        pg2.place(x=435, y=124)
        ph2 = Entry(modal, width=8, textvariable=xUSL2, state="readonly")           # Upper Set Limit
        ph2.place(x=495, y=124)
        pi2 = Entry(modal, width=8, textvariable=xLSL2, state="readonly")           # Lower Set Limit
        pi2.place(x=555, y=124)
        pj2 = Entry(modal, width=8, textvariable=tLyr2, state=pState)
        pj2.place(x=675, y=124)
        # ----------------- set entry field to read only ---------[]
        readonlyC = [pa2, pb2, pc2, pd2, pe2]
        for txtC in readonlyC:
            txtC.config(state='readonly')
        # --------------------------------------------------------[]
        # # ---------------- Line 4
        pa3 = Entry(modal, width=8, textvariable=tape3, state=pState)
        pa3.place(x=10, y=146)
        pb3 = Entry(modal, width=8, textvariable=xUCL3, state=pState)
        pb3.place(x=70, y=146)
        pc3 = Entry(modal, width=8, textvariable=xLCL3, state=pState)
        pc3.place(x=130, y=146)
        pd3 = Entry(modal, width=8, textvariable=sUCL3, state=pState)           # Upper Control Limit
        pd3.place(x=190, y=146)
        pe3 = Entry(modal, width=8, textvariable=sLCL3, state=pState)           # Lower control limit
        pe3.place(x=250, y=146)
        pf3 = Entry(modal, width=8, textvariable=xMean3, state="readonly")      # xMean Centre line
        pf3.place(x=375, y=146)
        pg3 = Entry(modal, width=8, textvariable=sMean3, state="readonly")      # sMean Centre line
        pg3.place(x=435, y=146)
        ph3 = Entry(modal, width=8, textvariable=xUSL3, state="readonly")       # Upper Set Limit
        ph3.place(x=495, y=146)
        pi3 = Entry(modal, width=8, textvariable=xLSL3, state="readonly")       # Lower Set Limit
        pi3.place(x=555, y=146)
        pj3 = Entry(modal, width=8, textvariable=tLyr3, state=pState)
        pj3.place(x=675, y=146)
        # ----------------- set entry field to read only ---------[]
        readonlyD = [pa3, pb3, pc3, pd3, pe3]
        for txtD in readonlyD:
            txtD.config(state='readonly')
        # --------------------------------------------------------[]

        # # ---------------- Line 5
        pa4 = Entry(modal, width=8, textvariable=tape4, state=pState)
        pa4.place(x=10, y=168)
        pb4 = Entry(modal, width=8, textvariable=xUCL4, state=pState)
        pb4.place(x=70, y=168)
        pc4 = Entry(modal, width=8, textvariable=xLCL4, state=pState)
        pc4.place(x=130, y=168)
        pd4 = Entry(modal, width=8, textvariable=sUCL4, state=pState)           # Upper Control Limit
        pd4.place(x=190, y=168)
        pe4 = Entry(modal, width=8, textvariable=sLCL4, state=pState)           # Lower control limit
        pe4.place(x=250, y=168)
        pf4 = Entry(modal, width=8, textvariable=xMean4, state="readonly")      # xMean Centre line
        pf4.place(x=375, y=168)
        pg4 = Entry(modal, width=8, textvariable=sMean4, state="readonly")      # sMean Centre line
        pg4.place(x=435, y=168)
        ph4 = Entry(modal, width=8, textvariable=xUSL4, state="readonly")       # Upper Set Limit
        ph4.place(x=495, y=168)
        pi4 = Entry(modal, width=8, textvariable=xLSL4, state="readonly")       # Lower Set Limit
        pi4.place(x=555, y=168)
        pj4 = Entry(modal, width=8, textvariable=tLyr4, state=pState)
        pj4.place(x=675, y=168)
        # ----------------- set entry field to read only ---------[]
        readonlyE = [pa4, pb4, pc4, pd4, pe4]
        for txtE in readonlyE:
            txtE.config(state='readonly')
        # --------------------------------------------------------[]
    else:
        # --------------- Line 1 (Lookup Rows)
        pass

    # TODO --------------------------------- Insert dynamic calculations for Mean, SD & USL []

    # Add Button for making selection -----------------------------------------------------[]
    Label(modal, text='EoL Sample [' + pTy + ']:').place(x=10, y=200)
    # Label(modal, text='sec').place(x=150, y=200)

    sRegime = Entry(modal, width=4, state='disabled', textvariable=sReg, bg='yellow', bd=4)
    sRegime.place(x=105, y=200)
    # ------------------------------------------------------------------------
    Label(modal, text='EoP Sample [' + pTy + ']:').place(x=150, y=200)
    # Label(modal, text='sec').place(x=150, y=200)

    pRegime = Entry(modal, width=4, state='disabled', textvariable=sReg, bg='purple', bd=4)
    pRegime.place(x=245, y=200)
    # ------------------------------------------------------------------------

    e_data = Button(modal, text="Edit " + pTy + " Metrics", width=12, bg="red", fg="white", command=editPHL)
    e_data.place(x=320, y=200)

    s_data = Button(modal, text="Save " + pTy + " Metrics", width=12, bg="blue", fg="white", state=pbutton, command=save_mMetrics)
    s_data.place(x=420, y=200)

    x_data = Button(modal, text="Exit Lookup", command=modal.destroy)
    x_data.place(x=630, y=200)

    modal.mainloop()