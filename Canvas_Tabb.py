# NEW TEST SCRIPT Showing the importance of Tabbed visualisation
# --------------------------------------------------------------

# The code for changing pages was derived from: http://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# License: http://creativecommons.org/licenses/by-sa/3.0/
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
LARGE_FONT = ("Verdana", 12)
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import loadSPCConfig as ty
import time
from datetime import datetime
import os
from pydub import AudioSegment

RetroReplay = True
HeadA, HeadB, vTFM = 0, 0, 0
# ----------------------- Audible alert --------------------------------------------------[]
impath ='C:\\CuttingEdge\\BETA_ver3.0\\Media\\'
nudge = AudioSegment.from_wav(impath+'tada.wav')
error = AudioSegment.from_wav(impath+'error.wav')

# Define statistical operations ----------------------------------------------------------[]
WeldQualityProcess = True
paused = False

url = 'http://www.magmaglobal.com'
localArray = []

# XBar Constants ------------------------------[]
A3 = [0.975, 0.789, 0.680, 0.6327, 0.606, 0.5525]       # 10, 15, 20, 23, 25, 30  sample sizes respectively
B3 = [0.284, 0.428, 0.510, 0.5452, 0.565, 0.6044]       # 10, 15, 20, 23, 25, 30  sample sizes respectively
B4 = [1.716, 1.572, 1.490, 1.4548, 1.435, 1.3956]       # 10, 15, 20, 23, 25, 30
processWON = []
# ------------- Dummy values ------
pPos = '6.2345'
layer = '03'
eSMC = 'Status: Tape laying process in progress...'
# from pylab import *

(sd, fd, gpz, gps, uhl, usm, qmz, xuca, xlca, xma, suca, slca, sma, d_ma, xucb, xlcb, xmb, sucb, slcb, smb,
 d_mb, xucc, xlcc, xmc, succ, slcc, smc, d_mc, xucd, xlcd, xmd, sucd, slcd, smd, d_md, a_s_p, pTagA, xucf,
 xlcf, xmf, sucf, slcf, smf, d_mf,  pTagB, xucg, xlcg, xmg, sucg, slcg, smg, d_mg) = ty.load_configSPC('configSPCError.ini')

smp_Sz = int(gpz)       # Allow SCADA User to specify window sample size
stp_Sz = int(gps)                   # Step Size
if stp_Sz == 1:                     # Domino group, single step slide
    type = 'Domino Group'
elif stp_Sz == 2:                   # Discrete group, discrete group slide
    type = 'Discrete Group'
else:
    print('Invalid group choice:', stp_Sz)
print('\nSample Size:', smp_Sz, 'Group Type:', type)

if uhl:
    hUCLa = xuca        # Upper Control Limit (UCL)
    hLCLa = xlca        # Lower Control Limit (LCL)
    hUCLb = xucb        # Upper Control Limit (UCL)
    hLCLb = xlcb        # Lower Control Limit (LCL)
    hUCLc = xucc        # Upper Control Limit (UCL)
    hLCLc = xlcc        # Lower Control Limit (LCL)
    hUCLd = xucd        # Upper Control Limit (UCL)
    hLCLd = xlcd        # Lower Control Limit (LCL)
    hUCLf = xucf        # Upper Control Limit (UCL)
    hLCLf = xlcf        # Lower Control Limit (LCL)
    hUCLg = xucg        # Upper Control Limit (UCL)
    hLCLg = xlcg        # Lower Control Limit (LCL)

    hMeanA = xma        # Sample Size group Mean of Xbar plot
    hMeanB = xmb
    hMeanC = xmc
    hMeanD = xmd
    hMeanF = xmf
    hMeanG = xmg

    hDevA = sma         # Sample size Group Mean of Sbar Plot
    hDevB = smb
    hDevC = smc
    hDevD = smd
    hDevF = smf
    hDevG = smg

    # Derive the XBar USLs -----------------------
    hUSLa = hMeanA + (hUCLa - hMeanA) / 3 * 6  # Upper Specification Limit (USL= 6 sigma above the mean)
    hUSLb = hMeanB + (hUCLb - hMeanB) / 3 * 6
    hUSLc = hMeanC + (hUCLc - hMeanC) / 3 * 6
    hUSLd = hMeanD + (hUCLd - hMeanD) / 3 * 6
    hUSLf = hMeanF + (hUCLf - hMeanF) / 3 * 6
    hUSLg = hMeanG + (hUCLg - hMeanG) / 3 * 6
    # Derived units for S-Chart -------------------
    hLSLa = hMeanA - (hMeanA - hLCLa) / 3 * 6  # Lower Specification Limit (LSL = 6 sigma below the mean)
    hLSLb = hMeanB - (hMeanB - hLCLb) / 3 * 6
    hLSLc = hMeanC - (hMeanC - hLCLc) / 3 * 6
    hLSLd = hMeanD - (hMeanD - hLCLd) / 3 * 6
    hLSLf = hMeanF - (hMeanF - hLCLf) / 3 * 6
    hLSLg = hMeanG - (hMeanG - hLCLg) / 3 * 6

    # Set distribution types ------
    dist_RF = d_ma
    dist_TT = d_mb
    dist_ST = d_mc
    dist_TG = d_md
    dist_LP = d_mf
    dist_LA = d_mg

    # S-Plot Upper / Lower Control Limits
    dUCLa = suca
    dLCLa = slca
    dUCLb = sucb
    dLCLb = slcb
    dUCLc = succ
    dLCLc = slcc
    dUCLd = sucd
    dLCLd = slcd
    dUCLd = sucd
    dLCLd = slcd
    dUCLf = sucf
    dLCLg = slcg

    PPerf = '$Pp_{k' + str(smp_Sz) + '}$'  # Using estimated or historical Mean
    plabel = 'Pp'
    # print('\nFixed XBar Mean:', hMeanA)
else:
    # Process performance label when using computed/automatic group Mean
    hUCL, hLCL, hUSL, hLSL, dUCL, dLCL = 0, 0, 0, 0, 0, 0
    PPerf = '$Cp_{k' + str(smp_Sz) + '}$'  # Using Automatic group Mean
    plabel = 'Cp'
    print('Current Limits:', hUCL, hLCL, round(hUSL, 3), round(hLSL, 3), dUCL, dLCL)

# --------------------------------------------------------------------------------------------------------------[]

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
        # root.destroy()
        localArray.clear()      # clear array held for GUI

    return

def menuExit():
    print('\nExiting Local GUI, bye for now...')
    # root.quit()
    os._exit(0)


# -------------------------------------------------------------------------------------------------------------[A1]
# def colletive_canvas():
#     # Collective canvas for visualisation of all 6 Process parameter
#     # Call main function using matplotlib ----------------------[A]
#     collective_model(root)


class common_process(ttk.Frame):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.createWidgets()

    def createWidgets(self):
        label = ttk.Label(self, text="Statistical Live-Evaluation: Production Parameters", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        f = Figure(figsize=(25, 4), dpi=100)
        f.subplots_adjust(left=0.029, bottom=0.088, right=0.99, top=0.9, wspace=0.193)
        a1 = f.add_subplot(1, 5, (1, 2))
        a2 = f.add_subplot(1, 5, (3, 4))
        a3 = f.add_subplot(1, 5, 5)

        # --------------------------------------------------------------[]
        a1.set_title('Laser Power [Control Plot]', fontsize=12, fontweight='bold')
        a2.set_title('Laser Angle [Control Plot]', fontsize=12, fontweight='bold')
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        # a1.legend(loc='upper left')
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")

        # Define limits for Laser Power Control Plots ----------------------#
        a1.axhline(y=hMeanF, color="green", linestyle="-", linewidth=1)
        a1.axhspan(hLCLf, hUCLf, facecolor='#A9EF91', edgecolor='#A9EF91')          # Light Green
        # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
        a1.axhspan(hUCLf, hUSLf, facecolor='#8d8794', edgecolor='#8d8794')          # grey area
        a1.axhspan(hLSLf, hLCLf, facecolor='#8d8794', edgecolor='#8d8794')          # grey area
        # clean up when Mean line changes ---
        a1.axhspan(hUSLf, hUSLf+10, facecolor='#FFFFFF', edgecolor='#FFFFFF')
        a1.axhspan(hLSLf-10, hLSLf, facecolor='#FFFFFF', edgecolor='#FFFFFF')

        # Define limits for Laser Angle Control Plots -----------------------#
        a2.axhline(y=hMeanG, color="green", linestyle="-", linewidth=1)
        a2.axhspan(hLCLg, hUCLg, facecolor='#A9EF91', edgecolor='#A9EF91')          # Light Green
        # Sigma 6 line (99.997% deviation) ------- times 6 above the mean value
        a2.axhspan(hUCLg, hUSLg, facecolor='#8d8794', edgecolor='#8d8794')          # grey area
        a2.axhspan(hLSLg, hLCLg, facecolor='#8d8794', edgecolor='#8d8794')          # grey area
        # clean up when Mean line changes ----------------------------------#
        a2.axhspan(hUSLg, hUSLg+0.005, facecolor='#FFFFFF', edgecolor='#FFFFFF')
        a2.axhspan(hLSLg-0.05, hLSLg, facecolor='#FFFFFF', edgecolor='#FFFFFF')

        # Model data --------------------------------------------------[]
        a1.plot([1857, 848, 1984, 529, 1740, 1136, 1012, 723, 1791, 600])
        a2.plot([-1.78, -1.0, -0.8, -1.3, -0.89, -0.92, -1.2, -1.5, -1.6, -0.85])
        # -------------------------------------------------------------[]
        a3.cla()
        a3.get_yaxis().set_visible(False)
        a3.get_xaxis().set_visible(False)
        if RetroReplay:
            a3.set_title('Machine Progressive Status', fontsize=12, fontweight='bold')
        else:
            a3.set_title('Machine Live Status Analysis', fontsize=12, fontweight='bold')
        # Data from OEE --------------------------[]
        a3.pie([1, 7, 0, 5, 9, 6], shadow=True)
        # ----------------------------------------[]

        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(expand=True)

class rollerForce(ttk.Frame):
    """ This application calculates BMI and returns a value. """

    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        # self.grid()
        self.place(x=10, y=10)
        self.createWidgets()

    def createWidgets(self):
        # import matplotlib as plt

        label = ttk.Label(self, text="Synchronous Roller Force", font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Set subplot embedded properties ----------------------------------[]
        f = Figure(figsize=(25, 8), dpi=100)
        f.subplots_adjust(left=0.029, bottom=0.05, right=0.99, top=0.955, wspace=0.117, hspace=0.157)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 4, (1, 3))
        a2 = f.add_subplot(2, 4, (5, 7))
        a3 = f.add_subplot(2, 4, (4, 8))

        # Declare Plots attributes -----------------------------------------[]
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        # a1.legend(loc='upper left')
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")

        # Define limits for XB Plots ----------------------------------#
        a1.axhline(y=hMeanA, color="green", linestyle="-", linewidth=1)
        a1.axhline(y=hUCLa, color="blue", linestyle="--", linewidth=0.95)
        a1.axhline(y=hLCLa, color="blue", linestyle="--", linewidth=0.95)
        a1.axhline(y=hUSLa, color="red", linestyle="--", linewidth=0.99)
        a1.axhline(y=hLSLa, color="red", linestyle="--", linewidth=0.99)
        # Define limits for S Plots -----------------------------------#
        a2.axhline(y=hDevA, color="green", linestyle="-", linewidth=1)
        a2.axhline(y=dUCLa, color="blue", linestyle="-", linewidth=0.95)
        a2.axhline(y=dLCLa, color="blue", linestyle="-", linewidth=0.95)
        # Define dynamic annotation ------------------------------------#
        f.text(0.75, 0.79, 'UCL', size=12, color='purple')      # X Bar
        f.text(0.75, 0.64, 'LCL', size=12, color='purple')      # X Bar
        # ---
        f.text(0.75, 0.43, 'UCL', size=12, color='purple')      # S Bar
        f.text(0.75, 0.20, 'LCL', size=12, color='purple')      # S Bar

        # Model data --------------------------------------------------[]
        a1.plot([1, 2, 3, 4, 5, 6, 7, 8], [5, 6, 1, 3, 8, 9, 3, 5])
        a2.plot([1, 2, 3, 4, 5, 6, 7, 8], [4, 5, 6, 1, 3, 0, 4, 2])

        a3.cla()
        a3.get_yaxis().set_visible(False)
        a3.get_xaxis().set_visible(False)
        # Statistical Feed ----------------------------------------------[]
        a3.text(0.466, 0.945, 'RF Performance Feed', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        a3.add_patch(rect1)
        a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)---------------------
        a3.text(0.145, 0.804, plabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.658, '#Pp Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.650, 0.820, 'Ring ' + plabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        a3.text(0.145, 0.403, PPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring ' + PPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        # -------------------------------------
        a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ----- Pipe Position and SMC Status -----
        a3.text(0.080, 0.090, 'Pipe Position: ' + pPos + '    Processing Layer #' + layer, fontsize=12, ha='left',
                transform=a3.transAxes)
        a3.text(0.080, 0.036, 'SMC Status: ' + eSMC, fontsize=12, ha='left', transform=a3.transAxes)
        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True)

class tapeTemp(ttk.Frame):
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        label = ttk.Label(self, text="Synchronous Tape Temperature", font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Set subplot embedded properties ----------------------------------[]
        f = Figure(figsize=(25, 8), dpi=100)
        f.subplots_adjust(left=0.029, bottom=0.05, right=0.99, top=0.955, wspace=0.117, hspace=0.157)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 4, (1, 3))
        a2 = f.add_subplot(2, 4, (5, 7))
        a3 = f.add_subplot(2, 4, (4, 8))

        # Declare Plots attributes -----------------------------------------[]
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        # a1.legend(loc='upper left')
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        # Define limits for XB Plots ----------------------------------#
        a1.axhline(y=hMeanB, color="green", linestyle="-", linewidth=1)
        a1.axhline(y=hUCLb, color="blue", linestyle="--", linewidth=0.95)
        a1.axhline(y=hLCLb, color="blue", linestyle="--", linewidth=0.95)
        # a1.axhline(y=hUSLb, color="red", linestyle="--", linewidth=0.99)
        a1.axhline(y=hLSLb, color="red", linestyle="--", linewidth=0.99)
        # Define limits for S Plots -----------------------------------#
        a2.axhline(y=hDevB, color="green", linestyle="-", linewidth=1)
        a2.axhline(y=dUCLb, color="blue", linestyle="-", linewidth=0.95)
        a2.axhline(y=dLCLb, color="blue", linestyle="-", linewidth=0.95)
        # Define dynamic annotation ------------------------------------#
        f.text(0.75, 0.8, 'UCL', size=12, color='purple')
        f.text(0.75, 0.63, 'LCL', size=12, color='purple')
        # ---
        f.text(0.75, 0.43, 'UCL', size=12, color='purple')  # S Bar
        f.text(0.75, 0.20, 'LCL', size=12, color='purple')  # S Bar

        # Model data --------------------------------------------------[]
        a1.plot([1, 2, 3, 4, 5, 6, 7, 8], [5, 6, 1, 3, 8, 9, 3, 5])
        a2.plot([1, 2, 3, 4, 5, 6, 7, 8], [4, 5, 6, 1, 3, 0, 4, 2])

        a3.cla()
        a3.get_yaxis().set_visible(False)
        a3.get_xaxis().set_visible(False)
        # Statistical Feed ----------------------------------------------[]
        a3.text(0.466, 0.945, 'TT Performance Feed', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        a3.add_patch(rect1)
        a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)---------------------
        a3.text(0.145, 0.804, plabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.658, '#Pp Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.650, 0.820, 'Ring ' + plabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        a3.text(0.145, 0.403, PPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring ' + PPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        # -------------------------------------
        a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ----- Pipe Position and SMC Status -----
        a3.text(0.080, 0.090, 'Pipe Position: ' + pPos + '    Processing Layer #' + layer, fontsize=12, ha='left',
                transform=a3.transAxes)
        a3.text(0.080, 0.036, 'SMC Status: ' + eSMC, fontsize=12, ha='left', transform=a3.transAxes)
        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True)


class deltaTemp(ttk.Frame):
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        label = ttk.Label(self, text="Synchronous Delta Temperature", font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Set subplot embedded properties ----------------------------------[]
        f = Figure(figsize=(25, 8), dpi=100)
        f.subplots_adjust(left=0.029, bottom=0.05, right=0.99, top=0.955, wspace=0.117, hspace=0.157)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 4, (1, 3))
        a2 = f.add_subplot(2, 4, (5, 7))
        a3 = f.add_subplot(2, 4, (4, 8))

        # Declare Plots attributes -----------------------------------------[]
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        # a1.legend(loc='upper left')
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        # Define limits for XB Plots ----------------------------------#
        a1.axhline(y=hMeanC, color="green", linestyle="-", linewidth=1)
        a1.axhline(y=hUCLc, color="blue", linestyle="--", linewidth=0.95)
        a1.axhline(y=hLCLc, color="blue", linestyle="--", linewidth=0.95)
        a1.axhline(y=hUSLc, color="red", linestyle="--", linewidth=0.99)
        #a1.axhline(y=hLSLc, color="red", linestyle="--", linewidth=0.99)
        # Define limits for S Plots -----------------------------------#
        a2.axhline(y=hDevC, color="green", linestyle="-", linewidth=1)
        a2.axhline(y=dUCLc, color="blue", linestyle="-", linewidth=0.95)
        a2.axhline(y=dLCLc, color="blue", linestyle="-", linewidth=0.95)
        # Define dynamic annotation ------------------------------------#
        f.text(0.75, 0.8, 'UCL', size=12, color='purple')
        f.text(0.75, 0.63, 'LCL', size=12, color='purple')
        # ---
        f.text(0.75, 0.43, 'UCL', size=12, color='purple')  # S Bar
        f.text(0.75, 0.20, 'LCL', size=12, color='purple')  # S Bar

        # Model data --------------------------------------------------[]
        a1.plot([1, 2, 3, 4, 5, 6, 7, 8], [5, 6, 1, 3, 8, 9, 3, 5])
        a2.plot([1, 2, 3, 4, 5, 6, 7, 8], [4, 5, 6, 1, 3, 0, 4, 2])

        a3.cla()
        a3.get_yaxis().set_visible(False)
        a3.get_xaxis().set_visible(False)
        # Statistical Feed ----------------------------------------------[]
        a3.text(0.466, 0.945, 'DT Performance Feed', fontsize=16, fontweight='bold', ha='center', va='center',
                transform=a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        a3.add_patch(rect1)
        a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)---------------------
        a3.text(0.145, 0.804, plabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.658, '#Pp Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.650, 0.820, 'Ring ' + plabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        a3.text(0.145, 0.403, PPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring ' + PPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        # -------------------------------------
        a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ----- Pipe Position and SMC Status -----
        a3.text(0.080, 0.090, 'Pipe Position: ' + pPos + '    Processing Layer #' + layer, fontsize=12, ha='left',
                transform=a3.transAxes)
        a3.text(0.080, 0.036, 'SMC Status: ' + eSMC, fontsize=12, ha='left', transform=a3.transAxes)
        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True)


class tapeGap(ttk.Frame):
    """ Application to convert feet to meters or vice versa. """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.place(x=10, y=10)
        self.create_widgets()

    def create_widgets(self):
        """Create the widgets for the GUI"""
        label = ttk.Label(self, text="Synchronous Gap Measurements", font=LARGE_FONT)
        label.pack(padx=10, pady=5)

        # Set subplot embedded properties ----------------------------------[]
        f = Figure(figsize=(25, 8), dpi=100)
        f.subplots_adjust(left=0.029, bottom=0.05, right=0.99, top=0.955, wspace=0.117, hspace=0.157)
        # ---------------------------------[]
        a1 = f.add_subplot(2, 4, (1, 3))
        a2 = f.add_subplot(2, 4, (5, 7))
        a3 = f.add_subplot(2, 4, (4, 8))

        # Declare Plots attributes -----------------------------------------[]
        a1.grid(color="0.5", linestyle='-', linewidth=0.5)
        a2.grid(color="0.5", linestyle='-', linewidth=0.5)
        # a1.legend(loc='upper left')
        a1.set_ylabel("Sample Mean [ " + "$ \\bar{x}_{t} = \\frac{1}{n-1} * \\Sigma_{x_{i}} $ ]")
        a2.set_ylabel("Sample Deviation [ " + "$ \\sigma_{t} = \\frac{\\Sigma(x_{i} - \\bar{x})^2}{N-1}$ ]")
        # Define limits for XB Plots ----------------------------------#
        a1.axhline(y=hMeanD, color="green", linestyle="-", linewidth=1)
        a1.axhline(y=hUCLd, color="blue", linestyle="--", linewidth=0.95)
        a1.axhline(y=hLCLd, color="blue", linestyle="--", linewidth=0.95)
        #a1.axhline(y=hUSLd, color="red", linestyle="--", linewidth=0.99)
        #a1.axhline(y=hLSLd, color="red", linestyle="--", linewidth=0.99)
        # Define limits for S Plots -----------------------------------#
        a2.axhline(y=hDevD, color="green", linestyle="-", linewidth=1)
        a2.axhline(y=dUCLd, color="blue", linestyle="-", linewidth=0.95)
        a2.axhline(y=dLCLd, color="blue", linestyle="-", linewidth=0.95)
        # Define dynamic annotation ------------------------------------#
        f.text(0.75, 0.8, 'UCL', size=12, color='purple')
        f.text(0.75, 0.63, 'LCL', size=12, color='purple')
        # ---
        f.text(0.75, 0.43, 'UCL', size=12, color='purple')  # S Bar
        f.text(0.75, 0.20, 'LCL', size=12, color='purple')  # S Bar

        # Model data --------------------------------------------------[]
        a1.plot([1, 2, 3, 4, 5, 6, 7, 8], [5, 6, 1, 3, 8, 9, 3, 5])
        a2.plot([1, 2, 3, 4, 5, 6, 7, 8], [4, 5, 6, 1, 3, 0, 4, 2])

        a3.cla()
        a3.get_yaxis().set_visible(False)
        a3.get_xaxis().set_visible(False)
        # Statistical Feed ----------------------------------------------[]
        a3.text(0.466, 0.945, 'TG Performance Feed', fontsize=16, fontweight='bold', ha='center', va='center', transform=a3.transAxes)
        # class matplotlib.patches.Rectangle(xy, width, height, angle=0.0)
        rect1 = patches.Rectangle((0.076, 0.538), 0.5, 0.3, linewidth=1, edgecolor='g', facecolor='#ebb0e9')
        rect2 = patches.Rectangle((0.076, 0.138), 0.5, 0.3, linewidth=1, edgecolor='b', facecolor='#b0e9eb')
        a3.add_patch(rect1)
        a3.add_patch(rect2)
        # ------- Process Performance Pp (the spread)---------------------
        a3.text(0.145, 0.804, plabel, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.658, '#Pp Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.650, 0.820, 'Ring ' + plabel + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        a3.text(0.755, 0.745, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.685, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.625, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.565, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ------- Process Performance Ppk (Performance)---------------------
        a3.text(0.145, 0.403, PPerf, fontsize=12, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.328, 0.282, '#Ppk Value', fontsize=28, fontweight='bold', ha='center', transform=a3.transAxes)
        a3.text(0.640, 0.420, 'Ring ' + PPerf + ' Data', fontsize=14, ha='left', transform=a3.transAxes)
        # -------------------------------------
        a3.text(0.755, 0.360, '#Value1', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.300, '#Value2', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.240, '#Value3', fontsize=12, ha='center', transform=a3.transAxes)
        a3.text(0.755, 0.180, '#Value4', fontsize=12, ha='center', transform=a3.transAxes)
        # ----- Pipe Position and SMC Status -----
        a3.text(0.080, 0.090, 'Pipe Position: '+ pPos + '    Processing Layer #'+ layer, fontsize=12, ha='left', transform=a3.transAxes)
        a3.text(0.080, 0.036, 'SMC Status: '+ eSMC, fontsize=12, ha='left', transform=a3.transAxes)
        # -----Canvas update --------------------------------------------[]
        canvas = FigureCanvasTkAgg(f, self)
        canvas.get_tk_widget().pack(expand=False)
        # Activate Matplot tools ------------------[Uncomment to activate]
        # toolbar = NavigationToolbar2Tk(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(expand=True)

def clearFields():  # for SQL server credentials -------
    # clear the content of text entry box
    serip.set('')
    sqlid.set('')
    uname.set('')
    autho.set('')

    # set initial variables or last known variables
    Entry(pop, state='normal', textvariable=serip).place(x=86, y=60)
    Entry(pop, state='normal', textvariable=sqlid).place(x=86, y=100)
    Entry(pop, state='normal', textvariable=uname).place(x=330, y=60)
    Entry(pop, state='normal', textvariable=autho, show="*").place(x=330, y=100)

    sqlRO = True
    print('Read Only Field State:', sqlRO)
    return sqlRO

def errorNoServer():
    messagebox.showerror('dB Server', 'Server offline or No connection')
    return

def pingError():
    messagebox.showerror('OSI layer Error', 'Network Error or Server offline..')
    return

def errorChoice():
    messagebox.showerror('Warning', 'Select Parameter before View Type')
    return

def errorNote():
    messagebox.showerror('Error', 'Empty field(s)')
    return

def errorNoconnect():
    messagebox.showerror("SPC Server", "Invalid Request!")

def successNote():
    messagebox.showinfo('Saved', 'Config Saved')
    return

def errorConfig():
    messagebox.showerror("Configuration:", "Enable Statistic on Two Parameters")

def clearSQL():  # SPC start/run clear
    svar7.set(0)
    svar8.set(0)
    return

def clearConn():
    svar4.set(0)
    svar5.set(0)


def saveSQLconfig():
    import loadSQLConfig as to

    ct1 = serip.get()
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

def serverConfig():
    global pop, sqlRO, serip, sqlid, uname, autho, e4
    pop = Toplevel(root)
    pop.wm_attributes('-topmost', True)

    # Define and initialise essential popup variables -------------------------------------
    serip, sqlid, uname, autho = StringVar(pop), StringVar(pop), StringVar(pop), StringVar(pop)
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

    labl_0 = Label(pop, text="SQL Server Credentials", width=20, font=("bold", 14))
    labl_0.place(x=130, y=10)

    # creating labels and positioning them on the grid --------[]
    Label(pop, text='Server IP').place(x=10, y=60)
    Label(pop, text='Database').place(x=10, y=100)
    Label(pop, text="Access ID").place(x=250, y=60)
    Label(pop, text="Authorize").place(x=250, y=100)

    # set initial variables or last known variables
    serip.set('Server ID')
    sqlid.set('dBase Repository')
    uname.set('User Name')
    autho.set('Authorization Code')

    # creating entries and positioning them on the grid -----
    if not sqlRO:
        e1 = Entry(pop, textvariable=serip, state='readonly')
        e1.place(x=86, y=60)
        e2 = Entry(pop, textvariable=sqlid, state='readonly')
        e2.place(x=86, y=100)
        e3 = Entry(pop, textvariable=uname, state='readonly')
        e3.place(x=330, y=60)
        e4 = Entry(pop, textvariable=autho, state='readonly') #, show="*")
        e4.place(x=330, y=100)
    else:
        e1 = Entry(pop, textvariable=serip, state='normal')
        e1.place(x=86, y=60)
        e2 = Entry(pop, textvariable=sqlid, state='normal')
        e2.place(x=86, y=100)
        e3 = Entry(pop, textvariable=uname, state='normal')
        e3.place(x=330, y=60)
        e4 = Entry(pop, textvariable=autho, state='normal', show="*")
        e4.place(x=330, y=100)

    # Button(pop, text="Save Details", bg="green", fg="white", command=saveSQLconfig).place(x=130, y=160)
    Button(pop, text="Save Details", bg="green", fg="white", command=saveSQLconfig).place(x=160, y=160)
    Button(pop, text="Change Details", bg="red", fg="white", command=clearFields).place(x=258, y=160)
    return

# ---------------------------------
def sOpenConn():
    global conn
    import UtilsSQLServer as mCon
    import Test_PING as sq

    agent = 0
    server_IP = "10.0.3.172"  # Hardwired SPC Server ID. Modify if IP changes
    try:
        # Test server connection over TCP/IP ---------------------------
        netTX = sq.testNetworkConn([server_IP], 1)  # if ICMP ping response is allowed on the server.
        # print('\nPING-OK:', netTX)
        if netTX:
            conn = mCon.DAQ_connect(0, agent)  # 0 = connection is inactive set active()
            if conn == 'failed' or conn == '' and filemenu.entrycget(2, 'state') != 'normal':
                # print('Resetting the menu command...')
                filemenu.entryconfig(2, label="Connect SQL Server", state='normal')
        else:
            pingError()  # Ping error failed -------
            conn = 'none'
            if filemenu.entrycget(2, 'state') != 'normal':
                filemenu.entryconfig(2, label="Connect SQL Server", state='normal')

    except Exception as err:
        errorLog(f"{err}")
        errorNoServer()  # errorNoServer()
        # reset the menu command ---------
        filemenu.entryconfig(2, label="Connect SQL Server", state='normal')
        filemenu.entryconfig(3, label='Disconnect SQL Server', state='normal')
        conn = 'none'

    return conn

def sCloseConn():
    import UtilsSQLServer as mCon
    agent = 0
    if agent == 0:
        conn = mCon.DAQ_connect(1, agent)  # 1 = connection is active to be .closed()
    else:
        conn = 'none'
    return conn

def connSQL():
    clearConn()     # clear array
    clearSQL()
    if not svar7.get():
        filemenu.entryconfig(2, label="Connect SQL Server", state='normal')
        activeSQL = sOpenConn()  # call main function
        if activeSQL != 'none':
            filemenu.entryconfig(2, label="Connect SQL Server", state='disabled')
            filemenu.entryconfig(3, label='Disconnect SQL Server', state='normal')
        else:
            filemenu.entryconfig(2, label="Connect SQL Server", state='normal')
            filemenu.entryconfig(3, label='Disconnect SQL Server', state='normal')

    return

def discSQL():
    # clearConn()     # clear array
    clearSQL()
    if not svar7.get():
        if filemenu.entrycget(2, 'state') == 'normal':
            # in assumption of an active connection
            connect = False
            errorNoconnect()
            print('\nNo active connection found..')
        else:
            connect = True
            sCloseConn()
            print('Server connection now closed!')
            filemenu.entryconfig(3, label='Disconnect SQL Server', state='disabled')
            filemenu.entryconfig(2, label="Connect SQL Server", state='normal')

    return connect

def vclicked():
    if not svar4.get():
        filemenu.entryconfig(5, label='Using PLC Query', state='disabled')
        sqlfmt = 1
        filemenu.entryconfig(6, label='Use SQL Query', state='normal')
        print("Menu enabled: PLC Query")
    return sqlfmt

def tclicked():
    if not svar4.get():
        filemenu.entryconfig(6, label='Using SQL Query', state='disabled')
        sqlfmt = 0
        filemenu.entryconfig(5, label='Use PLC Query', state='normal')
        print("Menu enabled: SQL Query")
    return sqlfmt

# function to allow historical limits entry--------------------------------------------------------------[]
def klr():
    global e7, e8

    # Do a toggle from Historical limits checkbutton to enforce one choice --------[]
    if hLmt.get():
        optm1.set(0)
    else:
        optm1.set(1)
        hLmt.set(0)

    # Function performs dynamic calculations ---[]
    def calculation(event=None):
        global xBarMa, xBarMb, xBarMc, xBarMd, xBarMe, xBarMf, xBarMg, sBarMa, sBarMb, sBarMc, sBarMd, sBarMe,\
        sBarMf, sBarMg, sUCLa, sUCLb, sUCLc, sUCLd, sUCLe, sUCLf, sUCLg, sLCLa, sLCLb, sLCLc, sLCLd, sLCLe, sLCLf,\
         sLCLg

        try:
            # Compute XBar mean / center line ----------------------[RF]
            if xUCLa.get() and xLCLa.get():
                xBarMa = float(xLCLa.get()) + ((float(xUCLa.get()) - float(xLCLa.get())) / 2)
                sUCLa, sLCLa, sBarMa = checkhistDev(float(xUCLa.get()), xBarMa, gSize1.get()) # Compute S-Chart Mean
                print('Roller Pressure  : XBar Mean', xBarMa)
                # Display values on user screen mat -----------[1]
                val1A["text"] = round(xBarMa, 3)
                val2A["text"] = round(sBarMa, 3)
            # ------------------------------------------------------[TT]
            if xUCLb.get() and xLCLb.get():
                xBarMb = float(xLCLb.get()) + ((float(xUCLb.get()) - float(xLCLb.get())) / 2)
                sUCLb, sLCLb, sBarMb = checkhistDev(float(xUCLb.get()), xBarMb, gSize1.get()) # Compute S-Chart Mean
                print('Tape Temperature : XBar Mean', xBarMb)
                # Display values on user screen mat -----------[2]
                val3A["text"] = round(xBarMb, 3)
                val4A["text"] = round(sBarMb, 3)
            # ------------------------------------------------------[ST]
            if xUCLc.get() and xLCLc.get():
                xBarMc = float(xLCLc.get()) + ((float(xUCLc.get()) - float(xLCLc.get())) / 2)
                sUCLc, sLCLc, sBarMc = checkhistDev(float(xUCLc.get()), xBarMc, gSize1.get())  # Compute S-Chart Mean
                print('Substrate Temperature: XBar Mean', xBarMc)
                # Display values on user screen mat -----------[3]
                val5A["text"] = round(xBarMc, 3)
                val6A["text"] = round(sBarMc, 3)
            # ------------------------------------------------------[TG]
            if xUCLd.get() and xLCLd.get():
                xBarMd = float(xLCLd.get()) + ((float(xUCLd.get()) - float(xLCLd.get())) / 2)
                sUCLd, sLCLd, sBarMd = checkhistDev(float(xUCLd.get()), xBarMd, gSize1.get())
                print('Tape Gap : XBar Mean', xBarMd)
                # sBarM = sLCL + (sUCL - sLCL) / 2 : Can be derived with this also.
                # Display values on user screen mat -----------[4]
                val7A["text"] = round(xBarMd, 3)
                val8A["text"] = round(sBarMd, 3)
            # --------------------------------------------[ Production Monitor Parameter][Laser Power]

            if xUCLf.get() and xLCLf.get():
                xBarMf = float(xLCLf.get()) + ((float(xUCLf.get()) - float(xLCLf.get())) / 2)
                sUCLf, sLCLf, sBarMf = checkhistDev(float(xUCLf.get()), xBarMf, gSize1.get())
                print(newLabelA +': XBar Mean', xBarMf)
                 # sBarM = sLCL + (sUCL - sLCL) / 2 : Can be derived with this also.
                # Display values on user screen mat -----------[5]
                val11A["text"] = round(xBarMf, 3)
                val12A["text"] = round(sBarMf, 3)
            # --------------------------------------------[ Production Monitor Parameter][Laser Angle]
            if xUCLg.get() and xLCLg.get():
                xBarMg = float(xLCLg.get()) + ((float(xUCLg.get()) - float(xLCLg.get())) / 2)
                sUCLg, sLCLg, sBarMg = checkhistDev(float(xUCLg.get()), xBarMg, gSize1.get())
                print(newLabelB + ': XBar Mean', xBarMg)
                # sBarM = sLCL + (sUCL - sLCL) / 2 : Can be derived with this also.
                # Display values on user screen mat -----------[6]
                val13A["text"] = round(xBarMg, 3)
                val14A["text"] = round(sBarMg, 3)

        except ValueError:
            val1A["text"] = "Entry not permitted, float numbers only"
            val2A["text"] = "Entry not Permitted, float numbers only"

            val3A["text"] = "Entry not permitted, float numbers only"
            val4A["text"] = "Entry not Permitted, float numbers only"

            val5A["text"] = "Entry not permitted, float numbers only"
            val6A["text"] = "Entry not Permitted, float numbers only"

            val7A["text"] = "Entry not permitted, float numbers only"
            val8A["text"] = "Entry not Permitted, float numbers only"

            val11A["text"] = "Entry not permitted, float numbers only"
            val12A["text"] = "Entry not Permitted, float numbers only"

            val13A["text"] = "Entry not permitted, float numbers only"
            val14A["text"] = "Entry not Permitted, float numbers only"

    # clear the content and allow entry of historical limits -------
    gSize1.set('20')
    gSize2.set('2')

    xUCLa.set('')
    xLCLa.set('')
   #  XBarMa.set('Auto')
    SBarMa.set('Auto')

    # ----- DNV --
    xUCLb.set('')
    xLCLb.set('')
    # XBarMe.set('Auto')
    SBarMb.set('Auto')
    # ------------------
    xUCLc.set('')
    xLCLc.set('')
    # XBarMf.set('Auto')
    SBarMc.set('Auto')
    # ------------------
    xUCLd.set('')
    xLCLd.set('')
    # XBarMb.set('Auto')
    SBarMd.set('Auto')
    # ----------------- [Omit E]
    # Codefying the parameter here ------
    xUCLf.set('')       # Laser Power/ HO Tension
    xLCLf.set('')
    # XBarMd.set('Auto')
    SBarMf.set('Auto')
    # ---------------- # Laser Angle / Dancer Load / Dancer Displacement
    xUCLg.set('')
    xLCLg.set('')
    # XBarMd.set('Auto')
    SBarMg.set('Auto')
    # ---------------- # HO Tension

    # -----------------------------------------------------------------------------------------
    e7 = ttk.Combobox(pop, width=8, values=[" Select", "10", "15", "20", "23", "25", "30"], state="normal")
    e7.bind("<<ComboboxSelected>>", display_sel)
    e7.current(0)               # set default choice
    e7.place(x=40, y=50)
    # single step slide [SS-Domino] or Group step slide [GS - Discrete]
    e8 = ttk.Combobox(pop, width=10, values=["SS-Domino", "GS-Discrete"], state="normal")
    e8.bind("<<ComboboxSelected>>", display_selection)
    e8.current(0)               # set default choice to first index
    e8.place(x=172, y=50)

    # -----------[Compute stats UCL/LCL] -----------[ Roller Force]
    val1 = Entry(pop, width=8, state='normal', textvariable=xUCLa)
    val1.place(x=65, y=110)
    val2 = Entry(pop, width=8, state='normal', textvariable=xLCLa)
    val2.place(x=190, y=110)
    # -----------------------------------------[ Tape Temperature ]
    val3 = Entry(pop, width=8, state='normal', textvariable=xUCLb)
    val3.place(x=65, y=140)
    val4 = Entry(pop, width=8, state='normal', textvariable=xLCLb)
    val4.place(x=190, y=140)
    # --------------------------------------[ SubstrateTemperature]
    val5 = Entry(pop, width=8, state='normal', textvariable=xUCLc)
    val5.place(x=65, y=170)
    val6 = Entry(pop, width=8, state='normal', textvariable=xLCLc)
    val6.place(x=190, y=170)
    # -------------------------------------[ Tape Gap Measurement]
    val7 = Entry(pop, width=8, state='normal', textvariable=xUCLd)
    val7.place(x=65, y=200)
    val8 = Entry(pop, width=8, state='normal', textvariable=xLCLd)
    val8.place(x=190, y=200)
    # --------------------------------------------- [Laser Power]
    val11 = Entry(pop, width=8, state='normal', textvariable=xUCLf)
    val11.place(x=65, y=290)
    val12 = Entry(pop, width=8, state='normal', textvariable=xLCLf)
    val12.place(x=190, y=290)
    # ---------------------------------------------- [Laser Angle]
    val13 = Entry(pop, width=8, state='normal', textvariable=xUCLg)
    val13.place(x=65, y=320)
    val14 = Entry(pop, width=8, state='normal', textvariable=xLCLg)
    val14.place(x=190, y=320)

    # ---------------------------------------------------------------------#
    # Compute derived mean values for XBar/Sbar Plot & fill dynamically ----
    val1A = Label(pop, width=8, state='normal', font=("bold", 10))
    val1A.place(x=325, y=110)
    val2A = Label(pop, width=8, state='normal', font=("bold", 10))
    val2A.place(x=447, y=110)
    # --------------------
    val3A = Label(pop, width=8, state='normal', font=("bold", 10))
    val3A.place(x=325, y=140)
    val4A = Label(pop, width=8, state='normal', font=("bold", 10))
    val4A.place(x=447, y=140)
    # ------------------------
    val5A = Label(pop, width=8, state='normal', font=("bold", 10))
    val5A.place(x=325, y=170)
    val6A = Label(pop, width=8, state='normal', font=("bold", 10))
    val6A.place(x=447, y=170)
    # ------------------------
    val7A = Label(pop, width=8, state='normal', font=("bold", 10))
    val7A.place(x=325, y=200)
    val8A = Label(pop, width=8, state='normal', font=("bold", 10))
    val8A.place(x=447, y=200)
    # -----------------------
    val11A = Label(pop, width=8, state='normal', font=("bold", 10))
    val11A.place(x=325, y=290)
    val12A = Label(pop, width=8, state='normal', font=("bold", 10))
    val12A.place(x=447, y=290)
    # -----------------------
    val13A = Label(pop, width=8, state='normal', font=("bold", 10))
    val13A.place(x=325, y=320)
    val14A = Label(pop, width=8, state='normal', font=("bold", 10))
    val14A.place(x=447, y=320)

    # ------------------ Binding properties -----------------------
    val1.bind("<KeyRelease>", calculation)
    val2.bind("<KeyRelease>", calculation)
    # -----
    val3.bind("<KeyRelease>", calculation)
    val4.bind("<KeyRelease>", calculation)
    # -----
    val5.bind("<KeyRelease>", calculation)
    val6.bind("<KeyRelease>", calculation)
    # ----- DNV --------------#
    val7.bind("<KeyRelease>", calculation)
    val8.bind("<KeyRelease>", calculation)
    # -------
    val11.bind("<KeyRelease>", calculation)
    val12.bind("<KeyRelease>", calculation)
    # -------
    val13.bind("<KeyRelease>", calculation)
    val14.bind("<KeyRelease>", calculation)

    # repopulate with default values
    metRO = True
    print('SQL Field State:', metRO)    # metric fields set to read only

    return metRO
    # -------------------------------------

def metricsConfig():
    global pop, metRO, xUCLa, xLCLa, xUCLb, xLCLb, xUCLc, xLCLc, sSta, sEnd, lPwr, lAng, eStat, optm1, optm2, e8,\
        xUCLd, xLCLd, XBarMa, SBarMa, XBarMb, SBarMb, XBarMc, SBarMc, XBarMd, SBarMd, hLmt, gSize1, gSize2, e7,\
        xUCLf, xLCLf, xUCLg, xLCLg, BarMf, SBarMf, BarMg, SBarMg, hoTens, dcLoad, dDispl, swA, swB, seRF, sdRF, \
        seTT, sdTT, seST, sdST, seTG, sdTG, seLP, sdLP, seLA, sdLA

    # newLabel = '??'
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

# -------------------

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

    labl_0 = Label(pop, text="Real-Time SPC (BETA Edition 3.0)", font=("bold", 14))
    labl_0.place(x=60, y=30)

    # creating labels and positioning them on the grid --------[]
    Label(pop, text='Real-Time Statistical Process Control System').place(x=90, y=80)
    Label(pop, text='Built Ver: 7.10, Built on: June 2024').place(x=110, y=100)
    Label(pop, text='Author: Robert B. Labs').place(x=140, y=120)
    Label(pop, text='Copyright (C) 2023-2025 Magma Global Ltd, Portchester, England.').place(x=30, y=180)
   # filewin = Toplevel(pop)

def onlinehelp():        # TODO configure menu item to functon
    import webbrowser
    webbrowser.open(url, new=1)
    return
# -------------------------------

def clearSPCrun():          # reset analysis menu partially
    if analysis.entrycget(2, 'onvalue') == 0:
        print('\nAm here C1....', analysis.entrycget(2, 'onvalue'))
        analysis.entryconfig(2, state='normal', onvalue=1)
        print('Am here C2....', analysis.entrycget(2, 'onvalue'))

    elif analysis.entrycget(2, 'onvalue') == 1:
        print('Am here C3....', analysis.entrycget(2, 'onvalue'))
        analysis.entryconfig(2, state='normal', onvalue=0)
        print('Am here C4....', analysis.entrycget(2, 'onvalue'))

    elif analysis.entrycget(3, 'onvalue') == 0:
        print('\nAm here C5....', analysis.entrycget(3, 'onvalue'))
        analysis.entryconfig(3, state='normal', onvalue=1)
        print('Am here C6....', analysis.entrycget(3, 'onvalue'))

    elif analysis.entrycget(3, 'onvalue') == 1:
        print('Am here C7....', analysis.entrycget(3, 'onvalue'))
        analysis.entryconfig(3, state='normal', onvalue=0)
        print('Am here C8....', analysis.entrycget(3, 'onvalue'))


def clear():
    svar2.set(0)
    svar3.set(0)

    return svar2, svar3

# One of the challenging object to configure both checkbox and state --------[]
def retroPlay():
    # import os
    # import signal
    # os.kill(sid, signal.SIGTERM)

    clear()     # clear array
    if analysis.entrycget(2, 'state') == 'normal':
        if analysis.entrycget(2, 'onvalue') == 0:
            print('Am here A1....', analysis.entrycget(2, 'onvalue'))
            analysis.entryconfig(2, state='disabled', onvalue=0)
            print('Am here A2....', analysis.entrycget(2, 'onvalue'))
        else:
            # print('Am here A3....', analysis.entrycget(2, 'onvalue'))
            analysis.entryconfig(2, state='disabled', onvalue=1)
            # print('Am here A4....', analysis.entrycget(2, 'onvalue'))

    elif analysis.entrycget(3, 'state') == 'disabled':
        if analysis.entrycget(3, 'onvalue') == 0:
            print('Am here A5....', analysis.entrycget(3, 'onvalue'))
            analysis.entryconfig(3, state='normal', onvalue=1)
            print('Am here A6....', analysis.entrycget(3, 'onvalue'))
        else:
            print('Am here A7....', analysis.entrycget(3, 'onvalue'))
            analysis.entryconfig(3, state='normal', onvalue=0)
            print('Am here A8....', analysis.entrycget(3, 'onvalue'))

    dataref()

def realTimePlay():
    clear()     # clear array
    if analysis.entrycget(3, 'state') == 'normal':
        if analysis.entrycget(3, 'onvalue') == 0:
            print('Am here B1....', analysis.entrycget(3, 'onvalue'))
            analysis.entryconfig(3, state='disabled', onvalue=0)
            print('Am here B2....', analysis.entrycget(3, 'onvalue'))
        else:
            print('Am here B3....', analysis.entrycget(3, 'onvalue'))
            analysis.entryconfig(3, state='disabled', onvalue=1)
            print('Am here B4....', analysis.entrycget(3, 'onvalue'))

    elif analysis.entrycget(2, 'state') == 'disabled':
        if analysis.entrycget(2, 'onvalue') == 0:
            print('Am here B5....', analysis.entrycget(2, 'onvalue'))
            analysis.entryconfig(2, state='normal', onvalue=1)
            print('Am here B6....', analysis.entrycget(2, 'onvalue'))
        else:
            print('Am here B7....', analysis.entrycget(2, 'onvalue'))
            analysis.entryconfig(2, state='normal', onvalue=0)
            print('Am here B8....', analysis.entrycget(2, 'onvalue'))

    dataref()

def terminateVis():
    if messagebox.askokcancel("Stop", "Terminating Visualisation?"):
        import mPipeMain as exit
        exit.callback()

    def clearSPCrun():          # reset analysis menu partially
        if analysis.entrycget(2, 'onvalue') == 0:
            print('\nAm here C1....', analysis.entrycget(2, 'onvalue'))
            analysis.entryconfig(2, state='normal', onvalue=1)
            print('Am here C2....', analysis.entrycget(2, 'onvalue'))

        elif analysis.entrycget(2, 'onvalue') == 1:
            print('Am here C3....', analysis.entrycget(2, 'onvalue'))
            analysis.entryconfig(2, state='normal', onvalue=0)
            print('Am here C4....', analysis.entrycget(2, 'onvalue'))

        elif analysis.entrycget(3, 'onvalue') == 0:
            print('\nAm here C5....', analysis.entrycget(3, 'onvalue'))
            analysis.entryconfig(3, state='normal', onvalue=1)
            print('Am here C6....', analysis.entrycget(3, 'onvalue'))

        elif analysis.entrycget(3, 'onvalue') == 1:
            print('Am here C7....', analysis.entrycget(3, 'onvalue'))
            analysis.entryconfig(3, state='normal', onvalue=0)
            print('Am here C8....', analysis.entrycget(3, 'onvalue'))

def stopSPCrun():                   # reset analysis menu command
    clear()                         # clear array
    if analysis.entrycget(5, 'state') == 'normal':
        analysis.entryconfig(5, state='disabled')
        analysis.entryconfig(2, state='normal')
        analysis.entryconfig(3, state='normal')
        print('\nAm here B2, Menu 3', analysis.entrycget(5, 'state'))
    clearSPCrun()
    terminateVis()  # TODO - this should close existing SPC window

# Define volatile runtime variables -------------------[]

# ================================================================================================[]
def main(): # listener, plash
    global root, filemenu, analysis, sqlRO, metRO, root, HeadA, HeadB, vTFM

    # splash = plash
    # del splash  # Turn off Splash timer -----[]
    print('Timer Paused for GUI...')

    # inherit PID from Splash Screen and transfer back when Object closes
    print('\nUser Menu: Inherited PARENT ID#:', os.getppid())
    print('User Menu: Inherited CHILD ID#:', os.getpid())
    # print('User Menu: New Object THREAD:', get_native_id())
    # print('\nNew Object ID', sid)
    time.sleep(2)

    root = Tk()

    svar1 = IntVar()
    svar2 = tk.BooleanVar()  # retroplay
    svar3 = tk.BooleanVar()  # realtime play

    sqlRO = False  # SQL server filed is read only
    metRO = False
    # ----------------------------------------------------------[]
    # Create an instance of ttk style --------------------------[]
    s = ttk.Style()
    s.theme_use('default')   # Option: ('clam', 'alt', 'default', 'classic', 'My.TFrame')
    s.configure('TNotebook.Tab', background="green3")  # 'TFrame', 'TNotebook.Tab', 'new.TFrame', 'frameName'
    s.map("TNotebook", background=[("selected", "green3")])

    # FIXME ------------------------------------------------------------[]
    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Server Credentials", command=serverConfig, accelerator="Ctrl+S")
    filemenu.add_separator()
    filemenu.add_command(label="Connect SQL Server", command=connSQL, accelerator="Ctrl+C")
    filemenu.add_command(label="Disconnect SQL Server", command=discSQL, accelerator="Ctrl+Q")

    filemenu.add_separator()
    filemenu.add_command(label="Use PLC Query", command=vclicked)  # PLC DBlock
    filemenu.add_command(label="Use SQL Query", command=tclicked)

    mytext = filemenu.entrycget("Use PLC Query", 'state')

    filemenu.add_command(label="Close", command=callback)  # root.destroy via callback func
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=menuExit)
    menubar.add_cascade(label="Server Setup", menu=filemenu)

    # Process Menu ----------------------------------------[]
    process = Menu(menubar, tearoff=0)

    process.add_cascade(label='Define Process Data')  # , command=dnv_submenu)
    process.add_command(label="Visualisation Modes")  # , command=selectParamALL)
    process.add_separator()
    process.add_command(label="Samples' Properties", command=metricsConfig)
    menubar.add_cascade(label="Process Configuration", menu=process)

    # Analysis Menu -----------------------------------------[]
    analysis = Menu(menubar, tearoff=0)
    analysis.add_checkbutton(label="Post Production", variable=svar2, command=retroPlay)
    analysis.add_checkbutton(label="Synchronous SPC", variable=svar3, command=realTimePlay)

    analysis.add_separator()
    analysis.add_command(label="Stop SPC Process", command=stopSPCrun)
    menubar.add_cascade(label="SPC Runtime", menu=analysis)

    # Help Menu ------------------------------------------------[]
    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Help Index", command=onlinehelp)
    helpmenu.add_command(label="About...", command=aboutSPC)
    menubar.add_cascade(label="Help", menu=helpmenu)

    root.config(menu=menubar)
    # ----------------------------------------------------------------------[]
    canvasOn(1)  # Update canvas on when GUI is active
    # ----------------------------------------------------------------------[]

    # capture closing events and activate snooze mode -------------[]
    # root.protocol("WM_DELETE_WINDOW", callback)

    # FIXME ============================================================[]
    # Create common Parameter plot here -------------------------[]
    common_process(root)
    svar4 = tk.BooleanVar()
    svar5 = tk.BooleanVar()
    svar7 = tk.BooleanVar(root)
    svar8 = tk.BooleanVar(root)

    # # Set up embedding notebook (tabs) --------------------------[B]
    notebook = ttk.Notebook(root, width=2500, height=850)     # Declare Tab overall Screen size

    notebook.grid(column=0, row=0, padx=10, pady=450)           # Tab's spatial position on the Parent

    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)
    tab3 = ttk.Frame(notebook)
    tab4 = ttk.Frame(notebook)
    tab5 = ttk.Frame(notebook)

    notebook.add(tab1, text="Roller Pressure")
    notebook.add(tab2, text="Tape Temperature")
    notebook.add(tab3, text="Subs Temperature")
    notebook.add(tab4, text="Gap Measurements")
    notebook.add(tab5, text="Progressive Report")
    notebook.grid()

    # Create tab frames properties ------------[]
    app1 = rollerForce(master=tab1)
    app1.grid(column=0, row=0, padx=10, pady=10)

    app2 = tapeTemp(master=tab2)
    app2.grid(column=0, row=0, padx=10, pady=10)

    app3 = deltaTemp(master=tab3)
    app3.grid(column=0, row=0, padx=10, pady=10)

    app4 = tapeGap(master=tab4)
    app4.grid(column=0, row=0, padx=10, pady=10)

    app5 = tapeGap(master=tab5)
    app5.grid(column=0, row=0, padx=10, pady=10)
    # -------------------------- TODO ---------------------------------------------------------------#
    root.protocol("WM_DELETE_WINDOW", callback)

    root.mainloop()


main()