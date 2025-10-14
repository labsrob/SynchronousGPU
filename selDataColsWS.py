"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Check SQL data columns ...
"""


def validCols(pParam, pWON=None):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'WS_' + pWON:
        columns = ['id_col', 'cLayer', 'Ring1', 'Ring2', 'Ring3', 'Ring4']

    elif pParam == 'SPC_WS':
        columns = ['cLayer', 'Ring1', 'Ring2', 'Ring3', 'Ring4']

    else:
        print('Invalid Columns or Query error...')

    return columns
