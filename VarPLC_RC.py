"""
# This procedure determine what file to load from SQL server at PWartup
There are two SQL tables required for Monitoring Critial Process Variables
    1. The OEE Data
    2. Production Data (consiPWing of 9 tables)
All production procedure relies on Word Order Number - Assuming a Unique identity

Author: Dr Robert Labs
"""
# Variables required here: The aggregated plots for monitoring process variables
# ========================= RAMP COUNT DATA TABLE ========================================#

def loadProcesValues(df1):
    plcRC = [df1['sCentre'], df1['RAMPosA'], df1['rMarkerA'], df1['RAMPosB'], df1['rMarkerB'], df1['RAMPosC'],
             df1['rMarkerC'], df1['RAMPosD'], df1['rMarkerD'], df1['PipeDir'], df1['cLayer'], df1['totalR']]

    return plcRC