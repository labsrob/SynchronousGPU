"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Laser Angle measured in Degres
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'LA':
        columns = ['R1H1LA', 'R1H2LA', 'R1H3LA', 'R1H4LA',
                   'R2H1LA', 'R2H2LA', 'R2H3LA', 'R2H4LA',
                   'R3H1LA', 'R3H2LA', 'R3H3LA', 'R3H4LA',
                   'R4H1LA', 'R4H2LA',' R4H3LA', 'R4H4LA']
    else:
        print('Invalid Columns or Query error...')

    return columns
