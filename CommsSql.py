
# About: Module saves all extracted data from prescription notes
# Author: Dr Robert B. Labs

import pyodbc                       # pyodbc is an open source Python module that makes accessing ODBC databases.
from datetime import date, datetime
import numpy as np
import loadSQLConfig as tx
# import Test_PING as sql
from tkinter import messagebox
today = date.today()

# Initialise relevant variables and load configuration settings ---------------------------
server_IP, db_ref, isAtho, yekref = tx.load_configSQL('checksumError.ini')  # server editable connection
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
    messagebox.showerror('MS-SQL', 'Server not accessible, check ODBC connector!')
    return

def errorNote():
    messagebox.showinfo('Connection', 'Connection Terminated!')
    return


def autoConn():
    import CommsPlc as scn
    scn.writeBool(db_number, start_offset[0], bit_offset[1], 1)  # Set SQL_ACK Bit HIGH
    print("\nMS-SQL Server: Connection successful, SCADA notified...")


# --------------------------------------------------------

# Connection to MS-SQL Server (MARS enabled connection) ------------[+ In-Memory OLTP]
def DAQ_connect():
    """
    state: 1 connected, 0 Not connected
    agent: 1 indicate SCADA remote call, 0 indicating SPC local User Call
    """

    # -------- Actual SQL Connection request -----------------#
    conn = None
    # ---------------------------------------------------------#

    if conn == None:
        print('\nConnecting to SQL server...')
        try:
            conn = pyodbc.connect('Driver={SQL Server};'
                                  'Server=' + server_IP + ';'
                                  'Database=' + db_ref + ';'
                                  'Encrypt=' + Encrypt + ';'
                                  'TrustServerCertificate=' + Certify + ';'
                                  'uid=' + isAtho + ';'
                                  'pwd=' + yekref + ';'
                                  'MultipleActiveResultSets=True')
            # conn = 'True'
            print('SQL Server connection active!\n')

        except Exception as err:
            errorLog(str(err))                      # Log the error in txt file
            errorConnect()
            print('[ODBC ver18] Connector failure: SQL Server is inaccessible...')
            conn = 'failed'

    else:                                           # when connection = 1 and requires disconnect
        try:
            conn.close()
            errorNote()
            print('\nActive connection will be closed...')

        except Exception as err:
            print(f"Connection Error: {err}")       # catch whatever error raised
            conn = 'failed'
            errorLog(err)
        print('\nConnection Summary:', conn)

    return conn


def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Database created successfully")
    except Exception as err:
        print(f"Error: '{err}'")
        errorLog(err)


def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = pyodbc.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Exception as err:
        print(f"Error: '{err}'")
        errorLog(err)

    return connection


def is_duplicate(anylist):

    if len(anylist) != len(set(anylist)):
        print("duplicates found in list")
        return True
    else:
        print("no duplicates found in list")
        return False


