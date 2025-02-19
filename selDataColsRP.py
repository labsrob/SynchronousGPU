"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Roller Pressure measured in Pascal (Pa)
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'RP':
        columns = ['R1H1RP', 'R1H2RP', 'R1H3RP', 'R1H4RP',
                   'R2H1RP', 'R2H2RP', 'R2H3RP', 'R2H4RP',
                   'R3H1RP', 'R3H2RP', 'R3H3RP', 'R3H4RP',
                   'R4H1RP', 'R4H2RP',' R4H3RP', 'R4H4RP']
    else:
        print('Invalid Columns or Query error...')

    return columns
