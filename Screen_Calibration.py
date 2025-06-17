#  DETECT THE NUMBER OF ATTACHED SCREENS TO THE SERVER
# AND ALLOW SPC TO CHOOSE THE BEST SCREEN RESOLUTION
# FOR CASCADE OR TABBED VISUALISATION
#
#
#
# Algorithm improved by Robbie Labs.

# -----------------------------------------[]
import ctypes
user = ctypes.windll.user32

class RECT(ctypes.Structure):
  _fields_ = [
    ('left', ctypes.c_long),
    ('top', ctypes.c_long),
    ('right', ctypes.c_long),
    ('bottom', ctypes.c_long)
    ]
  def dump(self):
    return [int(val) for val in (self.left, self.top, self.right, self.bottom)]

class MONITORINFO(ctypes.Structure):
  _fields_ = [
    ('cbSize', ctypes.c_ulong),
    ('rcMonitor', RECT),
    ('rcWork', RECT),
    ('dwFlags', ctypes.c_ulong)
    ]

def get_monitors():
  retval = []
  CBFUNC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(RECT), ctypes.c_double)
  def cb(hMonitor, hdcMonitor, lprcMonitor, dwData):
    r = lprcMonitor.contents
    #print("cb: %s %s %s %s %s %s %s %s" % (hMonitor, type(hMonitor), hdcMonitor, type(hdcMonitor), lprcMonitor, type(lprcMonitor), dwData, type(dwData)))
    data = [hMonitor]
    data.append(r.dump())
    retval.append(data)
    return 1
  cbfunc = CBFUNC(cb)
  temp = user.EnumDisplayMonitors(0, 0, cbfunc, 0)
  #print(temp)
  return retval

def monitor_areas():
  retval = []
  monitors = get_monitors()
  for hMonitor, extents in monitors:
    data = [hMonitor]
    mi = MONITORINFO()
    mi.cbSize = ctypes.sizeof(MONITORINFO)
    mi.rcMonitor = RECT()
    mi.rcWork = RECT()
    res = user.GetMonitorInfoA(hMonitor, ctypes.byref(mi))
    data = mi.rcMonitor.dump()
#    data.append(mi.rcWork.dump())
    retval.append(data)
  return retval


# if __name__ == "__main__":
def getSCRdetails():
    # print(monitor_areas())

    detectScr = monitor_areas()
    detSCR = len(detectScr)

    if detSCR == 1:
        print('Mono-screen(' + str(detSCR) + ') configuration, suitable for DNV/MGM Tabbed visualisation only')
        T1 = detectScr[0][2]
        T2 = 0
        T3 = 0
        T4 = 0
        T5 = 0
        T6 = 0
        T7 = 0
        T8 = 0
        print('Screen Width:', T1)

    elif 1 < detSCR < 3:  # greater than 1 but less than 3
        print('Multi-screen(' + str(detSCR) + ') configuration, but not valid for DNV/MGM Cascade.')
        T1 = detectScr[0][2]
        T2 = detectScr[1][2]
        T3 = 0
        T4 = 0
        T5 = 0
        T6 = 0
        T7 = 0
        T8 = 0
        print('Screen Widths:', T1, T2, T3)

    elif detSCR == 4:
        print('Multi-screen(' + str(detSCR) + ') configuration, suitable for DNV Cascade visualisation')
        T1 = detectScr[0][2]
        T2 = detectScr[1][2]
        T3 = detectScr[2][2]
        T4 = detectScr[3][2]
        T5 = 0
        T6 = 0
        T7 = 0
        T8 = 0
        print('Screen Widths:', T1, T2, T3, T4)

    elif 4 < detSCR < 8:
        print('Multi-screen(' + str(detSCR) + ') configuration, not suitable for MGM Cascade visualisation')
        T1 = detectScr[0][2]
        T2 = detectScr[1][2]
        T3 = detectScr[2][2]
        T4 = detectScr[3][2]
        T5 = detectScr[4][2]
        T6 = detectScr[5][2]
        T7 = detectScr[6][2]
        T8 = 0
        print('Screen Widths:', T1, T2, T3, T4, T5, T6, T7)

    else:
        print('Multi-screen(' + str(detSCR) + ') configuration, suitable for MGM Cascade visualisation')
        T1 = detectScr[0][2]
        T2 = detectScr[1][2]
        T3 = detectScr[2][2]
        T4 = detectScr[3][2]
        T5 = detectScr[4][2]
        T6 = detectScr[5][2]
        T7 = detectScr[6][2]
        T8 = detectScr[7][2]
        print('Screen Widths:', T1, T2, T3, T4, T5, T6, T7, T8)

    return detSCR, T1, T2, T3, T4, T5, T6, T7, T8