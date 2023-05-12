#  This software was developed by United States Army Corps of Engineers (USACE)
#  employees in the course of their official duties.  USACE used copyrighted,
#  open source code to develop this software, as such this software
#  (per 17 USC § 101) is considered "joint work."  Pursuant to 17 USC § 105,
#  portions of the software developed by USACE employees in the course of their
#  official duties are not subject to copyright protection and are in the public
#  domain.
#
#  USACE assumes no responsibility whatsoever for the use of this software by
#  other parties, and makes no guarantees, expressed or implied, about its
#  quality, reliability, or any other characteristic.
#
#  The software is provided "as is," without warranty of any kind, express or
#  implied, including but not limited to the warranties of merchantability,
#  fitness for a particular purpose, and noninfringement.  In no event shall the
#  authors or U.S. Government be liable for any claim, damages or other
#  liability, whether in an action of contract, tort or otherwise, arising from,
#  out of or in connection with the software or the use or other dealings in the
#  software.
#
#  Public domain portions of this software can be redistributed and/or modified
#  freely, provided that any derivative works bear some notice that they are
#  derived from it, and any modified versions bear some notice that they have
#  been modified.
#
#  Copyrighted portions of the software are annotated within the source code.
#  Open Source Licenses, included in the source code, apply to the applicable
#  copyrighted portions.  Copyrighted portions of the software are not in the
#  public domain.


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
    # Reverse compatibility step - Add utilities folder to path directly
    PYTHON_SCRIPTS_FOLDER = os.path.join(ROOT, 'Python Scripts')
    TEST = os.path.exists(PYTHON_SCRIPTS_FOLDER)
    if TEST:
        UTILITIES_FOLDER = os.path.join(PYTHON_SCRIPTS_FOLDER, 'utilities')
        sys.path.append(UTILITIES_FOLDER)
    else:
        ARC_FOLDER = os.path.join(ROOT, 'arc')
        UTILITIES_FOLDER = os.path.join(ARC_FOLDER, 'utilities')
        sys.path.append(UTILITIES_FOLDER)
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
                 distance, elevDiff, weightedDiff, StartDate, EndDate, ObservationDate,
                 CurrentRollingStartDate):
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
        self.ObservationDate = ObservationDate
        self.CurrentRollingStartDate = CurrentRollingStartDate

    def __call__(self):
        aclass = StationManager(self.dataType, self.index, self.name, self.location, self.locationTuple,
                      self.elevation, self.distance, self.elevDiff, self.weightedDiff,
                      self.StartDate, self.EndDate, self.ObservationDate,
                      self.CurrentRollingStartDate)
        return aclass


class StationManager(object):
    """
    Object representing one of NOAA's GHCN Weather Stations.
    Downloads the data from NOAA's servers, calculates the relationship
    between the station location and a given point, and slices the data
    by selected type and date range.
    """
    def __init__(self, dataType, index, name, location, locationTuple, elevation,
                 distance, elevDiff, weightedDiff, StartDate, EndDate, ObservationDate,
                 CurrentRollingStartDate):
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
        self.ObservationDate = ObservationDate
        self.CurrentRollingStartDate = CurrentRollingStartDate
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
                current_values = df_copy.loc[self.CurrentRollingStartDate:self.ObservationDate]
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

    def updateValues(self, site_loc, site_elev, StartDate, EndDate, CurrentRollingStartDate):
        """Updates station values based on new location and date range"""
        self.distance = round(great_circle(site_loc, self.locationTuple).miles, 3)
        self.elevDiff = round(abs(site_elev - self.elevation), 3)
        self.weightedDiff = round(self.distance*((self.elevDiff/1000)+0.45), 3)
        self.StartDate = StartDate
        self.EndDate = EndDate
        self.CurrentRollingStartDate = CurrentRollingStartDate
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
#                       CurrentRollingStartDate='2018-07-01')
#        print('Printing stats...')
#        f.print_stats()

    print('Creating constructor...')
    x = Constructor('PRCP', 'US1CAED0023', 'EL DORADO HILLS 0.9NNW', '38.598, -121.0869', (38.5, -121.5), 436.023636, 19.968887027645902, 1879.0777612485354, 46.50909069297444, '1991-09-01', '2023-04-22', '2023-03-25', '2022-12-26')
    print('Constructing instance...')
    f = x()
    print('Printing stats...')
    f.print_stats()
