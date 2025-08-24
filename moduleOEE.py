#
#
#
#
#
#
from datetime import datetime
from time import gmtime, strftime
import pandas as pd
import numpy as np

OTlayr, EPpos, pStatus = [], [], []


# Overall Equipment Effectiveness (OEE) Data -------------------------------------------[]
def chartOEE(Start_Day, FinishDay, dX3):

    # Define dataframe columns ---------------------------------------------------------[]
    colu = ['TimeLine', 'CurrentLayer', 'TransitionCode', 'Description', 'Duration(Sec)']
    df3 = pd.DataFrame(dX3, columns=colu)  # porte sql data into dataframe
    # --------------------------------
    # Allow the following code to run despite not on DNV condition ----------------#
    # TODO replace with process variable
    cLayer = df3['CurrentLayer']        # .tail(1)
    status = df3['Description'][1]      # .tail(1)
    curLayer = list(set(cLayer))        # shuffle list to obtain unique layer number at a time

    if len(curLayer) > 1:
        lastE = len(curLayer)
        curLayer = curLayer[lastE - 1]  # print the last index element
    # ---------------------------------
    # if VarPerHeadA or VarPerHeadB or VariProcess:
    OTlayr.append(curLayer[0])      # Post values into static array
    EPpos.append('N/A')             # Insert pipe position is available
    pStatus.append(status)
    print('\nTP05[Layer/Status]:', curLayer[0], status)
    # ----------------------------------------------------------------------------#

    # DNVspecify and VariProcess or not DNVspecify and VarPerHeadA or VarPerHeadB:
    print('\nTesting loop...')
    # Obtain current local time string ------------------------[]
    cTime = strftime("%H:%M:%S")

    # Convert current time string to datetime object ----------[]
    currentTime = str(datetime.strptime(cTime, "%H:%M:%S").time())
    print('\nCurrent Time:', currentTime)

    # Compute essential variables ------------------------------- TODO verify filter *****
    dayShiftTime = df3[(df3['TimeLine'] >= Start_Day) & (df3['TimeLine'] <= currentTime)]

    totalRun = dayShiftTime.copy()
    totalRun = totalRun.drop_duplicates(subset='TimeLine', keep='first')
    # print('Total Run:', totalRun)

    # Convert Shift start time to string format -----------------
    shiftStartTime = str(datetime.strptime(Start_Day, "%H:%M:%S").time())
    shiftEndTime = str(datetime.strptime(FinishDay, "%H:%M:%S").time())
    print("Shift Starts:", shiftStartTime)
    print("Shift Ends @:", shiftEndTime)

    # Compute production lapse time -----------------------------
    TShiftSec = datetime.strptime(FinishDay, '%H:%M:%S') - datetime.strptime(shiftStartTime, '%H:%M:%S')
    ShiftinSec = TShiftSec.total_seconds()      # Convert values into seconds
    print('=' * 22)
    print('Shift Hours:', ShiftinSec, '(Sec)')

    deltaT = datetime.strptime(str(currentTime), '%H:%M:%S') - datetime.strptime(shiftStartTime, '%H:%M:%S')
    opTime = deltaT.total_seconds()           # Convert values into seconds
    print('\n********* SUMMARY **********')
    print('Operation Time:', opTime, '(Sec)')

    # Compute downtime in seconds -------------------------------
    downtime = totalRun['Duration(Sec)'].sum()
    print('TCP1 Down Time:', float(downtime), '(Sec)')

    # Computer work time relative to total shift hours ----------
    prodTime = (opTime - downtime)
    print('Net Production:', prodTime, '(Sec)')
    print('-' * 28)

    endShiftHour = (ShiftinSec - prodTime)

    pieData = np.array([endShiftHour, prodTime, downtime])
    segexplode = [0, 0, 0.1]

    ind_metric = ['Current Shift', 'Production Time', 'OEE Time']

    # Pie Chart Plot ---------------------
    # add colors
    mycol = ['#4c72b0', 'green', 'orange']              # add colors
    a3.pie(pieData, labels=ind_metric, startangle=90, explode=segexplode, shadow=True, autopct='%1.1f%%',
            colors=mycol, textprops={'fontsize': 10})


