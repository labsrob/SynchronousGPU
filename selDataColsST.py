"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Substrate Temperature measured in Degree Celsius (°C)
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam[0:4] == 'ST1_':
        columns = ['id_col', 'cLayer', 'R1H1ST', 'R1H2ST', 'R1H3ST',
                   'R1H4ST', 'R2H1ST', 'R2H2ST', 'R2H3ST', 'R2H4ST']

    elif pParam[0:4] == 'ST2_':
        columns = ['id_col', 'cLayer', 'R3H1ST', 'R3H2ST', 'R3H3ST',
                   'R3H4ST', 'R4H1ST', 'R4H2ST', 'R4H3ST', 'R4H4ST']

    elif pParam[0:4] == 'SPC_ST':
        columns = ['cLayer', 'R1H1', 'R1H2', 'R1H3', 'R1H4',
                   'R2H1', 'R2H2', 'R2H3', 'R2H4', 'R3H1', 'R3H2',
                   'R3H3', 'R3H4', 'R4H1', 'R4H2','R4H3', 'R4H4']
    else:
        columns = 0
        print('Invalid Columns or Query error...')

    return columns