
# About: Module saves all extracted data from prescription notes
# Author: Dr Robert B. Labs

import pymssql
import pyodbc                       # pyodbc is an open source Python module that makes accessing ODBC databases.
from datetime import date, datetime

import numpy as np
import loadSQLConfig as tx

# import Test_PING as sql
from tkinter import messagebox
today = date.today()
import time

# Initialise relevant variables and load configuration settings ----------[]
server_IP, db_ref, isAtho, yekref = tx.load_configSQL('checksumError.ini')
# print('ServerUse Details:', server_IP, db_ref, isAtho, yekref)
Encrypt = 'no'                  # Added today 06/08/2024 [optional]
Certify = 'yes'                 # DITTO

# Define and initialise PLC Data Block --------------------------#
db_number = 89
start_offset = [898, 894]
bit_offset = [0, 1]


def errorLog(err):
    fileName = datetime.now().strftime('SQLLog '+"%Y-%m-%d")
    event = datetime.now().strftime("%Y-%m-%d %H:%M.%S")
    errorlogFile = str(fileName)
    f = open('.\\RuntimeLog\\'+errorlogFile+".txt", "a")
    f.write(event+' --- '+str(err)+'\n')
    f.close()


def successNote():
    messagebox.showinfo('MS-SQL', 'Connection Established')
    return

def errorConnect():
    messagebox.showerror('ODBC Error', 'Check if Server is Online')
    return

def errorNote():
    messagebox.showinfo('Connection', 'Connection Terminated!')
    return


def autoConn():
    import CommsPlc as scn
    scn.writeBool(db_number, start_offset[0], bit_offset[1], 1)  # Set SQL_ACK Bit HIGH
    print("\nMS-SQL Server: Connection successful, SCADA notified...")


def check_SQL_Status(maxAttempts, waitAttempts):
    """
    Returns True if the connection is successfully established before the maxAttempts number is reached
    Conversely returns False
    pyodbc.connect has a built-in timeout. Use a waitBetweenAttemptsSeconds greater than zero to add a delay on top of this timeout
    """
    for attemptNumber in range(maxAttempts):
        cnxn = None
        try:
            cnxn = pyodbc.connect('Driver={SQL Server};'
                                  'Server=' + server_IP + ';'
                                  'Database=' + db_ref + ';'
                                  'Encrypt=' + Encrypt + ';'
                                  'TrustServerCertificate=' + Certify + ';'
                                  'uid=' + isAtho + ';'
                                  'pwd=' + yekref + ';'
                                  'MultipleActiveResultSets=True')
            cursor = cnxn.cursor()
        except Exception as e:
            errorLog(str(e))  # Log the error in txt file
            # errorConnect()

        finally:
            if cnxn:
                print("\nThe DB Server is up and running!!")
                return True
            else:
                print("Sorry, Server connection failed. Remaining " +str((maxAttempts) - (attemptNumber)), 'attempts..')
                #return False
            time.sleep(waitAttempts)
    print("Giving up, maximum attempts for DB to come online exceeded!")

    return False

# ----------- Establish Independent SQl Connection for Parallel Processing ---
def sql_connectTT():
    # Tape Temperature SQL Instance
    """
    Parallel connection call for Tape Temperature Model - RL
    state: 1 connected, 0 Not connected
    agent: 1 indicate SCADA remote call, 0 indicating SPC local User Call
    """
    # print('\nDatasource Details:', server_IP, db_ref)
    # -------- Actual SQL Connection request -----------------#
    conn = None
    resilenceN = 5
    wait2retry = 2
    Certify = 'Certify'
    # ---------------------------------------------------------#

    if conn == None:
        print('[TT] Connecting to SQL server...')
        # Ensure connection is robust and resilience ------
        for attempt in range(1, resilenceN + 1):
            # Use pymssql or pyodbc
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
                print('\n[TT] SQL Server connection active!\n')
                return conn

            except Exception as err:
                wait_time = wait2retry * (2 ** (attempt - 1))
                errorLog(f"[TT] Reconnect attempt {attempt}/{resilenceN} failed: {err}") #(str(err))                      # Log the error in txt file
                # -----------------------
                if attempt < resilenceN:
                    #logging.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # logging.critical("Max retries reached. Exiting.")
                    # raise  # or return None if you prefer soft e
                    errorConnect()
                    print('\n[TT] Connection issue: Server is inaccessible!')
        return None        # conn = False

    else:                                           # when connection = 1 and requires disconnect
        try:
            conn.close()
            errorNote()
            print('\n[TT] Active connection will be closed...')

        except Exception as err:
            print(f"[TT] Connection Error: {err}")       # catch whatever error raised
            # conn = False
            errorLog(err)
        print('\nConnection Summary:', conn)

    return None

# -------------------------------------------------------------[ST Instance]
def sql_connectST():
    # Substrate Temperature SQL Instance
    """
    Parallel connection call for Tape Temperature Model - RL
    state: 1 connected, 0 Not connected
    agent: 1 indicate SCADA remote call, 0 indicating SPC local User Call
    """
    # print('\nDatasource Details:', server_IP, db_ref)
    # -------- Actual SQL Connection request -----------------#
    conn = None
    resilenceN = 5
    wait2retry = 2
    Certify = 'Certify'
    # ---------------------------------------------------------#

    if conn == None:
        print('[ST] Connecting to SQL server...')
        # Ensure connection is robust and resilience ------
        for attempt in range(1, resilenceN + 1):
            # Use pymssql or pyodbc
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
                print('\n[ST] SQL Server connection active!\n')
                return conn

            except Exception as err:
                wait_time = wait2retry * (2 ** (attempt - 1))
                errorLog(f"[ST] Reconnect attempt {attempt}/{resilenceN} failed: {err}") #(str(err))                      # Log the error in txt file
                # -----------------------
                if attempt < resilenceN:
                    #logging.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # logging.critical("Max retries reached. Exiting.")
                    # raise  # or return None if you prefer soft e
                    errorConnect()
                    print('\n[ST] Connection issue: Server is inaccessible!')
        return None        # conn = False

    else:                                           # when connection = 1 and requires disconnect
        try:
            conn.close()
            errorNote()
            print('\n[ST] Active connection will be closed...')

        except Exception as err:
            print(f"[ST] Connection Error: {err}")       # catch whatever error raised
            # conn = False
            errorLog(err)
        print('\nConnection Summary:', conn)

    return None


# ------------------------------------------------------------[]Ramp Mapping]

def sql_connectRMP():   # Temperature Ramp Profile
    """
    Parallel connection call for Ramp Profile Model - RL
    state: 1 connected, 0 Not connected
    agent: 1 indicate SCADA remote call, 0 indicating SPC local User Call
    """
    # print('\nDatasource Details:', server_IP, db_ref)
    # -------- Actual SQL Connection request -----------------#
    conn = None
    max_retry = 5
    wait2retry = 2
    # ---------------------------------------------------------#

    if conn == None:
        print('[RMP] Connecting to SQL server...\n')
        # Ensure connection is roboust enough ------
        for attempt in range(1, max_retry + 1):

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
                print('\n[RMP] SQL Server connection active!\n')
                return conn

            except Exception as err:
                wait_time = wait2retry * (2 ** (attempt - 1))
                errorLog(f"[RMP] Reconnect attempt {attempt}/{max_retry} failed: {err}") #(str(err))                      # Log the error in txt file
                # -----------------------
                if attempt < max_retry:
                    #logging.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # logging.critical("Max retries reached. Exiting.")
                    # raise  # or return None if you prefer soft e
                    errorConnect()
                    print('\n[RMP] Connection issue: Server is inaccessible!')
        return None        # conn = False


# -------------------------------------------------------------------------[Substrate]
def sql_connectVMP():
    # Void Mapping Profile instance
    """
    Parallel connection call for Substrate Temperature Model - RL
    state: 1 connected, 0 Not connected
    agent: 1 indicate SCADA remote call, 0 indicating SPC local User Call
    """
    # print('\nDatasource Details:', server_IP, db_ref)
    # -------- Actual SQL Connection request -----------------#
    conn = None
    max_retry = 5
    wait2retry = 2
    # ---------------------------------------------------------#

    if conn == None:
        print('[VMP] Connecting to SQL server...')
        # Ensure connection is roboust enough ------
        for attempt in range(1, max_retry + 1):

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
                print('\n[VMP] SQL Server connection active!\n')
                return conn

            except Exception as err:
                wait_time = wait2retry * (2 ** (attempt - 1))
                errorLog(f"[VMP] Reconnect attempt {attempt}/{max_retry} failed: {err}") #(str(err))                      # Log the error in txt file
                # -----------------------
                if attempt < max_retry:
                    #logging.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # logging.critical("Max retries reached. Exiting.")
                    # raise  # or return None if you prefer soft e
                    errorConnect()
                    print('\n[VMP] Connection issue: SQL Server is inaccessible!')
        return None        # conn = False

    else:                                           # when connection = 1 and requires disconnect
        try:
            conn.close()
            errorNote()
            print('\n[VMP] Active connection will be closed...')

        except Exception as err:
            print(f"[VMP] Connection Error: {err}")       # catch whatever error raised
            # conn = False
            errorLog(err)
        print('\nConnection Summary:', conn)

    return None

# -------------------------------------------------------------------------[Tape Gap]
def sql_connectTG():
    """
    Parallel connection call for Tape Gap Model - RL
    state: 1 connected, 0 Not connected
    agent: 1 indicate SCADA remote call, 0 indicating SPC local User Call
    """
    # print('\nDatasource Details:', server_IP, db_ref)
    # -------- Actual SQL Connection request -----------------#
    conn = None
    max_retry = 5
    wait2retry = 2
    # ---------------------------------------------------------#

    if conn == None:
        print('[TG] Connecting to SQL server...')
        # Ensure connection is roboust enough ------
        for attempt in range(1, max_retry + 1):

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
                print('\n[TG] SQL Server connection active!\n')
                return conn

            except Exception as err:
                wait_time = wait2retry * (2 ** (attempt - 1))
                errorLog(f"[TG] Reconnect attempt {attempt}/{max_retry} failed: {err}") #(str(err))                      # Log the error in txt file
                # -----------------------
                if attempt < max_retry:
                    #logging.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # logging.critical("Max retries reached. Exiting.")
                    # raise  # or return None if you prefer soft e
                    errorConnect()
                    print('\n[TG] Connection issue: SQL Server is inaccessible!')
        return None        # conn = False

    else:                                           # when connection = 1 and requires disconnect
        try:
            conn.close()
            errorNote()
            print('\n[TG] Active connection will be closed...')

        except Exception as err:
            print(f"[TG] Connection Error: {err}")       # catch whatever error raised
            # conn = False
            errorLog(err)
        print('\nConnection Summary:', conn)

    return None

# -------------------------------------------------------------------------[TG Mapping]
def sql_connectRTM():
    # Real-Time Monitoring Parameters
    """
    Parallel connection call for Process Monitors Model - RL
    state: 1 connected, 0 Not connected
    agent: 1 indicate SCADA remote call, 0 indicating SPC local User Call
    """
    # print('\nDatasource Details:', server_IP, db_ref)
    # -------- Actual SQL Connection request -----------------#
    conn = None
    max_retry = 5
    wait2retry = 2
    # ---------------------------------------------------------#

    if conn == None:
        print('[RTM] Connecting to SQL server...')
        # Ensure connection is roboust enough ------
        for attempt in range(1, max_retry + 1):

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
                print('\n[RTM] SQL Server connection active!\n')
                return conn

            except Exception as err:
                wait_time = wait2retry * (2 ** (attempt - 1))
                errorLog(f"[TM] Reconnect attempt {attempt}/{max_retry} failed: {err}") #(str(err))                      # Log the error in txt file
                # -----------------------
                if attempt < max_retry:
                    #logging.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # logging.critical("Max retries reached. Exiting.")
                    # raise  # or return None if you prefer soft e
                    errorConnect()
                    print('\n[RTM] Connection issue: SQL Server is inaccessible!')
        return None        # conn = False

    else:                                           # when connection = 1 and requires disconnect
        try:
            conn.close()
            errorNote()
            print('\n[RTM] Active connection will be closed...')

        except Exception as err:
            print(f"[RTM] Connection Error: {err}")       # catch whatever error raised
            # conn = False
            errorLog(err)
        print('\nConnection Summary:', conn)

    return None

# -------------------------------------------------------------------------[Monitoring Params]
def sql_connectLP():
    # Laser Power SQL Instance
    """
    state: 1 connected, 0 Not connected
    agent: 1 indicate SCADA remote call, 0 indicating SPC local User Call
    """
    # print('\nDatasource Details:', server_IP, db_ref)
    # -------- Actual SQL Connection request -----------------#
    conn = None
    max_retry = 5
    wait2retry = 2
    # ---------------------------------------------------------#

    if conn == None:
        print('[LP] Connecting to SQL server...')
        # Ensure connection is roboust enough ------
        for attempt in range(1, max_retry + 1):
            # {SQL Server}
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
                print('\n[LP] SQL Server connection active!\n')
                return conn

            except Exception as err:
                wait_time = wait2retry * (2 ** (attempt - 1))
                errorLog(f"[LP] Reconnect attempt {attempt}/{max_retry} failed: {err}") #(str(err))                      # Log the error in txt file
                # -----------------------
                if attempt < max_retry:
                    #logging.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # logging.critical("Max retries reached. Exiting.")
                    # raise  # or return None if you prefer soft e
                    errorConnect()
                    print('\n[LP] Connection issue: SQL Server is inaccessible!')
        return None        # conn = False

    return None

# -------------------------------------------------------------------------[]
def sql_connectEV():
    """
    Parallel connection call for commonClimate Profile Model - RL
    state: 1 connected, 0 Not connected
    agent: 1 indicate SCADA remote call, 0 indicating SPC local User Call
    """
    # print('\nDatasource Details:', server_IP, db_ref)
    # -------- Actual SQL Connection request -----------------#
    conn = None
    max_retry = 5
    wait2retry = 2
    # ---------------------------------------------------------#

    if conn == None:
        print('\n[cEV] Connecting to SQL server...')
        # Ensure connection is roboust enough ------
        for attempt in range(1, max_retry + 1):

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
                print('\n[cEV] SQL Server connection active!\n')
                return conn

            except Exception as err:
                wait_time = wait2retry * (2 ** (attempt - 1))
                errorLog(f"[cEV] Reconnect attempt {attempt}/{max_retry} failed: {err}") #(str(err))                      # Log the error in txt file
                # -----------------------
                if attempt < max_retry:
                    #logging.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # logging.critical("Max retries reached. Exiting.")
                    # raise  # or return None if you prefer soft e
                    errorConnect()
                    print('\n[cEV] Connection issue: SQL Server is inaccessible!')
        return None        # conn = False

    else:                                           # when connection = 1 and requires disconnect
        try:
            conn.close()
            errorNote()
            print('\n[cEV] Active connection will be closed...')

        except Exception as err:
            print(f"[cEV] Connection Error: {err}")       # catch whatever error raised
            # conn = False
            errorLog(err)
        print('\nConnection Summary:', conn)

    return None

# -------------------------------------------------------------------------------------------------------
def sql_connectVC():
    """
    Parallel connection call for common Ramp Count Model - RL
    state: 1 connected, 0 Not connected
    agent: 1 indicate SCADA remote call, 0 indicating SPC local User Call
    """
    # print('\nDatasource Details:', server_IP, db_ref)
    # -------- Actual SQL Connection request -----------------#
    conn = None
    max_retry = 5
    wait2retry = 2
    # ---------------------------------------------------------#

    if conn == None:
        print('[cVC] Connecting to SQL server...')
        # Ensure connection is roboust enough ------
        for attempt in range(1, max_retry + 1):

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
                print('\n[cVC] SQL Server connection active!\n')
                return conn

            except Exception as err:
                wait_time = wait2retry * (2 ** (attempt - 1))
                errorLog(f"[cVC] Reconnect attempt {attempt}/{max_retry} failed: {err}") #(str(err))                      # Log the error in txt file
                # -----------------------
                if attempt < max_retry:
                    #logging.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # logging.critical("Max retries reached. Exiting.")
                    # raise  # or return None if you prefer soft e
                    errorConnect()
                    print('\n[cVC] Connection issue: SQL Server is inaccessible!')
        return None        # conn = False

    else:                                           # when connection = 1 and requires disconnect
        try:
            conn.close()
            errorNote()
            print('\n[cVC] Active connection will be closed...')

        except Exception as err:
            print(f"[cVC] Connection Error: {err}")       # catch whatever error raised
            # conn = False
            errorLog(err)
        print('\nConnection Summary:', conn)

    return None

# --------------------------------------------------------------------
def sql_connectRC():
    """
    Parallel connection call for common Ramp Count model
    state: 1 connected, 0 Not connected
    agent: 1 indicate SCADA remote call, 0 indicating SPC local User Call
    """
    # print('\nDatasource Details:', server_IP, db_ref)
    # -------- Actual SQL Connection request -----------------#
    conn = None
    max_retry = 5
    wait2retry = 2
    # ---------------------------------------------------------#

    if conn == None:
        print('[cRC] Connecting to SQL server...')
        # Ensure connection is roboust enough ------
        for attempt in range(1, max_retry + 1):

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
                print('\n[cRC] SQL Server connection active!\n')
                return conn

            except Exception as err:
                wait_time = wait2retry * (2 ** (attempt - 1))
                errorLog(f"[cRC] Reconnect attempt {attempt}/{max_retry} failed: {err}") #(str(err))                      # Log the error in txt file
                # -----------------------
                if attempt < max_retry:
                    #logging.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # logging.critical("Max retries reached. Exiting.")
                    # raise  # or return None if you prefer soft e
                    errorConnect()
                    print('\n[cRC] Connection issue: SQL Server is inaccessible!')
        return None        # conn = False

    else:                                           # when connection = 1 and requires disconnect
        try:
            conn.close()
            errorNote()
            print('\n[cRC] Active connection will be closed...')

        except Exception as err:
            print(f"[cRC] Connection Error: {err}")       # catch whatever error raised
            # conn = False
            errorLog(err)
        print('\nConnection Summary:', conn)

    return None


# ----------------------------------------------------------------------------
def eolViz_connect():
    """
    state: 1 connected, 0 Not connected
    agent: 1 indicate SCADA remote call, 0 indicating SPC local User Call
    """
    # print('\nDatasource Details:', server_IP, db_ref)
    # -------- Actual SQL Connection request -----------------#
    conn = None
    # ---------------------------------------------------------#
    if conn == None:
        print('\n[EoL Viz] Connecting to SQL server...')

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
            print('\n[EoL Viz] SQL Server connection active!\n')
            return conn

        except Exception as err:
            errorLog(str(err))                      # Log the error in txt file
            errorConnect()
            print('\n[EoL Viz] Connection issue: SQL Server is inaccessible!')

        return None

# ----------------------------------------------------------------------------
def eolRPT_connect():
    """
    state: 1 connected, 0 Not connected
    agent: 1 indicate SCADA remote call, 0 indicating SPC local User Call
    """
    # print('\nDatasource Details:', server_IP, db_ref)
    # -------- Actual SQL Connection request -----------------#
    conn = None
    # ---------------------------------------------------------#
    if conn == None:
        print('\n[EoL RPT] Connecting to SQL server...')

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
            print('\n[EoL RPT] SQL Server connection active!\n')
            return conn

        except Exception as err:
            errorLog(str(err))                      # Log the error in txt file
            errorConnect()
            print('\n[EoL RPT] Connection issue: SQL Server is inaccessible!')

        return None

def wonFinder_connect():
    """
    state: 1 connected, 0 Not connected
    agent: 1 indicate SCADA remote call, 0 indicating SPC local User Call
    """
    # print('\nDatasource Details:', server_IP, db_ref)
    # -------- Actual SQL Connection request -----------------#
    conn = None
    # ---------------------------------------------------------#
    if conn == None:
        print('\n[WON Finder] Connecting to SQL server...')

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
            print('\n[WON Finder] SQL Server connection active!\n')
            return conn

        except Exception as err:
            errorLog(str(err))                      # Log the error in txt file
            errorConnect()
            print('\n[WON Finder] Connection issue: SQL Server is inaccessible!')

        return None

def ensure_connection(conn):
    """Check if connection is alive, reconnect if needed."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")  # lightweight test query
        cursor.close()
        return conn
    except Exception:
        print("Reconnecting...")
        return # DAQ_connect()

# --------------------------------------------------------------------------------
