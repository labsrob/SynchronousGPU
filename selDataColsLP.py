"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Laser Power measured in watts
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'LP':
        columns = ['R1H1LP', 'R1H2LP', 'R1H3LP', 'R1H4LP',
                   'R2H1LP', 'R2H2LP', 'R2H3LP', 'R2H4LP',
                   'R3H1LP', 'R3H2LP', 'R3H3LP', 'R3H4LP',
                   'R4H1LP', 'R4H2LP',' R4H3LP', 'R4H4LP']
    else:
        print('Invalid Columns or Query error...')

    return columns
