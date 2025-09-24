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
import threading
from multiprocessing import Process
from threading import *
from datetime import datetime
from time import sleep
import os
import psutil
from datetime import datetime, date

import CommsPlc as xp
# ----------------------------------------------------------------[]
sysrdy, sysidl, sysRun = 0, 1, 0
running = True
splashInUse = False
flag = 'Low'
# -------------------------- Initiate variable --------------------[]
user_url = "http://www.magmaglobal.com/synchronous_spc"
today = date.today()
# ------------ Launch-Screen Event Functional Control -------------[]
stup_messages = ["Evaluating ring-head combinations", "Checking SQL repository Hardware",
                 "Accessing selected parameters", "Checking SPC Constants and Metrics",
                 "Evaluating Sampling Resolution", "Testing High-Speed Connectivity",
                 'Downloading SPC initialization Files', 'Loading SPC Visualisation Model',
                 'Writing SPC values into .INI File...', 'Saving & Finalizing .INI Files']

error_handlers = ['M2M connection failed, re-trying...', 'Fatal Error!, SPC Process Exiting...',
                  "Connection now established!"]

# Ensure you update these parameters if anything changes in the SCADA  state machine codes ---------------------------
machineCode_Data = [40960, 40992, 41008, 41040, 41072, 41088, 43392, 43408, 45056, 45136, 45152, 45312, 45392, 45584,
					45600, 45648, 45712, 45872, 45968, 46160, 46176, 46384, 46464, 46592, 47488, 47504, 49152, 49200,
					49216, 49232, 49280, 49296, 49424, 49440, 49488, 49504, 49520, 49536, 49664, 51584, 51600, 53248,
					53280, 53328, 53376, 53392, 53648, 53792, 53824, 53840, 53872, 53888, 53904, 54032, 54048, 54064,
					54080, 55680, 55696, 57344, 57360, 57408, 57424, 57488, 57600, 57616, 57648, 59776, 59792, 49728]

codeDescript = ["StandBy State, Call Engineers ...", "Production Mode Confirmed", "Selecting Initial Direction",
				"Operator Confirming Pipe Load Procedure", "Operator Confirming Pipe Parameters",
				"Loading Pipe Parameter", "Startup Completed", "Unknown State!", "StandBy State...",
				"Running Pipe Param Algorithm", "Setting Production Mode", "Initiating Pipe Reversal Sequence",
				"Activating Chucks System", "Activating Pipe Reversal Mode", "Pipe in Reversing Motion…",
				"Activating Haffner Change Procedure", "Haffner Replacement Procedure Completed", "Adjusting Pipe Position",
				"Setting Polarised Camera to Position", "Setting Tape Feed to Start Position",
				"Setting Laser Angle to Start Position", "Moving to Tape Tracking Referenced Positions",
				"Moving Rings to Start Positions", "System Getting Ready", "System in Ready State …", "Unknown State!",
				"StandBy State...", "Re-tracking Shrinkage Encoders", "Activating Tape Laying System", "Checking Tape Present",
				"Feeding Tape under Rollers", "Setting Rollers Down ...", "Activating Lasers...", "Activating Auto-weld...",
				"Starting Tape Wind…", "Soft Stop Induced by Laser System", "Soft Stop Induced by Subsystem",
				"E-Stop OR Fault Activated Stop", "End of Tape Winding Procedure", "Pipe Running Algorithm Completed",
				"Unknown State!", "StandBy State...", "Activation Stop Recovery...", "Activating Haffner Replacement Procedure",
				"Positioning Rings for Haffner Replacement", "Haffner Replacement Procedure Completed", "Retracting Shrinkage Encoders",
				"Moving to Tails Removal Position", "Acknowledging Tails Removal Procedure", "Activating Camera Alignment Recovery",
				"Moving to Tape Tracking Ref Positions", "Referencing Tape Tracking Cameras", "Implementing Tape Tracking Recovery",
				"Moving to Recovery Start Positions", "Activating Shrinkage Encoder After Recovery",
				"Moving Tape Feed to Start Positions", "Moving Laser Angles to Start Positions",
				"Recovery Procedure Executed Successfully", "Unknown State!", "StandBy State...", "Pipe Unloading Procedure Started",
				"Positioning Rings for Haffner Replacement", "Haffner Replacement Completed", "Retracting KEYENCE Arms..",
				"Retracting Shrinkage Encoders...", "Executing Pipe Release Procedure..", "Executing Pipe UNLOAD Procedure…",
				"Pipe Build Completion Successful", "Unknown State!", "End of Pipe Layer"]

# -------------------------------------------------------------------------------------[]
db_number = 89
s_offset = [0, 874, 878, 880, 66, 360, 875, 876, 68, 882, 886, 890, 894, 2, 80, 898]
b_offset = [0, 1, 2, 3, 4, 5, 6, 7]

start_offset = [898, 894]
bit_offset = [0, 1]

loadOnce = False
inProgress = False
timeA = time.time()  						# start timing the entire loop
# -------------------------------------------------------------------------------------[]

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


def autoPausePlay():
	print('Checking SMC readiness...')
	# while True:
	try:
		sysRun = xp.readBool(db_number, s_offset[0], b_offset[0])			# False/True
		sysIdl = xp.readBool(db_number, s_offset[0], b_offset[1])  			# System idling
		sysRdy = xp.readBool(db_number, s_offset[0], b_offset[2])  			# System Ready
		mscTcp = xp.readInteger(db_number, s_offset[2], b_offset[0])   		# Machine State Code (msc)
		cLayer = xp.readBool(db_number, s_offset[264], b_offset[0])  		# Current achieved layer
		pipPos = xp.readBool(db_number, s_offset[436], b_offset[0])  		# Current achieved layer
		# Obtain State machine code description ----------------------------#
		rt_stat = dict(zip(machineCode_Data, codeDescript))

	except Exception as err:
		print(f"Exception Error: '{err}'")
		errorLog(f"{err}")
		print('Error loading autoplay..')
		sysRun = False														# Machine Unreachable
		sysIdl = 0
		sysRdy = 0
		mscTcp = 59792															# Machine No state / undefined state
		cLayer = 0
		pipPos = 0
		rt_stat = dict(zip(machineCode_Data, codeDescript))
	mstatus = rt_stat[mscTcp]

	return sysRun, sysIdl, sysRdy, mscTcp, cLayer, pipPos, mstatus


def rt_autoPausePlay():
	print('Checking SMC readiness...')
	try:
		sRun = xp.readBool(db_number, s_offset[0], b_offset[0])		# False/True
		msc = xp.readInteger(db_number, s_offset[2], b_offset[0])   # Machine State Code (msc)
		cLayr = xp.readInteger(db_number, s_offset[264], b_offset[0])
		rt_satus = dict(zip(machineCode_Data, codeDescript))
	except Exception as err:
		print(f"Exception Error: '{err}'")
		errorLog(f"{err}")
		print('Error loading autoplay..')
		sRun = False		# Machine Unreacheable
		msc = 59792			# Machine No state / undefined state
		cLayr = 0
		rt_satus = dict(zip(machineCode_Data, codeDescript))
	# Obtain State machine code description -------------------
	stat = rt_satus[msc]

	return sRun, msc, stat, cLayr

# --------------------- Determine if Host is Online/Offline -----------------#

def checkSQL():
	import CommsSql as st
	# Brisk test connection to SQL Server to determin Online/Offline Status
	status = st.check_SQL_Status(3, 5)

	return status

def checkPLC():
	import CommsPlc as st
	# Brisk test connection to SQL Server to determine Online/Offline Status
	status = st.check_PLC_Status()
	# print('TP02', status)
	return status


def liveProductionRdy():
	# Allow connection once unless connection drops out -----
	cPlc = xp.connectM2M(3, 2)
	# ------- Obtain readiness from host PLC --------
	if cPlc:
		try:
			sysidl = xp.readBool(db_number, s_offset[0], b_offset[1])  # System idling
			sysrdy = xp.readBool(db_number, s_offset[0], b_offset[2])  # System Ready
			sysRun = xp.readBool(db_number, s_offset[0], b_offset[0])  # System is runing
			# won_NO = xp.readBool(db_number, s_offset[4], b_offset[0])  # Work Order Number
			# msctcp = xp.readInteger(db_number, s_offset[2], b_offset[0])  # Machine State Code (msc)

		except Exception as err:
			print(f"Exception Error: '{err}'")
			errorLog(f"{err}")
			sysidl = False
			sysrdy = False
	else:
		sysidl = False
		sysrdy = False
		won_NO = False
		msctcp = False
		print('Sorry, PLC Host not responding, retry within seconds..')
	return sysidl, sysrdy, sysRun #, won_NO, msctcp


def watchDogController():
	# global c

	if not xp.connectPLC:
		connectPLC = xp.connectM2M()
		print('M2M Connection Established:', connectPLC)

	# if connectPLC:
	print('\nChecking machine state at interval...')
	# -------------------------------------------------------
	sysRun = xp.readBool(db_number, s_offset[0], b_offset[0])  # System is runing
	sysidl = xp.readBool(db_number, s_offset[0], b_offset[1])  # System idling
	sysrdy = xp.readBool(db_number, s_offset[0], b_offset[2])  # System Ready
	# ------------------------------------------------------
	rngONE = xp.readBool(db_number, s_offset[0], b_offset[3])  # Ring 1 is ready
	rngTWO = xp.readBool(db_number, s_offset[0], b_offset[4])  # Ring 2 is ready
	rngTHR = xp.readBool(db_number, s_offset[0], b_offset[5])  # Ring 3 is ready
	rngFOR = xp.readBool(db_number, s_offset[0], b_offset[6])  # Ring 4 is ready
	# -------------------------------------------------------
	msctcp = xp.readInteger(db_number, s_offset[2], b_offset[0])  # Machine State Code (msc)
	won_NO = xp.readString(db_number, s_offset[4], b_offset[0])  # Work Order Number
	prodTA = xp.readBool(db_number, s_offset[260], b_offset[0])  # Active DNV Process
	prodTB = xp.readBool(db_number, s_offset[261], b_offset[1])  # Active MGM Process
	# -------------------------------------------------------
	tLayer = xp.readBool(db_number, s_offset[262], b_offset[0])  # Total required Layer
	cLayer = xp.readBool(db_number, s_offset[264], b_offset[0])  # Current achieved layer
	pipPos = xp.readBool(db_number, s_offset[436], b_offset[0])  # Current achieved layer
	time.sleep(10)  # 10 seconds non-blocking interval

	rt_satus = dict(zip(machineCode_Data, codeDescript))
	msc_rt = rt_satus[msctcp]
	print('\nTCP01 Status:', msc_rt)

	return sysRun, sysidl, sysrdy, rngONE, rngTWO, rngTHR, rngFOR, won_NO, prodTA, prodTB, tLayer, cLayer, pipPos, msctcp


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
		if not xp.connectPLC:
			connectPLC = xp.connectM2M()
			print('Auto-Launch: M2M Connection Established:', connectPLC)

		# Obtain runtime Process variable -------------------------[]
		OE = xp.readBool(db_number, s_offset[1], b_offset[0])
		RP = xp.readBool(db_number, s_offset[1], b_offset[1])
		TT = xp.readBool(db_number, s_offset[1], b_offset[2])
		DT = xp.readBool(db_number, s_offset[1], b_offset[3])
		TG = xp.readBool(db_number, s_offset[1], b_offset[4])

		# Monitor a parameter --------------------------------
		LP = xp.readBool(db_number, s_offset[5], b_offset[0])
		TS = xp.readBool(db_number, s_offset[5], b_offset[1])
		LA = xp.readBool(db_number, s_offset[5], b_offset[2])

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
		HeadA = xp.readBool(db_number, s_offset[1], b_offset[6])		# View type A
		HeadB = xp.readBool(db_number, s_offset[1], b_offset[7])		# View type B
		HeadC = xp.readBool(db_number, s_offset[6], b_offset[0])		# FMC Grand View
		vAPT4 = 0 														# DNV Grand View
		sqlTbls = xp.readBool(db_number, s_offset[6], b_offset[1])
		plcTbls = xp.readBool(db_number, s_offset[6], b_offset[2])

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
	# Obtain dynamic values -----------------------------------------[]
	while True:
		try:
			# Update status every 10 sec ----------------------------[]
			sysRun, sysidl, sysrdy, rngONE, rngTWO, rngTHR, rngFOR, won_NO, prodTA, prodTB, tLayer, cLayer, pipPos, msctcp = watchDogController()
			# -------------------------------------------------------[]
		except Exception as err:
			print(f"Exception Error: '{err}'")
			rtError = True
			errorLog(f"{err}")

		finally:
			print('\nChecking the synchronous logic state...')
			if rtError:
				print('Reset connection request...')
				rtError = False
				continue

			elif not sysrdy and msctcp == 43408 or msctcp == 47504 or msctcp == 51600 or msctcp == 55696 and not sysRun:
				print('\nTCP in offline mode...')
				time.sleep(.5)

			elif not rngONE or not rngTWO or not rngTHR or not rngFOR and sysrdy:
				print('\nSPC in Disengage mode...')

			elif rngONE or rngTWO or rngTHR or rngFOR and sysrdy and not sysRun:
				print('\nSPC in Engage mode...')

			elif sysrdy or sysidl:
				print('\nTCP in Standby mode...')

			elif sysrdy and msctcp == 47488 and not sysidl:
				print('\nTCP in Ready mode...')

			# When TCP is in Error, indicate the SMC to Vis Screen ------------------------[]
			elif msctcp == 43408 or msctcp == 47504 or msctcp == 51600 or msctcp == 55696:
				state = codeDescript[25]  # TCP in Categorised process Error state --------[]
				print('\nTCP in ' + state)

			elif msctcp == 40960 or msctcp == 45056 or msctcp == 49152 or msctcp == 53248:
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

			elif sysrdy and sysRun:   			# ----- PAUSE CONDITION -------------------[]
				print("\nWatchDog: Real-Time visualization begins...", msctcp)
				if not inProgress and msctcp == machineCode_Data[27]:		# Activating Tape laying Process
					state = codeDescript[27]
					print('\nSTATUS NOW:', state)
					# Get this thread on a new process --------------------------------------------[]
					inProgress = True  						# Set validation Bit
					p2 = Process(target=autoLaunchViz) 		# Launch Visualisation Plot Screen ----[P]
					p2.start()								# Start on a new Thread/Processor
					p2.join()
					time.sleep(.5) 							# sleep for few millisec | p2.join()
				# Pause Condition --------------------------#
				elif inProgress and msctcp == machineCode_Data[28]:		# Laser triggered soft stop in effect"
					state = codeDescript[28]
					print('\nTCP: ' + state)
					inProgress = False

				elif inProgress and msctcp == machineCode_Data[29]:		# Dynamic triggered soft soft in effect
					state = codeDescript[29]
					print('\nTCP: ' + state)
					inProgress = False	  								# Set validation Bit LOW

				elif inProgress and msctcp == machineCode_Data[30]:
					state = codeDescript[30]							# E-Stop
					print('\nTCP: ' + state)
					inProgress = False

				elif inProgress and msctcp == machineCode_Data[31]:		# End of Tape Winding Procedure
					state = codeDescript[31]
					print('\nTCP: ' + state)
					inProgress = False

				elif inProgress and msctcp == machineCode_Data[32]:		# End of Tape Winding Procedure
					state = codeDescript[32]
					print('\nTCP: ' + state)
					inProgress = False

				elif inProgress and msctcp == machineCode_Data[33]:		# End of Tape Winding Procedure
					state = codeDescript[33]
					print('\nTCP: ' + state)
					inProgress = False

				elif inProgress and msctcp == machineCode_Data[35]:		# End of Tape Winding Procedure
					state = codeDescript[35]
					print('\nTCP: ' + state)
					inProgress = False

				elif inProgress and msctcp == machineCode_Data[36]:		# End of Tape Winding Procedure
					state = codeDescript[36]
					print('\nTCP: ' + state)
					inProgress = False

				elif inProgress and msctcp == machineCode_Data[37]:		# End of Tape Winding Procedure
					state = codeDescript[37]
					print('\nTCP: ' + state)
					inProgress = False

				elif inProgress and msctcp == machineCode_Data[34]:
					print('\nTCP: Tape laying Process Resumes..')

				else:
					print("\nWatchDog: Visualization Resumes...")

			else:
				if not sysrdy and msctcp == 0 and not sysRun:
					inProgress = False
					print('\nWatchDog: Ending the process...')
				time.sleep(.5)


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

	uCalling = 2
	pWON = today.strftime("%Y%m%d")
	rt_p = 0	# [0 = DNV | 1 = MGM]
	t3 = threading.Thread(target=rb.userMenu(uCalling, pWON, rt_p), name='OfflinePro')
	t3.start()
	t3.join()

	return


def to_dScr(event):
	# ---------------------------------[]
	print('\nExiting Splash Screen...')
	timer.cancel()
	mySplash.destroy()
	if mySplash.withdraw:
		import Screen_Saver as sz
		print('Loading SPC GUI...\n')
		print('\nMenu Thread ID:', get_ident())
	sz.sScreen()             # called function

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
	mySplash.geometry(f"{w}x{h}+{x_c}+{y_c}") 	# reset position
	sleep(.9)
	if prodTA and not prodTB:
		rt_p = 'DNV'
	elif not prodTA and prodTB:
		rt_p = 'MGM'
	else:
		rt_p = 'UKN'

	uCalling = 1
	pWON = won_NO
	t3 = threading.Thread(target=rb.userMenu(uCalling, pWON, rt_p), name='OnlinePro')
	t3.start()			# Open visualisation canvas
	t3.join()

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
        print('\nScreen resolution?, Please wait...')
        scrZ = '1k'
        updateSCRres()
        print('Screen resolution updated successful!')
        print('Primary display not SPC Compliant..')

    return scrZ

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


def move_window():
	global timer, flag
	t_snooze = 30000
	trefresh = 2

	timer = Timer(trefresh, move_window)       	# Start threading.Timer()

	mySplash.bind("<Motion>", to_GUI)           # To GUI Menu
	mySplash.bind("<Escape>", to_GUI)           # To GUI Menu
	if sysrdy and not sysidl:
		to_AutoProcess(event=None)
	mySplash.config(cursor="none")

	# --------------------------------------------------[]
	print('\nSPC in Snooze mode, press Esc to resume')             # Snooze function
	mySplash.geometry(f"{w}x{h}+{int(randint(10, 1900))}+{int(randint(10, 1000))}")
	if not timer.is_alive():
		timer.start()
		flag = 'High'
	else:
		timer.cancel()
		flag = 'Low'
		mySplash.deiconify()

	timeB = time.time()  # start timing the entire loop
	tLapsed = (t_snooze / (trefresh * 1000)) - (timeB - timeA)
	print('TP01', (timeB - timeA))
	print('TP02', (t_snooze / (trefresh * 1000)))
	print('Exiting to Snooze in '+str(tLapsed)+' sec(s)...')
	mySplash.after(t_snooze, lambda: dScreen()) 	# set to x minutes

	return


def localSplash():
	global img, mySplash, splashInUse, w, h

	# Check screen resolution for SPC compliance & update res
	# ack_PLC = BooleanVar()
	print('\nChecking Viz-Screen Resolution...')
	scrRes = checkRes()
	if scrRes == '4k':
		w, h, f, xp1, xp2, yp = 1400, 800, 25, 500, 462, 570
	elif scrRes == '2k':
		w, h, f, xp1, xp2, yp = 780, 450, 14, 302, 285, 370   # 302
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
			s_label = Label(mySplash, image=img, text="Welcome to Magma SPC", font=12)
			# --------------------------------------------------------------------------
			Label(mySplash, text="Synchronous Multivariate SPC", width=28, justify=CENTER, font=("NovaMono", 18)).place(x=60, y=125)
			Label(mySplash, text="Advanced Statistical Processing & Visualization System", justify=CENTER, font=("NovaMono", 12)).place(x=65, y=155)
			Label(mySplash, text="Integrated into SCADA's (CF/PEEK) Manufacturing Process", justify=CENTER, font=("NovaMono", 12)).place(x=50, y=180)
			Label(mySplash, text=user_url, font=("NovaMono", 10)).place(x=120, y=200)
			Label(mySplash, textvariable=init_str, width=30, justify=CENTER, font=("NovaMono", 10)).place(x=140, y=240)  #
			s_label.pack()
		mySplash.update()

		r = 10
		for n in range(r):
			sleep(.2)
			if n <= (r - 2):
				init_str.set(f"Connecting to PLC Subsystem.{'.' * n}".ljust(27))
				connectPLC = xp.connectM2M(1, 2)  # Is the main PLC up?
				print('\nIs Available:', connectPLC)
				# ----------------------------------
				if connectPLC and sysrdy:
					print('\nChecking PLC Production Ready M2M acknowledgement... (1)')
					sendM2M_ACK()

				elif connectPLC and not sysrdy:
					print('Test DB Server readiness...')
					connectDB = checkSQL()
					if connectDB:
						print('Database Server is Up and running')
					else:
						pass
					print('\nStream 2:', connectDB)

				else:
					print('\nIndustrial Server is Offline...')
					pass
			else:
				init_str.set(f"Establishing Connectivity...{'.' * n}".ljust(27))
				# recall M2M connection again ----------- 1st time try
				if connectPLC and sysrdy:
					print('\nChecking Production Readiness... (1)')
					sendM2M_ACK()
				else:
					print('\nIndustrial Server is Offline...')
					pass
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
		if sysrdy:
			Label(mySplash, text="Realtime Processing!", justify=CENTER, font=("NovaMono", f)).place(x=xp1, y=yp)
		else:
			Label(mySplash, text="Post Processing Available!", justify=CENTER, font=("NovaMono", f)).place(x=xp2, y=yp)
		mySplash.after(30000, lambda: move_window())		# move splash windo 3 min
	mySplash.update_idletasks()


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
	global running

	# ----------------
	running = False
	# ----------------
	print('Snooze exiting to Splash...')
	sleep(.9)
	root.destroy()

	mSplash()		# call Spalsh method

	os._exit(0)
	return running


def toProcess(event):
	# ----------------
	running = False
	# ----------------
	print('Snooze exiting to Process...')
	sleep(.9)
	root.destroy()

	# mSplash()		# TODO to synchronousMain:function

	os._exit(0)
	return running


def showDefaultScreen():
	# global running
	# ------------------
	while running:
		# print('TP01', running)
		tk_Owner.set(value='Magma Global SPC\n')
		tkinter_time.set(value=strftime("%H:%M:%S"))
		tkinter_date.set(value=strftime("%A, %e %B"))
		root.update_idletasks()

		root.update()
		sleep(1)

	return # actSCR


def dScreen():
	global tk_Owner, tkinter_time, tkinter_date, root, running

	if flag == 'High':
		timer.cancel()				# Stop random screen saver
		sleep(.2)					# allow arb system recovery
		mySplash.destroy()		    # This method does the job but throws in an exception TODO -- Investigate and correct
		running = True
		sleep(.2)

	root = Tk()
	# Window Attributes ---------------#
	root.overrideredirect(True)
	root.wm_attributes("-transparentcolor", "gray99")
	root.bind("<Motion>", toSplash)    # Mouse action to Splash Screen
	root.bind("<Escape>", toSplash)    # Code from watchdog to Visualisation

	if sysrdy:
		toProcess()						# Exit to auto Processing
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
	print('Exiting Snoozer...')
	os._exit(0)
	# mySplash.quit()

	return


def st_autoPausePlay():
    return None