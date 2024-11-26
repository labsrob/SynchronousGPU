"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'OEE':
        columns = ['TimeLine', 'R1H1RP(°C)', 'R1H2RP(°C)', 'R1H3RP(°C)', 'R1H4RP(°C)', 'R2H1RP(°C)', 'R2H2RP(°C)',
                   'R2H3RP(°C)', 'R2H4RP(°C)', 'R3H1RP(°C)', 'R3H2RP(°C)', 'R3H3RP(°C)', 'R3H4RP(°C)', 'R4H1RP(°C)',
                   'R4H2RP(°C)',' R4H3RP(°C)', 'R4H4RP(°C)']
    else:
        print('Invalid Columns or Query error...')

    return columns
