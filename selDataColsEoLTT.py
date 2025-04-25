"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Check SQL data columns ...
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'TT':
        columns = [ # Tape Temperature --------------[]
                   'tStmp', 'LyIDa', 'R1SPa', 'R1NVa', 'R2SPa',
                   'R2NVa', 'R3SPa', 'R3NVa', 'R4SPa',  'R4NVa']


    else:
        print('Invalid Columns or Query error...')

    return columns
