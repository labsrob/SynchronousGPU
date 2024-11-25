# This script is called in from Main program to load SQL execution syntax command and return a list in LisDat
# Author: Dr Labs, RB

from itertools import count
from datetime import datetime, timedelta
import time

UseRowIndex = True
idx = count()
now = datetime.now()

dataList0 = []
dL = []
Idx1 = []


def sqlexec(nGZ, grp_step, daq,  rT, idx,  fetch_no):

    data1 = daq.execute('SELECT TOP ' + fetch_no + ' * FROM ' + rT).fetchall()
    for result in data1:
        result = list(result)
        if UseRowIndex:
            dataList0.append(next(idx))
        else:
            now = time.strftime("%H:%M:%S")
            dataList0.append(time.strftime(now))
        dL.append(result)

    if grp_step > 1:
        print('\nSAMPLE SIZE SLIDE')
        print('=================')
    else:
        print('\nSINGLE STEP SLIDE')
        print('=================')
    print("Data Array1:", len(dL), dL)
    idx = 0

    return idx, dL         # returning lists' results

