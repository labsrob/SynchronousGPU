"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
YTape Void count data
"""


def validCols(pParam, pWON=None):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'EV_' + pWON:
        columns = ['tStamp', 'cLayer', 'Line1Temp', 'Line2Temp',
                   'Line3Temp', 'Line4Temp', 'Line5Temp', 'Line1Humi',
                    'Line2Humi',  'Line3Humi', 'Line4Humi', 'Line5Humi']

    elif pParam == 'SPC_EV':
        columns = ['cLayer', 'Line1Temp', 'Line2Temp',
                   'Line3Temp', 'Line4Temp', 'Line5Temp', 'Line1Humi',
                    'Line2Humi',  'Line3Humi', 'Line4Humi', 'Line5Humi']

    else:
        print('Invalid Columns or Query error...')

    return columns
