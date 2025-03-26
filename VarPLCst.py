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
    plcST = [df1['R1H1ST'], df1['R1H2ST'],
            df1['R1H3ST'], df1['R1H4ST'],
            df1['R2H1ST'], df1['R2H2ST'],
            df1['R2H3ST'], df1['R2H4ST'],
            df1['R3H1ST'], df1['R3H2ST'],
            df1['R3H3ST'], df1['R3H4ST'],
            df1['R4H1ST'], df1['R4H2ST'],
            df1['R4H3ST'], df1['R4H4ST']]

    return plcST
