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


def saveMetricspP(WorkOrderID, sSize, sGroup, shiftS, shiftE, OT, CT, RP, LA, WS, TG, ST, LP):
    shfS = shiftS.get()
    shfE = shiftE.get()
    print('Details of metrics to save:', WorkOrderID, sSize, sGroup, shfS, shfE)

    # ----------------------------------------------------------------[]
    try:
        print("Attempting to encrypt config values...")
        encryptMetricspP(WorkOrderID, sSize, sGroup, shfS, shfE, OT, CT, RP, LA, WS, TG, ST, LP)

    except ValueError:
        errorNote()     # response to save button when entry field is empty

    return

# --------------------------------------------------------------------[]


def encryptMetricspP(WON, sSize, sGroup, shiftS, shiftE, OT, CT, RP, LA, WS, TG, ST, LP):
    WONID = WON
    # objective of cryptography is to provide basic security concepts in data exchange & integrity
    print('\nWriting encryption into archive...')

    # Check variables----- []
    print('Saving the Lists:', WONID, "\n", sSize, "\n", sGroup, "\n", shiftS, "\n", shiftE)
    # ------------- Encrypt each line of information -----[]
    cf1 = onetimepad.encrypt(str(sSize), 'random')
    cf2 = onetimepad.encrypt(str(sGroup), 'random')
    cf3 = onetimepad.encrypt(str(shiftS), 'random')
    cf4 = onetimepad.encrypt(str(shiftE), 'random')
    # ------
    cf5 = onetimepad.encrypt(str(OT), 'random')
    cf6 = onetimepad.encrypt(str(CT), 'random')
    cf7 = onetimepad.encrypt(str(RP), 'random')
    cf8 = onetimepad.encrypt(str(LA), 'random')
    cf9 = onetimepad.encrypt(str(WS), 'random')
    cfA = onetimepad.encrypt(str(TG), 'random')
    cfB = onetimepad.encrypt(str(ST), 'random')
    cfC = onetimepad.encrypt(str(LP), 'random')

    # Open text file and save historical details -----------#
    with open("histProdParams.INI", 'a') as configfile:            # append mode.
        # Prevent duplicated instance ------ [TODO]
        # Prevent duplicated keys -----------[TODO]

        if not config.has_section("SampleProp_"+WONID):
            config.add_section("SampleProp_"+WONID)
            config.set("SampleProp_"+WONID, "sampleSize", str(cf1))
            config.set("SampleProp_"+WONID, "groupType", str(cf2))

        if not config.has_section("ShiftPattern_"+WONID):
            config.add_section("ShiftPattern_"+WONID)
            config.set("ShiftPattern_"+WONID, "shiftBegins", str(cf3))
            config.set("ShiftPattern_"+WONID, "ShiftEnds", str(cf4))

        if not config.has_section("ProdParameters_"+WONID):
            config.add_section("ProdParameters_"+WONID)
            # Plot type Min/Max or Control Charts -------
            config.set("ProdParameters_" + WONID, "Oven_Temp", str(cf5))
            config.set("ProdParameters_" + WONID, "Cell_Tens", str(cf6))
            config.set("ProdParameters_"+WONID, "Roller_Pre", str(cf7))
            config.set("ProdParameters_"+WONID, "Laser_Angle", str(cf8))
            # ------ ------------------------------------
            config.set("ProdParameters_" + WONID, "Winding_Spd", str(cf9))
            config.set("ProdParameters_" + WONID, "TapeGap_Pol", str(cfA))
            config.set("ProdParameters_" + WONID, "Spooling_T", str(cfB))
            config.set("ProdParameters_" + WONID, "Laser_Power", str(cfC))
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
            sSize = onetimepad.decrypt(limpSample["sampleSize"], 'random')
            gType = onetimepad.decrypt(limpSample["groupType"], 'random')
            sStart = onetimepad.decrypt(limpShifts["shiftBegins"], 'random')
            sStops = onetimepad.decrypt(limpShifts["ShiftEnds"], 'random')
            # ------------------------------------------------------------------#
            OT = onetimepad.decrypt(limpParams["Oven_Temp"], 'random')
            CT = onetimepad.decrypt(limpParams["Cell_Tens"], 'random')
            RP = onetimepad.decrypt(limpParams["Roller_Pre"], 'random')
            LA = onetimepad.decrypt(limpParams["Laser_Angle"], 'random')
            WS = onetimepad.decrypt(limpParams["Winding_Spd"], 'random')
            TG = onetimepad.decrypt(limpParams["TapeGap_Pol"], 'random')
            ST = onetimepad.decrypt(limpParams["Spooling_T"], 'random')
            LP = onetimepad.decrypt(limpParams["Laser_Power"], 'random')

        except KeyError:
            print('Configuration File or Key is missing. Loading default values...')
            sSize= 0
            gType = 0
            sStart = 0
            sStops = 0
            OT = 0
            CT = 0
            RP = 0
            LA = 0
            WS = 0
            TG = 0
            ST = 0
            LP = 0

    else:
        print('Config File exist', processFile)
        print('Configuration file does not exist, loading default variables...')
        LmType = 0  # used automatic limits is historical values are missing
        sSize = 0
        gType = 0
        sStart = 0
        sStops = 0
        OT = 0
        CT = 0
        RP = 0
        LA = 0
        WS = 0
        TG = 0
        ST = 0
        LP = 0

    # print('Fetch Data:','\n', sSize, '\n', gType, '\n', sStart, '\n', sStops, '\n', pParam1, '\n', pParam2)

    return sSize, gType, sStart, sStops, OT, CT, RP, LA, WS, TG, ST, LP
