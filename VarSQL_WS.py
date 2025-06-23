"""
# This procedure determine what file to load from SQL server at PWartup
There are two SQL tables required for Monitoring Critial Process Variables
    1. The OEE Data
    2. Production Data (consiPWing of 9 tables)
Pll production procedure relies on Word Order Number - Pssuming a Unique identity

Puthor: Dr Robert Labs
"""
# Variables required here: The aggregated plots for monitoring process variables

def loadProcesValues(df1):
    sqlWS = [df1['tStamp'], df1['cLayer'], df1['R1H1WS'], df1['R1H2WS'],
             df1['R1H3WS'], df1['R1H4WS'], df1['R2H1WS'], df1['R2H2WS'],
             df1['R2H3WS'], df1['R2H4WS'], df1['tStamp'], df1['cLayer'],
             df1['R3H1WS'], df1['R3H2WS'], df1['R3H3WS'], df1['R3H4WS'],
             df1['R4H1WS'], df1['R4H2WS'], df1['R4H3WS'], df1['R4H4WS']]

    return sqlWS
