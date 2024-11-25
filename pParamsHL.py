from tkinter import *
from configparser import ConfigParser
from datetime import datetime
from tkinter import messagebox
import onetimepad

# ---------- Initialise object instance ---
config_object = ConfigParser()
config = ConfigParser()


# XBar Constants ------------------------------[]
A3 = [0.975, 0.789, 0.680, 0.6327, 0.606, 0.5525]  # 10, 15, 20, 23, 25, 30  sample sizes respectively
B3 = [0.284, 0.428, 0.510, 0.5452, 0.565, 0.6044]  # 10, 15, 20, 23, 25, 30  sample sizes respectively
B4 = [1.716, 1.572, 1.490, 1.4548, 1.435, 1.3956]  # 10, 15, 20, 23, 25, 30

# -----------------------------------------------[]
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
# -----------------------------------------------[]
valueState1, valueState2, valueState3, valueState4 = False, False, False, False


def errorNote():
    # root.wm_attributes('-topmost', True)
    messagebox.showerror('Key Error', 'Work Order config Not found')
    return


def checkhistDev(xUCL, MeanP, sampSiz):
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

    UCL = (const3 * stdDev)  # Upper control limits of 1 std dev
    LCL = (const2 * stdDev)  # Lower control limits of 1 Std dev

    return UCL, LCL, stdDev


# function to allow historical limits entry--------------------------------------------------------------[]
def ppHLderivation(pop, gSize1, gSize2, xUCLa, xLCLa, xUCLb, xLCLb):
    global xBarMa, sBarMa, val1, val2, val3, val4 #, val5, val6, val7, val8

    # Function performs dynamic calculations ---[]
    def calculation(event=None):
        global pParam1, pParam1, pParam2, pParam3, pParam4, valueState1, valueState2, valueState3, valueState4

        try:
            # Compute XBar mean / center line ------------------------[Roller Force]
            if xUCLa.get() and xLCLa.get():
                xBarMa = float(xLCLa.get()) + ((float(xUCLa.get()) - float(xLCLa.get())) / 2)
                sUCLa, sLCLa, sBarMa = checkhistDev(float(xUCLa.get()), xBarMa, gSize1.get())  # Compute Mean
                xUSLa = xBarMa + (float(xUCLa.get()) - xBarMa) / 3 * 6
                xLSLa = xBarMa - (xBarMa - float(xLCLa.get())) / 3 * 6

                print('Production Parameter A: XBar Mean', xBarMa)
                print('Computed sMean/sUCL/sLCL:', sBarMa, sUCLa, sLCLa)
                # Display values on user screen mat -----[1]
                pParam1 = (
                dt_string, '**', xUCLa.get(), xLCLa.get(), round(sUCLa,3), round(sLCLa,3), round(xBarMa, 3), round(sBarMa, 3),
                round(xUSLa, 3), round(xLSLa, 3), '**')
                print('Roller Force Historical:', pParam1)
                # ---------------------------------------[]
                val1A["text"] = round(xBarMa, 3)
                val2A["text"] = round(sBarMa, 3)
                valueState1 = True
            else:
                valueState1 = False
            # --------------------------------------------------------[Cell Tension]
            if xUCLb.get() and xLCLb.get():
                xBarMb = float(xLCLb.get()) + ((float(xUCLb.get()) - float(xLCLb.get())) / 2)
                sUCLb, sLCLb, sBarMb = checkhistDev(float(xUCLb.get()), xBarMb, gSize1.get())  # Compute Mean
                xUSLb = xBarMb + (float(xUCLb.get()) - xBarMb) / 3 * 6
                xLSLb = xBarMb - (xBarMb - float(xLCLb.get())) / 3 * 6

                print('Production Parameter B: XBar Mean', xBarMb)
                print('Computed sMean/sUCL/sLCL:', sBarMb, sUCLb, sLCLb)
                # Display values on user screen mat -----[1]
                pParam2 = (
                    dt_string, '**', xUCLb.get(), xLCLb.get(), round(sUCLb,3), round(sLCLb,3), round(xBarMb, 3),
                    round(sBarMb, 3), round(xUSLb, 3), round(xLSLb, 3), '**')
                print('Cell Tension Historical:', pParam2)
                # Display values on user screen mat -----[2]
                val3A["text"] = round(xBarMb, 3)
                val4A["text"] = round(sBarMb, 3)
                valueState2 = True
            else:
                valueState2 = False

        except ValueError:
            val1A["text"] = "Integers or Float numbers only"
            val2A["text"] = "Integers or Float numbers only"

    # clear the content and allow entry of historical limits -------
    gSize1.set('30')
    gSize2.set('2')

    # -------------[RF - Roller Force]
    xUCLa.set('0')
    xLCLa.set('0')

    # -------------[CT - Cell Tension]
    xUCLb.set('0')
    xLCLb.set('0')

    # -----------[Compute stats UCL/LCL] ------------[Process A]
    val1 = Entry(pop, width=8, state='normal', textvariable=xUCLa)
    val1.place(x=65, y=110)
    val2 = Entry(pop, width=8, state='normal', textvariable=xLCLa)
    val2.place(x=190, y=110)

    # ----------------------------------------------[Process B]
    val3 = Entry(pop, width=8, state='normal', textvariable=xUCLb)
    val3.place(x=65, y=140)
    val4 = Entry(pop, width=8, state='normal', textvariable=xLCLb)
    val4.place(x=190, y=140)

    # ------------------------------------------------------------#
    # Compute derived mean values for XBar/Sbar Plot & fill -------
    val1A = Label(pop, width=8, state='normal', font=("bold", 10))
    val1A.place(x=325, y=110)
    val2A = Label(pop, width=8, state='normal', font=("bold", 10))
    val2A.place(x=447, y=110)
    # --------------------
    val3A = Label(pop, width=8, state='normal', font=("bold", 10))
    val3A.place(x=325, y=140)
    val4A = Label(pop, width=8, state='normal', font=("bold", 10))
    val4A.place(x=447, y=140)
    # # ------------------------

    # ------------------ Binding properties -----------------------
    val1.bind("<KeyRelease>", calculation)
    val2.bind("<KeyRelease>", calculation)
    # -----
    val3.bind("<KeyRelease>", calculation)
    val4.bind("<KeyRelease>", calculation)

    return


def saveMetricspP(WorkOrderID, sSize, sGroup, shiftS, shiftE, pMax, pCtrl, usepHL):
    shfS = shiftS.get()
    shfE = shiftE.get()
    print('Details of metrics to save:', WorkOrderID, sSize, sGroup, shfS, shfE, pMax, pCtrl)
    # ----------------------[]
    if valueState1 or valueState2:      # from defined global arrays
        config1 = pParam1
        config2 = pParam2

    else:
        config1 = 0
        config2 = 0

        # set rows data to readonly i.e lock down before save ------------[]

    # ----------------------------------------------------------------[]
    try:
        print("Attempting to encrypt config values...")
        encryptMetricspP(WorkOrderID, usepHL, sSize, sGroup, shfS, shfE, pMax, pCtrl, config1, config2)
        # set all fields to readonly -------------[]

        eFields = [val1, val2, val3, val4]      # val5, val6, val7, val8
        for entrz in eFields:
            entrz.config(state="readonly")

    except ValueError:
        errorNote()     # response to save button when entry field is empty

    return

# --------------------------------------------------------------------[]


def encryptMetricspP(WON, usepHL, sSize, sGroup, shiftS, shiftE, pMax, pCtrl, pParam1, pParam2):
    WONID = WON
    # objective of cryptography is to provide basic security concepts in data exchange & integrity
    print('\nWriting encryption into archive...')

    # Check variables----- []
    print('Saving the Lists:', usepHL, "\n", pMax, "\n", pCtrl, "\n", sSize, "\n", sGroup, "\n", shiftS, "\n", shiftE, "\n", pParam1, "\n", pParam2)
    # ------------- Encrypt each line of information -----[]
    cf0 = onetimepad.encrypt(str(usepHL), 'random')
    cf1 = onetimepad.encrypt(str(sSize), 'random')
    cf2 = onetimepad.encrypt(str(sGroup), 'random')
    cf3 = onetimepad.encrypt(str(shiftS), 'random')
    cf4 = onetimepad.encrypt(str(shiftE), 'random')
    # ------
    cf5 = onetimepad.encrypt(str(pMax), 'random')
    cf6 = onetimepad.encrypt(str(pCtrl), 'random')
    cf7 = onetimepad.encrypt(str(pParam1), 'random')
    cf8 = onetimepad.encrypt(str(pParam2), 'random')

    # Open text file and save historical details -----------#
    with open("histProdParams.INI", 'a') as configfile:            # append mode.
        # Prevent duplicated instance ------ [TODO]
        # Prevent duplicated keys -----------[TODO]

        if not config.has_section("SampleProp_"+WONID):
            config.add_section("SampleProp_"+WONID)
            config.set("SampleProp_" + WONID, "useHLSL", str(cf0))
            config.set("SampleProp_"+WONID, "sampleSize", str(cf1))
            config.set("SampleProp_"+WONID, "groupType", str(cf2))

        if not config.has_section("ShiftPattern_"+WONID):
            config.add_section("ShiftPattern_"+WONID)
            config.set("ShiftPattern_"+WONID, "shiftBegins", str(cf3))
            config.set("ShiftPattern_"+WONID, "ShiftEnds", str(cf4))

        if not config.has_section("ProdParameters_"+WONID):
            config.add_section("ProdParameters_"+WONID)
            # Plot type Min/Max or Control Charts -------
            config.set("ProdParameters_" + WONID, "PlotMinMax", str(cf5))
            config.set("ProdParameters_" + WONID, "PlotCtrlC", str(cf6))
            # ------ ------------------------------------
            config.set("ProdParameters_"+WONID, "prodParam1", str(cf7))
            config.set("ProdParameters_"+WONID, "prodParam2", str(cf8))
            config.set("ProdParameters_" + WONID, "[" + dt_string + "]", str("-" * 172) + "EndOfConfig.")
        else:
            pass

        config.write(configfile)


def decryptMetricspP(WONID):
    import os.path
    # initialise object instance ------------------[]
    processFile = os.path.exists("histProdParams.INI")

    # Read the file and check for duplicate keys --[]
    if processFile:
        config_object.read("histProdParams.INI")     # TODO detect duplicate Section and Keys and iterate accordingly

        try:
            # Load the content ------------------------------------------------[]
            limpSample = config_object["SampleProp_"+WONID]
            limpShifts = config_object["ShiftPattern_"+WONID]
            limpParams = config_object["ProdParameters_"+WONID]
            # --------- Fetch date under each Key -------------
            LmType = onetimepad.decrypt(limpSample["useHLSL"], 'random')
            sSize = onetimepad.decrypt(limpSample["sampleSize"], 'random')
            gType = onetimepad.decrypt(limpSample["groupType"], 'random')
            sStart = onetimepad.decrypt(limpShifts["shiftBegins"], 'random')
            sStops = onetimepad.decrypt(limpShifts["ShiftEnds"], 'random')
            # ------------------------------------------------------------------#
            pMinMax = onetimepad.decrypt(limpParams["PlotMinMax"], 'random')
            pContrl = onetimepad.decrypt(limpParams["PlotCtrlC"], 'random')
            pParam1 = onetimepad.decrypt(limpParams["prodParam1"], 'random')
            pParam2 = onetimepad.decrypt(limpParams["prodParam2"], 'random')

        except KeyError:
            print('Configuration File or Key is missing. Loading default values...')
            LmType = 0  # used automatic limits is historical values are missing
            sSize= 0
            gType = 0
            sStart = 0
            sStops = 0
            pMinMax = 0
            pContrl = 0
            pParam1 = 0
            pParam2 = 0

    else:
        print('Config File exist', processFile)
        print('Configuration file does not exist, loading default variables...')
        LmType = 0  # used automatic limits is historical values are missing
        sSize = 0
        gType = 0
        sStart = 0
        sStops = 0
        pMinMax = 0
        pContrl = 0
        pParam1 = 0
        pParam2 = 0

    # print('Fetch Data:','\n', sSize, '\n', gType, '\n', sStart, '\n', sStops, '\n', pParam1, '\n', pParam2)

    return LmType, sSize, gType, sStart, sStops, pMinMax, pContrl, pParam1, pParam2
