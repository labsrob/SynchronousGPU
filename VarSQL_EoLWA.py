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
    sqpWA = [df1['tStme'], df1['LyIDe'], df1['R1SPe'], df1['R1NVe'],
             df1['R2SPe'], df1['R2NVe'], df1['R3SPe'],
             df1['R3NVe'], df1['R4SPe'], df1['R4NVe']]

    return sqpWA
