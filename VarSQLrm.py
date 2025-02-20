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
    sqlRM = [df1['R1H1RM'], df1['R1H2RM'],
             df1['R1H3RM'], df1['R1H4RM'],
             df1['R2H1RM'], df1['R2H2RM'],
             df1['R2H3RM'], df1['R2H4RM'],
             df1['R3H1RM'], df1['R3H2RM'],
             df1['R3H3RM'], df1['R3H4RM'],
             df1['R4H1RM'], df1['R4H2RM'],
             df1['R4H3RM'], df1['R4H4RM']]


    return sqlRM