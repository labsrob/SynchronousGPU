# ----------------------------------------------------------------------
" Program: Communication protocol with Magma TCP01 Project"
# Editor & Author: Robert B. Labs,
# Reviewer:
# ======================================================================
import snap7
from datetime import datetime
from time import sleep
import time
from tkinter import messagebox, ttk

# ---------------------------------------------------------------------------
Ring1ON, Ring2ON, Ring3ON, Ring4ON = 0, 0, 0, 0,

Hist_xUCL, Hist_xLCL, Hist_XmL, Hist_SmL, Hist_sUCL, Hist_sLCL = 0, 0, 0, 0, 0, 0
ShiftsStarts, ShiftsEnds, SampleSize, SampleType, UseHistLimits = 0, 0, 0, 0, 0
MonitorLaserPower, MonitorTapeSpeed, MonitorLaserAngle = 0, 0, 0

# DNV Process Parameters -- Roller Force, Tape Speed, Tape Angle, Tape Temp, Temp Ratio, Tape Gap
y_rp, y_ts, y_ta, y_tt, y_st, y_tg = [], [], [], [], [], []
array2d, y_list, Idx1, y_common, array2D = [], [], [], [], []
y_lp, y_la = [], []
# Define 2 dimension arrays for RT production data ---------[]

# --------------------------------------------------------------------------[]
# Constants: Process capability with historical set limits -----------------[]
A3 = [0.975, 0.789, 0.680, 0.6327, 0.606, 0.5525]       # 10, 15, 20, 23, 25, 30  sample sizes respectively
B3 = [0.284, 0.428, 0.510, 0.5452, 0.565, 0.6044]       # 10, 15, 20, 23, 25, 30  sample sizes respectively
B4 = [1.716, 1.572, 1.490, 1.4548, 1.435, 1.3956]       # 10, 15, 20, 23, 25, 30

# default settings: connect Snap7 Server -----------------------------------
# Initiate connection when PLC is online and prevent double instances
connectPLC = False
TCP01_IP = '192.168.100.100'  		# Targeted PLC Device
RACK = 0							# Designated Hardware Rack number
SLOT = 1							# Designated hardware Slot number
plc = snap7.client.Client()

db_number, start_offset, bit_offset = 89, 0, 0
start_offset1, bit_offset1 = 2, 0
value, data = True, False  			# 1 = true | 0 = false

start_address = 0  					# starting address
r_length = 4  						# double word (4 Bytes)
b_length = 1  						# boolean size = 1 Byte
r_data = 52.4
initialise = 0
called = False						# only applicable to SPC class
# --------------------------------------------------------------------------
"""
Windows Platform:

The system library iphlpapi.dll is used, but it’s is loaded dynamically because 
it’s not officially supported by Microsoft (even if it is present in all platforms 
and now it’s fully documented by MSDN).

If its load fails (very rare case), an ICMP socket is created to perform the ping. 
We use it as B-plan since we need administrative privileges to create RAW sockets 
in Vista/Windows 7/Windows 8.
"""


def errorNoconnect():
	messagebox.showerror("Disconnect Alert", "Invalid request, no active connection(s) found.")


def errorLog(err):
	fileName = datetime.now().strftime('M2MLog '+"%Y-%m-%d")
	event = datetime.now().strftime("%Y-%m-%d %H:%M.%S")
	errorlogFile = str(fileName)
	f = open('.\\RuntimeLog\\'+errorlogFile+".txt", "a")
	f.write(event+' --- '+err+'\n')
	f.close()


def successNote():
	plc_info2 = plc.get_connected()  # Return connection status
	print(f'\nConnection Successfully established:, {plc_info2}')

	plc_info = plc.get_cpu_info()  # Retrieves CPU State from Client
	print(f'Module Type:,{plc_info.ModuleTypeName}')
	print(f'PLC State:,{plc_info}')
	return


def check_PLC_connect():
	if connectPLC:
		active_conn = 'true'
	else:
		active_conn = 'false'

	return active_conn


def disconnct_PLC():
	state = check_PLC_connect()
	if state == 'true':
		plc.disconnect(TCP01_IP, RACK, SLOT)
	else:
		errorNoconnect()
		state = 'false'
	return state


def connectM2M():
	global connectPLC, plc, err
	retry = 0

	while not connectPLC and retry < 5:
		sleep(2)		# Pause for connection to be through
		# continuously try to connect to PLC or set trial times using while loop
		# if not plc.get_connected() or plc.get_cpu_state() == 'S7CpuStatusUnknown':
		try:
			# ------------------------------------------------------------------------------
			print('Testing PLC connection...')
			plc.connect(TCP01_IP, RACK, SLOT)  	# Details of TCP/IP Connection (from HW settings)
			# set connectPLC bit to high/low for future uses----

		except Exception as err:
			connectPLC = False
			print(f"Error: '{err}'")
			errorLog(f"{err}")
			sleep(.5)
		else:
			if plc.get_connected() and plc.get_cpu_state() != 'S7CpuStatusUnknown':
				connectPLC = True
				# print('Connection state is:', connectPLC)
				successNote()
				print("\nM2M link established")
			else:
				plc.disconnect()        # destroy()	/ safe function
				connectPLC = False		# set bit to low
				errorLog('Issues with M2M Connection')
				print('Issues with M2M connection, try again later..')
		retry += 1

	return connectPLC
# ===================================================================== #
# establish PLC connection -----
# connectM2M()


def readBool(db_number, start_offset, bit_offset):
	reading = plc.db_read(db_number, start_offset, b_length)
	a = snap7.util.get_bool(reading, 0, bit_offset)
	print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
	return a


def readReal(db_number, start_offset, bit_offset):
	reading = plc.db_read(db_number, start_offset, r_length)
	a = snap7.util.get_real(reading, 0)
	# print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
	return a


def readInteger(db_number, start_offset, bit_offset):
	reading = plc.db_read(db_number, start_offset, r_length)
	a = snap7.util.get_int(reading, 0)
	# print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
	return a


def readString(db_number, start_offset, bit_offset):
	r_length = 16
	reading = plc.db_read(db_number, start_offset, r_length)
	a = snap7.util.get_string(reading, 0)
	print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
	return a

# ----------------------------------------------------------------------------------------------------------------
def writeBool(db_number, start_offset, bit_offset, value):
	bArray = plc.db_read(db_number, start_offset, b_length)    		# (db, start offset, [b_length = read 1 byte])
	snap7.util.set_bool(bArray, 0, bit_offset, value)    			# (value 1= true;0=false)
	plc.db_write(db_number, start_offset, bArray)       			# write back the bytearray
	return 	# None


# Write TrigValues for: R1H1/R1H2/R1H3/R1H4 | R2H1/R2H2/R2H3/R2H4 | R3H1/R3H2/R3H3/R3H4 | R4H1/R4H2/R4H3/R4H4 ---[]
# -----------------------------------------------------------------------------------------------------------------

def writeReal(db_number, start_offset, r_data):
	# reading = plc.db_read(db_number, start_offset, r_length)
	data = bytearray(4)
	snap7.util.set_real(data, 0, r_data)
	plc.db_write(db_number, start_offset, data)
	return

def writeInteger(db_number, start_offset, r_data):
	# reading = plc.db_read(db_number, start_offset, r_length)
	data = bytearray(4)
	snap7.util.set_int(data, 0, r_data)
	plc.db_write(db_number, start_offset, data)
	return


# Arrays: Read once, write into SPC INI config -----------------------------------------------------------------[]
# Obtain SCADA user metrics from PLC and save into config.ini
# This functions runs after it's launched by a remote SCADA operator ---


class spcMetricsModule(object):
	if not initialise:
		# called = False
		initialise = 1
		called = False
		print('\nInitialising SPC Metrics Module...')
	if initialise and called:
		print('\nOne-time callable function - tape laying process...')
		called = True

	def checkhistDev(cls, xUCL, MeanP, sampSiz):
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
		stdDev = (xUCL - MeanP) / const1

		sUCL = (const3 * stdDev)  # Upper control limits of 1 std dev
		sLCL = (const2 * stdDev)  # Lower control limits of 1 Std dev

		return sUCL, sLCL, stdDev		# Compute for S-Chart Plot

	# function to compute metrics for historical limits from SCADA----------------[]
	def historical(cls, xUCL, xLCL, sampSiz):
		global xBarM, sBarM, sUCL, sLCL
		try:
			if xUCL != 0 and xLCL != 0:
				# Compute XBar mean / center line
				xBarM = float(xLCL) + ((float(xUCL) - float(xLCL)) / 2)
				print('XBar Mean', xBarM)
				# Compute for S-Chart UCL/LCL in the function ---
				sUCL, sLCL, sBarM = spcMetricsModule.checkhistDev(cls, xUCL, xBarM, sampSiz)
			else:
				print('No valid historical limits, switch to default')
		except KeyboardInterrupt as err:
			errorLog(err)
			pass
		# output S chart limits ---
		return sUCL, sLCL, xBarM, sBarM

	def saveMetric(cls):		# SPC downloading SCADA metrics from PLC
		global called

		if cls.called:
			print("Function is a run once type. Already executed")
			return
		else:
			try:
				import loadSPCConfig as xt

				# Access PLC arrays --------------------------------------------------
				sta_offset = [1122, 1126, 1130, 1134, 1138, 1142, 1146, 1150, 1154, 1158, 1162, 1166, 76, 78, 80, 362,
							  618, 360, ]
				bit_offset = [0, 1, 2]

				# Obtain unique values for INI files -------------------
				xuclA = readReal(db_number, sta_offset[0], bit_offset[0])
				xlclA = readReal(db_number, sta_offset[1], bit_offset[0])
				# -----------
				xuclB = readReal(db_number, sta_offset[2], bit_offset[0])
				xlclB = readReal(db_number, sta_offset[3], bit_offset[0])
				#------------
				xuclC = readReal(db_number, sta_offset[4], bit_offset[0])
				xlclC = readReal(db_number, sta_offset[5], bit_offset[0])
				# ----------
				xuclD = readReal(db_number, sta_offset[6], bit_offset[0])
				xlclD = readReal(db_number, sta_offset[7], bit_offset[0])
				# ---------
				xuclE = readReal(db_number, sta_offset[8], bit_offset[0])
				xlclE = readReal(db_number, sta_offset[9], bit_offset[0])
				# ---------
				xuclF = readReal(db_number, sta_offset[10], bit_offset[0])
				xlclF = readReal(db_number, sta_offset[11], bit_offset[0])

				# Using Historical Limits ------------------------------
				usehl = readBool(db_number, sta_offset[12], bit_offset[0])
				gropz = readInteger(db_number, sta_offset[13], bit_offset[0])
				# -------------------------------------------------------

				if usehl == True:
					uhl = 1
					Smodel = 0
				else:
					uhl = 0
					Smodel = 1
				# Compute historical mean from UCL/LCL and save into .INI ------------------------[]
				suclA, slclA, xmeanA, smeanA = spcMetricsModule.historical(cls, xuclA, xlclA, gropz)
				suclB, slclB, xmeanB, smeanB = spcMetricsModule.historical(cls, xuclB, xlclB, gropz)
				suclC, slclC, xmeanC, smeanC = spcMetricsModule.historical(cls, xuclC, xlclC, gropz)
				suclD, slclD, xmeanD, smeanD = spcMetricsModule.historical(cls, xuclD, xlclD, gropz)
				suclE, slclE, xmeanE, smeanE = spcMetricsModule.historical(cls, xuclE, xlclE, gropz)
				suclF, slclF, xmeanF, smeanF = spcMetricsModule.historical(cls, xuclF, xlclF, gropz)

				shfts = readString(db_number, sta_offset[15], bit_offset[0])
				shfte = readString(db_number, sta_offset[16], bit_offset[0])

				gstepVal = readString(db_number, sta_offset[14], bit_offset[0])
				if str(gstepVal) == 'Domino':
					gstep = 1
				elif gstepVal == 'Discrete':
					gstep = 2
				else:
					print('invalid values')
				# monitorable process ------------
				laserp = readBool(db_number, sta_offset[17], bit_offset[0])
				tapesp = readBool(db_number, sta_offset[17], bit_offset[1])
				langle = readBool(db_number, sta_offset[17], bit_offset[2])

				if laserp == False:
					laserp = 0
				else:
					laserp = 1

				if tapesp == False:
					tapesp = 0
				else:
					tapesp = 1

				if langle == False:
					langle = 0
				else:
					langle = 1

				# Specify optimization technique from SCADA ------
				rtop1, rtop2 = 1, 0  # (Default to DrLabs RT Mem Optimisation | Pythonian optimisation)

				# From SCADA write User specified metrics to config.INI files -----------------
				xt.writeSPCconfig(rtop1, xuclA, xlclA, xuclD, xlclD, xuclE, xlclE, xuclF, xlclF, xuclB, xlclB, xuclC,
								  xlclC, xmeanA, xmeanD, xmeanE, xmeanF, xmeanB, xmeanC, suclA, slclA, suclD, slclD,
								  suclE, slclE, suclF, slclF, suclB, slclB, suclC, slclC, smeanA, smeanD, smeanE,
								  smeanF, smeanB, smeanC, shfts, shfte, gropz, gstep, uhl, Smodel, laserp, tapesp, langle)


			except Exception as err:
				print(f"Connection Error: {err}")  	# catch whatever error raised
				errorLog(f"{err}") 					# log error

			cls.called = True						# Set Bit to High (True)

			return

# Allow SPC loading user values from SCADA once for every pipe laying process ----


def collectiveProcessDataRequest(nGZ, grp_step, fetch_no):
	"""
	nGZ     : User defined Sample size
	grp_step: Group Sample step
	fetch_no: Animation Fetch Cycle
	"""
	timei = time.time()
	# Get contigous data from PLC Stream --- Dealing with very volatile data frame.
	start_offset = [922, 926, 930, 934, 938, 942, 946, 950, 954, 958, 962, 966, 970, 974, 978, 982, 986, 988, 990,
					994, 996, 998, 990, 992, 996, 998, 1000, 1002, 1004, 1006, 1008, 1010, 1012, 1014, 1016, 1018,
					1020, 1022, 1024, 1026, 1028, 1030, 1032, 1034, 1036, 1038, 1040, 1042, 1044, 1046, 1048, 1050,
					1054, 1058, 1062, 1066, 1070, 1074, 1078, 1082, 1084, 1086, 1088, 1090, 1094, 1098, 1102, 1106,
					1110, 1114, 1118, 68, 900]
	bit_offset = [0, 1, 2]
	id1 = str(0)
	# ------------------------------------------------------------------------
	group_step = int(grp_step)  	# group size/ sample sze
	fetch_no = int(fetch_no)  		# dbfreq = TODO look into any potential conflict
	print('\nSAMPLE SIZE:', nGZ, '| SLIDE STEP:', int(grp_step), '| FETCH CYCLE:', fetch_no)

	# ------------- Consistency Logic ensure list is filled with predetermined elements --------------
	if group_step == 1:
		print('Domino step mode..')
		print('\nSINGLE STEP SLIDE')
		print('=================')
		print('Array length:', len(array2d), 'Fetch Value', fetch_no)
		if len(array2d) == nGZ and fetch_no > 0:
			print('TP A')
			n2fetch = fetch_no
		elif len(array2d) == nGZ and fetch_no < 1:
			print('TP B')
			n2fetch = 1
		elif len(array2d) >= nGZ and fetch_no > 0:
			print('TP C')
			n2fetch = (len(array2d) + fetch_no)
		elif len(array2d) >= nGZ and fetch_no < 1:
			print('TP D')
			n2fetch = 0
		else:
			print('TP E')
			n2fetch = nGZ
		print('Fetching...:', n2fetch)
		# Evaluate rows in each tables ---------------------[]
		idxA = int(id1) + fetch_no + 1
		if len(Idx1) > 1:
			del Idx1[:1]
		Idx1.append(idxA)
		print('Processing Query #:', idxA)

	elif group_step > 1:
		print('Discrete step mode..')
		print('\nSAMPLE SIZE SLIDE')
		print('=================')
		if fetch_no != 0 and len(array2d) >= nGZ:
			n2fetch = nGZ # (nGZ * fetch_no)
		else:
			n2fetch = nGZ  # fetch twice
		print('Fetching..', n2fetch)
		# Evaluate rows in each tables ---------------------[]
		idxA = int(id1) + (((fetch_no + 1) - 2) * nGZ) + 1
		if len(Idx1) > 1:
			del Idx1[:1]
		Idx1.append(idxA)
		print('Processing SQL Row #:', idxA)

	while True:
		try:
			# Pipe position ------------------------------------------- [82 column data] ------------------#
			Ppos = readReal(db_number, start_offset[68], bit_offset[0])  		# Sql Table 3 Ring-2 - 906.0
			y_list.append(Ppos)
			TLayer = readInteger(db_number, start_offset[69], bit_offset[0])  	# Sql Table 4 Ring-2 - 908.0
			y_list.append(TLayer)

			# ------------ Roller Pressure -------------------------------------#
			RP1 = readInteger(db_number, start_offset[0], bit_offset[0])  		# Sql Table 1 Ring-1 - 902.0
			y_list.append(RP1)
			RP2 = readInteger(db_number, start_offset[1], bit_offset[0])  		# Sql Table 2 Ring-1 - 904.0
			y_list.append(RP2)
			RP3 = readInteger(db_number, start_offset[2], bit_offset[0])  		# Sql Table 3 Ring-2 - 906.0
			y_list.append(RP3)
			RP4 = readInteger(db_number, start_offset[3], bit_offset[0])  		# Sql Table 4 Ring-2 - 908.0
			y_list.append(RP4)
			# R2 ------
			RP5 = readInteger(db_number, start_offset[4], bit_offset[0])  		# Sql Table 1 Ring-1 - 902.0
			y_list.append(RP5)
			RP6 = readInteger(db_number, start_offset[5], bit_offset[0])  		# Sql Table 2 Ring-1 - 904.0
			y_list.append(RP6)
			RP7 = readInteger(db_number, start_offset[6], bit_offset[0])  		# Sql Table 3 Ring-2 - 906.0
			y_list.append(RP7)
			RP8 = readInteger(db_number, start_offset[7], bit_offset[0])  		# Sql Table 4 Ring-2 - 908.0
			y_list.append(RP8)
			# R3 -------
			RP9 = readInteger(db_number, start_offset[8], bit_offset[0])  		# Sql Table 1 Ring-1 - 902.0
			y_list.append(RP9)
			RP10 = readInteger(db_number, start_offset[9], bit_offset[0])  		# Sql Table 2 Ring-1 - 904.0
			y_list.append(RP10)
			RP11 = readInteger(db_number, start_offset[10], bit_offset[0])  	# Sql Table 3 Ring-2 - 906.0
			y_list.append(RP11)
			RP12 = readInteger(db_number, start_offset[11], bit_offset[0])  	# Sql Table 4 Ring-2 - 908.0
			y_list.append(RP12)
			# R4 ------
			RP13 = readInteger(db_number, start_offset[12], bit_offset[0])  	# Sql Table 1 Ring-1 - 902.0
			y_list.append(RP13)
			RP14 = readInteger(db_number, start_offset[13], bit_offset[0])  	# Sql Table 2 Ring-1 - 904.0
			y_list.append(RP14)
			RP15 = readInteger(db_number, start_offset[14], bit_offset[0])  	# Sql Table 3 Ring-2 - 906.0
			y_list.append(RP15)
			RP16 = readInteger(db_number, start_offset[15], bit_offset[0])  	# Sql Table 4 Ring-2 - 908.0
			y_list.append(RP16)

			# -------------------------Tape Speed ------------------------------#
			# Tape Speed --------R1
			TS1 = readInteger(db_number, start_offset[64], bit_offset[0])  # Sql Table 1 Ring-1 - 902.0
			y_list.append(TS1)
			TS2 = readInteger(db_number, start_offset[65], bit_offset[0])  # Sql Table 2 Ring-1 - 904.0
			y_list.append(TS2)
			TS3 = readInteger(db_number, start_offset[66], bit_offset[0])  # Sql Table 3 Ring-2 - 906.0
			y_list.append(TS3)
			TS4 = readInteger(db_number, start_offset[67], bit_offset[0])  # Sql Table 4 Ring-2 - 908.0
			y_list.append(TS4)
			# Tape Speed --------R2
			TS1 = readInteger(db_number, start_offset[64], bit_offset[0])  # Sql Table 1 Ring-1 - 902.0
			y_list.append(TS1)
			TS2 = readInteger(db_number, start_offset[65], bit_offset[0])  # Sql Table 2 Ring-1 - 904.0
			y_list.append(TS2)
			TS3 = readInteger(db_number, start_offset[66], bit_offset[0])  # Sql Table 3 Ring-2 - 906.0
			y_list.append(TS3)
			TS4 = readInteger(db_number, start_offset[67], bit_offset[0])  # Sql Table 4 Ring-2 - 908.0
			y_list.append(TS4)
			# Tape Speed --------R3
			TS1 = readInteger(db_number, start_offset[64], bit_offset[0])  # Sql Table 1 Ring-1 - 902.0
			y_list.append(TS1)
			TS2 = readInteger(db_number, start_offset[65], bit_offset[0])  # Sql Table 2 Ring-1 - 904.0
			y_list.append(TS2)
			TS3 = readInteger(db_number, start_offset[66], bit_offset[0])  # Sql Table 3 Ring-2 - 906.0
			y_list.append(TS3)
			TS4 = readInteger(db_number, start_offset[67], bit_offset[0])  # Sql Table 4 Ring-2 - 908.0
			y_list.append(TS4)
			# Tape Speed --------R4
			TS1 = readInteger(db_number, start_offset[64], bit_offset[0])  # Sql Table 1 Ring-1 - 902.0
			y_list.append(TS1)
			TS2 = readInteger(db_number, start_offset[65], bit_offset[0])  # Sql Table 2 Ring-1 - 904.0
			y_list.append(TS2)
			TS3 = readInteger(db_number, start_offset[66], bit_offset[0])  # Sql Table 3 Ring-2 - 906.0
			y_list.append(TS3)
			TS4 = readInteger(db_number, start_offset[67], bit_offset[0])  # Sql Table 4 Ring-2 - 908.0
			y_list.append(TS4)

			# ------------------------ Tape Temperature Data ---------------------------------------------#
			# Tape Temperature ---R1
			TT1 = readInteger(db_number, start_offset[16], bit_offset[0])  		# Sql Table 1 Ring-1 - 902.0
			y_list.append(TT1)
			TT2 = readInteger(db_number, start_offset[17], bit_offset[0])  		# Sql Table 2 Ring-1 - 904.0
			y_list.append(TT2)
			TT3 = readInteger(db_number, start_offset[18], bit_offset[0])  		# Sql Table 3 Ring-2 - 906.0
			y_list.append(TT3)
			TT4 = readInteger(db_number, start_offset[19], bit_offset[0])  		# Sql Table 4 Ring-2 - 908.0
			y_list.append(TT4)
			# R2 ------
			TT5 = readInteger(db_number, start_offset[20], bit_offset[0])  		# Sql Table 1 Ring-1 - 902.0
			y_list.append(TT5)
			TT6 = readInteger(db_number, start_offset[21], bit_offset[0])  		# Sql Table 2 Ring-1 - 904.0
			y_list.append(TT6)
			TT7 = readInteger(db_number, start_offset[22], bit_offset[0])  		# Sql Table 3 Ring-2 - 906.0
			y_list.append(TT7)
			TT8 = readInteger(db_number, start_offset[23], bit_offset[0])  		# Sql Table 4 Ring-2 - 908.0
			y_list.append(TT8)
			# R3 ------
			TT9 = readInteger(db_number, start_offset[24], bit_offset[0])  		# Sql Table 1 Ring-1 - 902.0
			y_list.append(TT9)
			TT10 = readInteger(db_number, start_offset[25], bit_offset[0])  	# Sql Table 2 Ring-1 - 904.0
			y_list.append(TT10)
			TT11 = readInteger(db_number, start_offset[26], bit_offset[0])  	# Sql Table 3 Ring-2 - 906.0
			y_list.append(TT11)
			TT12 = readInteger(db_number, start_offset[27], bit_offset[0])  	# Sql Table 4 Ring-2 - 908.0
			y_list.append(TT12)
			# R4 ------
			TT13 = readInteger(db_number, start_offset[28], bit_offset[0])  	# Sql Table 1 Ring-1 - 902.0
			y_list.append(TT13)
			TT14 = readInteger(db_number, start_offset[29], bit_offset[0])  	# Sql Table 2 Ring-1 - 904.0
			y_list.append(TT14)
			TT15 = readInteger(db_number, start_offset[30], bit_offset[0])  	# Sql Table 3 Ring-2 - 906.0
			y_list.append(TT15)
			TT16 = readInteger(db_number, start_offset[31], bit_offset[0])  	# Sql Table 4 Ring-2 - 908.0
			y_list.append(TT16)

			# ------------------- Tape/Sub Ratio or Delta Temp Temperature PLC calculated  -------------#
			# R1 ------
			TR1 = readInteger(db_number, start_offset[32], bit_offset[0])  		# Sql Table 1 Ring-1 - 902.0
			y_list.append(TR1)
			TR2 = readInteger(db_number, start_offset[33], bit_offset[0])  		# Sql Table 2 Ring-1 - 904.0
			y_list.append(TR2)
			TR3 = readInteger(db_number, start_offset[34], bit_offset[0])  		# Sql Table 3 Ring-2 - 906.0
			y_list.append(TR3)
			TR4 = readInteger(db_number, start_offset[35], bit_offset[0])  		# Sql Table 4 Ring-2 - 908.0
			y_list.append(TR4)
			# R2 ------
			TR5 = readInteger(db_number, start_offset[36], bit_offset[0])  		# Sql Table 1 Ring-1 - 902.0
			y_list.append(TR5)
			TR6 = readInteger(db_number, start_offset[37], bit_offset[0])  		# Sql Table 2 Ring-1 - 904.0
			y_list.append(TR6)
			TR7 = readInteger(db_number, start_offset[38], bit_offset[0])  		# Sql Table 3 Ring-2 - 906.0
			y_list.append(TR7)
			TR8 = readInteger(db_number, start_offset[39], bit_offset[0])  		# Sql Table 4 Ring-2 - 908.0
			y_list.append(TR8)
			# R3 ------
			TR9 = readInteger(db_number, start_offset[40], bit_offset[0])  		# Sql Table 1 Ring-1 - 902.0
			y_list.append(TR9)
			TR10 = readInteger(db_number, start_offset[41], bit_offset[0])  	# Sql Table 2 Ring-1 - 904.0
			y_list.append(TR10)
			TR11 = readInteger(db_number, start_offset[42], bit_offset[0])  	# Sql Table 3 Ring-2 - 906.0
			y_list.append(TR11)
			TR12 = readInteger(db_number, start_offset[43], bit_offset[0])  	# Sql Table 4 Ring-2 - 908.0
			y_list.append(TR12)
			# R4 ------
			TR13 = readInteger(db_number, start_offset[44], bit_offset[0])  	# Sql Table 1 Ring-1 - 902.0
			y_list.append(TR13)
			TR14 = readInteger(db_number, start_offset[45], bit_offset[0])  	# Sql Table 2 Ring-1 - 904.0
			y_list.append(TR14)
			TR15 = readInteger(db_number, start_offset[46], bit_offset[0])  	# Sql Table 3 Ring-2 - 906.0
			y_list.append(TR15)
			TR16 = readInteger(db_number, start_offset[47], bit_offset[0])  	# Sql Table 4 Ring-2 - 908.0
			y_list.append(TR16)

			# --------------------------------- Tape Gap Measurement Data ----------------------------------
			TG1 = readInteger(db_number, start_offset[48], bit_offset[0])  		# Sql Table 1 Ring-1 - 902.0
			y_list.append(TG1)
			TG2 = readInteger(db_number, start_offset[49], bit_offset[0])  		# Sql Table 2 Ring-1 - 904.0
			y_list.append(TG2)
			TG3 = readInteger(db_number, start_offset[50], bit_offset[0])  		# Sql Table 3 Ring-2 - 906.0
			y_list.append(TG3)
			TG4 = readInteger(db_number, start_offset[51], bit_offset[0])  		# Sql Table 4 Ring-2 - 908.0
			y_list.append(TG4)
			TG5 = readInteger(db_number, start_offset[52], bit_offset[0])  		# Sql Table 1 Ring-1 - 902.0
			y_list.append(TG5)
			TG6 = readInteger(db_number, start_offset[53], bit_offset[0])  		# Sql Table 2 Ring-1 - 904.0
			y_list.append(TG6)
			TG7 = readInteger(db_number, start_offset[54], bit_offset[0])  		# Sql Table 3 Ring-2 - 906.0
			y_list.append(TG7)
			TG8 = readInteger(db_number, start_offset[55], bit_offset[0])  		# Sql Table 4 Ring-2 - 908.0
			y_list.append(TG8)

			# -------------------------- Monitoring Parameters (Laser Power, Laser Angle, Tape Speed -------
			# Laser Power -------
			LP1 = readInteger(db_number, start_offset[56], bit_offset[0])  		# Sql Table 1 Ring-1 - 902.0
			y_list.append(LP1)
			LP2 = readInteger(db_number, start_offset[57], bit_offset[0])  		# Sql Table 2 Ring-1 - 904.0
			y_list.append(LP2)
			LP3 = readInteger(db_number, start_offset[58], bit_offset[0])  		# Sql Table 3 Ring-2 - 906.0
			y_list.append(LP3)
			LP4 = readInteger(db_number, start_offset[59], bit_offset[0])  		# Sql Table 4 Ring-2 - 908.0
			y_list.append(LP4)

			# Laser Angle ------
			LA1 = readInteger(db_number, start_offset[60], bit_offset[0])  # Sql Table 1 Ring-1 - 902.0
			y_list.append(LA1)
			LA2 = readInteger(db_number, start_offset[61], bit_offset[0])  # Sql Table 2 Ring-1 - 904.0
			y_list.append(LA2)
			LA3 = readInteger(db_number, start_offset[62], bit_offset[0])  # Sql Table 3 Ring-2 - 906.0
			y_list.append(LA3)
			LA4 = readInteger(db_number, start_offset[63], bit_offset[0])  # Sql Table 4 Ring-2 - 908.0
			y_list.append(LA4)


			# Deposit list column content into rows array ----------[]
			if len(y_list) > 82:
				del y_list[0:(len(y_list) - 82)]				# trim columns to shape
				print('\nResetting Column Size...', len(y_list))

			array2d.append(y_list)
			print('\nLIST COLUMN:', len(y_list))
			print('LIST D_ROWS:', len(array2d))
			print('Next Break @:', (n2fetch + nGZ) - len(array2d))

			if group_step == 1:
				# Beautiful Purgatory Procedure ------------------------------[]
				if len(array2d) >= n2fetch and fetch_no <= 20:
					del array2d[0:(len(array2d) - nGZ)]  			# [static window]
					print('Resetting Rows on Static.', len(array2d))
					break
				elif len(array2d) >= 21 and (fetch_no + 1) >= 21:
					del array2d[0:(len(array2d) - fetch_no)]  		# [moving window]
					print('Resetting Rows on Move..', len(array2d))
					break
				else:
					pass
			else:
				if group_step > 1 and len(array2d) == n2fetch and fetch_no <= 20:
					print('Keeping No of Rows on Static... Array Size:', len(array2d))
					break
				if group_step > 1 and len(array2d) >= (nGZ + n2fetch) and fetch_no <= 21:
					del array2d[0:(len(array2d) - nGZ)]
					print('Resetting Rows on Static... Array Size:', len(array2d))
					break
				elif group_step > 1 and len(array2d) >= (nGZ + n2fetch) and fetch_no >= 21:
					del array2d[0:(len(array2d) - fetch_no)]
					print('Resetting Rows on Move.... Array Size:', len(array2d))
					break
				print('Breaking at..', (n2fetch + nGZ), ' Array Length:', len(array2d))
				# break
			y_list.clear()  							# Clear content of the list for new round trip

		except Exception as err:
			print(f"Exception Error: '{err}'")

		finally:
			timef = time.time()
			print(f"Data Fetch Time: {timef - timei} sec", 'Fetch No:', fetch_no, '\n')

	return array2d


# saveMetric() #---------------- TODO -----------------------------------------------------------------------------[]
def plot_rt_LP():
	# Laser Power Averages fo each ring directly from PLC simotion values ------R1
	LPR1 = readInteger(db_number, start_offset[0], bit_offset[0])  # Sql Table 1 Ring-1 - 902.0
	y_lp.append(LPR1)
	LPR2 = readInteger(db_number, start_offset[1], bit_offset[0])  # Sql Table 2 Ring-1 - 904.0
	y_lp.append(LPR2)
	LPR3 = readInteger(db_number, start_offset[2], bit_offset[0])  # Sql Table 3 Ring-2 - 906.0
	y_lp.append(LPR3)
	LPR4 = readInteger(db_number, start_offset[3], bit_offset[0])  # Sql Table 4 Ring-2 - 908.0
	y_lp.append(LPR4)

	return

def plot_rt_LA():
	# Laser Angle Averages fo each ring directly from PLC simotion values ------R1
	LAR1 = readInteger(db_number, start_offset[0], bit_offset[0])  # Sql Table 1 Ring-1 - 902.0
	y_la.append(LAR1)
	LAR2 = readInteger(db_number, start_offset[1], bit_offset[0])  # Sql Table 2 Ring-1 - 904.0
	y_la.append(LAR2)
	LAR3 = readInteger(db_number, start_offset[2], bit_offset[0])  # Sql Table 3 Ring-2 - 906.0
	y_la.append(LAR3)
	LAR4 = readInteger(db_number, start_offset[3], bit_offset[0])  # Sql Table 4 Ring-2 - 908.0
	y_la.append(LAR4)

	return

# --------------------- TODO ---------------------------------------------------[set memory offset in PLC]
def plot_rt_HT():
	# Laser Angle Averages fo each ring directly from PLC simotion values ------R1
	LAR1 = readInteger(db_number, start_offset[0], bit_offset[0])  # Sql Table 1 Ring-1 - 902.0
	y_la.append(LAR1)
	LAR2 = readInteger(db_number, start_offset[1], bit_offset[0])  # Sql Table 2 Ring-1 - 904.0
	y_la.append(LAR2)
	LAR3 = readInteger(db_number, start_offset[2], bit_offset[0])  # Sql Table 3 Ring-2 - 906.0
	y_la.append(LAR3)
	LAR4 = readInteger(db_number, start_offset[3], bit_offset[0])  # Sql Table 4 Ring-2 - 908.0
	y_la.append(LAR4)

	return

# --------------------- TODO ---------------------------------------------------[set memory offset in PLC]
def plot_rt_DL():
	# Laser Angle Averages fo each ring directly from PLC simotion values ------R1
	LAR1 = readInteger(db_number, start_offset[0], bit_offset[0])  # Sql Table 1 Ring-1 - 902.0
	y_la.append(LAR1)
	LAR2 = readInteger(db_number, start_offset[1], bit_offset[0])  # Sql Table 2 Ring-1 - 904.0
	y_la.append(LAR2)
	LAR3 = readInteger(db_number, start_offset[2], bit_offset[0])  # Sql Table 3 Ring-2 - 906.0
	y_la.append(LAR3)
	LAR4 = readInteger(db_number, start_offset[3], bit_offset[0])  # Sql Table 4 Ring-2 - 908.0
	y_la.append(LAR4)

	return

def getData_rf():
	# Roller Force ------R1
	RP1 = readInteger(db_number, start_offset[0], bit_offset[0])  # Sql Table 1 Ring-1 - 902.0
	y_rp.append(RP1)
	RP2 = readInteger(db_number, start_offset[1], bit_offset[0])  # Sql Table 2 Ring-1 - 904.0
	y_rp.append(RP2)
	RP3 = readInteger(db_number, start_offset[2], bit_offset[0])  # Sql Table 3 Ring-2 - 906.0
	y_rp.append(RP3)
	RP4 = readInteger(db_number, start_offset[3], bit_offset[0])  # Sql Table 4 Ring-2 - 908.0
	y_rp.append(RP4)
	# Roller Force ------R2
	RP5 = readInteger(db_number, start_offset[4], bit_offset[0])  # Sql Table 1 Ring-1 - 902.0
	y_rp.append(RP5)
	RP6 = readInteger(db_number, start_offset[5], bit_offset[0])  # Sql Table 2 Ring-1 - 904.0
	y_rp.append(RP6)
	RP7 = readInteger(db_number, start_offset[6], bit_offset[0])  # Sql Table 3 Ring-2 - 906.0
	y_rp.append(RP7)
	RP8 = readInteger(db_number, start_offset[7], bit_offset[0])  # Sql Table 4 Ring-2 - 908.0
	y_rp.append(RP8)
	# Roller Force ------R3
	RP9 = readInteger(db_number, start_offset[8], bit_offset[0])  # Sql Table 1 Ring-1 - 902.0
	y_rp.append(RP9)
	RP10 = readInteger(db_number, start_offset[9], bit_offset[0])  # Sql Table 2 Ring-1 - 904.0
	y_rp.append(RP10)
	RP11 = readInteger(db_number, start_offset[10], bit_offset[0])  # Sql Table 3 Ring-2 - 906.0
	y_rp.append(RP11)
	RP12 = readInteger(db_number, start_offset[11], bit_offset[0])  # Sql Table 4 Ring-2 - 908.0
	y_rp.append(RP12)
	# Roller Force ------R4
	RP13 = readInteger(db_number, start_offset[12], bit_offset[0])  # Sql Table 1 Ring-1 - 902.0
	y_rp.append(RP13)
	RP14 = readInteger(db_number, start_offset[13], bit_offset[0])  # Sql Table 2 Ring-1 - 904.0
	y_rp.append(RP14)
	RP15 = readInteger(db_number, start_offset[14], bit_offset[0])  # Sql Table 3 Ring-2 - 906.0
	y_rp.append(RP15)
	RP16 = readInteger(db_number, start_offset[15], bit_offset[0])  # Sql Table 4 Ring-2 - 908.0
	y_rp.append(RP16)

	return y_rp


# --------------------- TODO ---------------------------------------------------[Tape Temperature db]
def getData_tt(db_number):
	# Tape Temp --------R1
	TS0 = readInteger(db_number, start_offset[0], bit_offset[0])  # cLayer
	y_tt.append(TS0)
	TS1 = readInteger(db_number, start_offset[2], bit_offset[0])  # R1H1
	y_tt.append(TS1)
	TS2 = readInteger(db_number, start_offset[4], bit_offset[0])  # R1H2
	y_tt.append(TS2)
	TS3 = readInteger(db_number, start_offset[6], bit_offset[0])  # R1H3
	y_tt.append(TS3)
	TS4 = readInteger(db_number, start_offset[8], bit_offset[0])  # R1H4
	y_tt.append(TS4)
	# Tape Temp --------R2
	TS1 = readInteger(db_number, start_offset[10], bit_offset[0])  # R2H1
	y_tt.append(TS1)
	TS2 = readInteger(db_number, start_offset[12], bit_offset[0])  # R2H2
	y_tt.append(TS2)
	TS3 = readInteger(db_number, start_offset[14], bit_offset[0])  # R2H3
	y_tt.append(TS3)
	TS4 = readInteger(db_number, start_offset[16], bit_offset[0])  # R2H4
	y_tt.append(TS4)
	# Tape Temp --------R3
	TS1 = readInteger(db_number, start_offset[18], bit_offset[0])  # R3H1
	y_tt.append(TS1)
	TS2 = readInteger(db_number, start_offset[20], bit_offset[0])  # R3H2
	y_tt.append(TS2)
	TS3 = readInteger(db_number, start_offset[22], bit_offset[0])  # R3H3
	y_tt.append(TS3)
	TS4 = readInteger(db_number, start_offset[24], bit_offset[0])  # R3H4
	y_tt.append(TS4)
	# Tape Temp --------R4
	TS1 = readInteger(db_number, start_offset[26], bit_offset[0])  # R4H1
	y_tt.append(TS1)
	TS2 = readInteger(db_number, start_offset[28], bit_offset[0])  # R4H2
	y_tt.append(TS2)
	TS3 = readInteger(db_number, start_offset[30], bit_offset[0])  # R4H3
	y_tt.append(TS3)
	TS4 = readInteger(db_number, start_offset[32], bit_offset[0])  # R4H4
	y_tt.append(TS4)

	return y_tt


# --------------------- TODO ---------------------------------------------------[set memory offset in PLC]

def getData_st():
	# ------------------------ Tape/Substrate Temp Ratio -------------------------#
	# Temperature Ratio ------ R1
	TT1 = readInteger(db_number, start_offset[16], bit_offset[0])  # Sql Table 1 Ring-1 - 902.0
	y_st.append(TT1)
	TT2 = readInteger(db_number, start_offset[17], bit_offset[0])  # Sql Table 2 Ring-1 - 904.0
	y_st.append(TT2)
	TT3 = readInteger(db_number, start_offset[18], bit_offset[0])  # Sql Table 3 Ring-2 - 906.0
	y_st.append(TT3)
	TT4 = readInteger(db_number, start_offset[19], bit_offset[0])  # Sql Table 4 Ring-2 - 908.0
	y_st.append(TT4)

	# Temperature Ratio ------ R2
	TT5 = readInteger(db_number, start_offset[20], bit_offset[0])  # Sql Table 1 Ring-1 - 902.0
	y_st.append(TT5)
	TT6 = readInteger(db_number, start_offset[21], bit_offset[0])  # Sql Table 2 Ring-1 - 904.0
	y_st.append(TT6)
	TT7 = readInteger(db_number, start_offset[22], bit_offset[0])  # Sql Table 3 Ring-2 - 906.0
	y_st.append(TT7)
	TT8 = readInteger(db_number, start_offset[23], bit_offset[0])  # Sql Table 4 Ring-2 - 908.0
	y_st.append(TT8)

	# Temperature Ratio ------ R3
	TT9 = readInteger(db_number, start_offset[24], bit_offset[0])  # Sql Table 1 Ring-1 - 902.0
	y_st.append(TT9)
	TT10 = readInteger(db_number, start_offset[25], bit_offset[0])  # Sql Table 2 Ring-1 - 904.0
	y_st.append(TT10)
	TT11 = readInteger(db_number, start_offset[26], bit_offset[0])  # Sql Table 3 Ring-2 - 906.0
	y_st.append(TT11)
	TT12 = readInteger(db_number, start_offset[27], bit_offset[0])  # Sql Table 4 Ring-2 - 908.0
	y_st.append(TT12)

	# Temperature Ratio ------ R4
	TT13 = readInteger(db_number, start_offset[28], bit_offset[0])  # Sql Table 1 Ring-1 - 902.0
	y_st.append(TT13)
	TT14 = readInteger(db_number, start_offset[29], bit_offset[0])  # Sql Table 2 Ring-1 - 904.0
	y_st.append(TT14)
	TT15 = readInteger(db_number, start_offset[30], bit_offset[0])  # Sql Table 3 Ring-2 - 906.0
	y_st.append(TT15)
	TT16 = readInteger(db_number, start_offset[31], bit_offset[0])  # Sql Table 4 Ring-2 - 908.0
	y_st.append(TT16)

	return y_st

def getData_tg():
	# --------------------------------- Tape Gap Measurement Data ----------------------------
	TG1 = readInteger(db_number, start_offset[48], bit_offset[0])  # Sql Table 1 Ring-1 - 902.0
	y_tg.append(TG1)
	TG2 = readInteger(db_number, start_offset[49], bit_offset[0])  # Sql Table 2 Ring-1 - 904.0
	y_tg.append(TG2)
	TG3 = readInteger(db_number, start_offset[50], bit_offset[0])  # Sql Table 3 Ring-2 - 906.0
	y_tg.append(TG3)
	TG4 = readInteger(db_number, start_offset[51], bit_offset[0])  # Sql Table 4 Ring-2 - 908.0
	y_tg.append(TG4)
	TG5 = readInteger(db_number, start_offset[52], bit_offset[0])  # Sql Table 1 Ring-1 - 902.0
	y_tg.append(TG5)
	TG6 = readInteger(db_number, start_offset[53], bit_offset[0])  # Sql Table 2 Ring-1 - 904.0
	y_tg.append(TG6)
	TG7 = readInteger(db_number, start_offset[54], bit_offset[0])  # Sql Table 3 Ring-2 - 906.0
	y_tg.append(TG7)
	TG8 = readInteger(db_number, start_offset[55], bit_offset[0])  # Sql Table 4 Ring-2 - 908.0
	y_tg.append(TG8)

	return y_tg


# Evaluate simultaneous DNV Process Parameters -- Roller Force, Tape Speed, Tape Angle, Tape Temp, Temp Ratio, Tape Gap
def paramDataRequest(pREQ, nGZ, grp_step, fetch_no):

	timei = time.time()
	# Get contiguous data from PLC Stream --- Dealing with very volatile data frame.
	start_offset = [922, 926, 930, 934, 938, 942, 946, 950, 954, 958, 962, 966, 970, 974, 978, 982, 986, 988, 990,
					994, 996, 998, 990, 992, 996, 998, 1000, 1002, 1004, 1006, 1008, 1010, 1012, 1014, 1016, 1018,
					1020, 1022, 1024, 1026, 1028, 1030, 1032, 1034, 1036, 1038, 1040, 1042, 1044, 1046, 1048, 1050,
					1054, 1058, 1062, 1066, 1070, 1074, 1078, 1082, 1084, 1086, 1088, 1090, 1094, 1098, 1102, 1106,
					1110, 1114, 1118, 68, 900]
	bit_offset = [0, 1, 2]
	id1 = str(0)
	# ------------------------------------------------------------------------------------------------
	group_step = int(grp_step)  			# group size/ sample sze
	fetch_no = int(fetch_no)  				# dbfreq = TODO look into any potential conflict
	print('\nSAMPLE SIZE:', nGZ, '| SLIDE STEP:', int(grp_step), '| FETCH CYCLE:', fetch_no)

	# ------------- Consistency Logic ensure list is filled with predetermined elements --------------
	if group_step == 1:
		print('Domino step mode..')
		print('\nSINGLE STEP SLIDE')
		print('=================')
		print('Array length:', len(array2D), 'Fetch Value', fetch_no)
		if len(array2D) == nGZ and fetch_no > 0:
			print('TP A')
			n2fetch = fetch_no
		elif len(array2D) == nGZ and fetch_no < 1:
			print('TP B')
			n2fetch = 1
		elif len(array2D) >= nGZ and fetch_no > 0:
			print('TP C')
			n2fetch = (len(array2D) + fetch_no)
		elif len(array2D) >= nGZ and fetch_no < 1:
			print('TP D')
			n2fetch = 0
		else:
			print('TP E')
			n2fetch = nGZ
		print('Fetch Valued:', n2fetch)
		# Evaluate rows in each tables ---------------------[]
		idxA = int(id1) + fetch_no + 1
		if len(Idx1) > 1:
			del Idx1[:1]
		Idx1.append(idxA)
		print('Processing Query #:', idxA)

	elif group_step > 1:
		print('Discrete step mode..')
		print('\nSAMPLE SIZE SLIDE')
		print('=================')
		if fetch_no != 0 and len(array2D) >= nGZ:
			n2fetch = nGZ
		else:
			n2fetch = nGZ  # fetch twice
		print('Fetching..', n2fetch)
		# Evaluate rows in each tables ---------------------[]
		idxA = int(id1) + (((fetch_no + 1) - 2) * nGZ) + 1
		if len(Idx1) > 1:
			del Idx1[:1]
		Idx1.append(idxA)
		print('Processing SQL Row #:', idxA)
	# ------------------ Live Process Data Acquisition Begins ----------------------------------------------[]
	while True:
		try:
			# Pipe Layer & Position Common to all Process -----
			Ppos = readReal(db_number, start_offset[68], bit_offset[0])  		# Sql Table 3 Ring-2 - 906.0
			y_common.append(Ppos)
			TLayer = readInteger(db_number, start_offset[69], bit_offset[0])  	# Sql Table 4 Ring-2 - 908.0
			y_common.append(TLayer)

			if pREQ == 'RF':
				y_rf = getData_rf(db_number)
				y_common.append(y_rf)
			elif pREQ == 'TT':
				y_tt = getData_tt(db_number)
				y_common.append(y_tt)
			elif pREQ == 'ST':
				y_st = getData_st(db_number)
				y_common.append(y_st)
			elif pREQ == 'TG':
				y_tg = getData_tg(db_number)
				y_common.append(y_tg)
			elif pREQ == 'LP':
				y_lp = getData_lp(db_number)
				y_common.append(y_lp)
			else:
				print('Invalid request!')
				pass		# ignore

			# Load Monitoring Production Parameters in Real-time ------#
			"""
			Values are situated in the upper side of PLC data block. 
			i.e higher offset values, therefore are loaded last.
			"""
			y_lp = plot_rt_LP()			# 4 data colums (Per Ring aggregates)
			y_common.append(y_lp)
			y_la = plot_rt_LA()			# 4 data columns (Per Ring Aggregates)
			y_common.append(y_la)
			# ---------------------------------------------------------#

			# Maximum of Four parameter combination can be selected -------[]
			if len(y_common) > 10 and (len(y_common)) < 20:					# Lowest possible Params [TG+ Common]
				del y_common[0:(len(y_common) - 10)]
				print('\nResetting Column Size...', len(y_common))

			elif len(y_common) > 18 and (len(y_common)) < 34:				# One Params selected
				del y_common[0:(len(y_common) - 18)]
				print('\nResetting Column Size...', len(y_common))

			elif len(y_common) > 90 and (len(y_common)) < 180:  			# All Params selected
				del y_common[0:(len(y_common) - 90)]
				print('\nResetting Column Size...', len(y_common))

			array2D.append(y_common)
			print('\nLIST COLUMN:', len(y_common))
			print('LIST D_ROWS:', len(array2D))
			print('Next Break @:', (n2fetch + nGZ) - len(array2D))

			if group_step == 1:
				# Beautiful Purgatory Procedure ------------------------------[]
				if len(array2D) >= n2fetch and fetch_no <= 21:
					del array2D[0:(len(array2D) - nGZ)]  # [static window]
					print('Resetting Rows on Static.', len(array2D))
					break
				elif group_step == 1 and (fetch_no + 1) >= 22:
					del array2D[0:(len(array2D) - fetch_no)]  # [moving window]
					print('Resetting Rows on Move..', len(array2D))
					break
			else:
				if group_step > 1 and len(array2D) == n2fetch and fetch_no <= 21:
					print('Keeping No of Rows on Static... Array Size:', len(array2D))
					break
				if group_step > 1 and len(array2D) >= (nGZ + n2fetch) and fetch_no <= 21:
					del array2D[0:(len(array2D) - nGZ)]
					print('Resetting Rows on Static... Array Size:', len(array2D))
					break
				elif group_step > 1 and len(array2D) >= (nGZ + n2fetch) and fetch_no >= 22:
					del array2D[0:(len(array2D) - fetch_no)]
					print('Resetting Rows on Move.... Array Size:', len(array2D))
					break
				print('Breaking at..', (n2fetch + nGZ), ' Array Length:', len(array2D))
			# break
			y_common.clear()

		except Exception as err:
			print(f"Exception Error: '{err}'")

		finally:
			timef = time.time()
			print(f"\nLoad Interval: {timef - timei} sec\n", 'Fetch No:', fetch_no)

	return array2D