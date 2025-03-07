"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Cell Tension measured in Newton per metre (N/m)
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH) 1 Mpa = 1 (N/mm2)
    if pParam == 'CT':
        columns = ['tStamp', 'cTensA', 'cTensB', 'PipeDi']
    else:
        print('Invalid Columns or Query error...')

    return columns
