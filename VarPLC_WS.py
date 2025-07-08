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
    plcWS = [df1['cLayer'], df1['Ring1'], df1['Ring2'], df1['Ring3'], df1['Ring4']]

    return plcWS
