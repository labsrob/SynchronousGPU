# ------------------------------------------------------------------------
# Author: Dr RB Labs
# Developed for Magma Global - TechnipFMC Industrialization
# Email: robbielabs@uwl.ac.uk
# Copyright (C) 2023-2025, Robbie Labs
# ------------------------------------------------------------------------
import time
from time import sleep, strftime
from tkinter import *               # Load this Library first
from random import randint
from PIL import ImageTk, Image      # Python Imaging Library
from multiprocessing import Process
import threading
from threading import *
from datetime import datetime
from time import sleep
import os
import psutil
import CommsPlc as plc
# -------------------------------------
sysrdy, sysidle = 0, 1		# details for AutoProcess visualisation
running = True				# Default Snooze argument
# ----------------------------------- Watch Dog Control ------------------
# Ensure you update these parameters if anything changes in the SCADA  state machine codes ---------------------------
machineCode_Data = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 200, 201, 202, 203, 204, 205, 206, 207,
					208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227,
					228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247,
					248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 300, 301, 302, 303, 304, 305,
					306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325,
					400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419,
					420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 500,
					501, 502, 503, 504, 505, 506, 507, 262, 0, 326]

codeDescript = ["No state @ Startup Mode",
				"Checking the Axes are enabled and relevant",
				"Checking the Axes are enabled and are healthy",
				"Confirm the Pipe loaded successfully",
				"The reference Position of the Haul-off Master is set",
				"Load Pipe Parameters from Work Order",
				"Calculating new Pipe parameters",
				"Pipe variables are reset for New Pipe",
				"Startup State Machine complete",
				"Load Pipe Params",
				"Initialise Pipe Data",
				"Startup Complete",
				"Error State @ Startup Mode",
				"No state @ Ready Mode",
				"Checking the Axes are enabled and healthy",
				"Checking if the current Layer has been completed",
				"Confirm the Pipe Diameter has been entered",
				"Checking the New Pipe Diameter is within Tolerance",
				"Running the Pipe parameter Algorithm",
				"Checking if a Pipe reverse is required",
				"Confirm to rewind Pipe",
				"Updating Axes Target Positions for Pipe Reversal",
				"Check Pipe Reverse is required",
				"Operator confirms Reversal Sequences",
				"Update positions for Reversal",
				"Position C Axes for Reversal",
				"Position Y Axes for Reversal",
				"Position Haul Off adjust for reversal",
				"Activate Chuck Systems",
				"Position Encoder Axes for reversal",
				"Moving Keyence sensor Axes to clearance positions",
				"Follow enables with Clamp Tense",
				"THL Clearance before Reverse",
				"S Axis Clearance before...",
				"Operator Confirm Pipe Reverse Position",
				"Pipe reversing, please wait...",
				"Run Per Pass Algorithm",
				"Check Hafner change requirement",
				"Operator Select Hafner change",
				"THL Clearance for Hafner change",
				"THL Move Angles for Hafner change",
				"Position Rings for Hafner change",
				"Operator Confirm Hafner change completed",
				"Check Hafner change successful",
				"Operator Ack Hafner change unsuccessful",
				"Reset Tape Counters",
				"Operator confirms Adjustment to Pipe Position",
				"Pipe position C Axes",
				"Pipe position Y Axes",
				"Pipe position Haul off Adjust",
				"Pipe position encoder Axes",
				"Pipe position S Axes",
				"Polarised Cameras to Pipe Position",
				"THL Clearance for Angle Move",
				"Target Position THL Angular Axes",
				"Pipe Position THL Linear Axes",
				"Target Position THL Angular Axes",
				"Extend Keyence Arms",
				"Tape Feed To Start Position",
				"Laser Angle Top start position",
				"System check recovery Pass",
				"Operator Confirm Pipe Reference",
				"Pipe Referencing...",
				"Reference Tape Tracking Standard",
				"Operator Camera Alignment Recovery",
				"Calculate Tape Tracking reference recovery Pos",
				"Move To Tape Tracking Reference Positions",
				"Reference Tape Tracking recovery",
				"Tape Tracking recovery",
				"Calculate Start Positions",
				"Operator Confirm Move to start Positions",
				"Move Rings Pipe to Start Position",
				"Tow Pipe Position Y Axes",
				"Ready to Run",
				"Ready Complete",
				"No State @ Running Mode",
				"Waiting for user to press start button",
				"Retract Shrinking Encoders",
				"Activate Tape System",
				"Check Tape Presence",
				"Operator Ack Tape Missing",
				"Auto Weld Mode Check",
				"Feed Tape under Rollers",
				"Rollers Down",
				"Operator Ack Apply Masking Tape",
				"Activate Lasers",
				"Activate Auto Weld",
				"Sounder on to indicate start of Tape Laying",
				"Synchronising Axes",
				"Tape laying in Progress",
				"Soft stop with lasers triggered",
				"Soft stop without Lasers Triggered",
				"Dynamic Stop has been Triggered",
				"Starting recovery State Machine",
				"End of Tape Wind",
				"Resetting all Tape Tracking Data",
				"Updating Tapes applied",
				"Updating Recovery Pass Data",
				"Update Layer Count",
				"Running State Machine Completed",
				"Error state @ Running Mode",
				"No state @ Recovery Mode",
				"Referencing & lowering the Shrinkage Encoders to Pipe",
				"Confirm to progress Stop Recovery",
				"Recovery Method is being selected",
				"Checking if a Hafner change is required",
				"Indicate if a Hafner change is wanted",
				"Moving Linear Adjustment Axes to Clearance Positions",
				"Moving Angular Adjustment Axes to Hafner change Pos",
				"Moving Rings to Start Positions for Hafner change",
				"Complete Hafner change, then confirm to continue",
				"Checking if the Hafner changes were successful",
				"Hafner change unsuccessful, check and repeat Procedure",
				"Resetting Tape length flags for all Tape Hheads",
				"Moving Angular adjustment Axes to Target Positions",
				"Moving Linear adjustment Axes to required Pipe Pos",
				"Checking if any Rings have been disabled",
				"Moving disabled Ring TLH Axes to Clearance Positions",
				"Recording Shrinkage Value Measurements",
				"Lifting the Shrinkage Encoders from the Pipe",
				"Referencing the Tape Tracking System for Shrinkage",
				"Calculating new Start Positions for Standard Recovery",
				"Moving to Tails removal Position",
				"Referencing and lowering the shrinkage encoders onto pipe",
				"Confirm that Tape Tails have been removed from the Pipe",
				"Performing the Camera Alignment Procedure",
				"Calculating new Reference Pos for Tape Tracking recovery",
				"Moving to new Tape Tracking reference Positions",
				"Referencing the Tape Tracking System for Camera Alignment",
				"Initiating Tape Tracking Recovery",
				"Calculating new Start Positions for Recovery",
				"Moving to new recovery Start Positions",
				"Referencing and lowering the Shrinkage Encoders onto Pipe",
				"Feeding Tape to start positions on all required Tape Heads",
				"Initialising Lasers",
				"Is another recovery method required?",
				"Choose recovery Method",
				"Recovery State Machine sequence completed",
				"Error state @ Recovery Mode",
				"No state @ Completion Mode",
				"Confirm ready to perform a Pipe unload operation",
				"Moving Axes to clearance positions",
				"Releasing the Pipe",
				"Checking the Axes are enabled & associates are healthy",
				"Ready for Pipe unload",
				"Completion State Machine sequence completed",
				"Error state @ Completion Mode",
				"System healthy issues - Cell Door opened",
				"Unknown State, ask any operating Supervisor",
				"Unknown State definition"]

db_number = 89
s_offset = [0, 874, 878, 880, 66, 360, 875, 876, 68, 882, 886, 890, 894, 2, 80, 898]
b_offset = [0, 1, 2, 3, 4, 5, 6, 7]

loadOnce = False
inProgress = False
# --------------------------------------------------------------------------------------------------------------------


def errorLog(err):
	fileName = datetime.now().strftime('WDELog '+"%Y-%m-%d")
	event = datetime.now().strftime("%Y-%m-%d %H:%M.%S")
	errorlogFile = str(fileName)
	f = open('.\\RuntimeLog\\'+errorlogFile+".txt", "a")
	f.write(event+' --- '+err+'\n')
	f.close()


def smc_status(rtc):			# Match MSC code with string description
	rt_satus = dict(zip(machineCode_Data, codeDescript))
	status_rt = rt_satus[rtc]
	if status_rt != 0:
		print(status_rt)
	else:
		pass
	return status_rt



def watchDogController():
	global plc
	# import CommsPlc as plc

	# Allow connection once unless connection drops out -----
	if not plc.connectPLC:
		connectPLC = plc.connectM2M()
		print('M2M Connection Established:', connectPLC)

	# if connectPLC:
	print('\nChecking machine state at interval...')
	# -------------------------------------------------------
	sysRun = plc.readBool(db_number, s_offset[0], b_offset[0])  # System is runing
	sysidl = plc.readBool(db_number, s_offset[0], b_offset[1])  # System idling
	sysrdy = plc.readBool(db_number, s_offset[0], b_offset[2])  # System Ready
	# ------------------------------------------------------
	rngONE = plc.readBool(db_number, s_offset[0], b_offset[3])  # Ring 1 is ready
	rngTWO = plc.readBool(db_number, s_offset[0], b_offset[4])  # Ring 2 is ready
	rngTHR = plc.readBool(db_number, s_offset[0], b_offset[5])  # Ring 3 is ready
	rngFOR = plc.readBool(db_number, s_offset[0], b_offset[6])  # Ring 4 is ready
	# -------------------------------------------------------
	msctcp = plc.readInteger(db_number, s_offset[2], b_offset[0])  # Machine State Code (msc)
	won_NO = plc.readString(db_number, s_offset[4], b_offset[0])  # Work Order Number
	prodTA = plc.readBool(db_number, s_offset[260], b_offset[0])  # Active DNV Process
	prodTB = plc.readBool(db_number, s_offset[261], b_offset[1])  # Active MGM Process
	# -------------------------------------------------------
	tLayer = plc.readInteger(db_number, s_offset[262], b_offset[0])  # Total required Layer
	cLayer = plc.readInteger(db_number, s_offset[264], b_offset[0])  # Current achieved layer
	time.sleep(10)														# 10 seconds non-blocking interval

	rt_satus = dict(zip(machineCode_Data, codeDescript))
	msc_rt = rt_satus[msctcp]
	print('\nTCP01 Status:', msc_rt)

	return sysRun, sysidl, sysrdy, rngONE, rngTWO, rngTHR, rngFOR, msctcp, won_NO, prodTA, prodTB, tLayer, cLayer


def autoLaunchViz():			# obtain required variables for playing visualization
	global loadOnce, inProgress
	import psutil
	print('Loading visualisation module, please wait......', not loadOnce)

	# Read once OR when state machine code is altered
	if not loadOnce:
		print('\nNumber of Core-CPU#:', os.cpu_count())
		print('=' * 24)
		print('Auto Launch Parent PID:', os.getppid())
		print('Auto Launch Child PID:', os.getpid())
		print(f"CPU utilization: {psutil.cpu_percent()}%")
		print(f"Memory utilization: {psutil.virtual_memory().percent}%")
		print('-' * 25)
		print('Auto Launch Thread:', get_native_id())
		print('Loading runtime variables...\n')

		# Allow connection once unless connection drops out -----
		if not plc.connectPLC:
			connectPLC = plc.connectM2M()
			print('Auto-Launch: M2M Connection Established:', connectPLC)

		# Obtain runtime Process variable -------------------------[]
		OE = plc.readBool(db_number, s_offset[1], b_offset[0])
		RP = plc.readBool(db_number, s_offset[1], b_offset[1])
		TT = plc.readBool(db_number, s_offset[1], b_offset[2])
		DT = plc.readBool(db_number, s_offset[1], b_offset[3])
		TG = plc.readBool(db_number, s_offset[1], b_offset[4])

		# Monitor a parameter --------------------------------
		LP = plc.readBool(db_number, s_offset[5], b_offset[0])
		TS = plc.readBool(db_number, s_offset[5], b_offset[1])
		LA = plc.readBool(db_number, s_offset[5], b_offset[2])

		# Permutate the active Monitoring Parameter ---------------[]
		if not LP and not TS and LA:
			MP = LA
		elif not LP and not LA and TS:
			MP = TS
		elif not TS and not LA and LP:
			MP = LP
		else:
			MP = 0
		print('\nLoading the monitoring parameter..', MP)
		# ----------------------------------------------------
		HeadA = plc.readBool(db_number, s_offset[1], b_offset[6])		# View type A
		HeadB = plc.readBool(db_number, s_offset[1], b_offset[7])		# View type B
		HeadC = plc.readBool(db_number, s_offset[6], b_offset[0])		# FMC Grand View
		vAPT4 = 0 														# DNV Grand View
		sqlTbls = plc.readBool(db_number, s_offset[6], b_offset[1])
		plcTbls = plc.readBool(db_number, s_offset[6], b_offset[2])

		# include retrospectivePlay, SQL date search start/end ----
		ret, stad, stpd = 0, 0, 0		# required for real-time runtime visualization.
		loadOnce = True					# Set bit High to prevent reloading unless SMC
		print('Load Once Variable', loadOnce)

		# Evaluate the variables HeadA, B, C, Sqltables or View -------[]
		if not HeadA and not HeadB and not HeadC:
			print('\nInvalid Visualisation selection, check Visualisation Mode in SCADA')
			print('-' * 67)
			pass
		if not plcTbls and not sqlTbls:
			print('\nInvalid Database Selection, please select [Utilise SQL Table / SQL View] in SCADA')
			print('-'*82)
			pass

		# Permutate the active Visualisation Mode----------------------[]
		if HeadA and not HeadB and not HeadC:
			Vis = HeadA
		elif HeadB and not HeadA and not HeadC:
			Vis = HeadB
		elif HeadC and not HeadA and HeadB:
			Vis = HeadC
		else:
			Vis = False
			print('\nMultiple Screen Mode not allowed...', Vis)
		print('\nCurrent Plot selection is', Vis)
		print('Progress Status', inProgress)
		print('Parameter Status', RP, TT, DT, TG)
		# Prepare the remote GUI for visualization process ------------[]
		if not inProgress and Vis and RP or TT or DT or TG:

			# Check data type selection from SCADA User ---
			if sqlTbls or plcTbls:
				print('RT in Process....')
				# Execute menu object selections --[]
				import Remote_GUI as rg
				try:
					rg.executeProcess(ret, stad, stpd, plcTbls, sqlTbls, HeadA, HeadB, HeadC, vAPT4, RP, TT, DT, TG, MP, OE)

				except Exception as err:
					errorLog(err)
				else:
					print('AutoLaunch: SPC Screen launched successfully')
					inProgress = True
		else:
			print('\nTape laying activity in progress...')

	return inProgress


# This is the THINK THANK common to all real-time procedures ======================================================[]
def watchDog():
	global sysRun, sysidl, sysrdy, rngONE, rngTWO, rngTHR, rngFOR, msctcp, won_NO, prodTA, prodTB, tLayer, cLayer

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
	print('Watchdog Thread:', get_ident())

	# Activate WatchDog function-------------------------------------[]
	rtError = False
	inProgress = False

	while True:
		try:
			# Update status every 10 sec ----------------------------[]
			sysRun, sysidl, sysrdy, rngONE, rngTWO, rngTHR, rngFOR, msctcp, won_NO, prodTA, prodTB, tLayer, cLayer = watchDogController()
			# -------------------------------------------------------[]
		except Exception as err:
			print(f"Exception Error: '{err}'")
			rtError = True
			errorLog(f"{err}")
			print('\nSafe function..')

		finally:
			print('\nChecking the synchronous logic state...')
			if rtError:
				print('Reset connection request...')
				rtError = False
				continue


			elif not sysrdy and msctcp == 0 and not sysRun:
				print('\nTCP in offline mode...')
				time.sleep(.5)

			elif not rngONE or not rngTWO or not rngTHR or not rngFOR and sysrdy:
				print('\nSPC in Disengage mode...')

			elif rngONE or rngTWO or rngTHR or rngFOR and sysrdy and not sysRun:
				print('\nSPC in Engage mode...')

			elif msctcp == 301 and sysrdy and sysidle:
				print('\nTCP in Standby mode...')

			elif sysrdy and msctcp == 110 and not sysidle:
				print('\nTCP in Ready mode...')

			# When TCP is in Error, indicate the SMC to Vis Screen ------------------------[]
			elif msctcp == 111 or msctcp == 261 or msctcp == 325 or msctcp == 438 or msctcp == 515:
				state = codeDescript[10]  # TCP in Categorised process Error state --------[]
				print('\nTCP in ' + state)

			elif msctcp == machineCode_Data[0]:
				state = codeDescript[0]  # Unknown State, Call Engineering Team --------[]
				print('\nTCP in ' + state)

			elif not inProgress and msctcp == machineCode_Data[5]:
				state = codeDescript[5]		# Successful Pipe Load, Indicate on Vis -------[]
				print('\nTCP '+state)

			elif not inProgress and msctcp == machineCode_Data[29]:
				state = codeDescript[29]		# Pipe Load reversing, Indicate on Vis ----[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[33]:
				state = codeDescript[33]		# Move rings to pos for Hafner change, ----[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[34]:
				state = codeDescript[34]		# Hafner change completed -----------------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[36]:
				state = codeDescript[36]		# Hafner change error, repeat. ------------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[38]:
				state = codeDescript[38]		# Confirm ready for production ------------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[48]:
				state = codeDescript[48]		# Feeding Tape through heads --------------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[49]:
				state = codeDescript[49]		# Setting laser Angle ---------------------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[53]:
				state = codeDescript[53]		# Performing Camera Alignment -------------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[60]:
				state = codeDescript[60]		# Moving Rings to Start Pos ---------------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[63]:
				state = codeDescript[63]		# Ready State machine is completed --------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[69]:
				state = codeDescript[69]		# Tape Missing consent to recovery --------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[71]:
				state = codeDescript[71]		# Tape Feeding protocol begins ------------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[72]:
				state = codeDescript[72]		# Applying Tape Rollers -------------------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[73]:
				state = codeDescript[73]		# Applying Masking Tapes ------------------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[75]:
				state = codeDescript[75]		# Recovery State Machine Recovery ---------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[76]:
				state = codeDescript[76]		# Tape Laying Process Completed -----------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[81]:
				state = codeDescript[81]		# Running State Machine completed ---------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[89]:
				state = codeDescript[89]		# Hafner Change completed, Ok continue ----[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[90]:
				state = codeDescript[90]		# Hafner Change Unsuccessful, Repeat ------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[103]:
				state = codeDescript[103]		# Camera Alignment Procedure begins -------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[112]:
				state = codeDescript[112]		# Recovery State machine Sequence completed[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[114]:
				state = codeDescript[114]		# Ready for Pipe upload -------------------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[118]:
				state = codeDescript[118]		# Hafner removal procedure completed ------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[119]:
				state = codeDescript[119]		# Hafner removal unsuccessful -------------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[123]:
				state = codeDescript[123]		# Releasing the Pipe, please wait ---------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[125]:
				state = codeDescript[125]		# Activate Pipe unload operation ------------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[126]:
				state = codeDescript[126]		# Completion State Machine Sequence -------[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[129]:
				state = codeDescript[129]		# Laser triggered soft stop in effect -----[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[130]:
				state = codeDescript[130]		# Error triggered soft stop in effect -----[]
				print('\nTCP: '+state)

			elif not inProgress and msctcp == machineCode_Data[131]:
				state = codeDescript[131]		# Dynamic triggered soft soft in effect ---[]
				print('\nTCP: '+state)

			elif sysrdy and sysRun:   							# ready to start prod [and sqlrdy]
				print("\nWatchDog: Real-Time visualization begins...", msctcp)
				if not inProgress and msctcp == machineCode_Data[128]:		# "Tape laying Process in Progress 314"
					print('Watchdog: Launching visualisation...')
					state = codeDescript[128]
					print('\nSTATUS NOW:', state)
					# Get this thread on a new process --------------------------------------------[]
					inProgress = True  						# Set validation Bit
					p2 = Process(target=autoLaunchViz) 		# Launch Visualisation Plot Screen ----[P]
					p2.start()								# Start on a new Thread/Processor
					p2.join()
					time.sleep(.5) 							# sleep for few millisec | p2.join()

				elif inProgress and msctcp == machineCode_Data[129]:		# "Laser triggered soft stop in effect"
					state = codeDescript[129]
					print('\nTCP: ' + state)
					inProgress = False 										# Set validation Bit LOW

				elif inProgress and msctcp == machineCode_Data[130]:		# "Error triggered soft stop in effect"
					state = codeDescript[130]
					print('\nTCP: ' + state)
					inProgress = False 										# Set validation Bit LOW

				elif inProgress and msctcp == machineCode_Data[131]:		# "Dynamic triggered soft soft in effect"
					state = codeDescript[131]
					print('\nTCP: ' + state)
					inProgress = False	  									# Set validation Bit LOW

				elif inProgress and msctcp == machineCode_Data[126]:		# "Completion of State Machine Sequence"
					state = codeDescript[126]
					print('\nTCP: ' + state)
					inProgress = False  									# Set validation Bit LOW

				elif inProgress and not msctcp == machineCode_Data[10] or not msctcp == machineCode_Data[64] \
						or not msctcp == machineCode_Data[82] or not msctcp == machineCode_Data[113] \
						or not msctcp == machineCode_Data[127] or not msctcp == machineCode_Data[129] \
						or not msctcp == machineCode_Data[130] or not msctcp == machineCode_Data[131]:
					print('\nTCP: Tape laying Process in Progress')

				else:
					print("\nWatchDog: Visualization Resumes...")

			else:
				if not sysrdy and msctcp == 0 and not sysRun:
					inProgress = False
					print('\nWatchDog: Ending the process...')
				time.sleep(.5)

# ------------------------------- Splash Screen --------------------------
# Author: Dr RB Labs
# Developed for Magma Global - TechnipFMC Industrialization
# Email: robbielabs@uwl.ac.uk
# Copyright (C) 2023-2025, Robbie Labs
# ------------------------------------------------------------------------
"""
Called from 
Consists of:
1. Splash function - loading all run-time variables and writing INI files
2. Snooze mode function - when no activity, random screen saver object
3. Snooze Auto-restore function after closing GUI by an operator
4. Standby mode function -  Activating watch dog
5. Errors Handlers - Capturing all issues relating to processing & launching

"""
# -------------------------- Initiate variable --------------------
splashInUse = False

db_number = 89
start_offset = [898, 894]
bit_offset = [0, 1]

# -----------------------
# w, h = 425, 250
# w, h = 780, 450
# w, h = 425, 250
# -----------------------

user_url = "http://www.magmaglobal.com/synchronous_spc"

# ------------ Launch-Screen Event Functional Control --------------
stup_messages = ["Evaluating ring-head combinations", "Checking SQL repository Hardware",
                 "Accessing selected parameters", "Checking SPC Constants and Metrics",
                 "Evaluating Sampling Resolution", "Testing High-Speed Connectivity",
                 'Downloading SPC initialization Files', 'Loading SPC Visualisation Model',
                 'Writing SPC values into .INI File...', 'Saving & Finalizing .INI Files']

error_handlers = ['M2M connection failed, re-trying...', 'Fatal Error!, SPC Process Exiting...',
                  "Connection now established!"]


def errorLog(err):
    fileName = datetime.now().strftime('SPHLog '+"%Y-%m-%d")
    event = datetime.now().strftime("%Y-%m-%d %H:%M.%S")
    errorlogFile = str(fileName)
    f = open('.\\RuntimeLog\\'+errorlogFile+".txt", "a")
    f.write(event+' --- '+err+'\n')
    f.close()


# Window Exit Functions ---------------[]
def to_GUI(event):
	# ---------------------------------[]
	print('\nExiting Splash Screen...')
	timer.cancel()
	mySplash.destroy()
	if mySplash.withdraw:
		import synchronousMain as rb
		print('Loading SPC GUI...\n')
		print('\nMenu Thread ID:', get_ident())
	t3 = threading.Thread(target=rb.main(), name='t3')
	t3.start()
	t3.join()
	return


def to_dScr(event):
    # ---------------------------------[]
    print('\nExiting Splash Screen...')
    timer.cancel()
    mySplash.destroy()
    if mySplash.withdraw:
        # import Screen_Saver as sz
        print('Loading SPC GUI...\n')
        print('\nMenu Thread ID:', get_ident())
    dScreen()             # called function

    return

def to_AutoProcess(event):
    # ------------------------------------------
    import synchronousMain as rb

    print('\nMomentary paused Screen Saver...')
    timer.cancel()

    mySplash.deiconify()

    screen_w = mySplash.winfo_screenwidth()
    screen_h = mySplash.winfo_screenheight()
    # -------------------------------------------
    x_c = int((screen_w / 2) - (w / 2))
    y_c = int((screen_h / 2) - (h / 2))

    mySplash.deiconify()
    mySplash.geometry(f"{w}x{h}+{x_c}+{y_c}") 				# reset position
    sleep(.9)
    rb.common_PA()
    # mySplash.after(10000, lambda: move_window())        # delay for 10 seconds

    return

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
        print('\n Attempting to update screen resolution, please wait...')
        scrZ = '1k'
        updateSCRres()
        print('Screen resolution updated successful!')
        print('Primary display not SPC Compliant..')

    return scrZ


def move_window():
	global timer, w, h

	timei = time.time()  # start timing the entire loop
	timer = Timer(2, move_window)       # Start threading.Timer()

	mySplash.bind("<Motion>", to_GUI)           # To GUI Menu
	mySplash.bind("<Escape>", to_GUI)           # To GUI Menu
	mySplash.config(cursor="none")
	# -------------------------------------------
	if sysrdy and not sysidle:
		to_AutoProcess(event=None)
	else:
		pass
	# --------------------------------------------------[]
	print('\nSPC in Snooze mode, press Esc to resume')             # Snooze function
	mySplash.geometry(f"{w}x{h}+{int(randint(10, 1900))}+{int(randint(10, 1000))}")
	if not timer.is_alive():
		timer.start()
	else:
		timer.cancel()
		mySplash.deiconify()
	mySplash.after(30000, lambda: to_dScr(event=None)) 	# snoozes in 30 seconds

	return


def sendM2M_ACK():
    # Send acknowledgement by raising M2MConACK on SCADA Process and activate watchdog ---[]
    try:
        # Check if the Bit is @Low then raise High --------------------------[A]
        m2mgood = plc.readBool(db_number, start_offset[0], bit_offset[0])
        if not m2mgood:
            print('\nM2M connection acknowledged by SCADA...')
            plc.writeBool(db_number, start_offset[0], bit_offset[0], 1)
            m2mgood = True

            # Initiate a new thread / process -------------------------------[B]
            print('Obtaining and writing SPC metrics to .INI..')
            call_once = plc.spcMetricsModule()      # prevent multiple call for this procedure class
            call_once.saveMetric()                  # download metrics from scada & write values into .INI

    except KeyboardInterrupt as err:
        errorLog(err)

    return m2mgood


def autoSplash(istener, splash):
    global img, mySplash, splashInUse, listener

    print('\nNumber of Core-CPU#:', os.cpu_count())
    print('=' * 24)
    print('Splash Parent PID:', os.getppid())
    print('Splash Child PID:', os.getpid())
    print('Splash Thread:', get_ident())
    print(f"CPU utilization: {psutil.cpu_percent()}%")
    print(f"Memory utilization: {psutil.virtual_memory().percent}%")
    print('-' * 25)

    """
    Auto acknowledgement (sendM2M_ACK() function was added to pipeline.. 
    19/Feb/2024 - RL
    """
    # Check screen resolution for SPC compliance
    print('\nChecking Viz-Screen Resolution...')
    checkRes()
    # -----------------------------------------
    listener = istener
    print('Listener prop:', listener)
    mySplash = splash                        # rename to allow usage in global.ini
    mySplash.overrideredirect(True)          # disable top bar

    # splash_root.geometry("450x250")           # defined above but can be altered to suit
    init_str = StringVar()
    init_str.set('Initializing variables...')

    print('SPC standby mode...')
    mySplash.title('SPC Industrialization')
    screen_w = mySplash.winfo_screenwidth()
    screen_h = mySplash.winfo_screenheight()
    # -------------------------------------------
    x_c = int((screen_w / 2) - (w / 2))
    y_c = int((screen_h / 2) - (h / 2))
    print(w, h, x_c, y_c)
    mySplash.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))

    img = ImageTk.PhotoImage(Image.open("200x120.png"))
    s_label = Label(mySplash, image=img, text="Welcome to Magma SPC", font=18)
    # x=35, y=122
    Label(mySplash, text="Synchronous Multivariate SPC", width=28, justify=CENTER, font=12).place(x=70, y=125)
    Label(mySplash, text="Advanced Statistical Processing & Visualization System", justify=CENTER).place(x=78, y=150)
    Label(mySplash, text="Integrated into SCADA's (CF/PEEK) Manufacturing Process", justify=CENTER).place(x=70, y=168)
    Label(mySplash, text=user_url).place(x=120, y=186)
    Label(mySplash, textvariable=init_str, width=30, justify=CENTER).place(x=100, y=215)  #
    s_label.pack()

    r = 10
    for n in range(r):
        sleep(.2)
        if n <= (r - 2):
            init_str.set(f"Connecting to PLC Subsystem.{'.' * n}".ljust(27))
            # print('Testing loop')

        else:
            init_str.set(f"Establishing connectivity.{'.' * n}".ljust(27))
            connectPLC = plc.connectM2M()  # Connect to Snap7 Server
            print('\nCONN1:', connectPLC)
            # recall M2M connection again ----------- 1st time try
            if connectPLC:
                print('\nSending M2M acknowledgement... (1)')
                sendM2M_ACK()
            else:
                print('\nM2M acknowledgement failed...')
            mySplash.update_idletasks()

            retry = 0
            while not connectPLC and retry < 10:       # create a persistent loop
                print('\nConnection failed at first instance, retrying...')
                init_str.set(f"{error_handlers[1]}{'.' * n}".ljust(27))
                try:
                    print('Second try...')
                    connectPLC = plc.connectM2M()                        # Connect to Snap7 Server
                    print('\nCONN2:', connectPLC)
                    # recall M2M connection again ----------- 2nd time
                    if connectPLC:
                        print('\nSending M2M acknowledgement... (2)')
                        sendM2M_ACK()
                    else:
                        print('\nM2M acknowledgement failed...')

                except Exception as err:
                    print(f"Exception Error: '{err}'")
                    errorLog(error_handlers[0])             # retrying connection
                    init_str.set(f"{error_handlers[1]}{'.' * n}".ljust(27))
                    sleep(.5)
                    mySplash.update_idletasks()

                else:   # Connection failed, show status
                    if connectPLC:
                        # recall M2M connection again ----------- 3rd time
                        print('Successful connection established...')
                        init_str.set(f"{error_handlers[2]}{'.' * n}".ljust(27))
                        print('\nSending M2M acknowledgement... (3)')
                        sendM2M_ACK()
                        sleep(.5)                               # rest a while
                        mySplash.update_idletasks()
                    else:
                        # sn7.plc.destroy()                     # reset command
                        plc.connectPLC = False
                        init_str.set(f"{error_handlers[1]}{'.' * n}".ljust(27))
                        print('Issues with M2M Connection, may shut down..')
                        sleep(.5)  # rest a while
                        mySplash.update_idletasks()
                retry += 1
                print('Counting', retry)
            # ---- TODO
            else:
                print('Runtime in progress...')
        sleep(.5)
        mySplash.update_idletasks()
        sleep(.5)

    for n in stup_messages:
        if plc.connectPLC:                              # Check connectivity if it's available
            init_str.set(n)
        elif stup_messages[0] and not connectPLC:
            # persistent loop on connection -----
            alpha_try = 0
            while alpha_try < 10:
                # print('Alpha Try #', alpha_try)
                print('No sign of connectivity yet...')
                init_str.set(f'{error_handlers[1]}'.ljust(27))
                errorLog(error_handlers[1])
                sleep(.5)
                alpha_try += 1
            else:
                print('M2M connectivity failed....')
                break
        sleep(5)
        mySplash.update_idletasks()

    for n in range(r):
        sleep(.2)
        init_str.set(f"Almost Done.{'.' * n}".ljust(27))
        mySplash.update_idletasks()

    for n in range(r):
        sleep(.5)
        init_str.set("Almost Done..........".ljust(27))
        sleep(.5)
        init_str.set("Initialization Sorted...".ljust(27))
        mySplash.update_idletasks()

    Label(mySplash, text="WatchDog activated, remote call!", justify=LEFT).place(x=140, y=215)

    # Initiate a new thread / process -------------------------------[C]
    # import spcWatchDog as wd
    # print('Loading Watchdog Module, please wait... ')
    # npid = wd.watchDog(listener, splash)  # carry 2 variables along, required to remove screen splash
    # p = Process(target=npid)
    # p.start()
    # # p.join()
    mySplash.after(60000, lambda: move_window())        # call snooze function with false token

    return splashInUse



def localSplash():
    global img, mySplash, splashInUse, w, h

    # Check screen resolution for SPC compliance & update res
    print('\nChecking Viz-Screen Resolution...')
    scrRes = checkRes()
    if scrRes == '4k':
        w, h, f, xp, yp = 1400, 800, 25, 450, 570
    elif scrRes == '2k':
        w, h, f, xp, yp = 780, 450, 14, 274, 370
    else:
        w, h, f, xp, yp = 425, 250, 12, 100, 220

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
        print('Screen Size:', w, h, x_c, y_c)                           # Screen Size: 425 250 1067 595
        mySplash.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))

        if scrRes == '4k':
            print('\nUsing 4k screen resolution...')
            img = ImageTk.PhotoImage(Image.open("820x267.png"))
            s_label = Label(mySplash, image=img, text="Welcome to Magma SPC", font=72)
            # --------------------------------------------------------------------------
            Label(mySplash, text="Synchronous Multivariate SPC", width=28, justify=CENTER, font=("NovaMono", 50)).place(x=150, y=300)
            Label(mySplash, text="Advanced Statistical Processing & Visualization System", justify=CENTER, font=("NovaMono", 25)).place(x=300, y=380)
            Label(mySplash, text="Integrated into SCADA's (CF/PEEK) Manufacturing Process", justify=CENTER, font=("NovaMono", 25)).place(x=255, y=420)
            Label(mySplash, text=user_url, font=("NovaMono", 20)).place(x=370, y=470)
            Label(mySplash, textvariable=init_str, width=30, justify=CENTER, font=("NovaMono", 25)).place(x=370, y=520)  #
            s_label.pack()

        elif scrRes == '2k':		# 2560 by 1440
            print('\nUsing 2k screen resolution...')
            img = ImageTk.PhotoImage(Image.open("291x180.png"))
            s_label = Label(mySplash, image=img, text="Welcome to Magma SPC", font=36)
            # --------------------------------------------------------------------------
            Label(mySplash, text="Synchronous Multivariate SPC", width=28, justify=CENTER, font=("NovaMono", 30)).place(x=70, y=185)
            Label(mySplash, text="Advanced Statistical Processing & Visualization System", justify=CENTER, font=("NovaMono", 14)).place(x=160, y=235)
            Label(mySplash, text="Integrated into SCADA's (CF/PEEK) Manufacturing Process", justify=CENTER, font=("NovaMono", 14)).place(x=135, y=260)
            Label(mySplash, text=user_url, font=("NovaMono", 12)).place(x=240, y=290)
            Label(mySplash, textvariable=init_str, width=30, justify=CENTER, font=("NovaMono", 14)).place(x=230, y=340)  #
            s_label.pack()

        else:
            print('\nUsing VGA screen resolution...')
            img = ImageTk.PhotoImage(Image.open("200x120.png"))
            s_label = Label(mySplash, image=img, text="Welcome to Magma SPC", font=18)
            # --------------------------------------------------------------------------
            Label(mySplash, text="Synchronous Multivariate SPC", width=28, justify=CENTER, font=14).place(x=70, y=125)
            Label(mySplash, text="Advanced Statistical Processing & Visualization System", justify=CENTER, font=14).place(x=78, y=150)
            Label(mySplash, text="Integrated into SCADA's (CF/PEEK) Manufacturing Process", justify=CENTER, font=14).place(x=70, y=168)
            Label(mySplash, text=user_url, font=12).place(x=120, y=220)
            Label(mySplash, textvariable=init_str, width=30, justify=CENTER, font=12).place(x=100, y=215)  #
            s_label.pack()
        mySplash.update()

        r = 10
        for n in range(r):
            sleep(.2)
            if n <= (r - 2):
                init_str.set(f"Checking OS and file System.{'.' * n}".ljust(27))

            else:
                init_str.set(f"Establishing Modular Connectivity.{'.' * n}".ljust(27))
                mySplash.update_idletasks()

            sleep(.5)
            mySplash.update_idletasks()
            sleep(.5)

        for n in range(r):
            sleep(.2)
            init_str.set(f"Almost Done.{'.' * n}".ljust(27))
            mySplash.update_idletasks()

        for n in range(r):
            sleep(.5)
            init_str.set("Almost Done..........".ljust(27))
            sleep(.5)
            init_str.set("System initialization completed".ljust(27))

            # Allow SPC loading user values from SCADA once for every pipe laying process ----
            mySplash.update_idletasks()
        Label(mySplash, text="OPC UA Watchdog enabled!", justify=CENTER, font=("NovaMono", f)).place(x=xp, y=yp)
        mySplash.after(5000, lambda: move_window())

    else:
        print('\nScreen Saver Active....')

    mySplash.update_idletasks()
    # mySplash.update()

def mSplash():
    global mySplash, img

    mySplash = Tk()

    mySplash.wm_attributes('-topmost', True)            # "-transparentcolor",
    print('\nNumber of Core-CPU#:', os.cpu_count())
    print('=' * 24)
    print('Alpha Parent PID:', os.getppid())
    print('Alpha Child PID:', os.getpid())
    print(f"CPU utilization: {psutil.cpu_percent()}%")
    print(f"Memory utilization: {psutil.virtual_memory().percent}%")
    print('-' * 25)

    # mySplash.after(5000, lambda: localSplash())
    localSplash()
    mySplash.mainloop()

# -------------------------------Default Screen Saver ----------------

# close window
def toSplash(event):
	# ----------------
	running = False
	# ----------------
	print('Exiting to Splash...')
	sleep(.9)
	root.destroy()
	mSplash()
	os._exit(0)
	return running

def toProcess(event):
	# ----------------
	running = False
	# ----------------
	print('Exiting to Process...')
	sleep(.9)
	root.destroy()
	to_AutoProcess(event=None)
	os._exit(0)
	return running


def showDefaultScreen():
    while running:
        tk_Owner.set(value='Magma Global SPC\n')
        tkinter_time.set(value=strftime("%H:%M:%S"))
        tkinter_date.set(value=strftime("%A, %e %B"))
        root.update_idletasks()
        root.update()
        sleep(1)


def dScreen():
	global running, tk_Owner, tkinter_time, tkinter_date, root
	root = Tk()

	msC = BooleanVar() 		# From PLC/SCADA
	# Window Attributes
	root.overrideredirect(True)
	root.wm_attributes("-transparentcolor", "gray99")

	#--------------
	msC.set(sysrdy)		# sysrdy
	#---------------

	root.bind("<Motion>", toSplash)    # Mouse action to Splash Screen
	root.bind("<Escape>", toSplash)    # Code from watchdog to Visualisation
	if msC == '4132':
		toProcess()
	else:
		pass
	root.config(cursor="none")

	screen_width = root.winfo_screenwidth()
	screen_height = root.winfo_screenheight()

	timeframe = Frame(root, width=screen_width, height=screen_height, bg="Black")
	timeframe.grid(row=0, column=0)

	tk_Owner = StringVar() #
	tk_label = Label(timeframe, textvariable=tk_Owner, fg="#808080", bg="Black", font=("NovaMono", 80),)
	tk_label.place(y=screen_height / 2 - 60, x=screen_width / 2, anchor="center")

	tkinter_time = StringVar()
	time_label = Label(timeframe, textvariable=tkinter_time, fg="#808080", bg="Black", font=("NovaMono", 150),)
	time_label.place(y=screen_height / 2 + 60, x=screen_width / 2, anchor="center")

	tkinter_date = StringVar()
	date_label = Label(timeframe, textvariable=tkinter_date, fg="#808080", bg="Black", font=("Bahnschrift", 30),)
	date_label.place(y=screen_height / 2 + 200, x=screen_width / 2, anchor="center")
	# ------------------#
	showDefaultScreen()	# Snooze default screen

	return

