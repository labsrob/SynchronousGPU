import time
from time import sleep, strftime
import tkinter as tk
from random import randint
from time import strftime
from tkinter import *
from PIL import ImageTk, Image      # Python Imaging Library
from datetime import datetime, date
from time import sleep
import threading
import snap7
import os
import psutil
from multiprocessing import Process
import CommsPlc as xp

splashInUse = False
user_url = "http://www.magmaglobal.com/synchronous_spc"
today = date.today()
# sysrdy, sysidl, sysRun = 0, 1, 0

# ------------ Launch-Screen Event Functional Control -------------[]
stup_messages = ["Evaluating ring-head combinations", "Checking SQL repository Hardware",
                 "Accessing selected parameters", "Checking SPC Constants and Metrics",
                 "Evaluating Sampling Resolution", "Testing High-Speed Connectivity",
                 'Downloading SPC initialization Files', 'Loading SPC Visualisation Model',
                 'Writing SPC values into .INI File...', 'Saving & Finalizing .INI Files']

error_handlers = ['M2M connection failed, re-trying...', 'Fatal Error!, SPC Process Exiting...',
                  "Connection now established!"]

# Ensure you update these parameters if anything changes in the SCADA  state machine codes ---------------------------
machineCode_Data = [40960, 40976, 40992, 41008, 41024, 41040, 41056, 41072, 41088, 41104, 43392, 43408, 45056, 45072,
					45088, 45104, 45120, 45136, 45152, 45168, 45184, 45200, 45312, 45328, 45344, 45360, 45376, 45392,
					45408, 45424, 45440, 45456, 45568, 45584, 45600, 45616, 45632, 45648, 45664, 45680, 45696, 45712,
					45824, 45840, 45856, 45872, 45888, 45904, 45920, 45936, 45952, 45968, 46080, 46096, 46112, 46128,
					46144, 46160, 46176, 46192, 46208, 46224, 46336, 46352, 46368, 46384, 46400, 46416, 46432, 46448,
					46464, 46480, 46592, 47488, 47504, 49152, 49168, 49184, 49200, 49216, 49232, 49248, 49264, 49280,
					49296, 49408, 49424, 49440, 49456, 49472, 49488, 49504, 49520, 49536, 49552, 49664, 49680, 49696,
					49712, 49728, 51584, 51600, 53248, 53264, 53280, 53296, 53312, 53328, 53344, 53360, 53376, 53392,
					53504, 53520, 53536, 53552, 53568, 53584, 53600, 53616, 53632, 53648, 53760, 53776, 53792, 53808,
					53824, 53840, 53856, 53872, 53888, 53904, 54016, 54032, 54048, 54064, 54080, 54096, 54112, 55680,
					55696, 57344, 57360, 57376, 57392, 57408, 57424, 57440, 57456, 57472, 57488, 57600, 57616, 57632,
					57648, 59776, 59792, 0]

smcDescription = ["No State or Undefined State ", "System health Check, please wait..", "Operator to confirm Production Mode.. ",
				 "Operator to select initial direction ", "Updating safety PLC...", "Confirm pipe load procedure completed. ",
				 "Commencing Pipe referencing procedure.. ", "Confirming valid pipe parameters..", "Loading Pipe Parameters … ",
				 "Initialisation of Pipe data…", "Startup procedure completed ", "Startup error state, please wait… ",
				 "No State or Undefined State ", "System health Check, please wait...", "Checking layer completion, please wait… ",
				 "Operator verifying Pipe diameter..", "Checking the target diameter for disparity ",
				 "Activating Pipe Parameter procedure ", "Confirming production mode", "Checking if Master Switchover is required ",
				 "Haul Off Master Switchover", "Checking if Pipe reversal is required..", "Operator confirming pipe reversal procedure ",
				 "Updating Position for Pipe Reversal..", "Position X Axis for reversal", "Position Y Axis for reversal ",
				 "Position Haul off for adjust reversal", "Activating Chucks System", "Position Encoder Axes for reversal ",
				 "Operator Enabling Clamp Tension..", "Enabler with Clamp Tension", "Preparing TLH clarance before reversal ",
				 "S Axis clearance before reversal", "Operator confirming Pipe Reversal Position", "Pipe is reversing, please wait.. ",
				 "Activating run per pass algorithm ", "Checking if Hafner Change is required ", "Confirming Hafner Change.. ",
				 "Accessing TLH clearance for Hafner change ", "Moving TLH angles for Hafner Change ", "Positioning Rings for Hafner Change ",
				 "Hafner Change completed ", "Check hafner change is successful", "Sorry, Hafner change is not successful ",
				 "Resetting Tape Counters", "Confirming adjustment to Pipe Position", "Adjusting Pipe to X Axis Position ",
				 "Adjusting Pipe to Y Axis Position", "Adjusting Haul off Pipe Position ", "Adjusting Encoder Axis to Pipe Position ",
				 "Adjusting Pipe Position Axes ", "Adjusting Polarised Camera to pipe Position", "Tape Laying Head Clearance for Angle Move ",
				 "Target Position TLH Angular Axes", "Pipe Position TLH Linear Axes", "Target Position TLH Axial Axes ",
				 "Extending Keyance Arms, please wait", "Resetting Tape Feed to Start Position", "Moving Laser Angle to Start position",
				 "System Check Recovery Pass", "Confirming Pipe Reference…", "Pipe Referencing Commencing", "Referencing tapeTracking Standard ",
				 "Commencing Camera Alignment", "Computing Tape Tracking Reference Positions", "Moving Tape Tracking to Reference Positions",
				 "Referencing Tape Tracking Recovery", "Tape Tracking Recovery Achieved", "Calculating Start Positions", "Moving to Start Position ",
				 "Moving Rings to Start Positions", "Tow Pipe Position to Y-Axes", "All Clear, Ready to Run...", "System is Ready to Run ",
				 "Pre-Check Error State detected", "No State or Undefined State..", "Awaiting HMI Acknowledgement", "Check Staggered Stopped Rings ",
				 "Retracting Shrinkage Encoders ", "Activating Tape System", "Checking Tape Presence", "Tape Missing Acknowledge ",
				 "Checking Auto Weld Mode ", "Feeding Tape under Rollers….", "Activating Rollers Active Position","Applying Masking Tape Procedure ",
				 "Activating Lasers… ", "Activating AutoWeld", "Start Up Sounder Activation", "Synchronising Axes ", "Starting TapeWind ",
				 "Soft Soft initiated without Laser", "Soft Soft initiated with Laser", "Detected Error or E-Stop Pressed on TapeWind ",
				 "Initial State Recovery Machine", "End of Tape Wind Procedure", "Resetting Tape Tracking Data", "Updating Tapes Applied ",
				 "Updating Recovery Pass Data", "Updating New Layer Count..", "Tape Running Now Completed", "Process Error State, please wait… ",
				 "No State or Undefined State", "Activating Shrinkage Encoders", "Acknowledging Stop Recovery", "Computing Recovery Method, Please Wait ",
				 "Checking Hafner Change is Required ", "Activating Hafner Replacement Procedure", "Preparing TLH clearance for Hafner Change ",
				 "Moving TLH angles for Hafner Change..", "Positioning Rings for Hafner Replacement", "Hafner Replacement Procedure Completed",
				 "Hafner Change Successful!", "Acknowledging Hafner Change Not successful..", "Resetting Tape Counters, Please wait… ",
				 "Checking Target position (TLH) Angular Axes ", "Checking Pipe position with TLH Linear Axes ", "Enabling Clamp Tension procedure ",
				 "Checking Rings after recovery", "Automatic clearance move, please wait..", "Obtaining shrinkage measurements.. ",
				 "Retracting Shrinkage Encoders", "Referencing Tape Tracking Shrinkage", "Calculating Recovery Track Position Shrinkage ",
				 "Moving to Tails Removal Position", "Activating Shrinkage Encoders after Tails Removal Move ", "Acknowledging Tails Removal Procedure",
				 "Activating Camera Alignment Recovery", "Calculate Tape Tracking Reference Position", "Moving to Tracking Reference Position ",
				 "Referencing Tape Tracking Camera", "Tape Tracking Recovery in Progress ", "Calculating Tape tracking Position ",
				 "Moving to Recovery Start Position ", "Activating Encoders After Recovery", "Feeding Tape to Start Position ",
				 "Moving Laser Angles to Start Position", "Further Recovery Acknowledge ", "Defining Recovery Method ", "System Recovery Completed ",
				 "Recovery Error State, please wait… ", "No State or Undefined State ", "Confirming Pipe Unload Procedure ",
				 "Moving Axes to Clearances ", "Preparing for Hafners Removal ", "Positioning Rings for Hafner Removal ",
				 "Confirming Hafner Removal Completed", "Checking if Hafner Removal is Successful", "Acknowledging Hafner Change Not successful..",
				 "Resetting Tape Counters ", "Retracting Keyance Arms ", "Retracking Shrinkage Encoders", "Commence with Releasing Pipe ",
				 "Conduction Health Checks, Please Wait ", "Starting Pipe Unloading Procedure", "End of Pipe Lay Completed ",
				 "EoP Error State, please wait…", "StandBy State, Call Engineers ..."]

# -------------------------------------------------------------------------------------[]
_plc = snap7.client.Client()	# Instantiate a PLC
# _Plc.set_session_password('Robb13!L')
TCP01_IP, RACK, SLOT = '192.168.100.100', 0, 1,
db_number, start_offset, bit_offset = 89, 0, 0

# disable Allow PUT/Get download HW info and enable again

try:
	print('Sorry cant connect now, try later..')
	pCon = _plc.connect(TCP01_IP, RACK, SLOT)
except Exception as e:
	print('PLC tracking error..')
	pCon = _plc.connect(TCP01_IP, RACK, SLOT)



# shared state
system_state = {
    "sysRun": False,
    "sysIdl": False,
    "sysRdy": False,
	"msctcp": '0',
    "won_NO": None
}

state_lock = threading.Lock()
stop_event = threading.Event()


# ---------------------------------OPC UA Details ---------------------------[Dr Labs, RB]
value, data = True, False  			# 1 = true | 0 = false
start_address = 0  					# starting address
r_length = 4  						# double word (4 Bytes = 32 bit value) / 9dp precision
r_length2 = 8						# Quadruple word (8 bytes = 64 bit value)/15dp precision
b_length = 1  						# boolean size = 1 Byte
r_data = 52.4
initialise = 0

con_plc = False
loadOnce = False
inProgress = False
timeA = time.time()  						# start timing the entire loop

# -------------------------------------------------------------------------------------[]

def check_PLC_Status():
	try:
		pCon.snap7.client.Client()
		pCon.connect(TCP01_IP, RACK, SLOT)
		conPlc = pCon.get_connected()

	except Exception as e:
		print('Failed to connect...')
		conPlc = False

	return conPlc


def readBool(db_number, start_offset, bit_offset):
	reading = pCon.db_read(db_number, start_offset, b_length)
	a = snap7.util.get_bool(reading, 0, bit_offset)
	print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
	return a


def readReal(db_number, start_offset, bit_offset):
	reading = pCon.db_read(db_number, start_offset, r_length)
	a = snap7.util.get_real(reading, 0)
	print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
	return a


def readLReal(db_number, start_offset, bit_offset):
	reading = pCon.db_read(db_number, start_offset, r_length2)
	a = snap7.util.get_real(reading, 0)
	print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
	return a


def readInteger(db_number, start_offset, bit_offset):
	reading = pCon.db_read(db_number, start_offset, r_length)
	a = snap7.util.get_int(reading, 0)
	print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
	return a


def readString(db_number, start_offset, bit_offset):
	r_length =  16 #4, 8, 16, 32, 64, 128, 256 (-2 Bytes)
	reading = pCon.db_read(db_number, start_offset, r_length)
	a = snap7.util.get_string(reading, 0)
	print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
	return a
# -----------------------------------------------------[]

def rt_autoPausePlay():
	"""
	NOTE: PLC real is represented in 4 bytes but the IEEE 754 encodes as binary32
	Datatype int in the PLC is represented in two bytes
	Datatype dword consists in 8 bytes in the PLC
	:return:
	"""
	print('\nChecking SMC readiness...')
	try:
		# sleep(3) # SPC_Automatic DB89
		sysRun = readBool(db_number, 0, 0)			# System Running
		sysIdl = readInteger(db_number, 0, 1)   		# System Idling
		sysRdy = readInteger(db_number, 0, 2)			# System Ready
		proWON = readString(db_number, 10, 0)
		cLayer = readInteger(db_number, 270,0)
		pipPos = readLReal(db_number, 442, 0)  	# Current pipe Position
		pipSpd = readLReal(db_number, 450, 0)
		pipLen = readLReal(db_number, 454, 0)
		sleep(0.1)

	except Exception as err:
		sysRun, sysIdl, sysRdy, proWON, cLayer, pipPos, pipSpd, pipLen = False, False, False, 0, 0, 0, 0, 0
		print(f"Exception Error: '{err}'")
		errorLog(f"{err}")
		print('Error loading autoplay..')

	return sysRun, sysIdl, sysRdy, proWON, cLayer, pipPos, pipSpd, pipLen


def eop_autoPausePlay():
	print('\nChecking SMC readiness...')
	try:
		sysRun = readBool(db_number, 0, 0)  # System Running
		sysIdl = readInteger(db_number, 0, 1)  # System Idling
		sysRdy = readInteger(db_number, 0, 2)  # System Ready
		proWON = readString(db_number, 10, 0)
		cLayer = readInteger(db_number, 270, 0)
		pipPos = readLReal(db_number, 442, 0)  # Current pipe Position
		pipSpd = readLReal(db_number, 450, 0)
		pipLen = readLReal(db_number, 454, 0)
		sleep(0.1)

	except Exception as err:
		sysRun, sysIdl, sysRdy, proWON, cLayer, pipPos, pipSpd, pipLen = False, False, False, 0, 0, 0, 0, 0
		print(f"Exception Error: '{err}'")
		errorLog(f"{err}")
		print('Error loading autoplay..')

	return sysRun, sysIdl, sysRdy, proWON, cLayer, pipPos, pipSpd, pipLen

# --------------------- Determine if Host is Online/Offline -----------------#

def checkSQL():
	import CommsSql as st
	# Brisk test connection to SQL Server to determin Online/Offline Status
	status = st.check_SQL_Status(2, 2)

	return status

def checkPLC():
	import CommsPlc as st
	# Brisk test connection to SQL Server to determine Online/Offline Status
	status = st.check_PLC_Status()
	# print('TP02', status)
	return status


def liveProductionRdy():
	# Take a peep into TCP01 activity ---------
	try:
		sysRun = readBool(db_number, 0, 0)  		# System is running
		sysIdl = readBool(db_number, 0, 1)  		# System idling
		sysRdy = readBool(db_number, 0, 2)  		# System Ready
		msctcp = readBool(db_number, 2, 0)  		# MSCTCP
		won_NO = readString(db_number, 4, 0)  	# Work Order Number

	except Exception as err:
		print(f"Exception Error: '{err}'")
		errorLog(f"{err}")
		sysRun = None
		sysIdl = False
		sysRdy = False
		msctcp, won_NO = 0, 0

	return sysRun, sysIdl, sysRdy, msctcp, won_NO



def watchDogController():
	global con_plc, sysRun, sysIdl, sysRdy, won_NO

	if not con_plc:
		conPlc = xp.connectM2M(1, 1)
		print('M2M Connection Established:', conPlc)
		con_plc = True

	# if connectPLC:
	print('\nChecking machine state at interval...')
	# -------------------------------------------------------
	sysRun = readBool(db_number, 0, 0)  	# System is runing
	sysIdl = readBool(db_number, 0, 1)  	# System idling
	sysRdy = readBool(db_number, 0, 2)  	# System Ready
	# ------------------------------------------------------
	msctcp = readInteger(db_number, 2, 0) # Machine State Code (msc)
	# -------------------------------------------------------
	tLayer = readInteger(db_number, 268, 0)  	# Total required Layer
	cLayer = readInteger(db_number, 270, 0)  	# Current achieved layer
	sleep(5)  # 5 seconds non-blocking interval

	rt_satus = dict(zip(machineCode_Data, smcDescription))
	msc_rt = rt_satus[msctcp]
	print('\nTCP01 Status:', msc_rt)

	return sysRun, sysIdl, sysRdy, tLayer, cLayer, msc_rt



# This is the THINK THANK common to all real-time procedures =================================================[]
def watchDog():
	# global sysRun, sysidl, sysrdy, rngONE, rngTWO, rngTHR, rngFOR, msctcp, won_NO, prodTA, prodTB, tLayer, cLayer

	"""
	Objective: Main controller to monitors and read PLC data block at intermittent
	and obtain TCP State machine code for processing
	msc_tcp - Machine State code from Simotion/PLC/Scada generated code
	"""
	# Turn off all splash and splash timer -------------------------[]
	print('\nWelcome to Watchdog Controller Module..')
	print('Number of Core-CPU#:', os.cpu_count())
	print('=' * 40)
	print('Watchdog Parent PID:', os.getppid())
	print('Watchdog Child PID:', os.getpid())

	# Activate WatchDog function-------------------------------------[]
	rtError = False
	inProgress = False
	# Obtain dynamic values -----------------------------------------[]
	while True:
		try:
			sleep(10)
			# Update status every 10 sec ----------------------------[]
			sysRun, sysIdl, sysRdy, rngONE, rngTWO, rngTHR, rngFOR, won_NO, prodTA, prodTB, tLayer, cLayer, msctcp, scadaT = watchDogController()
			# Initialise a Producer shared variables ---------------[]
			with state_lock:
				system_state["sysRun"] = sysRun
				system_state["sysIdl"] = sysIdl
				system_state["sysRdy"] = sysRdy
				system_state["won_NO"] = won_NO
				system_state["cLayer"] = cLayer

		except Exception as err:
			print(f"Exception Error: '{err}'")
			rtError = True
			errorLog(f"{err}")

		finally:
			print('\nWD: Updating Status...')
			if rtError:
				print('WD: Reset connection request...')
				rtError = False
				continue

# -----------------------------------------------------[]
def checkSQL():
	import CommsSql as st
	# Brisk test connection to SQL Server to determin Online/Offline Status
	status = st.check_SQL_Status(3, 5)

	return status

# Check Screen resolution -----------------------------[]
def updateSCRres():
    import win32api    # pywin32
    import win32con
    import pywintypes
    devmode = pywintypes.DEVMODEType()

    # Check compliance --------------------[]
    devmode.PelsWidth = 2560    # 1920, 1680
    devmode.PelsHeight = 1440   # 1080, 1050

    devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT
    win32api.ChangeDisplaySettings(devmode, 0)

# -----------------------------------------------------

def smc_status(rtc):			# Match MSC code with string description
	rt_satus = dict(zip(machineCode_Data, smcDescription))
	status_rt = rt_satus[rtc]
	if status_rt != 0:
		print(status_rt)
	else:
		pass
	return status_rt


def sendM2M_ACK():
    # Send acknowledgement by raising M2MConACK on SCADA Process and activate watchdog ---[]
    try:
        # Check if the Bit is @Low then raise High --------------------------[A]
        m2mgood = xp.readBool(db_number, start_offset[0], bit_offset[0])
        if not m2mgood:
            print('\nM2M connection acknowledged by SCADA...')
            xp.writeBool(db_number, start_offset[0], bit_offset[0], 1)
            m2mgood = True

            # Initiate a new thread / process -------------------------------[B]
            print('Obtaining and writing SPC metrics to .INI..')
            call_once = xp.spcMetricsModule()      # prevent multiple call for this procedure class
            call_once.saveMetric()                  # download metrics from scada & write values into .INI

    except KeyboardInterrupt as err:
        errorLog(err)

    return m2mgood


def errorLog(err):
    fileName = datetime.now().strftime('SPHLog '+"%Y-%m-%d")
    event = datetime.now().strftime("%Y-%m-%d %H:%M.%S")
    errorlogFile = str(fileName)
    f = open('.\\RuntimeLog\\'+errorlogFile+".txt", "a")
    f.write(event+' --- '+err+'\n')
    f.close()


# Window Exit Functions ---------------[]
def to_GUI(event=None):
	# ---------------------------------[]
	print('\nExiting to Operator GUI...')
	if mySplash and mySplash.winfo_exists():
		mySplash.destroy()
	import synchronousMain as rb
	print('Loading SPC GUI...\n')

	uCalling = 2        # User Auto Launched
	pWON = today.strftime("%Y%m%d")
	rt_p = 2	# vMode: [1. Cascade, 2. Tab Views]
	t4 = threading.Thread(target=rb.userMenu(uCalling, pWON, rt_p), name='UserTriggered', daemon=True)
	t4.start()  # Open visualisation canvas
	t4.join()

	return


def to_AutoProcess(event):
	print('\nSPC is auto-Triggered, Loading Statistical Interface...')
	if default_screen and default_screen.winfo_exists():
		default_screen.destroy()
	sysRun, sysIdl, sysRdy, msctcp, won_NO = liveProductionRdy()

	import synchronousMain as rb
	print(f'Loading SPC GUI on Word Order Number:# {won_NO} ...\n')
	if mySplash and mySplash.winfo_exists():
		mySplash.destroy()

	uCalling = 1
	pWON = won_NO
	rt_p = 2
	t3 = threading.Thread(target=rb.userMenu(uCalling, pWON, rt_p), name='OnlinePro', daemon=True)
	t3.start()			# Open visualisation canvas
	t3.join()

	return

def checkRes():
    global scrZ

    import ctypes
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    Width = user32.GetSystemMetrics(0)
    Height = user32.GetSystemMetrics(1)

    # -----------------------------------------------
    print('Current Screen Res:', Width, 'by', Height)
    # -----------------------------------------------

    if Width == 2560 and Height == 1440:
        print('Current Hardware resolution OK...')
        scrZ = '2k'

    elif Width > 2560 and Height > 1440:
        print('Current Hardware resolution is superb!')
        scrZ = '4k'

    else:
        print('\nScreen resolution?, Please wait...')
        scrZ = '1k'
        updateSCRres()
        print('Screen resolution updated successful!')
        print('Primary display not SPC Compliant..')

    return scrZ

# -----------------------------------------------------
def move_window():
	"""Show the moving splash screen."""
	global img, mySplash, root

	mySplash = tk.Toplevel(root)
	mySplash.overrideredirect(True)
	# Check screen resolution for SPC compliance & update res
	# ack_PLC = BooleanVar()
	print('\nChecking Viz-Screen Resolution...')
	scrRes = checkRes()
	if scrRes == '4k':
		w, h, f, xp1, xp2, yp = 1400, 800, 25, 500, 462, 570
	elif scrRes == '2k':
		w, h, f, xp1, xp2, yp = 780, 450, 14, 302, 285, 370  # 302
	else:
		w, h, f, xp1, xp2, yp = 500, 300, 12, 185, 168, 260

	# -----------------------------------------
	mySplash.overrideredirect(True)  # disable top bar
	# mySplash.wm_attributes("-transparentcolor", "gray99")

	init_str = StringVar()

	if not splashInUse:
		init_str.set('Initializing variables...')

		print('\nSPC standby mode...')
		mySplash.title('SPC Industrialization')
		screen_w = mySplash.winfo_screenwidth()
		screen_h = mySplash.winfo_screenheight()
		# -------------------------------------------

		x_c = int((screen_w / 2) - (w / 2))
		y_c = int((screen_h / 2) - (h / 2))
		print('Screen Size:', w, h, x_c, y_c)  # Screen Size: 425 250 1067 595
		mySplash.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))

		if scrRes == '4k':
			print('\nUsing 4k screen resolution...')
			img = ImageTk.PhotoImage(Image.open("820x267.png"))
			s_label = Label(mySplash, image=img, text="Welcome to Magma SPC", font=72)
			# --------------------------------------------------------------------------
			Label(mySplash, text="Synchronous Multivariate SPC", width=28, justify=CENTER, font=("NovaMono", 50)).place(
				x=150, y=300)
			Label(mySplash, text="Advanced Statistical Processing & Visualization System", justify=CENTER,
				  font=("NovaMono", 25)).place(x=300, y=380)
			Label(mySplash, text="Integrated into SCADA's (CF/PEEK) Manufacturing Process", justify=CENTER,
				  font=("NovaMono", 25)).place(x=255, y=420)
			Label(mySplash, text=user_url, font=("NovaMono", 20)).place(x=370, y=470)
			Label(mySplash, textvariable=init_str, width=30, justify=CENTER, font=("NovaMono", 25)).place(x=370,
																										  y=520)  #
			s_label.pack()

		elif scrRes == '2k':  # 2560 by 1440
			print('\nUsing 2k screen resolution...')
			img = ImageTk.PhotoImage(Image.open("291x180.png"))
			s_label = Label(mySplash, image=img, text="Welcome to Magma SPC", font=36)
			# --------------------------------------------------------------------------
			Label(mySplash, text="Synchronous Multivariate SPC", width=28, justify=CENTER, font=("NovaMono", 30)).place(
				x=70, y=185)
			Label(mySplash, text="Advanced Statistical Processing & Visualization System", justify=CENTER,
				  font=("NovaMono", 14)).place(x=160, y=235)
			Label(mySplash, text="Integrated into SCADA's (CF/PEEK) Manufacturing Process", justify=CENTER,
				  font=("NovaMono", 14)).place(x=135, y=260)
			Label(mySplash, text=user_url, font=("NovaMono", 12)).place(x=240, y=290)
			Label(mySplash, textvariable=init_str, width=30, justify=CENTER, font=("NovaMono", 14)).place(x=230,
																										  y=340)  #
			s_label.pack()

		else:
			print('\nUsing VGA screen resolution...')
			img = ImageTk.PhotoImage(Image.open("200x120.png"))
			s_label = Label(mySplash, image=img, text="Welcome to Magma SPC", font=12)
			# --------------------------------------------------------------------------
			Label(mySplash, text="Synchronous Multivariate SPC", width=28, justify=CENTER, font=("NovaMono", 18)).place(
				x=60, y=125)
			Label(mySplash, text="Advanced Statistical Processing & Visualization System", justify=CENTER,
				  font=("NovaMono", 12)).place(x=65, y=155)
			Label(mySplash, text="Integrated into SCADA's (CF/PEEK) Manufacturing Process", justify=CENTER,
				  font=("NovaMono", 12)).place(x=50, y=180)
			Label(mySplash, text=user_url, font=("NovaMono", 10)).place(x=120, y=200)
			Label(mySplash, textvariable=init_str, width=30, justify=CENTER, font=("NovaMono", 10)).place(x=140,
																										  y=240)  #
			s_label.pack()
		mySplash.update()

		r = 10
		for n in range(r):
			sleep(.2)
			if n <= (r - 2):
				init_str.set(f"performing system health checks..{'.' * n}".ljust(27))
				with state_lock:
					sysRun = system_state["sysRun"]
					sysIdl = system_state["sysIdl"]
					sysRdy = system_state["sysRdy"]

				if sysRdy:
					print('\nChecking M2M connectivity...')
					sendM2M_ACK()

				elif sysIdl or sysRdy:
					print('Test DB Server readiness...')
					init_str.set(f"testing SQL Server connectivity...{'.' * n}".ljust(27))
					connectDB = checkSQL()
					if connectDB:
						print('Database Server is Up and running')
					else:
						init_str.set(f"SQL data repository maybe offline...'{'.' * n}".ljust(27))
					sleep(.5)
					print('\nStream 2:', connectDB)

				else:
					print('\nCould not establish connectivity with host...')
					pass
			else:
				init_str.set(f"testing PLC M2M connectivity...{'.' * n}".ljust(27))
				# sleep(.5)
				# recall M2M connection again ----------- 1st time try

				if sysRdy:
					print('\nPLC connectivity successfully established!')
					sendM2M_ACK()
				else:
					print('\nCould not establish connectivity with host..')
					pass
				mySplash.update_idletasks()

			sleep(.5)
			mySplash.update_idletasks()
			sleep(.5)

		for n in range(r):
			sleep(.2)
			init_str.set(f"interfacing with SQL repository...{'.' * n}".ljust(27))
			mySplash.update_idletasks()

		for n in range(r):
			sleep(.5)
			init_str.set("system initialization completed".ljust(27))
			sleep(.5)
			if sysRun or sysRdy:
				init_str.set("Welcome to Synchronous SPC!".ljust(27))
			elif sysIdl or sysRdy:
				init_str.set("SPC Process is in Standby mode!".ljust(27))
			elif not sysRun and not sysIdl and not sysRdy:
				print('\nTP50', sysRun, sysIdl, sysRdy)
				init_str.set("SPC subsystem is Offline! [PPA Ready]".ljust(27))
			else:
				init_str.set("SPC subsystem cannot be determined!".ljust(27))
			mySplash.update_idletasks()

		if sysRdy or sysRdy:
			Label(mySplash, text="SPC in Realtime Mode", justify=CENTER, font=("NovaMono", f)).place(x=xp1, y=yp)
		elif sysIdl or sysRdy:
			Label(mySplash, text="SPC in Standby Mode", justify=CENTER, font=("NovaMono", f)).place(x=xp1, y=yp)
		elif not sysRun and not sysIdl and not sysRdy:
			Label(mySplash, text="Check:PLC⚠|SQL✅", justify=CENTER, font=("NovaMono", f)).place(x=xp2, y=yp)
		else:
			Label(mySplash, text="Checking:PLC⚠|SQL⚠", justify=CENTER, font=("NovaMono", f)).place(x=xp2, y=yp)
		sleep(.5)

	# Move window every 2 seconds
	def random_move():
		# global won_NO

		if not mySplash.winfo_exists():
			return  # avoid invalid command name
		# ------------------------- Exit strategy ---------[]
		mySplash.bind("<Motion>", to_GUI)  # To GUI Menu
		with state_lock:
			sysRun = system_state["sysRun"]
			sysIdl = system_state["sysIdl"]
			sysRdy = system_state["sysRdy"]

		if sysRun or sysRdy:
			to_AutoProcess(event=None)
		mySplash.config(cursor="none")
		# -------------------------------------------------[]

		x, y = randint(10, 1000), randint(10, 1000)
		mySplash.geometry(f"{w}x{h}+{int(randint(10, 1900))}+{int(randint(10, 1000))}")
		mySplash.after(2000, random_move)


	random_move()
	# Auto-switch to default screen after 30 seconds
	mySplash.after(30000, to_default)


# -----------------------------------------------------#
# DEFAULT SCREEN MODE
# -----------------------------------------------------#
def to_default(event=None):
    global mySplash

    """Destroy splash and show the default clock screen."""
    if mySplash and mySplash.winfo_exists():
        mySplash.destroy()

    show_default_screen()


def show_default_screen():
	"""Display full-screen clock."""
	global default_screen, owner, clock_time, clock_date

	default_screen = tk.Toplevel(root)
	default_screen.overrideredirect(True)
	default_screen.config(bg="black")

	sw, sh = default_screen.winfo_screenwidth(), default_screen.winfo_screenheight()
	frame = tk.Frame(default_screen, bg="black", width=sw, height=sh)
	frame.pack(fill="both", expand=True)

	owner = tk.StringVar(value="Magma Global SPC")
	tk.Label(frame, textvariable=owner, fg="#808080", bg="black", font=("NovaMono", 60)).place(x=sw / 2, y=sh / 2 - 140, anchor="center")
	clock_time = tk.StringVar()
	tk.Label(frame, textvariable=clock_time, fg="#808080", bg="black", font=("NovaMono", 150)).place(x=sw / 2, y=sh / 2 + 30, anchor="center")
	clock_date = tk.StringVar()
	tk.Label(frame, textvariable=clock_date, fg="#808080", bg="black", font=("Bahnschrift", 30)).place(x=sw / 2, y=sh / 2 + 180, anchor="center")
	with state_lock:
		sysRun = system_state["sysRun"]
		sysRdy = system_state["sysRdy"]

	print('\nTP20', sysRun, sysRdy)
	try:
		if sysRun or sysRdy:
			to_AutoProcess(event=None)
		else:
			pass
	except Exception as e:
		print('Error in transition..')

	# Bindings to go back to splash
	default_screen.bind("<Escape>", to_splash)
	default_screen.bind("<Motion>", to_splash)
	update_clock()


def update_clock():
	"""Refresh clock display every second."""
	if not default_screen.winfo_exists():
		return
	clock_time.set(strftime("%H:%M:%S"))
	clock_date.set(strftime("%A, %e %B"))
	sysRun, sysIdl, sysRdy, msctcp, won_NO = liveProductionRdy()
	print('\nTP30', sysRun, sysRdy)
	if sysRun or sysRdy:
		to_AutoProcess(event=None)

	default_screen.after(1000, update_clock)


def to_splash(event=None):
	"""Switch back to splash mode."""
	if default_screen and default_screen.winfo_exists():
		default_screen.destroy()

	# obtain realtime Work Order for live mode
	with state_lock:
		sysRun = system_state["sysRun"]
		sysRdy = system_state["sysRdy"]
		sysIdl = system_state["sysIdl"]
	# --------------- Exit strategy ---------[]
	print('\nTP10', sysRun, sysRdy)
	if sysRun or sysRdy:
		to_AutoProcess(event=None)
	move_window()


# -----------------------------------------------------
# MAIN SPC STARTUP SESSION
# -----------------------------------------------------
def startSession():
	global root

	root = tk.Tk()
	root.withdraw()  # hide root window

	show_default_screen()

	root.mainloop()

