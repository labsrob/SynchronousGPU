import tkinter as tk
from Test66 import collectiveEoP  # or paste the class above in this file

root = tk.Tk()
root.title("EoP Test")
root.geometry("1900x900")

tab5 = tk.Frame(root)
tab5.pack(fill="both", expand=True)

app = collectiveEoP(tab5)
app.pack(fill="both", expand=True)

root.mainloop()