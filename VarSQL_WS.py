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
    sqlWS = [df1['tStamp'], df1['cLayer'], df1['Ring1'], df1['Ring2'], df1['Ring3'], df1['Ring4']]

    return sqlWS
