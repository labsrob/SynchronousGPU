"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Check SQL data columns ...
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'RP':
        columns = [ # Tape Temperature --------------[]
                   'tStmb', 'LyIDb', 'R1SPb', 'R1NVb', 'R2SPb',
                   'R2NVb', 'R3SPb', 'R3NVb', 'R4SPb',  'R4NVb']

    else:
        print('Invalid Columns or Query error...')

    return columns
