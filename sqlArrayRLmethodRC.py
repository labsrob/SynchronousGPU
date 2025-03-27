# This script is called in from Main program to load SQL execution syntax command and return a list in LisDat
# Author: Dr Labs, RB
from collections import deque
from itertools import count
from datetime import datetime, timedelta
import time
import timeit
import os

# ================================ RAMP COUNT DATA =======================================#

UseRowIndex = True
idx = count()
now = datetime.now()

dataList0 = []
Idx, dL = [], []
st_id = 0                                           # SQL start index unless otherwise stated by the index tracker!


def sqlexec(daq, sqTable):
    """
    NOTE:
    """

    # ------------------------------------------------------------------------------------[]
    data1 = daq.execute('SELECT * FROM ' + sqTable).fetchall()
    # data1 = daq.execute('SELECT * FROM ' + sqTable + ' WHERE cLayer=' + cLayr).fetchmany(n2fetch)
    if len(data1) != 0:
        for result in data1:
            result = list(result)
            if UseRowIndex:
                dataList0.append(next(idx))
            else:
                now = time.strftime("%H:%M:%S")
                dataList0.append(time.strftime(now))
            dL.append(result)
        # print("Step List1:", len(dL1), dL1)

    else:
        print('Process EOF reached...')
        print('SPC Halting for 5 Minutes...')
        time.sleep(5)
    daq.close()

    return dL
# -----------------------------------------------------------------------------------[Dr Labs]
