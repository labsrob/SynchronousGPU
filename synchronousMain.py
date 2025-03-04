# --------------------------------------------------------------------------#
# Author: Dr RB Labs
# Developed for Magma Global - TechnipFMC Industrialization
# Email: robbielabs@uwl.ac.uk
# Copyright (C) 2023-2025, Robbie Labs
#
# -------------------- Primary User Graphic Interface ----------------------#

import numpy as np
import pandas as pd
import spcWatchDog as wd

# ----- PLC/SQL Query ---#
import selDataColsEV as qev     # Environmental Values
import selDataColsLA as qla     # Laser Angle
import selDataColsLP as qlp     # Laser Power
import selDataColsRC as qrc     # Ramp Count
import selDataColsRF as qrf     # Roller Force
import selDataColsRM as qrm     # Ramp Mapping
import selDataColsST as qst     # Substrate Temperature
import selDataColsTG as qtg     # Tape Gap Void
import selDataColsTP as qtp     # Tape Placement error
import selDataColsTT as qtt     # Tape Temperature
import selDataColsVC as qvc     # void (gap) count
import selDataColsVM as qvm     # Void mapping
import selDataColsEoL as eol    # End of Layer

# ----- DNV/MGM Params ---#
import selDataColsPM as qpm     # Production Monitors
import selDataColsRP as qrp     # Roller Pressure
import selDataColsWS as qws     # Tape winding Speed
import selDataColsCT as qct     # Cell Tension
import selDataColsOT as qot     # Oven Temperature
import selDataColsWA as qwa     # winding angle
import selDataColsOE as qoe     # OEE TechnipFMC
# -------------------------#

import time
import os
import sys
from datetime import datetime
from time import gmtime, strftime
import signal
import tkinter as tk
from tkinter import *
from threading import *
from multiprocessing import Process
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
from mpl_interactions import ioff, panhandler, zoom_factory
# --------------------------
import pParamsHL as dd
import pWON_finder as sqld

# import qParametersDNV as hla
# import qParametersMGM as hlb
# ------------------------------------------------------------------------[]
tabConfig = []
cpTapeW, cpLayerNo, runType = [], [], []
OTlayr, EPpos, pStatus = [], [], []
HeadA, HeadB, vTFM = 0, 0, 0
hostConn = 0
runStatus = 0

# -------------
gap_vol = 0
ramp_vol = 0
vCount = 1000
pExLayer = 100
pLength = 10000
# --------------
optm = True

# --------------
import subprocess
try:
    subprocess.check_output('nvidia-smi')
    print('Nvidia GPU detected!')
except Exception:
    print('No Nvidia GPU in system!')

# ----------------------- Audible alert --------------------------------------------------[]
impath ='C:\\Users\\DevEnv\\PycharmProjects\\SynchronousGPU\\Media\\'
nudge = AudioSegment.from_wav(impath+'tada.wav')
error = AudioSegment.from_wav(impath+'error.wav')

# -------------------------------------------------------------------------------------------#
path = ('C:\\Users\\DevEnv\\OneDrive - Magma Global LTD\\Documents\\Development DOCUMENTS\\'
                'Technical Reqs Docs\\Tape Gap Measurements\\testFile.csv')
csv_file = (path)
df = pd.read_csv(csv_file)

# Define statistical operations ----------------------------------------------------------[]
WeldQualityProcess = True
paused = False

url = 'http://www.magmaglobal.com'
localArray = []                                         # raising the bit for GUI canvas
exit_bit = []                                           # enable the close out of all cascade windows

# XBar Constants ------------------------------[]
A3 = [0.975, 0.789, 0.680, 0.6327, 0.606, 0.5525]       # 10, 15, 20, 23, 25, 30  sample sizes respectively
B3 = [0.284, 0.428, 0.510, 0.5452, 0.565, 0.6044]       # 10, 15, 20, 23, 25, 30  sample sizes respectively
B4 = [1.716, 1.572, 1.490, 1.4548, 1.435, 1.3956]       # 10, 15, 20, 23, 25, 30

UsePLC_DBS = True                                       # specify SQl Query or PLC DB Query is in use
processWON = []

# ------------- Dummy values -------------------[]
pPos = '6.2345'
layer = '03'
WON = "275044"
sel_SS = "30"
sel_gT = "S-Domino"
eSMC = 'Tape laying process in progress...'
# ------------------ Auto canvass configs ------[]
y_start = 110
y_incmt = 30
rtValues = []

# ---- Common to all Process Procedures --------[]
pRecipe = ""

# Call function and load WON specification -----[]
mLA, mLP, mCT, mOT, mRP, mWS, mSP, sStart, sStops, LP, LA, TP, RF, TT, ST, TG, SP = dd.decryptMetricsGeneral(WON)
print('\nDecrypted Prod Parameters:', mLA, mLP, mCT, mOT, mRP, mWS, mSP, sStart, sStops, LP, LA, TP, RF, TT, ST, TG, SP)

# ----------------------------------------------[]
if int(TT) and int(ST) and int(TG) and not int(LP) and not int(LA) and not int(TP) and not int(RF):
    pRecipe = 'DNV'
    import qParamsHL_DNV as prc
elif int(LP) and int(LA) and int(TP) and int(RF) and int(TT) and int(ST) and int(TG):
    pRecipe = 'MGM'
    import qParamsHL_MGM as prc
else:
    pRecipe = 'USR'
# ----------------------------------------------[]

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)

    # Create table header -------------------------------------[]
    for header in ["TCP01", "Actual", "Nominal", "Std Dev", "Tolerance +/-", "Status"]:
        pdf.cell(30, 10, header, 1)
    pdf.ln()

    # Create table label --------------------------------------[]
    for label in ['Ring1', 'Ring2', 'Ring3', 'Ring4']:
        pdf.cell(30, 10, label, 1)
    pdf.ln()

    # Create table rows ---------------------------------------[]
    for row in data:
        for item in row:
            pdf.cell(30, 10, str(item), 1)
        pdf.ln()

    pdf.output("QualityEOL.pdf")


def get_data():
    data = []
    for i in range(4):
        row = [entry.get() for entry in entries[i]]
        # row1 = r1_actual.get(), r1_nominal.get(), r1_stdDev.get(), r1_tolerance.get(), r1_status.get()
        # row2 = r2_actual.get(), r2_nominal.get(), r2_stdDev.get(), r2_tolerance.get(), r2_status.get()
        # row3 = r3_actual.get(), r3_nominal.get(), r3_stdDev.get(), r3_tolerance.get(), r3_status.get()
        # row4 = r4_actual.get(), r4_nominal.get(), r4_stdDev.get(), r4_tolerance.get(), r4_status.get()

        data.append(row)
    generate_pdf(data)

    # -------------------------------------------------[]

class autoResizableCanvas(tk.Canvas):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<Configure>", self.resize)

    def resize(self, event):
        self.config(width=event.width, height=event.height)


def diff_idx_Tracker(layer, idx1, idx2, idx3, idx4, idx5, idx6, pPos):    # Record for offline SPC analysis
    rtitle = ('================================= TCP01 - Realtime Index Tracker =============================\n')
    rheader = ('Time'+'\t\t'+'Layer#'+'\t'+'T1Row'+'\t'+'T2Row'+'\t'+'T3Row'+'\t'+'T4Row'+'\t'+'T5Row'+'\t'+'T6Row'+'\t'+'EstPos'+'\n')
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


# This function runs only once! When SPC stalls and replayed
def bufferEOF(fname, N):
    # open index tracker file, and load the values in the end of file
    with open(fname) as file:
        for line in (file.readlines()[-N:]):    # N = number of lines to read
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
    if not exit_bit:        # Check exit_bit for unitary value
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

# ------------------------------------------------------------------------------------[ MAIN PROGRAM ]

def tabbed_cascadeMode():  # Limited Tab default screen with multiple independent screens
    global p1, p2, p3, p4, p5, p6, p7
    """
    https://stackoverflow.com/questions/73088304/styling-a-single-tkinter-notebook-tab
    :return:
    """
    s = ttk.Style()
    s.theme_use('default')  # Options: ('clam', 'alt', 'default', 'classic')
    s.configure('TNotebook.Tab', background="green3", foreground="black")

    # s.map("TNotebook", background=[("selected", "red3")]) ------------------------------------------#
    s.map("TNotebook.Tab", background=[("selected", "lightblue")], foreground=[("selected", "red")])
    # Hover color if needed....-----------------------------------------------------------------------#

    # Insert 3 runtime objects [1] Ramp Profile [2] Location Based Climate [3] Tape Gap Profile ------[]
    common_rampCount()                                          # Ramp cumulative curve
    common_climateProfile()                                     # environmental factors
    common_gapCount()                                           # Void gap count curve

    # Load class object from Cascade Switcher Method -----------[x]
    import CascadeSwitcher as cs
    p1, p2, p3, p4, p5, p6, p7 = cs.myMain(rType, pRecipe)      # runtimeType, process RecipeType
    # ----------------------------------------------------------[]

    # Set up embedding notebook (tabs) ------------------------[B]
    notebook = ttk.Notebook(root, width=2500, height=850)       # Declare Tab overall Screen size
    notebook.grid(column=0, row=0, padx=10, pady=450)           # Tab's spatial position on the Parent
    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)
    tab3 = ttk.Frame(notebook)

    # Define common Tabb for DNV/MGM Procedure  ----------------#
    notebook.add(tab1, text="[Runtime Monitoring]")             # Default Min/Max x1
    notebook.add(tab2, text="EoL Report System")                # Report
    notebook.add(tab3, text="EoP Report System")                # Report
    notebook.grid()

    # ------------------------------------------[]
    app1 = MonitorTabb(master=tab1)
    app1.grid(column=0, row=0, padx=10, pady=10)
    # ------------------------------------------[]
    app2 = collectiveEoL(master=tab2)
    app2.grid(column=0, row=0, padx=10, pady=10)

    app3 = collectiveEoP(master=tab3)
    app3.grid(column=0, row=0, padx=10, pady=10)

    root.mainloop()


def tabbed_canvas():   # Tabbed Common Classes -------------------[TABBED ]
    """
    https://stackoverflow.com/questions/73088304/styling-a-single-tkinter-notebook-tab
    :return:
    """
    s = ttk.Style()
    s.theme_use('default')
    s.configure('TNotebook.Tab', background="green3", foreground="black")

    # s.map("TNotebook", background=[("selected", "red3")]) ------------------------------------------#
    s.map("TNotebook.Tab", background=[("selected", "lightblue")], foreground=[("selected", "red")])
    # Hover color if needed  -------------------------------------------------------------------------#

    common_rampCount()
    common_climateProfile()
    common_gapCount()
    # Load from CFG fine and parse the variables ------[x]

    # Set up embedding notebook (tabs) ----------------[B]
    notebook = ttk.Notebook(root, width=2500, height=850)   # Declare Tab overall Screen size
    notebook.grid(column=0, row=0, padx=10, pady=450)       # Tab's spatial position on the Parent
    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)
    tab3 = ttk.Frame(notebook)
    tab4 = ttk.Frame(notebook)
    tab5 = ttk.Frame(notebook)
    tab6 = ttk.Frame(notebook)
    tab7 = ttk.Frame(notebook)
    tab8 = ttk.Frame(notebook)
    tab9 = ttk.Frame(notebook)
    tab10 = ttk.Frame(notebook)

    # ------------------------------------------ DNV Statistical Process Parameters -----[]
    if int(TT) and int(ST) and int(TG):
        pRecipe = 'DNV'
        print('\nAm hee DNV....')
        notebook.add(tab1, text="Tape Temperature")         # Stats x16
        notebook.add(tab2, text="Substrate Temperature")    # Stats x16
        notebook.add(tab3, text="Tape Gap Polarisation")    # Stats x4 per Ring
        # ----------------------------------------------#
        notebook.add(tab4, text="[Runtime Monitoring]")     # Default Min/Max x16
        # ----------------------------------------------#
        notebook.add(tab5, text="EoL Report System")        # Report
        notebook.add(tab6, text="EoP Report System")        # Report

    elif int(LP) and int(LA) and int(TP) and int(RF) and int(TT) and int(ST) and int(TG):
        pRecipe = 'MGM'
        print('\nAm hee MGM....')
        notebook.add(tab1, text="Laser Power")              # Stats
        notebook.add(tab2, text="Laser Angle")              # Stats
        notebook.add(tab3, text="Roller Force")             # Stats
        # --------------------------------------------------#
        notebook.add(tab4, text="Tape Temperature")         # Stats x16
        notebook.add(tab5, text="Subs Temperature")         # Stats x16
        notebook.add(tab6, text="Tape Placement Error")     # Stats x8 (2 per Ring)
        notebook.add(tab7, text="Tape Gap Polarisation")    # Stats x4 (1 per Ring)
        # --------------------------------------------------#
        notebook.add(tab8, text="[Runtime Monitoring]")     # Commercial - LP, LA, RP, WS, TG, RP
        # --------------------------------------------------#
        notebook.add(tab9, text="EoL Report System")
        notebook.add(tab10, text="EoP Report System")

    else:  # Bespoke selection only affects Runtime Monitoring Reports
        pRecipe = 'USR'
        print('\nAm hee USR....')
        notebook.add(tab1, text="Laser Power")           # Stats
        notebook.add(tab2, text="Laser Angle")           # Stats
        notebook.add(tab3, text="Roller Force")          # Stats
        # -----------------------------------------------#
        notebook.add(tab4, text="Tape Temperature")      # Stats
        notebook.add(tab5, text="Subs Temperature")      # Stats
        notebook.add(tab6, text="Tape Placement Error")  # Stats
        notebook.add(tab7, text="Tape Gap Polarisation") # Stats x4 per Ring
        # -----------------------------------------------#
        notebook.add(tab8, text="[Runtime Monitoring]")  # User Bespoke selection - LP, LA, RP, WS, TG, RP
        # -----------------------------------------------#
        notebook.add(tab9, text="EoL Report System")
        notebook.add(tab10, text="EoP Report System")

    notebook.grid()

    # Create DNV tab frames properties -------------[]
    if pRecipe == 'DNV':
        app1 = tapeTempTabb(master=tab1)
        app1.grid(column=0, row=0, padx=10, pady=10)

        app2 = substTempTabb(master=tab2)
        app2.grid(column=0, row=0, padx=10, pady=10)

        app3 = tapeGapPolTabb(master=tab3)
        app3.grid(column=0, row=0, padx=10, pady=10)
        # ------------------------------------------[]
        app4 = MonitorTabb(master=tab4)
        app4.grid(column=0, row=0, padx=10, pady=10)
        # ------------------------------------------[]
        app5 = collectiveEoL(master=tab5)
        app5.grid(column=0, row=0, padx=10, pady=10)

        app6 = collectiveEoP(master=tab6)
        app6.grid(column=0, row=0, padx=10, pady=10)

    elif pRecipe == 'MGM':
        app1 = laserPowerTabb(master=tab1)
        app1.grid(column=0, row=0, padx=10, pady=10)

        app2 = laserAngleTabb(master=tab2)
        app2.grid(column=0, row=0, padx=10, pady=10)

        app3 = rollerForceTabb(master=tab3)
        app3.grid(column=0, row=0, padx=10, pady=10)

        app4 = tapeTempTabb(master=tab4)
        app4.grid(column=0, row=0, padx=10, pady=10)

        app5 = substTempTabb(master=tab5)
        app5.grid(column=0, row=0, padx=10, pady=10)

        app6 = tapePlacementTabb(master=tab6)
        app6.grid(column=0, row=0, padx=10, pady=10)    # Tape Placement Error

        app7 = tapeGapPolTabb(master=tab7)
        app7.grid(column=0, row=0, padx=10, pady=10)    # Tape Gap Polarisation
        # --------------------------------------------[]
        app8 = MonitorTabb(master=tab8)
        app8.grid(column=0, row=0, padx=10, pady=10)
        # --------------------------------------------[]
        app9 = collectiveEoL(master=tab9)
        app9.grid(column=0, row=0, padx=10, pady=10)

        app10 = collectiveEoP(master=tab10)
        app10.grid(column=0, row=0, padx=10, pady=10)
        # ------------------------------------------[]
    else:       # USR Selection
        app1 = laserPowerTabb(master=tab1)
        app1.grid(column=0, row=0, padx=10, pady=10)

        app2 = laserAngleTabb(master=tab2)
        app2.grid(column=0, row=0, padx=10, pady=10)

        app3 = rollerForceTabb(master=tab3)
        app3.grid(column=0, row=0, padx=10, pady=10)

        app4 = tapeTempTabb(master=tab4)
        app4.grid(column=0, row=0, padx=10, pady=10)

        app5 = substTempTabb(master=tab5)
        app5.grid(column=0, row=0, padx=10, pady=10)

        app6 = tapePlacementTabb(master=tab6)
        app6.grid(column=0, row=0, padx=10, pady=10)  # Tape Placement Error

        app7 = tapeGapPolTabb(master=tab7)
        app7.grid(column=0, row=0, padx=10, pady=10)  # Tape Gap Polarisation
        # --------------------------------------------[]
        app8 = MonitorTabb(master=tab8)
        app8.grid(column=0, row=0, padx=10, pady=10)
        # --------------------------------------------[]
        app9 = collectiveEoL(master=tab9)
        app9.grid(column=0, row=0, padx=10, pady=10)

        app10 = collectiveEoP(master=tab10)
        app10.grid(column=0, row=0, padx=10, pady=10)
        # ------------------------------------------[]

    root.mainloop()


def readEoP(text_widget, rptID):
    # file_path = filedialog.askopenfilename(title='Select a Text File', filetypes=[('Text files&quot', '*.txt')])
    file_path = 'D:\\CuttingEdge\\BETA_ver3.6\\FMEA_Log\\'+ rptID +'.txt'
    rpfMissing = 'D:\\CuttingEdge\\BETA_ver3.6\\FMEA_Log\\RPT_NOTFOUND.txt'
    conc_RPT = ["RPT_RP_", "RPT_TT_", "RPT_ST_", "RPT_WS_", "RPT_TG_"]
    # -----------------------------------------------------------------

    if rptID == "RPT_AL_":
        counter = 1
        file_path = 'D:\\CuttingEdge\\BETA_ver3.6\\FMEA_Log\\'+ conc_RPT +'.txt'
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                content = file.read()
                text_widget.delete(1.0, tk.END)         # Clear previous content
                text_widget.insert(tk.END, content)
        counter += 1

        if counter == len(conc_RPT):
            pass

        else:
            with open(rpfMissing, 'r') as file:
                content = file.read()
                text_widget.delete(1.0, tk.END)         # Clear previous content
                text_widget.insert(tk.END, content)

    elif os.path.isfile(file_path):
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


class collectiveEoL(ttk.Frame):                                # End of Layer Progressive Report Tabb
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.createWidgets()

    def createWidgets(self):

        label = ttk.Label(self, text='[End of Layer Summary - ' + rType + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)
        # ----------------------------------#
        gen_report = ttk.Button(self, text="Generate PDF Reports", command=get_data)
        gen_report.place(x=1920, y=1)
        # ---------------------------------#
        upload_report = ttk.Button(self, text="Upload Reports", command=get_data)
        upload_report.place(x=2380, y=1)

        # Define Axes ---------------------#
        f = Figure(figsize=(25, 8), dpi=100)
        f.subplots_adjust(left=0.022, bottom=0.05, right=0.993, top=0.936, wspace=0.1, hspace=0.17)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 4, 1)         # xbar plot
        a2 = f.add_subplot(2, 4, 2)         # s bar plot
        a3 = f.add_subplot(2, 4, 3)         # s bar plot
        a4 = f.add_subplot(2, 4, (4, 8))    # void mapping profile
        a5 = f.add_subplot(2, 4, 5)         # s bar plot
        a6 = f.add_subplot(2, 4, 6)         # s bar plot
        a7 = f.add_subplot(2, 4, 7)         # s bar plot

        # Declare Plots attributes -----------------------------[H]
        plt.rcParams.update({'font.size': 7})                   # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -------------------#
        YScale_minEOL, YScale_maxEOL = 12 - 8.5, 12 + 8.5       # Roller Force
        sBar_minEOL, sBar_maxEOL = 10 - 80, 10 + 80             # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, 13                        # windows view = visible data points
        # ------------------------------------------------------#
        # Load SQL Query Table ---------------------------------#
        if pRecipe == 'DNV':
            EoLRep = 'DNV'
            T1 = WON + '_TT'  # Identify Table
            T2 = WON + '_ST'  # Identify Table
            T3 = WON + '_TG'  # Identify Table
            T4 = WON + '_RM'  # Identify Table
        elif pRecipe == 'MGM':
            EoLRep = 'MGM'
            T5 = WON + '_LP'  # Identify Table
            T6 = WON + '_LA'  # Identify Table
            T7 = WON + '_TP'  # Identify Table
            T8 = WON + '_RF'  # Identify Table
            T1 = WON + '_TT'  # Identify Table
            T2 = WON + '_ST'  # Identify Table
            T3 = WON + '_TG'  # Identify Table
            T4 = WON + '_RM'  # Identify Table
        else:
            pass
        # ----------------------------------------------------------#

        # Initialise runtime limits
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a5.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")

        a1.set_title('EoL - Tape Temperature [XBar]', fontsize=12, fontweight='bold')
        a5.set_title('EoL - Tape Temperature [SDev]', fontsize=12, fontweight='bold')
        # ------
        a2.set_title('EoL - Substrate Temperature [XBar]', fontsize=12, fontweight='bold')
        a6.set_title('EoL - Substrate Temperature [SDev]', fontsize=12, fontweight='bold')
        # -------------------
        a3.set_title('EoL - Tape Gap Measurement [XBar]', fontsize=12, fontweight='bold')
        a7.set_title('EoL - Tape Gap Measurement [SDev]', fontsize=12, fontweight='bold')

        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a3.grid(color="0.5", linestyle='-', linewidth=0.5)
        a5.grid(color="0.5", linestyle='-', linewidth=0.5)
        a6.grid(color="0.5", linestyle='-', linewidth=0.5)
        a7.grid(color="0.5", linestyle='-', linewidth=0.5)

        a1.legend(loc='upper right', title='EoL - Tape Temperature')
        a2.legend(loc='upper right', title='EoL - Substrate Temperature')
        a3.legend(loc='upper right', title='EoL - Tape Gap Measurement')

        # ----------------------------------------------------------#
        a1.set_ylim([YScale_minEOL, YScale_maxEOL], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        a2.set_ylim([sBar_minEOL, sBar_maxEOL], auto=True)
        a2.set_xlim([window_Xmin, window_Xmax])
        # ---------------------------------------------------------[]
        a4.cla()
        a4.get_yaxis().set_visible(False)
        a4.get_xaxis().set_visible(False)

        # ---------------------------------------------------------[]
        # Define Plot area and axes -
        # ---------------------------------------------------------[1-5]
        if EoLRep == 'DNV':
            im10, = a1.plot([], [], 'o-', label='Tape Temp - (R1H1)')
            im11, = a1.plot([], [], 'o-', label='Tape Temp - (R1H2)')
            im12, = a1.plot([], [], 'o-', label='Tape Temp - (R1H3)')
            im13, = a1.plot([], [], 'o-', label='Tape Temp - (R1H4)')
            im14, = a1.plot([], [], 'o-', label='Tape Temp - (R2H1)')
            im15, = a1.plot([], [], 'o-', label='Tape Temp - (R2H2)')
            im16, = a1.plot([], [], 'o-', label='Tape Temp - (R2H3)')
            im17, = a1.plot([], [], 'o-', label='Tape Temp - (R2H4)')
            im18, = a1.plot([], [], 'o-', label='Tape Temp - (R3H1)')
            im19, = a1.plot([], [], 'o-', label='Tape Temp - (R3H2)')
            im20, = a1.plot([], [], 'o-', label='Tape Temp - (R3H3)')
            im21, = a1.plot([], [], 'o-', label='Tape Temp - (R3H4)')
            im22, = a1.plot([], [], 'o-', label='Tape Temp - (R4H1)')
            im23, = a1.plot([], [], 'o-', label='Tape Temp - (R4H2)')
            im24, = a1.plot([], [], 'o-', label='Tape Temp - (R4H3)')
            im25, = a1.plot([], [], 'o-', label='Tape Temp - (R4H4)')
            # -------------------------------------------------------
            im26, = a5.plot([], [], 'o-', label='Tape Temp')
            im27, = a5.plot([], [], 'o-', label='Tape Temp')
            im28, = a5.plot([], [], 'o-', label='Tape Temp')
            im29, = a5.plot([], [], 'o-', label='Tape Temp')
            im30, = a5.plot([], [], 'o-', label='Tape Temp')
            im31, = a5.plot([], [], 'o-', label='Tape Temp')
            im32, = a5.plot([], [], 'o-', label='Tape Temp')
            im33, = a5.plot([], [], 'o-', label='Tape Temp')
            im34, = a5.plot([], [], 'o-', label='Tape Temp')
            im35, = a5.plot([], [], 'o-', label='Tape Temp')
            im36, = a5.plot([], [], 'o-', label='Tape Temp')
            im37, = a5.plot([], [], 'o-', label='Tape Temp')
            im38, = a5.plot([], [], 'o-', label='Tape Temp')
            im39, = a5.plot([], [], 'o-', label='Tape Temp')
            im40, = a5.plot([], [], 'o-', label='Tape Temp')
            im41, = a5.plot([], [], 'o-', label='Tape Temp')
            # ---------------------------------------------------------[2-6]
            im42, = a2.plot([], [], 'o-', label='Substrate Temp - (R1H1)')
            im43, = a2.plot([], [], 'o-', label='Substrate Temp - (R1H2)')
            im44, = a2.plot([], [], 'o-', label='Substrate Temp - (R1H3)')
            im45, = a2.plot([], [], 'o-', label='Substrate Temp - (R1H4)')
            im46, = a2.plot([], [], 'o-', label='Substrate Temp - (R2H1)')
            im47, = a2.plot([], [], 'o-', label='Substrate Temp - (R2H2)')
            im48, = a2.plot([], [], 'o-', label='Substrate Temp - (R2H3)')
            im49, = a2.plot([], [], 'o-', label='Substrate Temp - (R2H4)')
            im50, = a2.plot([], [], 'o-', label='Substrate Temp - (R3H1)')
            im51, = a2.plot([], [], 'o-', label='Substrate Temp - (R3H2)')
            im52, = a2.plot([], [], 'o-', label='Substrate Temp - (R3H3)')
            im53, = a2.plot([], [], 'o-', label='Substrate Temp - (R3H4)')
            im54, = a2.plot([], [], 'o-', label='Substrate Temp - (R4H1)')
            im55, = a2.plot([], [], 'o-', label='Substrate Temp - (R4H2)')
            im56, = a2.plot([], [], 'o-', label='Substrate Temp - (R4H3)')
            im57, = a2.plot([], [], 'o-', label='Substrate Temp - (R4H4)')
            # -----------------------------------------------------------------
            im58, = a6.plot([], [], 'o-', label='Substrate Temp')
            im59, = a6.plot([], [], 'o-', label='Substrate Temp')
            im60, = a6.plot([], [], 'o-', label='Substrate Temp')
            im61, = a6.plot([], [], 'o-', label='Substrate Temp')
            im62, = a6.plot([], [], 'o-', label='Substrate Temp')
            im63, = a6.plot([], [], 'o-', label='Substrate Temp')
            im64, = a6.plot([], [], 'o-', label='Substrate Temp')
            im65, = a6.plot([], [], 'o-', label='Substrate Temp')
            im66, = a6.plot([], [], 'o-', label='Substrate Temp')
            im67, = a6.plot([], [], 'o-', label='Substrate Temp')
            im68, = a6.plot([], [], 'o-', label='Substrate Temp')
            im69, = a6.plot([], [], 'o-', label='Substrate Temp')
            im70, = a6.plot([], [], 'o-', label='Substrate Temp')
            im71, = a6.plot([], [], 'o-', label='Substrate Temp')
            im72, = a6.plot([], [], 'o-', label='Substrate Temp')
            im73, = a6.plot([], [], 'o-', label='Substrate Temp')
            # ---------------------------------------------------------[3-7]
            im74, = a3.plot([], [], 'o-', label='Tape Gap - (A1)')
            im75, = a3.plot([], [], 'o-', label='Tape Gap - (A2)')
            im76, = a3.plot([], [], 'o-', label='Tape Gap - (A3)')
            im77, = a3.plot([], [], 'o-', label='Tape Gap - (A4)')
            im78, = a3.plot([], [], 'o-', label='Tape Gap - (B1)')
            im79, = a3.plot([], [], 'o-', label='Tape Gap - (B2)')
            im80, = a3.plot([], [], 'o-', label='Tape Gap - (B3)')
            im81, = a3.plot([], [], 'o-', label='Tape Gap - (B4)')
            # -----------------------------------------------------
            im82, = a7.plot([], [], 'o-', label='Tape Gap')
            im83, = a7.plot([], [], 'o-', label='Tape Gap')
            im84, = a7.plot([], [], 'o-', label='Tape Gap')
            im85, = a7.plot([], [], 'o-', label='Tape Gap')
            im86, = a7.plot([], [], 'o-', label='Tape Gap')
            im87, = a7.plot([], [], 'o-', label='Tape Gap')
            im88, = a7.plot([], [], 'o-', label='Tape Gap')
            im89, = a7.plot([], [], 'o-', label='Tape Gap')
            # -------------------------------------------------------[Ramp Data]
            im90, = a3.plot([], [], 'o-', label='Ramp Mappings - (R1)')     # Ring 1 value count per layer
            im91, = a3.plot([], [], 'o-', label='Ramp Mappings - (R2)')     # Ring 2 value count per layer
            im92, = a3.plot([], [], 'o-', label='Ramp Mappings - (R3)')     # Ring 3 value count per layer
            im93, = a3.plot([], [], 'o-', label='Ramp Mappings - (R4)')     # Ring 4 value count per layer
            # im94, = a7.plot([], [], 'o-', label='Tape Gap')
            # im95, = a7.plot([], [], 'o-', label='Tape Gap')
            # im96, = a7.plot([], [], 'o-', label='Tape Gap')
            # im97, = a7.plot([], [], 'o-', label='Tape Gap')
        else:
            EoLRep = 'MGM'
            im10, = a1.plot([], [], 'o-', label='Tape Temp - (R1H1)')
            im11, = a1.plot([], [], 'o-', label='Tape Temp - (R1H2)')
            im12, = a1.plot([], [], 'o-', label='Tape Temp - (R1H3)')
            im13, = a1.plot([], [], 'o-', label='Tape Temp - (R1H4)')
            im14, = a1.plot([], [], 'o-', label='Tape Temp - (R2H1)')
            im15, = a1.plot([], [], 'o-', label='Tape Temp - (R2H2)')
            im16, = a1.plot([], [], 'o-', label='Tape Temp - (R2H3)')
            im17, = a1.plot([], [], 'o-', label='Tape Temp - (R2H4)')
            im18, = a1.plot([], [], 'o-', label='Tape Temp - (R3H1)')
            im19, = a1.plot([], [], 'o-', label='Tape Temp - (R3H2)')
            im20, = a1.plot([], [], 'o-', label='Tape Temp - (R3H3)')
            im21, = a1.plot([], [], 'o-', label='Tape Temp - (R3H4)')
            im22, = a1.plot([], [], 'o-', label='Tape Temp - (R4H1)')
            im23, = a1.plot([], [], 'o-', label='Tape Temp - (R4H2)')
            im24, = a1.plot([], [], 'o-', label='Tape Temp - (R4H3)')
            im25, = a1.plot([], [], 'o-', label='Tape Temp - (R4H4)')
            # -------------------------------------------------------
            im26, = a5.plot([], [], 'o-', label='Tape Temp')
            im27, = a5.plot([], [], 'o-', label='Tape Temp')
            im28, = a5.plot([], [], 'o-', label='Tape Temp')
            im29, = a5.plot([], [], 'o-', label='Tape Temp')
            im30, = a5.plot([], [], 'o-', label='Tape Temp')
            im31, = a5.plot([], [], 'o-', label='Tape Temp')
            im32, = a5.plot([], [], 'o-', label='Tape Temp')
            im33, = a5.plot([], [], 'o-', label='Tape Temp')
            im34, = a5.plot([], [], 'o-', label='Tape Temp')
            im35, = a5.plot([], [], 'o-', label='Tape Temp')
            im36, = a5.plot([], [], 'o-', label='Tape Temp')
            im37, = a5.plot([], [], 'o-', label='Tape Temp')
            im38, = a5.plot([], [], 'o-', label='Tape Temp')
            im39, = a5.plot([], [], 'o-', label='Tape Temp')
            im40, = a5.plot([], [], 'o-', label='Tape Temp')
            im41, = a5.plot([], [], 'o-', label='Tape Temp')
            # ---------------------------------------------------------[T2]
            im42, = a2.plot([], [], 'o-', label='Substrate Temp - (R1H1)')
            im43, = a2.plot([], [], 'o-', label='Substrate Temp - (R1H2)')
            im44, = a2.plot([], [], 'o-', label='Substrate Temp - (R1H3)')
            im45, = a2.plot([], [], 'o-', label='Substrate Temp - (R1H4)')
            im46, = a2.plot([], [], 'o-', label='Substrate Temp - (R2H1)')
            im47, = a2.plot([], [], 'o-', label='Substrate Temp - (R2H2)')
            im48, = a2.plot([], [], 'o-', label='Substrate Temp - (R2H3)')
            im49, = a2.plot([], [], 'o-', label='Substrate Temp - (R2H4)')
            im50, = a2.plot([], [], 'o-', label='Substrate Temp - (R3H1)')
            im51, = a2.plot([], [], 'o-', label='Substrate Temp - (R3H2)')
            im52, = a2.plot([], [], 'o-', label='Substrate Temp - (R3H3)')
            im53, = a2.plot([], [], 'o-', label='Substrate Temp - (R3H4)')
            im54, = a2.plot([], [], 'o-', label='Substrate Temp - (R4H1)')
            im55, = a2.plot([], [], 'o-', label='Substrate Temp - (R4H2)')
            im56, = a2.plot([], [], 'o-', label='Substrate Temp - (R4H3)')
            im57, = a2.plot([], [], 'o-', label='Substrate Temp - (R4H4)')
            # -----------------------------------------------------------------
            im58, = a6.plot([], [], 'o-', label='Substrate Temp')
            im59, = a6.plot([], [], 'o-', label='Substrate Temp')
            im60, = a6.plot([], [], 'o-', label='Substrate Temp')
            im61, = a6.plot([], [], 'o-', label='Substrate Temp')
            im62, = a6.plot([], [], 'o-', label='Substrate Temp')
            im63, = a6.plot([], [], 'o-', label='Substrate Temp')
            im64, = a6.plot([], [], 'o-', label='Substrate Temp')
            im65, = a6.plot([], [], 'o-', label='Substrate Temp')
            im66, = a6.plot([], [], 'o-', label='Substrate Temp')
            im67, = a6.plot([], [], 'o-', label='Substrate Temp')
            im68, = a6.plot([], [], 'o-', label='Substrate Temp')
            im69, = a6.plot([], [], 'o-', label='Substrate Temp')
            im70, = a6.plot([], [], 'o-', label='Substrate Temp')
            im71, = a6.plot([], [], 'o-', label='Substrate Temp')
            im72, = a6.plot([], [], 'o-', label='Substrate Temp')
            im73, = a6.plot([], [], 'o-', label='Substrate Temp')
            # -----------------------------------------------------[T3]
            im74, = a3.plot([], [], 'o-', label='Tape Gap - (A1)')
            im75, = a3.plot([], [], 'o-', label='Tape Gap - (A2)')
            im76, = a3.plot([], [], 'o-', label='Tape Gap - (A3)')
            im77, = a3.plot([], [], 'o-', label='Tape Gap - (A4)')
            im78, = a3.plot([], [], 'o-', label='Tape Gap - (B1)')
            im79, = a3.plot([], [], 'o-', label='Tape Gap - (B2)')
            im80, = a3.plot([], [], 'o-', label='Tape Gap - (B3)')
            im81, = a3.plot([], [], 'o-', label='Tape Gap - (B4)')
            # -----------------------------------------------------[T]
            im82, = a7.plot([], [], 'o-', label='Tape Gap')
            im83, = a7.plot([], [], 'o-', label='Tape Gap')
            im84, = a7.plot([], [], 'o-', label='Tape Gap')
            im85, = a7.plot([], [], 'o-', label='Tape Gap')
            im86, = a7.plot([], [], 'o-', label='Tape Gap')
            im87, = a7.plot([], [], 'o-', label='Tape Gap')
            im88, = a7.plot([], [], 'o-', label='Tape Gap')
            im89, = a7.plot([], [], 'o-', label='Tape Gap')
            # -------------------------------------------------------[Ramp Data T4]
            im90, = a3.plot([], [], 'o-', label='Ramp Mappings - (R1)')  # Ring 1 value count per layer
            im91, = a3.plot([], [], 'o-', label='Ramp Mappings - (R2)')  # Ring 2 value count per layer
            im92, = a3.plot([], [], 'o-', label='Ramp Mappings - (R3)')  # Ring 3 value count per layer
            im93, = a3.plot([], [], 'o-', label='Ramp Mappings - (R4)')  # Ring 4 value count per layer

            # ---------------------------------------------------[Laser Power T5]
            im94, = a2.plot([], [], 'o-', label='Laser Power - (R1H1)')
            im95, = a2.plot([], [], 'o-', label='Laser Power - (R1H2)')
            im96, = a2.plot([], [], 'o-', label='Laser Power - (R1H3)')
            im97, = a2.plot([], [], 'o-', label='Laser Power - (R1H4)')
            im98, = a2.plot([], [], 'o-', label='Laser Power - (R2H1)')
            im99, = a2.plot([], [], 'o-', label='Laser Power - (R2H2)')
            im100, = a2.plot([], [], 'o-', label='Laser Power - (R2H3)')
            im101, = a2.plot([], [], 'o-', label='Laser Power - (R2H4)')
            im102, = a2.plot([], [], 'o-', label='Laser Power - (R3H1)')
            im103, = a2.plot([], [], 'o-', label='Laser Power - (R3H2)')
            im104, = a2.plot([], [], 'o-', label='Laser Power - (R3H3)')
            im105, = a2.plot([], [], 'o-', label='Laser Power - (R3H4)')
            im106, = a2.plot([], [], 'o-', label='Laser Power - (R4H1)')
            im107, = a2.plot([], [], 'o-', label='Laser Power - (R4H2)')
            im108, = a2.plot([], [], 'o-', label='Laser Power - (R4H3)')
            im109, = a2.plot([], [], 'o-', label='Laser Power - (R4H4)')
            # -----------------------------------------------------------------
            im110, = a6.plot([], [], 'o-', label='Laser Power')
            im111, = a6.plot([], [], 'o-', label='Laser Power')
            im112, = a6.plot([], [], 'o-', label='Laser Power')
            im113, = a6.plot([], [], 'o-', label='Laser Power')
            im114, = a6.plot([], [], 'o-', label='Laser Power')
            im115, = a6.plot([], [], 'o-', label='Laser Power')
            im116, = a6.plot([], [], 'o-', label='Laser Power')
            im117, = a6.plot([], [], 'o-', label='Laser Power')
            im118, = a6.plot([], [], 'o-', label='Laser Power')
            im119, = a6.plot([], [], 'o-', label='Laser Power')
            im120, = a6.plot([], [], 'o-', label='Laser Power')
            im121, = a6.plot([], [], 'o-', label='Laser Power')
            im122, = a6.plot([], [], 'o-', label='Laser Power')
            im123, = a6.plot([], [], 'o-', label='Laser Power')
            im124, = a6.plot([], [], 'o-', label='Laser Power')
            im125, = a6.plot([], [], 'o-', label='Laser Power')
            # ---------------------------------------------------[Laser Angle T6]
            im126, = a2.plot([], [], 'o-', label='Laser Angle - (R1H1)')
            im127, = a2.plot([], [], 'o-', label='Laser Angle - (R1H2)')
            im128, = a2.plot([], [], 'o-', label='Laser Angle - (R1H3)')
            im129, = a2.plot([], [], 'o-', label='Laser Angle - (R1H4)')
            im130, = a2.plot([], [], 'o-', label='Laser Angle - (R2H1)')
            im131, = a2.plot([], [], 'o-', label='Laser Angle - (R2H2)')
            im132, = a2.plot([], [], 'o-', label='Laser Angle - (R2H3)')
            im133, = a2.plot([], [], 'o-', label='Laser Angle - (R2H4)')
            im134, = a2.plot([], [], 'o-', label='Laser Angle - (R3H1)')
            im135, = a2.plot([], [], 'o-', label='Laser Angle - (R3H2)')
            im136, = a2.plot([], [], 'o-', label='Laser Angle - (R3H3)')
            im137, = a2.plot([], [], 'o-', label='Laser Angle - (R3H4)')
            im138, = a2.plot([], [], 'o-', label='Laser Angle - (R4H1)')
            im139, = a2.plot([], [], 'o-', label='Laser Angle - (R4H2)')
            im140, = a2.plot([], [], 'o-', label='Laser Angle - (R4H3)')
            im141, = a2.plot([], [], 'o-', label='Laser Angle - (R4H4)')
            # -----------------------------------------------------------------
            im142, = a6.plot([], [], 'o-', label='Laser Angle')
            im143, = a6.plot([], [], 'o-', label='Laser Angle')
            im144, = a6.plot([], [], 'o-', label='Laser Angle')
            im145, = a6.plot([], [], 'o-', label='Laser Angle')
            im146, = a6.plot([], [], 'o-', label='Laser Angle')
            im147, = a6.plot([], [], 'o-', label='Laser Angle')
            im148, = a6.plot([], [], 'o-', label='Laser Angle')
            im149, = a6.plot([], [], 'o-', label='Laser Angle')
            im150, = a6.plot([], [], 'o-', label='Laser Angle')
            im151, = a6.plot([], [], 'o-', label='Laser Angle')
            im152, = a6.plot([], [], 'o-', label='Laser Angle')
            im153, = a6.plot([], [], 'o-', label='Laser Angle')
            im154, = a6.plot([], [], 'o-', label='Laser Angle')
            im155, = a6.plot([], [], 'o-', label='Laser Angle')
            im156, = a6.plot([], [], 'o-', label='Laser Angle')
            im157, = a6.plot([], [], 'o-', label='Laser Angle')
            # -----------------------------------------[Tape Placement]
            im158, = a2.plot([], [], 'o-', label='Tape Placement - (R1H1)')
            im159, = a2.plot([], [], 'o-', label='Tape Placement - (R1H2)')
            im160, = a2.plot([], [], 'o-', label='Tape Placement - (R1H3)')
            im161, = a2.plot([], [], 'o-', label='Tape Placement - (R1H4)')
            im162, = a2.plot([], [], 'o-', label='Tape Placement - (R2H1)')
            im163, = a2.plot([], [], 'o-', label='Tape Placement - (R2H2)')
            im164, = a2.plot([], [], 'o-', label='Tape Placement - (R2H3)')
            im165, = a2.plot([], [], 'o-', label='Tape Placement - (R2H4)')
            im166, = a2.plot([], [], 'o-', label='Tape Placement - (R3H1)')
            im167, = a2.plot([], [], 'o-', label='Tape Placement - (R3H2)')
            im168, = a2.plot([], [], 'o-', label='Tape Placement - (R3H3)')
            im169, = a2.plot([], [], 'o-', label='Tape Placement - (R3H4)')
            im170, = a2.plot([], [], 'o-', label='Tape Placement - (R4H1)')
            im171, = a2.plot([], [], 'o-', label='Tape Placement - (R4H2)')
            im172, = a2.plot([], [], 'o-', label='Tape Placement - (R4H3)')
            im173, = a2.plot([], [], 'o-', label='Tape Placement - (R4H4)')
            # -----------------------------------------------------------------
            im174, = a6.plot([], [], 'o-', label='Tape Placement')
            im175, = a6.plot([], [], 'o-', label='Tape Placement')
            im176, = a6.plot([], [], 'o-', label='Tape Placement')
            im177, = a6.plot([], [], 'o-', label='Tape Placement')
            im178, = a6.plot([], [], 'o-', label='Tape Placement')
            im179, = a6.plot([], [], 'o-', label='Tape Placement')
            im180, = a6.plot([], [], 'o-', label='Tape Placement')
            im181, = a6.plot([], [], 'o-', label='Tape Placement')
            im182, = a6.plot([], [], 'o-', label='Tape Placement')
            im183, = a6.plot([], [], 'o-', label='Tape Placement')
            im184, = a6.plot([], [], 'o-', label='Tape Placement')
            im185, = a6.plot([], [], 'o-', label='Tape Placement')
            im186, = a6.plot([], [], 'o-', label='Tape Placement')
            im187, = a6.plot([], [], 'o-', label='Tape Placement')
            im188, = a6.plot([], [], 'o-', label='Tape Placement')
            im189, = a6.plot([], [], 'o-', label='Tape Placement')
            # --------------------------------------------------[Roller Force T8]
            im190, = a2.plot([], [], 'o-', label='Roller Force - (R1H1)')
            im191, = a2.plot([], [], 'o-', label='Roller Force - (R1H2)')
            im192, = a2.plot([], [], 'o-', label='Roller Force - (R1H3)')
            im193, = a2.plot([], [], 'o-', label='Roller Force - (R1H4)')
            im194, = a2.plot([], [], 'o-', label='Roller Force - (R2H1)')
            im195, = a2.plot([], [], 'o-', label='Roller Force - (R2H2)')
            im196, = a2.plot([], [], 'o-', label='Roller Force - (R2H3)')
            im197, = a2.plot([], [], 'o-', label='Roller Force - (R2H4)')
            im198, = a2.plot([], [], 'o-', label='Roller Force - (R3H1)')
            im199, = a2.plot([], [], 'o-', label='Roller Force - (R3H2)')
            im200, = a2.plot([], [], 'o-', label='Roller Force - (R3H3)')
            im201, = a2.plot([], [], 'o-', label='Roller Force - (R3H4)')
            im202, = a2.plot([], [], 'o-', label='Roller Force - (R4H1)')
            im203, = a2.plot([], [], 'o-', label='Roller Force - (R4H2)')
            im204, = a2.plot([], [], 'o-', label='Roller Force - (R4H3)')
            im205, = a2.plot([], [], 'o-', label='Roller Force - (R4H4)')
            # -----------------------------------------------------------------
            im206, = a6.plot([], [], 'o-', label='Roller Force')
            im207, = a6.plot([], [], 'o-', label='Roller Force')
            im208, = a6.plot([], [], 'o-', label='Roller Force')
            im209, = a6.plot([], [], 'o-', label='Roller Force')
            im210, = a6.plot([], [], 'o-', label='Roller Force')
            im211, = a6.plot([], [], 'o-', label='Roller Force')
            im212, = a6.plot([], [], 'o-', label='Roller Force')
            im213, = a6.plot([], [], 'o-', label='Roller Force')
            im214, = a6.plot([], [], 'o-', label='Roller Force')
            im215, = a6.plot([], [], 'o-', label='Roller Force')
            im216, = a6.plot([], [], 'o-', label='Roller Force')
            im217, = a6.plot([], [], 'o-', label='Roller Force')
            im218, = a6.plot([], [], 'o-', label='Roller Force')
            im219, = a6.plot([], [], 'o-', label='Roller Force')
            im220, = a6.plot([], [], 'o-', label='Roller Force')
            im221, = a6.plot([], [], 'o-', label='Roller Force')
            # ---------------- EXECUTE SYNCHRONOUS METHOD -----------------------------#

        def synchronousEoL(dnv_Size, dnv_gType, fetchT):
            fetch_no = str(fetchT)  # entry value in string sql syntax

            # Initialise SQL Data connection per listed Table --------------------[]
            if EoLRep == 'DNV':
                eol1, eol2, eol3, eol4 = conn.cursor(), conn.cursor(), conn.cursor(), conn.cursor()
            elif EoLRep == 'MGM':
                eol1, eol2, eol3, eol4, eol5, eol6, eol7, eol8 = (conn.cursor(), conn.cursor(), conn.cursor(),
                                                                  conn.cursor(), conn.cursor(), conn.cursor(),
                                                                  conn.cursor(), conn.cursor())
            else:
                pass  # reserved for bespoke configuration

            """
            Load watchdog function with synchronous function every seconds
            """
            # Initialise variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard  # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                # Latch on SQL Query only a
                import sqlArrayRLmethodEoL as sel                  # DrLabs optimization method

                inProgress = False                                  # True for RetroPlay mode
                print('\nAsynchronous controller activated...')

                if not sysRun:
                    sysRun, msctcp, msc_rt = wd.autoPausePlay()     # Retrieve MSC from Watchdog
                print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                # Get list of relevant SQL Tables using conn() --------------------[]
                if keyboard.is_pressed(
                        "Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:  # Terminate file-fetch
                    print('\nProduction is pausing...')
                    if not autoSpcPause:
                        autoSpcRun = not autoSpcRun
                        autoSpcPause = True
                        print("\nVisualization in Paused Mode...")

                    else:
                        autoSpcPause = False
                        print("Visualization in Play Mode...")

                else:
                    # ------ Process data fetch sequences --------------------------#
                    if EoLRep == 'DNV':
                        rpTT, rpST, rpTG, rpRM = sel.dnv_sqlexec(smp_Sz, stp_Sz, eol1, eol2, eol3, eol4, T1, T2, T3, T4,  fetch_no)
                    elif EoLRep == 'MGM':
                        rpTT, rpST, rpTG, rpRM, rpLP, rpLA, rpTP, rpRF = sel.mgm_sqlexec(smp_Sz, stp_Sz, eol1, eol2, eol3, eol4, eol5, eol6, eol7, eol8, T1, T2, T3, T4, T5, T6, T7, T8, fetch_no)
                    else:
                        pass            # reserved for bespoke user selection ------#
                    print("Visualization in Play Mode...")
                print('\nUpdating....')

                # ------ Inhibit iteration ----------------------------------------------------------[]
                """
                # Set condition for halting real-time plots in watchdog class ---------------------
                """
                # TODO --- values for inhibiting the SQL processing
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    eol1.close()
                    eol2.close()
                    eol3.close()
                    eol4.close()
                    if EoLRep == 'MGM':
                        eol5.close()
                        eol6.close()
                        eol7.close()
                        eol8.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

            if EoLRep == 'DNV':
                return rpTT, rpST, rpTG, rpRM
            else:
                return rpTT, rpST, rpTG, rpRM, rpLP, rpLA, rpTP, rpRF

        # ================== End of synchronous Method ==========================
        def asynchronousEoL(db_freq):
            timei = time.time()  # start timing the entire loop

            # Obtain fetch SQl data from respective Tables ------------#
            if EoLRep == 'DNV':
                rdTT, rdST, rdTG, rdRM = synchronousEoL(smp_Sz, stp_Sz, db_freq)
            else:
                rdTT, rdST, rdTG, rdRM, rdLP, rdLA, rdTP, rdRF = synchronousEoL(smp_Sz, stp_Sz, db_freq)

            # ttData = synchronousTT(ttSize, ttgType, db_freq)  # data loading functions
            # rmData = synchronousTS(smp_Sz, stp_Sz, db_freq)   # Accumulated Gap Mean Profile
            # rmData = synchronousTG(smp_Sz, stp_Sz, db_freq)   # Accumulated Gap Mean Profile
            # --------------------------------------------------#

            import varSQL_DFeol as el                            # load SQL variables column names | rfVarSQL

            viz_cycle = 150
            if EoLRep == 'DNV':
                g1 = eol.validCols(T1)                           # Construct Table Column (Tape Temp)
                d1 = pd.DataFrame(rdTT, columns=g1)
                g2 = eol.validCols(T2)                           # Construct Table Column (Sub Temp)
                d2 = pd.DataFrame(rdST, columns=g2)
                g3 = eol.validCols(T3)                           # Construct Table Column (Tape Gap)
                d3 = pd.DataFrame(rdTG, columns=g3)
                g4 = eol.validCols(T4)                           # Construct Table Column (Tape Gap)
                d4 = pd.DataFrame(rdRM, columns=g4)
                # Concatenate all columns -----------[]
                df1 = pd.concat([d1, d2, d3, d4], axis=1)
            elif EoLRep == 'MGM':
                g1 = eol.validCols(T1)                          # Construct Table Column (Tape Temp)
                d1 = pd.DataFrame(rdTT, columns=g1)
                g2 = eol.validCols(T2)                          # Construct Table Column (Sub Temp)
                d2 = pd.DataFrame(rdST, columns=g2)
                g3 = eol.validCols(T3)                          # Construct Table Column (Tape Gap)
                d3 = pd.DataFrame(rdTG, columns=g3)
                g4 = eol.validCols(T4)                          # Construct Table Column (Tape Gap)
                d4 = pd.DataFrame(rdRM, columns=g4)
                # ---------------------------------
                g5 = qpm.validCols(T5)                          # Laser Power
                d5 = pd.DataFrame(rdLP, columns=g5)
                g6 = qpm.validCols(T6)                          # Laser Angle
                d6 = pd.DataFrame(rdLA, columns=g6)
                g7= qpm.validCols(T7)                           # Tape Placement
                d7 = pd.DataFrame( rdTP, columns=g7)
                g8 = qpm.validCols(T8)                          # Roller Force
                d8 = pd.DataFrame( rdRF, columns=g8)
                # Concatenate all columns -----------[]
                df1 = pd.concat([d1, d2, d3, d4, d5, d6, d7, d8], axis=1)
            else:
                df1 = 0
                pass

            # ----- Access data element within the concatenated columns -------------------------[A]
            EL = el.loadProcesValues(df1, EoLRep)
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
            # ------------------------------- S Plot
            im42.set_xdata(np.arange(db_freq))
            im43.set_xdata(np.arange(db_freq))
            im44.set_xdata(np.arange(db_freq))
            im45.set_xdata(np.arange(db_freq))
            im46.set_xdata(np.arange(db_freq))
            im47.set_xdata(np.arange(db_freq))
            im48.set_xdata(np.arange(db_freq))
            im49.set_xdata(np.arange(db_freq))
            im50.set_xdata(np.arange(db_freq))
            im51.set_xdata(np.arange(db_freq))
            im52.set_xdata(np.arange(db_freq))
            im53.set_xdata(np.arange(db_freq))
            im54.set_xdata(np.arange(db_freq))
            im55.set_xdata(np.arange(db_freq))
            im56.set_xdata(np.arange(db_freq))
            im56.set_xdata(np.arange(db_freq))
            # ------------------------------- S Plot
            im57.set_xdata(np.arange(db_freq))
            im58.set_xdata(np.arange(db_freq))
            im59.set_xdata(np.arange(db_freq))
            im60.set_xdata(np.arange(db_freq))
            im61.set_xdata(np.arange(db_freq))
            im62.set_xdata(np.arange(db_freq))
            im63.set_xdata(np.arange(db_freq))
            im64.set_xdata(np.arange(db_freq))
            im65.set_xdata(np.arange(db_freq))
            im66.set_xdata(np.arange(db_freq))
            im67.set_xdata(np.arange(db_freq))
            im68.set_xdata(np.arange(db_freq))
            im69.set_xdata(np.arange(db_freq))
            im70.set_xdata(np.arange(db_freq))
            im71.set_xdata(np.arange(db_freq))
            im72.set_xdata(np.arange(db_freq))
            # ------------------------------- S Plot
            im73.set_xdata(np.arange(db_freq))
            im74.set_xdata(np.arange(db_freq))
            im75.set_xdata(np.arange(db_freq))
            im76.set_xdata(np.arange(db_freq))
            im77.set_xdata(np.arange(db_freq))
            im78.set_xdata(np.arange(db_freq))
            im79.set_xdata(np.arange(db_freq))
            im80.set_xdata(np.arange(db_freq))
            im81.set_xdata(np.arange(db_freq))
            im82.set_xdata(np.arange(db_freq))
            im83.set_xdata(np.arange(db_freq))
            im84.set_xdata(np.arange(db_freq))
            im85.set_xdata(np.arange(db_freq))
            im86.set_xdata(np.arange(db_freq))
            im87.set_xdata(np.arange(db_freq))
            im88.set_xdata(np.arange(db_freq))
            im89.set_xdata(np.arange(db_freq))
            # --------------------------------
            im90.set_xdata(np.arange(db_freq))
            im91.set_xdata(np.arange(db_freq))
            im92.set_xdata(np.arange(db_freq))
            im93.set_xdata(np.arange(db_freq))
            im94.set_xdata(np.arange(db_freq))
            im95.set_xdata(np.arange(db_freq))
            im96.set_xdata(np.arange(db_freq))
            im97.set_xdata(np.arange(db_freq))
            im98.set_xdata(np.arange(db_freq))
            im99.set_xdata(np.arange(db_freq))
            im100.set_xdata(np.arange(db_freq))
            im101.set_xdata(np.arange(db_freq))
            im102.set_xdata(np.arange(db_freq))
            im103.set_xdata(np.arange(db_freq))
            im104.set_xdata(np.arange(db_freq))
            im105.set_xdata(np.arange(db_freq))
            im106.set_xdata(np.arange(db_freq))
            # -------------------------------
            im107.set_xdata(np.arange(db_freq))
            im108.set_xdata(np.arange(db_freq))
            im109.set_xdata(np.arange(db_freq))
            im110.set_xdata(np.arange(db_freq))
            im111.set_xdata(np.arange(db_freq))
            im112.set_xdata(np.arange(db_freq))
            im113.set_xdata(np.arange(db_freq))
            im114.set_xdata(np.arange(db_freq))
            im115.set_xdata(np.arange(db_freq))
            im116.set_xdata(np.arange(db_freq))
            im117.set_xdata(np.arange(db_freq))
            im118.set_xdata(np.arange(db_freq))
            im119.set_xdata(np.arange(db_freq))
            im120.set_xdata(np.arange(db_freq))
            im121.set_xdata(np.arange(db_freq))
            im122.set_xdata(np.arange(db_freq))
            im123.set_xdata(np.arange(db_freq))
            # -------------------------------
            im124.set_xdata(np.arange(db_freq))
            im125.set_xdata(np.arange(db_freq))
            im126.set_xdata(np.arange(db_freq))
            im127.set_xdata(np.arange(db_freq))
            im128.set_xdata(np.arange(db_freq))
            im129.set_xdata(np.arange(db_freq))
            im130.set_xdata(np.arange(db_freq))
            im131.set_xdata(np.arange(db_freq))
            im132.set_xdata(np.arange(db_freq))
            im133.set_xdata(np.arange(db_freq))
            im134.set_xdata(np.arange(db_freq))
            im135.set_xdata(np.arange(db_freq))
            im136.set_xdata(np.arange(db_freq))
            im137.set_xdata(np.arange(db_freq))
            im138.set_xdata(np.arange(db_freq))
            im139.set_xdata(np.arange(db_freq))
            im140.set_xdata(np.arange(db_freq))
            # --------------------------------
            im141.set_xdata(np.arange(db_freq))
            im142.set_xdata(np.arange(db_freq))
            im143.set_xdata(np.arange(db_freq))
            im144.set_xdata(np.arange(db_freq))
            im145.set_xdata(np.arange(db_freq))
            im146.set_xdata(np.arange(db_freq))
            im147.set_xdata(np.arange(db_freq))
            im148.set_xdata(np.arange(db_freq))
            im149.set_xdata(np.arange(db_freq))
            im150.set_xdata(np.arange(db_freq))
            im151.set_xdata(np.arange(db_freq))
            im152.set_xdata(np.arange(db_freq))
            im153.set_xdata(np.arange(db_freq))
            im154.set_xdata(np.arange(db_freq))
            im155.set_xdata(np.arange(db_freq))
            im156.set_xdata(np.arange(db_freq))
            im157.set_xdata(np.arange(db_freq))
            # --------------------------------
            im158.set_xdata(np.arange(db_freq))
            im159.set_xdata(np.arange(db_freq))
            im160.set_xdata(np.arange(db_freq))
            im161.set_xdata(np.arange(db_freq))
            im162.set_xdata(np.arange(db_freq))
            im163.set_xdata(np.arange(db_freq))
            im164.set_xdata(np.arange(db_freq))
            im165.set_xdata(np.arange(db_freq))
            im166.set_xdata(np.arange(db_freq))
            im167.set_xdata(np.arange(db_freq))
            im168.set_xdata(np.arange(db_freq))
            im169.set_xdata(np.arange(db_freq))
            im170.set_xdata(np.arange(db_freq))
            im171.set_xdata(np.arange(db_freq))
            im172.set_xdata(np.arange(db_freq))
            im173.set_xdata(np.arange(db_freq))
            im174.set_xdata(np.arange(db_freq))
            # --------------------------------
            im175.set_xdata(np.arange(db_freq))
            im176.set_xdata(np.arange(db_freq))
            im177.set_xdata(np.arange(db_freq))
            im178.set_xdata(np.arange(db_freq))
            im179.set_xdata(np.arange(db_freq))
            im180.set_xdata(np.arange(db_freq))
            im181.set_xdata(np.arange(db_freq))
            im182.set_xdata(np.arange(db_freq))
            im183.set_xdata(np.arange(db_freq))
            im184.set_xdata(np.arange(db_freq))
            im185.set_xdata(np.arange(db_freq))
            im186.set_xdata(np.arange(db_freq))
            im187.set_xdata(np.arange(db_freq))
            im188.set_xdata(np.arange(db_freq))
            im189.set_xdata(np.arange(db_freq))
            im190.set_xdata(np.arange(db_freq))
            im191.set_xdata(np.arange(db_freq))
            # --------------------------------
            im192.set_xdata(np.arange(db_freq))
            im193.set_xdata(np.arange(db_freq))
            im194.set_xdata(np.arange(db_freq))
            im195.set_xdata(np.arange(db_freq))
            im196.set_xdata(np.arange(db_freq))
            im197.set_xdata(np.arange(db_freq))
            im198.set_xdata(np.arange(db_freq))
            im199.set_xdata(np.arange(db_freq))
            im200.set_xdata(np.arange(db_freq))
            im201.set_xdata(np.arange(db_freq))
            im202.set_xdata(np.arange(db_freq))
            im203.set_xdata(np.arange(db_freq))
            im204.set_xdata(np.arange(db_freq))
            im205.set_xdata(np.arange(db_freq))
            im206.set_xdata(np.arange(db_freq))
            im207.set_xdata(np.arange(db_freq))
            im208.set_xdata(np.arange(db_freq))
            # --------------------------------
            im209.set_xdata(np.arange(db_freq))
            im210.set_xdata(np.arange(db_freq))
            im211.set_xdata(np.arange(db_freq))
            im212.set_xdata(np.arange(db_freq))
            im213.set_xdata(np.arange(db_freq))
            im214.set_xdata(np.arange(db_freq))
            im215.set_xdata(np.arange(db_freq))
            im216.set_xdata(np.arange(db_freq))
            im217.set_xdata(np.arange(db_freq))
            im218.set_xdata(np.arange(db_freq))

            if EoLRep == 'DNV':
                # X Plot Y-Axis data points for XBar ---------------------------------------------[ Mean T1 ]
                im10.set_ydata((EL[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
                im11.set_ydata((EL[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 2
                im12.set_ydata((EL[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 3
                im13.set_ydata((EL[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 4
                im14.set_ydata((EL[4]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
                im15.set_ydata((EL[5]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 2
                im16.set_ydata((EL[6]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 3
                im17.set_ydata((EL[7]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 4
                im18.set_ydata((EL[8]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
                im19.set_ydata((EL[9]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 2
                im20.set_ydata((EL[10]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 3
                im21.set_ydata((EL[11]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 4
                im22.set_ydata((EL[12]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
                im23.set_ydata((EL[13]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 2
                im24.set_ydata((EL[14]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 3
                im25.set_ydata((EL[15]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 4
                # ---------------------------------------[T1 std Dev]
                im26.set_ydata((EL[0]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im27.set_ydata((EL[1]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im28.set_ydata((EL[2]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im29.set_ydata((EL[3]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im30.set_ydata((EL[4]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im31.set_ydata((EL[5]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im32.set_ydata((EL[6]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im33.set_ydata((EL[7]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im34.set_ydata((EL[8]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im35.set_ydata((EL[9]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im36.set_ydata((EL[10]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im37.set_ydata((EL[11]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im38.set_ydata((EL[12]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im39.set_ydata((EL[13]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im40.set_ydata((EL[14]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im41.set_ydata((EL[15]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                # -----------------------------------------------------------------------------[Mean T2]
                im42.set_ydata((EL[16]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im43.set_ydata((EL[17]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im44.set_ydata((EL[18]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im45.set_ydata((EL[19]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im46.set_ydata((EL[20]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im47.set_ydata((EL[21]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im48.set_ydata((EL[22]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im49.set_ydata((EL[23]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im50.set_ydata((EL[24]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im51.set_ydata((EL[25]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im52.set_ydata((EL[26]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im53.set_ydata((EL[27]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im54.set_ydata((EL[28]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im55.set_ydata((EL[29]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im56.set_ydata((EL[30]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im57.set_ydata((EL[31]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                # ---------------------------------------[T2 std Dev]
                im58.set_ydata((EL[16]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im59.set_ydata((EL[17]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im60.set_ydata((EL[18]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im61.set_ydata((EL[19]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im62.set_ydata((EL[20]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im63.set_ydata((EL[21]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im64.set_ydata((EL[22]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im65.set_ydata((EL[23]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im66.set_ydata((EL[24]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im67.set_ydata((EL[25]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im68.set_ydata((EL[26]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im69.set_ydata((EL[27]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im70.set_ydata((EL[28]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im71.set_ydata((EL[29]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im72.set_ydata((EL[30]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im73.set_ydata((EL[31]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                # -----------------------------------------------------------------------------[Mean T3]
                im74.set_ydata((EL[32]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im75.set_ydata((EL[33]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im76.set_ydata((EL[34]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im77.set_ydata((EL[35]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im78.set_ydata((EL[36]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im79.set_ydata((EL[37]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im80.set_ydata((EL[38]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im81.set_ydata((EL[39]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                # ---------------------------------------[T3 std Dev]
                im82.set_ydata((EL[32]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im83.set_ydata((EL[33]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im84.set_ydata((EL[34]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im85.set_ydata((EL[35]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im86.set_ydata((EL[36]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im87.set_ydata((EL[37]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im88.set_ydata((EL[38]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im89.set_ydata((EL[39]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                # --------------------------------------------------------------------------- [Ramp (Sum9) T4]
                # EL[40] ---------> 'tStamp' |  EL[45] --->PipeDir' | EL[46] ----> 'cLayer'
                im90.set_ydata((EL[41]).rolling(window=smp_Sz, min_periods=1).sum()[0:db_freq])
                im91.set_ydata((EL[42]).rolling(window=smp_Sz, min_periods=1).sum()[0:db_freq])
                im92.set_ydata((EL[43]).rolling(window=smp_Sz, min_periods=1).sum()[0:db_freq])
                im93.set_ydata((EL[44]).rolling(window=smp_Sz, min_periods=1).sum()[0:db_freq])
                # Compute entire Process Capability ------------------------------------------#

            elif EoLRep == 'MGM':
                # X Plot Y-Axis data points for XBar -----------------------------------------[  # Ring 1 ]
                im10.set_ydata((EL[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
                im11.set_ydata((EL[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 2
                im12.set_ydata((EL[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 3
                im13.set_ydata((EL[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 4
                im14.set_ydata((EL[4]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
                im15.set_ydata((EL[5]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 2
                im16.set_ydata((EL[6]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 3
                im17.set_ydata((EL[7]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 4
                im18.set_ydata((EL[8]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
                im19.set_ydata((EL[9]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 2
                im20.set_ydata((EL[10]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 3
                im21.set_ydata((EL[11]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 4
                im22.set_ydata((EL[12]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
                im23.set_ydata((EL[13]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 2
                im24.set_ydata((EL[14]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 3
                im25.set_ydata((EL[15]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 4
                # ---------------------------------------[T1 std Dev]
                im26.set_ydata((EL[0]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im27.set_ydata((EL[1]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im28.set_ydata((EL[2]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im29.set_ydata((EL[3]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im30.set_ydata((EL[4]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im31.set_ydata((EL[5]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im32.set_ydata((EL[6]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im33.set_ydata((EL[7]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im34.set_ydata((EL[8]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im35.set_ydata((EL[9]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im36.set_ydata((EL[10]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im37.set_ydata((EL[11]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im38.set_ydata((EL[12]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im39.set_ydata((EL[13]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im40.set_ydata((EL[14]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im41.set_ydata((EL[15]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                # -----------------------------------------------------------------------------[Mean T2]
                im42.set_ydata((EL[16]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im43.set_ydata((EL[17]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im44.set_ydata((EL[18]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im45.set_ydata((EL[19]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im46.set_ydata((EL[20]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im47.set_ydata((EL[21]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im48.set_ydata((EL[22]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im49.set_ydata((EL[23]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im50.set_ydata((EL[24]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im51.set_ydata((EL[25]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im52.set_ydata((EL[26]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im53.set_ydata((EL[27]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im54.set_ydata((EL[28]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im55.set_ydata((EL[29]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im56.set_ydata((EL[30]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im57.set_ydata((EL[31]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                # ---------------------------------------[T2 std Dev]
                im58.set_ydata((EL[16]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im59.set_ydata((EL[17]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im60.set_ydata((EL[18]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im61.set_ydata((EL[19]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im62.set_ydata((EL[20]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im63.set_ydata((EL[21]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im64.set_ydata((EL[22]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im65.set_ydata((EL[23]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im66.set_ydata((EL[24]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im67.set_ydata((EL[25]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im68.set_ydata((EL[26]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im69.set_ydata((EL[27]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im70.set_ydata((EL[28]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im71.set_ydata((EL[29]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im72.set_ydata((EL[30]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im73.set_ydata((EL[31]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                # -----------------------------------------------------------------------------[Mean T3]
                im74.set_ydata((EL[32]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im75.set_ydata((EL[33]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im76.set_ydata((EL[34]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im77.set_ydata((EL[35]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im78.set_ydata((EL[36]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im79.set_ydata((EL[37]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im80.set_ydata((EL[38]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im81.set_ydata((EL[39]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                # ---------------------------------------[T3 std Dev]
                im82.set_ydata((EL[32]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im83.set_ydata((EL[33]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im84.set_ydata((EL[34]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im85.set_ydata((EL[35]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im86.set_ydata((EL[36]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im87.set_ydata((EL[37]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im88.set_ydata((EL[38]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im89.set_ydata((EL[39]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                # --------------------------------------------------------------------------- [Ramp (Sum9) T4]
                # EL[40] ---------> 'tStamp' |  EL[45] --->PipeDir' | EL[46] ----> 'cLayer'
                im90.set_ydata((EL[41]).rolling(window=smp_Sz, min_periods=1).sum()[0:db_freq])
                im91.set_ydata((EL[42]).rolling(window=smp_Sz, min_periods=1).sum()[0:db_freq])
                im92.set_ydata((EL[43]).rolling(window=smp_Sz, min_periods=1).sum()[0:db_freq])
                im93.set_ydata((EL[44]).rolling(window=smp_Sz, min_periods=1).sum()[0:db_freq])
                # ------ Evaluate Pp for Ring 1 ---------#
                # ---------------------------------------# start EL[87] ---------------------------[Mean T5]
                im94.set_ydata((EL[47]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
                im95.set_ydata((EL[48]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 2
                im96.set_ydata((EL[49]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 3
                im97.set_ydata((EL[50]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 4
                im98.set_ydata((EL[51]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
                im99.set_ydata((EL[52]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 2
                im100.set_ydata((EL[53]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 3
                im101.set_ydata((EL[54]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 4
                im102.set_ydata((EL[55]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
                im103.set_ydata((EL[56]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 2
                im104.set_ydata((EL[57]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 3
                im105.set_ydata((EL[58]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 4
                im106.set_ydata((EL[59]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im107.set_ydata((EL[60]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im108.set_ydata((EL[61]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im109.set_ydata((EL[62]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                # ---------------------------------------#[Stddev]
                im110.set_ydata((EL[47]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im111.set_ydata((EL[48]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im112.set_ydata((EL[49]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im113.set_ydata((EL[50]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im114.set_ydata((EL[51]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im115.set_ydata((EL[52]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im116.set_ydata((EL[53]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im117.set_ydata((EL[54]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im118.set_ydata((EL[55]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im119.set_ydata((EL[56]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im120.set_ydata((EL[57]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im121.set_ydata((EL[58]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im122.set_ydata((EL[59]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im123.set_ydata((EL[60]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im124.set_ydata((EL[61]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im125.set_ydata((EL[62]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                # ---------------------------------------------------------------------------------[Mean T6]
                im126.set_ydata((EL[63]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im127.set_ydata((EL[64]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im128.set_ydata((EL[65]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im129.set_ydata((EL[66]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im130.set_ydata((EL[67]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im131.set_ydata((EL[68]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im132.set_ydata((EL[69]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im133.set_ydata((EL[70]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im134.set_ydata((EL[71]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im135.set_ydata((EL[72]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im136.set_ydata((EL[73]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im137.set_ydata((EL[74]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im138.set_ydata((EL[75]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im139.set_ydata((EL[76]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im140.set_ydata((EL[77]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im141.set_ydata((EL[78]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                # ---------------------------------------#
                im142.set_ydata((EL[63]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im143.set_ydata((EL[64]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im144.set_ydata((EL[65]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im145.set_ydata((EL[66]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im146.set_ydata((EL[67]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im147.set_ydata((EL[68]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im148.set_ydata((EL[69]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im149.set_ydata((EL[70]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im150.set_ydata((EL[71]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im151.set_ydata((EL[72]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im152.set_ydata((EL[73]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im153.set_ydata((EL[74]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im154.set_ydata((EL[75]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im155.set_ydata((EL[76]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im156.set_ydata((EL[77]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im157.set_ydata((EL[78]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                # ------------------------------------------------------------------------------[Mean T7]
                im158.set_ydata((EL[79]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im159.set_ydata((EL[80]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im160.set_ydata((EL[81]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im161.set_ydata((EL[82]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im162.set_ydata((EL[83]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im163.set_ydata((EL[84]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im164.set_ydata((EL[85]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im165.set_ydata((EL[86]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im166.set_ydata((EL[87]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im167.set_ydata((EL[88]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im168.set_ydata((EL[89]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im169.set_ydata((EL[90]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im170.set_ydata((EL[91]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im171.set_ydata((EL[92]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im172.set_ydata((EL[93]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im173.set_ydata((EL[94]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                # -----------------------------------------------#
                im174.set_ydata((EL[79]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im175.set_ydata((EL[80]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im176.set_ydata((EL[81]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im177.set_ydata((EL[82]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im178.set_ydata((EL[83]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im179.set_ydata((EL[84]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im180.set_ydata((EL[85]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im181.set_ydata((EL[86]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im182.set_ydata((EL[87]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im183.set_ydata((EL[88]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im184.set_ydata((EL[89]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im185.set_ydata((EL[90]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im186.set_ydata((EL[91]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im187.set_ydata((EL[92]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im188.set_ydata((EL[93]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im189.set_ydata((EL[94]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                # ------------------------------------------------------------------------------[Mean T8]
                im190.set_ydata((EL[95]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im191.set_ydata((EL[96]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im192.set_ydata((EL[97]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im193.set_ydata((EL[98]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im194.set_ydata((EL[99]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im195.set_ydata((EL[100]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im196.set_ydata((EL[101]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im197.set_ydata((EL[102]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im198.set_ydata((EL[103]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im199.set_ydata((EL[104]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im200.set_ydata((EL[105]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im201.set_ydata((EL[106]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im202.set_ydata((EL[107]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im203.set_ydata((EL[108]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im204.set_ydata((EL[109]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                im205.set_ydata((EL[110]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])
                # -------------------------------------------------
                im206.set_ydata((EL[95]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im207.set_ydata((EL[96]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im208.set_ydata((EL[97]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im209.set_ydata((EL[98]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im210.set_ydata((EL[99]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im211.set_ydata((EL[100]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im212.set_ydata((EL[101]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im213.set_ydata((EL[102]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im214.set_ydata((EL[103]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im215.set_ydata((EL[104]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im216.set_ydata((EL[105]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im217.set_ydata((EL[106]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im218.set_ydata((EL[107]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im219.set_ydata((EL[108]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im220.set_ydata((EL[109]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                im221.set_ydata((EL[110]).rolling(window=smp_Sz, min_periods=1).std()[0:db_freq])
                # Compute entire Process Capability ------------------------------------------#

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
                a2.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a1.set_xlim(0, window_Xmax)
                a2.set_xlim(0, window_Xmax)

            # Set trip line for individual time-series plot -----------------------------------[R1]
            import triggerModule as sigma
            sigma.trigViolations(a1, UsePLC_DBS, 'EOL', YScale_minEOL, YScale_maxEOL, xucT, xlcT, xusT, xlsT, mnT, sdT)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousEoL, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)


class collectiveEoP(ttk.Frame):                                # End of Layer Progressive Report Tabb
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        # self.grid(column=0, row=0, padx=10, pady=10)
        self.place(x=10, y=10)
        self.createWidgets()

    def createWidgets(self):
        label = ttk.Label(self, text="End of Pipe Report:                                          ", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        # Define Axes ---------------------#
        combo = ttk.Combobox(self, values=["= Select Process Parameter =", "Roller Force",
                                           "Tape Temperature", "Subs Temperature", "Laser Power",
                                           "Laser Angle", "Tape Placement Error",
                                           "Tape Gap Polarisation"], width=25)
        combo.place(x=520, y=10)
        combo.current(0)

        # Create empty Text Space -----------------------------------
        text_widget = tk.Text(self, wrap='word', width=110, height=80)
        text_widget.pack(padx=10, pady=10)

        def option_selected(event):
            selected_option = combo.get()
            if selected_option == "Roller Pressure":
                rpt = "RPT_RP_" + str(processWON[0])
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder
            elif selected_option == "Tape Temperature":
                rpt = "RPT_TT_" + str(processWON[0])
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder
            elif selected_option == "Subs Temperature":
                rpt = "RPT_ST_" + str(processWON[0])
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder
            elif selected_option == "Winding Speed":
                rpt = "RPT_WS_" + str(processWON[0])
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder
            elif selected_option == "Gap Measurement":
                rpt = "RPT_TG_" + str(processWON[0])
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder
            else:
                rpt = "VOID_REPORT"
                readEoP(text_widget, rpt)

            print("You selected:", selected_option)
        combo.bind("<<ComboboxSelected>>", option_selected)

        # Update Canvas -----------------------------------------------------[NO FIGURE YET]
        # canvas = FigureCanvasTkAgg(fig, self)
        # canvas.get_tk_widget().pack(expand=False)

        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True)
# --------------------------------------------- COMMON VIEW CLASS OBJECTS -----------------[A]


class common_rampCount(ttk.Frame):
    # compute ram Count against cumulative layers ramp count --------[A]
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=20)
        self.createWidgets()

    def createWidgets(self):
        # -----------------------------------
        f = Figure(figsize=(9, 4), dpi=100)
        f.subplots_adjust(left=0.083, bottom=0.11, right=0.976, top=0.99, wspace=0.202)
        a1 = f.add_subplot(1, 1, 1)

        # Model data -----------------------------------------------[]
        # a3.cla()
        a1.get_yaxis().set_visible(True)
        a1.get_xaxis().set_visible(True)

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends

        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minRP, YScale_maxRP = 0, vCount                      # Ramp Count Profile (Per segment)
        window_Xmin, window_Xmax = 0, pExLayer                      # windows view = visible data points

        # Load SQL Query Table -------------------------------------#
        rcData = WON + '_RC'                                         # Identify Table
        # ----------------------------------------------------------#

        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a1.legend(loc='upper right', title='Cumulative Ramp Count')
        a1.set_ylabel("Cumulative Ramp Count / Segment")
        a1.set_xlabel("Pipe Nominal Layer")
        # ----------------------------------------------------------#

        a1.set_ylim([YScale_minRP, YScale_maxRP], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])

        # ------- plot ramp count ------------[]
        im10, = a1.plot([], [], 'o-', label='Ramp Count - Ring 1')                  # ramp count all layers
        im11, = a1.plot([], [], 'o-', label='Ramp Count - Ring 2')                  # ramp count all layers
        im12, = a1.plot([], [], 'o-', label='Ramp Count - Ring 3')                  # ramp count all layers
        im13, = a1.plot([], [], 'o-', label='Ramp Count - Ring 4')                  # ramp count all layers
        im14, = a1.plot([], [], 'o-', label='Cumulative Ramp Count - All Rings')    # ramp count all layers

        # ---------------- EXECUTE SYNCHRONOUS METHOD --------------#

        def synchronousRampC(smp_Sz, stp_Sz, fetchT):
            fetch_no = str(fetchT)              # entry value in string sql syntax

            # Obtain Volatile Data from sql Host Server ---------------------------[]
            con_ramp = conn.cursor()

            # Evaluate conditions for SQL Data Fetch ------------------------------[A]
            """
            Load watchdog function with synchronous function every seconds
            """
            # Initialise RT variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard                     # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                # Latch on SQL Query only a
                import sqlArrayRLmethodRC as srm                    # DrLabs optimization method

                inProgress = False  # True for RetroPlay mode
                print('\nAsynchronous controller activated...')
                print('DrLabs' + "' Runtime Optimisation is Enabled!")

                if not sysRun:
                    sysRun, msctcp, msc_rt = wd.autoPausePlay()     # Retrieve MSC from Watchdog
                print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                # Get list of relevant SQL Tables using conn() --------------------[]
                if keyboard.is_pressed(
                        "Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:  # Terminate file-fetch
                    print('\nProduction is pausing...')
                    if not autoSpcPause:
                        autoSpcRun = not autoSpcRun
                        autoSpcPause = True
                        print("\nVisualization in Paused Mode...")

                    else:
                        autoSpcPause = False
                    print("Visualization in Play Mode...")

                else:
                    rCount = srm.sqlexec(smp_Sz, stp_Sz, con_ramp, rcData, fetch_no)  # perform DB connections
                    print("Visualization in Play Mode...")
                print('\nUpdating....')

                # ------ Inhibit iteration ----------------------------------------------------------[]
                """
                # Set condition for halting real-time plots in watchdog class ---------------------
                """
                # TODO --- values for inhibiting the SQL processing
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    con_ramp.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

            return rCount

        # ================== End of synchronous Method ==========================obal

        def asynchronous_rc(db_freq):

            timei = time.time()                                 # start timing the entire loop

            # Call data loader Method---------------------------#
            rcData = synchronousRampC(smp_Sz, stp_Sz, db_freq)    # data loading functions

            # --------------------------------------------------#
            import VarSQLrc as rc                              # load SQL variables column names | rfVarSQL

            viz_cycle = 150
            g1 = qrc.validCols('RC')                            # Construct Data Column selSqlColumnsTFM.py
            df1 = pd.DataFrame(rcData, columns=g1)              # Import into python Dataframe
            RC = rc.loadProcesValues(df1)                       # Join data values under dataframe

            print('\nSQL Content', df1.head(10))
            print("Memory Usage:", df1.info(verbose=False))     # Check memory utilization
            total_cum = RC[0] + RC[1] + RC[2] + RC[3]
            # ----------------------------------------------------------------------------------[]
            # Plot X-Axis data points -------- X Plot
            im10.set_xdata(np.arange(db_freq))
            im11.set_xdata(np.arange(db_freq))
            im12.set_xdata(np.arange(db_freq))
            im13.set_xdata(np.arange(db_freq))
            im14.set_xdata(np.arange(db_freq))

            # X Plot Y-Axis data points for XBar --------------------------------------------[Ring 1]
            im10.set_ydata((RC[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
            im11.set_ydata((RC[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
            im12.set_ydata((RC[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
            im13.set_ydata((RC[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # head 1
            im14.set_ydata((total_cum).rolling(window=smp_Sz, min_periods=1)[0:db_freq])  # Cumulatie count

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
                # a2.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a1.set_xlim(0, window_Xmax)
                # a2.set_xlim(0, window_Xmax)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronous_rc, frames=None, save_count=100, repeat_delay=None,
                                interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)

        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)


class common_climateProfile(ttk.Frame):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=910, y=20)
        self.createWidgets()

    def createWidgets(self):
        # -----------------------------------
        f = Figure(figsize=(7, 4), dpi=100)
        f.subplots_adjust(left=0.076, bottom=0.098, right=0.91, top=0.99, wspace=0.202)
        a2 = f.add_subplot(1, 1, 1)
        a3 = a2.twinx()

        # --------------------------------------- Dump Data ----------[]
        x = np.arange(0, 100, 0.1)
        y1 = - 0.01 * x ** 2
        y2 = -1 * y1
        # configure plot curves -----
        a2.plot(x, y1, 'r-')
        a3.plot(x, y2, 'b-')

        # Model data --------------------------------------------------[]
        a2.get_yaxis().set_visible(True)
        a2.get_xaxis().set_visible(True)

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 9})                       # Reduce font size to 7pt for all legends

        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minCP, YScale_maxCP = -10, 80                        # Climate Data
        window_Xmin, window_Xmax = 0, 30                            # windows view = visible data points

        # Load SQL Query Table -------------------------------------#
        evData = WON + '_EV'                                        # Enviromental variables
        # ----------------------------------------------------------#

        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.legend(loc='upper right', title='Location-Based Climatic Profile')
        a2.set_ylabel("Temperature [°C]", color='r')
        a3.set_ylabel("Relative Humidity", color='b')
        a2.set_xlabel("Time Series")
        # ----------------------------------------------------------#

        a2.set_ylim([YScale_minCP, YScale_maxCP], auto=True)
        a2.set_xlim([window_Xmin, window_Xmax])

        # ------- plot ramp count ------------[]
        im10, = a2.plot([], [], 'o-', label='Oven Temperature (N)')
        im11, = a2.plot([], [], 'o-', label='Oven Temperature (S)')
        im12, = a2.plot([], [], 'o-', label='Cell Dew Point Temp')
        im13, = a3.plot([], [], 'o-', label='Cell Dew Point Humidity')
        im14, = a2.plot([], [], 'o-', label='Factory Dew Point Temp')
        im15, = a3.plot([], [], 'o-', label='Factory Relative Humidity')
        im16, = a2.plot([], [], 'o-', label='Location Data - Temp')
        im17, = a3.plot([], [], 'o-', label='Location Data - Humidity')

        # ---------------- EXECUTE SYNCHRONOUS METHOD ---------------#

        def synchronousClimate(smp_Sz, stp_Sz, fetchT):
            fetch_no = str(fetchT)  # entry value in string sql syntax

            # Obtain SQL Data Host Server ---------------------------[]
            con_ct = conn.cursor()

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
                import sqlArrayRLmethodEV as sct                            # DrLabs optimization method

                inProgress = True                                           # True for RetroPlay mode
                print('\nAsynchronous controller activated...')
                print('DrLabs' + "' Runtime Optimisation is Enabled!")

                if not sysRun:
                    sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve MSC from Watchdog
                print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                # Get list of relevant SQL Tables using conn() --------------------[]
                if keyboard.is_pressed(
                        "Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:  # Terminate file-fetch
                    print('\nProduction is pausing...')
                    if not autoSpcPause:
                        autoSpcRun = not autoSpcRun
                        autoSpcPause = True
                        print("\nVisualization in Paused Mode...")

                    else:
                        autoSpcPause = False
                        print("Visualization in Play Mode...")

                else:
                    cPRofile = sct.sqlexec(smp_Sz, stp_Sz, con_ct, evData, fetch_no)  # perform DB connections
                    print("Visualization in Play Mode...")
                print('\nUpdating....')

                # ------ Inhibit iteration ----------------------------------------------------------[]
                """
                # Set condition for halting real-time plots in watchdog class ---------------------
                """
                # TODO --- values for inhibiting the SQL processing
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    con_ct.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

            return cPRofile

        # ================== End of synchronous Method ===========================================================[]
        def asynchronousClimate(db_freq):
            timei = time.time()                                 # start timing the entire loop

            # Call data loader Method---------------------------#
            ctData = synchronousClimate(smp_Sz, stp_Sz, db_freq)     # data loading functions

            import VarSQLct as ev                               # load SQL variables column names | rfVarSQL

            viz_cycle = 150
            g1 = qev.validCols('EV')                            # Construct Data Column selSqlColumnsTFM.py
            df3 = pd.DataFrame(ctData, columns=g1)              # Import into python Dataframe

            # ----- Access data element within the concatenated columns -------------------------[A]
            EV = ev.loadProcesValues(df3)                       # Join data values under dataframe
            print('\nDataFrame Content', df3.head(10))          # Preview Data frame head
            print("Memory Usage:", df3.info(verbose=False))     # Check memory utilization

            # --------------------------------
            # Plot X-Axis data points -------- X Plot
            im10.set_xdata(np.arange(db_freq))
            im11.set_xdata(np.arange(db_freq))
            im12.set_xdata(np.arange(db_freq))
            im13.set_xdata(np.arange(db_freq))
            im14.set_xdata(np.arange(db_freq))
            im15.set_xdata(np.arange(db_freq))
            im16.set_xdata(np.arange(db_freq))
            im17.set_xdata(np.arange(db_freq))

            # X Plot Y-Axis data points for XBar --------------------------------------------[Ring 1]
            # im10.set_ydata((CT[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])   # time stamp
            im10.set_ydata((EV[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])     # oven tempA
            im11.set_ydata((EV[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])     # oven temp B
            im12.set_ydata((EV[6]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])     # Cell Rel Temperature
            im13.set_ydata((EV[7]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])     # Cell Rel Humidity
            im14.set_ydata((EV[8]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])     # Factory Dew Point Temp
            im15.set_ydata((EV[9]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])     # Factory Humidity
            im16.set_ydata((EV[10]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])    # Location Temp
            im17.set_ydata((EV[11]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])    # Location Humidity
            # im11.set_ydata((CT[12]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # UVIndex

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if db_freq > window_Xmax:
                a2.set_xlim(db_freq - window_Xmax, db_freq)
                a3.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a2.set_xlim(0, window_Xmax)
                a3.set_xlim(0, window_Xmax)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousClimate, frames=None, save_count=100, repeat_delay=None,
                                interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -------------------------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)

        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

# -------------------------------------------------------------------------------------------------------[]

class common_gapCount(ttk.Frame):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=1600, y=20)
        self.createWidgets()

    def createWidgets(self):
        # -----------------------------------
        f = Figure(figsize=(9, 4), dpi=100)   #w.h
        f.subplots_adjust(left=0.076, bottom=0.1, right=0.971, top=0.99, wspace=0.202)
        a3 = f.add_subplot(1, 1, 1)

        # Model data --------------------------------------------------[]
        a3.get_yaxis().set_visible(True)
        a3.get_xaxis().set_visible(True)

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 9})  # Reduce font size to 7pt for all legends

        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minGP, YScale_maxGP = 0, vCount
        window_Xmin, window_Xmax = 0, pExLayer                      # windows view = visible data points

        # Load SQL Query Table -------------------------------------#
        vData = WON + '_VC'                                         # Void Count
        # ----------------------------------------------------------#

        a3.grid(color="0.5", linestyle='-', linewidth=0.5)
        a3.legend(loc='upper right', title='Cumulative Gap Count')
        a3.set_ylabel("Cumulative Tape Gap Count / Segment")
        a3.set_xlabel("Pipe Nominal Layer")

        # ----------------------------------------------------------#
        a3.set_ylim([YScale_minGP, YScale_maxGP], auto=True)
        a3.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        im10, = a3.plot([], [], 'o-', label='Gap Count Segment A')
        im11, = a3.plot([], [], 'o-', label='Gap Count Segment B')
        im12, = a3.plot([], [], 'o-', label='Gap Count Segment C')
        im13, = a3.plot([], [], 'o-', label='Gap Count Segment D')
        im14, = a3.plot([], [], 'o-', label='Cumulative Gap Count')

        # ---------------- EXECUTE SYNCHRONOUS METHOD ---------------#
        def synchronousGapC(smp_Sz, smp_St, fetchT):
            fetch_no = str(fetchT)  # entry value in string sql syntax

            # Obtain SQL Data Host Server ---------------------------[]
            con_gc = conn.cursor()

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
                import sqlArrayRLmethodVC as svc                            # DrLabs optimized Loader

                inProgress = True                                          # True for RetroPlay mode
                print('\nAsynchronous controller activated...')
                print('DrLabs' + "' Runtime Optimisation is Enabled!")

                if not sysRun:
                    sysRun, msctcp, msc_rt = wd.autoPausePlay()            # Retrieve MSC from Watchdog
                print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                # Get list of relevant SQL Tables using conn() ------------[]
                if keyboard.is_pressed(
                        "Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:  # Terminate file-fetch
                    print('\nProduction is pausing...')
                    if not autoSpcPause:
                        autoSpcRun = not autoSpcRun
                        autoSpcPause = True
                        print("\nVisualization in Paused Mode...")

                    else:
                        autoSpcPause = False
                    print("Visualization in Play Mode...")

                else:
                    gCount = svc.sqlexec(smp_Sz, stp_Sz, con_gc, vData, fetch_no)  # perform DB connections
                    print("Visualization in Play Mode...")
                print('\nUpdating....')

                # ------ Inhibit iteration ----------------------------------------------------------[]
                """
                # Set condition for halting real-time plots in watchdog class ---------------------
                """
                # TODO --- values for inhibiting the SQL processing
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    con_gc.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

            return gCount

        # ================== End of synchronous Method ==========================
        def asynchronousGap(db_freq):

            timei = time.time()                                # start timing the entire loop
            # Call data loader Method--------------------------#
            gcData = synchronousGapC(smp_Sz, stp_Sz, db_freq)  # data loading functions

            import VarSQLvc as vc                              # load SQL variables column names | rfVarSQL

            viz_cycle = 150
            g1 = qvc.validCols('VC')                           # Construct Data Column void (gap) count
            df3 = pd.DataFrame(gcData, columns=g1)             # Import into python Dataframe

            VC = vc.loadProcesValues(df3)                      # Join data values under dataframe
            print('\nDataFrame Content', df3.head(10))         # Preview Data frame head
            print("Memory Usage:", df3.info(verbose=False))    # Check memory utilization

            # Plot X-Axis data points -------- X Plot
            im10.set_xdata(np.arange(db_freq))
            im11.set_xdata(np.arange(db_freq))
            im12.set_xdata(np.arange(db_freq))
            im13.set_xdata(np.arange(db_freq))
            im14.set_xdata(np.arange(db_freq))

            # X Plot Y-Axis data points for XBar --------------------------------------------[Ring 1]
            im10.set_ydata((VC[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Count under Ring 1
            im11.set_ydata((VC[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Count under Ring 2
            im12.set_ydata((VC[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Count under Ring 3
            im13.set_ydata((VC[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Count under Ring 4
            im14.set_ydata((VC[0]+VC[1]+VC[2]+VC[3]).rolling(window=smp_Sz, min_periods=1)[0:db_freq])  # Cumulative

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if db_freq > window_Xmax:
                a3.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a3.set_xlim(0, window_Xmax)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousGap, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -------------------------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)

        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

# ------------------------------------ Additional Tabb for Monitoring Parameters -----------------------------------[B]
# PRODUCTION PARAM - ROLLER FORCE ------------------[1]


class MonitorTabb(ttk.Frame):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=20)
        self.createWidgets()

    def createWidgets(self):
        # Load Quality Historical Values -----------[]
        label = ttk.Label(self, text='[' + rType + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)
        # ------------------------------------------[TODO if pMinMax:]
        f = Figure(figsize=(25, 8), dpi=100)

        if pRecipe == 'DNV':
            print('\n 4 params condition met....')
            f.subplots_adjust(left=0.029, bottom=0.057, right=0.99, top=0.979, wspace=0.167, hspace=0.164)
            a1 = f.add_subplot(2, 4, (1, 2))        # Roller Pressure
            a2 = f.add_subplot(2, 4, (3, 4))        # Winding Speed
            a3 = f.add_subplot(2, 4, (5, 6))        # Cell Tension
            a4 = f.add_subplot(2, 4, (7, 8))        # Oven Temperature
            # Load Query Tables --------------------#
            T1 = WON + '_RP'                        # Roller Pressure
            T2 = WON + '_WS'                        # Tape Winding Speed
            T3 = WON + '_CT'                        # Cell Tension & Oven Temp
            T4 = WON + '_OT'                        # Oven Temp already incorporated in common process
            # --------------------------------------#

        elif pRecipe == 'MGM':
            print('\n6 Param condition met....')

            f.subplots_adjust(left=0.029, bottom=0.057, right=0.99, top=0.979, wspace=0.245, hspace=0.164)
            a1 = f.add_subplot(2, 6, (1, 2))        # Laser power
            a2 = f.add_subplot(2, 6, (3, 4))        # Cell Tension
            a3 = f.add_subplot(2, 6, (5, 6))        # Roller Pressure
            a4 = f.add_subplot(2, 6, (7, 8))        # Laser Angle
            a5 = f.add_subplot(2, 6, (9, 10))       # Oven Temperature
            a6 = f.add_subplot(2, 6, (11, 12))      # Winding Speed
            # --------------------------------------#
            T1 = WON + '_LP'                        # Laser Power
            T2 = WON + '_LA'                        # Laser Angle
            T3 = WON + '_CT'                        # Cell Tension
            T4 = WON + '_RP'                        # Roller Pressure
            T5 = WON + '_WS'                        # Tape Winding Speed
            T6 = WON + '_OT'                        # Oven Temp already incorporated in common process
            # --------------------------------------#
        else:
            print('\n Users params condition met....')
            f.subplots_adjust(left=0.029, bottom=0.057, right=0.99, top=0.979, wspace=0.245, hspace=0.164)
            # Bespoke user selection criteria -------------------------
            print('\n Bespoke 2 params condition met....', OT, CT, RP, WS)

            if int(OT) and int(CT):
                a1 = f.add_subplot(1, 4, (1, 2))    # Cell Tension
                a2 = f.add_subplot(1, 4, (3, 4))    # Oven Temperature
                # ----------------------------------#
                T1 = WON + '_OT'                    # Oven Temperature
                T2 = WON + '_CT'                    # Cell Tension
                # ----------------------------------#

            elif int(LP) and int(LA):
                a1 = f.add_subplot(1, 4, (1, 2))    # Laser Power
                a2 = f.add_subplot(1, 4, (3, 4))    # Laser Angle
                # ----------------------------------#
                T1 = WON + '_RP'                    # Roller Pressure
                T2 = WON + '_WS'                    # Tape Winding Speed
                # ----------------------------------#

            elif int(RP) and int(WS):
                a1 = f.add_subplot(1, 4, (1, 2))    # Roller Pressure
                a2 = f.add_subplot(1, 4, (3, 4))    # Tape Winding Speed
                # ----------------------------------#
                T1 = WON + '_LP'                    # Laser Power
                T2 = WON + '_LA'                    # Laser Angle
                # ----------------------------------#

            elif int(ST) and int(TG):
                a1 = f.add_subplot(1, 4, (1, 2))    # Spooling Tension
                a2 = f.add_subplot(1, 4, (3, 4))    # Gap Polarising Error
                # ----------------------------------#
                T1 = WON + '_WS'  # Winding Speed
                T2 = WON + '_TG'  # Tape Gap Pol
                # ----------------------------------#
        # Declare Plots attributes -----------------[]
        plt.rcParams.update({'font.size': 7})        # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis --------#
        YScale_minMT, YScale_maxMT = 10 - 8.5, 10 + 8.5
        window_Xmin, window_Xmax = 0, 35             # windows view = visible data points
        # -------------------------------------------#

        # if process stalled, per SQL table ---------#
        # fname = 'f'
        # eoF = bufferEOF(fname, 1)
        # rT1dx = eoF[1]  # SQL data table index = 0 unless SPC stalled or relaunched.
        # rT2dx = eoF[2]  # SQL data table index = 0 unless SPC stalled or relaunched.
        # rT3dx = eoF[3]  # SQL data table index = 0 unless SPC stalled or relaunched.
        # rT4dx = eoF[4]  # SQL data table index = 0 unless SPC stalled or relaunched.
        # rT5dx = eoF[5]  # SQL data table index = 0 unless SPC stalled or relaunched.
        # rT6dx = eoF[6]  # SQL data table index = 0 unless SPC stalled or relaunched.
        # Monitoring Parameters --------------------------------------------#
        # Element in the Monitoring Parameter plot
        if int(mCT) and int(mOT) and int(mRP) and int(mWS):
            monitorP = 'DNV'
            a1.grid(color="0.5", linestyle='-', linewidth=0.5)
            a2.grid(color="0.5", linestyle='-', linewidth=0.5)
            a3.grid(color="0.5", linestyle='-', linewidth=0.5)
            a4.grid(color="0.5", linestyle='-', linewidth=0.5)
            # --------- Monitoring Legend Label -------------#
            a1.legend(loc='upper right', title='Roller Pressure - MPa')
            a2.legend(loc='upper right', title='Winding Speed - m/s')
            a3.legend(loc='upper right', title='Cell Tension - N.m')
            a4.legend(loc='upper right', title='Oven Temperature - °C')
            # Initialise runtime limits --------------------#
            a1.set_ylabel("Roller Pressure - MPa")          # Pressure measured in Pascal
            a2.set_ylabel("Tape Winding Speed - m/s")       # Angle measured in Degrees
            a3.set_ylabel("Cell Tension Force - N.m")       # Tension measured in Newton
            a4.set_ylabel("Oven Temperature - °C")          # Oven Temperature in Degrees Celsius
        elif int(mLP) and int(mLA) and int(mCT) and int(mOT) and int(mRP) and int(mWS):
            monitorP = 'MGM'
            a1.grid(color="0.5", linestyle='-', linewidth=0.5)
            a2.grid(color="0.5", linestyle='-', linewidth=0.5)
            a3.grid(color="0.5", linestyle='-', linewidth=0.5)
            a4.grid(color="0.5", linestyle='-', linewidth=0.5)
            a5.grid(color="0.5", linestyle='-', linewidth=0.5)
            a6.grid(color="0.5", linestyle='-', linewidth=0.5)
            # ---------------- Legend Label -----------------#
            a1.legend(loc='upper right', title='Laser Power - Watt')
            a2.legend(loc='upper right', title='Cell Tension - N.m')
            a3.legend(loc='upper right', title='Roller Pressure - MPa')
            a4.legend(loc='upper right', title='Laser Angle - Deg')
            a5.legend(loc='upper right', title='Oven Temperature - °C')
            a6.legend(loc='upper right', title='Winding Speed - m/s')
            # Initialise runtime limits --------------------#
            a1.set_ylabel("Laser Power")            # Force measured in Newton
            a2.set_ylabel("Cell Tension")           # Angle measured in Degrees
            a3.set_ylabel("Roller Pressure")        # Oven Temperature in Degree Celsius
            a4.set_ylabel("Laser Angle")            # Oven Temperature in Degrees Celsius
            a5.set_ylabel("Oven Temperature")       # Oven Temperature in Degrees Celsius
            a6.set_ylabel("Winding Speed")          # Oven Temperature in Degrees Celsius
        else:
            monitorP = 'USR'
            print('\n I am Here....', OT, CT, LP, LA, RP, WS)
            a1.grid(color="0.5", linestyle='-', linewidth=0.5)
            a2.grid(color="0.5", linestyle='-', linewidth=0.5)
            if int(OT) and int(CT):
                a1.legend(loc='upper right', title='Cell Tension - N.m')
                a2.legend(loc='upper right', title='Oven Temperature - °C')
                # Initialise runtime limits --------------------#
                a1.set_ylabel("Cell Tension")
                a2.set_ylabel("Oven Temperature")
            elif int(LP) and int(LA):
                a1.legend(loc='upper right', title='Laser Power - Watt')
                a2.legend(loc='upper right', title='Laser Angle - Deg')
                # Initialise runtime limits --------------------#
                a1.set_ylabel("Laser Power")
                a2.set_ylabel("Laser Angle")
            elif int(RP) and int(WS):
                a1.legend(loc='upper right', title='Roller Pressure - MPa')
                a2.legend(loc='upper right', title='Winding Speed - m/s')
                # Initialise runtime limits --------------------#
                a1.set_ylabel("Roller Pressure")
                a2.set_ylabel("Winding Speed")
            else: # Spooling Tension & Tape Gap Polarising Error
                a1.legend(loc='upper right', title='Spooling Tension - N.m')
                a2.legend(loc='upper right', title='Gap Polarising Error - %')
                # Initialise runtime limits --------------------#
                a1.set_ylabel("Spooling Tension")
                a2.set_ylabel("Tape Gap Polarising Error")

        # Initialise runtime limits --------------------------------#
        a1.set_ylim([YScale_minMT, YScale_maxMT], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # Model data -----------------------------------------------[]
        a1.plot([172, 48, 64, 59, 50, 136, 112, 223, 91, 320])
        # ----------------------------------------------------------[]
        # Define Plot area and axes -
        if monitorP == 'DNV':
            # -----------------------------------------------------[Roller Force]
            im10, = a1.plot([], [], 'o-', label='Roller Pressure - (R1H1)')
            im11, = a1.plot([], [], 'o-', label='Roller Pressure - (R1H2)')
            im12, = a1.plot([], [], 'o-', label='Roller Pressure - (R1H3)')
            im13, = a1.plot([], [], 'o-', label='Roller Pressure - (R1H4)')
            im14, = a1.plot([], [], 'o-', label='Roller Pressure - (R2H1)')
            im15, = a1.plot([], [], 'o-', label='Roller Pressure - (R2H2)')
            im16, = a1.plot([], [], 'o-', label='Roller Pressure - (R2H3)')
            im17, = a1.plot([], [], 'o-', label='Roller Pressure - (R2H4)')
            im18, = a1.plot([], [], 'o-', label='Roller Pressure - (R3H1)')
            im19, = a1.plot([], [], 'o-', label='Roller Pressure - (R3H2)')
            im20, = a1.plot([], [], 'o-', label='Roller Pressure - (R3H3)')
            im21, = a1.plot([], [], 'o-', label='Roller Pressure - (R3H4)')
            im22, = a1.plot([], [], 'o-', label='Roller Pressure - (R4H1)')
            im23, = a1.plot([], [], 'o-', label='Roller Pressure - (R4H2)')
            im24, = a1.plot([], [], 'o-', label='Roller Pressure - (R4H3)')
            im25, = a1.plot([], [], 'o-', label='Roller Pressure - (R4H4)')
            # ------------------------------------------------------[Winding Speed]
            im26, = a2.plot([], [], 'o-', label='Winding Speed - (R1H1)')
            im27, = a2.plot([], [], 'o-', label='Winding Speed - (R1H2)')
            im28, = a2.plot([], [], 'o-', label='Winding Speed - (R1H3)')
            im29, = a2.plot([], [], 'o-', label='Winding Speed - (R1H4)')
            im30, = a2.plot([], [], 'o-', label='Winding Speed - (R2H1)')
            im31, = a2.plot([], [], 'o-', label='Winding Speed - (R2H2)')
            im32, = a2.plot([], [], 'o-', label='Winding Speed - (R2H3)')
            im33, = a2.plot([], [], 'o-', label='Winding Speed - (R2H4)')
            im34, = a2.plot([], [], 'o-', label='Winding Speed - (R3H1)')
            im35, = a2.plot([], [], 'o-', label='Winding Speed - (R3H2)')
            im36, = a2.plot([], [], 'o-', label='Winding Speed - (R3H3)')
            im37, = a2.plot([], [], 'o-', label='Winding Speed - (R3H4)')
            im38, = a2.plot([], [], 'o-', label='Winding Speed - (R4H1)')
            im39, = a2.plot([], [], 'o-', label='Winding Speed - (R4H2)')
            im40, = a2.plot([], [], 'o-', label='Winding Speed - (R4H3)')
            im41, = a2.plot([], [], 'o-', label='Winding Speed - (R4H4)')
            # ------------------------------------------------------[Cell Tension]
            im42, = a3.plot([], [], 'o-', label='Cell Tension (Southward)')
            im43, = a3.plot([], [], 'o-', label='Cell Tension (Northward)')
            # -------------------------------------------------[Oven Temperature]
            im44, = a4.plot([], [], 'o-', label='Oven Temperature (Southward)')
            im45, = a4.plot([], [], 'o-', label='Oven Temperature (Northward)')

        elif monitorP == 'MGM':
            # --------------------------------------------------[Laser Power]
            im10, = a1.plot([], [], 'o-', label='Laser Power - (R1H1)')
            im11, = a1.plot([], [], 'o-', label='Laser Power - (R1H2)')
            im12, = a1.plot([], [], 'o-', label='Laser Power - (R1H3)')
            im13, = a1.plot([], [], 'o-', label='Laser Power - (R1H4)')
            im14, = a1.plot([], [], 'o-', label='Laser Power - (R2H1)')
            im15, = a1.plot([], [], 'o-', label='Laser Power - (R2H2)')
            im16, = a1.plot([], [], 'o-', label='Laser Power - (R2H3)')
            im17, = a1.plot([], [], 'o-', label='Laser Power - (R2H4)')
            im18, = a1.plot([], [], 'o-', label='Laser Power - (R3H1)')
            im19, = a1.plot([], [], 'o-', label='Laser Power - (R3H2)')
            im20, = a1.plot([], [], 'o-', label='Laser Power - (R3H3)')
            im21, = a1.plot([], [], 'o-', label='Laser Power - (R3H4)')
            im22, = a1.plot([], [], 'o-', label='Laser Power - (R4H1)')
            im23, = a1.plot([], [], 'o-', label='Laser Power - (R4H2)')
            im24, = a1.plot([], [], 'o-', label='Laser Power - (R4H3)')
            im25, = a1.plot([], [], 'o-', label='Laser Power - (R4H4)')
            # ---------------------------------------- [Cell Tension  & Oven Temp]
            im26, = a2.plot([], [], 'o-', label='Cell Tension (Southward)')
            im27, = a2.plot([], [], 'o-', label='Cell Tension (Northward)')
            # --------------------------------------------------[Roller Pressure]
            im28, = a3.plot([], [], 'o-', label='Roller Pressure - (R1H1)')
            im29, = a3.plot([], [], 'o-', label='Roller Pressure - (R1H2)')
            im30, = a3.plot([], [], 'o-', label='Roller Pressure - (R1H3)')
            im31, = a3.plot([], [], 'o-', label='Roller Pressure - (R1H4)')
            im32, = a3.plot([], [], 'o-', label='Roller Pressure - (R2H1)')
            im33, = a3.plot([], [], 'o-', label='Roller Pressure - (R2H2)')
            im34, = a3.plot([], [], 'o-', label='Roller Pressure - (R2H3)')
            im35, = a3.plot([], [], 'o-', label='Roller Pressure - (R2H4)')
            im36, = a3.plot([], [], 'o-', label='Roller Pressure - (R3H1)')
            im37, = a3.plot([], [], 'o-', label='Roller Pressure - (R3H2)')
            im38, = a3.plot([], [], 'o-', label='Roller Pressure - (R3H3)')
            im39, = a3.plot([], [], 'o-', label='Roller Pressure - (R3H4)')
            im40, = a3.plot([], [], 'o-', label='Roller Pressure - (R4H1)')
            im41, = a3.plot([], [], 'o-', label='Roller Pressure - (R4H2)')
            im42, = a3.plot([], [], 'o-', label='Roller Pressure - (R4H3)')
            im43, = a3.plot([], [], 'o-', label='Roller Pressure - (R4H4)')
            # --------------------------------------------------[Laser Angle]
            im44, = a4.plot([], [], 'o-', label='Laser Angle - (R1H1)')
            im45, = a4.plot([], [], 'o-', label='Laser Angle - (R1H2)')
            im46, = a4.plot([], [], 'o-', label='Laser Angle - (R1H3)')
            im47, = a4.plot([], [], 'o-', label='Laser Angle - (R1H4)')
            im48, = a4.plot([], [], 'o-', label='Laser Angle - (R2H1)')
            im49, = a4.plot([], [], 'o-', label='Laser Angle - (R2H2)')
            im50, = a4.plot([], [], 'o-', label='Laser Angle - (R2H3)')
            im51, = a4.plot([], [], 'o-', label='Laser Angle - (R2H4)')
            im52, = a4.plot([], [], 'o-', label='Laser Angle - (R3H1)')
            im53, = a4.plot([], [], 'o-', label='Laser Angle - (R3H2)')
            im54, = a4.plot([], [], 'o-', label='Laser Angle - (R3H3)')
            im55, = a4.plot([], [], 'o-', label='Laser Angle - (R3H4)')
            im56, = a4.plot([], [], 'o-', label='Laser Angle - (R4H1)')
            im57, = a4.plot([], [], 'o-', label='Laser Angle - (R4H2)')
            im58, = a4.plot([], [], 'o-', label='Laser Angle - (R4H3)')
            im59, = a4.plot([], [], 'o-', label='Laser Angle - (R4H4)')
            # -----------------------------------------------[ Oven Temperature]
            im60, = a5.plot([], [], 'o-', label='Oven Temperature (Southward)')
            im61, = a5.plot([], [], 'o-', label='Oven Temperature (Northward)')
            # ----------------------------------------------[Winding Speed x16]
            im62, = a6.plot([], [], 'o-', label='Winding Speed - (R1H1)')
            im63, = a6.plot([], [], 'o-', label='Winding Speed - (R1H2)')
            im64, = a6.plot([], [], 'o-', label='Winding Speed - (R1H3)')
            im65, = a6.plot([], [], 'o-', label='Winding Speed - (R1H4)')
            im66, = a6.plot([], [], 'o-', label='Winding Speed - (R2H1)')
            im67, = a6.plot([], [], 'o-', label='Winding Speed - (R2H2)')
            im68, = a6.plot([], [], 'o-', label='Winding Speed - (R2H3)')
            im69, = a6.plot([], [], 'o-', label='Winding Speed - (R2H4)')
            im70, = a6.plot([], [], 'o-', label='Winding Speed - (R3H1)')
            im71, = a6.plot([], [], 'o-', label='Winding Speed - (R3H2)')
            im72, = a6.plot([], [], 'o-', label='Winding Speed - (R3H3)')
            im73, = a6.plot([], [], 'o-', label='Winding Speed - (R3H4)')
            im74, = a6.plot([], [], 'o-', label='Winding Speed - (R4H1)')
            im75, = a6.plot([], [], 'o-', label='Winding Speed - (R4H2)')
            im76, = a6.plot([], [], 'o-', label='Winding Speed - (R4H3)')
            im77, = a6.plot([], [], 'o-', label='Winding Speed - (R4H4)')

        else:

            # -------------------------------------------[Cell Tension - Oven Temp]
            if int(OT) and int(CT):
                im10, = a1.plot([], [], 'o-', label='Cell Tension - (North)')
                im11, = a1.plot([], [], 'o-', label='Cell Tension - (South)')
                im12, = a2.plot([], [], 'o-', label='Oven Temperature - (North)')
                im13, = a2.plot([], [], 'o-', label='Oven Temperature - (South)')

            elif int(LP) and int(LA):
                # --------------------------------------------------[Laser Power]
                im10, = a1.plot([], [], 'o-', label='Laser Power - (R1H1)')
                im11, = a1.plot([], [], 'o-', label='Laser Power - (R1H2)')
                im12, = a1.plot([], [], 'o-', label='Laser Power - (R1H3)')
                im13, = a1.plot([], [], 'o-', label='Laser Power - (R1H4)')
                im14, = a1.plot([], [], 'o-', label='Laser Power - (R2H1)')
                im15, = a1.plot([], [], 'o-', label='Laser Power - (R2H2)')
                im16, = a1.plot([], [], 'o-', label='Laser Power - (R2H3)')
                im17, = a1.plot([], [], 'o-', label='Laser Power - (R2H4)')
                im18, = a1.plot([], [], 'o-', label='Laser Power - (R3H1)')
                im19, = a1.plot([], [], 'o-', label='Laser Power - (R3H2)')
                im20, = a1.plot([], [], 'o-', label='Laser Power - (R3H3)')
                im21, = a1.plot([], [], 'o-', label='Laser Power - (R3H4)')
                im22, = a1.plot([], [], 'o-', label='Laser Power - (R4H1)')
                im23, = a1.plot([], [], 'o-', label='Laser Power - (R4H2)')
                im24, = a1.plot([], [], 'o-', label='Laser Power - (R4H3)')
                im25, = a1.plot([], [], 'o-', label='Laser Power - (R4H4)')
                # --------------------------------------------------[Laser Angle]
                im26, = a2.plot([], [], 'o-', label='Laser Angle - (R1H1)')
                im27, = a2.plot([], [], 'o-', label='Laser Angle - (R1H2)')
                im28, = a2.plot([], [], 'o-', label='Laser Angle - (R1H3)')
                im29, = a2.plot([], [], 'o-', label='Laser Angle - (R1H4)')
                im30, = a2.plot([], [], 'o-', label='Laser Angle - (R2H1)')
                im31, = a2.plot([], [], 'o-', label='Laser Angle - (R2H2)')
                im32, = a2.plot([], [], 'o-', label='Laser Angle - (R2H3)')
                im33, = a2.plot([], [], 'o-', label='Laser Angle - (R2H4)')
                im34, = a2.plot([], [], 'o-', label='Laser Angle - (R3H1)')
                im35, = a2.plot([], [], 'o-', label='Laser Angle - (R3H2)')
                im36, = a2.plot([], [], 'o-', label='Laser Angle - (R3H3)')
                im37, = a2.plot([], [], 'o-', label='Laser Angle - (R3H4)')
                im38, = a2.plot([], [], 'o-', label='Laser Angle - (R4H1)')
                im39, = a2.plot([], [], 'o-', label='Laser Angle - (R4H2)')
                im40, = a2.plot([], [], 'o-', label='Laser Angle - (R4H3)')
                im41, = a2.plot([], [], 'o-', label='Laser Angle - (R4H4)')

            elif int(RP) and int(WS):
                # --------------------------------------------------[Roller Pressure]
                im10, = a1.plot([], [], 'o-', label='Roller Pressure - (R1H1)')
                im11, = a1.plot([], [], 'o-', label='Roller Pressure - (R1H2)')
                im12, = a1.plot([], [], 'o-', label='Roller Pressure - (R1H3)')
                im13, = a1.plot([], [], 'o-', label='Roller Pressure - (R1H4)')
                im14, = a1.plot([], [], 'o-', label='Roller Pressure - (R2H1)')
                im15, = a1.plot([], [], 'o-', label='Roller Pressure - (R2H2)')
                im16, = a1.plot([], [], 'o-', label='Roller Pressure - (R2H3)')
                im17, = a1.plot([], [], 'o-', label='Roller Pressure - (R2H4)')
                im18, = a1.plot([], [], 'o-', label='Roller Pressure - (R3H1)')
                im19, = a1.plot([], [], 'o-', label='Roller Pressure - (R3H2)')
                im20, = a1.plot([], [], 'o-', label='Roller Pressure - (R3H3)')
                im21, = a1.plot([], [], 'o-', label='Roller Pressure - (R3H4)')
                im22, = a1.plot([], [], 'o-', label='Roller Pressure - (R4H1)')
                im23, = a1.plot([], [], 'o-', label='Roller Pressure - (R4H2)')
                im24, = a1.plot([], [], 'o-', label='Roller Pressure - (R4H3)')
                im25, = a1.plot([], [], 'o-', label='Roller Pressure - (R4H4)')
                # --------------------------------------------------[Winding Speed]
                im26, = a2.plot([], [], 'o-', label='Winding Speed - (R1H1)')
                im27, = a2.plot([], [], 'o-', label='Winding Speed - (R1H2)')
                im28, = a2.plot([], [], 'o-', label='Winding Speed - (R1H3)')
                im29, = a2.plot([], [], 'o-', label='Winding Speed - (R1H4)')
                im30, = a2.plot([], [], 'o-', label='Winding Speed - (R2H1)')
                im31, = a2.plot([], [], 'o-', label='Winding Speed - (R2H2)')
                im32, = a2.plot([], [], 'o-', label='Winding Speed - (R2H3)')
                im33, = a2.plot([], [], 'o-', label='Winding Speed - (R2H4)')
                im34, = a2.plot([], [], 'o-', label='Winding Speed - (R3H1)')
                im35, = a2.plot([], [], 'o-', label='Winding Speed - (R3H2)')
                im36, = a2.plot([], [], 'o-', label='Winding Speed - (R3H3)')
                im37, = a2.plot([], [], 'o-', label='Winding Speed - (R3H4)')
                im38, = a2.plot([], [], 'o-', label='Winding Speed - (R4H1)')
                im39, = a2.plot([], [], 'o-', label='Winding Speed - (R4H2)')
                im40, = a2.plot([], [], 'o-', label='Winding Speed - (R4H3)')
                im41, = a2.plot([], [], 'o-', label='Winding Speed - (R4H4)')

            elif int(ST) and int(TG):
                # ----------------------------------------------[Spooling Tension]
                im10, = a1.plot([], [], 'o-', label='Spooling Tension - (North)')
                im11, = a1.plot([], [], 'o-', label='Spooling Tension - (South)')
                # ----------------------------------------------[Tape Gap Error]
                im12, = a2.plot([], [], 'o-', label='Tape Gap Pol - (H1A)')
                im13, = a2.plot([], [], 'o-', label='Tape Gap Pol - (H2A)')
                im14, = a2.plot([], [], 'o-', label='Tape Gap Pol - (H3A)')
                im15, = a2.plot([], [], 'o-', label='Tape Gap Pol - (H4A)')
                im16, = a2.plot([], [], 'o-', label='Tape Gap Pol - (H1B)')
                im17, = a2.plot([], [], 'o-', label='Tape Gap Pol - (H2B)')
                im18, = a2.plot([], [], 'o-', label='Tape Gap Pol - (H3B)')
                im19, = a2.plot([], [], 'o-', label='Tape Gap Pol - (H4B)')
            # ---------------- EXECUTE SYNCHRONOUS METHOD ---------------#

        def synchronousP(smp_Sz, smp_St, fetchT):
            fetch_no = str(fetchT)      # entry value in string sql syntax

            # Obtain SQL Data Host Server ---------------------------[]
            if monitorP == 'DNV':
                conA, conB, conC, conD  = conn.cursor(), conn.cursor(), conn.cursor(), conn.cursor()
            elif monitorP == 'MGM':
                conA, conB, conC, conD, conE, conF = (conn.cursor(), conn.cursor(), conn.cursor(), conn.cursor(),
                                                      conn.cursor(), conn.cursor())
            else:
                pass  # reserved for bespoke configuration

            # Evaluate conditions for SQL Data Fetch ---------------[A]
            """
            Load watchdog function with synchronous function every seconds
            """

            # Initialise RT variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard                     # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                # print('Indefinite looping...')
                import sqlArrayRLmethodPM as spm                             # DrLabs optimization method

                inProgress = True                                           # True for RetroPlay mode
                print('\nAsynchronous controller activated...')
                print('DrLabs' + "' Runtime Optimisation is Enabled!")

                if not sysRun:
                    sysRun, msctcp, msc_rt = wd.autoPausePlay()             # Retrieve M.State from Watchdog
                print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                if keyboard.is_pressed("Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:
                    print('\nProduction is pausing...')
                    if not autoSpcPause:
                        autoSpcRun = not autoSpcRun
                        autoSpcPause = True
                        print("\nVisualization in Paused Mode...")
                    else:
                        autoSpcPause = False
                        print("Visualization in Real-time Mode...")

                else:
                    # Get list of relevant SQL Tables using conn() and execute real-time query --------------------[]
                    if monitorP == 'DNV':
                        dtRP, dtWS, dtCT, dtOT = spm.dnv_sqlexec(smp_Sz, smp_St, conA, conB, conC, conD, T1, T2, T3, T4,
                                                                 fetch_no)

                    elif monitorP == 'MGM':
                        dtLP, dtCT, dtRP, dtLA, dtOT, dtWS = spm.mgm_sqlexec(smp_Sz, smp_St, conA, conB, conC, conD, conE,
                                                                      conF, T1, T2, T3, T4, T5, T6, fetch_no)
                    else:
                        dtLP, dtCT, dtRP, dtLA, dtOT, dtWS = 0, 0, 0, 0, 0, 0            # Assigned to Bespoke User Selection.

                # ------ Inhibit iteration ----------------------------------------------------------[]
                """
                # Set condition for halting real-time plots in watchdog class ---------------------
                """
                # TODO --- values for inhibiting the SQL processing
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    conA.close()
                    conB.close()
                    conC.close()
                    if monitorP == 'MGM':
                        conD.close()
                        conE.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

            if monitorP == 'DNV':
                return dtRP, dtWS, dtCT, dtOT
            else:
                return dtLP, dtCT, dtRP, dtLA, dtOT, dtWS

        # ================== End of synchronous Method ==========================================================[]

        def asynchronousP(db_freq):
            timei = time.time()                                                                 # start timing the entire loop

            # declare asynchronous variables ------------------[]
            if monitorP == 'DNV':
                dtRP, dtWS, dtCT, dtOT = synchronousP(smp_Sz, stp_Sz, db_freq)                  # data loading functions
            else:
                dtLP, dtCT, dtRP, dtLA, dtOT, dtWS = synchronousP(smp_Sz, stp_Sz, db_freq)      # data loading functions

            import varSQL_DFpm as pm                    # Contruct new data frame columns                                                # load SQL named columns

            viz_cycle = 150
            if monitorP == 'DNV':
                g1 = qpm.validCols(T1)                   # Roller Pressure
                d1 = pd.DataFrame(dtRP, columns=g1)
                g2 = qpm.validCols(T2)                   # Tape Winding Speed
                d2 = pd.DataFrame(dtWS, columns=g2)
                g3 = qpm.validCols(T3)                   # Cell Tension and Oven Temp
                d3 = pd.DataFrame(dtCT, columns=g3)
                g4 = qpm.validCols(T4)  # Cell Tension and Oven Temp
                d4 = pd.DataFrame(dtOT, columns=g4)

                # Concatenate all columns -----------[]
                df1 = pd.concat([d1, d2, d3, d4], axis=1)

            elif monitorP == 'MGM':
                g1 = qpm.validCols(T5)                   # Laser Power
                d1 = pd.DataFrame(dtLP, columns=g1)
                g2 = qpm.validCols(T3)                   # Cell Tension
                d2 = pd.DataFrame(dtCT, columns=g2)
                g3 = qpm.validCols(T1)                   # Roller Pressure
                d3 = pd.DataFrame(dtRP, columns=g3)
                g4 = qpm.validCols(T6)                   # Laser Angle
                d4 = pd.DataFrame(dtLA, columns=g4)
                g5 = qpm.validCols(T4)                  # Oven Temperature
                d5 = pd.DataFrame(dtOT, columns=g5)
                g6 = qpm.validCols(T2)                   # Tape Winding Speed
                d6 = pd.DataFrame(dtWS, columns=g6)

                # Concatenate all columns -----------[]
                df1 = pd.concat([d1, d2, d3, d4, d5, d6], axis=1)
            else:
                df1 = 0
                pass                                            # Reserve for process scaling -- RBL.

            # ----- Access data element within the concatenated columns -------------------------[A]
            PM = pm.loadProcesValues(df1, monitorP)             # Join data values under dataframe
            print('\nDataFrame Content', df1.head(10))          # Preview Data frame head
            print("Memory Usage:", df1.info(verbose=False))     # Check memory utilization

            # Declare Plots attributes ------------------------------------------------------------[]
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

            im42.set_xdata(np.arange(db_freq))
            im43.set_xdata(np.arange(db_freq))
            im44.set_xdata(np.arange(db_freq))
            im45.set_xdata(np.arange(db_freq))

            im46.set_xdata(np.arange(db_freq))
            im47.set_xdata(np.arange(db_freq))
            im48.set_xdata(np.arange(db_freq))
            im49.set_xdata(np.arange(db_freq))
            im50.set_xdata(np.arange(db_freq))
            im51.set_xdata(np.arange(db_freq))
            im52.set_xdata(np.arange(db_freq))
            im53.set_xdata(np.arange(db_freq))
            im54.set_xdata(np.arange(db_freq))
            im55.set_xdata(np.arange(db_freq))
            im56.set_xdata(np.arange(db_freq))
            im57.set_xdata(np.arange(db_freq))
            im58.set_xdata(np.arange(db_freq))
            im59.set_xdata(np.arange(db_freq))
            im60.set_xdata(np.arange(db_freq))
            im61.set_xdata(np.arange(db_freq))

            im62.set_xdata(np.arange(db_freq))
            im63.set_xdata(np.arange(db_freq))
            im64.set_xdata(np.arange(db_freq))
            im65.set_xdata(np.arange(db_freq))
            im66.set_xdata(np.arange(db_freq))
            im67.set_xdata(np.arange(db_freq))
            im68.set_xdata(np.arange(db_freq))
            im69.set_xdata(np.arange(db_freq))
            im70.set_xdata(np.arange(db_freq))
            im71.set_xdata(np.arange(db_freq))
            im72.set_xdata(np.arange(db_freq))
            im73.set_xdata(np.arange(db_freq))
            im74.set_xdata(np.arange(db_freq))
            im75.set_xdata(np.arange(db_freq))
            im76.set_xdata(np.arange(db_freq))
            im77.set_xdata(np.arange(db_freq))

            if monitorP == 'DNV':
                # X Plot Y-Axis data points for XBar ----------[Roller Pressure x16, A1]
                im10.set_ydata((PM[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # R1H1
                im11.set_ydata((PM[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # R1H2
                im12.set_ydata((PM[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # R1H3
                im13.set_ydata((PM[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # R1H4
                im14.set_ydata((PM[4]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # R2H1
                im15.set_ydata((PM[5]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # R2H2
                im16.set_ydata((PM[6]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # R2H3
                im17.set_ydata((PM[7]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # R2H4
                # No computation for PPk / Cpk
                im18.set_ydata((PM[8]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im19.set_ydata((PM[9]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                im20.set_ydata((PM[10]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im21.set_ydata((PM[11]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                # No computation for PPk / Cpk
                im22.set_ydata((PM[12]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im23.set_ydata((PM[13]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                im24.set_ydata((PM[14]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im25.set_ydata((PM[15]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                # ------------------------------------- Tape Winding Speed x16, A2
                im26.set_ydata((PM[16]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im27.set_ydata((PM[17]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                im28.set_ydata((PM[18]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im29.set_ydata((PM[19]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                # No computation for PPk / Cpk
                im30.set_ydata((PM[20]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im31.set_ydata((PM[21]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                im32.set_ydata((PM[22]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im33.set_ydata((PM[23]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                # No computation for PPk / Cpk
                im34.set_ydata((PM[24]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im35.set_ydata((PM[25]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                im36.set_ydata((PM[26]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im37.set_ydata((PM[27]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                # No computation for PPk / Cpk
                im38.set_ydata((PM[28]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im39.set_ydata((PM[29]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                im40.set_ydata((PM[30]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im41.set_ydata((PM[31]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                # -------------------------------------for Cell Tension x2, A3
                im42.set_ydata((PM[32]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im43.set_ydata((PM[33]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                # -------------------------------------for Oven Temperature x2 A4
                im44.set_ydata((PM[34]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im45.set_ydata((PM[35]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2

            elif monitorP == 'MGM':
                # -------------------------------------------------------------------------------[Laser Power]
                im10.set_ydata((PM[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im11.set_ydata((PM[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                im12.set_ydata((PM[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im13.set_ydata((PM[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                im14.set_ydata((PM[4]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im15.set_ydata((PM[5]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                im16.set_ydata((PM[6]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im17.set_ydata((PM[7]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                im18.set_ydata((PM[8]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im19.set_ydata((PM[9]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                im20.set_ydata((PM[10]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im21.set_ydata((PM[11]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                im22.set_ydata((PM[12]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im23.set_ydata((PM[13]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                im24.set_ydata((PM[14]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im25.set_ydata((PM[15]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                # -----------------------------------------------------[Cell Tension]
                im26.set_ydata((PM[16]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im27.set_ydata((PM[17]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                # --------------------------------------------------[Roller Pressure]
                im28.set_ydata((PM[18]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im29.set_ydata((PM[19]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                im30.set_ydata((PM[20]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im31.set_ydata((PM[21]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                im32.set_ydata((PM[22]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im33.set_ydata((PM[23]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                im34.set_ydata((PM[24]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im35.set_ydata((PM[25]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                im36.set_ydata((PM[26]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im37.set_ydata((PM[27]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                im38.set_ydata((PM[28]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im39.set_ydata((PM[29]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                im40.set_ydata((PM[30]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im41.set_ydata((PM[31]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                im42.set_ydata((PM[33]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im43.set_ydata((PM[34]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                # -------------------------------------------------------[Laser Angle]
                im44.set_ydata((PM[36]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im45.set_ydata((PM[37]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                im46.set_ydata((PM[46]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im47.set_ydata((PM[47]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                im48.set_ydata((PM[48]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im49.set_ydata((PM[49]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                im50.set_ydata((PM[50]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im51.set_ydata((PM[51]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                im52.set_ydata((PM[52]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im53.set_ydata((PM[53]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                im54.set_ydata((PM[54]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im55.set_ydata((PM[55]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                im56.set_ydata((PM[56]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im57.set_ydata((PM[57]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                im58.set_ydata((PM[58]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im59.set_ydata((PM[59]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                # -------------------------------------------------[Oven Temperature]
                im60.set_ydata((PM[60]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im61.set_ydata((PM[61]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                # ----------------------------------------------[Winding Speed x16]
                im62.set_ydata((PM[62]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im63.set_ydata((PM[63]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                im64.set_ydata((PM[64]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im65.set_ydata((PM[65]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                im66.set_ydata((PM[66]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im67.set_ydata((PM[67]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                im68.set_ydata((PM[68]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im69.set_ydata((PM[69]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                im70.set_ydata((PM[70]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im71.set_ydata((PM[71]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                im72.set_ydata((PM[72]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im73.set_ydata((PM[73]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                im74.set_ydata((PM[74]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                im75.set_ydata((PM[75]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                im76.set_ydata((PM[76]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                im77.set_ydata((PM[77]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4

            else:
                # X Plot Y-Axis data points for XBar -------------------------------------------[# Channels]
                if int(OT) and int(CT):
                    im10.set_ydata((PM[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                    im11.set_ydata((PM[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                    im12.set_ydata((PM[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                    im13.set_ydata((PM[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                elif int(LP) and int(LA):
                    im10.set_ydata((PM[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                    im11.set_ydata((PM[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                    im12.set_ydata((PM[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                    im13.set_ydata((PM[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                    # No computation for PPk / Cpk
                    im14.set_ydata((PM[4]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                    im15.set_ydata((PM[5]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                    im16.set_ydata((PM[6]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                    im17.set_ydata((PM[7]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                    # No computation for PPk / Cpk
                    im18.set_ydata((PM[8]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                    im19.set_ydata((PM[9]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                    im20.set_ydata((PM[10]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                    im21.set_ydata((PM[11]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                    # No computation for PPk / Cpk
                    im22.set_ydata((PM[12]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                    im23.set_ydata((PM[13]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                    im24.set_ydata((PM[14]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                    im25.set_ydata((PM[15]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                    # ------------------------------------- for Laser Angle
                    im26.set_ydata((PM[16]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                    im27.set_ydata((PM[17]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                    im28.set_ydata((PM[18]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                    im29.set_ydata((PM[19]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                    # No computation for PPk / Cpk
                    im30.set_ydata((PM[20]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                    im31.set_ydata((PM[21]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                    im32.set_ydata((PM[22]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                    im33.set_ydata((PM[23]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                    # No computation for PPk / Cpk
                    im34.set_ydata((PM[24]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                    im35.set_ydata((PM[25]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                    im36.set_ydata((PM[26]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                    im37.set_ydata((PM[27]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                    # No computation for PPk / Cpk
                    im38.set_ydata((PM[28]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                    im39.set_ydata((PM[29]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                    im40.set_ydata((PM[30]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                    im41.set_ydata((PM[31]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                elif int(RP) and int(WS):
                    im10.set_ydata((PM[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                    im11.set_ydata((PM[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                    im12.set_ydata((PM[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                    im13.set_ydata((PM[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                    # No computation for PPk / Cpk
                    im14.set_ydata((PM[4]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                    im15.set_ydata((PM[5]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                    im16.set_ydata((PM[6]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                    im17.set_ydata((PM[7]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                    # No computation for PPk / Cpk
                    im18.set_ydata((PM[8]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                    im19.set_ydata((PM[9]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                    im20.set_ydata((PM[10]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                    im21.set_ydata((PM[11]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                    # No computation for PPk / Cpk
                    im22.set_ydata((PM[12]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                    im23.set_ydata((PM[13]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                    im24.set_ydata((PM[14]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                    im25.set_ydata((PM[15]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                    # ------------------------------------- for Laser Angle
                    im26.set_ydata((PM[16]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                    im27.set_ydata((PM[17]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                    im28.set_ydata((PM[18]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                    im29.set_ydata((PM[19]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                    # No computation for PPk / Cpk
                    im30.set_ydata((PM[20]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                    im31.set_ydata((PM[21]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                    im32.set_ydata((PM[22]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                    im33.set_ydata((PM[23]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                    # No computation for PPk / Cpk
                    im34.set_ydata((PM[24]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                    im35.set_ydata((PM[25]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                    im36.set_ydata((PM[26]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                    im37.set_ydata((PM[27]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                    # No computation for PPk / Cpk
                    im38.set_ydata((PM[28]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                    im39.set_ydata((PM[29]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                    im40.set_ydata((PM[30]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                    im41.set_ydata((PM[31]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4

                elif int(ST) and int(TG):
                    # -------------------------------------for Roller Pressure
                    im10.set_ydata((PM[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                    im11.set_ydata((PM[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                    im12.set_ydata((PM[2]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                    im13.set_ydata((PM[3]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                    # No computation for PPk / Cpk
                    im14.set_ydata((PM[4]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                    im15.set_ydata((PM[5]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
                    im16.set_ydata((PM[6]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 3
                    im17.set_ydata((PM[7]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 4
                    # No computation for PPk / Cpk
                    im18.set_ydata((PM[8]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
                    im19.set_ydata((PM[9]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2

            # --------------------
            xline, sline = 10, 2.2
            # Declare Plots attributes ----------------------------[]
            a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
            # ---------------------- sBar_minTG, sBar_maxTG -------[]

            # Setting up the parameters for moving windows Axes ---[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a1.set_xlim(0, window_Xmax)

            # No trigger module processing - Production parameter is for monitoring purposes only.
            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousP, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)

        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

# ------------------------------------------------------------------------------------------------------[P1]

class laserPowerTabb(ttk.Frame):
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        # Load Quality Historical Values -----------[]
        lpSize, lpgType, lpSspace, lpHL, lpAL, lpFO, lpParam1, lpParam2, lpParam3, lpParam4, lpParam5 = mq.decryptpProcessLim(
            WON, 'LP')
        # Break down each element to useful list ---------------[Tape Temperature]
        if lpHL and lpParam1 and lpParam2 and lpParam3 and lpParam4 and lpParam5:  #
            lpPerf = '$Pp_{k' + str(sSize) + '}$'  # Using estimated or historical Mean
            lplabel = 'Pp'
            # -------------------------------
            One = lpParam1.split(',')                   # split into list elements
            Two = lpParam2.split(',')
            Thr = lpParam3.split(',')
            For = lpParam4.split(',')
            Fiv = lpParam5.split(',')
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
                lpUCL = float(One[2].strip("' "))       # Strip out the element of the list
                lpLCL = float(One[3].strip("' "))
                lpMean = float(One[4].strip("' "))
                lpDev = float(One[5].strip("' "))
                # --------------------------------
                sUCLlp = float(One[6].strip("' "))
                sLCLlp = float(One[7].strip("' "))
                # --------------------------------
                lpUSL = (lpUCL - lpMean) / 3 * 6
                lpLSL = (lpMean - lpLCL) / 3 * 6
                # --------------------------------
            elif cpTapeW == dTape2 and cpLayerNo == 2:
                lpUCL = float(Two[2].strip("' "))       # Strip out the element of the list
                lpLCL = float(Two[3].strip("' "))
                lpMean = float(Two[4].strip("' "))
                lpDev = float(Two[5].strip("' "))
                # --------------------------------
                sUCLlp = float(Two[6].strip("' "))
                sLCLlp = float(Two[7].strip("' "))
                # --------------------------------
                lpUSL = (lpUCL - lpMean) / 3 * 6
                lpLSL = (lpMean - lpLCL) / 3 * 6
            elif cpTapeW == dTape3 and cpLayerNo == range(3, 40):
                lpUCL = float(Thr[2].strip("' "))       # Strip out the element of the list
                lpLCL = float(Thr[3].strip("' "))
                lpMean = float(Thr[4].strip("' "))
                lpDev = float(Thr[5].strip("' "))
                # --------------------------------
                sUCLlp = float(Thr[6].strip("' "))
                sLCLlp = float(Thr[7].strip("' "))
                # --------------------------------
                lpUSL = (lpUCL - lpMean) / 3 * 6
                lpLSL = (lpMean - lpLCL) / 3 * 6
            elif cpTapeW == dTape4 and cpLayerNo == 41:
                lpUCL = float(For[2].strip("' "))       # Strip out the element of the list
                lpLCL = float(For[3].strip("' "))
                lpMean = float(For[4].strip("' "))
                lpDev = float(For[5].strip("' "))
                # --------------------------------
                sUCLlp = float(For[6].strip("' "))
                sLCLlp = float(For[7].strip("' "))
                # --------------------------------
                lpUSL = (lpUCL - lpMean) / 3 * 6
                lpLSL = (lpMean - lpLCL) / 3 * 6
            else:
                lpUCL = float(Fiv[2].strip("' "))       # Strip out the element of the list
                lpLCL = float(Fiv[3].strip("' "))
                lpMean = float(Fiv[4].strip("' "))
                lpDev = float(Fiv[5].strip("' "))
                # --------------------------------
                sUCLlp = float(Fiv[6].strip("' "))
                sLCLlp = float(Fiv[7].strip("' "))
                # --------------------------------
                lpUSL = (lpUCL - lpMean) / 3 * 6
                lpLSL = (lpMean - lpLCL) / 3 * 6
                # -------------------------------
        else:  # Computes Shewhart constants (Automatic Limits)
            lpUCL = 0
            lpLCL = 0
            lpMean = 0
            lpDev = 0
            sUCLlp = 0
            sLCLlp = 0
            lpUSL = 0
            lpLSL = 0
            lpPerf = '$Cp_{k' + str(sSize) + '}$'  # Using Automatic group Mean
            lplabel = 'Cp'

        # ------------------------------------[End of Tape Temperature Abstraction]
        label = ttk.Label(self, text='[' + rType + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Define Axes ---------------------#
        f = Figure(figsize=(25, 8), dpi=100)
        f.subplots_adjust(left=0.022, bottom=0.05, right=0.993, top=0.967, wspace=0.18, hspace=0.174)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 4, (1, 3))   # X Bar Plot
        a2 = f.add_subplot(2, 4, (5, 7))   # S Bar Plo
        a3 = f.add_subplot(2, 4, (4, 8))   # Performance Feeed
        # --------------- Former format -------------

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minLP, YScale_maxLP = lpLSL - 8.5, lpUSL + 8.5       # Roller Force
        sBar_minLP, sBar_maxLP = sLCLlp - 80, sUCLlp + 80           # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (int(lpSize) + 3)             # windows view = visible data points

        # ----------------------------------------------------------#
        # Real-Time Parameter according to updated requirements ----# 27/Feb/2025
        T1 = WON + '_LP'  # Laser Power
        # ----------------------------------------------------------#

        # Initialise runtime limits
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        a1.set_title('Laser Power [XBar]', fontsize=12, fontweight='bold')
        a2.set_title('Laser Power [StDev]', fontsize=12, fontweight='bold')

        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a1.legend(loc='upper right', title='Laser Power (Watt)')
        a2.legend(loc='upper right', title='Sigma curve')

        # ----------------------------------------------------------#
        a1.set_ylim([YScale_minLP, YScale_maxLP], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        a2.set_ylim([sBar_minLP, sBar_maxLP], auto=True)
        a2.set_xlim([window_Xmin, window_Xmax])

        # ---------------------------------------------------------[]
        a3.cla()
        a3.get_yaxis().set_visible(False)
        a3.get_xaxis().set_visible(False)

        # ---------------------------------------------------------[]
        # Define Plot area and axes -
        # ---------------------------------------------------------#
        im10, = a1.plot([], [], 'o-', label='Laser Power - (R1H1)')
        im11, = a1.plot([], [], 'o-', label='Laser Power - (R1H2)')
        im12, = a1.plot([], [], 'o-', label='Laser Power - (R1H3)')
        im13, = a1.plot([], [], 'o-', label='Laser Power - (R1H4)')
        im14, = a2.plot([], [], 'o-', label='Laser Power')
        im15, = a2.plot([], [], 'o-', label='Laser Power')
        im16, = a2.plot([], [], 'o-', label='Laser Power')
        im17, = a2.plot([], [], 'o-', label='Laser Power')

        im18, = a1.plot([], [], 'o-', label='Laser Power - (R2H1)')
        im19, = a1.plot([], [], 'o-', label='Laser Power - (R2H2)')
        im20, = a1.plot([], [], 'o-', label='Laser Power - (R2H3)')
        im21, = a1.plot([], [], 'o-', label='Laser Power - (R2H4)')
        im22, = a2.plot([], [], 'o-', label='Laser Power')
        im23, = a2.plot([], [], 'o-', label='Laser Power')
        im24, = a2.plot([], [], 'o-', label='Laser Power')
        im25, = a2.plot([], [], 'o-', label='Laser Power')

        im26, = a1.plot([], [], 'o-', label='Laser Power - (R3H1)')
        im27, = a1.plot([], [], 'o-', label='Laser Power - (R3H2)')
        im28, = a1.plot([], [], 'o-', label='Laser Power - (R3H3)')
        im29, = a1.plot([], [], 'o-', label='Laser Power - (R3H4)')
        im30, = a2.plot([], [], 'o-', label='Laser Power')
        im31, = a2.plot([], [], 'o-', label='Laser Power')
        im32, = a2.plot([], [], 'o-', label='Laser Power')
        im33, = a2.plot([], [], 'o-', label='Laser Power')

        im34, = a1.plot([], [], 'o-', label='Laser Power - (R4H1)')
        im35, = a1.plot([], [], 'o-', label='Laser Power - (R4H2)')
        im36, = a1.plot([], [], 'o-', label='Laser Power - (R4H3)')
        im37, = a1.plot([], [], 'o-', label='Laser Power - (R4H4)')
        im38, = a2.plot([], [], 'o-', label='Laser Power')
        im39, = a2.plot([], [], 'o-', label='Laser Power')
        im40, = a2.plot([], [], 'o-', label='Laser Power')
        im41, = a2.plot([], [], 'o-', label='Laser Power')

        # Statistical Feed -----------------------------------------[]
        a3.text(0.466, 0.945, 'Performance Feed - LP', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        a3.add_patch(rect1)
        a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)---------------------
        a3.text(0.145, 0.804, lplabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.658, '#Pp Value', fontsize=24, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.650, 0.820, 'Ring ' + lplabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        a3.text(0.145, 0.403, lpPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=22, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring ' + lpPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
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
        def synchronousLP(lpSize, lpgType, fetchT):
            fetch_no = str(fetchT)                  # entry value in string sql syntax

            # Obtain Volatile Data from PLC Host Server ---------------------------[]
            if not inUseAlready:                    # Load CommsPlc class once
                import CommsSql as q
                q.DAQ_connect(1, 0)
            else:
                con_lp = conn.cursor()

            # Evaluate conditions for SQL Data Fetch ------------------------------[A]
            """
            Load watchdog function with synchronous function every seconds
            """
            # Initialise RT variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard                         # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                if UsePLC_DBS:                              # Not Using PLC Data
                    import plcArrayRLmethodLP as slp         # DrLabs optimization method

                    inProgress = False                      # False for Real-time mode
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
                    # -----------------------------------------------------------------[]

                    # Allow selective runtime parameter selection on production critical process
                    procID = 'LP'
                    lpData = slp.paramDataRequest(procID, lpSize, lpgType, fetch_no)

                else:
                    import sqlArrayRLmethodLP as slp        # DrLabs optimization method

                    inProgress = True                       # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve M.State from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    if keyboard.is_pressed("Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            print("\nVisualization in Paused Mode...")
                        else:
                            autoSpcPause = False
                            print("Visualization in Real-time Mode...")
                    else:
                        # Get list of relevant SQL Tables using conn() --------------------[]
                        lpData = slp.sqlexec(lpSize, lpgType, con_lp, T1, fetchT)

                    # ------ Inhibit iteration ----------------------------------------------------------[]
                    """
                    # Set condition for halting real-time plots in watchdog class ---------------------
                    """
                    # TODO --- values for inhibiting the SQL processing
                    if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                        con_lp.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

            return lpData

        # ================== End of synchronous Method ==========================
        def asynchronousLP(db_freq):
            timei = time.time()                                 # start timing the entire loop

            # Bistream Data Pooling Method ---------------------#
            lpData = synchronousLP(lpSize, lpgType, db_freq)    # data loading functions
            # --------------------------------------------------#

            if UsePLC_DBS == 1:
                import VarPLClp as lp

                viz_cycle = 10
                # Call synchronous data function ---------------[]
                columns = qlp.validCols(T1)                     # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(lpData, columns=columns)     # Include table data into python Dataframe
                LP = lp.loadProcesValues(df1)                   # Join data values under dataframe

            else:
                import VarSQL_DFlp as lp                        # load SQL variables column names | rfVarSQL

                viz_cycle = 150
                g1 = qlp.validCols(T1)                          # Construct Data Column selSqlColumnsTFM.py
                df1 = pd.DataFrame(lpData, columns=g1)          # Import into python Dataframe
                LP = lp.loadProcesValues(df1)                   # Join data values under dataframe

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
            im10.set_ydata((LP[0]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 1
            im11.set_ydata((LP[1]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 2
            im12.set_ydata((LP[2]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 3
            im13.set_ydata((LP[3]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 1 ---------#
            mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(lpHL, lpSize, 'LP')
            # ---------------------------------------#
            im14.set_ydata((LP[4]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 1
            im15.set_ydata((LP[5]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 2
            im16.set_ydata((LP[6]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 3
            im17.set_ydata((LP[7]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 2 ---------#
            mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(lpHL, lpSize, 'LP')
            # ---------------------------------------#
            im18.set_ydata((LP[8]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 1
            im19.set_ydata((LP[9]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 2
            im20.set_ydata((LP[10]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 3
            im21.set_ydata((LP[11]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 3 ---------#
            mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(lpHL, lpSize, 'LP')
            # ---------------------------------------#
            im22.set_ydata((LP[12]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 1
            im23.set_ydata((LP[13]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 2
            im24.set_ydata((LP[14]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 3
            im25.set_ydata((LP[15]).rolling(window=lpSize, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 4 ---------#
            mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(lpHL, lpSize, 'LP')
            # ---------------------------------------#
            # S Plot Y-Axis data points for StdDev ----------------------------------------
            im26.set_ydata((LP[0]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
            im27.set_ydata((LP[1]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
            im28.set_ydata((LP[2]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
            im29.set_ydata((LP[3]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])

            im30.set_ydata((LP[4]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
            im31.set_ydata((LP[5]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
            im32.set_ydata((LP[6]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
            im33.set_ydata((LP[7]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])

            im34.set_ydata((LP[8]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
            im35.set_ydata((LP[9]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
            im36.set_ydata((LP[10]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
            im37.set_ydata((LP[11]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])

            im38.set_ydata((LP[12]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
            im39.set_ydata((LP[13]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
            im40.set_ydata((LP[14]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])
            im41.set_ydata((LP[15]).rolling(window=lpSize, min_periods=1).std()[0:db_freq])

            # Compute entire Process Capability -----------#
            if not lpHL:
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLb, ppT, pkT, xline, sline = tq.tAutoPerf(lpSize, mnA, mnB,
                                                                                                      mnC, mnD, sdA,
                                                                                                      sdB, sdC, sdD)
            else:
                xline, sline = lpMean, lpDev
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLba, ppT, pkT = tq.tManualPerf(mnA, mnB, mnC, mnD, sdA, sdB,
                                                                                           sdC, sdD, lpUSL, lpLSL,
                                                                                           lpUCL,
                                                                                           lpLCL)

            # # Declare Plots attributes --------------------------------------------------------[]
            # XBar Mean Plot
            a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
            a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 3 Sigma span (Purple)
            a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minLP, sBar_maxLP -------[]
            # Define Legend's Attributes  ----
            a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
            a2.axhspan(sLCLlp, sUCLlp, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 1 Sigma Span
            a2.axhspan(sUCLlp, sBar_maxLP, facecolor='#CCCCFF', edgecolor='#CCCCFF')  # 1 Sigma above the Mean
            a2.axhspan(sBar_minLP, sLCLlp, facecolor='#CCCCFF', edgecolor='#CCCCFF')

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
                a2.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a1.set_xlim(0, window_Xmax)
                a2.set_xlim(0, window_Xmax)

            # Set trip line for individual time-series plot -----------------------------------[R1]
            import triggerModule as sigma
            sigma.trigViolations(a1, UsePLC_DBS, 'LP', YScale_minLP, YScale_maxLP, xucT, xlcT, xusT, xlsT, mnT, sdT)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousLP, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)

        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

# ---------------------------------------------------------------------------------------------[P2]

class laserAngleTabb(ttk.Frame):      # -- Defines the tabbed region for QA param - Tape Temperature --[]
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        # Load Quality Historical Values -----------[]
        laSize, lagType, laSspace, laHL, laAL, laFO, laParam1, laParam2, laParam3, laParam4, laParam5 = mq.decryptpProcessLim(
            WON, 'LA')
        # Break down each element to useful list ---------------[Tape Temperature]
        if laHL and laParam1 and laParam2 and laParam3 and laParam4 and laParam5:  #
            laPerf = '$Pp_{k' + str(sSize) + '}$'  # Using estimated or historical Mean
            lalabel = 'Pp'
            # -------------------------------
            One = laParam1.split(',')                   # split into list elements
            Two = laParam2.split(',')
            Thr = laParam3.split(',')
            For = laParam4.split(',')
            Fiv = laParam5.split(',')
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
                laUCL = float(One[2].strip("' "))       # Strip out the element of the list
                laLCL = float(One[3].strip("' "))
                laMean = float(One[4].strip("' "))
                laDev = float(One[5].strip("' "))
                # --------------------------------
                sUCLla = float(One[6].strip("' "))
                sLCLla = float(One[7].strip("' "))
                # --------------------------------
                laUSL = (laUCL - laMean) / 3 * 6
                laLSL = (laMean - laLCL) / 3 * 6
                # --------------------------------
            elif cpTapeW == dTape2 and cpLayerNo == 2:
                laUCL = float(Two[2].strip("' "))       # Strip out the element of the list
                laLCL = float(Two[3].strip("' "))
                laMean = float(Two[4].strip("' "))
                laDev = float(Two[5].strip("' "))
                # --------------------------------
                sUCLla = float(Two[6].strip("' "))
                sLCLla = float(Two[7].strip("' "))
                # --------------------------------
                laUSL = (laUCL - laMean) / 3 * 6
                laLSL = (laMean - laLCL) / 3 * 6
            elif cpTapeW == dTape3 and cpLayerNo == range(3, 40):
                laUCL = float(Thr[2].strip("' "))       # Strip out the element of the list
                laLCL = float(Thr[3].strip("' "))
                laMean = float(Thr[4].strip("' "))
                laDev = float(Thr[5].strip("' "))
                # --------------------------------
                sUCLla = float(Thr[6].strip("' "))
                sLCLla = float(Thr[7].strip("' "))
                # --------------------------------
                laUSL = (laUCL - laMean) / 3 * 6
                laLSL = (laMean - laLCL) / 3 * 6
            elif cpTapeW == dTape4 and cpLayerNo == 41:
                laUCL = float(For[2].strip("' "))       # Strip out the element of the list
                laLCL = float(For[3].strip("' "))
                laMean = float(For[4].strip("' "))
                laDev = float(For[5].strip("' "))
                # --------------------------------
                sUCLla = float(For[6].strip("' "))
                sLCLla = float(For[7].strip("' "))
                # --------------------------------
                laUSL = (laUCL - laMean) / 3 * 6
                laLSL = (laMean - laLCL) / 3 * 6
            else:
                laUCL = float(Fiv[2].strip("' "))       # Strip out the element of the list
                laLCL = float(Fiv[3].strip("' "))
                laMean = float(Fiv[4].strip("' "))
                laDev = float(Fiv[5].strip("' "))
                # --------------------------------
                sUCLla = float(Fiv[6].strip("' "))
                sLCLla = float(Fiv[7].strip("' "))
                # --------------------------------
                laUSL = (laUCL - laMean) / 3 * 6
                laLSL = (laMean - laLCL) / 3 * 6
                # -------------------------------
        else:  # Computes Shewhart constants (Automatic Limits)
            laUCL = 0
            laLCL = 0
            laMean = 0
            laDev = 0
            sUCLla = 0
            sLCLla = 0
            laUSL = 0
            laLSL = 0
            laPerf = '$Cp_{k' + str(sSize) + '}$'  # Using Automatic group Mean
            lalabel = 'Cp'

        # ------------------------------------[End of Tape Temperature Abstraction]

        label = ttk.Label(self, text='[' + rType + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Define Axes ---------------------#
        f = Figure(figsize=(25, 8), dpi=100)
        f.subplots_adjust(left=0.022, bottom=0.05, right=0.993, top=0.967, wspace=0.18, hspace=0.174)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 4, (1, 3))   # X Bar Plot
        a2 = f.add_subplot(2, 4, (5, 7))   # S Bar Plo
        a3 = f.add_subplot(2, 4, (4, 8))   # Performance Feeed
        # --------------- Former format -------------

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minLA, YScale_maxLA = laLSL - 8.5, laUSL + 8.5       # Roller Force
        sBar_minLA, sBar_maxLA = sLCLla - 80, sUCLla + 80           # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (int(laSize) + 3)             # windows view = visible data points
        # ----------------------------------------------------------#
        # Real-Time Parameter according to updated requirements ----# 07/Feb/2025
        if int(LP) and int(LA) and int(CT) and int(OT) and int(RP) and int(WS):
            print('\n MGM params condition met....', OT, CT, RP, WS)
            T1 = WON + '_LA'  # Laser Power
        else:
            pass

        # Initialise runtime limits
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        a1.set_title('Laser Angle [XBar Plot]', fontsize=12, fontweight='bold')
        a2.set_title('Laser Angle [S Plot]', fontsize=12, fontweight='bold')

        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a1.legend(loc='upper right', title='Laser Angle (Deg)')
        a2.legend(loc='upper right', title='Sigma curve')

        # ----------------------------------------------------------#
        a1.set_ylim([YScale_minLA, YScale_maxLA], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        a2.set_ylim([sBar_minLA, sBar_maxLA], auto=True)
        a2.set_xlim([window_Xmin, window_Xmax])

        # ---------------------------------------------------------[]
        a3.cla()
        a3.get_yaxis().set_visible(False)
        a3.get_xaxis().set_visible(False)

        # ---------------------------------------------------------[]
        # Define Plot area and axes -
        # ---------------------------------------------------------#
        im10, = a1.plot([], [], 'o-.', label='Laser Angle - (R1H1)')
        im11, = a1.plot([], [], 'o-', label='Laser Angle - (R1H2)')
        im12, = a1.plot([], [], 'o-', label='Laser Angle - (R1H3)')
        im13, = a1.plot([], [], 'o-', label='Laser Angle - (R1H4)')
        im14, = a2.plot([], [], 'o-', label='Laser Angle')
        im15, = a2.plot([], [], 'o-', label='Laser Angle')
        im16, = a2.plot([], [], 'o-', label='Laser Angle')
        im17, = a2.plot([], [], 'o-', label='Laser Angle')

        im18, = a1.plot([], [], 'o-.', label='Laser Angle - (R2H1)')
        im19, = a1.plot([], [], 'o-', label='Laser Angle - (R2H2)')
        im20, = a1.plot([], [], 'o-', label='Laser Angle - (R2H3)')
        im21, = a1.plot([], [], 'o-', label='Laser Angle - (R2H4)')
        im22, = a2.plot([], [], 'o-', label='Laser Angle')
        im23, = a2.plot([], [], 'o-', label='Laser Angle')
        im24, = a2.plot([], [], 'o-', label='Laser Angle')
        im25, = a2.plot([], [], 'o-', label='Laser Angle')

        im26, = a1.plot([], [], 'o-.', label='Laser Angle - (R3H1)')
        im27, = a1.plot([], [], 'o-', label='Laser Angle - (R3H2)')
        im28, = a1.plot([], [], 'o-', label='Laser Angle - (R3H3)')
        im29, = a1.plot([], [], 'o-', label='Laser Angle - (R3H4)')
        im30, = a2.plot([], [], 'o-', label='Laser Angle')
        im31, = a2.plot([], [], 'o-', label='Laser Angle')
        im32, = a2.plot([], [], 'o-', label='Laser Angle')
        im33, = a2.plot([], [], 'o-', label='Laser Angle')

        im34, = a1.plot([], [], 'o-.', label='Laser Angle - (R4H1)')
        im35, = a1.plot([], [], 'o-', label='Laser Angle - (R4H2)')
        im36, = a1.plot([], [], 'o-', label='Laser Angle - (R4H3)')
        im37, = a1.plot([], [], 'o-', label='Laser Angle - (R4H4)')
        im38, = a2.plot([], [], 'o-', label='Laser Angle')
        im39, = a2.plot([], [], 'o-', label='Laser Angle')
        im40, = a2.plot([], [], 'o-', label='Laser Angle')
        im41, = a2.plot([], [], 'o-', label='Laser Angle')

        # Statistical Feed -----------------------------------------[]
        a3.text(0.466, 0.945, 'Performance Feed - LA', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        a3.add_patch(rect1)
        a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)---------------------
        a3.text(0.145, 0.804, lalabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.658, '#Pp Value', fontsize=24, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.650, 0.820, 'Ring ' + lalabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        a3.text(0.145, 0.403, laPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=22, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring ' + laPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
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
        def synchronousLA(laSize, lagType, fetchT):
            fetch_no = str(fetchT)  # entry value in string sql syntax

            # Obtain Volatile Data from PLC Host Server ---------------------------[]
            if not inUseAlready:  # Load CommsPlc class once
                import CommsSql as q
                q.DAQ_connect(1, 0)
            else:
                con_la = conn.cursor()

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
                if UsePLC_DBS:                               # Not Using PLC Data
                    import plcArrayRLmethodLA as sla         # DrLabs optimization method

                    inProgress = True                        # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')

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
                        print("Visualization in Real-time Mode...")
                        # Allow selective runtime parameter selection on production critical process
                        laData = sla.paramDataRequest(T1, laSize, lagType, fetch_no)

                else:
                    import sqlArrayRLmethodLA as sla

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
                            print("Visualization in Real-time Mode...")
                    else:
                        # Get list of relevant SQL Tables using conn() ----------------[]
                        laData = sla.sqlexec(laSize, lagType, con_la, T1, fetchT)

                    # ------ Inhibit iteration ----------------------------------------------------------[]
                    """
                    # Set condition for halting real-time plots in watchdog class ---------------------
                    """
                    # TODO --- values for inhibiting the SQL processing
                    if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                        con_la.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

            return laData

        # ================== End of synchronous Method ==========================
        def asynchronousLA(db_freq):
            timei = time.time()                                 # start timing the entire loop

            # Bistream Data Pooling Method ---------------------#
            laData = synchronousLA(laSize, lagType, db_freq)    # data loading functions
            # --------------------------------------------------#

            if UsePLC_DBS == 1:
                import VarPLCla as la

                viz_cycle = 10
                # Call synchronous data function ---------------[]
                columns = qla.validCols(T1)                    # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(laData, columns=columns)    # Include table data into python Dataframe
                LA = la.loadProcesValues(df1)                  # Join data values under dataframe

            else:
                import VarSQLla as la                          # load SQL variables column names | rfVarSQL

                viz_cycle = 150
                g1 = qla.validCols(T1)                         # Construct Data Column selSqlColumnsTFM.py
                df1 = pd.DataFrame(laData, columns=g1)         # Import into python Dataframe
                LA = la.loadProcesValues(df1)                  # Join data values under dataframe

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
            im10.set_ydata((LA[0]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 1
            im11.set_ydata((LA[1]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 2
            im12.set_ydata((LA[2]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 3
            im13.set_ydata((LA[3]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 1 ---------#
            mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(laHL, laSize, 'LA')
            # ---------------------------------------#
            im14.set_ydata((LA[4]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 1
            im15.set_ydata((LA[5]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 2
            im16.set_ydata((LA[6]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 3
            im17.set_ydata((LA[7]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 2 ---------#
            mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(laHL, laSize, 'LA')
            # ---------------------------------------#
            im18.set_ydata((LA[8]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 1
            im19.set_ydata((LA[9]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 2
            im20.set_ydata((LA[10]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 3
            im21.set_ydata((LA[11]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 3 ---------#
            mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(laHL, laSize, 'LA')
            # ---------------------------------------#
            im22.set_ydata((LA[12]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 1
            im23.set_ydata((LA[13]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 2
            im24.set_ydata((LA[14]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 3
            im25.set_ydata((LA[15]).rolling(window=laSize, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 4 ---------#
            mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(laHL, laSize, 'LA')
            # ---------------------------------------#
            # S Plot Y-Axis data points for StdDev ----------------------------------------
            im26.set_ydata((LA[0]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
            im27.set_ydata((LA[1]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
            im28.set_ydata((LA[2]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
            im29.set_ydata((LA[3]).rolling(window=laSize, min_periods=1).std()[0:db_freq])

            im30.set_ydata((LA[4]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
            im31.set_ydata((LA[5]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
            im32.set_ydata((LA[6]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
            im33.set_ydata((LA[7]).rolling(window=laSize, min_periods=1).std()[0:db_freq])

            im34.set_ydata((LA[8]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
            im35.set_ydata((LA[9]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
            im36.set_ydata((LA[10]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
            im37.set_ydata((LA[11]).rolling(window=laSize, min_periods=1).std()[0:db_freq])

            im38.set_ydata((LA[12]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
            im39.set_ydata((LA[13]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
            im40.set_ydata((LA[14]).rolling(window=laSize, min_periods=1).std()[0:db_freq])
            im41.set_ydata((LA[15]).rolling(window=laSize, min_periods=1).std()[0:db_freq])

            # Compute entire Process Capability -----------#
            if not laHL:
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLb, ppT, pkT, xline, sline = tq.tAutoPerf(laSize, mnA, mnB,
                                                                                                      mnC, mnD, sdA,
                                                                                                      sdB, sdC, sdD)
            else:
                xline, sline = laMean, laDev
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLba, ppT, pkT = tq.tManualPerf(mnA, mnB, mnC, mnD, sdA, sdB,
                                                                                           sdC, sdD, laUSL, laLSL,
                                                                                           laUCL,
                                                                                           laLCL)

            # # Declare Plots alaributes --------------------------------------------------------[]
            # XBar Mean Plot
            a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
            a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 3 Sigma span (Purple)
            a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minLP, sBar_maxLP -------[]
            # Define Legend's Alaributes  ----
            a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
            a2.axhspan(sLCLla, sUCLla, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 1 Sigma Span
            a2.axhspan(sUCLla, sBar_maxLA, facecolor='#CCCCFF', edgecolor='#CCCCFF')  # 1 Sigma above the Mean
            a2.axhspan(sBar_minLA, sLCLla, facecolor='#CCCCFF', edgecolor='#CCCCFF')

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
                a2.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a1.set_xlim(0, window_Xmax)
                a2.set_xlim(0, window_Xmax)

            # Set trip line for individual time-series plot -----------------------------------[R1]
            import triggerModule as sigma
            sigma.trigViolations(a1, UsePLC_DBS, 'LA', YScale_minLA, YScale_maxLA, xucT, xlcT, xusT, xlsT, mnT, sdT)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousLA, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

# ---------------------------------------------------------------------------------------------[Tape Placement P3]

class tapePlacementTabb(ttk.Frame):     # -- Defines the tabbed region for QA param - Substrate Temperature --[]
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        # --------------------------------------------------------------------[]
        tpSize, tpgType, tpSspace, tpHL, tpAL, tptFO, tpParam1, dud2, dud3, dud4, dud5 = mq.decryptpProcessLim(WON, 'WS')
        # Break down each element to useful list ----------------[Winding Speed]

        if tpHL and tpParam1:  # Roller Pressure TODO - layer metrics to guide TCP01
            tpPerf = '$Pp_{k' + str(sSize) + '}$'               # Using estimated or historical Mean
            tplabel = 'Pp'
            # -------------------------------
            tpOne = tpParam1.split(',')                 # split into list elements
            dTapetp = tpOne[1].strip("' ")              # defined Tape Width
            dLayer = tpOne[10].strip("' ")              # Defined Tape Layer

            # Load historical limits for the process------------#
            tpUCL = float(tpOne[2].strip("' "))          # Strip out the element of the list
            tpLCL = float(tpOne[3].strip("' "))
            tpMean = float(tpOne[4].strip("' "))
            tpDev = float(tpOne[5].strip("' "))
            # --------------------------------
            sUCLtp = float(tpOne[6].strip("' "))
            sLCLtp = float(tpOne[7].strip("' "))
            # --------------------------------
            tpUSL = (tpUCL - tpMean) / 3 * 6
            tpLSL = (tpMean - tpLCL) / 3 * 6
            # --------------------------------
        else:  # Computes Shewhart constants (Automatic Limits)
            tpUCL = 0
            tpLCL = 0
            tpMean = 0
            tpDev = 0
            sUCLtp = 0
            sLCLtp = 0
            tpUSL = 0
            tpLSL = 0
            tpPerf = '$Cp_{k' + str(sSize) + '}$'  # Using Automatic group Mean
            tplabel = 'Cp'

        # ------------------------------------[End of Winding Speed Abstraction]

        label = ttk.Label(self, text='[' + rType + ' Mode]', font=LARGE_FONT)
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
        YScale_minTP, YScale_maxTP = tpLSL - 8.5, tpUSL + 8.5       # Roller Force
        sBar_minTP, sBar_maxTP = sLCLtp - 80, sUCLtp + 80           # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (smp_Sz + 3)                  # windows view = visible data points

        # ----------------------------------------------------------#
        # Real-Time Parameter according to updated requirements ----# 27/Feb/2025
        T1 = WON + '_TP'  # Tape Placement Error
        # ----------------------------------------------------------#

        # Initialise runtime limits
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        a1.set_title('Tape Placement Error [XBar Plot]', fontsize=12, fontweight='bold')
        a2.set_title('Tape Placement Error [S Plot]', fontsize=12, fontweight='bold')
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a1.legend(loc='upper right', title='Tape Placement Error - %')
        a2.legend(loc='upper right', title='Sigma curve')
        # Initialise runtime limits --------------------------------#
        a1.set_ylim([YScale_minTP, YScale_maxTP], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        a2.set_ylim([sBar_minTP, sBar_maxTP], auto=True)
        a2.set_xlim([window_Xmin, window_Xmax])

        # ----------------------------------------------------------[]
        a3.cla()
        a3.get_yaxis().set_visible(False)
        a3.get_xaxis().set_visible(False)

        # --------------------------------------------------------------[]
        # Define Plot area and axes -
        # ----------------------------------------------------------------#
        im10, = a1.plot([], [], 'o-', label='Placement Error (%) - (R1H1)')
        im11, = a1.plot([], [], 'o-', label='Placement Error (%) - (R1H2)')
        im12, = a1.plot([], [], 'o-', label='Placement Error (%) - (R1H3)')
        im13, = a1.plot([], [], 'o-', label='Placement Error (%) - (R1H4)')
        im14, = a2.plot([], [], 'o-', label='Placement Error (%)')
        im15, = a2.plot([], [], 'o-', label='Placement Error (%)')
        im16, = a2.plot([], [], 'o-', label='Placement Error (%)')
        im17, = a2.plot([], [], 'o-', label='Placement Error (%)')

        im18, = a1.plot([], [], 'o-', label='Placement Error (%) - (R2H1)')
        im19, = a1.plot([], [], 'o-', label='Placement Error (%) - (R2H2)')
        im20, = a1.plot([], [], 'o-', label='Placement Error (%) - (R2H3)')
        im21, = a1.plot([], [], 'o-', label='Placement Error (%) - (R2H4)')
        im22, = a2.plot([], [], 'o-', label='Placement Error (%)')
        im23, = a2.plot([], [], 'o-', label='Placement Error (%)')
        im24, = a2.plot([], [], 'o-', label='Placement Error (%)')
        im25, = a2.plot([], [], 'o-', label='Placement Error (%)')

        im26, = a1.plot([], [], 'o-', label='Placement Error (%) - (R3H1)')
        im27, = a1.plot([], [], 'o-', label='Placement Error (%) - (R3H2)')
        im28, = a1.plot([], [], 'o-', label='Placement Error (%) - (R3H3)')
        im29, = a1.plot([], [], 'o-', label='Placement Error (%) - (R3H4)')
        im30, = a2.plot([], [], 'o-', label='Placement Error (%)')
        im31, = a2.plot([], [], 'o-', label='Placement Error (%)')
        im32, = a2.plot([], [], 'o-', label='Placement Error (%)')
        im33, = a2.plot([], [], 'o-', label='Placement Error (%)')

        im34, = a1.plot([], [], 'o-', label='Placement Error (%) - (R4H1)')
        im35, = a1.plot([], [], 'o-', label='Placement Error (%) - (R4H2)')
        im36, = a1.plot([], [], 'o-', label='Placement Error (%) - (R4H3)')
        im37, = a1.plot([], [], 'o-', label='Placement Error (%) - (R4H4)')
        im38, = a2.plot([], [], 'o-', label='Placement Error (%)')
        im39, = a2.plot([], [], 'o-', label='Placement Error (%)')
        im40, = a2.plot([], [], 'o-', label='Placement Error (%)')
        im41, = a2.plot([], [], 'o-', label='Placement Error (%)')

        # Statistical Feed -----------------------------------------[]
        a3.text(0.466, 0.945, 'Performance Feed - TP', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        a3.add_patch(rect1)
        a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)---------------------
        a3.text(0.145, 0.804, tplabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.658, '#Pp Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.650, 0.820, 'Ring ' + tplabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        a3.text(0.145, 0.403, tpPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring ' + tpPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
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
        def synchronousTP(wsSize, wsgType, fetchT):
            fetch_no = str(fetchT)  # entry value in string sql syntax

            # Obtain Volatile Data from PLC Host Server ---------------------------[]
            if not inUseAlready:  # Load CommsPlc class once
                import CommsSql as q
                q.DAQ_connect(1, 0)
            else:
                con_tp = conn.cursor()

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
                if UsePLC_DBS:                                          # Not Using PLC Data
                    import plcArrayRLmethodTP as stp                     # DrLabs optimization method

                    inProgress = True                                   # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')

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
                    # -----------------------------------------------------------------[]

                    # Allow selective runtime parameter selection on production critical process
                    procID = 'TP'
                    tpData = stp.paramDataRequest(procID, wsSize, wsgType, fetch_no)

                else:
                    import sqlArrayRLmethodTP as stp                # DrLabs optimization method

                    inProgress = False  # False for Real-time mode
                    print('\nSynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

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
                    else:
                        # Get list of relevant SQL Tables using conn() --------------------[]
                        tpData = stp.sqlexec(wsSize, wsgType, con_tp, T1, fetchT)

                    # ------ Inhibit iteration ----------------------------------------------------------[]
                    """
                    # Set condition for halting real-time plots in watchdog class ---------------------
                    """
                    # TODO --- values for inhibiting the SQL processing
                    if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                        con_tp.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

            return tpData

        # ================== End of synchronous Method ==========================
        def asynchronousTP(db_freq):

            timei = time.time()                                 # start timing the entire loop
            UsePLC_DBS = rType                                  # Query Type

            # Call data loader Method---------------------------#
            tpData = synchronousTP(tpSize, tpgType, db_freq)  # data loading functions
            if UsePLC_DBS == 1:
                import VarPLCrf as tp

                viz_cycle = 10
                # Call synchronous data function ---------------[]
                columns = qtp.validCols(T1)                    # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(tpData, columns=columns)    # Include table data into python Dataframe
                TP = tp.loadProcesValues(df1)                  # Join data values under dataframe

            else:
                import VarSQLrf as tp                          # load SQL variables column names | rfVarSQL

                viz_cycle = 150
                g1 = qtp.validCols('TP')                       # Construct Data Column selSqlColumnsTFM.py
                df1 = pd.DataFrame(tpData, columns=g1)         # Import into python Dataframe
                TP = tp.loadProcesValues(df1)                  # Join data values under dataframe

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
            im10.set_ydata((WS[0]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # head 1
            im11.set_ydata((WS[1]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # head 2
            im12.set_ydata((WS[2]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # head 3
            im13.set_ydata((WS[3]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 1 ---------#
            mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(tpHL, tpSize, 'TP')
            # ---------------------------------------#
            im14.set_ydata((WS[4]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # head 1
            im15.set_ydata((WS[5]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # head 2
            im16.set_ydata((WS[6]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # head 3
            im17.set_ydata((WS[7]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 2 ---------#
            mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(tpHL, tpSize, 'TP')
            # ---------------------------------------#
            im18.set_ydata((WS[8]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # head 1
            im19.set_ydata((WS[9]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # head 2
            im20.set_ydata((WS[10]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # head 3
            im21.set_ydata((WS[11]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 3 ---------#
            mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(tpHL, tpSize, 'TP')
            # ---------------------------------------#
            im22.set_ydata((WS[12]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # head 1
            im23.set_ydata((WS[13]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # head 2
            im24.set_ydata((WS[14]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # head 3
            im25.set_ydata((WS[15]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 4 ---------#
            mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(tpHL, tpSize, 'TP')
            # ---------------------------------------#
            # S Plot Y-Axis data points for StdDev ----------------------------------------
            im26.set_ydata((WS[0]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
            im27.set_ydata((WS[1]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
            im28.set_ydata((WS[2]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
            im29.set_ydata((WS[3]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])

            im30.set_ydata((WS[4]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
            im31.set_ydata((WS[5]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
            im32.set_ydata((WS[6]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
            im33.set_ydata((WS[7]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])

            im34.set_ydata((WS[8]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
            im35.set_ydata((WS[9]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
            im36.set_ydata((WS[10]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
            im37.set_ydata((WS[11]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])

            im38.set_ydata((WS[12]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
            im39.set_ydata((WS[13]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
            im40.set_ydata((WS[14]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
            im41.set_ydata((WS[15]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])

            # Compute entire Process Capability -----------#
            if not tpHL:
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLa, dLCLa, ppT, pkT, xline, sline = tq.tAutoPerf(tpSize, mnA, mnB,
                                                                                                      mnC, mnD, sdA,
                                                                                                      sdB, sdC, sdD)
            else:
                xline, sline = tpMean, tpDev
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLa, dLCLa, ppT, pkT = tq.tManualPerf(mnA, mnB, mnC, mnD, sdA, sdB,
                                                                                          sdC, sdD, tpUSL, tpLSL, tpUCL,
                                                                                          tpLCL)
            # # Declare Plots attributes ------------------------------------------------------------[]
            # XBar Mean Plot
            a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
            a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')            # 3 Sigma span (Purple)
            a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')            # grey area
            a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minTT, sBar_maxTT -------[]
            # Define Legend's Attributes  ----
            a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
            a2.axhspan(sLCLtp, sUCLtp, facecolor='#F9C0FD', edgecolor='#F9C0FD')        # 1 Sigma Span
            a2.axhspan(sUCLtp, sBar_maxTP, facecolor='#CCCCFF', edgecolor='#CCCCFF')    # 1 Sigma above the Mean
            a2.axhspan(sBar_minTP, sLCLtp, facecolor='#CCCCFF', edgecolor='#CCCCFF')

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
                a2.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a1.set_xlim(0, window_Xmax)
                a2.set_xlim(0, window_Xmax)

            # Set trip line for individual time-series plot -----------------------------------[R1]
            import triggerModule as sigma
            sigma.trigViolations(a1, UsePLC_DBS, 'WS', YScale_minTP, YScale_maxTP, xucT, xlcT, xusT, xlsT, mnT, sdT)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousTP, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)

        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)
# ----------------------------------------------------------------------------------------------[Roller Force P4]

class rollerForceTabb(ttk.Frame):
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        # Load Quality Historical Values -----------[]
        rfSize, rfgType, rfSspace, rfHL, rfAL, rfFO, rfParam1, rfParam2, rfParam3, rfParam4, rfParam5 = mq.decryptpProcessLim(
            WON, 'RF')
        # Break down each element to useful list ---------------[Tape Temperature]
        if rfHL and rfParam1 and rfParam2 and rfParam3 and rfParam4 and rfParam5:  #
            rfPerf = '$Pp_{k' + str(sSize) + '}$'  # Using estimated or historical Mean
            rflabel = 'Pp'
            # -------------------------------
            One = rfParam1.split(',')                   # split into list elements
            Two = rfParam2.split(',')
            Thr = rfParam3.split(',')
            For = rfParam4.split(',')
            Fiv = rfParam5.split(',')
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
                rfUCL = float(One[2].strip("' "))       # Strip out the element of the list
                rfLCL = float(One[3].strip("' "))
                rfMean = float(One[4].strip("' "))
                rfDev = float(One[5].strip("' "))
                # --------------------------------
                sUCLrf = float(One[6].strip("' "))
                sLCLrf = float(One[7].strip("' "))
                # --------------------------------
                rfUSL = (rfUCL - rfMean) / 3 * 6
                rfLSL = (rfMean - rfLCL) / 3 * 6
                # --------------------------------
            elif cpTapeW == dTape2 and cpLayerNo == 2:
                rfUCL = float(Two[2].strip("' "))       # Strip out the element of the list
                rfLCL = float(Two[3].strip("' "))
                rfMean = float(Two[4].strip("' "))
                rfDev = float(Two[5].strip("' "))
                # --------------------------------
                sUCLrf = float(Two[6].strip("' "))
                sLCLrf = float(Two[7].strip("' "))
                # --------------------------------
                rfUSL = (rfUCL - rfMean) / 3 * 6
                rfLSL = (rfMean - rfLCL) / 3 * 6
            elif cpTapeW == dTape3 and cpLayerNo == range(3, 40):
                rfUCL = float(Thr[2].strip("' "))       # Strip out the element of the list
                rfLCL = float(Thr[3].strip("' "))
                rfMean = float(Thr[4].strip("' "))
                rfDev = float(Thr[5].strip("' "))
                # --------------------------------
                sUCLrf = float(Thr[6].strip("' "))
                sLCLrf = float(Thr[7].strip("' "))
                # --------------------------------
                rfUSL = (rfUCL - rfMean) / 3 * 6
                rfLSL = (rfMean - rfLCL) / 3 * 6
            elif cpTapeW == dTape4 and cpLayerNo == 41:
                rfUCL = float(For[2].strip("' "))       # Strip out the element of the list
                rfLCL = float(For[3].strip("' "))
                rfMean = float(For[4].strip("' "))
                rfDev = float(For[5].strip("' "))
                # --------------------------------
                sUCLrf = float(For[6].strip("' "))
                sLCLrf = float(For[7].strip("' "))
                # --------------------------------
                rfUSL = (rfUCL - rfMean) / 3 * 6
                rfLSL = (rfMean - rfLCL) / 3 * 6
            else:
                rfUCL = float(Fiv[2].strip("' "))       # Strip out the element of the list
                rfLCL = float(Fiv[3].strip("' "))
                rfMean = float(Fiv[4].strip("' "))
                rfDev = float(Fiv[5].strip("' "))
                # --------------------------------
                sUCLrf = float(Fiv[6].strip("' "))
                sLCLrf = float(Fiv[7].strip("' "))
                # --------------------------------
                rfUSL = (rfUCL - rfMean) / 3 * 6
                rfLSL = (rfMean - rfLCL) / 3 * 6
                # -------------------------------
        else:  # Computes Shewhart constants (Automatic Limits)
            rfUCL = 0
            rfLCL = 0
            rfMean = 0
            rfDev = 0
            sUCLrf = 0
            sLCLrf = 0
            rfUSL = 0
            rfLSL = 0
            rfPerf = '$Cp_{k' + str(sSize) + '}$'  # Using Automatic group Mean
            rflabel = 'Cp'

        # ------ [End of Historical abstraction -------]

        label = ttk.Label(self, text='[' + rType + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Define Axes ---------------------#
        f = Figure(figsize=(25, 8), dpi=100)
        f.subplots_adjust(left=0.022, bottom=0.05, right=0.993, top=0.967, wspace=0.18, hspace=0.174)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 4, (1, 3))   # X Bar Plot
        a2 = f.add_subplot(2, 4, (5, 7))   # S Bar Plo
        a3 = f.add_subplot(2, 4, (4, 8))   # Performance Feeed

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minRF, YScale_maxRF = 10, 500                        # Roller Force
        sBar_minRF, sBar_maxRF = 10, 250                            # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (int(rfSize) + 3)             # windows view = visible data points

        # ----------------------------------------------------------#
        # Real-Time Parameter according to updated requirements ----# 28/Feb/2025
        T1 = WON + '_RF'        # Laser Power
        # ----------------------------------------------------------#

        # Initialise runtime limits
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        a1.set_title('Roller Force [XBar Plot]', fontsize=12, fontweight='bold')
        a2.set_title('Roller Force [S Plot]', fontsize=12, fontweight='bold')
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a1.legend(loc='upper right', title='Roller Force (N.m)')
        a2.legend(loc='upper right', title='Sigma curve')

        # ----------------------------------------------------------#
        a1.set_ylim([YScale_minRF, YScale_maxRF], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        a2.set_ylim([sBar_minRF, sBar_maxRF], auto=True)
        a2.set_xlim([window_Xmin, window_Xmax])

        # ---------------------------------------------------------[]
        a3.cla()
        a3.get_yaxis().set_visible(False)
        a3.get_xaxis().set_visible(False)

        # ---------------------------------------------------------[]
        # Define Plot area and axes -
        # ---------------------------------------------------------#
        im10, = a1.plot([], [], 'o-', label='Roller Force - (R1H1)')
        im11, = a1.plot([], [], 'o-', label='Roller Force - (R1H2)')
        im12, = a1.plot([], [], 'o-', label='Roller Force - (R1H3)')
        im13, = a1.plot([], [], 'o-', label='Roller Force - (R1H4)')
        im14, = a2.plot([], [], 'o-', label='Roller Force')
        im15, = a2.plot([], [], 'o-', label='Roller Force')
        im16, = a2.plot([], [], 'o-', label='Roller Force')
        im17, = a2.plot([], [], 'o-', label='Roller Force')

        im18, = a1.plot([], [], 'o-', label='Roller Force - (R2H1)')
        im19, = a1.plot([], [], 'o-', label='Roller Force - (R2H2)')
        im20, = a1.plot([], [], 'o-', label='Roller Force - (R2H3)')
        im21, = a1.plot([], [], 'o-', label='Roller Force - (R2H4)')
        im22, = a2.plot([], [], 'o-', label='Roller Force')
        im23, = a2.plot([], [], 'o-', label='Roller Force')
        im24, = a2.plot([], [], 'o-', label='Roller Force')
        im25, = a2.plot([], [], 'o-', label='Roller Force')

        im26, = a1.plot([], [], 'o-', label='Roller Force - (R3H1)')
        im27, = a1.plot([], [], 'o-', label='Roller Force - (R3H2)')
        im28, = a1.plot([], [], 'o-', label='Roller Force - (R3H3)')
        im29, = a1.plot([], [], 'o-', label='Roller Force - (R3H4)')
        im30, = a2.plot([], [], 'o-', label='Roller Force')
        im31, = a2.plot([], [], 'o-', label='Roller Force')
        im32, = a2.plot([], [], 'o-', label='Roller Force')
        im33, = a2.plot([], [], 'o-', label='Roller Force')

        im34, = a1.plot([], [], 'o-', label='Roller Force - (R4H1)')
        im35, = a1.plot([], [], 'o-', label='Roller Force - (R4H2)')
        im36, = a1.plot([], [], 'o-', label='Roller Force - (R4H3)')
        im37, = a1.plot([], [], 'o-', label='Roller Force - (R4H4)')
        im38, = a2.plot([], [], 'o-', label='Roller Force')
        im39, = a2.plot([], [], 'o-', label='Roller Force')
        im40, = a2.plot([], [], 'o-', label='Roller Force')
        im41, = a2.plot([], [], 'o-', label='Roller Force')
        # --------------- Ramp Profile ---------------------------[ Important ]
        # im42, = a2.plot([], [], 'o-', label='Cumulated Ramp')
        # im43, = a2.plot([], [], 'o-', label='Nominal Ramp')

        # Statistical Feed -----------------------------------------[]
        a3.text(0.466, 0.945, 'Performance Feed - RF', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        a3.add_patch(rect1)
        a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)---------------------
        a3.text(0.145, 0.804, rflabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.658, '#Pp Value', fontsize=24, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.650, 0.820, 'Ring ' + rflabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        a3.text(0.145, 0.403, rfPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=22, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring ' + rfPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
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
        def synchronousRF(ttSize, ttgType, fetchT):
            fetch_no = str(fetchT)  # entry value in string sql syntax

            # Obtain Volatile Data from PLC Host Server ---------------------------[]
            if not inUseAlready:  # Load CommsPlc class once
                import CommsPlc as q
                q.DAQ_connect(1, 0)
            else:
                con_rf = conn.cursor()

            # Evaluate conditions for SQL Data Fetch ------------------------------[A]
            """
            Load watchdog function with synchronous function every seconds
            """
            # Initialise RT variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard                                 # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                if UsePLC_DBS:                              # Not Using PLC Data
                    import plcArrayRLmethodRF as srf         # DrLabs optimization method

                    inProgress = True                       # True for RetroPlay mode
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
                    # -----------------------------------------------------------------[]

                    # Allow selective runtime parameter selection on production critical process
                    procID = 'RF'
                    rfData = srf.paramDataRequest(procID, rfSize, rfgType, fetch_no)

                else:
                    import sqlArrayRLmethodRF as srf  # DrLabs optimization method

                    inProgress = True  # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve M.State from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    if keyboard.is_pressed("Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            print("\nVisualization in Paused Mode...")
                        else:
                            autoSpcPause = False
                            print("Visualization in Real-time Mode...")
                    else:
                        # Get list of relevant SQL Tables using conn() --------------------[]
                        rfData = srf.sqlexec(rfSize, rfgType, con_rf, T1, fetchT)

                    # ------ Inhibit iteration ----------------------------------------------------------[]
                    """
                    # Set condition for halting real-time plots in watchdog class ---------------------
                    """
                    # TODO --- values for inhibiting the SQL processing
                    if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                        con_rf.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

            return rfData

        # -------------------------------------[A]

        # ================== End of synchronous Method ==========================
        def asynchronousRF(db_freq):
            timei = time.time()         # start timing the entire loop

            # Bistream Data Pooling Method ---------------------#
            rfData = synchronousRF(rfSize, rfgType, db_freq)    # data loading functions
            # --------------------------------------------------#

            if UsePLC_DBS == 1:
                import VarPLCrf as rf

                viz_cycle = 10
                # Call synchronous data function ---------------[]
                columns = qrf.validCols(T1)                    # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(rfData, columns=columns)    # Include table data into python Dataframe
                RF = rf.loadProcesValues(df1)                  # Join data values under dataframe

            else:
                import VarSQLrf as rf                          # load SQL variables column names | rfVarSQL

                viz_cycle = 150
                g1 = qrf.validCols(T1)                         # Construct Data Column selSqlColumnsTFM.py
                df1 = pd.DataFrame(rfData, columns=g1)         # Import into python Dataframe
                RF = rf.loadProcesValues(df1)                  # Join data values under dataframe

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
            im10.set_ydata((RF[0]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 1
            im11.set_ydata((RF[1]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 2
            im12.set_ydata((RF[2]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 3
            im13.set_ydata((RF[3]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 1 ---------#
            mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(rfHL, rfSize, 'RF')
            # ---------------------------------------#
            im14.set_ydata((RF[4]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 1
            im15.set_ydata((RF[5]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 2
            im16.set_ydata((RF[6]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 3
            im17.set_ydata((RF[7]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 2 ---------#
            mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(rfHL, rfSize, 'RF')
            # ---------------------------------------#
            im18.set_ydata((RF[8]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 1
            im19.set_ydata((RF[9]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 2
            im20.set_ydata((RF[10]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 3
            im21.set_ydata((RF[11]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 3 ---------#
            mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(rfHL, rfSize, 'RF')
            # ---------------------------------------#
            im22.set_ydata((RF[12]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 1
            im23.set_ydata((RF[13]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 2
            im24.set_ydata((RF[14]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 3
            im25.set_ydata((RF[15]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 4 ---------#
            mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(rfHL, rfSize, 'RF')
            # ---------------------------------------#
            # S Plot Y-Axis data points for StdDev ----------------------------------------
            im26.set_ydata((RF[0]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im27.set_ydata((RF[1]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im28.set_ydata((RF[2]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im29.set_ydata((RF[3]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])

            im30.set_ydata((RF[4]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im31.set_ydata((RF[5]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im32.set_ydata((RF[6]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im33.set_ydata((RF[7]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])

            im34.set_ydata((RF[8]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im35.set_ydata((RF[9]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im36.set_ydata((RF[10]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im37.set_ydata((RF[11]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])

            im38.set_ydata((RF[12]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im39.set_ydata((RF[13]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im40.set_ydata((RF[14]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im41.set_ydata((RF[15]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])

            # Compute entire Process Capability -----------#
            if not rfHL:
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLb, ppT, pkT, xline, sline = tq.tAutoPerf(rfSize, mnA, mnB,
                                                                                                      mnC, mnD, sdA,
                                                                                                      sdB, sdC, sdD)
            else:
                xline, sline = rfMean, rfDev
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLba, ppT, pkT = tq.tManualPerf(mnA, mnB, mnC, mnD, sdA, sdB,
                                                                                           sdC, sdD, rfUSL, rfLSL,
                                                                                           rfUCL,
                                                                                           rfLCL)

            # # Declare Plots attributes --------------------------------------------------------[]
            # XBar Mean Plot
            a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
            a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 3 Sigma span (Purple)
            a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minRF, sBar_maxRF -------[]
            # Define Legend's Attributes  ----
            a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
            a2.axhspan(sLCLrf, sUCLrf, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 1 Sigma Span
            a2.axhspan(sUCLrf, sBar_maxRF, facecolor='#CCCCFF', edgecolor='#CCCCFF')  # 1 Sigma above the Mean
            a2.axhspan(sBar_minRF, sLCLrf, facecolor='#CCCCFF', edgecolor='#CCCCFF')

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
                a2.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a1.set_xlim(0, window_Xmax)
                a2.set_xlim(0, window_Xmax)

            # Set trip line for individual time-series plot -----------------------------------[R1]
            import triggerModule as sigma
            sigma.trigViolations(a1, UsePLC_DBS, 'RF', YScale_minRF, YScale_maxRF, xucT, xlcT, xusT, xlsT, mnT, sdT)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousRF, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)


# -------------------------------------------------------------------------------------------[Tap Temperature P5]
class tapeTempTabb(ttk.Frame):  # -- Defines the tabbed region for QA param - Tape Temperature --[]
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""

        # Load Quality Historical Values -----------[]
        ttSize, ttgType, ttSspace, ttHL, ttAL, ttFO, ttParam1, ttParam2, ttParam3, ttParam4, ttParam5 = prc.decryptpProcessLim(
            WON, 'TT')

        # Break down each element to useful list ---------------[Tape Temperature]
        if ttHL and ttParam1 and ttParam2 and ttParam3 and ttParam4 and ttParam5:  #
            ttPerf = '$Pp_{k' + str(ttSize) + '}$'      # Using estimated or historical Mean
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
            ttPerf = '$Cp_{k' + str(ttSize) + '}$'  # Using Automatic group Mean
            ttlabel = 'Cp'

        # ------------------------------------[End of Tape Temperature Abstraction]

        label = ttk.Label(self, text='[' + rType + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Define Axes ---------------------#
        f = Figure(figsize=(25, 8), dpi=100)
        f.subplots_adjust(left=0.029, bottom=0.05, right=0.983, top=0.967, wspace=0.18, hspace=0.174)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 6, (1, 3))                            # xbar plot
        a2 = f.add_subplot(2, 6, (7, 9))                            # s bar plot
        a3 = f.add_subplot(2, 6, (4, 12))                           # void mapping profile

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends

        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minTT, YScale_maxTT = ttLSL - 8.5, ttUSL + 8.5       # Tape Temperature
        sBar_minTT, sBar_maxTT = sLCLtt - 80, sUCLtt + 80           # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (int(ttSize) + 3)             # windows view = visible data points
        # ----------------------------------------------------------#
        YScale_minRM, YScale_maxRM = 0, pExLayer                    # Valid layer number
        window_XminRM, window_XmaxRM = 0, pLength                   # Get details from SCADA PIpe Recipe TODO[1]

        # Real-Time Parameter according to updated requirements ----# 07/Feb/2025
        T1 = WON + '_TT'        # Tape Temperature
        T2 = WON + '_RM'        # Ramp Profile Mapping
        # ----------------------------------------------------------#

        # Initialise runtime limits --------------------------------#
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")

        a1.set_title('Tape Temperature [XBar]', fontsize=12, fontweight='bold')
        a2.set_title('Tape Temperature [SDev]', fontsize=12, fontweight='bold')
        a3.set_title('Ramp Mapping Profile - [RMP]', fontsize=12, fontweight='bold')
        a3.set_facecolor("blue")        # set background color to blue
        zoom_factory(a3)                # Allow plot's image  zooming

        a3.set_ylabel("2D - Staked Layer Ramp Mapping")
        a3.set_xlabel("Sample Distance (mt)")

        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a3.grid(color="0.5", linestyle='-', linewidth=0.5)

        a1.legend(loc='upper right', title='Tape Temperature')
        a2.legend(loc='upper right', title='Sigma Plot')
        a3.legend(loc='upper right', title='Temp Ramp Profile')
        # ----------------------------------------------------------#
        a1.set_ylim([YScale_minTT, YScale_maxTT], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        a2.set_ylim([sBar_minTT, sBar_maxTT], auto=True)
        a2.set_xlim([window_Xmin, window_Xmax])
        # --------------------------------------------------------[]
        a3.set_ylim([YScale_minRM, YScale_maxRM], auto=True)
        a3.set_xlim([window_XminRM, window_XmaxRM])

        # --------------------------------------------------------[]
        # Define Plot area and axes -
        # ---------------------------------------------------------#
        im10, = a1.plot([], [], 'o-', label='Tape Temp - (R1H1)')
        im11, = a1.plot([], [], 'o-', label='Tape Temp - (R1H2)')
        im12, = a1.plot([], [], 'o-', label='Tape Temp - (R1H3)')
        im13, = a1.plot([], [], 'o-', label='Tape Temp - (R1H4)')
        im14, = a2.plot([], [], 'o-', label='Tape Temp')
        im15, = a2.plot([], [], 'o-', label='Tape Temp')
        im16, = a2.plot([], [], 'o-', label='Tape Temp')
        im17, = a2.plot([], [], 'o-', label='Tape Temp')

        im18, = a1.plot([], [], 'o-', label='Tape Temp - (R2H1)')
        im19, = a1.plot([], [], 'o-', label='Tape Temp - (R2H2)')
        im20, = a1.plot([], [], 'o-', label='Tape Temp - (R2H3)')
        im21, = a1.plot([], [], 'o-', label='Tape Temp - (R2H4)')
        im22, = a2.plot([], [], 'o-', label='Tape Temp')
        im23, = a2.plot([], [], 'o-', label='Tape Temp')
        im24, = a2.plot([], [], 'o-', label='Tape Temp')
        im25, = a2.plot([], [], 'o-', label='Tape Temp')

        im26, = a1.plot([], [], 'o-', label='Tape Temp - (R3H1)')
        im27, = a1.plot([], [], 'o-', label='Tape Temp - (R3H2)')
        im28, = a1.plot([], [], 'o-', label='Tape Temp - (R3H3)')
        im29, = a1.plot([], [], 'o-', label='Tape Temp - (R3H4)')
        im30, = a2.plot([], [], 'o-', label='Tape Temp')
        im31, = a2.plot([], [], 'o-', label='Tape Temp')
        im32, = a2.plot([], [], 'o-', label='Tape Temp')
        im33, = a2.plot([], [], 'o-', label='Tape Temp')

        im34, = a1.plot([], [], 'o-', label='Tape Temp - (R4H1)')
        im35, = a1.plot([], [], 'o-', label='Tape Temp - (R4H2)')
        im36, = a1.plot([], [], 'o-', label='Tape Temp - (R4H3)')
        im37, = a1.plot([], [], 'o-', label='Tape Temp - (R4H4)')
        im38, = a2.plot([], [], 'o-', label='Tape Temp')
        im39, = a2.plot([], [], 'o-', label='Tape Temp')
        im40, = a2.plot([], [], 'o-', label='Tape Temp')
        im41, = a2.plot([], [], 'o-', label='Tape Temp')
        # --------------- Temperature Ramp Profile -------------------[ Important ]
        im42 = a3.plot([], [], marker='|', color='w', linestyle='', label='Ring 1 Ramp')
        im43 = a3.plot([], [], marker='|', color='w', linestyle='', label='Ring 2 Ramp')
        im44 = a3.plot([], [], marker='|', color='w', linestyle='', label='Ring 3 Ramp')
        im45 = a3.plot([], [], marker='|', color='w', linestyle='', label='Ring 4 Ramp')

        # ---------------- EXECUTE SYNCHRONOUS METHOD -----------------------------#

        def synchronousTT(smp_Sz, smp_St, fetchT):
            fetch_no = str(fetchT)                        # entry value in string sql syntax

            # Obtain Volatile Data from PLC Host Server ---------------------------[]
            if not inUseAlready:                         # Load Comm Plc class once
                import CommsSql as q
                con_tt = q.DAQ_connect(1, 0) # Connect PLC for real-time data
            else:
                con_tt = conn.cursor()

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
                # Using PLC Data ----------------#
                if UsePLC_DBS:
                    import plcArrayRLmethodTT as pdA

                    inProgress = True                               # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve M.State from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    if keyboard.is_pressed(
                            "Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:  # Terminate file-fetch
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            print("\nVisualization in Paused Mode...")
                    else:
                        autoSpcPause = False
                        print("Visualization in Real-time Mode...")

                        # Get list of relevant PLC Tables using conn() --------------------[]
                        ttData = pdA.paramDataRequest(T1, smp_Sz, smp_St, fetch_no)

                else:
                    import sqlArrayRLmethodTT as ptt

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
                        print("Visualization in Play Mode...")

                    else:
                        ttData = ptt.sqlexec(smp_Sz, smp_St, con_tt, T1, fetchT)
                        print("Visualization in Play Mode...")
                    print('\nUpdating....')

                    # ------ Inhibit iteration ----------------------------------------------------------[]
                    """
                    # Set condition for halting real-time plots in watchdog class -----------------------[]
                    """
                    # TODO --- values for inhibiting the SQL processing
                    if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                        con_tt.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

            return ttData

        # -------------------------------------[Strictly from SQL Repo Void Profile]
        def synchronousRM(smp_Sz, stp_Sz, fetchT):
            fetch_no = str(fetchT)  # entry value in string sql syntax

            # Obtain Data from SQL Repo ---------------------------[]
            con_rm = conn.cursor()  # Connect SQL for Near real-time data

            """
            Load watchdog function with synchronous function every seconds
            """

            # Initialise variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard  # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                # Latch on SQL Query only a
                import sqlArrayRLmethodRM as srm                # DrLabs optimization method

                inProgress = False  # True for RetroPlay mode
                print('\nAsynchronous controller activated...')

                if not sysRun:
                    sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve MSC from Watchdog
                print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                # Get list of relevant SQL Tables using conn() --------------------[]
                if keyboard.is_pressed("Ctrl"):                 # Terminate file-fetch
                    print('\nProduction is pausing...')
                    if not autoSpcPause:
                        autoSpcRun = not autoSpcRun
                        autoSpcPause = True
                        print("\nVisualization in Paused Mode...")
                    else:
                        autoSpcPause = False
                        con_rm.close()
                    print("Visualization in Near Real-time Mode...")
                    time.sleep(60)
                    rm_profile = 0
                    continue

                else:
                    rm_profile = srm.sqlexec(smp_Sz, stp_Sz, con_rm, T2, fetch_no)  # perform DB connections
                    print('\nUpdating....')

                # ------ Inhibit iteration ----------------------------------------------------------[]
                """
                # Set condition for halting real-time plots in watchdog class ---------------------
                """
                # TODO --- values for inhibiting the SQL processing
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    con_rm.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

            return rm_profile

        # ================== End of synchronous Method ==========================--------------------[]
        def asynchronousTT(db_freq):
            timei = time.time()         # start timing the entire loop

            # Bi-stream Data Pooling Method --------------------#
            ttData = synchronousTT(ttSize, ttgType, db_freq)    # data loading functions
            rmData = synchronousRM(smp_Sz, stp_Sz, db_freq)     # Accumulated Gap Mean Profile
            # --------------------------------------------------#
            import VarSQLrm as rm                               # load SQL variables column names | rfVarSQL

            # viz_cycle = 150
            g1 = qrm.validCols('RM')                            # Construct Data Column selSqlColumnsTFM.py
            df0 = pd.DataFrame(rmData, columns=g1)              # Import into python Dataframe
            RM = rm.loadProcesValues(df0)                       # Join data values under dataframe

            if UsePLC_DBS == 1:
                import VarPLCtt as tt
                viz_cycle = 10

                # Call synchronous data PLC function ----------[A]
                columns = qtt.validCols(T1)                     # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(ttData, columns=columns)     # Include table data into python Dataframe
                TT = tt.loadProcesValues(df1)                   # Join data values under dataframe
            else:
                import VarSQLtt as tt

                viz_cycle = 150
                columns = qtt.validCols(T1)                   # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(ttData, columns=columns)    # Include table data into python Dataframe
                TT = tt.loadProcesValues(df1)                  # Join data values under dataframe

            print('\nSQL Content', df1.head(10))
            print("Memory Usage:", df1.info(verbose=False))    # Check memory utilization

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
            im42.set_xdata(np.arange(db_freq))  # TODO - cross check with freq counter
            im43.set_xdata(np.arange(db_freq))
            im44.set_xdata(np.arange(db_freq))
            im45.set_xdata(np.arange(db_freq))

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
            # ---------------------------------------------------------------------------------------[RAMP]
            # TODO ----
            # im42.set_ydata((RM[1]).rolling(window=ttSize, min_periods=1).mean()[0:db_freq])  # tStamp
            im42.set_ydata((RM[1])[0:db_freq])              # Ring 1
            im43.set_ydata((RM[2])[0:db_freq])              # Ring 2
            im44.set_ydata((RM[3])[0:db_freq])              # Ring 3
            im45.set_ydata((RM[4])[0:db_freq])              # Ring 4

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

            # Setting up the parameters for windows moving Axes on Tape Temp only ---------------[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
                a2.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a1.set_xlim(0, window_Xmax)
                a2.set_xlim(0, window_Xmax)

            # Set trip line for individual time-series plot -----------------------------------[R1]
            import triggerModule as sigma
            sigma.trigViolations(a1, UsePLC_DBS, 'TT', YScale_minTT, YScale_maxTT, xucT, xlcT, xusT, xlsT, mnT, sdT)

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
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

# -----------------------------------------------------------------------------------[Substrate Temperature P6]

class substTempTabb(ttk.Frame):
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        # Load Quality Historical Values -----------[]
        if pRecipe == 'DNV':
            import qParamsHL_DNV as qp
        elif pRecipe == 'MGM':
            import qParamsHL_MGM as qp
        else:
            pass

        stSize, stgType, stSspace, stHL, stAL, stFO, stParam1, stParam2, stParam3, stParam4, stParam5 = qp.decryptpProcessLim(
            WON, 'ST')

        # Break down each element to useful list -----------[Substrate Temperature]
        if stHL and stParam1 and stParam2 and stParam3 and stParam4 and stParam5:
            stPerf = '$Pp_{k' + str(stSize) + '}$'  # Using estimated or historical Mean
            stlabel = 'Pp'
            # -------------------------------
            One = stParam1.split(',')                       # split into list elements
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
            stPerf = '$Cp_{k' + str(stSize) + '}$'           # Using Automatic group Mean
            stlabel = 'Cp'

        label = ttk.Label(self, text='[' + rType + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Define Axes ---------------------#
        f = Figure(figsize=(25, 8), dpi=100)
        f.subplots_adjust(left=0.029, bottom=0.05, right=0.99, top=0.955, wspace=0.117, hspace=0.157)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 4, (1, 3))
        a2 = f.add_subplot(2, 4, (5, 7))
        a3 = f.add_subplot(2, 4, (4, 8))

        # Declare Plots attributes --------------------------------[]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minST, YScale_maxST = stLSL - 8.5, stUSL + 8.5
        sBar_minST, sBar_maxST = sLCLst - 80, sUCLst + 80           # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (int(stSize) + 3)             # windows view = visible data points

        # Load SQL Query Table -------------------------------------#
        T1 = WON + '_ST'  # Identify Table
        # ----------------------------------------------------------#

        # Initialise runtime limits
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")

        a1.set_title('Substrate Temperature [XBar]', fontsize=12, fontweight='bold')
        a2.set_title('Substrate Temperature [StDev]', fontsize=12, fontweight='bold')
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)

        a1.legend(loc='upper right', title='Substrate Temp')
        a2.legend(loc='upper right', title='Sigma curve')
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
        im10, = a1.plot([], [], 'o-', label='Substrate Temp - (R1H1)')
        im11, = a1.plot([], [], 'o-', label='Substrate Temp - (R1H2)')
        im12, = a1.plot([], [], 'o-', label='Substrate Temp - (R1H3)')
        im13, = a1.plot([], [], 'o-', label='Substrate Temp - (R1H4)')
        im14, = a2.plot([], [], 'o-', label='Substrate Temp')
        im15, = a2.plot([], [], 'o-', label='Substrate Temp')
        im16, = a2.plot([], [], 'o-', label='Substrate Temp')
        im17, = a2.plot([], [], 'o-', label='Substrate Temp')

        im18, = a1.plot([], [], 'o-', label='Substrate Temp - (R2H1)')
        im19, = a1.plot([], [], 'o-', label='Substrate Temp - (R2H2)')
        im20, = a1.plot([], [], 'o-', label='Substrate Temp - (R2H3)')
        im21, = a1.plot([], [], 'o-', label='Substrate Temp - (R2H4)')
        im22, = a2.plot([], [], 'o-', label='Substrate Temp')
        im23, = a2.plot([], [], 'o-', label='Substrate Temp')
        im24, = a2.plot([], [], 'o-', label='Substrate Temp')
        im25, = a2.plot([], [], 'o-', label='Substrate Temp')

        im26, = a1.plot([], [], 'o-', label='Substrate Temp - (R3H1)')
        im27, = a1.plot([], [], 'o-', label='Substrate Temp - (R3H2)')
        im28, = a1.plot([], [], 'o-', label='Substrate Temp - (R3H3)')
        im29, = a1.plot([], [], 'o-', label='Substrate Temp - (R3H4)')
        im30, = a2.plot([], [], 'o-', label='Substrate Temp')
        im31, = a2.plot([], [], 'o-', label='Substrate Temp')
        im32, = a2.plot([], [], 'o-', label='Substrate Temp')
        im33, = a2.plot([], [], 'o-', label='Substrate Temp')

        im34, = a1.plot([], [], 'o-', label='Substrate Temp - (R4H1)')
        im35, = a1.plot([], [], 'o-', label='Substrate Temp - (R4H2)')
        im36, = a1.plot([], [], 'o-', label='Substrate Temp - (R4H3)')
        im37, = a1.plot([], [], 'o-', label='Substrate Temp - (R4H4)')
        im38, = a2.plot([], [], 'o-', label='Substrate Temp')
        im39, = a2.plot([], [], 'o-', label='Substrate Temp')
        im40, = a2.plot([], [], 'o-', label='Substrate Temp')
        im41, = a2.plot([], [], 'o-', label='Substrate Temp')

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
        def synchronousST(smp_Sz, smp_St, fetchT):
            fetch_no = str(fetchT)                          # entry value in string sql syntax

            # Obtain Volatile Data from PLC Host Server ---------------------------[]
            if not inUseAlready:                            # Load Coms Plc class once
                import CommsSql as q
                con_st = q.DAQ_connect(1, 0)
            else:
                con_st = conn.cursor()

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
                if UsePLC_DBS:                                      # Using PLC Data
                    import plcArrayRLmethodST as pdB                # DrLabs optimization method

                    inProgress = True                                   # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()     # Retrieve M.State from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    # Either of the 2 combo variables are assigned to trigger routine pause
                    if keyboard.is_pressed(
                            "Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:  # Terminate file-fetch
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            print("\nVisualization in Paused Mode...")
                    else:
                        autoSpcPause = False
                        print("Visualization in Real-time Mode...")
                        # -----------------------------------------------------------------[]
                        stData = pdB.paramDataRequest('ST', stSize, stgType, fetch_no)
                else:
                    import sqlArrayRLmethodST as pst

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
                        print("Visualization in Play Mode...")

                    else:
                        stData = pst.sqlexec(smp_Sz, smp_St, con_st, T1, fetchT)
                        print("Visualization in Play Mode...")
                    print('\nUpdating....')

                    # ------ Inhibit iteration ----------------------------------------------------------[]
                    """
                    # Set condition for halting real-time plots in watchdog class -----------------------[]
                    """
                    # TODO --- values for inhibiting the SQL processing
                    if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                        con_st.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

            return stData

        # ================== End of synchronous Method ==========================
        def asynchronousST(db_freq):
            timei = time.time()  # start timing the entire loop

            # Call data loader Method---------------------------#
            stData = synchronousST(smp_Sz, stp_Sz, db_freq)     # data loading functions
            # --------------------------------------------------#
            if UsePLC_DBS == 1:
                import VarPLCst as st

                viz_cycle = 10
                # Call synchronous data function ---------------[]
                g1 = qst.validCols(T1)                          # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(stData, columns=g1)          # Include table data into python Dataframe
                ST = st.loadProcesValues(df1)                   # Join data values under dataframe
            else:
                import VarSQLst as st                           # load SQL variables column names | rfVarSQL

                viz_cycle = 150
                g1 = qst.validCols(T1)                          # Construct Data Column selSqlColumnsTFM.py
                df1 = pd.DataFrame(stData, columns=g1)          # Import into python Dataframe
                ST = st.loadProcesValues(df1)                   # Join data values under dataframe

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


# ---------------------------------------------------------------------------------------------[Tape Gap P7]
class tapeGapPolTabb(ttk.Frame):

    """ Application to convert feet to meters or vice versa. """

    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        # define region ------
        self.display_rtStats()

    def display_rtStats(self):
        global a2, a4, gap_vol       # allow axial inheritance on new class method

        """Create the widgets for the GUI"""
        if pRecipe == 'DNV':
            import qParamsHL_DNV as qp
        elif pRecipe == 'MGM':
            import qParamsHL_MGM as qp
        else:
            pass

        # Load metrics from config -----------------------------------[Tape Gap]
        tgSize, tggType, tgSspace, tgHL, tgAL, tgtFO, tgParam1, dud2, dud3, dud4, dud5 = qp.decryptpProcessLim(WON, 'TG')

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
            tgPerf = '$Cp_{k' + str(tgSize) + '}$'                   # Using Automatic group Mean
            tglabel = 'Cp'

        # -------------------------------------------[End of Tape Gap]

        label = ttk.Label(self, text='[' + rType + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)     # 10 | 5

        # Define Axes ---------------------#
        f = Figure(figsize=(25, 8), dpi=100)                        # 25,  = 12 | 8
        f.subplots_adjust(left=0.026, bottom=0.045, right=0.986, top=0.967, wspace=0.217, hspace=0.162)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 6, (1, 3))                            # xbar plot
        a3 = f.add_subplot(2, 6, (7, 9))                            # s bar plot
        a4 = f.add_subplot(2, 6, (4, 12))                           # void mapping profile

        # ----------------------------------------------------------[H]
        plt.rcParams.update({'font.size': 9})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minTG, YScale_maxTG = tgLSL - 8.5, tgUSL + 8.5       # Roller Force
        sBar_minTG, sBar_maxTG = sLCLtg - 80, sUCLtg + 80           # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (int(tgSize) + 3)             # windows view = visible data points
        # ----------------------------------------------------------#
        YScale_minVM, YScale_maxVM = 0, pExLayer                    # Valid Void Mapping
        window_XminVM, window_XmaxVM = 0, pLength                   # Get details from SCADA PIpe Recipe TODO[1]

        # Real-Time Parameter according to updated requirements ----# 07/Feb/2025
        T1 = WON + '_TG'        # Tape Placement
        T2 = WON + '_VM'        # Void Mapping
        # ----------------------------------------------------------#

        # Initialise runtime limits --------------------------------#
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a3.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")

        a1.set_title('Tape Gap Polarisation [XBar]', fontsize=12, fontweight='bold')
        a3.set_title('Tape Gap Polarisation [SDev]', fontsize=12, fontweight='bold')
        a4.set_title('Tape Gap Mapping Profile', fontsize=12, fontweight='bold')

        a4.set_ylabel("2D - Staked Layer Void Mapping")
        a4.set_xlabel("Sample Distance (mt)")
        a4.set_facecolor("green")                           # set face color for Ramp mapping volume
        zoom_factory(a4)                                    # allow zooming on image plot

        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a3.grid(color="0.5", linestyle='-', linewidth=0.5)
        a4.grid(color="0.5", linestyle='-', linewidth=0.5)

        a1.legend(loc='upper right', title='Tape Gap Polarisation')
        a3.legend(loc='upper right', title='Sigma Plots')
        # a4.legend(loc='upper right', title='Void Map Profile')
        # ------------------------------------------------------[for Ramp Plot]
        colors = np.random.randint(50, 101, size=(367))     # TODO -- obtain length of element dynamically
        rlabel = ['< 0', '0 - 2', '2 - 4', '4 - 6', '6 - 8', '8 - 9', '9 - 10', 'above']

        # Initialise runtime limits -------------------------------#
        a1.set_ylim([YScale_minTG, YScale_maxTG], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        a3.set_ylim([sBar_minTG, sBar_maxTG], auto=True)
        a3.set_xlim([window_Xmin, window_Xmax])
        # --------------------------------------------------------[]
        a4.set_ylim([YScale_minVM, YScale_maxVM], auto=True)
        a4.set_xlim([window_XminVM, window_XmaxVM])

        # ----------------------------------------------------------[]
        # Define Plot area and axes -
        # ----------------------------------------------------------[8 into 4]
        im10, = a1.plot([], [], 'o-', label='Tape Gap Pol - (A1)')
        im11, = a1.plot([], [], 'o-', label='Tape Gap Pol - (B1)')
        im12, = a1.plot([], [], 'o-', label='Tape Gap Pol - (A2)')
        im13, = a1.plot([], [], 'o-', label='Tape Gap Pol - (B2)')
        im14, = a1.plot([], [], 'o-', label='Tape Gap Pol - (A3)')
        im15, = a1.plot([], [], 'o-', label='Tape Gap Pol - (B3)')
        im16, = a1.plot([], [], 'o-', label='Tape Gap Pol - (A4)')
        im17, = a1.plot([], [], 'o-', label='Tape Gap Pol - (B4)')
        # ------------ S Bar Plot ------------------------------
        im18, = a3.plot([], [], 'o-', label='Tape Gap Pol')
        im19, = a3.plot([], [], 'o-', label='Tape Gap Pol')
        im20, = a3.plot([], [], 'o-', label='Tape Gap Pol')
        im21, = a3.plot([], [], 'o-', label='Tape Gap Pol')
        im22, = a3.plot([], [], 'o-', label='Tape Gap Pol')
        im23, = a3.plot([], [], 'o-', label='Tape Gap Pol')
        im24, = a3.plot([], [], 'o-', label='Tape Gap Pol')
        im25, = a3.plot([], [], 'o-', label='Tape Gap Pol')
        # ------------------------------------------------------
        im26, = a4.plot([], [], 'o-', label='Tape Gap Pol')
        # im26 = a4.plot([], [], s=gap_vol, marker='s', c=colors, cmap='rainbow')
        # a4.legend(handles=im26.legend_elements()[0], labels=rlabel, title='Void Map (%)')
        # -------------------------------------------------------------------------#
        # loadSqlCumProfile(ttk.Frame)
        # loadSqlVoidMapping()
        # ---------------- EXECUTE SYNCHRONOUS TG METHOD --------------------------#

        def synchronousTG(smp_Sz, smp_St, fetchT):
            fetch_no = str(fetchT)                                                 # entry value in string sql syntax

            # Obtain Volatile Data from PLC Host Server ---------------------------[]
            if not inUseAlready:                                                   # Load CommsPlc class once
                import CommsSql as q
                con_tg = q.DAQ_connect(1, 0)
            else:
                con_tg = conn.cursor()

            # Evaluate conditions for SQL Data Fetch ------------------------------[A]
            """
            Load watchdog function with synchronous function every seconds
            """
            # Initialise RT variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard                                                        # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                # print('Indefinite looping...')
                if UsePLC_DBS:                                                      # Not Using PLC Data
                    import plcArrayRLmethodTG as pdC                                # DrLabs optimization method

                    inProgress = True                                               # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve M.State from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    if keyboard.is_pressed(
                            "Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:  # Terminate file-fetch
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            print("\nVisualization in Paused Mode...")
                    else:
                        autoSpcPause = False
                        print("Visualization in Real-time Mode...")
                        # Get list of relevant SQL Tables using conn() --------------------[]
                        # tgData = pdC.sqlexec(smp_Sz, smp_St, con_tg, T1, fetchT)  # get details from PLC array
                        tgData = q.paramDataRequest('TG', smp_Sz, smp_St, fetch_no)

                else:
                    import sqlArrayRLmethodTG as pdC

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
                        print("Visualization in Play Mode...")
                    else:
                        tgData = pdC.sqlexec(smp_Sz, smp_St, con_tg, T1, fetchT)
                        print("Visualization in Play Mode...")
                    print('\nUpdating....')

                    # ------ Inhibit iteration ----------------------------------------------------------[]
                    """
                    # Set condition for halting real-time plots in watchdog class -----------------------[]
                    """
                    # TODO --- values for inhibiting the SQL processing
                    if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                        con_tg.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

            return tgData

        # -------------------------------------[Strictly from SQL Repo Void Profile]
        def synchronousMP(smp_Sz, smp_St, fetchT):
            fetch_no = str(fetchT)                                                 # entry value in string sql syntax

            # Obtain Data from SQL Repo ---------------------------[]
            con_vm = conn.cursor()      # Void mapping

            """
            Load watchdog function with synchronous function every seconds
            """
            # Initialise variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard                                                        # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                # Latch on SQL Query only a
                import sqlArrayRLmethodVM as svm                                    # DrLabs optimization method

                inProgress = False                                                  # True for RetroPlay mode
                print('\nAsynchronous controller activated...')
                if not sysRun:
                    sysRun, msctcp, msc_rt = wd.autoPausePlay()                     # Retrieve MSC from Watchdog

                # Get list of relevant SQL Tables using conn() --------------------[]
                if keyboard.is_pressed("Ctrl"):                                    # Terminate file-fetch
                    print('\nProduction is pausing...')
                    if not autoSpcPause:
                        autoSpcRun = not autoSpcRun
                        autoSpcPause = True
                        # play(error)                                               # Pause mode with audible Alert
                        print("\nVisualization in Paused Mode...")
                    else:
                        autoSpcPause = False
                        con_vm.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    vm_profile = 0
                    continue

                else:
                    vm_profile = svm.sqlexec(smp_Sz, stp_Sz, con_vm, T2, fetchT)      # perform DB connections
                    print('\nUpdating....')

                # ------ Inhibit iteration ----------------------------------------------------------[]
                """
                # Set condition for halting real-time plots in watchdog class ---------------------
                """
                # TODO --- values for inhibiting the SQL processing
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    con_vm.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

            return vm_profile

        # ================== End of synchronous Method ==========================

        def asynchronousTG(db_freq):
            global gap_vol
            timei = time.time()                                   # start timing the entire loop

            # Bi-stream Data Pooling Method ----------------------#
            tgData = synchronousTG(smp_Sz, stp_Sz, db_freq)       # PLC synchronous Data loading method1
            vmData = synchronousMP(smp_Sz, stp_Sz, db_freq)       # Dr Labs Method for Void Mapping Profile
            # ----------------------------------------------------#

            if UsePLC_DBS == 1:
                import VarPLCtg as tg

                viz_cycle = 10
                columns = qtg.validCols('TG')                   # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(tgData, columns=columns)     # Include table data into python Dataframe
                TG = tg.loadProcesValues(df1)                   # Join data values under dataframe

            else:
                import VarSQLtg as tg                           # load SQL variables column names | rfVarSQL

                viz_cycle = 150
                g1 = qtg.validCols('TG')                        # Construct Data Column selSqlColumnsTFM.py
                df1 = pd.DataFrame(tgData, columns=g1)          # Import into python Dataframe
                TG = tg.loadProcesValues(df1)                   # Join data values under dataframe

            # Compulsory VoidMap function call -- SQL loader -[B]
            import VarSQLvm as vm                              # load SQL variables column names | rfVarSQL

            viz_cycle = 150
            g1 = qvm.validCols('VM')                            # Construct Data Column selSqlColumnsTFM.py
            df1 = pd.DataFrame(vmData, columns=g1)              # Import into python Dataframe
            VM = vm.loadProcesValues(df1)                       # Join data values under dataframe

            print('\nDataFrame Content', df1.head(10))          # Preview Data frame head
            print("Memory Usage:", df1.info(verbose=False))     # Check memory utilization

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
            # -------------------------------- Profile Axes
            # im26.set_xdata(np.arange(db_freq))
            a4.set_xdata(np.arange(db_freq))

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
            # ---- Profile rolling Data Plot -------------
            pScount = VM[0]
            pCenter = VM[1]
            pAvgGap = VM[2]
            pMaxGap = VM[3]
            vLayerN = VM[4]
            sLength = VM[5]

            gap_vol = (pAvgGap / sLength) * 100  # Percentage Void

            # im26.set_ydata((vLayerN),(gap_vol) [0:db_freq])  # ------------------------------ Profile A
            a4.set_ydata((vLayerN),(gap_vol) [0:db_freq])

            # # Declare Plots attributes ------------------------------------------------------------[]
            # XBar Mean Plot
            a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
            a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')            # 3 Sigma span (Purple)
            a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')            # grey area
            a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minTG, sBar_maxTG -------[]
            # Define Legend's Attributes  ----
            a3.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
            a3.axhspan(dLCLd, dUCLd, facecolor='#F9C0FD', edgecolor='#F9C0FD')          # 1 Sigma Span
            a3.axhspan(dUCLd, sBar_maxTG, facecolor='#CCCCFF', edgecolor='#CCCCFF')     # 1 Sigma above the Mean
            a3.axhspan(sBar_minTG, dLCLd, facecolor='#CCCCFF', edgecolor='#CCCCFF')

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
                a3.set_xlim(db_freq - window_Xmax, db_freq)
                # a4.set_xlim(db_freq - window_Xmax, db_freq)   # Non moving axis on profile B
            else:
                a1.set_xlim(0, window_Xmax)
                a3.set_xlim(0, window_Xmax)

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
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

class tapePlacementTabb(ttk.Frame):     # -- Defines the tabbed region for QA param - Substrate Temperature --[]
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        # --------------------------------------------------------------------[]
        tpSize, tpgType, tpSspace, tpHL, tpAL, tptFO, tpParam1, dud2, dud3, dud4, dud5 = mq.decryptpProcessLim(WON, 'TG')

        # Break down each element to useful list ----------------[Winding Speed]

        if tpHL and tpParam1:
            tgPerf = '$Pp_{k' + str(tpSize) + '}$'  # Estimated or historical Mean
            tglabel = 'Pp'
            # -------------------------------
            tgOne = tpParam1.split(',')  # split into list elements
            dTapetp = tpOne[1].strip("' ")  # defined Tape Width
            dLayer = tpOne[10].strip("' ")  # Defined Tape Layer

            # Load historical limits for the process----------------#
            # if cpTapeW == dTapetg and cpLayerNo == range(1, 100):   # '*.*',  | *.*
            tpUCL = float(tpOne[2].strip("' "))  # Strip out the element of the list
            tpLCL = float(tpOne[3].strip("' "))
            tpMean = float(tpOne[4].strip("' "))
            tpDev = float(tpOne[5].strip("' "))
            # --------------------------------
            sUCLtp = float(tpOne[6].strip("' "))
            sLCLtp = float(tpOne[7].strip("' "))
            # --------------------------------
            tpUSL = (tpUCL - tpMean) / 3 * 6
            tpLSL = (tpMean - tpLCL) / 3 * 6
            # --------------------------------
        else:  # Computes Shewhart constants (Automatic Limits)
            tpUCL = 0
            tpLCL = 0
            tpMean = 0
            tpDev = 0
            sUCLtp = 0
            sLCLtp = 0
            tpUSL = 0
            tpLSL = 0
            tpPerf = '$Cp_{k' + str(tpSize) + '}$'  # Using Automatic group Mean
            tplabel = 'Cp'

        # ------------------------------------[End of Winding Speed Abstraction]

        label = ttk.Label(self, text='[' + rType + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Set subplot embedded properties ----------------------------------[]
        f = Figure(figsize=(25, 8), dpi=100)
        f.subplots_adjust(left=0.029, bottom=0.05, right=0.99, top=0.955, wspace=0.117, hspace=0.157)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 4, (1, 3))        # xbar plot
        a2 = f.add_subplot(2, 4, (5, 7))        # s bar plot
        a3 = f.add_subplot(2, 4, (4, 8))        # CPk/PPk Feed

        # Declare Plots attributes ---------------------------------[]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minTP, YScale_maxTP = tpLSL - 8.5, tpUSL + 8.5       # Roller Force
        sBar_minTP, sBar_maxTP = sLCLtp - 80, sUCLtp + 80           # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (int(tpSize) + 3)             # windows view = visible data points

        # ----------------------------------------------------------#
        # Real-Time Parameter according to updated requirements ----# 07/Feb/2025
        T1 = WON + '_TP'  # Tape Placement
        # ----------------------------------------------------------#

        # Initialise runtime limits
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        a1.set_title('Tape Placement [XBar]', fontsize=12, fontweight='bold')
        a2.set_title('Tape Placement [StDev]', fontsize=12, fontweight='bold')

        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a1.legend(loc='upper right', title='Tape Placement')
        a2.legend(loc='upper right', title='Sigma curve')

        # Initialise runtime limits -------------------------------#
        a1.set_ylim([YScale_minTP, YScale_maxTP], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        a3.set_ylim([sBar_minTP, sBar_maxTP], auto=True)
        a3.set_xlim([window_Xmin, window_Xmax])

        # ----------------------------------------------------------[]
        a3.cla()
        a3.get_yaxis().set_visible(False)
        a3.get_xaxis().set_visible(False)

        # ----------------------------------------------------------[]
        # Define Plot area and axes -
        # ----------------------------------------------------------#
        im10, = a1.plot([], [], 'o-', label='Tape Placement - (A1)')
        im11, = a1.plot([], [], 'o-', label='Tape Placement - (B1)')
        im12, = a1.plot([], [], 'o-', label='Tape Placement - (A2)')
        im13, = a1.plot([], [], 'o-', label='Tape Placement - (B2)')
        im14, = a1.plot([], [], 'o-', label='Tape Placement - (A3)')
        im15, = a1.plot([], [], 'o-', label='Tape Placement - (B3)')
        im16, = a1.plot([], [], 'o-', label='Tape Placement - (A4)')
        im17, = a1.plot([], [], 'o-', label='Tape Placement - (B4)')
        # ------------ S Bar Plot ------------------------------
        im18, = a2.plot([], [], 'o-', label='Tape Placement')
        im19, = a2.plot([], [], 'o-', label='Tape Placement')
        im20, = a2.plot([], [], 'o-', label='Tape Placement')
        im21, = a2.plot([], [], 'o-', label='Tape Placement')
        im22, = a2.plot([], [], 'o-', label='Tape Placement')
        im23, = a2.plot([], [], 'o-', label='Tape Placement')
        im24, = a2.plot([], [], 'o-', label='Tape Placement')
        im25, = a2.plot([], [], 'o-', label='Tape Placement')

        # Statistical Feed -----------------------------------------[]
        a3.text(0.466, 0.945, 'Performance Feed - WP', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        a3.add_patch(rect1)
        a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)---------------------
        a3.text(0.145, 0.804, tplabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.658, '#Pp Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.650, 0.820, 'Ring ' + tplabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        a3.text(0.145, 0.403, tpPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring ' + tpPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
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
        def synchronousTP(tpSize, tpgType, fetchT):
            fetch_no = str(fetchT)  # entry value in string sql syntax

            # Obtain Volatile Data from PLC Host Server ---------------------------[]
            if not inUseAlready:  # Load CommsPlc class once
                import CommsSql as q
                q.DAQ_connect(1, 0)
            else:
                con_tp = conn.cursor()
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
                if UsePLC_DBS:                                          # Not Using PLC Data
                    import plcArrayRLmethodTP as stp                    # DrLabs optimization method

                    inProgress = True                                   # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve M.State from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    if keyboard.is_pressed(
                            "Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:  # Terminate file-fetch
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            print("\nVisualization in Paused Mode...")
                    else:
                        autoSpcPause = False
                        print("Visualization in Real-time Mode...")
                        # Get list of relevant SQL Tables using conn() --------------------[]
                        # tgData = pdC.sqlexec(smp_Sz, smp_St, con_tg, T1, fetchT)  # get details from PLC array
                        tpData = stp.paramDataRequest('TP', tpSize, tpgType, fetch_no)

                else:
                    import sqlArrayRLmethodTP as stp

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
                        print("Visualization in Play Mode...")
                    else:
                        tpData = stp.sqlexec(tpSize, tpgType, con_tp, T1, fetchT)
                        print("Visualization in Play Mode...")
                    print('\nUpdating....')

                    # ------ Inhibit iteration ----------------------------------------------------------[]
                    """
                    # Set condition for halting real-time plots in watchdog class -----------------------[]
                    """
                    # TODO --- values for inhibiting the SQL processing
                    if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                        con_tp.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

            return tpData

        # ================== End of synchronous Method ==========================
        def asynchronousTP(db_freq):
            timei = time.time()                                 # start timing the entire loop

            # Call data loader Method---------------------------#
            tpData = synchronousTP(tpSize, tpgType, db_freq)    # data loading functions
            # --------------------------------------------------#

            if UsePLC_DBS == 1:
                import VarPLCtp as tp

                viz_cycle = 10
                # Call synchronous data function ---------------[]
                columns = qtp.validCols(T1)                    # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(tpData, columns=columns)    # Include table data into python Dataframe
                TP = tp.loadProcesValues(df1)                  # Join data values under dataframe

            else:
                import VarSQLtp as tp                          # load SQL variables column names | rfVarSQL

                viz_cycle = 150
                g1 = qtp.validCols(T1)                         # Construct Data Column selSqlColumnsTFM.py
                df1 = pd.DataFrame(tpData, columns=g1)         # Import into python Dataframe
                TP = tp.loadProcesValues(df1)                  # Join data values under dataframe

            print('\nSQL Content', df1.head(10))
            print("Memory Usage:", df1.info(verbose=False))    # Check memory utilization

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

            # X Plot Y-Axis data points for XBar -------------------------------------------[# Channels]
            im10.set_ydata((TG[0]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # Segment 1
            im11.set_ydata((TG[1]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # Segment 2
            im12.set_ydata((TG[2]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # Segment 3
            im13.set_ydata((TG[3]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # Segment 4
            # ------ Evaluate Pp for Segments ---------#
            mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(tpHL, tpSize, 'TG')
            # ---------------------------------------#
            im14.set_ydata((TG[4]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # Segment 1
            im15.set_ydata((TG[5]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # Segment 2
            im16.set_ydata((TG[6]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # Segment 3
            im17.set_ydata((TG[7]).rolling(window=tpSize, min_periods=1).mean()[0:db_freq])  # Segment 4
            # ------ Evaluate Pp for Ring 2 ---------#
            mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(tpHL, tpSize, 'TG')

            # S Plot Y-Axis data points for StdDev ----------------------------------------[# S Bar Plot]
            im18.set_ydata((TG[0]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
            im19.set_ydata((TG[1]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
            im20.set_ydata((TG[2]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
            im21.set_ydata((TG[3]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])

            im22.set_ydata((TG[4]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
            im23.set_ydata((TG[5]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
            im24.set_ydata((TG[6]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])
            im25.set_ydata((TG[7]).rolling(window=tpSize, min_periods=1).std()[0:db_freq])


            # Compute entire Process Capability -----------#
            if not tpHL:
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLd, dLCLd, ppT, pkT, xline, sline = tq.tAutoPerf(tpSize, mnA,
                                                                                                      mnB,
                                                                                                      0, 0, sdA,
                                                                                                      sdB, 0, 0)
            else:
                xline, sline = tpMean, tpDev
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLd, dLCLd, ppT, pkT = tq.tManualPerf(mnA, mnB, 0, 0, sdA, sdB,
                                                                                          0, 0, tpUSL, tpLSL, tpUCL,
                                                                                          tpLCL)
            # # Declare Plots attributes ------------------------------------------------------------[]
            # XBar Mean Plot
            a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
            a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 3 Sigma span (Purple)
            a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minTT, sBar_maxTT -------[]
            # Define Legend's Attributes  ----
            a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
            a2.axhspan(sLCLtp, sUCLtp, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 1 Sigma Span
            a2.axhspan(sUCLtp, sBar_maxTP, facecolor='#CCCCFF', edgecolor='#CCCCFF')  # 1 Sigma above the Mean
            a2.axhspan(sBar_minTP, sLCLtp, facecolor='#CCCCFF', edgecolor='#CCCCFF')

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
                a2.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a1.set_xlim(0, window_Xmax)
                a2.set_xlim(0, window_Xmax)

            # Set trip line for individual time-series plot -----------------------------------[R1]
            import triggerModule as sigma
            sigma.trigViolations(a1, UsePLC_DBS, 'TG', YScale_minTP, YScale_maxTP, xucT, xlcT, xusT, xlsT, mnT, sdT)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(fig, asynchronousTP, frames=None, save_count=100, repeat_delay=None,
                                interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

# ============================================= CASCADE CLASS METHODS ===============================================#
#                                                                                                                    #
# This class procedure allows SCADA operator to split the screen into respective runtime process                     #
#                                                                                                                    #
# ===================================================================================================================#



# FIXME -----------------------------------------------------------------------------------------------------[]

class cascadeCommonViewsRF(ttk.Frame):          # Load common Cascade and all object in cascadeSwitcher() class
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.createWidgetsRF()

    def createWidgetsRF(self):

        # Load Quality Historical Values -----------[]
        rfSize, rfgType, rfSspace, rfHL, rfAL, rfFO, rfParam1, rfParam2, rfParam3, rfParam4, rfParam5 = mq.decryptpProcessLim(
            WON, 'RF')
        # Break down each element to useful list ---------------[Tape Temperature]
        if rfHL and rfParam1 and rfParam2 and rfParam3 and rfParam4 and rfParam5:  #
            rfPerf = '$Pp_{k' + str(sSize) + '}$'  # Using estimated or historical Mean
            rflabel = 'Pp'
            # -------------------------------------[]
            One = rfParam1.split(',')  # split into list elements
            Two = rfParam2.split(',')
            Thr = rfParam3.split(',')
            For = rfParam4.split(',')
            Fiv = rfParam5.split(',')
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
            # Load historical limits for the process----#
            if cpLayerNo == 1:  # '22mm'|'18mm',  1-40 | 41+ TODO
                rfUCL = float(One[2].strip("' "))  # Strip out the element of the list
                rfLCL = float(One[3].strip("' "))
                rfMean = float(One[4].strip("' "))
                rfDev = float(One[5].strip("' "))
                # --------------------------------
                sUCLrf = float(One[6].strip("' "))
                sLCLrf = float(One[7].strip("' "))
                # --------------------------------
                rfUSL = (rfUCL - rfMean) / 3 * 6
                rfLSL = (rfMean - rfLCL) / 3 * 6
                # --------------------------------
            elif cpTapeW == dTape2 and cpLayerNo == 2:
                rfUCL = float(Two[2].strip("' "))  # Strip out the element of the list
                rfLCL = float(Two[3].strip("' "))
                rfMean = float(Two[4].strip("' "))
                rfDev = float(Two[5].strip("' "))
                # --------------------------------
                sUCLrf = float(Two[6].strip("' "))
                sLCLrf = float(Two[7].strip("' "))
                # --------------------------------
                rfUSL = (rfUCL - rfMean) / 3 * 6
                rfLSL = (rfMean - rfLCL) / 3 * 6
            elif cpTapeW == dTape3 and cpLayerNo == range(3, 40):
                rfUCL = float(Thr[2].strip("' "))  # Strip out the element of the list
                rfLCL = float(Thr[3].strip("' "))
                rfMean = float(Thr[4].strip("' "))
                rfDev = float(Thr[5].strip("' "))
                # --------------------------------
                sUCLrf = float(Thr[6].strip("' "))
                sLCLrf = float(Thr[7].strip("' "))
                # --------------------------------
                rfUSL = (rfUCL - rfMean) / 3 * 6
                rfLSL = (rfMean - rfLCL) / 3 * 6
            elif cpTapeW == dTape4 and cpLayerNo == 41:
                rfUCL = float(For[2].strip("' "))  # Strip out the element of the list
                rfLCL = float(For[3].strip("' "))
                rfMean = float(For[4].strip("' "))
                rfDev = float(For[5].strip("' "))
                # --------------------------------
                sUCLrf = float(For[6].strip("' "))
                sLCLrf = float(For[7].strip("' "))
                # --------------------------------
                rfUSL = (rfUCL - rfMean) / 3 * 6
                rfLSL = (rfMean - rfLCL) / 3 * 6
            else:
                rfUCL = float(Fiv[2].strip("' "))  # Strip out the element of the list
                rfLCL = float(Fiv[3].strip("' "))
                rfMean = float(Fiv[4].strip("' "))
                rfDev = float(Fiv[5].strip("' "))
                # --------------------------------
                sUCLrf = float(Fiv[6].strip("' "))
                sLCLrf = float(Fiv[7].strip("' "))
                # --------------------------------
                rfUSL = (rfUCL - rfMean) / 3 * 6
                rfLSL = (rfMean - rfLCL) / 3 * 6
                # -------------------------------
        else:  # Computes Shewhart constants (Automatic Limits)
            rfUCL = 0
            rfLCL = 0
            rfMean = 0
            rfDev = 0
            sUCLrf = 0
            sLCLrf = 0
            rfUSL = 0
            rfLSL = 0
            rfPerf = '$Cp_{k' + str(sSize) + '}$'  # Using Automatic group Mean
            rflabel = 'Cp'

        # ------ [End of Historical abstraction -------]
        label = ttk.Label(self, text='[' + rType + ' Mode - RF]', font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        # Define Axes ---------------------#
        fig = Figure(figsize=(12.5, 7), dpi=100)
        fig.subplots_adjust(left=0.04, bottom=0.033, right=0.988, top=0.957, hspace=0.14, wspace=0.195)
        # ---------------------------------[]
        a1 = fig.add_subplot(2, 4, (1, 3))  # X Bar Plot
        a2 = fig.add_subplot(2, 4, (5, 7))  # S Bar Plo
        a3 = fig.add_subplot(2, 4, (4, 8))  # Performance Feeed

        # Declare Plots attributes --------------------------------[]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minRF, YScale_maxRF = 10, 500
        sBar_minRF, sBar_maxRF = 10, 250                            # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (int(sSize) + 3)              # windows view = visible data points

        # ----------------------------------------------------------#
        # Real-Time Parameter according to updated requirements ----# 28/Feb/2025
        T1 = WON + '_RF'                                            # Roller Force
        # ----------------------------------------------------------#

        # Common properties -------------------------------------------------#
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [" + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        a1.set_title('Roller Force [XBar Plot]', fontsize=12, fontweight='bold')
        a2.set_title('Roller Force [S Plot]', fontsize=12, fontweight='bold')
        # Apply grid lines -----
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a1.legend(loc='upper right', title='Roller Force (N.m)')
        a2.legend(loc='upper right', title='Sigma curve')

        # ----------------------------------------------------------#
        a1.set_ylim([YScale_minRF, YScale_maxRF], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ----------------------------------------------------------#
        a2.set_ylim([sBar_minRF, sBar_maxRF], auto=True)
        a2.set_xlim([window_Xmin, window_Xmax])

        # ---------------------------------------------------------[]
        a3.cla()
        a3.get_yaxis().set_visible(False)
        a3.get_xaxis().set_visible(False)

        # ----------------------------------------------------------[]
        # Define Plot area and axes -
        # ----------------------------------------------------------#
        im10, = a1.plot([], [], 'o-', label='Roller Force - (R1H1)')
        im11, = a1.plot([], [], 'o-', label='Roller Force - (R1H2)')
        im12, = a1.plot([], [], 'o-', label='Roller Force - (R1H3)')
        im13, = a1.plot([], [], 'o-', label='Roller Force - (R1H4)')
        im14, = a2.plot([], [], 'o-', label='Roller Force')
        im15, = a2.plot([], [], 'o-', label='Roller Force')
        im16, = a2.plot([], [], 'o-', label='Roller Force')
        im17, = a2.plot([], [], 'o-', label='Roller Force')

        im18, = a1.plot([], [], 'o-', label='Roller Force - (R2H1)')
        im19, = a1.plot([], [], 'o-', label='Roller Force - (R2H2)')
        im20, = a1.plot([], [], 'o-', label='Roller Force - (R2H3)')
        im21, = a1.plot([], [], 'o-', label='Roller Force - (R2H4)')
        im22, = a2.plot([], [], 'o-', label='Roller Force')
        im23, = a2.plot([], [], 'o-', label='Roller Force')
        im24, = a2.plot([], [], 'o-', label='Roller Force')
        im25, = a2.plot([], [], 'o-', label='Roller Force')

        im26, = a1.plot([], [], 'o-', label='Roller Force - (R3H1)')
        im27, = a1.plot([], [], 'o-', label='Roller Force - (R3H2)')
        im28, = a1.plot([], [], 'o-', label='Roller Force - (R3H3)')
        im29, = a1.plot([], [], 'o-', label='Roller Force - (R3H4)')
        im30, = a2.plot([], [], 'o-', label='Roller Force')
        im31, = a2.plot([], [], 'o-', label='Roller Force')
        im32, = a2.plot([], [], 'o-', label='Roller Force')
        im33, = a2.plot([], [], 'o-', label='Roller Force')

        im34, = a1.plot([], [], 'o-', label='Roller Force - (R4H1)')
        im35, = a1.plot([], [], 'o-', label='Roller Force - (R4H2)')
        im36, = a1.plot([], [], 'o-', label='Roller Force - (R4H3)')
        im37, = a1.plot([], [], 'o-', label='Roller Force - (R4H4)')
        im38, = a2.plot([], [], 'o-', label='Roller Force')
        im39, = a2.plot([], [], 'o-', label='Roller Force')
        im40, = a2.plot([], [], 'o-', label='Roller Force')
        im41, = a2.plot([], [], 'o-', label='Roller Force')
        # -----------------------------------------------------------#
        # Statistical Feed -----------------------------------------[]
        a3.text(0.466, 0.945, 'Performance Feed - RF', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        a3.add_patch(rect1)
        a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)---------------------
        a3.text(0.145, 0.804, rflabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.658, '#Pp Value', fontsize=24, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.650, 0.820, 'Ring ' + rflabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        a3.text(0.145, 0.403, rfPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=22, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring ' + rfPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        # -------------------------------------
        a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ----- Pipe Position and SMC Status -----
        a3.text(0.080, 0.090, 'Pipe Position: ' + pPos + '    Processing Layer #' + layer, fontsize=12, ha='left',
                transform=a3.transAxes)
        a3.text(0.080, 0.036, 'SMC Status: ' + eSMC, fontsize=12, ha='left', transform=a3.transAxes)

        # ---------------- EXECUTE SYNCHRONOUS METHOD ---------------#
        def synchronousRF(smp_Sz, smp_St, fetchT):
            fetch_no = str(fetchT)      # entry value in string sql syntax

            # Obtain Volatile Data from PLC Host Server ---------------------------[]
            if not inUseAlready:                    # Load CommsPlc class once
                import CommsSql as q
                q.DAQ_connect(1, 0)
            else:
                con_rf = conn.cursor()

            # Evaluate conditions for SQL Data Fetch ------------------------------[A]
            """
            Load watchdog function with synchronous function every seconds
            """
            # Initialise RT variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard                         # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                if UsePLC_DBS:  # Not Using PLC Data
                    import ArrayRP_sqlRLmethod as lq  # DrLabs optimization method

                    inProgress = True  # True for RetroPlay mode
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
                    # -----------------------------------------------------------------[]

                    # Allow selective runtime parameter selection on production critical process
                    procID = 'RF'
                    rfData = slp.paramDataRequest(procID, rfSize, rfgType, fetch_no)

                else:
                    import sqlArrayRLmethodLP as slp  # DrLabs optimization method

                    inProgress = True  # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

                    if not sysRun:
                        sysRun, msctcp, msc_rt = wd.autoPausePlay()  # Retrieve M.State from Watchdog
                    print('SMC- Run/Code:', sysRun, msctcp, msc_rt)

                    if keyboard.is_pressed("Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:
                        print('\nProduction is pausing...')
                        if not autoSpcPause:
                            autoSpcRun = not autoSpcRun
                            autoSpcPause = True
                            print("\nVisualization in Paused Mode...")
                        else:
                            autoSpcPause = False
                            print("Visualization in Real-time Mode...")
                    else:
                        # Get list of relevant SQL Tables using conn() --------------------[]
                        rfData = slp.sqlexec(rfSize, rfgType, con_rf, T1, fetchT)

                    # ------ Inhibit iteration ----------------------------------------------------------[]
                    """
                    # Set condition for halting real-time plots in watchdog class ---------------------
                    """
                    # TODO --- values for inhibiting the SQL processing
                    if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                        con_rf.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

            return rfData

        # ================== End of synchronous Method ==========================

        def asynchronousRF(db_freq):
            timei = time.time()  # start timing the entire loop

            # Bistream Data Pooling Method ---------------------#
            rfData = synchronousRF(rfSize, rfgType, db_freq)  # data loading functions
            # --------------------------------------------------#

            if UsePLC_DBS == 1:
                import VarPLClp as rf

                viz_cycle = 10
                # Call synchronous data function ---------------[]
                columns = qrf.validCols(T1)  # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(rfData, columns=columns)  # Include table data into python Dataframe
                RF = rf.loadProcesValues(df1)  # Join data values under dataframe

            else:
                import VarSQLlp as rf  # load SQL variables column names | rfVarSQL

                viz_cycle = 150
                g1 = qrf.validCols(T1)  # Construct Data Column selSqlColumnsTFM.py
                df1 = pd.DataFrame(rfData, columns=g1)  # Import into python Dataframe
                RF = rf.loadProcesValues(df1)  # Join data values under dataframe

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
            im10.set_ydata((RF[0]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 1
            im11.set_ydata((RF[1]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 2
            im12.set_ydata((RF[2]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 3
            im13.set_ydata((RF[3]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 1 ---------#
            mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(rfHL, rfSize, 'RF')
            # ---------------------------------------#
            im14.set_ydata((RF[4]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 1
            im15.set_ydata((RF[5]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 2
            im16.set_ydata((RF[6]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 3
            im17.set_ydata((RF[7]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 2 ---------#
            mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(rfHL, rfSize, 'RF')
            # ---------------------------------------#
            im18.set_ydata((RF[8]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 1
            im19.set_ydata((RF[9]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 2
            im20.set_ydata((RF[10]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 3
            im21.set_ydata((RF[11]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 3 ---------#
            mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(rfHL, rfSize, 'RF')
            # ---------------------------------------#
            im22.set_ydata((RF[12]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 1
            im23.set_ydata((RF[13]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 2
            im24.set_ydata((RF[14]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 3
            im25.set_ydata((RF[15]).rolling(window=rfSize, min_periods=1).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 4 ---------#
            mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(rfHL, rfSize, 'RF')
            # ---------------------------------------#
            # S Plot Y-Axis data points for StdDev ----------------------------------------
            im26.set_ydata((RF[0]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im27.set_ydata((RF[1]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im28.set_ydata((RF[2]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im29.set_ydata((RF[3]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])

            im30.set_ydata((RF[4]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im31.set_ydata((RF[5]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im32.set_ydata((RF[6]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im33.set_ydata((RF[7]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])

            im34.set_ydata((RF[8]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im35.set_ydata((RF[9]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im36.set_ydata((RF[10]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im37.set_ydata((RF[11]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])

            im38.set_ydata((RF[12]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im39.set_ydata((RF[13]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im40.set_ydata((RF[14]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])
            im41.set_ydata((RF[15]).rolling(window=rfSize, min_periods=1).std()[0:db_freq])

            # Compute entire Process Capability -----------#
            if not rfHL:
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLb, ppT, pkT, xline, sline = tq.tAutoPerf(rfSize, mnA, mnB,
                                                                                                      mnC, mnD, sdA,
                                                                                                      sdB, sdC, sdD)
            else:
                xline, sline = rfMean, rfDev
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLba, ppT, pkT = tq.tManualPerf(mnA, mnB, mnC, mnD, sdA, sdB,
                                                                                           sdC, sdD, rfUSL, rfLSL,
                                                                                           rfUCL,
                                                                                           rfLCL)

            # # Declare Plots attributes --------------------------------------------------------[]
            # XBar Mean Plot
            a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
            a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 3 Sigma span (Purple)
            a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minRF, sBar_maxRF -------[]
            # Define Legend's Attributes  ----
            a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
            a2.axhspan(sLCLrf, sUCLrf, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 1 Sigma Span
            a2.axhspan(sUCLrf, sBar_maxRF, facecolor='#CCCCFF', edgecolor='#CCCCFF')  # 1 Sigma above the Mean
            a2.axhspan(sBar_minRF, sLCLrf, facecolor='#CCCCFF', edgecolor='#CCCCFF')

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
                a2.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a1.set_xlim(0, window_Xmax)
                a2.set_xlim(0, window_Xmax)

            # Set trip line for individual time-series plot -----------------------------------[R1]
            import triggerModule as sigma
            sigma.trigViolations(a1, UsePLC_DBS, 'RF', YScale_minRF, YScale_maxRF, xucT, xlcT, xusT, xlsT, mnT, sdT)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousRF, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # Update Canvas -----------------------------------------------------[]
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)


class cascadeCommonViewsEoL(ttk.Frame):          # Load common Cascade and all object in cascadeSwitcher() class
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=1300, y=750)
        self.createWidgetsCT()

    def createWidgetsCT(self):
        label = ttk.Label(self, text="JIT - End of Layer Processing", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        # Define Axes ---------------------#
        # fig = Figure(figsize=(25, 12), dpi=100)   # 13
        fig = Figure(figsize=(12.5, 5.5), dpi=100)  # 13

        # Attempt to auto screen size ---
        fig.subplots_adjust(left=0.043, bottom=0.043, right=0.986, top=0.96, hspace=0.14, wspace=0.195)

        # Declare Plots attributes --------------------------------[]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minCT, YScale_maxCT = hLSLa - 8.5, hUSLa + 8.5
        window_Xmin, window_Xmax = 0, (int(sSize) + 3)              # windows view = visible data points
        # ----------------------------------------------------------#

        if pMinMax:
            a1 = fig.add_subplot(1, 1, 1)

            # Declare Plots attributes -----------------------------------------[]
            a1.set_title('Just inTime EoL Report', fontsize=12, fontweight='bold')

            a1.grid(color="0.5", linestyle='-', linewidth=0.5)
            a1.legend(loc='upper right', title='Cell Tension (N.mm2)')
            # Initialise runtime limits
            a1.set_ylabel("Min/Max Value Plot - N.mm2")
            a1.axhline(y=hMeanB, color="red", linestyle="-", linewidth=1)

        elif pContrl:
            a1 = fig.add_subplot(2, 2, (1, 2))  # Cell Tension X Bar Plot
            a2 = fig.add_subplot(2, 2, (3, 4))  # Cell Tension s Plot

            # Declare Plots attributes -----------------------------------------[]
            a1.set_title('Cell Tension [XBar Plot]', fontsize=12, fontweight='bold')
            a2.set_title('Cell Tension [SBar Plot]', fontsize=12, fontweight='bold')
            # Apply grid lines -----
            a1.grid(color="0.5", linestyle='-', linewidth=0.5)
            a2.grid(color="0.5", linestyle='-', linewidth=0.5)

            # Common properties -------------------------------------------------#
            a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
            a2.set_ylabel("Sample Deviation [" + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
            a1.legend(loc='upper right', title='Cell Tension Control Plot')
            a2.legend(loc='upper right', title='Sigma curve')
            # ----------------------------
            # a1.legend(loc='upper left')
            # axp.legend(loc='upper left')

            # Define limits for X Bar Plots -----------------------#
            a1.axhline(y=hMeanB, color="green", linestyle="-", linewidth=1)
            a1.axhspan(hLCLb, hUCLb, facecolor='#A9EF91', edgecolor='#A9EF91')  # Light Green
            # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
            a1.axhspan(hUCLb, hUSLb, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            a1.axhspan(hLSLb, hLCLb, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            # clean up when Mean line changes ---
            a1.axhspan(hUSLb, hUSLb + 10, facecolor='#FFFFFF', edgecolor='#FFFFFF')
            a1.axhspan(hLSLb - 10, hLSLb, facecolor='#FFFFFF', edgecolor='#FFFFFF')

            # Define limits for S Bar Plot -----------------------#
            a2.axhline(y=hDevB, color="green", linestyle="-", linewidth=1)
            a2.axhspan(dLCLb, dUCLb, facecolor='#A9EF91', edgecolor='#A9EF91')  # Light Green

            # clean up when Mean line changes ---
            a2.axhspan(dUCLb, dUCLb + 0.005, facecolor='#FFFFFF', edgecolor='#FFFFFF')
            a2.axhspan(dLCLb - 0.05, dLCLb, facecolor='#FFFFFF', edgecolor='#FFFFFF')

        # Model data --------------------------------------------------[]
        a1.plot([105, 120, 114, 109, 110, 86, 102, 103, 101, 100])
        # -------------------------------------------------------------[]
        # Calibrate the rest of the Plots -----------------------------#
        # ----------------------------------------------------------[]
        # Define Plot area and axes -
        # ----------------------------------------------------------#
        im10, = a1.plot([], [], 'o-', label='Cell Tension A (N/mm2)')
        im11, = a1.plot([], [], 'o-', label='Cell tension B (N/mm2)')


        # ---------------- EXECUTE SYNCHRONOUS METHOD ---------------#
        def synchronousEoL(smp_Sz, smp_St, fetchT):
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
                import sqlArrayRLmethodCT as ct  # DrLabs optimization method
                inProgress = True  # True for RetroPlay mode
                print('\nAsynchronous controller activated...')
                print('DrLabs' + "' Runtime Optimisation is Enabled!")

                # Get list of relevant SQL Tables using conn() --------------------[]
                ctData = ct.sqlexec(smp_Sz, smp_St, qRP, tblID, fetchT)  # perform DB connections
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    qRP.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')

            return ctData

        # ================== End of synchronous Method ==========================

        def asynchronousEoL(db_freq):

            timei = time.time()  # start timing the entire loop

            # Call data loader Method---------------------------#
            ctSQL = synchronousEoL(smp_Sz, stp_Sz, db_freq)      # data loading functions

            import VarSQLct as qct                              # load SQL variables column names | rfVarSQL
            viz_cycle = 150
            g1 = qc.validCols('CT')                             # Construct Data Column selSqlColumnsTFM.py
            df1 = pd.DataFrame(ctSQL, columns=g1)               # Import into python Dataframe
            RF = qct.loadProcesValues(df1)                      # Join data values under dataframe
            print('\nDataFrame Content', df1.head(10))          # Preview Data frame head
            print("Memory Usage:", df1.info(verbose=False))     # Check memory utilization

            # Declare Plots attributes ------------------------------------------------------------[]
            a1.grid(color="0.5", linestyle='-', linewidth=0.5)
            a1.legend(loc='upper left', title='XBar Plot')
            # -------------------------------------------------------------------------------------[]
            # Plot X-Axis data points -------- X Plot
            im10.set_xdata(np.arange(db_freq))
            im11.set_xdata(np.arange(db_freq))
            # X Plot Y-Axis data points for XBar -------------------------------------------[# Channels]
            im10.set_ydata((RF[0]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 1
            im11.set_ydata((RF[1]).rolling(window=smp_Sz, min_periods=1).mean()[0:db_freq])  # Segment 2
            if not useHL and not pMinMax:  # switch to control plot on shewhart model
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLd, dLCLd, ppT, pkT, xline, sline = tq.tAutoPerf(smp_Sz, mnA,
                                                                                                      mnB,
                                                                                                      0, 0, sdA,
                                                                                                      sdB, 0, 0)
            else:  # switch to historical limits
                xline, sline = hMeanA, hDevA

            # # Declare Plots attributes ------------------------------------------------------------[]
            # XBar Mean Plot
            a1.axhline(y=xline, color="red", linestyle="--", linewidth=0.8)
            a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')  # 3 Sigma span (Purple)
            a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')  # grey area
            a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minTG, sBar_maxTG -------[]
            # Setting up the parameters for moving windows Axes ---[]
            if db_freq > window_Xmax:
                a1.set_xlim(db_freq - window_Xmax, db_freq)
            else:
                a1.set_xlim(0, window_Xmax)

            # Set trip line for individual time-series plot -----[R1]
            # No trigger module processing - Production parameter is for monitoring purposes only.
            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(f, asynchronousEoL, frames=None, save_count=100, repeat_delay=None,
                                interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # Update Canvas ---------------------------------------------------[]
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)


class cascadeCommonViewsRPT(ttk.Frame):                                # End of Layer Progressive Report Tabb
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        # self.grid(column=0, row=0, padx=10, pady=10)
        self.place(x=10, y=750)
        self.createWidgets()

    def createWidgets(self):
        label = ttk.Label(self, text="End of Layer - Progressive Summary:                                          ", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        # label.place(x=100, y=50)
        # Define Axes ---------------------#
        combo = ttk.Combobox(self, values=["= Select Progressive Report =", "View EoL Curve", "Roller Pressure",
                                           "Tape Temperature", "Subs Temperature", "Winding Speed", "Gap Measurement",
                                           "Generate EoL Report", "Generate EoP Report"], width=25)
        combo.place(x=520, y=10)
        combo.current(0)

        # Create empty Text Space -----------------------------------
        text_widget = tk.Text(self, wrap='word', width=155, height=80)
        text_widget.pack(padx=10, pady=10)

        def option_selected(event):
            selected_option = combo.get()
            if selected_option == "View EoL Curve":
                # rpt = "RPT_EL_" + str(processWON[0])
                cascadeCommonViewsEoL()
            elif selected_option == "Roller Pressure":
                rpt = "RPT_RP_" + str(processWON[0])
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder
            elif selected_option == "Tape Temperature":
                rpt = "RPT_TT_" + str(processWON[0])
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder
            elif selected_option == "Subs Temperature":
                rpt = "RPT_ST_" + str(processWON[0])
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder
            elif selected_option == "Winding Speed":
                rpt = "RPT_WS_" + str(processWON[0])
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder
            elif selected_option == "Gap Measurement":
                rpt = "RPT_TG_" + str(processWON[0])
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder
            else:
                rpt = "VOID_REPORT"
                readEoP(text_widget, rpt)                                 # Clean up the matt instead

            print("You selected:", selected_option)
        combo.bind("<<ComboboxSelected>>", option_selected)

        # Update Canvas -----------------------------------------------------[NO FIGURE YET]
        # canvas = FigureCanvasTkAgg(fig, self)
        # canvas.get_tk_widget().pack(expand=False)

        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True)


class cascadeCommonViewsOEE(ttk.Frame):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=800)
        self.createWidgets()

    def createWidgets(self):
        # -----------------------------------
        f = Figure(figsize=(6, 5), dpi=100)
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

            import VarSQLoe as qoe                              # load SQL variables column names | rfVarSQL
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

# ====================================================== MAIN PIPELINE ===========================================[]
# qType = 0   # default play mode


def userMenu():     # listener, myplash
    print('Welcome to RL Synchronous SPC....')
    global sqlRO, metRO, root, HeadA, HeadB, vTFM, comboL, comboR, qType

    # splash = myplash
    # del splash                                  # Turn off Splash timer -----[]

    print('Timer Paused for GUI...')

    # inherit PID from Splash Screen and transfer back when Object closes
    print('\nUser Menu: Inherited PARENT ID#:', os.getppid())
    print('User Menu: Inherited CHILD ID#:', os.getpid())
    print('User Menu: New Object THREAD:', get_native_id())
    time.sleep(2)

    # for windows centralizing ---------[]
    window_height = 580     #1080
    window_width = 950      #1920

    root.title('Synchronous SPC - ' + strftime("%a, %d %b %Y", gmtime()))
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

    def save_pMetrics():                    # Save historical Limits for Production Parameters
        print("\nSaving Production Constants..")
        grayOut = [button2, e7, e8, m1, m2, m3, m4, m5, m6, m7, m8]     # set value entry field to read only
        e5.config(state='readonly')                                     # applicable to combo drop down
        e6.config(state='readonly')                                     # combo box property
        for fld in grayOut:
            fld.config(state="disabled")                        # for text fields
        if hLmtA.get() == 1:                                    # check condition of edit button
            hLmtA.set(0)                                        # uncheck the button
        s_butt.config(state="disabled")                         # disable Save button

        print('\nStacked Values:', rtValues)
        print('Array Length', len(rtValues))

        # print('Switch Values', rtValues[-1])
        if len(rtValues) > 1:                                   # Compute the length for dynamic arrays
            x = len(rtValues) - 1                               # Use the last index

            # Encrypt configuration on production params -------#
            mp.saveMetricspP(WON, sel_SS, sel_gT, sSta, sEnd, rtValues[x][0], rtValues[x][1], rtValues[x][2],
                             rtValues[x][3], rtValues[x][4], rtValues[x][5], rtValues[x][6], rtValues[x][7])
        else:
            mp.saveMetricspP(WON, sel_SS, sel_gT, sSta, sEnd, OT, CT, RP, LA, WS, TG, ST, LP)
        return


    def clearMetrics():
        # clear the content of chart parameter using change settings button ---
        global e5, e6, e7, e8, m1, m2, m3, m4, m5, m6, m7, m8, metRO

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

        s_butt.config(state="normal")  # enable edit button (Sve Details) on entry
        # mp.ppHLderivation(pop, gSize1, gSize2, xUCLLP, xLCLLP, xUCLLA, xLCLLA)

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


    def dMinMaxPlot():
        global pStat, dMax, mMax, oMax, OT, CT, RP, LA, WS, TG, ST, LP, m1, m2, m3, m4, m5, m6, m7, m8
        if dnvMinMax.get():
            print('\nMin/Max Monitoring for DNV Production Parameters..')
            dMax = 1
            mMax = 0
            oMax = 0
            pStat = 1
            dnvMinMax.set(dMax)
            mgmMinMax.set(mMax)
            othMinMax.set(oMax)

            # Set Production Parameter on DNV Params Monitor
            mOT.set(1)      # Oven Temperature
            mCT.set(1)      # Cell Tension
            mRP.set(1)      # Roller Pressure
            mWS.set(1)      # Tape Winding Speed
            # --------
            mST.set(0)      # Substrate emp
            mTG.set(0)      # Tape Gap pol
            mLA.set(0)      # Laser Angle
            mLP.set(0)      # Laser Power
            # ----------------------------------------------------
            if metRO:
                # repopulate with default values -----------#
                m1 = Checkbutton(pop, text="Oven Temperature", font=("bold", 10), variable=mOT, state="disabled")
                m1.place(x=10, y=y_start)

                m2 = Checkbutton(pop, text="Cell Tension", font=("bold", 10), variable=mCT, state="disabled")
                m2.place(x=150, y=y_start)

                m3 = Checkbutton(pop, text="Roller Pressure", font=("bold", 10), variable=mRP, state="disabled")
                m3.place(x=270, y=y_start)
                # mRP.set(1)

                m4 = Checkbutton(pop, text="Gap Polarisation", font=("bold", 10), variable=mTG, state="disabled")
                m4.place(x=270, y=y_start + y_incmt * 1)
                # mLA.set(1)

                m5 = Checkbutton(pop, text="Spooling Tension", font=("bold", 10), variable=mST, state="disabled")
                m5.place(x=10, y=y_start + y_incmt * 1)

                m6 = Checkbutton(pop, text="Winding Speed", font=("bold", 10), variable=mWS, state="disabled")
                m6.place(x=150, y=y_start + y_incmt * 1)
                # -------------------------------------------- Not included in DNV/MGM requirements
                m7 = Checkbutton(pop, text="Laser Power", font=("bold", 10), variable=mLP, state="disabled")
                m7.place(x=400, y=y_start)

                m8 = Checkbutton(pop, text="Laser Angle", font=("bold", 10), variable=mLA, state="disabled")
                m8.place(x=400, y=y_start + y_incmt * 1)
                # -----------------------------------
                OT, CT, RP, LA, WS, TG, ST, LP = 1, 1, 1, 0, 1, 0, 0, 0
            # -----------End of Parameters ----
        else:
            dMax = 0
            mMax = 0        # Defaulted to Commercial Production
            oMax = 0
            pStat = 0
            dnvMinMax.set(dMax)
            mgmMinMax.set(mMax)
            othMinMax.set(oMax)
            mOT.set(0)
            mCT.set(0)
            mRP.set(0)
            mWS.set(0)
            OT, CT, RP, LA, WS, TG, ST, LP = 0, 0, 0, 0, 0, 0, 0, 0
        print('Min/Max Monitoring:', dMax, 'Plot Stats:', pStat)
        return OT, CT, RP, LA, WS, TG, ST, LP

    def mMinMaxPlot():
        global pStat, dMax, mMax, oMax, OT, CT, RP, LA, WS, TG, ST, LP, m1, m2, m3, m4, m5, m6, m7, m8
        if mgmMinMax.get():
            print('\nMin/Max Monitoring for MGM Production Parameters..')
            dMax = 0
            mMax = 1
            oMax = 0
            pStat = 1
            dnvMinMax.set(dMax)
            mgmMinMax.set(mMax)
            othMinMax.set(oMax)
            # Set Production Parameter Variables
            mLA.set(1)
            mLP.set(1)
            mCT.set(1)
            mOT.set(1)
            mRP.set(1)
            mWS.set(1)
            # ---------
            mTG.set(0)
            mST.set(0)
            # ----------------------------------------------------[]

            if metRO:
                # repopulate with default values -----------#
                m1 = Checkbutton(pop, text="Oven Temperature", font=("bold", 10), variable=mOT, state="disabled")
                m1.place(x=10, y=y_start)

                m2 = Checkbutton(pop, text="Cell Tension", font=("bold", 10), variable=mCT, state="disabled")
                m2.place(x=150, y=y_start)

                m3 = Checkbutton(pop, text="Roller Pressure", font=("bold", 10), variable=mRP, state="disabled")
                m3.place(x=270, y=y_start)

                m4 = Checkbutton(pop, text="Gap Polarisation", font=("bold", 10), variable=mTG, state="disabled")
                m4.place(x=270, y=y_start + y_incmt * 1)

                m5 = Checkbutton(pop, text="Spooling Tension", font=("bold", 10), variable=mST, state="disabled")
                m5.place(x=10, y=y_start + y_incmt * 1)

                m6 = Checkbutton(pop, text="Winding Speed", font=("bold", 10), variable=mWS, state="disabled")
                m6.place(x=150, y=y_start + y_incmt * 1)
                # -------------------------------------------- Not included in DNV/MGM requirements
                m7 = Checkbutton(pop, text="Laser Power", font=("bold", 10), variable=mLP, state="disabled")
                m7.place(x=400, y=y_start)

                m8 = Checkbutton(pop, text="Laser Angle", font=("bold", 10), variable=mLA, state="disabled")
                m8.place(x=400, y=y_start + y_incmt * 1)
            # -----------------------------------
            OT, CT, RP, LA, WS, TG, ST, LP = 0, 0, 0, 1, 1, 1, 0, 1
            # -----------End of Parameters ----
        else:
            dMax = 0
            mMax = 0                # Defaulted to Commercial Production
            oMax = 0
            pStat = 0
            dnvMinMax.set(dMax)
            mgmMinMax.set(mMax)
            othMinMax.set(oMax)
            mLA.set(0)
            mLP.set(0)
            mCT.set(0)
            mOT.set(0)
            mRP.set(0)
            mWS.set(0)
            # ---------
            mTG.set(0)
            mST.set(0)

            OT, CT, RP, LA, WS, TG, ST, LP = 0, 0, 0, 0, 0, 0, 0, 0
        print('Monitoring Params:', OT, CT, RP, LA, WS, TG, ST, LP, 'Plot Stats:', pStat)
        return OT, CT, RP, LA, WS, TG, ST, LP


    def oMinMaxPlot():
        global pStat, dMax, mMax, oMax, m1, m2, m3, m4, m5, m6, m7, m8, OT, CT, RP, LA, WS, TG, ST, LP
        # ------------------------------------------------------------
        if othMinMax.get():
            print('\nMin/Max Monitoring for NEW Production Parameters..')
            dMax = 0
            mMax = 0
            oMax = 1
            pStat = 1
            dnvMinMax.set(dMax)
            mgmMinMax.set(mMax)
            othMinMax.set(oMax)
            # Reset variables for Production Parameters
            mLP.set(0)
            mLA.set(0)
            mTG.set(0)
            mST.set(0)
            # -------
            mWS.set(0)
            mRP.set(0)
            mOT.set(0)
            mCT.set(0)

            def testA():
                if mOT.get():  # Oven Temperature
                    mOT.set(1)
                    OT = 1
                else:
                    mOT.set(0)
                    OT = 0
                print('\nOven Temperature Status:', OT)

                if mCT.get():  # Cell Tension
                    mCT.set(1)
                    CT = 1
                else:
                    mCT.set(0)
                    CT = 0
                print('Cell Tension Status:', CT)

                # ---------------------------------
                if mRP.get():  # Roller pressure
                    mRP.set(1)
                    RP = 1
                else:
                    mRP.set(0)
                    RP = 0
                print('Roller Pressure:', RP)

                if mLA.get():  # Laser Angle
                    mLA.set(1)
                    LA = 1
                else:
                    mLA.set(0)
                    LA = 0
                print('Laser Angles:', LA)

                if mST.get():  # Spooling Tension
                    mST.set(1)
                    ST = 1
                else:
                    mST.set(0)
                    ST = 0
                print('Spooling Tension:', ST)

                if mTG.get():  #
                    mTG.set(1)
                    TG = 1
                else:
                    mTG.set(0)
                    TG = 0
                print('Tape Gap Polarisation:', TG)

                if mWS.get():  # Winding Speed
                    mWS.set(1)
                    WS = 1
                else:
                    mWS.set(0)
                    WS = 0
                print('Winding Speed:', WS)

                if mLP.get():  # Laser Power
                    mLP.set(1)
                    LP = 1
                else:
                    mLP.set(0)
                    LP = 0
                print('Laser Power:', LP)

                print('\nMonitoring Stored Values:', OT, CT, RP, LA, WS, TG, ST, LP)

                # --------- Use dynamic array to store user selection ------------
                storedV = [OT, CT, RP, LA, WS, TG, ST, LP]
                rtValues.append(storedV)

                return OT, CT, RP, LA, WS, TG, ST, LP

            if metRO:
                # repopulate with default values -----------#
                m1 = Checkbutton(pop, text="Oven Temperature", font=("bold", 10), variable=mOT, state="normal", command=testA)
                m1.place(x=10, y=y_start)

                m2 = Checkbutton(pop, text="Cell Tension", font=("bold", 10), variable=mCT, state="normal", command=testA)
                m2.place(x=150, y=y_start)

                m3 = Checkbutton(pop, text="Roller Pressure", font=("bold", 10), variable=mRP, state="normal", command=testA)
                m3.place(x=270, y=y_start)

                m4 = Checkbutton(pop, text="Gap Polarisation", font=("bold", 10), variable=mTG, state="normal", command=testA)
                m4.place(x=270, y=y_start + y_incmt * 1)

                m5 = Checkbutton(pop, text="Spooling Tension", font=("bold", 10), variable=mST, state="normal", command=testA)
                m5.place(x=10, y=y_start + y_incmt * 1)

                m6 = Checkbutton(pop, text="Winding Speed", font=("bold", 10), variable=mWS, state="normal", command=testA)
                m6.place(x=150, y=y_start + y_incmt * 1)
                # -------------------------------------------- Not included in DNV/MGM requirements
                m7 = Checkbutton(pop, text="Laser Power", font=("bold", 10), variable=mLP, state="normal", command=testA)
                m7.place(x=400, y=y_start)

                m8 = Checkbutton(pop, text="Laser Angle", font=("bold", 10), variable=mLA, state="normal", command=testA)
                m8.place(x=400, y=y_start + y_incmt * 1)
            # -----------------------------------
            else:
                dMax = 0
                mMax = 0        # Defaulted to Commercial Production
                oMax = 0
                pStat = 0
                dnvMinMax.set(dMax)
                mgmMinMax.set(mMax)
                othMinMax.set(oMax)
                OT, CT, RP, LA, WS, TG, ST, LP = 0, 0, 0, 0, 0, 0, 0, 0
                # ----------------------------------------------------
                if metRO:
                    # repopulate with default values -----------#
                    m1 = Checkbutton(pop, text="Oven Temperature", font=("bold", 10), variable=mOT, state="disabled")
                    m1.place(x=10, y=y_start)

                    m2 = Checkbutton(pop, text="Cell Tension", font=("bold", 10), variable=mCT, state="disabled")
                    m2.place(x=150, y=y_start)

                    m3 = Checkbutton(pop, text="Roller Pressure", font=("bold", 10), variable=mRP, state="disabled")
                    m3.place(x=270, y=y_start)

                    m4 = Checkbutton(pop, text="Gap Polarisation", font=("bold", 10), variable=mTG, state="disabled")
                    m4.place(x=270, y=y_start + y_incmt * 1)

                    m5 = Checkbutton(pop, text="Spooling Tension", font=("bold", 10), variable=mST, state="disabled")
                    m5.place(x=10, y=y_start + y_incmt * 1)

                    m6 = Checkbutton(pop, text="Winding Speed", font=("bold", 10), variable=mWS, state="disabled")
                    m6.place(x=160, y=y_start + y_incmt * 1)

                    m7 = Checkbutton(pop, text="Laser Power", font=("bold", 10), variable=mLP, state="disabled")
                    m7.place(x=400, y=y_start)

                    m8 = Checkbutton(pop, text="Laser Angle", font=("bold", 10), variable=mLA, state="disabled")
                    m8.place(x=400, y=y_start + y_incmt * 1)
                    # -----------------------------------
                print('\nMonitoring Stored...', OT, CT, RP, LA, WS, TG, ST, LP)
        # return OT, CT, RP, LA, WS, TG, ST, LP


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

    def mgmChecksA():
        if pLP.get():
            pLP.set(1)
            pLA.set(0)
            pTP.set(0)
            pRF.set(0)
            pTT.set(0)
            pST.set(0)
            pTG.set(0)
            hlb.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pLP, pLA, pTP, pRF, pTT, pST, pTG)
        else:
            pLP.set(0)

    # ------------------------
    def mgmChecksB():
        if pLA.get():
            pLP.set(0)
            pLA.set(1)
            pTP.set(0)
            pRF.set(0)
            pTT.set(0)
            pST.set(0)
            pTG.set(0)
            hlb.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pLP, pLA, pTP, pRF, pTT, pST, pTG)
        else:
            pLA.set(0)

    # ------------------------
    def mgmChecksC():
        if pTP.get():
            pLP.set(0)
            pLA.set(0)
            pTP.set(1)
            pRF.set(0)
            pTT.set(0)
            pST.set(0)
            pTG.set(0)
            hlb.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pLP, pLA, pTP, pRF, pTT, pST, pTG)
        else:
            pTP.set(0)

    # ------------------------
    def mgmChecksD():
        if pRF.get():
            pLP.set(0)
            pLA.set(0)
            pTP.set(0)
            pRF.set(1)
            pTT.set(0)
            pST.set(0)
            pTG.set(0)
            hlb.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pLP, pLA, pTP, pRF, pTT, pST, pTG)
        else:
            pRF.set(0)

    # ------------------------
    def mgmChecksE():
        if pTT.get():
            pLP.set(0)
            pLA.set(0)
            pTP.set(0)
            pRF.set(0)
            pTT.set(1)
            pST.set(0)
            pTG.set(0)
            hlb.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pLP, pLA, pTP, pRF, pTT, pST, pTG)
        else:
            pTT.set(0)

    # ------------------------
    def mgmChecksF():
        if pST.get():
            pLP.set(0)
            pLA.set(0)
            pTP.set(0)
            pRF.set(0)
            pTT.set(0)
            pST.set(1)
            pTG.set(0)
            hlb.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pLP, pLA, pTP, pRF, pTT, pST, pTG)
        else:
            pST.set(0)

    # ------------------------
    def mgmChecksG():
        if pTG.get():
            pLP.set(0)
            pLA.set(0)
            pTP.set(0)
            pRF.set(0)
            pTT.set(0)
            pST.set(0)
            pTG.set(1)
            hlb.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pLP, pLA, pTP, pRF, pTT, pST, pTG)
        else:
            pLA.set(0)


    def runChecksB():
        if pTT.get():
            pTT.set(1)
            pRP.set(0)
            pST.set(0)
            pWS.set(0)
            pTG.set(0)
            hla.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pRP, pTT, pST, pWS, pTG)
        else:
            pTT.set(0)

    def runChecksC():
        if pST.get():
            pST.set(1)
            pRP.set(0)
            pTT.set(0)
            pWS.set(0)
            pTG.set(0)
            hla.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pRP, pTT, pST, pWS, pTG)
        else:
            pST.set(0)

    def runChecksD():
        if pWS.get():
            pWS.set(1)
            pRP.set(0)
            pTT.set(0)
            pST.set(0)
            pTG.set(0)
            hla.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pRP, pTT, pST, pWS, pTG)
        else:
            pWS.set(0)

    def runChecksE():
        if pTG.get():
            pTG.set(1)
            pRP.set(0)
            pTT.set(0)
            pST.set(0)
            pWS.set(0)
            hla.paramsEntry(modal, sel_SS, sel_gT, dnv, mgm, aut, pRP, pTT, pST, pWS, pTG)
        else:
            pTG.set(0)


    def dnvConfigs():
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
        # a1 = Checkbutton(modal, text="RollerPressure", font=("bold", 10), variable=pRP, command=runChecksA)
        # a1.place(x=20, y=10)
        a2 = Checkbutton(modal, text="TapeTemp", font=("bold", 10), variable=pTT, command=runChecksB)
        # a2.place(x=145, y=10)
        a2.place(x=20, y=10)

        a3 = Checkbutton(modal, text="SubstrateTemp", font=("bold", 10), variable=pST, command=runChecksC)
        a3.place(x=250, y=10)

        # a4 = Checkbutton(modal, text="WindingSpeed", font=("bold", 10), variable=pWS, command=runChecksD)
        # a4.place(x=380, y=10)

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

        # # Add Button for making selection -----------------------------------------------------[]
        # rf = Button(modal, text="Save " + pTy + " Metrics", command=saveMetricRP, bg="green", fg="white")
        # rf.place(x=254, y=200)
        return

# ------------------------------------------------------------------------------------------------[]
    def mgmConfigs():
        global modal, pLP, pLA, pTP, pRF, pTT, pST, pTG

        # prevent parent window closure until 'Save settings' ---[]
        root.protocol("WM_DELETE_WINDOW", preventClose)  # prevent closure even when using (ALT + F4)
        # -------------------------------------------------------[]

        modal = Toplevel(root)
        modal.wm_attributes('-topmost', True)

        pLP, pLA, pTP, pRF, pTT, pST, pTG = IntVar(), IntVar(), IntVar(), IntVar(), IntVar(), IntVar(), IntVar()

        # --------------------------------------------------------------------------------------------------------[]
        modal.resizable(False, False)

        w, h = 750, 250
        modal.title('Lookup Table: Define Historical Limits')
        screen_w = modal.winfo_screenwidth()
        screen_h = modal.winfo_screenheight()
        x_c = int((screen_w / 2) - (w / 2))
        y_c = int((screen_h / 2) - (h / 2))
        modal.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))

        # --------------------------------------------------------[]
        a1 = Checkbutton(modal, text="Laser Power", font=("bold", 10), variable=pLP, command=mgmChecksA)
        a1.place(x=20, y=10)

        a2 = Checkbutton(modal, text="Laser Angle", font=("bold", 10), variable=pLA, command=mgmChecksB)
        a2.place(x=120, y=10)

        a3 = Checkbutton(modal, text="Tape Error", font=("bold", 10), variable=pTP, command=mgmChecksC)
        a3.place(x=220, y=10)

        a4 = Checkbutton(modal, text="Roller Force", font=("bold", 10), variable=pRF, command=mgmChecksD)
        a4.place(x=320, y=10)

        a5 = Checkbutton(modal, text="Tape Temp", font=("bold", 10), variable=pTT, command=mgmChecksE)
        a5.place(x=420, y=10)

        a6 = Checkbutton(modal, text="Substrate Temp", font=("bold", 10), variable=pST, command=mgmChecksF)
        a6.place(x=520, y=10)

        a7 = Checkbutton(modal, text="Tape Gaps", font=("bold", 10), variable=pTG, command=mgmChecksG)
        a7.place(x=650, y=10)

        separator = ttk.Separator(modal, orient='horizontal')
        separator.place(relx=0.01, rely=0.17, relwidth=0.98, relheight=0.02)

        # --------------------------------------------[LP]
        Label(modal, text='Tape Size').place(x=10, y=50)
        Label(modal, text='x̄UCL').place(x=80, y=50)
        Label(modal, text='x̄LCL').place(x=140, y=50)
        Label(modal, text='ŝUCL').place(x=200, y=50)
        Label(modal, text='ŝLCL').place(x=260, y=50)

        Label(modal, text='x̄Mean').place(x=380, y=50)
        Label(modal, text='ŝMean').place(x=440, y=50)
        Label(modal, text='x̄USL').place(x=500, y=50)
        Label(modal, text='x̄LSL').place(x=560, y=50)

        Label(modal, text='Tape Layer(s)').place(x=660, y=50)
        # 550, 670
        # # Add Button for making selection -----------------------------------------------------[]
        # rf = Button(modal, text="Save " + pTy + " Metrics", command=saveMetricRP, bg="green", fg="white")
        # rf.place(x=254, y=200)
        return

    def enDNV():
        global dnv, mgm, aut
        if pLmtA.get():
            dnv = 1
            mgm = 0
            aut = 0
            dnv_butt.config(state="normal")
            mgm_butt.config(state="disabled")
            pLmtA.set(dnv)
            shewhart.set(aut)
            pLmtB.set(mgm)
        else:
            dnv = 1
            mgm = 0
            aut = 0
            dnv_butt.config(state="disabled")
            mgm_butt.config(state="disabled")
            pLmtA.set(dnv)
            shewhart.set(aut)
            pLmtB.set(mgm)

        return dnv, mgm, aut

    def enAUTO():
        global dnv, mgm, aut
        if shewhart.get():
            dnv = 0
            mgm = 0
            aut = 1
            dnv_butt.config(state="disabled")
            mgm_butt.config(state="disabled")
            pLmtA.set(dnv)
            shewhart.set(aut)
            pLmtB.set(mgm)
        else:
            dnv = 0
            mgm = 0
            aut = 1
            dnv_butt.config(state="disabled")
            mgm_butt.config(state="disabled")
            pLmtA.set(dnv)
            shewhart.set(aut)
            pLmtB.set(mgm)

        return dnv, mgm, aut

    def enMGM():
        global dnv, mgm, aut
        if pLmtB.get():
            dnv = 0
            mgm = 1
            aut = 0
            mgm_butt.config(state="normal")
            dnv_butt.config(state="disabled")
            pLmtA.set(dnv)
            shewhart.set(aut)
            pLmtB.set(mgm)
        else:
            dnv = 0
            mgm = 1
            aut = 0
            mgm_butt.config(state="disabled")
            dnv_butt.config(state="disabled")
            pLmtA.set(dnv)
            shewhart.set(aut)
            pLmtB.set(mgm)

        return dnv, mgm, aut

    def preventClose():
        print('Variable State:', pLmtA.get())
        pass

    def newMetricsConfig():  # This is a DNV Metric Configuration Lookup Table ------[]

        global pLmtA, sSta, sEnd, eStat, gSize1, gSize2, xUCLLP, xLCLLP, xUCLLA, xLCLLA, xUCLHT, xLCLHT, xUCLDL, \
            xLCLDL, xUCLDD, xLCLDD, xUCLOT, xLCLOT, hLmtA, shewhart, pLmtB, dnvMinMax, mgmMinMax, othMinMax, \
            s_butt, sSta, sEnd, e5, e6, dnv_butt, mgm_butt, button2, pop, mOT, mCT, mRP, mLA, mST, mTG, mWS, mLP

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

        pLmtA, pLmtB, pLmtC, pLmtD, pLmtE, pLmtF, mWS, mLP = (IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop),
                                                              IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop))
        hLmtA, hLmtB, shewhart, Sample = IntVar(pop), IntVar(pop), IntVar(pop), StringVar(pop)
        dnvMinMax, mgmMinMax, othMinMax, mOT, mCT, mRP, mLA, mST, mTG = (IntVar(pop), IntVar(pop), IntVar(pop),
                                                                         IntVar(pop), IntVar(pop), IntVar(pop),
                                                                         IntVar(pop), IntVar(pop), IntVar(pop))

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
        Label(pop, text='[Configure Monitoring Parameters]  -  ', font=("bold", 10)).place(x=10, y=80)

        p4 = Checkbutton(pop, text="DNV Pipe", font=("bold", 10), variable=dnvMinMax, command=dMinMaxPlot)
        p4.place(x=230, y=y_start - y_incmt * 1)  # 6

        p5 = Checkbutton(pop, text="MGM Pipe", font=("bold", 10), variable=mgmMinMax, command=mMinMaxPlot)
        p5.place(x=325, y=y_start - y_incmt * 1)  # 6

        p6 = Checkbutton(pop, text="Bespoke", font=("bold", 10), variable=othMinMax, command=oMinMaxPlot)
        p6.place(x=425, y=y_start - y_incmt * 1)  # 6

        # -------------------------------------------------------------------------[]
        m1 = Checkbutton(pop, text="Oven Temperature", font=("bold", 10), variable=mOT, state="disabled")
        m1.place(x=10, y=y_start)
        mOT.set(1)

        m2 = Checkbutton(pop, text="Cell Tension", font=("bold", 10), variable=mCT, state="disabled")
        m2.place(x=150, y=y_start)  #x=160
        mCT.set(1)

        m3 = Checkbutton(pop, text="Roller Pressure", font=("bold", 10), variable=mRP, state="disabled")
        m3.place(x=270, y=y_start)
        mRP.set(1)

        m4 = Checkbutton(pop, text="Gap Polarisation", font=("bold", 10), variable=mTG, state="disabled")
        m4.place(x=270, y=y_start + y_incmt * 1)

        m5 = Checkbutton(pop, text="Spooling Tension", font=("bold", 10), variable=mST, state="disabled")
        m5.place(x=10, y=y_start + y_incmt * 1)

        m6 = Checkbutton(pop, text="Winding Speed", font=("bold", 10), variable=mWS, state="disabled")
        m6.place(x=150, y=y_start + y_incmt * 1)
        mWS.set(1)
        # -------------------------------------------- Not included in DNV/MGM requirements
        m7 = Checkbutton(pop, text="Laser Power", font=("bold", 10), variable=mLP, state="disabled")
        m7.place(x=400, y=y_start)

        m8 = Checkbutton(pop, text="Laser Angle", font=("bold", 10), variable=mLA, state="disabled")
        m8.place(x=400, y=y_start + y_incmt * 1)
        # ---------------------------------------------------------------------#
        # load variables directly from ini files --[TODO]
        sbutton = 'disabled'  # disable Save button on entry state
        cState = 'disabled'

        separatorU = ttk.Separator(pop, orient='horizontal')
        separatorU.place(relx=0.01, rely=0.53, relwidth=0.75, relheight=0.01)  # y=7.3

        # ---------------------------------------------------------------------#
        Label(pop, text='[Configure Quality Parameters]', font=("bold", 10)).place(x=10,
                                                                             y=(y_start + 5) + (y_incmt * 3))  # 320 | 7

        dnv_butt = Button(pop, text="DNV Key Parameters", wraplength=90, justify=CENTER, width=12,
                          height=3, font=("bold", 12), command=dnvConfigs, state=cState)
        dnv_butt.place(x=240, y=3 + y_start + y_incmt * 4)  # 350 | 8
        # --------------------------------------------------------------------------------------------#
        mgm_butt = Button(pop, text="MGM Key Parameters", wraplength=90, justify=CENTER, width=12,
                              height=3, font=("bold", 12), command=mgmConfigs, state=cState)
        mgm_butt.place(x=380, y=3 + y_start + y_incmt * 4)  # 350 | 8
        # --------------------------------------------------------------------------------------------#

        p1 = Checkbutton(pop, text="DNV Quality Limits", font=("bold", 10), variable=pLmtA, command=enDNV)
        p1.place(x=10, y=3 + y_start + y_incmt * 4)         # 353

        p2 = Checkbutton(pop, text="Shewhart's Limits", font=("bold", 10), variable=shewhart, command=enAUTO)
        p2.place(x=10, y=y_start + y_incmt * 5)             # 373 | 9
        shewhart.set(1)

        p3 = Checkbutton(pop, text="Commercial Limits", font=("bold", 10), variable=pLmtB, command=enMGM)
        p3.place(x=10, y=y_start + y_incmt * 6)             # 393 |10

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
        # sSize, gType, sStart, sStops, OT, CT, RP, LA, WS, TG, ST, LP = mp.decryptMetricspP(WON)

        # Set default values - Break down each element and show to users
        gSize1.set('30')
        gSize2.set('GS-Discrete')  # Group Type (1=Domino, 2=SemiDomino, 3=Discrete)
        sSta.set('07:00:00 ')
        sEnd.set('01:00:00 ')

        # TODO ------------------------------------- [Include command=klr ] ---------------------------------------[]
        c1 = Checkbutton(pop, text="Historical Limits", font=("bold", 10), variable=hLmtA, command=runChecksPQ)
        c1.place(x=370, y=6)  # x=290, y=80, width=20,
        # ------------------

        if not metRO:
            # TODO --------------------------------------------------------[]

            e7 = ttk.Combobox(pop, width=10, values=[" Select Size", "10", "15", "20", "23", "25", "30"],
                              state="disabled")
            e7.bind("<<ComboboxSelected>>", display_sel)
            e7.current(0)           # set default choice
            e7.place(x=100, y=10)

            e8 = ttk.Combobox(pop, width=10, values=["SS-Domino", "GS-Discrete"], state="disabled")
            e8.bind("<<ComboboxSelected>>", display_selection)
            e8.current(0)           # set default choice to first index
            e8.place(x=100, y=40)
            # --------------------------------------------------- [Shift information]
            e5 = Entry(pop, width=8, textvariable=sSta, state="readonly")
            e5.place(x=290, y=10)
            e6 = Entry(pop, width=8, textvariable=sEnd, state="readonly")
            e6.place(x=290, y=40)

            # # Add isolation button
            button2 = Button(pop, text="Edit Stats Properties", bg="red", fg="white", state="disabled", command=clearMetrics)
            button2.place(x=370, y=35)  # place(x=520, y=47)

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

        # ------------------------------ # TODO ---- command=saveMetricRP)
        s_butt = Button(pop, text="Save Config Details", fg="black", state=sbutton, command=save_pMetrics)
        s_butt.place(x=385, y=5 + y_start + y_incmt * 2)  # 295 now 2
        # --------------------------------
        button5 = Button(pop, text="Exit Configuration", command=pop.destroy)
        button5.place(x=391, y=22 + y_start + y_incmt * 6)  # 400 nowe 2
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
    #
    # def metricsConfig():
    #     global pop, metRO, xUCLa, xLCLa, xUCLb, xLCLb, xUCLc, xLCLc, sSta, sEnd, lPwr, lAng, eStat, optm1, optm2, e8,\
    #         xUCLd, xLCLd, XBarMa, SBarMa, XBarMb, SBarMb, XBarMc, SBarMc, XBarMd, SBarMd, hLmt, gSize1, gSize2, e7,\
    #         xUCLf, xLCLf, xUCLg, xLCLg, BarMf, SBarMf, BarMg, SBarMg, hoTens, dcLoad, dDispl, swA, swB, seRF, sdRF, \
    #         seTT, sdTT, seST, sdST, seTG, sdTG, seLP, sdLP, seLA, sdLA
    #
    #     # newLabel = '??'
    #     # modal = Toplevel(pop)
    #     pop = Toplevel(root)
    #     pop.wm_attributes('-topmost', True)
    #
    #     # Define and initialise essential popup variables -----------------------------------------
    #     xUCLa, xLCLa, sUCLa, sLCLa = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
    #     xUCLb, xLCLb, sUCLb, sLCLb = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
    #     xUCLc, xLCLc, sUCLc, sLCLc = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
    #     xUCLd, xLCLd, sUCLd, sLCLd = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
    #     # -----------------------------------------------
    #     xUCLf, xLCLf, sUCLf, sLCLf = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
    #     xUCLg, xLCLg, sUCLg, sLCLg = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
    #
    #     # --------------- Additional Prod Parameters ----
    #     seRF, sdRF, seTT, sdTT = IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop)
    #     seST, sdST, seTG, sdTG = IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop)
    #     seLP, sdLP, seLA, sdLA = IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop)
    #     hoTens, dcLoad, dDispl = IntVar(pop), IntVar(pop), IntVar(pop)
    #
    #     sSta, sEnd, gSize1, gSize2 = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
    #     lPwr, lAng, eStat, optm1, optm2 = IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop)
    #
    #     XBarMa, SBarMa, hLmt, Sample = StringVar(pop), StringVar(pop), IntVar(pop), StringVar(pop)
    #     XBarMb, SBarMb, XBarMc, SBarMc = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
    #     XBarMd, SBarMd = StringVar(pop), StringVar(pop)
    #     XBarMf, SBarMf, XBarMg, SBarMg = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
    #     print('State:', sqlRO)
    #
    #     # global pop, screen_h, screen_w, x_c, y_c
    #     # center object on the screen---
    #     pop.resizable(False, False)
    #     w, h = 660, 420
    #     pop.title('Setting Chart Parameters')
    #     screen_w = pop.winfo_screenwidth()
    #     screen_h = pop.winfo_screenheight()
    #     x_c = int((screen_w / 2) - (w / 2))
    #     y_c = int((screen_h / 2) - (h / 2))
    #     pop.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))
    #
    #     # creating labels and positioning them on the grid --------[]
    #     Label(pop, text='Size').place(x=10, y=50)
    #     Label(pop, text='Type').place(x=133, y=50)
    #     Label(pop, text='Shift @').place(x=278, y=50)
    #     Label(pop, text='Ends @').place(x=400, y=50)
    #
    #     # --------------------------------------------------------[]
    #     separatorU = ttk.Separator(pop, orient='horizontal')
    #     separatorU.place(relx=0.01, rely=0.230, relwidth=0.30, relheight=0.01)
    #     separatorLR = ttk.Separator(pop, orient='horizontal')
    #     separatorLR.place(relx=0.60, rely=0.230, relwidth=0.39, relheight=0.01)
    #
    #     Label(pop, text='Historical Limits [Quality Parameters]', font=("bold", 10)).place(x=160, y=80)
    #     Label(pop, text='Distribution').place(x=550, y=80)
    #     # Obtain historical limits of respective processes from User #
    #
    #     # ----------------------------------------[Roller Force]
    #     Label(pop, text='UCL-RF').place(x=10, y=110)
    #     Label(pop, text='LCL-RF').place(x=138, y=110)
    #
    #     Label(pop, text='X\u033FLine :').place(x=278, y=110)
    #     Label(pop, text='S\u0305Line :').place(x=400, y=110)
    #
    #     # ----------------------------------------[Tape Temp]
    #     Label(pop, text='UCL-TT').place(x=10, y=140)
    #     Label(pop, text='LCL-TT').place(x=138, y=140)
    #     Label(pop, text='X\u033FLine :').place(x=278, y=140)
    #     Label(pop, text='S\u0305Line :').place(x=400, y=140)
    #
    #     # -----------------------------------------[Temp Delta]
    #     Label(pop, text='UCL-DT').place(x=10, y=170)
    #     Label(pop, text='LCL-DT').place(x=138, y=170)
    #     Label(pop, text='X\u033FLine :').place(x=278, y=170)
    #     Label(pop, text='S\u0305Line :').place(x=400, y=170)
    #
    #     # -----------------------------------------[Tape Gap]
    #     Label(pop, text='UCL-TG').place(x=10, y=200)
    #     Label(pop, text='LCL-TG').place(x=138, y=200)
    #     Label(pop, text='X\u033FLine :').place(x=278, y=200)
    #     Label(pop, text='S\u0305Line :').place(x=400, y=200)
    #
    #     # ------------------------------------[Multiple options: Laser Power (M)]
    #     def swA():
    #         global newLabelA
    #         if lPwr.get():
    #             newLabelA = 'LP'
    #             print('Laser Power Selected..')
    #         elif hoTens.get():
    #             newLabelA = 'HT'
    #             print('H/O Tension Selected..')
    #         else:
    #             newLabelA = '???'
    #         Label(pop, text='UCL-' + newLabelA).place(x=10, y=290)
    #         Label(pop, text='LCL-' + newLabelA).place(x=138, y=290)
    #     Label(pop, text='UCL-???').place(x=10, y=290)        # GUI Illusion
    #     Label(pop, text='LCL-???').place(x=138, y=290)       # GUI Illusion
    #     Label(pop, text='X\u033FLine :').place(x=278, y=290)
    #     Label(pop, text='S\u0305Line :').place(x=400, y=290)
    #
    #     # ------------------------------------[Laser Angle (M)]
    #     def swB():
    #         global newLabelB
    #         if lAng.get():
    #             newLabelB = 'LA'
    #             print('Laser Angle Selected..')
    #         elif dcLoad.get():
    #             newLabelB = 'DL'
    #             print('Dancer Load Selected..')
    #         elif dDispl.get():
    #             newLabelB = 'DD'
    #             print('Dancer Displacement Selected..')
    #         else:
    #             newLabelB = '???'
    #         Label(pop, text='UCL-' + newLabelB).place(x=10, y=320)
    #         Label(pop, text='LCL-' + newLabelB).place(x=138, y=320)
    #     Label(pop, text='UCL-???').place(x=10, y=320)        # GUI Illusion
    #     Label(pop, text='LCL-???').place(x=138, y=320)       # GUI Illusion
    #     Label(pop, text='X\u033FLine :').place(x=278, y=320)
    #     Label(pop, text='S\u0305Line :').place(x=400, y=320)
    #
    #     # set initial variables or last known variables
    #     # Set default values --------------------------
    #     XBarMa.set('350.0')         # 352.1102
    #     SBarMa.set('17.50')         # 22.4268
    #     XBarMb.set('350.0')         # 352.1102
    #     SBarMb.set('17.50')         # 22.4268
    #     XBarMc.set('350.0')         # 352.1102
    #     SBarMc.set('17.50')         # 22.4268
    #     XBarMd.set('350.0')         # 352.1102
    #     SBarMd.set('17.50')         # 22.4268
    #     XBarMf.set('350.0')         # 352.1102
    #     SBarMf.set('17.50')         # 22.4268
    #     XBarMg.set('350.0')         # 352.1102
    #     SBarMg.set('17.50')         # 22.4268
    #
    #     xUCLa.set('361.90')         # 364.6894
    #     xLCLa.set('338.10')         # 343.0816
    #     xUCLb.set('361.90')         # 364.6894
    #     xLCLb.set('338.10')         # 343.0816
    #     xUCLc.set('361.90')         # 364.6894
    #     xLCLc.set('338.10')         # 343.0816
    #     xUCLd.set('361.90')         # 364.6894
    #     xLCLd.set('338.10')         # 343.0816
    #     xUCLf.set('361.90')         # 364.6894
    #     xLCLf.set('338.10')         # 343.0816
    #     xUCLg.set('361.90')         # 364.6894
    #     xLCLg.set('338.10')         # 343.0816
    #
    #     sUCLa.set('0')
    #     sLCLa.set('0')
    #     sUCLb.set('0')
    #     sLCLb.set('0')
    #     sUCLc.set('0')
    #     sLCLc.set('0')
    #     sUCLd.set('0')
    #     sLCLd.set('0')
    #     sUCLf.set('0')
    #     sLCLf.set('0')
    #     sUCLg.set('0')
    #     sLCLg.set('0')
    #
    #     sSta.set('07:00:00')
    #     sEnd.set('17:00:00')
    #     gSize1.set('20')            # Group Size
    #     gSize2.set('03')            # Group Type (1=Domino, 2=SemiDomino, 3=Discrete)
    #     lPwr.set(0)
    #     hLmt.set(0)
    #     optm1.set(1)
    #     optm2.set(0)
    #
    #     # Set default distribution for each listed Process ------[]
    #     sdRF.set(1)                 # 343.0816
    #     sdTT.set(1)
    #     sdST.set(1)
    #     sdTG.set(1)
    #     sdLP.set(1)
    #     sdLA.set(1)
    #
    #     # ------------------------------------------------------
    #     separatorL = ttk.Separator(pop, orient='horizontal')
    #     separatorL.place(relx=0.01, rely=0.590, relwidth=0.39, relheight=0.01)
    #     separatorR = ttk.Separator(pop, orient='horizontal')
    #     separatorR.place(relx=0.60, rely=0.590, relwidth=0.39, relheight=0.01)
    #
    #     Label(pop, text='Critical Production Parameters', font=("bold", 10)).place(x=240, y=230)
    #     Checkbutton(pop, text="Laser Power", variable=lPwr, command=monitorA).place(x=25, y=255)
    #     Checkbutton(pop, text="Laser Angle", variable=lAng, command=monitorB).place(x=125, y=255)
    #     # ------------------------------------------------------
    #     Checkbutton(pop, text="H/O Tension", variable=hoTens, command=monitorC).place(x=225, y=255)
    #     Checkbutton(pop, text="Dancer Load", variable=dcLoad, command=monitorD).place(x=325, y=255)
    #     Checkbutton(pop, text="Displacement", variable=dDispl, command=monitorE).place(x=425, y=255)
    #     # ------------------------------------------------------
    #     Checkbutton(pop, text="Enable Stats", variable=eStat, command=enableStats).place(x=525, y=255)
    #
    #     c1 = Checkbutton(pop, text="Enable Historical Limits", width=20, font=("bold", 12), variable=hLmt, command=klr)
    #     c1.place(x=15, y=8)
    #     # ------------------
    #     c2 = Checkbutton(pop, text='Enable Automatic Limits', width=20, font=("bold", 12), variable=optm1, command=en_button)
    #     c2.place(x=230, y=8)
    #     # ------------------
    #     c2 = Checkbutton(pop, text='Enable Failover', width=20, font=("bold", 12), variable=optm2, command=en_limits)
    #     c2.place(x=430, y=8)
    #
    #     if not metRO:
    #         # TODO --------------------------------------------------------[]
    #
    #         e7 = ttk.Combobox(pop, width=8, values=[" Select", "10", "15", "20", "23", "25", "30"], state="disabled")
    #         e7.bind("<<ComboboxSelected>>", display_sel)
    #         e7.current(0)  # set default choice
    #         e7.place(x=40, y=50)
    #
    #         e8 = ttk.Combobox(pop, width=10, values=["SS-Domino", "GS-Discrete"], state="disabled")
    #         e8.bind("<<ComboboxSelected>>", display_selection)
    #         e8.current(0)  # set default choice to first index
    #         e8.place(x=172, y=50)
    #         # --------------------------------------------------- [Shift information]
    #         e5 = Entry(pop, width=8, textvariable=sSta, state="readonly")
    #         e5.place(x=325, y=50)
    #         e6 = Entry(pop, width=8, textvariable=sEnd, state="readonly")
    #         e6.place(x=450, y=50)
    #         # Add isolation button
    #         button2 = Button(pop, text="Amend Properties", command=clearMetrics, bg="red", fg="white")
    #         button2.place(x=520, y=47)
    #
    #         # Declare variable arrays ----------------------------[Roller Force]
    #         a1a = Entry(pop, width=8, textvariable=xUCLa, state="readonly")
    #         a1a.place(x=65, y=110)
    #         a2a = Entry(pop, width=8, textvariable=xLCLa, state="readonly")
    #         a2a.place(x=190, y=110)
    #
    #         a3a = Entry(pop, width=8, textvariable=XBarMa, state="readonly")
    #         a3a.place(x=325, y=110)
    #         a4a = Entry(pop, width=8, textvariable=SBarMa, state="readonly")
    #         a4a.place(x=447, y=110)
    #         Checkbutton(pop, text="SE", variable=seRF, command=cseRF).place(x=550, y=110)  # cstat, UseSE
    #         Checkbutton(pop, text="SD", variable=sdRF, command=csdRF).place(x=600, y=110)
    #
    #         # ------------- DNV Requirements ----------------[Tape Temperature]
    #         b1b = Entry(pop, width=8, textvariable=xUCLb, state="readonly")
    #         b1b.place(x=65, y=140)
    #         b2b = Entry(pop, width=8, textvariable=xLCLb, state="readonly")
    #         b2b.place(x=190, y=140)
    #
    #         b3b = Entry(pop, width=8, textvariable=XBarMb, state="readonly")
    #         b3b.place(x=325, y=140)
    #         b4b = Entry(pop, width=8, textvariable=SBarMb, state="readonly")
    #         b4b.place(x=447, y=140)
    #         Checkbutton(pop, text="SE", variable=seTT, command=cseTT).place(x=550, y=140)  # cstat, UseSE
    #         Checkbutton(pop, text="SD", variable=sdTT, command=csdTT).place(x=600, y=140)
    #
    #         # ------------ DNV Requirements ---------------[Temperature Substrate]
    #         c1b = Entry(pop, width=8, textvariable=xUCLc, state="readonly")
    #         c1b.place(x=65, y=170)
    #         c2b = Entry(pop, width=8, textvariable=xLCLc, state="readonly")
    #         c2b.place(x=190, y=170)
    #         c3b = Entry(pop, width=8, textvariable=XBarMc, state="readonly")
    #         c3b.place(x=325, y=170)
    #         c4b = Entry(pop, width=8, textvariable=SBarMc, state="readonly")
    #         c4b.place(x=447, y=170)
    #         Checkbutton(pop, text="SE", variable=seST, command=cseST).place(x=550, y=170)  # cstat, UseSE
    #         Checkbutton(pop, text="SD", variable=sdST, command=csdST).place(x=600, y=170)
    #
    #         # -----------------------------------------[Tape Gap Measurement]
    #         a1b = Entry(pop, width=8, textvariable=xUCLd, state="readonly")
    #         a1b.place(x=65, y=200)
    #         a2b = Entry(pop, width=8, textvariable=xLCLd, state="readonly")
    #         a2b.place(x=190, y=200)
    #         a3b = Entry(pop, width=8, textvariable=XBarMd, state="readonly")
    #         a3b.place(x=325, y=200)
    #         a4b = Entry(pop, width=8, textvariable=SBarMd, state="readonly")
    #         a4b.place(x=447, y=200)
    #         Checkbutton(pop, text="SE", variable=seTG, command=cseTG).place(x=550, y=200)  # cstat, UseSE
    #         Checkbutton(pop, text="LN", variable=sdTG, command=csdTG).place(x=600, y=200)
    #
    #         # -----------------------------------------[Laser Power (Monitor)]
    #         a1d = Entry(pop, width=8, textvariable=xUCLf, state="readonly")
    #         a1d.place(x=65, y=290)
    #         a2d = Entry(pop, width=8, textvariable=xLCLf, state="readonly")
    #         a2d.place(x=190, y=290)
    #         a3d = Entry(pop, width=8, textvariable=XBarMf, state="readonly")
    #         a3d.place(x=325, y=290)
    #         a4d = Entry(pop, width=8, textvariable=SBarMf, state="readonly")
    #         a4d.place(x=447, y=290)
    #         Checkbutton(pop, text="SE", variable=seLP, command=cseLP).place(x=550, y=290)  # cstat, UseSE
    #         Checkbutton(pop, text="SD", variable=sdLP, command=csdLP).place(x=600, y=290)
    #
    #         # --------------------------------------[Laser Angle Measurement]
    #         a1d = Entry(pop, width=8, textvariable=xUCLg, state="readonly")
    #         a1d.place(x=65, y=320)
    #         a2d = Entry(pop, width=8, textvariable=xLCLg, state="readonly")
    #         a2d.place(x=190, y=320)
    #         a3d = Entry(pop, width=8, textvariable=XBarMg, state="readonly")
    #         a3d.place(x=325, y=320)
    #         a4d = Entry(pop, width=8, textvariable=SBarMg, state="readonly")
    #         a4d.place(x=447, y=320)
    #         Checkbutton(pop, text="SE", variable=seLA, command=cseLA).place(x=550, y=320)  # cstat, UseSE
    #         Checkbutton(pop, text="SD", variable=sdLA, command=csdLA).place(x=600, y=320)
    #
    #     else:
    #         e7 = ttk.Combobox(pop, width=8, values=[" Select", "10", "15", "20", "23", "25", "25"], state="normal")
    #         e7.bind("<<ComboboxSelected>>", display_sel)
    #         e7.current(0)  # set default choice
    #         e7.place(x=40, y=50)
    #
    #         e8 = ttk.Combobox(pop, width=10, values=["SS-Domino", "GS-Discrete"], state="normal")
    #         e8.bind("<<ComboboxSelected>>", display_selection)
    #         e8.current(0)  # set default choice to first index
    #         e8.place(x=172, y=50)
    #         # -------------------------------------------------[ Shift duration ]
    #         e5 = Entry(pop, width=8, textvariable=sSta, state="normal")
    #         e5.place(x=325, y=50)
    #         e6 = Entry(pop, width=8, textvariable=sEnd, state="normal")
    #         e6.place(x=450, y=50)
    #
    #         # Declare variable arrays -------------------------[Roller Force]
    #         a1a = Entry(pop, width=8, textvariable=xUCLa, state="normal")
    #         a1a.place(x=65, y=110)
    #         a2a = Entry(pop, width=8, textvariable=xLCLa, state="normal")
    #         a2a.place(x=190, y=110)
    #         a3a = Entry(pop, width=8, textvariable=XBarMa, state="normal")
    #         a3a.place(x=325, y=110)
    #         a4a = Entry(pop, width=8, textvariable=SBarMa, state="normal")
    #         a4a.place(x=447, y=110)
    #
    #         # ------------- DNV Requirements -------------[Tape Temperature]
    #         b1b = Entry(pop, width=8, textvariable=xUCLb, state="normal")
    #         b1b.place(x=65, y=140)
    #         b2b = Entry(pop, width=8, textvariable=xLCLb, state="normal")
    #         b2b.place(x=190, y=140)
    #         b3b = Entry(pop, width=8, textvariable=XBarMb, state="normal")
    #         b3b.place(x=325, y=140)
    #         b4b = Entry(pop, width=8, textvariable=SBarMb, state="normal")
    #         b4b.place(x=447, y=140)
    #         # ------------ DNV Requirements -------------[Delta Temperature]
    #         c1b = Entry(pop, width=8, textvariable=xUCLc, state="normal")
    #         c1b.place(x=65, y=170)
    #         c2b = Entry(pop, width=8, textvariable=xLCLc, state="normal")
    #         c2b.place(x=190, y=170)
    #         c3b = Entry(pop, width=8, textvariable=XBarMc, state="normal")
    #         c3b.place(x=325, y=170)
    #         c4b = Entry(pop, width=8, textvariable=SBarMc, state="normal")
    #         c4b.place(x=447, y=170)
    #         # ---------------------------------------[Tape Gap Measurements]
    #         a1b = Entry(pop, width=8, textvariable=xUCLd, state="normal")
    #         a1b.place(x=65, y=200)
    #         a2b = Entry(pop, width=8, textvariable=xLCLd, state="normal")
    #         a2b.place(x=190, y=200)
    #         a3b = Entry(pop, width=8, textvariable=XBarMd, state="normal")
    #         a3b.place(x=325, y=200)
    #         a4b = Entry(pop, width=8, textvariable=SBarMd, state="normal")
    #         a4b.place(x=447, y=200)
    #
    #         # ------------------------------------[Laser Power (Monitoring)]
    #         a1d = Entry(pop, width=8, textvariable=xUCLf, state="normal")
    #         a1d.place(x=65, y=290)
    #         a2d = Entry(pop, width=8, textvariable=xLCLf, state="normal")
    #         a2d.place(x=190, y=290)
    #         a3d = Entry(pop, width=8, textvariable=XBarMf, state="normal")
    #         a3d.place(x=325, y=290)
    #         a4d = Entry(pop, width=8, textvariable=SBarMf, state="normal")
    #         a4d.place(x=447, y=290)
    #         # -----------------------------------[Laser Angle (Monitoring)]
    #         a1d = Entry(pop, width=8, textvariable=xUCLg, state="normal")
    #         a1d.place(x=65, y=320)
    #         a2d = Entry(pop, width=8, textvariable=xLCLg, state="normal")
    #         a2d.place(x=190, y=320)
    #         a3d = Entry(pop, width=8, textvariable=XBarMg, state="normal")
    #         a3d.place(x=325, y=320)
    #         a4d = Entry(pop, width=8, textvariable=SBarMg, state="normal")
    #         a4d.place(x=447, y=320)
    #
    #     # Add Button for making selection -------------------------------
    #     button1 = Button(pop, text="Save All Settings", command=saveMetric, bg="green", fg="white")
    #     button1.place(x=280, y=370)

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
            e4 = Entry(pop, textvariable=autho, state='readonly')   #, show="*")
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
                conn = 'true'
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
                hostConnect()                                          # acknowledgement
                conn = 'true'
            else:
                pingError()                                            # Ping error failed -------
                conn = 'none'

        except Exception as err:
            errorLog(f"{err}")
            errorNoServer()                                            # errorNoServer()
            conn = 'none'

        return conn

    def sCloseConnSQL():
        global conn
        # ------------------------------------------------------------------ Start
        import CommsSql as mCon
        conn = mCon.DAQ_connect(1, 0)  # 1 = connection is active to be .closed()
        if conn == 'true':
            conn.close()
            print('SQL Data is disconnected')
        else:
            conn = 'none'
            print('No active connections!')
            errorNoconnect()
        return conn

    # ---------------------------------------------------------------------------[]

    def sCloseConnPLC():
        global conn
        # plc_stop() - beware not to halt PLC
        # ------------------------------------------------------------------ Start
        import CommsPlc as mCon
        conn_active = mCon.disconnct_PLC()                    # TODO: Check PLC server link
        if conn_active == 'true':
            print('Host PLC is disconnected')
        else:
            print('No active connections!')
            conn_active = 'false'

        return conn_active

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
        # Declare global variable available to all processes
        global stpd, WON, processID, OEEdataID, hostConn

        if process.entrycget(0, 'state') == 'disabled' or process.entrycget(1, 'state') == 'disabled':
            import CommsSql as hs

            # import signal
            # os.kill(sid, signal.SIGTERM)
            if (analysis.entrycget(0, 'state') == 'normal'
                    and analysis.entrycget(1, 'state') == 'normal'
                    and analysis.entrycget(3, 'state') == 'normal'):
                analysis.entryconfig(0, state='disabled')                             # turn command off

                # ----- Calling essential functions -----------[1]
                DATEentry, WONentry = retroUserSearchReq()                                  # Popup dialogue

                # ---------------------------------------------[2]
                print('Attempting connection with SQL Server...')
                hostConn = hs.DAQ_connect(0, 1)                                 # Connect to SQL Host

                if hostConn:
                    # -----------------------------------------[3]
                    OEEdataID, processID = sqld.searchSqlRecs(hostConn, DATEentry, WONentry)    # Query SQL record
                    # processID = processID +'RF'
                    qType = 2
                    runType.append(qType)
                else:
                    print('Connection to SQL Server failed. Please, check Server connection.')

            elif (analysis.entrycget(3, 'state') == 'disabled'
                  and analysis.entrycget(0, 'state') == 'normal'):
                analysis.entryconfig(3, state='normal')
                analysis.entryconfig(0, state='disabled')

                # ----- Calling essential functions ----------#
                DATEentry, WONentry = retroUserSearchReq()                                 # Search for Production data
                hostConn = hs.DAQ_connect(0, 1)                                # Connect to SQL Host
                print('Connecting to SQL Server...')

                if hostConn:
                    # connect SQL Server and obtain Process ID ----#
                    OEEdataID, processID = sqld.searchSqlRecs(hostConn, DATEentry, WONentry)    # Query SQL record
                    # ---------------------------------------------[]
                    qType = 2
                    runType.append(qType)
                else:
                    print('Connection to SQL Server failed. Please, check Server connection.')

            else:
                runtimeChange()
                qType = 0
                runType.append(qType)
                print('Invalid SQL Query connection...')

        else:
            print('Invalid selection. Please, enable a visualisation mode')

        # return # stpd, WON, processID, OEEdataID, qType, hostConn

    def realTimePlay():
        import CommsPlc as hp

        if process.entrycget(0, 'state') == 'disabled' or process.entrycget(1, 'state') == 'disabled':
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
        else:
            print('Invalid selection. Please, enable a visualisation mode')

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
        global p1, p2, p3, p4, p5, p6, p7, HeadA, rType                 # declare as global variables

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
                tabbed_cascadeMode()                                      # Default limited tabbed common screen
                print('\nStarting new GPU thread...')
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
            # cascadeViews()                                              # Critical Production Params
            tabbed_cascadeMode()                                          # Default limited tabbed common screen + Casc
            exit_bit.append(1)
            HeadA, HeadB, closeV = 1, 0, 0

        elif (process.entrycget(0, 'state') == 'normal'
              and process.entrycget(1, 'state') == 'normal'
              and process.entrycget(3, 'state') == 'normal'):
            process.entryconfig(0, state='disabled')
            process.entryconfig(1, state='normal')
            process.entryconfig(3, state='normal')

            # --- start parallel thread --------------------------------#
            # cascadeViews()                                            # Critical Production Params
            tabbed_cascadeMode()                                        # Provide limited Tabb and multiple screen
            exit_bit.append(1)
            HeadA, HeadB, closeV = 1, 0, 0

        else:
            process.entryconfig(0, state='normal')
            HeadA, HeadB, closeV = 0, 0, 1
            errorChoice()                               # pop up error
            print('Invalid! View selection before process parameter..')

        return HeadA, HeadB, closeV

    def viewTypeB():        # Tabbed View (This is configured for remote users)
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
                casc_clearOut()                                           # clear out visualisation frame
                tabbed_canvas()                                           # Call Canvas binding function
                exit_bit.append(0)                                        # Keep a byte into empty list
            else:
                process.entryconfig(0, state='disabled')            # revert to original state
                process.entryconfig(1, state='normal')              # revert to original state

            HeadA, HeadB, closeV = 0, 1, 0                                # call embedded functions

        elif process.entrycget(3, 'state') == 'disabled':
            process.entryconfig(1, state='disabled')
            process.entryconfig(0, state='normal')
            process.entryconfig(3, state='normal')

            tabbed_canvas()                                                 # Tabbed Visualisation
            exit_bit.append(0)

            HeadA, HeadB, closeV = 0, 1, 0                                  # call embedded functions

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

        if inUse == 9:
            # root.winfo_children()[9].destroy()
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
        inUse = len(root.winfo_children())
        # -------------
        print('\n******************************')
        print('Whats in Use', inUse)
        print('Get PPID', os.getppid())                         # Parent ID 37248
        print('Get PID', os.getpid())                           # Child ID 52692
        print('Get CWDB', os.getcwdb())                         # b'C:\\CuttingEdge\\BETA_ver3.6'
        print('Get CWD', os.getcwd())                           # C:\CuttingEdge\BETA_ver3.6
        print('Get INDENT', get_ident())                        # 32356
        print('Get Native ID', get_native_id())                 # 32356
        print('Current Thread Name', current_thread().name)     # MainThread
        print('Current Thread Ident', current_thread().ident)   # Current Thread 32356

        try:
            if pRecipe == 'DNV':
                kill_process(p3.pid)
                kill_process(p2.pid)
                kill_process(p1.pid)
            else:
                kill_process(p7.pid)  # convert process into pid number
                kill_process(p6.pid)
                kill_process(p5.pid)                                  # convert process into pid number
                kill_process(p4.pid)
                kill_process(p3.pid)
                kill_process(p2.pid)
                kill_process(p1.pid)
        except OSError:
            print(f'Process {p7} failed to terminate!')
            print(f'Process {p6} failed to terminate!')
            print(f'Process {p5} failed to terminate!')
            print(f'Process {p4} failed to terminate!')
            print(f'Process {p3} failed to terminate!')
            print(f'Process {p2} failed to terminate!')
            print(f'Process {p1} failed to terminate!')
        # clear out all children process --[]
        if pRecipe == 'DNV':
            root.winfo_children()[3].destroy()
            root.winfo_children()[2].destroy()
            root.winfo_children()[1].destroy()
        else:
            root.winfo_children()[7].destroy()
            root.winfo_children()[6].destroy()
            root.winfo_children()[5].destroy()
            root.winfo_children()[4].destroy()
            root.winfo_children()[3].destroy()
            root.winfo_children()[2].destroy()
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

    # Process Menu ----------------------------------------[]
    process = Menu(menubar, tearoff=0)
    process.add_command(label="Cascade Views", command=viewTypeA)
    process.add_command(label="Tabbed Views", command=viewTypeB)
    process.add_separator()
    process.add_command(label="Close Display", command=closeViews)
    menubar.add_cascade(label="Visualisation", menu=process)

    # Analysis Menu -----------------------------------------[]
    analysis = Menu(menubar, tearoff=0)
    analysis.add_command(label="Post Production", command=retroPlay)
    analysis.add_command(label="Synchronous SPC", command=realTimePlay)
    analysis.add_separator()
    analysis.add_command(label="Stop SPC Process", command=stopSPCrun)
    menubar.add_cascade(label="Runtime Mode", menu=analysis)

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
