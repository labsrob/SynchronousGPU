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
    sqlRM = [df1['id_col'], df1['R1Pos'], df1['R2Pos'],
             df1['R3Pos'], df1['R4Pos'], df1['PipeDir'], df1['cLayer']]

    return sqlRM