# --------------------------------------------------------------------------
# Author: Dr RB Labs
# Developed for Magma Global - TechnipFMC Industrialization
# Email: robbielabs@uwl.ac.uk
# Copyright (C) 2023-2025, Robbie Labs
#
#
# -------------------- Primary User Graphic Interface ----------------------

import numpy as np
import pandas as pd
import spcWatchDog as wd
import selPlcColumnsTFM as vq
import selSqlColumnsTFM as qq
import time
import os
import sys
from datetime import datetime
from time import gmtime, strftime
import signal
import tkinter as tk
from tkinter import *
from threading import *
from tkinter import messagebox, ttk
from tkinter.simpledialog import askstring
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
LARGE_FONT = ("Verdana", 10, 'bold')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import loadSPCConfig as ty
import rtP_Evaluator as tq
from pydub import AudioSegment
from matplotlib.animation import FuncAnimation
# ---------------------------------
import pParamsHL as mp
import qParamsHL as mq
import pWON_finder as sqld
import qParameterLP as hla
# ------------------------------------------------------------------------[]

cpTapeW, cpLayerNo, runType = [], [], []
HeadA, HeadB, vTFM = 0, 0, 0
hostConn = 0
optm = True

import subprocess
try:
    subprocess.check_output('nvidia-smi')
    print('Nvidia GPU detected!')
except Exception:
    print('No Nvidia GPU in system!')

# ----------------------- Audible alert --------------------------------------------------[]
impath ='C:\\Users\\Labs\\PycharmProjects\\SynchronousSPC\\Media\\'
nudge = AudioSegment.from_wav(impath+'tada.wav')
error = AudioSegment.from_wav(impath+'error.wav')

# Define statistical operations ----------------------------------------------------------[]
WeldQualityProcess = True
paused = False

url = 'http://www.magmaglobal.com'
localArray = []                     # raising the bit for GUI canvas
exit_bit = []                       # enable the close out of all cascade windows

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

# ---------------------------------------------- Common to all Process Procedures -------------------------------[]
# Call function for configuration file ----[]
useHL, sSize, gType, sStart, sStops, pMinMax, pContrl, pParam1, pParam2 = mp.decryptMetricspP(WON)

# Break down each element to useful list ---[]
if useHL and pContrl and pParam1:           # Roller Pressure
    pOne = pParam1.split(',')               # split into list elements
    hUCLa = float(pOne[2].strip("' "))      # Strip out the element of the list
    hLCLa = float(pOne[3].strip("' "))
    hMeanA = float(pOne[4].strip("' "))
    hDevA = float(pOne[5].strip("' "))
    # --------------------------------
    dUCLa = float(pOne[6].strip("' "))
    dLCLa = float(pOne[7].strip("' "))
    # -------------------------------
    hUSLa = (hUCLa - hMeanA) / 3 * 6
    hLSLa = (hMeanA - hLCLa) / 3 * 6
    # -------------------------------
    PPerf = '$Pp_{k' + str(sSize) + '}$'  # Using estimated or historical Mean
    plabel = 'Pp'

elif pMinMax:
    hUCLa = 0  # TODO -- Allow model to compute sample size average values as center line.
    hLCLa = 0
    hMeanA = 0
    hDevA = 0
    dUCLa = 0
    dLCLa = 0
    hUSLa = 0
    hLSLa = 0

else:
    hUCLa = 0      # Computes Shewhart constants (Automatic Limits)
    hLCLa = 0
    hMeanA = 0
    hDevA = 0
    dUCLa = 0
    dLCLa = 0
    hUSLa = 0
    hLSLa = 0
    PPerf = '$Cp_{k' + str(sSize) + '}$'  # Using Automatic group Mean
    plabel = 'Cp'
# --------------------------------------------------------------------[]
# Break down each element to useful list
if useHL and pContrl and pParam2:           # Cell Tension Parameter
    pTwo = pParam2.split(',')                # split into list elements
    hUCLb = float(pTwo[2].strip("' "))       # Strip out the element of the list
    hLCLb = float(pTwo[3].strip("' "))
    hMeanB = float(pTwo[4].strip("' "))
    hDevB = float(pTwo[5].strip("' "))
    # --------------------------------
    dUCLb = float(pTwo[6].strip("' "))
    dLCLb = float(pTwo[7].strip("' "))
    # --------------------------------
    hUSLb = (hUCLb - hMeanB) / 3 * 6
    hLSLb = (hMeanB - hLCLb) / 3 * 6
    # -------------------------------
    PPerf = '$Pp_{k' + str(sSize) + '}$'    # Using estimated or historical Mean
    plabel = 'Pp'

else:
    hUCLb = 0                               # Computes Schewhart constants (Automatic Limits)
    hLCLb = 0
    hMeanB = 0
    hDevB = 0
    dUCLb = 0
    dLCLb = 0
    hUSLb = 0
    hLSLb = 0
    # -------------------------------
    # Process performance label when using computed/automatic group Mean
    PPerf = '$Cp_{k' + str(sSize) + '}$'    # Using Automatic group Mean
    plabel = 'Cp'
    print('Current Limits:', hUCLb, hLCLb, round(hUSLb, 3), round(hLSLb, 3), dUCLb, dLCLb)
# -----------------------------------[]
if useHL and pMinMax:                      # Use Historical Limit is binary choice
    plotType = '[Min/Max Plot]'
else:
    plotType = '[Control Plot]'
# ----------------------------------[]

# -----------------------------------------------------------------------------------------------------------------[]
smp_Sz = int(sSize)                                   # Allow SCADA User to specify window sample size
stp_Sz = gType                                        # Step Size (smp_St) Domino or Discrete group steps
# --------------------------[]
if stp_Sz == 'GS-Discrete':
    viz_cycle = 100
elif stp_Sz == 'SS-Domino':
    viz_cycle = 500
else:
    viz_cycle = 10
print('\nGroup Type:', stp_Sz, 'Sample Size:', smp_Sz)

# --------------------------------------------------------


class autoResizableCanvas(tk.Canvas):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<Configure>", self.resize)

    def resize(self, event):
        self.config(width=event.width, height=event.height)


def differential_idx(layer, idx1, idx2, idx3, idx4, idx5, idx6, idx7, idx8, pPos):    # Record for offline SPC analysis
    rtitle = ('================================= TCP01 - Realtime Index Tracker =============================\n')
    rheader = ('Time'+'\t\t'+'Layer#'+'\t'+'T1Row'+'\t'+'T2Row'+'\t'+'T3Row'+'\t'+'T4Row'+'\t'+'T5Row'+'\t'+'T6Row'+'\t'+'T7Row'+'\t'+'T8Row'+'\t'+'EstPos'+'\n')
    rdemaca = ("----------------------------------------------------------------------------------------------\n")
    event = datetime.now().strftime("%H:%M.%S")                 # WON as name for easy retrieval method
    PidxLog = 'IDXLog_' + str(processWON[0])                    # processed SQL index Log

    filepath = '.\\RT_Index_Log\\'+PidxLog+".txt"
    old_report = os.path.isfile(filepath)

    if not old_report:                                          # if doing a new report...
        f = open('.\\RT_Index_Log\\'+PidxLog+".txt", "a")       # Open new file and ...
        f.write(rtitle)                                         # Insert a Title
        f.write(rheader)                                        # Insert new header
        f.write(rdemaca)                                        # Insert demarcator
    else:                                                       # if it's an existing report
        f = open('.\\RT_Index_Log\\' + PidxLog + ".txt", "a")   # Just open the file for a write operations
    # initialise a tab delimited data and insert corresponding values in string format ------------------------[]
    f.write(event+'\t'+str(layer)+'\t'+str(idx1)+'\t'+str(idx2)+'\t'+str(idx3)+'\t'+str(idx4)+ '\t'+str(idx5)+'\t'+str(idx6)+'\t'+str(idx7)+'\t'+str(idx8)+ '\t'+str(pPos)+'\n')
    f.close()


def timeProcessor(runtimeType, smp_Sz, runtimeParams, regime, lapsedT):    # Record for offline SPC analysis

    rtitle = ('=== TCP1 - Processing Speed Tracker - '+runtimeType+ ' Samples ===\n')
    rheader = ('Rolling Type'+'\t'+'Sample'+'\t'+'Parameters#'+'\t'+'Regime'+'\t'+'LapsedTime'+'\n')
    rdemaca = ("----------------------------------------------------------\n")
    PidxLog = 'TXLog_' + str(processWON[0])                           # processed SQL index Log

    filepath = '.\\ProcessTime_Log\\'+PidxLog+".txt"
    old_report = os.path.isfile(filepath)

    if not old_report:                                              # if doing a new report...
        f = open('.\\ProcessTime_Log\\'+PidxLog+".txt", "a")        # Open new file and ...
        f.write(rtitle)                                             # Insert a Title
        f.write(rheader)                                            # Insert new header
        f.write(rdemaca)                                            # Insert demarcator
    else:                                                           # if it's an existing report
        f = open('.\\ProcessTime_Log\\' + PidxLog + ".txt", "a")    # Just open the file for a write operations
    # initialise a tab delimited data and insert corresponding values in string format --------------------------[]
    f.write(str(runtimeType)+'\t'+str(smp_Sz)+'\t'+str(runtimeParams)+'\t'+str(regime)+'\t'+str(lapsedT) +'\n')
    f.close()


def errorLog(err):
    fileName = datetime.now().strftime('SQLM2MLog '+"%Y-%m-%d")
    event = datetime.now().strftime("%Y-%m-%d %H:%M.%S")
    errorlogFile = str(fileName)
    f = open('.\\RuntimeLog\\'+errorlogFile+".txt", "a")
    f.write(event+' --- '+err+'\n')
    f.close()


# This function runs only on retro-play when SPC stalls and replayed
def bufferEOF(fname, N):
    # open index tracker file, and load the values in the end of file
    with open(fname) as file:
        for line in (file.readlines()[-N:]):
            oem = line
        # print('\nEND OF FILE:', oem)
        # print(line, end='')
    return oem


def checkhistDev(xUCL, MeanP, sampSiz):
    # Evaluate SPC constants with chosen sample size --
    print('SAMPLE:', sampSiz)
    if sampSiz == '10':
        const1 = A3[0]
        const2 = B3[0]
        const3 = B4[0]
    elif sampSiz == '15':
        const1 = A3[1]
        const2 = B3[1]
        const3 = B4[1]
    elif sampSiz == '20':
        const1 = A3[2]
        const2 = B3[2]
        const3 = B4[2]
    elif sampSiz == '23':
        const1 = A3[3]
        const2 = B3[3]
        const3 = B4[3]
    elif sampSiz == '25':
        const1 = A3[4]
        const2 = B3[4]
        const3 = B4[4]
    elif sampSiz == '30':
        const1 = A3[5]
        const2 = B3[5]
        const3 = B4[5]
    else:
        print('Sample Size undefined!, Exiting...')
    # Compute for stdDev  in  [xUCL = meanP + (const1 * stdDev)]
    stdDev = (xUCL - MeanP)/const1

    UCL = (const3 * stdDev)  # Upper control limits of 1 std dev
    LCL = (const2 * stdDev)  # Lower control limits of 1 Std dev

    return UCL, LCL, stdDev


def canvasOn(bitHigh=None):
    if bitHigh:
        localArray.append(True)     # Update local array with bit from GUI when active
    else:
        localArray.append(False)
    return


def callback():
    if messagebox.askokcancel("Quit", "Do you really wish to quit?"):
        # root.protocol('WM_DELETE_WINDOW', lambda: quit())
        import magmaSPC as en
        en.move_window(True)
        print('\nAfter Menu closes, check timer is alive...')
        root.destroy()
        localArray.clear()      # clear array held for GUI

    return


def menuExit():
    print('\nExiting Local GUI, bye for now...')
    print('Exit Bit:', len(exit_bit))
    if not exit_bit:        #  Check exit_bit for unitary value
        root.quit()         # Exit Apps if exit_bit is empty
        os._exit(0)         # Close out all process
    else:
        if len(exit_bit) >= 1:
            # Evaluate exit_bit as true (if cascade was called atr any point in time)
            proc_list = [p1.pid, p2.pid, p3.pid, p4.pid]
            for p in proc_list:
                try:
                    os.kill(p, signal.SIGTERM)
                    print('Process:', p, ' terminated by the User')
                except Exception:
                    print(f'Process {p} failed to terminate!')
        root.quit()
        os._exit(0)
# -------------------------------------------------------------------------------------------[ MAIN PROGRAM ]


def tabbed_canvas():    # Tabbed Common Classes -------------------[]
    # Create an instance of ttk style
    s = ttk.Style()
    s.theme_use('default')                                          # Options: ('clam', 'alt', 'default', 'classic')
    s.configure('TNotebook.Tab', background="green3")

    # Allow user to change critical process during runtime ----------[ Production Critical Parameters ]
    comboL = ttk.Combobox(root, values=[" Change Runtime Plot", "Roller Force", "New Process A", "New Process C"])
    comboL.place(x=872, y=2)
    comboL.current(0)

    comboR = ttk.Combobox(root, values=[" Change Runtime Plot", "Cell Tension", "New Process B", "New Process D"])
    comboR.place(x=1870, y=2)
    comboR.current(0)

    # -------------------------------------------------[]
    common_OEE()
    # Load from CFG fine and parse the variables ------[]

    def option_Left(event):
        method_selectedL = comboL.get()
        print("Left Selected:", method_selectedL)
        # ----- Call function ---------------
        if method_selectedL == 'Roller Force':
            label = ttk.Label(root, text='Roller Force '+plotType, font=LARGE_FONT)
            label.place(x=350, y=3)
            common_RF(root)
        elif method_selectedL == "Unassigned A":
            label = ttk.Label(root, text='Unassigned A '+plotType, font=LARGE_FONT)
            label.place(x=350, y=3)
            # common_PA(root)           # Uncomment to enable
        elif method_selectedL == "Unassigned C":
            label = ttk.Label(root, text='Unassigned C '+plotType, font=LARGE_FONT)
            label.place(x=350, y=3)
            # common_PC(root)           # Uncomment to enable
        else:
            common_RF(root)
    comboL.bind("<<ComboboxSelected>>", option_Left)

    # --------------------------------------------------------------[]
    def option_Right(event):
        method_selectedR = comboR.get()
        print("Right Selected:", method_selectedR)
        # ----- Call function ---------------
        if method_selectedR == "Cell Tension":
            label = ttk.Label(root, text='Cell Tension '+plotType, font=LARGE_FONT)
            label.place(x=1480, y=3)
            common_CT(root)
        elif method_selectedR == "Unassigned B":
            label = ttk.Label(root, text='Unassigned B '+plotType, font=LARGE_FONT)
            label.place(x=1480, y=3)
            # common_PB(root)       # Uncomment to enable
        elif method_selectedR == "Unassigned D":
            label = ttk.Label(root, text='Unassigned D '+plotType, font=LARGE_FONT)
            label.place(x=1480, y=3)
            # common_PD(root)        # Uncomment to enable
        else:
            common_CT(root)
    comboR.bind("<<ComboboxSelected>>", option_Right)

    # common_process(root)        # call common monitoring module

    # Set up embedding notebook (tabs) --------------------------[B]
    notebook = ttk.Notebook(root, width=2500, height=850)   # Declare Tab overall Screen size
    notebook.grid(column=0, row=0, padx=10, pady=450)       # Tab's spatial position on the Parent
    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)
    tab3 = ttk.Frame(notebook)
    tab4 = ttk.Frame(notebook)
    tab5 = ttk.Frame(notebook)
    tab6 = ttk.Frame(notebook)
    # --------------------------DNV Parameters -----[]
    notebook.add(tab1, text="Roller Pressure")
    notebook.add(tab2, text="Tape Temperature")
    notebook.add(tab3, text="Substrate Temperature")
    notebook.add(tab4, text="Winding Tape Speed")
    notebook.add(tab5, text="Gap Measurements")
    notebook.add(tab6, text="EoL Reporting System")
    notebook.grid()

    # Create DNV tab frames properties -------------[]
    app1 = rollerPressure(master=tab1)
    app1.grid(column=0, row=0, padx=10, pady=10)

    app2 = tapeTemp(master=tab2)
    app2.grid(column=0, row=0, padx=10, pady=10)

    app3 = substTemp(master=tab3)
    app3.grid(column=0, row=0, padx=10, pady=10)

    app4 = windingSpeed(master=tab4)
    app4.grid(column=0, row=0, padx=10, pady=10)

    app5 = tapeGap(master=tab5)
    app5.grid(column=0, row=0, padx=10, pady=10)

    app6 = collectiveRPT(master=tab6)
    app6.grid(column=0, row=0, padx=10, pady=10)

    # ------------------------------------------[]
    root.mainloop()


def readRPTrf(text_widget, rptID):
    # file_path = filedialog.askopenfilename(title='Select a Text File', filetypes=[('Text files&quot', '*.txt')])
    file_path = 'D:\\CuttingEdge\\BETA_ver3.6\\FMEA_Log\\'+ rptID+'.txt'
    rpfMissing = 'D:\\CuttingEdge\\BETA_ver3.6\\FMEA_Log\\RPT_NOTFOUND.txt'
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            text_widget.delete(1.0, tk.END)            # Clear previous content
            text_widget.insert(tk.END, content)
    else:
        with open(rpfMissing, 'r') as file:
            content = file.read()
            text_widget.delete(1.0, tk.END)            # Clear previous content
            text_widget.insert(tk.END, content)


# --------------- Defines the collective one screen structure -------------------------------------[]


class collectiveRPT(ttk.Frame):                                # End of Layer Progressive Report Tabb
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        # self.grid(column=0, row=0, padx=10, pady=10)
        self.place(x=10, y=10)
        self.createWidgets()

    def createWidgets(self):
        label = ttk.Label(self, text="End of Layer - Progressive Summary:                                          ", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        # label.place(x=100, y=50)
        # Define Axes ---------------------#
        combo = ttk.Combobox(self, values=["= Select Progressive Report =", "Roller Pressure",
                                           "Tape Temperature", "Subs Temperature",
                                           "Winding Speed", "Gap Measurement"], width=25)
        combo.place(x=520, y=10)
        combo.current(0)

        # Create empty Text Space -----------------------------------
        text_widget = tk.Text(self, wrap='word', width=110, height=80)
        text_widget.pack(padx=10, pady=10)

        def option_selected(event):
            selected_option = combo.get()
            if selected_option == "Roller Pressure":
                rpt = "RPT_RP_" + str(processWON[0])
                readRPTrf(text_widget, rpt)                                 # Open txt file from FMEA folder
            elif selected_option == "Tape Temperature":
                rpt = "RPT_TT_" + str(processWON[0])
                readRPTrf(text_widget, rpt)                                 # Open txt file from FMEA folder
            elif selected_option == "Subs Temperature":
                rpt = "RPT_ST_" + str(processWON[0])
                readRPTrf(text_widget, rpt)                                 # Open txt file from FMEA folder
            elif selected_option == "Winding Speed":
                rpt = "RPT_WS_" + str(processWON[0])
                readRPTrf(text_widget, rpt)                                 # Open txt file from FMEA folder
            elif selected_option == "Gap Measurement":
                rpt = "RPT_TG_" + str(processWON[0])
                readRPTrf(text_widget, rpt)                                 # Open txt file from FMEA folder
            else:
                rpt = "VOID_REPORT"
                readRPTrf(text_widget, rpt)

            print("You selected:", selected_option)
        combo.bind("<<ComboboxSelected>>", option_selected)

        # Update Canvas -----------------------------------------------------[NO FIGURE YET]
        # canvas = FigureCanvasTkAgg(fig, self)
        # canvas.get_tk_widget().pack(expand=False)

        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True)

# --------------------------------------------- COMMON VIEW CLASSES -----------------------------------------------[A]


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
        if not HeadA:   # if HeadA (synchronous)
            a3.set_title('Post Production Status', fontsize=12, fontweight='bold')
        else:
            a3.set_title('Machine Live Status Analysis', fontsize=12, fontweight='bold')
        a3.pie([1, 7, 0, 5, 9, 6], shadow=True)

        # -------------------------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)

        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True)


class common_RF(ttk.Frame):     # PRODUCTION PARAM - ROLLER FORCE --------------------[1]
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=20)
        self.createWidgets()

    def createWidgets(self):
        # --------------------------------------------------------------[TODO if pMinMax:]
        f = Figure(figsize=(10, 4), dpi=100)
        f.subplots_adjust(left=0.071, bottom=0.057, right=0.99, top=0.998, wspace=0.193)
        a1 = f.add_subplot(1, 1, 1)

        # --------------------------------------------------------------[]
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        # a1.legend(loc='upper left')
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")

        # Define limits for Laser Power Control Plots -----------------------#
        a1.axhline(y=hMeanA, color="green", linestyle="-", linewidth=1)
        a1.axhspan(hLCLa, hUCLa, facecolor='#A9EF91', edgecolor='#A9EF91')      # Light Green
        # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
        a1.axhspan(hUCLa, hUSLa, facecolor='#8d8794', edgecolor='#8d8794')      # grey area
        a1.axhspan(hLSLa, hLCLa, facecolor='#8d8794', edgecolor='#8d8794')      # grey area
        # clean up when Mean line changes ---
        a1.axhspan(hUSLa, hUSLa+10, facecolor='#FFFFFF', edgecolor='#FFFFFF')
        a1.axhspan(hLSLa-10, hLSLa, facecolor='#FFFFFF', edgecolor='#FFFFFF')

        # Model data --------------------------------------------------[]
        a1.plot([1857, 848, 1984, 529, 1740, 1136, 1012, 723, 1791, 600])
        # -------------------------------------------------------------[]

        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)

        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True)


class common_CT(ttk.Frame):     # PRODUCTION PARAM - CELL TENSION --------------------[2]
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=20)
        self.createWidgets()

    def createWidgets(self):
        # --------------------------------------------------------------[]
        f = Figure(figsize=(10, 4), dpi=100)
        f.subplots_adjust(left=0.071, bottom=0.057, right=0.99, top=0.998, wspace=0.193)
        a1 = f.add_subplot(1, 1, 1)

        # --------------------------------------------------------------[]
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        # a1.legend(loc='upper left')
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")

        # Define limits for Laser Power Control Plots -----------------------#
        a1.axhline(y=hMeanB, color="green", linestyle="-", linewidth=1)
        a1.axhspan(hLCLb, hUCLb, facecolor='#A9EF91', edgecolor='#A9EF91')      # Light Green
        # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
        a1.axhspan(hUCLb, hUSLb, facecolor='#8d8794', edgecolor='#8d8794')      # grey area
        a1.axhspan(hLSLb, hLCLb, facecolor='#8d8794', edgecolor='#8d8794')      # grey area
        # clean up when Mean line changes ---
        a1.axhspan(hUSLb, hUSLb+10, facecolor='#FFFFFF', edgecolor='#FFFFFF')
        a1.axhspan(hLSLb-10, hLSLb, facecolor='#FFFFFF', edgecolor='#FFFFFF')

        # Model data --------------------------------------------------[]
        a1.plot([1857, 848, 1984, 529, 1740, 1136, 1012, 723, 1791, 600])
        # -------------------------------------------------------------[]

        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)

        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True)

# TODO - Incase of more process variable, enable this codefied block - Robbie Labs
class common_PA(ttk.Frame):     # PRODUCTION PARAM - SPARE PARAMETER A -------------[3]
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=20)
        self.createWidgets()

    def createWidgets(self):
        # --------------------------------------------------------------[]
        f = Figure(figsize=(10, 4), dpi=100)
        f.subplots_adjust(left=0.071, bottom=0.057, right=0.99, top=0.998, wspace=0.193)
        a1 = f.add_subplot(1, 1, 1)
        # --------------------------------------------------------------[]
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        # a1.legend(loc='upper left')
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")

        # Define limits for Laser Power Control Plots -----------------------#
        a1.axhline(y=hMeanc, color="green", linestyle="-", linewidth=1)
        a1.axhspan(hLCLc, hUCLc, facecolor='#A9EF91', edgecolor='#A9EF91')      # Light Green
        # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
        a1.axhspan(hUCLc, hUSLc, facecolor='#8d8794', edgecolor='#8d8794')      # grey area
        a1.axhspan(hLSLc, hLCLc, facecolor='#8d8794', edgecolor='#8d8794')      # grey area
        # clean up when Mean line changes ---
        a1.axhspan(hUSLc, hUSLc+10, facecolor='#FFFFFF', edgecolor='#FFFFFF')
        a1.axhspan(hLSLc-10, hLSLc, facecolor='#FFFFFF', edgecolor='#FFFFFF')

        # Model data --------------------------------------------------[]
        a1.plot([1857, 848, 1984, 529, 1740, 1136, 1012, 723, 1791, 600])
        # -------------------------------------------------------------[]

        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True
# ------------------------------------------------------


class common_PB(ttk.Frame):     # PRODUCTION PARAM - SPARE PARAMETER B --------------[4]
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=20)
        self.createWidgets()

    def createWidgets(self):
        # -------------------
        f = Figure(figsize=(10, 4), dpi=100)
        f.subplots_adjust(left=0.071, bottom=0.057, right=0.99, top=0.998, wspace=0.193)
        a1 = f.add_subplot(1, 1, 1)

        # --------------------------------------------------------------[]
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        # a1.legend(loc='upper left')
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")

        # Define limits for Laser Power Control Plots -----------------------#
        a1.axhline(y=hMeanD, color="green", linestyle="-", linewidth=1)
        a1.axhspan(hLCLd, hUCLd, facecolor='#A9EF91', edgecolor='#A9EF91')      # Light Green
        # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
        a1.axhspan(hUCLd, hUSLd, facecolor='#8d8794', edgecolor='#8d8794')      # grey area
        a1.axhspan(hLSLd, hLCLd, facecolor='#8d8794', edgecolor='#8d8794')      # grey area
        # clean up when Mean line changes ---
        a1.axhspan(hUSLd, hUSLd+10, facecolor='#FFFFFF', edgecolor='#FFFFFF')
        a1.axhspan(hLSLd-10, hLSLd, facecolor='#FFFFFF', edgecolor='#FFFFFF')

        # Model data --------------------------------------------------[]
        a1.plot([1857, 848, 1984, 529, 1740, 1136, 1012, 723, 1791, 600])
        # -------------------------------------------------------------[]

        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True

    # ------------------------------------------------- RIGHT HAND CONTROL PLOT -----------------------


class common_PC(ttk.Frame):  # PRODUCTION PARAM - SPARE PARAMETER C
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=1010, y=20)
        self.createWidgets()

    def createWidgets(self):
        # --------------------------------------------------------------[]
        f = Figure(figsize=(10, 4), dpi=100)
        f.subplots_adjust(left=0.06, bottom=0.057, right=0.99, top=0.99, wspace=0.193)
        a2 = f.add_subplot(1, 1, 1)

        # --------------------------------------------------------------[]
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        # a2.legend(loc='upper left')
        a2.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")

        # Define limits for Laser Angle Control Plots -----------------------#
        a2.axhline(y=hMeanE, color="green", linestyle="-", linewidth=1)
        a2.axhspan(hLCLe, hUCLe, facecolor='#A9EF91', edgecolor='#A9EF91')      # Light Green
        # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
        a2.axhspan(hUCLe, hUSLe, facecolor='#8d8794', edgecolor='#8d8794')     # grey area
        a2.axhspan(hLSLe, hLCLe, facecolor='#8d8794', edgecolor='#8d8794')    # grey area
        # clean up when Mean line changes ---
        a2.axhspan(hUSLe, hUSLe+0.005, facecolor='#FFFFFF', edgecolor='#FFFFFF')
        a2.axhspan(hLSLe-0.05, hLSLe, facecolor='#FFFFFF', edgecolor='#FFFFFF')

        # Model data --------------------------------------------------[]
        a2.plot([-1.78, -1.0, -0.8, -1.3, -0.89, -0.92, -1.2, -1.5, -1.6, -0.85])
        # -------------------------------------------------------------[]

        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True)
    # --------------------------------------------------


class common_PD(ttk.Frame):  # -- Defines tabbed production params common to QA parameters --[]
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=1010, y=20)
        self.createWidgets()

    def createWidgets(self):
        # -------------------
        f = Figure(figsize=(10, 4), dpi=100)
        f.subplots_adjust(left=0.06, bottom=0.057, right=0.99, top=0.99, wspace=0.193)
        a2 = f.add_subplot(1, 1, 1)

        # --------------------------------------------------------------[]
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        # a2.legend(loc='upper left')
        a2.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")

        # Define limits for Laser Angle Control Plots -----------------------#
        a2.axhline(y=hMeanF, color="green", linestyle="-", linewidth=1)
        a2.axhspan(hLCLf, hUCLf, facecolor='#A9EF91', edgecolor='#A9EF91')  # Light Green
        # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
        a2.axhspan(hUCLf, hUSLf, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
        a2.axhspan(hLSLf, hLCLf, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
        # clean up when Mean line changes ---
        a2.axhspan(hUSLf, hUSLf + 0.005, facecolor='#FFFFFF', edgecolor='#FFFFFF')
        a2.axhspan(hLSLf - 0.05, hLSLf, facecolor='#FFFFFF', edgecolor='#FFFFFF')

        # Model data --------------------------------------------------[]
        a2.plot([-1.78, -1.0, -0.8, -1.3, -0.89, -0.92, -1.2, -1.5, -1.6, -0.85])
        # -------------------------------------------------------------[]

        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True
# ------------------------------------------------------------------------------------------------------------------#

class rollerPressure(ttk.Frame):            # -- Defines the tabbed region for QA params - Roller Pressure --[]
    """ This application calculates the Mean/Std Dev and returns a value. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        # self.grid()
        self.place(x=10, y=10)
        self.createWidgets()

    def createWidgets(self):
        # Load Quality Historical Values -----------[]
        rpSize, rpgType, rpSspace, rpHL, rpAL, rpFO, rpParam1, rpParam2, rpParam3, rpParam4, rpParam5 = mq.decryptpProcessLim(
            WON, 'RP')
        # Break down each element to useful list ---------------[Roller Pressure]
        if rpHL and rpParam1 and rpParam2:  # Roller Pressure TODO - layer metrics to guide TCP01
            rpPerf = '$Pp_{k' + str(sSize) + '}$'  # Using estimated or historical Mean
            rplabel = 'Pp'
            # -------------------------------
            rpOne = rpParam1.split(',')                 # split into list elements
            rpTwo = rpParam1.split(',')
            dTaperp = rpOne[1].strip("' ")              # defined Tape Width
            dLayer = rpOne[10].strip("' ")              # Defined Tape Layer
            print(dTaperp)
            # Load historical limits for the process-------------#
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
            rpPerf = '$Cp_{k' + str(sSize) + '}$'    # Using Automatic group Mean
            rplabel = 'Cp'
        # ------------------------------------[End of Roller Pressure Abstraction]

        label = ttk.Label(self, text='['  ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Set subplot embedded properties ----------------------------------[]
        f = Figure(figsize=(25, 8), dpi=100)
        f.subplots_adjust(left=0.029, bottom=0.05, right=0.99, top=0.955, wspace=0.117, hspace=0.157)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 4, (1, 3))
        a2 = f.add_subplot(2, 4, (5, 7))
        a3 = f.add_subplot(2, 4, (4, 8))

        # --------------------------------------------------------------------------------------------[H]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minRP, YScale_maxRP = rpLSL - 8.5, rpUSL + 8.5       # Roller Pressuire
        sBar_minRP, sBar_maxRP = sLCLrp - 80, sUCLrp + 80             # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (smp_Sz + 3)                  # windows view = visible data points
        # ----------------------------------------------------------#
        # Initialise runtime limits
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        a1.set_title('Roller Pressure [XBar Plot]', fontsize=12, fontweight='bold')
        a2.set_title('Roller Pressure [S Plot]', fontsize=12, fontweight='bold')
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a1.legend(loc='upper left', title='XBar Plot')
        a2.legend(loc='upper right', title='SDev Plot')
        # ----------------------------------------------------------#
        a1.set_ylim([YScale_minRP, YScale_maxRP], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        a2.set_ylim([sBar_minRP, sBar_maxRP], auto=True)
        a2.set_xlim([window_Xmin, window_Xmax])

        # ----------------------------------------------------------[]
        a3.cla()
        a3.get_yaxis().set_visible(False)
        a3.get_xaxis().set_visible(False)

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

        # Statistical Feed -----------------------------------------[]
        a3.text(0.466, 0.945, 'Performance Feed - RP', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        a3.add_patch(rect1)
        a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)---------------------
        a3.text(0.145, 0.804, rplabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.658, '#Pp Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.650, 0.820, 'Ring ' + rplabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        a3.text(0.145, 0.403, rpPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring ' + rpPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
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
        def synchronousRP(rpSize, rpgType, fetchT):
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
                if not UsePLC_DBS:                              # Not Using PLC Data
                    import ArrayRP_sqlRLmethod as lq            # DrLabs optimization method
                    inProgress = True                           # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

                    # Get list of relevant SQL Tables using conn() --------------------[]
                    rpData = lq.sqlexec(rpSize, rpgType, qRP, tblID, fetchT)
                    if keyboard.is_pressed("Alt+Q"):            # Terminate file-fetch
                        qRP.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

                else:
                    inProgress = False                          # False for Real-time mode
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

        # ================== End of synchronous Method ==========================obal
        def asynchronousRP(db_freq):

            timei = time.time()  # start timing the entire loop
            UsePLC_DBS = pType  # Query Type

            # Call data loader Method---------------------------#
            rpData = synchronousRP(rpSize, rpgType, db_freq)  # data loading functions
            if UsePLC_DBS == 1:
                import rfVarPLC as qrf
                viz_cycle = 10
                # Call synchronous data function ---------------[]
                columns = vq.validColsPLCData()  # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(rpData, columns=columns)  # Include table data into python Dataframe
                RP = qrf.loadProcesValues(df1)  # Join data values under dataframe

            else:
                import rfVarSQL as qrf  # load SQL variables column names | rfVarSQL
                viz_cycle = 150
                g1 = qq.validCols('WS')  # Construct Data Column selSqlColumnsTFM.py
                df1 = pd.DataFrame(rpData, columns=g1)  # Import into python Dataframe
                RP = qrf.loadProcesValues(df1)  # Join data values under dataframe
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
            # Compute entire Process Capability ----------------------------------------#
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
            a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 3 Sigma span (Purple)
            a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minTT, sBar_maxTT -------[]
            # Define Legend's Attributes  ----
            a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
            a2.axhspan(sLCLrp, sUCLrp, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 1 Sigma Span
            a2.axhspan(sUCLrp, sBar_maxRP, facecolor='#CCCCFF', edgecolor='#CCCCFF')  # 1 Sigma above the Mean
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

            ani = FuncAnimation(f, asynchronousRP, frames=None, save_count=100, repeat_delay=None,
                                interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------[TODO MOVE TO LAST LINE]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True)  # ---------------------------------------------[]


class tapeTemp(ttk.Frame):      # -- Defines the tabbed region for QA param - Tape Temperature --[]
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        # Load Quality Historical Values -----------[]
        ttSize, ttgType, ttSspace, ttHL, ttAL, ttFO, ttParam1, ttParam2, ttParam3, ttParam4, ttParam5 = mq.decryptpProcessLim(
            WON, 'TT')
        # Break down each element to useful list ---------------[Tape Temperature]
        if ttHL and ttParam1 and ttParam2 and ttParam3 and ttParam4 and ttParam5:  #
            ttPerf = '$Pp_{k' + str(sSize) + '}$'  # Using estimated or historical Mean
            ttlabel = 'Pp'
            # -------------------------------
            One = ttParam1.split(',')                   # split into list elements
            Two = ttParam2.split(',')
            Thr = ttParam3.split(',')
            For = ttParam4.split(',')
            Fiv = ttParam5.split(',')
            # -------------------------------
            dTape1 = One[1].strip("' ")                 # defined Tape Width
            dTape2 = Two[1].strip("' ")                 # defined Tape Width
            dTape3 = Thr[1].strip("' ")                 # defined Tape Width
            dTape4 = For[1].strip("' ")                 # defined Tape Width
            dTape5 = Fiv[1].strip("' ")                 # defined Tape Width
            # --------------------------------
            dLayer1 = One[10].strip("' ")               # Defined Tape Layer
            dLayer2 = Two[10].strip("' ")
            dLayer3 = Thr[10].strip("' ")
            dLayer4 = For[10].strip("' ")
            dLayer5 = Fiv[10].strip("' ")
            # Load historical limits for the process----#
            if cpLayerNo == 1:                          # '22mm'|'18mm',  1-40 | 41+ TODO
                ttUCL = float(One[2].strip("' "))       # Strip out the element of the list
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
                ttUCL = float(Two[2].strip("' "))       # Strip out the element of the list
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
                ttUCL = float(Thr[2].strip("' "))       # Strip out the element of the list
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
                ttUCL = float(For[2].strip("' "))       # Strip out the element of the list
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
                ttUCL = float(Fiv[2].strip("' "))       # Strip out the element of the list
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
            ttPerf = '$Cp_{k' + str(sSize) + '}$'  # Using Automatic group Mean
            ttlabel = 'Cp'

        # ------------------------------------[End of Tape Temperature Abstraction]

        label = ttk.Label(self, text='['  ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Define Axes ---------------------#
        f = Figure(figsize=(25, 8), dpi=100)
        f.subplots_adjust(left=0.029, bottom=0.05, right=0.99, top=0.955, wspace=0.117, hspace=0.157)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 4, (1, 3))
        a2 = f.add_subplot(2, 4, (5, 7))
        a3 = f.add_subplot(2, 4, (4, 8))

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minTT, YScale_maxTT = ttLSL - 8.5, ttUSL + 8.5       # Roller Force
        sBar_minTT, sBar_maxTT = sLCLtt - 80, sUCLtt + 80           # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (int(ttSize) + 3)             # windows view = visible data points
        # ----------------------------------------------------------#
        # Initialise runtime limits
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        a1.set_title('Tape Temperature [XBar Plot]', fontsize=12, fontweight='bold')
        a2.set_title('Tape Temperature [S Plot]', fontsize=12, fontweight='bold')
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a1.legend(loc='upper left', title='XBar Plot')
        a2.legend(loc='upper right', title='SDev Plot')
        # ----------------------------------------------------------#
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

        # Statistical Feed -----------------------------------------[]
        a3.text(0.466, 0.945, 'Performance Feed - TT', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        a3.add_patch(rect1)
        a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)---------------------
        a3.text(0.145, 0.804, ttlabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.658, '#Pp Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.650, 0.820, 'Ring ' + ttlabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        a3.text(0.145, 0.403, ttPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring ' + ttPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
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
            import keyboard  # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                # print('Indefinite looping...')
                if not UsePLC_DBS:  # Not Using PLC Data
                    import ArrayRP_sqlRLmethod as lq        # DrLabs optimization method
                    inProgress = True                       # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

                    # Get list of relevant SQL Tables using conn() --------------------[]
                    ttData = lq.sqlexec(ttSize, ttgType, qRP, tblID, fetchT)
                    if keyboard.is_pressed("Alt+Q"):        # Terminate file-fetch
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
                    ttData = q.paramDataRequest(procID, ttSize, ttgType, fetch_no)

            return ttData

        # ================== End of synchronous Method ==========================
        def asynchronousTT(db_freq):

            timei = time.time()  # start timing the entire loop
            UsePLC_DBS = pType  # Query Type

            # Call data loader Method---------------------------#
            rpData = synchronousTT(ttSize, ttgType, db_freq)  # data loading functions
            if UsePLC_DBS == 1:
                import rfVarPLC as qrf
                viz_cycle = 10
                # Call synchronous data function ---------------[]
                columns = vq.validColsPLCData()  # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(rpData, columns=columns)  # Include table data into python Dataframe
                TT = qrf.loadProcesValues(df1)  # Join data values under dataframe

            else:
                import rfVarSQL as qrf  # load SQL variables column names | rfVarSQL
                viz_cycle = 150
                g1 = qq.validCols('WS')  # Construct Data Column selSqlColumnsTFM.py
                df1 = pd.DataFrame(rpData, columns=g1)  # Import into python Dataframe
                TT = qrf.loadProcesValues(df1)  # Join data values under dataframe
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
                                                                                           sdC, sdD, ttUSL, ttLSL,
                                                                                           ttUCL,
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

            ani = FuncAnimation(f, asynchronousTT, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True)


class substTemp(ttk.Frame):     # -- Defines the tabbed region for QA param - Substrate Temperature --[]
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        # Load Quality Historical Values -----------[]
        stSize, stgType, stSspace, stHL, stAL, stFO, stParam1, stParam2, stParam3, stParam4, stParam5 = mq.decryptpProcessLim(
            WON, 'ST')

        # Break down each element to useful list -----------[Substrate Temperature]
        if stHL and stParam1 and stParam2 and stParam3 and stParam4 and stParam5:
            stPerf = '$Pp_{k' + str(sSize) + '}$'  # Using estimated or historical Mean
            stlabel = 'Pp'
            # -------------------------------
            One = stParam1.split(',')  # split into list elements
            Two = stParam2.split(',')
            Thr = stParam3.split(',')
            For = stParam4.split(',')
            Fiv = stParam5.split(',')
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
            # Load historical limits for the process--------#
            if cpTapeW == dTape1 and cpLayerNo <= 1:        # '22mm'|'18mm',  1-40 | 41+
                stUCL = float(One[2].strip("' "))           # Strip out the element of the list
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
                stUCL = float(Two[2].strip("' "))           # Strip out the element of the list
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
                stUCL = float(Thr[2].strip("' "))           # Strip out the element of the list
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
                stUCL = float(For[2].strip("' "))           # Strip out the element of the list
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
                stUCL = float(Fiv[2].strip("' "))           # Strip out the element of the list
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
            stPerf = '$Cp_{k' + str(sSize) + '}$'           # Using Automatic group Mean
            stlabel = 'Cp'

        label = ttk.Label(self, text='['  ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Define Axes ---------------------#
        f = Figure(figsize=(25, 8), dpi=100)

        f.subplots_adjust(left=0.029, bottom=0.05, right=0.99, top=0.955, wspace=0.117, hspace=0.157)
        a1 = f.add_subplot(2, 4, (1, 3))
        a2 = f.add_subplot(2, 4, (5, 7))
        a3 = f.add_subplot(2, 4, (4, 8))

        # Declare Plots attributes --------------------------------[]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minST, YScale_maxST = stLSL - 8.5, stUSL + 8.5
        sBar_minST, sBar_maxST = sLCLst - 80, sUCLst + 80           # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (smp_Sz + 3)                  # windows view = visible data points
        # ----------------------------------------------------------#
        # Initialise runtime limits
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        a1.set_title('Substrate Temperature [XBar Plot]', fontsize=12, fontweight='bold')
        a2.set_title('Substrate Temperature [S Plot]', fontsize=12, fontweight='bold')
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a1.legend(loc='upper left', title='XBar Plot')
        a2.legend(loc='upper right', title='SDev Plot')
        # ----------------------------------------------------------#
        a1.set_ylim([YScale_minST, YScale_maxST], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        a2.set_ylim([sBar_minST, sBar_maxST], auto=True)
        a2.set_xlim([window_Xmin, window_Xmax])

        # ----------------------------------------------------------[]
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

        # Statistical Feed -----------------------------------------[]
        a3.text(0.466, 0.945, 'Performance Feed - ST', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        a3.add_patch(rect1)
        a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)---------------------
        a3.text(0.145, 0.804, stlabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.658, '#Pp Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.650, 0.820, 'Ring ' + stlabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        a3.text(0.145, 0.403, stPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring ' + stPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
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
                columns = vq.validColsPLCData()  # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(rpData, columns=columns)  # Include table data into python Dataframe
                ST = qrf.loadProcesValues(df1)  # Join data values under dataframe

            else:
                import rfVarSQL as qrf  # load SQL variables column names | rfVarSQL
                viz_cycle = 150
                g1 = qq.validCols('WS')  # Construct Data Column selSqlColumnsTFM.py
                df1 = pd.DataFrame(rpData, columns=g1)  # Import into python Dataframe
                ST = qrf.loadProcesValues(df1)  # Join data values under dataframe
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

            ani = FuncAnimation(f, asynchronousST, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True)


class windingSpeed(ttk.Frame):     # -- Defines the tabbed region for QA param - Substrate Temperature --[]
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        # --------------------------------------------------------------------[]
        wsSize, wsgType, wsSspace, wsHL, wsAL, wstFO, wsParam1, dud2, dud3, dud4, dud5 = mq.decryptpProcessLim(WON, 'WS')
        # Break down each element to useful list ----------------[Winding Speed]

        if wsHL and wsParam1:  # Roller Pressure TODO - layer metrics to guide TCP01
            wsPerf = '$Pp_{k' + str(sSize) + '}$'               # Using estimated or historical Mean
            wslabel = 'Pp'
            # -------------------------------
            wsOne = wsParam1.split(',')  # split into list elements
            dTapews = wsOne[1].strip("' ")               # defined Tape Width
            dLayer = wsOne[10].strip("' ")               # Defined Tape Layer

            # Load historical limits for the process------------#
            wsUCL = float(wsOne[2].strip("' "))          # Strip out the element of the list
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
            wsPerf = '$Cp_{k' + str(sSize) + '}$'  # Using Automatic group Mean
            wslabel = 'Cp'

        # ------------------------------------[End of Winding Speed Abstraction]

        label = ttk.Label(self, text='['  ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Set subplot embedded properties ----------------------------------[]
        f = Figure(figsize=(25, 8), dpi=100)
        f.subplots_adjust(left=0.029, bottom=0.05, right=0.99, top=0.955, wspace=0.117, hspace=0.157)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 4, (1, 3))
        a2 = f.add_subplot(2, 4, (5, 7))
        a3 = f.add_subplot(2, 4, (4, 8))

        # Declare Plots attributes ---------------------------------[]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minWS, YScale_maxWS = wsLSL - 8.5, wsUSL + 8.5       # Roller Force
        sBar_minWS, sBar_maxWS = sLCLws - 80, sUCLws + 80           # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (smp_Sz + 3)                  # windows view = visible data points
        # ----------------------------------------------------------#

        # Initialise runtime limits
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

        # Statistical Feed -----------------------------------------[]
        a3.text(0.466, 0.945, 'Performance Feed - WS', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        a3.add_patch(rect1)
        a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)---------------------
        a3.text(0.145, 0.804, wslabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.658, '#Pp Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.650, 0.820, 'Ring ' + wslabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        a3.text(0.145, 0.403, wsPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring ' + wsPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
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
        def synchronousWS(wsSize, wsgType, fetchT):
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
                    tgData = lq.sqlexec(wsSize, wsgType, qRP, tblID, fetchT)
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

            timei = time.time()  # start timing the entire loop
            UsePLC_DBS = pType  # Query Type

            # Call data loader Method---------------------------#
            wsData = synchronousWS(wsSize, wsgType, db_freq)  # data loading functions
            if UsePLC_DBS == 1:
                import rfVarPLC as qrf
                viz_cycle = 10
                # Call synchronous data function ---------------[]
                columns = vq.validColsPLCData()  # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(wsData, columns=columns)  # Include table data into python Dataframe
                WS = qrf.loadProcesValues(df1)  # Join data values under dataframe

            else:
                import rfVarSQL as qrf  # load SQL variables column names | rfVarSQL
                viz_cycle = 150
                g1 = qq.validCols('WS')  # Construct Data Column selSqlColumnsTFM.py
                df1 = pd.DataFrame(wsData, columns=g1)  # Import into python Dataframe
                WS = qrf.loadProcesValues(df1)  # Join data values under dataframe
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
            a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 3 Sigma span (Purple)
            a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minTT, sBar_maxTT -------[]
            # Define Legend's Attributes  ----
            a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
            a2.axhspan(sLCLws, sUCLws, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 1 Sigma Span
            a2.axhspan(sUCLws, sBar_maxWS, facecolor='#CCCCFF', edgecolor='#CCCCFF')  # 1 Sigma above the Mean
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

            ani = FuncAnimation(f, asynchronousWS, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True)


class tapeGap(ttk.Frame):       # -- Defines the tabbed region for QA param - Tape Gap Measurement --[]
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        # Load metrics from config -----------------------------------[Tape Gap]
        tgSize, tggType, tgSspace, tgHL, tgAL, tgtFO, tgParam1, dud2, dud3, dud4, dud5 = mq.decryptpProcessLim(WON, 'TG')

        # Break down each element to useful list ---------------------[Tape Gap]
        if tgHL and tgParam1:
            tgPerf = '$Pp_{k' + str(tgSize) + '}$'       # Estimated or historical Mean
            tglabel = 'Pp'
            # -------------------------------
            tgOne = tgParam1.split(',')                 # split into list elements
            dTapetg = tgOne[1].strip("' ")              # defined Tape Width
            dLayer = tgOne[10].strip("' ")              # Defined Tape Layer

            # Load historical limits for the process----#
            tgUCL = float(tgOne[2].strip("' "))         # Strip out the element of the list
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
        else:   # Computes Shewhart constants (Automatic Limits)
            tgUCL = 0
            tgLCL = 0
            tgMean = 0
            tgDev = 0
            sUCLtg = 0
            sLCLtg = 0
            tgUSL = 0
            tgLSL = 0
            tgPerf = '$Cp_{k' + str(sSize) + '}$'   # Using Automatic group Mean
            tglabel = 'Cp'

        # -------------------------------------------[End of Tape Gap]

        label = ttk.Label(self, text='['  ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Define Axes ---------------------#
        f = Figure(figsize=(25, 8), dpi=100)
        f.subplots_adjust(left=0.029, bottom=0.05, right=0.99, top=0.955, wspace=0.117, hspace=0.157)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 5, (1, 2))                            # xbar plot
        a2 = f.add_subplot(2, 5, (3, 4))                            # cumulative plot
        a3 = f.add_subplot(2, 5, (6, 7))                            # s bar plot
        a4 = f.add_subplot(2, 5, (8, 9))                            # cumulative contours
        a5 = f.add_subplot(2, 5, (5, 10))                           # CPk/PPk Feed

        # ----------------------------------------------------------[H]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minTG, YScale_maxTG = tgLSL - 8.5, tgUSL + 8.5       # Roller Force
        sBar_minTG, sBar_maxTG = sLCLtg - 80, sUCLtg + 80           # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (smp_Sz + 3)                  # windows view = visible data points
        # ----------------------------------------------------------#

        # Initialise runtime limits --------------------------------#
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
        a3.text(0.466, 0.945, 'Performance Feed - TS', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        a3.add_patch(rect1)
        a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)----------------[]
        a3.text(0.145, 0.804, tglabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.658, '#Pp Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.650, 0.820, 'Ring ' + tglabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)--------------[]
        a3.text(0.145, 0.403, tgPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring ' + tgPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        # -----------------------------------------------------------[]
        a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ----- Pipe Position and SMC Status -----
        a3.text(0.080, 0.090, 'Pipe Position: ' + pPos + '    Processing Layer #' + layer, fontsize=12, ha='left',
                transform=a3.transAxes)
        a3.text(0.080, 0.036, 'SMC Status: ' + eSMC, fontsize=12, ha='left', transform=a3.transAxes)

        # ---------------- EXECUTE SYNCHRONOUS METHOD -----------------------------#
        def synchronousTG(smp_Sz, smp_St, fetchT):
            fetch_no = str(fetchT)                                                 # entry value in string sql syntax

            # Obtain Volatile Data from PLC Host Server ---------------------------[]
            if not inUseAlready:                                                   # Load CommsPlc class once
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
            import keyboard                                                        # for temporary use

            # TODO ----------------------[]
            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                # print('Indefinite looping...')
                if not UsePLC_DBS:                                                      # Not Using PLC Data
                    import ArrayRP_sqlRLmethod as lq                                    # DrLabs optimization method
                    inProgress = True                                                   # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

                    # Get list of relevant SQL Tables using conn() --------------------[]
                    tgData = lq.sqlexec(smp_Sz, smp_St, qRP, tblID, fetchT)             # perform DB connections
                    if keyboard.is_pressed("Alt+Q"):                                    # Terminate file-fetch
                        qRP.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

                else:
                    inProgress = False                                                  # False for Real-time mode
                    print('\nSynchronous controller activated...')
                    if not sysRun:
                       sysRun, msctcp, msc_rt = wd.autoPausePlay()                      # Retrieve MSC from Watchdog
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
                    tgData = q.paramDataRequest(procID, smp_Sz, smp_St, fetch_no)

            return tgData
        # ================== End of synchronous Method ==========================

        def asynchronousTG(db_freq):

            timei = time.time()                                 # start timing the entire loop
            UsePLC_DBS = qType                                  # Query Type
            # declare asynchronous variables ------------------[]

            # Call data loader Method---------------------------#
            tgData = synchronousTG(smp_Sz, stp_Sz, db_freq)      # data loading functions

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
            # # Declare Plots attributes ------------------------------------------------------------[]
            # XBar Mean Plot
            a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
            a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')            # 3 Sigma span (Purple)
            a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')            # grey area
            a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minTG, sBar_maxTG -------[]
            # Define Legend's Attributes  ----
            a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
            a2.axhspan(dLCLd, dUCLd, facecolor='#F9C0FD', edgecolor='#F9C0FD')          # 1 Sigma Span
            a2.axhspan(dUCLd, sBar_maxTG, facecolor='#CCCCFF', edgecolor='#CCCCFF')     # 1 Sigma above the Mean
            a2.axhspan(sBar_minTG, dLCLd, facecolor='#CCCCFF', edgecolor='#CCCCFF')

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

            ani = FuncAnimation(f, asynchronousTG, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True)


# --------------------------------------------- CASCADE VIEW CLASSES -----------------------------------------------[]

class cascadeViews(ttk.Frame):          # Load common Cascade and all object in cascadeSwitcher() class
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.createWidgets()

    def createWidgets(self):
        label = ttk.Label(self, text="Monitoring: Critical Production Parameters", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        # Define Axes ---------------------#
        fig = Figure(figsize=(25, 12), dpi=100)   # 13
        # Attempt to auto screen size ---
        # fig = Figure(figsize=(self.winfo_screenwidth(), self.winfo_screenheight()), dpi=100)
        fig.subplots_adjust(left=0.03, bottom=0.02, right=0.99, top=0.976, hspace=0.14, wspace=0.195)
        if pMinMax:
            a1 = fig.add_subplot(1, 6, (1, 3))  # Roller Force X plot
            a2 = fig.add_subplot(1, 6, (4, 6))  # Cell Tension X plot

            # Declare Plots attributes -----------------------------------------[]
            a1.set_title('Roller Force [Min/Max Curve]', fontsize=12, fontweight='bold')
            a2.set_title('Cell Tension [Min/Max Curve]', fontsize=12, fontweight='bold')

        elif pContrl:
            a1 = fig.add_subplot(2, 5, (1, 2))          # Roller Force X plot
            a2 = fig.add_subplot(2, 5, (3, 4))          # Cell Tension X plot
            a3 = fig.add_subplot(2, 5, (6, 7))          # Roller Force S plot
            a4 = fig.add_subplot(2, 5, (8, 9))          # Cell Tension S plot
            a5 = fig.add_subplot(4, 5, (5, 20))         # Statistics Feed

            # Declare Plots attributes -----------------------------------------[]
            a1.set_title('Roller Force [XBar Plot]', fontsize=12, fontweight='bold')
            a3.set_title('Roller Force [SBar Plot]', fontsize=12, fontweight='bold')
            a2.set_title('Cell Tension [XBar Plot]', fontsize=12, fontweight='bold')
            a4.set_title('Cell Tension [SBar Plot]', fontsize=12, fontweight='bold')
            # Apply grid lines -----
            a1.grid(color="0.5", linestyle='-', linewidth=0.5)
            a3.grid(color="0.5", linestyle='-', linewidth=0.5)
            a2.grid(color="0.5", linestyle='-', linewidth=0.5)
            a4.grid(color="0.5", linestyle='-', linewidth=0.5)

            # Common properties -------------------------------------------------#
            a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
            a3.set_ylabel("Sample Deviation [" + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
            # ----------------------------
            # a1.legend(loc='upper left')
            # axp.legend(loc='upper left')

            # Define limits for Laser Power Control Plots -----------------------#
            a1.axhline(y=hMeanA, color="green", linestyle="-", linewidth=1)
            a1.axhspan(hLCLa, hUCLa, facecolor='#A9EF91', edgecolor='#A9EF91')  # Light Green
            # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
            a1.axhspan(hUCLa, hUSLa, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            a1.axhspan(hLSLa, hLCLa, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            # clean up when Mean line changes ---
            a1.axhspan(hUSLa, hUSLa + 10, facecolor='#FFFFFF', edgecolor='#FFFFFF')
            a1.axhspan(hLSLa - 10, hLSLa, facecolor='#FFFFFF', edgecolor='#FFFFFF')

            # Define limits for Cell Tension Control Plots -----------------------#
            a2.axhline(y=hMeanB, color="green", linestyle="-", linewidth=1)
            a2.axhspan(hLCLb, hUCLb, facecolor='#A9EF91', edgecolor='#A9EF91')  # Light Green
            # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
            a2.axhspan(hUCLb, hUSLb, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            a2.axhspan(hLSLb, hLCLb, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            # clean up when Mean line changes ---
            a2.axhspan(hUSLb, hUSLb + 0.005, facecolor='#FFFFFF', edgecolor='#FFFFFF')
            a2.axhspan(hLSLb - 0.05, hLSLb, facecolor='#FFFFFF', edgecolor='#FFFFFF')

            # Model data --------------------------------------------------[]
            a1.plot([1857, 848, 1984, 529, 1740, 1136, 1012, 723, 1791, 600])
            a2.plot([-1.78, -1.0, -0.8, -1.3, -0.89, -0.92, -1.2, -1.5, -1.6, -0.85])
            # -------------------------------------------------------------[]
            # Calibrate the rest of the Plots -----------------------------------#

            # Define limits for Roller Force XBar Plots -----------------------[A]
            a3.axhline(y=hMeanB, color="green", linestyle="-", linewidth=1)
            a3.axhspan(hLCLb, hUCLb, facecolor='#A9EF91', edgecolor='#A9EF91')  # Light Green
            # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
            a3.axhspan(hUCLb, hUSLb, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            a3.axhspan(hLSLb, hLCLb, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            # clean up when Mean line changes ---
            a3.axhspan(hUSLb, hUSLb + 10, facecolor='#FFFFFF', edgecolor='#FFFFFF')
            a3.axhspan(hLSLb - 10, hLSLb, facecolor='#FFFFFF', edgecolor='#FFFFFF')

            # Define limits for Tape Temp XBar Plots ---------------------------[B]
            a4.axhline(y=hMeand, color="green", linestyle="-", linewidth=1)
            a4.axhspan(hLCLd, hUCLd, facecolor='#A9EF91', edgecolor='#A9EF91')  # Light Green
            # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
            a4.axhspan(hUCLd, hUSLd, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            a4.axhspan(hLSLd, hLCLd, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            # clean up when Mean line changes ---
            a4.axhspan(hUSLd, hUSLd + 10, facecolor='#FFFFFF', edgecolor='#FFFFFF')
            a4.axhspan(hLSLd - 10, hLSLd, facecolor='#FFFFFF', edgecolor='#FFFFFF')

            # Statistical Feed --------------------------------[]:
            a5.cla()
            a5.get_yaxis().set_visible(False)
            a5.get_xaxis().set_visible(False)
            a5.text(0.466, 0.945, 'Process Performance Feed', fontsize=16, fontweight='bold', ha='center', va='center',
                    transform=a5.transAxes)
            # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
            rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
            rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
            a5.add_patch(rect1)
            a5.add_patch(rect2)
            # ------- Process Performance Pp (the spread)---------------------
            a5.text(0.145, 0.804, plabel, fontsize=12, fontweight='bold', ha='center', transform=a5.transAxes)
            a5.text(0.328, 0.658, '#Pp', fontsize=28, fontweight='bold', ha='center', transform=a5.transAxes)
            a5.text(0.650, 0.820, 'Ring ' + plabel + ' Data', fontsize=14, ha='left', transform=a5.transAxes)
            a5.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a5.transAxes)
            a5.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a5.transAxes)
            a5.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a5.transAxes)
            a5.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a5.transAxes)
            # ------- Process Performance Ppk (Performance)--------------------#
            a5.text(0.145, 0.403, PPerf, fontsize=12, fontweight='bold', ha='center', transform=a5.transAxes)
            a5.text(0.328, 0.282, '#Ppk', fontsize=28, fontweight='bold', ha='center', transform=a5.transAxes)
            a5.text(0.640, 0.420, 'Ring ' + PPerf + ' Data', fontsize=14, ha='left', transform=a5.transAxes)
            # -----------------------------------------------------------------#
            a5.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=a5.transAxes)
            a5.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=a5.transAxes)
            a5.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=a5.transAxes)
            a5.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=a5.transAxes)
            # ----- Pipe Position and SMC Status -----
            a5.text(0.080, 0.090, 'Pipe Position: ' + pPos + '    Processing Layer #' + layer, fontsize=12, ha='left',
                    transform=a5.transAxes)
            a5.text(0.080, 0.036, 'SMC Status: ' + eSMC, fontsize=12, ha='left', transform=a5.transAxes)

        # Update Canvas -----------------------------------------------------[]
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

# ====================================================== MAIN PIPELINE ===========================================[]
# qType = 0   # default play mode


def userMenu():     # listener, myplash
    print('Welcome to Dr Labs Multivariate SPC....')
    global sqlRO, metRO, root, HeadA, HeadB, vTFM, comboL, comboR, qType

    # splash = myplash
    # del splash                                  # Turn off Splash timer -----[]

    print('Timer Paused for GUI...')

    # inherit PID from Splash Screen and transfer back when Object closes
    print('\nUser Menu: Inherited PARENT ID#:', os.getppid())
    print('User Menu: Inherited CHILD ID#:', os.getpid())
    print('User Menu: New Object THREAD:', get_native_id())
    time.sleep(2)

    # --- call root ----
    # root = Tk()
    # root.wm_attributes('-topmost', True)  # '-topmost' | '-fullscreen'

    # for windows centralizing ---------[]
    window_height = 580     #1080
    window_width = 950      #1920

    root.title('Magma Synchronous SPC - ' + strftime("%a, %d %b %Y", gmtime()))
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Coordinates of the upper left corner of the window to make the window appear in the center
    x_cordinate = int((screen_width / 2) - (window_width / 2))
    y_cordinate = int((screen_height / 2) - (window_height / 2))
    root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
    # root.geometry("%dx%d" % (screen_width, screen_height))

    # canvas = autoResizableCanvas(root)
    # filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))
    icon1 = 'C:\\CuttingEdge\\SPC_ver12\\crb.png'
    # ----------------------------------------------------------------------------------------

    # Define volatile runtime variables -------------------[]
    svar1 = IntVar()

    sqlRO = False       # SQL server filed is read only
    metRO = False

    def clearFields():  # for SQL server credentials -------
        # clear the content of text entry box
        if sub_menu.entrycget(0, 'state') =='normal':
            seripSql.set('')
            Entry(pop, state='normal', textvariable=seripSql).place(x=86, y=60)
        else:
            seripPlc.set('')
            Entry(pop, state='normal', textvariable=seripPlc).place(x=86, y=60)
        sqlid.set('')
        uname.set('')
        autho.set('')

        # set initial variables or last known variables
        # Entry(pop, state='normal', textvariable=seripSql).place(x=86, y=60)
        Entry(pop, state='normal', textvariable=sqlid).place(x=86, y=100)
        Entry(pop, state='normal', textvariable=uname).place(x=330, y=60)
        Entry(pop, state='normal', textvariable=autho, show="*").place(x=330, y=100)

        sqlRO = True
        print('Read Only Field State:', sqlRO)
        return sqlRO

    # function to allow historical limits entry--------------------------------------------------------------[]
    def errorConfig():
        messagebox.showerror("Configuration:", "Enable Statistic on Two Parameters")

    def errorNote():
        messagebox.showerror('Error', 'Empty field(s)')
        return

    def successNote():
        messagebox.showinfo('Saved', 'Config Saved')
        return

    def save_pMetrics():  # Save historical Limits for Production Parameters
        print("\nSaving Production Constants..")
        grayOut = [e5, e6, e7, e8]  # set value entry field to read only
        for fld in grayOut:
            fld.config(state='readonly')
        e7.config(state='disabled')
        e8.config(state='disabled')
        mp.saveMetricspP(WON, sel_SS, sel_gT, sSta, sEnd, 0, 0, usepHL)  # Set limits for Quality parameters
        s_butt.config(state="disabled")  # disable safe button on entry

        return

    def clearMetrics():
        # clear the content of chart parameter using change settings button ---
        global e5, e6, e7, e8

        # pop = Toplevel(root)
        # pop.wm_attributes('-topmost', True)

        sSta.set('07:00:00')
        sEnd.set('17:00:00')
        e5 = Entry(pop, width=8, state='normal', textvariable=sSta)
        e5.place(x=290, y=10)  # Shift starts
        e6 = Entry(pop, width=8, state='normal', textvariable=sEnd)
        e6.place(x=290, y=40)  # Shift ends

        e7 = ttk.Combobox(pop, width=10, values=[" Select", "10", "15", "20", "23", "25", "30"], state="normal")
        e7.bind("<<ComboboxSelected>>", display_sel)
        e7.place(x=100, y=10)

        e8 = ttk.Combobox(pop, width=10, values=["SS-Domino", "GS-Discrete"], state="normal")
        e8.bind("<<ComboboxSelected>>", display_selection)
        e8.place(x=100, y=40)

        # repopulate with default values -----------#
        s_butt.config(state="normal")  # enable edit button (Sve Details) on entry
        mp.ppHLderivation(pop, gSize1, gSize2, xUCLLP, xLCLLP, xUCLLA, xLCLLA)

        metRO = True
        print('SQL Field State:', metRO)  # metric fields set to read only

        return metRO
    # ------------------------------

    def display_selection(event):
        global sel_gT

        # Get the selected value.
        sel_gT = e8.get()
        if sel_gT == "S-Domino":  # butterfly effect/small change
            messagebox.showinfo(message="Combines the rising/falling edges of previous subgroup",
                                title=f"{sel_gT} Group")
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
            messagebox.showinfo(message="Computed Mean with A3=0.975, B3=0.284, B4=1.716",
                                title=f"{sel_SS} Sample Size")
        elif sel_SS == "15":  # Unstable Domino
            messagebox.showinfo(message="Computed Mean with A3=0.789, B3=0.428, B4=1.572",
                                title=f"{sel_SS} Sample Size")
        elif sel_SS == "20":
            messagebox.showinfo(message="Computed Mean with A3=0.680, B3=0.510, B4=1.490",
                                title=f"{sel_SS} Sample Size")
        elif sel_SS == "23":
            messagebox.showinfo(message="Computed Mean with A3=0.633, B3=0.545, B4=1.455",
                                title=f"{sel_SS} Sample Size")
        elif sel_SS == "25":
            messagebox.showinfo(message="Computed Mean with A3=0.606, B3=0.565, B4=1.435",
                                title=f"{sel_SS} Sample Size")
        elif sel_SS == "30":
            messagebox.showinfo(message="Computed Mean with A3=0.553, B3=0.604, B4=1.396",
                                title=f"{sel_SS} Sample Size")
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
            usepHL = True  # Use production parameter historical limits
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

    def pConfigs():  # FIXME ------ Configuration page []
        global modal, pRP, pTT, pST, pWS, pTG

        # prevent parent window closure until 'Save settings' ---[]
        root.protocol("WM_DELETE_WINDOW", preventClose)  # prevent closure even when using (ALT + F4)
        # -------------------------------------------------------[]

        modal = Toplevel(root)
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

    def newMetricsConfig():  # This is a DNV Metric Configuration Lookup Table ------[]

        global pLmtA, sSta, sEnd, eStat, gSize1, gSize2, xUCLLP, xLCLLP, xUCLLA, xLCLLA, xUCLHT, xLCLHT, xUCLDL, \
            xLCLDL, xUCLDD, xLCLDD, xUCLOT, xLCLOT, hLmtA, pLmtB, minMax, ctrlS, shewhart, s_butt, sSta, sEnd, e5, e6, \
            dnv_butt, button2, pop

        pop = Toplevel(root)
        pop.wm_attributes('-topmost', True)

        # Define volatile runtime variables -------------------[]
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

        pLmtA, pLmtB, pLmtC, pLmtD, pLmtE, pLmtF = IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop), IntVar(
            pop), IntVar(pop)
        hLmtA, hLmtB, shewhart, Sample = IntVar(pop), IntVar(pop), IntVar(pop), StringVar(pop)
        minMax, ctrlS = IntVar(pop), IntVar(pop),

        # ------------------ Auto canvass configs -------[]
        y_start = 110
        y_incmt = 30
        # global pop, screen_h, screen_w, x_c, y_c
        # center object on the screen---
        pop.resizable(False, False)
        height = (95 + y_start + (y_incmt * 5))
        w, h = 520, height  # 450

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
        separator.place(relx=0.01, rely=0.21, relwidth=0.98, relheight=0.02)  # y=0.17
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
        separatorU.place(relx=0.33, rely=0.61, relwidth=0.65, relheight=0.01)  # y=7.3
        # ---------------------------------------------------------------------
        Label(pop, text='[DNV Quality Parameters]', font=("bold", 10)).place(x=10,
                                                                             y=(y_start + 5) + (y_incmt * 3))  # 320 | 7
        dnv_butt = Button(pop, text="Define Limits per Quality Parameter", wraplength=160, justify=CENTER, width=24,
                          height=3,
                          font=("bold", 12), command=pConfigs, state=cState)
        dnv_butt.place(x=260, y=3 + y_start + y_incmt * 4)  # 350 | 8

        p1 = Checkbutton(pop, text="Enable Historical DNV Limits", font=("bold", 10), variable=pLmtA, command=enQHL)
        p1.place(x=10, y=3 + y_start + y_incmt * 4)  # 353
        p2 = Checkbutton(pop, text="Use Shewhart's Auto Limits", font=("bold", 10), variable=pLmtB, command=enQAL)
        p2.place(x=10, y=y_start + y_incmt * 5)  # 373 | 9
        pLmtB.set(1)
        p3 = Checkbutton(pop, text="Enable Auto Fail-Over", font=("bold", 10), variable=shewhart, command=enAFO)
        p3.place(x=10, y=y_start + y_incmt * 6)  # 393 |10

        def display_selection(event):
            # Get the selected value.
            selection = e8.get()
            if selection == "S-Domino":  # butterfly effect/small change
                messagebox.showinfo(message="Combines the rising/falling edges of previous subgroup",
                                    title=f"{selection} Group")
            elif selection == "F-Discrete":
                messagebox.showinfo(message="Evaluates new subgroup samples in the order of index",
                                    title=f"{selection} Group")
            # print("The drop-down has been opened!")
            return

        def display_sel(event):
            # Get the selected value.
            selection = e7.get()
            if selection == "10":
                messagebox.showinfo(message="Computed Mean with A3=0.975, B3=0.284, B4=1.716",
                                    title=f"{selection} Sample Size")
            elif selection == "15":  # Unstable Domino
                messagebox.showinfo(message="Computed Mean with A3=0.789, B3=0.428, B4=1.572",
                                    title=f"{selection} Sample Size")
            elif selection == "20":
                messagebox.showinfo(message="Computed Mean with A3=0.680, B3=0.510, B4=1.490",
                                    title=f"{selection} Sample Size")
            elif selection == "23":
                messagebox.showinfo(message="Computed Mean with A3=0.633, B3=0.545, B4=1.455",
                                    title=f"{selection} Sample Size")
            elif selection == "25":
                messagebox.showinfo(message="Computed Mean with A3=0.606, B3=0.565, B4=1.435",
                                    title=f"{selection} Sample Size")
            elif selection == "30":
                messagebox.showinfo(message="Computed Mean with A3=0.553, B3=0.604, B4=1.396",
                                    title=f"{selection} Sample Size")
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
            gSize1.set(sSize)  # Group Size
            gSize2.set(gType)  # Group Type (1=Domino, 2=SemiDomino, 3=Discrete)
            sSta.set(sStart)
            sEnd.set(sStops)
        else:
            gSize1.set('30')
            gSize2.set('GS-Discrete')  # Group Type (1=Domino, 2=SemiDomino, 3=Discrete)
            sSta.set('07:00:00 ')
            sEnd.set('01:00:00 ')

        # unpack convoluted elements into list -[A]
        if pParam1:
            pOne = pParam1.split(',')  # split into list elements
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
            pTwo = pParam2.split(',')  # split into list elements
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

            e7 = ttk.Combobox(pop, width=10, values=[" Select Size", "10", "15", "20", "23", "25", "30"],
                              state="disabled")
            e7.bind("<<ComboboxSelected>>", display_sel)
            e7.current(0)  # set default choice
            e7.place(x=100, y=10)

            e8 = ttk.Combobox(pop, width=10, values=["SS-Domino", "GS-Discrete"], state="disabled")
            e8.bind("<<ComboboxSelected>>", display_selection)
            e8.current(0)  # set default choice to first index
            e8.place(x=100, y=40)
            # --------------------------------------------------- [Shift information]
            e5 = Entry(pop, width=8, textvariable=sSta, state="readonly")
            e5.place(x=290, y=10)
            e6 = Entry(pop, width=8, textvariable=sEnd, state="readonly")
            e6.place(x=290, y=40)

            # # Add isolation button
            button2 = Button(pop, text="Edit Stats Properties", bg="red", fg="white", state="disabled",
                             command=clearMetrics)
            button2.place(x=370, y=35)  # place(x=520, y=47)

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
        minMax.set(1)  # Set default Plot values to Min/Max Plot
        p4.place(x=10, y=y_start + y_incmt * 2)  # 6
        p4 = Checkbutton(pop, text="Plot Control Chart", font=("bold", 10), variable=ctrlS, command=plotCChart)
        p4.place(x=190, y=y_start + y_incmt * 2)  # 6
        # ------------------------------ # TODO ---- command=saveMetricRP)
        s_butt = Button(pop, text="Save Details", fg="black", state=sbutton, command=save_pMetrics)
        s_butt.place(x=410, y=5 + y_start + y_incmt * 2)  # 295 now 2
        # --------------------------------
        button5 = Button(pop, text="Exit Settings", command=pop.destroy)
        button5.place(x=410, y=22 + y_start + y_incmt * 6)  # 400 nowe 2
        # pop.mainloop()
    # ------------------------ Line 2604

    def errorNoServer():
        messagebox.showerror('dB Server', 'Server offline or No connection')
        return

    def pingError():
        messagebox.showerror('OSI layer Error', 'Network Error or Server offline..')
        return

    def errorChoice():
        messagebox.showerror('Warning - Display Modes', 'Invalid request, no active Visualisation found.')
        return

    def errorSelection():
        messagebox.showerror('Warning - Runtime', 'No active Runtime Process')
        return

    def runtimeChange():
        messagebox.showerror('Invalid Change', 'Stop the active Runtime before new selection')
        return

    def errorNoconnect():
        messagebox.showerror("Warning - Data Disconnect", "Invalid request, no active connection(s) found.")

    def hostConnect():
        messagebox.showinfo('Host Connection', 'Connection is successful!')
        return

    def saveSQLconfig():
        import loadSQLConfig as to
        if sub_menu.entrycget(0, 'state') == 'normal':
            ct1 = seripSql.get()
        else:
            ct1 = seripPlc.get()
        ct2 = sqlid.get()
        ct3 = uname.get()
        ct4 = autho.get()
        print('Variables:', ct1, ct2, ct3, ct4)
        if ct1 == "" or ct2 == "" or ct3 == "" or ct4 == "":
            errorNote()  # response to save button when entry field is empty
            print('Empty field...')

        else:
            to.writeSQLconfig(ct1, ct2, ct3, ct4)  # save into text file
            successNote()
        # Condition for saving entries ---------------[]
        Entry(pop, state='disabled').place(x=86, y=60)
        Entry(pop, state='disabled').place(x=86, y=100)
        Entry(pop, state='disabled').place(x=330, y=60)
        Entry(pop, state='disabled').place(x=330, y=100)
        pop.destroy()
        # pop.grab_release()
        return

    # Define function for user selection on hitorical model and schewhart model --------------------[]
    def en_button():                    # Do a toggle from Shewhart Model to enforce single choice --[]
        if optm1.get():
            hLmt.set(0)
            optm2.set(0)
        else:
            # hLmt.set(1)
            optm1.set(0)

    def en_limits():                    # Do a toggle from Shewhart Model to enforce single choice --[]
        if optm2.get():
            hLmt.set(1)
            optm1.set(0)
        else:
            optm1.set(0)
            optm2.set(0)

    # Define function for user selection on Parameter Monitoring -----------------------------------[]
    def monitorA():
        swA()                           # Call label switch func
        if lPwr.get():                  # Allow complementary Parameter (LA)
            lPwr.set(1)
            hoTens.set(0)
            dcLoad.set(0)
            dDispl.set(0)
        else:
            lPwr.set(0)

    def monitorB():
        swB()                           # Call label switch func
        if lAng.get():                  # Allow complementary Parameter (LP)
            lAng.set(1)                 # comment out to allow one selection at a time
            hoTens.set(0)
            dcLoad.set(0)
            dDispl.set(0)
        else:
            lAng.set(0)

    # ------------- Additional functional module for distribution selection ------------------------
    def monitorC():
        swA()
        if hoTens.get():
            lPwr.set(0)
            lAng.set(0)
            if dcLoad.get() == 0 and dDispl.get() != 0:
                hoTens.set(1)
            elif dcLoad.get() != 0 and dDispl.get() == 0:
                hoTens.set(1)
            elif dcLoad.get() != 0 and dDispl.get() != 0:
                errorConfig()
                hoTens.set(0)
        else:
            hoTens.set(0)
        return

    def monitorD():
        swB()
        if dcLoad.get():
            lPwr.set(0)
            lAng.set(0)
            if hoTens.get() == 0 and dDispl.get() != 0:
                dcLoad.set(1)
            elif hoTens.get() != 0 and dDispl.get() == 0:
                dcLoad.set(1)
            elif hoTens.get() != 0 and dDispl.get() != 0:
                errorConfig()
                dcLoad.set(0)
        else:
            dcLoad.set(0)
        return

    def monitorE():     # Dancer Displacement ----
        swB()
        if dDispl.get():
            lPwr.set(0)
            lAng.set(0)
            if dcLoad.get() == 0 and hoTens.get() != 0:
                dDispl.set(1)
            elif dcLoad.get() != 0 and hoTens.get() == 0:
                dDispl.set(1)
            elif dcLoad.get() != 0 and hoTens.get() != 0:
                errorConfig()
                dDispl.set(0)
        else:
            dDispl.set(0)
        return


    def cseRF():
        pass

    def csdRF():
        pass

    def cseTT():
        pass

    def csdTT():
        pass

    def cseST():
        pass

    def csdST():
        pass

    def cseTG():
        pass

    def csdTG():
        pass

    def cseLP():
        pass

    def csdLP():
        pass

    def cseLA():
        pass

    def csdLA():
        pass

    # ----------------------------------------------------------------
    def enableStats():
        if eStat.get():
            if lPwr.get() != 0 and lAng.get() != 0:
                eStat.set(1)
            elif hoTens.get() != 0 and dcLoad.get() != 0 or dDispl.get() != 0:
                eStat.set(1)
            else:
                print('Select Two Parameter for Statistical consideration..')
                errorConfig()
                eStat.set(0)
        else:
            eStat.set(0)
        return

    def metricsConfig():
        global pop, metRO, xUCLa, xLCLa, xUCLb, xLCLb, xUCLc, xLCLc, sSta, sEnd, lPwr, lAng, eStat, optm1, optm2, e8,\
            xUCLd, xLCLd, XBarMa, SBarMa, XBarMb, SBarMb, XBarMc, SBarMc, XBarMd, SBarMd, hLmt, gSize1, gSize2, e7,\
            xUCLf, xLCLf, xUCLg, xLCLg, BarMf, SBarMf, BarMg, SBarMg, hoTens, dcLoad, dDispl, swA, swB, seRF, sdRF, \
            seTT, sdTT, seST, sdST, seTG, sdTG, seLP, sdLP, seLA, sdLA

        # newLabel = '??'
        # modal = Toplevel(pop)
        pop = Toplevel(root)
        pop.wm_attributes('-topmost', True)

        # Define and initialise essential popup variables -----------------------------------------
        xUCLa, xLCLa, sUCLa, sLCLa = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
        xUCLb, xLCLb, sUCLb, sLCLb = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
        xUCLc, xLCLc, sUCLc, sLCLc = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
        xUCLd, xLCLd, sUCLd, sLCLd = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
        # -----------------------------------------------
        xUCLf, xLCLf, sUCLf, sLCLf = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
        xUCLg, xLCLg, sUCLg, sLCLg = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)

        # --------------- Additional Prod Parameters ----
        seRF, sdRF, seTT, sdTT = IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop)
        seST, sdST, seTG, sdTG = IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop)
        seLP, sdLP, seLA, sdLA = IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop)
        hoTens, dcLoad, dDispl = IntVar(pop), IntVar(pop), IntVar(pop)

        sSta, sEnd, gSize1, gSize2 = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
        lPwr, lAng, eStat, optm1, optm2 = IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop)

        XBarMa, SBarMa, hLmt, Sample = StringVar(pop), StringVar(pop), IntVar(pop), StringVar(pop)
        XBarMb, SBarMb, XBarMc, SBarMc = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
        XBarMd, SBarMd = StringVar(pop), StringVar(pop)
        XBarMf, SBarMf, XBarMg, SBarMg = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
        print('State:', sqlRO)

        # global pop, screen_h, screen_w, x_c, y_c
        # center object on the screen---
        pop.resizable(False, False)
        w, h = 660, 420
        pop.title('Setting Chart Parameters')
        screen_w = pop.winfo_screenwidth()
        screen_h = pop.winfo_screenheight()
        x_c = int((screen_w / 2) - (w / 2))
        y_c = int((screen_h / 2) - (h / 2))
        pop.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))

        # creating labels and positioning them on the grid --------[]
        Label(pop, text='Size').place(x=10, y=50)
        Label(pop, text='Type').place(x=133, y=50)
        Label(pop, text='Shift @').place(x=278, y=50)
        Label(pop, text='Ends @').place(x=400, y=50)

        # --------------------------------------------------------[]
        separatorU = ttk.Separator(pop, orient='horizontal')
        separatorU.place(relx=0.01, rely=0.230, relwidth=0.30, relheight=0.01)
        separatorLR = ttk.Separator(pop, orient='horizontal')
        separatorLR.place(relx=0.60, rely=0.230, relwidth=0.39, relheight=0.01)

        Label(pop, text='Historical Limits [Quality Parameters]', font=("bold", 10)).place(x=160, y=80)
        Label(pop, text='Distribution').place(x=550, y=80)
        # Obtain historical limits of respective processes from User #

        # ----------------------------------------[Roller Force]
        Label(pop, text='UCL-RF').place(x=10, y=110)
        Label(pop, text='LCL-RF').place(x=138, y=110)

        Label(pop, text='X\u033FLine :').place(x=278, y=110)
        Label(pop, text='S\u0305Line :').place(x=400, y=110)

        # ----------------------------------------[Tape Temp]
        Label(pop, text='UCL-TT').place(x=10, y=140)
        Label(pop, text='LCL-TT').place(x=138, y=140)
        Label(pop, text='X\u033FLine :').place(x=278, y=140)
        Label(pop, text='S\u0305Line :').place(x=400, y=140)

        # -----------------------------------------[Temp Delta]
        Label(pop, text='UCL-DT').place(x=10, y=170)
        Label(pop, text='LCL-DT').place(x=138, y=170)
        Label(pop, text='X\u033FLine :').place(x=278, y=170)
        Label(pop, text='S\u0305Line :').place(x=400, y=170)

        # -----------------------------------------[Tape Gap]
        Label(pop, text='UCL-TG').place(x=10, y=200)
        Label(pop, text='LCL-TG').place(x=138, y=200)
        Label(pop, text='X\u033FLine :').place(x=278, y=200)
        Label(pop, text='S\u0305Line :').place(x=400, y=200)

        # ------------------------------------[Multiple options: Laser Power (M)]
        def swA():
            global newLabelA
            if lPwr.get():
                newLabelA = 'LP'
                print('Laser Power Selected..')
            elif hoTens.get():
                newLabelA = 'HT'
                print('H/O Tension Selected..')
            else:
                newLabelA = '???'
            Label(pop, text='UCL-' + newLabelA).place(x=10, y=290)
            Label(pop, text='LCL-' + newLabelA).place(x=138, y=290)
        Label(pop, text='UCL-???').place(x=10, y=290)        # GUI Illusion
        Label(pop, text='LCL-???').place(x=138, y=290)       # GUI Illusion
        Label(pop, text='X\u033FLine :').place(x=278, y=290)
        Label(pop, text='S\u0305Line :').place(x=400, y=290)

        # ------------------------------------[Laser Angle (M)]
        def swB():
            global newLabelB
            if lAng.get():
                newLabelB = 'LA'
                print('Laser Angle Selected..')
            elif dcLoad.get():
                newLabelB = 'DL'
                print('Dancer Load Selected..')
            elif dDispl.get():
                newLabelB = 'DD'
                print('Dancer Displacement Selected..')
            else:
                newLabelB = '???'
            Label(pop, text='UCL-' + newLabelB).place(x=10, y=320)
            Label(pop, text='LCL-' + newLabelB).place(x=138, y=320)
        Label(pop, text='UCL-???').place(x=10, y=320)        # GUI Illusion
        Label(pop, text='LCL-???').place(x=138, y=320)       # GUI Illusion
        Label(pop, text='X\u033FLine :').place(x=278, y=320)
        Label(pop, text='S\u0305Line :').place(x=400, y=320)

        # set initial variables or last known variables
        # Set default values --------------------------
        XBarMa.set('350.0')         # 352.1102
        SBarMa.set('17.50')         # 22.4268
        XBarMb.set('350.0')         # 352.1102
        SBarMb.set('17.50')         # 22.4268
        XBarMc.set('350.0')         # 352.1102
        SBarMc.set('17.50')         # 22.4268
        XBarMd.set('350.0')         # 352.1102
        SBarMd.set('17.50')         # 22.4268
        XBarMf.set('350.0')         # 352.1102
        SBarMf.set('17.50')         # 22.4268
        XBarMg.set('350.0')         # 352.1102
        SBarMg.set('17.50')         # 22.4268

        xUCLa.set('361.90')         # 364.6894
        xLCLa.set('338.10')         # 343.0816
        xUCLb.set('361.90')         # 364.6894
        xLCLb.set('338.10')         # 343.0816
        xUCLc.set('361.90')         # 364.6894
        xLCLc.set('338.10')         # 343.0816
        xUCLd.set('361.90')         # 364.6894
        xLCLd.set('338.10')         # 343.0816
        xUCLf.set('361.90')         # 364.6894
        xLCLf.set('338.10')         # 343.0816
        xUCLg.set('361.90')         # 364.6894
        xLCLg.set('338.10')         # 343.0816

        sUCLa.set('0')
        sLCLa.set('0')
        sUCLb.set('0')
        sLCLb.set('0')
        sUCLc.set('0')
        sLCLc.set('0')
        sUCLd.set('0')
        sLCLd.set('0')
        sUCLf.set('0')
        sLCLf.set('0')
        sUCLg.set('0')
        sLCLg.set('0')

        sSta.set('07:00:00')
        sEnd.set('17:00:00')
        gSize1.set('20')            # Group Size
        gSize2.set('03')            # Group Type (1=Domino, 2=SemiDomino, 3=Discrete)
        lPwr.set(0)
        hLmt.set(0)
        optm1.set(1)
        optm2.set(0)

        # Set default distribution for each listed Process ------[]
        sdRF.set(1)                 # 343.0816
        sdTT.set(1)
        sdST.set(1)
        sdTG.set(1)
        sdLP.set(1)
        sdLA.set(1)

        # ------------------------------------------------------
        separatorL = ttk.Separator(pop, orient='horizontal')
        separatorL.place(relx=0.01, rely=0.590, relwidth=0.39, relheight=0.01)
        separatorR = ttk.Separator(pop, orient='horizontal')
        separatorR.place(relx=0.60, rely=0.590, relwidth=0.39, relheight=0.01)

        Label(pop, text='Critical Production Parameters', font=("bold", 10)).place(x=240, y=230)
        Checkbutton(pop, text="Laser Power", variable=lPwr, command=monitorA).place(x=25, y=255)
        Checkbutton(pop, text="Laser Angle", variable=lAng, command=monitorB).place(x=125, y=255)
        # ------------------------------------------------------
        Checkbutton(pop, text="H/O Tension", variable=hoTens, command=monitorC).place(x=225, y=255)
        Checkbutton(pop, text="Dancer Load", variable=dcLoad, command=monitorD).place(x=325, y=255)
        Checkbutton(pop, text="Displacement", variable=dDispl, command=monitorE).place(x=425, y=255)
        # ------------------------------------------------------
        Checkbutton(pop, text="Enable Stats", variable=eStat, command=enableStats).place(x=525, y=255)

        c1 = Checkbutton(pop, text="Enable Historical Limits", width=20, font=("bold", 12), variable=hLmt, command=klr)
        c1.place(x=15, y=8)
        # ------------------
        c2 = Checkbutton(pop, text='Enable Automatic Limits', width=20, font=("bold", 12), variable=optm1, command=en_button)
        c2.place(x=230, y=8)
        # ------------------
        c2 = Checkbutton(pop, text='Enable Failover', width=20, font=("bold", 12), variable=optm2, command=en_limits)
        c2.place(x=430, y=8)

        if not metRO:
            # TODO --------------------------------------------------------[]

            e7 = ttk.Combobox(pop, width=8, values=[" Select", "10", "15", "20", "23", "25", "30"], state="disabled")
            e7.bind("<<ComboboxSelected>>", display_sel)
            e7.current(0)  # set default choice
            e7.place(x=40, y=50)

            e8 = ttk.Combobox(pop, width=10, values=["SS-Domino", "GS-Discrete"], state="disabled")
            e8.bind("<<ComboboxSelected>>", display_selection)
            e8.current(0)  # set default choice to first index
            e8.place(x=172, y=50)
            # --------------------------------------------------- [Shift information]
            e5 = Entry(pop, width=8, textvariable=sSta, state="readonly")
            e5.place(x=325, y=50)
            e6 = Entry(pop, width=8, textvariable=sEnd, state="readonly")
            e6.place(x=450, y=50)
            # Add isolation button
            button2 = Button(pop, text="Amend Properties", command=clearMetrics, bg="red", fg="white")
            button2.place(x=520, y=47)

            # Declare variable arrays ----------------------------[Roller Force]
            a1a = Entry(pop, width=8, textvariable=xUCLa, state="readonly")
            a1a.place(x=65, y=110)
            a2a = Entry(pop, width=8, textvariable=xLCLa, state="readonly")
            a2a.place(x=190, y=110)

            a3a = Entry(pop, width=8, textvariable=XBarMa, state="readonly")
            a3a.place(x=325, y=110)
            a4a = Entry(pop, width=8, textvariable=SBarMa, state="readonly")
            a4a.place(x=447, y=110)
            Checkbutton(pop, text="SE", variable=seRF, command=cseRF).place(x=550, y=110)  # cstat, UseSE
            Checkbutton(pop, text="SD", variable=sdRF, command=csdRF).place(x=600, y=110)

            # ------------- DNV Requirements ----------------[Tape Temperature]
            b1b = Entry(pop, width=8, textvariable=xUCLb, state="readonly")
            b1b.place(x=65, y=140)
            b2b = Entry(pop, width=8, textvariable=xLCLb, state="readonly")
            b2b.place(x=190, y=140)

            b3b = Entry(pop, width=8, textvariable=XBarMb, state="readonly")
            b3b.place(x=325, y=140)
            b4b = Entry(pop, width=8, textvariable=SBarMb, state="readonly")
            b4b.place(x=447, y=140)
            Checkbutton(pop, text="SE", variable=seTT, command=cseTT).place(x=550, y=140)  # cstat, UseSE
            Checkbutton(pop, text="SD", variable=sdTT, command=csdTT).place(x=600, y=140)

            # ------------ DNV Requirements ---------------[Temperature Substrate]
            c1b = Entry(pop, width=8, textvariable=xUCLc, state="readonly")
            c1b.place(x=65, y=170)
            c2b = Entry(pop, width=8, textvariable=xLCLc, state="readonly")
            c2b.place(x=190, y=170)
            c3b = Entry(pop, width=8, textvariable=XBarMc, state="readonly")
            c3b.place(x=325, y=170)
            c4b = Entry(pop, width=8, textvariable=SBarMc, state="readonly")
            c4b.place(x=447, y=170)
            Checkbutton(pop, text="SE", variable=seST, command=cseST).place(x=550, y=170)  # cstat, UseSE
            Checkbutton(pop, text="SD", variable=sdST, command=csdST).place(x=600, y=170)

            # -----------------------------------------[Tape Gap Measurement]
            a1b = Entry(pop, width=8, textvariable=xUCLd, state="readonly")
            a1b.place(x=65, y=200)
            a2b = Entry(pop, width=8, textvariable=xLCLd, state="readonly")
            a2b.place(x=190, y=200)
            a3b = Entry(pop, width=8, textvariable=XBarMd, state="readonly")
            a3b.place(x=325, y=200)
            a4b = Entry(pop, width=8, textvariable=SBarMd, state="readonly")
            a4b.place(x=447, y=200)
            Checkbutton(pop, text="SE", variable=seTG, command=cseTG).place(x=550, y=200)  # cstat, UseSE
            Checkbutton(pop, text="LN", variable=sdTG, command=csdTG).place(x=600, y=200)

            # -----------------------------------------[Laser Power (Monitor)]
            a1d = Entry(pop, width=8, textvariable=xUCLf, state="readonly")
            a1d.place(x=65, y=290)
            a2d = Entry(pop, width=8, textvariable=xLCLf, state="readonly")
            a2d.place(x=190, y=290)
            a3d = Entry(pop, width=8, textvariable=XBarMf, state="readonly")
            a3d.place(x=325, y=290)
            a4d = Entry(pop, width=8, textvariable=SBarMf, state="readonly")
            a4d.place(x=447, y=290)
            Checkbutton(pop, text="SE", variable=seLP, command=cseLP).place(x=550, y=290)  # cstat, UseSE
            Checkbutton(pop, text="SD", variable=sdLP, command=csdLP).place(x=600, y=290)

            # --------------------------------------[Laser Angle Measurement]
            a1d = Entry(pop, width=8, textvariable=xUCLg, state="readonly")
            a1d.place(x=65, y=320)
            a2d = Entry(pop, width=8, textvariable=xLCLg, state="readonly")
            a2d.place(x=190, y=320)
            a3d = Entry(pop, width=8, textvariable=XBarMg, state="readonly")
            a3d.place(x=325, y=320)
            a4d = Entry(pop, width=8, textvariable=SBarMg, state="readonly")
            a4d.place(x=447, y=320)
            Checkbutton(pop, text="SE", variable=seLA, command=cseLA).place(x=550, y=320)  # cstat, UseSE
            Checkbutton(pop, text="SD", variable=sdLA, command=csdLA).place(x=600, y=320)

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
            e5.place(x=325, y=50)
            e6 = Entry(pop, width=8, textvariable=sEnd, state="normal")
            e6.place(x=450, y=50)

            # Declare variable arrays -------------------------[Roller Force]
            a1a = Entry(pop, width=8, textvariable=xUCLa, state="normal")
            a1a.place(x=65, y=110)
            a2a = Entry(pop, width=8, textvariable=xLCLa, state="normal")
            a2a.place(x=190, y=110)
            a3a = Entry(pop, width=8, textvariable=XBarMa, state="normal")
            a3a.place(x=325, y=110)
            a4a = Entry(pop, width=8, textvariable=SBarMa, state="normal")
            a4a.place(x=447, y=110)

            # ------------- DNV Requirements -------------[Tape Temperature]
            b1b = Entry(pop, width=8, textvariable=xUCLb, state="normal")
            b1b.place(x=65, y=140)
            b2b = Entry(pop, width=8, textvariable=xLCLb, state="normal")
            b2b.place(x=190, y=140)
            b3b = Entry(pop, width=8, textvariable=XBarMb, state="normal")
            b3b.place(x=325, y=140)
            b4b = Entry(pop, width=8, textvariable=SBarMb, state="normal")
            b4b.place(x=447, y=140)
            # ------------ DNV Requirements -------------[Delta Temperature]
            c1b = Entry(pop, width=8, textvariable=xUCLc, state="normal")
            c1b.place(x=65, y=170)
            c2b = Entry(pop, width=8, textvariable=xLCLc, state="normal")
            c2b.place(x=190, y=170)
            c3b = Entry(pop, width=8, textvariable=XBarMc, state="normal")
            c3b.place(x=325, y=170)
            c4b = Entry(pop, width=8, textvariable=SBarMc, state="normal")
            c4b.place(x=447, y=170)
            # ---------------------------------------[Tape Gap Measurements]
            a1b = Entry(pop, width=8, textvariable=xUCLd, state="normal")
            a1b.place(x=65, y=200)
            a2b = Entry(pop, width=8, textvariable=xLCLd, state="normal")
            a2b.place(x=190, y=200)
            a3b = Entry(pop, width=8, textvariable=XBarMd, state="normal")
            a3b.place(x=325, y=200)
            a4b = Entry(pop, width=8, textvariable=SBarMd, state="normal")
            a4b.place(x=447, y=200)

            # ------------------------------------[Laser Power (Monitoring)]
            a1d = Entry(pop, width=8, textvariable=xUCLf, state="normal")
            a1d.place(x=65, y=290)
            a2d = Entry(pop, width=8, textvariable=xLCLf, state="normal")
            a2d.place(x=190, y=290)
            a3d = Entry(pop, width=8, textvariable=XBarMf, state="normal")
            a3d.place(x=325, y=290)
            a4d = Entry(pop, width=8, textvariable=SBarMf, state="normal")
            a4d.place(x=447, y=290)
            # -----------------------------------[Laser Angle (Monitoring)]
            a1d = Entry(pop, width=8, textvariable=xUCLg, state="normal")
            a1d.place(x=65, y=320)
            a2d = Entry(pop, width=8, textvariable=xLCLg, state="normal")
            a2d.place(x=190, y=320)
            a3d = Entry(pop, width=8, textvariable=XBarMg, state="normal")
            a3d.place(x=325, y=320)
            a4d = Entry(pop, width=8, textvariable=SBarMg, state="normal")
            a4d.place(x=447, y=320)

        # Add Button for making selection -------------------------------
        button1 = Button(pop, text="Save All Settings", command=saveMetric, bg="green", fg="white")
        button1.place(x=280, y=370)

    def serverSQLConfig():
        global pop, sqlRO, seripSql, sqlid, uname, autho, e4
        pop = Toplevel(root)
        pop.wm_attributes('-topmost', True)

        # Define and initialise essential popup variables -------------------------------------
        seripSql, sqlid, uname, autho = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
        print('State:', sqlRO)

        # center object on the screen---
        w, h = 480, 210
        pop.resizable(False, False)
        pop.title('Modify SQL Server Connection')
        screen_w = pop.winfo_screenwidth()
        screen_h = pop.winfo_screenheight()
        x_c = int((screen_w / 2) - (w / 2))
        y_c = int((screen_h / 2) - (h / 2))
        pop.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))

        labl_0 = Label(pop, text="SQL Credentials", width=20, font=("bold", 14))
        labl_0.place(x=130, y=10)

        # creating labels and positioning them on the grid --------[]
        Label(pop, text='Server IP').place(x=10, y=60)
        Label(pop, text='Database').place(x=10, y=100)
        Label(pop, text="Access ID").place(x=250, y=60)
        Label(pop, text="Authorize").place(x=250, y=100)

        # set initial variables or last known variables
        seripSql.set('Server ID')
        sqlid.set('dBase Repository')
        uname.set('User Name')
        autho.set('Authorization Code')

        # creating entries and positioning them on the grid -----
        if not sqlRO:
            e1 = Entry(pop, textvariable=seripSql, state='readonly')
            e1.place(x=86, y=60)
            e2 = Entry(pop, textvariable=sqlid, state='readonly')
            e2.place(x=86, y=100)
            e3 = Entry(pop, textvariable=uname, state='readonly')
            e3.place(x=330, y=60)
            e4 = Entry(pop, textvariable=autho, state='readonly')   #, show="*")
            e4.place(x=330, y=100)
        else:
            e1 = Entry(pop, textvariable=seripSql, state='normal')
            e1.place(x=86, y=60)
            e2 = Entry(pop, textvariable=sqlid, state='normal')
            e2.place(x=86, y=100)
            e3 = Entry(pop, textvariable=uname, state='normal')
            e3.place(x=330, y=60)
            e4 = Entry(pop, textvariable=autho, state='normal', show="*")
            e4.place(x=330, y=100)

        Button(pop, text="Change Details", bg="red", fg="white", command=clearFields).place(x=160, y=150)
        Button(pop, text="Test Connection", command=testConnSQL).place(x=270, y=150)
        Button(pop, text="Save Details", bg="green", fg="white", command=saveSQLconfig).place(x=380, y=150)

        return

    # ------------------------------------------------------------------
    def serverPLCConfig():
        global pop, sqlRO, seripPlc, sqlid, uname, autho, e4
        pop = Toplevel(root)
        pop.wm_attributes('-topmost', True)

        # Define and initialise essential popup variables -------------------------------------
        seripPlc, sqlid, uname, autho = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
        print('State:', sqlRO)

        # center object on the screen---
        w, h = 480, 210
        pop.resizable(False, False)
        pop.title('Modify PLC Connection')
        screen_w = pop.winfo_screenwidth()
        screen_h = pop.winfo_screenheight()
        x_c = int((screen_w / 2) - (w / 2))
        y_c = int((screen_h / 2) - (h / 2))
        pop.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))

        labl_0 = Label(pop, text="PLC Credentials", width=20, font=("bold", 14))
        labl_0.place(x=130, y=10)

        # creating labels and positioning them on the grid --------[]
        Label(pop, text='Host PLC').place(x=10, y=60)
        Label(pop, text='Data Block').place(x=10, y=100)
        Label(pop, text="Access ID").place(x=250, y=60)
        Label(pop, text="Authorize").place(x=250, y=100)

        # set initial variables or last known variables
        seripPlc.set('Server ID')
        sqlid.set('Volatile Repository')
        uname.set('User Name')
        autho.set('Authorization Code')

        # creating entries and positioning them on the grid -----
        if not sqlRO:
            e1 = Entry(pop, textvariable=seripPlc, state='readonly')
            e1.place(x=86, y=60)
            e2 = Entry(pop, textvariable=sqlid, state='readonly')
            e2.place(x=86, y=100)
            e3 = Entry(pop, textvariable=uname, state='readonly')
            e3.place(x=330, y=60)
            e4 = Entry(pop, textvariable=autho, state='readonly') #, show="*")
            e4.place(x=330, y=100)
        else:
            e1 = Entry(pop, textvariable=seripPlc, state='normal')
            e1.place(x=86, y=60)
            e2 = Entry(pop, textvariable=sqlid, state='normal')
            e2.place(x=86, y=100)
            e3 = Entry(pop, textvariable=uname, state='normal')
            e3.place(x=330, y=60)
            e4 = Entry(pop, textvariable=autho, state='normal', show="*")
            e4.place(x=330, y=100)

        Button(pop, text="Change Details", bg="red", fg="white", command=clearFields).place(x=160, y=150)
        Button(pop, text="Test Connection", command=testConnPLC).place(x=270, y=150)
        Button(pop, text="Save Details", bg="green", fg="white", command=saveSQLconfig).place(x=380, y=150)

        return

    def oclicked():
        if svar1.get() == 1:
            oEE = 1
            print("OEE Data Disabled", oEE)
            svar1.set(0)
        else:
            oEE = 0
            print("OEE Data Enabled", not oEE)
            svar1.set(1)
        return oEE

    def aboutSPC():        # TODO configure menu item to functon
        pop = Toplevel(root)

        pop.wm_attributes('-topmost', True)
        # center object on the screen---
        pop.resizable(False, False)
        w, h = 430, 250
        pop.title('About MagmaSPC')
        screen_w = pop.winfo_screenwidth()
        screen_h = pop.winfo_screenheight()
        x_c = int((screen_w / 2) - (w / 2))
        y_c = int((screen_h / 2) - (h / 2))
        pop.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))

        labl_0 = Label(pop, text="The Synchronous SPC (GPU Edition 2.0)", font=("bold", 14))
        labl_0.place(x=60, y=30)

        # creating labels and positioning them on the grid --------[]
        Label(pop, text='Real-Time Statistical Process Control System').place(x=90, y=80)
        Label(pop, text='Built Ver: 12.0, Built on: November 2024').place(x=110, y=100)
        Label(pop, text='Author: Robert B. Labs').place(x=140, y=120)
        Label(pop, text='Copyright (C) 2023-2025 Magma Industrialisation, United Kingdom.').place(x=30, y=180)
       # filewin = Toplevel(pop)

    def onlinehelp():        # TODO configure menu item to functon
        import webbrowser
        webbrowser.open(url, new=1)
        return

    def testConnSQL():
        import Test_PING as sq
        agent = 0
        server_IP = seripSql.get()  # PLC Server IP

        try:
            # Test server connection over TCP/IP ---------------------[]
            netTX = sq.testNetworkConn([server_IP], 1)  # if ICMP ping response is allowed on the server
            if netTX:
                hostConnect()  # acknowledgement
            else:
                pingError()  # Ping error failed -------
                conn = 'none'

        except Exception as err:
            errorLog(f"{err}")
            errorNoServer()  # errorNoServer()
            conn = 'none'

        return conn

    def testConnPLC():
        import Test_PING as sq
        agent = 0
        server_IP = seripPlc.get()  # PLC Server IP

        try:
            # Test server connection over TCP/IP ---------------------[]
            netTX = sq.testNetworkConn([server_IP], 1)  # if ICMP ping response is allowed on the server
            if netTX:
                hostConnect()                                              # acknowledgement
            else:
                pingError()                                            # Ping error failed -------
                conn = 'none'

        except Exception as err:
            errorLog(f"{err}")
            errorNoServer()                                             # errorNoServer()
            conn = 'none'

        return conn

    def sCloseConnSQL():
        global conn

        import CommsSql as mCon
        agent = 0
        if agent == 0:
            conn = mCon.DAQ_connect(1, agent)  # 1 = connection is active to be .closed()
        else:
            conn = 'none'
            errorNoconnect()
        return conn

    def sCloseConnPLC():
        global conn

        import CommsPlc as mCon
        agent = 0
        if agent == 0:
            conn = mCon.connectM2M()                    # TODO: Check PLC server link
        else:
            conn = 'none'
            errorNoconnect()
        return conn

    # ---------------------------------------------------------------------------[]
    def discALL():
        if filemenu.entrycget(3, 'state') == 'disabled':
            filemenu.entryconfig(3, label='Disconnect SQL Data', state='normal')
            filemenu.entryconfig(4, label="Disconnect PLC Data", state='normal')
            filemenu.entryconfig(5, label='Terminate Connections', state='disabled')
            connect = True
            sCloseConnSQL()
            # ---- acknowledgement f(x) ----

        elif filemenu.entrycget(4, 'state') == 'disabled':
            filemenu.entryconfig(3, label='Disconnect SQL Data', state='normal')
            filemenu.entryconfig(4, label="Disconnect PLC Data", state='normal')
            filemenu.entryconfig(5, label='Terminate Connections', state='disabled')
            connect = True
            sCloseConnPLC()
            # ---- acknowledgement f(x) ----

        else:
            connect = False
            errorNoconnect()
            print('\nNo active connection found..')

        return connect
    # One of the challenging object to configure both checkbox and state --------[]

    def retroPlay():
        # Declare global variable available to all proceesses
        global stpd, WON, processID, OEEdataID, hostConn
        import CommsSql as hs

        # import signal
        # os.kill(sid, signal.SIGTERM)
        if (analysis.entrycget(0, 'state') == 'normal'
                and analysis.entrycget(1, 'state') == 'normal'
                and analysis.entrycget(3, 'state') == 'normal'):
            analysis.entryconfig(0, state='disabled')

            # ----- Calling essential functions ---------#
            DATEentry, WONentry = retroUserSearchReq()                                  # Search for Production data
            hostConn = hs.DAQ_connect(0, 1)                                 # Connect to SQL Host

            OEEdataID, processID = sqld.searchSqlRecs(hostConn, DATEentry, WONentry)    # Query SQL record
            # processID = processID +'RF'
            qType = 2
            runType.append(qType)
            print('Connecting to SQL Query...')

        elif (analysis.entrycget(3, 'state') == 'disabled'
              and analysis.entrycget(0, 'state') == 'normal'):
            analysis.entryconfig(3, state='normal')
            analysis.entryconfig(0, state='disabled')

            # ----- Calling essential functions ----------#
            DATEentry, WONentry = retroUserSearchReq()                                  # Search for Production data
            hostConn = hs.DAQ_connect(0, 1)                                 # Connect to SQL Host
            # connect SQL Server and obtain Process ID ----#
            OEEdataID, processID = sqld.searchSqlRecs(hostConn, DATEentry, WONentry)    # Query SQL record
            # ---------------------------------------------[]
            qType = 2
            runType.append(qType)
            print('Connecting to SQL Query...')

        else:
            runtimeChange()
            qType = 0
            runType.append(qType)
            print('Invalid SQL Query connection...')

        # return # stpd, WON, processID, OEEdataID, qType, hostConn

    def realTimePlay():
        import CommsPlc as hp

        global hostConn

        # import dataRepository as sqld
        if (analysis.entrycget(0, 'state') == 'normal'
                and analysis.entrycget(1, 'state') == 'normal'
                and analysis.entrycget(3, 'state') == 'normal'):
            analysis.entryconfig(1, state='disabled')
            # ----- Calling essential functions -----------[]
            qType = 1
            runType.append(qType)
            # ---------------------------------------------[]
            hostConn = hp.connectM2M()

        elif (analysis.entrycget(3, 'state') == 'disabled'
              and analysis.entrycget(1, 'state') == 'normal'):
            analysis.entryconfig(3, state='normal')
            analysis.entryconfig(1, state='disabled')
            # ----- Calling essential functions -----------
            qType = 1
            runType.append(qType)
            hostConn = hp.connectM2M()

        else:
            runtimeChange()
            qType = 0
            runType.append(qType)

        return

    def terminateVis(typeV):
        if messagebox.askokcancel("STOP: Visualisation", "Terminating Visualisation?"):
            if typeV == 1:
                casc_clearOut()
            else:
                tabb_clearOut()
        else:
            if typeV == 1:
                process.entryconfig(0, state='disabled')  # return to previous state
            else:
                process.entryconfig(1, state='disabled')  # return to previous state
            process.entryconfig(3, state='normal')        # return calling menu command to initial dstate

    def stopSPCrun():                   # reset analysis menu command
        if (analysis.entrycget(0, 'state') == 'disabled'
                or analysis.entrycget(1, 'state') == 'disabled'):
            analysis.entryconfig(3, state='disabled')
            analysis.entryconfig(0, state='normal')
            analysis.entryconfig(1, state='normal')
        else:
            errorSelection()
        # clearSPCrun()
        # terminateVis()  # TODO - this should close existing SPC window

    # ---------------------- CALL SPC FUNCTIONAL PROCEDURES ---------------------------------------------[]
    def validQueryObj():
        # Check SQL connection and selected option on SQL data Types ----------------------[]
        if filemenu.entrycget(5, 'state') == 'disabled' and filemenu.entrycget(2, 'state') == 'disabled':
            plcTbls, sqlTbls = 1, 0
            print('Using PLC Query System...')

        elif filemenu.entrycget(6, 'state') == 'disabled' and filemenu.entrycget(2, 'state') == 'disabled':
            plcTbls, sqlTbls = 0, 1
            print('Using SQL Query System...')

        else:
            plcTbls, sqlTbls = 0, 0
            print('Valid Query Object not found...')
            errorNoServer()
        return plcTbls, sqlTbls

    def retroUserSearchReq():       # Search for production data either by date or work order number
        pop = Toplevel(root)
        pop.wm_attributes('-topmost', True)

        # center root window --------------
        pop.tk.eval(f'tk::PlaceWindow {pop._w} center')
        pop.withdraw()
        stad = askstring(title="Date", prompt="Work Order Number (WON):", initialvalue="20240507", parent=root)

        # -----------------------############---------------------------[]
        # Test for null entry -------------
        if stad is None or stad == '':
            return

        elif stad.isnumeric():  # Checks if characters in the entry are numeric.
            print('\nProduction Record Search by Work Order Number...')
            ret = 1
            stad = str(stad)
            WONentry = stad                          # Obtain Work Order Number
            DATEentry = '0'                          # Date was not used
            lst_idx = 0

        else:  # calculate the next boundary date
            print('\nProduction Record Search by Production Date...')
            rangeD = stad.split('-', 2)
            print(rangeD)
            # treat calendar special casess ------------------------[]
            if rangeD[1] == '02' and rangeD[2] == '28':  # february
                # print('AM HERE 1')
                stpdA = int(rangeD[1]) + 1
                stpdB = '01'

            elif rangeD[2] == '31':  # Jan, March, May, July, August, October, December
                # print('AM HERE 2')
                if (rangeD[1] == '01' or rangeD[1] == '03' or rangeD[1] == '05' or rangeD[1] == '07'
                        or rangeD[1] == '08' or rangeD[1] == '10' or rangeD[1] == '12'):
                    stpdA = int(rangeD[1]) + 1
                    stpdB = '01'

            elif rangeD[2] == '30':  # April June, September, November
                # print('AM HERE 3')
                if rangeD[1] == '04' or rangeD[1] == '06' or rangeD[1] == '09' or rangeD[1] == '11':
                    stpdA = int(rangeD[1]) + 1
                    stpdB = '01'

            else:
                # print('AM HERE 4')
                stpdA = rangeD[1]
                stpdB = int(rangeD[2]) + 1
            DATEentry = rangeD[0] + '-' + str(stpdA) + '-' + str(stpdB)  # Date was used in search query

            # Convert to Work Order Number---
            WON = stad.split('-')
            WONentry = WON[0] + WON[1] + WON[2]

        return DATEentry, WONentry

    # -------------------------------- APP MENU PROCEDURE START ------------------------------------------------[]
    def viewTypeA():    # enforce selection integrity ------------------[Cascade Tabb View]
        global p1, p2, p3, p4, p5, HeadA, rType                             # declare as global variables
        #
        # Define run Type -------------[]
        if runType == 1:
            rType = 'Synchro'
        elif runType == 2:
            rType = 'PostPro'
        else:
            rType = 'Standby'
        # -----------------------------[]
        if process.entrycget(1, 'state') == 'disabled':      # If Tabbed View was in disabled state
            # if Tabbed view is active
            process.entryconfig(0, state='disabled')                # select cascade View becomes an option
            process.entryconfig(1, state='normal')                  # set Tabb View to normal
            process.entryconfig(3, state='normal')                  # set Close Display to normal

            if messagebox.askokcancel("Warning!!!", "Current Visualisation will be lost!"):
                tabb_clearOut()                                           # Clear out existing Tabbed View
                cascadeViews()                                            # --- start parallel thread
                # call function for parallel pipeline --------------------#
                import CascadeSwitcher as cs
                p1, p2, p3, p4, p5 = cs.myMain(rType)
                exit_bit.append(1)

            else:
                process.entryconfig(1, state='disabled')            # revert to original state
                process.entryconfig(0, state='normal')              # revert to original state

            HeadA, HeadB, closeV = 1, 0, 0

        elif process.entrycget(3, 'state') == 'disabled':        # If Closed Display state is disabled
            process.entryconfig(0, state='disabled')                    # select and disable Cascade View command
            process.entryconfig(1, state='normal')                      # set tabb view command to normal
            process.entryconfig(3, state='normal')                      # set close display to normal

            # --- start parallel thread ----------------------------------#
            cascadeViews()                                                   # Critical Production Params
            import CascadeSwitcher as cs
            p1, p2, p3, p4, p5 = cs.myMain(rType)                            # call function for parallel pipeline
            exit_bit.append(1)
            HeadA, HeadB, closeV = 1, 0, 0

        elif (process.entrycget(0, 'state') == 'normal'
              and process.entrycget(1, 'state') == 'normal'
              and process.entrycget(3, 'state') == 'normal'):
            process.entryconfig(0, state='disabled')
            process.entryconfig(1, state='normal')
            process.entryconfig(3, state='normal')

            # --- start parallel thread ------------------------------#
            cascadeViews()                                                  # Critical Production Params
            import CascadeSwitcher as cs

            p1, p2, p3, p4, p5 = cs.myMain(rType)                                # call function for parallel pipeline
            exit_bit.append(1)
            HeadA, HeadB, closeV = 1, 0, 0

        else:
            process.entryconfig(0, state='normal')
            HeadA, HeadB, closeV = 0, 0, 1
            errorChoice()                               # pop up error
            print('Invalid! View selection before process parameter..')

        return HeadA, HeadB, closeV

    def viewTypeB():
        global HeadA, HeadB, closeV, rType
        # Define run Type ---------------------[TODO]
        if runType == 1:
            rType = 'Synchro'
        elif runType == 2:
            rType = 'PostPro'
        else:
            rType = 'Standby'
        # -------------------------------------[]
        # enforce category selection integrity ---------------------#
        if process.entrycget(0,'state') == 'disabled':
            process.entryconfig(1, state='disabled')
            process.entryconfig(0, state='normal')
            process.entryconfig(3, state='normal')

            if messagebox.askokcancel("Warning!!!", "Current Visualisation will be lost!"):
                casc_clearOut()                                     # clear out visualisation frame
                tabbed_canvas()                                     # Call Canvas binding function
                exit_bit.append(0)                                  # Keep a byte into empty list
            else:
                process.entryconfig(0, state='disabled')        # revert to original state
                process.entryconfig(1, state='normal')          # revert to original state

            HeadA, HeadB, closeV = 0, 1, 0      # call embedded functions

        elif process.entrycget(3, 'state') == 'disabled':
            process.entryconfig(1, state='disabled')
            process.entryconfig(0, state='normal')
            process.entryconfig(3, state='normal')

            tabbed_canvas()                     # Tabbed Visualisation
            exit_bit.append(0)

            HeadA, HeadB, closeV = 0, 1, 0      # call embedded functions

        elif (process.entrycget(0, 'state') == 'normal'
                  and process.entrycget(1, 'state') == 'normal'
                  and process.entrycget(3, 'state') == 'normal'):
                process.entryconfig(1, state='disabled')
                process.entryconfig(0, state='normal')
                process.entryconfig(3, state='normal')

                tabbed_canvas()                 # Tabbed Visualisation
                exit_bit.append(0)
                HeadA, HeadB, closeV = 0, 1, 0

        else:
            process.entryconfig(1, state='normal')
            HeadA, HeadB, closeV = 0, 0, 1
            errorChoice()                                   # raise user exception
            print('Invalid! View selection before process parameter..')

        return HeadA, HeadB, closeV

    def tabb_clearOut():
        # evaluate how many widget is in use and clear accordingly
        inUse = len(root.winfo_children())
        print('TP2', inUse)
        if inUse == 9:
            root.winfo_children()[9].destroy()
            root.winfo_children()[8].destroy()
            root.winfo_children()[7].destroy()
            root.winfo_children()[6].destroy()
        elif inUse == 7:
            root.winfo_children()[6].destroy()
            root.winfo_children()[5].destroy()
        # ---------------------------------
        root.winfo_children()[4].destroy()
        root.winfo_children()[3].destroy()
        root.winfo_children()[2].destroy()
        root.winfo_children()[1].destroy()

    # ------------------------------------------#
    def kill_process(pid):
        # SIGKILL = terminate the process forcefully | SIGINT = interrupt ( equivalent to CONTROL-C)
        os.kill(pid, signal.SIGTERM)
    # ------------------------------------------#

    def casc_clearOut():
        # https://www.geeksforgeeks.org/python-different-ways-to-kill-a-thread/
        # inUse = len(root.winfo_children())
        # -------------
        # print('\n******************************')
        # print('Get PPID', os.getppid())                         # Parent ID 37248
        # print('Get PID', os.getpid())                           # Child ID 52692
        # # print('Get GID', os.getegid())
        # print('Get CWDB', os.getcwdb())                         # b'C:\\CuttingEdge\\BETA_ver3.6'
        # print('Get CWD', os.getcwd())                           # C:\CuttingEdge\BETA_ver3.6
        # print('Get INDENT', get_ident())                        # 32356
        # print('Get Native ID', get_native_id())                 # 32356
        # print('Current Thread Name', current_thread().name)     # MainThread
        # print('Current Thread Ident', current_thread().ident)   # Current Thread 32356

        try:
            kill_process(p5.pid)        # convert process into pid number, usually and integer number
            kill_process(p4.pid)
            kill_process(p3.pid)
            kill_process(p2.pid)
            kill_process(p1.pid)
        except OSError:
            print(f'Process {p5} failed to terminate!')
            print(f'Process {p4} failed to terminate!')
            print(f'Process {p3} failed to terminate!')
            print(f'Process {p2} failed to terminate!')
            print(f'Process {p1} failed to terminate!')
        # for widget in root.winfo_children():
        root.winfo_children()[1].destroy()

    def closeViews():
        # enforce category selection integrity ---------------------#
        if process.entrycget(0, 'state') == 'disabled':

            process.entryconfig(0, state='normal')
            process.entryconfig(1, state='normal')
            process.entryconfig(3, state='disabled')

            viewA = 1
            terminateVis(viewA)
            # casc_clearOut()
            HeadA, HeadB, closeV = 0, 0, 1

        elif process.entrycget(1, 'state') == 'disabled':
            process.entryconfig(0, state='normal')
            process.entryconfig(1, state='normal')
            process.entryconfig(3, state='disabled')

            viewB = 2
            terminateVis(viewB)
            # tabb_clearOut()                               # Call Canvas binding function
            HeadA, HeadB, closeV = 0, 0, 1                  # call embedded functions

        else:
            process.entryconfig(3, state='normal')
            HeadA, HeadB, closeV = 0, 0, 1
            errorChoice()                                   # raise user exception
            print('Invalid! View selection before process parameter..')

        return HeadA, HeadB, closeV

    # Menu Bar --------------------------------------------------------------------------------[]
    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    sub_menu = tk.Menu(menubar, tearoff=0)
    filemenu.add_cascade(label="Server Credentials", menu=sub_menu)
    sub_menu.add_command(label="SQL Connectivity", command=serverSQLConfig, accelerator="Ctrl+S")
    sub_menu.add_command(label="PLC Connectivity", command=serverPLCConfig, accelerator="Ctrl+P")
    filemenu.add_command(label="Statistical Limits", command=newMetricsConfig, accelerator="Ctrl+L")

    filemenu.add_separator()
    filemenu.add_command(label="Disconnect SQL Data", command=sCloseConnSQL, accelerator="Alt+S")  # enabled on connection
    filemenu.add_command(label="Disconnect PLC Data", command=sCloseConnPLC, accelerator="Alt+P")  # disable no connection
    filemenu.add_command(label="Terminate Connections", command=discALL, accelerator="Ctrl+Q")

    filemenu.add_separator()
    filemenu.add_command(label="Close", command=callback)           # root.destroy via callback func
    filemenu.add_command(label="Exit", command=menuExit)
    menubar.add_cascade(label="System Setup", menu=filemenu)

    # Analysis Menu -----------------------------------------[]
    analysis = Menu(menubar, tearoff=0)
    analysis.add_command(label="Post Production", command=retroPlay)
    analysis.add_command(label="Synchronous SPC", command=realTimePlay)

    analysis.add_separator()
    analysis.add_command(label="Stop SPC Process", command=stopSPCrun)
    menubar.add_cascade(label="Runtime Mode", menu=analysis)

    # Process Menu ----------------------------------------[]
    process = Menu(menubar, tearoff=0)
    process.add_command(label="Cascade Views", command=viewTypeA)
    process.add_command(label="Tabbed Views", command=viewTypeB)
    process.add_separator()
    process.add_command(label="Close Display", command=closeViews)
    menubar.add_cascade(label="Visualisation", menu=process)

    # Help Menu ------------------------------------------------[]
    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Help Index", command=onlinehelp)
    helpmenu.add_command(label="About...", command=aboutSPC)
    menubar.add_cascade(label="SPC Help", menu=helpmenu)

    root.config(menu=menubar)
    # ----------------------------------------------------------------------[]
    canvasOn(1)  # Update canvas on when GUI is active
    # ----------------------------------------------------------------------[]
    # tabbed_canvas()

    # capture closing events and activate snooze mode -------------[]
    root.protocol("WM_DELETE_WINDOW", callback)

    # root.mainloop()


if __name__ == '__main__':
    # This code will only be executed if the script is run as the main program
    root = Tk()
    userMenu()
    root.mainloop()
