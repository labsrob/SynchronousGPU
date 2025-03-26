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
    plcRF = [df1['R1H1RF'], df1['R1H2RF'],
            df1['R1H3RF'], df1['R1H4RF'],
            df1['R2H1RF'], df1['R2H2RF'],
            df1['R2H3RF'], df1['R2H4RF'],
            df1['R3H1RF'], df1['R3H2RF'],
            df1['R3H3RF'], df1['R3H4RF'],
            df1['R4H1RF'], df1['R4H2RF'],
            df1['R4H3RF'], df1['R4H4RF']]


    return plcRF

