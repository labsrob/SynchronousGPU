"""
# This procedure determine what file to load from SQL server at PWartup
There are two SQL tables required for Monitoring Critial Process Variables
    1. The OEE Data
    2. Production Data (consiPWing of 9 tables)
All production procedure relies on Word Order Number - Assuming a Unique identity

Author: Dr Robert Labs
"""
# MONITORING VARIABLES: The aggregated plots for monitoring process variables


def loadProcesValues(df1, prod):        # Load useful columns out of many
    if prod == 'DNV':
        # -------- Tape Temperature --------[T1]
        sqlEOL = [df1['R1H1TT'], df1['R1H2TT'],
                  df1['R1H3TT'], df1['R1H4TT'],
                  df1['R2H1TT'], df1['R2H2TT'],
                  df1['R2H3TT'], df1['R2H4TT'],
                  df1['R3H1TT'], df1['R3H2TT'],
                  df1['R3H3TT'], df1['R3H4TT'],
                  df1['R4H1TT'], df1['R4H2TT'],
                  df1['R4H3TT'], df1['R4H4TT'],
                  # ------ Substrate Temp ----[T2]
                  df1['R1H1ST'], df1['R1H2ST'],
                  df1['R1H3ST'], df1['R1H4ST'],
                  df1['R2H1ST'], df1['R2H2ST'],
                  df1['R2H3ST'], df1['R2H4ST'],
                  df1['R3H1ST'], df1['R3H2ST'],
                  df1['R3H3ST'], df1['R3H4ST'],
                  df1['R4H1ST'], df1['R4H2ST'],
                  df1['R4H3ST'], df1['R4H4ST'],
                  # ------ Substrate Temp ----[T3]
                  df1['GaugeA1'], df1['GaugeA2'],
                  df1['GaugeA3'], df1['GaugeA4'],
                  df1['GaugeB1'], df1['GaugeB2'],
                  df1['GaugeB3'], df1['GaugeB4'],
                  # ------- Ramp Data --------[T4]
                  df1['tStamp'], df1['R1Pos'],
                  df1['R2Pos'], df1['R3Pos'],
                  df1['R4Pos'], df1['PipeDir'],
                  df1['cLayer']]

    elif prod == 'MGM':
        sqlEOL = [df1['R1H1TT'], df1['R1H2TT'],
                  df1['R1H3TT'], df1['R1H4TT'],
                  df1['R2H1TT'], df1['R2H2TT'],
                  df1['R2H3TT'], df1['R2H4TT'],
                  df1['R3H1TT'], df1['R3H2TT'],
                  df1['R3H3TT'], df1['R3H4TT'],
                  df1['R4H1TT'], df1['R4H2TT'],
                  df1['R4H3TT'], df1['R4H4TT'],
                  # ------ Substrate Temp ----[T2]
                  df1['R1H1ST'], df1['R1H2ST'],
                  df1['R1H3ST'], df1['R1H4ST'],
                  df1['R2H1ST'], df1['R2H2ST'],
                  df1['R2H3ST'], df1['R2H4ST'],
                  df1['R3H1ST'], df1['R3H2ST'],
                  df1['R3H3ST'], df1['R3H4ST'],
                  df1['R4H1ST'], df1['R4H2ST'],
                  df1['R4H3ST'], df1['R4H4ST'],
                  # ------ Substrate Temp ----[T3]
                  df1['GaugeA1'], df1['GaugeA2'],
                  df1['GaugeA3'], df1['GaugeA4'],
                  df1['GaugeB1'], df1['GaugeB2'],
                  df1['GaugeB3'], df1['GaugeB4'],
                  # ------- Ramp Data --------[T4]
                  df1['tStamp'], df1['R1Pos'],
                  df1['R2Pos'], df1['R3Pos'],
                  df1['R4Pos'], df1['PipeDir'],
                  df1['cLayer'],
                  # - Laser Power Monitoring --[T5]
                  df1['R1H1LP'], df1['R1H2LP'],
                  df1['R1H3LP'], df1['R1H4LP'],
                  df1['R2H1LP'], df1['R2H2LP'],
                  df1['R2H3LP'], df1['R2H4LP'],
                  df1['R3H1LP'], df1['R3H2LP'],
                  df1['R3H3LP'], df1['R3H4LP'],
                  df1['R4H1LP'], df1['R4H2LP'],
                  df1['R4H3LP'], df1['R4H4LP'],
                  # -------- Laser Angle ----[T6]
                  df1['R1H1LA'], df1['R1H2LA'],
                  df1['R1H3LA'], df1['R1H4LA'],
                  df1['R2H1LA'], df1['R2H2LA'],
                  df1['R2H3LA'], df1['R2H4LA'],
                  df1['R3H1LA'], df1['R3H2LA'],
                  df1['R3H3LA'], df1['R3H4LA'],
                  df1['R4H1LA'], df1['R4H2LA'],
                  df1['R4H3LA'], df1['R4H4LA'],
                  # Tape Placement Error ----[T7]
                  df1['R1H1TP'], df1['R1H2TP'],
                  df1['R1H3TP'], df1['R1H4TP'],
                  df1['R2H1TP'], df1['R2H2TP'],
                  df1['R2H3TP'], df1['R2H4TP'],
                  df1['R3H1TP'], df1['R3H2TP'],
                  df1['R3H3TP'], df1['R3H4TP'],
                  df1['R4H1TP'], df1['R4H2TP'],
                  df1['R4H3TP'], df1['R4H4TP'],
                  # Tape Speed --------------[T8]
                  df1['R1H1RF'], df1['R1H2RF'],
                  df1['R1H3RF'], df1['R1H4RF'],
                  df1['R2H1RF'], df1['R2H2RF'],
                  df1['R2H3RF'], df1['R2H4RF'],
                  df1['R3H1RF'], df1['R3H2RF'],
                  df1['R3H3RF'], df1['R3H4RF'],
                  df1['R4H1RF'], df1['R4H2RF'],
                  df1['R4H3RF'], df1['R4H4RF']]
    else:
        print('SQL Query: Invalid request error...')

    return sqlEOL

