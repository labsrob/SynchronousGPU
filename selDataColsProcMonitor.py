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
    if pParam == 'T1':  # GENeric Table Winding Speed etc
        columns = ['tStamp', 'cTensX', 'oTempA', 'oTempB', 'iTempA', 'iTempB',
                   'wSpedA', 'wSpedB', 'wSpedC', 'wSpedD', 'PipeDi', 'cLayer']

    elif pParam == 'T2':    # Roller Pressure
        columns = ['cLayer', 'R1H1RP', 'R1H2RP', 'R1H3RP', 'R1H4RP',
                   'R2H1RP', 'R2H2RP', 'R2H3RP', 'R2H4RP',
                   'R3H1RP', 'R3H2RP', 'R3H3RP', 'R3H4RP',
                   'R4H1RP', 'R4H2RP',' R4H3RP', 'R4H4RP']

    elif pParam == 'T3': # Environmental Variables
        columns = ['tStamp', 'cLayer', 'oTempA', 'oTempB', 'cRTemp', 'cHumid',
                   'fDTemp', 'fHumid', 'locTemp', 'locHumid', 'UVIndex']

    elif pParam == 'T4': # Ramp Profile
        columns = ['tStamp', 'R1Pos', 'R2Pos', 'R3Pos',
                   'R4Pos', 'PipeDir', 'cLayer']

    elif pParam == 'T5': # Void Profile
        columns = ['sCount', 'sCenter', 'AvgGap',
                   'MaxGap', 'cLayer', 'sDistance']

    elif pParam == 'T6':    # Ramp Count
        columns = ['sCentre', 'RMCount', 'RAMPosA', 'RAMPosB', 'RAMPosC', 'RAMPosD', 'PipeDir', 'cLayer']

    elif pParam == 'T7':    # Void Count
        columns = ['sCentre', 'VDCount', 'VODPosA', 'VODPosB', 'VODPosC', 'VODPosD', 'PipeDir', 'cLayer']

    elif pParam == 'T8':
        columns = [ # Laser Power ------------------[]
                   'cLayer', 'R1H1LP', 'R1H2LP', 'R1H3LP', 'R1H4LP',
                   'R2H1LP', 'R2H2LP', 'R2H3LP', 'R2H4LP',
                   'R3H1LP', 'R3H2LP', 'R3H3LP', 'R3H4LP',
                   'R4H1LP', 'R4H2LP', 'R4H3LP', 'R4H4LP']

    elif pParam == 'T9':
        columns = [ # Laser Angle ---------------------[]
                   'cLayer', 'R1H1LA', 'R1H2LA', 'R1H3LA', 'R1H4LA',
                   'R2H1LA', 'R2H2LA', 'R2H3LA', 'R2H4LA',
                   'R3H1LA', 'R3H2LA', 'R3H3LA', 'R3H4LA',
                   'R4H1LA', 'R4H2LA', 'R4H3LA', 'R4H4LA',]

    else:
        print('Invalid Columns or Query error...')

    return columns
