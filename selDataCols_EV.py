"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
YTape Void count data
"""


def validCols(pParam, pWON=None):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'EV' + pWON:
        columns = ['tStamp', 'cLayer', 'cRTemp', 'cHumid', 'fDTemp',
                   'fHumid', 'locTemp', 'locHumid', 'UVIndex']

    elif pParam == 'SPC_EV':
        columns = ['cLayer', 'cRTemp', 'cHumid', 'fDTemp',
                   'fHumid', 'locTemp', 'locHumid', 'UVIndex']

    else:
        print('Invalid Columns or Query error...')

    return columns
