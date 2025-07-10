"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
YTape Void count data
"""


def validCols(pParam, pWON=None):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'VC_' + pWON:
        columns = ['sCentre', 'VODPosA', 'vMarkerA', 'VODPosB', 'vMarkerB', 'VODPosC',
                   'vMarkerC', 'VODPosD', 'vMarkerD', 'PipeDir', 'cLayer', 'totalV']

    elif pParam == 'SPC_VC':
        columns = ['sCentre', 'VODPosA', 'vMarkerA', 'VODPosB', 'vMarkerB', 'VODPosC',
                   'vMarkerC', 'VODPosD', 'vMarkerD', 'PipeDir', 'cLayer', 'totalV']

    else:
        print('Invalid Columns or Query error...')

    return columns
