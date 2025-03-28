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


def searchSqlData(DATEentry, WONentry):                   # Post Production data search
    # ----------------------#
    # Load SQL server library
    import CommsSql as sql_con

    StaSearchD = DATEentry                                      # Date Lower Boundary or WON #
    EndSearchD = int(DATEentry) + 1                             # Date Upper Boundary or 0
    EndSearchD = str(EndSearchD)

    # Test connection readiness and clear any flags ups.....
    sqlTableid = sql_con.DAQ_connect()  # Execute connection
    conn_sq = sqlTableid.cursor()       # Convert to cursor

    # ----------------------------------- If Search was by Date String ----------------------[]
    if StaSearchD != '0' and WONentry == '0':               # If Date search
        print('\nWON: Date Search.')

        # Find out how many tables meet this condition -----[A]
        pTables = conn_sq.execute('SELECT COUNT(create_date) AS ValidTotal from sys.tables where '
                                     'create_date BETWEEN ' + "'" + StaSearchD + "'" + ' AND ' + "'" + EndSearchD + "'").fetchone()
        time.sleep(10)                                      # allow SQL server response delay
        nTables = pTables[0]                                # pick values from sql column
        total_T = int(nTables)

        if not total_T % 2 == 0:                            # Test value and add 1 if value is odd
            nTables = pTables[0] + 1
        print('\nFound:', nTables, 'valid records..')

        if nTables > 1:                                     # Production file exist with OEE data
            # List tables that meet this condition ---------[# schema_name	table_name	create_date]
            mTables = conn_sq.execute(
                'SELECT schema_name(schema_id) as schema_name, name as table_name, create_date from '
                'sys.tables where create_date BETWEEN ' + "'" + StaSearchD + "'" + ' AND '
                + "'" + EndSearchD + "'" + 'order by table_name asc').fetchmany(nTables)

            # get the Work Order Name and keep for index-tracking ----
            newWON = mTables[1][1]                          # First_row, second column (Table_name)
            newWON = newWON.split('_')
            processWON.append(newWON[1])
            newWON = processWON[0]
            # OEEdataID = mTables[0][1]                     # Pick first table on the first row
            OEEdataID = mP.get_encodedFiles(StaSearchD)     # Computed OEE_ID for specific date

        else:
            errorSearchWON()                                # return error to the user.
            OEEdataID = 0
            newWON = 0

        # ------------------------------------- If Search was by Work Order Number -----------------------[]
    elif WONentry != 0 and StaSearchD == '0':                        # WON is searched by WO# -------[]
        print('WON: Work Order Number Search... True')

        pTables = conn_sq.execute('Select count(*) AS ValidTotal from Information_schema.Tables where '
                                     'TABLE_NAME like ' + "'" '%' + str(WONentry) + '%' "'").fetchone()
        time.sleep(4)                                       # allow SQL server response delay
        nTables = pTables[0]                                # Pick total from sql column, add OEE table
        print('\nFound:', nTables, 'valid records..')

        if nTables >= 1:                                    # Production file exist with OEE data
            # List out all valid tables, figure out OEE from the creation date --------------------------[]
            mTables = conn_sq.execute(
                'SELECT type_desc AS schema_name, name as table_name, create_date from '
                'sys.tables where name LIKE ' + "'" '%' + str(WONentry) + '%' "'" + 'order by name asc').fetchmany(
                nTables)
            checkOEE_date = mTables[1][2]
            newWON = WONentry
            OEEdataID = searchOEERecs(conn_sq, checkOEE_date)         # get OEE file name

        else:
            print('Invalid Work Order Number..')
            errorSearchWON()
            OEEdataID = 0
            newWON = 0
    else:
        print('Invalid Work Order Number..')
        errorSearchWON()
        OEEdataID = mP.seek_OEE_data()                             # Default to current date's OEE
        newWON = 0
        conn = 0

    return OEEdataID, newWON


def searchOEERecs(conn, MatchOEE):
    mOEEDataID = conn.cursor()  # NOTE: OEE Data can exist without Work Order
    # TODO --- Search for OEE records by date string & WON string -------------------------------[]

    # ------------------------------------- Load OEE Data from SQL Table  -----------------------[]
    print('\nVerifying the existence of OEE Data...')

    # find creation date of the known WON#
    locateOEE = 'OEE_' + str(MatchOEE)
    gOEE = mOEEDataID.execute('SELECT * FROM information_schema.Tables WHERE [Table_Name]=' + locateOEE).fetchone()
    time.sleep(5)
    gOEE = gOEE[2]

    print('Matched OEE Data:', gOEE)
    # --------------------------------- --------------------------------[]
    return gOEE