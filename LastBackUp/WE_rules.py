# ------------------------------------------------------------------------------#
#  Script: Western Electric Rules as applicable to Magma CF/PEEK Process
#  Author: Robert B. Labs
#  Date of Integration: 14/08/2024
#
# -------------------------------------------------------------------------------#
time_sequenc = 2        # 2 secs
window_tspan = 1800     # 30 min
window_Xmax = 29        # 30 - 1 for the minimum X-axis
# db_freq = 1
# Production Process Parameter ----#
_lp3x, _lp6x, _s3lp, _s6lp = [], [], [], []
_la3x, _la6x, _s3la, _s6la = [], [], [], []
# Quality Process Parameter ------ #
_rf3x, _rf6x, _s3rf, _s6rf = [], [], [], []
_tt3x, _tt6x, _s3tt, _s6tt = [], [], [], []
_dt3x, _dt6x, _s3dt, _s6dt = [], [], [], []
_tg3x, _tg6x, _s3tg, _s6tg = [], [], [], []

# Initialise trig variables Evaluate individual process signals ---[]
triglp1, triglp2, triglp3, triglp4 = 0, 0, 0, 0
trigla1, trigla2, trigla3, trigla4 = 0, 0, 0, 0
# -------------------------------------------- [RF]
trigrf1, trigrf2, trigrf3, trigrf4 = 0, 0, 0, 0
trigrf5, trigrf6, trigrf7, trigrf8 = 0, 0, 0, 0
trigrf9, trigrf10, trigrf11, trigrf12 = 0, 0, 0, 0
trigrf13, trigrf14, trigrf15, trigrf16 = 0, 0, 0, 0
# -------------------------------------------- [TT]
trigtt1, trigtt2, trigtt3, trigtt4 = 0, 0, 0, 0
trigtt5, trigtt6, trigtt7, trigtt8 = 0, 0, 0, 0
trigtt9, trigtt10, trigtt11, trigtt12 = 0, 0, 0, 0
trigrtt3, trigtt14, trigtt15, trigtt16 = 0, 0, 0, 0
# -------------------------------------------- [DT]
trigdt1, trigdt2, trigdt3, trigdt4 = 0, 0, 0, 0
trigdt5, trigdt6, trigdt7, trigdt8 = 0, 0, 0, 0
trigdt9, trigdt10, trigdt11, trigdt12 = 0, 0, 0, 0
trigdt13, trigdt14, trigdt15, trigdt16 = 0, 0, 0, 0
# -------------------------------------------- [TG]
trigtg1, trigtg2, trigtg3, trigtg4 = 0, 0, 0, 0
trigtg5, trigtg6, trigtg7, trigtg8 = 0, 0, 0, 0


# Capture points above Sigma threshold values --------------------------[A]
def evaluate_pSigma(lp1, lp2, lp3, lp4, s3L, s3U, s6L, s6U, db_freq):
    """
    lp1: mean values derived from rolling/moving average
    lp2
    lp3
    lp4
    UCL/LCL
    USL/LSL
    """
    rt_value = [lp1, lp2, lp3, lp4]                 # Obtained the Process values instance
    above_s3U = [i for i in rt_value if i > s3U]    # Search for +3Sigma Violations
    below_s3L = [j for j in rt_value if j < s3L]    # Search for -3Sigma Violations
    above_s6U = [k for k in rt_value if k > s6U]    # Search for +6Sigma Violations
    below_s6L = [l for l in rt_value if l < s6L]    # Search for -6Sigma Violations

    # Evaluate points above 6 sigma -----------------------------------[]
    # _lp3x, _lp6x, _s3lp, _s6lp
    if above_s3U:
        # Capture violations' xID and yID
        _lp3x.append(db_freq)
        _s3lp.append(above_s3U)
        if len(_s3lp) >= 2 and _lp3x >= (db_freq - window_Xmax):    # violation is within the screen view range
            # send exception to SCADA
            print('Warning alert...')
            # activate visual alert
    elif below_s3L:
        # Capture violations' x and y Identities
        _lp3x.append(db_freq)
        _s3lp.append(below_s3L)
        if len(_s3lp) >= 2 and _lp3x >= (db_freq - window_Xmax):    # violation is within the screen view range
            # send exception to SCADA
            print('Warning alert...')
            # activate visual alert
    elif above_s6U:
        # Capture violations' xID and yID
        _lp6x.append(db_freq)
        _s6lp.append(above_s6U)
        if len(_s6lp) >= 2 and _lp6x >= (db_freq - window_Xmax):    # violation is within the screen view range
            # send exception to SCADA
            print('Sig6 Violations:', above_s6U)
            # activate visual alert
    elif below_s6L:
        # Capture violations' x and y Identities
        _lp6x.append(db_freq)
        _s6lp.append(below_s6L)
        if len(_s6lp) >= 2 and _lp6x >= (db_freq - window_Xmax):    # violation is within the screen view range
            # send exception to SCADA
            print('Sig6 Violations:', below_s6L)
            # activate visual alert

    else:
        print('Process is under SPC control..')

# --------------------------------------------------------------------------------------------------------------#

# Capture points above Confidence Interval (Std Error SE) d values --------------------------[A]
def evaluate_StdError(lp1, lp2, lp3, lp4, s3L, s3U, s6L, s6U, db_freq):
    """
    lp1: mean values derived from rolling/moving average
    lp2
    lp3
    lp4
    UCL/LCL
    USL/LSL
    Confidence interval (SE) x = 3*Sigma/Sqr(n)
    """
    rt_value = [lp1, lp2, lp3, lp4]                 # Obtained the Process values instance
    above_s3U = [a for a in rt_value if a > s3U]    # Search for +3Sigma Violations
    below_s3L = [b for b in rt_value if b < s3L]    # Search for -3Sigma Violations
    above_s6U = [c for c in rt_value if c > s6U]    # Search for +6Sigma Violations
    below_s6L = [d for d in rt_value if d < s6L]    # Search for -6Sigma Violations

    # Evaluate points above 6 sigma -----------------------------------[]
    # _lp3x, _lp6x, _s3lp, _s6lp
    if above_s3U:
        # Capture violations' xID and yID
        _lp3x.append(db_freq)
        _s3lp.append(above_s3U)
        if len(_s3lp) >= 2 and _lp3x >= (db_freq - window_Xmax):    # violation is within the screen view range
            # send exception to SCADA
            print('Warning alert...')
            # activate visual alert
    elif below_s3L:
        # Capture violations' x and y Identities
        _lp3x.append(db_freq)
        _s3lp.append(below_s3L)
        if len(_s3lp) >= 2 and _lp3x >= (db_freq - window_Xmax):    # violation is within the screen view range
            # send exception to SCADA
            print('Warning alert...')
            # activate visual alert
    elif above_s6U:
        # Capture violations' xID and yID
        _lp6x.append(db_freq)
        _s6lp.append(above_s6U)
        if len(_s6lp) >= 2 and _lp6x >= (db_freq - window_Xmax):    # violation is within the screen view range
            # send exception to SCADA
            print('Sig6 Violations:', above_s6U)
            # activate visual alert
    elif below_s6L:
        # Capture violations' x and y Identities
        _lp6x.append(db_freq)
        _s6lp.append(below_s6L)
        if len(_s6lp) >= 2 and _lp6x >= (db_freq - window_Xmax):    # violation is within the screen view range
            # send exception to SCADA
            print('Sig6 Violations:', below_s6L)
            # activate visual alert

    else:
        print('Process is under SPC control..')


