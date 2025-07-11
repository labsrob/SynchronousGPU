"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Substrate Temperature measured in Degree Celsius (°C)
"""


def validCols(pParam, pWON=None):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'ST1_' + pWON:
        columns = ['tStamp', 'cLayer', 'R1H1TT', 'R1H2TT', 'R1H3TT',
                   'R1H4TT', 'R2H1TT', 'R2H2TT', 'R2H3TT', 'R2H4TT']

    elif pParam == 'ST2_' + pWON:
        columns = ['tStamp', 'cLayer', 'R3H1TT', 'R3H2TT', 'R3H3TT',
                   'R3H4TT', 'R4H1TT', 'R4H2TT', ' R4H3TT', 'R4H4TT']

    elif pParam == 'SPC_ST':
        columns = ['cLayer', 'R1H1', 'R1H2', 'R1H3', 'R1H4',
                   'R2H1', 'R2H2', 'R2H3', 'R2H4', 'R3H1', 'R3H2',
                   'R3H3', 'R3H4', 'R4H1', 'R4H2',' R4H3', 'R4H4']
    else:
        print('Invalid Columns or Query error...')

    return columns