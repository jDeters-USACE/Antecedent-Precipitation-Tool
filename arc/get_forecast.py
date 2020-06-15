# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

######################################
##  ------------------------------- ##
##          getForecast.py          ##
##  ------------------------------- ##
##     Written by: Jason Deters     ##
##  ------------------------------- ##
## Last Edited on:  16-May-2017     ##
##  ------------------------------- ##
######################################

"""Gets Rainfall Forecast data to plot on Antecedent Precipitation Tool output figure"""

from __future__ import (print_function, absolute_import)  # Python 3 support

# Import Standard Libraries
import os
import sys
import datetime
import time
import traceback

# Import 3rd Party Libraries
import urllib3
import json
import requests


# Find module path
MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
# Find ROOT folder
ROOT = os.path.split(MODULE_PATH)[0]

# import custom libraries
try:
    from .utilities import JLog
except Exception:
    TEST = os.path.exists('{}\\Python Scripts'.format(ROOT))
    if TEST:
        sys.path.append('{}\\Python Scripts\\utilities'.format(ROOT))
    else:
        sys.path.append('{}\\arc\\utilities'.format(ROOT))
    import JLog

L = JLog.PrintLog(Indent=2)

def get_json_multiple_ways(url=None):
    """Tries to pull JSON data from a URL using urllib3 first and then requests"""
    # Try urllib3
    try:
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED')
        response = http.request('GET', url)
        time.sleep(3)
        string_data = str(response.data, 'utf-8')
        json_conversion = json.loads(string_data)
        return json_conversion
    except Exception:
        urllib3_exception = traceback.format_exc()
    # Try Requests module
    try:
        content = requests.get(url)
        time.sleep(3)
        json_conversion = content.json()
        return json_conversion
    except Exception:
        requests_exception = traceback.format_exc()
        L.Write('    ---urllib3 Exception Traceback---')
        L.Write(urllib3_exception)
        L.Write('    ----------------------------------')
        L.Write('    ---Requests Exception Traceback---')
        L.Write(requests_exception)
        L.Write('    ----------------------------------')

class EightDayForecast(object):
    """Gets Rainfall Forecast data to plot on Antecedent Precipitation Tool output figure"""

    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
        self.key = '14e52c211e045a0f2b51bafc8eea36fb'
        self.days = []
        self.inches = []
        self.milimeters = []

    def __call__(self):
        self.yesterday()
        self.seven_day_forecast()
        return self.days, self.inches

    def seven_day_forecast(self):
        """Requests a 7-day forecast in JSON format and then parses just the dates and MMs from it"""
        url = 'https://api.darksky.net/forecast/{}/{},{}'.format(self.key, self.lat, self.lon)
        json_conversion = get_json_multiple_ways(url)
        daily = json_conversion['daily']
        daily_data = daily['data']
        # Print output heading
        L.Wrap('###############################')
        L.Wrap('## --- Rainfall Forecast --- ##')
        L.Wrap('###############################')
        # Get data
        for item in daily_data:
            timestamp = item['time']
            current_day = datetime.datetime.fromtimestamp(int(timestamp))
            self.days.append(current_day)
            precipitation_intensity = item['precipIntensity'] # inches per hour
            rain = float(precipitation_intensity)*24
            self.inches.append(rain)
            rain_mm = rain*25.4
            self.milimeters.append(rain_mm)
            # Print Current Day Data
            current_day_string = current_day.strftime('%Y-%m-%d')
            rain_mm_string = str(round(rain_mm, 2))
            while len(rain_mm_string) < 6:
                rain_mm_string = ' {}'.format(rain_mm_string)
            L.Wrap('### {} ## {} mm ###'.format(current_day_string, rain_mm_string))
        # Close output box
        L.Wrap('###############################')
        ### This section just makes the graph look better ###
        day_after = current_day + datetime.timedelta(days=1)
        self.days.append(day_after)
        self.inches.append(0)
        self.milimeters.append(0)
        ### This section just makes the graph look better ###

    def yesterday(self):
        """Requests yesterday's forecast data and then parses the date and mm of precip from the JSON"""
        ### This section just makes the graph look better ###
        two_days_ago = datetime.datetime.today()- datetime.timedelta(days=2)
        self.days.append(two_days_ago)
        self.inches.append(0)
        self.milimeters.append(0)
        ### This section just makes the graph look better ###
        yesterday = datetime.datetime.today()- datetime.timedelta(days=1)
        yesterday_string = yesterday.strftime('%Y-%m-%dT12:00:00')
        url = 'https://api.darksky.net/forecast/{}/{},{},{}'.format(self.key, self.lat, self.lon, yesterday_string)
        json_conversion = get_json_multiple_ways(url)
        daily = json_conversion['daily']
        daily_data = daily['data']
        for item in daily_data:
            timestamp = item['time']
            current_day = datetime.datetime.fromtimestamp(int(timestamp))
            self.days.append(current_day)
            precipitation_intensity = item['precipIntensity'] # self.inches per hour
            rain = float(precipitation_intensity)*24
            self.inches.append(rain)
            rain_mm = rain*25.4
            self.milimeters.append(rain_mm)
    # End of EightDays class


def main(lat, lon):
    """initializes and calls the EightDayForecast class, passing on the results"""
    instance = EightDayForecast(lat, lon)
    days, milimeters = instance()
    return days, milimeters

if __name__ == '__main__':
#    DAYS, MILIMETERS = main(46.925718, -117.682981)
#    for day, m in zip(DAYS, MILIMETERS):
#        L.Wrap(str(day))
#        L.Wrap(" " + str(m))

    DAYS, MILIMETERS = main(38.789972, -120.797499)
##    for day, m in zip(DAYS, MILIMETERS):
##        L.Wrap(str(day))
##        L.Wrap(" " + str(m))
