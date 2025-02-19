"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Tape Winding Speed measured in metre per sec (m/s)
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'WS':
        columns = ['R1WS', 'R2WS', 'R3WS', 'R4WS', 'PipePos']
    else:
        print('Invalid Columns or Query error...')

    return columns
