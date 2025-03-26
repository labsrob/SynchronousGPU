"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Check SQL data columns ...
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'EOLTT':
        columns = [ # Tape Temperature --------------[]
                   'tStamp', 'LyID', 'R1SP', 'R1NV', 'R2SP',
                   'R2NV', 'R3SP', 'R3NV', 'R4SP',  'R4NV']


    else:
        print('Invalid Columns or Query error...')

    return columns
