"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'WS':
        columns = ['TimeLine', 'SpeedRing1', 'SpeedRing2', 'SpedRing3', 'SpeedRing4', 'PipePosition']
    else:
        print('Invalid Columns or Query error...')

    return columns
