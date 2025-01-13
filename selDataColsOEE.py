"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Overall Equipment Efficiency measured by composite/derived factors
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'OEE':
        columns = ['TimeLine', 'CurrentLayer', 'TransitionCode', 'Description', 'Duration(Sec)', 'PipePosition',
                   'PipeDiameter', 'UserMessage']
    else:
        print('Invalid Columns or Query error...')

    return columns
