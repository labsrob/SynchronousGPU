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
    vizTG = [df1['id_col'], df1['cLyr'], df1['R1SP'], df1['R1NV'],
             df1['R2SP'], df1['R2NV'], df1['R3SP'],
             df1['R3NV'], df1['R4SP'], df1['R4NV']]

    return vizTG