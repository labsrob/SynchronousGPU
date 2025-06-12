"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Roller Pressure measured in Pascal (Pa)
"""

def validCols(pParam, WON):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'GEN_'+ WON[0]:
        columns = ['tStamp', 'cTensX', 'oTempA', 'oTempB',
                   'iTempA', 'iTempB', 'wSpeedA', 'wSpeedB', 'wSpeedC', 'wSpeedD', 'PipeDi', 'cLayer']
    else:
        print('Invalid Columns or Query error...')

    return columns