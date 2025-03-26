"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Tape Winding Angle measured in Degres
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'WS':
        columns = ['cLayer', 'R1H1WS', 'R1H2WS', 'R1H3WS', 'R1H4WS',
                   'R2H1WS', 'R2H2WS', 'R2H3WS', 'R2H4WS',
                   'R3H1WS', 'R3H2WS', 'R3H3WS', 'R3H4WS',
                   'R4H1WS', 'R4H2WS',' R4H3WS', 'R4H4WS']
    else:
        print('Invalid Columns or Query error...')

    return columns
