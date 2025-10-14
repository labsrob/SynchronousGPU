"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
2-D Void Mapping Data SQL Tabel
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam[0:3] == 'VM_':
        columns = ['id_col', 'sCount', 'sCenter', 'AvgGap',
                   'MaxGap', 'cLayer', 'sDistance']

    elif pParam[0:6] == 'SPC_VM':
        columns = ['sCount', 'sCentre', 'AvgGap', 'MaxGap', 'cLayer', 'sDistance']

    else:
        columns = 0
        print('Invalid Columns or Query error...')

    return columns
