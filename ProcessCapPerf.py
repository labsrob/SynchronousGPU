# Process capabilityu and proesss performance per monitoring params

# Process capability ------------------[]
A3 = [0.975, 0.789, 0.680, 0.606]  # 10, 15, 20, 25 sample sizes respectively
B3 = [0.284, 0.428, 0.510, 0.565]  # 10, 15, 20, 25 sample sizes respectively
B4 = [1.716, 1.572, 1.490, 1.435]


def processCap(meanP, stdDev, sampSiz):
    # Evaluate constants with defined sample size --
    if sampSiz == 10:
        const1 = A3[0]
        const2 = B3[0]
        const3 = B4[0]
    elif sampSiz == 15:
        const1 = A3[1]
        const2 = B3[1]
        const3 = B4[1]
    elif sampSiz == 20:
        const1 = A3[2]
        const2 = B3[2]
        const3 = B4[2]
    elif sampSiz == 25:
        const1 = A3[3]
        const2 = B3[3]
        const3 = B4[3]
    else:
        print('Sample Size undefined!, Exiting...')
        exit()

    # ' Cpk indicate both the lower and upper limit values in the process'
    if stdDev != 0 and meanP != 0:
        xUSL = meanP + (const1 * stdDev * 2)        # 3sigma *2 = 6 Sigma plus mean line
        xLSL = meanP - (const1 * stdDev * 2)        # 3sigma *2 = 6 Sigma plus mean line

        xUCL = meanP + (const1 * stdDev)            # Upper control limits @ 3 sigma
        xLCL = meanP - (const1 * stdDev)            # Lower control Limits @ 3 sigma

        sUCL = (const3 * stdDev)                    # Upper control limits of 1 std dev
        sLCL = (const2 * stdDev)                    # Lower control limits of 1 Std dev

        # Compute for process capability -------------------------------[]
        # TODO - Cpk uses the WITHIN (group automatic) standard deviation
        CpkL = (meanP - xLSL) / (3 * stdDev)  # Ppkl, rational subgroup (miniTab)
        CpkU = (xUSL - meanP) / (3 * stdDev)  # Ppku, of rational subgroup (miniTab)
        Cpro = (xUSL - xLSL) / (6 * stdDev)   # Pp, StDev is for a subgroup of >11 (n=20)

    else:
        # if Mean & Std Dev are Zero - Error handling -------------------[]
        xUSL = meanP + (const1 * stdDev * 2)
        xLSL = meanP - (const1 * stdDev * 2)
        xUCL = meanP + (const1 * stdDev)
        xLCL = meanP - (const1 * stdDev)
        sUCL = (const3 * stdDev)                # 1.490
        sLCL = (const2 * stdDev)                # 0.510
        CpkL = (meanP - xLSL) / (3 * stdDev)
        CpkU = (xUSL - meanP) / (3 * stdDev)
        Cpro = (xUSL - xLSL) / (6 * stdDev)

    return xUSL, xLSL, xUCL, xLCL, sUCL, sLCL, CpkL, CpkU, Cpro


def hisCap(meanP, stdDev, LSL, USL):

    if stdDev != 0:
        # TODO - Ppk uses the OVERALL (historical) standard deviation
        PpkL = (meanP - LSL) / (3 * stdDev)           # Ppkl, rational subgroup
        PpkU = (USL - meanP) / (3 * stdDev)           # Ppku, of rational subgroup
        Ppro = (USL - LSL) / (6 * stdDev)             # Pp, StDev is for a subgroup of >11 (n=20)
    else:
        stdDev = 0.68
        meanP = 0.0
        # NaN Error handling -----------------------------------------------[]
        PpkL = (meanP - LSL) / (3 * stdDev)
        PpkU = (USL - meanP) / (3 * stdDev)
        Ppro = (USL - LSL) / (6 * stdDev)

    return PpkL, PpkU, Ppro