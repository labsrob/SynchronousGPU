"""
# This procedure determine what file to load from SQL server at PWartup
There are two SQL tables required for Monitoring Critial Process Variables
    1. The OEE Data
    2. Production Data (consiPWing of 9 tables)
All production procedure relies on Word Order Number - Assuming a Unique identity

Author: Dr Robert Labs
"""
# Variables required here: The aggregated plots for monitoring process variables
# 1. Laser Power, 2. Laser Angle, 3. Tape Speed


def loadProcesValues(df1):
    plcTT = [df1['R1H1TT(°C)'], df1['R1H2TT(°C)'],
            df1['R1H3TT(°C)'], df1['R1H4TT(°C)'],
            df1['R2H1TT(°C)'], df1['R2H2TT(°C)'],
            df1['R2H3TT(°C)'], df1['R2H4TT(°C)'],
            df1['R3H1TT(°C)'], df1['R3H2TT(°C)'],
            df1['R3H3TT(°C)'], df1['R3H4TT(°C)'],
            df1['R4H1TT(°C)'], df1['R4H2TT(°C)'],
            df1['R4H3TT(°C)'], df1['R4H4TT(°C)']]

    return plcTT
