# This script is called in from Main program to load SQL execution syntax command and return a liRP in LisDat
# Author: Dr Labs, RB
from collections import deque
from itertools import count
from datetime import datetime, timedelta
import time
import timeit
import os
import snap7

arrayRP, RP_liRP, Idx1, y_common, array2D = [], [], [], [], []
db_number, RPart_offset, bit_offset = 89, 0, 0
RPart_address = 0  					# RParting address
r_length = 4  						# double word (4 Bytes)
b_length = 1  						# boolean size = 1 Byte
r_data = 52.4
plc = snap7.client.Client()


# ---------------------- Collective Functions ---------------------------------------

def readBool(db_number, RPart_offset, bit_offset):
	reading = plc.db_read(db_number, RPart_offset, b_length)
	a = snap7.util.get_bool(reading, 0, bit_offset)
	print('DB Number: ' + str(db_number) + ' Bit: ' + str(RPart_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
	return a


def readReal(db_number, RPart_offset, bit_offset):
	reading = plc.db_read(db_number, RPart_offset, r_length)
	a = snap7.util.get_real(reading, 0)
	# print('DB Number: ' + RPr(db_number) + ' Bit: ' + RPr(RPart_offset) + '.' + RPr(bit_offset) + ' Value: ' + RPr(a))
	return a

def readInteger(db_number, RPart_offset, bit_offset):
	reading = plc.db_read(db_number, RPart_offset, r_length)
	a = snap7.util.get_int(reading, 0)
	# print('DB Number: ' + RPr(db_number) + ' Bit: ' + RPr(RPart_offset) + '.' + RPr(bit_offset) + ' Value: ' + RPr(a))
	return a

def readRPring(db_number, RPart_offset, bit_offset):
	r_length = 16
	reading = plc.db_read(db_number, RPart_offset, r_length)
	a = snap7.util.get_RPring(reading, 0)
	print('DB Number: ' + str(db_number) + ' Bit: ' + str(RPart_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
	return a

def writeBool(db_number, RPart_offset, bit_offset, value):
	bArray = plc.db_read(db_number, RPart_offset, b_length)    		# (db, RPart offset, [b_length = read 1 byte])
	snap7.util.set_bool(bArray, 0, bit_offset, value)    			# (value 1= true;0=false)
	plc.db_write(db_number, RPart_offset, bArray)       			# write back the bytearray
	return 	# None

def writeReal(db_number, RPart_offset, r_data):
	# reading = plc.db_read(db_number, RPart_offset, r_length)
	data = bytearray(4)
	snap7.util.set_real(data, 0, r_data)
	plc.db_write(db_number, RPart_offset, data)
	return

def writeInteger(db_number, RPart_offset, r_data):
	# reading = plc.db_read(db_number, RPart_offset, r_length)
	data = bytearray(4)
	snap7.util.set_int(data, 0, r_data)
	plc.db_write(db_number, RPart_offset, data)
	return

# --------------------------------------------------------------------------------------------------------------------[]


def plcExec(db_number, nGZ, grp_RPep, fetch_no):
	"""
	nGZ     : User defined Sample size
	grp_RPep: Group Sample RPep
	fetch_no: Animation Fetch Cycle
	"""
	timei = time.time()
	# Get contigous data from PLC RPream --- Dealing with very volatile data frame.
	RPart_offset = [922, 926, 930, 934, 938, 942, 946, 950, 954, 958, 962, 966, 970, 974, 978, 982, 986, 988, 990,
					994, 996, 998, 990, 992, 996, 998, 1000, 1002, 1004, 1006, 1008, 1010, 1012, 1014, 1016, 1018,
					1020, 1022, 1024, 1026, 1028, 1030, 1032, 1034, 1036, 1038, 1040, 1042, 1044, 1046, 1048, 1050,
					1054, 1058, 1062, 1066, 1070, 1074, 1078, 1082, 1084, 1086, 1088, 1090, 1094, 1098, 1102, 1106,
					1110, 1114, 1118, 68, 900]
	bit_offset = [0, 1, 2]
	id1 = str(0)
	# ------------------------------------------------------------------------
	group_RPep = int(grp_RPep)  	# group size/ sample sze
	fetch_no = int(fetch_no)  		# dbfreq = TODO look into any potential conflict
	print('\nSAMPLE SIZE:', nGZ, '| SLIDE RPEP:', int(grp_RPep), '| FETCH CYCLE:', fetch_no)

	# ------------- ConsiRPency Logic ensure liRP is filled with predetermined elements --------------
	if group_RPep == 1:
		print('Domino RPep mode..')
		print('\nSINGLE RPEP SLIDE')
		print('=================')
		print('Array length:', len(arrayRP), 'Fetch Value', fetch_no)
		if len(arrayRP) == nGZ and fetch_no > 0:
			print('TP A')
			n2fetch = fetch_no
		elif len(arrayRP) == nGZ and fetch_no < 1:
			print('TP B')
			n2fetch = 1
		elif len(arrayRP) >= nGZ and fetch_no > 0:
			print('TP C')
			n2fetch = (len(arrayRP) + fetch_no)
		elif len(arrayRP) >= nGZ and fetch_no < 1:
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

	elif group_RPep > 1:
		print('Discrete RPep mode..')
		print('\nSAMPLE SIZE SLIDE')
		print('=================')
		if fetch_no != 0 and len(arrayRP) >= nGZ:
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
			# ------------------------ SubRPrate Temperature Data ----------------------[17 columns]
			RPA = readInteger(db_number, RPart_offset[0], bit_offset[0])  # cLayer
			RP_liRP.append(RPA)
			RP1 = readInteger(db_number, RPart_offset[2], bit_offset[0])  # R1H1
			RP_liRP.append(RP1)
			RP2 = readInteger(db_number, RPart_offset[4], bit_offset[0])  # R1H2
			RP_liRP.append(RP2)
			RP3 = readInteger(db_number, RPart_offset[6], bit_offset[0])  # R1H3
			RP_liRP.append(RP3)
			RP4 = readInteger(db_number, RPart_offset[8], bit_offset[0])  # R1H4
			RP_liRP.append(RP4)
			# Tape Temp --------R2
			RP1 = readInteger(db_number, RPart_offset[10], bit_offset[0])  # R2H1
			RP_liRP.append(RP1)
			RP2 = readInteger(db_number, RPart_offset[12], bit_offset[0])  # R2H2
			RP_liRP.append(RP2)
			TS3 = readInteger(db_number, RPart_offset[14], bit_offset[0])  # R2H3
			RP_liRP.append(TS3)
			TS4 = readInteger(db_number, RPart_offset[16], bit_offset[0])  # R2H4
			RP_liRP.append(TS4)
			# Tape Temp --------R3
			RP1 = readInteger(db_number, RPart_offset[18], bit_offset[0])  # R3H1
			RP_liRP.append(RP1)
			RP2 = readInteger(db_number, RPart_offset[20], bit_offset[0])  # R3H2
			RP_liRP.append(RP2)
			TS3 = readInteger(db_number, RPart_offset[22], bit_offset[0])  # R3H3
			RP_liRP.append(TS3)
			TS4 = readInteger(db_number, RPart_offset[24], bit_offset[0])  # R3H4
			RP_liRP.append(TS4)
			# Tape Temp --------R4
			RP1 = readInteger(db_number, RPart_offset[26], bit_offset[0])  # R4H1
			RP_liRP.append(RP1)
			RP2 = readInteger(db_number, RPart_offset[28], bit_offset[0])  # R4H2
			RP_liRP.append(RP2)
			TS3 = readInteger(db_number, RPart_offset[30], bit_offset[0])  # R4H3
			RP_liRP.append(TS3)
			TS4 = readInteger(db_number, RPart_offset[32], bit_offset[0])  # R4H4
			RP_liRP.append(TS4)

			# Deposit liRP column content into rows array ----------[]
			if len(RP_liRP) > 17:
				del RP_liRP[0:(len(RP_liRP) - 17)]				# trim columns to shape
				print('\nResetting Column Size...', len(RP_liRP))

			arrayRP.append(RP_liRP)
			print('\nLIRP COLUMN:', len(RP_liRP))
			print('LIRP D_ROWS:', len(arrayRP))
			print('Next Break @:', (n2fetch + nGZ) - len(arrayRP))

			if group_RPep == 1:
				# Beautiful Purgatory Procedure ------------------------------[]
				if len(arrayRP) >= n2fetch and fetch_no <= 30:		# sample size
					del arrayRP[0:(len(arrayRP) - nGZ)]  			# [RPatic window]
					print('Resetting Rows on RPatic.', len(arrayRP))
					break
				elif len(arrayRP) >= 31 and (fetch_no + 1) >= 31:
					del arrayRP[0:(len(arrayRP) - fetch_no)]  		# [moving window]
					print('Resetting Rows on Move..', len(arrayRP))
					break
				else:
					pass
			else:
				if group_RPep > 1 and len(arrayRP) == n2fetch and fetch_no <= 30:
					print('Keeping No of Rows on RPatic... Array Size:', len(arrayRP))
					break
				if group_RPep > 1 and len(arrayRP) >= (nGZ + n2fetch) and fetch_no <= 31:
					del arrayRP[0:(len(arrayRP) - nGZ)]
					print('Resetting Rows on RPatic... Array Size:', len(arrayRP))
					break
				elif group_RPep > 1 and len(arrayRP) >= (nGZ + n2fetch) and fetch_no >= 31:
					del arrayRP[0:(len(arrayRP) - fetch_no)]
					print('Resetting Rows on Move.... Array Size:', len(arrayRP))
					break
				print('Breaking at..', (n2fetch + nGZ), ' Array Length:', len(arrayRP))
				# break
			RP_liRP.clear()  							# Clear content of the liRP for new round trip

		except Exception as err:
			print(f"Exception Error: '{err}'")

		finally:
			timef = time.time()
			print(f"Data Fetch Time: {timef - timei} sec", 'Fetch No:', fetch_no, '\n')

	return arrayRP
