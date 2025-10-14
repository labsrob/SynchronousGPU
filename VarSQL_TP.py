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
    sqlTP = [df1['cLayer'],
             df1['R1H1TP'], df1['R1H2TP'], df1['R1H3TP'],
             df1['R1H4TP'], df1['R2H1TP'], df1['R2H2TP'],
             df1['R2H3TP'], df1['R2H4TP'],
             df1['cLayer'],
             df1['R3H1TP'], df1['R3H2TP'], df1['R3H3TP'],
             df1['R3H4TP'], df1['R4H1TP'], df1['R4H2TP'],
             df1['R4H3TP'], df1['R4H4TP']]

    return sqlTP
