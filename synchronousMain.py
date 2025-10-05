# --------------------------------------------------------------------------#
# Author: Dr RB Labs
# Developed for Magma Global - TechnipFMC Industrialization
# Email: robbielabs@uwl.ac.uk
# Copyright (C) 2023-2025, Robbie Labs
#
# -------------------- Primary User Graphic Interface ----------------------#

# from cgitb import reset
import pandas as pd
import deltaM2_Functions as wd
import ctypes

# ----- PLC/SQL Query ---#
import selDataColsGEN as gv     # General Table
import selDataCols_EV as qev    # Environmental Values
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

# ------------------------------#
import selDataColsEoLLP as olp  # EoL Laser Power (on DNV)
import selDataColsEoLLA as ola  # EoL Laser Angle (on DNV)
# import selDataColsEoLRP as orp# EoL Roller Pressure (on MGM)

# ------------------------------#
import selDataColsEoLTT as ott  # EoL Tape Temperature (Control Temperature)
import selDataColsEoLST as ost  # EoL Substrate Temperature (on DNV)
import selDataColsEoLTG as otg  # EoL Tape Gape (on DNV)
import selDataColsEoLWS as ows  # EoL Winding Speed (on DNV)
import selDataColsEoLWA as owa  # EoL Winding Angle (on MGM)
import sqlArrayRLmethodEoL as pdfrp

# ----- DNV/MGM Params ---#
import selDataColsPM as qpm        # Production Monitors
import selDataColsWA as qwa        # winding angle
# import selDataColsOE as qoe      # OEE TechnipFMC

# -------------------------#
# import GPUtil as gp
# import screeninfo as m
from random import randint
import threading

from fpdf import FPDF
import time
import os
import sys
import math
from datetime import datetime, date
from time import gmtime, strftime
from pynput.keyboard import Key, Listener
import signal
import triggerModule as gma
import tkinter as tk
from tkinter import *
from threading import *
from multiprocessing import Process
from tkinter import messagebox, ttk
from tkinter.simpledialog import askstring
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# from CascadeSwitcher import pRecipe

LARGE_FONT = ("Verdana", 10, 'bold')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import loadSPCConfig as ty
import rtP_Evaluator as tq
import ProcessCapPerf as tz
from pydub import AudioSegment
from matplotlib.animation import FuncAnimation
from mpl_interactions import ioff, zoom_factory, panhandler
import keyboard  # for temporary use
from matplotlib.ticker import MultipleLocator
# --------------------------[]
import pParamsHL as dd
import pWON_finder as wo

# -------------------------[]
import qParametersDNV as hla
import qParametersMGM as hlb
import Screen_Calibration as cal
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import fitz
from tkinter import filedialog
from tkinter import simpledialog
import CommsSql as sq


# ------------------------[]
# # Try GPU (CuPy), else fall back to NumPy
# try:
#     import cupy as np
#     GPU_ENABLED = True
# except ImportError:
#     import numpy as np
#     GPU_ENABLED = False
# # make numpy compatible with cupy API
# np.asnumpy = lambda x: x
import warnings
import subprocess
import json
import shutil

def get_nvidia_info():
    """Return GPU info (name, memory, utilization, temperature) if available."""
    if not shutil.which("nvidia-smi"):
        return None

    try:
        query = "--query-gpu=name,memory.total,memory.used,utilization.gpu,temperature.gpu --format=csv,noheader,nounits"
        result = subprocess.run(["nvidia-smi"] + query.split(), capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")
        if not lines:
            return None
        fields = lines[0].split(", ")
        return {
            "name": fields[0],
            "mem_total": float(fields[1]),
            "mem_used": float(fields[2]),
            "utilization": float(fields[3]),
            "temp": float(fields[4]),
        }
    except Exception:
        return None

try:
    import cupy as cp
    import numpy as np
    GPU_ENABLED = False

    try:
        num_gpus = cp.cuda.runtime.getDeviceCount()
        if num_gpus > 0:
            gpu_info = get_nvidia_info()
            free_mem, total_mem = cp.cuda.runtime.memGetInfo()
            free_gb = free_mem / 1e9
            total_gb = total_mem / 1e9
            used_pct = (1 - free_mem / total_mem) * 100

            if free_mem / total_mem > 0.1:
                np = cp
                GPU_ENABLED = True
                print(f"✅ Using GPU (CuPy)")
                if gpu_info:
                    print(f"   GPU: {gpu_info['name']}")
                    print(f"   Temp: {gpu_info['temp']}°C | Utilization: {gpu_info['utilization']}%")
                    print(f"   Memory: {gpu_info['mem_used'] / 1024:.2f} / {gpu_info['mem_total'] / 1024:.2f} GB")
                else:
                    print(f"   Free: {free_gb:.2f} / {total_gb:.2f} GB  ({used_pct:.1f}% used)")
            else:
                warnings.warn(f"⚠️ GPU memory too low ({free_gb:.2f} GB free). Falling back to CPU (NumPy).")
        else:
            warnings.warn("⚠️ No CUDA GPUs found. Using CPU (NumPy).")

    except cp.cuda.runtime.CUDARuntimeError:
        warnings.warn("⚠️ CUDA runtime error. Using CPU (NumPy).")

except ImportError:
    import numpy as np

    GPU_ENABLED = False
    warnings.warn("⚠️ CuPy not installed. Using CPU (NumPy).")

# --- Make np.asnumpy safe for both backends ---
if not hasattr(np, "asnumpy"):
    np.asnumpy = lambda x: x

# ------------------------[]
# Cross-platform simple beep
def beep():
    try:
        if sys.platform.startswith("win"):
            import winsound
            winsound.Beep(1000, 200)  # 1000 Hz for 200 ms
        else:
            os.system("printf '\\a'")  # Linux/macOS terminal bell
    except Exception:
        pass


# matplotlib.use("TkAgg")
# -------------------------[]

sptDat, valuDat, stdDat, tolDat, pgeDat, psData, r1Data, r2Data, r3Data, r4Data = [], [], [], [], [], [], [], [], [], []
sDat1, sDat2, sDat3, sDat4 = [], [], [], []
tabConfig, vppA, vpkA = [], [], []
cpTapeW, cpLayerNo, pType = [], [], []
OTlayr, EPpos, pStatus = [], [], []
HeadA, HeadB, vTFM = 0, 0, 0
hostConn = 0
runStatus = 0
qMarker_rpt = 0.1
sysrdy, sysRun, sysidl = 1, 0, 0
# -------------
gap_vol, ramp_vol = 0, 0
vCount, pExLayer, pLength = 1000, 70, 100
# Pipe Expected/Predicted final Layer
# --------------
optm = True
p_layer, pdf_layer = [], []
# initialise connections --#
gc_con = None
# tt_con = None  # process TT
pst_con = None  # Process ST
ptg_con = None
prm_con = None
pvm_con = None
# --------------------------
dataReady = []
Dtt_ready = []
Dts_ready = []
Dtg_ready = []
Drt_ready = []
Dtr_ready = []
Dol_ready = []
Dop_ready = []
# ---------------------

xpiPos = []
xcLayer = []

# ------------------------------------------#
# Storing the list of PLC data Block        #
#                                           #
# Load PLC DB address once -----------------#
SPC_LP = 112
SPC_LA = 210
SPC_TP = 215
SPC_RF = 71
SPC_TT = 152
SPC_ST = 153
SPC_TG = 208
SPC_EV = 213
SPC_GEN = 211
SPC_RC = 116
SPC_VC = 117
SPC_RM = 114
SCP_VM = 115
SPC_RP = 151
SPC_WS = 216    # not Tape speed
SPC_WA = 214
# ------------------------------------------#

import subprocess
try:
    subprocess.check_output('nvidia-smi')
    print('Nvidia GPU detected!')
except Exception:
    print('No Nvidia GPU in system!')

# -----[Detect attached Screen, Extract details to Set GUI Canvas ------[]
aSCR, scrW1, scrW2, scrW3, scrW4, scrW5, scrW6, scrW7, scrW8 = cal.getSCRdetails()

if scrW1 == 2560:   # Digital monitor
    scrW = 2535     # Set GUI Canvas size
    scrX = 8.5      # Set GUI Figure size
    pEvX = 860      # Environmental Values
    pTgX = 1700     # TapeGap Count
    pMtX = 25.5     # Canvas for Monitoring Tab

elif scrW1 == 3840: # Digital Screen/TV
    scrW = 3810     # Set GUI Canvas size
    scrX = 9        # Set GUI Figure size
    pEvX = 860      # Environmental Values
    pTgX = 1700     # TapeGap Count
    pMtX = 27       # Canvas for Monitoring Tab

else:               # Digital Screen # 4864
    print('Chosen.....')
    scrW = 2535     # Set GUI Canvas size
    scrX = 8.5      # Set GUI Figure size
    pEvX = 860      # Environmental Values
    pTgX = 1700     # TapeGap Count
    pMtX = 25.5     # Canvas for monitoring Tab

# ----------------------- Audible alert ---------------------------------[]
impath ='C:\\synchronousGPU\\Media\\'
EoL_Doc = 'C:\\synchronousDOCS\\'
path = 'C:\\synchronousDOCS\\BrandS\\testFile.csv'
saveState = 'C:\\crashRecovery\\'
# ----------------------------------------------
nudge = AudioSegment.from_wav(impath+'tada.wav')
error = AudioSegment.from_wav(impath+'error.wav')
csv_file = (path)
Testdf = pd.read_csv(csv_file)

# Define statistical operations ---------------[]
WeldQualityProcess = True
paused = False

url = 'http://www.magmaglobal.com'
localArray = []                                         # raising the bit for GUI canvas
exit_bit = []                                           # enable the close out of all cascade windows

# XBar Constants ------------------------------[]
A3 = [0.975, 0.789, 0.680, 0.6327, 0.606, 0.5525]       # 10, 15, 20, 23, 25, 30  sample sizes respectively
B3 = [0.284, 0.428, 0.510, 0.5452, 0.565, 0.6044]       # 10, 15, 20, 23, 25, 30  sample sizes respectively
B4 = [1.716, 1.572, 1.490, 1.4548, 1.435, 1.3956]       # 10, 15, 20, 23, 25, 30
# ----------------------------------------------[]

plcConnex = []
# UsePLC_DBS = False                                      # specify SQl Query or PLC DB Query is in use
# UseSQL_DBS = True
ql_alive = False
rm_alive = False

# ------------------ Auto canvass configs ------[]
y_start = 110
y_incmt = 30
rtValues = []

# ---- Common to all Process Procedures --------[]
def load_Stats_Params(pWON):
    global cDM, cSS, cGS, mLA, mLP, mCT, mOT, mRP, mWS, sStart, sStops, LP, LA, TP, RF, TT, ST, TG, pRecipe

    print('New PWON', pWON)
    # Call function and load WON specifications per Parameter -----[]
    if pWON == 'DEFAULT':
        cDM, cSS, cGS, mLA, mLP, mCT, mOT, mRP, mWS, sStart, sStops, LP, LA, TP, RF, TT, ST, TG = dd.decryptMetricsGeneral(
            pWON)
    else:
        cDM, cSS, cGS, mLA, mLP, mCT, mOT, mRP, mWS, sStart, sStops, LP, LA, TP, RF, TT, ST, TG = dd.decryptMetricsGeneral(pWON)

    if cGS == 'Smooth Edge Slide':
        cGS = 1
    elif cGS == 'Non-Overlapping':
        cGS = 2
    else:
        cGS = 0
    # ----------------------------------------------[A]
    if len(pWON) == 8 or int(TT) and int(ST) and int(TG) and not int(LP) and not int(LA):
        pRecipe = 'DNV'
        import qParamsHL_DNV as dnv
        print('Loading DNV default parameters...\n')

    elif len(pWON) >= 8 or int(LP) and int(LA) and int(TP) and int(RF) and int(TT) and int(ST) and int(TG):
        pRecipe = 'MGM'
        import qParamsHL_MGM as mgm
        print('Loading MGM default parameters...\n')

    else:
        pRecipe = 'UKN'
        print('Reverting to DNV default parameters...\n')
        # exit()
    print('\nActive Recipe:', pRecipe)
    # ----------------------------------------------[]
    return

def clear_DF():
    print('\nEmpty Dataframe:', rpData)
    rept = [r1Data, r2Data, r3Data, r4Data, sptDat, valuDat, stdDat, tolDat]
    # Clean up unsued variables to optimise memory usage ---------------------
    for i in range(len(rept)):
        if len(rept[i]) > 0:
            del rept[i][:]      # common variables
            del pgID[:]         # Page ID
            # del proID[:]        # process id
        else:
            pass
    # ----- Empty Data frame

def generate_pdf(rptID, cPipe, custm, usrID, layrN, ring1, ring2, ring3, ring4, SetPt, Value, Stdev, Tvalu, pgiD, sDat1, sDat2, sDat3, sDat4):
    global pgID, pdf_genA
    # --------------------------------------[]
    from pylab import title, xlabel, ylabel, savefig
    pdf_genA = True

    # Initialise dataframe from Tables -[]
    if rptID == 'EoL':
        rpID = 'QA Report (EoL) # ' + str(layrN)           # Report ID/Description
    else:
        rpID = 'QA Report (EoP) # ' + str(layrN)           # Report ID/Description
    # ----------------------------------#
    proj = custm                        # Project ID
    pID = cPipe                         # Pipe ID
    oID = usrID                         # User ID
    dID = datetime.now()                # Date ID
    pgID = pgiD                         # Page ID/Description
    lID = layrN                         # Layer ID
    # print('\nPage Identification:', pgID)
    # ----------------------------------[]
    for x in range(len(pgiD)):
        # ------------------------------[]
        if pRecipe == 'MGM':
            if x == 0:
                proID = 'Laser Power'
                rID = 'TT'  # report ID
                ringD1 = ring1[0]
                ringD2 = ring2[0]
                ringD3 = ring3[0]
                ringD4 = ring4[0]
                sPoint1 = SetPt[0]
                sPoint2 = SetPt[1]
                sPoint3 = SetPt[2]
                sPoint4 = SetPt[3]
                sValue1 = Value[0]
                sValue2 = Value[1]
                sValue3 = Value[2]
                sValue4 = Value[3]
                sStdev1 = Stdev[0]
                sStdev2 = Stdev[1]
                sStdev3 = Stdev[2]
                sStdev4 = Stdev[3]
                tolDat1 = Tvalu[0][0]
                tolDat2 = Tvalu[0][1]
                tolDat3 = Tvalu[0][2]
                tolDat4 = Tvalu[0][3]
            elif x == 1:
                proID = 'Laser Angle'
                rID = 'TT'  # report ID
                ringD1 = ring1[1]
                ringD2 = ring2[1]
                ringD3 = ring3[1]
                ringD4 = ring4[1]
                sPoint1 = SetPt[4]
                sPoint2 = SetPt[5]
                sPoint3 = SetPt[6]
                sPoint4 = SetPt[7]
                sValue1 = Value[4]
                sValue2 = Value[5]
                sValue3 = Value[6]
                sValue4 = Value[7]
                sStdev1 = Stdev[4]
                sStdev2 = Stdev[5]
                sStdev3 = Stdev[6]
                sStdev4 = Stdev[7]
                tolDat1 = Tvalu[1][0]
                tolDat2 = Tvalu[1][1]
                tolDat3 = Tvalu[1][2]
                tolDat4 = Tvalu[1][3]
            elif x == 2:
                proID = 'Tape Temperature'
                rID = 'TT'  # report ID
                ringD1 = ring1[2]
                ringD2 = ring2[2]
                ringD3 = ring3[2]
                ringD4 = ring4[2]
                sPoint1 = SetPt[8]
                sPoint2 = SetPt[9]
                sPoint3 = SetPt[10]
                sPoint4 = SetPt[11]
                sValue1 = Value[8]
                sValue2 = Value[9]
                sValue3 = Value[10]
                sValue4 = Value[11]
                sStdev1 = Stdev[8]
                sStdev2 = Stdev[9]
                sStdev3 = Stdev[10]
                sStdev4 = Stdev[11]
                tolDat1 = Tvalu[2][0]
                tolDat2 = Tvalu[2][1]
                tolDat3 = Tvalu[2][2]
                tolDat4 = Tvalu[2][3]
            elif x == 3:
                proID = 'Substrate Temperature'
                rID = 'ST'  # report ID
                ringD1 = ring1[3]
                ringD2 = ring2[3]
                ringD3 = ring3[3]
                ringD4 = ring4[3]
                sPoint1 = SetPt[12]
                sPoint2 = SetPt[13]
                sPoint3 = SetPt[14]
                sPoint4 = SetPt[15]
                sValue1 = Value[12]
                sValue2 = Value[13]
                sValue3 = Value[14]
                sValue4 = Value[15]
                sStdev1 = Stdev[12]
                sStdev2 = Stdev[13]
                sStdev3 = Stdev[14]
                sStdev4 = Stdev[15]
                tolDat1 = Tvalu[3][0]
                tolDat2 = Tvalu[3][1]
                tolDat3 = Tvalu[3][2]
                tolDat4 = Tvalu[3][3]
            elif x == 4:
                proID = 'Gap Measurement'
                rID = 'TG'
                ringD1 = ring1[4]
                ringD2 = ring2[4]
                ringD3 = ring3[4]
                ringD4 = ring4[4]
                sPoint1 = SetPt[16]
                sPoint2 = SetPt[17]
                sPoint3 = SetPt[18]
                sPoint4 = SetPt[19]
                sValue1 = Value[16]
                sValue2 = Value[17]
                sValue3 = Value[18]
                sValue4 = Value[19]
                sStdev1 = Stdev[16]
                sStdev2 = Stdev[17]
                sStdev3 = Stdev[18]
                sStdev4 = Stdev[19]
                tolDat1 = Tvalu[4][0]
                tolDat2 = Tvalu[4][1]
                tolDat3 = Tvalu[4][2]
                tolDat4 = Tvalu[4][3]

            elif x == 5:
                proID = 'Winding Angle'
                rID = 'WA'
                ringD1 = ring1[5]
                ringD2 = ring2[5]
                ringD3 = ring3[5]
                ringD4 = ring4[5]
                sPoint1 = SetPt[20]
                sPoint2 = SetPt[21]
                sPoint3 = SetPt[22]
                sPoint4 = SetPt[23]
                sValue1 = Value[20]
                sValue2 = Value[21]
                sValue3 = Value[22]
                sValue4 = Value[23]
                sStdev1 = Stdev[20]
                sStdev2 = Stdev[21]
                sStdev3 = Stdev[22]
                sStdev4 = Stdev[23]
                tolDat1 = Tvalu[5][0]
                tolDat2 = Tvalu[5][1]
                tolDat3 = Tvalu[5][2]
                tolDat4 = Tvalu[5][3]

            elif x == 6:
                proID = 'OD Properties'
                rID = 'PP'
                ringD1 = ring1[6]       # Pipe Diameter
                ringD2 = ring2[6]       # Ramp Count
                ringD3 = ring3[6]       # Hafner Tape Change
                ringD4 = ring4[6]       # Cell Tension
                sPoint1 = SetPt[24]     # Pipe Position
                sPoint2 = SetPt[25]     # Pipe Ovality
                sPoint3 = SetPt[26]     # Void COunt
                sPoint4 = SetPt[27]     # Tape Width
                sValue1 = 0
                sValue2 = 0
                sValue3 = 0
                sValue4 = 0
                sStdev1 = 0
                sStdev2 = 0
                sStdev3 = 0
                sStdev4 = 0
                tolDat1 = Tvalu[6][0]   # Tape Width
                tolDat2 = Tvalu[6][1]
                tolDat3 = Tvalu[6][2]
                tolDat4 = Tvalu[6][3]
            else:
                print('Protocol is missing...')

        elif pRecipe == 'DNV':
            if x == 0:
                proID = 'Laser Power'
                rID = 'LP'  # report ID
                ringD1 = ring1[0]
                ringD2 = ring2[0]
                ringD3 = ring3[0]
                ringD4 = ring4[0]

                sPoint1 = SetPt[0]
                sPoint2 = SetPt[1]
                sPoint3 = SetPt[2]
                sPoint4 = SetPt[3]
                print('\nTPX', sPoint1, ) # TPX [450.0, 450.0, 450.0, 0.0]

                sValue1 = Value[0]
                sValue2 = Value[1]
                sValue3 = Value[2]
                sValue4 = Value[3]
                sStdev1 = Stdev[0]
                sStdev2 = Stdev[1]
                sStdev3 = Stdev[2]
                sStdev4 = Stdev[3]
                tolDat1 = Tvalu[0][0]
                tolDat2 = Tvalu[0][1]
                tolDat3 = Tvalu[0][2]
                tolDat4 = Tvalu[0][3]

            elif x == 1:
                proID = 'Tape Temperature'
                rID = 'TT'  # report ID
                ringD1 = ring1[1]
                ringD2 = ring2[1]
                ringD3 = ring3[1]
                ringD4 = ring4[1]
                sPoint1 = SetPt[4]
                sPoint2 = SetPt[5]
                sPoint3 = SetPt[6]
                sPoint4 = SetPt[7]
                sValue1 = Value[4]
                sValue2 = Value[5]
                sValue3 = Value[6]
                sValue4 = Value[7]
                sStdev1 = Stdev[4]
                sStdev2 = Stdev[5]
                sStdev3 = Stdev[6]
                sStdev4 = Stdev[7]
                tolDat1 = Tvalu[1][0]
                tolDat2 = Tvalu[1][1]
                tolDat3 = Tvalu[1][2]
                tolDat4 = Tvalu[1][3]

            elif x == 2:
                proID = 'Substrate Temperature'
                rID = 'ST'
                ringD1 = ring1[2]
                ringD2 = ring2[2]
                ringD3 = ring3[2]
                ringD4 = ring4[2]
                sPoint1 = SetPt[8]
                sPoint2 = SetPt[9]
                sPoint3 = SetPt[10]
                sPoint4 = SetPt[11]
                sValue1 = Value[8]
                sValue2 = Value[9]
                sValue3 = Value[10]
                sValue4 = Value[11]
                sStdev1 = Stdev[8]
                sStdev2 = Stdev[9]
                sStdev3 = Stdev[10]
                sStdev4 = Stdev[11]
                tolDat1 = Tvalu[2][0]
                tolDat2 = Tvalu[2][1]
                tolDat3 = Tvalu[2][2]
                tolDat4 = Tvalu[2][3]

            elif x == 3:
                proID = 'Gap Measurement' # Winding Speed
                rID = 'TG'
                ringD1 = ring1[3]
                ringD2 = ring2[3]
                ringD3 = ring3[3]
                ringD4 = ring4[3]
                sPoint1 = SetPt[12]
                sPoint2 = SetPt[13]
                sPoint3 = SetPt[14]
                sPoint4 = SetPt[15]
                sValue1 = Value[12]
                sValue2 = Value[13]
                sValue3 = Value[14]
                sValue4 = Value[15]
                sStdev1 = Stdev[12]
                sStdev2 = Stdev[13]
                sStdev3 = Stdev[14]
                sStdev4 = Stdev[15]
                tolDat1 = Tvalu[3][0]
                tolDat2 = Tvalu[3][1]
                tolDat3 = Tvalu[3][2]
                tolDat4 = Tvalu[3][3]

            elif x == 4:
                proID = 'Winding Speed'  #
                rID = 'WS'
                ringD1 = ring1[4]
                ringD2 = ring2[4]
                ringD3 = ring3[4]
                ringD4 = ring4[4]
                sPoint1 = SetPt[16]
                sPoint2 = SetPt[17]
                sPoint3 = SetPt[18]
                sPoint4 = SetPt[19]
                sValue1 = Value[16]
                sValue2 = Value[17]
                sValue3 = Value[18]
                sValue4 = Value[19]
                sStdev1 = Stdev[16]
                sStdev2 = Stdev[17]
                sStdev3 = Stdev[18]
                sStdev4 = Stdev[19]
                tolDat1 = Tvalu[4][0]
                tolDat2 = Tvalu[4][1]
                tolDat3 = Tvalu[4][2]
                tolDat4 = Tvalu[4][3]

            elif x == 5:
                proID = 'OD Properties'
                rID = 'PP'
                # ------------------------------------------
                ringD1 = ring1[5]       # Pipe Diameter [rolling series]
                ringD2 = ring2[5]       # AVG Ramp Count
                ringD3 = ring3[5]       # AVG Hafner Tape Change
                ringD4 = ring4[5]       # AVG Cell ension
                # ----------------------#
                sPoint1 = sDat1     # Pipe Position  [Series]
                sPoint2 = sDat2     # Pipe Ovality   [Series]
                sPoint3 = sDat3     # Avg Void Count
                sPoint4 = sDat4     # Avg Tape Width
                sValue1 = 0
                sValue2 = 0
                sValue3 = 0
                sValue4 = 0
                sStdev1 = 0
                sStdev2 = 0
                sStdev3 = 0
                sStdev4 = 0
                tolDat1 = Tvalu[5][0]   # Tape Width
                tolDat2 = Tvalu[5][1]
                tolDat3 = Tvalu[5][2]
                tolDat4 = Tvalu[5][3]
            else:
                print('End of Layer (EoL) Report successfully generated!\n')
                progressB.stop()
                successPDF()  # indicate success using a popup
                exit()
        else:
            print('End of Layer (EoL) Report successfully generated!\n')
            progressB.stop()
            successPDF()  # indicate success using a popup
            exit()

        # ----------------------------------------------
        df = pd.DataFrame()
        if x == 5 or x == 6:
            df['RingID'] = ['Ring1', 'Ring2', 'Ring3', 'Ring4']  # [ringA, ringB, ringC, ringD]
            df["SetPoint"] = [ringD2, ringD2, ringD2, ringD2]
            df["Nominal"] = [sPoint3[0], sPoint3[0], sPoint3[0], sPoint3[0]]
            df["StdDev"] = [ringD3, ringD3, ringD3, ringD3]
            df["Tolerance"] = [sPoint4[0], sPoint4[0], sPoint4[0], sPoint4[0]]

            df["Status"] = ['OK', 'OK', 'OK', 'OK']
        else:
            df['RingID'] = ['Ring1', 'Ring2', 'Ring3', 'Ring4'] #[ringA, ringB, ringC, ringD]
            df["SetPoint"] = [round(sPoint1,2), round(sPoint2,2), round(sPoint3,2), round(sPoint4,2)]
            df["Nominal"] = [round(sValue1,2), round(sValue2, 2), round(sValue3, 2), round(sValue4,2)]
            df["StdDev"] = [round(sStdev1,2), round(sStdev2,2), round(sStdev3,2), round(sStdev4,2)]
            df["Tolerance"] = [round(tolDat1,2), round(tolDat2,2), round(tolDat3,2), round(tolDat4,2)]
            # -------------------------------------------[]

            if ((df["SetPoint"][0] * df['Tolerance'][0]) - df["SetPoint"][0])  <= df['Nominal'][0] <= ((df["SetPoint"][0] * df['Tolerance'][0]) + df["SetPoint"][0]):
                A = 'OK'
            else:
                A = 'CHECK'
            # -----------------
            if ((df["SetPoint"][1] * df['Tolerance'][1]) - df["SetPoint"][1])  <= df['Nominal'][1] <= ((df["SetPoint"][1] * df['Tolerance'][1]) + df["SetPoint"][1]):
                B = 'OK'
            else:
                B = 'CHECK'
            # -----------------
            if ((df["SetPoint"][2] * df['Tolerance'][2]) - df["SetPoint"][2])  <= df['Nominal'][2] <= ((df["SetPoint"][2] * df['Tolerance'][2]) + df["SetPoint"][2]):
                C = 'OK'
            else:
                C = 'CHECK'
            # -----------------
            if ((df["SetPoint"][3] * df['Tolerance'][3]) - df["SetPoint"][3])  <= df['Nominal'][3] <= ((df["SetPoint"][3] * df['Tolerance'][3]) + df["SetPoint"][3]):
                D = 'OK'
            else:
                D = 'CHECK'
            df["Status"] = [A, B, C, D]

        if x == 5 or x == 6:
            # -- Construct new validation method ------------------[B]
            plt.title('Layer # ' + str(lID) + " Summary")  # Report ID + 'Report'
            plt.xlabel('Sample Distance')
            plt.ylabel('Quality Properties')
            # ------------------------ Compute running average for Pipe Diameter
            numbers_series = pd.Series(ringD1)  # Pipe Diameter's running Mean
            moving_averages = round(numbers_series.ewm(alpha=0.5, adjust=False).mean(), 2)
            m_avg = moving_averages.tolist()
            # Oval_series = np.array(sPoint2)

            # y_nDiam = np.array(ringD1) #.reshape(len(ringD1))       # Pipe Diameter
            # y_nOval = np.array(sPoint2)                             # Ovality
            # m_nDiam = np.array(m_avg)
            # ------------------------
            # x_ppPos = np.array(sPoint1) # .reshape(len(sPoint1))       # Pipe Position
            # ------------------------
            # print('Rolling averages1:', m_avg)
            # plt.plot(x_ppPos, y_nDiam, label='OD (nominal)', linestyle="-")
            # plt.plot(x_ppPos, m_nDiam, label='OD (Mean)', linestyle=":")
            # plt.plot(x_ppPos, y_nOval, label='Ovality %', linestyle="-.")

            plt.plot(moving_averages.index, moving_averages.values, label='OD Nominal', linestyle="-")
            plt.plot(moving_averages.index, m_avg, label='OD (Avg)', linestyle="-")
            # plt.plot(moving_averages.index, nOval_series.values, label='Ovality %', linestyle="-.")
            # plt.plot(x_ppPos, Oval_series) #, label='Ovality %', linestyle="-.")
            plt.legend()
            # ---------------------------------------------------------------------------#
        else:
            # -- Construct new validation method ------------
            title('Layer # ' + str(lID) + " Summary")     # Report ID + 'Report'
            xlabel('Performance Analytics')
            ylabel('Rated Quality')
            # -- Plot Ring Data --[]
            data1 = ringD1
            data2 = ringD2
            data3 = ringD3
            data4 = ringD4
            data = [data1, data2, data3, data4]
            plt.boxplot(data, tick_labels=['Ring 1', 'Ring 2', 'Ring 3', 'Ring 4'])
            # -----------------------------------------------
        savefig(EoL_Doc+'chart_L' + str(lID) + '_' + str(pgID[x]) + '.png', dpi=300)
        # ------ refresh data --------------------------------
        plt.close()
        time.sleep(5)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_xy(0, 0)
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(60)
        pdf.cell(75, 10, rpID + " Report", 0, 2, 'C')
        pdf.cell(90, 10, " ", 0, 2, 'C')

        pdf.cell(-40)
        pdf.cell(5, 10, "Customer Project ID: " + (str(proj)), 0, 2, 'L')
        pdf.cell(5, 10, "Pipe ID                      : " + (str(pID)), 0, 2, 'L')
        pdf.cell(5, 10, "Operators ID            : " + (str(oID)), 0, 2, 'L')
        pdf.cell(5, 10, "Date Time                : " + (str(dID)), 0, 2, 'L')
        pdf.cell(5, 10, "Layer Number         : " + (str(lID)), 0, 2, 'L')
        pdf.cell(5, 10, "Process Name         : " + (str(proID)), 0, 2, 'L')
        pdf.cell(40)
        pdf.cell(90, 10, " ", 0, 2, 'C')

        if x == 5 or x == 6:
            # draw a rectangle over the text area for Report header ----
            pdf.rect(x=20.0, y=20.5, w=150.0, h=50, style='')
            # construct report header ----------------------------------
            pdf.cell(-40)
            pdf.cell(5, 10, (str(proID)), 0, 2, 'L')
            pdf.cell(30, 8, 'RingID', 1, 0, 'C')
            pdf.cell(25, 8, 'R-Count', 1, 0, 'C')
            pdf.cell(25, 8, 'V-Count', 1, 0, 'C')
            pdf.cell(25, 8, 'TapeChg', 1, 0, 'C')
            pdf.cell(25, 8, 'T-Width', 1, 0, 'C')
            pdf.cell(20, 8, "Status", 1, 2, 'C')
            pdf.set_font('helvetica', '', 12)
            pdf.cell(-130)
        else:
            # draw a rectangle over the text area for Report header ----
            pdf.rect(x=20.0, y=20.5, w=150.0, h=50, style='')
            # construct report header r1RC, r2RC, r3RC, r4RC, rR1VC, r2VC, r3VC, r4VC,
            pdf.cell(-40)
            pdf.cell(5, 10, (str(proID)), 0, 2, 'L')
            pdf.cell(30, 8, 'RingID', 1, 0, 'C')
            pdf.cell(25, 8, 'PValue', 1, 0, 'C')   # Process set Value
            pdf.cell(25, 8, "[Mean]", 1, 0, 'C')    # Mean of measured Value
            pdf.cell(25, 8, "[SDev]", 1, 0, 'C')
            pdf.cell(25, 8, "Tol(±)", 1, 0, 'C')
            pdf.cell(20, 8, "Status", 1, 2, 'C')
            pdf.set_font('helvetica', '', 12)
            pdf.cell(-130)

        for i in range(0, len(df)):
            print('Iteration ...')   # Instead of ln=2 use new_x=XPos.LEFT, new_y=YPos.NEXT.
            pdf.cell(30, 8, '%s' % (str(df.RingID.iloc[i])), 1, 0, 'C')  # 1: Next line under
            pdf.cell(25, 8, '%s' % (str(df.SetPoint.iloc[i])), 1, 0, 'C')  # 0: to the right
            pdf.cell(25, 8, '%s' % (str(df.Nominal.iloc[i])), 1, 0, 'C')
            pdf.cell(25, 8, '%s' % (str(df.StdDev.iloc[i])), 1, 0, 'C')
            pdf.cell(25, 8, '%s' % (str(df.Tolerance.iloc[i])), 1, 0, 'C')
            if str(df["Status"].iloc[i]) == "OK":
                pdf.set_fill_color(0, 255, 0)
                pdf.cell(20, 8, '%s' % (str(df["Status"].iloc[i])), 1, 2, 'C', 1)
            else:
                pdf.set_fill_color(255, 255, 0)
                pdf.cell(20, 8, '%s' % (str(df["Status"].iloc[i])), 1, 2, 'C', 1)
            pdf.cell(-130)  # newly added for testing
        # ----------------------------------------------------------------------------------------
        pdf.cell(90, 20, " ", 0, 2, 'C')  # 2: place new line below

        pdf.cell(-30)
        pdf.image(EoL_Doc+'chart_L' + str(lID) + '_' + str(pgID[x]) + '.png', x=10, y=145, w=0, h=130, type='', link='')

        # pdf.set_font('arial', '', 8)
        pdf.set_font('helvetica', '', 7)
        with pdf.rotation(angle=90, x=3, y=280):
            pdf.text(10, 280, "SPC Generated Report - " + (str(dID)))
            pdf.image(impath + 'magmaDot.png', x=270, y=430, w=10, h=50)

        # Encode EoL report as <LayerNumber_PageDescription_Process Short Name>.pdf --------------[]
        pdf.output(EoL_Doc+'L' + str(layrN) + '_' + str(pgID[x]) + '_' + str(rID) + '.pdf')
        time.sleep(5)
    clear_DF()
    print('End of Layer (EoL) Report successfully generated!\n')
    progressB.stop()
    pdf_genA = False
    successPDF()    # indicate success using a popup

    return
# -------------------------------------------------------------------------------------------------[B]
def errorNote():
    messagebox.showerror('Error!', 'Specified an Invalid layer #')
    return

def errorDuplicate():
    messagebox.showerror('Duplicate Error!', 'This layer report was generated!')
    return

def reportPDFcancel():
    messagebox.showinfo('User Action', 'Report Generation Cancelled!')
    return

def pdfViewError():
    messagebox.showerror('View Error', 'Exceed maximum pages per layer!')
    return

def errorConnect():
    messagebox.showerror('Data', 'Sorry, Data is inaccessible!')
    return

def successPDF():
    messagebox.showinfo('EoL Report', 'Report Successfully Generated!')
    return

def successLaunchRPM():
    messagebox.showinfo('[RPM]:', 'Successfully Launched!')
    return

def random_with_N_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1

    return randint(range_start, range_end)

# ----------------------------------------------------------------
def layerProcess(cLayerN=None):
    global layerN
    # Generate Enf of Layer Report ---------[]

    # Get current layer number or Obtain layer number User input -
    if uCalling == 1 and not sysRun:
        if not pdf_layer or pdf_layer[-1] < cLayerN:
            layerN = cLayerN
            print('Activating SPC Automatic Report Generation, please wait... ')
            Process(target=lambda: get_data(layerN), name='Progress_Bar', daemon=True).start()
        else:
            errorDuplicate()
            print('Duplicate report is not allowed!')

    elif uCalling == 2:
        layerN = simpledialog.askstring("EoL", "Specify Layer Number#:")
        if not pdf_layer or layerN not in pdf_layer:
            if layerN and len(layerN) < 3:
                Process(target=lambda: get_data(layerN), name='Progress_Bar', daemon=True).start()
            else:
                errorNote()
                print('\nInvalid Layer # specified, try again....')
        else:
            errorDuplicate()
            print('Duplicate report is not allowed!')

    elif uCalling == 3:
        layerN = simpledialog.askstring("EoL", "Specify Layer Number#:")
        if layerN not in pdf_layer:
            if layerN and len(layerN) < 3:
                Thread(target=lambda: get_data(layerN), name='Progress_Bar', daemon=True).start()
            else:
                errorNote()
                print('\nInvalid Layer # specified, try again....')
        else:
            errorDuplicate()
            print('Duplicate report is not allowed!')
    else:
        progressB.stop()
        reportPDFcancel()

    pdf_layer.append(layerN)
    print('\nProcessing Layer #:', layerN)
# -------------------------------------------------------------------------------------------------[]

def get_data(layerN):
    global rpData, pdf_genA, ol_con

    pdf_genA, sq_con = True, None
    layrN = layerN
    # ---------- Based on Group's URS ------------------#
    if pRecipe == 'DNV':
        T1 = 'ZLP_' + str(pWON)       # Laser Power
        T2 = 'ZTT_' + str(pWON)       # Identify EOL_TT Table
        T3 = 'ZST_' + str(pWON)       # Identify EOL_ST Table
        T4 = 'ZTG_' + str(pWON)       # Identify EOL_TG Table
        T5 = 'ZWS_' + str(pWON)       # Winding Speed
        T6 = 'ZPP_' + str(pWON)       # Identify RampCount Table - not visualised but reckoned on pdf report

    else:
        T1 = 'ZLP_' + pWON      # Identify Laser Power EOL Table
        T2 = 'ZLA_' + pWON      # Identify Laser Angle EOL Table
        T3 = 'ZTT_' + pWON      # Identify Tape Temperature EOL Table
        T4 = 'ZST_' + pWON      # Identify Substrate Temperature EOL Table
        T5 = 'ZTG_' + pWON      # Identify Tape Gap EOL Table
        T6 = 'ZWA_' + pWON      # Identify Winding Angle EOL Table
        T7 = 'ZPP_' + pWON      # Identify RampCount Table
    # ------------------------------#

    # Initialise SQL Data connection per listed Table --------------------[]
    progressB.start()
    print("Retrieving data for Layer#:", layrN, ' please wait...')
    if sq_con is None:
        sq_con = sq.rpt_SQLconnect()
    else:
        sq_con = viz_con
    # ------------------------------#
    if sq_con:
        time.sleep(2)
        # Split Process & Map SQL data columns into Dataframe -------------------------------------------[]
        if pRecipe == 'MGM':    # Winding Angle Parameter
            print('\nProcessing MGM Reports.....')
            # ----------------------------------------
            zLP, zLA, zTT, zST, zTG, zWA, zPP = pdfrp.mgm_sqlExec(sq_con, T1, T2, T3, T4, T5, T6, layrN)
            coluA = ['cLyr', 'R1SP', 'R1NV', 'R2SP', 'R2NV', 'R3SP', 'R3NV', 'R4SP', 'R4NV']  # LP
            coluB = ['cLyr', 'R1SP', 'R1NV', 'R2SP', 'R2NV', 'R3SP', 'R3NV', 'R4SP', 'R4NV']  # LA
            coluC = ['cLyr', 'R1SP', 'R1NV', 'R2SP', 'R2NV', 'R3SP', 'R3NV', 'R4SP', 'R4NV']  # TT
            coluD = ['cLyr', 'R1SP', 'R1NV', 'R2SP', 'R2NV', 'R3SP', 'R3NV', 'R4SP', 'R4NV']  # ST
            coluE = ['cLyr', 'R1SP', 'R1NV', 'R2SP', 'R2NV', 'R3SP', 'R3NV', 'R4SP', 'R4NV']  # TG
            coluF = ['cLyr', 'R1SP', 'R1NV', 'R2SP', 'R2NV', 'R3SP', 'R3NV', 'R4SP', 'R4NV']  # WA
            coluG = ['cLyr', 'PipePos', 'PipeDiam', 'Ovality', 'RampCnt', 'VoidCnt', 'TChange', 'TpWidth', 'Tension']  # PP
        else:
            print('\nProcessing DNV Reports.....')
            # ----------------------------------------
            zLP, zTT, zST, zTG, zWS, zPP = pdfrp.dnv_sqlExec(sq_con, T1, T2, T3, T4, T5, T6, layrN)
            coluF = ['id_col', 'cLyr', 'R1SP', 'R1NV', 'R2SP', 'R2NV', 'R3SP', 'R3NV', 'R4SP', 'R4NV']
            coluA = ['id_col', 'cLyr', 'R1SP', 'R1NV', 'R2SP', 'R2NV', 'R3SP', 'R3NV', 'R4SP', 'R4NV']
            coluB = ['id_col', 'cLyr', 'R1SP', 'R1NV', 'R2SP', 'R2NV', 'R3SP', 'R3NV', 'R4SP', 'R4NV']
            coluC = ['id_col', 'cLyr', 'R1SP', 'R1NV', 'R2SP', 'R2NV', 'R3SP', 'R3NV', 'R4SP', 'R4NV']
            coluD = ['id_col', 'cLyr', 'R1SP', 'R1NV', 'R2SP', 'R2NV', 'R3SP', 'R3NV', 'R4SP', 'R4NV']
            coluE = ['id_col', 'cLyr', 'PipePos', 'PipeDiam', 'Ovality', 'RampCnt', 'VoidCnt', 'TChange', 'TpWidth', 'Tension']
        # ------------------------------------
        szA, szB, szC, szD = len(zTT), len(zST), len(zTG), len(zWS)
        if pRecipe == 'MGM':
            df1 = pd.DataFrame(zLP, columns=coluA)  # Inherited from global variable EoL/EoP Process
            df2 = pd.DataFrame(zLA, columns=coluB)
            df3 = pd.DataFrame(zTT, columns=coluC)
            df4 = pd.DataFrame(zST, columns=coluD)
            df5 = pd.DataFrame(zTG, columns=coluE)
            df6 = pd.DataFrame(zWA, columns=coluF)
            df7 = pd.DataFrame(zPP, columns=coluG)
            rpData = [df1, df2, df3, df4, df5, df6, df7]
        elif pRecipe == 'DNV':
            df6 = pd.DataFrame(zLP, columns=coluF)      # New structural update. Add Laser Power to Report
            df1 = pd.DataFrame(zTT, columns=coluA)      # Dataframe level resampling is disabled. Table level is enabled
            # df1 = df1.sample(frac=0.3, axis='rows', random_state=9)
            df2 = pd.DataFrame(zST, columns=coluB)
            # df2 = df2.sample(frac=0.3, axis='rows', random_state=9)
            df3 = pd.DataFrame(zTG, columns=coluC)
            # df3 = df3.sample(frac=0.3, axis='rows', random_state=9)
            df4 = pd.DataFrame(zWS, columns=coluD)
            # df4 = df4.sample(frac=0.3, axis='rows', random_state=9)
            # ------ Saphire Pipe Property ------#
            df5 = pd.DataFrame(zPP, columns=coluE)
            # ---------------------------------------
            rpData = [df6, df1, df2, df3, df4, df5]                   # Dynamic aggregated List
        else:
            print('Unknown Process not defined...')
        # ---------------------------------------
        autoProp = random_with_N_digits(10)
        # Constants per Pipe -------------------#
        rptID = 'EoL'
        cPipe = str(autoProp)                   # Pipe ID TODO -- Automate varibles
        cstID = 'Customer cID'                  # Customer ID
        usrID = 'Operator ID'                   # User ID
        layrNO = layrN                          # Layer ID
        # --------------------------------------#
        for i in range(len(rpData)):
            if pRecipe == 'DNV':
                if i == 0:
                    cProc = 'Laser Power'                   # Process ID
                    rPage = '1of6'
                    Tvalu = [0.057, 0.057, 0.057, 0.057]    # Tolerance
                    ring1A = rpData[i]['R1SP']              # Actual value (SP)
                    ring1B = rpData[i]['R1NV']              # Measured values = Real value  = (NV)
                    ring2A = rpData[i]['R2SP']
                    ring2B = rpData[i]['R2NV']
                    ring3A = rpData[i]['R3SP']
                    ring3B = rpData[i]['R3NV']
                    ring4A = rpData[i]['R4SP']
                    ring4B = rpData[i]['R4NV']
                elif i == 1:
                    cProc = 'Tape Temperature'              # Process ID
                    rPage = '2of6'
                    Tvalu = [0.057, 0.057, 0.057, 0.057]    # Tolerance
                    ring1A = rpData[i]['R1SP']              # Actual value (SP)
                    ring1B = rpData[i]['R1NV']              # Measured values = Real value  = (NV)
                    ring2A = rpData[i]['R2SP']
                    ring2B = rpData[i]['R2NV']
                    ring3A = rpData[i]['R3SP']
                    ring3B = rpData[i]['R3NV']
                    ring4A = rpData[i]['R4SP']
                    ring4B = rpData[i]['R4NV']
                elif i == 2:
                    cProc = 'Substrate Temperature'     # Process ID
                    rPage = '3of6'
                    Tvalu = [0.07, 0.07, 0.07, 0.07]     # Tolerance
                    ring1A = rpData[i]['R1SP']          # Actual value (SP)
                    ring1B = rpData[i]['R1NV']          # Measured values = Real value  = (NV)
                    ring2A = rpData[i]['R2SP']          #
                    ring2B = rpData[i]['R2NV']          #
                    ring3A = rpData[i]['R3SP']          #
                    ring3B = rpData[i]['R3NV']          #
                    ring4A = rpData[i]['R4SP']          #
                    ring4B = rpData[i]['R4NV']
                elif i == 3:
                    cProc = 'Gap Measurement'           # Process ID
                    rPage = '4of6'
                    Tvalu = [0.05, 0.05, 0.05, 0.05]    # Awaiting Tolerance values from QA
                    ring1A = rpData[i]['R1SP']          # Actual value (SP)
                    ring1B = rpData[i]['R1NV']          # Measured values = Real value  = (NV)
                    ring2A = rpData[i]['R2SP']          #
                    ring2B = rpData[i]['R2NV']          #
                    ring3A = rpData[i]['R3SP']          #
                    ring3B = rpData[i]['R3NV']          #
                    ring4A = rpData[i]['R4SP']          #
                    ring4B = rpData[i]['R4NV']
                elif i == 4:
                    cProc = 'Winding Speed'             # Process ID
                    rPage = '5of6'
                    Tvalu = [0.05, 0.05, 0.05, 0.05]    # Set Tolerance (axis=1 columns)
                    ring1A = rpData[i]['R1SP']          # Actual value (SP)
                    ring1B = rpData[i]['R1NV']          # Measured values = Real value  = (NV)
                    ring2A = rpData[i]['R2SP']          #
                    ring2B = rpData[i]['R2NV']          #
                    ring3A = rpData[i]['R3SP']          #
                    ring3B = rpData[i]['R3NV']          #
                    ring4A = rpData[i]['R4SP']          #
                    ring4B = rpData[i]['R4NV']          #
                elif i == 5:
                    # 'LyID', 'PipePos', 'PipeDiam', 'Ovality', 'RampCnt', 'VoidCnt', 'TChange', 'TpWidth', 'Tension'
                    cProc = 'OD Properties'
                    rPage = '6of6'
                    Tvalu = [0.05, 0.05, 0.05, 0.05]
                    ring1A = rpData[i]['PipePos']
                    ring1B = rpData[i]['PipeDiam']
                    ring2A = rpData[i]['Ovality']
                    ring2B = rpData[i]['RampCnt']
                    ring3A = rpData[i]['VoidCnt']
                    ring3B = rpData[i]['TChange']
                    ring4A = rpData[i]['TpWidth']
                    ring4B = rpData[i]['Tension']

            elif pRecipe == 'MGM':
                if i == 0:
                    cProc = 'Laser Power'              # Process ID
                    rPage = '1of7'
                    Tvalu = [0.0, 0.0, 0.0, 0.0]       # Tolerance
                    ring1A = rpData[i]['R1SP']         # Actual value (SP)
                    ring1B = rpData[i]['R1NV']         # Measured values = Real value  = (NV)
                    ring2A = rpData[i]['R2SP']         #
                    ring2B = rpData[i]['R2NV']         #
                    ring3A = rpData[i]['R3SP']         #
                    ring3B = rpData[i]['R3NV']         #
                    ring4A = rpData[i]['R4SP']         #
                    ring4B = rpData[i]['R4NV']
                elif i == 1:
                    cProc = 'Laser Angle'               # Process ID
                    rPage = '2of7'
                    Tvalu = [0.02, 0.02, 0.02, 0.02]    # Tolerance
                    ring1A = rpData[i]['R1SP']          # Actual value (SP)
                    ring1B = rpData[i]['R1NV']          # Measured values = Real value  = (NV)
                    ring2A = rpData[i]['R2SP']          #
                    ring2B = rpData[i]['R2NV']          #
                    ring3A = rpData[i]['R3SP']          #
                    ring3B = rpData[i]['R3NV']          #
                    ring4A = rpData[i]['R4SP']          #
                    ring4B = rpData[i]['R4NV']
                elif i == 2:
                    cProc = 'Tape Temperature'           # Process ID
                    rPage = '3of7'
                    Tvalu = [0.057, 0.057, 0.057, 0.057] # Tolerance
                    ring1A = rpData[i]['R1SP']          # Actual value (SP)
                    ring1B = rpData[i]['R1NV']          # Measured values = Real value  = (NV)
                    ring2A = rpData[i]['R2SP']          #
                    ring2B = rpData[i]['R2NV']          #
                    ring3A = rpData[i]['R3SP']          #
                    ring3B = rpData[i]['R3NV']          #
                    ring4A = rpData[i]['R4SP']          #
                    ring4B = rpData[i]['R4NV']
                elif i == 3:
                    cProc = 'Substrate Temperature'      # Process ID
                    rPage = '4of7'
                    Tvalu = [0.04, 0.04, 0.04, 0.04]     # Set Tolerance (axis=1 columns)
                    ring1A = rpData[i]['R1SP']          # Actual value (SP)
                    ring1B = rpData[i]['R1NV']          # Measured values = Real value  = (NV)
                    ring2A = rpData[i]['R2SP']          #
                    ring2B = rpData[i]['R2NV']          #
                    ring3A = rpData[i]['R3SP']          #
                    ring3B = rpData[i]['R3NV']          #
                    ring4A = rpData[i]['R4SP']          #
                    ring4B = rpData[i]['R4NV']          #
                elif i == 4:
                    cProc = 'Gap Measurement'           # Process ID
                    rPage = '5of7'
                    Tvalu = [0.04, 0.04, 0.04, 0.04]     # Set Tolerance (axis=1 columns)
                    ring1A = rpData[i]['R1SP']          # Actual value (SP)
                    ring1B = rpData[i]['R1NV']          # Measured values = Real value  = (NV)
                    ring2A = rpData[i]['R2SP']          #
                    ring2B = rpData[i]['R2NV']          #
                    ring3A = rpData[i]['R3SP']          #
                    ring3B = rpData[i]['R3NV']          #
                    ring4A = rpData[i]['R4SP']          #
                    ring4B = rpData[i]['R4NV']          #
                elif i == 5:
                    cProc = 'Winding Angle'              # Process ID
                    rPage = '6of7'
                    Tvalu = [0.04, 0.04, 0.04, 0.04]    # Set Tolerance (axis=1 columns)
                    ring1A = rpData[i]['R1SP']          # Actual value (SP)
                    ring1B = rpData[i]['R1NV']          # Measured values = Real value  = (NV)
                    ring2A = rpData[i]['R2SP']          #
                    ring2B = rpData[i]['R2NV']          #
                    ring3A = rpData[i]['R3SP']          #
                    ring3B = rpData[i]['R3NV']          #
                    ring4A = rpData[i]['R4SP']          #
                    ring4B = rpData[i]['R4NV']          #
                elif i == 6:
                    # 'LyID', 'PipePos', 'PipeDiam', 'Ovality', 'RampCnt', 'VoidCnt', 'TChange', 'TpWidth', 'Tension'
                    cProc = 'OD Properties'
                    rPage = '7of7'
                    Tvalu = [0.04, 0.04, 0.04, 0.04]
                    ring1A = rpData[i]['PipePos']
                    ring1B = rpData[i]['PipeDiam']
                    ring2A = rpData[i]['Ovality']
                    ring2B = rpData[i]['RampCnt']
                    ring3A = rpData[i]['VoidCnt']
                    ring3B = rpData[i]['TChange']
                    ring4A = rpData[i]['TpWidth']
                    ring4B = rpData[i]['Tension']
            # --------------------------#
            # psData.append(cProc)
            pgeDat.append(rPage)                    # Page ID
            # --------------------------#
            if cProc == 'OD Properties':
                # ------------------------------
                r1Data.append(ring1B)                                   # Pipe Diameter
                if len(ring2B) > 0 or len(ring3B) > 0 or len(ring4B) > 0:
                    r2Data.append(round(sum(ring2B)/len(ring2B), 2))    # Ramp Count
                    r3Data.append(round(sum(ring3B) / len(ring3B), 2))  # Hafner Tape Change
                    r4Data.append(round(sum(ring4B) / len(ring4B), 2))  # Cell Tension
                else:
                    r2Data.append(round(sum(ring2B) / 1, 2))            # avoid zero division error
                    r3Data.append(round(sum(ring3B) / 1, 2))            # Hafner Tape Change
                    r4Data.append(round(sum(ring4B) / 1, 2))            # Cell Tension
                # ------------------------------------------------------#
                sDat1.append(ring1A)                                    # Pipe longitudinal Position
                sDat2.append(ring2A)                                    # Pipe Ovality
                if len(ring3A) > 0 or len(ring4A) > 0:
                    sDat3.append(round(sum(ring3A)/len(ring3A), 2))     # Void Count
                    sDat4.append(round(sum(ring4A)/len(ring4A),2))      # Tape Width
                else:
                    sDat3.append(round(sum(ring3A) / 1, 2))             # Void Count
                    sDat4.append(round(18.0/ 1, 2))             # Tape Width
                # ------------------------------------------------------#
                valuDat.append(0)                                       # Void Count Values R1
                valuDat.append(0)
                valuDat.append(0)
                valuDat.append(0)
                # - Stad Deviation --
                stdDat.append(0)
                stdDat.append(0)
                stdDat.append(0)
                stdDat.append(0)
                # -------------------
                tolDat.append(Tvalu)
            else:
                # Process Set Point values (Average all the values per ring) ---[]
                if (sum(ring1A)) != 0 or (sum(ring2A)) != 0 or (sum(ring3A)) != 0 or (sum(ring4A)) != 0:
                    dataL1 = len(ring1A)
                    dataL2 = len(ring2A)
                    dataL3 = len(ring3A)
                    dataL4 = len(ring4A)
                    dataX1 = len(ring1B)
                    dataX2 = len(ring2B)
                    dataX3 = len(ring3B)
                    dataX4 = len(ring4B)
                else:
                    dataL1 = 1
                    dataL2 = 1
                    dataL3 = 1
                    dataL4 = 1
                    dataX1 = 1
                    dataX2 = 1
                    dataX3 = 1
                    dataX4 = 1
                # ----- Set points per Ring ----
                SetAvgSPa = (sum(ring1A)) / dataL1      # Mean values for per Ring Setpoint values
                SetAvgSPb = (sum(ring2A)) / dataL2
                SetAvgSPc = (sum(ring3A)) / dataL3
                SetAvgSPd = (sum(ring4A)) / dataL4
                # ---- Mean values per Ring -----
                SetAvgMVa = (sum(ring1B)) / dataX1      # Mean values for per Ring Measured Values
                SetAvgMVb = (sum(ring2B)) / dataX2
                SetAvgMVc = (sum(ring3B)) / dataX3
                if sum(ring4B) > 0:
                    SetAvgMVd = (sum(ring4B)) / dataX4
                else:
                    SetAvgMVd = 1
                # -----------------------------
                Stdev1 = round(np.std(ring1B), 2)       # Standard Deviation on Measured Values to 2 precision
                Stdev2 = round(np.std(ring2B), 2)
                Stdev3 = round(np.std(ring3B), 2)
                Stdev4 = round(np.std(ring4B), 2)
                # ------------------------------
                r1Data.append(ring1B)                   # Box Plot Values for Ring 1
                r2Data.append(ring2B)                   # Box Plot Values for Ring 2
                r3Data.append(ring3B)                   # Box Plot Values for Ring 3
                r4Data.append(ring4B)                   # Box Plot Values for Ring 4
                # ----------------------
                sptDat.append(SetAvgSPa)
                sptDat.append(SetAvgSPb)
                sptDat.append(SetAvgSPc)
                sptDat.append(SetAvgSPd)

                valuDat.append(SetAvgMVa)
                valuDat.append(SetAvgMVb)
                valuDat.append(SetAvgMVc)
                valuDat.append(SetAvgMVd)
                # ---- Stad Deviation ----
                stdDat.append(Stdev1)
                stdDat.append(Stdev2)
                stdDat.append(Stdev3)
                stdDat.append(Stdev4)
                # -------------------
                tolDat.append(Tvalu)
        # Send values to PDG generator and repeat until last process ----------------[]
        generate_pdf(rptID, cPipe, cstID, usrID, layrNO, r1Data, r2Data, r3Data, r4Data, sptDat, valuDat, stdDat, tolDat, pgeDat, sDat1, sDat2, sDat3, sDat4)
    else:
        progressB.stop()
        print('Report Generation Failed! Post Production Data is not reachable...')
        errorConnect()

    return
    # -------------------------------------------------------------------------------[]

class autoResizableCanvas(tk.Canvas):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<Configure>", self.resize)

    def resize(self, event):
        self.config(width=event.width, height=event.height)


def recoveryTT(layer, batch_TT, piPos):                             # Record for offline SPC analysis
    rtitle = ('========= TCP01 - Batch Tracker =============\n')
    rheader = ('Time'+'\t\t'+'Layer#'+'\t'+'TT-Batch'+'\t'+'EstPos'+'\n')
    rdemaca = ("--------------------------------------------\n")
    event = datetime.now().strftime("%H:%M.%S")                     # WON as name for easy retrieval method
    RecoveryLog = 'TTLog_' + str(pWON)                              # processed SQL index Log

    filepath = '.\\crashRecovery\\'+RecoveryLog+".txt"
    old_report = os.path.isfile(filepath)

    if not old_report:                                              # if doing a new report...
        f = open('.\\crashRecovery\\'+RecoveryLog+".txt", "a")      # Open new file and ...
        f.write(rtitle)                                             # Insert a Title
        f.write(rheader)                                            # Insert new header
        f.write(rdemaca)                                            # Insert demarcator
    else:                                                           # if it's an existing report
        f = open('.\\crashRecovery\\' + RecoveryLog + ".txt", "a")  # Just open the file for a write operations
    # initialise a tab delimited data and insert corresponding values in string format ------------------------[]
    f.write(event+'\t'+str(layer)+'\t'+str(batch_TT)+'\t'+str(piPos)+'\n')
    f.close()

def recoveryST(layer, batch_ST, piPos):                             # Record for offline SPC analysis
    rtitle = ('========= TCP01 - Batch Tracker =============\n')
    rheader = ('Time'+'\t\t'+'Layer#'+'\t'+'TT-Batch'+'\t'+'EstPos'+'\n')
    rdemaca = ("--------------------------------------------\n")
    event = datetime.now().strftime("%H:%M.%S")                     # WON as name for easy retrieval method
    RecoveryLog = 'STLog_' + str(pWON)                              # processed SQL index Log

    filepath = '.\\crashRecovery\\'+RecoveryLog+".txt"
    old_report = os.path.isfile(filepath)

    if not old_report:                                              # if doing a new report...
        f = open('.\\crashRecovery\\'+RecoveryLog+".txt", "a")      # Open new file and ...
        f.write(rtitle)                                             # Insert a Title
        f.write(rheader)                                            # Insert new header
        f.write(rdemaca)                                            # Insert demarcator
    else:                                                           # if it's an existing report
        f = open('.\\crashRecovery\\' + RecoveryLog + ".txt", "a")  # Just open the file for a write operations
    # initialise a tab delimited data and insert corresponding values in string format ------------------------[]
    f.write(event+'\t'+str(layer)+'\t'+str(batch_ST)+'\t'+str(piPos)+'\n')
    f.close()

def recoveryTG(layer, batch_TG, piPos):                             # Record for offline SPC analysis
    rtitle = ('========= TCP01 - Batch Tracker =============\n')
    rheader = ('Time'+'\t\t'+'Layer#'+'\t'+'TT-Batch'+'\t'+'EstPos'+'\n')
    rdemaca = ("--------------------------------------------\n")
    event = datetime.now().strftime("%H:%M.%S")                     # WON as name for easy retrieval method
    RecoveryLog = 'TGLog_' + str(pWON)                              # processed SQL index Log

    filepath = '.\\crashRecovery\\'+RecoveryLog+".txt"
    old_report = os.path.isfile(filepath)

    if not old_report:                                              # if doing a new report...
        f = open('.\\crashRecovery\\'+RecoveryLog+".txt", "a")      # Open new file and ...
        f.write(rtitle)                                             # Insert a Title
        f.write(rheader)                                            # Insert new header
        f.write(rdemaca)                                            # Insert demarcator
    else:                                                           # if it's an existing report
        f = open('.\\crashRecovery\\' + RecoveryLog + ".txt", "a")  # Just open the file for a write operations
    # initialise a tab delimited data and insert corresponding values in string format ------------------------[]
    f.write(event+'\t'+str(layer)+'\t'+str(batch_TG)+'\t'+str(piPos)+'\n')
    f.close()

def recoveryWS(layer, batch_WS, piPos):                             # Record for offline SPC analysis
    rtitle = ('========= TCP01 - Batch Tracker =============\n')
    rheader = ('Time'+'\t\t'+'Layer#'+'\t'+'TT-Batch'+'\t'+'EstPos'+'\n')
    rdemaca = ("--------------------------------------------\n")
    event = datetime.now().strftime("%H:%M.%S")                     # WON as name for easy retrieval method
    RecoveryLog = 'WSLog_' + str(pWON)                              # processed SQL index Log

    filepath = '.\\crashRecovery\\'+RecoveryLog+".txt"
    old_report = os.path.isfile(filepath)

    if not old_report:                                              # if doing a new report...
        f = open('.\\crashRecovery\\'+RecoveryLog+".txt", "a")      # Open new file and ...
        f.write(rtitle)                                             # Insert a Title
        f.write(rheader)                                            # Insert new header
        f.write(rdemaca)                                            # Insert demarcator
    else:                                                           # if it's an existing report
        f = open('.\\crashRecovery\\' + RecoveryLog + ".txt", "a")  # Just open the file for a write operations
    # initialise a tab delimited data and insert corresponding values in string format ------------------------[]
    f.write(event+'\t'+str(layer)+'\t'+str(batch_WS)+'\t'+str(piPos)+'\n')
    f.close()


# -------------------------------------------------------------------------#
def timeProcessor(runtimeType, smp_Sz, runtimeParams, regime, lapsedT):    # Record for offline SPC analysis

    rtitle = ('=== TCP1 - Processing Speed Tracker - '+runtimeType+ ' Samples ===\n')
    rheader = ('Rolling Type'+'\t'+'Sample'+'\t'+'Parameters#'+'\t'+'Regime'+'\t'+'LapsedTime'+'\n')
    rdemaca = ("----------------------------------------------------------\n")
    PidxLog = 'TXLog_' + str(pWON)                                          # processed SQL index Log

    filepath = '.\\ProcessTime_Log\\'+PidxLog+".txt"
    old_report = os.path.isfile(filepath)

    if not old_report:                                                      # if doing a new report...
        f = open('.\\ProcessTime_Log\\'+PidxLog+".txt", "a")                # Open new file and ...
        f.write(rtitle)                                                     # Insert a Title
        f.write(rheader)                                                    # Insert new header
        f.write(rdemaca)                                                    # Insert demarcator
    else:                                                                   # if it's an existing report
        f = open('.\\ProcessTime_Log\\' + PidxLog + ".txt", "a")            # Just open the file for a write operations
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


def check_pid(pid):
    PROCESS_QUERY_INFROMATION = 0x1000
    processHandle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFROMATION, 0, pid)
    if processHandle == 0:
        return False
    else:
        ctypes.windll.kernel32.CloseHandle(processHandle)
    return True

def menuExit():
    # print('ExitBit H/L:', exit_bit)
    inUse = os.getpid()

    if not exit_bit and inUse == 1:                         # Check exit_bit for unitary value
        print('\nExiting Local GUI, bye for now...')
        root.quit()                                         # Exit Apps if exit_bit is empty
        os._exit(0)                                         # Close out all process

    elif len(exit_bit) >= 4 and inUse > 1:
        print('\nExiting Local GUI, bye for now...')

        # Evaluate active process before exiting -------#
        proc_list = [p1.pid, p2.pid, p3.pid, p4.pid]        # Evaluate exit_bit as true if all active
        for p in proc_list:
            try:
                os.kill(p, signal.SIGTERM)
                print('Process:', p, ' terminated by the User')
            except Exception:
                print(f'Process {p} failed to terminate, attempting force termination!')

    elif len(exit_bit) < 4 and inUse:
        print('Exiting...')
        root.quit()
        os._exit(0)

    else:
        root.quit()
        os._exit(0)

# ------------------------------------------------------------------------------------[ MAIN PROGRAM ]

def tabbed_cascadeMode(pWON, cType):
    global p1, p2, p3, p4, p5, p6, p7, hostConn, pRecipe, pMode
    """
    https://stackoverflow.com/questions/73088304/styling-a-single-tkinter-notebook-tab
    :return:
    
    cType = DNV / MGM
    pMode = Auto / Manual 
    """

    if uCalling == 1:
        print('Connecting to PLC Host...')
        pMode = 'Auto Triggered RT Live Procedure'
    elif uCalling == 2:
        print('Connecting to SQL Server...')
        pMode = 'Operator Triggered PPA Procedure'
    else:
        print('Standby/Maintenance Mode...')
    # Specify production type -----------[DNV/MGM]

    pRecipe = cType
    print('Loading ' + pRecipe + ' Production Data...\n')

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
    p1, p2, p3, p4, p5, p6, p7, p8 = cs.myMain(pMode, pWON, pRecipe)   # runtimeType, process RecipeType
    # ----------------------------------------------------------[]

    # Set up embedding notebook (tabs) ------------------------[B]
    notebook = ttk.Notebook(root, width=scrW, height=850)       # Declare Tab overall Screen size [2500]
    notebook.grid(column=0, row=0, padx=10, pady=450)           # Tab's spatial position on the Parent [10]
    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)
    tab3 = ttk.Frame(notebook)

    # Define common Tabb for DNV/MGM Procedure  ----------------#
    notebook.add(tab1, text="[Runtime Monitoring]")             # Default Min/Max x1
    notebook.add(tab2, text="EoL Report System")                # Report
    notebook.add(tab3, text="EoP Report System")                # Report
    notebook.grid()

    # ------------------------------------------[]
    MonitorTabb(master=tab1).grid(column=0, row=0, padx=10, pady=10)
    # ------------------------------------------[]
    collectiveEoL(master=tab2).grid(column=0, row=0, padx=10, pady=10)
    collectiveEoP(master=tab3).grid(column=0, row=0, padx=10, pady=10)

    root.mainloop()

# -------- Controls --------

def tabbed_canvas(cMode, cType):   # Tabbed Common Classes -------------------[TABBED]
    global hostConn, pRecipe, pMode, actTabb
    """
    https://stackoverflow.com/questions/73088304/styling-a-single-tkinter-notebook-tab
    :return:
    """
    if cMode == 1:
        print('Connecting to PLC Host...')
        pMode = 'Auto Triggered: Live Processing'
    elif cMode == 2:
        print('Connecting to SQL Server...')
        pMode = 'Operator Triggered PPA Procedure'
    else:
        pMode = 'Standby/Maintenance'
        print('Standby/Maintenance Mode...')
    # Specify production type -----------[DNV/MGM]

    # Specify production type -----------[DNV/MGM]
    pRecipe = cType     # DNV/MGM
    print('Loading ' + pRecipe + ' Production Data...\n')

    s = ttk.Style()
    s.theme_use('default')
    s.configure('TNotebook.Tab', background="green3", foreground="black")

    # s.map("TNotebook", background=[("selected", "red3")]) #
    s.map("TNotebook.Tab", background=[("selected", "lightblue")], foreground=[("selected", "red")])

    # Hover color if needed  -------------------------------#
    common_rampCount()                                      # called function
    common_climateProfile()                                 # called function
    common_gapCount()                                       # called function
    # Load from CFG fine and parse the variables ---------[x]

    # Set up embedding notebook (tabs) -------------------[B]
    notebook = ttk.Notebook(root, width=scrW, height=850)     # Declare Tab overall Screen size[2500, 2540,]
    notebook.grid(column=0, row=0, padx=10, pady=450)         # Tab's spatial position on the Parent [450]
    if pRecipe == 'DNV':
        tab1 = ttk.Frame(notebook)
        tab2 = ttk.Frame(notebook)
        tab3 = ttk.Frame(notebook)
        tab4 = ttk.Frame(notebook)
        tab5 = ttk.Frame(notebook)
        tab6 = ttk.Frame(notebook)
    else:
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
    if pRecipe == 'DNV':                                    # int(LP) and not int(LA):
        print('Loading DNV Algorithm...\n')
        notebook.add(tab1, text="Tape Temperature")         # Stats x16
        notebook.add(tab2, text="Substrate Temperature")    # Stats x16
        notebook.add(tab3, text="Tape Gap Polarisation")    # Stats x4 per Ring
        # ----------------------------------------------#
        notebook.add(tab4, text="[Runtime Monitoring]")     # Default Min/Max x16
        # ----------------------------------------------#
        notebook.add(tab5, text="EoL Report System")        # Report
        notebook.add(tab6, text="EoP Report System")        # Report

    elif pRecipe == 'MGM':                                  # int(TT) and int(ST) and int(TG):
        print('Loading Commercial Algorithm...\n')
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
        pass
        print('Loading Bespoke User Selection Algorithm...')

    notebook.grid()

    # Create DNV tab frames properties -------------[]
    if pRecipe == 'DNV':
        tapeTempTabb(master=tab1).grid(column=0, row=0, padx=10, pady=10)
        substTempTabb(master=tab2).grid(column=0, row=0, padx=10, pady=10)
        tapeGapPolTabb(master=tab3).grid(column=0, row=0, padx=10, pady=10)
        # ------------------------------------------[]
        MonitorTabb(master=tab4).grid(column=0, row=0, padx=10, pady=10)
        # ------------------------------------------[]
        collectiveEoL(master=tab5).grid(column=0, row=0, padx=10, pady=10)
        collectiveEoP(master=tab6).grid(column=0, row=0, padx=10, pady=10)

    elif pRecipe == 'MGM':
        laserPowerTabb(master=tab1).grid(column=0, row=0, padx=10, pady=10)
        laserAngleTabb(master=tab2).grid(column=0, row=0, padx=10, pady=10)
        rollerForceTabb(master=tab3).grid(column=0, row=0, padx=10, pady=10)
        tapeTempTabb(master=tab4).grid(column=0, row=0, padx=10, pady=10)
        substTempTabb(master=tab5).grid(column=0, row=0, padx=10, pady=10)
        tapePlacementTabb(master=tab6).grid(column=0, row=0, padx=10, pady=10)
        tapeGapPolTabb(master=tab7).grid(column=0, row=0, padx=10, pady=10)
        # --------------------------------------------[]
        MonitorTabb(master=tab8).grid(column=0, row=0, padx=10, pady=10)
        # --------------------------------------------[]
        collectiveEoL(master=tab9).grid(column=0, row=0, padx=10, pady=10)
        collectiveEoP(master=tab10).grid(column=0, row=0, padx=10, pady=10)
        # ------------------------------------------[]
    else:       # USR Selection
        print('Details not found!')

    root.mainloop()


def plotView(titleMean):
    # Define Axes ----------------------------------#
    fig = Figure(figsize=(27, 7), dpi=100)  # 12.5, 7
    fig.subplots_adjust(left=0.04, bottom=0.033, right=0.988, top=0.957, hspace=0.14, wspace=0.033)
    # ---------------------------------[]
    a1 = fig.add_subplot(2, 3, (1, 2))  # X Bar Plot
    a2 = fig.add_subplot(2, 3, (4, 5))  # S Bar Plot
    a3 = fig.add_subplot(2, 3, (3, 6))  # Combo Ref

    # Declare Plots attributes ---------------------[]
    plt.rcParams.update({'font.size': 7})  # Reduce font size to 7pt for all legends

    # Calibrate limits for X-moving Axis -----------#
    YScale_minRF, YScale_maxRF = 10, 500
    sBar_minRF, sBar_maxRF = 10, 250    # Calibrate Y-axis for S-Plot
    window_Xmin, window_Xmax = 0, 120   # windows view = visible data points
    # Common properties ------------------------#
    a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
    a2.set_ylabel("Sample Deviation [" + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
    a1.set_title(titleMean + '[XBar Plot]', fontsize=12, fontweight='bold')
    a2.set_title(titleMean + '[SDev Plot]', fontsize=12, fontweight='bold')

    # Apply grid lines ------------------------------
    a1.grid(color="0.5", linestyle='-', linewidth=0.5)
    a2.grid(color="0.5", linestyle='-', linewidth=0.5)
    a1.legend(loc='upper right', title='Mean curve')
    a2.legend(loc='upper right', title='Sigma curve')

    # ----------------------------------------------------------#
    a1.set_ylim([YScale_minRF, YScale_maxRF], auto=True)
    a1.set_xlim([window_Xmin, window_Xmax])
    # ----------------------------------------------------------#
    a2.set_ylim([sBar_minRF, sBar_maxRF], auto=True)
    a2.set_xlim([window_Xmin, window_Xmax])
    # ----------------------------------------------------------#
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


def readEoP(text_widget, rptID):        # End of Pipe Report
    # file_path = filedialog.askopenfilename(title='Select a Text File', filetypes=[('Text files&quot', '*.txt')])

    file_path = 'C:\\SynchronousGPU\\FMEA_Log\\'+ rptID +'.txt'
    rpfMissing = 'C:\\SynchronousGPU\\FMEA_Log\\RPT_NOTFOUND.txt'
    conc_RPT = ["RPT_LP_", "RPT_LA_", "RPT_TP_", "RPT_RF_", "RPT_TT_", "RPT_ST_", "RPT_TG_"]
    # -----------------------------------------------------------------

    if rptID == "RPT_AL_":
        counter = 1
        file_path = 'C:\\SynchronousGPU\\FMEA_Log\\' + conc_RPT +'.txt'
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


# -------- Defines the collective screen structure -----------------------[EOL Reports]
class PDFViewer(ScrolledText):

    def show(self, pdf_file):
        self.delete('1.0', 'end')       # clear current content
        pdf = fitz.open(pdf_file)                   # open the PDF file
        # pdf = pymupdf.open(pdf_file)

        self.images = []                            # for storing the page images
        for page in pdf:
            pix = page.get_pixmap()
            pix1 = fitz.Pixmap(pix, 0) if pix.alpha else pix
            photo = tk.PhotoImage(data=pix1.tobytes('ppm'))

            # insert into the text box
            self.image_create('end', image=photo)
            self.insert('end', '\n')
            # save the image to avoid garbage collected
            self.images.append(photo)

    def viewReport(self):
        pdfs = filedialog.askopenfilenames(initialdir=EoL_Doc, title="EoL Report",
                                           filetype=[("PDF Files", "*.pdf"), ("All Files", "*.*")])
        if not pdfs:
            return

        images = []
        print('\nLoading the following PDF report(s):')
        for page in pdfs:
            if len(pdfs) <= 6:          # set limits to number of paged report
                print(page)
            images.append(page)

        qawin = Toplevel(root)
        qawin.title("Magma QA Prompt")
        qawin.resizable(False, False)
        # --------------------------------------
        if len(images) == 1:
            w, h = 600, 850
        elif len(images) == 6:
            w, h = 1800, 850
        else:
            w, h = 1200, 850
        screen_w = qawin.winfo_screenwidth()
        screen_h = qawin.winfo_screenheight()
        # --------------------------------------#
        x_c = int((screen_w / 2) - (w / 2))
        y_c = int((screen_h / 2) - (h / 2))
        qawin.geometry(f"{w}x{h}+{x_c}+{y_c}")  # reset position
        # --------------------------------------#
        qawin.rowconfigure(0, weight=1)
        qawin.columnconfigure((0,1), weight=1)
        # ---------------[]
        if len(images) <= 1:
            pdf1 = PDFViewer(qawin, width=72, height=20, spacing3=5, bg='blue')
            pdf1.grid(row=0, column=0, sticky='nsew')
            pdf1.show(images[0])

        elif len(images) == 2:
            pdf1 = PDFViewer(qawin, width=72, height=20, spacing3=5, bg='blue')
            pdf1.grid(row=0, column=0, sticky='nsew')
            pdf1.show(images[0])

            pdf2 = PDFViewer(qawin, width=72, height=20, spacing3=5, bg='blue')
            pdf2.grid(row=0, column=1, sticky='nsew')
            pdf2.show(images[1])

        elif len(images) == 3:
            pdf1 = PDFViewer(qawin, width=72, height=20, spacing3=5, bg='blue')
            pdf1.grid(row=0, column=0, sticky='nsew')
            pdf1.show(images[0])

            pdf2 = PDFViewer(qawin, width=72, height=20, spacing3=5, bg='blue')
            pdf2.grid(row=0, column=1, sticky='nsew')
            pdf2.show(images[1])

            pdf3 = PDFViewer(qawin, width=72, height=20, spacing3=5, bg='blue')
            pdf3.grid(row=1, column=0, sticky='nsew')
            pdf3.show(images[2])

        elif len(images) == 4:
            pdf1 = PDFViewer(qawin, width=72, height=20, spacing3=5, bg='blue')
            pdf1.grid(row=0, column=0, sticky='nsew')
            pdf1.show(images[0])

            pdf2 = PDFViewer(qawin, width=72, height=20, spacing3=5, bg='blue')
            pdf2.grid(row=0, column=1, sticky='nsew')
            pdf2.show(images[1])

            pdf3 = PDFViewer(qawin, width=72, height=20, spacing3=5, bg='blue')
            pdf3.grid(row=1, column=0, sticky='nsew')
            pdf3.show(images[2])

            pdf4 = PDFViewer(qawin, width=72, height=20, spacing3=5, bg='blue')
            pdf4.grid(row=1, column=1, sticky='nsew')
            pdf4.show(images[3])

        elif len(images) == 5:
            pdf1 = PDFViewer(qawin, width=72, height=20, spacing3=5, bg='blue')
            pdf1.grid(row=0, column=0, sticky='nsew')
            pdf1.show(images[0])

            pdf2 = PDFViewer(qawin, width=72, height=20, spacing3=5, bg='blue')
            pdf2.grid(row=0, column=1, sticky='nsew')
            pdf2.show(images[1])

            pdf3 = PDFViewer(qawin, width=72, height=20, spacing3=5, bg='blue')
            pdf3.grid(row=1, column=0, sticky='nsew')
            pdf3.show(images[2])

            pdf4 = PDFViewer(qawin, width=72, height=20, spacing3=5, bg='blue')
            pdf4.grid(row=1, column=1, sticky='nsew')
            pdf4.show(images[3])

            # 5th Page with column span option -----
            pdf5 = PDFViewer(qawin, width=72, height=20, spacing3=5, bg='blue')
            pdf5.grid(row=0, column=2, columnspan=1, rowspan=2, sticky='nsew')
            pdf5.show(images[4])

        elif len(images) == 6:
            pdf1 = PDFViewer(qawin, width=72, height=20, spacing3=5, bg='blue')
            pdf1.grid(row=0, column=0, sticky='nsew')
            pdf1.show(images[0])

            pdf2 = PDFViewer(qawin, width=72, height=20, spacing3=5, bg='blue')
            pdf2.grid(row=0, column=1, sticky='nsew')
            pdf2.show(images[1])

            pdf3 = PDFViewer(qawin, width=72, height=20, spacing3=5, bg='blue')
            pdf3.grid(row=1, column=0, sticky='nsew')
            pdf3.show(images[2])

            pdf4 = PDFViewer(qawin, width=72, height=20, spacing3=5, bg='blue')
            pdf4.grid(row=1, column=1, sticky='nsew')
            pdf4.show(images[3])

            pdf5 = PDFViewer(qawin, width=72, height=20, spacing3=5, bg='blue')
            pdf5.grid(row=0, column=2, sticky='nsew')
            pdf5.show(images[4])

            pdf6 = PDFViewer(qawin, width=72, height=20, spacing3=5, bg='blue')
            pdf6.grid(row=1, column=2, sticky='nsew')
            pdf6.show(images[5])
        else:
            pdfViewError()
            print('You are loading more pages than allowed..')


class collectiveEoL(ttk.Frame):
    # ------ SmpleSize, GroupType, SEOLSpace, SEOPSpace, EnableDNV, EnableAUT, EnableMGM, size20, size18
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.running = True
        self.loadEoL = False
        self.toggle_state = True
        # self.createEoLViz()

        # Button-------Trigger --------------
        if uCalling == 1:  # TCP01 Process Triggered msctcp == 49728:
            self.createEoLViz()
            self.running = True

        elif uCalling == 2:
            self.enViz = ttk.Button(self, text="Open EoL Static Report", command=self.toggle)
            self.enViz.pack(padx=1220, pady=1)
        else:
            self.enViz = ttk.Button(self, text="Open EoL Static Report", command=self.catch_virtue)
            self.enViz.pack(padx=1220, pady=1)
        # # ------------------------ End of Layer Static Data Call/Stop Call ------------------[]
    #
    def toggle(self):
        if self.toggle_state:
            self.enableEoLReport()
            self.enViz.config(text="Close EoL Visualisation")
        else:
            self.closeOutEoL()
            self.enViz.config(text="Open EoL Static Report")
        self.toggle_state = not self.toggle_state

    def enableEoLReport(self):  # Only on Post production ----------------[]
        global eol

        self.running = True
        self.canvas = True
        if not self.loadEoL:
            self.loadEoL = True
            eol = threading.Thread(target=self.createEoLViz, daemon=True)
            eol.start()
        print('[EoL Viz] is now running....')
        self.acknEoLOpened()

    def closeOutEoL(self):
        global eol

        self.loadEoL = False
        self.running = False
        if self.canvas:
            print('User requested for cancellation, please wait...')
            self.canvas.get_tk_widget().destroy()
            self.toolbar.destroy()
            label.destroy()
            self.canvas = None
            print('[EoL] report viz is now closed!')
        # eol.terminate() # not required since the process is daemon set!
        eol.join()
        self.acknEoLClosed()


    def catch_virtue(self):
        messagebox.showinfo("User Request:", "End of Layer report is unpacking in 5sec")
        time.sleep(5)
        self.toggle()

    def acknEoLOpened(self):
        messagebox.showinfo("EoL:", "End of Layer successfully loaded!")

    def acknEoLClosed(self):
        messagebox.showinfo("EoL:", "End of Layer successfully closed!")
    # ----------------------------------------------------------------[]
    # -------------------------- Ramp Profiling Static Data Call --------------------------[]

    def createEoLViz(self):
        global progressB, im10, im11, im12, \
        im13, im14, im15, im16, im17, im18, im19, im20, im21, im22, im23, im24, im25, im26, im27, im28, im29, im30, \
        im31, im32, im33, im34, im35, im36, im37, im38, im39, im40, im41, im42, im43, im44, im45, im46, im47, im48, \
        im49, im50, im51, im52, im53, im54, im55, im56, im57, wsS, ttS, stS, tgS, rcS, vcS, lpS, laS, ttS, stS, tgS, \
        waS, ttSoL, stSoL, tgSoL, wsSoL, lpSoL, laSoL, waSoL, label

        if pRecipe == 'DNV':
            import qParamsHL_DNV as dnv
            ttS, ttTy, ttSoL, ttSoP, ttHL, ttAL, ttFO, A, B, C, D, E = dnv.decryptpProcessLim(pWON, 'TT')
            stS, stTy, stSoL, stSoP, stHL, stAL, stFO, A, B, C, D, E = dnv.decryptpProcessLim(pWON, 'ST')
            tgS, tgTy, tgSoL, tgSoP, tgHL, tgAL, tgFO, A, B, C, D, E = dnv.decryptpProcessLim(pWON, 'TG')
            wsS, wsTy, wsSoL, wsSoP, wsHL, wsAL, wsFO, A, B, C, D, E = dnv.decryptpProcessLim(pWON, 'WS')
            # ----
            rcS, rcTy, rcSoL, rcSoP, rcHL, rcAL, rcFO, A, B, C, D, E = dnv.decryptpProcessLim(pWON, 'RC')
            vcS, vcTy, vcSoL, vcSoP, vcHL, vcAL, vcFO, A, B, C, D, E = dnv.decryptpProcessLim(pWON, 'VC')
        else:
            import qParamsHL_MGM as mgm
            lpS, lpTy, lpSoL, lpSoP, lpHL, lpAL, lpFO, A, B, C, D, E = mgm.decryptpProcessLim(pWON, 'LP')
            laS, laTy, laSoL, laSoP, laHL, laAL, laFO, A, B, C, D, E = mgm.decryptpProcessLim(pWON, 'LA')
            ttS, ttTy, ttSoL, ttSoP, ttHL, ttAL, ttFO, A, B, C, D, E = mgm.decryptpProcessLim(pWON, 'TT')
            stS, stTy, stSoL, stSoP, stHL, stAL, stFO, A, B, C, D, E = mgm.decryptpProcessLim(pWON, 'ST')
            tgS, tgTy, tgSoL, tgSoP, tgHL, tgAL, tgFO, A, B, C, D, E = mgm.decryptpProcessLim(pWON, 'TG')
            waS, waTy, waSoL, waSoP, waHL, waAL, waFO, A, B, C, D, E = mgm.decryptpProcessLim(pWON, 'WA')
        # ----------------------------------------------[]
        # Load metrics from config ------------[TG, TT, ST]
        label = ttk.Label(self, text='[End of Layer Summary - ' + str(pMode) + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)
        # ----------------------------------#
        gen_report = ttk.Button(self, text="Generate PDF Reports", command=layerProcess)
        gen_report.place(x=1920, y=1)

        # --------------------------------- DOnt remove Process Bar -----
        progressB = ttk.Progressbar(self, mode="indeterminate")
        progressB.place(x=2090, y=1, width=250)
        # ---------------------------------#
        upload_report = ttk.Button(self, text="View EoL Summary", command=lambda: PDFViewer.viewReport(self=None))
        upload_report.place(x=2380, y=1)
        # Define Axes ---------------------#
        self.f = Figure(figsize=(pMtX, 8), dpi=100)  # pMtX
        self.f.subplots_adjust(left=0.022, bottom=0.05, right=0.983, top=0.955, wspace=0.138, hspace=0.18)
        # ---------------------------------[]
        if pRecipe == 'DNV':
            self.a1 = self.f.add_subplot(2, 4, 1)         # xbar plot
            self.a2 = self.f.add_subplot(2, 4, 2)         # s bar plot
            self.a3 = self.f.add_subplot(2, 4, 3)         # s bar plot
            self.a4 = self.f.add_subplot(2, 4, 4)
            self.a5 = self.f.add_subplot(2, 4, 5)         # s bar plot
            self.a6 = self.f.add_subplot(2, 4, 6)         # s bar plot
            self.a7 = self.f.add_subplot(2, 4, 7)         # s bar plot
            self.a8 = self.f.add_subplot(2, 4, 8)
        else:
            self.a1 = self.f.add_subplot(2, 6, 1)         # xbar plot
            self.a2 = self.f.add_subplot(2, 6, 2)         # sbar plot
            self.a3 = self.f.add_subplot(2, 6, 3)         # xbar plot
            self.a4 = self.f.add_subplot(2, 6, 4)         # sbar plot
            self.a5 = self.f.add_subplot(2, 6, 5)         # xbar plot
            self.a6 = self.f.add_subplot(2, 6, 6)         # sbar plot
            self.a7 = self.f.add_subplot(2, 6, 7)         # xbar plot
            self.a8 = self.f.add_subplot(2, 6, 8)         # sbar plot
            self.a9 = self.f.add_subplot(2, 6, 9)         # xbar plot
            self.a10 = self.f.add_subplot(2, 6, 10)       # sbar plot
            self.a11 = self.f.add_subplot(2, 6, 11)       # xbar plot
            self.a12 = self.f.add_subplot(2, 6, 12)       # sbar plot

        # Declare Plots attributes ----------------------------[H]
        plt.rcParams.update({'font.size': 7})                   # Reduce font size to 7pt for all legends
        # self.canvas.draw()

        # Calibrate limits for X-moving Axis -------------------#
        YScale_minTT, YScale_maxTT = 200, 600
        YScale_minST, YScale_maxST = 200, 600
        YScale_minTG, YScale_maxTG = -12, 12
        YScale_minWS, YScale_maxWS = -7, 7
        sBar_minTT, sBar_maxTT = -10, 10                      # Calibrate Y-axis for S-Plot
        sBar_minST, sBar_maxST = -10, 10
        sBar_minTG, sBar_maxTG = -10, 10
        sBar_minWS, sBar_maxWS = -10, 10

        self.win_Xmin, self.win_Xmax = 0, pLength            # 1 meter = 10sec data if 6m/min @ 10Hz

        # Load SQL Query Table [Important] ---------------------#
        if pRecipe == 'DNV':
            EoLRep = 'DNV'
            # ---------- Based on Group's URS ------------------#
            print('\nLoading specified WON', str(pWON))
            self.T1 = 'ZTT_' + str(pWON)          # Identify EOL_TT Table
            self.T2 = 'ZST_' + str(pWON)          # Identify EOL_ST Table
            self.T3 = 'ZTG_' + str(pWON)          # Identify EOL_TG Table
            self.T4 = 'ZWS_' + str(pWON)          # Winding Speed

        elif pRecipe == 'MGM':
            EoLRep = 'MGM'
            # --------- Based on Group's URS -------------------#
            T1 = 'ZLP_' + str(pWON)          # Identify Laser Power EOL Table
            T2 = 'ZLA_' + str(pWON)          # Identify Laser Angle EOL Table
            T3 = 'ZTT_' + str(pWON)          # Identify Tape Temperature EOL Table
            T4 = 'ZST_' + str(pWON)          # Identify Substrate Temperature EOL Table
            T5 = 'ZTG_' + str(pWON)          # Identify Tape Gap EOL Table
            T6 = 'ZWA_' + str(pWON)          # Identify Winding Angle EOL Table
            # Identify Void count table

        else:
            pass
        # ----------------------------------------------------------#

        # Initialise runtime limits
        self.a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        if pRecipe == 'DNV':
            self.a5.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
            # -----------------------------
            self.a1.set_title('EoL - Tape Temperature [XBar]', fontsize=12, fontweight='bold')
            self.a5.set_title('EoL - Tape Temperature [SDev]', fontsize=12, fontweight='bold')
            self.a5.set_xlabel("Pipe Segment (mt)")
            # ------
            self.a2.set_title('EoL - Substrate Temperature [XBar]', fontsize=12, fontweight='bold')
            self.a6.set_title('EoL - Substrate Temperature [SDev]', fontsize=12, fontweight='bold')
            self.a6.set_xlabel("Pipe Segment (mt)")
            # -------------------
            self.a3.set_title('EoL - Tape Gap Measurement [XBar]', fontsize=12, fontweight='bold')
            self.a7.set_title('EoL - Tape Gap Measurement [SDev]', fontsize=12, fontweight='bold')
            self.a7.set_xlabel("Pipe Segment (mt)")
            # -------------------
            self.a4.set_title('EoL - Tape Winding Speed [XBar]', fontsize=12, fontweight='bold')
            self.a8.set_title('EoL - Tape Winding Speed [SDev]', fontsize=12, fontweight='bold')
            self.a8.set_xlabel("Pipe Segment (mt)")
            # ----------------------------------------------------
            self.a1.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a2.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a3.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a4.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a5.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a6.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a7.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a8.grid(color="0.5", linestyle='-', linewidth=0.5)

            self.a1.legend(['EoL - Tape Temperature'], loc='upper right', fontsize=9)
            self.a2.legend(['EoL - Substrate Temperature'], loc='upper right', fontsize=9)
            self.a3.legend(['EoL - Tape Gap Measurement'], loc='upper right', fontsize=9)
            self.a4.legend(['EoL - Winding Speed'], loc='upper right', fontsize=9)
            # ----------------------------------------------------------#
            self.a1.set_ylim([YScale_minTT, YScale_maxTT], auto=True)
            self.a1.set_xlim([self.win_Xmin, self.win_Xmax])

            self.a5.set_ylim([sBar_minTT, sBar_maxTT], auto=True)
            self.a5.set_xlim([self.win_Xmin, self.win_Xmax])

            # ----------------------------------------------------------#
            self.a2.set_ylim([YScale_minST, YScale_maxST], auto=True)
            self.a2.set_xlim([self.win_Xmin, self.win_Xmax])

            self.a6.set_ylim([sBar_minST, sBar_maxST], auto=True)
            self.a6.set_xlim([self.win_Xmin, self.win_Xmax])

            self.a3.set_ylim([YScale_minTG, YScale_maxTG], auto=True)
            self.a3.set_xlim([self.win_Xmin, self.win_Xmax])

            self.a7.set_ylim([sBar_minTG, sBar_maxTG], auto=True)
            self.a7.set_xlim([self.win_Xmin, self.win_Xmax])

            self.a4.set_ylim([YScale_minWS, YScale_maxWS], auto=True)
            self.a4.set_xlim([self.win_Xmin, self.win_Xmax])

            self.a8.set_ylim([sBar_minWS, sBar_maxWS], auto=True)
            self.a8.set_xlim([self.win_Xmin, self.win_Xmax])

        else:
            self.a7.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
            # -----------------------------
            self.a1.set_title('EoL - Laser Power [XBar]', fontsize=12, fontweight='bold')
            self.a7.set_title('EoL - Laser Power [SDev]', fontsize=12, fontweight='bold')
            # ------
            self.a2.set_title('EoL - Laser Angle [XBar]', fontsize=12, fontweight='bold')
            self.a8.set_title('EoL - Laser Angle [SDev]', fontsize=12, fontweight='bold')
            # -------------------
            self.a3.set_title('EoL - Tape Temperature [XBar]', fontsize=12, fontweight='bold')
            self.a9.set_title('EoL - Tape Temperature [SDev]', fontsize=12, fontweight='bold')
            # ------
            self.a4.set_title('EoL - Substrate Temperature [XBar]', fontsize=12, fontweight='bold')
            self.a10.set_title('EoL - Substrate Temperature [SDev]', fontsize=12, fontweight='bold')
            # -------------------
            self.a5.set_title('EoL - Tape Gap Measurement [XBar]', fontsize=12, fontweight='bold')
            self.a11.set_title('EoL - Tape Gap Measurement [SDev]', fontsize=12, fontweight='bold')
            # -------------------
            self.a6.set_title('EoL - Tape Winding Angle [XBar]', fontsize=12, fontweight='bold')
            self.a12.set_title('EoL - Tape Winding Angle [SDev]', fontsize=12, fontweight='bold')

            # -----------------------------------------------------[]
            self.a1.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a2.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a3.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a4.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a5.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a6.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a7.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a8.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a9.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a10.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a11.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a12.grid(color="0.5", linestyle='-', linewidth=0.5)

            self.a1.legend(loc='upper right', title='EoL - Laser Power')
            self.a2.legend(loc='upper right', title='EoL - Laser Angle')
            self.a3.legend(loc='upper right', title='EoL - Tape Temperature')
            self.a4.legend(loc='upper right', title='EoL - Substrate Temperature')
            self.a5.legend(loc='upper right', title='EoL - Tape Gap Measurement')
            self.a6.legend(loc='upper right', title='EoL - Tape Winding Speed')

            # ----------------------------------------------------------#
            self.a1.set_ylim([0, 10], auto=True)
            self.a1.set_xlim([self. win_Xmin, self.win_Xmax])

            self.a2.set_ylim([0, 10], auto=True)
            self.a2.set_xlim([self.win_Xmin, self.win_Xmax])

            self.a3.set_ylim([0, 10], auto=True)
            self.a3.set_xlim([self.win_Xmin, self.win_Xmax])

            self.a4.set_ylim([0, 10], auto=True)
            self.a4.set_xlim([self.win_Xmin, self.win_Xmax])

            self.a5.set_ylim([0, 10], auto=True)
            self.a5.set_xlim([self.win_Xmin, self.win_Xmax])

            self.a6.set_ylim([0, 10], auto=True)
            self.a6.set_xlim([self.win_Xmin, self.win_Xmax])

            self.a7.set_ylim([0, 10], auto=True)
            self.a7.set_xlim([self.win_Xmin, self.win_Xmax])

            self.a8.set_ylim([0, 10], auto=True)
            self.a8.set_xlim([self.win_Xmin, self.win_Xmax])

            self.a9.set_ylim([0, 10], auto=True)
            self.a9.set_xlim([self.win_Xmin, self.win_Xmax])

            self.a10.set_ylim([0, 10], auto=True)
            self.a10.set_xlim([self.win_Xmin, self.win_Xmax])

            self.a11.set_ylim([0, 10], auto=True)
            self.a11.set_xlim([self.win_Xmin, self.win_Xmax])

            self.a12.set_ylim([0, 10], auto=True)
            self.a12.set_xlim([self.win_Xmin, self.win_Xmax])
        # ---------------------------------------------------------[]
        # Define Plot area and axes -
        # ---------------------------------------------------------[1-5]
        if EoLRep == 'DNV':
            # ----------Stats for aggregated Values for Tape Temperature -----
            im10, = self.a1.plot([], [], '-o', label='Tape Temp - Ring 1')
            im11, = self.a1.plot([], [], '-o', label='Tape Temp - Ring 2')
            im12, = self.a1.plot([], [], '-o', label='Tape Temp - Ring 3')
            im13, = self.a1.plot([], [], '-o', label='Tape Temp - Ring 4')
            # -------------- Standard Deviation S Plot --------------[TT]
            im14, = self.a5.plot([], [], '--', label='Tape Temp')
            im15, = self.a5.plot([], [], '--', label='Tape Temp')
            im16, = self.a5.plot([], [], '--', label='Tape Temp')
            im17, = self.a5.plot([], [], '--', label='Tape Temp')

            # ---- Stats for aggregated Values for Substrate Temperature -----
            im18, = self.a2.plot([], [], '-o', label='Sub Temp - Ring 1')
            im19, = self.a2.plot([], [], '-o', label='Sub Temp - Ring 2')
            im20, = self.a2.plot([], [], '-o', label='Sub Temp - Ring 3')
            im21, = self.a2.plot([], [], '-o', label='Sub Temp - Ring 4')
            # -------------- Standard Deviation S Plot --------------[ST]
            im22, = self.a6.plot([], [], '--', label='Sub Temp')
            im23, = self.a6.plot([], [], '--', label='Sub Temp')
            im24, = self.a6.plot([], [], '--', label='Sub Temp')
            im25, = self.a6.plot([], [], '--', label='Sub Temp')

            # X Plot --------------------Tape Gap ---------------------------
            im26, = self.a3.plot([], [], '-o', label='Tape Gap - Ring 1')
            im27, = self.a3.plot([], [], '-o', label='Tape Gap - Ring 2')
            im28, = self.a3.plot([], [], '-o', label='Tape Gap - Ring 3')
            im29, = self.a3.plot([], [], '-o', label='Tape Gap - Ring 4')
            #  S Plot ---------------------Tape Gap ---------------------------
            im30, = self.a7.plot([], [], '--', label='Tape Gap')
            im31, = self.a7.plot([], [], '--', label='Tape Gap')
            im32, = self.a7.plot([], [], '--', label='Tape Gap')
            im33, = self.a7.plot([], [], '--', label='Tape Gap')

            # X Plot --------------------Winding Speed -------------------------
            im34, = self.a4.plot([], [], '-o', label='Winding Speed - Ring 1')
            im35, = self.a4.plot([], [], '-o', label='Winding Speed - Ring 2')
            im36, = self.a4.plot([], [], '-o', label='Winding Speed - Ring 3')
            im37, = self.a4.plot([], [], '-o', label='Winding Speed - Ring 4')
            im38, = self.a8.plot([], [], '--', label='Winding Speed')
            im39, = self.a8.plot([], [], '--', label='Winding Speed')
            im40, = self.a8.plot([], [], '--', label='Winding Speed')
            im41, = self.a8.plot([], [], '--', label='Winding Speed')
            # ---------------------------------------------------------[2-6]
        else:
            EoLRep = 'MGM'
            # ------------------------------------------------[Laser Power x4]
            im10, = self.a1.plot([], [], 'o-', label='Laser Power - (R1H1)')
            im11, = self.a1.plot([], [], 'o-', label='Laser Power - (R1H2)')
            im12, = self.a1.plot([], [], 'o-', label='Laser Power - (R1H3)')
            im13, = self.a1.plot([], [], 'o-', label='Laser Power - (R1H4)')
            im14, = self.a7.plot([], [], 'o-', label='Laser Power')
            im15, = self.a7.plot([], [], 'o-', label='Laser Power')
            im16, = self.a7.plot([], [], 'o-', label='Laser Power')
            im17, = self.a7.plot([], [], 'o-', label='Laser Power')

            # ---------------------------------------------------[Laser Angle x4]
            im18, = self.a2.plot([], [], 'o-', label='Laser Angle - (R1H1)')
            im19, = self.a2.plot([], [], 'o-', label='Laser Angle - (R1H2)')
            im20, = self.a2.plot([], [], 'o-', label='Laser Angle - (R1H3)')
            im21, = self.a2.plot([], [], 'o-', label='Laser Angle - (R1H4)')
            im22, = self.a2.plot([], [], 'o-', label='Laser Angle')
            im23, = self.a2.plot([], [], 'o-', label='Laser Angle')
            im24, = self.a2.plot([], [], 'o-', label='Laser Angle')
            im25, = self.a2.plot([], [], 'o-', label='Laser Angle')

            # ----------------------------------------[Tape Temperature x16]
            im26, = self.a3.plot([], [], 'o-', label='Tape Temp - (R1H1)')
            im27, = self.a3.plot([], [], 'o-', label='Tape Temp - (R1H2)')
            im28, = self.a3.plot([], [], 'o-', label='Tape Temp - (R1H3)')
            im29, = self.a3.plot([], [], 'o-', label='Tape Temp - (R1H4)')
            im30, = self.a9.plot([], [], 'o-', label='Tape Temp')
            im31, = self.a9.plot([], [], 'o-', label='Tape Temp')
            im32, = self.a9.plot([], [], 'o-', label='Tape Temp')
            im33, = self.a9.plot([], [], 'o-', label='Tape Temp')

            # ----------------------------------------[Substrate Temperature x16]
            im34, = self.a4.plot([], [], 'o-', label='Substrate Temp - (R1H1)')
            im35, = self.a4.plot([], [], 'o-', label='Substrate Temp - (R1H2)')
            im36, = self.a4.plot([], [], 'o-', label='Substrate Temp - (R1H3)')
            im37, = self.a4.plot([], [], 'o-', label='Substrate Temp - (R1H4)')
            # ------
            im38, = self.a10.plot([], [], 'o-', label='Substrate Temp')
            im39, = self.a10.plot([], [], 'o-', label='Substrate Temp')
            im40, = self.a10.plot([], [], 'o-', label='Substrate Temp')
            im41, = self.a10.plot([], [], 'o-', label='Substrate Temp')

            # --------------------------------------------------[Tape Gap x8]
            im42, = self.a5.plot([], [], 'o-', label='Tape Gap - (A1)')
            im43, = self.a5.plot([], [], 'o-', label='Tape Gap - (A2)')
            im44, = self.a5.plot([], [], 'o-', label='Tape Gap - (A3)')
            im45, = self.a5.plot([], [], 'o-', label='Tape Gap - (A4)')

            im46, = self.a11.plot([], [], 'o-', label='Tape Gap')
            im47, = self.a11.plot([], [], 'o-', label='Tape Gap')
            im48, = self.a11.plot([], [], 'o-', label='Tape Gap')
            im49, = self.a11.plot([], [], 'o-', label='Tape Gap')

            # -------------------------------------------------------[Ramp Data T4]
            im50, = self.a6.plot([], [], 'o-', label='Winding Angle - (R1H1)')
            im51, = self.a6.plot([], [], 'o-', label='Winding Angle - (R1H2)')
            im52, = self.a6.plot([], [], 'o-', label='Winding Angle - (R1H3)')
            im53, = self.a6.plot([], [], 'o-', label='Winding Angle - (R1H4)')
            # ------ -----------------------------------------------Std Dev
            im54, = self.a12.plot([], [], 'o-', label='Winding Angle')
            im55, = self.a12.plot([], [], 'o-', label='Winding Angle')
            im56, = self.a12.plot([], [], 'o-', label='Winding Angle')
            im57, = self.a12.plot([], [], 'o-', label='Winding Angle)')

        # ------------------------------------------------------
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Activate Matplot tools ----------------[Uncomment to activate]
        # self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        # self.toolbar.update()
        # self.canvas._tkcanvas.pack(expand=True)

        # --------- call data block -------------------------------------#
        threading.Thread(target=self.dataControlEoL, daemon=True).start()
        # ---------------- EXECUTE SYNCHRONOUS METHOD -------------------------#

    def dataControlEoL(self):
        global layerN, msctcp, sysRun, batch_EoL, viz_con, s_fetch

        batch_EoL = 1
        s_fetch, stp_Sz = 100, 1  # 100 data points per Pipe's 1 meter length

        # Initialise SQL Data connection per listed Table --------------------[]
        if self.running and UseSQL_DBS:
            print('\n[EoL VIz] Connecting to surrogate model...')
            viz_con = sq.eolViz_connect()
        else:
            pass
        """
        Load watchdog function with synchronous function every seconds
        """
        import keyboard                                         # for temporary use

        # Define PLC/SMC error state ----------------------------------------------------#
        import sqlArray_EoL_VizReport as sel
        paused = False
        sysRun = False
        msctcp = 0

        while True:
            print('[\nEOL Viz] now running....')
            if uCalling == 1:                                           # Running Live Analysis
                sysRun, sysIdl, sysRdy, msc_rt, cLayer, pipPos, mstatus = wd.autoPausePlay()

                if not sysRun and not paused or sysIdl or sysRdy:
                    print('\n[EoL] Production is pausing...')
                    paused = True

                    while paused:
                        time.sleep(5)
                        print("\n[EoL Viz] Visualization in Paused Mode...")
                        sysRun, msctcp, msc_rt, cLayr = wd.rt_autoPausePlay()
                        if sysRun:
                            paused = False
                            print('[EoL] Visualisation Resumes...')
                        time.sleep(0.2)

                # Activate End of Layer Report ------------------------------------------#
                elif not sysRun and msc_rt == 49728 or msc_rt == 49712 or msc_rt == 49664:
                    layerN = cLayer
                    if not pdf_layer:
                        pdf_layer.append(layerN)  # start at layer 1
                    if len(pdf_layer) > 1:
                        layerN = pdf_layer[-2]
                    else:
                        layerN = pdf_layer[0]
                    # Trigger EoL report -- Verify MSC State machine Code update
                    layerProcess(layerN)

                elif not sysRun and msc_rt == 59776:            # End of Pipe lay
                    # trigger EoP Report                        # TODO Wrapp up this method asap.
                    continue                                    # keep looping on the spot until operator action

                else:
                    layerN = cLayer
                    print('[EoL Viz] Visualisation in progress, please wait....')
                    self.rpTT, self.rpST, self.rpTG, self.rpWS = sel.dnv_sqlExec(viz_con, s_fetch, stp_Sz, self.T1,
                                                                                 self.T2, self.T3, self.T4, batch_EoL)
                    time.sleep(10)  # pools 100dp of data every 10 seconds. Equivalent to 1mtr @ 6mt/min & 10hz

            elif uCalling == 2 or uCalling == 3:
                if keyboard.is_pressed("Alt+Q"):
                    paused = True

                    while paused:
                        time.sleep(5)
                        print("\n[EoL Viz] Visualization in Paused Mode...")
                        if keyboard.is_pressed("esc"):
                            paused = False
                            print('[EoL Viz] Visualisation Resumes...')
                        time.sleep(0.2)
                else:
                    print('[EoL Viz] Visualisation in progress, please wait....')
                    self.rpTT, self.rpST, self.rpTG, self.rpWS = sel.dnv_sqlExec(viz_con, s_fetch, stp_Sz, self.T1,
                                                                                 self.T2, self.T3, self.T4, batch_EoL)
                    time.sleep(10)  # pools 100dp of data every 10 seconds. Equivalent to 1mtr @ 6mt/min & 10hz

                    if keyboard.is_pressed("Alt+Q"):
                        viz_con.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

            if viz_con:
                self.canvas.get_tk_widget().after(0, self.eolDataPlot)
                batch_EoL += 1
            else:
                print('[EoL Viz] sorry, instance not granted, trying again..')
                viz_con = sq.check_SQL_Status(3, 30)
            print('[EoL Viz] Waiting for refresh..')

    # ================== End of synchronous Method =========================================[]
    def eolDataPlot(self):
        timei = time.time()  # start timing the entire loop

        # sliding window -------
        lastLayer = 1 # pdf_layer[0]
        regm1, regm2, regm3, regm4 = 0.3, 0.3, 0.3, 0.3
        # --------------------------------------------------# , , ,
        # declare asynchronous variables ------------------[]
        if UseSQL_DBS or UsePLC_DBS:
            import VarSQL_EoLTT as rptt
            import VarSQL_EoLST as rpst
            import VarSQL_EoLTG as rptg
            import VarSQL_EoLWS as rpws
            # load SQL variables column names | rfVarSQL

            g1 = ott.validCols(self.T1)                          # Construct Table Column (Tape Temp)
            d1 = pd.DataFrame(self.rpTT, columns=g1)
            print('\nFetched In:', d1.shape[0])
            if d1.shape[0] >= s_fetch * 2:
                d1.drop(d1.index[0:s_fetch])
            print('Fetched Out:', len(d1), d1.shape[0])
            # Setting a Seed for Random Reproducibility --[ Seed of 9, FYI:TP]
            d1 = d1.sample(frac=regm1, axis='rows', random_state=9) # Do random sapling
            zTT = rptt.loadProcesValues(d1)
            tt_wsize = int(d1.shape[0] * regm1)
            # print('\n[EoL TT Viz] Content', d1.head(10))

            g2 = ost.validCols(self.T2)                          # Construct Table Column (Sub Temp)
            d2 = pd.DataFrame(self.rpST, columns=g2)
            if d2.shape[0] >= s_fetch * 2:
                d2.drop(d2.index[0:s_fetch])
            # Setting a Seed for Random Reproducibility --[ Seed of 9, FYI:TP]
            d2 = d2.sample(frac=regm2, axis='rows', random_state=9)
            zST = rpst.loadProcesValues(d2)
            st_wsize = int(d2.shape[0] * regm2)
            # print('\n[EoL ST Viz] Content', d2.head(10))

            g3 = otg.validCols(self.T3)                          # Construct Table Column (Tape Gap)
            d3 = pd.DataFrame(self.rpTG, columns=g3)
            if d3.shape[0] >= s_fetch * 2:
                d3.drop(d3.index[0:s_fetch])
            # Setting a Seed for Random Reproducibility --[ Seed of 9, FYI:TP]
            d3 = d3.sample(frac=regm3, axis='rows', random_state=9)
            zTG = rptg.loadProcesValues(d3)
            tg_wsize = int(d3.shape[0] * regm3)
            # print('\n[EoL TG Viz] Content', d3.head(10))

            g4 = ows.validCols(self.T4)                             # Construct Table Column (Tape Gap)
            d4 = pd.DataFrame(self.rpWS, columns=g4)                # EoL_reached > 0 or layerN
            if d4.shape[0] >= s_fetch * 2:
                d4.drop(d4.index[0:s_fetch])
            # Setting a Seed for Random Reproducibility --[ Seed of 9, FYI:TP]
            d4 = d4.sample(frac=regm4, axis='rows', random_state=9)
            zWS = rpws.loadProcesValues(d4)
            ws_wsize = int(d4.shape[0] * regm4)
            # Concatenate all columns ----------------------[]
            print('\nNew Windows Samples:', tt_wsize, st_wsize, tg_wsize, ws_wsize)
            # update layer count number on PPA Mode --------[]
            if zTT[1].any() > 1 and uCalling == 3 or uCalling == 2:
                pdf_layer[1].append(zTT[1].any())
            else:
                pass
        else:
            zTT = 0
            zST = 0
            zTG = 0
            zWS = 0
            print('[EoL] Unknown Protocol...')

        if self.running:
            _fetch = 30
            self.a1.legend(loc='upper right', title='Tape Temp')
            self.a5.legend(loc='upper right', title='Sigma')
            self.a2.legend(loc='upper right', title='Sub Temp')
            self.a6.legend(loc='upper right', title='Sigma')
            self.a3.legend(loc='upper right', title='Tape Gap')
            self.a7.legend(loc='upper right', title='Sigma')
            self.a4.legend(loc='upper right', title='Winding Speed')
            self.a8.legend(loc='upper right', title='Sigma')

            # ---------------------------------------------------------------[]
            im10.set_xdata(np.arange(batch_EoL))
            im11.set_xdata(np.arange(batch_EoL))
            im12.set_xdata(np.arange(batch_EoL))
            im13.set_xdata(np.arange(batch_EoL))
            im14.set_xdata(np.arange(batch_EoL))
            im15.set_xdata(np.arange(batch_EoL))
            im16.set_xdata(np.arange(batch_EoL))
            im17.set_xdata(np.arange(batch_EoL))
            im18.set_xdata(np.arange(batch_EoL))
            im19.set_xdata(np.arange(batch_EoL))
            im20.set_xdata(np.arange(batch_EoL))
            im21.set_xdata(np.arange(batch_EoL))
            im22.set_xdata(np.arange(batch_EoL))
            im23.set_xdata(np.arange(batch_EoL))
            im24.set_xdata(np.arange(batch_EoL))
            im25.set_xdata(np.arange(batch_EoL))
            # ------------------------------- S Plot TT
            im26.set_xdata(np.arange(batch_EoL))
            im27.set_xdata(np.arange(batch_EoL))
            im28.set_xdata(np.arange(batch_EoL))
            im29.set_xdata(np.arange(batch_EoL))
            im30.set_xdata(np.arange(batch_EoL))
            im31.set_xdata(np.arange(batch_EoL))
            im32.set_xdata(np.arange(batch_EoL))
            im33.set_xdata(np.arange(batch_EoL))
            im34.set_xdata(np.arange(batch_EoL))
            im35.set_xdata(np.arange(batch_EoL))
            im36.set_xdata(np.arange(batch_EoL))
            im37.set_xdata(np.arange(batch_EoL))
            im38.set_xdata(np.arange(batch_EoL))
            im39.set_xdata(np.arange(batch_EoL))
            im40.set_xdata(np.arange(batch_EoL))
            im41.set_xdata(np.arange(batch_EoL))
            # ------------------------------- X Plot ST
            if pRecipe == 'MGM':
                im42.set_xdata(np.arange(batch_EoL))
                im43.set_xdata(np.arange(batch_EoL))
                im44.set_xdata(np.arange(batch_EoL))
                im45.set_xdata(np.arange(batch_EoL))
                im46.set_xdata(np.arange(batch_EoL))
                im47.set_xdata(np.arange(batch_EoL))
                im49.set_xdata(np.arange(batch_EoL))
                im50.set_xdata(np.arange(batch_EoL))
                im51.set_xdata(np.arange(batch_EoL))
                im52.set_xdata(np.arange(batch_EoL))
                im53.set_xdata(np.arange(batch_EoL))
                im54.set_xdata(np.arange(batch_EoL))
                im55.set_xdata(np.arange(batch_EoL))
                im56.set_xdata(np.arange(batch_EoL))
                im56.set_xdata(np.arange(batch_EoL))
                im57.set_xdata(np.arange(batch_EoL))
            # ------------------------------- S Plot ST
            if pRecipe == 'DNV':
                # X Plot Y-Axis data points for XBar --------[ Mean TT ]
                im10.set_ydata((zTT[3]).rolling(window=_fetch, min_periods=1).mean()[0:batch_EoL])  # head 1
                im11.set_ydata((zTT[5]).rolling(window=_fetch, min_periods=1).mean()[0:batch_EoL])  # head 2
                im12.set_ydata((zTT[7]).rolling(window=_fetch, min_periods=1).mean()[0:batch_EoL])  # head 3
                im13.set_ydata((zTT[9]).rolling(window=_fetch, min_periods=1).mean()[0:batch_EoL])  # head 4
                # ----------------------------------
                im14.set_ydata((zTT[3]).rolling(window=_fetch, min_periods=1).std()[0:batch_EoL])  # head 1
                im15.set_ydata((zTT[5]).rolling(window=_fetch, min_periods=1).std()[0:batch_EoL])  # head 2
                im16.set_ydata((zTT[7]).rolling(window=_fetch, min_periods=1).std()[0:batch_EoL])  # head 3
                im17.set_ydata((zTT[9]).rolling(window=_fetch, min_periods=1).std()[0:batch_EoL])  # head 4
                # ------------------ Substrate Temperature ----[ ST ]
                im18.set_ydata((zST[3]).rolling(window=_fetch, min_periods=1).mean()[0:batch_EoL])  # head 1
                im19.set_ydata((zST[5]).rolling(window=_fetch, min_periods=1).mean()[0:batch_EoL])  # head 2
                im20.set_ydata((zST[7]).rolling(window=_fetch, min_periods=1).mean()[0:batch_EoL])  # head 3
                im21.set_ydata((zST[9]).rolling(window=_fetch, min_periods=1).mean()[0:batch_EoL])  # head 4
                # ---------------------------------
                im22.set_ydata((zST[3]).rolling(window=_fetch, min_periods=1).std()[0:batch_EoL])  # head 1
                im23.set_ydata((zST[5]).rolling(window=_fetch, min_periods=1).std()[0:batch_EoL])  # head 3S
                im24.set_ydata((zST[7]).rolling(window=_fetch, min_periods=1).std()[0:batch_EoL])  # head 3
                im25.set_ydata((zST[9]).rolling(window=_fetch, min_periods=1).std()[0:batch_EoL])
                # ------------------ Tape Gap Polarisation ---

                im26.set_ydata((zTG[3]).rolling(window=_fetch).mean()[0:batch_EoL])  # head 1
                im27.set_ydata((zTG[5]).rolling(window=_fetch).mean()[0:batch_EoL])  # head 2
                im28.set_ydata((zTG[7]).rolling(window=_fetch).mean()[0:batch_EoL])  # head 3
                im29.set_ydata((zTG[9]).rolling(window=_fetch).mean()[0:batch_EoL])  # head 4
                # ---------------------------------------
                im30.set_ydata((zTG[3]).rolling(window=_fetch).std()[0:batch_EoL])  # head 1
                im31.set_ydata((zTG[5]).rolling(window=_fetch).std()[0:batch_EoL])  # head 2
                im32.set_ydata((zTG[7]).rolling(window=_fetch).std()[0:batch_EoL])  # head 3
                im33.set_ydata((zTG[9]).rolling(window=_fetch).std()[0:batch_EoL])
                # ---------------------------------------[Winding Speed S]
                im34.set_ydata((zWS[3]).rolling(window=_fetch).mean()[0:batch_EoL])
                im35.set_ydata((zWS[5]).rolling(window=_fetch).mean()[0:batch_EoL])
                im36.set_ydata((zWS[7]).rolling(window=_fetch).mean()[0:batch_EoL])
                im37.set_ydata((zWS[9]).rolling(window=_fetch).mean()[0:batch_EoL])
                # ------------------------------------------
                im38.set_ydata((zWS[3]).rolling(window=_fetch).std()[0:batch_EoL])
                im39.set_ydata((zWS[5]).rolling(window=_fetch).std()[0:batch_EoL])
                im40.set_ydata((zWS[7]).rolling(window=_fetch).std()[0:batch_EoL])
                im41.set_ydata((zWS[9]).rolling(window=_fetch).std()[0:batch_EoL])

            # ------------------------------------------------------ Std Dev
            if batch_EoL > self.win_Xmax:
                self.a1.set_xlim(batch_EoL - self.win_Xmax, batch_EoL)
                self.a2.set_xlim(batch_EoL - self.win_Xmax, batch_EoL)
                self.a3.set_xlim(batch_EoL - self.win_Xmax, batch_EoL)
                self.a4.set_xlim(batch_EoL - self.win_Xmax, batch_EoL)
                self.a5.set_xlim(batch_EoL - self.win_Xmax, batch_EoL)
                self.a6.set_xlim(batch_EoL - self.win_Xmax, batch_EoL)
                self.a7.set_xlim(batch_EoL - self.win_Xmax, batch_EoL)
                self.a8.set_xlim(batch_EoL - self.win_Xmax, batch_EoL)
                zTT.pop(0)
                zST.pop(0)
                zTG.pop(0)
                zWS.pop(0)
            else:
                self.a1.set_xlim(0, self.win_Xmax)
                self.a2.set_xlim(0, self.win_Xmax)
                self.a3.set_xlim(0, self.win_Xmax)
                self.a4.set_xlim(0, self.win_Xmax)
                self.a5.set_xlim(0, self.win_Xmax)
                self.a6.set_xlim(0, self.win_Xmax)
                self.a7.set_xlim(0, self.win_Xmax)
                self.a8.set_xlim(0, self.win_Xmax)
            self.canvas.draw_idle()
        else:
            if pRecipe == 'MGM':
                self.a1.text(0.200, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left', transform=self.a1.transAxes)
                self.a2.text(0.200, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left', transform=self.a2.transAxes)
                self.a3.text(0.200, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left', transform=self.a3.transAxes)
                self.a4.text(0.200, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left', transform=self.a4.transAxes)
                self.a5.text(0.200, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left', transform=self.a5.transAxes)
                self.a6.text(0.200, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left', transform=self.a6.transAxes)
                self.a7.text(0.200, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left', transform=self.a7.transAxes)
                self.a8.text(0.200, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left', transform=self.a8.transAxes)
                # ---------
                self.a9.text(0.200, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left', transform=self.a9.transAxes)
                self.a10.text(0.200, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left', transform=self.a10.transAxes)
                self.a11.text(0.200, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left', transform=self.a11.transAxes)
                self.a12.text(0.200, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left', transform=self.a12.transAxes)
            else:
                self.a1.text(0.355, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left', transform=self.a1.transAxes)
                self.a2.text(0.355, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left', transform=self.a2.transAxes)
                self.a3.text(0.355, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left', transform=self.a3.transAxes)
                self.a4.text(0.355, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left', transform=self.a4.transAxes)
                self.a5.text(0.355, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left', transform=self.a5.transAxes)
                self.a6.text(0.355, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left', transform=self.a6.transAxes)
                self.a7.text(0.355, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left', transform=self.a7.transAxes)
                self.a8.text(0.355, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left', transform=self.a8.transAxes)
        timef = time.time()
        lapsedT = timef - timei
        print(f"[EoL] Process Interval: {lapsedT} sec\n")
        # -----Canvas update --------------------------------------------[]


# ------- Defines the collective screen structure ------------------------[EOP Reports]
class collectiveEoP(ttk.Frame):                                # End of Layer Progressive Report Tabb
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.running = True

        # prevents user possible double loading -----
        if not self.running:
            self.running = True
            threading.Thread(target=self.createEoPViz, daemon=True).start()


def createEoPViz(self):
        label = ttk.Label(self, text="End of Pipe Report", font=LARGE_FONT)
        label.place(x=400, y=10)

        # Define Axes ----------------------------------#
        self.fig = Figure(figsize=(pMtX - 9.5, 7.21), dpi=100)        # 12.5, 7.22, 18
        self.fig.subplots_adjust(left=0.04, bottom=0.033, right=0.983, top=0.957, hspace=0.14, wspace=0.033)
        # ---------------------------------[]
        self.a1 = self.fig.add_subplot(2, 3, (1, 3))              # X Bar Plot
        self.a2 = self.fig.add_subplot(2, 3, (4, 6))              # S Bar Plot

        # Declare Plots attributes ---------------------[]
        plt.rcParams.update({'font.size': 7})           # Reduce font size to 7pt for all legends

        # Calibrate limits for X-moving Axis -----------#
        YScale_minRF, YScale_maxRF = 10, 500
        sBar_minRF, sBar_maxRF = 10, 250                # Calibrate Y-axis for S-Plot
        self.win_Xmin, self.win_Xmax = 0, 30                # windows view = visible data points

        # Common properties ------------------------#
        self.a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        self.a2.set_ylabel("Sample Deviation [" + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        self.a1.set_title('[XBar Plot]', fontsize=12, fontweight='bold')
        self.a2.set_title('[SDev Plot]', fontsize=12, fontweight='bold')

        # Apply grid lines ------------------------------
        self.a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        self.a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        self.a1.legend(loc='upper right', title='Mean curve')
        self.a2.legend(loc='upper right', title='Sigma curve')

        # ----------------------------------------------------------#
        self.a1.set_ylim([YScale_minRF, YScale_maxRF], auto=True)
        self.a1.set_xlim([self.win_Xmin, self.win_Xmax])
        # ----------------------------------------------------------#
        self.a2.set_ylim([sBar_minRF, sBar_maxRF], auto=True)
        self.a2.set_xlim([self.win_Xmin, self.win_Xmax])
        # ----------------------------------------------------------[]
        # Define Plot area and axes -
        # ----------------------------------------------------------#
        im10, = self.a1.plot([], [], 'o-', label='Roller Force - (R1H1)')
        im11, = self.a1.plot([], [], 'o-', label='Roller Force - (R1H2)')
        im12, = self.a1.plot([], [], 'o-', label='Roller Force - (R1H3)')
        im13, = self.a1.plot([], [], 'o-', label='Roller Force - (R1H4)')
        im14, = self.a2.plot([], [], 'o-', label='Roller Force')
        im15, = self.a2.plot([], [], 'o-', label='Roller Force')
        im16, = self.a2.plot([], [], 'o-', label='Roller Force')
        im17, = self.a2.plot([], [], 'o-', label='Roller Force')

        # Define dropdown List ---------------------#
        combo = ttk.Combobox(self, values=["= Select Process Parameter =", "Roller Force",
                                           "Tape Temperature", "Subs Temperature", "Laser Power",
                                           "Laser Angle", "Tape Placement Error",
                                           "Tape Gap Polarisation"], width=25)
        combo.place(x=385, y=30)
        combo.current(0)

        # Create empty Text Space -----------------------------------
        self.text_widget = tk.Text(self, wrap='word', width=110, height=47)  # 110 | 70
        self.text_widget.pack(padx=10, pady=50, side=tk.LEFT)
        # text_widget.place(x=10, y=10)

        # ---------------------------------------------------------[]
        def option_selected(event):
            selected_option = combo.get()
            if selected_option == "Roller Force":
                label = ttk.Label(self, text='Roller Force', width=16, font=14, background='#fff') #, justify='center')
                label.place(x=1540, y=54)

                rpt = "RPT_RF_" + str(pWON)
                readEoP(self.text_widget, rpt)                              # Open txt file from FMEA folder

            elif selected_option == "Tape Temperature":
                label = ttk.Label(self, text='Tape Temperature', width=16, background='#fff', font=14)
                label.place(x=1540, y=54)

                rpt = "RPT_TT_" + str(pWON)
                readEoP(self.text_widget, rpt)                              # Open txt file from FMEA folder

            elif selected_option == "Subs Temperature":
                label = ttk.Label(self, text='Subs Temperature', width=16, background='#fff', font=14)
                label.place(x=1540, y=54)

                rpt = "RPT_ST_" + str(pWON)
                readEoP(self.text_widget, rpt)                               # Open txt file from FMEA folder

            elif selected_option == "Laser Power":
                label = ttk.Label(self, text='Laser Power', width=16, background='#fff', font=14)
                label.place(x=1540, y=54)

                rpt = "RPT_LP_" + str(pWON)
                readEoP(self.text_widget, rpt)                                 # Open txt file from FMEA folder

            elif selected_option == "Laser Angle":
                label = ttk.Label(self, text='Laser Angle', width=16, background='#fff', font=14)
                label.place(x=1540, y=54)

                rpt = "RPT_LA_" + str(pWON)
                readEoP(self.text_widget, rpt)                                 # Open txt file from FMEA folder

            elif selected_option == "Tape Placement Error":
                label = ttk.Label(self, text='Tape Placement', width=16, background='#fff', font=14)
                label.place(x=1540, y=54)

                rpt = "RPT_TP_" + str(pWON)
                readEoP(self.text_widget, rpt)                                 # Open txt file from FMEA folder

            elif selected_option == "Tape Gap Polarisation":
                label = ttk.Label(self, text='Gap Measurement', width=16, background='#fff', font=14)
                label.place(x=1540, y=54)

                rpt = "RPT_TG_" + str(pWON)
                readEoP(self.text_widget, rpt)                                 # Open txt file from FMEA folder

            else:
                label = ttk.Label(self, text=' ')
                label.place(x=1540, y=54)

                rpt = "VOID_REPORT"
                readEoP(self.text_widget, rpt)

            print("You selected:", selected_option)
        combo.bind("<<ComboboxSelected>>", option_selected)

        # Update Canvas -----------------------------------------------------[NO FIGURE YET]
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(expand=True)    #01

        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        self.canvas._tkcanvas.pack(expand=True)

# ---------------------------- End of Collective Reporting Functions ----------------------------[]

#     ********   These set of functions defines the common canvas Area  *******************
# ---------------------------------- COMMON VIEW CLASS OBJECTS ---------[Ramp Count Plot]
class common_rampCount(ttk.Frame):
    # compute ram Count against cumulative layers ramp count --------[A]
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=20)
        self.running = False

        # prevents user possible double loading -----
        if not self.running:
            self.running = True
            threading.Thread(target=self.createCommonRC, daemon=True).start()
            print('[cRC] is now running....')


    def createCommonRC(self):
        global rcT
        # ---------------------------------------------------------[]

        self.f = Figure(figsize=(scrX, 4), dpi=100)
        self.f.subplots_adjust(left=0.083, bottom=0.11, right=0.976, top=0.99, wspace=0.202)
        self.a1 = self.f.add_subplot(1, 1, 1)

        # Model data -----------------------------------------------[]
        # self.a1.cla()
        self.a1.get_yaxis().set_visible(True)
        self.a1.get_xaxis().set_visible(True)

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 9})                       # Reduce font size to 7pt for all legends

        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minRC, YScale_maxRC = 0, 1000                        # vCount# Ramp Count Profile (Per segment)
        self.win_XminRC, self.win_XmaxRC = 0, 10                    # windows view = visible data points

        # Load SQL Query Table -------------------------------------#
        # self.T1 = 'RC_' + str(pWON) # replaced / switched to
        self.T1 = 'RM_' + str(pWON)
        # ----------------------------------------------------------#
        self.a1.xaxis.set_major_locator(MultipleLocator(1))
        self.a1.legend(["Layer Ramp Count"], loc='upper right', fontsize="x-large")
        self.a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        self.a1.set_xlabel("Pipe Segment")
        self.a1.set_ylabel("Ramp Count")

        # ----------------------------------------------------------#
        self.a1.set_ylim([YScale_minRC, YScale_maxRC], auto=True)
        self.a1.set_xlim([self.win_XminRC, self.win_XmaxRC], auto=True)

        # ------- plot ramp count ------------[]
        self.im10, = self.a1.plot([], [], 'o-', label='Total Ramp')                  # ramp count all layers
        # self.im11, = self.a1.plot([], [], 'o-', label='Ring 2 Ramp')                  # ramp count all layers
        # self.im12, = self.a1.plot([], [], 'o-', label='Ring 3 Ramp')                  # ramp count all layers
        # self.im13, = self.a1.plot([], [], 'o-', label='Ring 4 Ramp')                  # ramp count all layers
        # self.im14, = self.a1.plot([], [], 'o-', label='Cumulative')                  # ramp count all layers

        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Activate Matplot tools ------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(self.canvas, self)
        # toolbar.update()
        # self.canvas._tkcanvas.pack(expand=True)

        # --------- call data block --------------
        threading.Thread(target=self.dataControlRC, daemon=True).start()
        # ---------------- EXECUTE SYNCHRONOUS METHOD --------------#

    def dataControlRC(self):           #  data_worker
        global batch_RC, s_fetch

        batch_RC = 1
        s_fetch, stp_Sz = 300, 1        # entry value in string sql syntax

        # Obtain Volatile Data from sql Host Server ---------------------------[]
        if self.running:
            import sqlArrayRLmethodRM as rmp
            rc_con = sq.sql_connectRC()
        else:
            pass

        # Evaluate conditions for SQL Data Fetch ------------------------------[A]
        """
        Load watchdog function with synchronous function every seconds
        """
        # Initialise RT variables ---[]
        autoSpcRun = True
        paused = False
        import keyboard                     # for temporary use

        while True:
            # This procedure must be valid either on PLC/SQL baseed runtime
            if UseSQL_DBS and self.running and rc_con:
                print('\n[cRC] Asynchronous controller activated...')

                if uCalling == 1:
                    sysRun, msctcp, msc_rt, cLayr = wd.rt_autoPausePlay()

                    if not sysRun and not paused:
                        print('\n[cRC] Production is pausing...')
                        paused = True

                        while paused:
                            time.sleep(5)
                            print("\n[cRC Viz] Visualization in Paused Mode...")
                            sysRun, msctcp, msc_rt, cLayr = wd.rt_autoPausePlay()
                            if sysRun:
                                paused = False
                                print('[cRC] Visualisation Resumes...')
                            time.sleep(0.2)
                    else:
                        # Get list of relevant SQL Tables using conn() --------------------[]
                        self.rcP = rmp.sqlExec(rc_con, s_fetch, stp_Sz, self.T1, batch_RC)
                        time.sleep(30)

                elif uCalling == 2 or uCalling == 3:
                    if keyboard.is_pressed("Alt+Q"):
                        paused = True

                        while paused:
                            time.sleep(5)
                            print("\n[cRC Viz] Visualization in Paused Mode...")
                            if keyboard.is_pressed("esc"):
                                paused = False
                                print('[cRC] Visualisation Resumes...')
                            time.sleep(0.2)

                    else:
                        # Get list of relevant SQL Tables using conn() --------------------[]
                        self.rcP = rmp.sqlExec(rc_con, s_fetch, stp_Sz, self.T1, batch_RC)
                        time.sleep(30)

                        # ------ Inhibit iteration -----rm_con---------------------------------[]
                        if not self.rcP:  # Terminate file-fetch

                            print('[cRC] End of File, connection closes after 30 mins...')
                            time.sleep(60)
                            rc_con.close()
                            continue
                        else:
                            print('\n[cRC] Updating....')

                if rc_con:
                    self.canvas.get_tk_widget().after(0, self.rcDataPlot) # Regime = every 10000 ms = 10seconds
                    batch_RC += 1
                else:
                    print('[cRC] sorry, instance not granted, trying again..')
                    rc_con = sq.check_SQL_Status(5, 40)
            else:
                print('\n[cRC] is active but no visualisation!')
            print('[cRC] Waiting for refresh..')

    # ================== End of synchronous Method ==========================obal

    def rcDataPlot(self):
        timei = time.time()                                 # start timing the entire loop

        # Call data loader Method---------------------------#
        import VarSQL_RM as rmp                             # load SQL variables column names | rfVarSQL
        g1 = qrm.validCols(self.T1)                         # Construct Data Column selSqlColumnsTFM.py
        df1 = pd.DataFrame(self.rcP, columns=g1)            # Import into python Dataframe
        # ------------------------------------------
        data1 = df1.select_dtypes(include=["number"])
        df1 = data1.interpolate(method="linear", axis=0).ffill().bfill()  # column-wise
        # -----------------------------------------
        # var_plyr = df1["cLayer"][-1:]             # not a scalar value
        var_plyr = df1["cLayer"].iloc[-1]           # most efficient
        # var_plyr = df1["cLayer"].values[-1]       # valid
        # var_plyr = df1["cLayer"].tail(1).item()   # valid
        # ----------------------------------------
        # print('\nProcessing Layer:', var_plyr)
        # uPosA = df1[(df1["cLayer"] == var_plyr) & (df1["R1Pos"] > 0) & (df1["sCentre"] > 0)]["R1Pos"].value_counts()
        # uPosB = df1[(df1["cLayer"] == var_plyr) & (df1["R2Pos"] > 0) & (df1["sCentre"] > 0)]["R2Pos"].value_counts()
        # uPosC = df1[(df1["cLayer"] == var_plyr) & (df1["R3Pos"] > 0) & (df1["sCentre"] > 0)]["R3Pos"].value_counts()
        # uPosD = df1[(df1["cLayer"] == var_plyr) & (df1["R4Pos"] > 0) & (df1["sCentre"] > 0)]["R4Pos"].value_counts()
        # --------- Enable above method when Table is updated with sCentre column ----
        uPosA = df1[(df1["cLayer"] == var_plyr) & (df1["R1Pos"] > 0)].shape[0]
        uPosB = df1[(df1["cLayer"] == var_plyr) & (df1["R2Pos"] > 0)].shape[0]
        uPosC = df1[(df1["cLayer"] == var_plyr) & (df1["R3Pos"] > 0)].shape[0]
        uPosD = df1[(df1["cLayer"] == var_plyr) & (df1["R4Pos"] > 0)].shape[0]
        # print('\nComputed Values:', uPosA, uPosB, uPosC, uPosD)
        # print('\nComputed lengths:', len(uPosA), len(uPosB), len(uPosC), len(uPosD))

        RC = rmp.loadProcesValues(df1)  # Join data values under dataframe
        # print('\n[RC] Content', df1.tail())

        if self.running:
            # ------- plot ramp count ----------------------------------#
            self.a1.legend(loc='upper right', title='Cumulative Ramp Count')
            # ----------------------------------------------------------[]
            # Plot X-Axis data points -------- X Plot
            self.im10.set_xdata(np.arange(batch_RC))
            # self.im11.set_xdata(np.arange(batch_RC))
            # self.im12.set_xdata(np.arange(batch_RC))
            # self.im13.set_xdata(np.arange(batch_RC))

            # X Plot Y-Axis data points for XBar --------------------------------------------[Ring 1]
            # self.im10.set_ydata(uPosA)  # .rolling(window=s_fetch).mean().dropna()) #[0:batch_RC])  # head 1
            # self.im11.set_ydata(uPosB)  #.rolling(window=s_fetch).mean().dropna()) #[0:batch_RC]) # head 1
            # self.im12.set_ydata(uPosC)  #.rolling(window=s_fetch).mean().dropna()) #[0:batch_RC])  # head 1
            # self.im13.set_ydata(uPosD)  #.rolling(window=s_fetch).mean().dropna()) #[0:batch_RC])  # head 1
            # -----------------------Layer
            self.im10.set_ydata(RC[0].rolling(window=s_fetch, min_periods=1).mean()[0:batch_RC])
            # self.im11.set_ydata(RC[0].rolling(window=s_fetch, min_periods=1).mean()[0:batch_RC])
            # self.im12.set_ydata(RC[0].rolling(window=s_fetch, min_periods=1).mean()[0:batch_RC])
            # self.im13.set_ydata(RC[0].rolling(window=s_fetch, min_periods=1).sum()[0:batch_RC])

            # Setting up the parameters for moving windows Axes --[]
            if batch_RC > self.win_XmaxRC:
                self.a1.set_xlim(batch_RC - self.win_XmaxRC, batch_RC)
                RC.pop(0)
            else:
                self.a1.set_xlim(0, self.win_XmaxRC)
            print('[cRC] Data Stream Buffer Size 2:', len(RC))
            self.canvas.draw_idle()

        else:
            print('[cRC] standby mode, no active session...')
            self.a1.text(0.355, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left', transform=self.a1.transAxes)

        timef = time.time()
        lapsedT = timef - timei
        print(f"[cRC] Process Interval: {lapsedT} sec\n")
        # -----Canvas update --------------------------------------------[]


# ---------------------------------- COMMON VIEW CLASS OBJECTS ------[Climatic Variables]
class common_climateProfile(ttk.Frame):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=pEvX, y=20)     # 915
        self.running = False

        # prevents user possible double loading -----
        if not self.running:
            self.running = True
            threading.Thread(target=self.createCommonEV, daemon=True).start()
            print('[cEV] is now running....')

    def createCommonEV(self):
        global evT #, win_Xmin, win_Xmax, im10, im11, im12, im13, im14, im15, im16, im17, im18, im19, a1, a2, a3

        # -----------------------------------
        self.f = Figure(figsize=(scrX, 4), dpi=100)
        self.f.subplots_adjust(left=0.098, bottom=0.098, right=0.91, top=0.99, wspace=0.202) # 0.76
        self.a2 = self.f.add_subplot(1, 1, 1)

        # # Model data --------------------------------------------------[]
        self.a2.get_yaxis().set_visible(True)
        self.a2.get_xaxis().set_visible(True)

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 9})       # Reduce font size to 7pt for all legends

        # Calibrate limits for X-moving Axis -----------------------#
        self.minT, self.maxT = -126, 126            # Temperature Limits in (F)
        self.minH, self.maxH = -60, 120             # Relative Humidity
        self.win_Xmin, self.win_Xmax = 0, 32        # X - Axis range

        # Load SQL Query Table -------------------------------------#
        # if UseSQL_DBS:
        self.evT = 'EV_' + str(pWON)
        # else:
        #     self.evT = SPC_EV  # PLC Data
        # Environmental Values Reprocessed from SQL

        uvIndex = 3.6
        # ----------------------------------------------------------#
        self.a2.legend(["PO64PX E-Profile"], fontsize="x-large")
        self.a2.set_xlabel("Time Series")
        # ----------------------------------------------------------#
        self.a2.set_ylabel("Temperature [°C]", color='blue')
        self.a2.tick_params(axis='y', labelcolor='blue')
        self.a2.set_ylim(self.minT, self.maxT)

        self.a3 = self.a2.twinx()       # plot label opposite each axis

        self.a3.set_ylabel("Rel Humidity", color='red')
        self.a3.tick_params(axis='y', labelcolor='red')
        self.a3.set_ylim(self.minH, self.maxH)
        # ----------------------------------------------------------#
        self.im10, = self.a2.plot([], [], 'o-', label='Line 1 Temp', linewidth=0.4)
        self.im11, = self.a2.plot([], [], 'o-', label='Line 2 Temp', linewidth=0.4)
        self.im12, = self.a2.plot([], [], 'o-', label='Line 3 Temp', linewidth=0.4)
        self.im13, = self.a2.plot([], [], 'o-', label='Line 4 Temp', linewidth=0.4)
        self.im14, = self.a2.plot([], [], 'o-', label='Line 5 Temp', linewidth=0.4)

        self.im15, = self.a3.plot([], [], '--', label='Line 1 Humidity', linewidth=0.6)
        self.im16, = self.a3.plot([], [], '--', label='Line 2 Humidity', linewidth=0.6)
        self.im17, = self.a3.plot([], [], '--', label='Line 3 Humidity', linewidth=0.6)
        self.im18, = self.a3.plot([], [], '--', label='Line 4 Humidity', linewidth=0.6)
        self.im19, = self.a3.plot([], [], '--', label='Line 5 Humidity', linewidth=0.6)

        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(self.canvas, self)
        # toolbar.update()
        # self.canvas._tkcanvas.pack(expand=True)

        # --------- call data block --------------
        threading.Thread(target=self.dataControlEV, daemon=True).start()
        # ---------------- EXECUTE SYNCHRONOUS METHOD --------------#

    def dataControlEV(self):
        global frqC, s_fetch

        frqC = 1
        s_fetch, stp_Sz = 30, 1        # entry value in string sql syntax 30=14, 60=13,

        # Obtain SQL Data Host Server ---------------------------[]
        if self.running:                # Load CommsPlc class once
            ev_con = sq.sql_connectEV()
        else:
            pass

        # Evaluate conditions for SQL Data Fetch ---------------[A]
        """
        Load watchdog function with synchronous function every seconds
        """
        # Initialise RT variables ---[]
        autoSpcRun = True
        paused = False
        import keyboard  # for temporary use

        import sqlArrayRLmethodEV as sev

        while True:
            # procedure must be valid either on PLC/SQL based runtime
            if UseSQL_DBS and self.running and ev_con:
                print('\n[cEV] Asynchronous controller activated...')

                if uCalling == 1:
                    sysRun, msctcp, msc_rt, cLayr = wd.rt_autoPausePlay()

                    if not sysRun and not paused:
                        print('\n[cEV] Production is pausing...')
                        paused = True

                        while paused:
                            time.sleep(5)
                            print("\n[cEV Viz] Visualization in Paused Mode...")
                            sysRun, msctcp, msc_rt, cLayr = wd.rt_autoPausePlay()
                            if sysRun:
                                paused = False
                                print('[cEV] Visualisation Resumes...')
                            time.sleep(0.2)
                    else:
                        # Get list of relevant SQL Tables using conn() --------------------[]
                        self.evStr = sev.sqlExec(ev_con, s_fetch, stp_Sz, self.evT, frqC)
                        time.sleep(10)

                elif uCalling == 2 or uCalling == 3:
                    if keyboard.is_pressed("Alt+Q"):
                        paused = True

                        while paused:
                            time.sleep(5)
                            print("\n[cEV Viz] Visualization in Paused Mode...")
                            if keyboard.is_pressed("esc"):
                                paused = False
                                print('[cEV] Visualisation Resumes...')
                            time.sleep(0.2)
                    else:
                        # Get list of relevant SQL Tables using conn() --------------------[]
                        self.evStr = sev.sqlExec(ev_con, s_fetch, stp_Sz, self.evT, frqC)
                        time.sleep(10)
                        # ------ Inhibit iteration ----------------------------------------[
                        if  not self.evStr:  # Terminate file-fetch
                            ev_con.close()
                            print('[cEV] SQL End of File, connection closes after 30 mins...')
                            time.sleep(60)
                            continue
                        else:
                            print('\n[cEV] Updating....')

                if ev_con:
                    self.canvas.get_tk_widget().after(0, self.evDataPlot)  # Regime = every 5seconds
                    frqC += 1
                else:
                    print('[cEV] sorry, instance not granted, trying again..')
                    ev_con = sq.check_SQL_Status(5, 30)
            else:
                print('\n[cEV] is active but no visualisation!')
            print('[cEV] Waiting for refresh..')

    # ================== End of synchronous Method ===========================================================[]
    def evDataPlot(self):
        timei = time.time()                                 # start timing the entire loop

        # Call data loader Method---------------------------#
        import VarSQL_EV as ev                          # load SQL variables column names | rfVarSQL

        if self.running:
            g1 = qev.validCols(self.evT)                        # SQL Table
            df1 = pd.DataFrame(self.evStr, columns=g1)          # Import data into Dataframe

            data1 = df1.select_dtypes(include=["number"])
            df1 = data1.interpolate(method="linear", axis=0).ffill().bfill()  # column-wise

            EV = ev.loadProcesValues(df1)                       # Join data values under dataframe
            # print('\nDataFrame Content', df1.tail(10))          # Preview Data frame head
            # print("Memory Usage:", df1.info(verbose=False))   # Check memory utilization
            uvIndex = 3.0
            # ------- plot ramp count ----------------------------------#
            self.a2.legend(loc='upper left', title='PO64PX Climate Profile')
            self.a2.grid(color="0.5", linestyle='-', linewidth=0.5)

            self.a3.legend(loc='upper right', title="UV-Index:" + str(uvIndex))
            self.a3.grid(color="0.5", linestyle='-', linewidth=0.5)

            # --------------------------------
            # rRg = len(EV[1])    # 32,
            # Plot X-Axis data points -------- X Plot
            self.im10.set_xdata(np.arange(frqC))
            self.im11.set_xdata(np.arange(frqC))
            self.im12.set_xdata(np.arange(frqC))
            self.im13.set_xdata(np.arange(frqC))
            self.im14.set_xdata(np.arange(frqC))
            self.im15.set_xdata(np.arange(frqC))
            self.im16.set_xdata(np.arange(frqC))
            self.im17.set_xdata(np.arange(frqC))
            self.im18.set_xdata(np.arange(frqC))
            self.im19.set_xdata(np.arange(frqC))

            # X Plot Y-Axis data points for XBar --------------------------------------------[Ring 1]
            # im10.set_ydata((EV[2]).rolling(window=smp_Sz).mean()[0:db_freq])      # time stamp
            self.im10.set_ydata((EV[1]).rolling(window=s_fetch).mean()[0:frqC])           # oven tempA
            self.im11.set_ydata((EV[2]).rolling(window=s_fetch).mean()[0:frqC])           # oven temp B
            self.im12.set_ydata((EV[3]).rolling(window=s_fetch).mean()[0:frqC])           # Cell Rel Temperature
            self.im13.set_ydata((EV[4]).rolling(window=s_fetch).mean()[0:frqC])           # Cell Rel Humidity
            self.im14.set_ydata((EV[5]).rolling(window=s_fetch).mean()[0:frqC])           # Factory Dew Point Temp
            self.im15.set_ydata((EV[6]).rolling(window=s_fetch).mean()[0:frqC])           # Factory Humidity
            self.im16.set_ydata((EV[7]).rolling(window=s_fetch).mean()[0:frqC])           # Cell Rel Temperature
            self.im17.set_ydata((EV[8]).rolling(window=s_fetch).mean()[0:frqC])           # Cell Rel Humidity
            self.im18.set_ydata((EV[9]).rolling(window=s_fetch).mean()[0:frqC])           # Factory Dew Point Temp
            self.im19.set_ydata((EV[10]).rolling(window=s_fetch).mean()[0:frqC])
            # im20.set_ydata((CT[12]).rolling(window=smp_Sz).mean()[0:db_freq])  # UVIndex
            # step=smp_St

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if frqC > self.win_Xmax:
                self.a2.set_xlim(frqC - self.win_Xmax, frqC)
                # self.a3.set_xlim(frqC - self.win_Xmax, frqC)
                EV.pop(0)
            else:
                self.a2.set_xlim(0, self.win_Xmax)
                self.a3.set_xlim(0, self.win_Xmax)
            print('Data Stream Buffer Size 2:', len(EV))
            self.canvas.draw_idle()

        else:
            print('[cEV] standby mode, no active session...')
            self.a2.text(0.342, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left',  transform=self.a2.transAxes)
        timef = time.time()
        lapsedT = timef - timei
        print(f"[cEV] Process Interval: {lapsedT} sec\n")
        # -----Canvas update --------------------------------------------[]

# ---------------------------------- COMMON VIEW CLASS OBJECTS -----------[Gap Count Plot]
class common_gapCount(ttk.Frame):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=pTgX, y=20)
        self.running = False

        # prevents user possible double loading -----
        if not self.running:
            self.running = True
            threading.Thread(target=self.createCommonGC, daemon=True).start()
            print('[cVC] is now running....')

    def createCommonGC(self):
        global gcT
        # -----------------------------------
        self.f = Figure(figsize=(scrX, 4), dpi=100)   #w.h
        self.f.subplots_adjust(left=0.076, bottom=0.1, right=0.971, top=0.99, wspace=0.202)
        self.a3 = self.f.add_subplot(1, 1, 1)

        # Model data --------------------------------------------------[]
        self.a3.get_yaxis().set_visible(True)
        self.a3.get_xaxis().set_visible(True)

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 7})  # Reduce font size to 7pt for all legends

        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minVC, YScale_maxVC = 0, 1000
        self.win_Xmin, self.win_Xmax = 0, 10                         # windows view = visible data points

        # Load SQL Query Table -------------------------------------#
        # if UseSQL_DBS:
        self.gcT = 'VC_' + str(pWON)
        # ----------------------------------------------------------#
        self.a3.xaxis.set_major_locator(MultipleLocator(1))
        self.a3.legend(["Layer Void Count"], loc='upper right', fontsize="x-large")
        self.a3.grid(color="0.5", linestyle='-', linewidth=0.5)
        self.a3.set_xlabel("Pipe Segment")
        self.a3.set_ylabel("Void Count")

        # ----------------------------------------------------------#
        self.a3.set_ylim([YScale_minVC, YScale_maxVC], auto=True)
        self.a3.set_xlim([self.win_Xmin, self.win_Xmax])
        # ----------------------------------------------------------#
        self.im10, = self.a3.plot([], [], 'o-', label='Void Count Segment A')
        self.im11, = self.a3.plot([], [], 'o-', label='Void Count Segment B')
        self.im12, = self.a3.plot([], [], 'o-', label='Void Count Segment C')
        self.im13, = self.a3.plot([], [], 'o-', label='Void Count Segment D')
        # self.im14, = self.a3.plot([], [], 'o-', label='Cumulative Gap Count')

        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(self.canvas, self)
        # toolbar.update()
        # self.canvas._tkcanvas.pack(expand=True)

        # --------- call data block --------------
        threading.Thread(target=self.dataControlCgc, daemon=True).start()
        # ---------------- EXECUTE SYNCHRONOUS METHOD ---------------#

    def dataControlCgc(self):
        global batch_VC, s_fetch

        batch_VC = 1
        s_fetch, stp_Sz = 300, 1  # entry value in string sql syntax

        # Obtain SQL Data Host Server ---------------------------[]
        if self.running:                          # Load CommsPlc class once
            import sqlArrayRLmethodVC as svc
            gc_con = sq.sql_connectVC()
        else:
            gc_con = None

        # Evaluate conditions for SQL Data Fetch ---------------[A]
        """
        Load watchdog function with synchronous function every seconds
        """
        # Initialise RT variables ---[]
        sysRun = False
        paused = False
        import keyboard  # for temporary use

        while True:
            if UseSQL_DBS and self.running and gc_con:
                print('\n[cVC] Asynchronous controller activated...')

                if uCalling == 1:       # Running Live Analysis
                    sysRun, msctcp, msc_rt, cLayr = wd.rt_autoPausePlay()

                    if not sysRun and not paused:
                        print('\n[cVC] Production is pausing...')
                        paused = True

                        while paused:
                            time.sleep(5)
                            print("\n[cVC Viz] Visualization in Paused Mode...")
                            sysRun, msctcp, msc_rt, cLayr = wd.rt_autoPausePlay()
                            if sysRun:
                                paused = False
                                print('[cVC] Visualisation Resumes...')
                            time.sleep(0.2)
                    else:
                        # Get list of relevant SQL Tables using conn() --------------------[]
                        self.gcD = svc.sqlExec(gc_con, s_fetch, stp_Sz, self.gcT, batch_VC)
                        time.sleep(30)

                elif uCalling == 2 or uCalling == 3:
                    if keyboard.is_pressed("Alt+Q"):
                        paused = True

                        while paused:
                            time.sleep(5)
                            print("\n[cVC Viz] Visualization in Paused Mode...")
                            if keyboard.is_pressed("esc"):
                                paused = False
                                print('[cVC] Visualisation Resumes...')
                            time.sleep(0.2)

                    else:
                        # Get list of relevant SQL Tables using conn() --------------------[]
                        self.gcD = svc.sqlExec(gc_con, s_fetch, stp_Sz, self.gcT, batch_VC)
                        time.sleep(30)

                        # ------ Inhibit iteration ----------------------------------------------------------[]
                        if not self.gcD:  # Terminate file-fetch

                            print('[cVC] SQL End of File, connection closes after 30 mins...')
                            time.sleep(60)
                            gc_con.close()
                            continue
                        else:
                            print('\n[cVC] Updating....')

                if gc_con:
                    self.canvas.get_tk_widget().after(0, self.gcDataPlot)  # Regime = every 10seconds
                    batch_VC += 1
                else:
                    print('[cVC] sorry, instance not granted, trying again..')
                    gc_con = sq.check_SQL_Status(5, 60)  # Retry 5 times, wait 60 seconds

            else:
                print('\n[cVC] is active but no visualisation!')
            print('[cVC] protocol si being refreshed..')

    # ================== End of synchronous Method ==========================

    def gcDataPlot(self):
        timei = time.time()  # start timing the entire loop

        # Call data loader Method--------------------------#
        import VarSQL_VC as vc                          # load SQL variables column names | rfVarSQL
        g1 = qvc.validCols(self.gcT)
        df1 = pd.DataFrame(self.gcD, columns=g1)        # Import into python Dataframe vData
        # ----------------------------------------
        data1 = df1.select_dtypes(include=["number"])
        df1 = data1.interpolate(method="linear", axis=0).ffill().bfill()  # column-wise
        # ----------------------------------------
        # print('TP03', df1)
        var_plyr = df1["cLayer"].iloc[-1]
        # -------------------------
        print('\nProcessing Layer:', var_plyr)
        uPosA = df1[(df1["cLayer"] == var_plyr) & (df1["VODPosA"] > 0) & (df1["sCentre"] > 0)].shape[0]
        uPosB = df1[(df1["cLayer"] == var_plyr) & (df1["VODPosB"] > 0) & (df1["sCentre"] > 0)].shape[0]
        uPosC = df1[(df1["cLayer"] == var_plyr) & (df1["VODPosC"] > 0) & (df1["sCentre"] > 0)].shape[0]
        uPosD = df1[(df1["cLayer"] == var_plyr) & (df1["VODPosD"] > 0) & (df1["sCentre"] > 0)].shape[0]

        VC = vc.loadProcesValues(df1)           # Join data values under dataframe
        # print('\n[cVC] Content', df1.head())     # Preview Data frame head
        # print("Memory Usage:", df1.info(verbose=False))  # Check memory utilization

        if self.running:
            # ------- plot ramp count ----------------------------------#
            self.a3.legend(loc='upper right', title='Cumulative Void Count')
            # ----------------------------------------------------------[]
            # Plot X-Axis data points -------- X Plot Pipe segement
            self.im10.set_xdata(np.arange(batch_VC))
            self.im11.set_xdata(np.arange(batch_VC))
            self.im12.set_xdata(np.arange(batch_VC))
            self.im13.set_xdata(np.arange(batch_VC))
            # self.im14.set_xdata(np.arange(batch_VC))

            # X Plot Y-Axis data points for XBar. Values -[Rings]
            self.im10.set_ydata(VC[0].rolling(window=s_fetch, min_periods=1).mean()[0:batch_VC])   # Count under Ring 1
            self.im11.set_ydata(VC[0].rolling(window=s_fetch, min_periods=1).mean()[0:batch_VC])   # Count under Ring 2
            self.im12.set_ydata(VC[0].rolling(window=s_fetch, min_periods=1).mean()[0:batch_VC])   # Count under Ring 3
            self.im13.set_ydata(VC[0].rolling(window=s_fetch, min_periods=1).mean()[0:batch_VC])   # Count under Ring 4
            # self.im14.set_ydata(VC[11][0:batch_VC])   # Cumulative

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if batch_VC > self.win_Xmax:
                self.a3.set_xlim(batch_VC - self.win_Xmax, batch_VC)
                VC.pop(0)
            else:
                self.a3.set_xlim(0, self.win_Xmax)
            print('Data Stream Buffer Size 2:', len(VC))
            self.canvas.draw_idle()

        else:
            print('[cVC] standby mode, no active session...')
            self.a3.text(0.354, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left',
                         transform=self.a3.transAxes)
        timef = time.time()
        lapsedT = timef - timei
        print(f"[cVC] Process Interval: {lapsedT} sec\n")
        # -----Canvas update --------------------------------------------[]

# ***************************************** END  OF COMMON CANVAS ************************************

# ------------------------- Additional Tabb for Monitoring Parameters -------------[Monitoring Tabs]
class MonitorTabb(ttk.Frame):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=20)
        self.running = True

        # prevents user possible double loading -----
        if not self.running:
            self.running = True
            threading.Thread(target=self.createMonitorStance, daemon=True).start()
            print('[PM] is now running....')

    def createMonitorStance(self):
        # Load metrics from config -----------------------------------[TG, TT, ST]
        global T1, T2, T3, T4, T5, T6, T7, win_Xmin, win_Xmax, im10, im11, im12, im13, im14, a1, a2, a3, a4, a5, \
            a6, im14, im15, im16, im17, im18, im19, im20, im21, im22, im23, im24, im25, im26, im27, im28, im29, im30, \
            im31, im32, im33, im34, im35, im36, im37, im38, im39, im40, im41, im42, im43, im44, im45, im46, im47, im48, \
            im49, im50, im51, im52, im53, im54, im55, im56, im57, im58, im59, im60, im61, im62, im63, im64, im65, im66

        # Load Quality Historical Values -----------[]
        label = ttk.Label(self, text='[' + str(pMode) + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)
        self.f = Figure(figsize=(pMtX, 8), dpi=100)

        if pRecipe == 'DNV':
            print('\n4 params condition met....')
            self.f.subplots_adjust(left=0.029, bottom=0.057, right=0.983, top=0.964, wspace=0.167, hspace=0.164)
            self.a1 = self.f.add_subplot(2, 4, (1, 2))        # Roller Pressure
            self.a2 = self.f.add_subplot(2, 4, (3, 4))        # Winding Speed
            self.a3 = self.f.add_subplot(2, 4, (5, 6))        # Cell Tension
            self.a4 = self.f.add_subplot(2, 4, (7, 8))        # Oven Temperature

            # Load Query Tables --------------------#
            # if runType == 2:
            self.T1 = 'GEN_' + str(pWON)                      # Tape Winding Speed, Cell Tension & Oven Temp
            self.T2 = 'RP1_' + str(pWON)                      # Roller Pressure
            self.T3 = 'RP2_' + str(pWON)                      # Table 2 to be concatenated
            # self.T4 = 'WS_' + str(pWON)                     # Not necesary see GEN_
            # --------------------------------------#
        elif pRecipe == 'MGM':
            print('\n6 Param condition met....')
            self.f.subplots_adjust(left=0.029, bottom=0.057, right=0.99, top=0.979, wspace=0.245, hspace=0.164)
            self.a1 = self.f.add_subplot(2, 6, (1, 2))        # Laser power
            self.a2 = self.f.add_subplot(2, 6, (3, 4))        # Cell Tension
            self.a3 = self.f.add_subplot(2, 6, (5, 6))        # Roller Pressure
            self.a4 = self.f.add_subplot(2, 6, (7, 8))        # Laser Angle
            self.a5 = self.f.add_subplot(2, 6, (9, 10))       # Oven Temperature
            self.a6 = self.f.add_subplot(2, 6, (11, 12))      # Winding Speed

            # Load SQL Query Tables ----------------#
            # if runType == 2:
            self.T1 = 'GEN_' + str(pWON)                     # Tape Winding Speed, Cell Tension & Oven Temp
            self.T2 = 'RP1_' + str(pWON)                      # Roller Pressure Table 1
            self.T3 = 'RP2_' + str(pWON)                      # Roller Pressure T2
            # --------------------------------------#
            self.T4 = 'LP1_' + str(pWON)                      # Laser Power Table 1
            self.T5 = 'LP2_' + str(pWON)                      # Laser Power Table 2
            self.T6 = 'LA1_' + str(pWON)                      # Laser Angle Table 1
            self.T7 = 'LA2_' + str(pWON)                      # Laser Angle Table 2

            # --------------------------------------#
        else:
            print('\n Users params condition met....')
            self.f.subplots_adjust(left=0.029, bottom=0.057, right=0.99, top=0.929, wspace=0.245, hspace=0.164)
            print('Bespoke Selection Not allowed in this Version...')
            # ----------------------------------#

        # Declare Plots attributes -----------------[]
        plt.rcParams.update({'font.size': 7})        # Reduce font size to 7pt for all legends

        # Calibrate limits for X-moving Axis --------#
        YScale_minRP, YScale_maxRP = 0, 5
        YScale_minCT, YScale_maxCT = 0, 5
        YScale_minWS, YScale_maxWS = 0, 10
        YScale_minOT, YScale_maxOT = 0, 200
        self.win_Xmin, self.win_Xmax = 0, 25              # windows view = visible data points
        # -------------------------------------------#

        # Monitoring Parameters --------------------------------------------#
        if pRecipe == 'DNV':                            # int(mCT) and int(mOT) and int(mRP) and int(mWS):
            self.a1.set_title('Roller Pressure - MPa', fontsize=12, fontweight='bold')
            self.a2.set_title('Winding Speed - m/s', fontsize=12, fontweight='bold')
            self.a3.set_title('Cell Tension - N.m', fontsize=12, fontweight='bold')
            self.a4.set_title('Oven Temperature - °C', fontsize=12, fontweight='bold')

            self.a1.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a2.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a3.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a4.grid(color="0.5", linestyle='-', linewidth=0.5)

            # --------- Monitoring Legend Label -------------#
            self.a1.legend(['Roller Pressure - MPa'], loc='upper right', fontsize='x-large')
            self.a2.legend(['Winding Speed - m/s'], loc='upper right', fontsize='x-large')
            self.a3.legend(['Cell Tension - N.m'], loc='upper right', fontsize='x-large')
            self.a4.legend(['Oven Temperature - °C'], loc='upper right', fontsize='x-large')

            # Initialise runtime limits --------------------#
            self.a1.set_ylabel("Roller Pressure - MPa")          # Pressure measured in Pascal
            self.a2.set_ylabel("Tape Winding Speed - m/s")       # Angle measured in Degrees
            self.a3.set_ylabel("Cell Tension Force - N.m")       # Tension measured in Newton
            self.a4.set_ylabel("Oven Temperature - °C")          # Oven Temperature in Degrees Celsius

        elif pRecipe == 'MGM':       # int(mLP) and int(mLA) and int(mCT) and int(mOT) and int(mRP):
            # monitorP = 'MGM'
            self.a1.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a2.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a3.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a4.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a5.grid(color="0.5", linestyle='-', linewidth=0.5)
            self.a6.grid(color="0.5", linestyle='-', linewidth=0.5)
            # ---------------- Legend Label -----------------#
            self.a1.legend(loc='upper right', title='Laser Power - Watt')
            self.a2.legend(loc='upper right', title='Cell Tension - N.m')
            self.a3.legend(loc='upper right', title='Roller Pressure - MPa')
            self.a4.legend(loc='upper right', title='Laser Angle - Deg')
            self.a5.legend(loc='upper right', title='Oven Temperature - °C')
            self.a6.legend(loc='upper right', title='Winding Speed - m/s')
            # Initialise runtime limits --------------------#
            self.a1.set_ylabel("Laser Power")            # Force measured in Newton
            self.a2.set_ylabel("Cell Tension")           # Angle measured in Degrees
            self.a3.set_ylabel("Roller Pressure")        # Oven Temperature in Degree Celsius
            self.a4.set_ylabel("Laser Angle")            # Oven Temperature in Degrees Celsius
            self.a5.set_ylabel("Oven Temperature")       # Oven Temperature in Degrees Celsius
            self.a6.set_ylabel("Winding Speed")          # Oven Temperature in Degrees Celsius
        else:
            print('\n Bespoke Selection NOT allowed....')

        # Initialise runtime limits --------------------------------#
        self.a1.set_ylim([YScale_minRP, YScale_maxRP], auto=True)
        self.a1.set_xlim([self.win_Xmin, self.win_Xmax])

        self.a2.set_ylim([YScale_minWS, YScale_maxWS], auto=True)
        self.a2.set_xlim([self.win_Xmin, self.win_Xmax])

        self.a3.set_ylim([YScale_minCT, YScale_maxCT], auto=True)
        self.a3.set_xlim([self.win_Xmin, self.win_Xmax])

        self.a4.set_ylim([YScale_minOT, YScale_maxOT], auto=True)
        self.a4.set_xlim([self.win_Xmin, self.win_Xmax])

        # Define Plot area and axes -
        if pRecipe == 'DNV':
            # -----------------------------------------------------[Roller Force]
            im10, = self.a1.plot([], [], 'o-', label='Roller Pressure - (R1H1)')
            im11, = self.a1.plot([], [], 'o-', label='Roller Pressure - (R1H2)')
            im12, = self.a1.plot([], [], 'o-', label='Roller Pressure - (R1H3)')
            im13, = self.a1.plot([], [], 'o-', label='Roller Pressure - (R1H4)')
            im14, = self.a1.plot([], [], 'o-', label='Roller Pressure - (R2H1)')
            im15, = self.a1.plot([], [], 'o-', label='Roller Pressure - (R2H2)')
            im16, = self.a1.plot([], [], 'o-', label='Roller Pressure - (R2H3)')
            im17, = self.a1.plot([], [], 'o-', label='Roller Pressure - (R2H4)')
            im18, = self.a1.plot([], [], 'o-', label='Roller Pressure - (R3H1)')
            im19, = self.a1.plot([], [], 'o-', label='Roller Pressure - (R3H2)')
            im20, = self.a1.plot([], [], 'o-', label='Roller Pressure - (R3H3)')
            im21, = self.a1.plot([], [], 'o-', label='Roller Pressure - (R3H4)')
            im22, = self.a1.plot([], [], 'o-', label='Roller Pressure - (R4H1)')
            im23, = self.a1.plot([], [], 'o-', label='Roller Pressure - (R4H2)')
            im24, = self.a1.plot([], [], 'o-', label='Roller Pressure - (R4H3)')
            im25, = self.a1.plot([], [], 'o-', label='Roller Pressure - (R4H4)')
            # ------------------------------------------------------[Winding Speed]
            im26, = self.a2.plot([], [], 'o-', label='Winding Speed - (Ring 1)')
            im27, = self.a2.plot([], [], 'o-', label='Winding Speed - (Ring 2)')
            im28, = self.a2.plot([], [], 'o-', label='Winding Speed - (Ring 3)')
            im29, = self.a2.plot([], [], 'o-', label='Winding Speed - (Ring 4)')
            # ------------------------------------------------------[Cell Tension]
            im30, = self.a3.plot([], [], 'o-', label='Active Cell Tension')
            # -------------------------------------------------[Oven Temperature]
            im31, = self.a4.plot([], [], 'o-', label='RTD Oven Temperature (Lower Segment)')
            im32, = self.a4.plot([], [], 'o-', label='RTD Oven Temperature (Upper Segment)')
            im33, = self.a4.plot([], [], 'o-', label='IR Oven Temperature (Lower Segment)')
            im34, = self.a4.plot([], [], 'o-', label='IR Oven Temperature (Upper Segment)')

        elif pRecipe == 'MGM':
            # --------------------------------------------------[Laser Power]
            im10, = self.a1.plot([], [], 'o-', label='Laser Power - (R1H1)')
            im11, = self.a1.plot([], [], 'o-', label='Laser Power - (R1H2)')
            im12, = self.a1.plot([], [], 'o-', label='Laser Power - (R1H3)')
            im13, = self.a1.plot([], [], 'o-', label='Laser Power - (R1H4)')
            im14, = self.a1.plot([], [], 'o-', label='Laser Power - (R2H1)')
            im15, = self.a1.plot([], [], 'o-', label='Laser Power - (R2H2)')
            im16, = self.a1.plot([], [], 'o-', label='Laser Power - (R2H3)')
            im17, = self.a1.plot([], [], 'o-', label='Laser Power - (R2H4)')
            im18, = self.a1.plot([], [], 'o-', label='Laser Power - (R3H1)')
            im19, = self.a1.plot([], [], 'o-', label='Laser Power - (R3H2)')
            im20, = self.a1.plot([], [], 'o-', label='Laser Power - (R3H3)')
            im21, = self.a1.plot([], [], 'o-', label='Laser Power - (R3H4)')
            im22, = self.a1.plot([], [], 'o-', label='Laser Power - (R4H1)')
            im23, = self.a1.plot([], [], 'o-', label='Laser Power - (R4H2)')
            im24, = self.a1.plot([], [], 'o-', label='Laser Power - (R4H3)')
            im25, = self.a1.plot([], [], 'o-', label='Laser Power - (R4H4)')
            # ---------------------------------------- [Cell Tension  & Oven Temp]
            im26, = self.a2.plot([], [], 'o-', label='Active Cell Tension')
            # --------------------------------------------------[Roller Pressure]
            im27, = self.a3.plot([], [], 'o-', label='Roller Pressure - (R1H1)')
            im28, = self.a3.plot([], [], 'o-', label='Roller Pressure - (R1H2)')
            im29, = self.a3.plot([], [], 'o-', label='Roller Pressure - (R1H3)')
            im30, = self.a3.plot([], [], 'o-', label='Roller Pressure - (R1H4)')
            im31, = self.a3.plot([], [], 'o-', label='Roller Pressure - (R2H1)')
            im32, = self.a3.plot([], [], 'o-', label='Roller Pressure - (R2H2)')
            im33, = self.a3.plot([], [], 'o-', label='Roller Pressure - (R2H3)')
            im34, = self.a3.plot([], [], 'o-', label='Roller Pressure - (R2H4)')
            im35, = self.a3.plot([], [], 'o-', label='Roller Pressure - (R3H1)')
            im36, = self.a3.plot([], [], 'o-', label='Roller Pressure - (R3H2)')
            im37, = self.a3.plot([], [], 'o-', label='Roller Pressure - (R3H3)')
            im38, = self.a3.plot([], [], 'o-', label='Roller Pressure - (R3H4)')
            im39, = self.a3.plot([], [], 'o-', label='Roller Pressure - (R4H1)')
            im40, = self.a3.plot([], [], 'o-', label='Roller Pressure - (R4H2)')
            im41, = self.a3.plot([], [], 'o-', label='Roller Pressure - (R4H3)')
            im42, = self.a3.plot([], [], 'o-', label='Roller Pressure - (R4H4)')
            # --------------------------------------------------[Laser Angle]
            im43, = self.a4.plot([], [], 'o-', label='Laser Angle - (R1H1)')
            im44, = self.a4.plot([], [], 'o-', label='Laser Angle - (R1H2)')
            im45, = self.a4.plot([], [], 'o-', label='Laser Angle - (R1H3)')
            im46, = self.a4.plot([], [], 'o-', label='Laser Angle - (R1H4)')
            im47, = self.a4.plot([], [], 'o-', label='Laser Angle - (R2H1)')
            im48, = self.a4.plot([], [], 'o-', label='Laser Angle - (R2H2)')
            im49, = self.a4.plot([], [], 'o-', label='Laser Angle - (R2H3)')
            im50, = self.a4.plot([], [], 'o-', label='Laser Angle - (R2H4)')
            im51, = self.a4.plot([], [], 'o-', label='Laser Angle - (R3H1)')
            im52, = self.a4.plot([], [], 'o-', label='Laser Angle - (R3H2)')
            im53, = self.a4.plot([], [], 'o-', label='Laser Angle - (R3H3)')
            im54, = self.a4.plot([], [], 'o-', label='Laser Angle - (R3H4)')
            im55, = self.a4.plot([], [], 'o-', label='Laser Angle - (R4H1)')
            im56, = self.a4.plot([], [], 'o-', label='Laser Angle - (R4H2)')
            im57, = self.a4.plot([], [], 'o-', label='Laser Angle - (R4H3)')
            im58, = self.a4.plot([], [], 'o-', label='Laser Angle - (R4H4)')
            # -----------------------------------------------[ Oven Temperature]
            im59, = self.a5.plot([], [], 'o-', label='RTD Oven Temperature (Lower Segment)')
            im60, = self.a5.plot([], [], 'o-', label='RTD Oven Temperature (Upper Segment)')
            im61, = self.a6.plot([], [], 'o-', label='IR Oven Temperature (Lower Segment)')
            im62, = self.a6.plot([], [], 'o-', label='IR Oven Temperature (Upper Segment)')
            # ----------------------------------------------[Winding Speed x16]
            im63, = self.a6.plot([], [], 'o-', label='Winding Speed - (Ring 1)')
            im64, = self.a6.plot([], [], 'o-', label='Winding Speed - (Ring 2)')
            im65, = self.a6.plot([], [], 'o-', label='Winding Speed - (Ring 3)')
            im66, = self.a6.plot([], [], 'o-', label='Winding Speed - (Ring 4)')

        # self.canvas = FigureCanvasTkAgg(self.f, master=root)
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(self.canvas, self)
        # toolbar.update()
        # self.canvas._tkcanvas.pack(expand=True)

        # --------- call data block --------------------------------
        threading.Thread(target=self.dataControlPM, daemon=True).start()
        # ---------------- EXECUTE SYNCHRONOUS METHOD ---------------#


    def dataControlPM(self):
        global batch_PM

        batch_PM = 1
        s_fetch, stp_Sz = 600, 1        #i.e. 6 mtr worth of data every minute

        # Obtain RT Monitoring Data ---------------------------[]
        # if UseSQL_DBS:
        if self.running:
            import sqlArrayRLmethodPM as spm
            mt_con = sq.sql_connectRTM()
        else:
            print('[RTM] Data Source selection is Unknown')
            mt_con = None

        # Initialise RT variables ---[]
        autoSpcRun = True
        autoSpcPause = False
        import keyboard                     # for temporary use

        while True:
            # ------------------------------
            if self.running and mt_con:
                inProgress = True                                            # True for RetroPlay mode
                print('\nAsynchronous controller activated...')

                if keyboard.is_pressed("Alt+Q") and not inProgress:
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
                    if pRecipe == 'DNV':
                        self.gEN, self.RPa, self.RPb = spm.dnv_sqlExec(mt_con, s_fetch, stp_Sz, self.T1, self.T2, self.T3, batch_PM)

                    elif pRecipe == 'MGM':
                         self.gEN, self.RPa, self.RPb, self.LPa, self.LPb, self.LAa, self.LAb = spm.mgm_sqlExec(
                            mt_con, s_fetch, stp_Sz, self.T1, self.T2, self.T3,
                            self.T4, self.T5, self.T6, self.T7, batch_PM)
                    else:
                        self.gEN, self.RP, self.LP, self.LA = 0, 0, 0, 0            # Assigned to Bespoke User Selection.
                    time.sleep(60)
                # ------ Inhibit iteration ----------------------------------------------------------[]
                """
                # Set condition for halting real-time plots in watchdog class ---------------------
                """
                # TODO --- values for inhibiting the SQL processing
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    mt_con.close()
                    if pRecipe == 'MGM':
                        mt_con.close()
                    else:
                        pass
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\n[PM] Updating....')

            else:
                print('[PM] is active but no visualisation!\n')
            print('[RMP] Waiting for refresh..')
            if mt_con:
                self.canvas.get_tk_widget().after(30, self.mtDataPlot)
                batch_PM += 1
            else:
                print('[PM] sorry, instance not granted, trying again..')
                mt_con = sq.check_SQL_Status(5, 10)
            print('[PM] protocol is refreshed, the wait is over...')

    # ----------------------------------------------------------------------------[]

    def mtDataPlot(self):
        timei = time.time()                                                             # start timing the entire loop

        # declare asynchronous variables ------------------[]
        if self.running:
            print('\nMonitor Tabb running......')
            import VarSQL_PM as mt
            # ----------------------------------------------#
            if pRecipe == 'DNV':
                g1 = qpm.validCols(self.T1)                          # General Table (OT/CT)
                d1 = pd.DataFrame(self.gEN, columns=g1)
                g2 = qpm.validCols(self.T2)                          # Roller Pressure Table 1
                d2 = pd.DataFrame(self.RPa, columns=g2)
                g3 = qpm.validCols(self.T3)                          # Roller Pressure Table 2
                d3 = pd.DataFrame(self.RPb, columns=g3)
                # g4 = qpm.validCols(self.T4)                          # Winding Speed
                # d4 = pd.DataFrame(self.RPc, columns=g4)

                # Concatenate all columns -----------------------[]
                df1 = pd.concat([d1, d2, d3], axis=1)

            elif pRecipe == 'MGM':
                g1 = qpm.validCols(self.T1)                          # General Table
                d1 = pd.DataFrame(self.gEN, columns=g1)
                g2 = qpm.validCols(self.T2)                          # Roller Pressure Table 1
                d2 = pd.DataFrame(self.RPa, columns=g2)
                g3 = qpm.validCols(self.T3)                          # Roller Pressure Table 2
                d3 = pd.DataFrame(self.RPb, columns=g3)
                g4 = qpm.validCols(self.T4)                          # Laser Power Table 1
                d4 = pd.DataFrame(self.LPa, columns=g4)
                g5 = qpm.validCols(self.T5)                          # Laser Power Table 2
                d5 = pd.DataFrame(self.LPb, columns=g5)
                g6 = qpm.validCols(self.T6)                          # Laser Angle
                d6 = pd.DataFrame(self.LAa, columns=g6)
                g7 = qpm.validCols(self.T7)                          # Laser Angle
                d7 = pd.DataFrame(self.LAb, columns=g7)

                # Concatenate all columns -----------[]
                df1 = pd.concat([d1, d2, d3, d4, d5, d6, d7], axis=1)
            else:
                df1 = 0
                pass                                        # Reserve for process scaling -- RBL.

            # ----- Access data element within the concatenated columns -------------------------[A]
            PM = mt.loadProcesValues(df1, pRecipe)              # Join data values under dataframe
            print('\nDataFrame Content', df1.head(10))          # Preview Data frame head
            print("Memory Usage:", df1.info(verbose=False))     # Check memory utilization

            # Declare Plots attributes ------------------------------------------------------------[]
            if self.running:
                self.a1.legend(title='Roller Pressure - MPa', loc='upper right')
                self.a2.legend(title='Winding Speed - m/s', loc='upper right')
                self.a3.legend(title='Cell Tension - N.m', loc='upper right')
                self.a4.legend(title='Oven Temperature - °C', loc='upper right')
                # ------------------------------------------#
                im10.set_xdata(np.arange(batch_PM))
                im11.set_xdata(np.arange(batch_PM))
                im12.set_xdata(np.arange(batch_PM))
                im13.set_xdata(np.arange(batch_PM))
                im14.set_xdata(np.arange(batch_PM))
                im15.set_xdata(np.arange(batch_PM))
                im16.set_xdata(np.arange(batch_PM))
                im17.set_xdata(np.arange(batch_PM))
                im18.set_xdata(np.arange(batch_PM))
                im19.set_xdata(np.arange(batch_PM))
                im20.set_xdata(np.arange(batch_PM))
                im21.set_xdata(np.arange(batch_PM))
                im22.set_xdata(np.arange(batch_PM))
                im23.set_xdata(np.arange(batch_PM))
                im24.set_xdata(np.arange(batch_PM))
                im25.set_xdata(np.arange(batch_PM))

                im26.set_xdata(np.arange(batch_PM))
                im27.set_xdata(np.arange(batch_PM))
                im28.set_xdata(np.arange(batch_PM))
                im29.set_xdata(np.arange(batch_PM))
                im30.set_xdata(np.arange(batch_PM))
                im31.set_xdata(np.arange(batch_PM))
                im32.set_xdata(np.arange(batch_PM))
                im33.set_xdata(np.arange(batch_PM))
                im34.set_xdata(np.arange(batch_PM))
                if pRecipe == 'MGM':
                    im35.set_xdata(np.arange(batch_PM))
                    im36.set_xdata(np.arange(batch_PM))
                    im37.set_xdata(np.arange(batch_PM))
                    im38.set_xdata(np.arange(batch_PM))
                    im39.set_xdata(np.arange(batch_PM))
                    im40.set_xdata(np.arange(batch_PM))
                    im41.set_xdata(np.arange(batch_PM))

                    im42.set_xdata(np.arange(batch_PM))
                    im43.set_xdata(np.arange(batch_PM))
                    im44.set_xdata(np.arange(batch_PM))
                    im45.set_xdata(np.arange(batch_PM))

                    im46.set_xdata(np.arange(batch_PM))
                    im47.set_xdata(np.arange(batch_PM))
                    im48.set_xdata(np.arange(batch_PM))
                    im49.set_xdata(np.arange(batch_PM))
                    im50.set_xdata(np.arange(batch_PM))
                    im51.set_xdata(np.arange(batch_PM))
                    im52.set_xdata(np.arange(batch_PM))
                    im53.set_xdata(np.arange(batch_PM))
                    im54.set_xdata(np.arange(batch_PM))
                    im55.set_xdata(np.arange(batch_PM))
                    im56.set_xdata(np.arange(batch_PM))
                    im57.set_xdata(np.arange(batch_PM))
                    im58.set_xdata(np.arange(batch_PM))
                    im59.set_xdata(np.arange(batch_PM))
                    im60.set_xdata(np.arange(batch_PM))
                    im61.set_xdata(np.arange(batch_PM))

                    im62.set_xdata(np.arange(batch_PM))
                    im63.set_xdata(np.arange(batch_PM))
                    im64.set_xdata(np.arange(batch_PM))
                    im65.set_xdata(np.arange(batch_PM))
                    im66.set_xdata(np.arange(batch_PM))

            if self.running and pRecipe == 'DNV':
                # X Plot Y-Axis data points for XBar ----------[Roller Pressure x16, A1]
                im10.set_ydata((PM[14]).rolling(window=25).mean()[0:batch_PM])  # R1H1
                im11.set_ydata((PM[15]).rolling(window=25).mean()[0:batch_PM])  # R1H2
                im12.set_ydata((PM[16]).rolling(window=25).mean()[0:batch_PM])  # R1H3
                im13.set_ydata((PM[17]).rolling(window=25).mean()[0:batch_PM])  # R1H4
                im14.set_ydata((PM[18]).rolling(window=25).mean()[0:batch_PM])  # R2H1
                im15.set_ydata((PM[19]).rolling(window=25).mean()[0:batch_PM])  # R2H2
                im16.set_ydata((PM[20]).rolling(window=25).mean()[0:batch_PM])  # R2H3
                im17.set_ydata((PM[21]).rolling(window=25).mean()[0:batch_PM])  # R2H4
                im18.set_ydata((PM[24]).rolling(window=25).mean()[0:batch_PM])  # Segment 1
                im19.set_ydata((PM[25]).rolling(window=25).mean()[0:batch_PM])  # Segment 2
                im20.set_ydata((PM[26]).rolling(window=25).mean()[0:batch_PM])  # Segment 3
                im21.set_ydata((PM[27]).rolling(window=25).mean()[0:batch_PM])  # Segment 4
                im22.set_ydata((PM[28]).rolling(window=25).mean()[0:batch_PM])  # Segment 1
                im23.set_ydata((PM[29]).rolling(window=25).mean()[0:batch_PM])  # Segment 2
                im24.set_ydata((PM[30]).rolling(window=25).mean()[0:batch_PM])  # Segment 3
                im25.set_ydata((PM[31]).rolling(window=25).mean()[0:batch_PM])  # Segment 4
                # ------------------------------------- Tape Winding Speed x16, A2
                im26.set_ydata((PM[6]).rolling(window=25).mean()[0:batch_PM])  # Winding SPeed
                im27.set_ydata((PM[7]).rolling(window=25).mean()[0:batch_PM])  # WS Ring2
                im28.set_ydata((PM[8]).rolling(window=25).mean()[0:batch_PM])  # WS Ring3
                im29.set_ydata((PM[9]).rolling(window=25).mean()[0:batch_PM])  # WS Ring4
                # --------------------------------------Active Cell Tension x1
                im30.set_ydata((PM[1]).rolling(window=25).mean()[0:batch_PM])  # SCell Tension
                # ----------------------------------------Oven Temperature x4 (RTD & IR Temp)
                im31.set_ydata((PM[2]).rolling(window=25).mean()[0:batch_PM])  # Segment 2
                im32.set_ydata((PM[3]).rolling(window=25).mean()[0:batch_PM])  # Segment 3
                im33.set_ydata((PM[4]).rolling(window=25).mean()[0:batch_PM])  # Segment 4
                im34.set_ydata((PM[5]).rolling(window=25).mean()[0:batch_PM])  # Segment 1

            elif self.running and pRecipe == 'MGM':
                # -------------------------------------------------------------------------------[Laser Power]
                im10.set_ydata((PM[30]).rolling(window=25).mean()[0:batch_PM])  # Segment 1
                im11.set_ydata((PM[31]).rolling(window=25).mean()[0:batch_PM])  # Segment 2
                im12.set_ydata((PM[32]).rolling(window=25).mean()[0:batch_PM])  # Segment 3
                im13.set_ydata((PM[33]).rolling(window=25).mean()[0:batch_PM])  # Segment 4
                im14.set_ydata((PM[34]).rolling(window=25).mean()[0:batch_PM])  # Segment 1
                im15.set_ydata((PM[35]).rolling(window=25).mean()[0:batch_PM])  # Segment 2
                im16.set_ydata((PM[36]).rolling(window=25).mean()[0:batch_PM])  # Segment 3
                im17.set_ydata((PM[37]).rolling(window=25).mean()[0:batch_PM])  # Segment 4
                im18.set_ydata((PM[38]).rolling(window=25).mean()[0:batch_PM])  # Segment 1
                im19.set_ydata((PM[39]).rolling(window=25).mean()[0:batch_PM])  # Segment 2
                im20.set_ydata((PM[40]).rolling(window=25).mean()[0:batch_PM])  # Segment 3
                im21.set_ydata((PM[41]).rolling(window=25).mean()[0:batch_PM])  # Segment 4
                im22.set_ydata((PM[42]).rolling(window=25).mean()[0:batch_PM])  # Segment 1
                im23.set_ydata((PM[43]).rolling(window=25).mean()[0:batch_PM])  # Segment 2
                im24.set_ydata((PM[44]).rolling(window=25).mean()[0:batch_PM])  # Segment 3
                im25.set_ydata((PM[45]).rolling(window=25).mean()[0:batch_PM])  # Segment 4
                # -----------------------------------------------------[Cell Tension]
                im26.set_ydata((PM[1]).rolling(window=25).mean()[0:batch_PM])   # Segment 1
                # --------------------------------------------------[Roller Pressure]
                im27.set_ydata((PM[13]).rolling(window=25).mean()[0:batch_PM])  # Segment 2
                im28.set_ydata((PM[14]).rolling(window=25).mean()[0:batch_PM])  # Segment 3
                im29.set_ydata((PM[15]).rolling(window=25).mean()[0:batch_PM])  # Segment 4
                im30.set_ydata((PM[16]).rolling(window=25).mean()[0:batch_PM])  # Segment 1
                im31.set_ydata((PM[17]).rolling(window=25).mean()[0:batch_PM])  # Segment 2
                im32.set_ydata((PM[18]).rolling(window=25).mean()[0:batch_PM])  # Segment 3
                im33.set_ydata((PM[19]).rolling(window=25).mean()[0:batch_PM])  # Segment 4
                im34.set_ydata((PM[20]).rolling(window=25).mean()[0:batch_PM])  # Segment 1
                im35.set_ydata((PM[21]).rolling(window=25).mean()[0:batch_PM])  # Segment 2
                im36.set_ydata((PM[22]).rolling(window=25).mean()[0:batch_PM])  # Segment 3
                im37.set_ydata((PM[23]).rolling(window=25).mean()[0:batch_PM])  # Segment 4
                im38.set_ydata((PM[24]).rolling(window=25).mean()[0:batch_PM])  # Segment 1
                im39.set_ydata((PM[25]).rolling(window=25).mean()[0:batch_PM])  # Segment 2
                im40.set_ydata((PM[26]).rolling(window=25).mean()[0:batch_PM])  # Segment 3
                im41.set_ydata((PM[27]).rolling(window=25).mean()[0:batch_PM])  # Segment 4
                im42.set_ydata((PM[28]).rolling(window=25).mean()[0:batch_PM])  # Segment 1
                # -------------------------------------------------------[Laser Angle]
                im43.set_ydata((PM[47]).rolling(window=25).mean()[0:batch_PM])  # Segment 2
                im44.set_ydata((PM[48]).rolling(window=25).mean()[0:batch_PM])  # Segment 1
                im45.set_ydata((PM[49]).rolling(window=25).mean()[0:batch_PM])  # Segment 2
                im46.set_ydata((PM[50]).rolling(window=25).mean()[0:batch_PM])  # Segment 1
                im47.set_ydata((PM[51]).rolling(window=25).mean()[0:batch_PM])  # Segment 2
                im48.set_ydata((PM[52]).rolling(window=25).mean()[0:batch_PM])  # Segment 3
                im49.set_ydata((PM[53]).rolling(window=25).mean()[0:batch_PM])  # Segment 4
                im50.set_ydata((PM[54]).rolling(window=25).mean()[0:batch_PM])  # Segment 1
                im51.set_ydata((PM[55]).rolling(window=25).mean()[0:batch_PM])  # Segment 2
                im52.set_ydata((PM[56]).rolling(window=25).mean()[0:batch_PM])  # Segment 3
                im53.set_ydata((PM[57]).rolling(window=25).mean()[0:batch_PM])  # Segment 4
                im54.set_ydata((PM[58]).rolling(window=25).mean()[0:batch_PM])  # Segment 1
                im55.set_ydata((PM[59]).rolling(window=25).mean()[0:batch_PM])  # Segment 2
                im56.set_ydata((PM[60]).rolling(window=25).mean()[0:batch_PM])  # Segment 3
                im57.set_ydata((PM[61]).rolling(window=25).mean()[0:batch_PM])  # Segment 4
                im58.set_ydata((PM[62]).rolling(window=25).mean()[0:batch_PM])  # Segment 1
                # -------------------------------------------------[Oven Temperature]
                im59.set_ydata((PM[2]).rolling(window=25).mean()[0:batch_PM])  # Segment 2
                im60.set_ydata((PM[3]).rolling(window=25).mean()[0:batch_PM])  # Segment 3
                im61.set_ydata((PM[4]).rolling(window=25).mean()[0:batch_PM])  # Segment 4
                im62.set_ydata((PM[5]).rolling(window=25).mean()[0:batch_PM])  # Segment 1
                # ----------------------------------------------[Winding Speed x16]
                im63.set_ydata((PM[6]).rolling(window=25).mean()[0:batch_PM])  # Segment 2
                im64.set_ydata((PM[7]).rolling(window=25).mean()[0:batch_PM])  # Segment 3
                im65.set_ydata((PM[8]).rolling(window=25).mean()[0:batch_PM])  # Segment 4
                im66.set_ydata((PM[9]).rolling(window=25).mean()[0:batch_PM])  # Segment 1

            # Setting up the parameters for moving windows Axes ---[]
            if batch_PM > self.win_Xmax:
                self.a1.set_xlim(batch_PM - self.win_Xmax, batch_PM)
                self.a2.set_xlim(batch_PM - self.win_Xmax, batch_PM)
                self.a3.set_xlim(batch_PM - self.win_Xmax, batch_PM)
                self.a4.set_xlim(batch_PM - self.win_Xmax, batch_PM)
                # self.a5.set_xlim(batch_PM - self.win_Xmax, batch_PM)
                # self.a6.set_xlim(batch_PM - self.win_Xmax, batch_PM)
                PM.pop(0)
            else:
                self.a1.set_xlim(0, self.win_Xmax)
                self.a2.set_xlim(0, self.win_Xmax)
                self.a3.set_xlim(0, self.win_Xmax)
                self.a4.set_xlim(0, self.win_Xmax)
                # self.a5.set_xlim(0, self.win_Xmax)
                # self.a6.set_xlim(0, self.win_Xmax)
            print('[PM] Data Stream Buffer Size 2:', len(PM))
            self.canvas.draw_idle()

        else:
            print('[MPM] in standby mode, no active session...')
            self.a1.text(0.400, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left',
                         transform=self.a1.transAxes)
            self.a2.text(0.400, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left',
                         transform=self.a2.transAxes)
            self.a3.text(0.400, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left',
                         transform=self.a3.transAxes)
            self.a4.text(0.400, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left',
                         transform=self.a4.transAxes)
            if pRecipe == 'MGM':
                self.a5.text(0.355, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left',
                             transform=self.a5.transAxes)
                self.a6.text(0.355, 0.500, '--------- No Data Feed ---------', fontsize=12, ha='left',
                             transform=self.a6.transAxes)


        timef = time.time()
        lapsedT = timef - timei
        print(f"[MPM] Process Interval: {lapsedT} sec\n")

    # -----Canvas update --------------------------------------------[]


# ------------------------------------------------------------------------------------------[Laser Power Tab]
class laserPowerTabb(ttk.Frame):
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        global lpS, lpTy, olS, opS, pHL, pAL, pFO, win_Xmin, win_Xmax, im10, im11, im12, im13, im14, im15, im16, im17, \
            im18, im19, im20, im21, im22, im23, im24, im25, im26, im27, im28, im29, im30, im31, im32, im33, im34, im35, \
            im36, im37, im38, im39, im40, im41, T1, T2

        # Load Quality Historical Values -----------[]
        if pRecipe == 'DNV':
            import qParamsHL_DNV as dnv
            lpS, lpTy, olS, opS, pHL, pAL, pFO, pP1, pP2, pP3, pP4, pP5 = dnv.decryptpProcessLim(pWON, 'LP')
        else:
            import qParamsHL_MGM as mgm
            lpS, lpTy, olS, opS, pHL, pAL, pFO, pP1, pP2, pP3, pP4, pP5 = mgm.decryptpProcessLim(pWON, 'LP')
        # Break down each element to useful list ---------------[Tape Temperature]

        if pHL and pP1 and pP2 and pP3 and pP4 and pP5:  #
            lpPerf = '$Pp_{k' + str(lpS) + '}$'  # Using estimated or historical Mean
            lplabel = 'Pp'
            # -------------------------------
            One = pP1.split(',')                   # split into list elements
            Two = pP2.split(',')
            Thr = pP3.split(',')
            For = pP4.split(',')
            Fiv = pP5.split(',')
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
            lpPerf = '$Cp_{k' + str(lpS) + '}$'  # Using Automatic group Mean
            lplabel = 'Cp'

        # ------------------------------------[End of Tape Temperature Abstraction]
        label = ttk.Label(self, text='[' + str(pMode) + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Define Axes ---------------------#
        self.f = Figure(figsize=(pMtX, 8), dpi=100)  #[25 on 1920 x 1200 resolution screen, 27 on 4096 x2160]
        self.f.subplots_adjust(left=0.022, bottom=0.05, right=0.983, top=0.955, wspace=0.117, hspace=0.157)
        # ---------------------------------[]
        self.a1 = self.f.add_subplot(2, 4, (1, 3))   # X Bar Plot
        self.a2 = self.f.add_subplot(2, 4, (5, 7))   # S Bar Plo
        self.a3 = self.f.add_subplot(2, 4, (4, 8))   # Performance Feeed
        # --------------- Former format -------------

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minLP, YScale_maxLP = lpLSL - 8.5, lpUSL + 8.5       # Roller Force
        sBar_minLP, sBar_maxLP = sLCLlp - 80, sUCLlp + 80           # Calibrate Y-axis for S-Plot
        self.win_Xmin, self.win_Xmax = 0, (int(lpS) + 3)            # windows view = visible data points

        # Select betweeen straem -----------------------------------#
        if pRecipe == 'DNV':                  # PLC Data
            T1 = SPC_LP
        else:
            T1 = 'LP1_' + pWON            # SQL Data                # Laser Power
            T2 = 'LP2_' + pWON
        # ----------------------------------------------------------#

        # Initialise runtime limits
        self.a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        self.a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        self.a1.set_title('Laser Power [XBar]', fontsize=12, fontweight='bold')
        self.a2.set_title('Laser Power [StDev]', fontsize=12, fontweight='bold')

        self.a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        self.a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        self.a1.legend(loc='upper right', title='Laser Power (Watt)')
        self.a2.legend(loc='upper right', title='Sigma curve')

        # ----------------------------------------------------------#
        self.a1.set_ylim([YScale_minLP, YScale_maxLP], auto=True)
        self.a1.set_xlim([self.win_Xmin, self.win_Xmax])
        # ----------------------------------------------------------#
        self.a2.set_ylim([sBar_minLP, sBar_maxLP], auto=True)
        self.a2.set_xlim([self.win_Xmin, self.win_Xmax])

        # ---------------------------------------------------------[]
        self.a3.cla()
        self.a3.get_yaxis().set_visible(False)
        self.a3.get_xaxis().set_visible(False)

        # ---------------------------------------------------------[]
        # Define Plot area and axes -
        # ---------------------------------------------------------#
        im10, = self.a1.plot([], [], 'o-', label='Laser Power - (R1H1)')
        im11, = self.a1.plot([], [], 'o-', label='Laser Power - (R1H2)')
        im12, = self.a1.plot([], [], 'o-', label='Laser Power - (R1H3)')
        im13, = self.a1.plot([], [], 'o-', label='Laser Power - (R1H4)')
        im14, = self.a2.plot([], [], 'o-', label='Laser Power')
        im15, = self.a2.plot([], [], 'o-', label='Laser Power')
        im16, = self.a2.plot([], [], 'o-', label='Laser Power')
        im17, = self.a2.plot([], [], 'o-', label='Laser Power')

        im18, = self.a1.plot([], [], 'o-', label='Laser Power - (R2H1)')
        im19, = self.a1.plot([], [], 'o-', label='Laser Power - (R2H2)')
        im20, = self.a1.plot([], [], 'o-', label='Laser Power - (R2H3)')
        im21, = self.a1.plot([], [], 'o-', label='Laser Power - (R2H4)')
        im22, = self.a2.plot([], [], 'o-', label='Laser Power')
        im23, = self.a2.plot([], [], 'o-', label='Laser Power')
        im24, = self.a2.plot([], [], 'o-', label='Laser Power')
        im25, = self.a2.plot([], [], 'o-', label='Laser Power')

        im26, = self.a1.plot([], [], 'o-', label='Laser Power - (R3H1)')
        im27, = self.a1.plot([], [], 'o-', label='Laser Power - (R3H2)')
        im28, = self.a1.plot([], [], 'o-', label='Laser Power - (R3H3)')
        im29, = self.a1.plot([], [], 'o-', label='Laser Power - (R3H4)')
        im30, = self.a2.plot([], [], 'o-', label='Laser Power')
        im31, = self.a2.plot([], [], 'o-', label='Laser Power')
        im32, = self.a2.plot([], [], 'o-', label='Laser Power')
        im33, = self.a2.plot([], [], 'o-', label='Laser Power')

        im34, = self.a1.plot([], [], 'o-', label='Laser Power - (R4H1)')
        im35, = self.a1.plot([], [], 'o-', label='Laser Power - (R4H2)')
        im36, = self.a1.plot([], [], 'o-', label='Laser Power - (R4H3)')
        im37, = self.a1.plot([], [], 'o-', label='Laser Power - (R4H4)')
        im38, = self.a2.plot([], [], 'o-', label='Laser Power')
        im39, = self.a2.plot([], [], 'o-', label='Laser Power')
        im40, = self.a2.plot([], [], 'o-', label='Laser Power')
        im41, = self.a2.plot([], [], 'o-', label='Laser Power')

        # Statistical Feed -----------------------------------------[]
        self.a3.text(0.466, 0.945, 'Performance Feed - LP', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=self.a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        self.rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        self.rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        self.a3.add_patch(self.rect1)
        self.a3.add_patch(self.rect2)
        # ------- Process Performance Pp (the spread)---------------------
        self.a3.text(0.145, 0.804, lplabel, fontsize=12, fontweight='bold', ha='center', transform=self.a3.transAxes)
        self.a3.text(0.328, 0.658, '#Pp Value', fontsize=24, fontweight='bold', ha='center', transform=self.a3.transAxes)
        self.a3.text(0.650, 0.820, 'Ring ' + lplabel + ' Data', fontsize=14, ha='left', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=self.a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        self.a3.text(0.145, 0.403, lpPerf, fontsize=12, fontweight='bold', ha='center', transform=self.a3.transAxes)
        self.a3.text(0.328, 0.282, '#Ppk Value', fontsize=22, fontweight='bold', ha='center', transform=self.a3.transAxes)
        self.a3.text(0.640, 0.420, 'Ring ' + lpPerf + ' Data', fontsize=14, ha='left', transform=self.a3.transAxes)
        # -------------------------------------
        self.a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=self.a3.transAxes)
        # ----- Pipe Position and SMC Status -----
        self.a3.text(0.080, 0.090, 'Pipe Position: ' + str(piPos) + '    Processing Layer #' + str(cLayerN), fontsize=12, ha='left',
                transform=self.a3.transAxes)
        self.a3.text(0.080, 0.036, 'SMC Status: ' + msc_rt, fontsize=12, ha='left', transform=self.a3.transAxes)

        # self.canvas = FigureCanvasTkAgg(self.f, master=root) -----------#
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        self.canvas._tkcanvas.pack(expand=True)
        # --------- call data block -------------------------------------#
        threading.Thread(target=self._dataControlLP, daemon=True).start()

    # ---------------- EXECUTE SYNCHRONOUS METHOD -----------------------#


    def _dataControlLP(self):
        s_fetch, stp_Sz, s_regm = str(lpS), lpTy, olS

        # Obtain Volatile Data from PLC Host Server ---------------------------[]
        if not dataReady:                          # Load Comm Plc class once
            lp_con = sq.DAQ_connect(1, 0)             # Connect PLC for real-time data
        else:
            pass

        # Evaluate conditions for SQL Data Fetch ------------------------------[A]
        """
        Load watchdog function with synchronous function every seconds
        """
        # Initialise RT variables ---[]
        autoSpcRun = True
        autoSpcPause = False
        import keyboard                         # for temporary use

        # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
        # sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
        # Define PLC/SMC error state -------------------------------------------#
        if UsePLC_DBS:
            import plcArrayRLmethodLP as slp                    # DrLabs optimization method
        elif UseSQL_DBS:
            import sqlArrayRLmethodLP as slp                    # DrLabs optimization method

        while True:
            if UsePLC_DBS:                                      # Not Using PLC Data
                sysRun, msctcp, msc_rt, cLayr = wd.autoPausePlay()
                if sysRun:
                    inProgress = True                               # True for RetroPlay mode
                else:
                    inProgress = False
                print('\nSynchronous controller activated...')

                # Either of the 2 combo variables are assigned to trigger routine pause
                if keyboard.is_pressed("Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:
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
                    self.lpDta = slp.plcExec(T1, s_fetch, stp_Sz, s_regm)
                    self.lpDtb = 0

            elif UseSQL_DBS:
                inProgress = True       # True for RetroPlay mode
                print('\nAsynchronous controller activated...')

                if keyboard.is_pressed("Alt+Q") and not inProgress:
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
                    self.lpDta, self.lpDtb = slp.sqlExec(lp_con, s_fetch, stp_Sz, s_regm, T1, T2)
                    print("Visualization in Play Mode...")
                print('\nUpdating....')
                # ------ Inhibit iteration ----------------------------------------------------------[]
                """
                # Set condition for halting real-time plots in watchdog class ---------------------
                """
                # TODO --- values for inhibiting the SQL processing
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    lp_con.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')
            else:
                pass
            self.canvas.get_tk_widget().after(2, self._lpDataPlot)  # Regime = every 10nseconds
            time.sleep(0.5)

    # ================== End of synchronous Method ==========================


    def _lpDataPlot(self):
        timei = time.time()                                 # start timing the entire loop

        if UsePLC_DBS == 1:
            import VarPLC_LP as lp

            # Call synchronous data function ---------------[]
            columns = qlp.validCols(T1)                     # Load defined valid columns for PLC Data
            df1 = pd.DataFrame(self.lpDta, columns=columns) # Include table data into python Dataframe
            LP = lp.loadProcesValues(df1)                   # Join data values under dataframe

        elif UseSQL_DBS:
            import VarSQL_LP as lp                          # load SQL variables column names | rfVarSQL
            g1 = qlp.validCols(T1)                          # Construct Data Column selSqlColumnsTFM.py
            d1 = pd.DataFrame(self.lpDta, columns=g1)
            g2 = qlp.validCols(T2)
            d2 = pd.DataFrame(self.lpDtb, columns=g2)       # Import into python Dataframe

            # Concatenate all columns -----------[]
            df1 = pd.concat([d1, d2], axis=1)          # Join data values under dataframe
            LP = lp.loadProcesValues(df1)
            print('\nSQL Content', df1.head(10))
            print("Memory Usage:", df1.info(verbose=False))     # Check memory utilization
        else:
            print('Unknown Process Protocol...')

        # -------------------------------------------------------------------------------------[]
        if UsePLC_DBS or UseSQL_DBS:
            im10.set_xdata(np.arange(self.win_Xmax))
            im11.set_xdata(np.arange(self.win_Xmax))
            im12.set_xdata(np.arange(self.win_Xmax))
            im13.set_xdata(np.arange(self.win_Xmax))
            im14.set_xdata(np.arange(self.win_Xmax))
            im15.set_xdata(np.arange(self.win_Xmax))
            im16.set_xdata(np.arange(self.win_Xmax))
            im17.set_xdata(np.arange(self.win_Xmax))
            im18.set_xdata(np.arange(self.win_Xmax))
            im19.set_xdata(np.arange(self.win_Xmax))
            im20.set_xdata(np.arange(self.win_Xmax))
            im21.set_xdata(np.arange(self.win_Xmax))
            im22.set_xdata(np.arange(self.win_Xmax))
            im23.set_xdata(np.arange(self.win_Xmax))
            im24.set_xdata(np.arange(self.win_Xmax))
            im25.set_xdata(np.arange(self.win_Xmax))
            # ------------------------------- S Plot
            im26.set_xdata(np.arange(self.win_Xmax))
            im27.set_xdata(np.arange(self.win_Xmax))
            im28.set_xdata(np.arange(self.win_Xmax))
            im29.set_xdata(np.arange(self.win_Xmax))
            im30.set_xdata(np.arange(self.win_Xmax))
            im31.set_xdata(np.arange(self.win_Xmax))
            im32.set_xdata(np.arange(self.win_Xmax))
            im33.set_xdata(np.arange(self.win_Xmax))
            im34.set_xdata(np.arange(self.win_Xmax))
            im35.set_xdata(np.arange(self.win_Xmax))
            im36.set_xdata(np.arange(self.win_Xmax))
            im37.set_xdata(np.arange(self.win_Xmax))
            im38.set_xdata(np.arange(self.win_Xmax))
            im39.set_xdata(np.arange(self.win_Xmax))
            im40.set_xdata(np.arange(self.win_Xmax))
            im41.set_xdata(np.arange(self.win_Xmax))      # lpS, lTy

            # X Plot Y-Axis data points for XBar --------------------------------------------[  # Ring 1 ]
            im10.set_ydata((LP[0]).rolling(window=lpS).mean()[0:self.win_Xmax])  # head 1
            im11.set_ydata((LP[1]).rolling(window=lpS).mean()[0:self.win_Xmax])  # head 2
            im12.set_ydata((LP[2]).rolling(window=lpS).mean()[0:self.win_Xmax])  # head 3
            im13.set_ydata((LP[3]).rolling(window=lpS).mean()[0:self.win_Xmax])  # head 4
            # ------ Evaluate Pp for Ring 1 ---------#
            mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(pAL, lpS, 'LP')
            # ---------------------------------------#
            im14.set_ydata((LP[4]).rolling(window=lpS).mean()[0:self.win_Xmax])  # head 1
            im15.set_ydata((LP[5]).rolling(window=lpS).mean()[0:self.win_Xmax])  # head 2
            im16.set_ydata((LP[6]).rolling(window=lpS).mean()[0:self.win_Xmax])  # head 3
            im17.set_ydata((LP[7]).rolling(window=lpS).mean()[0:self.win_Xmax])  # head 4
            # ------ Evaluate Pp for Ring 2 ---------#
            mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(pAL, lpS, 'LP')
            # ---------------------------------------#
            im18.set_ydata((LP[8]).rolling(window=lpS).mean()[0:self.win_Xmax])  # head 1
            im19.set_ydata((LP[9]).rolling(window=lpS).mean()[0:self.win_Xmax])  # head 2
            im20.set_ydata((LP[10]).rolling(window=lpS).mean()[0:self.win_Xmax])  # head 3
            im21.set_ydata((LP[11]).rolling(window=lpS).mean()[0:self.win_Xmax])  # head 4
            # ------ Evaluate Pp for Ring 3 ---------#
            mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(pAL, lpS, 'LP')
            # ---------------------------------------#
            im22.set_ydata((LP[12]).rolling(window=lpS).mean()[0:self.win_Xmax])  # head 1
            im23.set_ydata((LP[13]).rolling(window=lpS).mean()[0:self.win_Xmax])  # head 2
            im24.set_ydata((LP[14]).rolling(window=lpS).mean()[0:self.win_Xmax])  # head 3
            im25.set_ydata((LP[15]).rolling(window=lpS).mean()[0:self.win_Xmax])  # head 4
            # ------ Evaluate Pp for Ring 4 ---------#
            mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(pAL, lpS, 'LP')
            # ---------------------------------------#
            # S Plot Y-Axis data points for StdDev ----------------------------------------
            im26.set_ydata((LP[0]).rolling(window=lpS).std()[0:self.win_Xmax])
            im27.set_ydata((LP[1]).rolling(window=lpS).std()[0:self.win_Xmax])
            im28.set_ydata((LP[2]).rolling(window=lpS).std()[0:self.win_Xmax])
            im29.set_ydata((LP[3]).rolling(window=lpS).std()[0:self.win_Xmax])

            im30.set_ydata((LP[4]).rolling(window=lpS).std()[0:self.win_Xmax])
            im31.set_ydata((LP[5]).rolling(window=lpS).std()[0:self.win_Xmax])
            im32.set_ydata((LP[6]).rolling(window=lpS).std()[0:self.win_Xmax])
            im33.set_ydata((LP[7]).rolling(window=lpS).std()[0:self.win_Xmax])

            im34.set_ydata((LP[8]).rolling(window=lpS).std()[0:self.win_Xmax])
            im35.set_ydata((LP[9]).rolling(window=lpS).std()[0:self.win_Xmax])
            im36.set_ydata((LP[10]).rolling(window=lpS).std()[0:self.win_Xmax])
            im37.set_ydata((LP[11]).rolling(window=lpS).std()[0:self.win_Xmax])

            im38.set_ydata((LP[12]).rolling(window=lpS).std()[0:self.win_Xmax])
            im39.set_ydata((LP[13]).rolling(window=lpS).std()[0:self.win_Xmax])
            im40.set_ydata((LP[14]).rolling(window=lpS).std()[0:self.win_Xmax])
            im41.set_ydata((LP[15]).rolling(window=lpS).std()[0:self.win_Xmax])

            # Compute entire Process Capability -----------#
            if not pAL:
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLb, ppT, pkT, xline, sline = tq.tAutoPerf(lpS, mnA, mnB,
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
            if len(LP) > win_Xmax:
                LP.pop(0)
            self.canvas.draw_idle()

        else:
            print('Laser Power standby mode, no active session...')
            self.a2.text(0.440, 0.520, '--------- No Data Feed ---------', fontsize=12, ha='left',
                         transform=self.a2.transAxes)
            self.a1.text(0.440, 0.520, '--------- No Data Feed ---------', fontsize=12, ha='left',
                         transform=self.a1.transAxes)

        timef = time.time()
        lapsedT = timef - timei
        print(f"Process Interval LP: {lapsedT} sec\n")

# ------------------------------------------------------------------------------------------[Laser Angle Tab]


class laserAngleTabb(ttk.Frame):
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        global win_Xmin, win_Xmax, im10, im11, im12, im13, im14, im15, a1, a2, a3, laS, laTy, eolS, eopS, T1, T2

        import qParamsHL_MGM as mgm
        # Load Quality Historical Values -----------[]
        laS, laTy, eolS, eopS, laHL, laAL, laFO, laP1, laP2, laP3, laP4, laP5 = mgm.decryptpProcessLim(pWON, 'LA')

        # Break down each element to useful list ---------------[Tape Temperature]
        if laHL and laP1 and laP2 and laP3 and laP4 and laP5:  #
            laPerf = '$Pp_{k' + str(laS) + '}$'  # Using estimated or historical Mean
            lalabel = 'Pp'
            # -------------------------------
            One = laP1.split(',')                   # split into list elements
            Two = laP2.split(',')
            Thr = laP3.split(',')
            For = laP4.split(',')
            Fiv = laP5.split(',')
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
            laPerf = '$Cp_{k' + str(laS) + '}$'  # Using Automatic group Mean
            lalabel = 'Cp'

        # ------------------------------------[End of Tape Temperature Abstraction]

        label = ttk.Label(self, text='[' + str(pMode) + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Define Axes ---------------------#
        self.f = Figure(figsize=(pMtX, 8), dpi=100)
        self.f.subplots_adjust(left=0.022, bottom=0.05, right=0.983, top=0.955, wspace=0.117, hspace=0.157)
        # ---------------------------------[]
        self.a1 = self.f.add_subplot(2, 4, (1, 3))   # X Bar Plot
        self.a2 = self.f.add_subplot(2, 4, (5, 7))   # S Bar Plo
        self.a3 = self.f.add_subplot(2, 4, (4, 8))   # Performance Feeed
        # --------------- Former format -------------

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minLA, YScale_maxLA = laLSL - 8.5, laUSL + 8.5       # Roller Force
        sBar_minLA, sBar_maxLA = sLCLla - 80, sUCLla + 80           # Calibrate Y-axis for S-Plot
        self.win_Xmin, self.win_Xmax = 0, (int(laS) + 3)             # windows view = visible data points

        # ----------------------------------------------------------#
        # Real-Time Parameter according to updated requirements ----# 07/Feb/2025
        # Select betweeen straem -----------------------------------#
        if pRecipe == 1:                # PLC Data
            T1 = SPC_LA
        else:
            T1 = 'LA1_' + pWON          # SQL Data
            T2 = 'LA2_' + pWON          # SQL Data
        # ----------------------------------------------------------#

        # Initialise runtime limits
        self.a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        self.a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        self.a1.set_title('Laser Angle [XBar Plot]', fontsize=12, fontweight='bold')
        self.a2.set_title('Laser Angle [S Plot]', fontsize=12, fontweight='bold')

        self.a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        self.a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        self.a1.legend(loc='upper right', title='Laser Angle (Deg)')
        self.a2.legend(loc='upper right', title='Sigma curve')

        # ----------------------------------------------------------#
        self.a1.set_ylim([YScale_minLA, YScale_maxLA], auto=True)
        self.a1.set_xlim([self.win_Xmin, self.win_Xmax])
        # ----------------------------------------------------------#
        self.a2.set_ylim([sBar_minLA, sBar_maxLA], auto=True)
        self.a2.set_xlim([self.win_Xmin, self.win_Xmax])

        # ---------------------------------------------------------[]
        self.a3.cla()
        self.a3.get_yaxis().set_visible(False)
        self.a3.get_xaxis().set_visible(False)

        # ---------------------------------------------------------[]
        # Define Plot area and axes -
        # ---------------------------------------------------------#
        im10, = self.a1.plot([], [], 'o-.', label='Laser Angle - (R1H1)')
        im11, = self.a1.plot([], [], 'o-', label='Laser Angle - (R1H2)')
        im12, = self.a1.plot([], [], 'o-', label='Laser Angle - (R1H3)')
        im13, = self.a1.plot([], [], 'o-', label='Laser Angle - (R1H4)')
        im14, = self.a2.plot([], [], 'o-', label='Laser Angle')
        im15, = self.a2.plot([], [], 'o-', label='Laser Angle')
        im16, = self.a2.plot([], [], 'o-', label='Laser Angle')
        im17, = self.a2.plot([], [], 'o-', label='Laser Angle')

        im18, = self.a1.plot([], [], 'o-.', label='Laser Angle - (R2H1)')
        im19, = self.a1.plot([], [], 'o-', label='Laser Angle - (R2H2)')
        im20, = self.a1.plot([], [], 'o-', label='Laser Angle - (R2H3)')
        im21, = self.a1.plot([], [], 'o-', label='Laser Angle - (R2H4)')
        im22, = self.a2.plot([], [], 'o-', label='Laser Angle')
        im23, = self.a2.plot([], [], 'o-', label='Laser Angle')
        im24, = self.a2.plot([], [], 'o-', label='Laser Angle')
        im25, = self.a2.plot([], [], 'o-', label='Laser Angle')

        im26, = self.a1.plot([], [], 'o-.', label='Laser Angle - (R3H1)')
        im27, = self.a1.plot([], [], 'o-', label='Laser Angle - (R3H2)')
        im28, = self.a1.plot([], [], 'o-', label='Laser Angle - (R3H3)')
        im29, = self.a1.plot([], [], 'o-', label='Laser Angle - (R3H4)')
        im30, = self.a2.plot([], [], 'o-', label='Laser Angle')
        im31, = self.a2.plot([], [], 'o-', label='Laser Angle')
        im32, = self.a2.plot([], [], 'o-', label='Laser Angle')
        im33, = self.a2.plot([], [], 'o-', label='Laser Angle')

        im34, = self.a1.plot([], [], 'o-.', label='Laser Angle - (R4H1)')
        im35, = self.a1.plot([], [], 'o-', label='Laser Angle - (R4H2)')
        im36, = self.a1.plot([], [], 'o-', label='Laser Angle - (R4H3)')
        im37, = self.a1.plot([], [], 'o-', label='Laser Angle - (R4H4)')
        im38, = self.a2.plot([], [], 'o-', label='Laser Angle')
        im39, = self.a2.plot([], [], 'o-', label='Laser Angle')
        im40, = self.a2.plot([], [], 'o-', label='Laser Angle')
        im41, = self.a2.plot([], [], 'o-', label='Laser Angle')

        # Statistical Feed -----------------------------------------[]
        self.a3.text(0.466, 0.945, 'Performance Feed - LA', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=self.a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        self.rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        self.rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        self.a3.add_patch(self.rect1)
        self.a3.add_patch(self.rect2)
        # ------- Process Performance Pp (the spread)---------------------
        self.a3.text(0.145, 0.804, lalabel, fontsize=12, fontweight='bold', ha='center', transform=self.a3.transAxes)
        self.a3.text(0.328, 0.658, '#Pp Value', fontsize=24, fontweight='bold', ha='center', transform=self.a3.transAxes)
        self.a3.text(0.650, 0.820, 'Ring ' + lalabel + ' Data', fontsize=14, ha='left', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=self.a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        self.a3.text(0.145, 0.403, laPerf, fontsize=12, fontweight='bold', ha='center', transform=self.a3.transAxes)
        self.a3.text(0.328, 0.282, '#Ppk Value', fontsize=22, fontweight='bold', ha='center', transform=self.a3.transAxes)
        self.a3.text(0.640, 0.420, 'Ring ' + laPerf + ' Data', fontsize=14, ha='left', transform=self.a3.transAxes)
        # -------------------------------------
        self.a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=self.a3.transAxes)
        # ----- Pipe Position and SMC Status -----
        self.a3.text(0.080, 0.090, 'Pipe Position: ' + str(piPos) + '    Processing Layer #' + str(cLayerN), fontsize=12, ha='left',
                transform=self.a3.transAxes)
        self.a3.text(0.080, 0.036, 'SMC Status: ' + msc_rt, fontsize=12, ha='left', transform=self.a3.transAxes)

        # self.canvas = FigureCanvasTkAgg(self.f, master=root)
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        self.canvas._tkcanvas.pack(expand=True)
        # --------- call data block -------------------------------------#
        threading.Thread(target=self._dataControlLA, daemon=True).start()
        # ------------ EXECUTE SYNCHRONOUS METHOD -----------------------#


    def _dataControlLA(self):
        s_fetch, stp_Sz, s_regm = str(laS), laTy, eolS

        # Obtain Volatile Data from PLC Host Server ---------------------------[]
        if not dataReady:                        # Load ComsPlc class once
            la_con = sq.DAQ_connect(1, 0)
        else:
            pass

        # Evaluate conditions for SQL Data Fetch ------------------------------[A]
        """
        Load watchdog function with synchronous function every seconds
        """
        # Initialise RT variables ---[]
        autoSpcRun = True
        autoSpcPause = False
        import keyboard  # for temporary use

        # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
        # sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
        # Define PLC/SMC error state -------------------------------------------#

        if UsePLC_DBS:
            import plcArrayRLmethodLA as sla                # DrLabs optimization method
        elif UseSQL_DBS:
            import sqlArrayRLmethodLA as sla                # DrLabs optimization method

        while True:
            if UsePLC_DBS:                                  # Not Using PLC Data
                sysRun, msctcp, msc_rt, cLayr = wd.autoPausePlay()
                if sysRun:
                    inProgress = True                               # True for RetroPlay mode
                else:
                    inProgress = False

                # Either of the 2 combo variables are assigned to trigger routine pause
                if keyboard.is_pressed("Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:
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
                    self.laDta = sla.plcExec(T1, laS, s_fetch, stp_Sz, s_regm)
                    self.laDtb = 0


            elif UseSQL_DBS:
                inProgress = False  # False for Real-time mode
                print('\nSynchronous controller activated...')

                # Either of the 2 combo variables are assigned to trigger routine pause
                if keyboard.is_pressed("Alt+Q") and not inProgress:
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
                    self.laDta, self.laDtb = sla.sqlExec(la_con, s_fetch, stp_Sz, s_regm, T1, T2)
                    print("Visualization in Real-time Mode...")
                print('\nUpdating....')

                # ------ Inhibit iteration ----------------------------------------------------------[]
                """
                # Set condition for halting real-time plots in watchdog class ---------------------
                """
                # TODO --- values for inhibiting the SQL processing
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    la_con.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')
            else:
                pass
            self.canvas.get_tk_widget().after(s_regm, self._laDataPlot)  # Regime = every 10nseconds
            time.sleep(0.5)
    # ================== End of synchronous Method ==========================

    def _laDataPlot(self):
        timei = time.time()                                 # start timing the entire loop

        # Bistream Data Pooling Method ---------------------#

        if UsePLC_DBS == 1:
            import VarPLC_LA as la
            # Call synchronous data function ---------------[]
            columns = qla.validCols(T1)                         # Load defined valid columns for PLC Data
            df1 = pd.DataFrame(self.laDta, columns=columns)     # Include table data into python Dataframe
            LA = la.loadProcesValues(df1)                       # Join data values under dataframe

        elif UseSQL_DBS:
            import VarSQL_LA as la                              # load SQL variables column names | rfVarSQL
            # -----------------------------------------#
            g1 = qla.validCols(T1)                              # Construct Data Column selSqlColumnsTFM.py
            d1 = pd.DataFrame(self.laDta, columns=g1)           # Import into python Dataframe
            g2 = qla.validCols(T2)
            d2 = pd.DataFrame(self.laDtb, columns=g2)

            # Concatenate all columns -----------[]
            df1 = pd.concat([d1, d2], axis=1)
            LA = la.loadProcesValues(df1)                       # Join data values under dataframe
            print('\nSQL Content', df1.head(10))
            print("Memory Usage:", df1.info(verbose=False))     # Check memory utilization
        else:
            print('Unknown Process Protocol...')
        # -------------------------------------------#
        if UsePLC_DBS or UseSQL_DBS:
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
            im10.set_ydata((LA[0]).rolling(window=laS).mean()[0:db_freq])  # head 1
            im11.set_ydata((LA[1]).rolling(window=laS).mean()[0:db_freq])  # head 2
            im12.set_ydata((LA[2]).rolling(window=laS).mean()[0:db_freq])  # head 3
            im13.set_ydata((LA[3]).rolling(window=laS).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 1 ---------#
            mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(laHL, laS, 'LA')
            # ---------------------------------------#
            im14.set_ydata((LA[4]).rolling(window=laS).mean()[0:db_freq])  # head 1
            im15.set_ydata((LA[5]).rolling(window=laS).mean()[0:db_freq])  # head 2
            im16.set_ydata((LA[6]).rolling(window=laS).mean()[0:db_freq])  # head 3
            im17.set_ydata((LA[7]).rolling(window=laS).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 2 ---------#
            mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(laHL, laS, 'LA')
            # ---------------------------------------#
            im18.set_ydata((LA[8]).rolling(window=laS).mean()[0:db_freq])  # head 1
            im19.set_ydata((LA[9]).rolling(window=laS).mean()[0:db_freq])  # head 2
            im20.set_ydata((LA[10]).rolling(window=laS).mean()[0:db_freq])  # head 3
            im21.set_ydata((LA[11]).rolling(window=laS).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 3 ---------#
            mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(laHL, laS, 'LA')
            # ---------------------------------------#
            im22.set_ydata((LA[12]).rolling(window=laS).mean()[0:db_freq])  # head 1
            im23.set_ydata((LA[13]).rolling(window=laS).mean()[0:db_freq])  # head 2
            im24.set_ydata((LA[14]).rolling(window=laS).mean()[0:db_freq])  # head 3
            im25.set_ydata((LA[15]).rolling(window=laS).mean()[0:db_freq])  # head 4
            # ------ Evaluate Pp for Ring 4 ---------#
            mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(laHL, laS, 'LA')
            # ---------------------------------------#
            # S Plot Y-Axis data points for StdDev ----------------------------------------
            im26.set_ydata((LA[0]).rolling(window=laS).std()[0:db_freq])
            im27.set_ydata((LA[1]).rolling(window=laS).std()[0:db_freq])
            im28.set_ydata((LA[2]).rolling(window=laS).std()[0:db_freq])
            im29.set_ydata((LA[3]).rolling(window=laS).std()[0:db_freq])

            im30.set_ydata((LA[4]).rolling(window=laS).std()[0:db_freq])
            im31.set_ydata((LA[5]).rolling(window=laS).std()[0:db_freq])
            im32.set_ydata((LA[6]).rolling(window=laS).std()[0:db_freq])
            im33.set_ydata((LA[7]).rolling(window=laS).std()[0:db_freq])

            im34.set_ydata((LA[8]).rolling(window=laS).std()[0:db_freq])
            im35.set_ydata((LA[9]).rolling(window=laS).std()[0:db_freq])
            im36.set_ydata((LA[10]).rolling(window=laS).std()[0:db_freq])
            im37.set_ydata((LA[11]).rolling(window=laS).std()[0:db_freq])

            im38.set_ydata((LA[12]).rolling(window=laS).std()[0:db_freq])
            im39.set_ydata((LA[13]).rolling(window=laS).std()[0:db_freq])
            im40.set_ydata((LA[14]).rolling(window=laS).std()[0:db_freq])
            im41.set_ydata((LA[15]).rolling(window=laS).std()[0:db_freq])

            # Compute entire Process Capability -----------#
            if not laHL:
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLb, ppT, pkT, xline, sline = tq.tAutoPerf(laS, mnA, mnB,
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
            a1.axhspan(xlcT, xucT, facecolor='#F9C0FD', edgecolor='#F9C0FD')            # 3 Sigma span (Purple)
            a1.axhspan(xucT, xusT, facecolor='#8d8794', edgecolor='#8d8794')            # grey area
            a1.axhspan(xlcT, xlsT, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minLP, sBar_maxLP -------[]
            # Define Legend's Alaributes  ----
            a2.axhline(y=sline, color="blue", linestyle="--", linewidth=0.8)
            a2.axhspan(sLCLla, sUCLla, facecolor='#F9C0FD', edgecolor='#F9C0FD')        # 1 Sigma Span
            a2.axhspan(sUCLla, sBar_maxLA, facecolor='#CCCCFF', edgecolor='#CCCCFF')    # 1 Sigma above the Mean
            a2.axhspan(sBar_minLA, sLCLla, facecolor='#CCCCFF', edgecolor='#CCCCFF')

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if len(LA) > win_Xmax:
                LA.pop(0)
            self.canvas.draw_idle()

        else:
            print('Laser Angle standby mode, no active session...')
            self.a2.text(0.440, 0.520, '--------- No Data Feed ---------', fontsize=12, ha='left',
                         transform=self.a2.transAxes)
            self.a1.text(0.440, 0.520, '--------- No Data Feed ---------', fontsize=12, ha='left',
                         transform=self.a1.transAxes)

        timef = time.time()
        lapsedT = timef - timei
        print(f"Process Interval LA: {lapsedT} sec\n")
        # -----Canvas update --------------------------------------------[]
# ---------------------------------------------------------------------------------------------[Roller Force]
class rollerForceTabb(ttk.Frame):
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.running = False
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        global win_Xmin, win_Xmax, im10, im11, im12, im13, im14, im15, a1, a2, a3, rfS, rfTy, eolS, eopS, T1, T2

        # Load Quality Historical Values -----------[]
        if pRecipe == 'DNV':
            import qParamsHL_DNV as dnv
            rfS, rfTy, eolS, eopS, rfHL, rfAL, rfFO, rfP1, rfP2, rfP3, rfP4, rfP5 = dnv.decryptpProcessLim(pWON, 'RF')
        else:
            import qParamsHL_MGM as mgm
            rfS, rfTy, eolS, eopS, rfHL, rfAL, rfFO, rfP1, rfP2, rfP3, rfP4, rfP5 = mgm.decryptpProcessLim(pWON, 'RF')
        # Break down each element to useful list ---------------[Tape Temperature]

        if rfHL and rfP1 and rfP2 and rfP3 and rfP4 and rfP5:  #
            rfPerf = '$Pp_{k' + str(rfS) + '}$'  # Using estimated or historical Mean
            rflabel = 'Pp'
            # -------------------------------
            One = rfP1.split(',')                   # split into list elements
            Two = rfP2.split(',')
            Thr = rfP3.split(',')
            For = rfP4.split(',')
            Fiv = rfP5.split(',')
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
            rfPerf = '$Cp_{k' + str(rfS) + '}$'  # Using Automatic group Mean
            rflabel = 'Cp'

        # ------ [End of Historical abstraction -------]

        label = ttk.Label(self, text='[' + str(pMode) + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Define Axes ---------------------#
        self.f = Figure(figsize=(pMtX, 8), dpi=100)
        self.f.subplots_adjust(left=0.022, bottom=0.05, right=0.983, top=0.955, wspace=0.117, hspace=0.157)
        # ---------------------------------[]
        self.a1 = self.f.add_subplot(2, 4, (1, 3))   # X Bar Plot
        self.a2 = self.f.add_subplot(2, 4, (5, 7))   # S Bar Plo
        self.a3 = self.f.add_subplot(2, 4, (4, 8))   # Performance Feeed

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minRF, YScale_maxRF = 10, 500                        # Roller Force
        sBar_minRF, sBar_maxRF = 10, 250                            # Calibrate Y-axis for S-Plot
        self.win_Xmin, self.win_Xmax = 0, (int(rfS) + 3)            # windows view = visible data points

        # ----------------------------------------------------------#
        # Real-Time Parameter according to updated requirements ----# 28/Feb/2025
        if pRecipe == 1:                # PLC Data
            T1 = SPC_RF
        else:
            T1 = 'RF1_' + pWON          # SQL Data
            T2 = 'RF2_' + pWON
        # ----------------------------------------------------------#

        # Initialise runtime limits
        self.a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        self.a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        self.a1.set_title('Roller Force [XBar Plot]', fontsize=12, fontweight='bold')
        self.a2.set_title('Roller Force [S Plot]', fontsize=12, fontweight='bold')
        self.a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        self.a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        self.a1.legend(loc='upper right', title='Roller Force (N.m)')
        self.a2.legend(loc='upper right', title='Sigma curve')

        # ----------------------------------------------------------#
        self.a1.set_ylim([YScale_minRF, YScale_maxRF], auto=True)
        self.a1.set_xlim([self.win_Xmin, self.win_Xmax])
        # ----------------------------------------------------------#
        self.a2.set_ylim([sBar_minRF, sBar_maxRF], auto=True)
        self.a2.set_xlim([self.win_Xmin, self.win_Xmax])

        # ---------------------------------------------------------[]
        self.a3.cla()
        self.a3.get_yaxis().set_visible(False)
        self.a3.get_xaxis().set_visible(False)

        # ---------------------------------------------------------[]
        # Define Plot area and axes -
        # ---------------------------------------------------------#
        im10, = self.a1.plot([], [], 'o-', label='Roller Force - (R1H1)')
        im11, = self.a1.plot([], [], 'o-', label='Roller Force - (R1H2)')
        im12, = self.a1.plot([], [], 'o-', label='Roller Force - (R1H3)')
        im13, = self.a1.plot([], [], 'o-', label='Roller Force - (R1H4)')
        im14, = self.a2.plot([], [], 'o-', label='Roller Force')
        im15, = self.a2.plot([], [], 'o-', label='Roller Force')
        im16, = self.a2.plot([], [], 'o-', label='Roller Force')
        im17, = self.a2.plot([], [], 'o-', label='Roller Force')

        im18, = self.a1.plot([], [], 'o-', label='Roller Force - (R2H1)')
        im19, = self.a1.plot([], [], 'o-', label='Roller Force - (R2H2)')
        im20, = self.a1.plot([], [], 'o-', label='Roller Force - (R2H3)')
        im21, = self.a1.plot([], [], 'o-', label='Roller Force - (R2H4)')
        im22, = self.a2.plot([], [], 'o-', label='Roller Force')
        im23, = self.a2.plot([], [], 'o-', label='Roller Force')
        im24, = self.a2.plot([], [], 'o-', label='Roller Force')
        im25, = self.a2.plot([], [], 'o-', label='Roller Force')

        im26, = self.a1.plot([], [], 'o-', label='Roller Force - (R3H1)')
        im27, = self.a1.plot([], [], 'o-', label='Roller Force - (R3H2)')
        im28, = self.a1.plot([], [], 'o-', label='Roller Force - (R3H3)')
        im29, = self.a1.plot([], [], 'o-', label='Roller Force - (R3H4)')
        im30, = self.a2.plot([], [], 'o-', label='Roller Force')
        im31, = self.a2.plot([], [], 'o-', label='Roller Force')
        im32, = self.a2.plot([], [], 'o-', label='Roller Force')
        im33, = self.a2.plot([], [], 'o-', label='Roller Force')

        im34, = self.a1.plot([], [], 'o-', label='Roller Force - (R4H1)')
        im35, = self.a1.plot([], [], 'o-', label='Roller Force - (R4H2)')
        im36, = self.a1.plot([], [], 'o-', label='Roller Force - (R4H3)')
        im37, = self.a1.plot([], [], 'o-', label='Roller Force - (R4H4)')
        im38, = self.a2.plot([], [], 'o-', label='Roller Force')
        im39, = self.a2.plot([], [], 'o-', label='Roller Force')
        im40, = self.a2.plot([], [], 'o-', label='Roller Force')
        im41, = self.a2.plot([], [], 'o-', label='Roller Force')
        # --------------- Ramp Profile ---------------------------[ Important ]
        # im42, = self.a2.plot([], [], 'o-', label='Cumulated Ramp')
        # im43, = self.a2.plot([], [], 'o-', label='Nominal Ramp')

        # Statistical Feed -----------------------------------------[]
        self.a3.text(0.466, 0.945, 'Performance Feed - RF', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=self.a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        self.rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        self.rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        self.a3.add_patch(self.rect1)
        self.a3.add_patch(self.rect2)
        # ------- Process Performance Pp (the spread)---------------------
        self.a3.text(0.145, 0.804, rflabel, fontsize=12, fontweight='bold', ha='center', transform=self.a3.transAxes)
        self.a3.text(0.328, 0.658, '#Pp Value', fontsize=24, fontweight='bold', ha='center', transform=self.a3.transAxes)
        self.a3.text(0.650, 0.820, 'Ring ' + rflabel + ' Data', fontsize=14, ha='left', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=self.a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        self.a3.text(0.145, 0.403, rfPerf, fontsize=12, fontweight='bold', ha='center', transform=self.a3.transAxes)
        self.a3.text(0.328, 0.282, '#Ppk Value', fontsize=22, fontweight='bold', ha='center', transform=self.a3.transAxes)
        self.a3.text(0.640, 0.420, 'Ring ' + rfPerf + ' Data', fontsize=14, ha='left', transform=self.a3.transAxes)
        # -------------------------------------
        self.a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=self.a3.transAxes)
        # ----- Pipe Position and SMC Status -----
        self.a3.text(0.080, 0.090, 'Pipe Position: ' + str(piPos) + '    Processing Layer #' + str(cLayerN), fontsize=12, ha='left',
                transform=self.a3.transAxes)
        self.a3.text(0.080, 0.036, 'SMC Status: ' + msc_rt, fontsize=12, ha='left', transform=self.a3.transAxes)

        # self.canvas = FigureCanvasTkAgg(self.f, master=root)------------#
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        self.canvas._tkcanvas.pack(expand=True)
        # --------- call data block -------------------------------------#
        threading.Thread(target=self._dataControlRF, daemon=True).start()
        # ---------------- EXECUTE SYNCHRONOUS METHOD -------------------#

    def _dataControlRF(self):
        s_fetch, stp_Sz, s_regm = str(rfS), rfTy, eolS

        # Obtain Volatile Data from PLC Host Server ---------------------------[]
        if UseSQL_DBS and self.running:  # Load Coms Plc class once
            rf_con = sq.DAQ_connect(1, 0)
        else:
            pass
        # Evaluate conditions for SQL Data Fetch ------------------------------[A]
        """
        Load watchdog function with synchronous function every seconds
        """
        # Initialise RT variables ---[]
        autoSpcRun = True
        autoSpcPause = False
        import keyboard                                 # for temporary use

        # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
        # sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
        # Define PLC/SMC error state -------------------------------------------#
        if UsePLC_DBS:
            import plcArrayRLmethodRF as srf           # DrLabs optimization method
        elif UseSQL_DBS:
            import sqlArrayRLmethodRF as srf            # DrLabs optimization method

        while True:
            if UsePLC_DBS:                              # Not Using PLC Data
                sysRun, msctcp, msc_rt, cLayr = wd.autoPausePlay()
                if sysRun:
                    inProgress = True                               # True for RetroPlay mode
                else:
                    inProgress = False
                print('\nSynchronous controller activated...')

                # Either of the 2 combo variables are assigned to trigger routine pause
                if keyboard.is_pressed("Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:
                    print('\nProduction is pausing...')
                    if not autoSpcPause:
                        autoSpcRun = not autoSpcRun
                        autoSpcPause = True
                        # play(error)                            # Pause mode with audible Alert
                        print("\nVisualization in Paused Mode...")
                else:
                    autoSpcPause = False
                    print("Visualization in Play Mode...")
                    self.rfDta = srf.plcExec(T1, s_fetch, stp_Sz, s_regm)
                    self.rfDtb = 0

            elif UseSQL_DBS and self.running:
                inProgress = True  # True for RetroPlay mode
                print('\nAsynchronous controller activated...')
                print('DrLabs' + "' Runtime Optimisation is Enabled!")

                if keyboard.is_pressed("Alt+Q") and not inProgress:
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
                    self.rfDta, self.rfDtb = srf.sqlExec(rf_con, s_fetch, stp_Sz, s_regm, T1, T2)
                    print("Visualization in Play Mode...")
                print('\nUpdating....')
                # ------ Inhibit iteration ----------------------------------------------------------[]
                """
                # Set condition for halting real-time plots in watchdog class ---------------------
                """
                # TODO --- values for inhibiting the SQL processing
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    rf_con.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')
            else:
                pass
            self.canvas.get_tk_widget().after(s_regm, self._rfDataPlot)  # Regime = every 10nseconds
            time.sleep(0.5)
    # ================== End of synchronous Method ==========================


    def _rfDataPlot(self):
        timei = time.time()         # start timing the entire loop

        if UsePLC_DBS == 1:
            import VarPLCrf as rf
            # Call synchronous data function ---------------[]
            columns = qrf.validCols(T1)                     # Load defined valid columns for PLC Data
            df1 = pd.DataFrame(self.rfDta, columns=columns) # Include table data into python Dataframe
            RF = rf.loadProcesValues(df1)                   # Join data values under dataframe

        elif UseSQL_DBS:
            import VarSQL_RF as rf                           # load SQL variables column names | rfVarSQL
            # -----------------------------------------#
            g1 = qrf.validCols(T1)                           # Construct Data Column selSqlColumnsTFM.py
            d1 = pd.DataFrame(self.rfDta, columns=g1)        # Import into python Dataframe
            g2 = qrf.validCols(T1)                           # Construct Data Column selSqlColumnsTFM.py
            d2 = pd.DataFrame(self.rfDtb, columns=g2)

            # Concatenate all columns -----------------------[]
            df1 = pd.concat([d1, d2], axis=1)
            RF = rf.loadProcesValues(df1)                       # Join data values under dataframe
            print('\nSQL Content', df1.head(10))
            print("Memory Usage:", df1.info(verbose=False))         # Check memory utilization
        else:
            print('Unknown Process Protocol...')

        # -------------------------------------------------------------------------------------[]
        if UsePLC_DBS or UseSQL_DBS:
            im10.set_xdata(np.arange(self.win_Xmax))
            im11.set_xdata(np.arange(self.win_Xmax))
            im12.set_xdata(np.arange(self.win_Xmax))
            im13.set_xdata(np.arange(self.win_Xmax))
            im14.set_xdata(np.arange(self.win_Xmax))
            im15.set_xdata(np.arange(self.win_Xmax))
            im16.set_xdata(np.arange(self.win_Xmax))
            im17.set_xdata(np.arange(self.win_Xmax))
            im18.set_xdata(np.arange(self.win_Xmax))
            im19.set_xdata(np.arange(self.win_Xmax))
            im20.set_xdata(np.arange(self.win_Xmax))
            im21.set_xdata(np.arange(self.win_Xmax))
            im22.set_xdata(np.arange(self.win_Xmax))
            im23.set_xdata(np.arange(self.win_Xmax))
            im24.set_xdata(np.arange(self.win_Xmax))
            im25.set_xdata(np.arange(self.win_Xmax))
            # ------------------------------- S Plot
            im26.set_xdata(np.arange(self.win_Xmax))
            im27.set_xdata(np.arange(self.win_Xmax))
            im28.set_xdata(np.arange(self.win_Xmax))
            im29.set_xdata(np.arange(self.win_Xmax))
            im30.set_xdata(np.arange(self.win_Xmax))
            im31.set_xdata(np.arange(self.win_Xmax))
            im32.set_xdata(np.arange(self.win_Xmax))
            im33.set_xdata(np.arange(self.win_Xmax))
            im34.set_xdata(np.arange(self.win_Xmax))
            im35.set_xdata(np.arange(self.win_Xmax))
            im36.set_xdata(np.arange(self.win_Xmax))
            im37.set_xdata(np.arange(self.win_Xmax))
            im38.set_xdata(np.arange(self.win_Xmax))
            im39.set_xdata(np.arange(self.win_Xmax))
            im40.set_xdata(np.arange(self.win_Xmax))
            im41.set_xdata(np.arange(self.win_Xmax))

            # X Plot Y-Axis data points for XBar --------------------------------------------[  # Ring 1 ]
            im10.set_ydata((RF[0]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 1
            im11.set_ydata((RF[1]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 2
            im12.set_ydata((RF[2]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 3
            im13.set_ydata((RF[3]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 4
            # ------ Evaluate Pp for Ring 1 ---------#
            mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(rfHL, rfS, 'RF')
            # ---------------------------------------#
            im14.set_ydata((RF[4]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 1
            im15.set_ydata((RF[5]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 2
            im16.set_ydata((RF[6]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 3
            im17.set_ydata((RF[7]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 4
            # ------ Evaluate Pp for Ring 2 ---------#
            mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(rfHL, rfS, 'RF')
            # ---------------------------------------#
            im18.set_ydata((RF[8]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 1
            im19.set_ydata((RF[9]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 2
            im20.set_ydata((RF[10]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 3
            im21.set_ydata((RF[11]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 4
            # ------ Evaluate Pp for Ring 3 ---------#
            mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(rfHL, rfS, 'RF')
            # ---------------------------------------#
            im22.set_ydata((RF[12]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 1
            im23.set_ydata((RF[13]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 2
            im24.set_ydata((RF[14]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 3
            im25.set_ydata((RF[15]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 4
            # ------ Evaluate Pp for Ring 4 ---------#
            mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(rfHL, rfS, 'RF')
            # ---------------------------------------#
            # S Plot Y-Axis data points for StdDev ----------------------------------------
            im26.set_ydata((RF[0]).rolling(window=rfS).std()[0:self.win_Xmax])
            im27.set_ydata((RF[1]).rolling(window=rfS).std()[0:self.win_Xmax])
            im28.set_ydata((RF[2]).rolling(window=rfS).std()[0:self.win_Xmax])
            im29.set_ydata((RF[3]).rolling(window=rfS).std()[0:self.win_Xmax])

            im30.set_ydata((RF[4]).rolling(window=rfS).std()[0:self.win_Xmax])
            im31.set_ydata((RF[5]).rolling(window=rfS).std()[0:self.win_Xmax])
            im32.set_ydata((RF[6]).rolling(window=rfS).std()[0:self.win_Xmax])
            im33.set_ydata((RF[7]).rolling(window=rfS).std()[0:self.win_Xmax])

            im34.set_ydata((RF[8]).rolling(window=rfS).std()[0:self.win_Xmax])
            im35.set_ydata((RF[9]).rolling(window=rfS).std()[0:self.win_Xmax])
            im36.set_ydata((RF[10]).rolling(window=rfS).std()[0:self.win_Xmax])
            im37.set_ydata((RF[11]).rolling(window=rfS).std()[0:self.win_Xmax])

            im38.set_ydata((RF[12]).rolling(window=rfS).std()[0:self.win_Xmax])
            im39.set_ydata((RF[13]).rolling(window=rfS).std()[0:self.win_Xmax])
            im40.set_ydata((RF[14]).rolling(window=rfS).std()[0:self.win_Xmax])
            im41.set_ydata((RF[15]).rolling(window=rfS).std()[0:self.win_Xmax])

            # Compute entire Process Capability -----------#
            if not rfHL:
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLb, ppT, pkT, xline, sline = tq.tAutoPerf(rfS, mnA, mnB,
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
            if len(RF) > win_Xmax:
                RF.pop(0)
            self.canvas.draw_idle()
        else:
            print('Roller Force standby mode, no active session...')
            self.a2.text(0.440, 0.520, '--------- No Data Feed ---------', fontsize=12, ha='left',
                         transform=self.a2.transAxes)
            self.a1.text(0.440, 0.520, '--------- No Data Feed ---------', fontsize=12, ha='left',
                         transform=self.a1.transAxes)

        timef = time.time()
        lapsedT = timef - timei
        print(f"Process Interval RF: {lapsedT} sec\n")
        # -----Canvas update --------------------------------------------[]


# -----------------------------------------------------------------------------------------[Tape Temperature]
class tapeTempTabb(ttk.Frame):  # -- Defines the tabbed region for QA param - Tape Temperature --[]
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.running = False
        self.runRMP = False

        # prevents user possible double loading -----
        if not self.running:
            self.running = True
            threading.Thread(target=self.createProcessTT, daemon=True).start()
            print('[TT] is now running...')

    # ------------------------ Ramp Profiling Static Data Call/Stop Call ------------------[]
    def do_RMP_viz(self):
        if not self.runRMP:
            self.runRMP = True
            print('[RMP] Visualisation started ...')
            threading.Thread(target=self.dataControlRMP, daemon=True).start()
            self.rampVizCall()      # Acknowledge request

    def clear_RMP_viz(self):
        self.runRMP = False
        self.rampVizClose()

    def rampVizCall(self):
        messagebox.showinfo("RAMP:", "Ramp Profile successfully loaded!")

    def rampVizClose(self):
        messagebox.showinfo("RAMP:", "Ramp Profile successfully closed!")

    # -------------------------------------------------------------------------[ Pan/Zoom ]
    def pan_factory(self, ax):
        def on_press(event):
            if event.inaxes != ax:
                return
            ax._pan_start = event.x, event.y, ax.get_xlim(), ax.get_ylim()

        def on_release(event):
            ax._pan_start = None
            ax.figure.canvas.draw()

        def on_motion(event):
            if ax._pan_start is None or event.inaxes != ax:
                return

            x_press, y_press, xlim_start, ylim_start = ax._pan_start
            dx = event.x - x_press
            dy = event.y - y_press

            # Transform the mouse movement into data coordinates
            scale_x = (xlim_start[1] - xlim_start[0]) / ax.bbox.width
            scale_y = (ylim_start[1] - ylim_start[0]) / ax.bbox.height

            dx_data = dx * scale_x
            dy_data = dy * scale_y

            ax.set_xlim(xlim_start[0] - dx_data, xlim_start[1] - dx_data)
            ax.set_ylim(ylim_start[0] - dy_data, ylim_start[1] - dy_data)
            ax.figure.canvas.draw_idle()

        ax.figure.canvas.mpl_connect('button_press_event', on_press)
        ax.figure.canvas.mpl_connect('button_release_event', on_release)
        ax.figure.canvas.mpl_connect('motion_notify_event', on_motion)
        ax._pan_start = None
    # -------------------------- Ramp Profiling Static Data Call --------------------------[]

    def createProcessTT(self):
        """Create the widgets for the GUI"""
        global ttUCL, ttLCL, ttMean, ttDev, sUCLtt, sLCLtt, ttUSL, ttLSL #, im10, im11, im12, im13, im14, im15, im16, \
        # im17, im18, im19, im20, im21, im22, im23, im24, im25, im26, im27, im28, im29, im30, im31, im32, im33, im34, \
        # im35, im36, im37, im38, im39, im40, im41, im42, im43, im44, im45

        # Load Quality Historical Values -----------[]
        if pRecipe == 'DNV':
            import qParamsHL_DNV as qp
        else:
            import qParamsHL_MGM as qp
        # ------------------------------------------[]
        self.ttS, self.ttTy, self.olS, self.opS, self.DNV, self.AUTO, self.MGM, self.tape1, self.tape2, self.tape3, self.tape4, self.tape5 = qp.decryptpProcessLim(
            pWON, 'TT')

        if self.ttS == 0 or self.ttTy == 0:
            self.ttS, self.ttTy, self.olS, self.opS = 30, 1, 50, 20
        print('\nCondition met, reset variables', self.ttS, self.ttTy, self.olS, self.opS)

        # Break down each element to useful list ---------------[Tape Temperature]
        print('\nSamples/Group Samples:', self.ttS, self.ttTy)

        if self.tape1 != 0 and self.tape2 != 0 and self.tape3 != 0 and self.tape5 != 0 and self.tape5 != 0:
            ttPerf = '$Pp_{k' + str(self.ttS) + '}$'      # Using estimated or historical Mean
            ttlabel = 'Pp'
            # -------------------------------
            One = self.tape1.split(',')                   # split into list elements
            Two = self.tape2.split(',')
            Thr = self.tape3.split(',')
            For = self.tape4.split(',')
            Fiv = self.tape5.split(',')
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
        else:  # Use default Limit values
            ttUCL = 600
            ttLCL = 200
            ttMean = 400
            ttDev = 300
            sUCLtt = 450
            sLCLtt = 150
            ttUSL = 700
            ttLSL = 100
            # ttPerf = '$Cp_{k' + str(self.ttS) + '}$'  # Using Automatic group Mean
            # ttlabel = 'Cp'

        # ------------------------------------[End of Tape Temperature Abstraction]

        label = ttk.Label(self, text='[' + str(pMode) + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # -------------------------Button #
        ramp_report = ttk.Button(self, text="View Ramp Profile", command=self.do_RMP_viz)
        ramp_report.place(x=1850, y=1)      # 1970
        # ------
        ramp_clear = ttk.Button(self, text="Stop Ramp View", command=self.clear_RMP_viz)
        ramp_clear.place(x=1990, y=1)
        # Define Axes ---------------------#

        self.f = Figure(figsize=(pMtX, 8), dpi=100)
        self.f.subplots_adjust(left=0.026, bottom=0.05, right=0.983, top=0.936, wspace=0.18, hspace=0.174)
        # ---------------------------------[]
        self.a1 = self.f.add_subplot(2, 6, (1, 3))                 # xbar plot
        self.a2 = self.f.add_subplot(2, 6, (7, 9))                 # s bar plot
        self.a3 = self.f.add_subplot(2, 6, (4, 12))                # void mapping profile

        # Declare Plots attributes --------------------------------[H]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends

        # Calibrate limits for X-moving Axis -----------------------#
        self.y_minTT, self.y_maxTT = ttLSL - 8.5, ttUSL + 8.5       # Tape Temperature
        self.sBar_minTT, self.sBar_maxTT = sLCLtt - 80, sUCLtt + 80 # Calibrate Y-axis for S-Plot
        self.win_Xmin, self.win_Xmax = 0, 120                       # every 3 sec (1mt makes 20 visible data points)
        # ----------------------------------------------------------#
        YScale_minRM, YScale_maxRM = 0, pExLayer                    # Valid layer number
        self.win_XminRM, self.win_XmaxRM = 0, 10000                 # Get details from SCADA PIpe Recipe TODO[1]

        # Real-Time Parameter according to updated requirements ----# 07/Feb/2025
        if UseSQL_DBS:                                              # PLC Data - for Live Production Analysis
            # SQL Data --------------------#
            self.T1 = 'TT1_' + str(pWON)                            # Tape Temperature
            self.T2 = 'TT2_' + str(pWON)
        elif UsePLC_DBS:
            self.T1 = SPC_TT
        # self.T3 = 'RM_' + str(pWON) # replaced / switched to
        self.T3 = 'RC_' + str(pWON)
        # ----------------------------------------------------------#

        # Initialise runtime limits --------------------------------#
        self.a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        self.a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")

        self.a1.set_title('Tape Temperature [XBar]', fontsize=12, fontweight='bold')
        self.a2.set_title('Tape Temperature [SDev]', fontsize=12, fontweight='bold')
        self.a3.set_title('Ramp Mapping Profile - [RMP]', fontsize=12, fontweight='bold')
        self.a3.set_facecolor("blue")                        # set background color to blue
        zoom_factory(self.a3, base_scale=1.2)                # Allow plot's image  zooming, anchor='left'
        self.pan_factory(self.a3)
        # pan_handler = panhandler(self.a3, button=1)

        self.a3.set_ylabel("2D - Staked Layer Ramp Mapping")
        self.a3.set_xlabel("Sample Distance (mt)")
        self.a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        self.a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        self.a3.grid(color="0.5", linestyle='-', linewidth=0.5)
        self.a1.legend(['Tape Temperature'], loc='upper right', fontsize="x-large")
        self.a2.legend(['Sigma Curve'], loc='upper right', fontsize="x-large")
        self.a3.legend(['Temp Ramp Profile'], loc='upper right', fontsize="x-large")
        # ----------------------------------------------------------#
        self.a1.set_ylim([self.y_minTT, self.y_maxTT], auto=True)
        self.a1.set_xlim([self.win_Xmin, self.win_Xmax])
        # ----------------------------------------------------------#
        self.a2.set_ylim([self.sBar_minTT, self.sBar_maxTT], auto=True)
        self.a2.set_xlim([self.win_Xmin, self.win_Xmax])
        # --------------------------------------------------------[]
        self.a3.set_ylim([YScale_minRM, YScale_maxRM], auto=True)
        self.a3.set_xlim([self.win_XminRM, self.win_XmaxRM])

        # --------------------------------------------------------[]
        # Define Plot area and axes -
        # ---------------------------------------------------------#
        self.im10, = self.a1.plot([], [], 'o-', label='Tape Temp - (R1H1)')
        self.im11, = self.a1.plot([], [], 'o-', label='Tape Temp - (R1H2)')
        self.im12, = self.a1.plot([], [], 'o-', label='Tape Temp - (R1H3)')
        self.im13, = self.a1.plot([], [], 'o-', label='Tape Temp - (R1H4)')
        self.im14, = self.a2.plot([], [], 'o-', label='Tape Temp')
        self.im15, = self.a2.plot([], [], 'o-', label='Tape Temp')
        self.im16, = self.a2.plot([], [], 'o-', label='Tape Temp')
        self.im17, = self.a2.plot([], [], 'o-', label='Tape Temp')

        self.im18, = self.a1.plot([], [], 'o-', label='Tape Temp - (R2H1)')
        self.im19, = self.a1.plot([], [], 'o-', label='Tape Temp - (R2H2)')
        self.im20, = self.a1.plot([], [], 'o-', label='Tape Temp - (R2H3)')
        self.im21, = self.a1.plot([], [], 'o-', label='Tape Temp - (R2H4)')
        self.im22, = self.a2.plot([], [], 'o-', label='Tape Temp')
        self.im23, = self.a2.plot([], [], 'o-', label='Tape Temp')
        self.im24, = self.a2.plot([], [], 'o-', label='Tape Temp')
        self.im25, = self.a2.plot([], [], 'o-', label='Tape Temp')

        self.im26, = self.a1.plot([], [], 'o-', label='Tape Temp - (R3H1)')
        self.im27, = self.a1.plot([], [], 'o-', label='Tape Temp - (R3H2)')
        self.im28, = self.a1.plot([], [], 'o-', label='Tape Temp - (R3H3)')
        self.im29, = self.a1.plot([], [], 'o-', label='Tape Temp - (R3H4)')
        self.im30, = self.a2.plot([], [], 'o-', label='Tape Temp')
        self.im31, = self.a2.plot([], [], 'o-', label='Tape Temp')
        self.im32, = self.a2.plot([], [], 'o-', label='Tape Temp')
        self.im33, = self.a2.plot([], [], 'o-', label='Tape Temp')

        self.im34, = self.a1.plot([], [], 'o-', label='Tape Temp - (R4H1)')
        self.im35, = self.a1.plot([], [], 'o-', label='Tape Temp - (R4H2)')
        self.im36, = self.a1.plot([], [], 'o-', label='Tape Temp - (R4H3)')
        self.im37, = self.a1.plot([], [], 'o-', label='Tape Temp - (R4H4)')
        self.im38, = self.a2.plot([], [], 'o-', label='Tape Temp')
        self.im39, = self.a2.plot([], [], 'o-', label='Tape Temp')
        self.im40, = self.a2.plot([], [], 'o-', label='Tape Temp')
        self.im41, = self.a2.plot([], [], 'o-', label='Tape Temp')
        # --------------- Temperature Ramp Profile -------------------[  self.important ]
        self.im42, = self.a3.plot([], [], marker='|', color='w', linestyle='', label='Ramp R1')
        self.im43, = self.a3.plot([], [], marker='|', color='r', linestyle='', label='Ramp R2')
        self.im44, = self.a3.plot([], [], marker='|', color='g', linestyle='', label='Ramp R3')
        self.im45, = self.a3.plot([], [], marker='|', color='y', linestyle='', label='Ramp R4')

        # self.canvas = FigureCanvasTkAgg(self.f, master=root) ----------#
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        self.canvas._tkcanvas.pack(expand=True)

        # --------- call data block -------------------------------------#
        pTT = threading.Thread(target=self.dataControlTT, daemon=True)
        pTT.start()
        # ---------------- EXECUTE SYNCHRONOUS METHOD -------------------#


    def dataControlTT(self):
        global s_fetch, stp_Sz, batch_TT, sysRun, sysIdl, sysRdy, msc_rt, cLayer, piPos, mstatus

        batch_TT = 1
        s_fetch, stp_Sz = 30, 1
        # Evaluate conditions for SQL Data Fetch ------------------------------[A]

        # Obtain Volatile Data from PLC/SQL Host Server -------[]
        if UseSQL_DBS:
            if self.running:
                import sqlArrayRLmethodTT as tta
                tt_con = sq.sql_connectTT()
            else:
                tt_con = None

        elif UsePLC_DBS:
            if self.running:
                import plcArrayRLmethodTT as ttb
                print('\n[TT] Activating watchdog...')      # primary connection to watch dog
            else:
                # Dtt_ready = True
                print('[TT] Data Source selection is Unknown')
        else:
            print('[TT] Unknown Protocol...')

        # Initialise RT variables ---[]
        autoSpcRun = True
        paused = False
        sysRun, sysIdl, sysRdy, msc_rt, cLayer, piPos, mstatus = 0, 0, 0, 0, 0, 0, 'Pipe Position Not Specified'
        # ----------------------------------------------------------------------------#

        while True:
            # ------------------------------#
            if UseSQL_DBS or UsePLC_DBS and self.running:
                print('\n[TT] Synchronous controller activated...')

                if uCalling == 1:
                    sysRun, sysIdl, sysRdy, msc_rt, cLayer, piPos, mstatus = wd.autoPausePlay()

                    if not sysRun and not paused or msc_rt == 49296:
                        print('\n[TT] Live mode controller pausing...')
                        paused = True

                        while paused:
                            time.sleep(5)
                            print("\n[TT] Visualization in Paused Mode...")
                            sysRun, msctcp, msc_rt, cLayr = wd.rt_autoPausePlay()
                            if sysRun:
                                paused = False
                                print('[TT] Visualisation Resumes...')
                            time.sleep(0.2)
                    else:
                        print("[TT] Visualization in Real-time Mode...")
                        self.ttD1, self.rmD3 = ttb.plcExec(self.T1, self.T3, s_fetch, stp_Sz, batch_TT)
                        time.sleep(3)
                    # Closing up the Loop with batch_ var
                    self.canvas.get_tk_widget().after(0, self.ttDataPlot)
                    batch_TT += 1

                elif uCalling == 2 or uCalling == 3 and tt_con:
                    if keyboard.is_pressed("Alt+Q"):
                        paused = True

                        while paused:
                            time.sleep(5)
                            print("\n[TT Viz] Visualization in Paused Mode...")
                            sysRun, msctcp, msc_rt, cLayr = wd.rt_autoPausePlay()
                            if sysRun:
                                paused = False
                                print('[TT] Visualisation Resumes...')
                            time.sleep(0.2)

                    else:
                        print("[TT] Visualization in Real-time Mode...")
                        self.ttD1, self.ttD2 = tta.sqlExec(tt_con, s_fetch, stp_Sz, self.T1, self.T2, batch_TT)
                        time.sleep(3)
                        # Treat EOF as event ---------------------
                        if keyboard.is_pressed("Alt+Q") or not self.ttD1:  # Terminate file-fetch
                            tt_con.close()
                            print('SQL End of File, [TT] connection closes after 60 sec...')
                            time.sleep(60)
                            continue
                        else:
                                print('\n[TT] Updating....')
                    # ---------- Add batch loop here -----------------[]
                    if tt_con:
                        self.canvas.get_tk_widget().after(0, self.ttDataPlot)
                        batch_TT += 1
                    else:
                        print('[TT] sorry, instance not granted, trying again..')
                        tt_con = sq.check_SQL_Status(5, 10)

            else:
                print('\n[TT] is active but no visualisation!')
            print('[TT] protocol is refreshed, the wait is over...')

    # ================== End of synchronous Method ==========================--------------------[]
    def dataControlRMP(self):
        global batch_RMP, sysRun, sysIdl, sysRdy, msc_rt, cLayer, piPos, mstatus

        batch_RMP = 1
        s_fetch, stp_Sz = 100, 1
        # Evaluate conditions for SQL Data Fetch ------------------------------[A]

        # Obtain Volatile Data from PLC/SQL Host Server -------[]
        if UseSQL_DBS and self.running:
            import sqlArrayRLmethodRC as rC
            rmp_con = sq.sql_connectRMP()
        else:
            rmp_con = None

        # Initialise RT variables ---[]
        paused = False

        # ----------------------------------------------Only pulling from SQL Stream
        while True:
            if UseSQL_DBS and rmp_con:
                print('\n[RMP] PostProd Mode controller activated...')

                if uCalling == 1:
                    sysRun, sysIdl, sysRdy, msc_rt, cLayer, piPos, mstatus = wd.autoPausePlay()

                    if not sysRun and not paused:
                        print('[RMP] Live is pausing...')
                        paused = True

                        while paused:
                            time.sleep(5)
                            print("\n[RMP Viz] Visualization in Paused Mode...")
                            sysRun, msctcp, msc_rt, cLayr = wd.rt_autoPausePlay()
                            if sysRun:
                                paused = False
                                print('[RMP] Visualisation Resumes...')
                            time.sleep(0.2)
                    else:
                        self.rmD3 = rC.sqlExec(rmp_con, s_fetch, stp_Sz, self.T3, batch_RMP)
                        time.sleep(10)
                        print("[RMP] Visualization in Play Mode...")

                elif uCalling == 2 or uCalling == 3:
                    if keyboard.is_pressed("Alt+Q"):
                        paused = True

                        while paused:
                            time.sleep(5)
                            print("\n[RMP Viz] Visualization in Paused Mode...")
                            if keyboard.is_pressed("esc"):
                                paused = False
                                print('[RMP] Visualisation Resumes...')
                            time.sleep(0.2)
                    else:
                        self.rmD3 = rC.sqlExec(rmp_con, s_fetch, stp_Sz, self.T3, batch_RMP)
                        time.sleep(10)
                        print("[RMP] Visualization in Live Mode...")
                        # ------ Inhibit iteration ----------------------------------------[]
                        if not self.rmD3:  # Terminate file-fetch
                            rmp_con.close()  # close connection
                            print('SQL End of File, [RMP] connection closes after 30 secs...')
                            time.sleep(60)
                            continue
                        else:
                            print('\n[RMP] Updating....')
                # -------------------------------------------------------------------------[]
                if rmp_con:
                    self.canvas.get_tk_widget().after(0, self.rmDataPlot)
                    batch_RMP += 1
                else:
                    print('[RMP] sorry, instance not granted, trying again..')
                    rmp_con = sq.check_SQL_Status(5, 60)

            else:
                print('\n[RMP] is active but no visualisation!')
            print('[RMP] protocol is being refreshed...')

    # ================== End of synchronous Method ==========================--------------[]

    def ttDataPlot(self):
        timei = time.time()         # start timing the entire loop

        # Call data loader Method-----------------------#
        if UsePLC_DBS and self.running:
            import VarPLC_TT as tt
            # Call synchronous data PLC function ------[A]
            g1 = qtt.validCols(self.T1)                                 # Load PLC-dB [SPC_TT]
            df1 = pd.DataFrame(self.ttD1, columns=g1)                   # Include table data into python Dataframe
            # ------------------------------------------#
            # Do some data cleansing & interpolation if Nans occurs
            data1 = df1.select_dtypes(include=["number"])
            df1_interp = data1.interpolate(method="linear", axis=0).ffill().bfill()  # column-wise
            # Convert pandas -> cuDF
            if GPU_ENABLED:
                gpu_df1 = cudf.from_pandas(df1_interp.select_dtypes(include="number"))
                TT = tt.loadProcesValues(gpu_df1)
            else:
                TT = tt.loadProcesValues(df1_interp)                    # Join data values under dataframe

        elif UseSQL_DBS and self.running:
            import VarSQL_TT as tt                                      # load SQL variables column names | rfVarSQL
            g1 = qtt.validCols(self.T1)
            data1 = pd.DataFrame(self.ttD1, columns=g1)
            # Do some data cleansing ------------[Perform back or forward fill interpolation if Nans occurs]
            # data1 = data1.apply(pd.to_numeric, errors="coerce")
            data1 = data1.select_dtypes(include=["number"])
            df1_interp = data1.interpolate(method="linear", axis=0).ffill().bfill()  # column-wise
            if GPU_ENABLED:
                # Convert pandas -> cuDF
                gpu_df1 = cudf.from_pandas(df1_interp.select_dtypes(include="number"))
                TA = tt.loadPVT1(gpu_df1)
            else:
                TA = tt.loadPVT1(df1_interp)

            # ---------------------------------------------[]
            g2 = qtt.validCols(self.T2)
            data2 = pd.DataFrame(self.ttD2, columns=g2)
            # data2 = data2.apply(pd.to_numeric, errors="coerce")
            data2 = data2.select_dtypes(include=["number"])
            df2_interp = data2.interpolate(method="linear", axis=0).ffill().bfill()  # column-wise
            if GPU_ENABLED:
                # Convert pandas → cuDF
                gpu_df2 = cudf.from_pandas(df1_interp.select_dtypes(include="number"))
                TB = tt.loadPVT2(gpu_df2)
            else:
                TB = tt.loadPVT2(df2_interp)
            # --------------------------------------------[]
            # print("Memory Usage:", p_data.info(verbose=False))
            # print("Stats Usage:", tData1.describe())
            # print("Stats Usage:", tData2.describe())
            # print("Memory Usage:", p_data.head())
            # print('\nTP-In:', p_data.head())
            # --------------------------------------------[]
        else:
            TA = 0
            TB = 0
            print('[TT] Unknown Protocol...')

        # ------------------------------------------#
        if self.running:
            # print('Observations DataPoint:', len(TA[3]))
            self.a1.legend(loc='upper right', title='Tape Temp')
            self.a2.legend(loc='upper right', title='Sigma curve')
            # -------------------------------------[]
            # Plot X-Axis data points -------- X Plot
            self.im10.set_xdata(np.arange(batch_TT))
            self.im11.set_xdata(np.arange(batch_TT))
            self.im12.set_xdata(np.arange(batch_TT))
            self.im13.set_xdata(np.arange(batch_TT))
            self.im14.set_xdata(np.arange(batch_TT))
            self.im15.set_xdata(np.arange(batch_TT))
            self.im16.set_xdata(np.arange(batch_TT))
            self.im17.set_xdata(np.arange(batch_TT))
            self.im18.set_xdata(np.arange(batch_TT))
            self.im19.set_xdata(np.arange(batch_TT))
            self.im20.set_xdata(np.arange(batch_TT))
            self.im21.set_xdata(np.arange(batch_TT))
            self.im22.set_xdata(np.arange(batch_TT))
            self.im23.set_xdata(np.arange(batch_TT))
            self.im24.set_xdata(np.arange(batch_TT))
            self.im25.set_xdata(np.arange(batch_TT))
            # ------------------------------- S Plot
            self.im26.set_xdata(np.arange(batch_TT))
            self.im27.set_xdata(np.arange(batch_TT))
            self.im28.set_xdata(np.arange(batch_TT))
            self.im29.set_xdata(np.arange(batch_TT))
            self.im30.set_xdata(np.arange(batch_TT))
            self.im31.set_xdata(np.arange(batch_TT))
            self.im32.set_xdata(np.arange(batch_TT))
            self.im33.set_xdata(np.arange(batch_TT))
            self.im34.set_xdata(np.arange(batch_TT))
            self.im35.set_xdata(np.arange(batch_TT))
            self.im36.set_xdata(np.arange(batch_TT))
            self.im37.set_xdata(np.arange(batch_TT))
            self.im38.set_xdata(np.arange(batch_TT))
            self.im39.set_xdata(np.arange(batch_TT))
            self.im40.set_xdata(np.arange(batch_TT))
            self.im41.set_xdata(np.arange(batch_TT))

            # Compute rolling mean on GPU or CPU -
            if UsePLC_DBS:
                # X Plot Y-Axis data points for XBar --------------------------------------------[Ring 1 TT]
                self.im10.set_ydata((TT[1]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 1
                self.im11.set_ydata((TT[2]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 2
                self.im12.set_ydata((TT[3]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 3
                self.im13.set_ydata((TT[4]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 4
                # S Plot Y-Axis data points for StdDev ----------------------------------------[S Plot]
                self.im14.set_ydata((TT[1]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im15.set_ydata((TT[2]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im16.set_ydata((TT[3]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im17.set_ydata((TT[4]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])

                # X Bar Plot for Ring 2 --------------------------------------------------------[ Ring 2 TT]
                self.im18.set_ydata((TT[5]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 1
                self.im19.set_ydata((TT[6]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 2
                self.im20.set_ydata((TT[7]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 3
                self.im21.set_ydata((TT[8]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 4
                # S Plot for Ring 2 -------------------------------------------------------------[S Plot]
                self.im22.set_ydata((TT[5]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im23.set_ydata((TT[6]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im24.set_ydata((TT[7]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im25.set_ydata((TT[8]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])

                # X Bar Plot for Ring 3 --------------------------------------------------------[ Ring 3 TT]
                self.im26.set_ydata((TT[9]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 1
                self.im27.set_ydata((TT[10]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 2
                self.im28.set_ydata((TT[11]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 3
                self.im29.set_ydata((TT[12]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 4
                # ------ Evaluate Pp for Ring 3 ---------#
                self.im30.set_ydata((TT[9]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im31.set_ydata((TT[10]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im32.set_ydata((TT[11]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im33.set_ydata((TT[12]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])

                # X Bar Plot for Ring 4 --------------------------------------------------------[ Ring 4 TT]
                self.im34.set_ydata((TT[13]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 1
                self.im35.set_ydata((TT[14]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 2
                self.im36.set_ydata((TT[15]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 3
                self.im37.set_ydata((TT[16]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 4
                # ------ Evaluate Pp for Ring 4 ---------#
                self.im38.set_ydata((TT[13]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im39.set_ydata((TT[14]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im40.set_ydata((TT[15]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im41.set_ydata((TT[16]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
            else:
                # X Plot Y-Axis data points for XBar --------------------------------------------[Ring 1 TT]
                self.im10.set_ydata((TA[2]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 1
                self.im11.set_ydata((TA[3]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 2
                self.im12.set_ydata((TA[4]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 3
                self.im13.set_ydata((TA[5]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 4
                # S Plot Y-Axis data points for StdDev ----------------------------------------[S Plot]
                self.im14.set_ydata((TA[2]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im15.set_ydata((TA[3]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im16.set_ydata((TA[4]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im17.set_ydata((TA[5]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])

                # X Bar Plot for Ring 2 --------------------------------------------------------[ Ring 2 TT]
                self.im18.set_ydata((TA[6]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 1
                self.im19.set_ydata((TA[7]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 2
                self.im20.set_ydata((TA[8]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 3
                self.im21.set_ydata((TA[9]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 4
                # S Plot for Ring 2 -------------------------------------------------------------[S Plot]
                self.im22.set_ydata((TA[6]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im23.set_ydata((TA[7]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im24.set_ydata((TA[8]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im25.set_ydata((TA[9]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])

                # X Bar Plot for Ring 3 --------------------------------------------------------[ Ring 3 TT]
                self.im26.set_ydata((TB[2]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 1
                self.im27.set_ydata((TB[3]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 2
                self.im28.set_ydata((TB[4]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 3
                self.im29.set_ydata((TB[5]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 4
                # ------ Evaluate Pp for Ring 3 ---------#
                self.im30.set_ydata((TB[2]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im31.set_ydata((TB[3]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im32.set_ydata((TB[4]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im33.set_ydata((TB[5]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])

                # X Bar Plot for Ring 4 --------------------------------------------------------[ Ring 4 TT]
                self.im34.set_ydata((TB[6]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 1
                self.im35.set_ydata((TB[7]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 2
                self.im36.set_ydata((TB[8]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 3
                self.im37.set_ydata((TB[9]).rolling(window=s_fetch, min_periods=1).mean()[0:batch_TT])  # head 4
                # ------ Evaluate Pp for Ring 4 ---------#
                self.im38.set_ydata((TB[6]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im39.set_ydata((TB[7]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im40.set_ydata((TB[8]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])
                self.im41.set_ydata((TB[9]).rolling(window=s_fetch, min_periods=1).std()[0:batch_TT])

            # Declare Plots attributes --------------------------------------------------------[]
            # XBar Mean Plot
            self.a1.axhline(y=ttMean, color="red", linestyle="--", linewidth=0.8)
            self.a1.axhspan(ttLCL, ttUCL, facecolor='#6783e0', edgecolor='#6783e0')         # 3 Sigma span (Purple)
            self.a1.axhspan(ttUCL, ttUSL, facecolor='#8d8794', edgecolor='#8d8794')         # upper grey area
            self.a1.axhspan(ttLSL, ttLCL, facecolor='#8d8794', edgecolor='#8d8794')         # Lower grey area
            # ---------------------- sBar_minTT, sBar_maxTT -------[]
            self.a2.axhline(y=ttDev, color="blue", linestyle="--", linewidth=0.8)
            self.a2.axhspan(sLCLtt, sUCLtt, facecolor='#73de83', edgecolor='#73de83')           # 3 Sigma span (Purple)
            self.a2.axhspan(sUCLtt, self.sBar_maxTT, facecolor='#8d8794', edgecolor='#CCCCFF')  # upper grey area
            self.a2.axhspan(self.sBar_minTT, sLCLtt, facecolor='#8d8794', edgecolor='#CCCCFF')  # Lower grey area
            # Copy dynamic arrays ------
            # x_limits = self.a2.get_xlim()
            # print('Current View Size:', x_limits)

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if batch_TT > self.win_Xmax:
                self.a1.set_xlim(batch_TT - self.win_Xmax, batch_TT)
                self.a2.set_xlim(batch_TT - self.win_Xmax, batch_TT)
                TA.pop(0) # reset batch no
                TB.pop(0)
            else:
                self.a1.set_xlim(0, self.win_Xmax)
                self.a2.set_xlim(0, self.win_Xmax)
            self.canvas.draw_idle()

            # Set trip line for individual time-series plot -----------------------------------[R1]
            # sigma = gma.trigViolations(self.a1, uCalling, TT, self.y_minTT, self.y_maxTT, ttUCL, ttLCL, ttUSL, ttLSL, ttMean, ttDev)


        else:
            print('[TT] in standby mode, no active session...')
            self.a2.text(0.400, 0.520, '--------- No Data Feed ---------', fontsize=12, ha='left',
                         transform=self.a2.transAxes)
            self.a1.text(0.400, 0.520, '--------- No Data Feed ---------', fontsize=12, ha='left',
                         transform=self.a1.transAxes)
        timef = time.time()
        lapsedT = timef - timei
        self.canvas.draw_idle()
        print(f"\n[TT] Process Interval: {lapsedT} sec\n")

    # -----Canvas update ----------------------------------------[]

    def rmDataPlot(self):
        timei = time.time()  # start timing the entire loop

        # Call data loader Method-----------------------#
        if UseSQL_DBS and self.runRMP:
            import VarSQL_RC as rc
            g3 = qrc.validCols(self.T3)
            d3 = pd.DataFrame(self.rmD3, columns=g3)
            # Do some data cleansing ------------[Perform back or forward fill interpolation if Nans occurs]
            data1 = d3.apply(pd.to_numeric, errors="coerce")
            df3 = data1.interpolate(method="linear", axis=0).ffill().bfill()  # column-wise
            # print(df3.dtypes)
            # --------------------------------------#
            RM = rc.loadProcesValues(df3)
            # --------------------------------------#

        else:
            RM = 0
            print('[RMP] Unknown Protocol...')

        # ------------------------------------------#
        if self.runRMP:
            self.a3.legend(loc='upper right', title='Ramp Profile')
            # -------------------------------------[]
            # Plot X-Axis data points -------- X Plot
            self.im42.set_xdata(RM[2][0:self.win_XmaxRM])
            self.im43.set_xdata(RM[4][0:self.win_XmaxRM])
            self.im44.set_xdata(RM[6][0:self.win_XmaxRM])
            self.im45.set_xdata(RM[8][0:self.win_XmaxRM])
            # Compute entire Process Capability -----------#
            self.im42.set_ydata(RM[11])  # Layer Number reached
            self.im43.set_ydata(RM[11])
            self.im44.set_ydata(RM[11])
            self.im45.set_ydata(RM[11])

            # Setting up RMP parameters for static zoomable windows Axes --------------[]
            if batch_RMP > self.win_XmaxRM: # unlikely !
                RM.pop(0)
            else:
                self.a3.set_xlim(0, self.win_XmaxRM)
            self.canvas.draw_idle()

        else:
            print('[RMP] standby mode, no active session...')
            self.a3.text(0.400, 0.520, '--------- No Data Feed ---------', fontsize=12, ha='left',
                         transform=self.a3.transAxes)

        timef = time.time()
        lapsedT = timef - timei
        print(f"[RMP] Process Interval: {lapsedT} sec\n")
    # -----Canvas update ----------------------------------------[]


# ------------------------------------------------------------------------------------[Substrate Temperature]
class substTempTabb(ttk.Frame):
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.running = True

        # prevents user possible double loading -----
        if not self.running:
            self.running = True
            threading.Thread(target=self.createProcessST, daemon=True).start()
            print('[ST] is now running....')

    # ------------------------ Ramp Profiling Static Data Call/Stop Call ------------------[]
    def createProcessST(self):
        """Create the widgets for the GUI"""
        global xUCL, xLCL, xMean, sDev, sUCL, sLCL, xUSL, xLSL

        # Load Quality Historical Values -----------[]
        if pRecipe == 'DNV':
            import qParamsHL_DNV as qp
        else:
            import qParamsHL_MGM as qp
        # -----------------------------------------
        self.stS, self.stTy, self.olS, self.opS, self.DNV, self.AUTO, self.MGM, self.tape1, self.tape2, self.tape3, self.tape4, self.tape5 = qp.decryptpProcessLim(pWON, 'ST')
        if self.stS == 0 or self.stTy == 0:
            self.stS, self.stTy, self.olS, self.opS = 30, 1, 50, 20

        # Break down each element to useful list -----------[Substrate Temperature]

        if self.tape1 != 0 and self.tape2 != 0 and self.tape3 != 0 and self.tape5 != 0 and self.tape5 != 0:
            self.stPerf = '$Pp_{k' + str(self.stS) + '}$'  # Using estimated or historical Mean
            self.stlabel = 'Pp'
            # -------------------------------
            One = self.tape1.split(',')                       # split into list elements
            Two = self.tape2.split(',')
            Thr = self.tape3.split(',')
            For = self.tape4.split(',')
            Fiv = self.tape5.split(',')
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
                xUCL = float(One[2].strip("' "))           # Strip out the element of the list
                xLCL = float(One[3].strip("' "))
                xMean = float(One[4].strip("' "))
                sDev = float(One[5].strip("' "))
                # --------------------------------
                sUCL = float(One[6].strip("' "))
                sLCL = float(One[7].strip("' "))
                # --------------------------------
                xUSL = (xUCL - xMean) / 3 * 6
                xLSL = (xMean - xLCL) / 3 * 6
                # --------------------------------
            elif cpTapeW == dTape2 and cpLayerNo == 2:
                xUCL = float(Two[2].strip("' "))           # Strip out the element of the list
                xLCL = float(Two[3].strip("' "))
                xMean = float(Two[4].strip("' "))
                sDev = float(Two[5].strip("' "))
                # --------------------------------
                sUCL = float(Two[6].strip("' "))
                sLCL = float(Two[7].strip("' "))
                # --------------------------------
                xUSL = (xUCL - xMean) / 3 * 6
                xLSL = (xMean - xLCL) / 3 * 6
            elif cpTapeW == dTape3 and cpLayerNo == range(3, 40):
                xUCL = float(Thr[2].strip("' "))           # Strip out the element of the list
                xLCL = float(Thr[3].strip("' "))
                xMean = float(Thr[4].strip("' "))
                sDev = float(Thr[5].strip("' "))
                # --------------------------------
                sUCL = float(Thr[6].strip("' "))
                sLCL = float(Thr[7].strip("' "))
                # --------------------------------
                xUSL = (xUCL - xMean) / 3 * 6
                xLSL = (xMean - xLCL) / 3 * 6
            elif cpTapeW == dTape4 and cpLayerNo == 41:
                xUCL = float(For[2].strip("' "))           # Strip out the element of the list
                xLCL = float(For[3].strip("' "))
                xMean = float(For[4].strip("' "))
                sDev = float(For[5].strip("' "))
                # --------------------------------
                sUCL = float(For[6].strip("' "))
                sLCL = float(For[7].strip("' "))
                # --------------------------------
                xUSL = (xUCL - xMean) / 3 * 6
                xLSL = (xMean - xLCL) / 3 * 6
            else:
                xUCL = float(Fiv[2].strip("' "))           # Strip out the element of the list
                xLCL = float(Fiv[3].strip("' "))
                xMean = float(Fiv[4].strip("' "))
                sDev = float(Fiv[5].strip("' "))
                # --------------------------------
                sUCL = float(Fiv[6].strip("' "))
                sLCL = float(Fiv[7].strip("' "))
                # --------------------------------
                xUSL = (xUCL - xMean) / 3 * 6
                xLSL = (xMean - xLCL) / 3 * 6
                # -------------------------------
        else:  # Computes Shewhart constants (Automatic Limits)
            print('Loading arbitrary values for the plot..')
            xUCL = 500
            xLCL = 100
            xMean = 250
            sDev = 100
            sUCL = 200
            sLCL = 10
            xUSL = 550
            xLSL = 5
            self.stPerf = '$Cp_{k' + str(self.stS) + '}$'           # Using Automatic group Mean
            self.stlabel = 'Cp'

        label = ttk.Label(self, text='[' + str(pMode) + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Define Axes ---------------------#
        self.f = Figure(figsize=(pMtX, 8), dpi=100)    # 27
        self.f.subplots_adjust(left=0.029, bottom=0.05, right=0.983, top=0.955, wspace=0.117, hspace=0.157)
        # ---------------------------------[]
        self.a1 = self.f.add_subplot(2, 4, (1, 3))
        self.a2 = self.f.add_subplot(2, 4, (5, 7))
        self.a3 = self.f.add_subplot(2, 4, (4, 8))

        # Declare Plots attributes --------------------------------[]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minST, YScale_maxST = xLSL - 8.5, xUSL + 8.5
        self.sBar_minST, self.sBar_maxST = sLCL - 80, sUCL + 80     # Calibrate Y-axis for S-Plot
        self.win_Xmin, self.win_Xmax = 0, 120                       # windows view = visible data points

        # Load SQL Query Table -------------------------------------#
        if UseSQL_DBS:
            self.T1 = 'ST1_' + str(pWON)    # Identify Table
            self.T2 = 'ST2_' + str(pWON)
        else:
            self.T1 = SPC_ST
        # ----------------------------------------------------------#

        # Initialise runtime limits
        self.a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        self.a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")

        self.a1.set_title('Substrate Temperature [XBar]', fontsize=12, fontweight='bold')
        self.a2.set_title('Substrate Temperature [StDev]', fontsize=12, fontweight='bold')
        self.a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        self.a2.grid(color="0.5", linestyle='-', linewidth=0.5)

        self.a1.legend(['Substrate Temp'], loc='upper right', fontsize="x-large")
        self.a2.legend(['Sigma curve'], loc='upper right', fontsize="x-large")
        # ----------------------------------------------------------#
        self.a1.set_ylim([YScale_minST, YScale_maxST], auto=True)
        self.a1.set_xlim([self.win_Xmin, self.win_Xmax])
        # ----------------------------------------------------------#
        self.a2.set_ylim([self.sBar_minST, self.sBar_maxST], auto=True)
        self.a2.set_xlim([self.win_Xmin, self.win_Xmax])

        # ----------------------------------------------------------[]
        self.a3.cla()
        self.a3.get_yaxis().set_visible(False)
        self.a3.get_xaxis().set_visible(False)

        # ----------------------------------------------------------------[]
        # Define Plot area and axes -
        # ----------------------------------------------------------------#
        self.im10, = self.a1.plot([], [], 'o-', label='Substrate Temp - (R1H1)')
        self.im11, = self.a1.plot([], [], 'o-', label='Substrate Temp - (R1H2)')
        self.im12, = self.a1.plot([], [], 'o-', label='Substrate Temp - (R1H3)')
        self.im13, = self.a1.plot([], [], 'o-', label='Substrate Temp - (R1H4)')
        self.im14, = self.a2.plot([], [], '--', label='Substrate Temp')
        self.im15, = self.a2.plot([], [], '--', label='Substrate Temp')
        self.im16, = self.a2.plot([], [], '--', label='Substrate Temp')
        self.im17, = self.a2.plot([], [], '--', label='Substrate Temp')

        self.im18, = self.a1.plot([], [], 'o-', label='Substrate Temp - (R2H1)')
        self.im19, = self.a1.plot([], [], 'o-', label='Substrate Temp - (R2H2)')
        self.im20, = self.a1.plot([], [], 'o-', label='Substrate Temp - (R2H3)')
        self.im21, = self.a1.plot([], [], 'o-', label='Substrate Temp - (R2H4)')
        self.im22, = self.a2.plot([], [], '--', label='Substrate Temp')
        self.im23, = self.a2.plot([], [], '--', label='Substrate Temp')
        self.im24, = self.a2.plot([], [], '--', label='Substrate Temp')
        self.im25, = self.a2.plot([], [], '--', label='Substrate Temp')

        self.im26, = self.a1.plot([], [], 'o-', label='Substrate Temp - (R3H1)')
        self.im27, = self.a1.plot([], [], 'o-', label='Substrate Temp - (R3H2)')
        self.im28, = self.a1.plot([], [], 'o-', label='Substrate Temp - (R3H3)')
        self.im29, = self.a1.plot([], [], 'o-', label='Substrate Temp - (R3H4)')
        self.im30, = self.a2.plot([], [], '--', label='Substrate Temp')
        self.im31, = self.a2.plot([], [], '--', label='Substrate Temp')
        self.im32, = self.a2.plot([], [], '--', label='Substrate Temp')
        self.im33, = self.a2.plot([], [], '--', label='Substrate Temp')

        self.im34, = self.a1.plot([], [], 'o-', label='Substrate Temp - (R4H1)')
        self.im35, = self.a1.plot([], [], 'o-', label='Substrate Temp - (R4H2)')
        self.im36, = self.a1.plot([], [], 'o-', label='Substrate Temp - (R4H3)')
        self.im37, = self.a1.plot([], [], 'o-', label='Substrate Temp - (R4H4)')
        self.im38, = self.a2.plot([], [], '--', label='Substrate Temp')
        self.im39, = self.a2.plot([], [], '--', label='Substrate Temp')
        self.im40, = self.a2.plot([], [], '--', label='Substrate Temp')
        self.im41, = self.a2.plot([], [], '--', label='Substrate Temp')

        # Statistical Feed -----------------------------------------[]
        self.a3.text(0.466, 0.945, 'Performance Feed - ST', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=self.a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        self.rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        self.rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        self.a3.add_patch(self.rect1)
        self.a3.add_patch(self.rect2)
        # self.canvas = FigureCanvasTkAgg(self.f, master=root)------------#
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(self.canvas, self)
        # toolbar.update()
        # self.canvas._tkcanvas.pack(expand=True)

        # --------- call data block -------------------------------------#
        mp_ST = threading.Thread(target=self.dataControlST, daemon=True)
        mp_ST.start()
        # ---------------- EXECUTE SYNCHRONOUS METHOD -------------------#


    def dataControlST(self):
        global batch_ST, sysRun, sysIdl, sysRdy, msc_rt, cLayer, piPos, mstatus

        batch_ST = 1
        s_fetch, stp_Sz, s_regm = 30, self.stTy, self.olS      # entry value in string sql syntax ttS, ttTy,
        # Evaluate conditions for SQL Data Fetch ------------------------------[A]

        # Obtain Volatile Data from PLC/SQL Host Server -------[]
        if UseSQL_DBS:
            if self.running:
                import sqlArrayRLmethodST as stA
                st_con = sq.sql_connectST()
            else:
                st_con = None

        elif UsePLC_DBS:
            if self.running:
                import plcArrayRLmethodST as stB
                print('\n[ST] Activating watchdog...')
            else:
                # dtST_ready = True
                print('[ST] Data Source selection is Unknown')
        else:
            print('[ST] Unknown Protocol...')

        # Initialise RT variables ---[]
        autoSpcRun = True
        paused = False
        sysRun, sysIdl, sysRdy, msc_rt, cLayer, piPos, mstatus = 0, 0, 0, 0, 0, 0, 'Pipe Position Not Specified'

        while True:
            if UseSQL_DBS or UsePLC_DBS and self.running:
                print('\n[ST] Synchronous controller activated...')

                if uCalling == 1:
                    sysRun, sysIdl, sysRdy, msc_rt, cLayer, piPos, mstatus = wd.autoPausePlay()

                    if not sysRun and not paused or msc_rt == 49296:  # Terminate file-fetch
                        print('\n[ST] Production is pausing...')
                        paused = True

                        while paused:
                            time.sleep(5)
                            print("\n[ST] Visualization in Paused Mode...")
                            sysRun, msctcp, msc_rt, cLayr = wd.rt_autoPausePlay()
                            if sysRun:
                                paused = False
                                print('[ST] Visualisation Resumes...')
                            time.sleep(0.2)
                    else:
                        print("[ST] Visualization in Real-time Mode...")
                        # -----------------------------------------------------------------[]
                        self.stDta = stB.plcExec(self.T1, s_fetch, stp_Sz, s_regm)
                        time.sleep(3)
                    self.canvas.get_tk_widget().after(0, self.stDataPlot)
                    batch_ST += 1

                elif uCalling == 2 or uCalling == 3 and st_con:
                    if keyboard.is_pressed("Alt+Q"):
                        paused = True

                        while paused:
                            time.sleep(5)
                            print("\n[ST Viz] Visualization in Paused Mode...")
                            sysRun, msctcp, msc_rt, cLayr = wd.rt_autoPausePlay()
                            if sysRun:
                                paused = False
                                print('[ST] Visualisation Resumes...')
                            time.sleep(0.2)
                    else:
                        self.stDta, self.stDtb = stA.sqlExec(st_con, s_fetch, stp_Sz, self.T1, self.T2, batch_ST)
                        time.sleep(3)
                        # Treat EOF as event ---------------------
                        if keyboard.is_pressed("Alt+Q") or not self.stDta:  # Terminate file-fetch
                            st_con.close()  # DB connection close
                            print('SQL End of File, [ST] connection closes after 30 mins...')
                            time.sleep(60)
                            continue
                        else:
                            print('\n[ST] Updating....')
                    if st_con:
                        self.canvas.get_tk_widget().after(0, self.stDataPlot)
                        batch_ST += 1
                    else:
                        print('[ST] sorry, instance not granted, trying again..')
                        st_con = sq.check_SQL_Status(5, 10)

            else:
                print('[ST] is active but no visualisation!\n')
            print('[ST] protocol is refreshed, the wait is over...')

    # ================== End of synchronous Method ==========================

    def stDataPlot(self):
        timei = time.time()                                 # start timing the entire loop

        # Call data loader Method---------------------#
        if UsePLC_DBS and self.running:
            import VarPLC_ST as st
            # Call synchronous data function ---------[]
            g1 = qst.validCols(self.T1)                         # Load defined valid columns for PLC Data
            df1 = pd.DataFrame(self.stDta, columns=g1)          # Include table data into python Dataframe
            # ------------------------------------------#
            # Do some data cleansing & interpolation if Nans occurs
            data1 = df1.select_dtypes(include=["number"])
            df1_interp = data1.interpolate(method="linear", axis=0).ffill().bfill()  # column-wise
            # Convert pandas -> cuDF
            if GPU_ENABLED:
                gpu_df1 = cudf.from_pandas(df1_interp.select_dtypes(include="number"))
                ST = st.loadProcesValues(gpu_df1)                    # Join data values under dataframe
            else:
                ST = st.loadProcesValues(df1_interp)                 # Join data values under dataframe
            # print("Memory Usage:", df1.info(verbose=False))

        elif UseSQL_DBS and self.running:
            import VarSQL_ST as st
            g1 = qst.validCols(self.T1)                     # Construct Data Column selSqlColumnsTFM.py
            d1 = pd.DataFrame(self.stDta, columns=g1)       # Import into python Dataframe
            g2 = qst.validCols(self.T2)
            d2 = pd.DataFrame(self.stDtb, columns=g2)

            p_data = pd.concat([d1, d2], axis=1)
            # ----------------------------------
            # Do some data cleansing & interpolation if Nans occurs
            data1 = p_data.select_dtypes(include=["number"])
            df1_interp = data1.interpolate(method="linear", axis=0).ffill().bfill()  # column-wise
            # Convert pandas -> cuDF
            if GPU_ENABLED:
                gpu_df1 = cudf.from_pandas(df1_interp.select_dtypes(include="number"))
                ST = st.loadProcesValues(gpu_df1)
            else:
                ST = st.loadProcesValues(df1_interp)
            # ---------------------------------
            # print('\nSQL Content [ST]', p_data.head())
            # print("Memory Usage:", p_data.info(verbose=False))
            # --------------------------------------#
        else:
            ST = 0
            print('[ST] Unknown Protocol...')

        # -------------------------------------------#
        if self.running:
            self.a1.legend(loc='upper right', title='Substrate Temp')
            self.a2.legend(loc='upper right', title='Sigma curve')
            # ---------------------------------------[]
            # Plot X-Axis data points -------- X Plot
            self.im10.set_xdata(np.arange(batch_ST))
            self.im11.set_xdata(np.arange(batch_ST))
            self.im12.set_xdata(np.arange(batch_ST))
            self.im13.set_xdata(np.arange(batch_ST))
            self.im14.set_xdata(np.arange(batch_ST))
            self.im15.set_xdata(np.arange(batch_ST))
            self.im16.set_xdata(np.arange(batch_ST))
            self.im17.set_xdata(np.arange(batch_ST))
            self.im18.set_xdata(np.arange(batch_ST))
            self.im19.set_xdata(np.arange(batch_ST))
            self.im20.set_xdata(np.arange(batch_ST))
            self.im21.set_xdata(np.arange(batch_ST))
            self.im22.set_xdata(np.arange(batch_ST))
            self.im23.set_xdata(np.arange(batch_ST))
            self.im24.set_xdata(np.arange(batch_ST))
            self.im25.set_xdata(np.arange(batch_ST))
            # ------------------------------- S Plot
            self.im26.set_xdata(np.arange(batch_ST))
            self.im27.set_xdata(np.arange(batch_ST))
            self.im28.set_xdata(np.arange(batch_ST))
            self.im29.set_xdata(np.arange(batch_ST))
            self.im30.set_xdata(np.arange(batch_ST))
            self.im31.set_xdata(np.arange(batch_ST))
            self.im32.set_xdata(np.arange(batch_ST))
            self.im33.set_xdata(np.arange(batch_ST))
            self.im34.set_xdata(np.arange(batch_ST))
            self.im35.set_xdata(np.arange(batch_ST))
            self.im36.set_xdata(np.arange(batch_ST))
            self.im37.set_xdata(np.arange(batch_ST))
            self.im38.set_xdata(np.arange(batch_ST))
            self.im39.set_xdata(np.arange(batch_ST))
            self.im40.set_xdata(np.arange(batch_ST))
            self.im41.set_xdata(np.arange(batch_ST))
            # X Plot Y-Axis data points for XBar --------------------------------------------[# Ring 1 ]
            self.im10.set_ydata((ST[3]).rolling(window=self.stS, min_periods=1).mean()[0:batch_ST])  # head 1
            self.im11.set_ydata((ST[4]).rolling(window=self.stS, min_periods=1).mean()[0:batch_ST])  # head 2
            self.im12.set_ydata((ST[5]).rolling(window=self.stS, min_periods=1).mean()[0:batch_ST])  # head 3
            self.im13.set_ydata((ST[6]).rolling(window=self.stS, min_periods=1).mean()[0:batch_ST])  # head 4
            # S Plot Y-Axis data points for StdDev ----------------------------------------------
            self.im14.set_ydata((ST[3]).rolling(window=self.stS, min_periods=1).std()[0:batch_ST])
            self.im15.set_ydata((ST[4]).rolling(window=self.stS, min_periods=1).std()[0:batch_ST])
            self.im16.set_ydata((ST[5]).rolling(window=self.stS, min_periods=1).std()[0:batch_ST])
            self.im17.set_ydata((ST[6]).rolling(window=self.stS, min_periods=1).std()[0:batch_ST])
            # ------ Evaluate Pp for Ring 1 ---------#
            rMa = ((ST[3]).mean() + (ST[4]).mean() + (ST[5]).mean() + (ST[6]).mean()).mean()
            sda = [ST[3].std(), ST[4].std(), ST[5].std(), ST[6].std()]
            sMa = np.std(sda)
            PpA, PkA = tz.processCap(rMa, sMa, xUSL, xLSL, self.stS)
            # ---------------------------------------#
            self.im18.set_ydata((ST[7]).rolling(window=self.stS, min_periods=1).mean()[0:batch_ST])  # head 1
            self.im19.set_ydata((ST[8]).rolling(window=self.stS, min_periods=1).mean()[0:batch_ST])  # head 2
            self.im20.set_ydata((ST[9]).rolling(window=self.stS, min_periods=1).mean()[0:batch_ST])  # head 3
            self.im21.set_ydata((ST[10]).rolling(window=self.stS, min_periods=1).mean()[0:batch_ST])  # head 4
            # # S Plot Y-Axis data points for StdDev ---------------------------------------#
            self.im22.set_ydata((ST[7]).rolling(window=self.stS, min_periods=1).std()[0:batch_ST])
            self.im23.set_ydata((ST[8]).rolling(window=self.stS, min_periods=1).std()[0:batch_ST])
            self.im24.set_ydata((ST[9]).rolling(window=self.stS, min_periods=1).std()[0:batch_ST])
            self.im25.set_ydata((ST[10]).rolling(window=self.stS, min_periods=1).std()[0:batch_ST])
            # ------ Evaluate Pp for Ring 2 ---------#
            rMb = ((ST[7]).mean() + (ST[8]).mean() + (ST[9]).mean() + (ST[10]).mean()).mean()
            sdb = [ST[7].std(), ST[8].std(), ST[9].std(), ST[10].std()]
            sMb = np.std(sdb)
            PpB, PkB = tz.processCap(rMb, sMb, xUSL, xLSL, self.stS)
            # ---------------------------------------#
            self.im26.set_ydata((ST[14]).rolling(window=self.stS, min_periods=1).mean()[0:batch_ST])  # head 1
            self.im27.set_ydata((ST[15]).rolling(window=self.stS, min_periods=1).mean()[0:batch_ST])  # head 2
            self.im28.set_ydata((ST[16]).rolling(window=self.stS, min_periods=1).mean()[0:batch_ST])  # head 3
            self.im29.set_ydata((ST[17]).rolling(window=self.stS, min_periods=1).mean()[0:batch_ST])  # head 4
            # # S Plot Y-Axis data points for StdDev ---------------------------------------#
            self.im30.set_ydata((ST[14]).rolling(window=self.stS, min_periods=1).std()[0:batch_ST])
            self.im31.set_ydata((ST[15]).rolling(window=self.stS, min_periods=1).std()[0:batch_ST])
            self.im32.set_ydata((ST[16]).rolling(window=self.stS, min_periods=1).std()[0:batch_ST])
            self.im33.set_ydata((ST[17]).rolling(window=self.stS, min_periods=1).std()[0:batch_ST])
            # ------ Evaluate Pp for Ring 3 ---------#
            rMc = ((ST[14]).mean() + (ST[15]).mean() + (ST[16]).mean() + (ST[17]).mean()).mean()
            sdc = [ST[14].std(), ST[15].std(), ST[16].std(), ST[17].std()]
            sMc = np.std(sdc)
            PpC, PkC = tz.processCap(rMc, sMc, xUSL, xLSL, self.stS)
            # ---------------------------------------#
            self.im34.set_ydata((ST[18]).rolling(window=self.stS, min_periods=1).mean()[0:batch_ST])  # head 1
            self.im35.set_ydata((ST[19]).rolling(window=self.stS, min_periods=1).mean()[0:batch_ST])  # head 2
            self.im36.set_ydata((ST[20]).rolling(window=self.stS, min_periods=1).mean()[0:batch_ST])  # head 3
            self.im37.set_ydata((ST[21]).rolling(window=self.stS, min_periods=1).mean()[0:batch_ST])  # head 4
            # S Plot Y-Axis data points for StdDev --------------------------------------------#
            self.im38.set_ydata((ST[18]).rolling(window=self.stS, min_periods=1).std()[0:batch_ST])
            self.im39.set_ydata((ST[19]).rolling(window=self.stS, min_periods=1).std()[0:batch_ST])
            self.im40.set_ydata((ST[20]).rolling(window=self.stS, min_periods=1).std()[0:batch_ST])
            self.im41.set_ydata((ST[21]).rolling(window=self.stS, min_periods=1).std()[0:batch_ST])
            # ------ Evaluate Pp for Ring 4 ---------#
            rMd = ((ST[18]).mean() + (ST[19]).mean() + (ST[20]).mean() + (ST[21]).mean()).mean()
            sdd = [ST[18].std(), ST[19].std(), ST[20].std(), ST[21].std()]
            sMd = np.std(sdd)
            PpD, PkD = tz.processCap(rMd, sMd, xUSL, xLSL, self.stS)
            # ---------------------------------------#
            # Compute for ST Process PP/Cpk ------------#
            # Cp, Cpk = tz.hisCap(stMean, stDev, stUSL, stLSL)
            Cp, Cpk = tz.processCap(xMean, sDev, xUSL, xLSL, self.stS)

            # XBar Mean Plot ------------------------#
            self.a1.axhline(y=xMean, color="red", linestyle="--", linewidth=0.8)
            self.a1.axhspan(xLCL, xUCL, facecolor='#F9C0FD', edgecolor='#F9C0FD')             # 3 Sigma span (Purple)
            self.a1.axhspan(xUCL, xUSL, facecolor='#8d8794', edgecolor='#8d8794')             # grey area
            self.a1.axhspan(xLSL, xLCL, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minST, sBar_maxST -------[]
            # Define Legend's Attributes  ----
            self.a2.axhline(y=sDev, color="blue", linestyle="--", linewidth=0.8)
            self.a2.axhspan(sLCL, sUCL, facecolor='#F9C0FD', edgecolor='#F9C0FD')           # 1 Sigma Span
            self.a2.axhspan(sLCL, self.sBar_maxST, facecolor='#CCCCFF', edgecolor='#CCCCFF')  # 1 Sigma above the Mean
            self.a2.axhspan(self.sBar_minST, sLCL, facecolor='#CCCCFF', edgecolor='#CCCCFF')

            # -----------------------------------------------------------------------------------[]
            self.a3.cla()
            self.a3.text(0.466, 0.945, 'Performance Feed - ST', fontsize=16, fontweight='bold', ha='center',
                         va='center',
                         transform=self.a3.transAxes)
            # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
            self.rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
            self.rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
            self.a3.add_patch(self.rect1)
            self.a3.add_patch(self.rect2)
            self.a3.text(0.145, 0.804, self.stlabel, fontsize=12, fontweight='bold', ha='center',
                         transform=self.a3.transAxes)
            self.a3.text(0.328, 0.658, round(Cp,2), fontsize=28, fontweight='bold', ha='center',
                         transform=self.a3.transAxes)
            self.a3.text(0.650, 0.820, 'Ring ' + self.stlabel + ' Data', fontsize=14, ha='left', transform=self.a3.transAxes)
            self.a3.text(0.755, 0.745, str(round(PpA, 3)), fontsize=12, ha='center', transform=self.a3.transAxes)
            self.a3.text(0.755, 0.685, str(round(PpB, 3)), fontsize=12, ha='center', transform=self.a3.transAxes)
            self.a3.text(0.755, 0.625, str(round(PpC, 3)), fontsize=12, ha='center', transform=self.a3.transAxes)
            self.a3.text(0.755, 0.565, str(round(PpD, 3)), fontsize=12, ha='center', transform=self.a3.transAxes)
            # ------- Process Performance Ppk (Performance)---------------------
            self.a3.text(0.145, 0.403, self.stPerf, fontsize=12, fontweight='bold', ha='center', transform=self.a3.transAxes)
            self.a3.text(0.328, 0.282, round(Cpk, 2), fontsize=28, fontweight='bold', ha='center',
                         transform=self.a3.transAxes)
            self.a3.text(0.640, 0.420, 'Ring ' + self.stPerf + ' Data', fontsize=14, ha='left', transform=self.a3.transAxes)
            # -------------------------------------
            self.a3.text(0.755, 0.360, str(round(PkA,3)), fontsize=12, ha='center', transform=self.a3.transAxes)
            self.a3.text(0.755, 0.300, str(round(PkB,3)), fontsize=12, ha='center', transform=self.a3.transAxes)
            self.a3.text(0.755, 0.240, str(round(PkC,3)), fontsize=12, ha='center', transform=self.a3.transAxes)
            self.a3.text(0.755, 0.180, str(round(PkD,3)), fontsize=12, ha='center', transform=self.a3.transAxes)
            # ----- Pipe Position and SMC Status -----
            self.a3.text(0.080, 0.090, 'Pipe Position: ' + str(round(piPos, 4)) + '    Processing Layer #:' + str(cLayer),
                         fontsize=12, ha='left',
                         transform=self.a3.transAxes)
            self.a3.text(0.080, 0.036, 'SMC Status: ' + str(mstatus), fontsize=12, ha='left', transform=self.a3.transAxes)
            # -----------------------------------------------------------------------------------[]
            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if batch_ST > self.win_Xmax:
                self.a1.set_xlim(batch_ST - self.win_Xmax, batch_ST)
                self.a2.set_xlim(batch_ST - self.win_Xmax, batch_ST)
                ST.pop(0)
            else:
                self.a1.set_xlim(0, self.win_Xmax)
                self.a2.set_xlim(0, self.win_Xmax)
            self.canvas.draw_idle()

        else:
            print('[ST] standby mode, no active session...')
            self.a2.text(0.440, 0.520, '--------- No Data Feed ---------', fontsize=12, ha='left',
                         transform=self.a2.transAxes)
            self.a1.text(0.440, 0.520, '--------- No Data Feed ---------', fontsize=12, ha='left',
                         transform=self.a1.transAxes)

        timef = time.time()
        lapsedT = timef - timei
        print(f"\n[ST] Process Interval: {lapsedT} sec\n")
        # -----Canvas update --------------------------------------------[]


# ---------------------------------------------------------------------------------------------[Tape Gap Tab]
class tapeGapPolTabb(ttk.Frame):

    """ Application to convert feet to meters or vice versa. """

    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.running = True
        self.runVMP = False
        self.gapPercent = True
        self.toggle_state = True

        # prevents user possible double loading -----
        if not self.running:
            self.running = True
            threading.Thread(target=self.createProcessTG, daemon=True).start()
            print('[TG] is now running....')


        self.swtchVMP = ttk.Button(self, text="Void by Volume (x̄)", command=self.toggle)
        self.swtchVMP.place(x=1880, y=1)
    # ----------------------------------------------------------------------------------------

    def toggle(self):
        if self.toggle_state:
            self.gapPercent = False
            self.swtchVMP.config(text="Void Percentage (%)")
        else:
            self.gapPercent = True
            self.swtchVMP.config(text="Void by Volume (x̄)")
        self.toggle_state = not self.toggle_state

    # ------------------------ Ramp Profiling Static Data Call/Stop Call ------------------[]
    def do_VMP_viz(self):
        if not self.runVMP:
            self.runVMP = True
            print('[VMP] Visualisation started...')
            # reload class method for Ramp plot
            threading.Thread(target=self.dataControlVMP, daemon=True).start()
            self.voidVizCall()

    def clear_VMP_viz(self):
        self.runVMP = False
        self.voidVizClose()

    def voidVizCall(self):
        messagebox.showinfo("VoidMap:", "Void Profile successfully loaded!")

    def voidVizClose(self):
        messagebox.showinfo("VoidMap:", "Void Profile successfully closed!")

    # -------------------------------------------------------------------------[ Pan/Zoom ]
    def pan_factory(self, ax):
        def on_press(event):
            if event.inaxes != ax:
                return
            ax._pan_start = event.x, event.y, ax.get_xlim(), ax.get_ylim()

        def on_release(event):
            ax._pan_start = None
            ax.figure.canvas.draw()

        def on_motion(event):
            if ax._pan_start is None or event.inaxes != ax:
                return

            x_press, y_press, xlim_start, ylim_start = ax._pan_start
            dx = event.x - x_press
            dy = event.y - y_press

            # Transform the mouse movement into data coordinates
            scale_x = (xlim_start[1] - xlim_start[0]) / ax.bbox.width
            scale_y = (ylim_start[1] - ylim_start[0]) / ax.bbox.height

            dx_data = dx * scale_x
            dy_data = dy * scale_y

            ax.set_xlim(xlim_start[0] - dx_data, xlim_start[1] - dx_data)
            ax.set_ylim(ylim_start[0] - dy_data, ylim_start[1] - dy_data)
            ax.figure.canvas.draw_idle()

        ax.figure.canvas.mpl_connect('button_press_event', on_press)
        ax.figure.canvas.mpl_connect('button_release_event', on_release)
        ax.figure.canvas.mpl_connect('motion_notify_event', on_motion)
        ax._pan_start = None

    # -------------------------- Ramp Profiling Static Data Call --------------------------[]

    def createProcessTG(self):
        """Create the widgets for the GUI"""
        global tgUCL, tgLCL, tgMean, tgDev, sUCLtg, sLCLtg, tgUSL, tgLSL

        # Load Quality Historical Values -----------[]
        if pRecipe == 'DNV':
            import qParamsHL_DNV as qp
        else:
            import qParamsHL_MGM as qp
        # Load metrics from config -----------------------------------[Tape Gap]
        self.tgS, self.tgTy, self.olS, self.opS, self.DNV, self.AUTO, self.MGM, self.tgP1, dud2, dud3, dud4, dud5 = qp.decryptpProcessLim(pWON, 'TG')
        if self.tgS == 0 or self.tgTy == 0:
            self.tgS, self.tgTy, self.olS, self.opS = 600, 1, 50, 20

        # Break down each element to useful list ---------------------[Tape Gap]

        if self.DNV and self.tgP1:
            tgPerf = '$Pp_{k' + str(self.tgS) + '}$'    # Estimated or historical Mean
            tglabel = 'Pp'
            # -------------------------------
            tgOne = self.tgP1.split(',')                # split into list elements
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
            tgUCL = 8
            tgLCL = 2
            tgMean = 5
            tgDev = 5
            sUCLtg = 8
            sLCLtg = 2
            tgUSL = 9
            tgLSL = 1
            tgPerf = '$Cp_{k' + str(self.tgS) + '}$'                   # Using Automatic group Mean
            tglabel = 'Cp'

        # -------------------------------------------[End of Tape Gap]

        label = ttk.Label(self, text='[' + str(pMode) + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)     # 10 | 5

        # -------------------------Button #
        ramp_report = ttk.Button(self, text="View Gap Profile", command=self.do_VMP_viz)
        ramp_report.place(x=1600, y=1)  # 1970
        # ------
        ramp_clear = ttk.Button(self, text="Stop Gap View", command=self.clear_VMP_viz)
        ramp_clear.place(x=1740, y=1)

        # Define Axes ---------------------#
        self.f = Figure(figsize=(pMtX, 8), dpi=100)                           # 25, 27 = 12 | 8
        self.f.subplots_adjust(left=0.021, bottom=0.06, right=0.99, top=0.967, wspace=0.302, hspace=0.179)
        # ---------------------------------[]
        self.a1 = self.f.add_subplot(2, 6, (1, 3))                            # xbar plot
        self.a3 = self.f.add_subplot(2, 6, (7, 9))                            # s bar plot
        self.a4 = self.f.add_subplot(2, 6, (4, 12))                           # void mapping profile

        # ----------------------------------------------------------[H]
        plt.rcParams.update({'font.size': 9})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minTG, YScale_maxTG = tgLSL - 8.5, tgUSL + 8.5       # Tape Gap
        self.sBar_minTG, self.sBar_maxTG = 0, 10                    # Calibrate Y-axis for S-Plot
        self.win_Xmin, self.win_Xmax = 0, 3700                      # windows view = visible data points

        # ----------------------------------------------------------#
        YScale_minVM, YScale_maxVM = 0, pExLayer                    # Valid Void Mapping
        self.win_XminVM, self.win_XmaxVM = 0, pLength               # Get details from SCADA PIpe Recipe TODO[1]

        # Real-Time Parameter according to updated requirements ----# 07/Feb/2025
        if UseSQL_DBS:
            self.T1 = 'TG_' + str(pWON)  # Tape Gap
        else:
            self.T1 = SPC_TG
        self.T2 = 'VM_' + str(pWON)  # Void Mapping - Must be loaded from SQL repository
        # ----------------------------------------------------------#

        # Initialise runtime limits --------------------------------#
        self.a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        self.a3.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")

        self.a1.set_title('Tape Gap Polarisation [XBar]', fontsize=12, fontweight='bold')
        self.a3.set_title('Tape Gap Polarisation [SDev]', fontsize=12, fontweight='bold')
        self.a4.set_title('Tape Gap Mapping Profile', fontsize=12, fontweight='bold')

        self.a4.set_ylabel("2D - Staked Layer Void Mapping")
        self.a4.set_xlabel("Sample Distance (mt)")
        self.a4.set_facecolor("green")                           # set face color for Ramp mapping volume
        zoom_factory(self.a4)                                    # allow zooming on image plot
        self.pan_factory(self.a4)                                # allow panning 30/09/2025- RL

        self.a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        self.a3.grid(color="0.5", linestyle='-', linewidth=0.5)
        self.a4.grid(color="y", linestyle='-', linewidth=0.2)

        self.a1.legend(['Tape Gap Polarisation'], loc='upper right', fontsize='x-large')
        self.a3.legend(['Sigma Curve'], loc='upper right', fontsize='x-large')
        self.a4.legend(['Void Map Profile'], loc='upper right', fontsize='x-large')
        # ------------------------------------------------------[for Ramp Plot]

        # Initialise runtime limits -------------------------------#
        self.a1.xaxis.set_major_locator(MultipleLocator(600))   # put grid every 600 (on full range)
        self.a1.set_ylim([YScale_minTG, YScale_maxTG], auto=True)
        self.a1.set_xlim([self.win_Xmin, self.win_Xmax])
        # ----------------------------------------------------------#
        self.a3.xaxis.set_major_locator(MultipleLocator(600))
        self.a3.set_ylim([self.sBar_minTG, self.sBar_maxTG], auto=True)
        self.a3.set_xlim([self.win_Xmin, self.win_Xmax])
        # --------------------------------------------------------[]
        self.a4.set_ylim([YScale_minVM, YScale_maxVM], auto=True)
        self.a4.set_xlim([self.win_XminVM, self.win_XmaxVM])

        # ----------------------------------------------------------[]
        # Define Plot area and axes -
        # ----------------------------------------------------------[8 into 4]
        self.im10, = self.a1.plot([], [], 'o-', label='Tape Gap Pol - (A1)')
        self.im11, = self.a1.plot([], [], 'o-', label='Tape Gap Pol - (B1)')
        self.im12, = self.a1.plot([], [], 'o-', label='Tape Gap Pol - (A2)')
        self.im13, = self.a1.plot([], [], 'o-', label='Tape Gap Pol - (B2)')
        # ------------ S Bar Plot ------------------------------
        self.im14, = self.a3.plot([], [], '--', label='Tape Gap Pol')
        self.im15, = self.a3.plot([], [], '--', label='Tape Gap Pol')
        self.im16, = self.a3.plot([], [], '--', label='Tape Gap Pol')
        self.im17, = self.a3.plot([], [], '--', label='Tape Gap Pol')

        # ----------------------------------------------------------[8 into 4]
        self.im18, = self.a1.plot([], [], 'o-', label='Tape Gap Pol - (A3)')
        self.im19, = self.a1.plot([], [], 'o-', label='Tape Gap Pol - (B3)')
        self.im20, = self.a1.plot([], [], 'o-', label='Tape Gap Pol - (A4)')
        self.im21, = self.a1.plot([], [], 'o-', label='Tape Gap Pol - (B4)')
        # ------------ S Bar Plot ------------------------------
        self.im22, = self.a3.plot([], [], '--', label='Tape Gap Pol')
        self.im23, = self.a3.plot([], [], '--', label='Tape Gap Pol')
        self.im24, = self.a3.plot([], [], '--', label='Tape Gap Pol')
        self.im25, = self.a3.plot([], [], '--', label='Tape Gap Pol')
        # --------------------------------------------------------------------#
        self.im26 = self.a4.scatter([], [], [], c=[], cmap='rainbow', marker='|') # viridis, cool, hsv, magma
        # Attach colorbar to scatter ------------
        cbar = self.f.colorbar(self.im26, ax=self.a4)
        if self.gapPercent:
            cbar.set_label("Percentage Void")
        else:
            cbar.set_label("AvgGap value")
        # self.canvas = FigureCanvasTkAgg(self.f, master=root) ----------#
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        self.canvas._tkcanvas.pack(expand=True)

        # --------- call data block -------------------------------------#
        pTG = threading.Thread(target=self.dataControlTG, daemon=True) # .start()
        pTG.start()
        # ---------------- EXECUTE SYNCHRONOUS TG METHOD --------------------------#


    def dataControlTG(self):
        global batch_TG

        batch_TG = 1
        s_fetch, stp_Sz, s_regm = 600, 1, 10  # @ 6m/min & 10Hz res,
        # Evaluate conditions for SQL Data Fetch ------------------------------[A]

        # Obtain Volatile Data from PLC/SQL Host Server -------[]
        if UseSQL_DBS:
            if self.running:
                import sqlArrayRLmethodTG as pdC
                tg_con = sq.sql_connectTG()
            else:
                print('[TG] Data Source selection is Unknown')
                tg_con = None

        elif UsePLC_DBS:
            if self.running:
                import plcArrayRLmethodTG as pdD
                print('\n[TG] Activating watchdog...')  # primary connection to watch dog
            else:
                # Dtt_ready = True
                print('[TG] Data Source selection is Unknown')
        else:
            print('[TG] Data Source selection is Unknown')

        # Initialise RT variables ---[]
        paused = False

        while True:
            # ------------------------------#
            if UsePLC_DBS or UseSQL_DBS and self.running:
                print('\n[TG] Synchronous controller activated...')

                if uCalling == 1:
                    sysRun, sysIdl, sysRdy, msc_rt, cLayer, piPos, mstatus = wd.autoPausePlay()

                    if not sysRun and not paused or msc_rt == 49296:
                        print('[TG] is requesting for SMC status...')
                        paused = True

                        while paused:
                            time.sleep(5)
                            print("\n[TG Viz] Visualization in Paused Mode...")
                            sysRun, msctcp, msc_rt, cLayr = wd.rt_autoPausePlay()
                            if sysRun:
                                paused = False
                                print('[TG] Visualisation Resumes...')
                            time.sleep(0.2)

                    else:
                        print("[TG] Visualization in Real-time Mode...")
                        # -----------------------------------------------------------------[]
                        self.stDta = pdD.plcExec(self.T1, s_fetch, stp_Sz, s_regm)
                        time.sleep(60)
                    self.canvas.get_tk_widget().after(0, self.tgDataPlot)
                    batch_TG += 1

                elif uCalling == 2 or uCalling == 3 and tg_con:
                    if keyboard.is_pressed("Alt+Q"):
                        paused = True

                        while paused:
                            time.sleep(5)
                            print("\n[TG Viz] Visualization in Paused Mode...")
                            sysRun, msctcp, msc_rt, cLayr = wd.rt_autoPausePlay()
                            if sysRun:
                                paused = False
                                print('[TG] Visualisation Resumes...')
                    else:
                        self.gD1 = pdC.sqlExec(tg_con, s_fetch, stp_Sz, self.T1, batch_TG)
                        time.sleep(60)
                        # Treat EOF as event ---------------------
                        if keyboard.is_pressed("Alt+Q") or not self.gD1:  # Terminate file-fetch
                            tg_con.close()
                            print('SQL End of File, [TG] connection closes after 60 sec...')
                            time.sleep(60)
                            continue
                        else:
                            print('\n[TG] Updating....')
                    if tg_con:
                        self.canvas.get_tk_widget().after(0, self.tgDataPlot)
                        batch_TG += 1
                    else:
                        print('[TG] sorry, instance not granted, trying again..')
                        tg_con = sq.check_SQL_Status(5, 10)
            else:
                print('[TG] is active but no visualisation!\n')
            print('[TG] protocol is refreshed, the wait is over...')

    # ------------------------------------------------------------------
    def dataControlVMP(self):
        global batch_VMP, sysRun, sysIdl, sysRdy, msc_rt, cLayer, piPos, mstatus

        batch_VMP = 1
        s_fetch, stp_Sz = 10, 1
        # Evaluate conditions for SQL Data Fetch ------------------------------[A]

        # Obtain Volatile Data from PLC/SQL Host Server -------[]
        if UseSQL_DBS and self.running:
            import sqlArrayRLmethodVM as vmp
            vmp_con = sq.sql_connectVMP()
        else:
            vmp_con = None

        # Initialise RT variables ---[]
        paused = False

        # ----------------------------------------------#
        while True:
            if UseSQL_DBS and vmp_con:
                print('\n[VMP] PostProd Mode controller activated...')

                if uCalling == 1 and not sysRun:
                    sysRun, sysIdl, sysRdy, msc_rt, cLayer, piPos, mstatus = wd.autoPausePlay()

                    if not sysRun and not paused:
                        print('\n[VMP] Live is pausing...')
                        paused = True

                        while paused:
                            time.sleep(5)
                            print("\n[VMP Viz] Visualization in Paused Mode...")
                            sysRun, msctcp, msc_rt, cLayr = wd.rt_autoPausePlay()
                            if sysRun:
                                paused = False
                                print('[VMP] Visualisation Resumes...')
                            time.sleep(0.2)
                    else:
                        # USe SQL repository for VMP stream ------[]
                        self.vmD3 = vmp.sqlExec(vmp_con, s_fetch, stp_Sz, self.T2, batch_VMP)
                        time.sleep(10)

                elif uCalling == 2 or uCalling == 3:
                    if keyboard.is_pressed("Alt+Q"):
                        paused = True

                        while paused:
                            time.sleep(5)
                            print("\n[VMP Viz] Visualization in Paused Mode...")
                            if keyboard.is_pressed("esc"):
                                paused = False
                                print('[VMP] Visualisation Resumes...')
                            time.sleep(0.2)
                    else:
                        # USe SQL repository for VMP stream ------[]
                        self.vmD3 = vmp.sqlExec(vmp_con, s_fetch, stp_Sz, self.T2, batch_VMP)
                        time.sleep(10)
                        print("[VMP] Visualization in Live Mode...")
                        # ------ Inhibit iteration ----------------------------------------[]
                        if not self.vmD3:           # No new data coming through
                            print('SQL End of File, [VMP] connection closes after 30 min...')
                            time.sleep(60)
                            vmp_con.close()       # close connection
                            continue
                        else:
                            print('\n[VMP] Updating....')
                # ------------------------------------------------------------
                if vmp_con:
                    self.canvas.get_tk_widget().after(0, self.vmDataPlot)
                    batch_VMP += 1
                else:
                    print('[VMP] sorry, instance not granted, trying again..')
                    vmp_con = sq.check_SQL_Status(5, 60)
            else:
                print('\n[VMP] is active but no visualisation!')
            print('[VM] protocol is being refreshed...')

    # ================== End of synchronous Method ==========================--------------------[]
    def tgDataPlot(self):
        timei = time.time()                                   # start timing the entire loop

        # Bi-stream Data Pooling Method ----------------------#
        if UsePLC_DBS and self.running:
            import VarPLC_TG as tg
            stream = 1
            dcA = qtg.validCols(self.T1)                     # Load defined valid columns for PLC Data
            df1 = pd.DataFrame(self.gD1, columns=dcA)        # Include table data into python Dataframe
            # -----------------------------------------------#
            # Do some data cleansing & interpolation if Nans occurs
            data1 = df1.select_dtypes(include=["number"])
            df1_interp = data1.interpolate(method="linear", axis=0).ffill().bfill()  # column-wise
            # Convert pandas -> cuDF
            if GPU_ENABLED:
                gpu_df1 = cudf.from_pandas(df1_interp.select_dtypes(include="number"))
                TG = tg.loadProcesValues(gpu_df1)
            else:
                TG = tg.loadProcesValues(df1_interp)            # Join data values under dataframe

            # ----------------------------------------------#
            # print('\nDataFrame Content', df1.head(10))        # Preview Data frame head

        elif UseSQL_DBS and self.running:
            import VarSQL_TG as tg                          # load SQL variables column names | rfVarSQL
            g1 = qtg.validCols(self.T1)                     # Construct Data Column selSqlColumnsTFM.py
            df1 = pd.DataFrame(self.gD1, columns=g1)        # Import into python Dataframe
            # ----------------------------------------------#
            data1 = df1.select_dtypes(include=["number"])
            df1_interp = data1.interpolate(method="linear", axis=0).ffill().bfill()
            if GPU_ENABLED:
                gpu_df1 = cudf.from_pandas(df1_interp.select_dtypes(include="number"))
                TG = tg.loadProcesValues(gpu_df1)
            else:
                TG = tg.loadProcesValues(df1_interp)        # Join data values under dataframe
            # ----------------------------------------------#
            # print('\nDataFrame Content', df1.head(10))
            # print("Memory Usage:", df1.info(verbose=False))  # Check memory utilization
            # --------------------------------------#
        else:
            TG = 0
            print('[TG] Unknown Protocol...')

        # ------------------------------------------#
        if self.running:
            self.a1.legend(loc='upper right', title='Tape Gap')
            self.a3.legend(loc='upper right', title='Sigma curve')
            # Plot X-Axis data points -------- X Plot
            self.im10.set_xdata(np.arange(batch_TG))
            self.im11.set_xdata(np.arange(batch_TG))
            self.im12.set_xdata(np.arange(batch_TG))
            self.im13.set_xdata(np.arange(batch_TG))
            self.im14.set_xdata(np.arange(batch_TG))
            self.im15.set_xdata(np.arange(batch_TG))
            self.im16.set_xdata(np.arange(batch_TG))
            self.im17.set_xdata(np.arange(batch_TG))
            # ------------------------------- S Plot
            self.im18.set_xdata(np.arange(batch_TG))
            self.im19.set_xdata(np.arange(batch_TG))
            self.im20.set_xdata(np.arange(batch_TG))
            self.im21.set_xdata(np.arange(batch_TG))
            self.im22.set_xdata(np.arange(batch_TG))
            self.im23.set_xdata(np.arange(batch_TG))
            self.im24.set_xdata(np.arange(batch_TG))
            self.im25.set_xdata(np.arange(batch_TG))

            # X Plot Y-Axis data points for XBar -------------------------------------------[# Channels]
            self.im10.set_ydata((TG[6]).rolling(window=self.tgS).mean()[0:batch_TG])  # Segment 1
            self.im11.set_ydata((TG[7]).rolling(window=self.tgS).mean()[0:batch_TG])  # Segment 2
            self.im12.set_ydata((TG[8]).rolling(window=self.tgS).mean()[0:batch_TG])  # Segment 3
            self.im13.set_ydata((TG[9]).rolling(window=self.tgS).mean()[0:batch_TG])  # Segment 4
            # ------ Evaluate Pp for Segments ---------#
            # S Plot Y-Axis data points for StdDev ----------------------------------------[# S Bar Plot]
            self.im14.set_ydata((TG[6]).rolling(window=self.tgS).std()[0:batch_TG])
            self.im15.set_ydata((TG[7]).rolling(window=self.tgS).std()[0:batch_TG])
            self.im16.set_ydata((TG[8]).rolling(window=self.tgS).std()[0:batch_TG])
            self.im17.set_ydata((TG[9]).rolling(window=self.tgS).std()[0:batch_TG])

            # ---------------------------------------#
            self.im18.set_ydata((TG[10]).rolling(window=self.tgS).mean()[0:batch_TG])   # Segment 1
            self.im19.set_ydata((TG[11]).rolling(window=self.tgS).mean()[0:batch_TG])  # Segment 2
            self.im20.set_ydata((TG[12]).rolling(window=self.tgS).mean()[0:batch_TG])  # Segment 3
            self.im21.set_ydata((TG[13]).rolling(window=self.tgS).mean()[0:batch_TG])  # Segment 4
            # ------ Evaluate Pp for Ring 2 ---------#
            self.im22.set_ydata((TG[10]).rolling(window=self.tgS).std()[0:batch_TG])
            self.im23.set_ydata((TG[11]).rolling(window=self.tgS).std()[0:batch_TG])
            self.im24.set_ydata((TG[12]).rolling(window=self.tgS).std()[0:batch_TG])
            self.im25.set_ydata((TG[13]).rolling(window=self.tgS).std()[0:batch_TG])

            # # ---- Profile rolling Data Plot ------------------------------------------------------------------------[]
            # # Declare Plots attributes ------------------------------------------------------------[]
            # XBar Mean Plot
            self.a1.axhline(y=tgMean, color="red", linestyle="--", linewidth=0.8)
            self.a1.axhspan(tgLCL, tgUCL, facecolor='#F9C0FD', edgecolor='#F9C0FD')            # 3 Sigma span (Purple)
            self.a1.axhspan(tgUCL, tgUSL, facecolor='#8d8794', edgecolor='#8d8794')            # grey area
            self.a1.axhspan(tgLSL, tgLCL, facecolor='#8d8794', edgecolor='#8d8794')
            # ---------------------- sBar_minTG, sBar_maxTG -------[]
            # Define Legend's Attributes  ----
            self.a3.axhline(y=tgDev, color="blue", linestyle="--", linewidth=0.8)
            self.a3.axhspan(sLCLtg, sUCLtg, facecolor='#F9C0FD', edgecolor='#F9C0FD')          # 1 Sigma Span
            self.a3.axhspan(sLCLtg, self.sBar_maxTG, facecolor='#CCCCFF', edgecolor='#CCCCFF')     # 1 Sigma above the Mean
            self.a3.axhspan(self.sBar_minTG, sLCLtg, facecolor='#CCCCFF', edgecolor='#CCCCFF')

            # Setting up the parameters for moving windows Axes ---------------------------------[]
            if batch_TG > self.win_Xmax:
                self.a1.set_xlim(batch_TG - self.win_Xmax, batch_TG)
                self.a3.set_xlim(batch_TG - self.win_Xmax, batch_TG)
                TG.pop(0)
            else:
                self.a1.set_xlim(0, self.win_Xmax)
                self.a3.set_xlim(0, self.win_Xmax)
            print('[TG] Data Stream Buffer Size 2:', len(TG))
            self.canvas.draw_idle()

        else:
            print('[TG] in standby mode, no active session...')
            self.a3.text(0.400, 0.520, '--------- No Data Feed ---------', fontsize=12, ha='left',
                         transform=self.a3.transAxes)
            self.a1.text(0.400, 0.520, '--------- No Data Feed ---------', fontsize=12, ha='left',
                         transform=self.a1.transAxes)

        timef = time.time()
        lapsedT = timef - timei
        print(f"\n[TG] Process Interval: {lapsedT} sec\n")
    # -----Canvas update --------------------------------------------[]


    def vmDataPlot(self):
        timei = time.time()  # start timing the entire loop

        # Call data loader Method-----------------------#
        if UseSQL_DBS and self.runVMP:
            import VarSQL_VM as vm
            g3 = qvm.validCols(self.T2)
            d3 = pd.DataFrame(self.vmD3, columns=g3)
            # ---------------------------------
            VM = vm.loadProcesValues(d3)
            # ---------------------------------
            print('\nSQL Content RM:', d3.tail(300))
            # print("Memory Usage:", d3.info(verbose=False))  # Check memory utilization
            # --------------------------------------#
        else:
            VM = 0
            print('[VMP] Unknown Protocol...')

        # ------------------------------------------#
        if UseSQL_DBS and self.running:  # accessible through sql only!
            self.a4.legend(['Void Mapping Profile'], loc='upper right', fontsize="x-large")
            pScount = VM[1]                         # Sample count
            pCenter = np.array(VM[2] * 0.001)       # Sample centre -- X axis convert to mt
            pAvgGap = np.array(VM[3])               # Average Gap
            pMaxGap = VM[4]                         # Max Gap
            vLayerN = np.array(VM[5])               # current Layer  - y axis
            sLength = VM[6]                         # Sample length
            gap_vol = (pAvgGap / sLength) * 100     # Percentage Void
            # ---------------------------------------------------------------------[VOID]
            coords = np.column_stack((pCenter, vLayerN))  # shape (N, 2)
            self.im26.set_offsets(coords)
            # --------------------------------------------------------------#
            if self.gapPercent:
                self.im26.set_array(gap_vol[0:batch_VMP])  #
                self.im26.set_clim(vmin=gap_vol.min(), vmax=gap_vol.max())
            else:
                self.im26.set_array(pAvgGap[0:batch_VMP]) #
                self.im26.set_clim(vmin=pAvgGap.min(), vmax=pAvgGap.max())

            # Setting up VMP parameters for static zoomable windows Axes ------------------------[]
            if batch_VMP > self.win_Xmax:
                pCenter.pop(0)
            self.canvas.draw_idle()

        else:
            print('[VMP] standby mode, no active session...')
            self.a3.text(0.400, 0.520, '--------- No Data Feed ---------', fontsize=12, ha='left',
                         transform=self.a3.transAxes)

        timef = time.time()
        lapsedT = timef - timei
        print(f"[VMP] Process Interval: {lapsedT} sec\n")

    # End of second stream


# -------------------------------------------------------------------------------------------[Tape Placement]
class tapePlacementTabb(ttk.Frame):     # -- Defines the tabbed region for QA param - Substrate Temperature --[]
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.running = True
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        global tpS, tpTy, eolS, eopS

        # --------------------------------------------------------------------[]
        if pRecipe == 'DNV':
            import qParamsHL_DNV as qp
        else:
            import qParamsHL_MGM as qp
        # Load metrics from config -----------------------------------[Tape Gap]
        tpS, tpTy, eolS, eopS, tpHL, tpAL, tptFO, tpP1, dud2, dud3, dud4, dud5 = qp.decryptpProcessLim(pWON, 'TP')

        # Break down each element to useful list ----------------[Tape Placement]

        if tpHL and tpP1:
            tpPerf = '$Pp_{k' + str(tpS) + '}$'  # Estimated or historical Mean
            tplabel = 'Pp'
            # -------------------------------
            tpOne = tpP1.split(',')  # split into list elements
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
            tpPerf = '$Cp_{k' + str(tpS) + '}$'  # Using Automatic group Mean
            tplabel = 'Cp'

        # ------------------------------------[End of Winding Speed Abstraction]

        label = ttk.Label(self, text='[' + str(pMode) + ' Mode]', font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Set subplot embedded properties ----------------------------------[]
        self.f = Figure(figsize=(pMtX, 8), dpi=100)      # 25, 27
        self.f.subplots_adjust(left=0.029, bottom=0.05, right=0.983, top=0.955, wspace=0.117, hspace=0.157)
        # ---------------------------------[]
        self.a1 = self.f.add_subplot(2, 4, (1, 3))        # xbar plot
        self.a2 = self.f.add_subplot(2, 4, (5, 7))        # s bar plot
        self.a3 = self.f.add_subplot(2, 4, (4, 8))        # CPk/PPk Feed

        # Declare Plots attributes ---------------------------------[]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minTP, YScale_maxTP = tpLSL - 8.5, tpUSL + 8.5       # Roller Force
        sBar_minTP, sBar_maxTP = sLCLtp - 80, sUCLtp + 80           # Calibrate Y-axis for S-Plot
        self.win_Xmin, self.win_Xmax = 0, (int(tpS) + 3)             # windows view = visible data points

        # ----------------------------------------------------------#
        # Real-Time Parameter according to updated requirements ----# 07/Feb/2025
        if pRecipe == 1:
            T1 = SPC_TP
        else:
            T1 = 'TP1_' + pWON  # Tape Placement
            T2 = 'TP2_' + pWON
        # ----------------------------------------------------------#

        # Initialise runtime limits
        self.a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        self.a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        self.a1.set_title('Tape Placement [XBar]', fontsize=12, fontweight='bold')
        self.a2.set_title('Tape Placement [StDev]', fontsize=12, fontweight='bold')

        self.a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        self.a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        self.a1.legend(loc='upper right', title='Tape Placement')
        self.a2.legend(loc='upper right', title='Sigma curve')

        # Initialise runtime limits -------------------------------#
        self.a1.set_ylim([YScale_minTP, YScale_maxTP], auto=True)
        self.a1.set_xlim([self.win_Xmin, self.win_Xmax])
        # ----------------------------------------------------------#
        self.a3.set_ylim([sBar_minTP, sBar_maxTP], auto=True)
        self.a3.set_xlim([self.win_Xmin, self.win_Xmax])

        # ----------------------------------------------------------[]
        self.a3.cla()
        self.a3.get_yaxis().set_visible(False)
        self.a3.get_xaxis().set_visible(False)

        # ----------------------------------------------------------[]
        # Define Plot area and axes -
        # ----------------------------------------------------------#
        im10, = self.a1.plot([], [], 'o-', label='Tape Placement - (A1)')
        im11, = self.a1.plot([], [], 'o-', label='Tape Placement - (B1)')
        im12, = self.a1.plot([], [], 'o-', label='Tape Placement - (A2)')
        im13, = self.a1.plot([], [], 'o-', label='Tape Placement - (B2)')
        im14, = self.a1.plot([], [], 'o-', label='Tape Placement - (A3)')
        im15, = self.a1.plot([], [], 'o-', label='Tape Placement - (B3)')
        im16, = self.a1.plot([], [], 'o-', label='Tape Placement - (A4)')
        im17, = self.a1.plot([], [], 'o-', label='Tape Placement - (B4)')
        # ------------ S Bar Plot ------------------------------
        im18, = self.a2.plot([], [], 'o-', label='Tape Placement')
        im19, = self.a2.plot([], [], 'o-', label='Tape Placement')
        im20, = self.a2.plot([], [], 'o-', label='Tape Placement')
        im21, = self.a2.plot([], [], 'o-', label='Tape Placement')
        im22, = self.a2.plot([], [], 'o-', label='Tape Placement')
        im23, = self.a2.plot([], [], 'o-', label='Tape Placement')
        im24, = self.a2.plot([], [], 'o-', label='Tape Placement')
        im25, = self.a2.plot([], [], 'o-', label='Tape Placement')

        # Statistical Feed -----------------------------------------[]
        self.a3.text(0.466, 0.945, 'Performance Feed - WP', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=self.a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        self.a3.add_patch(rect1)
        self.a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)---------------------
        self.a3.text(0.145, 0.804, tplabel, fontsize=12, fontweight='bold', ha='center', transform=self.a3.transAxes)
        self.a3.text(0.328, 0.658, '#Pp Value', fontsize=28, fontweight='bold', ha='center', transform=self.a3.transAxes)
        self.a3.text(0.650, 0.820, 'Ring ' + tplabel + ' Data', fontsize=14, ha='left', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=self.a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        self.a3.text(0.145, 0.403, tpPerf, fontsize=12, fontweight='bold', ha='center', transform=self.a3.transAxes)
        self.a3.text(0.328, 0.282, '#Ppk Value', fontsize=28, fontweight='bold', ha='center', transform=self.a3.transAxes)
        self.a3.text(0.640, 0.420, 'Ring ' + tpPerf + ' Data', fontsize=14, ha='left', transform=self.a3.transAxes)
        # -------------------------------------
        self.a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=self.a3.transAxes)
        self.a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=self.a3.transAxes)
        # ----- Pipe Position and SMC Status -----
        self.a3.text(0.080, 0.090, 'Pipe Position: ' + str(piPos) + '    Processing Layer #' + str(cLayerN), fontsize=12, ha='left',
                transform=self.a3.transAxes)
        self.a3.text(0.080, 0.036, 'SMC Status: ' + msc_rt, fontsize=12, ha='left', transform=self.a3.transAxes)

        # self.canvas = FigureCanvasTkAgg(self.f, master=root) ----------#
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        self.canvas._tkcanvas.pack(expand=True)

        # --------- call data block -------------------------------------#
        threading.Thread(target=self.dataControlTP, daemon=True).start()
        # ---------------- EXECUTE SYNCHRONOUS METHOD -------------------#


    def dataControlTP(self):
        s_fetch, stp_Sz, s_regm = 300, 1, 10  # 10 sec per meter length

        # Obtain Volatile Data from PLC Host Server ---------------------------[]
        if UseSQL_DBS and self.running:
            tp_con = sq.DAQ_connect(1, 0)
        else:
            pass

        # Evaluate conditions for SQL Data Fetch ------------------------------[A]
        """
        Load watchdog function with synchronous function every seconds
        """
        # Initialise RT variables ---[]
        autoSpcRun = True
        autoSpcPause = False
        import keyboard  # for temporary use

        # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
        # sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
        # Define PLC/SMC error state -------------------------------------------#
        if UsePLC_DBS:
            import plcArrayRLmethodTP as stp
        elif UseSQL_DBS:
            import sqlArrayRLmethodTP as stp

        while True:
            # print('Indefinite looping...')
            if UsePLC_DBS:                                          # Not Using PLC Data
                sysRun, msctcp, msc_rt, cLayr = wd.autoPausePlay()
                if sysRun:
                    inProgress = True                               # True for RetroPlay mode
                else:
                    inProgress = False
                print('\nAsynchronous controller activated...')

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
                    self.tpDta = stp.plcExec(T1, s_fetch, stp_Sz, s_regm)
                    self.tpDtb = 0

            elif UseSQL_DBS:
                inProgress = False  # False for Real-time mode
                print('\nSynchronous controller activated...')

                # Either of the 2 combo variables are assigned to trigger routine pause
                if keyboard.is_pressed("Alt+Q") and not inProgress:
                    print('\nProduction is pausing...')
                    if not autoSpcPause:
                        autoSpcRun = not autoSpcRun
                        autoSpcPause = True
                        # play(error)                                               # Pause mode with audible Alert
                        print("\nVisualization in Paused Mode...")
                    else:
                        autoSpcPause = False
                    print("Visualization in Real-time Mode...")

                else:
                    self.tpDta, self.tpDtb = stp.sqlExec(tp_con, s_fetch, stp_Sz, s_regm, T1, T2)
                    print("Visualization in Play Mode...")
                print('\nUpdating....')
                # ------ Inhibit iteration ----------------------------------------------------------[]
                """
                # Set condition for halting real-time plots in watchdog class -----------------------[]
                """
                # TODO --- values for inhibiting the SQL processing
                if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                    tp_con.close()
                    print('SQL End of File, connection closes after 30 mins...')
                    time.sleep(60)
                    continue
                else:
                    print('\nUpdating....')
            else:
                pass
            self.canvas.get_tk_widget().after(s_regm, self._tpDataPlot)  # Regime = every 10nseconds
            time.sleep(0.5)


    # ================== End of synchronous Method ==========================
    def _tpDataPlot(self):
        timei = time.time()                                 # start timing the entire loop

        # Call data loader Method---------------------------#

        if UsePLC_DBS == 1:
            import VarPLCtp as tp
            # Call synchronous data function ---------------[]
            columns = qtp.validCols(T1)                         # Load defined valid columns for PLC Data
            df1 = pd.DataFrame(self.tpDta, columns=columns)     # Include table data into python Dataframe
            TP = tp.loadProcesValues(df1)                       # Join data values under dataframe
            print('\nSQL Content', df1.head(10))
            print("Memory Usage:", df1.info(verbose=False))     # Check memory utilization

        elif UseSQL_DBS:
            import VarSQLtp as tp                               # load SQL variables column names | rfVarSQL
            g1 = qtp.validCols(T1)                              # Construct Data Column selSqlColumnsTFM.py
            d1 = pd.DataFrame(self.tpDta, columns=g1)           # Import into python Dataframe
            g2 = qla.validCols(T2)
            d2 = pd.DataFrame(self.tpDtb, columns=g2)

            # Concatenate all columns -----------[]
            df1 = pd.concat([d1, d2], axis=1)
            TP = tp.loadProcesValues(df1)                       # Join data values under dataframe
            print('\nSQL Content', df1.head(10))
            print("Memory Usage:", df1.info(verbose=False))    # Check memory utilization
        else:
            print('Unknown Process Protocol...')
        # -------------------------------------------------------------------------------------[]
        if UsePLC_DBS or UseSQL_DBS and self.running:
            im10.set_xdata(np.arange(self.win_Xmax))
            im11.set_xdata(np.arange(self.win_Xmax))
            im12.set_xdata(np.arange(self.win_Xmax))
            im13.set_xdata(np.arange(self.win_Xmax))
            im14.set_xdata(np.arange(self.win_Xmax))
            im15.set_xdata(np.arange(self.win_Xmax))
            im16.set_xdata(np.arange(self.win_Xmax))
            im17.set_xdata(np.arange(self.win_Xmax))
            im18.set_xdata(np.arange(self.win_Xmax))
            im19.set_xdata(np.arange(self.win_Xmax))
            im20.set_xdata(np.arange(self.win_Xmax))
            im21.set_xdata(np.arange(self.win_Xmax))
            im22.set_xdata(np.arange(self.win_Xmax))
            im23.set_xdata(np.arange(self.win_Xmax))
            im24.set_xdata(np.arange(self.win_Xmax))
            im25.set_xdata(np.arange(self.win_Xmax))

            # X Plot Y-Axis data points for XBar -------------------------------------------[# Channels]
            im10.set_ydata((TP[0]).rolling(window=tpS).mean()[0:self.win_Xmax])  # Segment 1
            im11.set_ydata((TP[1]).rolling(window=tpS).mean()[0:self.win_Xmax])  # Segment 2
            im12.set_ydata((TP[2]).rolling(window=tpS).mean()[0:self.win_Xmax])  # Segment 3
            im13.set_ydata((TP[3]).rolling(window=tpS).mean()[0:self.win_Xmax])  # Segment 4
            # ------ Evaluate Pp for Segments ---------#
            mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(tpHL, tpS, 'TP')
            # ---------------------------------------#
            im14.set_ydata((TP[4]).rolling(window=tpS).mean()[0:self.win_Xmax])  # Segment 1
            im15.set_ydata((TP[5]).rolling(window=tpS).mean()[0:self.win_Xmax])  # Segment 2
            im16.set_ydata((TP[6]).rolling(window=tpS).mean()[0:self.win_Xmax])  # Segment 3
            im17.set_ydata((TP[7]).rolling(window=tpS).mean()[0:self.win_Xmax])  # Segment 4
            # ------ Evaluate Pp for Ring 2 ---------#
            mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(tpHL, tpS, 'TP')

            # S Plot Y-Axis data points for StdDev ----------------------------------------[# S Bar Plot]
            im18.set_ydata((TP[0]).rolling(window=tpS).std()[0:self.win_Xmax])
            im19.set_ydata((TP[1]).rolling(window=tpS).std()[0:self.win_Xmax])
            im20.set_ydata((TP[2]).rolling(window=tpS).std()[0:self.win_Xmax])
            im21.set_ydata((TP[3]).rolling(window=tpS).std()[0:self.win_Xmax])

            im22.set_ydata((TP[4]).rolling(window=tpS).std()[0:self.win_Xmax])
            im23.set_ydata((TP[5]).rolling(window=tpS).std()[0:self.win_Xmax])
            im24.set_ydata((TP[6]).rolling(window=tpS).std()[0:self.win_Xmax])
            im25.set_ydata((TP[7]).rolling(window=tpS).std()[0:self.win_Xmax])


            # Compute entire Process Capability -----------#
            if not tpHL:
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLd, dLCLd, ppT, pkT, xline, sline = tq.tAutoPerf(tpS, mnA,
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
            if len(TP) > win_Xmax:
                TP.pop(0)
            self.canvas.draw_idle()

        else:
            print('Tape Placement standby mode, no active session...')
            self.a2.text(0.440, 0.520, '--------- No Data Feed ---------', fontsize=12, ha='left',
                         transform=self.a2.transAxes)
            self.a1.text(0.440, 0.520, '--------- No Data Feed ---------', fontsize=12, ha='left',
                         transform=self.a1.transAxes)

        timef = time.time()
        lapsedT = timef - timei
        print(f"Process Interval TP: {lapsedT} sec\n")
        # -----Canvas update --------------------------------------------[]

# ============================================= CASCADE CLASS METHODS ===============================================#
# This class procedure allows SCADA operator to split the screen into respective runtime process                     #
# ===================================================================================================================#

class cascadeCommonViewsRF(ttk.Frame):          # Load common Cascade and all object in cascadeSwitcher() class
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.createWidgetsRF()

    def createWidgetsRF(self):

        # Load metrics from config -----------------------------------[]
        if pRecipe == 'DNV':
            import qParamsHL_DNV as qp
        else:
            import qParamsHL_MGM as qp
        # ------------------------------------------------------------[]
        rfS, rfTy, rfSoL, rfSoP, rfHL, rfAL, rfFO, rfP1, rfP2, rfP3, rfP4, rfP5 = qp.decryptpProcessLim(pWON, 'RF')
        # Break down each element to useful list -----[Tape Temperature]

        if rfHL and rfP1 and rfP2 and rfP3 and rfP4 and rfP5:  #
            rfPerf = '$Pp_{k' + str(rfS) + '}$'  # Using estimated or historical Mean
            rflabel = 'Pp'
            # -------------------------------------[]
            One = rfP1.split(',')  # split into list elements
            Two = rfP2.split(',')
            Thr = rfP3.split(',')
            For = rfP4.split(',')
            Fiv = rfP5.split(',')
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
            rfPerf = '$Cp_{k' + str(rfS) + '}$'  # Using Automatic group Mean
            rflabel = 'Cp'

        # ------ [End of Historical abstraction -------]
        label = ttk.Label(self, text='[' + str(pMode) + ' Mode - RF]', font=LARGE_FONT)
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
        window_Xmin, window_Xmax = 0, (int(rfS) + 3)                # windows view = visible data points

        # ----------------------------------------------------------#
        # Real-Time Parameter according to updated requirements ----# 28/Feb/2025
        if pRecipe == 1:
            T1 = SPC_RF
        else:
            T1 = 'RF1_' + pWON                                            # Roller Force
            T2 = 'RF2_' + pWON
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
        im10, = self.a1.plot([], [], 'o-', label='Roller Force - (R1H1)')
        im11, = self.a1.plot([], [], 'o-', label='Roller Force - (R1H2)')
        im12, = self.a1.plot([], [], 'o-', label='Roller Force - (R1H3)')
        im13, = self.a1.plot([], [], 'o-', label='Roller Force - (R1H4)')
        im14, = self.a2.plot([], [], 'o-', label='Roller Force')
        im15, = self.a2.plot([], [], 'o-', label='Roller Force')
        im16, = self.a2.plot([], [], 'o-', label='Roller Force')
        im17, = self.a2.plot([], [], 'o-', label='Roller Force')

        im18, = self.a1.plot([], [], 'o-', label='Roller Force - (R2H1)')
        im19, = self.a1.plot([], [], 'o-', label='Roller Force - (R2H2)')
        im20, = self.a1.plot([], [], 'o-', label='Roller Force - (R2H3)')
        im21, = self.a1.plot([], [], 'o-', label='Roller Force - (R2H4)')
        im22, = self.a2.plot([], [], 'o-', label='Roller Force')
        im23, = self.a2.plot([], [], 'o-', label='Roller Force')
        im24, = self.a2.plot([], [], 'o-', label='Roller Force')
        im25, = self.a2.plot([], [], 'o-', label='Roller Force')

        im26, = self.a1.plot([], [], 'o-', label='Roller Force - (R3H1)')
        im27, = self.a1.plot([], [], 'o-', label='Roller Force - (R3H2)')
        im28, = self.a1.plot([], [], 'o-', label='Roller Force - (R3H3)')
        im29, = self.a1.plot([], [], 'o-', label='Roller Force - (R3H4)')
        im30, = self.a2.plot([], [], 'o-', label='Roller Force')
        im31, = self.a2.plot([], [], 'o-', label='Roller Force')
        im32, = self.a2.plot([], [], 'o-', label='Roller Force')
        im33, = self.a2.plot([], [], 'o-', label='Roller Force')

        im34, = self.a1.plot([], [], 'o-', label='Roller Force - (R4H1)')
        im35, = self.a1.plot([], [], 'o-', label='Roller Force - (R4H2)')
        im36, = self.a1.plot([], [], 'o-', label='Roller Force - (R4H3)')
        im37, = self.a1.plot([], [], 'o-', label='Roller Force - (R4H4)')
        im38, = self.a2.plot([], [], 'o-', label='Roller Force')
        im39, = self.a2.plot([], [], 'o-', label='Roller Force')
        im40, = self.a2.plot([], [], 'o-', label='Roller Force')
        im41, = self.a2.plot([], [], 'o-', label='Roller Force')
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
        a3.text(0.650, 0.820, 'Ring '+ rflabel +' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        a3.text(0.145, 0.403, rfPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=22, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring '+ rfPerf +' Data', fontsize=14, ha='left', transform=a3.transAxes)
        # -------------------------------------
        a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ----- Pipe Position and SMC Status -----
        a3.text(0.080, 0.090, 'Pipe Position: ' + str(piPos) + '    Processing Layer #' + str(cLayerN), fontsize=12, ha='left',
                transform=a3.transAxes)
        a3.text(0.080, 0.036, 'SMC Status: ' + msc_rt, fontsize=12, ha='left', transform=a3.transAxes)

        # ---------------- EXECUTE SYNCHRONOUS METHOD ---------------#
        def synchronousRF(rfS, rfTy, fetchT):
            fetch_no = str(fetchT)      # entry value in string sql syntax

            # Obtain Volatile Data from PLC Host Server ---------------------------[]
            if not dataReady:                    # Load CommsPlc class once
                import CommsSql as q
                q.DAQ_connect(1, 0)
            else:
                con_a, con_b = conn.cursor(), conn.cursor()

            # Evaluate conditions for SQL Data Fetch ------------------------------[A]
            """
            Load watchdog function with synchronous function every seconds
            """
            # Initialise RT variables ---[]
            autoSpcRun = True
            autoSpcPause = False
            import keyboard                         # for temporary use

            # import spcWatchDog as wd ----------------------------------[OBTAIN MSC]
            # sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
            # Define PLC/SMC error state -------------------------------------------#

            while True:
                if UsePLC_DBS:  # Not Using PLC Data
                    import plcArrayRLmethodRF as crf                    # DrLabs optimization method
                    sysRun, msctcp, msc_rt, cLayr = wd.autoPausePlay()
                    if sysRun:
                        inProgress = True  # True for RetroPlay mode
                    else:
                        inProgress = False
                    print('\nSynchronous controller activated...')

                    # Either of the 2 combo variables are assigned to trigger routine pause
                    if keyboard.is_pressed("Alt+Q") or not msctcp == 315 and not sysRun and not inProgress:
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

                    # Allow selective runtime parameter selection on production-critical process
                    rfMta = crf.plcExec(T1, rfS, rfTy, fetch_no)
                    rfMtb = 0

                else:
                    import sqlArrayRLmethodRF as crf  # DrLabs optimization method

                    inProgress = True  # True for RetroPlay mode
                    print('\nAsynchronous controller activated...')
                    print('DrLabs' + "' Runtime Optimisation is Enabled!")

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
                        rfMta, rfMtb = crf.sqlExec(rfS, rfTy, con_a, con_b, T1, T2, fetchT)
                        print("Visualization in Play Mode...")
                    print('\nUpdating....')
                    # ------ Inhibit iteration ----------------------------------------------------------[]
                    """
                    # Set condition for halting real-time plots in watchdog class ---------------------
                    """
                    # TODO --- values for inhibiting the SQL processing
                    if keyboard.is_pressed("Alt+Q"):  # Terminate file-fetch
                        con_a.close()
                        con_b.close()
                        print('SQL End of File, connection closes after 30 mins...')
                        time.sleep(60)
                        continue
                    else:
                        print('\nUpdating....')

            return rfMta, rfMtb

        # ================== End of synchronous Method ==========================

        def asynchronousRF(self):
            timei = time.time()  # start timing the entire loop

            # Bistream Data Pooling Method ---------------------#
            rfMta, rfMtb = synchronousRF(rfS, rfTy, db_freq)    # data loading functions
            # --------------------------------------------------#

            if UsePLC_DBS == 1:
                import VarPLClp as rf

                viz_cycle = 10
                # Call synchronous data function ---------------[]
                columns = qrf.validCols(T1)  # Load defined valid columns for PLC Data
                df1 = pd.DataFrame(rfMta, columns=columns)  # Include table data into python Dataframe
                cRF = rf.loadProcesValues(df1)  # Join data values under dataframe

            else:
                import VarSQLlp as rf                   # load SQL variables column names | rfVarSQL

                viz_cycle = 150
                g1 = qrf.validCols(T1)                  # Construct Data Column selSqlColumnsTFM.py
                d1 = pd.DataFrame(rfMta, columns=g1)    # Import into python Dataframe

                g2 = qla.validCols(T2)
                d2 = pd.DataFrame(rfMtb, columns=g2)

                # Concatenate all columns -----------[]
                df1 = pd.concat([d1, d2], axis=1)

                cRF = rf.loadProcesValues(df1)          # Join data values under dataframe
            print('\nSQL Content', df1.head(10))
            print("Memory Usage:", df1.info(verbose=False))  # Check memory utilization

            # -------------------------------------------------------------------------------------[]
            # Plot X-Axis data points -------- X Plot
            im10.set_xdata(np.arange(self.win_Xmax))
            im11.set_xdata(np.arange(self.win_Xmax))
            im12.set_xdata(np.arange(self.win_Xmax))
            im13.set_xdata(np.arange(self.win_Xmax))
            im14.set_xdata(np.arange(self.win_Xmax))
            im15.set_xdata(np.arange(self.win_Xmax))
            im16.set_xdata(np.arange(self.win_Xmax))
            im17.set_xdata(np.arange(self.win_Xmax))
            im18.set_xdata(np.arange(self.win_Xmax))
            im19.set_xdata(np.arange(self.win_Xmax))
            im20.set_xdata(np.arange(self.win_Xmax))
            im21.set_xdata(np.arange(self.win_Xmax))
            im22.set_xdata(np.arange(self.win_Xmax))
            im23.set_xdata(np.arange(self.win_Xmax))
            im24.set_xdata(np.arange(self.win_Xmax))
            im25.set_xdata(np.arange(self.win_Xmax))
            # ------------------------------- S Plot
            # ------------------------------- S Plot
            im26.set_xdata(np.arange(self.win_Xmax))
            im27.set_xdata(np.arange(self.win_Xmax))
            im28.set_xdata(np.arange(self.win_Xmax))
            im29.set_xdata(np.arange(self.win_Xmax))
            im30.set_xdata(np.arange(self.win_Xmax))
            im31.set_xdata(np.arange(self.win_Xmax))
            im32.set_xdata(np.arange(self.win_Xmax))
            im33.set_xdata(np.arange(self.win_Xmax))
            im34.set_xdata(np.arange(self.win_Xmax))
            im35.set_xdata(np.arange(self.win_Xmax))
            im36.set_xdata(np.arange(self.win_Xmax))
            im37.set_xdata(np.arange(self.win_Xmax))
            im38.set_xdata(np.arange(self.win_Xmax))
            im39.set_xdata(np.arange(self.win_Xmax))
            im40.set_xdata(np.arange(self.win_Xmax))
            im41.set_xdata(np.arange(self.win_Xmax))

            # X Plot Y-Axis data points for XBar --------------------------------------------[  # Ring 1 ]
            im10.set_ydata((cRF[0]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 1
            im11.set_ydata((cRF[1]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 2
            im12.set_ydata((cRF[2]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 3
            im13.set_ydata((cRF[3]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 4
            # ------ Evaluate Pp for Ring 1 ---------#
            mnA, sdA, xusA, xlsA, xucA, xlcA, ppA, pkA = tq.eProcessR1(rfHL, rfS, 'RF')
            # ---------------------------------------#
            im14.set_ydata((cRF[4]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 1
            im15.set_ydata((cRF[5]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 2
            im16.set_ydata((cRF[6]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 3
            im17.set_ydata((cRF[7]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 4
            # ------ Evaluate Pp for Ring 2 ---------#
            mnB, sdB, xusB, xlsB, xucB, xlcB, ppB, pkB = tq.eProcessR2(rfHL, rfS, 'RF')
            # ---------------------------------------#
            im18.set_ydata((cRF[8]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 1
            im19.set_ydata((cRF[9]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 2
            im20.set_ydata((cRF[10]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 3
            im21.set_ydata((cRF[11]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 4
            # ------ Evaluate Pp for Ring 3 ---------#
            mnC, sdC, xusC, xlsC, xucC, xlcC, ppC, pkC = tq.eProcessR3(rfHL, rfS, 'RF')
            # ---------------------------------------#
            im22.set_ydata((cRF[12]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 1
            im23.set_ydata((cRF[13]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 2
            im24.set_ydata((cRF[14]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 3
            im25.set_ydata((cRF[15]).rolling(window=rfS).mean()[0:self.win_Xmax])  # head 4
            # ------ Evaluate Pp for Ring 4 ---------#
            mnD, sdD, xusD, xlsD, xucD, xlcD, ppD, pkD = tq.eProcessR4(rfHL, rfS, 'RF')
            # ---------------------------------------#
            # S Plot Y-Axis data points for StdDev ----------------------------------------
            im26.set_ydata((cRF[0]).rolling(window=rfS).std()[0:self.win_Xmax])
            im27.set_ydata((cRF[1]).rolling(window=rfS).std()[0:self.win_Xmax])
            im28.set_ydata((cRF[2]).rolling(window=rfS).std()[0:self.win_Xmax])
            im29.set_ydata((cRF[3]).rolling(window=rfS).std()[0:self.win_Xmax])

            im30.set_ydata((cRF[4]).rolling(window=rfS).std()[0:self.win_Xmax])
            im31.set_ydata((cRF[5]).rolling(window=rfS).std()[0:self.win_Xmax])
            im32.set_ydata((cRF[6]).rolling(window=rfS).std()[0:self.win_Xmax])
            im33.set_ydata((cRF[7]).rolling(window=rfS).std()[0:self.win_Xmax])

            im34.set_ydata((cRF[8]).rolling(window=rfS).std()[0:self.win_Xmax])
            im35.set_ydata((cRF[9]).rolling(window=rfS).std()[0:self.win_Xmax])
            im36.set_ydata((cRF[10]).rolling(window=rfS).std()[0:self.win_Xmax])
            im37.set_ydata((cRF[11]).rolling(window=rfS).std()[0:self.win_Xmax])

            im38.set_ydata((cRF[12]).rolling(window=rfS).std()[0:self.win_Xmax])
            im39.set_ydata((cRF[13]).rolling(window=rfS).std()[0:self.win_Xmax])
            im40.set_ydata((cRF[14]).rolling(window=rfS).std()[0:self.win_Xmax])
            im41.set_ydata((cRF[15]).rolling(window=rfS).std()[0:self.win_Xmax])

            # Compute entire Process Capability -----------#
            if not rfHL:
                mnT, sdT, xusT, xlsT, xucT, xlcT, dUCLb, dLCLb, ppT, pkT, xline, sline = tq.tAutoPerf(rfS, mnA, mnB,
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
            if self.win_Xmax > window_Xmax:
                a1.set_xlim(self.win_Xmax - window_Xmax, self.win_Xmax)
                a2.set_xlim(self.win_Xmax - window_Xmax, self.win_Xmax)
            else:
                a1.set_xlim(0, window_Xmax)
                a2.set_xlim(0, window_Xmax)

            # Set trip line for individual time-series plot -----------------------------------[R1]
            sigma = gma.trigViolations(a1, UsePLC_DBS, 'RF', YScale_minRF, YScale_maxRF, xucT, xlcT, xusT, xlsT, mnT, sdT)

            timef = time.time()
            lapsedT = timef - timei
            print(f"\nProcess Interval: {lapsedT} sec\n")

            ani = FuncAnimation(fig, asynchronousRF, frames=None, save_count=100, repeat_delay=None, interval=viz_cycle,
                                blit=False)
            plt.tight_layout()
            plt.show()

        # Update Canvas -----------------------------------------------------[]
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().pack(expand=True)
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
        oLS, oLTy = cDM, cSS
        # Load metrics from config -----------------------------------[]
        if pRecipe == 'DNV':
            import qParamsHL_DNV as qp
        else:
            import qParamsHL_MGM as qp
        # ------------------------------------------------------------[]
        rfS, rfTy, rfSoL, rfSoP, rfHL, rfAL, rfFO, rfP1, rfP2, rfP3, rfP4, rfP5 = qp.decryptpProcessLim(pWON, 'RF')
        # Break down each element to useful list -----[Tape Temperature]

        if rfHL and rfP1 and rfP2 and rfP3 and rfP4 and rfP5:  #
            rfPerf = '$Pp_{k' + str(rfS) + '}$'  # Using estimated or historical Mean
            rflabel = 'Pp'
            # -------------------------------------[]
            One = rfP1.split(',')  # split into list elements
            Two = rfP2.split(',')
            Thr = rfP3.split(',')
            For = rfP4.split(',')
            Fiv = rfP5.split(',')
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
            rfPerf = '$Cp_{k' + str(rfS) + '}$'  # Using Automatic group Mean
            rflabel = 'Cp'

        label = ttk.Label(self, text="JIT - End of Layer Processing", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        # Define Axes ---------------------#
        fig = Figure(figsize=(12.5, 5.5), dpi=100)
        fig.subplots_adjust(left=0.043, bottom=0.043, right=0.986, top=0.96, hspace=0.14, wspace=0.195)
        # ----------------------------------
        a1 = fig.add_subplot(2, 2, (1, 2))                          # Cell Tension X Bar Plot
        a2 = fig.add_subplot(2, 2, (3, 4))                          # Cell Tension s Plot

        # Declare Plots attributes --------------------------------[]
        plt.rcParams.update({'font.size': 7})                       # Reduce font size to 7pt for all legends
        # Calibrate limits for X-moving Axis -----------------------#
        YScale_minEOL, YScale_maxEOL = 18.5, 38.5
        sBar_minEOL, sBar_maxEOL = 10, 250                          # Calibrate Y-axis for S-Plot
        window_Xmin, window_Xmax = 0, (int(oLS) + 3)                # windows view = visible data points

        # ----------------------------------------------------------#
        # Real-Time Parameter according to updated requirements ----# 28/Feb/2025
        T1 = 'RF1_' + pWON                                          # Roller Force
        T2 = 'RF2_' + pWON
        # ----------------------------------------------------------#

        # Common properties ----------------------------------------#
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [" + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        a1.set_title('Cell Tension [XBar Plot]', fontsize=12, fontweight='bold')
        a2.set_title('Cell Tension [SBar Plot]', fontsize=12, fontweight='bold')
        # Apply grid lines -----
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        a1.legend(loc='upper right', title='Cell Tension Control Plot')
        a2.legend(loc='upper right', title='Sigma curve')

        # ---------------------------------------------------------#
        a1.set_ylim([YScale_minEOL, YScale_maxEOL], auto=True)
        a1.set_xlim([window_Xmin, window_Xmax])
        # ---------------------------------------------------------#
        a2.set_ylim([sBar_minEOL, sBar_maxEOL], auto=True)
        a2.set_xlim([window_Xmin, window_Xmax])

        # ----------------------------------------------------------[]
        # Define Plot area and axes -
        # ----------------------------------------------------------#
        im10, = self.a1.plot([], [], 'o-', label='Roller Force - (R1H1)')
        im11, = self.a1.plot([], [], 'o-', label='Roller Force - (R1H2)')
        im12, = self.a1.plot([], [], 'o-', label='Roller Force - (R1H3)')
        im13, = self.a1.plot([], [], 'o-', label='Roller Force - (R1H4)')
        im14, = self.a2.plot([], [], 'o-', label='Roller Force')
        im15, = self.a2.plot([], [], 'o-', label='Roller Force')
        im16, = self.a2.plot([], [], 'o-', label='Roller Force')
        im17, = self.a2.plot([], [], 'o-', label='Roller Force')

        im18, = self.a1.plot([], [], 'o-', label='Roller Force - (R2H1)')
        im19, = self.a1.plot([], [], 'o-', label='Roller Force - (R2H2)')
        im20, = self.a1.plot([], [], 'o-', label='Roller Force - (R2H3)')
        im21, = self.a1.plot([], [], 'o-', label='Roller Force - (R2H4)')
        im22, = self.a2.plot([], [], 'o-', label='Roller Force')
        im23, = self.a2.plot([], [], 'o-', label='Roller Force')
        im24, = self.a2.plot([], [], 'o-', label='Roller Force')
        im25, = self.a2.plot([], [], 'o-', label='Roller Force')

        im26, = self.a1.plot([], [], 'o-', label='Roller Force - (R3H1)')
        im27, = self.a1.plot([], [], 'o-', label='Roller Force - (R3H2)')
        im28, = self.a1.plot([], [], 'o-', label='Roller Force - (R3H3)')
        im29, = self.a1.plot([], [], 'o-', label='Roller Force - (R3H4)')
        im30, = self.a2.plot([], [], 'o-', label='Roller Force')
        im31, = self.a2.plot([], [], 'o-', label='Roller Force')
        im32, = self.a2.plot([], [], 'o-', label='Roller Force')
        im33, = self.a2.plot([], [], 'o-', label='Roller Force')

        im34, = self.a1.plot([], [], 'o-', label='Roller Force - (R4H1)')
        im35, = self.a1.plot([], [], 'o-', label='Roller Force - (R4H2)')
        im36, = self.a1.plot([], [], 'o-', label='Roller Force - (R4H3)')
        im37, = self.a1.plot([], [], 'o-', label='Roller Force - (R4H4)')
        im38, = self.a2.plot([], [], 'o-', label='Roller Force')
        im39, = self.a2.plot([], [], 'o-', label='Roller Force')
        im40, = self.a2.plot([], [], 'o-', label='Roller Force')
        im41, = self.a2.plot([], [], 'o-', label='Roller Force')
        # -----------------------------------------------------------#
        # Calibrate the rest of the Plots ---------------------------#
        # -----------------------------------------------------------[]
        # Define Plot area and axes -
        # ----------------------------------------------------------#
        im10, = self.a1.plot([], [], 'o-', label='Cell Tension A (N/mm2)')
        im11, = self.a1.plot([], [], 'o-', label='Cell tension B (N/mm2)')


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
            # sysRun, msctcp, msc_rt = False, 100, 'Unknown state, Check PLC & Watchdog...'
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

        def asynchronousEoL(self):

            timei = time.time()  # start timing the entire loop

            # Call data loader Method---------------------------#
            ctSQL = synchronousEoL(smp_Sz, stp_Sz, self.win_Xmax)      # data loading functions

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
            im10.set_xdata(np.arange(self.win_Xmax))
            im11.set_xdata(np.arange(self.win_Xmax))
            # X Plot Y-Axis data points for XBar -------------------------------------------[# Channels]
            im10.set_ydata((RF[0]).rolling(window=smp_Sz).mean()[0:self.win_Xmax])  # Segment 1
            im11.set_ydata((RF[1]).rolling(window=smp_Sz).mean()[0:self.win_Xmax])  # Segment 2
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
            if self.win_Xmax > window_Xmax:
                a1.set_xlim(self.win_Xmax - window_Xmax, self.win_Xmax)
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
        canvas.get_tk_widget().pack(expand=True)
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
                rpt = "RPT_RP_" + str(pWON)
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder
            elif selected_option == "Tape Temperature":
                rpt = "RPT_TT_" + str(pWON)
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder
            elif selected_option == "Subs Temperature":
                rpt = "RPT_ST_" + str(pWON)
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder
            elif selected_option == "Winding Speed":
                rpt = "RPT_WS_" + str(pWON)
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder
            elif selected_option == "Gap Measurement":
                rpt = "RPT_TG_" + str(pWON)
                readEoP(text_widget, rpt)                                 # Open txt file from FMEA folder
            else:
                rpt = "VOID_REPORT"
                readEoP(text_widget, rpt)                                 # Clean up the matt instead

            print("You selected:", selected_option)
        combo.bind("<<ComboboxSelected>>", option_selected)

        # Update Canvas -----------------------------------------------------[NO FIGURE YET]
        # canvas = FigureCanvasTkAgg(fig, self)
        # canvas.get_tk_widget().pack(expand=True)

        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True)

# --------------------------------------------------------------------------------------------------------------
# def load_snoozeScreen():
#     print("Task 1 assigned to thread: {}".format(threading.current_thread().name))
#     print("ID of process running task 1: {}".format(os.getpid()))
#     # ----- load screen saver
#     nw.dScreen()
#
# def load_spalshScreen():
#     print("Task 2 assigned to thread: {}".format(threading.current_thread().name))
#     print("ID of process running task 2: {}".format(os.getpid()))
#     nw.watchDog()
# ====================================================== MAIN PIPELINE ===========================================[]
# qType = 0   # default play mode


def userMenu(cMode, WON, vMode=None):     # listener, myplash
    print('\nWelcome to Magma Synchronous SPC!')
    global uCalling, pWON, root, sqlRO, metRO, HeadA, HeadB, vTFM, comboL, comboR, qType, cLayerN, \
        sysRun, sysidl, sysrdy, pRecipe, msc_rt, piPos, UsePLC_DBS, UseSQL_DBS

    uCalling = cMode
    # ---- retrieve WON from called Method -----------------------------[]
    """
    uCalled = 1 (PLC Trigger)
    uCalled = 2 (SQL Trigger)
    uCalled = 3 (Operator launched)
    # -----------------------------
    vMode = 1 (Cascade View)
    vMode = 2 (Tabbed View)
    
    """

    # -----------------------------------------------------------------#

    root = Tk()
    # inherit PID from Splash Screen and transfer back when Object closes
    print('\nUser Menu: Inherited PARENT ID#:', os.getppid())
    print('User Menu: Inherited CHILD ID#:', os.getpid())
    print('User Menu: New Object THREAD:', get_native_id())
    time.sleep(2)

    # for windows centralizing ---------[]
    window_height = 580     #1080
    window_width = 950      #1920

    root.title('Synchronous SPC - ' + strftime("%a, %d %b %Y", gmtime())+ ' WON #: '+ WON)
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
    # --------------------------------------------------------------------------------------[]

    # Define volatile runtime variables -------------------[]
    svar1 = IntVar()

    sqlRO = False       # SQL server filed is read only
    metRO = False

    def clearFields():  # for SQL server credentials -------
        # clear the content of text entry box
        if sub_menu.entrycget(0, 'state') == 'disabled' and sub_menu.entrycget(1, 'state') == 'normal':
            seripSql.set('')
            sqlid.set('')
            uname.set('')
            autho.set('')
            Entry(pop, state='normal', textvariable=seripSql).place(x=86, y=60)
            Entry(pop, state='normal', textvariable=sqlid).place(x=86, y=100)
            Entry(pop, state='normal', textvariable=uname).place(x=330, y=60)
            Entry(pop, state='normal', textvariable=autho, show="*").place(x=330, y=100)

        elif sub_menu.entrycget(1, 'state') == 'disabled' and sub_menu.entrycget(0, 'state') == 'normal':
            hostIPv4.set('')
            hostName.set('')
            deviceNm.set('')
            authopwd.set('')
            Entry(pop, state='normal', width=15, textvariable=hostIPv4).place(x=105, y=60)
            Entry(pop, state='normal', width=15, textvariable=hostName).place(x=105, y=100)
            Entry(pop, state='normal', width=15, textvariable=deviceNm).place(x=330, y=60)
            Entry(pop, state='normal', width=15, textvariable=authopwd, show="*").place(x=330, y=100)
        else:
            pass
        sqlRO = True
        print('Read Only Field State:', sqlRO)

        return sqlRO

    # function to allow historical limits entry---------------------------------------------[]

    def errorNote():
        messagebox.showerror('Error', 'Empty field(s)')
        return

    def successNote():
        messagebox.showinfo('Saved', 'Config Saved')
        return

    def save_pMetrics():                    # Save historical Limits for Production Parameters
        print("\nSaving Production Constants..")
        grayOut = [button2, e7, e8, m1, m2, m3, m4, m5, m6]             # set value entry field to read only
        e5.config(state='readonly')                                     # applicable to combo drop down
        e6.config(state='readonly')                                     # combo box property

        for fld in grayOut:
            fld.config(state="disabled")                                # for text fields
        if hLmtA.get() == 1:                                            # check condition of edit button
            hLmtA.set(0)                                                # uncheck the button
        s_butt.config(state="disabled")                                 # disable Save button

        print('\nStacked Values:', rtValues)
        print('Array Length', len(rtValues))

        # print('Switch Values', rtValues[-1])
        if len(rtValues) > 1:                                           # Compute the length for dynamic arrays
            x = len(rtValues) - 1                                       # Use the last index
            print('\nTest Vars:', m1, m2, m3, m4, m5, m6)

            # Encrypt configuration on production params ---------------#
            dd.saveMetricspP(pWON,  rMode, sel_SS, sel_gT, LA, LP, CT, OT, RP, WS, sSta, sEnd, rtValues[x][0], rtValues[x][1], rtValues[x][2],
                             rtValues[x][3], rtValues[x][4], rtValues[x][5], rtValues[x][6])
        else:
            print('\nTest Vars:', m1, m2, m3, m4, m5, m6)
            dd.saveMetricspP(pWON, rMode, sel_SS, sel_gT, LA, LP, CT, OT, RP, WS, sSta, sEnd, xlp, xla, xtp, xrf, xtt, xst, xtg)

        return


    def clearMetrics():
        # clear the content of chart parameter using change settings button ---
        global e5, e6, e7, e8, m1, m2, m3, m4, m5, m6, metRO, clearM

        # pop = Toplevel(root)
        # pop.wm_attributes('-topmost', True)
        clearM = 1
        if clearM:
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
        else:
            clearM = 0
            metRO = False
        print('SQL Field State:', metRO, clearM)  # metric fields set to read only

        return
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
        global pStat, dMax, mMax, oMax, OT, CT, RP, WS, LP, LA, m1, m2, m3, m4, m5, m6, xlp, xla, xtp, xrf, xtt, xst, xtg

        if dnvMinMax.get():
            print('\nMonitoring Parameters for DNV Production..')
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
            mLA.set(0)      # Laser Angle
            mLP.set(0)      # Laser Power
            # ----------------------------------------------------
            if metRO:
                # repopulate with default values -----------#
                m1 = Checkbutton(pop, text="Oven Temperature", font=("bold", 10), variable=mOT, state="disabled")
                m1.place(x=10, y=y_start)

                m2 = Checkbutton(pop, text="Active Cell Tension", font=("bold", 10), variable=mCT, state="disabled")
                m2.place(x=150, y=y_start)

                m3 = Checkbutton(pop, text="Tape Winding Spd", font=("bold", 10), variable=mWS, state="disabled")
                m3.place(x=10, y=y_start + y_incmt * 1)

                m4 = Checkbutton(pop, text="Reinforced Pressure", font=("bold", 10), variable=mRP, state="disabled")
                m4.place(x=150, y=y_start + y_incmt * 1)

                # -------------------------------------------- Not included in DNV/MGM requirements
                m5 = Checkbutton(pop, text="Laser Power", font=("bold", 10), variable=mLP, state="disabled")
                m5.place(x=305, y=y_start)

                m6 = Checkbutton(pop, text="Laser Angle", font=("bold", 10), variable=mLA, state="disabled")
                m6.place(x=305, y=y_start + y_incmt * 1)
                # -----------------------------------
            OT, CT, WS, RP, LP, LA = 1, 1, 1, 1, 0, 0
            xlp, xla, xtp, xrf, xtt, xst, xtg = 0, 0, 0, 0, 1, 1, 1
        # -----------End of Parameters ---------------
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
            OT, CT, WS, RP, LP, LA = 0, 0, 0, 0, 0, 0
            xlp, xla, xtp, xrf, xtt, xst, xtg = 0, 0, 0, 0, 0, 0, 0

        print('Monitoring DNV Params:', OT, CT, WS, RP, LP, LA, 'Plot Stats:', pStat)
        return OT, CT, WS, RP, LP, LA

    def mMinMaxPlot():
        global pStat, dMax, mMax, oMax, OT, CT, WS, RP, LP, LA, xlp, xla, xtp, xrf, xtt, xst, xtg, m1, m2, m3, m4, m5, m6

        if mgmMinMax.get():
            print('\nMonitoring Parameters for Commercial Production..')
            dMax = 0
            mMax = 1
            oMax = 0
            pStat = 1
            dnvMinMax.set(dMax)
            mgmMinMax.set(mMax)
            othMinMax.set(oMax)
            # Set default Monitoring params for MGM
            mOT.set(1)  # Oven Temperature
            mCT.set(1)  # Cell Tension
            mRP.set(1)  # Roller Pressure
            mWS.set(1)  # Tape Winding Speed
            # --------
            mLA.set(1)  # Laser Angle
            mLP.set(1)  # Laser Power
            # ----------------------------------------------------[]
            if metRO:
                # repopulate with default values -----------#
                m1 = Checkbutton(pop, text="Oven Temperature", font=("bold", 10), variable=mOT, state="disabled")
                m1.place(x=10, y=y_start)
                mOT.set(1)

                m2 = Checkbutton(pop, text="Active Cell Tension", font=("bold", 10), variable=mCT, state="disabled")
                m2.place(x=150, y=y_start)  # x=160
                mCT.set(1)

                m3 = Checkbutton(pop, text="Tape Winding Spd", font=("bold", 10), variable=mWS, state="disabled")
                m3.place(x=10, y=y_start + y_incmt * 1)
                mWS.set(1)

                m4 = Checkbutton(pop, text="Reinforced Pressure", font=("bold", 10), variable=mRP, state="disabled")
                m4.place(x=150, y=y_start + y_incmt * 1)
                mRP.set(1)
                # -------------------------------------------- Not included in DNV/MGM requirements
                m5 = Checkbutton(pop, text="Laser Power", font=("bold", 10), variable=mLP, state="disabled")
                m5.place(x=305, y=y_start)

                m6 = Checkbutton(pop, text="Laser Angle", font=("bold", 10), variable=mLA, state="disabled")
                m6.place(x=305, y=y_start + y_incmt * 1)
            # --------Summary of Monitors -----------
            OT, CT, WS, RP, LP, LA = 1, 1, 1, 1, 1, 1
            xlp, xla, xtp, xrf, xtt, xst, xtg = 1, 1, 1, 1, 1, 1, 1
            # -----------End of Parameters ----------
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
            OT, CT, WS, RP, LP, LA = 0, 0, 0, 0, 0, 0
            xlp, xla, xtp, xrf, xtt, xst, xtg = 0, 0, 0, 0, 0, 0, 0

        print('Monitoring MGM Params:', OT, CT, WS, RP, LP, LA, 'Plot Stats:', pStat)
        return OT, CT, WS, RP, LP, LA


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
            hlb.paramsEntry(modal, sel_SS, sel_gT, mdnv, aut, ymgm, pLP, pLA, pTP, pRF, pTT, pST, pTG)
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
            hlb.paramsEntry(modal, sel_SS, sel_gT, mdnv, aut, ymgm, pLP, pLA, pTP, pRF, pTT, pST, pTG)
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
            hlb.paramsEntry(modal, sel_SS, sel_gT, mdnv, aut, ymgm, pLP, pLA, pTP, pRF, pTT, pST, pTG)
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
            hlb.paramsEntry(modal, sel_SS, sel_gT, mdnv, aut, ymgm, pLP, pLA, pTP, pRF, pTT, pST, pTG)
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
            hlb.paramsEntry(modal, sel_SS, sel_gT, mdnv, aut, ymgm, pLP, pLA, pTP, pRF, pTT, pST, pTG)
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
            hlb.paramsEntry(modal, sel_SS, sel_gT, mdnv, aut, ymgm, pLP, pLA, pTP, pRF, pTT, pST, pTG)
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
            hlb.paramsEntry(modal, sel_SS, sel_gT, mdnv, aut, ymgm, pLP, pLA, pTP, pRF, pTT, pST, pTG)
        else:
            pLA.set(0)

    def runChecksB():
        if pTT.get():
            pTT.set(1)
            pRP.set(0)
            pST.set(0)
            pWS.set(0)
            pTG.set(0)
            hla.paramsEntry(modal, sel_SS, sel_gT, mdnv, aut, ymgm, pRP, pTT, pST, pWS, pTG) #
        else:
            pTT.set(0)
            pRP.set(0)
            pST.set(0)
            pWS.set(0)
            pTG.set(0)

    def runChecksC():
        if pST.get():
            pST.set(1)
            pRP.set(0)
            pTT.set(0)
            pWS.set(0)
            pTG.set(0)
            hla.paramsEntry(modal, sel_SS, sel_gT, mdnv, aut, ymgm, pRP, pTT, pST, pWS, pTG)
        else:
            pST.set(0)
            pRP.set(0)
            pTT.set(0)
            pWS.set(0)
            pTG.set(0)

    def runChecksD():
        if pWS.get():
            pWS.set(1)
            pRP.set(0)
            pTT.set(0)
            pST.set(0)
            pTG.set(0)
            hla.paramsEntry(modal, sel_SS, sel_gT, mdnv, aut, ymgm, pRP, pTT, pST, pWS, pTG)
        else:
            pWS.set(0)
            pRP.set(0)
            pTT.set(0)
            pST.set(0)
            pTG.set(0)

    def runChecksE():
        if pTG.get():
            pTG.set(1)
            pRP.set(0)
            pTT.set(0)
            pST.set(0)
            pWS.set(0)
            hla.paramsEntry(modal, sel_SS, sel_gT, mdnv, aut, ymgm, pRP, pTT, pST, pWS, pTG)
        else:
            pTG.set(0)
            pRP.set(0)
            pTT.set(0)
            pST.set(0)
            pWS.set(0)


    def dnvConfigs():
        global modal, pRP, pTT, pST, pWS, pTG, mdnv, aut, ymgm

        # prevent parent window closure until 'Save settings' ---[]
        root.protocol("WM_DELETE_WINDOW", preventClose)  # prevent closure even when using (ALT + F4)
        # -------------------------------------------------------[]
        mdnv, aut, ymgm = 1, 0, 0

        modal = Toplevel(root)
        modal.wm_attributes('-topmost', True)

        pRP, pTT, pST, pWS, pTG = IntVar(), IntVar(), IntVar(), IntVar(), IntVar()
        # ----------------------------------------------------------------------------------[]
        modal.resizable(False, False)

        w, h = 615, 250
        modal.title('Lookup Table: Define Historical Limits')
        screen_w = modal.winfo_screenwidth()
        screen_h = modal.winfo_screenheight()
        x_c = int((screen_w / 2) - (w / 2))
        y_c = int((screen_h / 2) - (h / 2))
        modal.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))

        # ----------------------------------------------------------------------------------[]
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
        global modal, pLP, pLA, pTP, pRF, pTT, pST, pTG, mdnv, aut, ymgm

        # prevent parent window closure until 'Save settings' ---[]
        root.protocol("WM_DELETE_WINDOW", preventClose)  # prevent closure even when using (ALT + F4)
        # -------------------------------------------------------[]

        mdnv, aut, ymgm = 0, 0, 1

        modal = Toplevel(root)
        modal.wm_attributes('-topmost', True)

        pLP, pLA, pTP, pRF, pTT, pST, pTG = IntVar(), IntVar(), IntVar(), IntVar(), IntVar(), IntVar(), IntVar()

        # ----------------------------------------------------------------------------------------[]
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
        global dnv, aut, mgm

        if pLmtA.get():
            dnv = 1
            aut = 0
            mgm = 0
            dnv_butt.config(state="normal")
            mgm_butt.config(state="disabled")
            pLmtA.set(dnv)
            shewhart.set(aut)
            pLmtB.set(mgm)
        else:
            dnv = 1
            aut = 0
            mgm = 0
            dnv_butt.config(state="disabled")
            mgm_butt.config(state="disabled")
            pLmtA.set(dnv)
            shewhart.set(aut)
            pLmtB.set(mgm)

        return dnv, aut, mgm

    def enAUTO():
        global dnv, aut, mgm

        if shewhart.get():
            dnv = 0
            aut = 1
            mgm = 0
            dnv_butt.config(state="disabled")
            mgm_butt.config(state="disabled")
            pLmtA.set(dnv)
            shewhart.set(aut)
            pLmtB.set(mgm)
        else:
            dnv = 0
            aut = 1
            mgm = 0
            dnv_butt.config(state="disabled")
            mgm_butt.config(state="disabled")
            pLmtA.set(dnv)
            shewhart.set(aut)
            pLmtB.set(mgm)

        return dnv, aut, mgm

    def enMGM():
        global dnv, aut, mgm

        if pLmtB.get():
            dnv = 0
            aut = 0
            mgm = 1
            mgm_butt.config(state="normal")
            dnv_butt.config(state="disabled")
            pLmtA.set(dnv)
            shewhart.set(aut)
            pLmtB.set(mgm)
        else:
            dnv = 0
            aut = 0
            mgm = 1
            mgm_butt.config(state="disabled")
            dnv_butt.config(state="disabled")
            pLmtA.set(dnv)
            shewhart.set(aut)
            pLmtB.set(mgm)

        return dnv, aut, mgm

    def watchDG():
        global rMode, HeadA, HeadB, closeV
        if pWDG.get():
            rMode = 1                   # set auto synchronous mode
            process.entryconfig(0, state='disabled')
            process.entryconfig(1, state='disabled')
            process.entryconfig(3, state='disabled')
            # -------------------------------------------
            analysis.entryconfig(0, state='normal')
            analysis.entryconfig(1, state='disabled')
            analysis.entryconfig(3, state='disabled')
            pWDG.set(rMode)
            HeadA, HeadB, closeV = 0, 1, 0  # call embedded functions

        else:
            rMode = 0                       # clear auto synchronous mode
            process.entryconfig(0, state='normal')
            process.entryconfig(1, state='normal')
            process.entryconfig(3, state='normal')
            # -------------------------------------------
            analysis.entryconfig(0, state='normal')
            analysis.entryconfig(1, state='normal')
            analysis.entryconfig(3, state='normal')
            pWDG.set(rMode)
            HeadA, HeadB, closeV = 0, 1, 0  # call embedded functions

        return # rMode, HeadA, HeadB, closeV

    def preventClose():
        print('Variable State:', pLmtA.get())
        pass

    def newMetricsConfig():  # This is a DNV Metric Configuration Lookup Table ------[]

        global pLmtA, sSta, sEnd, eStat, gSize1, gSize2, xUCLLP, xLCLLP, xUCLLA, xLCLLA, xUCLHT, xLCLHT, xUCLDL, \
            xLCLDL, xUCLDD, xLCLDD, xUCLOT, xLCLOT, hLmtA, shewhart, pLmtB, dnvMinMax, mgmMinMax, othMinMax, pWDG, \
            s_butt, sSta, sEnd, e5, e6, dnv_butt, mgm_butt, button2, pop, mLA, mLP, mCT, mOT, mRP, mWS, m1, m2, m3, \
            m4, m5, m6, pWDG

        pop = Toplevel(root)
        pop.wm_attributes('-topmost', True)

        # center root window ------------------------[]
        pop.tk.eval(f'tk::PlaceWindow {pop._w} center')
        # pop.withdraw()

        # Define volatile runtime variables ---------[]
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

        pLmtA, pLmtB, pLmtC, pLmtD, pLmtE, pLmtF = (IntVar(pop), IntVar(pop), IntVar(pop), IntVar(pop),
                                                    IntVar(pop), IntVar(pop))

        hLmtA, hLmtB, shewhart, Sample = IntVar(pop), IntVar(pop), IntVar(pop), StringVar(pop)

        dnvMinMax, mgmMinMax, othMinMax, mLA, mLP, mCT, mOT, mRP, mWS = (IntVar(pop), IntVar(pop), IntVar(pop),
                                                                         IntVar(pop), IntVar(pop), IntVar(pop),
                                                                         IntVar(pop), IntVar(pop), IntVar(pop))
        pWDG = IntVar(pop)

        # global pop, screen_h, screen_w, x_c, y_c
        # center object on the screen---
        pop.resizable(False, False)
        height = (95 + y_start + (y_incmt * 5))
        w, h = 520, height  # 450

        pop.title('Configure Samples & Parameters')
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
        p4.place(x=230, y=y_start - y_incmt * 1)    # 6

        p5 = Checkbutton(pop, text="MGM Pipe", font=("bold", 10), variable=mgmMinMax, command=mMinMaxPlot)
        p5.place(x=325, y=y_start - y_incmt * 1)    # 6

        p6 = Checkbutton(pop, text="AutoMode", font=("bold", 10), variable=pWDG, command=watchDG)
        p6.place(x=415, y=124)                      # 6
        if int(cDM):
            pWDG.set(1)
        else:
            pWDG.set(0)
        # -------------------------------------------------------------------------[]
        m1 = Checkbutton(pop, text="Oven Temperature", font=("bold", 10), variable=mOT, state="disabled")
        m1.place(x=10, y=y_start)
        mOT.set(1)

        m2 = Checkbutton(pop, text="Active Cell Tension", font=("bold", 10), variable=mCT, state="disabled")
        m2.place(x=150, y=y_start)  #x=160
        mCT.set(1)

        m3 = Checkbutton(pop, text="Tape Winding Spd", font=("bold", 10), variable=mWS, state="disabled")
        m3.place(x=10, y=y_start + y_incmt * 1)
        mWS.set(1)

        m4 = Checkbutton(pop, text="Reinforced Pressure", font=("bold", 10), variable=mRP, state="disabled")
        m4.place(x=150, y=y_start + y_incmt * 1)
        mRP.set(1)
        # -------------------------------------------- Not included in DNV/MGM requirements
        m5 = Checkbutton(pop, text="Laser Power", font=("bold", 10), variable=mLP, state="disabled")
        m5.place(x=305, y=y_start)

        m6 = Checkbutton(pop, text="Laser Angle", font=("bold", 10), variable=mLA, state="disabled")
        m6.place(x=305, y=y_start + y_incmt * 1)

        # ---------------------------------------------------------------------#
        # load variables directly from ini files --[TODO]
        sbutton = 'disabled'  # disable Save button on entry state
        cState = 'disabled'

        separatorU = ttk.Separator(pop, orient='horizontal')
        separatorU.place(relx=0.01, rely=0.53, relwidth=0.75, relheight=0.01)  # y=7.3

        # ---------------------------------------------------------------------#
        Label(pop, text='[Configure Statistical Limits]', font=("bold", 10)).place(x=10,
                                                                             y=(y_start + 5) + (y_incmt * 3))  # 320 | 7

        # --------------------------------------------------------------------------------------------#
        dnv_butt = Button(pop, text="DNV Key Parameters", wraplength=90, justify=CENTER, width=12,
                          height=3, font=("bold", 12), command=dnvConfigs, state=cState)
        dnv_butt.place(x=240, y=3 + y_start + y_incmt * 4)  # 350 | 8
        # --------------------------------------------------------------------------------------------#
        # EoLP_butt = Button(pop, text=" EoL/EoP Sampling ", width=15, command=eolpConfigs, state='normal')
        # EoLP_butt.place(x=240, y=3 + y_start + y_incmt * 6.6)
        # p4 = Checkbutton(pop, text="AutoSynchronous", font=("bold", 10), variable=pWDG, command=watchDG)
        # p4.place(x=240, y=3 + y_start + y_incmt * 6.6)  # 393 |10
        # --------------------------------------------------------------------------------------------#
        mgm_butt = Button(pop, text="MGM Key Parameters", wraplength=90, justify=CENTER, width=12,
                              height=3, font=("bold", 12), command=mgmConfigs, state=cState)
        mgm_butt.place(x=380, y=3 + y_start + y_incmt * 4)  # 350 | 8
        # --------------------------------------------------------------------------------------------#

        p1 = Checkbutton(pop, text="Set DNV Limits", font=("bold", 10), variable=pLmtA, command=enDNV)
        p1.place(x=10, y=3 + y_start + y_incmt * 4)         # 353

        p2 = Checkbutton(pop, text="Use Auto Limits", font=("bold", 10), variable=shewhart, command=enAUTO)
        p2.place(x=10, y=y_start + y_incmt * 5)             # 373 | 9
        shewhart.set(1)

        p3 = Checkbutton(pop, text="Set MGM Limits", font=("bold", 10), variable=pLmtB, command=enMGM)
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
        # TODO ---- command=saveMetricRP)

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
            ct1 = seripSql.get()
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

    def savePLCconfig():
        import OPC_UA_settings as to

        if sub_menu.entrycget(0, 'state') == 'normal':
            ct1 = hostName.get()
        else:
            ct1 = hostName.get()
        ct2 = hostIPv4.get()
        ct3 = deviceNm.get()
        ct4 = authopwd.get()
        print('Variables:', ct1, ct2, ct3, ct4)
        if ct1 == "" or ct2 == "" or ct3 == "" or ct4 == "":
            errorNote()  # response to save button when entry field is empty
            print('Empty field...')

        else:
            to.writePLCconfig(ct1, ct2, ct3, ct4)  # save into text file
            successNote()
        # Condition for saving entries ---------------[]
        Entry(pop, state='disabled').place(x=86, y=60)
        Entry(pop, state='disabled').place(x=86, y=100)
        Entry(pop, state='disabled').place(x=330, y=60)
        Entry(pop, state='disabled').place(x=330, y=100)
        pop.destroy()
        # pop.grab_release()
        return

    def serverSQLConfig():
        global pop, sqlRO, seripSql, sqlid, uname, autho, e4

        import loadSQLConfig as ls
        pop = Toplevel(root)
        # pop.wm_attributes('-topmost', True)
        pop.wm_attributes('-alpha', 0.9)

        # Define and initialise essential popup variables -------------------------------------------
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
        sub_menu.entryconfig(0, label='SQL Connectivity', state='disabled')  # disable submenu
        Label(pop, text='Server IP').place(x=10, y=60)
        Label(pop, text='Database').place(x=10, y=100)
        Label(pop, text="Access ID").place(x=250, y=60)
        Label(pop, text="Authorize").place(x=250, y=100)

        # set initial variables or last known variables
        configFile = 'checksumError.ini'
        if os.path.isfile('C:\\SynchronousGPU\\' + configFile):
            IP, name, User, Pswd = ls.load_configSQL(configFile)
            seripSql.set(IP)
            sqlid.set(name)
            uname.set(User)
            autho.set(Pswd)
            print('Using decrypted details...')
        else:
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
            e4 = Entry(pop, textvariable=autho, state='readonly', show="*")
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

    # ------------------------------------------------------------------[]
    def serverPLCConfig():
        global pop, sqlRO, hostName, hostIPv4, deviceNm, authopwd, e4

        import OPC_UA_settings as ld

        pop = Toplevel(root)
        # pop.wm_attributes('-topmost', True)
        pop.wm_attributes('-alpha', 0.9)

        # Define and initialise essential popup variables --------------[]
        hostName, hostIPv4, deviceNm, authopwd = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
        print('State:', sqlRO)

        # center object on the screen---
        w, h = 470, 210
        pop.resizable(False, False)
        pop.title('Modify PLC Connection')
        screen_w = pop.winfo_screenwidth()
        screen_h = pop.winfo_screenheight()
        x_c = int((screen_w / 2) - (w / 2))
        y_c = int((screen_h / 2) - (h / 2))
        pop.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))

        labl_0 = Label(pop, text="OPC UA Credentials", width=20, font=("bold", 14))
        labl_0.place(x=130, y=10)

        # creating labels and positioning them on the grid --------[]
        sub_menu.entryconfig(1, label='PLC Connectivity', state='disabled') # disable submenu
        Label(pop, text='Host PLC Name:').place(x=10, y=60)
        Label(pop, text="Device Access:").place(x=238, y=60)
        Label(pop, text='TCPV4 Address:').place(x=10, y=100)
        Label(pop, text="AccessID Code:").place(x=238, y=100)

        # set initial variables or last known variables
        configFile = 'ISO62264_ISA95.ini'
        if os.path.isfile('C:\\SynchronousGPU\\'+configFile):
            IP, name, User, Pswd = ld.load_configPLC(configFile)
            hostName.set(name)
            hostIPv4.set(IP)
            deviceNm.set(User)
            authopwd.set(Pswd)
            print('Using decrypted details:', name, IP, User, Pswd)
        else:
            hostName.set('DefaultHost')
            hostIPv4.set('192.168.100.XXX')
            deviceNm.set('TCP01_SPC')
            authopwd.set('*********')

        # creating entries and positioning them on the grid -----
        if not sqlRO:
            e1 = Entry(pop, textvariable=hostName, width=15, state='readonly')
            e1.place(x=105, y=60)
            e2 = Entry(pop, textvariable=hostIPv4, width=15, state='readonly')
            e2.place(x=105, y=100)
            e3 = Entry(pop, textvariable=deviceNm, width=15, state='readonly')
            e3.place(x=330, y=60)
            e4 = Entry(pop, textvariable=authopwd, width=15, state='readonly')   #, show="*")
            e4.place(x=330, y=100)
        else:
            e1 = Entry(pop, textvariable=hostName, width=15, state='normal')
            e1.place(x=105, y=60)
            e2 = Entry(pop, textvariable=hostIPv4, width=15, state='normal')
            e2.place(x=105, y=100)
            e3 = Entry(pop, textvariable=deviceNm, width=15, state='normal')
            e3.place(x=330, y=60)
            e4 = Entry(pop, textvariable=authopwd, width=15, state='normal', show="*")
            e4.place(x=330, y=100)

        Button(pop, text="Modify OPC-UA", bg="red", fg="white", command=clearFields).place(x=245, y=140)
        Button(pop, text="Test Connection",  bg="green", fg="white", command=testConnPLC).place(x=350, y=140)
        Button(pop, text="Save OPC-UA Details & Exit", command=savePLCconfig).place(x=295, y=175)

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
        Label(pop, text='Sole Author: Robert B. Labs').place(x=140, y=120)
        Label(pop, text='Copyright (C) 2023-2025 Group Industrialisation, United Kingdom.').place(x=30, y=180)
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
            netTX = sq.testNetworkConn([server_IP], 1)
            # if ICMP ping response is allowed on the server
            if netTX:
                hostConnect()       # acknowledgement
                conn = 'true'
            else:
                pingError()         # Ping error failed -------
                conn = 'none'

        except Exception as err:
            errorLog(f"{err}")
            errorNoServer()         # errorNoServer()
            conn = 'none'

        return conn

    def testConnPLC():
        import Test_PING as sq

        agent = 0
        server_IP = hostIPv4.get()  # PLC Server IP

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
        global stpd, pWON, pID, OeeID, hostConn

        # ------------------------------[ Check valid number of attached Monitors]
        # myMon = m.get_monitors()                    # Automatically detect attached monitors
        # print('\nAttached Monitors:', len(myMon))

        if process.entrycget(0, 'state') == 'disabled' or process.entrycget(1, 'state') == 'disabled':
            print('\nSelection Condition met...')
            # import signal
            # os.kill(sid, signal.SIGTERM)
            # Cascade View Date String Search ------------------------[]
            if (process.entrycget(0, 'state') == 'disabled'
                    and process.entrycget(1, 'state') == 'normal'
                    and process.entrycget(3, 'state') == 'normal'):

                # ----- Calling essential functions -----------[]
                process.entryconfig(0, state='disabled')                     # turn command off
                analysis.entryconfig(0, state='normal')
                analysis.entryconfig(1, state='normal')
                analysis.entryconfig(3, state='normal')

                # ------- Indicate Record Date or WON ---------[TODO...]
                sDate1, sDate2, uWON = searchBox()                                  # Popup dialogue
                print('\nCascade Date String - Between:', sDate1, 'and:', sDate2, 'WON_#:', uWON)
                # ---------------------------------------------[2]
                if sDate1 == '?' and sDate2 == '?' and uWON == '?':
                    print('Search Aborted!')
                    process.entryconfig(0, state='normal')
                else:
                    print('Attempting connection with SQL Server...')
                    cMode = 2
                    pType.append(cMode)

                    # Connect to SQL Server -----------------------[]
                    oeeValid, organicID, cType, nTables = wo.srcTable(sDate1, sDate2, uWON)     # Query record [pType=DnV/MGM]
                    print('\nSearch Return:', oeeValid, organicID, nTables)
                    # ---------------------------------------------[]
                    if organicID != 'G' and aSCR >= 4 and pRecipe == 'DNV' and nTables >=18:
                        print('\nSelecting Cascade View....')
                        tabbed_cascadeMode(cMode, cType)                        # Cascade View

                    elif organicID != 'G' and aSCR >= 8 and pRecipe == 'MGM' and nTables <= 30:
                        print('\nSelecting Cascade View....')
                        tabbed_cascadeMode(cMode, cType)                        # Cascade View

                    elif organicID != 'G' and aSCR >= 1 or aSCR <= 4:
                        print('\nSorry, multiple Screen display is required for Cascade View!')
                        print('Attached Monitor(s):', aSCR)
                        print('Switching back to Tabbed View...')
                        tabbed_canvas(cMode, cType)                             # Tabbed View
                    else:
                        process.entryconfig(0, state='normal')
                        print('Invalid post processing data or Production record not found..')

            # Tabbed View Date String Search -------------------------------[]
            elif (process.entrycget(1, 'state') == 'disabled'
                  and process.entrycget(0, 'state') == 'normal'
                  and process.entrycget(3, 'state') == 'normal'):

                # ----- Calling essential functions ---------#
                process.entryconfig(1, state='disabled')
                analysis.entryconfig(0, state='normal')
                analysis.entryconfig(1, state='normal')
                analysis.entryconfig(3, state='normal')

                # ------- Indicate Record Date or WON ---------[]
                sDate1, sDate2, uWON = searchBox()                                   # Search for Production data
                print('Tabbed Date String - Between:', sDate1, '&', sDate2, ':WON_# -', uWON)

                if sDate1 == '?' and sDate2 == '?' and uWON == '?':
                    print('Search Aborted!')
                    process.entryconfig(1, state='normal')
                else:
                    print('\nAttempting connection with SQL Server...')
                    cMode = 2
                    pType.append(cMode)

                    # connect SQL Server and obtain Process ID ----#
                    oeeValid, organicID, cType, nTables = wo.srcTable(sDate1, sDate2, uWON)    # Query SQL record
                    print('\nSearch Return:', oeeValid, organicID, nTables)

                    # ---------------------------------------------[]
                    if organicID != 'G' and nTables >= 18 or nTables ==30:
                        print('\nSelecting Tabbed View....')
                        tabbed_canvas(cMode, cType)        # Tabbed View
                    else:
                        process.entryconfig(1, state='normal')
                        print('Invalid post processing data or Production record not found..')

            else:
                runtimeChange()
                pMode = 0
                pType.append(pMode)
                print('Invalid SQL Query connection...')

        else:
            print('Invalid selection. Please, enable a visualisation mode')

        return


    def realTimePlay():
        # Declare global variable available to all processes
        global stpd, pWON, pID, OeeID, hostConn

        # ------------------------------[ Check valid number of attached Monitors]
        import screeninfo as m
        # myMon = m.get_monitors()            # Automatically detect attached monitors
        # print('Attached Monitors:', len(myMon))

        if analysis.entrycget(0, 'state') == 'disabled' or analysis.entrycget(1, 'state') == 'disabled':
            print('\nSelection A Condition met....')
            # import dataRepository as sqld

            # Test condition for CASCADE VIEW -----------------#
            if (analysis.entrycget(0, 'state') == 'disabled'
                    and analysis.entrycget(1, 'state') == 'normal'
                    and analysis.entrycget(3, 'state') == 'normal'):

                # ----- Calling essential functions -----------[]
                analysis.entryconfig(0, state='disabled')
                process.entryconfig(0, state='normal')
                process.entryconfig(1, state='normal')
                process.entryconfig(3, state='normal')

                cMode = 1
                pType.append(cMode)
                print('\nSelecting Cascade View....')

                if aSCR >= 4 and pRecipe == 'DNV':
                    print('\nSelecting Cascade View....')
                    if sysrdy or sysRun or sysidl:
                        tabbed_cascadeMode(cMode, pRecipe)                  # Cascade View
                    else:
                        print('\nSorry, condition for live visualisation not met..')
                        pass

                elif aSCR >= 8 and pRecipe == 'MGM':
                    print('\nSelecting Cascade View....')
                    if sysrdy or sysRun or sysidl:
                        tabbed_cascadeMode(cMode, pRecipe)                  # Cascade View
                    else:
                        print('\nSorry, condition for live visualisation not met..')
                        pass

                elif aSCR >= 1 or aSCR <= 4:
                    print('\nSorry, multiple screen function is NOT available, attach 4 or 8 Monitors!')
                    print('Attached Monitors', aSCR)
                    print('Selecting Tabbed View....')
                    if sysrdy or sysRun or sysidl:
                        tabbed_canvas(cMode, pRecipe)                       # Tabbed View
                    else:
                        print('\nSorry, condition for live visualisation not met..' )
                        pass
                else:
                    print('Invalid post processing data or Production record not found..')

            # Test condition for TABBED VIEW -----------------#
            elif (analysis.entrycget(1, 'state') == 'disabled'
                  and analysis.entrycget(0, 'state') == 'normal'
                  and analysis.entrycget(3, 'state') == 'normal'):

                # ----- Calling essential functions ----------#
                analysis.entryconfig(1, state='disabled')
                process.entryconfig(0, state='normal')
                process.entryconfig(1, state='normal')
                process.entryconfig(3, state='normal')

                cMode = 1
                pType.append(cMode)
                print('\nSelecting Tabbed View....')
                if sysrdy or sysRun or sysidl:
                    tabbed_canvas(cMode, pRecipe)                         # Call tabbed canvas functions
                else:
                    print('\nSorry, condition for live visualisation not met..')
                    pass

            else:
                runtimeChange()
                pMode = 0
                pType.append(pMode)
        else:
            print('Invalid selection. Please, enable visualisation mode')

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

    def searchBox():       # Indicate DATE/WON Search for production data
        pop = Toplevel(root)
        pop.wm_attributes('-topmost', True)

        # center root window --------------
        pop.tk.eval(f'tk::PlaceWindow {pop._w} center')
        pop.withdraw()
        uWON = askstring(title="Search Records", prompt="By WON / (YYYY-MM-DD)", initialvalue="20240507", parent=root)

        # -----------------------############---------------------------[]
        validWON = 8

        # Test for null entry -------------
        if uWON is None or uWON == '':
            fmDATE, toDATE, uWON = '?', '?', '?'  # Date was not used
            print('Search was aborted by User action')

        # elif isinstance(uWON, str):                # Search data rec by date
        elif '\\' in uWON or '-' in uWON or '/' in uWON:

            # calculate the next boundary date
            print('SearchBox Production by date...')
            if '-' in uWON:
                # print('Dash found...')
                rangeD = uWON.split('-', 2)
                # print('DT1:', rangeD)

            elif '\\' in uWON:
                # print('Slash found...\\')
                rangeD = uWON.split('\\', 2)
                # print('DT2', rangeD)

            else:
                # print('Slash found.../')
                rangeD = uWON.split('/', 2)
                # print('DT3', rangeD)

            # ----------------------------------------------#
            begMO = int(rangeD[1])
            begDA = int(rangeD[2])                          # The current Month
            nextMnth = int(rangeD[1]) + 1                   # New Month interval
            nextDate = int(rangeD[2]) + 1                   # New date interval

            # treat calendar special cases ----------------[]
            if rangeD[1] == '02':                           # Find February Month (28)
                if nextDate > 28:                           # February
                    endMO = nextMnth                        # Spilling into next Month
                    endDA = nextDate - 28                   # keep current date
                else:
                    endMO = int(rangeD[1])                  # The current Day
                    endDA = nextDate                        # Current date + 1

            # -----------------------------------   # Jan, March, May, July, August, October, December
            elif (rangeD[1] == '01' or rangeD[1] == '03' or rangeD[1] == '05' or rangeD[1] == '07'
                        or rangeD[1] == '08' or rangeD[1] == '10' or rangeD[1] == '12'):
                # ------------------------------------------#
                if nextDate > 31:                           # end search interval
                   endMO = nextMnth                         # Spilling into next Month
                   endDA = nextDate - 31                    # keep current date
                else:
                    endMO = int(rangeD[1])                  # The current Day
                    endDA = nextDate                        # Current date + 1

            elif rangeD[1] == '04' or rangeD[1] == '06' or rangeD[1] == '09' or rangeD[1] == '11': #rangeD[2] == '30':                         # April, June, September, November

                if nextDate > 30:                           # Month and date search interval
                    endMO = nextMnth                        # Spilling into next Month
                    endDA = nextDate - 30                   # keep current date
                else:
                    endMO = int(rangeD[1])                  # The current Day
                    endDA = nextDate                        # Current date + 1
            else:
                # print('AM HERE 4')
                endMO = int(rangeD[1])                      # The current Day
                endDA = nextDate                            # Current date + 1

            # Convert to Work Order Number--- YYYY-MM-DD -----------
            fmDATE = rangeD[0] + '-' + str(begMO) + '-' + str(begDA)    # Date was used in search query
            toDATE = rangeD[0] + '-' + str(endMO) + '-' + str(endDA)    # Date was used in search query

            uWON = rangeD[0] + rangeD[1] + rangeD[2]
            # print('WON:', uWON)

        elif validWON == len(uWON):
            print('\nSearch by Work Order Number...')
            ret = 1
            stad = str(uWON)
            fmDATE, toDATE, uWON = '0', '0', stad        # Date was not used
            print('WON:', uWON)
        else:
            print('Search was aborted by Operator...')
            return

        return fmDATE, toDATE, uWON

    # -------------------------------- APP MENU PROCEDURE START ------------------------------------------------[]
    def viewTypeA():    # enforce selection integrity ------------------[Cascade Tabb View]
        global HeadA, rType                 # declare as global variables

        # # Define run Type -------------[]
        # if rType == 1:
        #     rType = 'Synchro'
        # elif rType == 2:
        #     rType = 'PostPro'
        # else:
        #     rType = 'Standby'
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
            retroPlay()                                                  # Call objective function

        elif process.entrycget(3, 'state') == 'disabled':    # If Closed Display state is disabled
            process.entryconfig(0, state='disabled')                # select and disable Cascade View command
            process.entryconfig(1, state='normal')                  # set tabb view command to normal
            process.entryconfig(3, state='normal')                  # set close display to normal

            # --- start parallel thread ----------------------------------#
            # cascadeViews()                                              # Critical Production Params
            retroPlay()                                                   # Call objective function
            # tabbed_cascadeMode()                                        # Default limited tabbed common screen + Casc
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
            retroPlay()                                                 # Call objective function
            # tabbed_cascadeMode()                                      # Provide limited Tabb and multiple screen
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
        # if rType == 1:
        #     rType = 'Synchro'
        # elif rType == 2:
        #     rType = 'PostPro'
        # else:
        #     rType = 'Standby'
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
            retroPlay()                                                   # Call objective function

        elif process.entrycget(3, 'state') == 'disabled':
            process.entryconfig(1, state='disabled')
            process.entryconfig(0, state='normal')
            process.entryconfig(3, state='normal')

            retroPlay()                                                     # Call objective function
            # tabbed_canvas()                                               # Tabbed Visualisation
            exit_bit.append(0)

            HeadA, HeadB, closeV = 0, 1, 0                                  # call embedded functions

        elif (process.entrycget(0, 'state') == 'normal'
                  and process.entrycget(1, 'state') == 'normal'
                  and process.entrycget(3, 'state') == 'normal'):
                process.entryconfig(1, state='disabled')
                process.entryconfig(0, state='normal')
                process.entryconfig(3, state='normal')

                retroPlay()                     # Call objective function
                # tabbed_canvas()               # Tabbed Visualisation
                exit_bit.append(0)
                HeadA, HeadB, closeV = 0, 1, 0

        else:
            process.entryconfig(1, state='normal')
            HeadA, HeadB, closeV = 0, 0, 1
            errorChoice()                                   # raise user exception
            print('Invalid! View selection before process parameter..')

        return HeadA, HeadB, closeV

# -----------------------------------------[ For Spalsh Control]
    def abortKey(key):
        # you can terminate the program with 'End' button ----
        if key == Key.end:
            print('\nTotal Number of Core-CPU#:', os.cpu_count())
            print('Killing Parent PID:', os.getppid())
            print('Killing Child PID:', os.getpid())
            print('SPC terminated by Local User...')
            # mySplash.withdraw()
            # lt.timer.cancel()
            os._exit(0)
            return True
# --------------------------------------------------------------------------------#
    def viewTypeC():
        global HeadA, rType  # declare as global variables

        # Define run Type -------------[]
        # if rType == 1:
        #     rType = 'Synchro'
        # elif rType == 2:
        #     rType = 'PostPro'
        # else:
        #     rType = 'Standby'
        # -----------------------------[]
        if analysis.entrycget(1, 'state') == 'disabled':  # If Tabbed View was in disabled state
            # if Tabbed view is active
            analysis.entryconfig(0, state='disabled')   # select cascade View becomes an option
            analysis.entryconfig(1, state='normal')     # set Tabb View to normal
            analysis.entryconfig(3, state='normal')     # set Close Display to normal

            if messagebox.askokcancel("Warning!!!", "Current Visualisation will be lost!"):
                tabb_clearOut()                                             # Clear out existing Tabbed View

                # --- start parallel thread --------------------------------#
                # call realtime method -----------[]
                if sysrdy or sysRun or sysidl:
                    dataReady.append(True)
                    realTimePlay()                                          # Call objective function (tabbed_cascade)
                else:
                    print('\nSorry, cannot initiate visualisation due to failed connection...')
                    errorSelection()  # raise user exception
                # ----------------------------------------------------------[]
                print('\nStarting new GPU thread...')
                exit_bit.append(1)

            else:
                analysis.entryconfig(1, state='disabled')   # revert to original state
                analysis.entryconfig(0, state='normal')     # revert to original state
            HeadA, HeadB, closeV = 1, 0, 0


        elif analysis.entrycget(3, 'state') == 'disabled':    # If Closed Display state is disabled
            analysis.entryconfig(0, state='disabled')               # select and disable Cascade View command
            analysis.entryconfig(1, state='normal')                 # set tabb view command to normal
            analysis.entryconfig(3, state='normal')                 # set close display to normal

            # --- start parallel thread ---------------------------------#
            # call realtime method -----------[]
            if sysrdy or sysRun or sysidl:
                dataReady.append(True)
                realTimePlay()                                           # Call objective function (tabbed_cascade)
            else:
                print('\nSorry, cannot initiate visualisation due to failed connection...')
                errorSelection()
                # ----------------------------------------------------------[]
            exit_bit.append(1)
            HeadA, HeadB, closeV = 1, 0, 0

        # ---------------- Fresh selection ------------------------------#
        elif (analysis.entrycget(0, 'state') == 'normal'
              and analysis.entrycget(1, 'state') == 'normal'
              and analysis.entrycget(3, 'state') == 'normal'):
            analysis.entryconfig(0, state='disabled')               # Disable selected command
            analysis.entryconfig(1, state='normal')                 # Keep command Enabled
            analysis.entryconfig(3, state='normal')                 # Keep command enabled
            # Prevent Post Production analysis Menu object
            process.entryconfig(0, state='normal')
            process.entryconfig(1, state='normal')
            process.entryconfig(3, state='normal')

            # --- start parallel thread ---------------------------------#
            # call realtime method -----------[]
            if sysrdy or sysRun or sysidl:
                dataReady.append(True)
                realTimePlay()                                           # Call objective function (tabbed_cascade)
            else:
                print('\nSorry, cannot initiate visualisation due to failed connection...')
                errorSelection()
                # ----------------------------------------------------------[]
            exit_bit.append(1)
            HeadA, HeadB, closeV = 1, 0, 0

        else:
            analysis.entryconfig(0, state='normal')
            HeadA, HeadB, closeV = 0, 0, 1
            errorChoice()                                               # pop up error
            print('Invalid! View selection before process parameter..')

        return HeadA, HeadB, closeV


    def viewTypeD():  # Tabbed View (This is configured for remote users)
        global HeadA, HeadB, closeV, rType
        # Define run Type -----------------------------------------[]
        # if rType == 1:
        #     rType = 'Synchro'
        # elif rType == 2:
        #     rType = 'PostPro'
        # else:
        #     rType = 'Standby'
        # ---------------------------------------------------------[]
        # enforce category selection integrity ---------------------#
        if analysis.entrycget(0, 'state') == 'disabled':
            analysis.entryconfig(1, state='disabled')
            analysis.entryconfig(0, state='normal')
            analysis.entryconfig(3, state='normal')

            if messagebox.askokcancel("Warning!!!", "Current Visualisation will be lost!"):
                casc_clearOut()                                     # clear out visualisation frame
                # tabbed_canvas()                                   # Call Canvas binding function

                # --- start parallel thread ------------------------#
                # call realtime method -----------[]
                if sysrdy or sysRun or sysidl:
                    dataReady.append(True)
                    realTimePlay()                                  # Call objective function (tabbed_cascade)
                else:
                    print('\nSorry, cannot initiate visualisation due to failed connection...')
                    errorSelection() # raise user exception
                # --------------------------------------------------[]
                exit_bit.append(0)                                  # Keep a byte into empty list

            else:
                analysis.entryconfig(0, state='disabled')     # revert to original state
                analysis.entryconfig(1, state='normal')       # revert to original state
            HeadA, HeadB, closeV = 0, 1, 0                          # call embedded functions

        elif analysis.entrycget(3, 'state') == 'disabled':
            analysis.entryconfig(1, state='disabled')
            analysis.entryconfig(0, state='normal')
            analysis.entryconfig(3, state='normal')

            # --- start parallel thread ---------------------------------#
            # call realtime method -----------[]
            if sysrdy or sysRun or sysidl:
                dataReady.append(True)
                realTimePlay()          # Call objective function (tabbed_cascade)
            else:
                print('\nSorry, cannot initiate visualisation due to failed connection...')
                errorSelection() # raise user exception
            # ----------------------------------------------------------[]
            exit_bit.append(0)
            HeadA, HeadB, closeV = 0, 1, 0  # call embedded functions

        elif (analysis.entrycget(0, 'state') == 'normal'
              and analysis.entrycget(1, 'state') == 'normal'
              and analysis.entrycget(3, 'state') == 'normal'):
            analysis.entryconfig(1, state='disabled')
            analysis.entryconfig(0, state='normal')
            analysis.entryconfig(3, state='normal')

            # --- start parallel thread ---------------------------------#
            # call realtime method -----------[]
            if sysrdy or sysRun or sysidl:
                dataReady.append(True)
                realTimePlay()              # Call objective function (tabbed_cascade)
            else:
                print('\nSorry, cannot initiate visualisation due to failed connection...')
                errorSelection()            # raise user exception
            # ----------------------------------------------------------[]
            exit_bit.append(0)
            HeadA, HeadB, closeV = 0, 1, 0

        else:
            analysis.entryconfig(1, state='normal')
            HeadA, HeadB, closeV = 0, 0, 1
            errorChoice()  # raise user exception
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
        if inUse == 4:
            root.winfo_children()[4].destroy()
            root.winfo_children()[3].destroy()
            root.winfo_children()[2].destroy()
            root.winfo_children()[1].destroy()
        else:
            pass #root.winfo_children()[1].destroy()
    # ------------------------------------------#
    def kill_process(pid):
        # SIGKILL = terminate the process forcefully | SIGINT = interrupt ( equivalent to CONTROL-C)
        os.kill(pid, signal.SIGTERM)
    # ------------------------------------------#

    def casc_clearOut():
        # killing active threads ---------
        inUse = len(root.winfo_children())
        # --------------------------------
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
            if pRecipe == 'DNV' and inUse > 1:
                kill_process(p3.pid)
                kill_process(p2.pid)
                kill_process(p1.pid)
            elif pRecipe == 'MGM' and inUse > 1:
                kill_process(p7.pid)  # convert process into pid number
                kill_process(p6.pid)
                kill_process(p5.pid)                                  # convert process into pid number
                kill_process(p4.pid)
                kill_process(p3.pid)
                kill_process(p2.pid)
                kill_process(p1.pid)
            else:
                print('\nNo active Process in force')
                pass

        except OSError:
            print(f'Process {p7} failed to terminate!')
            print(f'Process {p6} failed to terminate!')
            print(f'Process {p5} failed to terminate!')
            print(f'Process {p4} failed to terminate!')
            print(f'Process {p3} failed to terminate!')
            print(f'Process {p2} failed to terminate!')
            print(f'Process {p1} failed to terminate!')

        # clear out all children process --[]
        if pRecipe == 'DNV' and inUse > 1:
            root.winfo_children()[3].destroy()
            root.winfo_children()[2].destroy()
            root.winfo_children()[1].destroy()
        elif pRecipe == 'MGM' and inUse > 1:
            root.winfo_children()[7].destroy()
            root.winfo_children()[6].destroy()
            root.winfo_children()[5].destroy()
            root.winfo_children()[4].destroy()
            root.winfo_children()[3].destroy()
            root.winfo_children()[2].destroy()
            root.winfo_children()[1].destroy()
        else:
            pass

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
    if cMode == 2 or cMode == 3:
        inautoMode = 'normal'  # enable Synchronous and PostProd Menu if in AutoMod
    else:
        inautoMode = 'disabled'  # disable Synchronous and PostProd Menu if in AutoMode

    # ---------------------------------------------------------------[Menu GUI Canvas Begins Here]
    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    sub_menu = tk.Menu(menubar, tearoff=0)

    filemenu.add_cascade(label="Server Credentials", menu=sub_menu)
    sub_menu.add_command(label="SQL Connectivity", command=serverSQLConfig, accelerator="Ctrl+S")
    sub_menu.add_command(label="PLC Connectivity", command=serverPLCConfig, accelerator="Ctrl+P")

    filemenu.add_command(label="Statistical Process", command=newMetricsConfig, accelerator="Ctrl+L")

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

    analysis.add_command(label="Set Cascade View", state=inautoMode, command=viewTypeC)
    analysis.add_command(label="Set Tabbed View", state=inautoMode, command=viewTypeD)

    analysis.add_separator()
    analysis.add_command(label="Stop SPC Process", command=stopSPCrun)
    menubar.add_cascade(label="Synchronous Live Mode", menu=analysis)

    # Process Menu ----------------------------------------[]
    process = Menu(menubar, tearoff=0)

    process.add_command(label="Use Cascade View", state=inautoMode, command=viewTypeA)
    process.add_command(label="Use Tabbed View", state=inautoMode, command=viewTypeB)

    process.add_separator()
    process.add_command(label="Close Display", command=closeViews)
    menubar.add_cascade(label="PostProd Analysis", menu=process)

    # Help Menu ------------------------------------------------[]
    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Help Index", command=onlinehelp)
    helpmenu.add_command(label="About...", command=aboutSPC)
    menubar.add_cascade(label="SPC Help", menu=helpmenu)

    root.config(menu=menubar)
    # ----------------------------------------------------------------------[]
    canvasOn(1)  # Update canvas on when GUI is active
    # ----------------------------------------------------------------------[]

    # ##### ---This script provides logic for lunching SPC in auto mode ---####
    # capture closing events and activate snooze mode -------------[]
    root.protocol("WM_DELETE_WINDOW", callback)
    # auto-Activate relevant view ---------------------------------[]
    if cMode == 1:       # Process Call Procedure
        print('Automatic Process Call Procedure...\n')
        # sysRun, sysidl, sysrdy, msc_rt, cLyr, piPos, mStatus = wd.autoPausePlay()
        # cLayerN = cLyr          # default layer number
        pWON = WON
        # ------------------
        UsePLC_DBS = True
        UseSQL_DBS = True
        # ------------------

        if len(pWON) == 8:
            import qParamsHL_DNV as dnv
            print('processing DNV parameters...\n')
            pRecipe = 'DNV'

            # --------- based on Hardware Screen -----
            if 1 <= aSCR <= 3 and vMode == 2:                  # allow Tabbed visualisation
                viewTypeD()
            elif 4 <= aSCR <= 8 and vMode == 1:                # allow cascade view
                viewTypeC()
            else:
                pass

        elif len(pWON) >= 8:                            # allow cascade view on MGM
            import qParamsHL_MGM as mgm
            print('processing MGM parameters...\n')
            pRecipe = 'MGM'

            # ---------------------------------------
            if 1 <= aSCR <= 6 and vMode == 2:
                viewTypeD()
            elif 7 <= aSCR <= 10 and vMode == 1:
                viewTypeC()
            else:
                pass
        load_Stats_Params('DEFAULT')     # Load state Parameter (pParam_HL)

    elif cMode == 2:     # User GUI Call Procedure
        print('Loading GUI Semi-Automatic Procedure..')
        # ------------------
        UsePLC_DBS = True
        UseSQL_DBS = True
        # ------------------

        if WON != 0:
            pWON = WON
        else:
            today = date.today()
            pWON = today.strftime("%Y%m%d")

        if len(pWON) == 8:
            print('\nRequesting for DNV Procedure...')
        elif len(pWON) >= 8:
            print('\nRequesting for MGM Procedure...')
        else:
            print('Invalid command sequence')
            exit('Exiting...')
        # -----------------------------------
        mStatus = 'NA'
        piPos = 'N/A in offline mode.'
        cLayerN = 0  # assumed layer number
        msc_rt = 'Not available in offline mode, valid in live mode!'
        sysrdy = 'NA'
        sysidl = 'NA'
        sysRun = 'NA'
        load_Stats_Params(pWON)

    elif cMode == 3:     # uCalling == 3, Manual Call Procedure
        print('Operator launched Procedure commencing...')
        # ------------------
        UsePLC_DBS = False
        UseSQL_DBS = True
        # ------------------

        if WON != 0:
            pWON = WON
        else:
            today = date.today()
            pWON = today.strftime("%Y%m%d")
        # -----------------------------------
        if len(pWON) == 8:
            print('\nStarting DNV Operator Triggered Procedure...')
        elif len(pWON) >= 8:
            print('\nStarting MGM Operator Triggered Procedure...')
        else:
            print('Invalid command sequence detected, please try again..')
            exit('Exiting...')

        mStatus = 'NA'
        piPos = 'N/A in offline mode.'
        cLayerN = 0          # assumed layer number
        msc_rt = 'Not available in offline mode, valid in live mode!'
        sysrdy = 'NA'
        sysidl = 'NA'
        sysRun = 'NA'
        load_Stats_Params(pWON)

    else:
        print('Sorry, invalid process specified...')
        exit('Exiting')
    # ----- Load Statistical limits and Process details
    root.mainloop()


# uCalled: 1. PLC 2, SQL, 3. User  Triggered
# vMode: [1. Cascade, 2. Tab Views]
userMenu(3, '20250923', 2)
