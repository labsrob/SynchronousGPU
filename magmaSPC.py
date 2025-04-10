# ------------------------------------------------------------------------
# Author: Dr RB Labs
# Developed for Magma Global - TechnipFMC Industrialization
# Email: robbielabs@uwl.ac.uk
# Copyright (C) 2023-2025, Robbie Labs
# ------------------------------------------------------------------------
"""
Called from LaunchSPC
Consists of:
1. Splash function - loading all run-time variables and writing INI files
2. Snooze mode function - when no activity, random screen saver object
3. Snooze Auto-restore function after closing GUI by an operator
4. Standby mode function -  Activating watch dog
5. Errors Handlers - Capturing all issues relating to processing & launching

"""
from tkinter import *
import tkinter as tk
from random import randint

from PIL import ImageTk, Image              # Python Imaging Library
# import ImageTk, Image
from matplotlib.image import imread
import matplotlib.pyplot as plt

import numpy as np
from multiprocessing import Process
from threading import *
import keyboard
from datetime import datetime
from time import sleep
import os
import psutil

# load a derived module ---
import CommsPlc as sn7
# import asyncio
# import sys

# -------------------------- Initiate variable --------------------
splashInUse = False
db_number = 89
start_offset = [898, 894]
bit_offset = [0, 1]

w, h = 425, 250
user_url = "http://www.magmaglobal.com"

stup_messages = ["Evaluating ring-head combinations", "Checking SQL repository Hardware",
                 "Accessing selected parameters", "Checking SPC Constants and Metrics",
                 "Evaluating Sampling Resolution", "Testing High-Speed Connectivity",
                 'Downloading SPC initialization Files', 'Loading SPC Visualisation Model',
                 'Writing SPC values into .INI File...', 'Saving & Finalizing .INI Files']

error_handlers = ['M2M connection failed, re-trying...', 'Fatal Error!, SPC Process Exiting...',
                  "Connection now established!"]


def errorLog(err):
    fileName = datetime.now().strftime('SPHLog '+"%Y-%m-%d")
    event = datetime.now().strftime("%Y-%m-%d %H:%M.%S")
    errorlogFile = str(fileName)
    f = open('.\\RuntimeLog\\'+errorlogFile+".txt", "a")
    f.write(event+' --- '+err+'\n')
    f.close()


# Check Screen resolution -----------------------------[]
def updateSCRres():
    import win32api    # pywin32
    import win32con
    import pywintypes
    devmode = pywintypes.DEVMODEType()
    # Check compliance ---------------
    devmode.PelsWidth = 2560  # 1920,  1680 (minimum resolution on 32inch Monitors)
    devmode.PelsHeight = 1440  # 1080, 1050

    devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT
    win32api.ChangeDisplaySettings(devmode, 0)


def checkRes():
    import ctypes
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    Width = user32.GetSystemMetrics(0)
    Height = user32.GetSystemMetrics(1)
    print('Current Screen Res:', Width, 'by', Height)
    if Width < 2560 and Height < 1440:
        print('Primary display not SPC Compliant..')
        print('\n Attempting to update screen resolution, please wait...')
        updateSCRres()
        print('Screen resolution updated successful!')
    else:
        print('Current Hardware resolution OK...')
    return


def move_window(token=None):
    global timer

    timer = Timer(2, move_window)       # Start threading.Timer()
    magic_token = token

    # Obtain magic token from primary GUI when closed by the user  Auto-restore splash
    if magic_token:
        print('Token is True, restoring snooze mode...')
        if not timer.is_alive():
            print('Timer is NOT active, after receiving the Token..')
            del timer
            mySplash.deiconify()
        else:
            print('Timer is Active, after receiving the Token')
            mySplash.deiconify()

    # --------------------------------------------------[]
    elif keyboard.is_pressed("esc"):                # Put Splash in Standby mode
        print('\nSPC in standby mode, press End to Exit or Alt-gr to GUI...')
        mySplash.geometry(f"{w}x{h}+{1080}+{595}")
        timer.cancel()
        mySplash.after(60000, lambda: move_window())

    elif keyboard.is_pressed("alt gr") and not timer.is_alive():            # Put Splash in Standby mode
        print('\nRelaunching GUI...')
        mySplash.withdraw()
        import Primary_GUI as um
        p1 = Thread(target=mySplash.after, args=(1, lambda: um.userMenu(listener, mySplash)))
        p1.start()

    else:
        # print('\nSPC in Snooze mode, press Esc to standby or Alt-gr to GUI...')             # Snooze function
        mySplash.geometry(f"{w}x{h}+{int(randint(10, 1900))}+{int(randint(10, 1000))}")
        if timer.is_alive():
            mySplash.deiconify()
        else:
            timer.start()


def sendM2M_ACK():
    # Send acknowledgement by raising M2MConACK on SCADA Process and activate watchdog ---[]
    try:

        # Check if the Bit is @Low then raise High --------------------------[A]
        m2mgood = sn7.readBool(db_number, start_offset[0], bit_offset[0])

        if not m2mgood:

            print('\nM2M connection acknowledged by SCADA...')
            sn7.writeBool(db_number, start_offset[0], bit_offset[0], 1)
            m2mgood = True

            # Initiate a new thread / process -------------------------------[B]
            print('Obtaining and writing SPC metrics to .INI..')

            call_once = sn7.spcMetricsModule()      # prevent multiple call for this procedure class
            call_once.saveMetric()                  # download metrics from scada & write values into .INI

    except KeyboardInterrupt as err:
        errorLog(err)

    return m2mgood


def autoSplash(istener, splash):
    global img, mySplash, splashInUse, listener

    print('\nNumber of Core-CPU#:', os.cpu_count())
    print('=' * 24)
    print('Splash Parent PID:', os.getppid())
    print('Splash Child PID:', os.getpid())
    print('Splash Thread:', get_ident())
    print(f"CPU utilization: {psutil.cpu_percent()}%")
    print(f"Memory utilization: {psutil.virtual_memory().percent}%")
    print('-' * 25)

    """
    Auto acknowledgement (sendM2M_ACK() function was added to pipeline.. 
    19/Feb/2024 - RL
    """
    # Check screen resolution for SPC compliance
    print('\nChecking Viz-Screen Resolution...')
    checkRes()
    # -----------------------------------------
    listener = istener
    print('Listerner prop:', listener)
    mySplash = splash                        # rename to allow usage in global.ini
    mySplash.overrideredirect(True)          # disable top bar

    # splash_root.geometry("450x250")           # defined above but can be altered to suit
    init_str = StringVar()
    init_str.set('Initializing variables...')

    print('SPC standby mode...')
    mySplash.title('SPC Industrialization')
    screen_w = mySplash.winfo_screenwidth()
    screen_h = mySplash.winfo_screenheight()
    # -------------------------------------------
    x_c = int((screen_w / 2) - (w / 2))
    y_c = int((screen_h / 2) - (h / 2))
    print(w, h, x_c, y_c)
    mySplash.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))

    # img = ImageTk.PhotoImage(Image.open("200x120.png"))
    path = 'C:\\Users\\DevEnv\\PycharmProjects\\SynchronousGPU\\Media\\Images\\'
    img = ImageTk.PhotoImage(Image.open(path + "200x120.png"))
    s_label = Label(mySplash, image=img, text="Welcome to Magma SPC", font=18)
    # x=35, y=122
    Label(mySplash, text="Synchronous Multivariate SPC", width=28, justify=CENTER, font=12).place(x=70, y=125)
    Label(mySplash, text="Advanced Statistical Processing & Visualization System", justify=CENTER).place(x=78, y=150)
    Label(mySplash, text="Integrated into SCADA's (CF/PEEK) Manufacturing Process", justify=CENTER).place(x=70, y=168)
    Label(mySplash, text=user_url).place(x=120, y=186)
    Label(mySplash, textvariable=init_str, width=30, justify=CENTER).place(x=100, y=215)  #
    s_label.pack()

    r = 10
    for n in range(r):
        sleep(.2)
        if n <= (r - 2):
            init_str.set(f"Connecting to PLC Subsystem.{'.' * n}".ljust(27))
            # print('Testing loop')

        else:
            init_str.set(f"Establishing connectivity.{'.' * n}".ljust(27))
            connectPLC = sn7.connectM2M()  # Connect to Snap7 Server
            print('\nCONN1:', connectPLC)
            # recall M2M connection again ----------- 1st time try
            if connectPLC:
                print('\nSending M2M acknowledgement... (1)')
                sendM2M_ACK()
            else:
                print('\nM2M acknowledgement failed...')
            mySplash.update_idletasks()

            retry = 0
            while not connectPLC and retry < 10:       # create a persistent loop
                try:
                    print('\nConnection failed at first instance, retrying...')
                    init_str.set(f"{error_handlers[1]}{'.' * n}".ljust(27))

                    print('Second try...')
                    connectPLC = sn7.connectM2M()                        # Connect to Snap7 Server
                    print('\nCONN2:', connectPLC)

                    # recall M2M connection again ----------- 2nd time
                    if connectPLC:
                        print('\nSending M2M acknowledgement... (2)')
                        sendM2M_ACK()
                        init_str.set("Sending M2M acknowledgement... (2)".ljust(27))
                        sleep(.5)
                        mySplash.update_idletasks()
                    else:
                        print('\nM2M acknowledgement failed...')
                        init_str.set("M2M acknowledgement failed...".ljust(27))
                        sleep(.5)
                        mySplash.update_idletasks()
                    # -----------------------------------------------#

                    init_str.set("PLC Connection is sorted".ljust(27))
                    sleep(.5)
                    mySplash.update_idletasks()

                except Exception as err:
                    print(f"Exception Error: '{err}'")
                    errorLog(error_handlers[0])             # retrying connection
                    init_str.set(f"{error_handlers[1]}{'.' * n}".ljust(27))
                    sleep(.5)
                    mySplash.update_idletasks()

                else:   # Connection failed, show status
                    if connectPLC:
                        # recall M2M connection again ----------- 3rd time
                        print('Successful connection established...')
                        init_str.set(f"{error_handlers[2]}{'.' * n}".ljust(27))
                        print('\nSending M2M acknowledgement... (3)')
                        sendM2M_ACK()
                        sleep(.5)                               # rest a while
                        mySplash.update_idletasks()
                    else:
                        # sn7.plc.destroy()                     # reset command
                        sn7.connectPLC = False
                        init_str.set(f"{error_handlers[1]}{'.' * n}".ljust(27))
                        print('Issues with M2M Connection, may shut down..')
                        sleep(.5)  # rest a while
                        mySplash.update_idletasks()
                retry += 1
                print('Counting', retry)
            # ---- TODO
            else:
                print('Runtime in progress...')
        sleep(.5)
        mySplash.update_idletasks()
        sleep(.5)

    for n in stup_messages:
        if sn7.connectPLC:                              # Check connectivity if it's available
            init_str.set(n)
        elif stup_messages[0] and not connectPLC:
            # persistent loop on connection -----
            alpha_try = 0
            while alpha_try < 10:
                # print('Alpha Try #', alpha_try)
                print('No sign of connectivity yet...')
                init_str.set(f'{error_handlers[1]}'.ljust(27))
                errorLog(error_handlers[1])
                sleep(.5)
                alpha_try += 1
            else:
                print('M2M connectivity failed....')
                break
        sleep(5)
        mySplash.update_idletasks()

    for n in range(r):
        sleep(.2)
        init_str.set(f"Almost Done.{'.' * n}".ljust(27))
        mySplash.update_idletasks()

    for n in range(r):
        sleep(.5)
        init_str.set("Almost Done..........".ljust(27))
        sleep(.5)
        init_str.set("Initialization Sorted...".ljust(27))
        mySplash.update_idletasks()

    Label(mySplash, text="WatchDog activated, remote call!", justify=LEFT).place(x=140, y=215)

    # Initiate a new thread / process -------------------------------[C]
    import spcWatchDog as wd
    print('Loading Watchdog Module, please wait... ')
    npid = wd.watchDog(listener, splash)  # carry 2 variables along, required to remove screen splash
    p = Process(target=npid)
    p.start()
    # p.join()

    mySplash.after(60000, lambda: move_window(False))        # call snooze function with false token

    return splashInUse


def localSplash(istener, splash):
    global img, mySplash, splashInUse, listener

    # Check screen resolution for SPC compliance & update res
    print('\nChecking Viz-Screen Resolution...')
    checkRes()

    # Initiate a new thread / process -------[C]
    # import spcWatchDog as wd
    # ----------------------------------------[]

    if not splashInUse:
        listener = istener
        print('Listener property:', listener)
        mySplash = splash                           # rename to allow usage in global.ini
        mySplash.overrideredirect(True)             # disable top bar

        # mySplash.geometry("450x250", bg='#f48024')           # defined above but can be altered to suit

        init_str = StringVar()
        init_str.set('Initializing variables...')

        print('\nSPC standby mode...')
        mySplash.title('SPC Industrialization')
        screen_w = mySplash.winfo_screenwidth()
        screen_h = mySplash.winfo_screenheight()
        # -------------------------------------------
        x_c = int((screen_w / 2) - (w / 2))
        y_c = int((screen_h / 2) - (h / 2))

        print(w, h, x_c, y_c)
        mySplash.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))

        path = 'C:\\Users\\DevEnv\\PycharmProjects\\SynchronousGPU\\Media\\Images\\'
        img = ImageTk.PhotoImage(Image.open(path + "200x120.png"))

        # Best practices ----------------------------------
        # im = Image.open(path + "200x120.png")           # image reference
        # img = tk.PhotoImage(file=im)

        # -------------------------------------------------
        pStatus = '#f48024'                                # '#f48024', '#66f424', '#249df4'
        mySplash.configure(bg=pStatus)                      # Change to default color

        s_label = Label(master=mySplash, image=img, text="Welcome to Magma SPC", font=18, bg=pStatus)
        Label(mySplash, text="Synchronous Multivariate SPC", width=28, justify=CENTER, font=12, bg=pStatus).place(x=80, y=125)
        Label(mySplash, text="Advanced Statistical Processing & Visualization System", justify=CENTER, bg=pStatus).place(x=65, y=150)
        Label(mySplash, text="Integrated into SCADA's (CF/PEEK) Manufacturing Process", justify=CENTER, bg=pStatus).place(x=55, y=168)
        Label(mySplash, text=user_url, bg=pStatus).place(x=120, y=186)
        Label(mySplash, textvariable=init_str, width=30, justify=CENTER, bg=pStatus).place(x=100, y=215)  #
        s_label.pack()

        r = 10
        for n in range(r):
            sleep(.2)
            if n <= (r - 2):
                init_str.set(f"Checking OS and file System.{'.' * n}".ljust(27))

            else:
                init_str.set(f"Establishing Modular Connectivity.{'.' * n}".ljust(27))
                mySplash.update_idletasks()

            sleep(.5)
            mySplash.update_idletasks()
            sleep(.5)

        for n in range(r):
            sleep(.2)
            init_str.set(f"Almost Done.{'.' * n}".ljust(27))

            sleep(.5)
            init_str.set(f"Connecting to PLC...{'.' * n}".ljust(27))
            mySplash.update_idletasks()

        for n in range(r):
            # ---------------------------------------------------------------#
            print('\nConnecting to PLC subsystem....')
            sleep(.2)
            init_str.set(f"Establishing connectivity.{'.' * n}".ljust(27))
            connectPLC = sn7.connectM2M()  # Connect to Snap7 Server

            # recall M2M connection again ----------- TODO 1st time try
            if connectPLC:
                init_str.set(f"Sending M2M acknowledgement....{'.' * n}".ljust(27))
                sendM2M_ACK()
                conPLC = True
            else:
                init_str.set(f"M2M acknowledgement failed.....{'.' * n}".ljust(27))
                conPLC = False
            mySplash.update_idletasks()
            # ------------------------------------------------------------[]

            retry = 0
            while not connectPLC and retry < 10:  # create a persistent loop
                try:
                    print('\nConnection failed at first instance, retrying...')
                    init_str.set(f"{error_handlers[1]}{'.' * n}".ljust(27))
                    sleep(.5)
                    connectPLC = sn7.connectM2M()  # Connect to Snap7 Server
                    mySplash.update_idletasks()

                    # recall M2M connection again ----------- 2nd time
                    if connectPLC:
                        init_str.set(f"Sending M2M acknowledgement... (2)".ljust(27))
                        sleep(.5)
                        sendM2M_ACK()
                        conPLC = True
                        mySplash.update_idletasks()
                    else:
                        init_str.set(f"M2M acknowledgement failed...".ljust(27))
                        sleep(.5)
                        conPLC = False
                        mySplash.update_idletasks()
                    # -----------------------------------------------#

                    init_str.set("PLC Connection is sorted !".ljust(27))
                    sleep(.5)
                    conPLC = True
                    mySplash.update_idletasks()

                except Exception as err:
                    print(f"Exception Error: '{err}'")
                    errorLog(error_handlers[0])                     # retrying connection
                    init_str.set(f"{error_handlers[1]}{'.' * n}".ljust(27))
                    sleep(.5)
                    mySplash.update_idletasks()

                else:  # Connection failed, show status
                    if connectPLC:
                        # recall M2M connection again ----------- 3rd time
                        print('Successful connection established...')
                        init_str.set(f"{error_handlers[2]}{'.' * n}".ljust(27))
                        print('\nSending M2M acknowledgement... (3)')
                        sendM2M_ACK()
                        sleep(.5)  # rest a while
                        conPLC = True
                        mySplash.update_idletasks()
                    else:
                        # sn7.plc.destroy()                     # reset command
                        sn7.connectPLC = False
                        init_str.set(f"{error_handlers[1]}{'.' * n}".ljust(27))
                        print('Issues with M2M Connection, may shut down..')
                        sleep(.5)  # rest a while
                        conPLC = False
                        mySplash.update_idletasks()
                retry += 1
                print('Counting', retry)

        for n in range(r):
            sleep(.5)
            init_str.set("Almost Done..........".ljust(27))

            sleep(.5)
            init_str.set("Initialization Sorted...".ljust(27))
            conPLC = True

            # Allow SPC loading user values from SCADA once for every pipe laying process ----
            mySplash.update_idletasks()

        Label(mySplash, text="Watchdog activated, auto call...", justify=LEFT).place(x=120, y=215)
        mySplash.after(60000, lambda: move_window(False))

        # Initiate a new thread / process -------------------------------[C]
        # npid = wd.watchDog(listener, splash)                # carry 2 variables along
        # p = Process(target=npid)
        # p.start()
        # # p.join()

        return conPLC