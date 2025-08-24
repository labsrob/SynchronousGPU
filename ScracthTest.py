# # Importing tkinter to make gui in python
# from tkinter import*
#
# # Importing tkPDFViewer to place pdf file in gui.
# # In tkPDFViewer library there is
# # an tkPDFViewer module. That I have imported as pdf
# from tkPDFViewer import tkPDFViewer as pdf
#
# # Initializing tk
# root = Tk()
#
# # Set the width and height of our root window.
# root.geometry("550x750")
#
# # creating object of ShowPdf from tkPDFViewer.
# v1 = pdf.ShowPdf()
#
# # Adding pdf location and width and height.
# v2 = v1.pdf_view(root, pdf_location=r"location", width=80, height=100)
#
# # Placing Pdf in my gui.
# v2.pack()
# root.mainloop()

# ---------------------------------------------------------------------[]


# ----------------------------------------[]
# importing modules
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
from fontTools import ttLib
import pyautogui

# initializing variables with values
fileName = 'SamplePDF.pdf'
image = '200x120.png'

documentTitle = 'Test Sample'
title = 'TCP01-WON#_224744'
subTitle = 'Enf of Layer Quality Report'
textLines = ['Technology makes us aware of', 'the world around us.',
			 'The object manages file input and output, and offers a convenient way of accessing tables',
			 'Tables will be only decompiled when necessary, ie. when they’re actually accessed']


pdf = canvas.Canvas(fileName)
pdf.setTitle(documentTitle)
pdfmetrics.registerFont(TTFont('abc', 'arial.ttf'))

pdf.setFont('abc', 36)
pdf.drawCentredString(300, 770, title)

# colour and putting it on the canvas
pdf.setFillColorRGB(0, 0, 255)
pdf.setFont("Courier-Bold", 24)
pdf.drawCentredString(290, 720, subTitle)

# drawing a line
pdf.line(30, 710, 550, 710)

# creating a multiline text using
text = pdf.beginText(40, 680)
text.setFont("Courier", 18)
text.setFillColor(colors.black)
pdf.drawInlineImage(image, 130, 400)

for line in textLines:
	text.textLine(line)
pdf.drawText(text)

# drawing a image at the
# specified (x.y) position


# saving the pdf
pdf.save()
# ---------------------------
#importing pdfkit
import pdfkit

# calling the from file method to convert file to pdf
pdfkit.from_file('file.html', 'file.pdf')
