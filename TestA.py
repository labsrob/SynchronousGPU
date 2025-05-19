import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog


# def make_draggable(widget):
#     widget.bind("<Button-1>", on_drag_start)
#     widget.bind("<B1-Motion>", on_drag_motion)
#
#
# def on_drag_start(event):
#     widget = event.widget
#     widget._drag_start_x = event.x
#     widget._drag_start_y = event.y
#
#
# def on_drag_motion(event):
#     widget = event.widget
#     x = widget.winfo_x() - widget._drag_start_x + event.x
#     y = widget.winfo_y() - widget._drag_start_y + event.y
#     widget.place(x=x, y=y)

#
# root = tk.Tk()
# notebook = ttk.Notebook(root)
# notebook.bind("<<NotebookTabChanged>>", handleTabChange)
# notebook.pack(fill="both", expand=True)
# make_draggable(notebook)
# notebook.bind("<B3-Motion>", reorder)
# # add a tab that creates new tabs when selected
# frame = tk.Frame()
# notebook.add(frame, text="+")

# root.mainloop()

# from cryptography.fernet import Fernet
#
# key = Fernet.generate_key()
# fernet = Fernet(key)

# we will be encrypting the below string.
# lineA = "('28/10/2024 09:21:17', '22mm', '245', '123', '133.662', '45.75', 184.0, 89.706, 306.0, 62.0, '1-40')"
# lineA = 'gAAAAABnH2DBi8Q_neGE6vJK9JDXEVXLduXqpvNeeiiAkKMJjxvE8b0ztOxHO1WcuWlelS-j8VKgP23mhgjygfpHQ12p2Rg7IqGJ-8SDfBHLducmIshNjaCbAa-K1yj-HFynGI5A90IYGSnsZ69JSV9TDNZGHUIlYMhoxP2XHewiVGpIzAj_ac49Qx8H5pPJVUqBvkBlGw64gOHJvjnzrI3Rbv_z6LT1cg=='
# cfg1 = fernet.encrypt(lineA.encode())

# cfg2 = "b'gAAAAABnH5SPM5QZzHx2Z0YupiIBWhUkh_2EzDrImAvX97G72Fi5TRpHRr1r7mQ8a-TSmm-Bl9OIOBewpyaareE5JiftIYKIpvF3aqxqJBTiKsNY15Vo7daw-2AZ9oJ_LQ-UcmbUBYG0OGnuqEjAqSpBdFPNEH_gaUREkEnDPD0GCv9338ZX5m3sspMWwY47MOC0C5fDmEm2PM0OaCTNKg_DYlQocQZ_4Q=='"
# print("original string: ", lineA)
# print("encrypted string: ", cfg1)
#
# decMessage = fernet.decrypt(cfg2).decode()
# print("decrypted string: ", decMessage)

# -------------------------------------------------
import rsa

# generate public and private keys with
# rsa.newkeys method,this method accepts
# key length as its parameter
# key length should be atleast 16
# publicKey, privateKey = rsa.newkeys(890) # 512
#
# # this is the string that we will be encrypting
# message1 = "('28/10/2024 09:21:17', '22mm', '245', '123', '133.662', '45.75', 184.0, 89.706, 306.0, 62.0, '1-40')"
# message2 = "hello geeks and hello geeks"
# encMessage = '\x00\x1f\xd3_Y1\xe1\x88\xcb\x01\xd5\x90\x04MUj1~.\xea\x14R\xa8>\xa8\xb1\r^\x89:B\xb6\x06\xd4\x973\xd2\xc5\xd8\xff+\xd4\xf8\x02\xf0\xed\x82\x0c\xca\xf3\xf3\xa8B\xf4\x1d\xcf\xdd\xf5\xef4$\xa7\xa6\x1d\x90\x00\x7fF\x91\xe0\xf6\x18h\xc9k\xea\xf2\xa2\x186\xe7B"3Go\xb9\xda\xfa\xc7\x96*\x9e\xd3\xc30\xc9\x95\xd6wS\x1f\x0b\xca\x98`~\x06\xa3G\xa8{'
#
# # rsa.encrypt method is used to encrypt
# # encMessage = rsa.encrypt(message1.encode(), publicKey)
#
# # print("original string: ", message1)
# # print("encrypted string: ", encMessage)
#
# # the encrypted message can be decrypted
# # with ras.decrypt method and private key
# # decrypt method returns encoded byte string,
# # use decode method to convert it to string
# # public key cannot be used for decryption
# decMessage = rsa.decrypt(encMessage, privateKey).decode()
#
# print("decrypted string: ", decMessage)

# from cryptography.fernet import Fernet
#
# # Generate a key and instantiate a Fernet instance
# key = Fernet.generate_key()
# cipher_suite = Fernet(key)

# Encrypt a message
# text = "Hello, World!"
# encrypted_text = cipher_suite.encrypt(text.encode())
# print("Encrypted:", encrypted_text)

# encrypted_text = b'gAAAAABnH5tYtK490SsUoSz7UWyQBNk-yCjqUq6AUJYPNsLCYCQDBpw7NqZYRPqlgbgZRBFdDqrMLgJPf1opdvKt_K2TyC0Ggw=='
# # Decrypt the message
# decrypted_text = cipher_suite.decrypt(encrypted_text)
# print("Decrypted:", decrypted_text.decode())
# Using base64 encoding
# import base64
#
# # Encoding a message in UTF-8
# # message = "('28/10/2024 09:21:17', '22mm', '245', '123', '133.662', '45.75', 184.0, 89.706, 306.0, 62.0, '1-40')"
#
# message = "Hello, World!"
#
# message_encoded = message.encode('utf-8')
# print("\nEncoded in UTF-8:", message_encoded)
#
# base64_encoded = base64.b64encode(message_encoded)
# print("Encoded in Base64:", base64_encoded)

# -----------------------------------------------
# from cryptography.fernet import Fernet

# # key generation
# key = Fernet.generate_key()
#
# # string the key in a file ---------------
# with open('filekey.key', 'wb') as filekey:
#     filekey.write(key)


# key generation ------------------------[]
# key = Fernet.generate_key()
#
# # opening the key
# with open('filekey.key', 'rb') as filekey:
#     key = filekey.read()
#
# # using the generated key
# fernet = Fernet(key)
#
# # opening the original file to encrypt
# with open('nba.csv', 'rb') as file:
#     original = file.read()
#
# # encrypting the file
# encrypted = fernet.encrypt(original)
#
# # opening the file in write mode and
# # writing the encrypted data
# with open('nba.csv', 'wb') as encrypted_file:
#     encrypted_file.write(encrypted)

# Create an input field
from cryptography.fernet import Fernet

# we will be encrypting the below string.
# message = "hello geeks"

# generate a key for encryption and decryption
# You can use fernet to generate
# the key or use random key generator
# here I'm using fernet to generate key

# key = Fernet.generate_key()
#
# # Instance the Fernet class with the key
#
# fernet = Fernet(key)
#
# # then use the Fernet class instance
# # to encrypt the string string must
# # be encoded to byte string before encryption
# encMessage = fernet.encrypt(message.encode())
#
# print("original string: ", message)
# print("encrypted string: ", encMessage)

# decrypt the encrypted string with the
# Fernet instance of the key,
# that was used for encrypting the string
# encoded byte string is returned by decrypt method,
# so decode it to string with decode methods
# encMessage = "('28/10/2024 09:21:17', '22mm', '245', '123', '133.662', '45.75', 184.0, 89.706, 306.0, 62.0, '1-40')"
# decMessage = "5a465c5c405c424e5c545d595251575e5d5c48505943434d55535c09024a5e4149565b58554d4e435e5f41464244485c41524052595f554d4e435b585c565b43434d43595a4a5f415259574a585d444d4e575f5b5c514244595f5c514244485c5f555e4346"
#
# import onetimepad
# md = onetimepad.encrypt(encMessage, 'random')
# print("Encrypted string: ", md)
#
# my = onetimepad.decrypt(decMessage, 'random')
# print("Decrypted string: ", my)


# Using * unpacking method
# tuples = ('Spark', 'Python', 'pandas', 'Java')
# tuples2 = ('28/10/2024 15:01:36', '**', '277', '131', '289.235', '99.0', 204.0, 107.353, 350.0, 58.0, '**')
# list1 = [*tuples2,]
# print('TP01', tuples2)
# print('TP02', list1)
# from configparser import ConfigParser
# # ----------------------------------------------------------
# config_parser = ConfigParser()
# keyword = "SampleProp_275045"
#
# with open("histProdParams.INI", 'r') as configfile:
#     for section in config_parser.sections():
#         print(section)

    #     for key in dict(config_parser.items(section)):
    #         print(section)
    #     if section == keyword:
    #         print("\nTrue")
    #     else:
    #         print('FALSE')
    # print('\nTP01', section)




# def bufferEOF(fname, N):
#     # open index tracker file, and load the     # values in the end of file
#     with open(fname) as file:
#         for line in (file.readlines()[-N:]):    # N = number of lines to read
#             oem = line
#         print('\nEND OF FILE:', oem)
#         print(line, end='')
#     return oem
#
#
# fname = 'C:\\Users\\DevEnv\\PycharmProjects\\SynchronousGPU\\RT_Index_Log\\IDXLog_20240507Z.txt'
# eoF = bufferEOF(fname, 1)
# print('\nParsed1:', eoF[10:])
#
# testY = list(eoF[10:])
# print('Parsed2', testY)
#
# lines = eoF[10:].splitlines()
# print('Parsed3', lines)


# from Tkinter import *
# ----------------------------------------------
# import tkinter as tk
# from tkinter import ttk
#
# root = tk.Tk()
# root.title("Progress Bar in Tk")
# progressbar = ttk.Progressbar(mode="indeterminate")
# progressbar.place(x=30, y=60, width=200)
# # Start moving the indeterminate progress bar.
# progressbar.start()
# root.geometry("300x200")
# root.mainloop()

# ---------------------------------------------[RUNTIME PROCESS BAR]

# import tkinter as tk
# from tkinter import ttk
# from threading import Thread
# from urllib.request import urlretrieve, urlcleanup
#
#
# def connectSQLquery():
#     url = "10.0.3.72"
#     urlretrieve(url, "[dbo].[OEE_20230614]", eolProgressBar)
#     urlcleanup()
#
#
# def processEOL_button():
#     # Download the file in a new thread.
#     Thread(target=connectSQLquery).start()
#
#
# def eolProgressBar(count, data_size, total_data):
#     """
#     This function is called by urlretrieve() every time
#     a chunk of data is downloaded.
#     """
#     if count == 0:
#         # Set the maximum value for the progress bar.
#         progressbar.configure(maximum=total_data)
#     else:
#         # Increase the progress.
#         progressbar.step(data_size)
#
# # ----------------------------------------[]
# root = tk.Tk()
#
# root.title("Process EoL Summary")
# progressbar = ttk.Progressbar()
#
# progressbar.place(x=30, y=60, width=200)
# download_button = ttk.Button(text="Start EoL", command=processEOL_button)
# download_button.place(x=30, y=20)
#
# root.geometry("300x200")
#
# root.mainloop()

# --------------------------------------------------------------------------------[PDF Converter]
# Import Module
# from tkinter import *
# from tkinter.filedialog import askopenfilenames
# import img2pdf
#
# # Create Object
# root = Tk()
# # set Geometry
# root.geometry('400x200')
#
# def select_file():
# 	global file_names
# 	file_names = askopenfilenames(initialdir = "/",
# 								title = "Select File")
#
# # IMAGE TO PDF
# def image_to_pdf():
# 	for index, file_name in enumerate(file_names):
# 		with open(f"file {index}.pdf", "wb") as f:
# 			f.write(img2pdf.convert(file_name))
#
# # IMAGES TO PDF
# def images_to_pdf():
# 	with open(f"file.pdf", "wb") as f:
# 		f.write(img2pdf.convert(file_names))
#
# # Add Labels and Buttons
# Label(root, text = "IMAGE CONVERSION",
# 	font = "italic 15 bold").pack(pady = 10)
#
# Button(root, text = "Select Images",
# 	command = select_file, font = 14).pack(pady = 10)
#
# frame = Frame()
# frame.pack(pady = 20)
#
# Button(frame, text = "Image to PDF",
# 	command = image_to_pdf,
# 	relief = "solid",
# 	bg = "white", font = 15).pack(side = LEFT, padx = 10)
#
# Button(frame, text = "Images to PDF",
# 	command = images_to_pdf, relief = "solid",
# 	bg = "white", font = 15).pack()
#
# # Execute Tkinter
# root.mainloop()


# -------------------------------------------------------------------------------[Tables]
# Python program to create a table
#
# from tkinter import *
#
# widths = [10, 10] + [10]*(10 - 2)
#
# class Table:
#
#     def __init__(self, root):
#
#         # code for creating table ---
#         for i in range(total_rows):
#             for j in range(total_columns):
#                 self.e = Entry(root, width=widths[j], justify="center", fg='blue', font=('Arial', 12, 'bold'))    #16
#
#                 if lst[0] == 'Tape Temperature in Degrees Celsius':
#                     self.e.grid(row=0, column=0, columnspan=2)
#                 else:
#                     self.e.grid(row=i, column=j)
#                 self.e.insert(END, lst[i][j])
#
#
# # take the data
# lst = [('Tape Temperature in Degrees Celsius', '', '', '', '', ''),
#        ('TCP01', 'Actual', 'Nominal', 'StdDev', 'Tolerance ±', 'Status'),
#        ('Ring 1', 4.6, 4.5, 0.25, 0.5, 'OK'),
#        ('Ring 2', 4.5, 4.5, 0.16, 0.5, 'OK'),
#        ('Ring 3', 4.7, 4.5, 0.27, 0.5, 'OK'),
#        ('Ring 4', 4.5, 4.5, 0.32, 0.5, 'OK')]
#
# # find total number of rows and
# # ('Tape Temperature in Degrees Celsius', '', '', '', '', '')
# # columns in list
# total_rows = len(lst)
# total_columns = len(lst[0])
#
# # create root window
# root = Tk()
# t = Table(root)
#
#
# root.title("Grid Column Spanning")
# root.geometry("600x360")  # Set the window size
# # -----------------------------------------------
# # Create some placeholder labels (widgets)
# text1 = tk.Label(root, text="Label 1")
# text2 = tk.Label(root, text="Label 2")
# text3 = tk.Label(root, text="Label 3")
# text4 = tk.Label(root, text="Label 4")
#
# # Place widgets in the grid using tkinter's grid manager
# text1.grid(row=0, column=0)
# text2.grid(row=1, column=0, columnspan=2)
# text3.grid(row=0, column=1)
#
# root.mainloop()


# -------------------------------------------------------------------
#
# import tkinter as tk
# from tkinter import ttk
# from fpdf import FPDF
#
#
# def generate_pdf(data):
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_font("helvetica", size=12)
#
#     # Create table header -------------------------------------[]
#     for header in ["TCP01", "Actual", "Nominal", "Std Dev", "Tolerance +/-", "Status"]:
#         pdf.cell(30, 10, header, 1)
#     pdf.ln()
#
#     # Create table label --------------------------------------[]
#     for label in ['Ring1', 'Ring2', 'Ring3', 'Ring4']:
#         pdf.cell(30, 10, label, 1)
#     pdf.ln()
#
#     # Create table rows ---------------------------------------[]
#     for row in data:
#         for item in row:
#             pdf.cell(30, 10, str(item), 1)
#         pdf.ln()
#
#     pdf.output("QualityEOL.pdf")
#
#
# def get_data():  # Function to generate PDF
#     data = []
#     for i in range(4):
#         row = [entry.get() for entry in entries[i]]
#         # row1 = r1_actual.get(), r1_nominal.get(), r1_stdDev.get(), r1_tolerance.get(), r1_status.get()
#         # row2 = r2_actual.get(), r2_nominal.get(), r2_stdDev.get(), r2_tolerance.get(), r2_status.get()
#         # row3 = r3_actual.get(), r3_nominal.get(), r3_stdDev.get(), r3_tolerance.get(), r3_status.get()
#         # row4 = r4_actual.get(), r4_nominal.get(), r4_stdDev.get(), r4_tolerance.get(), r4_status.get()
#
#         data.append(row)
#     generate_pdf(data)

# # Create main window -----------------------[]
# root = tk.Tk()
# root.title("6 Column Table")
#
# # Create table -----------------------------[]
# entries = []
# for i in range(5):  # Example: 5 rows
#     row_entries = []
#     for j in range(6):  # 6 columns
#         entry = tk.Entry(root)
#         entry.grid(row=i, column=j)
#         row_entries.append(entry)
#     entries.append(row_entries)
#
# # Create button to generate PDF
# generate_button = tk.Button(root, text="Generate PDF Report", command=get_data)
# # generate_button.grid(row=6, columnspan=6)
# generate_button.place(x=170, y=110)
#
# # Run the application
# root.mainloop()
# ------------------------------------------[]

# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# import ipywidgets as widgets
# import seaborn as sns
#
# # Get dataset
# data_url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/cases_deaths/total_deaths_per_million.csv"
# df = pd.read_csv(data_url, index_col=0, parse_dates=[0], engine='python')
#
# # na values = 0
# df.fillna(0, inplace=True)
# df.head()
#
# # add year-week column
# df['Year_Week'] = df.index.to_period('W').strftime('%Y-%U')
#
# # keep only last day of week and change to datetime type
# df = df.groupby(df['Year_Week']).last('1D')
# df.index = pd.to_datetime(df.index + '-0', format='%Y-%U-%w')
#
# # drop columns that aren't a country
# df_country = df.drop(['World',
#                       'Africa',
#                       'Asia',
#                       'Europe',
#                       'European Union',
#                       'High income',
#                       'Low income',
#                       'Lower middle income',
#                       'North America',
#                       'South America',
#                       'Upper middle income'],
#                      axis=1)
#
#
# # create function to update plot based on selected country
# def update_plot(country):
#     ax.clear()  # clear existing plot
#     ax.plot(df.index, df_country[country])  # plot selected country
#
#     # set x-axis tick locations and labels
#     xticks = pd.date_range(start=df_country.index[0].strftime('%Y-01-01'), end=df_country.index[-1], freq='AS')
#     xticklabels = [x.strftime('%Y') for x in xticks]
#     ax.set_xticks(xticks)
#     ax.set_xticklabels(xticklabels)
#     ax.set_title(f"Total deaths per million ({country})")  # update plot title
#     ax.set_xlabel("Date")
#     ax.set_ylabel("Deaths per million")
#     fig.canvas.draw()  # redraw canvas
#
#
# # create drop-down menu with country names as options
# country_dropdown = widgets.Dropdown(
#     options=df_country.columns,
#     value=df_country.columns[0],
#     description='Country'
# )
#
# # create plot
# fig, ax = plt.subplots()
# update_plot(country_dropdown.value)  # initial plot
#
# # set up widget interaction
# output = widgets.Output()
# display(country_dropdown, output)
#
#
# def on_change(change):
#     if change['type'] == 'change' and change['name'] == 'value':
#         with output:
#             output.clear_output()
#             update_plot(change['new'])
#             display(fig)
#
#
# country_dropdown.observe(on_change)
import json

x = {"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[-1.1273,50.8395,1.0]},"properties":{"location":{"name":"Portchester"},"requestPointDistance":961.7344,"modelRunDate":"2025-03-12T13:00Z","timeSeries":[{"time":"2025-03-12T13:00Z","screenTemperature":7.64,"maxScreenAirTemp":8.15,"minScreenAirTemp":7.6,"screenDewPointTemperature":0.11,"feelsLikeTemperature":4.83,"windSpeed10m":4.55,"windDirectionFrom10m":335,"windGustSpeed10m":6.43,"max10mWindGust":6.45,"visibility":39177,"screenRelativeHumidity":58.76,"mslp":100294,"uvIndex":2,"significantWeatherCode":7,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":6},{"time":"2025-03-12T14:00Z","screenTemperature":6.38,"maxScreenAirTemp":7.64,"minScreenAirTemp":6.34,"screenDewPointTemperature":1.78,"feelsLikeTemperature":3.0,"windSpeed10m":5.11,"windDirectionFrom10m":344,"windGustSpeed10m":6.67,"max10mWindGust":7.83,"visibility":35723,"screenRelativeHumidity":72.43,"mslp":100270,"uvIndex":2,"significantWeatherCode":7,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":7},{"time":"2025-03-12T15:00Z","screenTemperature":6.03,"maxScreenAirTemp":6.38,"minScreenAirTemp":5.97,"screenDewPointTemperature":1.77,"feelsLikeTemperature":3.01,"windSpeed10m":4.22,"windDirectionFrom10m":357,"windGustSpeed10m":5.89,"max10mWindGust":6.53,"visibility":36225,"screenRelativeHumidity":74.03,"mslp":100255,"uvIndex":1,"significantWeatherCode":8,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":9},{"time":"2025-03-12T16:00Z","screenTemperature":6.46,"maxScreenAirTemp":6.47,"minScreenAirTemp":6.03,"screenDewPointTemperature":0.97,"feelsLikeTemperature":3.96,"windSpeed10m":3.49,"windDirectionFrom10m":354,"windGustSpeed10m":5.38,"max10mWindGust":6.02,"visibility":39375,"screenRelativeHumidity":67.91,"mslp":100220,"uvIndex":1,"significantWeatherCode":3,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":2},{"time":"2025-03-12T17:00Z","screenTemperature":6.66,"maxScreenAirTemp":6.8,"minScreenAirTemp":6.46,"screenDewPointTemperature":0.8,"feelsLikeTemperature":4.28,"windSpeed10m":3.45,"windDirectionFrom10m":351,"windGustSpeed10m":5.42,"max10mWindGust":5.97,"visibility":32985,"screenRelativeHumidity":66.27,"mslp":100220,"uvIndex":1,"significantWeatherCode":3,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-12T18:00Z","screenTemperature":5.71,"maxScreenAirTemp":6.66,"minScreenAirTemp":5.69,"screenDewPointTemperature":1.12,"feelsLikeTemperature":3.65,"windSpeed10m":2.67,"windDirectionFrom10m":349,"windGustSpeed10m":5.04,"max10mWindGust":5.6,"visibility":27526,"screenRelativeHumidity":72.3,"mslp":100230,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":4},{"time":"2025-03-12T19:00Z","screenTemperature":5.33,"maxScreenAirTemp":5.71,"minScreenAirTemp":5.23,"screenDewPointTemperature":1.26,"feelsLikeTemperature":3.32,"windSpeed10m":2.53,"windDirectionFrom10m":337,"windGustSpeed10m":5.65,"max10mWindGust":7.81,"visibility":27382,"screenRelativeHumidity":74.99,"mslp":100252,"uvIndex":0,"significantWeatherCode":2,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":6},{"time":"2025-03-12T20:00Z","screenTemperature":5.05,"maxScreenAirTemp":5.33,"minScreenAirTemp":5.02,"screenDewPointTemperature":1.18,"feelsLikeTemperature":2.05,"windSpeed10m":3.83,"windDirectionFrom10m":352,"windGustSpeed10m":8.04,"max10mWindGust":8.38,"visibility":27735,"screenRelativeHumidity":76.09,"mslp":100266,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-12T21:00Z","screenTemperature":4.48,"maxScreenAirTemp":5.05,"minScreenAirTemp":4.46,"screenDewPointTemperature":1.36,"feelsLikeTemperature":1.05,"windSpeed10m":4.26,"windDirectionFrom10m":358,"windGustSpeed10m":8.2,"max10mWindGust":8.67,"visibility":28992,"screenRelativeHumidity":80.18,"mslp":100290,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-12T22:00Z","screenTemperature":3.9,"maxScreenAirTemp":4.48,"minScreenAirTemp":3.89,"screenDewPointTemperature":1.35,"feelsLikeTemperature":0.58,"windSpeed10m":3.86,"windDirectionFrom10m":358,"windGustSpeed10m":7.8,"max10mWindGust":8.55,"visibility":28775,"screenRelativeHumidity":83.43,"mslp":100296,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-12T23:00Z","screenTemperature":3.74,"maxScreenAirTemp":3.99,"minScreenAirTemp":3.68,"screenDewPointTemperature":1.38,"feelsLikeTemperature":0.27,"windSpeed10m":4.07,"windDirectionFrom10m":0,"windGustSpeed10m":8.12,"max10mWindGust":8.51,"visibility":27453,"screenRelativeHumidity":84.67,"mslp":100300,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-13T00:00Z","screenTemperature":3.4,"maxScreenAirTemp":3.74,"minScreenAirTemp":3.38,"screenDewPointTemperature":1.25,"feelsLikeTemperature":-0.01,"windSpeed10m":3.85,"windDirectionFrom10m":1,"windGustSpeed10m":7.73,"max10mWindGust":8.79,"visibility":28256,"screenRelativeHumidity":85.9,"mslp":100300,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-13T01:00Z","screenTemperature":3.38,"maxScreenAirTemp":3.44,"minScreenAirTemp":3.35,"screenDewPointTemperature":1.18,"feelsLikeTemperature":-0.15,"windSpeed10m":3.99,"windDirectionFrom10m":1,"windGustSpeed10m":7.83,"max10mWindGust":8.05,"visibility":28070,"screenRelativeHumidity":85.73,"mslp":100300,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-13T02:00Z","screenTemperature":2.87,"maxScreenAirTemp":3.38,"minScreenAirTemp":2.86,"screenDewPointTemperature":0.97,"feelsLikeTemperature":-0.69,"windSpeed10m":3.91,"windDirectionFrom10m":359,"windGustSpeed10m":7.83,"max10mWindGust":8.29,"visibility":25531,"screenRelativeHumidity":87.4,"mslp":100289,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-13T03:00Z","screenTemperature":2.57,"maxScreenAirTemp":2.87,"minScreenAirTemp":2.54,"screenDewPointTemperature":0.73,"feelsLikeTemperature":-1.09,"windSpeed10m":3.95,"windDirectionFrom10m":356,"windGustSpeed10m":8.03,"max10mWindGust":8.34,"visibility":24018,"screenRelativeHumidity":87.69,"mslp":100270,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-13T04:00Z","screenTemperature":2.49,"maxScreenAirTemp":2.57,"minScreenAirTemp":2.48,"screenDewPointTemperature":0.54,"feelsLikeTemperature":-1.56,"windSpeed10m":4.55,"windDirectionFrom10m":1,"windGustSpeed10m":8.63,"max10mWindGust":8.96,"visibility":21743,"screenRelativeHumidity":87.07,"mslp":100271,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-13T05:00Z","screenTemperature":2.39,"maxScreenAirTemp":2.49,"minScreenAirTemp":2.38,"screenDewPointTemperature":0.47,"feelsLikeTemperature":-1.57,"windSpeed10m":4.39,"windDirectionFrom10m":0,"windGustSpeed10m":8.59,"max10mWindGust":9.04,"visibility":18975,"screenRelativeHumidity":87.32,"mslp":100291,"uvIndex":0,"significantWeatherCode":2,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-13T06:00Z","screenTemperature":2.17,"maxScreenAirTemp":2.39,"minScreenAirTemp":2.14,"screenDewPointTemperature":0.44,"feelsLikeTemperature":-1.72,"windSpeed10m":4.19,"windDirectionFrom10m":356,"windGustSpeed10m":8.63,"max10mWindGust":8.92,"visibility":18055,"screenRelativeHumidity":88.43,"mslp":100311,"uvIndex":0,"significantWeatherCode":2,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-13T07:00Z","screenTemperature":2.73,"maxScreenAirTemp":2.74,"minScreenAirTemp":2.17,"screenDewPointTemperature":0.48,"feelsLikeTemperature":-0.76,"windSpeed10m":3.86,"windDirectionFrom10m":349,"windGustSpeed10m":8.11,"max10mWindGust":8.63,"visibility":18892,"screenRelativeHumidity":85.32,"mslp":100340,"uvIndex":1,"significantWeatherCode":3,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-13T08:00Z","screenTemperature":3.8,"maxScreenAirTemp":3.82,"minScreenAirTemp":2.73,"screenDewPointTemperature":0.69,"feelsLikeTemperature":0.23,"windSpeed10m":4.34,"windDirectionFrom10m":356,"windGustSpeed10m":7.41,"max10mWindGust":7.44,"visibility":26220,"screenRelativeHumidity":80.36,"mslp":100379,"uvIndex":1,"significantWeatherCode":8,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":7},{"time":"2025-03-13T09:00Z","screenTemperature":4.8,"maxScreenAirTemp":4.83,"minScreenAirTemp":3.8,"screenDewPointTemperature":0.6,"feelsLikeTemperature":1.06,"windSpeed10m":5.07,"windDirectionFrom10m":6,"windGustSpeed10m":8.42,"max10mWindGust":8.42,"visibility":34074,"screenRelativeHumidity":74.34,"mslp":100400,"uvIndex":1,"significantWeatherCode":8,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":8},{"time":"2025-03-13T10:00Z","screenTemperature":5.52,"maxScreenAirTemp":5.61,"minScreenAirTemp":4.8,"screenDewPointTemperature":0.63,"feelsLikeTemperature":1.98,"windSpeed10m":5.02,"windDirectionFrom10m":11,"windGustSpeed10m":8.3,"max10mWindGust":8.3,"visibility":35800,"screenRelativeHumidity":70.93,"mslp":100401,"uvIndex":2,"significantWeatherCode":8,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":9},{"time":"2025-03-13T11:00Z","screenTemperature":6.31,"maxScreenAirTemp":6.53,"minScreenAirTemp":5.52,"screenDewPointTemperature":0.41,"feelsLikeTemperature":2.62,"windSpeed10m":5.82,"windDirectionFrom10m":9,"windGustSpeed10m":9.06,"max10mWindGust":9.19,"visibility":37908,"screenRelativeHumidity":66.48,"mslp":100402,"uvIndex":2,"significantWeatherCode":8,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":8},{"time":"2025-03-13T12:00Z","screenTemperature":6.24,"maxScreenAirTemp":6.63,"minScreenAirTemp":6.04,"screenDewPointTemperature":0.6,"feelsLikeTemperature":2.52,"windSpeed10m":5.9,"windDirectionFrom10m":22,"windGustSpeed10m":8.73,"max10mWindGust":8.73,"visibility":25443,"screenRelativeHumidity":67.47,"mslp":100421,"uvIndex":2,"significantWeatherCode":12,"precipitationRate":0.2,"totalPrecipAmount":0.06,"totalSnowAmount":0,"probOfPrecipitation":55},{"time":"2025-03-13T13:00Z","screenTemperature":6.76,"maxScreenAirTemp":6.9,"minScreenAirTemp":5.9,"screenDewPointTemperature":0.31,"feelsLikeTemperature":4.32,"windSpeed10m":3.81,"windDirectionFrom10m":351,"windGustSpeed10m":6.64,"max10mWindGust":6.94,"visibility":32553,"screenRelativeHumidity":64.37,"mslp":100402,"uvIndex":2,"significantWeatherCode":8,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":8},{"time":"2025-03-13T14:00Z","screenTemperature":6.62,"maxScreenAirTemp":7.2,"minScreenAirTemp":6.47,"screenDewPointTemperature":0.25,"feelsLikeTemperature":3.02,"windSpeed10m":6.03,"windDirectionFrom10m":6,"windGustSpeed10m":9.38,"max10mWindGust":9.79,"visibility":37130,"screenRelativeHumidity":64.95,"mslp":100411,"uvIndex":2,"significantWeatherCode":3,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":4},{"time":"2025-03-13T15:00Z","screenTemperature":6.83,"maxScreenAirTemp":6.96,"minScreenAirTemp":6.46,"screenDewPointTemperature":0.06,"feelsLikeTemperature":3.83,"windSpeed10m":4.57,"windDirectionFrom10m":24,"windGustSpeed10m":7.37,"max10mWindGust":9.32,"visibility":34410,"screenRelativeHumidity":62.33,"mslp":100410,"uvIndex":1,"significantWeatherCode":7,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":7},{"time":"2025-03-13T16:00Z","screenTemperature":6.82,"maxScreenAirTemp":7.06,"minScreenAirTemp":6.46,"screenDewPointTemperature":0.42,"feelsLikeTemperature":3.64,"windSpeed10m":5.13,"windDirectionFrom10m":13,"windGustSpeed10m":8.03,"max10mWindGust":9.96,"visibility":32299,"screenRelativeHumidity":63.93,"mslp":100440,"uvIndex":1,"significantWeatherCode":3,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":10},{"time":"2025-03-13T17:00Z","screenTemperature":6.19,"maxScreenAirTemp":6.82,"minScreenAirTemp":6.1,"screenDewPointTemperature":0.57,"feelsLikeTemperature":3.42,"windSpeed10m":3.84,"windDirectionFrom10m":14,"windGustSpeed10m":5.94,"max10mWindGust":7.96,"visibility":37330,"screenRelativeHumidity":67.5,"mslp":100489,"uvIndex":1,"significantWeatherCode":7,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":13},{"time":"2025-03-13T18:00Z","screenTemperature":5.61,"maxScreenAirTemp":6.19,"minScreenAirTemp":5.57,"screenDewPointTemperature":0.94,"feelsLikeTemperature":3.21,"windSpeed10m":3.08,"windDirectionFrom10m":355,"windGustSpeed10m":5.59,"max10mWindGust":6.74,"visibility":34007,"screenRelativeHumidity":72.22,"mslp":100519,"uvIndex":0,"significantWeatherCode":2,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":7},{"time":"2025-03-13T19:00Z","screenTemperature":5.17,"maxScreenAirTemp":5.61,"minScreenAirTemp":5.12,"screenDewPointTemperature":0.94,"feelsLikeTemperature":2.63,"windSpeed10m":3.11,"windDirectionFrom10m":354,"windGustSpeed10m":6.16,"max10mWindGust":7.34,"visibility":33686,"screenRelativeHumidity":74.46,"mslp":100578,"uvIndex":0,"significantWeatherCode":2,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-13T20:00Z","screenTemperature":4.46,"maxScreenAirTemp":5.17,"minScreenAirTemp":4.41,"screenDewPointTemperature":1.0,"feelsLikeTemperature":1.74,"windSpeed10m":3.19,"windDirectionFrom10m":6,"windGustSpeed10m":6.35,"max10mWindGust":7.71,"visibility":31473,"screenRelativeHumidity":78.63,"mslp":100638,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-13T21:00Z","screenTemperature":3.83,"maxScreenAirTemp":4.46,"minScreenAirTemp":3.82,"screenDewPointTemperature":1.06,"feelsLikeTemperature":0.95,"windSpeed10m":3.2,"windDirectionFrom10m":5,"windGustSpeed10m":6.4,"max10mWindGust":7.38,"visibility":31001,"screenRelativeHumidity":82.32,"mslp":100679,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-13T22:00Z","screenTemperature":3.41,"maxScreenAirTemp":3.83,"minScreenAirTemp":3.39,"screenDewPointTemperature":1.12,"feelsLikeTemperature":0.3,"windSpeed10m":3.42,"windDirectionFrom10m":11,"windGustSpeed10m":6.64,"max10mWindGust":7.69,"visibility":30232,"screenRelativeHumidity":85.27,"mslp":100699,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-13T23:00Z","screenTemperature":2.99,"maxScreenAirTemp":3.41,"minScreenAirTemp":2.95,"screenDewPointTemperature":1.09,"feelsLikeTemperature":-0.11,"windSpeed10m":3.24,"windDirectionFrom10m":9,"windGustSpeed10m":6.59,"max10mWindGust":7.49,"visibility":25988,"screenRelativeHumidity":87.72,"mslp":100701,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-14T00:00Z","screenTemperature":2.53,"maxScreenAirTemp":2.99,"minScreenAirTemp":2.52,"screenDewPointTemperature":0.87,"feelsLikeTemperature":-0.53,"windSpeed10m":3.1,"windDirectionFrom10m":10,"windGustSpeed10m":6.11,"max10mWindGust":7.62,"visibility":24850,"screenRelativeHumidity":89.1,"mslp":100694,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-14T01:00Z","screenTemperature":2.16,"maxScreenAirTemp":2.53,"minScreenAirTemp":2.16,"screenDewPointTemperature":0.75,"feelsLikeTemperature":-0.95,"windSpeed10m":3.07,"windDirectionFrom10m":14,"windGustSpeed10m":6.26,"max10mWindGust":7.57,"visibility":23018,"screenRelativeHumidity":90.78,"mslp":100694,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-14T02:00Z","screenTemperature":1.97,"maxScreenAirTemp":2.16,"minScreenAirTemp":1.93,"screenDewPointTemperature":0.65,"feelsLikeTemperature":-1.16,"windSpeed10m":3.05,"windDirectionFrom10m":13,"windGustSpeed10m":6.05,"max10mWindGust":7.53,"visibility":20691,"screenRelativeHumidity":91.42,"mslp":100693,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-14T03:00Z","screenTemperature":1.68,"maxScreenAirTemp":1.97,"minScreenAirTemp":1.64,"screenDewPointTemperature":0.25,"feelsLikeTemperature":-1.42,"windSpeed10m":2.94,"windDirectionFrom10m":15,"windGustSpeed10m":6.03,"max10mWindGust":7.63,"visibility":20996,"screenRelativeHumidity":90.55,"mslp":100693,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-14T04:00Z","screenTemperature":1.46,"maxScreenAirTemp":1.68,"minScreenAirTemp":1.46,"screenDewPointTemperature":0.13,"feelsLikeTemperature":-1.81,"windSpeed10m":3.13,"windDirectionFrom10m":14,"windGustSpeed10m":6.26,"max10mWindGust":8.08,"visibility":19492,"screenRelativeHumidity":91.3,"mslp":100724,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":0},{"time":"2025-03-14T05:00Z","screenTemperature":1.22,"maxScreenAirTemp":1.46,"minScreenAirTemp":1.21,"screenDewPointTemperature":-0.07,"feelsLikeTemperature":-2.11,"windSpeed10m":3.12,"windDirectionFrom10m":20,"windGustSpeed10m":6.09,"max10mWindGust":8.14,"visibility":18571,"screenRelativeHumidity":91.6,"mslp":100755,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-14T06:00Z","screenTemperature":0.91,"maxScreenAirTemp":1.31,"minScreenAirTemp":0.85,"screenDewPointTemperature":-0.19,"feelsLikeTemperature":-2.3,"windSpeed10m":2.91,"windDirectionFrom10m":21,"windGustSpeed10m":6.0,"max10mWindGust":7.9,"visibility":7857,"screenRelativeHumidity":92.98,"mslp":100795,"uvIndex":0,"significantWeatherCode":0,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":3},{"time":"2025-03-14T07:00Z","screenTemperature":1.53,"maxScreenAirTemp":1.53,"minScreenAirTemp":0.91,"screenDewPointTemperature":-0.03,"feelsLikeTemperature":-1.4,"windSpeed10m":2.75,"windDirectionFrom10m":21,"windGustSpeed10m":5.86,"max10mWindGust":7.69,"visibility":16810,"screenRelativeHumidity":89.97,"mslp":100846,"uvIndex":1,"significantWeatherCode":1,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-14T08:00Z","screenTemperature":2.64,"maxScreenAirTemp":2.64,"minScreenAirTemp":1.53,"screenDewPointTemperature":0.32,"feelsLikeTemperature":-0.23,"windSpeed10m":2.92,"windDirectionFrom10m":26,"windGustSpeed10m":5.67,"max10mWindGust":7.29,"visibility":20808,"screenRelativeHumidity":85.21,"mslp":100888,"uvIndex":1,"significantWeatherCode":3,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-14T09:00Z","screenTemperature":3.82,"maxScreenAirTemp":3.82,"minScreenAirTemp":2.64,"screenDewPointTemperature":0.59,"feelsLikeTemperature":1.06,"windSpeed10m":3.09,"windDirectionFrom10m":28,"windGustSpeed10m":5.42,"max10mWindGust":6.4,"visibility":23621,"screenRelativeHumidity":80.03,"mslp":100930,"uvIndex":2,"significantWeatherCode":3,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-14T10:00Z","screenTemperature":4.98,"maxScreenAirTemp":4.98,"minScreenAirTemp":3.82,"screenDewPointTemperature":-0.24,"feelsLikeTemperature":2.25,"windSpeed10m":3.48,"windDirectionFrom10m":38,"windGustSpeed10m":6.06,"max10mWindGust":6.06,"visibility":27606,"screenRelativeHumidity":70.01,"mslp":100979,"uvIndex":2,"significantWeatherCode":3,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-14T11:00Z","screenTemperature":6.04,"maxScreenAirTemp":6.04,"minScreenAirTemp":4.98,"screenDewPointTemperature":-1.28,"feelsLikeTemperature":3.23,"windSpeed10m":3.99,"windDirectionFrom10m":48,"windGustSpeed10m":6.89,"max10mWindGust":6.89,"visibility":31108,"screenRelativeHumidity":60.52,"mslp":101011,"uvIndex":2,"significantWeatherCode":3,"precipitationRate":0.0,"totalPrecipAmount":0.0,"totalSnowAmount":0,"probOfPrecipitation":1},{"time":"2025-03-14T12:00Z","screenTemperature":6.77,"screenDewPointTemperature":-0.96,"feelsLikeTemperature":3.48,"windSpeed10m":5.59,"windDirectionFrom10m":50,"windGustSpeed10m":8.79,"visibility":25458,"screenRelativeHumidity":58.13,"mslp":101052,"uvIndex":3,"significantWeatherCode":7,"precipitationRate":0.0,"probOfPrecipitation":17},{"time":"2025-03-14T13:00Z","screenTemperature":6.85,"screenDewPointTemperature":-0.69,"feelsLikeTemperature":4.12,"windSpeed10m":4.15,"windDirectionFrom10m":70,"windGustSpeed10m":7.25,"visibility":27266,"screenRelativeHumidity":59.11,"mslp":101099,"uvIndex":2,"significantWeatherCode":7,"precipitationRate":0.0,"probOfPrecipitation":12}]}}],"parameters":[{"totalSnowAmount":{"type":"Parameter","description":"Total Snow Amount Over Previous Hour","unit":{"label":"millimetres","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"mm"}}},"screenTemperature":{"type":"Parameter","description":"Screen Air Temperature","unit":{"label":"degrees Celsius","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"Cel"}}},"visibility":{"type":"Parameter","description":"Visibility","unit":{"label":"metres","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"m"}}},"windDirectionFrom10m":{"type":"Parameter","description":"10m Wind From Direction","unit":{"label":"degrees","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"deg"}}},"precipitationRate":{"type":"Parameter","description":"Precipitation Rate","unit":{"label":"millimetres per hour","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"mm/h"}}},"maxScreenAirTemp":{"type":"Parameter","description":"Maximum Screen Air Temperature Over Previous Hour","unit":{"label":"degrees Celsius","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"Cel"}}},"feelsLikeTemperature":{"type":"Parameter","description":"Feels Like Temperature","unit":{"label":"degrees Celsius","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"Cel"}}},"screenDewPointTemperature":{"type":"Parameter","description":"Screen Dew Point Temperature","unit":{"label":"degrees Celsius","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"Cel"}}},"screenRelativeHumidity":{"type":"Parameter","description":"Screen Relative Humidity","unit":{"label":"percentage","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"%"}}},"windSpeed10m":{"type":"Parameter","description":"10m Wind Speed","unit":{"label":"metres per second","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"m/s"}}},"probOfPrecipitation":{"type":"Parameter","description":"Probability of Precipitation","unit":{"label":"percentage","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"%"}}},"max10mWindGust":{"type":"Parameter","description":"Maximum 10m Wind Gust Speed Over Previous Hour","unit":{"label":"metres per second","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"m/s"}}},"significantWeatherCode":{"type":"Parameter","description":"Significant Weather Code","unit":{"label":"dimensionless","symbol":{"value":"https://datahub.metoffice.gov.uk/","type":"1"}}},"minScreenAirTemp":{"type":"Parameter","description":"Minimum Screen Air Temperature Over Previous Hour","unit":{"label":"degrees Celsius","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"Cel"}}},"totalPrecipAmount":{"type":"Parameter","description":"Total Precipitation Amount Over Previous Hour","unit":{"label":"millimetres","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"mm"}}},"mslp":{"type":"Parameter","description":"Mean Sea Level Pressure","unit":{"label":"pascals","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"Pa"}}},"windGustSpeed10m":{"type":"Parameter","description":"10m Wind Gust Speed","unit":{"label":"metres per second","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"m/s"}}},"uvIndex":{"type":"Parameter","description":"UV Index","unit":{"label":"dimensionless","symbol":{"value":"http://www.opengis.net/def/uom/UCUM/","type":"1"}}}}]}

# parse x:
# y = json.loads(json_string)

# the result is a Python dictionary:
# print(y["features"][1])

# convert into JSON:
# y = json.dumps(json_string)
#
# # the result is a JSON string:
# print(y)
# # ---------------------------------
# y = json.loads(y)
# print('\nLabel:', y["features"][0])

# f = open('jsondemo.js')
# data = json.load(f)
#
# print(data["mydata"]["color"])
# print(data["mydata"]["amount"])
# # Pull something out of the middle of an array
# print(data["mydata"]["arrayTest"][3])
# print(data["mydata"]["boolTest"])
# print(data["mydata"]["nullTest"])
#
# # Use a boolean value
# if data["mydata"]["boolTest"]:
#     print("So boolean!")
#
# # Dig down into a data structure
# print(data["mydata"]["addressBookEntry"]["address"]["city"])
#
# print("-- mydata properties: --")
# for p in data["mydata"]:
#     print(p)
#
# print("-- list addressBookEntry property names and values: --")
# for p in data["mydata"]["addressBookEntry"]:
#     print(p + ': ' + str(data["mydata"]["addressBookEntry"][p]))
#
# # Testing whether values are present.
# if "familyName" in data["mydata"]["addressBookEntry"]:
#     print("There is a family name value.")
# else:
#     print("There is no family name value.")
#
# if "phone" in data["mydata"]["addressBookEntry"]:
#     print("There is a phone value.")
# else:
#     print("There is no phone value.")
#
# f.close()
# --------------------------------------------------------
# x = {"name": "John", "age": 30, "married": True, "divorced": False, "children": ("Ann","Billy"), "pets": None, "cars": [{"model": "BMW 230", "mpg": 27.5}, {"model": "Ford Edge", "mpg": 24.1}]}

# convert into JSON ------------------------
# y = json.dumps(x)
# print('Data1', y)
#
# # Convert JSON to single quote string ------
# z = json.loads(y)
# print('Data2:', z)
#
# print('\nData3', z["features"])
# print('\nData4', z["features"][0]['geometry'])
# print('\nData5', z["features"][0]['properties'])  # -- embedded values in this Key
#
#
# print('\n')
#
# for key in z:
#    print("Key ID: %s , value: %s:" % (key, y[key]))

# -----------------------------------------------------------------
import torch
import torchvision
import subprocess

print('Cuda Available:', torch.cuda.is_available())

try:
    subprocess.check_output('nvidia-smi')
    print('Nvidia GPU detected!')
except Exception:
    print('No Nvidia GPU in system!')

# --------------------------------------------------
import torch
import GPUtil as gp

use_cuda = gp.getAvailable()
print('\nCUDA Available', use_cuda)
print(torch.version.cuda)

if use_cuda:
    print('__CUDNN VERSION:', torch.backends.cudnn.version())
    print('__Number CUDA Devices:', torch.cuda.device_count())
    print('__CUDA Device Name:', torch.cuda.get_device_name(0))
    print('__CUDA Device Total Memory [GB]:',torch.cuda.get_device_properties(0).total_memory/1e9)
else:
    print('GPU Not detected...')
    device = torch.device("cuda" if use_cuda else "cpu")
    print("Device In Use: ", device)

# Payload Tester ---------------------------#
from numba import jit, cuda
import numpy as np
# to measure exec time
from timeit import default_timer as timer

# ----- Factorial TIme ------
def heap_permutation(data, n):
    if n == 1:
        print(data)
        return

    for i in range(n):
        heap_permutation(data, n - 1)
        if n % 2 == 0:
            data[i], data[n - 1] = data[n - 1], data[i]
        else:
            data[0], data[n - 1] = data[n - 1], data[0]


def merge_sort(data):
    if len(data) <= 1:
        return

    mid = len(data) // 2
    left_data = data[:mid]
    right_data = data[mid:]

    merge_sort(left_data)
    merge_sort(right_data)

    left_index = 0
    right_index = 0
    data_index = 0

    while left_index < len(left_data) and right_index < len(right_data):
        if left_data[left_index] < right_data[right_index]:
            data[data_index] = left_data[left_index]
            left_index += 1
        else:
            data[data_index] = right_data[right_index]
            right_index += 1
        data_index += 1

    if left_index < len(left_data):
        del data[data_index:]
        data += left_data[left_index:]
    elif right_index < len(right_data):
        del data[data_index:]
        data += right_data[right_index:]

def binary_search(data, value):
    n = len(data)
    left = 0
    right = n - 1
    while left <= right:
        middle = (left + right) // 2
        if value < data[middle]:
            right = middle - 1
        elif value > data[middle]:
            left = middle + 1
        else:
            return middle
    raise ValueError('Value is not in the list')

def linear_search(data, value):
    for index in range(len(data)):
        if value == data[index]:
            return index
    raise ValueError('Value not found in the list')

def bubble_sort(data):
    swapped = True
    while swapped:
        swapped = False
        for i in range(len(data)-1):
            if data[i] > data[i+1]:
                data[i], data[i+1] = data[i+1], data[i]
                swapped = True


# normal function to run on cpu
def func(a):
    for i in range(10000000):
        a[i] += 1
    # function optimized to run on gpu

@jit(target_backend='cuda')
def func2(a):
    for i in range(10000000):
        a[i] += 1


if __name__ == "__main__":
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    n = 10000000
    a = np.ones(n, dtype=np.float64)

    start = timer()
    func(a)
    print("with CPU:", timer() - start)

    start = timer()
    func2(a)
    print("with GPU:", timer() - start)

    start = timer()
    binary_search(data, 8)
    print("with GPU:", timer() - start)

    # Merge Sort ------
    data = [9, 1, 7, 6, 2, 8, 5, 3, 4, 0]
    merge_sort(data)

    # --Bubble Sort ------
    bubble_sort(data)
    print(data)

    # -- Permutation Data
    data = [1, 2, 3]
    heap_permutation(data, len(data))
# -----------------

# import pycuda.driver as cuda
# import pycuda.autoinit
# from pycuda.compiler import SourceModule
