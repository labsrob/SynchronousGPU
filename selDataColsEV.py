"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
YTape Void count data
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'EV':
        columns = ['tStamp', 'cLayer', 'oTempA', 'oTempB', 'cRTemp', 'cHumid',
                   'fDTemp', 'fHumid', 'locTemp', 'locHumid', 'UVIndex']
    else:
        print('Invalid Columns or Query error...')

    return columns
