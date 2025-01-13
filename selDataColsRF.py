"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Roller Force measured in Newton (N)
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'RF':
        columns = ['TimeLine', 'R1H1RF(N)', 'R1H2RP(N)', 'R1H3RP(N)', 'R1H4RP(N)', 'R2H1RP(N)', 'R2H2RP(N)',
                   'R2H3RP(N)', 'R2H4RP(N)', 'R3H1RP(N)', 'R3H2RP(N)', 'R3H3RP(N)', 'R3H4RP(N)', 'R4H1RP(N)',
                   'R4H2RP(N)', ' R4H3RP(N)', 'R4H4RP(N)']
    else:
        print('Invalid Columns or Query error...')

    return columns
