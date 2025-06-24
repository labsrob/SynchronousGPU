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
    sqlWS = [df1['tStamp'], df1['cLayer'], df1['R1H1WA'], df1['R1H2WA'],
             df1['R1H3WA'], df1['R1H4WA'], df1['R2H1WA'], df1['R2H2WA'],
             df1['R2H3WA'], df1['R2H4WA'], df1['tStamp'], df1['cLayer'],
             df1['R3H1WA'], df1['R3H2WA'], df1['R3H3WA'], df1['R3H4WA'],
             df1['R4H1WA'], df1['R4H2WA'], df1['R4H3WA'], df1['R4H4WA']]

    return sqlWS
