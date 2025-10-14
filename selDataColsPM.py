"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Check SQL data columns ...
"""
# sequel data columns for process monitors 'id_col',

def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam[0:4] == 'GEN_':      # GENeric Table Winding Speed etc
        columns = ['id_col', 'cTensX', 'oTempA', 'oTempB', 'iTempA', 'iTempB',
                   'iTempC', 'iTempD', 'wSpedA', 'wSpedB', 'wSpedC',
                   'wSpedD', 'cLayer']

    elif pParam[0:4] == 'RP1_':    # Roller Pressure
        columns = ['cLayer',
                   'R1H1RP', 'R1H2RP', 'R1H3RP', 'R1H4RP',
                   'R2H1RP', 'R2H2RP', 'R2H3RP', 'R2H4RP']

    elif pParam[0:4] == 'RP2_':
        columns = ['cLayer',
                   'R3H1RP', 'R3H2RP', 'R3H3RP', 'R3H4RP',
                   'R4H1RP', 'R4H2RP', 'R4H3RP', 'R4H4RP']

    elif pParam[0:3] == 'WS_':
        columns = [ # Laser Power ------------------[]
                   'id_col', 'cLayer', 'Ring1', 'Ring2', 'Ring3', 'Ring4']

    elif pParam[0:4] == 'LP1_':
        columns = [ # Laser Power ------------------[]
                   'id_col', 'cLayer',
                   'R1H1LP', 'R1H2LP', 'R1H3LP', 'R1H4LP',
                   'R2H1LP', 'R2H2LP', 'R2H3LP', 'R2H4LP']

    elif pParam[0:4] == 'LP2_':
        columns = [ # Laser Power ------------------[]
                    'id_col', 'cLayer',
                    'R3H1LP', 'R3H2LP', 'R3H3LP', 'R3H4LP',
                    'R4H1LP', 'R4H2LP', 'R4H3LP', 'R4H4LP']

    elif pParam[0:4] == 'LA1_':
        columns = [ # Laser Angle ---------------------[]
                   'id_col', 'cLayer',
                   'R1H1LA', 'R1H2LA', 'R1H3LA', 'R1H4LA',
                   'R2H1LA', 'R2H2LA', 'R2H3LA', 'R2H4LA']

    elif pParam[0:4] == 'LA2_':
        columns = [ # Laser Angle ---------------------[]
                   'id_col', 'cLayer',
                   'R3H1LA', 'R3H2LA', 'R3H3LA', 'R3H4LA',
                   'R4H1LA', 'R4H2LA', 'R4H3LA', 'R4H4LA']


    else:
        columns = 0
        print('Invalid Columns or Query error...')

    return columns
