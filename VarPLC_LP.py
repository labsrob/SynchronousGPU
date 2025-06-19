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
    plcLP = [df1['tStamp'], df1['cLayer'], df1['R1H1LP'],
             df1['R1H2LP'], df1['R1H3LP'], df1['R1H4LP'],
             df1['R2H1LP'], df1['R2H2LP'], df1['R2H3LP'],
             df1['R2H4LP'], df1['R3H1LP'], df1['R3H2LP'],
             df1['R3H3LP'], df1['R3H4LP'], df1['R4H1LP'],
             df1['R4H2LP'], df1['R4H3LP'], df1['R4H4LP']]

    return plcLP
