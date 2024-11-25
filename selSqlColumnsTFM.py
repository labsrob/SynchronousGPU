"""
Title: Statistical Process Control Pipeline (CUSUM Method) **********
Select Columns

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
"""


def validCols(pParam):
    # print('Detected RingHead Combo:', configH)
    if pParam == 'LP':
        columns = ['DX1A', 'R1H1LaserPower(W)', 'R1H2aserPower(W)', 'R1H3LaserPower(W)', 'R1H4LaserPower(W)',
                   'R2H1LaserPower(W)', 'R2H2LaserPower(W)', 'R2H3LaserPower(W)', 'R2H4LaserPower(W)',
                   'R3H1LaserPower(W)', 'R3H2LaserPower(W)', 'R3H3LaserPower(W)', 'R3H4LaserPower(W)',
                   'R4H1LaserPower(W)', 'R4H2LaserPower(W)', 'R4H3LaserPower(W)', 'R4H4LaserPower(W)']
    else:
        pass

    if pParam == 'LA':
        columns = ['DX1B', 'R1H1LaserAngle(Rad)', 'R1H2LaserAngle(Rad)', 'R1H3LaserAngle(Rad)', 'R1H4LaserAngle(Rad)',
                   'R1H1LaserAngle(Rad)', 'R1H2LaserAngle(Rad)', 'R1H3LaserAngle(Rad)', 'R1H4LaserAngle(Rad)',
                   'R1H1LaserAngle(Rad)', 'R1H2LaserAngle(Rad)', 'R1H3LaserAngle(Rad)', 'R1H4LaserAngle(Rad)',
                   'R1H1LaserAngle(Rad)', 'R1H2LaserAngle(Rad)', 'R1H3LaserAngle(Rad)', 'R1H4LaserAngle(Rad)']
    else:
        pass

    if pParam == 'HT':
        columns = ['DX2A', 'MHaulTension(N)', 'SHaulTension(N)']
    else:
        pass

    if pParam == 'DL':
        columns = ['DX2B', 'SouthDL(Kg)', 'North(Kg)']
    else:
        pass

    if pParam == 'RF':
        columns = ['DX3A', 'R1H1RollerForce(N)', 'R1H2RollerForce(N)', 'R1H3RollerForce(N)', 'R1H4RollerForce(N)',
                   'R2H1RollerForce(N)', 'R21H2RollerForce(N)', 'R2H3RollerForce(N)', 'R2H4RollerForce(N)',
                   'R3H1RollerForce(N)', 'R3H2RollerForce(N)', 'R3H3RollerForce(N)', 'R3H4RollerForce(N)',
                   'R4H1RollerForce(N)', 'R4H2RollerForce(N)', 'R4H3RollerForce(N)', 'R4H4RollerForce(N)']
    else:
        pass

    if pParam == 'TT':
        columns = ['DX3B', 'R1H1TapeTemperature(°C)', 'R1H2TapeTemperature(°C)', 'R1H3TapeTemperature(°C)', 'R1H4SubstrateTemp(°C)',
                   'R2H1TapeTemperature(°C)', 'R2H2TapeTemperature(°C)', 'R2H3TapeTemperature(°C)', 'R2H4SubstrateTemp(°C)',
                   'R3H1TapeTemperature(°C)', 'R3H2TapeTemperature(°C)', 'R3H3TapeTemperature(°C)', 'R3H4SubstrateTemp(°C)',
                   'R4H1TapeTemperature(°C)', 'R4H2TapeTemperature(°C)', 'R4H3TapeTemperature(°C)', 'R4H4SubstrateTemp(°C)',]
    else:
        pass

    if pParam == 'ST':
        columns = ['DX4A', 'R1H1SubstrateTemp(°C)', 'R1H2SubstrateTemp(°C)', 'R1H3SubstrateTemp(°C)', 'R1H4SubstrateTemp(°C)',
                   'R2H1SubstrateTemp(°C)', 'R2H2SubstrateTemp(°C)', 'R2H3SubstrateTemp(°C)', 'R2H4SubstrateTemp(°C)',
                   'R3H1SubstrateTemp(°C)', 'R3H2SubstrateTemp(°C)', 'R3H3SubstrateTemp(°C)', 'R3H4SubstrateTemp(°C)',
                   'R4H1SubstrateTemp(°C)', 'R4H2SubstrateTemp(°C)', 'R4H3SubstrateTemp(°C)', 'R4H4SubstrateTemp(°C)']
    else:
        pass

    if pParam == 'TG':
        columns = ['DX4B', 'TapeGapGaugeA1', 'TapeGapGaugeA2', 'TapeGapGaugeA3', 'TapeGapGaugeA4',
                   'TapeGapGaugeB1', 'TapeGapGaugeB2', 'TapeGapGaugeB3', 'TapeGapGaugeB4']

    else:
        print('Config combination not found!')

    return columns
