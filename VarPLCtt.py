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
    plcTT = [df1['R1H1TT'], df1['R1H2TT'],
             df1['R1H3TT'], df1['R1H4TT'],
             df1['R2H1TT'], df1['R2H2TT'],
             df1['R2H3TT'], df1['R2H4TT'],
             df1['R3H1TT'], df1['R3H2TT'],
             df1['R3H3TT'], df1['R3H4TT'],
             df1['R4H1TT'], df1['R4H2TT'],
             df1['R4H3TT'], df1['R4H4TT']]

    return plcTT
