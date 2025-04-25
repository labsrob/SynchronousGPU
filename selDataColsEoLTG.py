"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Check SQL data columns ...
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'TP':
        columns = [ # Tape Temperature --------------[]
                   'tStmc', 'LyIDc', 'R1SPc', 'R1NVc', 'R2SPc',
                   'R2NVc', 'R3SPc', 'R3NVc', 'R4SPc',  'R4NVc']


    else:
        print('Invalid Columns or Query error...')

    return columns
