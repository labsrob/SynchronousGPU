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
    sqlST = [df1['R1H1ST(°C)'], df1['R1H2ST(°C)'],
            df1['R1H3ST(°C)'], df1['R1H4ST(°C)'],
            df1['R2H1ST(°C)'], df1['R2H2ST(°C)'],
            df1['R2H3ST(°C)'], df1['R2H4ST(°C)'],
            df1['R3H1ST(°C)'], df1['R3H2ST(°C)'],
            df1['R3H3ST(°C)'], df1['R3H4ST(°C)'],
            df1['R4H1ST(°C)'], df1['R4H2ST(°C)'],
            df1['R4H3ST(°C)'], df1['R4H4ST(°C)']]


    return sqlST

