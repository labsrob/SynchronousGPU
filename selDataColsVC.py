"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
YTape Void count data
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'VC':
        columns = ['sCentre', 'V1Count', 'V2Count', 'V3Count', 'V4Count', 'PipeDir', 'cLayer']
    else:
        print('Invalid Columns or Query error...')

    return columns
