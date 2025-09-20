from scipy import signal
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def norm_factor_Gauss_window(s, dt):
    numer = np.arange(-3 * s, 3 * s + dt, dt)
    multiplic_fac = np.exp(-(numer) ** 2 / (2 * s ** 2))
    norm_factor = np.sum(multiplic_fac)
    window = len(multiplic_fac)

    return window, multiplic_fac, norm_factor


# # Create dataframe for MRE
# aa = np.sin(np.linspace(0, 2 * np.pi, 1000000)) + 0.15 * np.random.rand(1000000)
# df = pd.DataFrame({'x': aa})
#
# hmany = 10
# dt = 1  # ['seconds']
# s = hmany * dt  # Define averaging window size ['s']
#
# # Estimate multip factor, normalizatoon factor etc
# window, multiplic_fac, norm_factor = norm_factor_Gauss_window(s, dt)
#
# # averaged timeseries
#
# res2 = (1 / norm_factor) * signal.fftconvolve(df.x.values, multiplic_fac[::-1], 'same')
#
# # Plot
# plt.plot(df.x[0:2000])
# plt.plot(res2[0:2000])

# ------------------------------------------ thid fid fid fnd dif  nimjdfidnfiu ig
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
rc('mathtext', default='regular')

fig = plt.figure()
a2 = fig.add_subplot(111)

a2.plot(time, Swdown, '-', label = 'Swdown')
a2.plot(time, Rn, '-', label = 'Rn')

ax3 = a2.twinx()
ax3.plot(time, temp, '-r', label = 'temp')

a2.legend(loc=0)
a2.grid()
a2.set_xlabel("Time (h)")
a2.set_ylabel(r"Radiation ($MJ\,m^{-2}\,d^{-1}$)")

ax2.set_ylabel(r"Temperature ($^\circ$C)")
ax2.set_ylim(0, 35)
ax.set_ylim(-20,100)
plt.show()


# --------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
rc('mathtext', default='regular')

fig = plt.figure()
ax = fig.add_subplot(111)
a2.plot(time, Swdown, '-', label = 'Swdown')
a2.plot(time, Rn, '-', label = 'Rn')

a3 = ax.twinx()
a3.plot(time, temp, '-r', label = 'temp')

a2.legend(loc=0)
a2.grid()
a2.set_xlabel("Time (h)")
a2.set_ylabel(r"Radiation ($MJ\,m^{-2}\,d^{-1}$)")

a3.set_ylabel(r"Temperature ($^\circ$C)")
a3.set_ylim(0, 35)

a2.set_ylim(-20,100)
plt.show()
