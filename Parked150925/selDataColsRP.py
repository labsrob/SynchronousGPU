"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Roller Pressure measured in Pascal (Pa)
"""

def validCols(pParam, pWON=None):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'RP1_'+ pWON:
        columns = ['tStamp', 'cLayer', 'R1H1RP', 'R1H2RP', 'R1H3RP',
                   'R1H4RP', 'R2H1RP', 'R2H2RP', 'R2H3RP', 'R2H4RP']

    elif pParam == 'RP2_'+ pWON:
        columns = ['tStamp', 'cLayer','R3H1RP', 'R3H2RP', 'R3H3RP',
                   'R3H4RP', 'R4H1RP', 'R4H2RP', ' R4H3RP', 'R4H4RP']

    elif pParam == 'SPC_RP':
        columns = ['cLayer', 'R1H1', 'R1H2', 'R1H3', 'R1H4',
                   'R2H1', 'R2H2', 'R2H3', 'R2H4', 'R3H1', 'R3H2',
                   'R3H3', 'R3H4', 'R4H1', 'R4H2',' R4H3', 'R4H4']

    else:
        print('Invalid Columns or Query error...')

    return columns
