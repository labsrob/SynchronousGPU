"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'ST':
        columns = ['TimeLine', 'R1H1ST(°C)', 'R1H2ST(°C)', 'R1H3ST(°C)', 'R1H4ST(°C)', 'R2H1ST(°C)', 'R2H2ST(°C)',
                   'R2H3ST(°C)', 'R2H4ST(°C)', 'R3H1ST(°C)', 'R3H2ST(°C)', 'R3H3ST(°C)', 'R3H4ST(°C)', 'R4H1ST(°C)',
                    'R4H2ST(°C)', 'R4H3ST(°C)', 'R4H4ST(°C)']
    else:
        print('Invalid Columns or Query error...')

    return columns
