"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH) 1 Mpa = 1 (N/mm2)
    if pParam == 'CT':
        columns = ['CellTensionA (Mpa)', 'CellTensionB (Mpa)', 'PipeDirection']
    else:
        print('Invalid Columns or Query error...')

    return columns
