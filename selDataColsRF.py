"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Roller Force measured in Newton (N)
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'RF':
        columns = ['cLayer', 'R1H1RF', 'R1H2RF', 'R1H3RF', 'R1H4RF',
                   'R2H1RF', 'R2H2RF', 'R2H3RF', 'R2H4RF',
                   'R3H1RF', 'R3H2RF', 'R3H3RF', 'R3H4RF',
                   'R4H1RF', 'R4H2RF', ' R4H3RF','R4H4RF']
    else:
        print('Invalid Columns or Query error...')

    return columns
