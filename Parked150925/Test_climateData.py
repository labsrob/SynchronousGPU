
# 2023 (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of Weather DataHub and is released under the
# BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
# (c) Met Office 2023

#########################################################################################
#
#           Client API key, latitude and longitude are the only mandatory parameters.
#
##########################################################################################
"""
--timesteps: There are three frequencies of timesteps available - hourly, three-hourly or daily
--latitude :  Provide the latitude of the location for the forecast. This should be a valid latitude, btw -90 and 90.
--longitude: Provide the longitude of the location for the forecast. This should be a valid longitude, btw -180 and 180.

Ref: https://github.com/MetOffice/weather_datahub_utilities/blob/main/site_specific_download/Documentation.md
"""

import requests
import argparse
import time
import sys
import json
import logging as log

log.basicConfig(filename='ss_download.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

base_url = "https://data.hub.api.metoffice.gov.uk/sitespecific/v0/point/"


def retrieve_forecast(baseUrl, timesteps, requestHeaders, latitude, longitude, excludeMetadata, includeLocation):
    url = baseUrl + timesteps

    headers = {'accept': "application/json"}
    headers.update(requestHeaders)
    params = {
        # 'excludeParameterMetadata': excludeMetadata,
        'includeLocationName': includeLocation,
        'latitude': latitude,
        'longitude': longitude
    }

    success = False
    retries = 5

    while not success and retries > 0:
        try:
            req = requests.get(url, headers=headers, params=params)
            success = True
        except Exception as e:
            log.warning("Exception occurred", exc_info=True)
            retries -= 1
            time.sleep(10)
            if retries == 0:
                log.error("Retries exceeded", exc_info=True)
                sys.exit()

    req.encoding = 'utf-8'
    print('REPLY:', req)
    # print('REPLY:', req.headers)
    print('\nREPLY1:', req.text)
    print('REPLY2:', " '" + req.text + "' \n")

    data = json.loads(req.text)
    print('SData1', data)

    print('\nSData2', data['type'])
    print('SData3', data['features'])
    # print('SData5', data['properties'])
    # # print('SData4', data['geometry'])
    # json.dumps(data, indent=4)

    # json.dumps(req, indent=4)
    # json.dumps(req.text, indent=4, separators=(". ", " = "))
    # json.dumps(req, indent=4, sort_keys=True)


    # print('Test', x)
    # y = json.loads(x)

    # json.dumps(x, indent=4, separators=(". ", " = "))
    # print(req.headers["longitude"])


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Retrieve the site-specific forecast for a single location"
    )
    parser.add_argument(
        "-t",
        "--timesteps",
        action="store",
        dest="timesteps",
        default="hourly",
        help="The frequency of the timesteps provided in the forecast. The options are hourly, three-hourly or daily",
    )
    parser.add_argument(
        "-m",
        "--metadata",
        action="store",
        dest="excludeMetadata",
        default="FALSE",
        help="Provide a boolean value for whether parameter metadata should be excluded."
    )
    parser.add_argument(
        "-n",
        "--name",
        action="store",
        dest="includeLocation",
        default="TRUE",
        help="Provide a boolean value for whether the location name should be included."
    )
    parser.add_argument(
        "-y",
        "--latitude",
        action="store",
        dest="latitude",
        default="50.844853",
        help="Provide the latitude of the location you wish to retrieve the forecast for."
    )
    parser.add_argument(
        "-x",
        "--longitude",
        action="store",
        dest="longitude",
        default="-1.116545",
        help="Provide the longitude of the location you wish to retrieve the forecast for."
    )
    parser.add_argument(
        "-k",
        "--apikey",
        action="store",
        dest="apikey",
        default="eyJ4NXQiOiJOak16WWpreVlUZGlZVGM0TUdSalpEaGtaV1psWWpjME5UTXhORFV4TlRZM1ptRTRZV1JrWWc9PSIsImtpZCI6ImdhdGV3YXlfY2VydGlmaWNhdGVfYWxpYXMiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJsYWJzcm9iQGdtYWlsLmNvbUBjYXJib24uc3VwZXIiLCJhcHBsaWNhdGlvbiI6eyJvd25lciI6ImxhYnNyb2JAZ21haWwuY29tIiwidGllclF1b3RhVHlwZSI6bnVsbCwidGllciI6IlVubGltaXRlZCIsIm5hbWUiOiJzaXRlX3NwZWNpZmljLWNhYmI5MWZhLWQ0ZDgtNDg5NS04MzRhLWQ2ZWI1OWM0YWYwMCIsImlkIjo4ODI1LCJ1dWlkIjoiZDNiNWM1ZDktMTQ2Zi00MjNhLWI1NzctZDY3NTljY2I4YjIyIn0sImlzcyI6Imh0dHBzOlwvXC9hcGktbWFuYWdlci5hcGktbWFuYWdlbWVudC5tZXRvZmZpY2UuY2xvdWQ6NDQzXC9vYXV0aDJcL3Rva2VuIiwidGllckluZm8iOnsid2RoX3NpdGVfc3BlY2lmaWNfZnJlZSI6eyJ0aWVyUXVvdGFUeXBlIjoicmVxdWVzdENvdW50IiwiZ3JhcGhRTE1heENvbXBsZXhpdHkiOjAsImdyYXBoUUxNYXhEZXB0aCI6MCwic3RvcE9uUXVvdGFSZWFjaCI6dHJ1ZSwic3Bpa2VBcnJlc3RMaW1pdCI6MCwic3Bpa2VBcnJlc3RVbml0Ijoic2VjIn19LCJrZXl0eXBlIjoiUFJPRFVDVElPTiIsInN1YnNjcmliZWRBUElzIjpbeyJzdWJzY3JpYmVyVGVuYW50RG9tYWluIjoiY2FyYm9uLnN1cGVyIiwibmFtZSI6IlNpdGVTcGVjaWZpY0ZvcmVjYXN0IiwiY29udGV4dCI6Ilwvc2l0ZXNwZWNpZmljXC92MCIsInB1Ymxpc2hlciI6IkphZ3Vhcl9DSSIsInZlcnNpb24iOiJ2MCIsInN1YnNjcmlwdGlvblRpZXIiOiJ3ZGhfc2l0ZV9zcGVjaWZpY19mcmVlIn1dLCJ0b2tlbl90eXBlIjoiYXBpS2V5IiwiaWF0IjoxNzM3MDQwNDY3LCJqdGkiOiJhNzI2NTJmZi1kOTQzLTQ4MGItODVhZC02N2Q0MTMyM2NhYzgifQ==.RBKYn5edS7dcly11Duvzg-eTX5HKb0AyTNqOYLEyxgn6AS0_d87zb2fOLklRBBVYnAzscAoJoP5DHG0mMhbcvCq1qwmrCuf-nPTwTqMTdbUwGc3QmZ3ZNTXN3zdHO5C7FU6_BnFAd-69wsXva37dY_C7mWiy7evj65AO7SlYa1a87isuwyRM_AaKQ6H_nBBEJ0DbLy1ANu6ImT5BbQVb_X_uJ1-OW-3S8ga49VSnQuSP-ND2cKWTGu9ZYEmte0MBU1bktXTmG26k74E5sXwiXVCmPF50clHrBo6cDo_Z1u-l9w38SlLqIF4Uc0KLmOgUgrG3tZ1wQpveZe9atzBpUg==",
        help="REQUIRED: Your WDH API Credentials."
    )

    args = parser.parse_args()

    timesteps = args.timesteps
    includeLocation = args.includeLocation
    excludeMetadata = args.excludeMetadata
    latitude = args.latitude
    longitude = args.longitude
    apikey = args.apikey

    # Client API key must be supplied
    if apikey == "":
        print("ERROR: API credentials must be supplied.")
        sys.exit()
    else:
        requestHeaders = {"apikey": apikey}

    if latitude == "" or longitude == "":
        print("ERROR: Latitude and longitude must be supplied")
        sys.exit()

    if timesteps != "hourly" and timesteps != "three-hourly" and timesteps != "daily":
        print("ERROR: The available frequencies for timesteps are hourly, three-hourly or daily.")
        sys.exit()

    retrieve_forecast(base_url, timesteps, requestHeaders, latitude, longitude, excludeMetadata, includeLocation)

