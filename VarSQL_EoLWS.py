"""
# This procedure determine what file to load from SQL server at PWartup
There are two SQL tables required for Monitoring Critial Process Variables
    1. The OEE Data
    2. Production Data (consiPWing of 9 tables)
All production procedure relies on Word Order Number - Assuming a Unique identity

Author: Dr Robert Labs
"""
# Variables required here: The aggregated plots for monitoring process variables


def loadProcesValues(df1):
    sqpWS = [df1['tStmd'], df1['LyIDd'], df1['R1SPd'], df1['R1NVd'],
             df1['R2SPd'], df1['R2NVd'], df1['R3SPd'],
             df1['R3NVd'], df1['R4SPd'], df1['R4NVd']]

    return sqpWS