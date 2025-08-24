

def viewTypeD():  # Tabbed View (This is configured for remote users)
    global HeadA, HeadB, closeV, rType
    # Define run Type -----------------------------------------[]
    if runType == 1:
        rType = 'Synchro'
    elif runType == 2:
        rType = 'PostPro'
    else:
        rType = 'Standby'
    # ---------------------------------------------------------[]
    # enforce category selection integrity ---------------------#
    if analysis.entrycget(0, 'state') == 'disabled':
        analysis.entryconfig(1, state='disabled')
        analysis.entryconfig(0, state='normal')
        analysis.entryconfig(3, state='normal')

        if messagebox.askokcancel("Warning!!!", "Current Visualisation will be lost!"):
            casc_clearOut()                                     # clear out visualisation frame
            # tabbed_canvas()                                   # Call Canvas binding function
            # --- start parallel thread ------------------------#
            import autoSPCGUI as lt
            conPLC = lt.splashT(root)
            # call realtime method -----------[]
            if conPLC:
                inUseAlready.append(True)
                realTimePlay()  # Call objective function (tabbed_cascade)
            else:
                print('Failed connection...')
            # --------------------------------------------------[]
            exit_bit.append(0)                                  # Keep a byte into empty list
        else:
            analysis.entryconfig(0, state='disabled')     # revert to original state
            analysis.entryconfig(1, state='normal')       # revert to original state

        HeadA, HeadB, closeV = 0, 1, 0                          # call embedded functions
        realTimePlay()                                          # Call objective function

    elif analysis.entrycget(3, 'state') == 'disabled':
        analysis.entryconfig(1, state='disabled')
        analysis.entryconfig(0, state='normal')
        analysis.entryconfig(3, state='normal')

        # --- start parallel thread ---------------------------------#
        import autoSPCGUI as lt
        conPLC = lt.splashT(root)
        # call realtime method -----------[]
        if conPLC:
            inUseAlready.append(True)
            realTimePlay()  # Call objective function (tabbed_cascade)
        else:
            print('Failed connection...')
        # ----------------------------------------------------------[]
        exit_bit.append(0)
        HeadA, HeadB, closeV = 0, 1, 0  # call embedded functions

    elif (analysis.entrycget(0, 'state') == 'normal'
          and analysis.entrycget(1, 'state') == 'normal'
          and analysis.entrycget(3, 'state') == 'normal'):
        analysis.entryconfig(1, state='disabled')
        analysis.entryconfig(0, state='normal')
        analysis.entryconfig(3, state='normal')

        # --- start parallel thread ---------------------------------#
        import autoSPCGUI as lt
        conPLC = lt.splashT(root)
        # call realtime method -----------[]
        if conPLC:
            inUseAlready.append(True)
            realTimePlay()  # Call objective function (tabbed_cascade)
        else:
            print('Failed connection...')
        # ----------------------------------------------------------[]
        exit_bit.append(0)
        HeadA, HeadB, closeV = 0, 1, 0

    else:
        analysis.entryconfig(1, state='normal')
        HeadA, HeadB, closeV = 0, 0, 1
        errorChoice()  # raise user exception
        print('Invalid! View selection before process parameter..')

    return HeadA, HeadB, closeV