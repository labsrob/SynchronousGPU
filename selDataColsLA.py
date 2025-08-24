"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Laser Angle measured in Degrees - This function is common to PLC data and SQL data
"""


def validCols(pParam, pWON=None):

    # print('Detected RingHead Combo:', configH)
    if pParam == 'LA1_' + pWON:
        columns = ['tStamp', 'cLayer', 'R1H1LA', 'R1H2LA', 'R1H3LA',
                   'R1H4LA', 'R2H1LA', 'R2H2LA', 'R2H3LA', 'R2H4LA']

    elif pParam == 'LA2_' + pWON:
        columns = ['tStamp', 'cLayer', 'R3H1LA', 'R3H2LA', 'R3H3LA',
                   'R3H4LA', 'R4H1LA', 'R4H2LA',' R4H3LA', 'R4H4LA' ]

    elif pParam == 'SPC_LA':
        columns = ['cLayer', 'R1H1', 'R1H2', 'R1H3', 'R1H4',
                   'R2H1', 'R2H2', 'R2H3', 'R2H4',
                   'R3H1', 'R3H2', 'R3H3', 'R3H4',
                   'R4H1', 'R4H2',' R4H3', 'R4H4']
    else:
        print('Invalid Columns or Query error...')

    return columns
