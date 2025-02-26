"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Check SQL data columns ...
"""
# sequel data columns for process monitors

def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'T1':
        columns = [ # Roller Pressure --------------[]
                    'R1H1RP', 'R1H2RP', 'R1H3RP', 'R1H4RP',
                   'R2H1RP', 'R2H2RP', 'R2H3RP', 'R2H4RP',
                   'R3H1RP', 'R3H2RP', 'R3H3RP', 'R3H4RP',
                   'R4H1RP', 'R4H2RP', 'R4H3RP', 'R4H4RP',]

    elif pParam == 'T2':
        columns = [
                   # Winding Speed ---------------[]
                   'R1H1WS', 'R1H2WS', 'R1H3WS', 'R1H4LA',
                   'R2H1WS', 'R2H2WS', 'R2H3WS', 'R2H4WS',
                   'R3H1WS', 'R3H2WS', 'R3H3WS', 'R3H4WS',
                   'R4H1WS', 'R4H2WS', 'R4H3WS', 'R4H4WS']

    elif pParam == 'T3':
        columns = [
                   # Cell Tension & Oven Temp ----[]
                   'tStamp', 'oTempA', 'oTempB', 'cTensA',
                   'cTensB', 'PipeDi', 'cRTemp', 'cHumid',
                   'fDTemp', 'fHumid', 'locTemp', 'locHumid',
                   'UVIndex']

    elif pParam == 'T4':
        columns = [ # Laser Power ------------------[]
                    'R1H1LP', 'R1H2LP', 'R1H3LP', 'R1H4LP',
                   'R2H1LP', 'R2H2LP', 'R2H3LP', 'R2H4LP',
                   'R3H1LP', 'R3H2LP', 'R3H3LP', 'R3H4LP',
                   'R4H1LP', 'R4H2LP', 'R4H3LP', 'R4H4LP',]

    elif pParam == 'T5':
        columns = [ # Laser Angle ---------------------[]
                   'R1H1LA', 'R1H2LA', 'R1H3LA', 'R1H4LA',
                   'R2H1LA', 'R2H2LA', 'R2H3LA', 'R2H4LA',
                   'R3H1LA', 'R3H2LA', 'R3H3LA', 'R3H4LA',
                   'R4H1LA', 'R4H2LA', 'R4H3LA', 'R4H4LA',]

    if pParam == 'T6':
        columns = [ # Cell Tension & Oven Temp ---------[]
                   'tStamp', 'oTempA', 'oTempB', 'cTensA',
                   'cTensB', 'PipeDi', 'cRTemp', 'cHumid',
                   'fDTemp', 'fHumid', 'locTemp', 'locHumid',
                   'UVIndex',]

    elif pParam == 'T7':
        columns = [ # Roller Pressure ------------------[]
                   'R1H1RP', 'R1H2RP', 'R1H3RP', 'R1H4RP',
                   'R2H1RP', 'R2H2RP', 'R2H3RP', 'R2H4RP',
                   'R3H1RP', 'R3H2RP', 'R3H3RP', 'R3H4RP',
                   'R4H1RP', 'R4H2RP', 'R4H3RP', 'R4H4RP']

    elif pParam == 'T8':
        columns = [ # Tape Winding Speed ---------------[]
                   'R1H1WS', 'R1H2WS', 'R1H3WS', 'R1H4WS',
                   'R2H1WS', 'R2H2WS', 'R2H3WS', 'R2H4WS',
                   'R3H1WS', 'R3H2WS', 'R3H3WS', 'R3H4WS',
                   'R4H1WS', 'R4H2WS', 'R4H3WS', 'R4H4WS']

    else:
        print('Invalid Columns or Query error...')

    return columns
