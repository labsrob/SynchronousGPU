# ---------------- READ ME ---------------------------------------------
# This Script is Created Only For Practise And Educational Purpose Only
# This is an Example Of Tkinter Canvas Graphics
# This Script Is Created For http://bitforestinfo.blogspot.in
# This Script is Written By
#
#
##################################################
######## Please Don't Remove Author Name #########
############### Thanks ###########################
##################################################
#
#
__author__='''

######################################################
                Industrialisation Group                          
######################################################

    Lead Author: Robert B. Labs
    Team:        T. Preston, E. V-Harcourt, O. Oldham
    Company:     Magma Global, England
######################################################
'''
print(__author__)

# ---------------------------------------------------------[]
import sys
from tkinter import *
from time import sleep, strftime
from tkinter import messagebox
import os
running = True

# close window --------------[]
def mMenu(event):           # Terminate using Mouse motion
    running = False
    os._exit(0)             # root.protocol('WM_DELETE_WINDOW', lambda: quit())


def mSpalsh(event):         # Terminate using Escape Key
    import magmaSplash as spc

    running = False
    root.deiconify()
    os._exit(0)             # root.protocol('WM_DELETE_WINDOW', lambda: quit())
    spc.repoxy(event)


def mVisual(event):
    running = False
    # spc.myMain()
    os._exit(0)             # root.protocol('WM_DELETE_WINDOW', lambda: quit())


def defltSaver():
    global running
    # --------------
    while running:
        tk_Owner.set(value='Magma Global SPC\n')
        tkinter_time.set(value=strftime("%H:%M:%S"))
        tkinter_date.set(value=strftime("%A, %e %B"))
        root.update_idletasks()
        root.update()
        sleep(1)


def splashSever():
    global tk_Owner, tkinter_time, tkinter_date, root
    root = Tk()

    # Window Attributes ----------------------------[]
    root.overrideredirect(True)
    root.wm_attributes("-transparentcolor", "gray99")

    root.bind("<Motion>", mMenu)        # back to Program GUI Menu
    root.bind("<Escape>", mSpalsh)      # back to splash screen
    # ----------------------------------#
    # ACKN =
    root.bind("<Key>", mVisual)         # ACKN bit from PLC
    # ----------------------------------------------[]
    root.config(cursor="none")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    timeframe = Frame(root, width=screen_width, height=screen_height, bg="Black")
    timeframe.grid(row=0, column=0)

    tk_Owner = StringVar() #
    tk_label = Label(timeframe, textvariable=tk_Owner, fg="#808080", bg="Black", font=("NovaMono", 80),)
    tk_label.place(y=screen_height / 2 - 60, x=screen_width / 2, anchor="center")

    tkinter_time = StringVar()
    time_label = Label(timeframe, textvariable=tkinter_time, fg="#808080", bg="Black", font=("NovaMono", 150),)
    time_label.place(y=screen_height / 2 + 60, x=screen_width / 2, anchor="center")

    tkinter_date = StringVar()
    date_label = Label(timeframe, textvariable=tkinter_date, fg="#808080", bg="Black", font=("Bahnschrift", 30),)
    date_label.place(y=screen_height / 2 + 200, x=screen_width / 2, anchor="center")
    root.update_idletasks()

    defltSaver()

    # root.mainloop()
# ------------[]
splashSever()