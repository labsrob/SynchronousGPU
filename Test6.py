# import tkinter as tk
# from Test66 import collectiveEoP  # or paste the class above in this file
#
# root = tk.Tk()
# root.title("EoP Test")
# root.geometry("1900x900")
#
# tab5 = tk.Frame(root)
# tab5.pack(fill="both", expand=True)
#
# app = collectiveEoP(tab5)
# app.pack(fill="both", expand=True)
#
# root.mainloop()

import pandas as pd
import numpy as np

def moving_average(numbers, window_size):
    numbers_series = pd.Series(numbers)
    windows = numbers_series.rolling(window_size)
    moving_averages = windows.mean()

    return moving_averages.tolist()[window_size - 1:]


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    value_list = [[10, 2, 3, 4, 6, 2, 1, 5, 2, 13, 14, 2, 5, 4, 7, 12, ],
                  [4, 5, 6, 12, 32, 42, 75, 6, 3, 4, 7, 4, 7, 5, 1, 10],
                  [2, 7, 8, 9, 83, 12, 16, 3, 4, 7, 5, 2, 9, 45, 23, 2]]
    output_list = []
    for nums in value_list:
        output_list.append(moving_average(nums, 4))

    print('TP01', output_list)
    print('TP02', np.nanmean(output_list))