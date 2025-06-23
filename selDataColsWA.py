"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Tape Winding Angle measured in Degres
"""


def validCols(pParam, pWON=None):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'WA' + pWON:
        columns = ['cLayer', 'R1H1WA', 'R1H2WA', 'R1H3WA', 'R1H4WA',
                   'R2H1WA', 'R2H2WA', 'R2H3WA', 'R2H4WA',
                   'R3H1WA', 'R3H2WA', 'R3H3WA', 'R3H4WA',
                   'R4H1WA', 'R4H2WA',' R4H3WA', 'R4H4WA']

    elif pParam == 'SPC_WA':
        columns = ['cLayer', 'R1H1', 'R1H2', 'R1H3', 'R1H4',
                   'R2H1', 'R2H2', 'R2H3', 'R2H4',
                   'R3H1', 'R3H2', 'R3H3', 'R3H4',
                   'R4H1', 'R4H2',' R4H3', 'R4H4']
    else:
        print('Invalid Columns or Query error...')

    return columns
