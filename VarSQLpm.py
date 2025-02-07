"""
# This procedure determine what file to load from SQL server at PWartup
There are two SQL tables required for Monitoring Critial Process Variables
    1. The OEE Data
    2. Production Data (consiPWing of 9 tables)
All production procedure relies on Word Order Number - Assuming a Unique identity

Author: Dr Robert Labs
"""
# Variables required here: The aggregated plots for monitoring process variables


def loadProcesValues(df1, prod):
    if prod == 'DNV':
        # -------- Roller Force Monitoring --#
        sqlPM = [df1['R1H1RF'], df1['R1H2RF'],
                 df1['R1H3RF'], df1['R1H4RF'],
                 df1['R2H1RF'], df1['R2H2RF'],
                 df1['R2H3RF'], df1['R2H4RF'],
                 df1['R3H1RF'], df1['R3H2RF'],
                 df1['R3H3RF'], df1['R3H4RF'],
                 df1['R4H1RF'], df1['R4H2RF'],
                 df1['R4H3RF'], df1['R4H4RF'],
                 # -------- Laser Angle ----#
                 df1['R1H1LA'], df1['R1H2LA'],
                 df1['R1H3LA'], df1['R1H4LA'],
                 df1['R2H1LA'], df1['R2H2LA'],
                 df1['R2H3LA'], df1['R2H4LA'],
                 df1['R3H1LA'], df1['R3H2LA'],
                 df1['R3H3LA'], df1['R3H4LA'],
                 df1['R4H1LA'], df1['R4H2LA'],
                 df1['R4H3LA'], df1['R4H4LA'],
                 # ------- Cell Tension ----#
                 df1['cTensA'], df1['cTensB'],
                 df1['PipeDi'], df1['cRTemp'],
                 df1['cHumid'], df1['fDTemp'],
                 df1['fHumid'], df1['locTemp'],
                 df1['locHumid'], df1['UVIndex'],
                 # ------ Oven Temperature ---#
                 df1['oTempA'], df1['oTempB']]
    elif prod == 'MGM':
        # -------- Roller Force Monitoring --#
        sqlPM = [df1['R1H1RF'], df1['R1H2RF'],
                 df1['R1H3RF'], df1['R1H4RF'],
                 df1['R2H1RF'], df1['R2H2RF'],
                 df1['R2H3RF'], df1['R2H4RF'],
                 df1['R3H1RF'], df1['R3H2RF'],
                 df1['R3H3RF'], df1['R3H4RF'],
                 df1['R4H1RF'], df1['R4H2RF'],
                 df1['R4H3RF'], df1['R4H4RF'],
                 # -------- Laser Angle ----#
                 df1['R1H1LA'], df1['R1H2LA'],
                 df1['R1H3LA'], df1['R1H4LA'],
                 df1['R2H1LA'], df1['R2H2LA'],
                 df1['R2H3LA'], df1['R2H4LA'],
                 df1['R3H1LA'], df1['R3H2LA'],
                 df1['R3H3LA'], df1['R3H4LA'],
                 df1['R4H1LA'], df1['R4H2LA'],
                 df1['R4H3LA'], df1['R4H4LA'],
                 # ------ Oven Temperature ---#
                 df1['oTempA'], df1['oTempB'],
                 # ------- Cell Tension ----#
                 df1['cTensA'], df1['cTensB'],
                 df1['PipeDi'], df1['cRTemp'],
                 df1['cHumid'], df1['fDTemp'],
                 df1['fHumid'], df1['locTemp'],
                 df1['locHumid'], df1['UVIndex'],
                 # Placement Error -----------[]
                 df1['R1H1PE'], df1['R1H2PE'],
                 df1['R1H3PE'], df1['R1H4PE'],
                 df1['R2H1PE'], df1['R2H2PE'],
                 df1['R2H3PE'], df1['R2H4PE'],
                 df1['R3H1PE'], df1['R3H2PE'],
                 df1['R3H3PE'], df1['R3H4PE'],
                 df1['R4H1PE'], df1['R4H2PE'],
                 df1['R4H3PE'], df1['R4H4PE'],
                 # Tape Speed -----------[]
                 df1['R1H1TS'], df1['R1H2TS'],
                 df1['R1H3TS'], df1['R1H4TS'],
                 df1['R2H1TS'], df1['R2H2TS'],
                 df1['R2H3TS'], df1['R2H4TS'],
                 df1['R3H1TS'], df1['R3H2TS'],
                 df1['R3H3TS'], df1['R3H4TS'],
                 df1['R4H1TS'], df1['R4H2TS'],
                 df1['R4H3TS'], df1['R4H4TS']]
    else:
        print('SQL Query: Invalid request error...')

    return sqlPM

