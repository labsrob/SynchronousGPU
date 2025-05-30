# User Interface for defining and viewing Historical limits on Quality parameters ----------------#
# Author: Dr Labs, RB
#
#
# Using ConfigParser Utility - file formats like .ini, .conf, and .cfg files
# NOTE: This module presented few challenges that made me query the config.parser() class module
# When dealing with recursive variable using python's statement 'with open() as xx'
# write() class performs the write but then keep the written keys in its memory indefinitely unless
# when a new instance is obtained by closing the app and re launched.
# This was very frustrating, and it took efforts to realise this unusual persistency.
# I was able to detect this by changing the key and section and attempt writing into a new txt file
# This action clearly showed two records as against one.
# Now that duplicated section values are recorded, we can then remove the section before recursive
# to a new entry values. This was achieved with config.remove_section() method.
# -------------------------------------------------------------------------------------------------#
from datetime import datetime
from tkinter import *
from tkinter import messagebox
from configparser import ConfigParser
import onetimepad

pa1, pa2, =  0, 0
rollerForceHL, tapeTempHL, substTempHL, tapeSpeedHL, tapeGapHL = [], [], [], [], []
cSelectVar = []
tup = []
arrayTG, arrayWS, arrayRP, arrayTT, arrayST = [], [], [], [], []
# --------------------------------------------[]
# Get the configparser object
config_object = ConfigParser()
config = ConfigParser()

# XBar Constants ------------------------------[]
A3 = [0.975, 0.789, 0.680, 0.6327, 0.606, 0.5525]  # 10, 15, 20, 23, 25, 30  sample sizes respectively
B3 = [0.284, 0.428, 0.510, 0.5452, 0.565, 0.6044]  # 10, 15, 20, 23, 25, 30  sample sizes respectively
B4 = [1.716, 1.572, 1.490, 1.4548, 1.435, 1.3956]  # 10, 15, 20, 23, 25, 30

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")


def loadConst(xUCL, MeanP, sampSiz):
    # Evaluate SPC constants with chosen sample size --
    print('SAMPLE:', sampSiz)
    if sampSiz == '10':
        const1 = A3[0]
        const2 = B3[0]
        const3 = B4[0]
    elif sampSiz == '15':
        const1 = A3[1]
        const2 = B3[1]
        const3 = B4[1]
    elif sampSiz == '20':
        const1 = A3[2]
        const2 = B3[2]
        const3 = B4[2]
    elif sampSiz == '23':
        const1 = A3[3]
        const2 = B3[3]
        const3 = B4[3]
    elif sampSiz == '25':
        const1 = A3[4]
        const2 = B3[4]
        const3 = B4[4]
    elif sampSiz == '30':
        const1 = A3[5]
        const2 = B3[5]
        const3 = B4[5]
    else:
        print('Sample Size undefined!, Exiting...')
    # Compute for stdDev  in  [xUCL = meanP + (const1 * stdDev)]
    stdDev = (xUCL - MeanP) / const1

    sUCL = (const3 * stdDev)  # Upper control limits of 1 std dev
    sLCL = (const2 * stdDev)  # Lower control limits of 1 Std dev

    return sUCL, sLCL, stdDev
# -------------------------------------------------------------------[]


def errorEntry():
    # root.wm_attributes('-topmost', True)
    messagebox.showwarning('Entry Error', 'Field suitable for floating point numbers only')
    return


def errorNote():
    # root.wm_attributes('-topmost', True)
    messagebox.showerror('Key Error', 'Work Order config Not found')
    return



def qpHLtt(pop, gSize, ttxUCL, ttxLCL, ttsUCL, ttsLCL, ttxUCL1, ttxLCL1,  ttsUCL1, ttsLCL1, ttxUCL2, ttxLCL2, ttsUCL2,\
           ttsLCL2, ttxUCL3, ttxLCL3, ttsUCL3, ttsLCL3, ttxUCL4, ttxLCL4, ttsUCL4, ttsLCL4, WONID):

    global processID, val1, val2, val3, val4, val5, val6, val7, val8, val9, val10, val11, val12, val13, \
        val14, val15, val16, val17, val18, val19, val20, val25, val26

    processID = WONID
    # ------------------
    sReg, pReg = StringVar(pop), StringVar(pop)

    # Function performs dynamic calculations ---[]
    def calculation(event=None):
        global testVarTT, testVarTTa, testVarTTb, testVarTTc, testVarTTd, testVarTTe

        try:
            # Compute XBar mean / center line ----------------------[Line1]
            if ttxUCL.get() and ttxLCL.get():
                xBarMa = float(ttxLCL.get()) + ((float(ttxUCL.get()) - float(ttxLCL.get())) / 2)
                sUCLa, sLCLa, sBarMa = loadConst(float(ttxUCL.get()), xBarMa, gSize)  # Compute S-Chart Mean
                xUSLa = xBarMa + (float(ttxUCL.get()) - xBarMa) / 3 * 6
                xLSLa = xBarMa - (xBarMa - float(ttxLCL.get())) / 3 * 6

                # print('\nTape Temp (22mm): xMean/xUSL/xLSL:', xBarMa, xUSLa, xLSLa)
                # Archiving values into dynamic List
                testVarTTa = (dt_string, '22mm', ttxUCL.get(), ttxLCL.get(), ttsUCL.get(), ttsLCL.get(), round(xBarMa, 3),
                              round(sBarMa, 3), round(xUSLa, 3), round(xLSLa, 3), '1')
                # print('TT Historical:', testVarTTa)

                # -------------------------------------------------------[for Tom Preston]
                def click(event):
                    cSelect = 1
                    cSelectVar.append(cSelect)
                    # print('Focus is selected......', cSelect)
                    val3.config(state=NORMAL)
                    val3.delete(0, END)
                    val4.config(state=NORMAL)
                    val4.delete(0, END)
                    # allow new manual entry ----
                    val3.get()
                    val4.get()

                val3.bind('<Button-1>', click)

                # copy calculated values into user entry and allow edit--
                if not cSelectVar:
                    # print('Focus is NOT selected...')
                    # val3.insert(0, round(sUCLa, 3))   # Allow static values
                    ttsUCL.set(round(sUCLa, 3))         # allow dynamic updated values
                    val3.config(state='readonly')
                    ttsLCL.set(round(sLCLa, 3))
                    val4.config(state='readonly')

                else:
                    # print('Focus is selected......')
                    val3.get()  # delete(0, 'end')
                    val4.get()
                # -----------------------------------------------[End of function Tom Preston]
                # Display values on user screen mat -------------[1]
                val1A["text"] = round(xBarMa, 3)
                val2A["text"] = round(sBarMa, 3)
                val3A["text"] = round(xUSLa, 3)
                val4A["text"] = round(xLSLa, 3)

            # ------------------------------------------------------[Line 2]
            if ttxUCL1.get() and ttxLCL1.get():
                xBarMb = float(ttxLCL1.get()) + ((float(ttxUCL1.get()) - float(ttxLCL1.get())) / 2)
                sUCLb, sLCLb, sBarMb = loadConst(float(ttxUCL1.get()), xBarMb, gSize)  # Compute S-Chart Mean
                xUSLb = xBarMb + (float(ttxUCL1.get()) - xBarMb) / 3 * 6
                xLSLb = xBarMb - (xBarMb - float(ttxLCL1.get())) / 3 * 6

                # print('Tape Temp (22mm): xMean/xUSL/xLSL:', xBarMb, xUSLb, xLSLb)
                # Archiving values into dynamic List
                testVarTTb = (dt_string, '22mm', ttxUCL1.get(), ttxLCL1.get(), ttsUCL1.get(), ttsLCL1.get(), round(xBarMb, 3),
                              round(sBarMb, 3), round(xUSLb, 3), round(xLSLb, 3), '2')
                # print('TT Historical:', testVarTTb)

                # -------------------------------------------------------[for Tom Preston]
                def click(event):
                    cSelect = 1
                    cSelectVar.append(cSelect)
                    # print('Focus is selected......', cSelect)
                    val7.config(state=NORMAL)
                    val7.delete(0, END)
                    val8.config(state=NORMAL)
                    val8.delete(0, END)
                    # allow new manual entry ----
                    val7.get()
                    val8.get()

                val7.bind('<Button-1>', click)

                # copy calculated values into user entry and allow edit--
                if not cSelectVar:
                    # print('Focus is NOT selected...')
                    # val3.insert(0, round(sUCLa, 3))   # Allow static values
                    ttsUCL1.set(round(sUCLb, 3))  # allow dynamic updated values
                    val7.config(state='readonly')
                    ttsLCL1.set(round(sLCLb, 3))
                    val8.config(state='readonly')
                else:
                    # print('Focus is selected......')
                    val7.get()  # delete(0, 'end')
                    val8.get()
                # -----------------------------------------------[End of function Tom Preston]
                # Display values on user screen mat -------------[2]
                val5A["text"] = round(xBarMb, 3)
                val6A["text"] = round(sBarMb, 3)
                val7A["text"] = round(xUSLb, 3)
                val8A["text"] = round(xLSLb, 3)

            # ------------------------------------------------------[Line 3]
            if ttxUCL2.get() and ttxLCL2.get():
                xBarMc = float(ttxLCL2.get()) + ((float(ttxUCL2.get()) - float(ttxLCL2.get())) / 2)
                sUCLc, sLCLc, sBarMc = loadConst(float(ttxUCL2.get()), xBarMc, gSize)  # Compute S-Chart Mean
                xUSLc = xBarMc + (float(ttxUCL2.get()) - xBarMc) / 3 * 6
                xLSLc = xBarMc - (xBarMc - float(ttxLCL2.get())) / 3 * 6

                # print('Tape Temp (22mm): xMean/xUSL/xLSL:', xBarMc, xUSLc, xLSLc)
                # Archiving values into dynamic List
                testVarTTc = (dt_string, '22mm', ttxUCL2.get(), ttxLCL2.get(), ttsUCL2.get(), ttsLCL2.get(), round(xBarMc, 3),
                              round(sBarMc, 3), round(xUSLc, 3), round(xLSLc, 3), '3-40')
                # print('TT Historical:', testVarTTc)

                # -------------------------------------------------------[for Tom Preston]
                def click(event):
                    cSelect = 1
                    cSelectVar.append(cSelect)
                    # print('Focus is selected......', cSelect)
                    val11.config(state=NORMAL)
                    val11.delete(0, END)
                    val12.config(state=NORMAL)
                    val12.delete(0, END)
                    # allow new manual entry ----
                    val11.get()
                    val12.get()

                val11.bind('<Button-1>', click)

                # copy calculated values into user entry and allow edit--
                if not cSelectVar:
                    # print('Focus is NOT selected...')
                    # val3.insert(0, round(sUCLa, 3))   # Allow static values
                    ttsUCL2.set(round(sUCLc, 3))  # allow dynamic updated values
                    val11.config(state='readonly')
                    ttsLCL2.set(round(sLCLc, 3))
                    val12.config(state='readonly')

                else:
                    # print('Focus is selected......')
                    val11.get()  # delete(0, 'end')
                    val12.get()
                # -----------------------------------------------[End of function Tom Preston]
                # Display values on user screen mat ----------------[2]
                val9A["text"] = round(xBarMc, 3)
                valA0["text"] = round(sBarMc, 3)
                valA1["text"] = round(xUSLc, 3)
                valA2["text"] = round(xLSLc, 3)

            # ------------------------------------------------------[Line 4]
            if ttxUCL3.get() and ttxLCL3.get():
                xBarMd = float(ttxLCL3.get()) + ((float(ttxUCL3.get()) - float(ttxLCL3.get())) / 2)
                sUCLd, sLCLd, sBarMd = loadConst(float(ttxUCL3.get()), xBarMd, gSize)  # Compute S-Chart Mean
                xUSLd = xBarMd + (float(ttxUCL3.get()) - xBarMd) / 3 * 6
                xLSLd = xBarMd - (xBarMd - float(ttxLCL3.get())) / 3 * 6

                # print('Tape Temp (18mm): xMean/xUSL/xLSL:', xBarMd, xUSLd, xLSLd)
                # Archiving values into dynamic List
                testVarTTd = (dt_string, '18mm', ttxUCL3.get(), ttxLCL3.get(), ttsUCL3.get(), ttsLCL3.get(), round(xBarMd, 3),
                              round(sBarMd, 3), round(xUSLd, 3), round(xLSLd, 3), '41')
                # print('TT Historical:', testVarTTd)

                # -------------------------------------------------------[for Tom Preston]
                def click(event):
                    cSelect = 1
                    cSelectVar.append(cSelect)
                    # print('Focus is selected......', cSelect)
                    val15.config(state=NORMAL)
                    val15.delete(0, END)
                    val16.config(state=NORMAL)
                    val16.delete(0, END)
                    # allow new manual entry ----
                    val15.get()
                    val16.get()

                val15.bind('<Button-1>', click)

                # copy calculated values into user entry and allow edit--
                if not cSelectVar:
                    # print('Focus is NOT selected...')
                    # val3.insert(0, round(sUCLa, 3))   # Allow static values
                    ttsUCL3.set(round(sUCLd, 3))  # allow dynamic updated values
                    val15.config(state='readonly')
                    ttsLCL3.set(round(sLCLd, 3))
                    val16.config(state='readonly')

                else:
                    # print('Focus is selected......')
                    val15.get()  # delete(0, 'end')
                    val16.get()
                # -----------------------------------------------[End of function Tom Preston]
                # Display values on user screen mat ----------------[2]
                valA3["text"] = round(xBarMd, 3)
                valA4["text"] = round(sBarMd, 3)
                valA5["text"] = round(xUSLd, 3)
                valA6["text"] = round(xLSLd, 3)

            # ------------------------------------------------------[Line 5]
            if ttxUCL4.get() and ttxLCL4.get():
                xBarMe = float(ttxLCL4.get()) + ((float(ttxUCL4.get()) - float(ttxLCL4.get())) / 2)
                sUCLe, sLCLe, sBarMe = loadConst(float(ttxUCL4.get()), xBarMe, gSize)  # Compute S-Chart Mean
                xUSLe = xBarMe + (float(ttxUCL4.get()) - xBarMe) / 3 * 6
                xLSLe = xBarMe - (xBarMe - float(ttxLCL4.get())) / 3 * 6

                # print('Tape Temp (18mm): xMean/xUSL/xLSL:', xBarMe, xUSLe, xLSLe)
                # Archiving values into dynamic List
                testVarTTe = (dt_string, '18mm', ttxUCL4.get(), ttxLCL4.get(), ttsUCL4.get(), ttsLCL4.get(), round(xBarMe, 3),
                              round(sBarMe, 3), round(xUSLe, 3), round(xLSLe, 3), '42+')
                # print('TT Historical:', testVarTTe)

                # -------------------------------------------------------[for Tom Preston]
                def click(event):
                    cSelect = 1
                    cSelectVar.append(cSelect)
                    # print('Focus is selected......', cSelect)
                    val19.config(state=NORMAL)
                    val19.delete(0, END)
                    val20.config(state=NORMAL)
                    val20.delete(0, END)
                    # allow new manual entry ----
                    val19.get()
                    val20.get()

                val19.bind('<Button-1>', click)

                # copy calculated values into user entry and allow edit--
                if not cSelectVar:
                    # print('Focus is NOT selected...')
                    # val3.insert(0, round(sUCLa, 3))   # Allow static values
                    ttsUCL4.set(round(sUCLe, 3))  # allow dynamic updated values
                    val19.config(state='readonly')
                    ttsLCL4.set(round(sLCLe, 3))
                    val20.config(state='readonly')

                else:
                    # print('Focus is selected......')
                    val19.get()  # delete(0, 'end')
                    val20.get()
                # -----------------------------------------------[End of function Tom Preston]
                # Display values on user screen mat ----------------[2]
                valA7["text"] = round(xBarMe, 3)
                valA8["text"] = round(sBarMe, 3)
                valA9["text"] = round(xUSLe, 3)
                valB0["text"] = round(xLSLe, 3)

        except ValueError:
            errorEntry()  # call error alert on entry errors

    # clear the content and allow entry of historical limits -------[]
    # TODO -------------[LOAD METRICS FROM ENCRYPTED FILE]

    # changeable state ----------------------------------------------#
    pState = 'normal'

    # -----------[Compute stats UCL/LCL] -----------[ Laser Power]
    val1 = Entry(pop, width=8, state=pState, textvariable=ttxUCL)
    val1.place(x=70, y=80)
    val2 = Entry(pop, width=8, state=pState, textvariable=ttxLCL)
    val2.place(x=130, y=80)
    # ----------------------
    val3 = Entry(pop, width=8, state=pState, textvariable=ttsUCL)
    val3.place(x=190, y=80)
    val4 = Entry(pop, width=8, state=pState, textvariable=ttsLCL)
    val4.place(x=250, y=80)

    # --------------------------------------[ Lin/Row Two]
    val5 = Entry(pop, width=8, state=pState, textvariable=ttxUCL1)
    val5.place(x=70, y=102)
    val6 = Entry(pop, width=8, state=pState, textvariable=ttxLCL1)
    val6.place(x=130, y=102)
    # -------------------------
    val7 = Entry(pop, width=8, state=pState, textvariable=ttsUCL1)
    val7.place(x=190, y=102)
    val8 = Entry(pop, width=8, state=pState, textvariable=ttsLCL1)
    val8.place(x=250, y=102)
    # --------------------------------------[ Line Three]
    val9 = Entry(pop, width=8, textvariable=ttxUCL2, state=pState)
    val9.place(x=70, y=124)
    val10 = Entry(pop, width=8, textvariable=ttxLCL2, state=pState)
    val10.place(x=130, y=124)
    val11 = Entry(pop, width=8, textvariable=ttsUCL2, state=pState)  # Upper Control Limit
    val11.place(x=190, y=124)
    val12 = Entry(pop, width=8, textvariable=ttsLCL2, state=pState)  # Lower control limit
    val12.place(x=250, y=124)
    # ----------------------------------------[Line Four ]
    val13 = Entry(pop, width=8, textvariable=ttxUCL3, state=pState)
    val13.place(x=70, y=146)
    val14 = Entry(pop, width=8, textvariable=ttxLCL3, state=pState)
    val14.place(x=130, y=146)
    val15 = Entry(pop, width=8, textvariable=ttsUCL3, state=pState)  # Upper Control Limit
    val15.place(x=190, y=146)
    val16 = Entry(pop, width=8, textvariable=ttsLCL3, state=pState)  # Lower control limit
    val16.place(x=250, y=146)
    # ---------------------------------------[Line Five]
    val17 = Entry(pop, width=8, textvariable=ttxUCL4, state=pState)
    val17.place(x=70, y=168)
    val18 = Entry(pop, width=8, textvariable=ttxLCL4, state=pState)
    val18.place(x=130, y=168)
    val19 = Entry(pop, width=8, textvariable=ttsUCL4, state=pState)  # Upper Control Limit
    val19.place(x=190, y=168)
    val20 = Entry(pop, width=8, textvariable=ttsLCL4, state=pState)  # Lower control limit
    val20.place(x=250, y=168)
    # ------------------------------------------------------------------[]
    val25 = Entry(pop, width=4, state='normal', textvariable=sReg, bg='yellow', bd=4)
    val25.place(x=105, y=200)
    sReg.set('40dp')
    # ------------------------------------------------------------------[]
    val26 = Entry(pop, width=4, state='normal', textvariable=pReg, bg='green2', bd=4)
    val26.place(x=245, y=200)
    pReg.set('04dp')
    # Binder Label --------------------------------------------------------#
    # Compute derived mean values for XBar/Sbar Plot & fill dynamically ---- [Trim values = x - 2]
    val1A = Label(pop, width=7, state='normal', font=("bold", 10))
    val1A.place(x=308, y=80)
    val2A = Label(pop, width=7, state='normal', font=("bold", 10))
    val2A.place(x=368, y=80)
    # --------------------
    val3A = Label(pop, width=7, state='normal', font=("bold", 10))
    val3A.place(x=428, y=80)
    val4A = Label(pop, width=7, state='normal', font=("bold", 10))
    val4A.place(x=488, y=80)
    # ------------------------------------ Line 2
    val5A = Label(pop, width=7, state='normal', font=("bold", 10))
    val5A.place(x=308, y=102)
    val6A = Label(pop, width=7, state='normal', font=("bold", 10))
    val6A.place(x=368, y=102)
    # ------------------------
    val7A = Label(pop, width=7, state='normal', font=("bold", 10))
    val7A.place(x=428, y=102)
    val8A = Label(pop, width=7, state='normal', font=("bold", 10))
    val8A.place(x=488, y=102)
    # --------------------------------------Line 3
    val9A = Label(pop, width=7, state="normal", font=("bold", 10))  # xMean Centre line
    val9A.place(x=308, y=124)
    valA0 = Label(pop, width=7, state="normal", font=("bold", 10))  # sMean Centre line
    valA0.place(x=368, y=124)
    valA1 = Label(pop, width=7, state="normal", font=("bold", 10))  # Upper Set Limit
    valA1.place(x=428, y=124)
    valA2 = Label(pop, width=7, state="normal", font=("bold", 10))  # Lower Set Limit
    valA2.place(x=488, y=124)
    # --------------------------------------Line 4
    valA3 = Label(pop, width=7, state="normal", font=("bold", 10))  # xMean Centre line
    valA3.place(x=308, y=146)
    valA4 = Label(pop, width=7, state="normal", font=("bold", 10))  # sMean Centre line
    valA4.place(x=368, y=146)
    valA5 = Label(pop, width=7, state="normal", font=("bold", 10))  # Upper Set Limit
    valA5.place(x=428, y=146)
    valA6 = Label(pop, width=7, state="normal", font=("bold", 10))  # Lower Set Limit
    valA6.place(x=480, y=146)
    # --------------------------------------Line 5
    valA7 = Label(pop, width=7, state="normal", font=("bold", 10))  # xMean Centre line
    valA7.place(x=308, y=168)
    valA8 = Label(pop, width=7, state="normal", font=("bold", 10))  # sMean Centre line
    valA8.place(x=368, y=168)
    valA9 = Label(pop, width=7, state="normal", font=("bold", 10))  # Upper Set Limit
    valA9.place(x=428, y=168)
    valB0 = Label(pop, width=7, state="normal", font=("bold", 10))  # Lower Set Limit
    valB0.place(x=480, y=168)

    # ------------------ Binding properties ----------------------[]
    val1.bind("<KeyRelease>", calculation)
    val2.bind("<KeyRelease>", calculation)
    val3.bind("<KeyRelease>", calculation)
    val4.bind("<KeyRelease>", calculation)
    # ----- Line Row 2
    val5.bind("<KeyRelease>", calculation)
    val6.bind("<KeyRelease>", calculation)
    val7.bind("<KeyRelease>", calculation)
    val8.bind("<KeyRelease>", calculation)
    # ----- Line Row 3
    val9.bind("<KeyRelease>", calculation)
    val10.bind("<KeyRelease>", calculation)
    val11.bind("<KeyRelease>", calculation)
    val12.bind("<KeyRelease>", calculation)
    # ----- Line Row 4
    val13.bind("<KeyRelease>", calculation)
    val14.bind("<KeyRelease>", calculation)
    val15.bind("<KeyRelease>", calculation)
    val16.bind("<KeyRelease>", calculation)
    # ----- Line Row 5
    val17.bind("<KeyRelease>", calculation)
    val18.bind("<KeyRelease>", calculation)
    val19.bind("<KeyRelease>", calculation)
    val20.bind("<KeyRelease>", calculation)
    # repopulate with default values

    return processID


def qpHLst(pop, gSize, xUCL, xLCL, sUCL, sLCL, xUCL1, xLCL1,  sUCL1, sLCL1, xUCL2, xLCL2,  sUCL2, sLCL2, xUCL3, xLCL3,  sUCL3, sLCL3, xUCL4, xLCL4, sUCL4, sLCL4, WONID):
    global processID, val1, val2, val3, val4, val5, val6, val7, val8, val9, val10, val11, val12, val13, \
        val14, val15, val16, val17, val18, val19, val20, val25, val26

    processID = WONID
    # ------------------
    sReg, pReg = StringVar(pop), StringVar(pop)

    # Function performs dynamic calculations ---[]
    def calculation(event=None):
        global testVarSTa, testVarSTb, testVarSTc, testVarSTd, testVarSTe

        try:
            # Compute XBar mean / center line ----------------------[Line1]
            if xUCL.get() and xLCL.get():
                xBarMa = float(xLCL.get()) + ((float(xUCL.get()) - float(xLCL.get())) / 2)
                sUCLa, sLCLa, sBarMa = loadConst(float(xUCL.get()), xBarMa, gSize)  # Compute S-Chart Mean
                xUSLa = xBarMa + (float(xUCL.get()) - xBarMa) / 3 * 6
                xLSLa = xBarMa - (xBarMa - float(xLCL.get())) / 3 * 6

                print('\nSubstrate Temp (22mm): xMean/xUSL/xLSL:', xBarMa, xUSLa, xLSLa)
                # Archiving values into dynamic List
                testVarSTa = (dt_string, '22mm', xUCL.get(), xLCL.get(), sUCL.get(), sLCL.get(), round(xBarMa, 3),
                              round(sBarMa, 3), round(xUSLa, 3), round(xLSLa, 3), '1')
                # print('ST Historical:', testVarSTa)

                # -------------------------------------------------------[for Tom Preston]
                def click(event):
                    cSelect = 1
                    cSelectVar.append(cSelect)
                    # print('Focus is selected......', cSelect)
                    val3.config(state=NORMAL)
                    val3.delete(0, END)
                    val4.config(state=NORMAL)
                    val4.delete(0, END)
                    # allow new manual entry ----
                    val3.get()
                    val4.get()

                val3.bind('<Button-1>', click)

                # copy calculated values into user entry and allow edit--
                if not cSelectVar:
                    # print('Focus is NOT selected...')
                    # val3.insert(0, round(sUCLa, 3))   # Allow static values
                    sUCL.set(round(sUCLa, 3))  # allow dynamic updated values
                    val3.config(state='readonly')
                    sLCL.set(round(sLCLa, 3))
                    val4.config(state='readonly')

                else:
                    # print('Focus is selected......')
                    val3.get()  # delete(0, 'end')
                    val4.get()
                # -----------------------------------------------[End of function Tom Preston]

                # Display values on user screen mat -----------[1]
                val1A["text"] = round(xBarMa, 3)
                val2A["text"] = round(sBarMa, 3)
                val3A["text"] = round(xUSLa, 3)
                val4A["text"] = round(xLSLa, 3)

            # ------------------------------------------------------[Line 2]
            if xUCL1.get() and xLCL1.get():
                xBarMb = float(xLCL1.get()) + ((float(xUCL1.get()) - float(xLCL1.get())) / 2)
                sUCLb, sLCLb, sBarMb = loadConst(float(xUCL1.get()), xBarMb, gSize)  # Compute S-Chart Mean
                xUSLb = xBarMb + (float(xUCL1.get()) - xBarMb) / 3 * 6
                xLSLb = xBarMb - (xBarMb - float(xLCL1.get())) / 3 * 6

                # print('Substrate Temp (22mm): xMean/xUSL/xLSL:', xBarMb, xUSLb, xLSLb)
                # Archiving values into dynamic List
                testVarSTb = (dt_string, '22mm', xUCL1.get(), xLCL1.get(), sUCL1.get(), sLCL1.get(), round(xBarMb, 3),
                              round(sBarMb, 3), round(xUSLb, 3), round(xLSLb, 3), '2')
                # print('ST Historical:', testVarSTb)

                # -------------------------------------------------------[for Tom Preston]
                def click(event):
                    cSelect = 1
                    cSelectVar.append(cSelect)
                    # print('Focus is selected......', cSelect)
                    val7.config(state=NORMAL)
                    val7.delete(0, END)
                    val8.config(state=NORMAL)
                    val8.delete(0, END)
                    # allow new manual entry ----
                    val7.get()
                    val8.get()

                val7.bind('<Button-1>', click)

                # copy calculated values into user entry and allow edit--
                if not cSelectVar:
                    # print('Focus is NOT selected...')
                    # val3.insert(0, round(sUCLa, 3))   # Allow static values
                    sUCL1.set(round(sUCLb, 3))  # allow dynamic updated values
                    val7.config(state='readonly')
                    sLCL1.set(round(sLCLb, 3))
                    val8.config(state='readonly')

                else:
                    # print('Focus is selected......')
                    val7.get()  # delete(0, 'end')
                    val8.get()
                # -----------------------------------------------[End of function Tom Preston]

                # Display values on user screen mat ------------[2]
                val5A["text"] = round(xBarMb, 3)
                val6A["text"] = round(sBarMb, 3)
                val7A["text"] = round(xUSLb, 3)
                val8A["text"] = round(xLSLb, 3)

            # ------------------------------------------------------[Line 3]
            if xUCL2.get() and xLCL2.get():
                xBarMc = float(xLCL2.get()) + ((float(xUCL2.get()) - float(xLCL2.get())) / 2)
                sUCLc, sLCLc, sBarMc = loadConst(float(xUCL2.get()), xBarMc, gSize)  # Compute S-Chart Mean
                xUSLc = xBarMc + (float(xUCL2.get()) - xBarMc) / 3 * 6
                xLSLc = xBarMc - (xBarMc - float(xLCL2.get())) / 3 * 6

                # print('Substrate Temp (22mm): xMean/xUSL/xLSL:', xBarMc, xUSLc, xLSLc)
                # Archiving values into dynamic List
                testVarSTc = (dt_string, '22mm', xUCL2.get(), xLCL2.get(), sUCL2.get(), sLCL2.get(), round(xBarMc, 3),
                              round(sBarMc, 3), round(xUSLc, 3), round(xLSLc, 3), '3-40')
                # print('ST Historical:', testVarSTc)

                # -------------------------------------------------------[for Tom Preston]
                def click(event):
                    cSelect = 1
                    cSelectVar.append(cSelect)
                    # print('Focus is selected......', cSelect)
                    val11.config(state=NORMAL)
                    val11.delete(0, END)
                    val12.config(state=NORMAL)
                    val12.delete(0, END)
                    # allow new manual entry ----
                    val11.get()
                    val12.get()

                val11.bind('<Button-1>', click)

                # copy calculated values into user entry and allow edit--
                if not cSelectVar:
                    # print('Focus is NOT selected...')
                    # val3.insert(0, round(sUCLa, 3))   # Allow static values
                    sUCL2.set(round(sUCLc, 3))  # allow dynamic updated values
                    val11.config(state='readonly')
                    sLCL2.set(round(sLCLc, 3))
                    val12.config(state='readonly')

                else:
                    # print('Focus is selected......')
                    val11.get()  # delete(0, 'end')
                    val12.get()
                # -----------------------------------------------[End of function Tom Preston]
                # Display values on user screen mat ----------------[2]
                val9A["text"] = round(xBarMc, 3)
                valA0["text"] = round(sBarMc, 3)
                valA1["text"] = round(xUSLc, 3)
                valA2["text"] = round(xLSLc, 3)

            # ------------------------------------------------------[Line 4]
            if xUCL3.get() and xLCL3.get():
                xBarMd = float(xLCL3.get()) + ((float(xUCL3.get()) - float(xLCL3.get())) / 2)
                sUCLd, sLCLd, sBarMd = loadConst(float(xUCL3.get()), xBarMd, gSize)  # Compute S-Chart Mean
                xUSLd = xBarMd + (float(xUCL3.get()) - xBarMd) / 3 * 6
                xLSLd = xBarMd - (xBarMd - float(xLCL3.get())) / 3 * 6

                print('Substrate Temp (18mm): xMean/xUSL/xLSL:', xBarMd, xUSLd, xLSLd)
                # Archiving values into dynamic List
                testVarSTd = (dt_string, '18mm', xUCL3.get(), xLCL3.get(), sUCL3.get(), sLCL3.get(), round(xBarMd, 3),
                              round(sBarMd, 3), round(xUSLd, 3), round(xLSLd, 3), '41')
                # print('ST Historical:', testVarSTd)

                # -------------------------------------------------------[for Tom Preston]
                def click(event):
                    cSelect = 1
                    cSelectVar.append(cSelect)
                    # print('Focus is selected......', cSelect)
                    val15.config(state=NORMAL)
                    val15.delete(0, END)
                    val16.config(state=NORMAL)
                    val16.delete(0, END)
                    # allow new manual entry ----
                    val15.get()
                    val16.get()

                val15.bind('<Button-1>', click)

                # copy calculated values into user entry and allow edit--
                if not cSelectVar:
                    # print('Focus is NOT selected...')
                    # val3.insert(0, round(sUCLa, 3))   # Allow static values
                    sUCL3.set(round(sUCLd, 3))  # allow dynamic updated values
                    val15.config(state='readonly')
                    sLCL3.set(round(sLCLd, 3))
                    val16.config(state='readonly')

                else:
                    # print('Focus is selected......')
                    val15.get()  # delete(0, 'end')
                    val16.get()
                # -----------------------------------------------[End of function Tom Preston]

                # Display values on user screen mat ----------------[2]
                valA3["text"] = round(xBarMd, 3)
                valA4["text"] = round(sBarMd, 3)
                valA5["text"] = round(xUSLd, 3)
                valA6["text"] = round(xLSLd, 3)

            # ------------------------------------------------------[Line 5]
            if xUCL4.get() and xLCL4.get():
                xBarMe = float(xLCL4.get()) + ((float(xUCL4.get()) - float(xLCL4.get())) / 2)
                sUCLe, sLCLe, sBarMe = loadConst(float(xUCL4.get()), xBarMe, gSize)  # Compute S-Chart Mean
                xUSLe = xBarMe + (float(xUCL4.get()) - xBarMe) / 3 * 6
                xLSLe = xBarMe - (xBarMe - float(xLCL4.get())) / 3 * 6

                # print('Substrate Temp (18mm): xMean/xUSL/xLSL:', xBarMe, xUSLe, xLSLe)
                # Archiving values into dynamic List
                testVarSTe = (dt_string, '18mm', xUCL4.get(), xLCL4.get(), sUCL4.get(), sLCL4.get(), round(xBarMe, 3),
                              round(sBarMe, 3), round(xUSLe, 3), round(xLSLe, 3), '42+')
                # print('ST Historical:', testVarSTe)

                # -------------------------------------------------------[for Tom Preston]
                def click(event):
                    cSelect = 1
                    cSelectVar.append(cSelect)
                    print('Focus is selected......', cSelect)
                    val19.config(state=NORMAL)
                    val19.delete(0, END)
                    val20.config(state=NORMAL)
                    val20.delete(0, END)
                    # allow new manual entry ----
                    val19.get()
                    val20.get()

                val19.bind('<Button-1>', click)

                # copy calculated values into user entry and allow edit--
                if not cSelectVar:
                    # print('Focus is NOT selected...')
                    # val3.insert(0, round(sUCLa, 3))   # Allow static values
                    sUCL4.set(round(sUCLe, 3))  # allow dynamic updated values
                    val19.config(state='readonly')
                    sLCL4.set(round(sLCLe, 3))
                    val20.config(state='readonly')

                else:
                    # print('Focus is selected......')
                    val19.get()  # delete(0, 'end')
                    val20.get()
                # -----------------------------------------------[End of function Tom Preston]
                # Display values on user screen mat -------------[2]
                valA7["text"] = round(xBarMe, 3)
                valA8["text"] = round(sBarMe, 3)
                valA9["text"] = round(xUSLe, 3)
                valB0["text"] = round(xLSLe, 3)

        except ValueError:
            errorEntry()                                            # call error alert on entry errors

    # clear the content and allow entry of historical limits -------[]
    # TODO -------------[LOAD METRICS FROM ENCRYPTED FILE]

    # changeable state ----------------------------------------------#
    pState = 'normal'

    # -----------[Compute stats UCL/LCL] -----------[ Laser Power]
    val1 = Entry(pop, width=8, state=pState, textvariable=xUCL)
    val1.place(x=70, y=80)
    val2 = Entry(pop, width=8, state=pState, textvariable=xLCL)
    val2.place(x=130, y=80)
    # ----------------------
    val3 = Entry(pop, width=8, state=pState, textvariable=sUCL)
    val3.place(x=190, y=80)
    val4 = Entry(pop, width=8, state=pState, textvariable=sLCL)
    val4.place(x=250, y=80)

    # --------------------------------------[ Lin/Row Two]
    val5 = Entry(pop, width=8, state=pState, textvariable=xUCL1)
    val5.place(x=70, y=102)
    val6 = Entry(pop, width=8, state=pState, textvariable=xLCL1)
    val6.place(x=130, y=102)
    # -------------------------
    val7 = Entry(pop, width=8, state=pState, textvariable=sUCL1)
    val7.place(x=190, y=102)
    val8 = Entry(pop, width=8, state=pState, textvariable=sLCL1)
    val8.place(x=250, y=102)
    # --------------------------------------[ Line Three]
    val9 = Entry(pop, width=8, textvariable=xUCL2, state=pState)
    val9.place(x=70, y=124)
    val10 = Entry(pop, width=8, textvariable=xLCL2, state=pState)
    val10.place(x=130, y=124)
    val11 = Entry(pop, width=8, textvariable=sUCL2, state=pState)  # Upper Control Limit
    val11.place(x=190, y=124)
    val12 = Entry(pop, width=8, textvariable=sLCL2, state=pState)  # Lower control limit
    val12.place(x=250, y=124)
    # ----------------------------------------[Line Four ]
    val13 = Entry(pop, width=8, textvariable=xUCL3, state=pState)
    val13.place(x=70, y=146)
    val14 = Entry(pop, width=8, textvariable=xLCL3, state=pState)
    val14.place(x=130, y=146)
    val15 = Entry(pop, width=8, textvariable=sUCL3, state=pState)  # Upper Control Limit
    val15.place(x=190, y=146)
    val16 = Entry(pop, width=8, textvariable=sLCL3, state=pState)  # Lower control limit
    val16.place(x=250, y=146)
    # ---------------------------------------[Line Five]
    val17 = Entry(pop, width=8, textvariable=xUCL4, state=pState)
    val17.place(x=70, y=168)
    val18 = Entry(pop, width=8, textvariable=xLCL4, state=pState)
    val18.place(x=130, y=168)
    val19 = Entry(pop, width=8, textvariable=sUCL4, state=pState)  # Upper Control Limit
    val19.place(x=190, y=168)
    val20 = Entry(pop, width=8, textvariable=sLCL4, state=pState)  # Lower control limit
    val20.place(x=250, y=168)
    # ------------------------------------------------------------------[]
    val25 = Entry(pop, width=4, state='normal', textvariable=sReg, bg='yellow', bd=4)
    val25.place(x=105, y=200)
    sReg.set('40dp')
    # ------------------------------------------------------------------[]
    val26 = Entry(pop, width=4, state='normal', textvariable=pReg, bg='green2', bd=4)
    val26.place(x=245, y=200)
    pReg.set('04dp')
    # Binder Label --------------------------------------------------------#
    # Compute derived mean values for XBar/Sbar Plot & fill dynamically ---- [Trim values = x - 2]
    val1A = Label(pop, width=7, state='normal', font=("bold", 10))
    val1A.place(x=308, y=80)
    val2A = Label(pop, width=7, state='normal', font=("bold", 10))
    val2A.place(x=368, y=80)
    # --------------------
    val3A = Label(pop, width=7, state='normal', font=("bold", 10))
    val3A.place(x=428, y=80)
    val4A = Label(pop, width=7, state='normal', font=("bold", 10))
    val4A.place(x=488, y=80)
    # ------------------------------------ Line 2
    val5A = Label(pop, width=7, state='normal', font=("bold", 10))
    val5A.place(x=308, y=102)
    val6A = Label(pop, width=7, state='normal', font=("bold", 10))
    val6A.place(x=368, y=102)
    # ------------------------
    val7A = Label(pop, width=7, state='normal', font=("bold", 10))
    val7A.place(x=428, y=102)
    val8A = Label(pop, width=7, state='normal', font=("bold", 10))
    val8A.place(x=488, y=102)
    # --------------------------------------Line 3
    val9A = Label(pop, width=7, state="normal", font=("bold", 10))  # xMean Centre line
    val9A.place(x=308, y=124)
    valA0 = Label(pop, width=7, state="normal", font=("bold", 10))  # sMean Centre line
    valA0.place(x=368, y=124)
    valA1 = Label(pop, width=7, state="normal", font=("bold", 10))  # Upper Set Limit
    valA1.place(x=428, y=124)
    valA2 = Label(pop, width=7, state="normal", font=("bold", 10))  # Lower Set Limit
    valA2.place(x=488, y=124)
    # --------------------------------------Line 4
    valA3 = Label(pop, width=7, state="normal", font=("bold", 10))  # xMean Centre line
    valA3.place(x=308, y=146)
    valA4 = Label(pop, width=7, state="normal", font=("bold", 10))  # sMean Centre line
    valA4.place(x=368, y=146)
    valA5 = Label(pop, width=7, state="normal", font=("bold", 10))  # Upper Set Limit
    valA5.place(x=428, y=146)
    valA6 = Label(pop, width=7, state="normal", font=("bold", 10))  # Lower Set Limit
    valA6.place(x=480, y=146)
    # --------------------------------------Line 5
    valA7 = Label(pop, width=7, state="normal", font=("bold", 10))  # xMean Centre line
    valA7.place(x=308, y=168)
    valA8 = Label(pop, width=7, state="normal", font=("bold", 10))  # sMean Centre line
    valA8.place(x=368, y=168)
    valA9 = Label(pop, width=7, state="normal", font=("bold", 10))  # Upper Set Limit
    valA9.place(x=428, y=168)
    valB0 = Label(pop, width=7, state="normal", font=("bold", 10))  # Lower Set Limit
    valB0.place(x=480, y=168)

    # ------------------ Binding properties ----------------------[]
    val1.bind("<KeyRelease>", calculation)
    val2.bind("<KeyRelease>", calculation)
    val3.bind("<KeyRelease>", calculation)
    val4.bind("<KeyRelease>", calculation)
    # ----- Line Row 2
    val5.bind("<KeyRelease>", calculation)
    val6.bind("<KeyRelease>", calculation)
    val7.bind("<KeyRelease>", calculation)
    val8.bind("<KeyRelease>", calculation)
    # ----- Line Row 3
    val9.bind("<KeyRelease>", calculation)
    val10.bind("<KeyRelease>", calculation)
    val11.bind("<KeyRelease>", calculation)
    val12.bind("<KeyRelease>", calculation)
    # ----- Line Row 4
    val13.bind("<KeyRelease>", calculation)
    val14.bind("<KeyRelease>", calculation)
    val15.bind("<KeyRelease>", calculation)
    val16.bind("<KeyRelease>", calculation)
    # ----- Line Row 5
    val17.bind("<KeyRelease>", calculation)
    val18.bind("<KeyRelease>", calculation)
    val19.bind("<KeyRelease>", calculation)
    val20.bind("<KeyRelease>", calculation)
    # repopulate with default values

    return processID


def qpHLtg(pop, gSize, tgxUCL, tgxLCL, tgsUCL, tgsLCL, WONID):
    global processID, val1, val2, val3, val4, val25, val26

    processID = WONID
    # ------------------
    sReg, pReg = IntVar(pop), IntVar(pop)

    # Function performs dynamic calculations ---[]
    def calculation(event=None):
        global testVarTG

        try:
            # Compute XBar mean / center line ----------------------[LP]
            if tgxUCL.get() and tgxLCL.get():
                xBarMa = float(tgxLCL.get()) + ((float(tgxUCL.get()) - float(tgxLCL.get())) / 2)
                sUCLa, sLCLa, sBarMa = loadConst(float(tgxUCL.get()), xBarMa, gSize)  # Compute S-Chart Mean
                xUSLa = xBarMa + (float(tgxUCL.get()) - xBarMa) / 3 * 6
                xLSLa = xBarMa - (xBarMa - float(tgxLCL.get())) / 3 * 6

                # print('\nTape Speed: xMean/xUSL/xLSL:', xBarMa, xUSLa, xLSLa)
                # print('Computed sMean/sUCL/sLCL:', sBarMa, sUCLa, sLCLa)
                # Archiving values into dynamic List
                testVarTG = (dt_string, '**', tgxUCL.get(), tgxLCL.get(), tgsUCL.get(), tgsLCL.get(), round(xBarMa, 3), round(sBarMa, 3), round(xUSLa,3), round(xLSLa,3), '**')
                # print('TG Historical:', testVarTG)

                # -------------------------------------------------------[for Tom Preston]
                def click(event):
                    cSelect = 1
                    cSelectVar.append(cSelect)
                    # print('Focus is selected......', cSelect)
                    val3.config(state=NORMAL)
                    val3.delete(0, END)
                    val4.config(state=NORMAL)
                    val4.delete(0, END)
                    # allow new manual entry ----
                    val3.get()
                    val4.get()
                val3.bind('<Button-1>', click)

                # copy calculated values into user entry and allow edit--
                if not cSelectVar:
                    # print('Focus is NOT selected...')
                    # val3.insert(0, round(sUCLa, 3))       # Allow static values
                    tgsUCL.set(round(sUCLa, 3))             # allow dynamic updated values
                    val3.config(state='readonly')
                    tgsLCL.set(round(sLCLa, 3))
                    val4.config(state='readonly')

                else:
                    print('Focus is selected......')
                    val3.get()  # delete(0, 'end')
                    val4.get()
                # -----------------------[End of function Tom Preston]

                # Display values on user screen mat ----------------[1]
                val1A["text"] = round(xBarMa, 3)
                val2A["text"] = round(sBarMa, 3)
                val3A["text"] = round(xUSLa, 3)
                val4A["text"] = round(xLSLa, 3)

        except ValueError:
            errorEntry()        # call error alert on entry errors

    # clear the content and allow entry of historical limits -----------[]
    # TODO -------------[LOAD METRICS FROM ENCRYPTED FILE]

    # -----------[Compute stats UCL/LCL] -----------[ Laser Power]
    val1 = Entry(pop, width=8, state='normal', textvariable=tgxUCL)
    val1.place(x=70, y=80)
    val2 = Entry(pop, width=8, state='normal', textvariable=tgxLCL)
    val2.place(x=130, y=80)
    # ----------------------
    val3 = Entry(pop, width=8, state='normal', textvariable=tgsUCL)
    val3.place(x=190, y=80)
    val4 = Entry(pop, width=8, state='normal', textvariable=tgsLCL)
    val4.place(x=250, y=80)
    # ------------------------------------------------------------------[]
    val25 = Entry(pop, width=4, state='normal', textvariable=sReg, bg='yellow', bd=4)
    val25.place(x=105, y=200)
    sReg.set('60dp')
    # ------------------------------------------------------------------[]
    val26 = Entry(pop, width=4, state='normal', textvariable=pReg, bg='green2', bd=4)
    val26.place(x=245, y=200)
    pReg.set('06dp')

    # Binder Label --------------------------------------------------------#
    # Compute derived mean values for XBar/Sbar Plot & fill dynamically ----
    val1A = Label(pop, width=7, state='normal', font=("bold", 10))
    val1A.place(x=308, y=80)
    val2A = Label(pop, width=7, state='normal', font=("bold", 10))
    val2A.place(x=368, y=80)
    # --------------------
    val3A = Label(pop, width=7, state='normal', font=("bold", 10))
    val3A.place(x=428, y=80)
    val4A = Label(pop, width=7, state='normal', font=("bold", 10))
    val4A.place(x=488, y=80)

    # ------------------ Binding properties ----------------------[]
    val1.bind("<KeyRelease>", calculation)
    val2.bind("<KeyRelease>", calculation)
    val3.bind("<KeyRelease>", calculation)
    val4.bind("<KeyRelease>", calculation)
    # -------

    return processID
# -----------------------------------------------------------------------------[]


def saveMetricsQP(processID, WON, sSize, gType, enHL, enAL, enFO):

    # ------------------------------[]
    if processID == "TT":
        ttA = testVarTTa
        ttB = testVarTTb
        ttC = testVarTTc
        ttD = testVarTTd
        ttE = testVarTTe
        # --------------- set rows data to readonly i.e. lock down before save
        canvasBlank = [val1, val2, val3, val4, val5, val6, val7, val8, val9, val10,
                       val11, val12, val13, val14, val15, val16, val17, val18, val19, val20]

        for line in canvasBlank:
            line.config(state="readonly")
        # ------------------------ Codefy ----------------[]
        try:
            # print("Attempting to encrypt config values...")
            encryptMetricsQP(WON, processID, sSize, gType, val25.get(), val26.get(), enHL, enAL, enFO, ttA, ttB, ttC, ttD, ttE)

        except ValueError:
            print(processID + ' - Error: Encryption utility encounters error!')
            errorNote()             # response to save button when entry field is empty

    elif processID == "ST":
        stA = testVarSTa
        stB = testVarSTb
        stC = testVarSTc
        stD = testVarSTd
        stE = testVarSTe
        # --------------- set rows data to readonly then save
        canvasBlank = [val1, val2, val3, val4, val5,
                       val6, val7, val8, val9, val10,
                       val11, val12, val13, val14, val15,
                       val16, val17, val18, val19, val20]

        for line in canvasBlank:
            line.config(state="readonly")

        # ------------------------ Codefy ----------------[]
        try:
            print("Attempting to encrypt config values...")
            encryptMetricsQP(WON, processID, sSize, gType, val25.get(), val26.get(), enHL, enAL, enFO, stA, stB, stC, stD, stE)

        except ValueError:
            print(processID + ' - Error: Encryption utility encounters error!')
            errorNote()             # response to save button when entry field is empty

    elif processID == "TG":
        tgA = testVarTG
        tgB = ""
        tgC = ""
        tgD = ""
        tgE = ""
        # --------------- set rows data to readonly then save
        canvasBlank = [val1, val2, val3, val4]
        for line in canvasBlank:
            line.config(state="readonly")

        # ------------------------ Codefy ----------------[]

        try:
            print("\nActivating the encryption utility")
            encryptMetricsQP(WON, processID, sSize, gType, val25.get(), val26.get(), enHL, enAL, enFO, tgA, tgB, tgC, tgD, tgE)

        except ValueError:
            print(processID + ' - Error: Encryption utility encounters error!')
            errorNote()             # response to save button when entry field is empty

    else:
        pass

    return


def encryptMetricsQP(WON, processID, sSize, gType, sCyc, pCyc, enDNV, enMGM, enAUT, lineA, lineB, lineC, lineD, lineE):
    WONID = WON
    # objective of cryptography is to provide basic security concepts in data exchange & integrity
    # initialise object instance ---

    # Check variables----- []
    # print('Write Output:', processID, '\n', lineA, "\n", lineB, "\n", lineC, "\n", lineD, "\n", lineE)

    # validate calling process before saving into file -----------------------------------------------
    if processID == 'TG':
        tgA = onetimepad.encrypt(str(sSize), 'random')
        tgB = onetimepad.encrypt(str(gType), 'random')
        tgK = onetimepad.encrypt(str(sCyc), 'random')
        tgP = onetimepad.encrypt(str(pCyc), 'random')
        tgC = onetimepad.encrypt(str(enDNV), 'random')
        tgD = onetimepad.encrypt(str(enMGM), 'random')
        tgE = onetimepad.encrypt(str(enAUT), 'random')
        tgF = onetimepad.encrypt(str(lineA), 'random')
        tgG = 0  # Do nothing -- Can be used for future scalability
        tgH = 0
        tgI = 0
        tgJ = 0

    elif processID == 'TT':
        ttA = onetimepad.encrypt(str(sSize), 'random')
        ttB = onetimepad.encrypt(str(gType), 'random')
        ttK = onetimepad.encrypt(str(sCyc), 'random')
        ttP = onetimepad.encrypt(str(pCyc), 'random')
        ttC = onetimepad.encrypt(str(enDNV), 'random')
        ttD = onetimepad.encrypt(str(enMGM), 'random')
        ttE = onetimepad.encrypt(str(enAUT), 'random')
        ttF = onetimepad.encrypt(str(lineA), 'random')
        ttG = onetimepad.encrypt(str(lineB), 'random')
        ttH = onetimepad.encrypt(str(lineC), 'random')
        ttI = onetimepad.encrypt(str(lineD), 'random')
        ttJ = onetimepad.encrypt(str(lineE), 'random')

    elif processID == 'ST':
        stA = onetimepad.encrypt(str(sSize), 'random')
        stB = onetimepad.encrypt(str(gType), 'random')
        stK = onetimepad.encrypt(str(sCyc), 'random')
        stP = onetimepad.encrypt(str(pCyc), 'random')
        stC = onetimepad.encrypt(str(enDNV), 'random')
        stD = onetimepad.encrypt(str(enMGM), 'random')
        stE = onetimepad.encrypt(str(enAUT), 'random')
        stF = onetimepad.encrypt(str(lineA), 'random')
        stG = onetimepad.encrypt(str(lineB), 'random')
        stH = onetimepad.encrypt(str(lineC), 'random')
        stI = onetimepad.encrypt(str(lineD), 'random')
        stJ = onetimepad.encrypt(str(lineE), 'random')
    else:
        pass

    # Open text file and save historical details -----------#
    iniName = "hisLim"+processID+".INI"
    with open(iniName, 'a') as configfile:                                 # append to config file

        if processID == 'TG':
            if not config.has_section(processID +"HL_" + WONID):
                config.add_section(processID +"HL_" + WONID)
                config.set(processID + "HL_" + WONID, "SmpleSize", str(tgA))
                config.set(processID + "HL_" + WONID, "GroupType", str(tgB))
                config.set(processID + "HL_" + WONID, "SEOLSpace", str(tgK))
                config.set(processID + "HL_" + WONID, "SEOPSpace", str(tgP))
                config.set(processID + "HL_" + WONID, "EnableDNV", str(tgC))
                config.set(processID + "HL_" + WONID, "EnableAUT", str(tgD))
                config.set(processID + "HL_" + WONID, "EnableMGM", str(tgE))
                config.set(processID + "HL_" + WONID, "Size" + processID + "d1", str(tgF))
                config.set(processID + "HL_" + WONID, "EndOfConfig", str("-" * 172)+"["+dt_string+"]")
            config.write(configfile)
            usedVar = ("TGHL_" + WONID)
            config.remove_section(usedVar)
            # print('Deleting unused variables...')

        elif processID == 'TT':
            if not config.has_section(processID +"HL_" + WONID):
                config.add_section(processID +"HL_" + WONID)
                config.set(processID + "HL_" + WONID, "SmpleSize", str(ttA))
                config.set(processID + "HL_" + WONID, "GroupType", str(ttB))
                config.set(processID + "HL_" + WONID, "SEOLSpace", str(ttK))
                config.set(processID + "HL_" + WONID, "SEOPSpace", str(ttP))
                config.set(processID + "HL_" + WONID, "EnableDNV", str(ttC))
                config.set(processID + "HL_" + WONID, "EnableAUT", str(ttD))
                config.set(processID + "HL_" + WONID, "EnableMGM", str(ttE))
                config.set(processID + "HL_" + WONID, "Size20" + processID + "d1", str(ttF))
                config.set(processID + "HL_" + WONID, "Size20" + processID + "d2", str(ttG))
                config.set(processID + "HL_" + WONID, "Size20" + processID + "d3", str(ttH))
                config.set(processID + "HL_" + WONID, "Size18" + processID + "d4", str(ttI))
                config.set(processID + "HL_" + WONID, "Size18" + processID + "d5", str(ttJ))
                config.set(processID + "HL_" + WONID, "EndOfConfig", str("-" * 172)+"["+dt_string+"]")
            config.write(configfile)
            usedVar = ("TTHL_" + WONID)
            config.remove_section(usedVar)
            # print('Deleting unused variables...')

        elif processID == 'ST':
            if not config.has_section(processID +"HL_"+WONID):
                config.add_section(processID +"HL_"+WONID)
                config.set(processID + "HL_" + WONID, "SmpleSize", str(stA))
                config.set(processID + "HL_" + WONID, "GroupType", str(stB))
                config.set(processID + "HL_" + WONID, "SEOLSpace", str(stK))
                config.set(processID + "HL_" + WONID, "SEOPSpace", str(stP))
                config.set(processID + "HL_" + WONID, "EnableDNV", str(stC))
                config.set(processID + "HL_" + WONID, "EnableAUT", str(stD))
                config.set(processID + "HL_" + WONID, "EnableMGM", str(stE))
                config.set(processID + "HL_" + WONID, "Size20" + processID + "d1", str(stF))
                config.set(processID + "HL_" + WONID, "Size20" + processID + "d2", str(stG))
                config.set(processID + "HL_" + WONID, "Size20" + processID + "d3", str(stH))
                config.set(processID + "HL_" + WONID, "Size18" + processID + "d4", str(stI))
                config.set(processID + "HL_" + WONID, "Size18" + processID + "d5", str(stJ))
                config.set(processID + "HL_" + WONID, "EndOfConfig", str("-" * 172)+"["+dt_string+"]")
            config.write(configfile)
            usedVar = ("STHL_" + WONID)
            config.remove_section(usedVar)
            # print('Deleting unused variables...')

        else:
            pass

        print(processID + ' - Config file successfully saved!')

# ------------------------------------------------------------------------------


def decryptpProcessLim(WONID, processID):

    # initialise object instance -----------[]
    processFile = 'hisLim' + processID + '.INI'
    # print('Config FileName:', processFile)

    if processFile:
        config_object.read(processFile)
    else:
        print('Configuration file does not exist...')

    try:
        limX = config_object[processID + "HL_" + WONID]

        if processID == 'TG':  # Tape Gap (Polarisation)
            gen10 = onetimepad.decrypt(limX['SmpleSize'], 'random')
            gen20 = onetimepad.decrypt(limX['GroupType'], 'random')
            gen25 = onetimepad.decrypt(limX['SEOLSpace'], 'random')
            gen26 = onetimepad.decrypt(limX['SEOPSpace'], 'random')
            gen30 = onetimepad.decrypt(limX['EnableDNV'], 'random')
            gen40 = onetimepad.decrypt(limX['EnableAUT'], 'random')
            gen50 = onetimepad.decrypt(limX['EnableMGM'], 'random')
            # ----------------------------------------------------------
            tapeA = onetimepad.decrypt(limX['Size'+processID+'d1'], 'random')
            tapeB = 0
            tapeC = 0
            tapeD = 0
            tapeE = 0

        elif processID == 'TT':     # Tape Temperature
            gen10 = onetimepad.decrypt(limX['SmpleSize'], 'random')
            gen20 = onetimepad.decrypt(limX['GroupType'], 'random')
            gen25 = onetimepad.decrypt(limX['SEOLSpace'], 'random')
            gen26 = onetimepad.decrypt(limX['SEOPSpace'], 'random')
            gen30 = onetimepad.decrypt(limX['EnableDNV'], 'random')
            gen40 = onetimepad.decrypt(limX['EnableAUT'], 'random')
            gen50 = onetimepad.decrypt(limX['EnableMGM'], 'random')
            # ----------------------------------------------------------
            tapeA = onetimepad.decrypt(limX['size20'+processID+'d1'], 'random')
            tapeB = onetimepad.decrypt(limX['size20'+processID+'d2'], 'random')
            tapeC = onetimepad.decrypt(limX['size20'+processID+'d3'], 'random')
            tapeD = onetimepad.decrypt(limX['size18'+processID+'d4'], 'random')
            tapeE = onetimepad.decrypt(limX['size18'+processID+'d5'], 'random')

        elif processID == 'ST':     # Substrate Temperature
            gen10 = onetimepad.decrypt(limX['SmpleSize'], 'random')
            gen20 = onetimepad.decrypt(limX['GroupType'], 'random')
            gen25 = onetimepad.decrypt(limX['SEOLSpace'], 'random')
            gen26 = onetimepad.decrypt(limX['SEOPSpace'], 'random')
            gen30 = onetimepad.decrypt(limX['EnableDNV'], 'random')
            gen40 = onetimepad.decrypt(limX['EnableAUT'], 'random')
            gen50 = onetimepad.decrypt(limX['EnableMGM'], 'random')
            # ----------------------------------------------------------
            tapeA = onetimepad.decrypt(limX['size20'+processID+'d1'], 'random')
            tapeB = onetimepad.decrypt(limX['size20'+processID+'d2'], 'random')
            tapeC = onetimepad.decrypt(limX['size20'+processID+'d3'], 'random')
            tapeD = onetimepad.decrypt(limX['size18'+processID+'d4'], 'random')
            tapeE = onetimepad.decrypt(limX['size18'+processID+'d5'], 'random')

        elif processID == 'WS':  # Substrate Temperature
            gen10 = onetimepad.decrypt(limX['SmpleSize'], 'random')
            gen20 = onetimepad.decrypt(limX['GroupType'], 'random')
            gen25 = onetimepad.decrypt(limX['SEOLSpace'], 'random')
            gen26 = onetimepad.decrypt(limX['SEOPSpace'], 'random')
            gen30 = onetimepad.decrypt(limX['EnableDNV'], 'random')
            gen40 = onetimepad.decrypt(limX['EnableAUT'], 'random')
            gen50 = onetimepad.decrypt(limX['EnableMGM'], 'random')
            # ----------------------------------------------------------
            tapeA = onetimepad.decrypt(limX['size20' + processID + 'd1'], 'random')
            tapeB = onetimepad.decrypt(limX['size20' + processID + 'd2'], 'random')
            tapeC = onetimepad.decrypt(limX['size20' + processID + 'd3'], 'random')
            tapeD = onetimepad.decrypt(limX['size18' + processID + 'd4'], 'random')
            tapeE = onetimepad.decrypt(limX['size18' + processID + 'd5'], 'random')

        else:
            print('Error! Invalid Process Choice..')

    except KeyError:
        print('Configuration file is missing. Loading default values...')
        gen10 = 0
        gen20 = 0
        gen25 = 0   # EOL Sample Space
        gen26 = 0   # EOP sample space
        gen30 = 0
        gen40 = 0
        gen50 = 0
        tapeA = 0
        tapeB = 0
        tapeC = 0
        tapeD = 0
        tapeE = 0
        # errorNote()

    return gen10, gen20, gen25, gen26, gen30, gen40, gen50, tapeA, tapeB, tapeC, tapeD, tapeE

