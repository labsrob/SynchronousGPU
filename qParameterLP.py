#
from tkinter import *
import tkinter as tk
from tkinter.simpledialog import Dialog
import qParamsHL as mx
pa1, pa2 = 0, 0

# Initialise example FIXME -- Work order number must be obtained from SQL or PLC
WON = "275044"


def save_mMetrics():
    print("\nCalling Function is:", pTy, WON)
    mx.saveMetricsQP(pTy, WON, sSize, gType, enHL, enAL, enFO)        # Set limits for Quality parameters
    s_data.config(state="disabled")                     # disable safe button on entry
    e_data.config(state="normal")                       # enable edit button on entry
    return


def editPHL():
    if pTy == 'RP':
        s_data.config(state="normal")                   # enable safe button on entry
        sRegime.config(state="normal")                  # enable data entry
        mx.qpHLrp(popmodal, sSize, xUCL, xLCL, sUCL, sLCL, xUCL1, xLCL1,  sUCL1, sLCL1, WON)
        e_data.config(state="disabled")     # prevent accidental entry clearance by use of edit button once!
    elif pTy == 'TT':                       # Tape Temp
        s_data.config(state="normal")
        sRegime.config(state="normal")      # enable data entry
        mx.qpHLtt(popmodal, sSize, xUCL, xLCL, sUCL, sLCL, xUCL1, xLCL1,  sUCL1, sLCL1, xUCL2, xLCL2,  sUCL2, sLCL2, xUCL3, xLCL3,  sUCL3, sLCL3, xUCL4, xLCL4, sUCL4, sLCL4, WON)
        e_data.config(state="disabled")
    elif pTy == 'ST':                       # Substrate Temp
        s_data.config(state="normal")
        sRegime.config(state="normal")      # enable data entry
        mx.qpHLst(popmodal, sSize, xUCL, xLCL, sUCL, sLCL, xUCL1, xLCL1,  sUCL1, sLCL1, xUCL2, xLCL2,  sUCL2, sLCL2, xUCL3, xLCL3,  sUCL3, sLCL3, xUCL4, xLCL4, sUCL4, sLCL4, WON)
        e_data.config(state="disabled")
    elif pTy == 'WS':                       # Winding Temp
        s_data.config(state="normal")
        sRegime.config(state="normal")      # enable data entry
        mx.qpHLws(popmodal, sSize, xUCL, xLCL, sUCL, sLCL, WON)
        e_data.config(state="disabled")
    elif pTy == 'TG':                       # Tape Ga
        s_data.config(state="normal")
        sRegime.config(state="normal")      # enable data entry
        mx.qpHLtg(popmodal, sSize, xUCL, xLCL, sUCL, sLCL, WON)
        e_data.config(state="disabled")
    else:
        pass


def paramsEntry(modal, gSize, gMode, defHL, defAL, defFO, pRP, pTT, pST, pWS, pTG):
    global pTy, xUCL, xUCL1, xUCL2, xUCL3, xUCL4, xLCL, xLCL1, xLCL2, xLCL3, xLCL4, \
           xMean, xMean1, xMean2, xMean3, xMean4, sMean, sMean1, sMean2, sMean3, sMean4,\
           xUSL, xUSL1, xUSL2, xUSL3, xUSL4, xLSL, xLSL1, xLSL2, xLSL3, xLSL4, \
           sUCL, sUCL1, sUCL2, sUCL3, sUCL4, sLCL, sLCL1, sLCL2, sLCL3, sLCL4,\
           pa1, pb1, pc1, pd1, pe1, pf1, pg1, ph1, pi1, pj1, pa2, pb2, pc2, pd2, pe2, pf2, pg2, ph2, pi2, pj2, \
           pa3, pb3, pc3, pd3, pe3, pf3, pg3, ph3, pi3, pj3, pa4, pb4, pc4, pd4, pe4, pf4, pg4, ph4, pi4, pj4, \
           pf, pg, ph, pi, pf1, pg1, ph1, pi1, sSize, popmodal, s_data, e_data, gType, enHL, enAL, enFO, sel_SS, \
           sRegime, sReg

    # Define and initialise essential popup variables -------[RP  2 entries for hist limits]
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

    # -------------------------------------------------------[TT 5 entries for hist limits]
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

    # -------------------------------------------------------[ST 5 entries for hist limits]
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

    # -------------------------------------------------------[WS]
    Tapets, TLyts, xclts, sclts = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLts, xLCLts, sUCLts, sLCLts = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLts, xLSLts = StringVar(modal), StringVar(modal)
    # -----------------------
    Tapets1, TLyts1, xclts1, sclts1 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLts1, xLCLts1, sUCLts1, sLCLts1 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLts1, xLSLts1 = StringVar(modal), StringVar(modal)
    # ------------------------
    Tapets2, TLyts2, xclts2, sclts2 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLts2, xLCLts2, sUCLts2, sLCLts2 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLts2, xLSLts2 = StringVar(modal), StringVar(modal)
    # ------------------------
    Tapets3, TLyts3, xclts3, sclts3 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLts3, xLCLts3, sUCLts3, sLCLts3 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLts3, xLSLts3 = StringVar(modal), StringVar(modal)
    # -----------------------
    Tapets4, TLyts4, xclts4, sclts4 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUCLts4, xLCLts4, sUCLts4, sLCLts4 = StringVar(modal), StringVar(modal), StringVar(modal), StringVar(modal)
    xUSLts4, xLSLts4 = StringVar(modal), StringVar(modal)

    # -------------------------------------------------------[TG]
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
    gType = gMode
    enHL = defHL
    enAL = defAL
    enFO = defFO
    popmodal = modal        # copy into new var

    if pRP.get():
        print("\nRoller Pressure Checked..")
        pTy = 'RP'
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
        gen10, gen20, gen25, gen30, gen40, gen50, tupa, tupb, c, d, e = mx.decryptpProcessLim(WON, pTy)
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

    elif pTT.get():
        print("\nTape Temp Checked..")
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
        gen10, gen20, gen25, gen30, gen40, gen50, tupa, tupb, tupc, tupd, tupe = mx.decryptpProcessLim(WON, pTy)
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
        print("\nSubstrate Temp Checked..")
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
        gen10, gen20, gen25, gen30, gen40, gen50, tupa, tupb, tupc, tupd, tupe = mx.decryptpProcessLim(WON, pTy)
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

    elif pWS.get():
        print("\nWinding Speed Checked..")
        pTy = 'WS'
        pState = 'normal'
        pbutton = 'disabled'
        tape0 = Tapets
        xUCL = xUCLts
        xLCL = xLCLts
        sUCL = sUCLts
        sLCL = sLCLts
        xMean = xclts
        sMean = sclts
        xUSL = xUSLts
        xLSL = xLSLts
        tLyr = TLyts
        # ----------
        tape1 = Tapets1
        xUCL1 = xUCLts1
        xLCL1 = xLCLts1
        sUCL1 = sUCLts1
        sLCL1 = sLCLts1
        xMean1 = xclts1
        sMean1 = sclts1
        xUSL1 = xUSLts1
        xLSL1 = xLSLts1
        tLyr1 = TLyts1
        # -----------
        tape2 = Tapets2
        xUCL2 = xUCLts2
        xLCL2 = xLCLts2
        sUCL2 = sUCLts2
        sLCL2 = sLCLts2
        xMean2 = xclts2
        sMean2 = sclts2
        xUSL2 = xUSLts2
        xLSL2 = xLSLts2
        tLyr2 = TLyts2
        # ------------
        tape3 = Tapets3
        xUCL3 = xUCLts3
        xLCL3 = xLCLts3
        sUCL3 = sUCLts3
        sLCL3 = sLCLts3
        xMean3 = xclts3
        sMean3 = sclts3
        xUSL3 = xUSLts3
        xLSL3 = xLSLts3
        tLyr3 = TLyts3
        # ------------
        tape4 = Tapets4
        xUCL4 = xUCLts4
        xLCL4 = xLCLts4
        sUCL4 = sUCLts4
        sLCL4 = sLCLts4
        xMean4 = xclts4
        sMean4 = sclts4
        xUSL4 = xUSLts4
        xLSL4 = xLSLts4
        tLyr4 = TLyts4
        # Set static Values ---[l1, l2, l3]
        # TODO -- Load last used parameters ----------------[]
        gen10, gen20, gen25, gen30, gen40, gen50, tupa, tupb, c, d, e = mx.decryptpProcessLim(WON, pTy)
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
        print("\nTape Gap Checked..")
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
        gen10, gen20, gen25, gen30, gen40, gen50, tupa, tupb, c, d, e = mx.decryptpProcessLim(WON, pTy)
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
    # -----------------------------------------------------

    pf = Entry(modal, width=8, state="readonly", textvariable=xMean)        # xMean Centre line
    pf.place(x=310, y=80)
    pg = Entry(modal, width=8, state="readonly", textvariable=sMean)        # sMean Centre line
    pg.place(x=370, y=80)
    ph = Entry(modal, width=8,  state="readonly", textvariable=xUSL)         # Upper Set Limit
    ph.place(x=430, y=80)
    pi = Entry(modal, width=8, state="readonly", textvariable=xLSL)         # Lower Set Limit
    pi.place(x=490, y=80)
    pj = Entry(modal, width=8, textvariable=tLyr, state=pState)
    pj.place(x=550, y=80)
    pk = Entry(modal, width=8, state="readonly", textvariable=sReg)

    # ----------------- set entry field to read only ---------[]
    readonlyA = [pa, pb, pc, pd, pe]
    for txtA in readonlyA:
        txtA.config(state='readonly')
    # --------------------------------------------------------[]
    if pa1 and pTG.get() or pa1 and pWS.get():
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

    if not pWS.get() and not pTG.get():
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
        pf1.place(x=310, y=102)
        pg1 = Entry(modal, width=8, textvariable=sMean1, state="readonly")      # sMean Centre line
        pg1.place(x=370, y=102)
        ph1 = Entry(modal, width=8, textvariable=xUSL1, state="readonly")       # Upper Set Limit
        ph1.place(x=430, y=102)
        pi1 = Entry(modal, width=8, textvariable=xLSL1, state="readonly")       # Lower Set Limit
        pi1.place(x=490, y=102)
        pj1 = Entry(modal, width=8, textvariable=tLyr1, state=pState)
        pj1.place(x=550, y=102)
        # ----------------- set entry field to read only ---------[]
        readonlyB = [pa1, pb1, pc1, pd1, pe1]
        for txtB in readonlyB:
            txtB.config(state='readonly')
        # --------------------------------------------------------[]
        if pRP.get() and pa2:
            # Blank out irrelevant rows & its transient values in the Lookup Table
            canvasBlank = [pa2, pb2, pc2, pd2, pe2, pf2, pg2, ph2, pi2, pj2,
                           pa3, pb3, pc3, pd3, pe3, pf3, pg3, ph3, pi3, pj3,
                           pa4, pb4, pc4, pd4, pe4, pf4, pg4, ph4, pi4, pj4]
            for line in canvasBlank:
                line.config(state="normal")
                line.delete(0, 'end')
                line. config(state="disabled")
            # perform derived calculations ----[]

    if not pRP.get() and not pWS.get() and not pTG.get():
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
        pf2.place(x=310, y=124)
        pg2 = Entry(modal, width=8, textvariable=sMean2, state="readonly")          # sMean Centre line
        pg2.place(x=370, y=124)
        ph2 = Entry(modal, width=8, textvariable=xUSL2, state="readonly")           # Upper Set Limit
        ph2.place(x=430, y=124)
        pi2 = Entry(modal, width=8, textvariable=xLSL2, state="readonly")           # Lower Set Limit
        pi2.place(x=490, y=124)
        pj2 = Entry(modal, width=8, textvariable=tLyr2, state=pState)
        pj2.place(x=550, y=124)
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
        pf3.place(x=310, y=146)
        pg3 = Entry(modal, width=8, textvariable=sMean3, state="readonly")      # sMean Centre line
        pg3.place(x=370, y=146)
        ph3 = Entry(modal, width=8, textvariable=xUSL3, state="readonly")       # Upper Set Limit
        ph3.place(x=430, y=146)
        pi3 = Entry(modal, width=8, textvariable=xLSL3, state="readonly")       # Lower Set Limit
        pi3.place(x=490, y=146)
        pj3 = Entry(modal, width=8, textvariable=tLyr3, state=pState)
        pj3.place(x=550, y=146)
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
        pf4.place(x=310, y=168)
        pg4 = Entry(modal, width=8, textvariable=sMean4, state="readonly")      # sMean Centre line
        pg4.place(x=370, y=168)
        ph4 = Entry(modal, width=8, textvariable=xUSL4, state="readonly")       # Upper Set Limit
        ph4.place(x=430, y=168)
        pi4 = Entry(modal, width=8, textvariable=xLSL4, state="readonly")       # Lower Set Limit
        pi4.place(x=490, y=168)
        pj4 = Entry(modal, width=8, textvariable=tLyr4, state=pState)
        pj4.place(x=550, y=168)
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
    Label(modal, text='Sample Space [' + pTy + ']:').place(x=10, y=200)
    Label(modal, text='sec').place(x=150, y=200)
    sRegime = Entry(modal, width=4, state='disabled', textvariable=sReg, bg='yellow', bd=4)
    sRegime.place(x=120, y=200)

    e_data = Button(modal, text="Edit " + pTy + " Metrics", width=13, bg="red", fg="white", command=editPHL)
    e_data.place(x=220, y=200)

    s_data = Button(modal, text="Save " + pTy + " Metrics", width=13, bg="blue", fg="white", state=pbutton, command=save_mMetrics)
    s_data.place(x=350, y=200)

    x_data = Button(modal, text="Exit Lookup", command=modal.destroy)
    x_data.place(x=530, y=200)

    modal.mainloop()