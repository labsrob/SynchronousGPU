# ------------------------------------------------------------------------
# Author: Dr RB Labs
# Developed for Magma Global - TechnipFMC Industrialization
# Email: robbielabs@uwl.ac.uk
# Copyright (C) 2023-2025, Robbie Labs
# ------------------------------------------------------------------------
from multiprocessing import Process
from threading import *
import asyncio
import time
from datetime import datetime
import os
import CommsPlc as plc

# ----------------------------------- Watch Dog Control --------------------------------------------------------------
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


def autoPausePlay():
	print('Checking SMC readiness...')
	try:
		sysRun = plc.readBool(db_number, s_offset[0], b_offset[0])		# False/True
		msctcp = plc.readInteger(db_number, s_offset[2], b_offset[0])   # Machine State Code (msc)
	except Exception as err:
		print(f"Exception Error: '{err}'")
		errorLog(f"{err}")
		print('Error loading autoplay..')
		sysRun = False		# Machine Unreacheable
		msctcp = 100		# Machine No state / undefined state

	# Obtain State machine code description -------------------
	rt_satus = dict(zip(machineCode_Data, codeDescript))
	msc_rt = rt_satus[msctcp]

	return sysRun, msctcp, msc_rt


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
	sysRun = plc.readBool(db_number, s_offset[0], b_offset[0])			# System is runing
	sysidl = plc.readBool(db_number, s_offset[0], b_offset[1])			# System idling
	sysrdy = plc.readBool(db_number, s_offset[0], b_offset[2])			# System Ready
	# ------------------------------------------------------
	rngONE = plc.readBool(db_number, s_offset[0], b_offset[3])			# Ring 1 is ready
	rngTWO = plc.readBool(db_number, s_offset[0], b_offset[4])  		# Ring 2 is ready
	rngTHR = plc.readBool(db_number, s_offset[0], b_offset[5])  		# Ring 3 is ready
	rngFOR = plc.readBool(db_number, s_offset[0], b_offset[6])  		# Ring 4 is ready
	# -------------------------------------------------------
	msctcp = plc.readInteger(db_number, s_offset[2], b_offset[0])		# Machine State Code (msc)
	won_NO = plc.readBool(db_number, s_offset[4], b_offset[0])			# Work Order Number
	prodTA = plc.readBool(db_number, s_offset[260], b_offset[0])		# Active DNV Process
	prodTB = plc.readBool(db_number, s_offset[261], b_offset[1])  		# Active MGM Process
	# -------------------------------------------------------
	tLayer = plc.readBool(db_number, s_offset[262], b_offset[0])		# Total required Layer
	cLayer = plc.readBool(db_number, s_offset[264], b_offset[0])  		# Current achieved layer

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
def watchDog(splash):
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
	splash.destroy()

	# Activate WatchDog function-------------------------------------[]
	rtError = False
	inProgress = False

	while True:
		try:
			# Update status every 10 sec ----------------------------[]
			sysRun, sysidl, sysrdy, rngONE, rngTWO, rngTHR, rngFOR, msctcp, won_NO, prodTA, prodTB, tLayer, cLayer = watchDogController()
			# -----------------------------------------------------[]
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

			elif sysidl and msctcp == 301:
				print('\nTCP in Standby mode...')

			elif sysrdy and msctcp == 110:
				print('\nTCP in Ready mode...')

			# When TCP is in Error, indicate the SMC to Vis Screen ------------------------[]
			elif msctcp == 111 or msctcp == 261 or msctcp == 325 or msctcp == 438 or msctcp == 515:
				state = codeDescript[10]  # TCP in Categorised process Error state --------[]
				print('\nTCP in '+state)

			elif msctcp == machineCode_Data[0]:
				state = codeDescript[0]		# Unknown State, Call Engineering Team --------[]
				print('\nTCP in '+state)

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


