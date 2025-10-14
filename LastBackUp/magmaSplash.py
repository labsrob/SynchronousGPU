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
from tkinter import *               # Load this Library first
from random import randint
from PIL import ImageTk, Image      # Python Imaging Library
from multiprocessing import Process
from threading import *
from datetime import datetime
from time import sleep
import os
import psutil

# load a derived module ---
import CommsPlc as sn7
#
import asyncio
import sys

# -------------------------- Initiate variable --------------------
splashInUse = False

db_number = 89
start_offset = [898, 894]
bit_offset = [0, 1]

# -----------------------
# w, h = 425, 250
# w, h = 780, 450
# w, h = 425, 250
# -----------------------

user_url = "http://www.magmaglobal.com/synchronous_spc"

# ------------ Launch-Screen Event Functional Control --------------
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


# Window Exit Functions -----------------------------------------------------[]
def out(event):
    # import DefaultScreen as um
    print('\nExiting Splash Screen...')
    mySplash.deiconify()
    timer.cancel()
    mySplash.destroy()
    if mySplash.withdraw:
        print('Loading SPC GUI...\n')

        print('\nMenu Thread ID:', get_ident())
        # mySplash.protocol('WM_DELETE_WINDOW', lambda: quit())
        # um.defltSaver()         # listener, mySplash

    # running = False
    # p1 = Thread(target=mySplash.after, args=(1, lambda: um.userMenu(listener, mySplash)))
    # p1.start()
    # mySplash.mainloop()

    return

def repoxy(event):
    print('\nMomentary paused Screen Saver...')
    timer.cancel()

    mySplash.deiconify()

    screen_w = mySplash.winfo_screenwidth()
    screen_h = mySplash.winfo_screenheight()
    # -------------------------------------------
    x_c = int((screen_w / 2) - (w / 2))
    y_c = int((screen_h / 2) - (h / 2))

    mySplash.deiconify()
    mySplash.geometry(f"{w}x{h}+{x_c}+{y_c}")
    sleep(.9)
    # ------------------------------------------
    import DefaultScreen as um
    # mySplash.after(10000, lambda: move_window())        # delay for 10 seconds
    mySplash.iconify()
    timer.cancel()
    mySplash.destroy()
    um.splashSever()

    return

# Check Screen resolution -----------------------------[]
def updateSCRres():
    import win32api    # pywin32
    import win32con
    import pywintypes
    devmode = pywintypes.DEVMODEType()

    # Check compliance --------------------[]
    devmode.PelsWidth = 2560    # 1920, 1680
    devmode.PelsHeight = 1440   # 1080, 1050

    devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT
    win32api.ChangeDisplaySettings(devmode, 0)


def checkRes():
    global scrZ

    import ctypes
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    Width = user32.GetSystemMetrics(0)
    Height = user32.GetSystemMetrics(1)

    # -----------------------------------------------
    print('Current Screen Res:', Width, 'by', Height)
    # -----------------------------------------------

    if Width == 2560 and Height == 1440:
        print('Current Hardware resolution OK...')
        scrZ = '2k'

    elif Width > 2560 and Height > 1440:
        print('Current Hardware resolution is superb!')
        scrZ = '4k'

    else:
        print('\n Attempting to update screen resolution, please wait...')
        scrZ = '1k'     # 2416 by 1274 - VGA
        updateSCRres()
        print('Screen resolution updated successful!')
        print('Primary display not SPC Compliant..')

    return scrZ

def new_instanceMenu():
    pass


def move_window():
    global timer

    timer = Timer(2, move_window)       # Start threading.Timer()

    mySplash.bind("<Motion>", out)          # Mouse Program Menu
    mySplash.bind("<Escape>", repoxy)       # Re-centralise splash & access default screen save

    mySplash.config(cursor="none")

    # --------------------------------------------------[]
    # checkRes()
    print('\nSPC in Snooze mode, press Esc to standby or Other keys to resume')             # Snooze function
    # --------------------------------------------------[]
    # while 1 < 60:
    mySplash.geometry(f"{w}x{h}+{int(randint(10, 1900))}+{int(randint(10, 1000))}")
    if not timer.is_alive():
        timer.start()
    else:
        timer.cancel()
        mySplash.deiconify()
        # out(event)                   # default screen saver
        # mySplash.after(5000, lambda: out())
        new_instanceMenu()   # GUI



    return


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
    print('Listener prop:', listener)
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

    img = ImageTk.PhotoImage(Image.open("200x120.png"))
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
                print('\nConnection failed at first instance, retrying...')
                init_str.set(f"{error_handlers[1]}{'.' * n}".ljust(27))
                try:
                    print('Second try...')
                    connectPLC = sn7.connectM2M()                        # Connect to Snap7 Server
                    print('\nCONN2:', connectPLC)
                    # recall M2M connection again ----------- 2nd time
                    if connectPLC:
                        print('\nSending M2M acknowledgement... (2)')
                        sendM2M_ACK()
                    else:
                        print('\nM2M acknowledgement failed...')

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

    mySplash.after(60000, lambda: move_window())        # call snooze function with false token

    return splashInUse



def localSplash():
    global img, mySplash, splashInUse, w, h, m

    # Check screen resolution for SPC compliance & update res
    print('\nChecking Viz-Screen Resolution...')
    scrRes = checkRes()
    if scrRes == '4k':
        w, h, f, p, v, u = 1450, 900, 18, 280, 230, 120     # width, height, font size, xpos, ypos, uxpos
    elif scrRes == '2k':
        w, h, f, p, v, u = 780, 450, 14, 280, 230, 120      # width, height, font size, xpos, ypos, uxpos
    else:
        w, h, f, p, v, u = 425, 260, 10, 121, 234, 80      # width, height, font size, xpos, ypos, uxpos

    # -----------------------------------------
    mySplash.overrideredirect(True)  # disable top bar
    # mySplash.wm_attributes("-transparentcolor", "gray99")

    init_str = StringVar()
    if not splashInUse:

        init_str.set('Initializing variables...')

        print('\nSPC standby mode...')
        mySplash.title('SPC Industrialization')
        screen_w = mySplash.winfo_screenwidth()
        screen_h = mySplash.winfo_screenheight()
        # -------------------------------------------

        x_c = int((screen_w / 2) - (w / 2))
        y_c = int((screen_h / 2) - (h / 2))
        print('Screen Size:', w, h, x_c, y_c)                           # Screen Size: 425 250 1067 595
        mySplash.geometry("{}x{}+{}+{}".format(w, h, x_c, y_c))

        if scrRes == '4k':
            print('\nUsing 4k screen resolution...')
            img = ImageTk.PhotoImage(Image.open("400x220.png"))
            s_label = Label(mySplash, image=img, text="Welcome to Magma SPC", font=72)
            # --------------------------------------------------------------------------
            Label(mySplash, text="Synchronous Multivariate SPC", width=28, justify=CENTER, font=85).place(x=70, y=125)
            Label(mySplash, text="Advanced Statistical Processing & Visualization System", justify=CENTER).place(x=78, y=150)
            Label(mySplash, text="Integrated into SCADA's (CF/PEEK) Manufacturing Process", justify=CENTER).place(x=70, y=168)
            Label(mySplash, text=user_url, font=("NovaMono", 18)).place(x=u, y=186)
            Label(mySplash, textvariable=init_str, width=30, justify=CENTER).place(x=100, y=215)  #
            s_label.pack()

        elif scrRes == '2k':
            print('\nUsing 2k screen resolution...')
            img = ImageTk.PhotoImage(Image.open("200x120.png"))
            s_label = Label(mySplash, image=img, text="Welcome to Magma SPC", font=36)
            # --------------------------------------------------------------------------
            Label(mySplash, text="Synchronous Multivariate SPC", width=28, justify=CENTER, font=("NovaMono", 30)).place(x=70, y=125)
            Label(mySplash, text="Advanced Statistical Processing & Visualization System", justify=CENTER, font=("NovaMono", 14)).place(x=160, y=175)
            Label(mySplash, text="Integrated into SCADA's (CF/PEEK) Manufacturing Process", justify=CENTER, font=("NovaMono", 14)).place(x=135, y=200)
            Label(mySplash, text=user_url, font=("NovaMono", 12)).place(x=u, y=230)
            Label(mySplash, textvariable=init_str, width=30, justify=CENTER, font=("NovaMono", 14)).place(x=230, y=280)  #
            s_label.pack()

        else:
            print('\nUsing VGA screen resolution...')
            img = ImageTk.PhotoImage(Image.open("200x120.png"))
            s_label = Label(mySplash, image=img, text="Welcome to Magma SPC", font=18)
            # --------------------------------------------------------------------------
            Label(mySplash, text="Synchronous Multivariate SPC", width=28, justify=CENTER, font=12).place(x=80, y=125)
            Label(mySplash, text="Advanced Statistical Processing & Visualization System", justify=CENTER).place(x=65, y=150)
            Label(mySplash, text="Integrated into SCADA's (CF/PEEK) Manufacturing Process", justify=CENTER).place(x=55, y=168)
            Label(mySplash, text=user_url).place(x=u, y=186)
            Label(mySplash, textvariable=init_str, width=30, justify=CENTER).place(x=100, y=215)  #
            s_label.pack()
        mySplash.update()

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
            mySplash.update_idletasks()

        for n in range(r):
            sleep(.5)
            init_str.set("Almost Done..........".ljust(27))
            sleep(.5)
            init_str.set("Initialization successful...".ljust(27))

            # Allow SPC loading user values from SCADA once for every pipe laying process ---- f, p, v
            mySplash.update_idletasks()

        Label(mySplash, text="OPC UA Watchdog enabled!", justify=LEFT, font=("NovaMono", f)).place(x=p, y=v)
        # Initiate a new thread / process -------------------------------[C]
        import spcWatchDog as wd
        print('Loading Watchdog Module, please wait... ')
        npid = wd.watchDog(mySplash)                    # required to remove screen splash
        p = Process(target=npid)
        p.start()
        mySplash.after(5000, lambda: move_window())

    mySplash.update_idletasks()
    # mySplash.update()


if __name__ == '__main__':
    mySplash = Tk()

    mySplash.wm_attributes('-topmost', True)            # "-transparentcolor",
    print('\nNumber of Core-CPU#:', os.cpu_count())
    print('=' * 24)
    print('Alpha Parent PID:', os.getppid())
    print('Alpha Child PID:', os.getpid())
    print(f"CPU utilization: {psutil.cpu_percent()}%")
    print(f"Memory utilization: {psutil.virtual_memory().percent}%")
    print('-' * 25)

    # mySplash.after(5000, lambda: localSplash())
    localSplash()
    mySplash.mainloop()

