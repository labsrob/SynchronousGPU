
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
                print("Sorry, DB Server connection failed. Remaining " +str((maxAttempts) - (attemptNumber)), 'attempts..')
                #return False
            time.sleep(waitAttempts)
    print("Giving up, maximum attempts for DB to come online exceeded!")

    return False

# ----------- Establish Independent SQl Connection for Parallel Processing ---
def sql_connectTT():
    """
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
        print('\n[TT] Connecting to SQL server...')
        # Ensure connection is robust and resillence ------
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

# -------------------------------------------------------------------------[]Ramp Mapping
def sql_connectRMP():
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
def sql_connectST():
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
        print('\n[ST] Connecting to SQL server...')
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
                print('\n[ST] SQL Server connection active!\n')
                return conn

            except Exception as err:
                wait_time = wait2retry * (2 ** (attempt - 1))
                errorLog(f"[ST] Reconnect attempt {attempt}/{max_retry} failed: {err}") #(str(err))                      # Log the error in txt file
                # -----------------------
                if attempt < max_retry:
                    #logging.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # logging.critical("Max retries reached. Exiting.")
                    # raise  # or return None if you prefer soft e
                    errorConnect()
                    print('\n[ST] Connection issue: SQL Server is inaccessible!')
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

# -------------------------------------------------------------------------[Tape Gap]
def sql_connectTG():
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
        print('\n[TG] Connecting to SQL server...')
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
def sql_connectVMP():
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
        print('\n[TM] Connecting to SQL server...')
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
                print('\n[TM] SQL Server connection active!\n')
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
                    print('\n[TM] Connection issue: SQL Server is inaccessible!')
        return None        # conn = False

    else:                                           # when connection = 1 and requires disconnect
        try:
            conn.close()
            errorNote()
            print('\n[TM] Active connection will be closed...')

        except Exception as err:
            print(f"[TM] Connection Error: {err}")       # catch whatever error raised
            # conn = False
            errorLog(err)
        print('\nConnection Summary:', conn)

    return None

# -------------------------------------------------------------------------[Monitoring Params]
def sql_connectMP():
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
        print('\n[MP] Connecting to SQL server...')
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
                print('\n[MP] SQL Server connection active!\n')
                return conn

            except Exception as err:
                wait_time = wait2retry * (2 ** (attempt - 1))
                errorLog(f"[MP] Reconnect attempt {attempt}/{max_retry} failed: {err}") #(str(err))                      # Log the error in txt file
                # -----------------------
                if attempt < max_retry:
                    #logging.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # logging.critical("Max retries reached. Exiting.")
                    # raise  # or return None if you prefer soft e
                    errorConnect()
                    print('\n[MP] Connection issue: SQL Server is inaccessible!')
        return None        # conn = False

    return None

# -------------------------------------------------------------------------[]
def DAQ_connect():
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
            errorLog(str(err))                      # Log the error in txt file
            errorConnect()
            print('\n[EoL] Connection issue: SQL Server is inaccessible!')

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
        return DAQ_connect()

# --------------------------------------------------------------------------------


# -----------------------------------------------------------------------
# import pyodbc
# import threading
# import time
# import random
#
# # Connection string - change as per your SQL Server configuration
# CONNECTION_STRING = (
#     "DRIVER={ODBC Driver 17 for SQL Server};"
#     "SERVER=localhost;"  # Or IP address or server\instance
#     "DATABASE=YourDatabaseName;"
#     "UID=your_username;"
#     "PWD=your_password;"
# )
#
#
# def create_user_table(user_id):
#     conn = pyodbc.connect(CONNECTION_STRING)
#     cursor = conn.cursor()
#     table_name = f"user_{user_id}_data"
#
#     create_table_sql = f"""
#     IF NOT EXISTS (
#         SELECT * FROM INFORMATION_SCHEMA.TABLES
#         WHERE TABLE_NAME = '{table_name}'
#     )
#     BEGIN
#         CREATE TABLE {table_name} (
#             id INT IDENTITY(1,1) PRIMARY KEY,
#             value NVARCHAR(255)
#         )
#     END
#     """
#
#     cursor.execute(create_table_sql)
#     conn.commit()
#     conn.close()
#     print(f"[User {user_id}] Table ensured.")
#
#
# def user_session(user_id, data_to_insert):
#     table_name = f"user_{user_id}_data"
#     conn = pyodbc.connect(CONNECTION_STRING)
#     cursor = conn.cursor()
#
#     # Insert data
#     for value in data_to_insert:
#         cursor.execute(f"INSERT INTO {table_name} (value) VALUES (?)", value)
#         conn.commit()
#         print(f"[User {user_id}] Inserted: {value}")
#         time.sleep(random.uniform(0.1, 0.5))  # Simulate delay
#
#     # Fetch data
#     cursor.execute(f"SELECT * FROM {table_name}")
#     rows = cursor.fetchall()
#     print(f"[User {user_id}] Data in table:")
#     for row in rows:
#         print(f"   {row.id}: {row.value}")
#
#     conn.close()
#
#
# def main():
#     user_ids = ['TT', 'ST', 'TG']
#     threads = []
#
#     # Create a table for each user
#     for user_id in user_ids:
#         create_user_table(user_id)
#
#     # Launch a thread for each user session
#     for user_id in user_ids:
#         data = [f"Data-{user_id}-{i}" for i in range(5)]
#         thread = threading.Thread(target=user_session, args=(user_id, data))
#         threads.append(thread)
#         thread.start()
#
#     # Wait for all threads to complete
#     for thread in threads:
#         thread.join()
#
#     print("All user sessions completed.")
#
#
# if __name__ == "__main__":
#     main()
