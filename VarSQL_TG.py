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
    sqlTG = [df1['tStamp'], df1['cLayer'], df1['sCount'], df1['sCenter'],
             df1['PipePos'], df1['GaugeA1'], df1['GaugeA2'], df1['GaugeA3'],
             df1['GaugeA4'], df1['GaugeB1'], df1['GaugeB2'], df1['GaugeB3'],
             df1['GaugeB4'], df1['PipeDir']]


    return sqlTG

