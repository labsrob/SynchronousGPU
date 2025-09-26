# today = date.today()
import time
import pyodbc
import loadSQLConfig as tx

# Initialise relevant variables and load configuration settings ----------[]
# server_IP, db_ref, isAtho, yekref = tx.load_configSQL('checksumError.ini')
# print('ServerUse Details:', server_IP, db_ref, isAtho, yekref)

server_IP = '10.0.3.172'
db_ref = 'DAQ_sSPC'
isAtho = 'TCP01'
yekref = 'Testing27!'
Encrypt = 'no'                  # Added today 06/08/2024 [optional]
Certify = 'yes'                 # DITTO

def EOLrpt_connect():
    """
    state: 1 connected, 0 Not connected
    agent: 1 indicate SCADA remote call, 0 indicating SPC local User Call
    """
    # print('\nDatasource Details:', server_IP, db_ref)
    # -------- Actual SQL Connection request -----------------#
    conn = None
    # ---------------------------------------------------------#
    if conn == None:
        print('\n[EoL] Connecting to SQL server...')

        try:
            conn = pyodbc.connect('Driver={SQL Server};'
                                  'Server=' + server_IP + ';'
                                  'Database=' + db_ref + ';'
                                  'Encrypt=' + Encrypt + ';'
                                  'TrustServerCertificate=' + Certify + ';'
                                  'uid=' + isAtho + ';'
                                  'pwd=' + yekref + ';'
                                  'MultipleActiveResultSets=True', timeout=5, autocommit=True)
            # conn = True
            print('\n[EoL] SQL Server connection active!\n')
            return conn

        except Exception as err:
            print('\n[EoL] Connection issue: SQL Server is inaccessible!')

    return None

# # Determine EOL Random sampling regime ---------------------------------------------------------------[X]
tempo = EOLrpt_connect()
t1 = tempo.cursor()
t2 = tempo.cursor()

T1 = 'ZTT_20250923'
T2 = 'ZST_20250923'
layerNo = 1

# Query = 'Select count([R1SP]) AS ValidTotal from [' + str(T1) + '] where [cLyr] = ' + str(layerNo)
# t1.execute(Query)
# data1 = t1.fetchone()

# ttSR = t1.execute('Select count([R1SP]) AS ValidTotal from [' + str(T1) + '] where [cLyr] = ' + str(layerNo)).fetchone()
# stSR = t2.execute('Select count([R1SP]) AS ValidTotal from [' + str(T2) + '] where [cLyr] = ' + str(layerNo)).fetchone()
#
#
# print('TP01', ttSR[0])
# Data1 = round(ttSR[0] * 0.5, )
# print('TP02', Data1)
#
# print('\nTP03', stSR[0])
# Data2 = round(stSR[0] * 0.5, )
# print('TP04', Data2)
#
# t1.close()
# t2.close()
# -----------------------------------------------------------------------------#
last_t1 = None
dL1 = []
n2fetch = 100

try:
    if last_t1 is None:
        t1.execute('SELECT * FROM ' + str(T1) + ' ORDER BY cLyr ASC')
    else:
        t1.execute('SELECT * FROM ' + str(T1) + ' WHERE id_col > ? ORDER BY cLyr ASC', last_t1)
    data1 = t1.fetchmany(n2fetch)
    print('\nDT01', len(data1))
    # --------------- Re-assemble into dynamic buffer -----
    if len(data1) != 0:
        for result in data1:
            result = list(result)
            dL1.append(result)
        last_t1 = data1[-1].id_col
        print('\nDT02', dL1)
    else:
        print('[vTT] Process EOF reached...')
        print('[vTT] Halting for 5 Minutes...')
        time.sleep(3)

except Exception as e:
    print("[vTT Error] Tape Temp Data trickling...")  # , e)
    time.sleep(2)
t1.close()

# ---------------------------- Testing PLC Communication -----------------------------------#
# import snap7
#
# _Plc= snap7.client.Client()
# pCon = _Plc.connect('192.168.100.100', 0, 1)
# db_number, start_offset, bit_offset = 89, 0, 0
#
# start_offset1, bit_offset1 = 2, 0
# value, data = True, False  			# 1 = true | 0 = false
#
# start_address = 0  					# starting address
# r_length = 4  						# double word (4 Bytes)
# b_length = 1  						# boolean size = 1 Byte
# r_data = 52.4
# initialise = 0
#
#
# def readBool(db_number, start_offset, bit_offset):
# 	reading = pCon.db_read(db_number, start_offset, b_length)
# 	a = snap7.util.get_bool(reading, 0, bit_offset)
# 	print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
# 	return a
#
#
# def readReal(db_number, start_offset, bit_offset):
# 	reading = pCon.db_read(db_number, start_offset, r_length)
# 	a = snap7.util.get_real(reading, 0)
# 	# print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
# 	return a
#
#
# def readInteger(db_number, start_offset, bit_offset):
# 	reading = pCon.db_read(db_number, start_offset, r_length)
# 	a = snap7.util.get_int(reading, 0)
# 	print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
# 	return a
#
#
# def readString(db_number, start_offset, bit_offset):
# 	r_length = 2 # 16
# 	reading = pCon.db_read(db_number, start_offset, r_length)
# 	a = snap7.util.get_string(reading, 0)
# 	print('DB Number: ' + str(db_number) + ' Bit: ' + str(start_offset) + '.' + str(bit_offset) + ' Value: ' + str(a))
# 	return a

# -----------------------------------------------------------
#
# def liveProductionRdy():
# 	# Allow connection once unless connection drops out -----
#     try:
#         sysRun = readBool(db_number,0, 0)  # System is runing
#         sysidl = readBool(db_number, 0, 1)  # System idling
#         sysrdy = readBool(db_number, 0, 2)  # System Ready
#         msctcp = readInteger(db_number, 2, 0)  # Machine State Code (msc)
#         won_NO = readString(db_number, 4, 0)  # Work Order Number
#
#
#     except Exception as err:
#         print(f"Exception Error: '{err}'")
#         sysidl = False
#         sysrdy = False
#
#         print('Sorry, PLC Host not responding, retry within seconds..')
#     return sysRun, sysidl, sysrdy, msctcp, won_NO

# sysRun, sysidl, sysrdy, msctcp, won_NO = liveProductionRdy()

# print('WON:', won_NO)

# ---------------------------------------
# # import packages
# import pandas as pd
#
# # reading csv file
# result = pd.read_csv('C:\\synchronousDOCS\\fossilfuels.csv')
# pd.set_option('display.max_columns', None)
# print('TP01',result.head(5))
# print()
#
# # randomly selecting columns
# sampled = result.sample(frac=0.3, axis='rows', random_state=9)
# print('TP02', sampled.head(5))