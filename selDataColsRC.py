"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Ramp count data
"""


def validCols(pParam, pWON=None):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'RC_' + pWON:
        columns = ['sCentre', 'RMCount', 'RAMPosA', 'RAMPosB', 'RAMPosC', 'RAMPosD', 'PipeDir', 'cLayer']

    elif pParam == 'SPC_RC':
        columns = ['sCentre', 'RMCount', 'RAMPosA', 'RAMPosB', 'RAMPosC', 'RAMPosD', 'PipeDir', 'cLayer']

    else:
        print('Invalid Columns or Query error...')

    return columns
