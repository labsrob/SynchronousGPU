import tkinter as tk

from tkinter import *
from tkinter.dialog import Dialog, DIALOG_ICON

import tkinter as tk
from tkinter.simpledialog import Dialog

#
# class MyDialog(Dialog):
#     def __init__(self, parent, **kwargs):
#         Dialog.__init__(self, parent, **kwargs)
#
#     def body(self, parent):
#         label = tk.Label(self, text='Can hold tkinter widgets such as label, listbox, etc...', wraplength=300,
#                          justify='left', anchor='w')
#         label.pack()
#
#     def validate(self):
#         return 1
#
#     def apply(self):
#         pass
#
#
# class Window:
#     def __init__(self, parent):
#         self.parent = parent
#         btn = tk.Button(parent, text='Click Me', command=self.opendialog)
#         btn.pack()
#
#     def opendialog(self):
#         MyDialog(self.parent)
#
#
# if __name__ == '__main__':
#     # This code will only be executed if the script is run as the main program
#     # metricsConfig()
#     #
#     # pop.mainloop()
#     root = tk.Tk()
#     Window(root)
#     root.mainloop()

import tkinter as tk

class App(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, height=42, width=42)
        self.entry = tk.Entry(self)
        self.entry.focus()
        self.entry.pack()
        self.clear_button = tk.Button(self, text="Clear text", command=self.clear_text)
        self.clear_button.pack()

    def clear_text(self):
        self.entry.delete(0, 'end')

def main():
    root = tk.Tk()
    App(root).pack(expand=True, fill='both')
    root.mainloop()

if __name__ == "__main__":
    main()
