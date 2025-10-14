"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Laser Power measured in watts
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam[0:3] == 'LP1_':
        columns = ['id_col', 'cLayer', 'R1H1LP', 'R1H2LP', 'R1H3LP',
                   'R1H4LP', 'R2H1LP', 'R2H2LP', 'R2H3LP', 'R2H4LP']

    elif pParam[0:3] == 'LP2_':
        columns = ['id_col', 'cLayer', 'R3H1LP', 'R3H2LP', 'R3H3LP',
                   'R3H4LP', 'R4H1LP', 'R4H2LP',' R4H3LP', 'R4H4LP' ]

    elif pParam[0:5] == 'SPC_LP':
        columns = ['cLayer', 'R1H1', 'R1H2', 'R1H3', 'R1H4',
                   'R2H1', 'R2H2', 'R2H3', 'R2H4',
                   'R3H1', 'R3H2', 'R3H3', 'R3H4',
                   'R4H1', 'R4H2',' R4H3', 'R4H4']
    else:
        print('Invalid Columns or Query error...')

    return columns
