"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
2-D Void Mapping Data
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'VM':
        columns = ['tStamp', 'sCount', 'sCenter',
                   'AvgGap', 'PipePos', 'vCount']
    else:
        print('Invalid Columns or Query error...')

    return columns
