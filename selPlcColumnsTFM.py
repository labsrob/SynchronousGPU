"""
Title: Statistical Process Control Pipeline  **********
Select Columns
PLC Data Structure (TFM Requirements)

Author: Dr Robert B Labs (PhD), TFMC-Magma Global Ltd.
# -------------------------------------------------------------------------------------------------------- #
"""


def validColsPLCData(): # TODO --------------------------------------[ Start Here ]

    columns = ['Est Pipe Position(mt)', 'Current Pipe Layer',
               'R1H1RollerForce(N)', 'R1H2RollerForce(N)', 'R1H3RollerForce(N)', 'R1H4RollerForce(N)',
               'R2H1RollerForce(N)', 'R2H2RollerForce(N)', 'R2H3RollerForce(N)', 'R2H4RollerForce(N)',
               'R3H1RollerForce(N)', 'R3H2RollerForce(N)', 'R3H3RollerForce(N)', 'R3H4RollerForce(N)',
               'R4H1RollerForce(N)', 'R4H2RollerForce(N)', 'R4H3RollerForce(N)', 'R4H4RollerForce(N)',
               # Tape Temperature ------[]
               'R1H1TapeTemperature(°C)', 'R1H2TapeTemperature(°C)', 'R1H3TapeTemperature(°C)',
               'R1H4TapeTemperature(°C)', 'R2H1TapeTemperature(°C)', 'R2H2TapeTemperature(°C)',
               'R2H3TapeTemperature(°C)', 'R2H4TapeTemperature(°C)', 'R3H1TapeTemperature(°C)',
               'R3H2TapeTemperature(°C)', 'R3H3TapeTemperature(°C)', 'R3H4TapeTemperature(°C)',
               'R4H1TapeTemperature(°C)', 'R4H2TapeTemperature(°C)', 'R4H3TapeTemperature(°C)',
               'R4H4TapeTemperature(°C)',
               # Delta Temperature -----[]
               'R1H1DeltaTemperature(°C)', 'R1H2DeltaTemperature(°C)', 'R1H3DeltaTemperature(°C)',
               'R1H4DeltaTemperature(°C)', 'R2H1DeltaTemperature(°C)', 'R2H2DeltaTemperature(°C)',
               'R2H3DeltaTemperature(°C)', 'R2H4DeltaTemperature(°C)', 'R3H1DeltaTemperature(°C)',
               'R3H2DeltaTemperature(°C)', 'R3H3DeltaTemperature(°C)', 'R3H4DeltaTemperature(°C)',
               'R4H1DeltaTemperature(°C)', 'R4H2DeltaTemperature(°C)', 'R4H3DeltaTemperature(°C)',
               'R4H4DeltaTemperature(°C)',
               # Tape Gap Measurement --[]
               'TapeGapGaugeA1', 'TapeGapGaugeA2', 'TapeGapGaugeA3', 'TapeGapGaugeA4',
               'TapeGapGaugeB1', 'TapeGapGaugeB2', 'TapeGapGaugeB3', 'TapeGapGaugeB4',
               # Monitoring Parameters -[]
               'R1H14LaserPower(W)', 'R2H14LaserPower(W)', 'R3H14LaserPower(W)', 'R4H14LaserPower(W)',
               'R1H14LaserAngle(Rad)', 'R2H14LaserAngle(Rad)', 'R3H14LaserAngle(Rad)', 'R4H14LaserAngle(Rad)',
               'R1H14TapeSpeed(V)', 'R2H14TapeSpeed(V)', 'R3H14TapeSpeed(V)', 'R4H14TapeSpeed(V)']

    return columns