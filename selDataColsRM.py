"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Ramp data
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'RM':
        columns = ['tStamp', 'R1Pos', 'R2Pos', 'R3Pos',
                   'R4Pos', 'PipeDir', 'cLayer']
    else:
        print('Invalid Columns or Query error...')

    return columns
