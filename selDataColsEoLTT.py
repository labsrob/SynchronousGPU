"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Check SQL data columns ...
"""


def validCols(pParam, pWON=None):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'ZTT_' + str(pWON):
        columns = [ # Tape Temperature --------------[]
                   'LyIDa', 'R1SPa', 'R1NVa', 'R2SPa',
                   'R2NVa', 'R3SPa', 'R3NVa', 'R4SPa',  'R4NVa']

    else:
        columns = 0
        print('Invalid Columns or Query error...')

    return columns
