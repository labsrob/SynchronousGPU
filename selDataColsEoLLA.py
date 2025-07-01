"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Check SQL data columns ...
"""


def validCols(pParam, pWON=None):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'ZLA_' + pWON:
        columns = [ # Tape Temperature --------------[]
                   'tStmg', 'LyIDg', 'R1SPg', 'R1NVg', 'R2SPg',
                   'R2NVg', 'R3SPg', 'R3NVg', 'R4SPg',  'R4NVg']

    else:
        print('Invalid Columns or Query error...')

    return columns
