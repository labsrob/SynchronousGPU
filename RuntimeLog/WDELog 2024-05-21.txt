# Authour: Dr Robert B. Labs


def trippWire(meanValue, maxTrigL, minTrigL, maxUSL, minLSL):

    fcolor = '#FFFFFF'  # Initialise a default color

    # Set Ring 3 Triggers with edge color ----------[R1R2R3R4]
    if (meanValue > maxTrigL and meanValue < maxUSL) or (meanValue < minTrigL and meanValue > minLSL):
        fcolor = '#F7F5AB'

    elif meanValue > maxUSL or meanValue < minLSL:
        fcolor = '#FE9CC9'
    else:
        fcolor = '#FFFFFF'          # reset to default

    return fcolor

