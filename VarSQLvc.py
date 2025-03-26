"""
# This procedure determine what file to load from SQL server at PWartup
There are two SQL tables required for Monitoring Critial Process Variables
    1. The OEE Data
    2. Production Data (consiPWing of 9 tables)
All production procedure relies on Word Order Number - Assuming a Unique identity

Author: Dr Robert Labs
"""
# Variables required here: The aggregated plots for monitoring process variables
# ========================= VOID COUNT DATA TABLE ========================================#

def loadProcesValues(df1):
    sqlVC = [df1['sCentre'], df1['VDCount'], df1['VODPosA'], df1['VODPosB'],
             df1['VODPosC'], df1['VODPosD'], df1['PipeDir'], df1['cLayer']]

    return sqlVC