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
    plcRP = [df1['R1H1RPF(Pa)'], df1['R1H2RP(Pa)'],
            df1['R1H3RP(Pa)'], df1['R1H4RP(Pa)'],
            df1['R2H1RP(Pa)'], df1['R2H2RP(Pa)'],
            df1['R2H3RP(Pa)'], df1['R2H4RP(Pa)'],
            df1['R3H1RP(Pa)'], df1['R3H2RP(Pa)'],
            df1['R3H3RP(Pa)'], df1['R3H4RP(Pa)'],
            df1['R4H1RP(Pa)'], df1['R4H2RP(Pa)'],
            df1['R4H3RP(Pa)'], df1['R4H4RP(Pa)']]

    return plcRP
