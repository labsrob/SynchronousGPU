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
    messagebox.showwarning('Local GUI', 'Specific WON# Not found. Try again!')
    return


def srcforOEE(MatchOEE):

    import CommsSql as sqlc
    sql = sqlc.wonFinder_connect()        # Execute connection
    conn_oee = sql.cursor()         # Convert to cursor


    # TODO --- Search for OEE records by date string & WON string -------------------------------[]

    # ------------------------------------- Load OEE Data from SQL Table  -----------------------[]
    # find creation date of the known WON#
    locateOEE = 'OEE_' + str(MatchOEE)
    print('\nSearching for OEE records...', locateOEE)

    # Locate specific Table -------------[]
    try:
        gOEE = conn_oee.execute('SELECT * FROM information_schema.Tables WHERE [Table_Name]=' + locateOEE).fetchone()
        time.sleep(5)

    except Exception as err:
        # print(f"Exception Error: '{err}'")
        # print("OEE Table is missing...")
        validOEE = 'E'                  # SQL Search Error
        oeeID = '0'                     # Error
        time.sleep(5)

    else:   # when there is no error ---#
        gOEE = gOEE[2]                  # i.e <OEE_WON>
        if gOEE == 'OEE_' + MatchOEE:
            # print('Matched OEE Data:', gOEE)
            validOEE = 'G'              # Organic Table
            oeeID = gOEE
        else:
            # print('Complicated....:', gOEE)
            validOEE = 'C'                  # Complicated or multiple matching Tables
            oeeID = gOEE

    # ---------------------------------[]
    return validOEE, oeeID


def srcTable(sD1, sD2, uWON):               # Post Production data search
    global pWON
    # ----------------------#
    # Load SQL server library --------------#
    import CommsSql as s_con

    StaSearchD = str(sD1)                    # Date Lower Boundary or WON #
    EndSearchD = str(sD2)

    # Test connection readiness and clear any flags
    sqlT = s_con.wonFinder_connect()        # Execute connection
    conn = sqlT.cursor()                    # Convert to cursor
    # --------------------------------------#
    pWON = uWON

    # ----------------------------------- If Search was by Date String ----------------------[]
    if StaSearchD != '0' and EndSearchD != '0':               # If Date search
        print('\nSearching for WON by date...')

        # Find out how many tables meet this condition -----[A]
        pTables = conn.execute('SELECT COUNT(create_date) AS ValidTotal from sys.tables where '
                                     'create_date BETWEEN ' + "'" + StaSearchD + "'" + ' AND ' + "'" + EndSearchD + "'").fetchone()
        time.sleep(10)                                      # allow SQL server response delay

        total_T = pTables[0]                                # Pick total from sql column, add OEE table
        if total_T != 0:
            if not total_T % 2 == 0:                        # Test value and add 1 if value is odd
                nTables = pTables[0] + 1
            else:
                nTables = pTables[0]
        else:
            nTables = total_T
        print('Found:', nTables, 'valid records...')

        # ------------------------------------------------#
        # Verify OEE data against user specified WON ---[]
        checkOEE = str(StaSearchD)  # pick data created date [2025-06-04 10:41:46.613000]
        print('\nTP0:', checkOEE)   # TP0: 2025-5-29
        newWON = checkOEE.split('-')

        # -------------------------------------------------#
        if len(newWON[1]) < 2:
            xmonth = '0' + str(newWON[1])
        else:
            xmonth = str(newWON[1])

        if len(newWON[2]) < 2:
            xday = '0' + str(newWON[2])
        else:
            xday = str(newWON[2])
        print('Month:', xmonth, 'Date:', xday)
        derivedWON = newWON[0] + xmonth + xday              # TP5: 2025 06 04
        derivedOEE = derivedWON
        # --------------------------------------------------#

        if nTables != 0 and nTables <= 25:                   # Production file for DNV exist - OEE data
            # List tables that meet this condition ---------[# schema_name	table_name	create_date]
            # mTables = conn_sq.execute(
            #     'SELECT name as table_name, create_date from '
            #     'sys.tables where create_date BETWEEN ' + "'" + StaSearchD + "'" + ' AND '
            #     + "'" + EndSearchD + "'" + 'order by table_name asc').fetchmany(nTables)
            # -------------------------------------------------------------------------------------[]
            mTables = conn.execute('SELECT name as table_name, create_date from sys.tables where '
                                      'name LIKE ' + "'" '%' + str(derivedWON) + '%' "'" +
                                      'order by name asc').fetchmany(nTables)
            # get the Work Order Name and keep for index-tracking ----[]

            ptype = 'DNV'
            # List all tables in DNV Configuration -----------[]
            T1 = str(mTables[0][0])  # EV_
            T2 = str(mTables[1][0])  # GEN_
            T3 = str(mTables[2][0])  # OEE_
            T4 = str(mTables[3][0])  # RC_
            T5 = str(mTables[4][0])  # RM_
            T6 = str(mTables[5][0])  # RP1_
            T7 = str(mTables[6][0])  # RP2_
            T8 = str(mTables[7][0])  # ST1_
            T9 = str(mTables[8][0])  # ST2_
            T10 = str(mTables[9][0])  # TG_
            T11 = str(mTables[10][0])  # TT1_
            T12 = str(mTables[11][0])  # TT2_
            T13 = str(mTables[12][0])  # VC_
            T14 = str(mTables[13][0])  # VM_
            T15 = str(mTables[14][0])  # ZST_
            T16 = str(mTables[15][0])  # ZTG_
            T17 = str(mTables[16][0])  # ZTT_
            T18 = str(mTables[17][0])  # ZWS_
            T19 = str(mTables[18][0])
            T20 = str(mTables[19][0])

            DNV_tables = [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20]
            for (i, item) in enumerate(DNV_tables, start=1):
                print(i, item)

        elif nTables > 21 and nTables <= 35:
            # List tables that meet this condition ---------[# schema_name	table_name	create_date]
            # mTables = conn_sq.execute(
            #     'SELECT schema_name(schema_id) as schema_name, name as table_name, create_date from '
            #     'sys.tables where create_date BETWEEN ' + "'" + StaSearchD + "'" + ' AND '
            #     + "'" + EndSearchD + "'" + 'order by table_name asc').fetchmany(nTables)
            # -------------------------------------------------------------------------------------[]
            mTables = conn.execute('SELECT name as table_name, create_date from sys.tables where '
                                      'name LIKE ' + "'" '%' + str(derivedWON) + '%' "'" +
                                      'order by name asc').fetchmany(nTables)
            ptype = 'MGM'
            # List all tables in DNV Configuration -----------[]
            T1 = str(mTables[0][0])  # EV_
            T2 = str(mTables[1][0])  # GEN
            T3 = str(mTables[2][0])  # LA1
            T4 = str(mTables[3][0])  # LA2
            T5 = str(mTables[4][0])  # LP1
            T6 = str(mTables[5][0])  # LP2
            T7 = str(mTables[6][0])  # OEE
            T8 = str(mTables[7][0])  # RC
            T9 = str(mTables[8][0])  # RF1
            T10 = str(mTables[9][0])  # RF2
            T11 = str(mTables[10][0])  # RM
            T12 = str(mTables[11][0])  # RP1
            T13 = str(mTables[12][0])  # RP2
            T14 = str(mTables[13][0])  # ST1
            T15 = str(mTables[14][0])  # ST2
            T16 = str(mTables[15][0])  # TG
            T17 = str(mTables[16][0])  # TP1
            T18 = str(mTables[17][0])  # TP2
            T19 = str(mTables[18][0])  # TT1
            T20 = str(mTables[19][0])  # TT2
            T21 = str(mTables[20][0])  # VC
            T22 = str(mTables[21][0])  # VM
            T23 = str(mTables[22][0])  # WA1
            T24 = str(mTables[23][0])  # WA2
            T25 = str(mTables[24][0])  # ZLA
            T26 = str(mTables[25][0])  # ZLP
            T27 = str(mTables[26][0])  # ZST
            T28 = str(mTables[27][0])  # ZTG
            T29 = str(mTables[28][0])  # ZTT
            T30 = str(mTables[29][0])  # ZWA

            MGM_tables = [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17,
                          T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30]
            for (i, item) in enumerate(MGM_tables, start=1):
                print(i, item)

        else:
            print('Invalid number of PPA records found!')
            mTables = 0
            ptype = 'UNK'
            errornotFoundWON()
        # -----------------------------------------#

    # ------------------------------------- If Search was by Work Order Number -----------------------[]
    elif uWON != 0 and StaSearchD == '0' and EndSearchD =='0':                        # WON is searched by WO# -------[]

        # print('Work Order Number Search...')
        pTables = conn.execute('Select count(*) AS ValidTotal from information_schema.Tables where '
                                     'TABLE_NAME like ' + "'" '%' + str(uWON) + '%' "'").fetchone()
        time.sleep(4)                                       # allow SQL server response delay
        nTables = pTables[0]                                # Pick total from sql column, add OEE table
        print('\nFound:', nTables, 'valid records..')

        if nTables != 0 and nTables <= 25:                    # DNV Production file exist - OEE data
            # List out all valid tables, figure out OEE from the creation date --------------------------[]
            mTables = conn.execute(
                'SELECT name as table_name, create_date from '
                'sys.tables where name LIKE ' + "'" '%' + str(uWON) + '%' "'" + 'order by name asc').fetchmany(
                nTables)

            ptype = 'DNV'
            # List all tables in DNV Configuration -----------[]
            T1 = str(mTables[0][0])     # EV_
            T2 = str(mTables[1][0])     # GEN_
            T3 = str(mTables[2][0])     # OEE_
            T4 = str(mTables[3][0])     # RC_
            T5 = str(mTables[4][0])     # RM_
            T6 = str(mTables[5][0])     # RP1_
            T7 = str(mTables[6][0])     # RP2_
            T8 = str(mTables[7][0])     # ST1_
            T9 = str(mTables[8][0])     # ST2_
            T10 = str(mTables[9][0])    # TG_
            T11 = str(mTables[10][0])   # TT1_
            T12 = str(mTables[11][0])   # TT2_
            T13 = str(mTables[12][0])   # VC_
            T14 = str(mTables[13][0])   # VM_
            T15 = str(mTables[14][0])  # ZPP_
            T16 = str(mTables[15][0])  # ZST_
            T17 = str(mTables[16][0])  # ZTG_
            T18 = str(mTables[17][0])  # ZTT_
            T19 = str(mTables[18][0])  # ZWS_
            T20 = str(mTables[19][0])  # ZWS_
            #
            DNV_tables = [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20]
            for (i, item) in enumerate(DNV_tables, start=1):
                print(i, item)

        elif nTables > 21 and nTables <= 35:
            # List out all valid tables, figure out OEE from the creation date ----------------[]
            mTables = conn.execute(
                'SELECT name as table_name, create_date from '
                'sys.tables where name LIKE ' + "'" '%' + str(uWON) + '%' "'" + 'order by name asc').fetchmany(
                nTables)

            ptype = 'MGM'
            # List all tables in DNV Configuration -----------[]
            T1 = str(mTables[0][0])     # EV_
            T2 = str(mTables[1][0])     # GEN
            T3 = str(mTables[2][0])     # LA1
            T4 = str(mTables[3][0])     # LA2
            T5 = str(mTables[4][0])     # LP1
            T6 = str(mTables[5][0])     # LP2
            T7 = str(mTables[6][0])     # OEE
            T8 = str(mTables[7][0])     # RC
            T9 = str(mTables[8][0])     # RF1
            T10 = str(mTables[9][0])    # RF2
            T11 = str(mTables[10][0])   # RM
            T12 = str(mTables[11][0])   # RP1
            T13 = str(mTables[12][0])   # RP2
            T14 = str(mTables[13][0])   # ST1
            T15 = str(mTables[14][0])   # ST2
            T16 = str(mTables[15][0])   # TG
            T17 = str(mTables[16][0])   # TP1
            T18 = str(mTables[17][0])   # TP2
            T19 = str(mTables[18][0])   # TT1
            T20 = str(mTables[19][0])   # TT2
            T21 = str(mTables[20][0])   # VC
            T22 = str(mTables[21][0])   # VM
            T23 = str(mTables[22][0])   # WA1
            T24 = str(mTables[23][0])   # WA2
            T25 = str(mTables[24][0])   # ZLA
            T26 = str(mTables[25][0])   # ZLP
            T27 = str(mTables[26][0])   # ZST
            T28 = str(mTables[27][0])   # ZTG
            T29 = str(mTables[28][0])   # ZTT
            T30 = str(mTables[29][0])   # ZWA

            MGM_tables = [T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17,
                          T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30]
            for (i, item) in enumerate(MGM_tables, start=1):
                print(i, item)
        else:
            print('User specified an invalid WON #..')
            mTables = 0
            ptype = 'UNK'
            errornotFoundWON()


        # Verify OEE data against user specified WON ----[] # we require OEE data.
        if not mTables:
            checkOEE = mP.seek_OEE_data()
            derivedOEE = checkOEE
            prodT = ptype
        else:
            # Locate production OEE's original date
            checkOEE = str(mTables[0][1])      # pick date column data [2025-06-04 10:41:46.613]
            date = datetime.strptime(checkOEE, "%Y-%m-%d  %H:%M:%S.%f")
            # print('\nTP3', date)
            checkOEE = str(date.year)
            prodT = ptype

            # Parse the date string -----------------------------#
            if len(str(date.month)) < 2:
                xmonth = '0' + str(date.month)
            else:
                xmonth = str(date.month)

            if len(str(date.day)) < 2:
                xday = '0' + str(date.day)
            else:
                xday = str(date.day)
            # print('TP5:', checkOEE, xmonth, xday)             # TP5: 2025 06 04
            derivedOEE = checkOEE + xmonth + xday               # TP6: 20250604
            # print('Computed Table: OEE_', derivedOEE)
    # --------------------------------------------------------------------------------[]
    # Locate the matching OEE Table for the WON, otherwise load current OEE
    if mTables != 0:
        organicID, oeeID = srcforOEE(derivedOEE)  # search table record for matching OEEid
        if organicID == 'E':  # Empty, NO corresponding OEE table found
            gOEE = mP.get_encodedFiles()
            newREC = organicID
            pType = prodT
            print('\nNo valid OEE records found! Using current OEE..', gOEE)
        else:
            gOEE = oeeID
            newREC = organicID  # Valid  = 'O' for organic
            pType = 'UNK'
            # gOEE = OEE Table | newREC = if OEE is not multiple | pType = DNV/MGM
            print('\nLoading OEE records for specified WON #:', gOEE)
    else:
        gOEE = 0
        newREC = 0              # Valid  = 'O' for organic
        pType = 'IVLD'

    return gOEE, newREC, pType, nTables


