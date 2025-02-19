"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Overall Equipment Efficiency measured by composite/derived factors
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'OEE':
        columns = ['tStamp', 'cLayer', 'tCode', 'Desc', 'Lapsed', 'PipePos', 'nDiam', 'Ovality', 'tChange', 'uMessag']
    else:
        print('Invalid Columns or Query error...')

    return columns
