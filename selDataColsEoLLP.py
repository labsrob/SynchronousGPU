"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Check SQL data columns ...
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'LP':
        columns = [ # Tape Temperature --------------[]
                   'tStmf', 'LyIDf', 'R1SPf', 'R1NVf', 'R2SPf',
                   'R2NVf', 'R3SPf', 'R3NVf', 'R4SPf',  'R4NVf']


    else:
        print('Invalid Columns or Query error...')

    return columns
