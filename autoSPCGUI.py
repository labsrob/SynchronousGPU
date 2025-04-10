# -------------------------------------------------------------------------#
# Author: Dr RB Labs
# Developed for Magma Global - TechnipFMC Industrialization
# Email: robbielabs@uwl.ac.uk
# Copyright (C) 2023-2025, Robbie Labs
# --------------------------------------------------------------------------#
from multiprocessing import Process
import psutil
from threading import *
from pynput.keyboard import Key, Listener
from tkinter import *
import magmaSPC as lt
import os
# -------------------- Launch-keypress Functional Control ------------------#


def threadingCanvas(mySplash):
    import Primary_GUI as um
    if mySplash.withdraw:
        print('\nMenu Thread ID:', get_ident())
        mySplash.protocol('WM_DELETE_WINDOW', lambda: quit())
        um.userMenu()                                           # listener, mySplash
    # Call Canvas object in multi-threading process-----------------------------[P1]
    # p1 = Thread(target=mySplash.after, args=(1, lambda: um.userMenu(listener, mySplash)))
    # p1.start()


def showMenu(key):
    # you can terminate the program with 'End' button ----#
    if key == Key.end:
        print('\nTotal Number of Core-CPU#:', os.cpu_count())
        print('Killing Parent PID:', os.getppid())
        print('Killing Child PID:', os.getpid())
        print('SPC terminated by current user...')
        os._exit(0)

        return False        # Stop listener --------------#


def splashT(root=None):
    # if __name__ == '__main__':
    listener = Listener(on_press=showMenu, suppress=False)      # as listener:     # childP = Toplevel(root)
    listener.start()

    if root==None:
        cSplash = Tk()
    else:
        cSplash = Toplevel(root)
    cSplash.wm_attributes('-topmost', True)   # -topmost, -alpha, -disabled, -fullscreen, -toolwindow, -topmost

    print('\nNumber of Core-CPU#:', os.cpu_count())
    print('='*24)
    print('Alpha Parent PID:', os.getppid())
    print('Alpha Child PID:', os.getpid())
    print(f"CPU utilization: {psutil.cpu_percent()}%")
    print(f"Memory utilization: {psutil.virtual_memory().percent}%")
    print('-' * 25)

    # Use Main (primary) Process ID ------------------------[P1]
    conPLC = cSplash.after(10, lambda: lt.localSplash(listener, cSplash))
    print('Listener Thread:', get_ident())                      # get_native_id()

    if listener.is_alive():
        print('Listener is active')
    cSplash.mainloop()
    cSplash.protocol('WM_DELETE_WINDOW', lambda: quit())

    listener.join()                                             # block until block terminates

    return conPLC
