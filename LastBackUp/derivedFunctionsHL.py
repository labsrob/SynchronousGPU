##
from tkinter import *
import tkinter as tk
from tkinter.simpledialog import Dialog

#

def clearMetrics():
    # clear the content of chart parameter using change settings button ---
    global e8, e7
    sSta.set('07:00:00')
    sEnd.set('17:00:00')

    Entry(pop, width=8, state='normal', textvariable=sSta).place(x=325, y=50)      # Shift starts
    Entry(pop, width=8, state='normal', textvariable=sEnd).place(x=450, y=50)      # Shift ends

    e7 = ttk.Combobox(pop, width=8, values=[" Select", "10", "15", "20", "23", "25", "25", "30"], state="normal")
    e7.bind("<<ComboboxSelected>>", display_sel)
    e7.place(x=40, y=50)
    e8 = ttk.Combobox(pop, width=10, values=["SS-Domino", "GS-Discrete"], state="normal")
    e8.bind("<<ComboboxSelected>>", display_selection)
    e8.place(x=172, y=50)
    # repopulate with default values

    metRO = True
    print('SQL Field State:', metRO)    # metric fields set to read only

    return metRO


def calculationRF(xUCLa, xLCLa, xUCLb, xLCLb, gSize1, pf, pf1, pg, pg1, ph, ph1, pi, pi1, event=None):
    global xBarMa, xBarMb, xBarMc, xBarMd, xBarMe, xBarMf, xBarMg, sBarMa, sBarMb, sBarMc, sBarMd, sBarMe,\
    sBarMf, sBarMg, sUCLa, sUCLb, sUCLc, sUCLd, sUCLe, sUCLf, sUCLg, sLCLa, sLCLb, sLCLc, sLCLd, sLCLe, sLCLf,\
     sLCLg

    try:
        # Compute XBar mean / center line ----------------------[RF]
        if xUCLa.get() and xLCLa.get():
            xBarMa = float(xLCLa.get()) + ((float(xUCLa.get()) - float(xLCLa.get())) / 2)
            sUCLa, sLCLa, sBarMa = checkhistDev(float(xUCLa.get()), xBarMa, gSize1.get()) # Compute S-Chart Mean
            xUSLa = xBarMa + (float(xUCLa.get()) - xBarMa) / 3 * 6
            xLSLa = xBarMa - (xBarMa - float(xLCLa.get())) / 3 * 6

            print('Roller Force: XBar Mean', xBarMa)
            # Display values on user screen mat ----------------[1]
            pf["text"] = round(xBarMa, 3)   # XBar Mean value
            pg["text"] = round(sBarMa, 3)   # S Bar Mean
            ph["text"] = round(xUSLa, 3)    # XBar Upper Set Limit
            pi["text"] = round(xLSLa, 3)    # XBar Lower Set Limit
        # ------------------------------------------------------[TT]
        if xUCLb.get() and xLCLb.get():
            xBarMb = float(xLCLb.get()) + ((float(xUCLb.get()) - float(xLCLb.get())) / 2)
            sUCLb, sLCLb, sBarMb = checkhistDev(float(xUCLb.get()), xBarMb, gSize1.get())  # Compute S-Chart Mean
            xUSLb = xBarMb + (float(xUCLb.get()) - xBarMb) / 3 * 6
            xLSLb = xBarMb - (xBarMb - float(xLCLb.get())) / 3 * 6

            print('Roller Force: XBar Mean', xBarMb)
            # Display values on user screen mat ----------------[1]
            pf1["text"] = round(xBarMb, 3)  # XBar Mean value
            pg1["text"] = round(sBarMb, 3)  # S Bar Mean
            ph1["text"] = round(xUSLb, 3)  # XBar Upper Set Limit
            pi1["text"] = round(xLSLb, 3)  # XBar Lower Set Limit
        # ------------------------------------------------------[ST]

    except ValueError:
        pf["text"] = "Entry not permitted, float numbers only"
        pg["text"] = "Entry not Permitted, float numbers only"

        ph["text"] = "Entry not permitted, float numbers only"
        pi["text"] = "Entry not Permitted, float numbers only"

        pf1["text"] = "Entry not permitted, float numbers only"
        pg1["text"] = "Entry not Permitted, float numbers only"

        ph1["text"] = "Entry not permitted, float numbers only"
        pi1["text"] = "Entry not Permitted, float numbers only"

    # clear the content and allow entry of historical limits -------

    xUCLa.set('')
    xLCLa.set('')
    # xBarMa.set('')

    xUCLb.set('')
    xLCLb.set('')
    # xBarMb.set('')
