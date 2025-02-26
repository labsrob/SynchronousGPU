"""
# This procedure determine what file to load from SQL server at PWartup
There are two SQL tables required for Monitoring Critial Process Variables
    1. The OEE Data
    2. Production Data (consiPWing of 9 tables)
All production procedure relies on Word Order Number - Assuming a Unique identity

Author: Dr Robert Labs
"""
# MONITORING VARIABLES: The aggregated plots for monitoring process variables


def loadProcesValues(df1, prod):        # Load useful columns out of many
    if prod == 'DNV':
        # -------- Roller Force Monitoring --#
        sqlPM = [df1['R1H1RP'], df1['R1H2RP'],
                 df1['R1H3RP'], df1['R1H4RP'],
                 df1['R2H1RP'], df1['R2H2RP'],
                 df1['R2H3RP'], df1['R2H4RP'],
                 df1['R3H1RP'], df1['R3H2RP'],
                 df1['R3H3RP'], df1['R3H4RP'],
                 df1['R4H1RP'], df1['R4H2RP'],
                 df1['R4H3RP'], df1['R4H4RP'],
                 # ------ Winding Speed ----#
                 df1['R1H1WS'], df1['R1H2WS'],
                 df1['R1H3WS'], df1['R1H4WS'],
                 df1['R2H1WS'], df1['R2H2WS'],
                 df1['R2H3WS'], df1['R2H4WS'],
                 df1['R3H1WS'], df1['R3H2WS'],
                 df1['R3H3WS'], df1['R3H4WS'],
                 df1['R4H1WS'], df1['R4H2WS'],
                 df1['R4H3WS'], df1['R4H4WS'],
                 # -Cell Tension & Oven Temp -#
                 df1['oTempA'], df1['oTempB'],
                 df1['cTensA'], df1['cTensB'],
                 df1['PipeDi'], df1['cRTemp'],
                 df1['cHumid'], df1['fDTemp'],
                 df1['fHumid'], df1['locTemp'],
                 df1['locHumid'], df1['UVIndex']]
    elif prod == 'MGM':
        # -------- Laser Power Monitoring --#
        sqlPM = [df1['R1H1LP'], df1['R1H2LP'],
                 df1['R1H3LP'], df1['R1H4LP'],
                 df1['R2H1LP'], df1['R2H2LP'],
                 df1['R2H3LP'], df1['R2H4LP'],
                 df1['R3H1LP'], df1['R3H2LP'],
                 df1['R3H3LP'], df1['R3H4LP'],
                 df1['R4H1LP'], df1['R4H2LP'],
                 df1['R4H3LP'], df1['R4H4LP'],
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
                 # Roller Pressure -----------[]
                 df1['R1H1RP'], df1['R1H2RP'],
                 df1['R1H3RP'], df1['R1H4RP'],
                 df1['R2H1RP'], df1['R2H2RP'],
                 df1['R2H3RP'], df1['R2H4RP'],
                 df1['R3H1RP'], df1['R3H2RP'],
                 df1['R3H3RP'], df1['R3H4RP'],
                 df1['R4H1RP'], df1['R4H2RP'],
                 df1['R4H3RP'], df1['R4H4RP'],
                 # Tape Speed -----------[]
                 df1['R1H1WS'], df1['R1H2WS'],
                 df1['R1H3WS'], df1['R1H4WS'],
                 df1['R2H1WS'], df1['R2H2WS'],
                 df1['R2H3WS'], df1['R2H4WS'],
                 df1['R3H1WS'], df1['R3H2WS'],
                 df1['R3H3WS'], df1['R3H4WS'],
                 df1['R4H1WS'], df1['R4H2WS'],
                 df1['R4H3WS'], df1['R4H4WS']]
    else:
        print('SQL Query: Invalid request error...')

    return sqlPM

