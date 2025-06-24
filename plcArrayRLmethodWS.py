# This script is called in from Main program to load SQL execution syntax command and return a list in LisDat
# Author: Dr WSbs, RB
from collections import deque
from itertools import count
from datetime import datetime, timedelta
import time
import timeit
import os
import snap7

arrayWS, WS_list, Idx1, y_common, array2D = [], [], [], [], []
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

# --------------------------------------------------------------------------------------------------------------------[]


def plcExec(nGZ, grp_step, fetch_no):
	"""
	nGZ     : User defined Sample size
	grp_step: Group Sample step
	fetch_no: Animation Fetch Cycle
	"""
	timei = time.time()
	# Get contigous data from PLC Stream --- Dealing with very voWStile data frame.
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
		print('Array length:', len(arrayWS), 'Fetch Value', fetch_no)
		if len(arrayWS) == nGZ and fetch_no > 0:
			print('TP A')
			n2fetch = fetch_no
		elif len(arrayWS) == nGZ and fetch_no < 1:
			print('TP B')
			n2fetch = 1
		elif len(arrayWS) >= nGZ and fetch_no > 0:
			print('TP C')
			n2fetch = (len(arrayWS) + fetch_no)
		elif len(arrayWS) >= nGZ and fetch_no < 1:
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
		if fetch_no != 0 and len(arrayWS) >= nGZ:
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
			# ------------------------ Tape Temperature Data ----------------------[17 columns]
			# Tape Temperature ---R1
			WSA = readInteger(db_number, start_offset[0], bit_offset[0])  		# Current WSyer
			WS_list.append(WSA)
			WS1 = readInteger(db_number, start_offset[2], bit_offset[0])  		# R1H1
			WS_list.append(WS1)
			WS2 = readInteger(db_number, start_offset[4], bit_offset[0])  		# R1H2
			WS_list.append(WS2)
			WS3 = readInteger(db_number, start_offset[6], bit_offset[0])  		# R1H3
			WS_list.append(WS3)
			WS4 = readInteger(db_number, start_offset[8], bit_offset[0])  		# R1H4
			WS_list.append(WS4)
			# R2 ------
			WS5 = readInteger(db_number, start_offset[10], bit_offset[0])  		# R2H1
			WS_list.append(WS5)
			WS6 = readInteger(db_number, start_offset[12], bit_offset[0])  		# R2H2
			WS_list.append(WS6)
			WS7 = readInteger(db_number, start_offset[14], bit_offset[0])  		# R2H3
			WS_list.append(WS7)
			WS8 = readInteger(db_number, start_offset[16], bit_offset[0])  		# R2H4
			WS_list.append(WS8)
			# R3 ------
			WS9 = readInteger(db_number, start_offset[18], bit_offset[0])  		# R3H1
			WS_list.append(WS9)
			WS10 = readInteger(db_number, start_offset[20], bit_offset[0])  	# R3H2
			WS_list.append(WS10)
			WS11 = readInteger(db_number, start_offset[22], bit_offset[0])  	# R3H3
			WS_list.append(WS11)
			WS12 = readInteger(db_number, start_offset[24], bit_offset[0])  	# R3H4
			WS_list.append(WS12)
			# R4 ------
			WS13 = readInteger(db_number, start_offset[26], bit_offset[0])  	# R4H1
			WS_list.append(WS13)
			WS14 = readInteger(db_number, start_offset[28], bit_offset[0])  	# R4H2
			WS_list.append(WS14)
			WS15 = readInteger(db_number, start_offset[30], bit_offset[0])  	# R4H3
			WS_list.append(WS15)
			WS16 = readInteger(db_number, start_offset[32], bit_offset[0])  	# R4H4
			WS_list.append(WS16)

			# Deposit list column content into rows array ----------[]
			if len(WS_list) > 82:
				del WS_list[0:(len(WS_list) - 82)]				# trim columns to shape
				print('\nReseWSing Column Size...', len(WS_list))

			arrayWS.append(WS_list)
			print('\nLIST COLUMN:', len(WS_list))
			print('LIST D_ROWS:', len(arrayWS))
			print('Next Break @:', (n2fetch + nGZ) - len(arrayWS))

			if group_step == 1:
				# Beautiful Purgatory Procedure ------------------------------[]
				if len(arrayWS) >= n2fetch and fetch_no <= 30:		# sample size = 30
					del arrayWS[0:(len(arrayWS) - nGZ)]  			# [static window]
					print('ReseWSing Rows on Static.', len(arrayWS))
					break
				elif len(arrayWS) >= 31 and (fetch_no + 1) >= 31:
					del arrayWS[0:(len(arrayWS) - fetch_no)]  		# [moving window]
					print('ReseWSing Rows on Move..', len(arrayWS))
					break
				else:
					pass
			else:
				if group_step > 1 and len(arrayWS) == n2fetch and fetch_no <= 30:
					print('Keeping No of Rows on Static... Array Size:', len(arrayWS))
					break
				if group_step > 1 and len(arrayWS) >= (nGZ + n2fetch) and fetch_no <= 31:
					del arrayWS[0:(len(arrayWS) - nGZ)]
					print('ReseWSing Rows on Static... Array Size:', len(arrayWS))
					break
				elif group_step > 1 and len(arrayWS) >= (nGZ + n2fetch) and fetch_no >= 31:
					del arrayWS[0:(len(arrayWS) - fetch_no)]
					print('ReseWSing Rows on Move.... Array Size:', len(arrayWS))
					break
				print('Breaking at..', (n2fetch + nGZ), ' Array Length:', len(arrayWS))
				# break
			WS_list.clear()  							# Clear content of the list for new round trip

		except Exception as err:
			print(f"Exception Error: '{err}'")

		finally:
			timef = time.time()
			print(f"Data Fetch Time: {timef - timei} sec", 'Fetch No:', fetch_no, '\n')

	return arrayWS
