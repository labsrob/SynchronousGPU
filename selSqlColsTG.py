"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'TG':
        columns = ['TimeStamp', 'CurrentLayer', 'SampleCount', 'SampleCentre', 'PipePosition', 'GapGaugeA1(mm)',
                   'GapGaugeA2(mm)', 'GapGaugeA3(mm)', 'GapGaugeA4(mm)', 'GapGaugeB1(mm)', 'GapGaugeB2(mm)',
                   'GapGaugeB3(mm)', 'GapGaugeB4(mm)', 'PipeDirection']
    else:
        print('Invalid Columns or Query error...')

    return columns
