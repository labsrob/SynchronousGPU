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




def bufferEOF(fname, N):
    # open index tracker file, and load the     # values in the end of file
    with open(fname) as file:
        for line in (file.readlines()[-N:]):    # N = number of lines to read
            oem = line
        print('\nEND OF FILE:', oem)
        print(line, end='')
    return oem


fname = 'C:\\Users\\DevEnv\\PycharmProjects\\SynchronousGPU\\RT_Index_Log\\IDXLog_20240507Z.txt'
eoF = bufferEOF(fname, 1)
print('\nParsed1:', eoF[10:])

testY = list(eoF[10:])
print('Parsed2', testY)

lines = eoF[10:].splitlines()
print('Parsed3', lines)
