"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Check SQL data columns ...
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'WA':
        columns = [ # Tape Temperature --------------[]
                   'tStme', 'LyIDe', 'R1SPe', 'R1NVe', 'R2SPe',
                   'R2NVe', 'R3SPe', 'R3NVe', 'R4SPe',  'R4NVe']


    else:
        print('Invalid Columns or Query error...')

    return columns
