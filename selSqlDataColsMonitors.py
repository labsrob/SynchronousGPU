"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
Substrate Temperature measured in Degree Celsius (°C)
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'DNV':
        columns = ['R1H1RF', 'R1H2RF', 'R1H3RF', 'R1H4RF',
                   'R2H1RF', 'R2H2RF', 'R2H3RF', 'R2H4RF',
                   'R3H1RF', 'R3H2RF', 'R3H3RF', 'R3H4RF',
                   'R4H1RF', 'R4H2RF', 'R4H3RF', 'R4H4RF',
                   # Laser Angle -----------[]
                   'R1H1LA', 'R1H2LA', 'R1H3LA', 'R1H4LA',
                   'R2H1LA', 'R2H2LA', 'R2H3LA', 'R2H4LA',
                   'R3H1LA', 'R3H2LA', 'R3H3LA', 'R3H4LA',
                   'R4H1LA', 'R4H2LA', 'R4H3LA', 'R4H4LA',
                   # Cell Tension -----------[]
                   'tStamp', 'cTensA','cTensB', 'PipeDi',
                   'cRTemp', 'cHumid', 'fDTemp', 'fHumid',
                   'locTemp', 'locHumid', 'UVIndex',
                   # Oven Temperature -----------[]
                   'tStamp', 'oTempA', 'oTempB']

    elif pParam == 'MGM':
        columns = ['R1H1RF', 'R1H2RF', 'R1H3RF', 'R1H4RF',
                   'R2H1RF', 'R2H2RF', 'R2H3RF', 'R2H4RF',
                   'R3H1RF', 'R3H2RF', 'R3H3RF', 'R3H4RF',
                   'R4H1RF', 'R4H2RF', 'R4H3RF', 'R4H4RF',
                   # Laser Angle -----------[]
                   'R1H1LA', 'R1H2LA', 'R1H3LA', 'R1H4LA',
                   'R2H1LA', 'R2H2LA', 'R2H3LA', 'R2H4LA',
                   'R3H1LA', 'R3H2LA', 'R3H3LA', 'R3H4LA',
                   'R4H1LA', 'R4H2LA', 'R4H3LA', 'R4H4LA',
                   # Oven Temperature -----------[]
                   'tStamp', 'oTempA', 'oTempB',
                   # Cell Tension -----------[]
                   'tStamp', 'cTensA', 'cTensB', 'PipeDi',
                   'cRTemp', 'cHumid', 'fDTemp', 'fHumid',
                   'locTemp', 'locHumid', 'UVIndex',
                   # Placement Error -----------[]
                   'R1H1PE', 'R1H2PE', 'R1H3PE', 'R1H4PE',
                   'R2H1PE', 'R2H2PE', 'R2H3PE', 'R2H4PE',
                   'R3H1PE', 'R3H2PE', 'R3H3PE', 'R3H4PE',
                   'R4H1PE', 'R4H2PE', 'R4H3PE', 'R4H4PE',
                   # Tape Speed -----------[62]
                   'R1H1TS', 'R1H2TS', 'R1H3TS', 'R1H4TS',
                   'R2H1TS', 'R2H2TS', 'R2H3TS', 'R2H4TS',
                   'R3H1TS', 'R3H2TS', 'R3H3TS', 'R3H4TS',
                   'R4H1TS', 'R4H2TS', 'R4H3TS', 'R4H4TS'] #77


    else:
        print('Invalid Columns or Query error...')

    return columns
