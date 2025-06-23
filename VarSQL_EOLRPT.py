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
                    df1['tStmp'], df1['LyIDa'], df1['R1SPa'],  df1['R1NVa'], df1['R2SPa'],
                    df1['R2NVa'], df1['R3SPa'], df1['R3NVa'], df1['R4SPa'], df1['R4NVa'],

                    # ------ Substrate Temp ------------------------------------------#
                    df1['tStmb'], df1['LyIDb'], df1['R1SPb'], df1['R1NVb'], df1['R2SPb'],
                    df1['R2NVb'], df1['R3SPb'], df1['R3NVb'], df1['R4SPb'], df1['R4NVb'],
                    
                    # ------ Tape Gap Placement ----------------------------------------#
                    df1['tStmc'], df1['LyIDc'], df1['R1SPc'], df1['R1NVc'], df1['R2SPc'],
                    df1['R2NVc'], df1['R3SPc'], df1['R3NVc'], df1['R4SPc'], df1['R4NVc'],

                    # ------ Winding Speed --------------------------------------------#
                    df1['tStmd'], df1['LyIDd'], df1['R1SPd'], df1['R1NVd'], df1['R2SPd'],
                    df1['R2NVd'], df1['R3SPd'], df1['R3NVd'], df1['R4SPd'], df1['R4NVd'],
                    ]

    elif prodtnID == 'MGM':
        sqrptEOL = [ # ------ Tape Temperature ----------------------------------------#
                    df1['tStmp'], df1['LyIDa'], df1['R1SPa'], df1['R1NVa'], df1['R2SPa'],
                    df1['R2NVa'], df1['R3SPa'], df1['R3NVa'], df1['R4SPa'], df1['R4NVa'],

                    # ------ Substrate Temp ------------------------------------------#
                    df1['tStmb'], df1['LyIDb'], df1['R1SPb'], df1['R1NVb'], df1['R2SPb'],
                    df1['R2NVb'], df1['R3SPb'], df1['R3NVb'], df1['R4SPb'], df1['R4NVb'],

                    # ------ Tape Gap Placement ---------------------------------------#
                    df1['tStmc'], df1['LyIDc'], df1['R1SPc'], df1['R1NVc'], df1['R2SPc'],
                    df1['R2NVc'], df1['R3SPc'], df1['R3NVc'], df1['R4SPc'], df1['R4NVc'],

                    # ------ Winding Angle --------------------------------------------#
                    df1['tStme'], df1['LyIDe'], df1['R1SPe'], df1['R1NVe'], df1['R2SPe'],
                    df1['R2NVe'], df1['R3SPe'], df1['R3NVe'], df1['R4SPe'], df1['R4NVe'],

                    # ------ Laser Power --------------------------------------------#
                    df1['tStmf'], df1['LyIDf'], df1['R1SPf'], df1['R1NVf'], df1['R2SPf'],
                    df1['R2NVf'], df1['R3SPf'], df1['R3NVf'], df1['R4SPf'], df1['R4NVf'],

                    # ------ Laser Angle --------------------------------------------#
                    df1['tStmg'], df1['LyIDg'], df1['R1SPg'], df1['R1NVg'], df1['R2SPg'],
                    df1['R2NVg'], df1['R3SPg'], df1['R3NVg'], df1['R4SPg'], df1['R4NVg'],
                    ]

    else:
        print('Invalid Columns or Query error...')

    return sqrptEOL
