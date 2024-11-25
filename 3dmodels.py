# import time
#
# import matplotlib.pyplot as plt
# import numpy as np
#
# fig = plt.figure()
# ax = fig.add_subplot(projection='3d')
#
# # Make the X, Y meshgrid.
# xs = np.linspace(-1, 1, 50)
# ys = np.linspace(-1, 1, 50)
# X, Y = np.meshgrid(xs, ys)
#
# # Set the z axis limits, so they aren't recalculated each frame.
# ax.set_zlim(-1, 1)
#
# # Begin plotting.
# wframe = None
# tstart = time.time()
#
# for phi in np.linspace(0, 180. / np.pi, 100):
#
#     # If a line collection is already remove it before drawing.
#     if wframe:
#         wframe.remove()
#
#     # Generate data.
#     Z = np.cos(2 * np.pi * X + phi) * (1 - np.hypot(X, Y))
#
#     # Plot the new wireframe and pause briefly before continuing.
#     wframe = ax.plot_wireframe(X, Y, Z, rstride=2, cstride=2)
#     plt.pause(.9)
#
# print('Average FPS: %f' % (100 / (time.time() - tstart)))

# ---------------------------------------------------------------
# import tkinter as tk
# from tkinter import ttk
#
# def clear(event):
#     _value.set('???')
#
# def set_statusBar(event):
#     _value.set(widget_name[event.widget])
#
#
# root = tk.Tk()
#
# _value = tk.StringVar()
# _value.set('Status Bar...')
#
# entry1 = ttk.Entry(root)
# dummy = ttk.Entry(root)
# entry2 = ttk.Entry(root)
#
# widget_name = {entry1:'Entry 1 has focus', entry2:'Entry 2 has focus'}
#
# statusBar = ttk.Label(root, textvariable=_value).place(x=10, y=80)
#
# entry1.grid()
# dummy.grid()
# entry2.grid()
#
# # statusBar.grid()
#
# entry1.bind('<FocusIn>', set_statusBar)
# entry1.bind('<FocusOut>', clear)
#
# entry2.bind('<FocusIn>', set_statusBar)
# entry2.bind('<FocusOut>', clear)
#
# root.mainloop()

# ---------------------------------------------------------

# from tkinter import *
#
# def prep():
#     global label
#
#     if check_1.get(): # lPwr | lAng |
#         label = 'LP'
#     else:
#         label = '??'
#     Label(root, text=label).place(x=200, y=200)
#     # print(label)
#
#
# root = Tk()
# root.geometry('450x350')
# # Initialise variable ---
# label = '??'
# check_1 = IntVar()
#
# # check_but_1 = Checkbutton(root, text = 'Listening to Music', variable = check_1, onvalue = 1, offvalue = 0, command=check1Clicked)
#
# # ------------------------------------------
# ex1 = Checkbutton(root, text="Laser Power", variable=check_1, command=prep)
# # ex1.bind('<Button-1>', prep)
# ex1.place(x=200, y=100)
#
# Label(root, text=label).place(x=200, y=200)
#
# mainloop()

# -------------------------------------------------

# -----------------------------------------------
import matplotlib.pyplot as plt

time_discret = range(1, 13)                                                     # x data
avg_ycordina = [1, 2, 5, 8, 19, 21, 23, 25, 11, 13, 15, 17]                     # y value data (position data)
avg_gapvalue = [110, 105, 94, 61, 66, 31, 222, 23, 98, 110, 188, 143]           # s value data showing the magnitude

plt.scatter(x=time_discret, y=avg_ycordina, s=avg_gapvalue, c='b', alpha=0.5, marker='D')
plt.xlabel("Axial Position /mt")
plt.ylabel("Tape Layers")
plt.show()

#-----------------------------------------------

# import matplotlib.pyplot as plt
# import pandas as pd
# import numpy as np
#
# np.random.seed(42)
# N = 12
#
# x = np.random.normal(170, 20, N)
# z = x + np.random.normal(5, 25, N)
# print('T1', len(x))
#
#
# months = range(1, 13)
# axiapos = [8, 12, 15, 20, 21, 23, 24, 28, 30, 32, 34, 41]
# tapegap = [110, 105, 94, 61, 66, 31, 222, 23, 98, 110, 188, 143]
#
# colors = np.random.rand(N)
# area = (25 * np.random.rand(N))**2
#
# df = pd.DataFrame({'X': axiapos, 'Y': tapegap, 'Z':z, 'Colors': colors, "bubble_size": area})
# df.head()
#
# plt.style.use('ggplot')
# plt.scatter('X', 'Y', s='bubble_size', c=colors, alpha=0.5, data=df)   # y, zs=0, zdir='y' | s='bubble_size',
# plt.xlabel("Axial Pipe Position ==>", size=16)
# plt.ylabel("Area (PiR^2) ==>", size=16)
# plt.show()

# -----------------------------------------------------
# from mpl_toolkits import mplot3d
# import numpy as np
# import matplotlib.pyplot as plt
# import random
#
# fig = plt.figure(figsize=(12, 12))
# ax = fig.add_subplot(projection='3d')
#
# # sequence_containing_x_vals = list(range(0, 100))
# # sequence_containing_y_vals = list(range(0, 100))
# # sequence_containing_z_vals = list(range(0, 100))
#
# zdata = 15 * np.random.random(100)
# xdata = np.sin(zdata) + 0.1 * np.random.randn(100)
# ydata = np.cos(zdata) + 0.1 * np.random.randn(100)
# ax.scatter3D(xdata, ydata, zdata);
#
# # random.shuffle(sequence_containing_x_vals)
# # random.shuffle(sequence_containing_y_vals)
# # random.shuffle(sequence_containing_z_vals)
# #
# # ax.scatter(sequence_containing_x_vals, sequence_containing_y_vals, sequence_containing_z_vals)
# plt.show()

# ------------------------------------------------------

# time_syntesr = np.array([np.ones(6) * i for i in range(2)]).flatten()
# print('TP1:', len(time_syntesr))
# time_discret = range(1, 13)                                                     # x data
# avg_ycordina = [8, 12, 15, 18, 17, 13, 14, 10, 17, 13, 14, 11]                  # y value data (position data)
# avg_gapvalue = [110, 105, 94, 61, 66, 31, 222, 23, 98, 110, 288, 143]           # s value data showing the magnitude
#
#
# # df = pd.DataFrame({"time": t, "x": a[:, 0], "y": a[:, 1], "z": a[:, 2], 'Colors': colors, "bubble_size": gap_size})
# df = pd.DataFrame({"time": time_syntesr, "x": time_discret, "y": avg_ycordina, "z": avg_gapvalue, 'Colors': colors})
#
# def update_graph(num):
#     data=df[df['time'] == num]
#     graph._offsets3d = (data.x, data.y, data.z)
#     title.set_text('3D Test, time={}'.format(num))
#
#
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# title = ax.set_title('3D Test')
#
# data = df[df['time'] == 0]
# graph = ax.scatter(data.x, data.y, data.z, c='b', linewidth=0.7, alpha=0.4, marker="s")
# # ani = matplotlib.animation.FuncAnimation(fig, update_graph, 19, interval=140, blit=False)
#
# plt.show()

# ------------------------------------------------------
import matplotlib.pyplot as plt
import numpy as np

# Fixing random state for reproducibility
np.random.seed(19680801)

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

avg_gap = [10, 105, 94, 61, 66, 31, 222, 23, 98, 110, 288, 143, 66, 31, 22, 16, 99, 26, 72, 17]
colors = ['r', 'g', 'b', 'y']
yticks = [3, 2, 1, 0]

for c, k in zip(colors, yticks):
    # Generate the random data for the y=k 'layer'.
    xs = np.arange(20)
    ys = np.random.rand(20)

    # You can provide either a single color or an array with the same length as
    # xs and ys. To demonstrate this, we color the first bar of each set cyan.
    cs = [c] * len(xs)
    cs[0] = 'c'

    # Plot the bar graph given by xs and ys on the plane y=k with 80% opacity.
    ax.scatter(xs, ys, zs=k, zdir='y', s=avg_gap, color=cs, alpha=0.5, marker='D', label='Layer Data'+str(k+1))
    # ax.bar(xs, ys, zs=k, zdir='y', color=cs, alpha=0.8, label='Layer Data' + str(k))

ax.legend()
ax.set_xlabel('X - Pipe Distance /mt')
ax.set_ylabel('Z - Discrete Layers')
ax.set_zlabel('Y - Values')

# On the y-axis let's only label the discrete values that we have data for.
ax.set_yticks(yticks)
ax.view_init(elev=20., azim=-35, roll=0)

plt.show()


# --------------------------------------------------------- #
import matplotlib.pyplot as plt
import numpy as np

ax = plt.figure().add_subplot(projection='3d')

# Plot scatterplot data (20 2D points per colour) on the x and z axes.
colors = ('r', 'g', 'b', 'k')

# Plot a sin curve using the x and y axes.
x = np.linspace(0, 1, 100)
y = np.sin(x * 2 * np.pi) / 2 + 0.5
ax.plot(x, y, zs=0, zdir='z', label='Cumulated curve')

# Fixing random state for reproducibility
np.random.seed(1801)

x = np.random.sample(20 * len(colors))   # range(1, 81)
y = np.random.sample(20 * len(colors))
avg_gap = np.random.sample(20 * len(colors))*100

c_list = []
for c in colors:
    c_list.extend([c] * 20)

# By using zdir='y', the y value of these points is fixed to the zs value 0
print('TP:', y)
print('TP2:', len(y))
ax.scatter(x, y, zs=0, zdir='y', s=avg_gap, c=c_list, alpha=0.5, marker='D', label='Cumulated Gap')

# Make legend, set axes limits and labels
ax.legend()
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_zlim(0, 1)
ax.set_xlabel('X - Pipe Distance /mt')
ax.set_ylabel('Y - Gap Spread / sq mtr')
ax.set_zlabel('Z - Discrete Layers')

# Customize the view angle so it's easier to see that the scatter points lie
# on the plane y=0
# ax.view_init(elev=20., azim=-35, roll=0)

plt.show()