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

import tkinter as tk
from tkinter import *
from threading import *
from tkinter import messagebox, ttk
LARGE_FONT = ("Verdana", 10, 'bold')
# ---------------------------------
import qParameterLP as hla
import pParamsHL as mp

import pWON_finder as sqld

# ---------------------------------------------

# Initialise example FIXME -- Work order number must be obtained from SQL or PLC
WON = "275044"
sel_SS = "30"
sel_gT = "S-Domino"


# -----------------

def errorConfig():
    messagebox.showerror("Configuration:", "Enable Statistic on Two Parameters")


def errorNote():
    messagebox.showerror('Error', 'Empty field(s)')
    return


def successNote():
    messagebox.showinfo('Saved', 'Config Saved')
    return


def save_pMetrics():            # Save historical Limits for Production Parameters
    print("\nSaving Production Constants..")
    grayOut = [e5, e6, e7, e8]                                                      # set value entry field to read only
    for fld in grayOut:
        fld.config(state='readonly')
    e7.config(state='disabled')
    e8.config(state='disabled')
    mp.saveMetricspP(WON, sel_SS, sel_gT, sSta, sEnd, 0, 0, usepHL)      # Set limits for Quality parameters
    s_butt.config(state="disabled")                                                 # disable safe button on entry

    return


def clearMetrics():
    # clear the content of chart parameter using change settings button ---
    global e5, e6, e7, e8

    sSta.set('07:00:00')
    sEnd.set('17:00:00')
    e5 = Entry(pop, width=8, state='normal', textvariable=sSta)
    e5.place(x=290, y=10)           # Shift starts
    e6 = Entry(pop, width=8, state='normal', textvariable=sEnd)
    e6.place(x=290, y=40)           # Shift ends

    e7 = ttk.Combobox(pop, width=10, values=[" Select", "10", "15", "20", "23", "25", "30"], state="normal")
    e7.bind("<<ComboboxSelected>>", display_sel)
    e7.place(x=100, y=10)

    e8 = ttk.Combobox(pop, width=10, values=["SS-Domino", "GS-Discrete"], state="normal")
    e8.bind("<<ComboboxSelected>>", display_selection)
    e8.place(x=100, y=40)

    # repopulate with default values -----------#
    s_butt.config(state="normal")               # enable edit button (Sve Details) on entry
    mp.ppHLderivation(pop, gSize1, gSize2, xUCLLP, xLCLLP, xUCLLA, xLCLLA)

    metRO = True
    print('SQL Field State:', metRO)            # metric fields set to read only

    return metRO


def display_selection(event):
    global sel_gT

    # Get the selected value.
    sel_gT = e8.get()
    if sel_gT == "S-Domino":     # butterfly effect/small change
        messagebox.showinfo(message="Combines the rising/falling edges of previous subgroup", title=f"{sel_gT} Group")
    elif sel_gT == "F-Discrete":
        messagebox.showinfo(message="Evaluates new subgroup samples in the order of index", title=f"{sel_gT} Group")
    else:
        pass
    # print("The drop-down has been opened!")
    print('Selected Group Type:', sel_gT)
    return


def display_sel(event):
    global sel_SS

    # Get the selected value ------#
    sel_SS = e7.get()
    if sel_SS == "10":
        messagebox.showinfo(message="Computed Mean with A3=0.975, B3=0.284, B4=1.716", title=f"{sel_SS} Sample Size")
    elif sel_SS == "15":   # Unstable Domino
        messagebox.showinfo(message="Computed Mean with A3=0.789, B3=0.428, B4=1.572", title=f"{sel_SS} Sample Size")
    elif sel_SS == "20":
        messagebox.showinfo(message="Computed Mean with A3=0.680, B3=0.510, B4=1.490", title=f"{sel_SS} Sample Size")
    elif sel_SS == "23":
        messagebox.showinfo(message="Computed Mean with A3=0.633, B3=0.545, B4=1.455", title=f"{sel_SS} Sample Size")
    elif sel_SS == "25":
        messagebox.showinfo(message="Computed Mean with A3=0.606, B3=0.565, B4=1.435", title=f"{sel_SS} Sample Size")
    elif sel_SS == "30":
        messagebox.showinfo(message="Computed Mean with A3=0.553, B3=0.604, B4=1.396", title=f"{sel_SS} Sample Size")
    else:
        pass
    print('\nSelected Sample Size:', sel_SS)

    return

# pMax, pStat

def plotMinMax():
    global pStat, pMax
    if minMax.get():
        print('\nMin Max selected..')
        pMax = 1
        pStat = 0
        minMax.set(1)
        ctrlS.set(0)
    else:
        pMax = 1
        pStat = 0
        minMax.set(1)
        ctrlS.set(0)
    print('Plot Min/Max:', pMax, 'Plot Stats:', pStat)


def plotCChart():
    global pStat, pMax
    print('\nControl Chart selected..')
    if ctrlS.get():
        pStat = 1
        pMax = 0
        ctrlS.set(1)
        minMax.set(0)
    else:
        pStat = 1
        pMax = 0
        minMax.set(0)
        ctrlS.set(1)
    print('Plot Stats:', pStat, 'Plot Min/Max:', pMax)


def runChecksPQ():
    global usepHL
    # Do a toggle from Historical limits checkbutton to enforce one choice --------[]
    if hLmtA.get():
        button2.config(state="normal")
        hLmtA.set(1)
        usepHL = True      # Use production parameter historical limits
    else:
        button2.config(state="disabled")
        hLmtA.set(0)
        usepHL = False

    return usepHL


def runChecksA():
    if pRP.get():
        pRP.set(1)
        pTT.set(0)
        pST.set(0)
        pWS.set(0)
        pTG.set(0)
        hla.paramsEntry(modal, sel_SS, sel_gT, qHl, qAl, f_over, pRP, pTT, pST, pWS, pTG)
    else:
        pRP.set(0)


def runChecksB():
    if pTT.get():
        pTT.set(1)
        pRP.set(0)
        pST.set(0)
        pWS.set(0)
        pTG.set(0)
        hla.paramsEntry(modal, sel_SS, sel_gT, qHl, qAl, f_over, pRP, pTT, pST, pWS, pTG)
    else:
        pTT.set(0)


def runChecksC():
    if pST.get():
        pST.set(1)
        pRP.set(0)
        pTT.set(0)
        pWS.set(0)
        pTG.set(0)
        hla.paramsEntry(modal, sel_SS, sel_gT, qHl, qAl, f_over, pRP, pTT, pST, pWS, pTG)
    else:
        pST.set(0)


def runChecksD():
    if pWS.get():
        pWS.set(1)
        pRP.set(0)
        pTT.set(0)
        pST.set(0)
        pTG.set(0)
        hla.paramsEntry(modal, sel_SS, sel_gT, qHl, qAl, f_over, pRP, pTT, pST, pWS, pTG)
    else:
        pWS.set(0)


def runChecksE():
    if pTG.get():
        pTG.set(1)
        pRP.set(0)
        pTT.set(0)
        pST.set(0)
        pWS.set(0)
        hla.paramsEntry(modal, sel_SS, sel_gT, qHl, qAl, f_over, pRP, pTT, pST, pWS, pTG)
    else:
        pTG.set(0)


def pConfigs():                             # FIXME ------ Configuration page []
    global modal, pRP, pTT, pST, pWS, pTG

    # prevent parent window closure until 'Save settings' ---[]
    pop.protocol("WM_DELETE_WINDOW", preventClose)      # prevent closure even when using (ALT + F4)
    # -------------------------------------------------------[]

    modal = Toplevel(pop)
    modal.wm_attributes('-topmost', True)

    pRP, pTT, pST, pWS, pTG = IntVar(), IntVar(), IntVar(), IntVar(), IntVar()

    # --------------------------------------------------------------------------------------------------------[]
    modal.resizable(False, False)

    w, h = 615, 250
    modal.title('Lookup Table: Define Historical Limits')
    screen_w = modal.winfo_screenwidth()
    screen_h = modal.winfo_screenheight()
    x_c = int((screen_w / 2) - (w / 2))
    y_c = int((screen_h / 2) - (h / 2))
    modal.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))

    # --------------------------------------------------------[]
    a1 = Checkbutton(modal, text="RollerPressure", font=("bold", 10), variable=pRP, command=runChecksA)
    a1.place(x=20, y=10)
    a2 = Checkbutton(modal, text="TapeTemp", font=("bold", 10), variable=pTT, command=runChecksB)
    a2.place(x=145, y=10)
    a3 = Checkbutton(modal, text="SubstrateTemp", font=("bold", 10), variable=pST, command=runChecksC)
    a3.place(x=250, y=10)
    a4 = Checkbutton(modal, text="WindingSpeed", font=("bold", 10), variable=pWS, command=runChecksD)
    a4.place(x=380, y=10)
    a5 = Checkbutton(modal, text="TapeGaps", font=("bold", 10), variable=pTG, command=runChecksE)
    a5.place(x=500, y=10)

    separator = ttk.Separator(modal, orient='horizontal')
    separator.place(relx=0.01, rely=0.17, relwidth=0.98, relheight=0.02)

    # ----------------------------------------[Laser Power]
    Label(modal, text='Tape Size').place(x=10, y=50)
    Label(modal, text='x̄UCL').place(x=80, y=50)
    Label(modal, text='x̄LCL').place(x=140, y=50)
    Label(modal, text='ŝUCL').place(x=200, y=50)
    Label(modal, text='ŝLCL').place(x=260, y=50)
    Label(modal, text='x̄Mean').place(x=320, y=50)
    Label(modal, text='ŝMean').place(x=380, y=50)
    Label(modal, text='x̄USL').place(x=440, y=50)
    Label(modal, text='x̄LSL').place(x=500, y=50)
    Label(modal, text='Layer(s)').place(x=550, y=50)

    # Label(pop, text='X\u033FLine :').place(x=278, y=110)
    # Label(pop, text='S\u0305Line :').place(x=400, y=110)

    # # Add Button for making selection -----------------------------------------------------[]
    # rf = Button(modal, text="Save " + pTy + " Metrics", command=saveMetricRP, bg="green", fg="white")
    # rf.place(x=254, y=200)
    return


def enQHL():
    global qHl, qAl, f_over
    if pLmtA.get():
        qHl = 1
        qAl = 0
        f_over = shewhart.get()
        dnv_butt.config(state="normal")
        pLmtA.set(qHl)
        pLmtB.set(0)
    else:
        qHl = 0
        qAl = 1
        f_over = shewhart.get()
        dnv_butt.config(state="disabled")
        pLmtA.set(qHl)
        pLmtB.set(0)
        shewhart.set(0)

    return qHl, qAl, f_over


def enQAL():
    global qAl, qHl, f_over
    if pLmtB.get():
        qAl = 1
        qHl = 0
        f_over = 0
        dnv_butt.config(state="disabled")
        pLmtB.set(qAl)
        pLmtA.set(0)
        shewhart.set(0)
    else:
        qAl = 0
        qHl = 0
        f_over = 0
        dnv_butt.config(state="disabled")
        pLmtB.set(qAl)
        pLmtA.set(0)
        shewhart.set(0)

    return qAl, qHl, f_over


def enAFO():
    global f_over
    if shewhart.get():
        f_over = 1
        shewhart.set(1)
        pLmtB.set(0)
    else:
        f_over = 0
        shewhart.set(0)
        pLmtB.set(0)

    return f_over


def preventClose():
    print('Variable State:', pLmtA.get())
    pass


def metricsConfig():        # FIXME -----------------------[Lookup Table Page]

    global pLmtA, sSta, sEnd, eStat, gSize1, gSize2, xUCLLP, xLCLLP, xUCLLA, xLCLLA, xUCLHT, xLCLHT, xUCLDL, \
        xLCLDL, xUCLDD, xLCLDD, xUCLOT, xLCLOT, hLmtA, pLmtB, minMax, ctrlS, shewhart, s_butt, sSta, sEnd, e5, e6, \
        dnv_butt, button2

    # Define volatile runtime variables -------------------[]
    sqlRO = False  # SQL server filed is read only
    metRO = False

    # Define and initialise essential popup variables -----------------------------------------
    xUCLLP, xLCLLP, sUCLLP, sLCLLP = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
    xUCLLA, xLCLLA, sUCLLA, sLCLLA = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
    xUCLHT, xLCLHT, sUCLHT, sLCLHT = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
    xUCLDL, xLCLDL, sUCLDL, sLCLDL = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
    xUCLDD, xLCLDD, sUCLDD, sLCLDD = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
    xUCLOT, xLCLOT, sUCLOT, sLCLOT = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
    # -----------------------------------------------

    sSta, sEnd, gSize1, gSize2 = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
    lPwr, lAng, eStat, optm1, optm2 = IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop)

    XBarMLP, SBarMLP, XBarMLA, SBarMLA = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
    XBarMHT, SBarMHT, XBarMDL, SBarMDL = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
    XBarMDD, SBarMDD, XBarMOT, SBarMOT = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)

    pLmtA, pLmtB, pLmtC, pLmtD, pLmtE, pLmtF = IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop)
    hLmtA, hLmtB, shewhart, Sample = IntVar(pop), IntVar(pop), IntVar(pop), StringVar(pop)
    minMax, ctrlS = IntVar(pop), IntVar(pop),

    # ------------------ Auto canvass configs -------[]
    y_start = 110
    y_incmt = 30
    # global pop, screen_h, screen_w, x_c, y_c
    # center object on the screen---
    pop.resizable(False, False)
    height = (95 + y_start + (y_incmt * 5))
    w, h = 520,  height # 450

    pop.title('Setting Chart Parameters')
    screen_w = pop.winfo_screenwidth()
    screen_h = pop.winfo_screenheight()
    x_c = int((screen_w / 2) - (w / 2))
    y_c = int((screen_h / 2) - (h / 2))
    pop.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))

    # creating labels and positioning them on the grid --------[]
    Label(pop, text='Sample Size').place(x=10, y=10)
    Label(pop, text='Group Type').place(x=10, y=40)
    Label(pop, text='Shift Begins @').place(x=200, y=10)
    Label(pop, text='Shift Closes @').place(x=200, y=40)

    # --------------------------------------------------------[]
    Label(pop, text='[Critical Production Parameters]', font=("bold", 10)).place(x=10, y=80)
    separator = ttk.Separator(pop, orient='horizontal')
    separator.place(relx=0.01, rely=0.21, relwidth=0.98, relheight=0.02) #y=0.17
    # -------------------------------------------------------------------------[]

    # ----------------------------------------[Roller Force]
    Label(pop, text='UCL-RF').place(x=10, y=y_start)
    Label(pop, text='LCL-RF').place(x=138, y=y_start)
    Label(pop, text='X\u033FLine :').place(x=278, y=y_start)
    Label(pop, text='S\u0305Line :').place(x=400, y=y_start)

    # ----------------------------------------[Cell Tension]
    Label(pop, text='UCL-CT').place(x=10, y=y_start + y_incmt * 1)
    Label(pop, text='LCL-CT').place(x=138, y=y_start + y_incmt * 1)
    Label(pop, text='X\u033FLine :').place(x=278, y=y_start + y_incmt * 1)
    Label(pop, text='S\u0305Line :').place(x=400, y=y_start + y_incmt * 1)

    # --------------------------------------------------------------------
    # load variables directly from ini files --[TODO]
    sbutton = 'disabled'  # disable Save button on entry state
    cState = 'disabled'

    separatorU = ttk.Separator(pop, orient='horizontal')
    separatorU.place(relx=0.33, rely=0.61, relwidth=0.65, relheight=0.01) # y=7.3
    # ---------------------------------------------------------------------
    Label(pop, text='[DNV Quality Parameters]', font=("bold", 10)).place(x=10, y=(y_start + 5) + (y_incmt * 3))  #320 | 7
    dnv_butt = Button(pop, text="Define Limits per Quality Parameter", wraplength=160, justify=CENTER, width=24, height=3,
                     font=("bold", 12), command=pConfigs, state=cState)
    dnv_butt.place(x=260, y=3+y_start + y_incmt * 4)  # 350 | 8

    p1 = Checkbutton(pop, text="Enable Historical DNV Limits", font=("bold", 10), variable=pLmtA, command=enQHL)
    p1.place(x=10, y=3 + y_start + y_incmt * 4) # 353
    p2 = Checkbutton(pop, text="Use Shewhart's Auto Limits", font=("bold", 10), variable=pLmtB, command=enQAL)
    p2.place(x=10, y=y_start + y_incmt * 5) #373 | 9
    pLmtB.set(1)
    p3 = Checkbutton(pop, text="Enable Auto Fail-Over", font=("bold", 10), variable=shewhart, command=enAFO)
    p3.place(x=10, y=y_start + y_incmt * 6)  # 393 |10

    def display_selection(event):
        # Get the selected value.
        selection = e8.get()
        if selection == "S-Domino":     # butterfly effect/small change
            messagebox.showinfo(message="Combines the rising/falling edges of previous subgroup", title=f"{selection} Group")
        elif selection == "F-Discrete":
            messagebox.showinfo(message="Evaluates new subgroup samples in the order of index", title=f"{selection} Group")
        # print("The drop-down has been opened!")
        return

    def display_sel(event):
        # Get the selected value.
        selection = e7.get()
        if selection == "10":
            messagebox.showinfo(message="Computed Mean with A3=0.975, B3=0.284, B4=1.716", title=f"{selection} Sample Size")
        elif selection == "15":   # Unstable Domino
            messagebox.showinfo(message="Computed Mean with A3=0.789, B3=0.428, B4=1.572", title=f"{selection} Sample Size")
        elif selection == "20":
            messagebox.showinfo(message="Computed Mean with A3=0.680, B3=0.510, B4=1.490", title=f"{selection} Sample Size")
        elif selection == "23":
            messagebox.showinfo(message="Computed Mean with A3=0.633, B3=0.545, B4=1.455", title=f"{selection} Sample Size")
        elif selection == "25":
            messagebox.showinfo(message="Computed Mean with A3=0.606, B3=0.565, B4=1.435", title=f"{selection} Sample Size")
        elif selection == "30":
            messagebox.showinfo(message="Computed Mean with A3=0.553, B3=0.604, B4=1.396", title=f"{selection} Sample Size")
        else:
            pass

        return

    # ------------------------------------[Multiple options: Laser Power (M)]
    # set initial variables or last known variables
    # Set default values for Production Params ----
    # TODO ---- command=saveMetricRP)

    # Call function for configuration file ----[]
    LmType, sSize, gType, sStart, sStops, pMinMax, pContrl, pParam1, pParam2 = mp.decryptMetricspP(WON)
    # Break down each element to useful list
    if gSize1 and gType:
        gSize1.set(sSize)                       # Group Size
        gSize2.set(gType)                       # Group Type (1=Domino, 2=SemiDomino, 3=Discrete)
        sSta.set(sStart)
        sEnd.set(sStops)
    else:
        gSize1.set('30')
        gSize2.set('GS-Discrete')               # Group Type (1=Domino, 2=SemiDomino, 3=Discrete)
        sSta.set('07:00:00 ')
        sEnd.set('01:00:00 ')

    # unpack convoluted elements into list -[A]
    if pParam1:
        pOne = pParam1.split(',')               # split into list elements
        xUCLLP.set(float(pOne[2].strip("' ")))  # Strip out the element of the list
        xLCLLP.set(float(pOne[3].strip("' ")))
        XBarMLP.set(float(pOne[4].strip("' ")))
        SBarMLP.set(float(pOne[5].strip("' ")))
    else:
        xUCLLP.set('0')
        xLCLLP.set('0')
        XBarMLP.set('0')
        SBarMLP.set('0')
    # --------------------------------------[B]
    if pParam2:
        pTwo = pParam2.split(',')               # split into list elements
        xUCLLA.set(float(pTwo[2].strip("' ")))  # Strip out the element of the list
        xLCLLA.set(float(pTwo[3].strip("' ")))
        XBarMLA.set(float(pTwo[4].strip("' ")))
        SBarMLA.set(float(pTwo[5].strip("' ")))
    else:
        xUCLLA.set('0')
        xLCLLA.set('0')
        XBarMLA.set('0')
        SBarMLA.set('0')

    sUCLLP.set('0')
    sLCLLP.set('0')
    sUCLLA.set('0')
    sLCLLA.set('0')
    sUCLHT.set('0')
    sLCLHT.set('0')

    lPwr.set(0)
    hLmtA.set(0)
    hLmtB.set(0)
    optm1.set(1)
    optm2.set(0)

    # TODO ------------------------------------- [Include command=klr ] ---------------------------------------[]
    c1 = Checkbutton(pop, text="Historical Limits", font=("bold", 10), variable=hLmtA, command=runChecksPQ)
    c1.place(x=370, y=6)  # x=290, y=80, width=20,
    # ------------------

    if not metRO:
        # TODO --------------------------------------------------------[]

        e7 = ttk.Combobox(pop, width=10, values=[" Select Size", "10", "15", "20", "23", "25", "30"], state="disabled")
        e7.bind("<<ComboboxSelected>>", display_sel)
        e7.current(0)                       # set default choice
        e7.place(x=100, y=10)

        e8 = ttk.Combobox(pop, width=10, values=["SS-Domino", "GS-Discrete"], state="disabled")
        e8.bind("<<ComboboxSelected>>", display_selection)
        e8.current(0)                       # set default choice to first index
        e8.place(x=100, y=40)
        # --------------------------------------------------- [Shift information]
        e5 = Entry(pop, width=8, textvariable=sSta, state="readonly")
        e5.place(x=290, y=10)
        e6 = Entry(pop, width=8, textvariable=sEnd, state="readonly")
        e6.place(x=290, y=40)

        # # Add isolation button
        button2 = Button(pop, text="Edit Stats Properties", bg="red", fg="white", state="disabled", command=clearMetrics)
        button2.place(x=370, y=35)        # place(x=520, y=47)

        # Declare variable arrays ----------------------------[Roller Force]
        a1a = Entry(pop, width=8, textvariable=xUCLLP, state="readonly")
        a1a.place(x=65, y=y_start)
        a2a = Entry(pop, width=8, textvariable=xLCLLP, state="readonly")
        a2a.place(x=190, y=y_start)

        a3a = Entry(pop, width=8, textvariable=XBarMLP, state="readonly")
        a3a.place(x=325, y=y_start)
        a4a = Entry(pop, width=8, textvariable=SBarMLP, state="readonly")
        a4a.place(x=447, y=y_start)

        # ------------- DNV Requirements ----------------[Cell Tension]
        b1b = Entry(pop, width=8, textvariable=xUCLLA, state="readonly")
        b1b.place(x=65, y=y_start + y_incmt * 1)
        b2b = Entry(pop, width=8, textvariable=xLCLLA, state="readonly")
        b2b.place(x=190, y=y_start + y_incmt * 1)

        b3b = Entry(pop, width=8, textvariable=XBarMLA, state="readonly")
        b3b.place(x=325, y=y_start + y_incmt * 1)
        b4b = Entry(pop, width=8, textvariable=SBarMLA, state="readonly")
        b4b.place(x=447, y=y_start + y_incmt * 1)

    else:
        e7 = ttk.Combobox(pop, width=8, values=[" Select", "10", "15", "20", "23", "25", "25"], state="normal")
        e7.bind("<<ComboboxSelected>>", display_sel)
        e7.current(0)  # set default choice
        e7.place(x=40, y=50)

        e8 = ttk.Combobox(pop, width=10, values=["SS-Domino", "GS-Discrete"], state="normal")
        e8.bind("<<ComboboxSelected>>", display_selection)
        e8.current(0)  # set default choice to first index
        e8.place(x=172, y=50)
        # -------------------------------------------------[ Shift duration ]
        e5 = Entry(pop, width=8, textvariable=sSta, state="normal")
        e5.place(x=290, y=10)
        e6 = Entry(pop, width=8, textvariable=sEnd, state="normal")
        e6.place(x=290, y=40)

        # Declare variable arrays -------------------------[Roller Force]
        a1a = Entry(pop, width=8, textvariable=xUCLLP, state="normal")
        a1a.place(x=65, y=y_start)
        a2a = Entry(pop, width=8, textvariable=xLCLLP, state="normal")
        a2a.place(x=190, y=y_start)
        a3a = Entry(pop, width=8, textvariable=XBarMLP, state="normal")
        a3a.place(x=325, y=y_start)
        a4a = Entry(pop, width=8, textvariable=SBarMLP, state="normal")
        a4a.place(x=447, y=y_start)

        # ------------- DNV Requirements -------------[Cell Tension]
        b1b = Entry(pop, width=8, textvariable=xUCLLA, state="normal")
        b1b.place(x=65, y=y_start + y_incmt * 1)
        b2b = Entry(pop, width=8, textvariable=xLCLLA, state="normal")
        b2b.place(x=190, y=y_start + y_incmt * 1)
        b3b = Entry(pop, width=8, textvariable=XBarMLA, state="normal")
        b3b.place(x=325, y=y_start + y_incmt * 1)
        b4b = Entry(pop, width=8, textvariable=SBarMLA, state="normal")
        b4b.place(x=447, y=y_start + y_incmt * 1)

    # Add Button for making selection -------------------------------
    p4 = Checkbutton(pop, text="Plot Min/Max Chart", font=("bold", 10), variable=minMax, command=plotMinMax)
    minMax.set(1)   # Set default Plot values to Min/Max Plot
    p4.place(x=10, y=y_start + y_incmt * 2)     # 6
    p4 = Checkbutton(pop, text="Plot Control Chart", font=("bold", 10), variable=ctrlS, command=plotCChart)
    p4.place(x=190, y=y_start + y_incmt * 2)    # 6
    # ------------------------------ # TODO ---- command=saveMetricRP)
    s_butt = Button(pop, text="Save Details",  fg="black", state=sbutton, command=save_pMetrics)
    s_butt.place(x=410, y=5 + y_start + y_incmt * 2)  #295 now 2
    # --------------------------------
    button5 = Button(pop, text="Exit Settings", command=pop.destroy)
    button5.place(x=410, y=22 + y_start + y_incmt * 6)     # 400 nowe 2
    # pop.mainloop()


if __name__ == '__main__':
    # root = tk.Tk()
    pop = Tk()

    # the main program
    metricsConfig()
    pop.mainloop()