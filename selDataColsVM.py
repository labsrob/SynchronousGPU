"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
2-D Void Mapping Data SQL Tabel
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'VM':
        columns = ['sCount', 'sCenter', 'AvgGap',
                   'MaxGap', 'cLayer', 'sLength']
    else:
        print('Invalid Columns or Query error...')

    return columns
