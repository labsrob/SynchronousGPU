"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'CT':
        columns = ['CellTension A', 'CellTension B', 'PipeDirection']
    else:
        print('Invalid Columns or Query error...')

    return columns
