"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
YTape Void count data
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'GEN':
        columns = ['tStamp', 'cTensX', 'oTempA', 'oTempB', 'iTempA', 'iTempB',
                   'wSpedA', 'wSpedB', 'wSpedC', 'wSpedD', 'PipeDi', 'cLayer']
    else:
        print('Invalid Columns or Query error...')

    return columns