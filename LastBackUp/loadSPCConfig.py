
# Authour: Dr Robert B. Labs, 2023 TFMC - Magma Global.

from configparser import ConfigParser

# #Get the configparser object
config_object = ConfigParser()
config = ConfigParser()


def load_configSPC(configFile):
    config_object.read(configFile)

    Info = config_object["SHIFTS_INFO"]
    Ctrl = config_object["TRIGGERINFO"]
    Mont = config_object["MONI_PARAMS"]

    # Shift Info group ----------------------------[]
    sd = Info["Start_Day"]      # Start of Shift
    fd = Info["FinishDay"]      # End of Shift
    gpz = int(Info["GSize"])    # Specify data group size
    gps = int(Info["GStep"])    # Specify group step
    uhl = int(Info["UseHL"])    # Activate Historical Module
    usm = int(Info["UseSM"])    # Activate Shewhart Module
    qmz = int(Info["Optmz"])    # Activate Optimised Runtime Memory Array (Dr Labs Method)

    # Triggering group ----------[RF]
    xuca = float(Ctrl["xUCLma"])
    xlca = float(Ctrl["xLCLma"])
    xma = float(Ctrl["xbmlmA"])
    suca = float(Ctrl["sUCLma"])
    slca = float(Ctrl["sLCLma"])
    sma = float(Ctrl["sbmlmA"])
    d_ma = str(Ctrl["distma"])
    # -------------------------[TT}
    xucb = float(Ctrl["xUCLmb"])
    xlcb = float(Ctrl["xLCLmb"])
    xmb = float(Ctrl["xbmlmB"])
    sucb = float(Ctrl["sUCLmb"])
    slcb = float(Ctrl["sLCLmb"])
    smb = float(Ctrl["sbmlmB"])
    d_mb = str(Ctrl["distmb"])
    # -------------------------[ST]
    xucc = float(Ctrl["xUCLmc"])
    xlcc = float(Ctrl["xLCLmc"])
    xmc = float(Ctrl["xbmlmC"])
    succ = float(Ctrl["sUCLmc"])
    slcc = float(Ctrl["sLCLmc"])
    smc = float(Ctrl["sbmlmC"])
    d_mc = str(Ctrl["distmc"])
    # -------------------------[TG]
    xucd = float(Ctrl["xUCLmd"])
    xlcd = float(Ctrl["xLCLmd"])
    xmd = float(Ctrl["xbmlmD"])
    sucd = float(Ctrl["sUCLmd"])
    slcd = float(Ctrl["sLCLmd"])
    smd = float(Ctrl["sbmlmD"])
    d_md = str(Ctrl["distmd"])

    # Monitor info group ------------------------[]
    a_s_p = int(Mont["Stat_param"])                  # Activate statistics on monitoring parameter
    # -------------------------[Enable Laser Power]
    # try:
    for key, value in Mont.items():
        # print(key)
        if key == 'lpower':
            pTagA = int(Mont["lpower"])
            xucf = float(Mont["xUCLmf"])
            xlcf = float(Mont["xLCLmf"])
            xmf = float(Mont["xbmlmF"])
            sucf = float(Mont["sUCLmf"])
            slcf = float(Mont["sLCLmf"])
            smf = float(Mont["sbmlmF"])
            d_mf = str(Mont["distmf"])
        if key == 'langle':
            pTagB = int(Mont["langle"])
            xucg = float(Mont["xUCLmg"])
            xlcg = float(Mont["xLCLmg"])
            xmg = float(Mont["xbmlmG"])
            sucg = float(Mont["sUCLmg"])
            slcg = float(Mont["sLCLmg"])
            smg = float(Mont["sbmlmG"])
            d_mg = str(Mont["distmg"])
        if key == 'hotens':
            pTagC = int(Mont["hotens"])
            xuch = float(Mont["xUCLmh"])
            xlch = float(Mont["xLCLmh"])
            xmh = float(Mont["xbmlmH"])
            such = float(Mont["sUCLmh"])
            slch = float(Mont["sLCLmh"])
            smh = float(Mont["sbmlmH"])
            d_mh = str(Mont["distmh"])
        if key == 'dcload':
            pTagD = int(Mont["daload"])
            xuci = float(Mont["xUCLmi"])
            xlci = float(Mont["xLCLmi"])
            xmi = float(Mont["xbmlmI"])
            suci = float(Mont["sUCLmi"])
            slci = float(Mont["sLCLmi"])
            smi = float(Mont["sbmlmI"])
            d_mi = str(Mont["distmi"])
        else:
            pTagA = int(Mont["lpower"])
            xucf = float(Mont["xUCLmf"])
            xlcf = float(Mont["xLCLmf"])
            xmf = float(Mont["xbmlmF"])
            sucf = float(Mont["sUCLmf"])
            slcf = float(Mont["sLCLmf"])
            smf = float(Mont["sbmlmF"])
            d_mf = str(Mont["distmf"])
            # ------------------------
            pTagB = int(Mont["langle"])
            xucg = float(Mont["xUCLmg"])
            xlcg = float(Mont["xLCLmg"])
            xmg = float(Mont["xbmlmG"])
            sucg = float(Mont["sUCLmg"])
            slcg = float(Mont["sLCLmg"])
            smg = float(Mont["sbmlmG"])
            d_mg = str(Mont["distmg"])
            # ------------------------
            pTagC = int(Mont["hotens"])
            xuch = float(Mont["xUCLmh"])
            xlch = float(Mont["xLCLmh"])
            xmh = float(Mont["xbmlmH"])
            such = float(Mont["sUCLmh"])
            slch = float(Mont["sLCLmh"])
            smh = float(Mont["sbmlmH"])
            d_mh = str(Mont["distmh"])
            # -------------------------
            pTagD = int(Mont["daload"])
            xuci = float(Mont["xUCLmi"])
            xlci = float(Mont["xLCLmi"])
            xmi = float(Mont["xbmlmI"])
            suci = float(Mont["sUCLmi"])
            slci = float(Mont["sLCLmi"])
            smi = float(Mont["sbmlmI"])
            d_mi = str(Mont["distmi"])

    return (sd, fd, gpz, gps, uhl, usm, qmz, xuca, xlca, xma, suca, slca, sma, d_ma, xucb, xlcb, xmb, sucb, slcb, smb,
            d_mb, xucc, xlcc, xmc, succ, slcc, smc, d_mc, xucd, xlcd, xmd, sucd, slcd, smd, d_md, a_s_p, pTagA, xucf,
            xlcf, xmf, sucf, slcf, smf, d_mf,  pTagB, xucg, xlcg, xmg, sucg, slcg, smg, d_mg, pTagC, xuch, xlch, xmh,
            such, slch, smh, d_mh, pTagD, xuci, xlci, xmi, suci, slci, smi, d_mi)

# Write to config.ini file -------------
def writeSPCconfig(a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z, a1, a2, a3, a4, a5, a6,
                   a7, a8, a9, b1, b2, b3, b4, b5, b6, b7, b8, b9, c1, c2, c3, c4, c5, c6, c7, c8, c9, d1):
    # Shift Information group ---------------------[SHIFTS_INFO]
    info1 = str(a)
    info2 = str(b)
    info3 = str(c)
    info4 = str(d)
    info5 = str(e)
    info6 = str(f)
    info7 = str(g)

    # Triggering group ----------------------------[TRIGGERINFO]
    # Historical Limits for Roller Force/Pressure
    info8 = str(h)
    info9 = str(i)
    infoA = str(j)
    infoB = str(k)
    infoC = str(l)
    infoD = str(m)
    infoE = str(n)

    # Historical Limits for Tape Temperature
    infoF = str(o)
    infoG = str(p)
    infoH = str(q)
    infoI = str(r)
    infoJ = str(s)
    infoK = str(t)
    infoL = str(u)

    # Historical Limits for Substrate Temperature
    infoM = str(v)
    infoN = str(w)
    infoO = str(x)
    infoP = str(y)
    infoQ = str(z)
    infoR = str(a1)
    infoS = str(a2)

    # Historical Limits for Tape Gap Measurements
    infoT = str(a3)
    infoU = str(a4)
    infoV = str(a5)
    infoW = str(a6)
    infoX = str(a7)
    infoY = str(a8)
    infoZ = str(a9)   # DistmD

    # Monitoring Params group ---------------------[C]
    infoAa = str(b1)        # Digital Bit for the enabling of Statistics on Production Parameters
    # ----------------------------------------------#
    pTagA = str(b2)         # Tag Name
    infoAb = str(b3)        # Bit to enable selected Parameter [Laser Power ! H/O Tension]
    infoAc = str(b4)        # Historical UCL
    infoAd = str(b5)        # Historical LCL
    infoAe = str(b6)        # Historical Mean
    infoAf = str(b7)        # Computed S-plot UCL
    infoAg = str(b8)        # Computed S-plot LCL
    infoAh = str(b9)        # Computed S-plot Mean
    infoAi = str(c1)        # Statistical Distribution

    # Monitoring Params Laser Angle or Dancer Load or Dancer Displacement
    pTagB = str(c2)         # Tag Name
    infoBb = str(c3)        # Bit to enable selected Parameter [Laser Angle | Dancer Load | Dancer Displacement]
    infoBc = str(c4)        # Historical UCL
    infoBd = str(c5)        # Historical LCL
    infoBe = str(c6)        # Historical Mean
    infoBf = str(c7)        # Computed S-plot UCL
    infoBg = str(c8)        # Computed S-plot LCL
    infoBh = str(c9)        # Computed S-plot Mean
    infoBi = str(d1)        # Statistical Distribution

    # Monitoring Params HO Tension
    pTagC = str(c2)         # Tag Name
    infoCb = str(c3)        # Bit to enable selected Parameter [Laser Angle | Dancer Load | Dancer Displacement]
    infoCc = str(c4)        # Historical UCL
    infoCd = str(c5)        # Historical LCL
    infoCe = str(c6)        # Historical Mean
    infoCf = str(c7)        # Computed S-plot UCL
    infoCg = str(c8)        # Computed S-plot LCL
    infoCh = str(c9)        # Computed S-plot Mean
    infoCi = str(d1)        # Statistical Distribution

    # Monitoring Params Dancer Load
    pTagD = str(c2)         # Tag Name
    infoDb = str(c3)        # Bit to enable selected Parameter [Laser Angle | Dancer Load | Dancer Displacement]
    infoDc = str(c4)        # Historical UCL
    infoDd = str(c5)        # Historical LCL
    infoDe = str(c6)        # Historical Mean
    infoDf = str(c7)        # Computed S-plot UCL
    infoDg = str(c8)        # Computed S-plot LCL
    infoDh = str(c9)        # Computed S-plot Mean
    infoDi = str(d1)        # Statistical Distribution

    with open("configSPCError.ini", 'w') as configfile:
        if not config.has_section("SHIFTS_INFO"):

            # ---------------------------- SHIFT INFO -------------------[]
            config.add_section("SHIFTS_INFO")
            config.set("SHIFTS_INFO", "Start_Day", info1)
            config.set("SHIFTS_INFO", "FinishDay", info2)
            config.set("SHIFTS_INFO", "GSize", info3)
            config.set("SHIFTS_INFO", "GStep", info4)
            config.set("SHIFTS_INFO", "UseHL", info5)
            config.set("SHIFTS_INFO", "UseSM", info6)
            config.set("SHIFTS_INFO", "Optmz", info7)

            # --------------------- TRIGGER INFO -----------------[]
            # ---------------- Parameter Roller Force -------------
            config.add_section("TRIGGERINFO")
            config.set("TRIGGERINFO", "xUCLma", info8)
            config.set("TRIGGERINFO", "xLCLma", info9)
            config.set("TRIGGERINFO", "xbmlmA", infoA)
            config.set("TRIGGERINFO", "sUCLma", infoB)
            config.set("TRIGGERINFO", "sLCLma", infoC)
            config.set("TRIGGERINFO", "sbmlmA", infoD)
            config.set("TRIGGERINFO", "distmA", infoE)
            # config.set("TRIGGERINFO", "\\n")

            # ------------------ Parameter Tape Temperature -------
            config.set("TRIGGERINFO", "xUCLmb", infoF)
            config.set("TRIGGERINFO", "xLCLmb", infoG)
            config.set("TRIGGERINFO", "xbmlmB", infoH)
            config.set("TRIGGERINFO", "sUCLmb", infoI)
            config.set("TRIGGERINFO", "sLCLmb", infoJ)
            config.set("TRIGGERINFO", "sbmlmB", infoK)
            config.set("TRIGGERINFO", "distmB", infoL)
            # config.set("TRIGGERINFO", "\\n")

            # ------------------ Parameter Substrate Tempe --------
            config.set("TRIGGERINFO", "xUCLmc", infoM)
            config.set("TRIGGERINFO", "xLCLmc", infoN)
            config.set("TRIGGERINFO", "xbmlmC", infoO)
            config.set("TRIGGERINFO", "sUCLmc", infoP)
            config.set("TRIGGERINFO", "sLCLmc", infoQ)
            config.set("TRIGGERINFO", "sbmlmC", infoR)
            config.set("TRIGGERINFO", "distmC", infoS)
            # config.set("TRIGGERINFO", "\\n")

            # ----------------- Parameter Tape Gap ----------------
            config.set("TRIGGERINFO", "xUCLmd", infoT)
            config.set("TRIGGERINFO", "xLCLmd", infoU)
            config.set("TRIGGERINFO", "xbmlmD", infoV)
            config.set("TRIGGERINFO", "sUCLmd", infoW)
            config.set("TRIGGERINFO", "sLCLmd", infoX)
            config.set("TRIGGERINFO", "sbmlmD", infoY)
            config.set("TRIGGERINFO", "distmD", infoZ)

            # --------------------- MONITOR INFO ------------------
            config.add_section("MONI_PARAMS")
            config.set("MONI_PARAMS", "Stat_param", infoAa)
            # config.set("MONI_PARAMS", "\\n")

            # ------------ Do transposition of Static Optional Params
            if pTagA == 'LPower':
                config.set("MONI_PARAMS", 'LPower', infoAb)        # Specify Param Name and Activating Bit
            config.set("MONI_PARAMS", "xUCLmf", infoAc)
            config.set("MONI_PARAMS", "xLCLmf", infoAd)
            config.set("MONI_PARAMS", "xbmlmF", infoAe)
            config.set("MONI_PARAMS", "sUCLmf", infoAf)
            config.set("MONI_PARAMS", "sLCLmf", infoAg)
            config.set("MONI_PARAMS", "sbmlmF", infoAh)
            config.set("MONI_PARAMS", "distmF", infoAi)
            # config.set("MONI_PARAMS", "\\n")

            if pTagB == "LAngle":
                config.set("MONI_PARAMS", 'LAngle', infoBb)
            config.set("MONI_PARAMS", "xUCLmg", infoBc)
            config.set("MONI_PARAMS", "xLCLmg", infoBd)
            config.set("MONI_PARAMS", "xbmlmG", infoBe)
            config.set("MONI_PARAMS", "sUCLmg", infoBf)
            config.set("MONI_PARAMS", "sLCLmg", infoBg)
            config.set("MONI_PARAMS", "sbmlmG", infoBh)
            config.set("MONI_PARAMS", "distmG", infoBi)

            # ------------ Do transposition of Static Optional Params
            if pTagC == "HTensn":
                config.set("MONI_PARAMS", "LAngle", infoCb)       # Specify Param Name and Activating Bit
            config.set("MONI_PARAMS", "xUCLmg", infoCc)
            config.set("MONI_PARAMS", "xLCLmg", infoCd)
            config.set("MONI_PARAMS", "xbmlmG", infoCe)
            config.set("MONI_PARAMS", "sUCLmg", infoCf)
            config.set("MONI_PARAMS", "sLCLmg", infoCg)
            config.set("MONI_PARAMS", "sbmlmG", infoCh)
            config.set("MONI_PARAMS", "distmG", infoCi)

            if pTagD == "DcLoad":
                config.set("MONI_PARAMS", "DcLoad", infoDb)
            config.set("MONI_PARAMS", "xUCLmg", infoDc)
            config.set("MONI_PARAMS", "xLCLmg", infoDd)
            config.set("MONI_PARAMS", "xbmlmG", infoDe)
            config.set("MONI_PARAMS", "sUCLmg", infoDf)
            config.set("MONI_PARAMS", "sLCLmg", infoDg)
            config.set("MONI_PARAMS", "sbmlmG", infoDh)
            config.set("MONI_PARAMS", "distmG", infoDi)

        config.write(configfile)
