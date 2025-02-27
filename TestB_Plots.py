# TEst Scratch file

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_interactions import ioff, panhandler, zoom_factory
from matplotlib.figure import Figure
from matplotlib.colors import ListedColormap
import plotly.express as px
import pandas as pd

from matplotlib.colors import Normalize

path = ('C:\\Users\\DevEnv\\OneDrive - Magma Global LTD\\Documents\\Development DOCUMENTS\\Technical Reqs Docs\\Tape Gap Measurements\\testFile.csv')
csv_file = (path)

df = pd.read_csv(csv_file)
print('Test Print', df.head())
print('Test2:', df['VoidPercent'])
# df['VoidPercent'].plot()

import seaborn as sns

# construct custom cmap -----
# flatui = ["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e", "#2ecc71"]
# my_cmap = ListedColormap(sns.color_palette(flatui).as_hex())

colors = np.random.randint(50, 101, size=(367))
# colors = np.random.rand(367)

'''

Ref: https://matplotlib.org/stable/users/explain/colors/colormaps.html
'viridis', 'viridis_r', 'plasma' 'inferno', 'magma', 'cividis', 'Greens', 'Blues',
'winter', 'hsv', 'jet', 'cool', 'hot', 'OrRd', 'rainbow'

'''
dataX = df['sDistanceX']
dataY = df['Pipe LayersY']
dataZ = df['VoidPercent']

# plot the data -----------------------[]
f = plt.figure(figsize=(12, 8), dpi=100)
f.subplots_adjust(left=0.022, bottom=0.05, right=0.993, top=0.936, wspace=0.1, hspace=0.17)
ax1 = f.add_subplot(2, 1, 1)
ax2 = f.add_subplot(2, 1, 2)


# Enable scroll to zoom with the help of MPL
# Interactions library function like ioff and zoom_factory.
# with plt.ioff():
#    ax1 = f.add_subplot(2, 1, 1)
#    ax2 = f.add_subplot(2, 1, 2)

scatter = ax1.scatter(data=df, x='sDistanceX', y='Pipe LayersY', s='VoidPercent', marker='s', c=colors, cmap='rainbow', label='Gap Volume')

ax1.set_facecolor("green")
ax1.set_xlabel('Sample Distance')
ax1.set_ylabel('Tape on Pipe Layer')
ax1.set_title('Tape Gap Volume Mapping')
# Useful utilities ---------#
zoom_factory(ax1)           # Allow image zooming
# pan_ = panhandler(ax1)    # Allow image panning

rlabel = ['< 0', '0 - 2', '2 - 4', '4 - 6', '6 - 8',  '8 - 9', '9 - 10', 'above']
ax1.legend(handles=scatter.legend_elements()[0], labels=rlabel, title='Void Map (%)')
# ax1.colorbar()

# --------------------------------[]
ax2.plot(dataX, dataY, marker='|', color='w', linestyle='', label='Ramp Volume')

ax2.set_facecolor("blue")
ax2.legend()
ax2.set_xlabel('Sample Distance')
ax2.set_ylabel('Tape on Pipe Layer')
ax2.set_title('Ramp Position Mapping')
# Useful utilities ---------#
zoom_factory(ax2)           # Allow image zooming
# pan_ = panhandler(ax2)     # Allow image panning

plt.show()


# --------------------------------------------------------------------------------------------------------------------[]

# # Importing required library
# from mpl_interactions import ioff, panhandler, zoom_factory
# import matplotlib.pyplot as plt
#
# # creating the dataset
# data = {'Operating System': 10, 'Data Structure': 7,
# 		'Machine Learning': 14, 'Deep Learning': 12}
#
# courses = list(data.keys())
# values = list(data.values())
#
# # Enable scroll to zoom with the help of MPL
# # Interactions library function like ioff and zoom_factory.
# with plt.ioff():
# 	figure, axis = plt.subplots()
#
# # creating the bar plot
# plt.xlabel("Courses offered")
# plt.ylabel("No. of students enrolled")
# plt.title("Students enrolled in different courses")
#
# plt.bar(courses, values, color='green', width=0.4)
# disconnect_zoom = zoom_factory(axis)
#
# # Enable scrolling and panning with the help of MPL
# # Interactions library function like panhandler.
# pan_handler = panhandler(figure)
# plt.show()

# ==================================================================================================================[]
# import matplotlib.pyplot as plt
# from matplotlib.legend_handler import HandlerTuple
# import numpy as np
#
# fig, ax = plt.subplots()
#
# radii = [1, 2, 3, 4, 5]
# angle = np.linspace(0, 2 * np.pi, 150)
#
# cmap = plt.get_cmap('viridis_r')
# norm = plt.Normalize(radii[0], radii[-1])
#
# lines = []  # list of lines to be used for the legend
#
# for radius in radii:
#      x = radius * np.cos(angle)
#      y = radius * np.sin(angle)
#      line, = ax.plot(x, y, color=cmap(norm(radius)))
#      lines.append(line)
#
# ax.legend(handles=[tuple(lines)], labels=['Radius'], handlelength=5, handler_map={tuple: HandlerTuple(ndivide=None, pad=0)})
# ax.set_aspect('equal')
#
# plt.tight_layout()
# plt.show()

# -------------------------------------------------------------------------------------------------------------------[]
# N = 45
# x, y = np.random.rand(2, N)
# c = np.random.randint(1, 5, size=N)
# s = np.random.randint(10, 220, size=N)
#
# fig, ax = plt.subplots()
#
# scatter = ax.scatter(x, y, c=c, s=s)
#
# # produce a legend with the unique colors from the scatter
# legend1 = ax.legend(*scatter.legend_elements(), loc="lower left", title="Classes")
# ax.add_artist(legend1)
#
# # produce a legend with a cross-section of sizes from the scatter
# handles, labels = scatter.legend_elements(prop="sizes", alpha=0.6)
# legend2 = ax.legend(handles, labels, loc="upper right", title="Sizes")
#
# plt.show()

# -------------------------------------------------------------------------------------------------------------------[]
# import matplotlib.pyplot as plt
# from matplotlib.colors import ListedColormap
#
# x = [1, 3, 4, 6, 7, 9]
# y = [0, 0, 5, 8, 8, 8]
#
# classes = ['A', 'B', 'C']
# values = [0, 0, 1, 2, 2, 2]
#
# colors = ListedColormap(['r','b','g'])
#
# scatter = plt.scatter(x, y, c=values, cmap=colors)
# plt.legend(handles=scatter.legend_elements()[0], labels=classes)
#
# plt.show()