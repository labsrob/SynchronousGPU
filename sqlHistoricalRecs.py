"""
# This procedure determine what file to load from SQL server at startup
There are two SQL tables required for Control Chart
    1. The OEE Data
    2. Production Data (consisting of 9 tables)
All production procedure relies on Word Order Number - Assuming a Unique identity

Author: Dr Robert Labs
"""
import time
from time import gmtime, strftime #, strptime
from datetime import datetime #, timedelta


def seek_OEE_data():
    # Time - Load local Time
    now = datetime.now()

    string = str.maketrans(" ", '-')                    # format date into ISO 8610
    cDate = strftime("%Y%m%d").translate(string)        # Obtain local date
    print('Current Date:', cDate)

    # Obtain OEE record in real-time ----------------------------
    mfilename = ('OEE_' + cDate)
    print('ActiveOEE Table', mfilename)
    return mfilename


def get_encodedFiles(StaSearchD=None):

    now = datetime.now()
    string = str.maketrans(" ", '-')                    # format date into ISO 8610
    retroOEE = StaSearchD.replace('-', '')              # remove all hypernation

    if StaSearchD == None:
        cDate = strftime("%Y%m%d").translate(string)    # Obtain local date
    else:
        cDate = strftime(retroOEE).translate(string)    # Obtain local date

    vDate = strftime("%m%d").translate(string)          # Obtain local date
    # print('Current Date:', cDate)
    print('\nToday\'s Date:', strftime("%a, %d %b %Y", gmtime()))
    # Obtain OEE record in real-time ----------------------------
    mOEE = ('OEE_' + cDate)
    print('Searching for the Specific OEE Data:', mOEE)

    return mOEE

