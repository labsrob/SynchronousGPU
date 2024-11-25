# ----------------------------------------------------------------------
# Author: Dr RB Labs
# Developed for Magma Global - TechnipFMC Industrialization
# Email: robbielabs@uwl.ac.uk
# Copyright (C) 2023-2025, Robbie Labs
# ------------------------------------------------------------------------
# from tkinter import messagebox, ttk
from multiprocessing import Process
import psutil
from threading import *
from pynput.keyboard import Key, Listener
from tkinter import *
from tkinter import messagebox
import magmaSPC as lt
import os
import win32gui

# -------------------- Launch-keypress Functional Control ------------------


def errorlocalGUI():
    messagebox.showerror('Local GUI', 'Access to GUI is not possible. USe SCADA Screen')
    return


def respiteAct(key):
    if key == Key.alt_gr:
        print('\nTotal Number of Core-CPU#:', os.cpu_count())
        print('Local GUI not available, access through SCADA only.')
        errorlocalGUI()

    # you can terminate the program with 'End' button ----
    if key == Key.end:
        print('Emergency Abort: User\'s termination attempt...')
        print('Killing Parent PID:', os.getppid())
        print('Killing Child PID:', os.getpid())
        print('SPC terminated by Local User...')
        # mySplash.withdraw()
        # lt.timer.cancel()
        os._exit(0)
        return True


if __name__ == '__main__':
    listener = Listener(on_press=respiteAct, suppress=False)  # .start()
    listener.start()

    mySplash = Tk()
    mySplash.wm_attributes("-topmost", True)  # set splash screen on top

    print('\nNumber of Core-CPU#:', os.cpu_count())
    print('='*24)
    print('Alpha Parent PID:', os.getppid())
    print('Alpha Child PID:', os.getpid())
    print(f"CPU utilization: {psutil.cpu_percent()}%")
    print(f"Memory utilization: {psutil.virtual_memory().percent}%")
    print('-' * 25)

    # Start screen splash --------------------------------[P]
    mySplash.after(1, lambda: lt.autoSplash(listener, mySplash))
    print('Listener Thread:', get_ident())  # get_native_id()

    if listener.is_alive():
        print('Listener is active')
    mySplash.mainloop()
    mySplash.protocol('WM_DELETE_WINDOW', lambda: quit())

    listener.join()
