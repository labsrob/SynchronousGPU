


base_url = 'https://api.openweathermap.org/data/2.5/weather?'

latit = 50.844853
longi = -1.116545
APIKey = 'ba8d89fa4ac773e35670847cca5154e2'

weatherVar = 'lat=50.844853&lon=-1.116545&appid=ba8d89fa4ac773e35670847cca5154e2'

wVar = 'lat=latit&lon=longi&appid=APIKey'

# 'https://api.openweathermap.org/data/2.5/weather?lat=50.844853&lon=-1.116545&appid=ba8d89fa4ac773e35670847cca5154e2'

'https://pro.openweathermap.org/data/2.5/forecast/climate?lat=50.844853&lon=-1.116545&appid=ba8d89fa4ac773e35670847cca5154e2'
# 'https://pro.openweathermap.org/data/2.5/forecast/climate?zip=PO64PX,UK&appid=ba8d89fa4ac773e35670847cca5154e2'
#####################################
# by Johannes Kinzig (M. Sc.)		#
# https://johanneskinzig.de			#
#####################################

import requests
# import BeautifulSoup

## Tested with S7 1212C AC/DC/Rly and FW Version 4.2.1

#########################################
#           Login                       #
#########################################
payload_login = {'Login': 'WebUser', 'Password': '123456789', 'Redirection': ''}
posturl_login = 'https://192.168.178.50/FormLogin'

headers = {
    'Host': '192.168.178.50',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://192.168.178.50/Portal/Portal.mwsl',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Content-Length': '45',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

session = requests.Session()
login_response = session.post(posturl_login, data=payload_login, headers=headers, verify=False)
print(login_response.status_code)
print(login_response.headers)
#print login_response.cookies.get_dict() # will stay empty
webpage =  login_response.content

#########################################
#     Extract authentication Cookie     #
#########################################
webpage_soup = BeautifulSoup.BeautifulSoup(webpage)
auth_cookie_part = webpage_soup.find('input', attrs={'name': 'Cookie'})
auth_cookie_part = str(auth_cookie_part)
auth_cookie = auth_cookie_part.split('"')[5]
print("Authentication cookie: ", auth_cookie)

#########################################
#     Set Authentication Cookie         #
#########################################
s7cookies = dict(siemens_ad_session=auth_cookie, coming_from_login='true')

#########################################
# Run Actions (require authentication)  #
#########################################
payload_control = {'"webHMIData".webHMI_DO1_User': '1', '"webHMIData".webHMI_DO0_User': '1'}
usage = session.post('https://192.168.178.50/awp/AnalogInputs/api.io', cookies=s7cookies, data=payload_control, verify=False)
print(usage.status_code)
print(usage.headers)
print(usage.content)

#########################################
#           Logout                      #
#########################################
payload_logout = {'Cookie': auth_cookie, 'Redirection': ''}
posturl_logout = 'https://192.168.178.50/FormLogin?LOGOUT'
logout = session.post(posturl_logout, cookies=s7cookies, headers=headers, data=payload_logout, verify=False)
print(logout.status_code)
print(logout.headers)
#print logout.content


"""
if @10Hz
@6m/min = (10cm/sec),   [100cm/10sec]  - @ 10.0sec * 10 = 100 * 4 heads = 400 data points / mt
@8m/min = (13.3cm/sec), [100cm/7.5sec] - @ 07.5sec * 10 = 075 * 4 heads = 300 data points / mt
12m/min = (20cm/sec),   [100cm/5sec]   - @ 05.0sec * 10 = 050 * 4 heads = 200 data points / mt
"""

# -----------------------------------------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
x = np.arange(0, 10, 0.1)
y1 = 0.05 * x**2
y2 = -1 *y1

fig, ax1 = plt.subplots()

ax2 = ax1.twinx()
ax1.plot(x, y1, 'g-')
ax2.plot(x, y2, 'b-')

ax1.set_xlabel('X data')
ax1.set_ylabel('Y1 data', color='g')
ax2.set_ylabel('Y2 data', color='b')

plt.show()