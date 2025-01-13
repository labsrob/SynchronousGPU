import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

path = ('C:\\Users\\DevEnv\\OneDrive - Magma Global LTD\\Documents\\Magma SPC Development\\Tape Gap Measurements\\testFile.csv')
csv_file = (path)

df = pd.read_csv(csv_file)
print('Test Print', df.head())

import seaborn as sns

# construct cmap
flatui = ["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e", "#2ecc71"]
my_cmap = ListedColormap(sns.color_palette(flatui).as_hex())

# sns.scatterplot(data=df, x='sDistanceX', y='Pipe LayersY', size='VoidZ', cmap=my_cmap)
# sns.color_palette("rocket_r", as_cmap=True)
# sns.set()

plt.scatter(data=df, x='sDistanceX', y='Pipe LayersY', cmap=my_cmap)
plt.colorbar()
plt.show()

# df2 = (df.rename_axis('sDistanceXX').reset_index().melt(id_vars=['sDistanceXX'], var_name='VoidZX'))
# print('Test Print2:', df2.head())