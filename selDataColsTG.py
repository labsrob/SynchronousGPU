"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Tape Gap Measured in millimeters (mm)
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'TG':
        columns = ['TimeStamp', 'cLayer', 'sCount', 'sCentre', 'PipePos', 'GaugeA1',
                   'GaugeA2', 'GaugeA3', 'GaugeA4', 'GaugeB1', 'GaugeB2',
                   'GaugeB3', 'GaugeB4', 'PipeDir']
    else:
        print('Invalid Columns or Query error...')

    return columns
