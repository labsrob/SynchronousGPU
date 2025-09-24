#------------ Start Here ----------------------------
import threading
import os
import time
import deltaM2_Functions as nw


def get_pStatus():
    print('Testing TCP01 Active Status...')
    sysidl, sysrdy, sysRun = nw.liveProductionRdy() # System idling
    if sysidl or sysrdy or sysRun:
        nw.watchDog()             # Launch Watchdog from Snooze if live production
    else:
        condB = nw.checkSQL()
        print('\nChecking SQL Server Status, please wait...')
        if condB:
            print('Database Server is Up and running.')
        else:
            print('Database Server seems to be offline.')
            print('\nPLC maybe Offline or no new recipe found!')
        stop_event.set()        # terminate session if connections fail
    return


def get_qStatus():
    # Check live production and launch WatchDog Daemon -------

    print('\nChecking DB Repository Status, please wait...')
    condB = nw.checkSQL()
    if condB:
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
        nw.dScreen()
        stop_event.set()    # set stop flag if dS exited
    print("Snooze thread is removed.")


def load_WD(event):
    # Load WD if TCP01 standby Bit is High
    print("\nLoad Synchronous Watchdog Program: {}".format(threading.current_thread().name))
    print("ID of process running Synchronous Watchdog request: {}".format(os.getpid()))

    while not stop_event.set():
        lapt = 0
        # Set priority to PLC connection -----------------------------
        timei = time.time()                 # start timing the entire loop

        conPx = nw.checkPLC()               # Check if PLC Host is online
        print('\nConnection Good?', conPx)
        if conPx !='False':
            print('TCP01 Production Status is Ok')
        else:
            print('Re-checking TCP1 Production Status, please wait...')
            timef = time.time()
            deltaT = round((180 - lapt), 2)

            time.sleep(deltaT)              # relax for stochastic bandwidth ripple.

            lapt = (timef - timei)
            print(f'Retrying M2M connection in:', str(deltaT), ' sec')
            get_pStatus()
        print(f"Lapsed: {lapt} sec")
    stop_event.set()


# Create the event ----------
stop_event = threading.Event()

if __name__ == "__main__":

    print("\nID of process running SPC program: {}".format(os.getpid()))
    print("Synchronous SPC: {}\n".format(threading.current_thread().name))

    # Create and start the thread ----------
    DS = threading.Thread(target=load_DS, args=(stop_event,), name='DefScreen', daemon=True)
    WD = threading.Thread(target=load_WD, args=(stop_event,), name='WatchDog', daemon=True)

    DS.start()
    time.sleep(5)
    WD.start()

    # print("Stopping the thread...")
    stop_event.set()

    DS.join()
    WD.join(timeout=1.0)