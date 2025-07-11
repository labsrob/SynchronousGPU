"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Ramp data
"""


def validCols(pParam, pWON=None):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'RM_' + pWON:
        columns = ['tStamp', 'R1Pos', 'R2Pos', 'R3Pos',
                   'R4Pos', 'PipeDir', 'cLayer']

    elif pParam == 'SPC_RM':
        columns = ['R1Pos', 'R2Pos', 'R3Pos', 'R4Pos', 'PipeDir', 'cLayer']

    else:
        print('Invalid Columns or Query error...')

    return columns
