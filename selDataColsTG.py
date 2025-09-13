"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Tape Gap Measured in millimeters (mm)
"""


def validCols(pParam, pWON=None):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'TG_' + str(pWON):
        columns = ['tStamp', 'cLayer', 'sCount', 'sCentre', 'PipePos',
                   'GaugeA1', 'GaugeA2', 'GaugeA3', 'GaugeA4',
                   'GaugeB1', 'GaugeB2', 'GaugeB3', 'GaugeB4', 'PipeDir']

    elif pParam == 'SPC_TG':
        columns = ['tLayer', 'cLayer', 'sCount', 'gCentre', 'PipePos',
                   'GaugeA1', 'GaugeA2', 'GaugeA3', 'GaugeA4',
                   'GaugeB1', 'GaugeB2', 'GaugeB3', 'GaugeB4', 'PipeDir']

    else:
        columns = 0
        print('Invalid Columns or Query error...')

    return columns
