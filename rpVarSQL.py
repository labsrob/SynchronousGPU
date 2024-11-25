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
    sqlRP = [df1['R1H1RollerForce(N)'], df1['R1H2RollerForce(N)'],
            df1['R1H3RollerForce(N)'], df1['R1H4RollerForce(N)'],
            df1['R2H1RollerForce(N)'], df1['R2H2RollerForce(N)'],
            df1['R2H3RollerForce(N)'], df1['R2H4RollerForce(N)'],
            df1['R3H1RollerForce(N)'], df1['R3H2RollerForce(N)'],
            df1['R3H3RollerForce(N)'], df1['R3H4RollerForce(N)'],
            df1['R4H1RollerForce(N)'], df1['R4H2RollerForce(N)'],
            df1['R4H3RollerForce(N)'], df1['R4H4RollerForce(N)']]

    return sqlRP

