#------------ Start Here ----------------------------
import threading
import os
import time
import tkinter as tk
# import deltaM2_Functions as nw
import deltaStartup as nw

# shared state -------
system_state = {
    "sysRun": False,
    "sysIdl": True,
    "sysRdy": False,
    "won_NO": None
}

state_lock = threading.Lock()
stop_event = threading.Event()


def get_pStatus():
    print('Testing TCP01 Active Status...')
    sysRun, sysIdl, sysRdy, msctcp, won_NO, scadaT = nw.liveProductionRdy() # System idling
    if sysIdl or sysRdy or sysRun:
        nw.watchDog()             # Launch Watchdog from Snooze if live production
    else:
        status = nw.checkSQL()
        print('\nChecking SQL Server Status, please wait...')
        if status:
            print('Database Server is Up and running.')
        else:
            print('Database Server seems to be offline.')
            print('\nPLC maybe Offline or no new recipe found!')
        stop_event.set()        # terminate session if connections fail
    return


def get_qStatus():
    # Check live production and launch WatchDog Daemon -------

    print('\nChecking DB Repository Status, please wait...')
    status = nw.checkSQL()
    if status:
        print('\nDatabase Server is Up and running.')
    else:
        print('\nDatabase Server seems to be offline.')
    stop_event.set()            # terminate session if connections fail
# ----------------------------------------------------------------

def load_DS(event):
    # global event

    while not event.is_set():
        print("\nLoading Snooze default screen to thread: {}".format(threading.current_thread().name))
        print("ID of process running Snooze default Screen: {}".format(os.getpid()))

        # ----- load screen saver
        nw.startSession()

        stop_event.set()    # set stop flag if dS exited
    print("Snooze thread is removed.")


def load_WD(event):
    # Load WD if TCP01 standby Bit is High
    print("Loading M2M Algorithm: {}".format(threading.current_thread().name))
    print("Live GPU Process ID #: {}".format(os.getpid()))

    while not stop_event.set():
        sysRun, sysIdl, sysRdy, msctcp, won_NO, scadaT = nw.liveProductionRdy()
        with state_lock:
            system_state["sysRun"] = sysRun
            system_state["sysIdl"] = sysIdl
            system_state["sysRdy"] = sysRdy
            system_state["won_NO"] = won_NO
            system_state["scadaT"] = scadaT
        lapt = 0
        # Set priority to PLC connection -----------------------------
        timei = time.time()                 # start timing the entire loop

        status = nw.checkPLC()               # Check if PLC Host is online
        print('\nM2M Connection Status:', status)

        if scadaT:
            print('TCP01 Production Status is Ok')
            nw.watchDog()                   # Launch Watchdog
        elif not system_state["sysRdy"]:
            timef = time.time()
            deltaT = round((60 - lapt), 2)
            print(f'Retrying PLC (M2M) connection in:', str(deltaT), ' sec')
            time.sleep(deltaT)      # relax for stochastic bandwidth ripple.
            get_pStatus()           # call plc status function

    lapt = (timef - timei)
    print(f"Lapsed: {lapt} sec")
    stop_event.set()


#  if __name__ == "__main__":
print("Synchronous SPC: {}\n".format(threading.current_thread().name))

# Create and start the thread ----------
DS = threading.Thread(target=load_DS, args=(stop_event,), name='DefScreen', daemon=True)
WD = threading.Thread(target=load_WD, args=(stop_event,), name='WatchDog', daemon=True)

DS.start()
WD.start()

# print("Stopping the thread...")
stop_event.set()

DS.join()
WD.join(timeout=1.0)

