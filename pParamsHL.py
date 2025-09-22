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

# processWON[0], rMode, sel_SS, sel_gT, LA, LP, CT, OT, RP, WS, sSta, sEnd, xlp, xla, xtp, xrf, xtt, xst, xtg
def saveMetricspP(WorkOrderID, rMode, sel_SS, sel_gT, sLA, sLP, sCT, sOT, sRP, sWS, shiftS, shiftE, LP, LA, TP, RF, TT, ST, TG):
    shfS = shiftS.get()
    shfE = shiftE.get()
    print('Details of Monitors to save:', sLA, sLP, sCT, sOT, sRP, sWS)
    print('Details of metrics to save:', WorkOrderID, shfS, shfE)

    # ----------------------------------------------------------------[]
    try:
        print("Attempting to encrypt config values...")
        encryptMetricspP(WorkOrderID, rMode, sel_SS, sel_gT, sLA, sLP, sCT, sOT, sRP, sWS, shfS, shfE, LP, LA, TP, RF, TT, ST, TG)

    except ValueError:
        errorNote()     # response to save button when entry field is empty

    return

# --------------------------------------------------------------------[]


def encryptMetricspP(WON, eDM, eSS, SgT, eLA, eLP, eCT, eOT, eRP, eWS, shiftS, shiftE, LP, LA, TP, RF, TT, ST, TG):
    WONID = WON
    # objective of cryptography is to provide basic security concepts in data exchange & integrity
    print('\nWriting encryption into archive...')

    # Check variables----- []
    print('Saving the Lists:', WONID, "\n", shiftS, "\n", shiftE)
    ab1 = onetimepad.encrypt(str(eDM), 'random')    # Default Run Mode
    ab2 = onetimepad.encrypt(str(eSS), 'random')    # monitor LP
    ab3 = onetimepad.encrypt(str(SgT), 'random')    # monitor CT
    # ------------- Encrypt each line of information -----[]

    af1 = onetimepad.encrypt(str(eLA), 'random')    # monitor LA
    af2 = onetimepad.encrypt(str(eLP), 'random')    # monitor LP
    af3 = onetimepad.encrypt(str(eCT), 'random')    # monitor CT
    af4 = onetimepad.encrypt(str(eOT), 'random')    # monitor OT
    af5 = onetimepad.encrypt(str(eRP), 'random')    # monitor RP
    af6 = onetimepad.encrypt(str(eWS), 'random')    # monitor WS

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

    # Open text file and save historical details -----------#
    with open("histProdParams.INI", 'a') as configfile:            # append mode.
        # Prevent duplicated instance ------ [TODO]
        if not config.has_section("CommonStatistic_" + WONID):
            config.add_section("CommonStatistic_" + WONID)
            # Plot type Min/Max or Control Charts ----------#
            config.set("CommonStatistic_" + WONID, "DefaultMOD", str(ab1))
            config.set("CommonStatistic_" + WONID, "SampleSize", str(ab2))
            config.set("CommonStatistic_" + WONID, "SubgSample", str(ab3))

        if not config.has_section("WorkOrderNumber_" + WONID):
            config.add_section("WorkOrderNumber_" + WONID)
            # Plot type Min/Max or Control Charts ------------#
            config.set("WorkOrderNumber_" + WONID, "monitor_LA", str(af1))
            config.set("WorkOrderNumber_" + WONID, "monitor_LP", str(af2))
            config.set("WorkOrderNumber_" + WONID, "monitor_CT", str(af3))
            config.set("WorkOrderNumber_" + WONID, "monitor_OT", str(af4))
            config.set("WorkOrderNumber_" + WONID, "monitor_RP", str(af5))
            config.set("WorkOrderNumber_" + WONID, "monitor_WS", str(af6))

        if not config.has_section("ShiftPattern_" + WONID):
            config.add_section("ShiftPattern_" + WONID)
            # Plot type Min/Max or Control Charts -------
            config.set("ShiftPattern_" + WONID, "shiftBegn", str(cf3))
            config.set("ShiftPattern_" + WONID, "ShiftEnds", str(cf4))

        if not config.has_section("ActiveParams_" + WONID):
            config.add_section("ActiveParams_" + WONID)
            # Plot type Min/Max or Control Charts -------
            config.set("ActiveParams_" + WONID, "Laser_pwr", str(cf5))
            config.set("ActiveParams_" + WONID, "Laser_ang", str(cf6))
            config.set("ActiveParams_" + WONID, "Tape_plac", str(cf7))
            config.set("ActiveParams_" + WONID, "Roller_fc", str(cf8))
            # ------ ------------------------------------
            config.set("ActiveParams_" + WONID, "Tape_Temp", str(cf9))
            config.set("ActiveParams_" + WONID, "Subs_temp", str(cfA))
            config.set("ActiveParams_" + WONID, "Tape_void", str(cfB))
            config.set("ActiveParams_" + WONID, "[" + dt_string + "]", str("-" * 172) + "EndOfConfig.")
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
            comnSample = config_object["CommonStatistic_" + WONID]
            limpSample = config_object["WorkOrderNumber_" + WONID]
            limpShifts = config_object["ShiftPattern_" + WONID]
            limpParams = config_object["ActiveParams_" + WONID]

            cDM = onetimepad.decrypt(comnSample["DefaultMOD"], 'random')
            cSS = onetimepad.decrypt(comnSample["SampleSize"], 'random')
            cGS = onetimepad.decrypt(comnSample["SubgSample"], 'random')
            # ---------------------------------------------------------------#
            dLA = onetimepad.decrypt(limpSample["monitor_LA"], 'random')
            dLP = onetimepad.decrypt(limpSample["monitor_LP"], 'random')
            dCT = onetimepad.decrypt(limpSample["monitor_CT"], 'random')
            dOT = onetimepad.decrypt(limpSample["monitor_OT"], 'random')
            dRP = onetimepad.decrypt(limpSample["monitor_RP"], 'random')
            dWS = onetimepad.decrypt(limpSample["monitor_WS"], 'random')

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

        except KeyError:
            print('Existing configuration file not found! \nLoading default config on WON# ' + WONID)
            cDM = 0
            cSS = 0
            cGS = 0
            dLA = 0
            dLP = 0
            dCT = 0
            dOT = 0
            dRP = 0
            dWS = 0
            sStart = '07:00:00'
            sStops = '17:00:00'
            LP = 0
            LA = 0
            TP = 0
            RF = 0
            TT = 0
            ST = 0
            TG = 0

    else:
        print('Configuration not found, \nloading default values...')
        cDM = 0
        cSS = 30
        cGS = 2
        # -----
        dLA = 0
        dLP = 0
        dCT = 0
        dOT = 0
        dRP = 0
        dWS = 0
        sStart = '07:00:00'
        sStops = '17:00:00'
        LP = 0
        LA = 0
        TP = 0
        RF = 0
        TT = 1
        ST = 1
        TG = 1

    # print('Fetch Data:','\n', dCT, '\n', dOT, '\n', sStart, '\n', sStops, '\n',  RF, '\n', TT)

    return cDM, cSS, cGS, dLA, dLP, dCT, dOT, dRP, dWS, sStart, sStops, LP, LA, TP, RF, TT, ST, TG
