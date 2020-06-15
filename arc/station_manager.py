# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
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
##       station_manager.py         ##
##  ------------------------------- ##
##     Written by: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on: 2020-05-27    ##
##  ------------------------------- ##
######################################

"""
Creates an object representing one of NOAA's GHCN Weather Stations.
Downloads the data from NOAA's servers, calculates the relationship 
between the station location and a given point, and slices the data
by selected type and date range.
"""

# Import built-in modules
import os
import sys
import traceback
import time

# Import third-party modules
from geopy.distance import great_circle
import ulmo
import numpy

# Find module path
MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
# Find ROOT folder
ROOT = os.path.split(MODULE_PATH)[0]

# Import custom modules from Utilities folder
try:
    from .utilities import JLog
except Exception:
    TEST = os.path.exists('{}\\Python Scripts'.format(ROOT))
    if TEST:
        sys.path.append('{}\\Python Scripts\\utilities'.format(ROOT))
    else:
        sys.path.append('{}\\arc\\utilities'.format(ROOT))
    import JLog

# CLASS DEFINITIONS
class Constructor(object):
    """
    Creates an object representing one of NOAA's GHCN Weather Stations.
    Downloads the data from NOAA's servers, calculates the relationship 
    between the station location and a given point, and slices the data
    by selected type and date range.
    """
    def __init__(self, dataType, index, name, location, locationTuple, elevation,
                 distance, elevDiff, weightedDiff, StartDate, EndDate,
                 currentRollingStartDate):
        self.L = JLog.PrintLog()
        self.dataType = dataType
        self.index = index
        self.name = name
        self.location = location
        self.locationTuple = locationTuple
        self.elevation = elevation
        self.distance = distance
        self.elevDiff = elevDiff
        self.weightedDiff = weightedDiff
        self.StartDate = StartDate
        self.EndDate = EndDate
        self.currentRollingStartDate = currentRollingStartDate

    def __call__(self):
        aclass = Main(self.dataType, self.index, self.name, self.location, self.locationTuple,
                      self.elevation, self.distance, self.elevDiff, self.weightedDiff,
                      self.StartDate, self.EndDate, self.currentRollingStartDate)
        return aclass


class Main(object):
    """
    Object representing one of NOAA's GHCN Weather Stations.
    Downloads the data from NOAA's servers, calculates the relationship 
    between the station location and a given point, and slices the data
    by selected type and date range.
    """
    def __init__(self, dataType, index, name, location, locationTuple, elevation,
                 distance, elevDiff, weightedDiff, StartDate, EndDate,
                 currentRollingStartDate):
        self.L = JLog.PrintLog()
        self.dataType = dataType
        self.index = index
        self.name = str(name)
        self.location = str(location)
        self.locationTuple = locationTuple
        self.elevation = round(float(elevation), 3)
        self.distance = round(float(distance), 3)
        self.elevDiff = round(float(elevDiff), 3)
        self.weightedDiff = round(float(weightedDiff), 3)
        self.StartDate = StartDate
        self.EndDate = EndDate
        self.currentRollingStartDate = currentRollingStartDate
        self.data = None
        self.Values = None
        self.actual_rows = 0
        self.current_actual_rows = 0
        self.run()
    # End of __init__

    def run(self):
        """Download All Station Data and send it to the trimData function"""
        tries = 5
        while tries > 0:
            try:
                self.data = ulmo.ncdc.ghcn_daily.get_data(self.index,
                                                          elements=self.dataType,
                                                          update=True,
                                                          as_dataframe=True)
                tries = 0
                self.trimData()
            except Exception:
                #self.L.Write(traceback.format_exc())
                tries -= 1
                time.sleep(2)
    # End of Run

    def trimData(self):
        """Trims data to current date range"""
        self.Values = None
        self.actual_rows = 0
        self.current_actual_rows = 0
        # GET VALUES
        try:
            # Copying prcp data
            try:
                df_copy = self.data[self.dataType].copy()
            except KeyError:
                self.L.Write('The station "{}" lacked PRCP data (Likely a server-side glitch)'.format(self.name))
                keys = self.data.keys()
                self.L.Write('  For debugging: The following data types were found: {}'.format(keys))
                num_rows = 0
            try:
                # Slicing relevant rows
                self.Values = df_copy.loc[self.StartDate:self.EndDate, 'value']
                del df_copy
                self.Values.replace('', numpy.nan, inplace=True)
                self.Values.dropna(inplace=True)
                # Index Values and count rows
                self.Values.index = self.Values.index.to_timestamp()
                num_rows = len(self.Values.index)
                # Filter out any station with a year with no precipitation
                if self.dataType == 'PRCP':
                    days = 365
                    daySum = 0
                    for row in self.Values.iteritems():
                        if days < 1:
                            if daySum < 1:
                                self.L.Wrap("Whole year of Zeros!  ---Excluding This Dataset---")
                                num_rows = 0
                                break
                            days = 365
                            daySum = 0
                        days -= 1
                        daySum += row[1]
            except UnboundLocalError:
                print("UnboundLocalError")
                pass
            if num_rows > 1:
                num_null = self.Values.isnull().sum().sum()
                self.actual_rows = num_rows - num_null
                # Slicing just current year rows to perform separate tests
                df_copy = self.Values.copy()
                current_values = df_copy.loc[self.currentRollingStartDate:self.EndDate]
                current_values.replace('', numpy.nan, inplace=True)
                current_values.dropna(inplace=True)
                current_num_rows = len(current_values.index)
                test = current_num_rows > 1
                if test:
                    current_num_null = current_values.isnull().sum().sum()
                    self.current_actual_rows = current_num_rows - current_num_null
                del df_copy
        except Exception as exc_str:
#            self.L.Write(traceback.format_exc())
            self.L.Write(exc_str)
    # End of trimData

    def updateValues(self, site_loc, site_elev, StartDate, EndDate, currentRollingStartDate):
        """Updates station values based on new location and date range"""
        self.distance = round(great_circle(site_loc, self.locationTuple).miles, 3)
        self.elevDiff = round(abs(site_elev - self.elevation), 3)
        self.weightedDiff = round(self.distance*((self.elevDiff/1000)+0.45), 3)
        self.StartDate = StartDate
        self.EndDate = EndDate
        self.currentRollingStartDate = currentRollingStartDate
        self.trimData()

    def print_stats(self):
        """Prints stats..."""
        print('actual_rows = {}'.format(self.actual_rows))
        print('current_actual_rows = {}'.format(self.current_actual_rows))
        print('weightedDiff = {}'.format(self.weightedDiff))

    def __str__(self):
        return '{}'.format(self.name)


########################################################################

if __name__ == '__main__':
#    print('Creating constructor...')
#    x = Constructor('PRCP', 'USC00044484', 'KELSEY 1 N', '38.8089, -120.8208', (38.8089, -120.8208), 436.023636, 19.968887027645902, 1879.0777612485354, 46.50909069297444, '1987-09-01', '2018-10-15', '2018-07-01')
#    print('Constructing instance...')
#    f = x()
#    print('Printing stats...')
#    f.print_stats()
#    for x in range(10):
#        print('Updating Values...')
#        f.updateValues(site_loc=(38.789972, -120.797499),
#                       site_elev=436.023636,
#                       StartDate='1987-09-01',
#                       EndDate='2018-10-15',
#                       currentRollingStartDate='2018-07-01')
#        print('Printing stats...')
#        f.print_stats()

    print('Creating constructor...')
    x = Constructor('PRCP', 'US1CAED0023', 'EL DORADO HILLS 0.9NNW', '38.598, -121.0869', (38.5, -121.5), 436.023636, 19.968887027645902, 1879.0777612485354, 46.50909069297444, '1987-09-01', '2018-10-15', '2018-07-01')
    print('Constructing instance...')
    f = x()
    print('Printing stats...')
    f.print_stats()
