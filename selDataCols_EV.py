"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
YTape Void count data
"""


def validCols(pParam):

    if pParam[0:3] == 'EV_':
        columns = ['id_col', 'cLayer', 'Line1Temp', 'Line2Temp',
                   'Line3Temp', 'Line4Temp', 'Line5Temp', 'Line1Humi',
                    'Line2Humi', 'Line3Humi', 'Line4Humi', 'Line5Humi']

    elif pParam[0:3] == 'SPC_EV':
        columns = ['cLayer', 'Line1Temp', 'Line2Temp',
                   'Line3Temp', 'Line4Temp', 'Line5Temp', 'Line1Humi',
                    'Line2Humi', 'Line3Humi', 'Line4Humi', 'Line5Humi']

    else:
        columns = 0
        print('Invalid Columns or Query error...')

    return columns
