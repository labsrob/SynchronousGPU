"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Ramp count data
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'RC':
        columns = ['sCentre', 'RMCount', 'RAMPosA', 'RAMPosB', 'RAMPosC', 'RAMPosD', 'PipeDir', 'cLayer']
    else:
        print('Invalid Columns or Query error...')

    return columns
