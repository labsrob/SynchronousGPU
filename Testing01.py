import neurokit2 as nk
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.signal import find_peaks
import numpy as np

#create realistic data
data = nk.ecg_simulate(duration = 50, sampling_rate = 100, noise = 0.05, random_state = 1)

#scale data
scaler = MinMaxScaler()
scaled_arr = scaler.fit_transform(data.reshape(-1,1))
#find peaks
peak = find_peaks(scaled_arr.squeeze(), height = .66, distance = 60, prominence = .5)

ymin, ymax = min(scaled_arr), max(scaled_arr)
fig = plt.figure()
ax = fig.add_subplot(111)
line, = ax.plot([],[], lw=2)
scat = ax.scatter([], [], s=20, facecolor='red')

idx = [(s,e) for s,e in zip(np.arange(0,len(scaled_arr), 1), np.arange(499,len(scaled_arr)+1, 1))]

def init():
    line.set_data([], [])
    return line,

def animate(i):
  id = idx[i]
  #print(id[0], id[1])
  line.set_data(np.arange(id[0], id[1]), scaled_arr[id[0]:id[1]])
  x = peak[0][(peak[0] > id[0]) & (peak[0] < id[1])]
  y = peak[1]['peak_heights'][(peak[0] > id[0]) & (peak[0] < id[1])]
  #scat.set_offsets(x, y)
  ax.scatter(x, y, s=20, c='red')
  ax.set_xlim(id[0], id[1])
  ax.set_ylim(ymin, ymax)
  return line,scat

anim = FuncAnimation(fig, animate, init_func=init, frames=50, interval=50, blit=True)

plt.show()
