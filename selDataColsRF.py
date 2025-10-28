"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Roller Force measured in Newton (N)
"""

def validCols(pParam, pWON=None):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'RF1_'+ pWON:
        columns = ['id_col', 'cLayer', 'R1H1RF', 'R1H2RF', 'R1H3RF', 'R1H4RF',
                   'R2H1RF', 'R2H2RF', 'R2H3RF', 'R2H4RF']

    elif pParam == 'RF2_' + pWON:
        columns = ['id_col', 'cLayer', 'R3H1RF', 'R3H2RF', 'R3H3RF', 'R3H4RF',
                   'R4H1RF', 'R4H2RF', ' R4H3RF','R4H4RF']

    elif pParam == 'SPC_RF':
        columns = ['cLayer', 'R1H1', 'R1H2', 'R1H3', 'R1H4',
                   'R2H1', 'R2H2', 'R2H3', 'R2H4', 'R3H1', 'R3H2',
                   'R3H3', 'R3H4', 'R4H1', 'R4H2',' R4H3', 'R4H4']

    else:
        print('Invalid Columns or Query error...')

    return columns
