"""
# This procedure determine what file to load from SQL server at PWartup
There are two SQL tables required for Monitoring Critial Process Variables
    1. The OEE Data
    2. Production Data (consiPWing of 9 tables)
All production procedure relies on Word Order Number - Assuming a Unique identity

Author: Dr Robert Labs
"""


# Variables required here: Environmental variables
# pull data from simotion and Met Office for location specific data

def loadProcesValues(df1):
    sqlEV = [df1['tStamp'], df1['cLayer'], df1['cTensionA'], df1['cTensionB'], df1['cRTemp'],
             df1['cHumid'], df1['fDTemp'], df1['fHumid'], df1['locTemp'], df1['locHumid'], df1['UVIndex']]

    return sqlEV