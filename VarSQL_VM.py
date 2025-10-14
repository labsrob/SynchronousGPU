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
    sqlVM = [df1['sCount'], df1['sCenter'], df1['AvgGap'],
             df1['MaxGap'], df1['cLayer'], df1['sDistance']]
            # df1['id_col'],
    return sqlVM