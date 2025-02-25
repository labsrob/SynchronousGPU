"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Check SQL data columns ...
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'EoL1':
        columns = [ # Tape Temperature --------------[]
                    'R1H1TT', 'R1H2TT', 'R1H3TT', 'R1H4TT',
                   'R2H1TT', 'R2H2TT', 'R2H3TT', 'R2H4TT',
                   'R3H1TT', 'R3H2TT', 'R3H3TT', 'R3H4TT',
                   'R4H1TT', 'R4H2TT', 'R4H3TT', 'R4H4TT',]

    elif pParam == 'EoL2':
        columns = [
                   # Substrate Temperature -----------[]
                   'R1H1ST', 'R1H2ST', 'R1H3ST', 'R1H4ST',
                   'R2H1ST', 'R2H2ST', 'R2H3ST', 'R2H4ST',
                   'R3H1ST', 'R3H2ST', 'R3H3ST', 'R3H4ST',
                   'R4H1ST', 'R4H2ST', 'R4H3ST', 'R4H4ST']

    elif pParam == 'EoL3':
        columns = [ # TAPE PLACEMENT  -----------------[]
                   'R1H1TG', 'R1H2TG', 'R1H3TG', 'R1H4TG',
                   'R2H1TG', 'R2H2TG', 'R2H3TG', 'R2H4TG',
                   'R3H1TG', 'R3H2TG', 'R3H3TG', 'R3H4TG',
                   'R4H1TG', 'R4H2TG', 'R4H3TG', 'R4H4TG']

    elif pParam == 'EoL4':
        columns = [ # Laser Power ------------------[]
                   'R1H1RM', 'R1H2RM', 'R1H3RM', 'R1H4RM',
                   'R2H1RM', 'R2H2RM', 'R2H3RM', 'R2H4RM',
                   'R3H1RM', 'R3H2RM', 'R3H3RM', 'R3H4RM',
                   'R4H1RM', 'R4H2RM', 'R4H3RM', 'R4H4RM',]

    elif pParam == 'EoL5':
        columns = [ # Laser Angle ---------------------[]
                   'R1H1LP', 'R1H2LP', 'R1H3LP', 'R1H4LP',
                   'R2H1LP', 'R2H2LP', 'R2H3LP', 'R2H4LP',
                   'R3H1LP', 'R3H2LP', 'R3H3LP', 'R3H4LP',
                   'R4H1LP', 'R4H2LP', 'R4H3LP', 'R4H4LP',]

    elif pParam == 'EoL6':
        columns = [ # Laser Angle ---------------------[]
                   'R1H1LA', 'R1H2LA', 'R1H3LA', 'R1H4LA',
                   'R2H1LA', 'R2H2LA', 'R2H3LA', 'R2H4LA',
                   'R3H1LA', 'R3H2LA', 'R3H3LA', 'R3H4LA',
                   'R4H1LA', 'R4H2LA', 'R4H3LA', 'R4H4LA',]

    elif pParam == 'EoL7':
        columns = [ # TAPE PLACEMENT  ------------------[]
                   'R1H1TP', 'R1H2TP', 'R1H3TP', 'R1H4TP',
                   'R2H1TP', 'R2H2TP', 'R2H3TP', 'R2H4TP',
                   'R3H1TP', 'R3H2TP', 'R3H3TP', 'R3H4TP',
                   'R4H1TP', 'R4H2TP', 'R4H3TP', 'R4H4TP']

    elif pParam == 'EoL8':
        columns = [ # Roller Force --------------------[]
                   'R1H1RF', 'R1H2RF', 'R1H3RF', 'R1H4RF',
                   'R2H1RF', 'R2H2RF', 'R2H3RF', 'R2H4RF',
                   'R3H1RF', 'R3H2RF', 'R3H3RF', 'R3H4RF',
                   'R4H1RF', 'R4H2RF', 'R4H3RF', 'R4H4RF']

    else:
        print('Invalid Columns or Query error...')

    return columns
