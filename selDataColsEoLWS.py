"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Check SQL data columns ...
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'WS':
        columns = [ # Tape Temperature --------------[]
                   'tStmd', 'LyIDd', 'R1SPd', 'R1NVd', 'R2SPd',
                   'R2NVd', 'R3SPd', 'R3NVd', 'R4SPd',  'R4NVd']


    else:
        print('Invalid Columns or Query error...')

    return columns
