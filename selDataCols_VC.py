"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
YTape Void count data
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam[0:3] == 'VC_':  # 'id_col',
        columns = ['id_col', 'sCentre', 'VODPosA', 'vMarkerA', 'VODPosB',
                   'vMarkerB', 'VODPosC', 'vMarkerC', 'VODPosD', 'vMarkerD',
                   'PipeDir', 'cLayer', 'totalV']

    else:
        print('Invalid Columns or Query error...')

    return columns
