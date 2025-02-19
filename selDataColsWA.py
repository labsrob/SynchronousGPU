"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Tape Winding Angle measured in Degres
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'WA':
        columns = ['R1H1WA', 'R1H2WA', 'R1H3WA', 'R1H4WA',
                   'R2H1WA', 'R2H2WA', 'R2H3WA', 'R2H4WA',
                   'R3H1WA', 'R3H2WA', 'R3H3WA', 'R3H4WA',
                   'R4H1WA', 'R4H2WA',' R4H3WA', 'R4H4WA']
    else:
        print('Invalid Columns or Query error...')

    return columns
