# This script is called in from Main program to load SQL execution syntax command and return a list in LisDat
# Author: Dr Labs, RB
from collections import deque
from itertools import count
from datetime import datetime, timedelta
import time
import pyodbc

# ------------------------------
server_IP = '10.0.3.172'
db_ref = 'DAQ_sSPC'
isAtho = 'TCP01'
yekref = 'Testing27!'
Encrypt = 'no'                  # Added today 06/08/2024 [optional]
Certify = 'yes'
# -----------------------------

UseRowIndex = True
idx = count()
now = datetime.now()

dataList0 = []
rLP, rLA, rRP, rTT, rST, rTG, rWA, rWS, rPP = [], [], [], [], [], [], [], [], []
reg = 0.2
st_id  = 0                                               # SQL start index unless otherwise tracker!
eol_sr = 0.5
# ------------ PDF Generator Method ---------------------------------------------------------

def rpt_SQLconnect():
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

# ---------------------------- END OF LAYER REPORT GENERATION -----------------------#

def dnv_updateSqlExec(eop_con, pWON):
    """
    NOTE:
    """
    # Provide critical and robust connection for End of Pipe Data (Position Data)
    if eop_con is None:
        tempo = rpt_SQLconnect()
        mainStream = True
        print('\nUsing a new param connection..')
    else:
        mainStream = False
        tempo = eop_con
        print('\nUsing mainstream connection..')
    # --------------------------------------
    t1, t2 = tempo.cursor(), tempo.cursor()
    t3, t4 = tempo.cursor(), tempo.cursor()

    # Create New SQL table to host spc live data for EoP ---
    try:
        sq1 = t1.execute('SELECT * INTO QRP_ '+pWON+' FROM 20_EoPRP')
        sq2 = t2.execute('SELECT * INTO QTT_ '+pWON+' FROM 18_EoPTT')
        sq3 = t3.execute('SELECT * INTO QST_ '+pWON+' FROM 19_EoPST')
    except Exception as err:
        print('Error creating SQL Tables')
    finally:
        print('New Table(s) created on SQL Repository')

    if not mainStream:
        t1.close()
        t2.close()
        t3.close()

    return sq1, sq2, sq3

# Check for EoP Tables on SQL Server ---------------------

def sql_checkEoPTables(eop_con, T1, T2, T3):
    """
    NOTE:
    """
    # Provide critical and robust connection for End of Pipe Data (Position Data)
    if eop_con is None:
        tempo = rpt_SQLconnect()
        mainStream = True
        print('\nUsing a new param connection..')
    else:
        mainStream = False
        tempo = eop_con
        print('\nUsing mainstream connection..')
    # --------------------------------------
    t1, t2 = tempo.cursor(), tempo.cursor()
    t3 = tempo.cursor()

    # Check the existence of the tables required for  EoP ---
    sql_to_check = [T1, T2, T3]
    # +sql_to_check
    try:
        # Use placeholder to forestall any future sql injection -----
        q1, q2, q3 = t1.execute('SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = ? AND TABLE_NAME IN (?, ?, ?)')

    except Exception as err:
        q1, q2, q3 = False, False, False
        print('Error creating SQL Tables')

    else:
        print('New Table(s) created on SQL Repository')

    if not mainStream:
        t1.close()
        t2.close()
        t3.close()

    return q1, q2, q3