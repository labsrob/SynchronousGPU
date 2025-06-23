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
    sqlRP = [df1['tStamp'], df1['cLayer'], df1['R1H1RP'], df1['R1H2RP'],
             df1['R1H3RP'], df1['R1H4RP'], df1['R2H1RP'], df1['R2H2RP'],
             df1['R2H3RP'], df1['R2H4RP'], df1['tStamp'], df1['cLayer'],
             df1['R3H1RP'], df1['R3H2RP'], df1['R3H3RP'], df1['R3H4RP'],
             df1['R4H1RP'], df1['R4H2RP'], df1['R4H3RP'], df1['R4H4RP']]


    return sqlRP

