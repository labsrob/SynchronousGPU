#
# MODULE ASYNCHRONOUS Data Frame (moduleAsynchronousData.py)
# Magma Global Ltd., TechnipFMC
# Author: Robert B. Labs, PhD
# -----------------------------------------------------

import sqlHistoricalRecs as mP
from tkinter import messagebox
import spcWatchDog as wd
from datetime import datetime
from itertools import count
import time
import os

conn = 'from sql connection'
apCalledby = []


srchA, srchB = [], []
processWON = []
# Declare empty arrays ------------[]
dL0, dX2, dX3 = [], [], []

# Specify row index for database ------[]
UseRowIndex = True
idx = count()
now = datetime.now()

rtUpdateCONNX = False               # import realTimeUpdate as pq | ALLOW CONNECTION ONCE
inUseAlready = False                # import realTPostProdUpdate as pq | ALLOW USAGE of CLASS ONCE
UsePLC_DBS = True


def connSQL():
    import CommsSql as mCon
    agent = 0
    if agent == 0:
        conn = mCon.DAQ_connect(1, agent)  # 1 = connection is active to be .closed()
    else:
        conn = 'none'
        # errorNoconnect()
    return conn


def errorSearchWON():
    messagebox.showerror('Local GUI', 'Invalid Work Order Number. Try again!')
    return

def errornotFoundWON():
    messagebox.showwarning('Local GUI', 'Specirfic WON# Not found. Try again!')
    return


def srcforOEE(MatchOEE):

    import CommsSql as sqlc
    sql = sqlc.DAQ_connect()    # Execute connection
    conn_oee = sql.cursor()         # Convert to cursor


    # TODO --- Search for OEE records by date string & WON string -------------------------------[]

    # ------------------------------------- Load OEE Data from SQL Table  -----------------------[]
    print('\nVerifying the existence of OEE Data...')

    # find creation date of the known WON#
    locateOEE = 'OEE_' + str(MatchOEE)
    print('To locate:', locateOEE)

    # Locate specific Table -------------[]
    try:
        gOEE = conn_oee.execute('SELECT * FROM information_schema.Tables WHERE [Table_Name]=' + locateOEE).fetchone()
        time.sleep(5)

    except Exception as err:
        print(f"Exception Error: '{err}'")
        print("OEE Table is not found or Not available")
        validOEE = 'E'                  # SQL Search Error
        oeeID = '0'                     # Error
        time.sleep(5)

    else:   # when there is no error ---#
        gOEE = gOEE[2]                  # i.e <OEE_WON>
        if gOEE == 'OEE_' + MatchOEE:
            print('Matched OEE Data:', gOEE)
            validOEE = 'O'              # Organic Table
            oeeID = gOEE
        else:
            print('Complicated....:', gOEE)
            validOEE = 'C'  # Complicated or multiple matching Tables
            oeeID = gOEE

    # ---------------------------------[]
    return validOEE, oeeID


def srcTable(sD1, sD2, uWON):                   # Post Production data search
    # ----------------------#
    # Load SQL server library
    import CommsSql as sql_con

    StaSearchD = str(sD1)                             # Date Lower Boundary or WON #
    EndSearchD = str(sD2)
    # print('\nDate Range02:', sD1, 'and', sD2)
    # print('Date Range03:', StaSearchD, 'and', EndSearchD)
    # print('Date Range04:', StaSearchD, 'and', EndSearchD, 'WON#:', uWON)

    # Test connection readiness and clear any flags ups.....
    sqlTableid = sql_con.DAQ_connect()      # Execute connection
    conn_sq = sqlTableid.cursor()           # Convert to cursor

    # ----------------------------------- If Search was by Date String ----------------------[]
    if StaSearchD != '0' and EndSearchD != '0':               # If Date search
        print('\nWON Date Search.')

        # Find out how many tables meet this condition -----[A]
        pTables = conn_sq.execute('SELECT COUNT(create_date) AS ValidTotal from sys.tables where '
                                     'create_date BETWEEN ' + "'" + StaSearchD + "'" + ' AND ' + "'" + EndSearchD + "'").fetchone()

        time.sleep(10)                                      # allow SQL server response delay

        total_T = int(pTables[0])
        print('Record found4:', pTables[2])

        if total_T != 0:
            if not total_T % 2 == 0:                        # Test value and add 1 if value is odd
                nTables = pTables[0] + 1
            else:
                nTables = pTables[0]
        else:
            nTables = total_T
        print('\nFound:', nTables, 'valid records..')

        if nTables > 1:                                     # Production file exist with OEE data
            # List tables that meet this condition ---------[# schema_name	table_name	create_date]
            mTables = conn_sq.execute(
                'SELECT schema_name(schema_id) as schema_name, name as table_name, create_date from '
                'sys.tables where create_date BETWEEN ' + "'" + StaSearchD + "'" + ' AND '
                + "'" + EndSearchD + "'" + 'order by table_name asc').fetchmany(nTables)

            # get the Work Order Name and keep for index-tracking ----
            print('\n List Tables Found:', mTables)
            newWON = mTables[1][1]                          # First_row, second column (Table_name)
            print('\nTP1:', newWON)

            newWON = newWON.split('_')
            processWON.append(newWON[1])
            print('TP2:', newWON)

            # Construct GENeral Table presence ---
            newREC = processWON[0]
            print('TP3:', newREC)

            # Compute OEE for the requested data -----------#
            currentOEE = mP.get_encodedFiles(StaSearchD)     # Computed OEE_ID for specific date
            reqMathdOEE = uWON
            if currentOEE == 'OEE_'+reqMathdOEE:
                gOEE = currentOEE
                newREC = '1'
            else:
                gOEE = uWON
                newREC = '0'
            print('TP4:', gOEE)

        else:
            errornotFoundWON()                                # return error to the user.
            gOEE = '0'
            newREC = '0'

            print('No matching records found !')

        # ------------------------------------- If Search was by Work Order Number -----------------------[]
    elif uWON != 0 and StaSearchD == '0' and EndSearchD =='0':                        # WON is searched by WO# -------[]
        print('Work Order Number Search...')

        pTables = conn_sq.execute('Select count(*) AS ValidTotal from Information_schema.Tables where '
                                     'TABLE_NAME like ' + "'" '%' + str(uWON) + '%' "'").fetchone()
        time.sleep(4)                                       # allow SQL server response delay
        nTables = pTables[0]                                # Pick total from sql column, add OEE table
        print('\nFound:', nTables, 'valid records..')

        if nTables >= 1:                                    # Production file exist with OEE data
            # List out all valid tables, figure out OEE from the creation date --------------------------[]
            mTables = conn_sq.execute(
                'SELECT name as table_name, create_date from '
                'sys.tables where name LIKE ' + "'" '%' + str(uWON) + '%' "'" + 'order by name asc').fetchmany(
                nTables)

            # Verify OEE data against user specified WON -----[]
            checkOEE = str(mTables[0][1])                           # pick data created date [2025-06-04 10:41:46.613000]
            print('TP4:', checkOEE)

            # parse date time string --
            date = datetime.strptime(checkOEE, "%Y-%m-%d  %H:%M:%S.%f")

            checkOEE = str(date.year)
            # -------------------------------------------------#
            if len(str(date.month)) < 2:
                xmonth = '0' + str(date.month)
            if len(str(date.day)) < 2:
                xday = '0' + str(date.day)
            # print('TP5:', checkOEE, xmonth, xday)               # TP5: 2025 06 04
            checkOEE = checkOEE+xmonth+xday
            # print('TP6:', checkOEE)                             # TP6: 20250604

            conn_sq.close()

            organicID, oeeID = srcforOEE(checkOEE)              # search table record for matching OEEid
            # print('TPXXX:', organicID)
            # print('TPZZZ:', oeeID)

            if organicID == 'E':
                gOEE = mP.get_encodedFiles(StaSearchD)
                newREC = organicID
            else:
                gOEE = oeeID
                newREC = organicID      # Valid  = 'O' for organic
            # print('TP7:', gOEE, newREC)

        else:
            print('Work Order Number not found !')
            errornotFoundWON()
            gOEE = '0'
            newREC = '0'

    else:
        print('Invalid Work Order Number..')
        errorSearchWON()
        gOEE = mP.seek_OEE_data()                             # Default to current date's OEE
        newREC = '0'

    return gOEE, newREC


