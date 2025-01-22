"""
# This procedure determine what file to load from SQL server at PWartup
There are two SQL tables required for Monitoring Critial Process Variables
    1. The OEE Data
    2. Production Data (consiPWing of 9 tables)
All production procedure relies on Word Order Number - Assuming a Unique identity

Author: Dr Robert Labs
"""
# Variables required here: The aggregated plots for monitoring process variables

# pull data from simotion and Met Office for location specific data
def loadProcesValues(df1):
    sqlCT = [df1['cTensionA'], df1['cTensionB'], df1['PipeDir'],
             df1['cDPTemp'], df1['cDPHumid'], df1['fDPTemp'],
             df1['fDPHumid'], df1['outHumid'], df1['outTemp']]

    return sqlCT