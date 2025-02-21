import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# path = ('C:\\Users\\DevEnv\\OneDrive - Magma Global LTD\\Documents\\Magma SPC Development\\Tape Gap Measurements\\testFile.csv')
path = ('C:\\Users\\DevEnv\\OneDrive - Magma Global LTD\\Documents\\Development DOCUMENTS\\Technical Reqs Docs\\Tape Gap Measurements\\testFile.csv')
csv_file = (path)

df = pd.read_csv(csv_file)
print('Test Print', df.head())
print('Test2:', df['VoidPercent'])
import seaborn as sns

# construct cmap
flatui = ["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e", "#2ecc71"]
my_cmap = ListedColormap(sns.color_palette(flatui).as_hex())

# sns.scatterplot(data=df, x='sDistanceX', y='Pipe LayersY', markers='s', hue='VoidPercent', size='VoidPercent')
# sns.color_palette("rocket_r", as_cmap=True)
# sns.set()

if df['VoidPercent'] <= 1.0:
    fcoded = 'b'
elif 1.0 <= df['VoidPercent'] <= 3.0:
    fcoded = 'g'
elif 3.0 <= df['VoidPercent'] <= 5.0:
    fcoded = 'y'
elif 5.0 <= df['VoidPercent'] <= 7.0:
    fcoded = 'r'
else:
    fcoded = 'b'

plt.scatter(data=df, x='sDistanceX', y='Pipe LayersY', marker='|', c=fcoded) #, cmap=my_cmap  # z='Pipe LayersY',
# plt.plot_surface(data=df, x='sDistanceX', y='Pipe LayersY', Z='Pipe LayersY', marker='|', cmap=my_cmap)
plt.colorbar()
plt.show()

# df2 = (df.rename_axis('sDistanceXX').reset_index().melt(id_vars=['sDistanceXX'], var_name='VoidZX'))
# print('Test Print2:', df2.head())