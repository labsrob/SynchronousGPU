# This script is called in from Main program to load SQL execution syntax command and return a list in LisDat
# Author: Dr Labs, RB
from collections import deque
from itertools import count
from datetime import datetime, timedelta
import time
import timeit
import os
import snap7

arrayRC, RC_list, Idx1, y_common, array2D = [], [], [], [], []
db_number, start_offset, bit_offset = 89, 0, 0
start_address = 0  					# starting address
r_length = 4  						# double word (4 Bytes)
b_length = 1  						# boolean size = 1 Byte
r_data = 52.4
plc = snap7.client.Client()

# ---------------------- Collective Functions ---------------------------------------

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

def writeBool(db_number, start_offset, bit_offset, value):
	bArray = plc.db_read(db_number, start_offset, b_length)    		# (db, start offset, [b_length = read 1 byte])
	snap7.util.set_bool(bArray, 0, bit_offset, value)    			# (value 1= true;0=false)
	plc.db_write(db_number, start_offset, bArray)       			# write back the bytearray
	return 	# None

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

# --------------------------------------------------------------------------------------------------------------------[

def plcExec(db_number, nGZ, grp_step, fetch_no):
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

	# ------------- Consistency Logic ensure list is filled with predeteRCined elements --------------
	if group_step == 1:
		print('Domino step mode..')
		print('\nSINGLE STEP SLIDE')
		print('=================')
		print('Array length:', len(arrayRC), 'Fetch Value', fetch_no)
		if len(arrayRC) == nGZ and fetch_no > 0:
			print('TP A')
			n2fetch = fetch_no
		elif len(arrayRC) == nGZ and fetch_no < 1:
			print('TP B')
			n2fetch = 1
		elif len(arrayRC) >= nGZ and fetch_no > 0:
			print('TP C')
			n2fetch = (len(arrayRC) + fetch_no)
		elif len(arrayRC) >= nGZ and fetch_no < 1:
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
		if fetch_no != 0 and len(arrayRC) >= nGZ:
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
			# Ramp Map Data  ------------------------------------------------------ [6 column data]
			Ppos = readReal(db_number, start_offset[0], bit_offset[0])  			# Ring1 Position
			RC_list.append(Ppos)
			TLayer = readReal(db_number, start_offset[8], bit_offset[0])  			# Ring2 Position
			RC_list.append(TLayer)
			RP1 = readReal(db_number, start_offset[16], bit_offset[0])  			# Ring3 Position
			RC_list.append(RP1)
			RP2 = readReal(db_number, start_offset[18], bit_offset[0])  			# Ring4 Position
			RC_list.append(RP2)
			RP3 = readReal(db_number, start_offset[26], bit_offset[0])  			# Pipe Direction
			RC_list.append(RP3)
			RP4 = readReal(db_number, start_offset[28], bit_offset[0])  			# Current Layer
			RC_list.append(RP4)
			# --------------------------
			RP5 = readReal(db_number, start_offset[36], bit_offset[0])  			# Pipe Direction
			RC_list.append(RP5)
			RP6 = readReal(db_number, start_offset[38], bit_offset[0])  			# Current Layer
			RC_list.append(RP6)
			# -----
			RP7 = readReal(db_number, start_offset[46], bit_offset[0])  			# Pipe Direction
			RC_list.append(RP7)
			RP8 = readReal(db_number, start_offset[48], bit_offset[0])  			# Current Layer
			RC_list.append(RP8)
			RP9 = readReal(db_number, start_offset[50], bit_offset[0])  			# Pipe Direction
			RC_list.append(RP9)
			RP10= readReal(db_number, start_offset[52], bit_offset[0])  			# Current Layer
			RC_list.append(RP10)

			# Deposit list column content into rows array ----------[]
			if len(RC_list) > 12:
				del RC_list[0:(len(RC_list) - 12)]				# trim columns to shape
				print('\nResetting Column Size...', len(RC_list))

			arrayRC.append(RC_list)
			print('\nLIST COLUMN:', len(RC_list))
			print('LIST D_ROWS:', len(arrayRC))
			print('Next Break @:', (n2fetch + nGZ) - len(arrayRC))

			if group_step == 1:
				# Beautiful Purgatory Procedure ------------------------------[TODO - CODEFY SAMPLE SIZE]
				if len(arrayRC) >= n2fetch and fetch_no <= 30:		# Sample Size
					del arrayRC[0:(len(arrayRC) - nGZ)]  			# [static window]
					print('Resetting Rows on Static.', len(arrayRC))
					break
				elif len(arrayRC) >= 31 and (fetch_no + 1) >= 31:
					del arrayRC[0:(len(arrayRC) - fetch_no)]  		# [moving window]
					print('Resetting Rows on Move..', len(arrayRC))
					break
				else:
					pass
			else:
				if group_step > 1 and len(arrayRC) == n2fetch and fetch_no <= 30:
					print('Keeping No of Rows on Static... Array Size:', len(arrayRC))
					break
				if group_step > 1 and len(arrayRC) >= (nGZ + n2fetch) and fetch_no <= 31:
					del arrayRC[0:(len(arrayRC) - nGZ)]
					print('Resetting Rows on Static... Array Size:', len(arrayRC))
					break
				elif group_step > 1 and len(arrayRC) >= (nGZ + n2fetch) and fetch_no >= 31:
					del arrayRC[0:(len(arrayRC) - fetch_no)]
					print('Resetting Rows on Move.... Array Size:', len(arrayRC))
					break
				print('Breaking at..', (n2fetch + nGZ), ' Array Length:', len(arrayRC))
				# break
			RC_list.clear()  							# Clear content of the list for new round trip

		except Exception as err:
			print(f"Exception Error: '{err}'")

		finally:
			timef = time.time()
			print(f"Data Fetch Time: {timef - timei} sec", 'Fetch No:', fetch_no, '\n')

	return arrayRC