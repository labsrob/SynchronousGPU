"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Tape Placement Error - Keyance
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'TP':
        columns = ['cLayer', 'R1H1TP', 'R1H2TP', 'R1H3TP', 'R1H4TP',
                   'R2H1TP', 'R2H2TP', 'R2H3TP', 'R2H4TP',
                   'R3H1TP', 'R3H2TP', 'R3H3TP', 'R3H4TP',
                   'R4H1TP', 'R4H2TP', ' R4H3TP', 'R4H4TP']
    else:
        print('Invalid Columns or Query error...')

    return columns
