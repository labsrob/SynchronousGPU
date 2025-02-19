"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Substrate Temperature measured in Degree Celsius (°C)
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'ST':
        columns = ['R1H1ST', 'R1H2ST', 'R1H3ST', 'R1H4ST',
                   'R2H1ST', 'R2H2ST', 'R2H3ST', 'R2H4ST',
                   'R3H1ST', 'R3H2ST', 'R3H3ST', 'R3H4ST',
                   'R4H1ST', 'R4H2ST', 'R4H3ST', 'R4H4ST']
    else:
        print('Invalid Columns or Query error...')

    return columns
