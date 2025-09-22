"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
2-D Void Mapping Data SQL Tabel
"""


def validCols(pParam, pWON=None):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'VM_' +pWON:
        columns = ['id_col', 'sCount', 'sCenter', 'AvgGap',
                   'MaxGap', 'cLayer', 'sDistance']

    elif pParam == 'SPC_VM':
        columns = ['sCount', 'sCentre', 'AvgGap', 'MaxGap', 'cLayer', 'sDistance']

    else:
        print('Invalid Columns or Query error...')

    return columns
