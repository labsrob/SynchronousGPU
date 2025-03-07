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
# # # Create some placeholder labels (widgets)
# # text1 = tk.Label(root, text="Label 1")
# # text2 = tk.Label(root, text="Label 2")
# # text3 = tk.Label(root, text="Label 3")
# # text4 = tk.Label(root, text="Label 4")
# #
# # # Place widgets in the grid using tkinter's grid manager
# # text1.grid(row=0, column=0)
# # text2.grid(row=1, column=0, columnspan=2)
# # text3.grid(row=0, column=1)
#
# root.mainloop()


# -------------------------------------------------------------------

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
#
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
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ipywidgets as widgets
import seaborn as sns

# Get dataset
data_url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/cases_deaths/total_deaths_per_million.csv"
df = pd.read_csv(data_url, index_col=0, parse_dates=[0], engine='python')

# na values = 0
df.fillna(0, inplace=True)
df.head()

# add year-week column
df['Year_Week'] = df.index.to_period('W').strftime('%Y-%U')

# keep only last day of week and change to datetime type
df = df.groupby(df['Year_Week']).last('1D')
df.index = pd.to_datetime(df.index + '-0', format='%Y-%U-%w')

# drop columns that aren't a country
df_country = df.drop(['World',
                      'Africa',
                      'Asia',
                      'Europe',
                      'European Union',
                      'High income',
                      'Low income',
                      'Lower middle income',
                      'North America',
                      'South America',
                      'Upper middle income'],
                     axis=1)


# create function to update plot based on selected country
def update_plot(country):
    ax.clear()  # clear existing plot
    ax.plot(df.index, df_country[country])  # plot selected country

    # set x-axis tick locations and labels
    xticks = pd.date_range(start=df_country.index[0].strftime('%Y-01-01'), end=df_country.index[-1], freq='AS')
    xticklabels = [x.strftime('%Y') for x in xticks]
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_title(f"Total deaths per million ({country})")  # update plot title
    ax.set_xlabel("Date")
    ax.set_ylabel("Deaths per million")
    fig.canvas.draw()  # redraw canvas


# create drop-down menu with country names as options
country_dropdown = widgets.Dropdown(
    options=df_country.columns,
    value=df_country.columns[0],
    description='Country'
)

# create plot
fig, ax = plt.subplots()
update_plot(country_dropdown.value)  # initial plot

# set up widget interaction
output = widgets.Output()
display(country_dropdown, output)


def on_change(change):
    if change['type'] == 'change' and change['name'] == 'value':
        with output:
            output.clear_output()
            update_plot(change['new'])
            display(fig)


country_dropdown.observe(on_change)