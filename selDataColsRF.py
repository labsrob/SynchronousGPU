"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'RF':
        columns = ['R1H1RollerForce(N)', 'R1H2RollerForce(N)', 'R1H3RollerForce(N)', 'R1H4RollerForce(N)',
                   'R2H1RollerForce(N)', 'R21H2RollerForce(N)', 'R2H3RollerForce(N)', 'R2H4RollerForce(N)',
                   'R3H1RollerForce(N)', 'R3H2RollerForce(N)', 'R3H3RollerForce(N)', 'R3H4RollerForce(N)',
                   'R4H1RollerForce(N)', 'R4H2RollerForce(N)', 'R4H3RollerForce(N)', 'R4H4RollerForce(N)']
    else:
        print('Invalid Columns or Query error...')

    return columns
