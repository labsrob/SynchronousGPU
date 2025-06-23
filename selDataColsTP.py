"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Tape Placement Error - Keyance
"""

def validCols(pParam, pWON=None):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'TP1_' + pWON:
        columns = ['tStamp', 'cLayer', 'R1H1TP', 'R1H2TP', 'R1H3TP',
                   'R1H4TP', 'R2H1TP', 'R2H2TP', 'R2H3TP', 'R2H4TP']

    elif pParam == 'TP2_' + pWON:
        columns = ['tStamp', 'cLayer', 'R3H1TP', 'R3H2TP', 'R3H3TP',
                   'R3H4TP', 'R4H1TP', 'R4H2TP',' R4H3TP', 'R4H4TP' ]

    elif pParam == 'SPC_TP':
        columns = ['cLayer', 'R1H1', 'R1H2', 'R1H3', 'R1H4',
                   'R2H1', 'R2H2', 'R2H3', 'R2H4',
                   'R3H1', 'R3H2', 'R3H3', 'R3H4',
                   'R4H1', 'R4H2',' R4H3', 'R4H4']
    else:
        print('Invalid Columns or Query error...')

    return columns