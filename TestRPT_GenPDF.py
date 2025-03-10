import time
import math
import datetime
import pandas as pd
import matplotlib
from pylab import title, figure, xlabel, ylabel, xticks, bar, legend, axis, savefig
from fpdf import FPDF


# Initialise dataframe from Tables
rID = ' Layer (EoP)'

df = pd.DataFrame()

df['RingID'] = ['Ring1', 'Ring2', 'Ring3', 'Ring4']
df["Actual"] = [2.2, 2.0, 2.8, 2.1]
df["Nominal"] = [1.8, 1.9, 2.2, 2.2]
df["StdDev"] = [round(((df['Actual'][0] - df['Nominal'][0])/math.sqrt(2)), 2), round(((df['Actual'][1] - df['Nominal'][1])/math.sqrt(2)), 2), round(((df['Actual'][2] - df['Nominal'][2])/math.sqrt(2)), 2),  round(((df['Actual'][3] - df['Nominal'][3])/math.sqrt(2)), 2)]
# df["StdDev"] = [0.25, 0.16, 0.27, 0.32]
df["Tolerance"] = [round(((df['Actual'][0] - df['Nominal'][0])/df['Nominal'][0]), 2), round(((df['Actual'][1] - df['Nominal'][1])/df['Nominal'][1]),2), round(((df['Actual'][2] - df['Nominal'][2])/df['Nominal'][2]), 2), round(((df['Actual'][3] - df['Nominal'][3])/df['Nominal'][3]), 2)]
# df["Tolerance"] = [0.5, 0.4, 0.39, 0.42]
if df['Tolerance'][0] > 0.1:
    A = 'CHECK'
else:
    A = 'OK'
# -----------------
if df['Tolerance'][1] > 0.1:
    B = 'CHECK'
else:
    B = 'OK'
# -----------------
if df['Tolerance'][2] > 0.1:
    C = 'CHECK'
else:
    C = 'OK'
# -----------------
if df['Tolerance'][3] > 0.1:
    D = 'CHECK'
else:
    D = 'OK'
df["Status"] = [A, B, C, D]

title(rID+" Report")
xlabel('Ring Analytics')
ylabel('Rated Quality')

a = [1.0, 2.0, 3.0, 4.0]
# a = a.sort()
n = [x - 1.2 for x in a]
s = [x - 1.9 for x in a]

proj = 12332
pID = 3222
oID = 'TC'
dID = datetime.datetime.now()
lID = 24
# processID = 'ROLLER PRESSURE'
# processID = 'TAPE TEMPERATURE'
# processID = 'TAPE SPEED'
processID = 'TAPE PLACEMENT ERROR'


xticks(a, df['RingID'])
bar(a, df['Actual'], width=0.3, color="blue", label="Actual")
bar(n, df['Nominal'], width=0.3, color="#51eb87", label="Nominal")
bar(s, df["StdDev"], width=0.3, color="#eb379c", label="StDev")

legend()
axis([0, 4, 0, 5])
savefig('barchart.png')

pdf = FPDF()
pdf.add_page()
pdf.set_xy(0, 0)
pdf.set_font('arial', 'B', 14)
pdf.cell(60)
pdf.cell(75, 10, "End of" +rID+ " Report", 0, 2, 'C')
pdf.cell(90, 10, " ", 0, 2, 'C')

pdf.cell(-40)
pdf.cell(5, 10, "Customer Project ID: " + (str(proj)), 0, 2, 'L')
pdf.cell(5, 10, "Pipe ID                      : " + (str(pID)), 0, 2, 'L')
pdf.cell(5, 10, "Operators ID            : " + (str(oID)), 0, 2, 'L')
pdf.cell(5, 10, "Date Time                : " + (str(dID)), 0, 2, 'L')
pdf.cell(5, 10, "Layer Number         : " + (str(lID)), 0, 2, 'L')
# pdf.cell(5, 10, "Process Name         : " + (str(processID)), 0, 2, 'L')

pdf.cell(40)
pdf.cell(90, 10, " ", 0, 2, 'C')
# draw a rectangle over the text area for Report header ----
pdf.rect(x=20.0, y=20.5, w=150.0, h=50, style='')
# construct report header
pdf.cell(-40)
pdf.cell(5, 10,  (str(processID)), 0, 2, 'L')
pdf.cell(35, 8, 'RingID', 1, 0, 'C')
pdf.cell(25, 8, 'Actual', 1, 0, 'C')
pdf.cell(25, 8, 'Nominal', 1, 0, 'C')
pdf.cell(25, 8, "StdDev", 1, 0, 'C')
pdf.cell(20, 8, "Tol(±)", 1, 0, 'C')
pdf.cell(20, 8, "Status", 1, 2, 'C')
pdf.set_font('arial', '', 12)
pdf.cell(-130)

for i in range(0, len(df)):
    print('Iteration ...')
    pdf.cell(35, 8, '%s' % (str(df.RingID.iloc[i])), 1, 0, 'C')    # 1: Next line under
    pdf.cell(25, 8, '%s' % (str(df.Actual.iloc[i])), 1, 0, 'C')    # 0: to the right
    pdf.cell(25, 8, '%s' % (str(df.Nominal.iloc[i])), 1, 0, 'C')
    pdf.cell(25, 8, '%s' % (str(df.StdDev.iloc[i])), 1, 0, 'C')
    pdf.cell(20, 8, '%s' % (str(df.Tolerance.iloc[i])), 1, 0, 'C')
    if str(df["Status"].iloc[i]) == "OK":
        pdf.set_fill_color(0, 255, 0)
        pdf.cell(20, 8, '%s' % (str(df["Status"].iloc[i])), 1, 2, 'C', 1)
    else:
        pdf.set_fill_color(255, 255, 0)
        pdf.cell(20, 8, '%s' % (str(df["Status"].iloc[i])), 1, 2, 'C', 1)
    pdf.cell(-130)                                                                            # newly added for testing
pdf.cell(90, 20, " ", 0, 2, 'C')                                    # 2: place new line below

pdf.cell(-30)
pdf.image('barchart.png', x=10, y=135, w=0, h=130, type='', link='')

# pdf.set_font('arial', '', 8)
pdf.set_font('helvetica', '', 7)
with pdf.rotation(angle=90, x=3, y=280):
    pdf.text(10, 280, "Statistical Process Control generated report - "+(str(dID)))

pdf.output('testReport26.pdf', 'F')