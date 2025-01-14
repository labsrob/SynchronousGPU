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
    sqlOEE = [df1['tStamp'], df1['cLayer'], df1['tCode'],
             df1['Desc'], df1['Lapsed'], df1['PipePos'],
             df1['nDiam'], df1['Ovality'], df1['tChange']]

    return sqlOEE

