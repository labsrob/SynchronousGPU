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
    plcLA = [df1['tStamp'], df1['cLayer'], df1['R1H1LA'],
             df1['R1H2LA'], df1['R1H3LA'], df1['R1H4LA'],
             df1['R2H1LA'], df1['R2H2LA'], df1['R2H3LA'],
             df1['R2H4LA'], df1['R3H1LA'], df1['R3H2LA'],
             df1['R3H3LA'], df1['R3H4LA'], df1['R4H1LA'],
             df1['R4H2LA'], df1['R4H3LA'], df1['R4H4LA']]

    return plcLA
