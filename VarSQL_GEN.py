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
    sqlGEN = [df1['tStamp'], df1['cTensX'], df1['oTempA'], df1['oTempB'],
              df1['iTempA'], df1['iTempB'], df1['wSpedA'], df1['wSpedB'],
              df1['wSpedC'], df1['wSpedD'], df1['PipeDi'], df1['cLayer']]

    return sqlGEN

