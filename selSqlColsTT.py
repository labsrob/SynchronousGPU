"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'TT':
        columns = ['TimeLine', 'R1H1TT(°C)', 'R1H2TT(°C)', 'R1H3TT(°C)', 'R1H4TT(°C)', 'R2H1TT(°C)', 'R2H2TT(°C)',
                   'R2H3TT(°C)', 'R2H4TT(°C)', 'R3H1TT(°C)', 'R3H2TT(°C)', 'R3H3TT(°C)', 'R3H4TT(°C)', 'R4H1TT(°C)',
                   'R4H2TT(°C)',' R4H3TT(°C)', 'R4H4TT(°C)']
    else:
        print('Invalid Columns or Query error...')

    return columns
