"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Check SQL data columns ...
"""


def validCols(pParam, pWON=None):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'WS1_' + pWON:
        columns = ['tStamp', 'cLayer', 'R1H1WS', 'R1H2WS',
                   'R1H3WS', 'R1H4WS', 'R2H1WS', 'R2H2WS',
                   'R2H3WS', 'R2H4WS']

    elif pParam == 'WS2_' + pWON:
        columns = ['tStamp', 'cLayer', 'R3H1WS', 'R3H2WS',
                   'R3H3WS', 'R3H4WS', 'R4H1WS', 'R4H2WS',
                   'R4H3WS', 'R4H4WS']

    elif pParam == 'SPC_WS':
        columns = ['cLayer', 'R1H1', 'R1H2', 'R1H3', 'R1H4',
                   'R2H1', 'R2H2', 'R2H3', 'R2H4', 'R3H1',
                   'R3H2', 'R3H3', 'R3H4', 'R4H1', 'R4H2',
                   'R4H3', 'R4H4']
    else:
        print('Invalid Columns or Query error...')

    return columns
