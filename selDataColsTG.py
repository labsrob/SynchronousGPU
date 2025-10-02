"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Tape Gap Measured in millimeters (mm)
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam[0:3] == 'TG_':
        columns = ['id_col', 'tStamp', 'cLayer', 'sCount', 'sCenter', 'PipePos',
                   'GaugeA1', 'GaugeA2', 'GaugeA3', 'GaugeA4',
                   'GaugeB1', 'GaugeB2', 'GaugeB3', 'GaugeB4', 'PipeDir']

    elif pParam[0:6] == 'SPC_TG':
        columns = ['tLayer', 'cLayer', 'sCount', 'gCenter', 'PipePos',
                   'GaugeA1', 'GaugeA2', 'GaugeA3', 'GaugeA4',
                   'GaugeB1', 'GaugeB2', 'GaugeB3', 'GaugeB4', 'PipeDir']

    else:
        columns = 0
        print('Invalid Columns or Query error...')

    return columns
