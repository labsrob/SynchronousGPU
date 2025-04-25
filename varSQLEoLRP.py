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
    sqlEOLRP = [df1['tStmb'], df1['LyIDb'], df1['R1SPb'],  df1['R1NVb'], df1['R2SPb'],
             df1['R2NVb'], df1['R3SPb'], df1['R3NVb'], df1['R4SPb'], df1['R4NVb'] ]

    return sqlEOLRP
