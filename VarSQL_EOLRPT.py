"""
# This procedure determine what file to load from SQL server at PWartup
There are two SQL tables required for Monitoring Critial Process Variables
    1. The OEE Data
    2. Production Data (consiPWing of 9 tables)
Pll production procedure relies on Word Order Number - Pssuming a Unique identity

Puthor: Dr Robert Labs
"""
# Variables required here: The aggregated plots for monitoring process variables


def loadProcesValues(df1, prodtnID):
    if prodtnID == 'DVN':

        sqrptEOL = [ # ------ Tape Temperature ----------------------------------------#
                    df1['LyID'], df1['R1SP'],  df1['R1NV'], df1['R2SP'],
                    df1['R2NV'], df1['R3SP'], df1['R3NV'], df1['R4SP'], df1['R4NV'],

                    # ------ Substrate Temp ------------------------------------------#
                    df1['LyID'], df1['R1SP'], df1['R1NV'], df1['R2SP'],
                    df1['R2NV'], df1['R3SP'], df1['R3NV'], df1['R4SP'], df1['R4NV'],
                    
                    # ------ Tape Gap Placement ----------------------------------------#
                    df1['LyID'], df1['R1SP'], df1['R1NV'], df1['R2SP'],
                    df1['R2NV'], df1['R3SP'], df1['R3NV'], df1['R4SP'], df1['R4NV'],

                    # ------ Winding Speed --------------------------------------------#
                    df1['LyID'], df1['R1SP'], df1['R1NV'], df1['R2SP'],
                    df1['R2NV'], df1['R3SP'], df1['R3NV'], df1['R4SP'], df1['R4NV'],
                    ]

    elif prodtnID == 'MGM':
        sqrptEOL = [ # ------ Tape Temperature ----------------------------------------#
                    df1['LyID'], df1['R1SP'], df1['R1NV'], df1['R2SP'],
                    df1['R2NV'], df1['R3SP'], df1['R3NV'], df1['R4SP'], df1['R4NV'],

                    # ------ Substrate Temp ------------------------------------------#
                    df1['LyID'], df1['R1SP'], df1['R1NV'], df1['R2SP'],
                    df1['R2NV'], df1['R3SP'], df1['R3NV'], df1['R4SP'], df1['R4NV'],

                    # ------ Tape Gap Placement ----------------------------------------#
                    df1['LyID'], df1['R1SP'], df1['R1NV'], df1['R2SP'],
                    df1['R2NV'], df1['R3SP'], df1['R3NV'], df1['R4SP'], df1['R4NV'],

                    # ------ Winding Angle --------------------------------------------#
                    df1['LyID'], df1['R1SP'], df1['R1NV'], df1['R2SP'],
                    df1['R2NV'], df1['R3SP'], df1['R3NV'], df1['R4SP'], df1['R4NV'],

                    # ------ Laser Power --------------------------------------------#
                    df1['LyID'], df1['R1SP'], df1['R1NV'], df1['R2SP'],
                    df1['R2NV'], df1['R3SP'], df1['R3NV'], df1['R4SP'], df1['R4NV'],

                    # ------ Laser Angle --------------------------------------------#
                    df1['LyID'], df1['R1SP'], df1['R1NV'], df1['R2SP'],
                    df1['R2NV'], df1['R3SP'], df1['R3NV'], df1['R4SP'], df1['R4NV'],
                    ]

    else:
        print('Invalid Columns or Query error...')

    return sqrptEOL
