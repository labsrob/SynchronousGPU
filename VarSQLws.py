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
    sqlWS = [df1['R1H1WS(m/s)'], df1['R1H2WS(m/s)'],
            df1['R1H3WS(m/s)'], df1['R1H4WS(m/s)'],
            df1['R2H1WS(m/s)'], df1['R2H2WS(m/s)'],
            df1['R2H3WS(m/s)'], df1['R2H4WS(m/s)'],
            df1['R3H1WS(m/s)'], df1['R3H2WS(m/s)'],
            df1['R3H3WS(m/s)'], df1['R3H4WS(m/s)'],
            df1['R4H1WS(m/s)'], df1['R4H2WS(m/s)'],
            df1['R4H3WS(m/s)'], df1['R4H4WS(m/s)']]


    return sqlWS

