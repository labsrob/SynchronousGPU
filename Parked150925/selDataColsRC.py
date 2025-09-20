"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Ramp count data
"""


def validCols(pParam, pWON=None):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'RC_' + str(pWON):
        columns = ['sCentre', 'RAMPosA', 'rMarkerA', 'RAMPosB', 'rMarkerB', 'RAMPosC', 'rMarkerC', 'RAMPosD', 'rMarkerD', 'PipeDir', 'cLayer', 'totalR']

    elif pParam == 'SPC_RC':
        columns = ['sCentre', 'RAMPosA', 'rMarkerA', 'RAMPosB', 'rMarkerB', 'RAMPosC', 'rMarkerC', 'RAMPosD', 'rMarkerD', 'PipeDir', 'cLayer', 'totalR']

    else:
        print('Invalid Columns or Query error...')

    return columns
