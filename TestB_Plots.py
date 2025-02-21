# TEst Scratch file

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
# from matplotlib.colors import Normalize

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

# ---------------------------------------[]
# if int(dataZ) <= 1.0:
#     dColor = 'g'
# elif 1.0 <= int(dataZ) <= 2.0:
#     dColor = 'b'
# elif 2.1 <= int(dataZ) <= 4.0:
#     dColor = 'y'
# elif 4.1 <= int(dataZ) <= 6.0:
#     dColor = 'r'
# else:
#     dColor = 'black'
# ----------------------------------------[]

plt.scatter(data=df, x='sDistanceX', y='Pipe LayersY', s='VoidPercent', marker='s', c=colors, cmap='rainbow', label='Gap Volume')
plt.colorbar()

# plt.plot(dataX, dataY, marker='|', color='b', linestyle='', label='Gap Volume')


plt.xlabel('Sample Distance')
plt.ylabel('Tape on Pipe Layer')
plt.title('Tape Gap Mapping Profile')
plt.legend()

plt.show()

