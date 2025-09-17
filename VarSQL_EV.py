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
    sqlEV = [df1['cLayer'], df1['Line1Temp'], df1['Line2Temp'],
             df1['Line3Temp'], df1['Line4Temp'], df1['Line5Temp'], df1['Line1Humi'],
             df1['Line2Humi'],  df1['Line3Humi'], df1['Line4Humi'], df1['Line5Humi']]

    return sqlEV