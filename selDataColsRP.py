"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Pressure measured in Pascal (Pa)
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'RP':
        columns = ['TimeLine', 'R1H1RP(kPa)', 'R1H2RP(kPa)', 'R1H3RP(kPa)', 'R1H4RP(kPa)', 'R2H1RP(°C)', 'R2H2RP(°C)',
                   'R2H3RP(kPa)', 'R2H4RP(kPa)', 'R3H1RP(kPa)', 'R3H2RP(kPa)', 'R3H3RP(kPa)', 'R3H4RP(kPa)', 'R4H1RP(kPa)',
                   'R4H2RP(kPa)',' R4H3RP(kPa)', 'R4H4RP(kPa)']
    else:
        print('Invalid Columns or Query error...')

    return columns
