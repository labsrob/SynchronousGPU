# This script is called in from Main program to load SQL execution syntax command and return a list in LisDat
# Author: Dr Labs, RB
from collections import deque
from itertools import count
from datetime import datetime, timedelta
import time
import timeit
import os
import snap7

arrayRP, RP_list, Idx1, y_common, array2D = [], [], [], [], []
db_number, start_offset, bit_offset = 235, 0, 0		# SPC_LogQA_RP[DB235]
start_address = 0  					# starting address
r_length = 4  						# double word (4 Bytes)
b_length = 1  						# boolean size = 1 Byte
r_data = 52.4
pCon = snap7.client.Client()

# ---------------------- Collective Functions ---------------------------------------

def readInteger(db_number, start_offset, bit_offset):
	reading = pCon.db_read(db_number, start_offset, r_length)
	a = snap7.util.get_int(reading, 0)
	# print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
	return a

def writeInteger(db_number, start_offset, r_data):
	# reading = plc.db_read(db_number, start_offset, r_length)
	data = bytearray(4)
	snap7.util.set_int(data, 0, r_data)
	pCon.db_write(db_number, start_offset, data)
	return

# --------------------------------------------------------------------------------------------------------------------[]


def plcExec(db_number, nGZ, grp_step, fetch_no):
	"""
	nGZ     : User defined Sample size
	grp_step: Group Sample step
	fetch_no: Animation Fetch Cycle
	"""
	timei = time.time()
	# Get contigous data from PLC Stream --- Dealing with very volatile data frame.
	start_offset = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32]
	bit_offset = [0, 1, 2]
	id1 = str(0)
	# ------------------------------------------------------------------------
	n2fetch = int(nGZ)
	group_step = int(grp_step)
	fetch_no = int(fetch_no)
	if group_step == 1:
		slideType = 'Smooth Edge*'
	else:
		slideType = 'Non-overlapping*'

	print('\n[TT] SAMPLE SIZE:', nGZ, '| SLIDE MODE:', slideType, '| BATCH:', fetch_no)
	print('=' * 60)

	# ------------- Consistency Logic ensure list is filled with predetermined elements --------------
	if group_step == 1:
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

	elif group_step > 1:
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
			# ------------------------ Tape Temperature Data ----------------------[17 columns]
			# Tape Temperature ---R1
			RPA = readInteger(db_number, start_offset[0], bit_offset[0])  		# Current Layer
			RP_list.append(RPA)
			RP1 = readInteger(db_number, start_offset[2], bit_offset[0])  		# R1H1
			RP_list.append(RP1)
			RP2 = readInteger(db_number, start_offset[4], bit_offset[0])  		# R1H2
			RP_list.append(RP2)
			RP3 = readInteger(db_number, start_offset[6], bit_offset[0])  		# R1H3
			RP_list.append(RP3)
			RP4 = readInteger(db_number, start_offset[8], bit_offset[0])  		# R1H4
			RP_list.append(RP4)
			# R2 ------
			RP5 = readInteger(db_number, start_offset[10], bit_offset[0])  		# R2H1
			RP_list.append(RP5)
			RP6 = readInteger(db_number, start_offset[12], bit_offset[0])  		# R2H2
			RP_list.append(RP6)
			RP7 = readInteger(db_number, start_offset[14], bit_offset[0])  		# R2H3
			RP_list.append(RP7)
			RP8 = readInteger(db_number, start_offset[16], bit_offset[0])  		# R2H4
			RP_list.append(RP8)
			# R3 ------
			RP9 = readInteger(db_number, start_offset[18], bit_offset[0])  		# R3H1
			RP_list.append(RP9)
			RP10 = readInteger(db_number, start_offset[20], bit_offset[0])  	# R3H2
			RP_list.append(RP10)
			RP11 = readInteger(db_number, start_offset[22], bit_offset[0])  	# R3H3
			RP_list.append(RP11)
			RP12 = readInteger(db_number, start_offset[24], bit_offset[0])  	# R3H4
			RP_list.append(RP12)
			# R4 ------
			RP13 = readInteger(db_number, start_offset[26], bit_offset[0])  	# R4H1
			RP_list.append(RP13)
			RP14 = readInteger(db_number, start_offset[28], bit_offset[0])  	# R4H2
			RP_list.append(RP14)
			RP15 = readInteger(db_number, start_offset[30], bit_offset[0])  	# R4H3
			RP_list.append(RP15)
			RP16 = readInteger(db_number, start_offset[32], bit_offset[0])  	# R4H4
			RP_list.append(RP16)
			RP17 = readInteger(db_number, start_offset[34], bit_offset[0])  	# Pipe Pos
			RP_list.append(RP17)
			RP18 = readInteger(db_number, start_offset[36], bit_offset[0])  	# PipeDir			RP_list.append(RP18)
			RP_list.append(RP18)

			# Deposit list column content into rows array ----------[]
			if len(RP_list) > 19:
				del RP_list[0:(len(RP_list) - 19)]				# trim columns to shape
				print('\nReseRPing Column Size...', len(RP_list))

			arrayRP.append(RP_list)
			print('\nLIST COLUMN:', len(RP_list))
			print('LIST D_ROWS:', len(arrayRP))
			print('Next Break @:', (n2fetch + nGZ) - len(arrayRP))

			if group_step == 1:
				# Beautiful Purgatory Procedure ------------------------------[]
				if len(arrayRP) >= n2fetch and fetch_no <= 30:		# sample size = 30
					del arrayRP[0:(len(arrayRP) - nGZ)]  			# [static window]
					print('ReseRPing Rows on Static.', len(arrayRP))
					break
				elif len(arrayRP) >= 31 and (fetch_no + 1) >= 31:
					del arrayRP[0:(len(arrayRP) - fetch_no)]  		# [moving window]
					print('ReseRPing Rows on Move..', len(arrayRP))
					break
				else:
					pass
			else:
				if group_step > 1 and len(arrayRP) == n2fetch and fetch_no <= 30:
					print('Keeping No of Rows on Static... Array Size:', len(arrayRP))
					break
				if group_step > 1 and len(arrayRP) >= (nGZ + n2fetch) and fetch_no <= 31:
					del arrayRP[0:(len(arrayRP) - nGZ)]
					print('ReseRPing Rows on Static... Array Size:', len(arrayRP))
					break
				elif group_step > 1 and len(arrayRP) >= (nGZ + n2fetch) and fetch_no >= 31:
					del arrayRP[0:(len(arrayRP) - fetch_no)]
					print('ReseRPing Rows on Move.... Array Size:', len(arrayRP))
					break
				print('Breaking at..', (n2fetch + nGZ), ' Array Length:', len(arrayRP))
				# break
			RP_list.clear()  # Clear content of the list for new round trip

		except Exception as err:
			print(f"Exception Error: '{err}'")

		finally:
			timef = time.time()
			print(f"Data Fetch Time: {timef - timei} sec", 'Fetch No:', fetch_no, '\n')

	return arrayRP


