# This script is called in from Main program to load SQL execution syntax command and return a list in LisDat
# Author: Dr Labs, RB
from collections import deque
from itertools import count
from datetime import datetime, timedelta
import time
import timeit
import os
import snap7

arrayTG, tg_list, Idx1, y_common, array2D = [], [], [], [], []
start_offset, bit_offset = 0, 0
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


def plcExec(nGZ, grp_step, DB, fetch_no):
	"""
	nGZ     : User defined Sample size
	grp_step: Group Sample step
	fetch_no: Animation Fetch Cycle
	"""
	db_number = DB
	# Get contiguous data from PLC Stream --- Dealing with very volatile data frame.
	start_offset = [0, 2, 4, 6, 14, 22, 26, 30, 38, 42, 46, 50, 54]
	bit_offset = [0, 1, 2]
	id1 = str(0)

	timei = time.time()
	# ------------------------------------------------------------------------
	group_step = int(grp_step)  	# group size/ sample sze
	fetch_no = int(fetch_no)  		# dbfreq = TODO look into any potential conflict
	print('\nSAMPLE SIZE:', nGZ, '| SLIDE STEP:', int(grp_step), '| FETCH CYCLE:', fetch_no)

	# ------------- Consistency Logic ensure list is filled with predetermined elements --------------
	if group_step == 1:
		print('Domino step mode..')
		print('\nSINGLE STEP SLIDE')
		print('=================')
		print('Array length:', len(arrayTG), 'Fetch Value', fetch_no)
		if len(arrayTG) == nGZ and fetch_no > 0:
			print('TP A')
			n2fetch = fetch_no
		elif len(arrayTG) == nGZ and fetch_no < 1:
			print('TP B')
			n2fetch = 1
		elif len(arrayTG) >= nGZ and fetch_no > 0:
			print('TP C')
			n2fetch = (len(arrayTG) + fetch_no)
		elif len(arrayTG) >= nGZ and fetch_no < 1:
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
		if fetch_no != 0 and len(arrayTG) >= nGZ:
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
			# --------------------------------- Tape Gap Measurement Data ---------------------[14 columns]
			TG1 = readInteger(db_number, start_offset[0], bit_offset[0])  		# time stamp
			tg_list.append(TG1)
			TG2 = readInteger(db_number, start_offset[1], bit_offset[0])  		# Current Layr
			tg_list.append(TG2)
			TG3 = readInteger(db_number, start_offset[2], bit_offset[0])  		# Sample Count
			tg_list.append(TG3)
			TG4 = readReal(db_number, start_offset[3], bit_offset[0])  			# Sample Centre
			tg_list.append(TG4)
			TG5 = readReal(db_number, start_offset[4], bit_offset[0])  		# Pipe Position
			tg_list.append(TG5)
			TG6 = readReal(db_number, start_offset[5], bit_offset[0])  		# Gauge A1
			tg_list.append(TG6)
			TG7 = readReal(db_number, start_offset[6], bit_offset[0])  		# Gauge A2
			tg_list.append(TG7)
			TG8 = readReal(db_number, start_offset[7], bit_offset[0])  		# Gauge A3
			tg_list.append(TG8)
			LP1 = readReal(db_number, start_offset[8], bit_offset[0])  		# Gauge A4
			tg_list.append(LP1)
			LP2 = readReal(db_number, start_offset[9], bit_offset[0])  		# Gauge B1
			tg_list.append(LP2)
			LP3 = readReal(db_number, start_offset[10], bit_offset[0])  		# Gauge B2
			tg_list.append(LP3)
			LP4 = readReal(db_number, start_offset[11], bit_offset[0])  		# Gauge B3
			tg_list.append(LP4)
			LA1 = readReal(db_number, start_offset[12], bit_offset[0])  	 	# Gauge B4
			tg_list.append(LA1)
			LA2 = readInteger(db_number, start_offset[13], bit_offset[0])  		# Pipe Direction
			tg_list.append(LA2)


			# Deposit list column content into rows array ----------[]
			if len(tg_list) > 14:
				del tg_list[0:(len(tg_list) - 14)]				# trim columns to shape
				print('\nResetting Column Size...', len(tg_list))

			arrayTG.append(tg_list)
			print('\nLIST COLUMN:', len(tg_list))
			print('LIST D_ROWS:', len(arrayTG))
			print('Next Break @:', (n2fetch + nGZ) - len(arrayTG))

			if group_step == 1:
				# Beautiful Purgatory Procedure ------------------------------[]
				if len(arrayTG) >= n2fetch and fetch_no <= 20:
					del arrayTG[0:(len(arrayTG) - nGZ)]  			# [static window]
					print('Resetting Rows on Static.', len(arrayTG))
					break
				elif len(arrayTG) >= 21 and (fetch_no + 1) >= 21:
					del arrayTG[0:(len(arrayTG) - fetch_no)]  		# [moving window]
					print('Resetting Rows on Move..', len(arrayTG))
					break
				else:
					pass
			else:
				if group_step > 1 and len(arrayTG) == n2fetch and fetch_no <= 20:
					print('Keeping No of Rows on Static... Array Size:', len(arrayTG))
					break
				if group_step > 1 and len(arrayTG) >= (nGZ + n2fetch) and fetch_no <= 21:
					del arrayTG[0:(len(arrayTG) - nGZ)]
					print('Resetting Rows on Static... Array Size:', len(arrayTG))
					break
				elif group_step > 1 and len(arrayTG) >= (nGZ + n2fetch) and fetch_no >= 21:
					del arrayTG[0:(len(arrayTG) - fetch_no)]
					print('Resetting Rows on Move.... Array Size:', len(arrayTG))
					break
				print('Breaking at..', (n2fetch + nGZ), ' Array Length:', len(arrayTG))
				# break
			tg_list.clear()  							# Clear content of the list for new round trip

		except Exception as err:
			print(f"Exception Error: '{err}'")

		finally:
			timef = time.time()
			print(f"Data Fetch Time: {timef - timei} sec", 'Fetch No:', fetch_no, '\n')

	return arrayTG
