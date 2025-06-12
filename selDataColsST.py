"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Substrate Temperature measured in Degree Celsius (°C)
"""


def validCols(pParam, WON):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'ST1_' + WON[0]:
        columns = ['tStamp', 'cLayer', 'R1H1TT', 'R1H2TT', 'R1H3TT',
                   'R1H4TT', 'R2H1TT', 'R2H2TT', 'R2H3TT', 'R2H4TT']

    elif pParam == 'ST2_' + WON[0]:
        columns = ['tStamp', 'cLayer', 'R3H1TT', 'R3H2TT', 'R3H3TT',
                   'R3H4TT', 'R4H1TT', 'R4H2TT', ' R4H3TT', 'R4H4TT']

    else:
        print('Invalid Columns or Query error...')

    return columns