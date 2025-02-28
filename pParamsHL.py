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


def saveMetricspP(WorkOrderID, sLA, sLP, sCT, sOT, sRP, sWS, sSP, shiftS, shiftE, LP, LA, TP, RF, TT, ST, TG, SP):
    shfS = shiftS.get()
    shfE = shiftE.get()
    print('Details of metrics to save:', WorkOrderID, shfS, shfE)

    # ----------------------------------------------------------------[]
    try:
        print("Attempting to encrypt config values...")
        encryptMetricspP(WorkOrderID, sLA, sLP, sCT, sOT, sRP, sWS, sSP, shfS, shfE, LP, LA, TP, RF, TT, ST, TG, SP)

    except ValueError:
        errorNote()     # response to save button when entry field is empty

    return

# --------------------------------------------------------------------[]


def encryptMetricspP(WON, eLA, eLP, eCT, eOT, eRP, eWS, eSP, shiftS, shiftE, LP, LA, TP, RF, TT, ST, TG, SP):
    WONID = WON
    # objective of cryptography is to provide basic security concepts in data exchange & integrity
    print('\nWriting encryption into archive...')

    # Check variables----- []
    print('Saving the Lists:', WONID, "\n", shiftS, "\n", shiftE)
    # ------------- Encrypt each line of information -----[]
    af1 = onetimepad.encrypt(str(eLA), 'random')
    af2 = onetimepad.encrypt(str(eLP), 'random')
    af3 = onetimepad.encrypt(str(eCT), 'random')
    af4 = onetimepad.encrypt(str(eOT), 'random')
    af5 = onetimepad.encrypt(str(eRP), 'random')
    af6 = onetimepad.encrypt(str(eWS), 'random')
    af7 = onetimepad.encrypt(str(eSP), 'random')

    cf3 = onetimepad.encrypt(str(shiftS), 'random')
    cf4 = onetimepad.encrypt(str(shiftE), 'random')
    # ------
    cf5 = onetimepad.encrypt(str(LP), 'random')
    cf6 = onetimepad.encrypt(str(LA), 'random')
    cf7 = onetimepad.encrypt(str(TP), 'random')
    cf8 = onetimepad.encrypt(str(RF), 'random')
    cf9 = onetimepad.encrypt(str(TT), 'random')
    cfA = onetimepad.encrypt(str(ST), 'random')
    cfB = onetimepad.encrypt(str(TG), 'random')
    cfC = onetimepad.encrypt(str(SP), 'random')

    # Open text file and save historical details -----------#
    with open("histProdParams.INI", 'a') as configfile:            # append mode.
        # Prevent duplicated instance ------ [TODO]
        # Prevent duplicated keys -----------[TODO]

        if not config.has_section("WorkOrderNumber_"+WONID):
            config.add_section("WorkOrderNumber_"+WONID)
            # Plot type Min/Max or Control Charts -------
            config.set("WorkOrderNumber_" + WONID, "monitor_LA", str(af1))
            config.set("WorkOrderNumber_" + WONID, "monitor_LP", str(af2))
            config.set("WorkOrderNumber_" + WONID, "monitor_CT", str(af3))
            config.set("WorkOrderNumber_" + WONID, "monitor_OT", str(af4))
            config.set("WorkOrderNumber_" + WONID, "monitor_RP", str(af5))
            config.set("WorkOrderNumber_" + WONID, "monitor_WS", str(af6))
            config.set("WorkOrderNumber_" + WONID, "monitor_SP", str(af7))

        if not config.has_section("ShiftPattern_"+WONID):
            config.add_section("ShiftPattern_"+WONID)
            # Plot type Min/Max or Control Charts -------
            config.set("ShiftPattern_"+WONID, "shiftBegn", str(cf3))
            config.set("ShiftPattern_"+WONID, "ShiftEnds", str(cf4))

        if not config.has_section("ProdParameters_"+WONID):
            config.add_section("ProdParameters_"+WONID)
            # Plot type Min/Max or Control Charts -------
            config.set("ProdParameters_" + WONID, "Laser_pwr", str(cf5))
            config.set("ProdParameters_" + WONID, "Laser_ang", str(cf6))
            config.set("ProdParameters_" + WONID, "Tape_plac", str(cf7))
            config.set("ProdParameters_" + WONID, "Roller_fc", str(cf8))
            # ------ ------------------------------------
            config.set("ProdParameters_" + WONID, "Tape_Temp", str(cf9))
            config.set("ProdParameters_" + WONID, "Subs_temp", str(cfA))
            config.set("ProdParameters_" + WONID, "Tape_void", str(cfB))
            config.set("ProdParameters_" + WONID, "Spool_ten", str(cfC))
            config.set("ProdParameters_" + WONID, "[" + dt_string + "]", str("-" * 172) + "EndOfConfig.")
        else:
            pass

        config.write(configfile)


def decryptMetricsGeneral(WONID):
    import os.path
    # initialise object instance ------------------[]
    processFile = os.path.exists("histProdParams.INI")

    # Read the file and check for duplicate keys --[]
    if processFile:
        config_object.read("histProdParams.INI")     # TODO detect duplicate Section and Keys and iterate accordingly

        try:
            # Load the content ------------------------------------------------[]
            limpSample = config_object["WorkOrderNumber_" + WONID]
            limpShifts = config_object["ShiftPattern_" + WONID]
            limpParams = config_object["ActiveParams_" + WONID]

            # ---------------------------------------------------------------#
            dLA = onetimepad.decrypt(limpSample["monitor_LA"], 'random')
            dLP = onetimepad.decrypt(limpSample["monitor_LP"], 'random')
            dCT = onetimepad.decrypt(limpSample["monitor_CT"], 'random')
            dOT = onetimepad.decrypt(limpSample["monitor_OT"], 'random')
            dRP = onetimepad.decrypt(limpSample["monitor_RP"], 'random')
            dWS = onetimepad.decrypt(limpSample["monitor_WS"], 'random')
            dSP = onetimepad.decrypt(limpSample["monitor_SP"], 'random')

            # --------- Fetch date under each Key ---------------------------#
            sStart = onetimepad.decrypt(limpShifts["ShiftBegn"], 'random')
            sStops = onetimepad.decrypt(limpShifts["ShiftEnds"], 'random')
            # ----------------------------------------------------------------#
            LP = onetimepad.decrypt(limpParams["Laser_pwr"], 'random')
            LA = onetimepad.decrypt(limpParams["Laser_ang"], 'random')
            TP = onetimepad.decrypt(limpParams["Tape_plac"], 'random')
            RF = onetimepad.decrypt(limpParams["Roller_fc"], 'random')
            TT = onetimepad.decrypt(limpParams["Tape_Temp"], 'random')
            ST = onetimepad.decrypt(limpParams["Subs_temp"], 'random')
            TG = onetimepad.decrypt(limpParams["Tape_void"], 'random')
            SP = onetimepad.decrypt(limpParams["Spool_ten"], 'random')

        except KeyError:
            print('Configuration File or Key is missing. Loading default values...')
            dLA = 0
            dLP = 0
            dCT = 0
            dOT = 0
            dRP = 0
            dWS = 0
            dSP = 0
            sStart = 0
            sStops = 0
            LP = 0
            LA = 0
            TP = 0
            RF = 0
            TT = 0
            ST = 0
            TG = 0
            SP = 0

    else:
        print('Config File exist', processFile)
        print('Configuration file does not exist, loading default variables...')
        LmType = 0  # used automatic limits is historical values are missing
        dLA = 0
        dLP = 0
        dCT = 0
        dOT = 0
        dRP = 0
        dWS = 0
        dSP = 0
        sStart = 0
        sStops = 0
        LP = 0
        LA = 0
        TP = 0
        RF = 0
        TT = 0
        ST = 0
        TG = 0
        SP = 0

    print('Fetch Data:','\n', dCT, '\n', dOT, '\n', sStart, '\n', sStops, '\n',  RF, '\n', TT)

    return dLA, dLP, dCT, dOT, dRP, dWS, dSP, sStart, sStops, LP, LA, TP, RF, TT, ST, TG, SP
