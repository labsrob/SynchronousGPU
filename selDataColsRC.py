"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Ramp count data
"""


def validCols(pParam):
    if pParam[0:3] == 'RC_':
        columns = ['id_col', 'sCentre', 'RAMPosA', 'rMarkerA', 'RAMPosB', 'rMarkerB', 'RAMPosC', 'rMarkerC', 'RAMPosD', 'rMarkerD', 'PipeDir', 'cLayer', 'totalR']

    elif pParam[0:3] == 'SPC_RC':
        columns = ['sCentre', 'RAMPosA', 'rMarkerA', 'RAMPosB', 'rMarkerB', 'RAMPosC', 'rMarkerC', 'RAMPosD', 'rMarkerD', 'PipeDir', 'cLayer', 'totalR']

    else:
        columns = 0
        print('Invalid Columns or Query error...')

    return columns
