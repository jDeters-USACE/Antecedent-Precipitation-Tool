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
##         anteProcess.py           ##
##  ------------------------------- ##
##      Writen by: Jason Deters     ##
##      Edited by: Joseph Gutenson  ##
##      Edited by: Chase Hamilton   ##
##  ------------------------------- ##
##    Last Edited on: 2022-11-10    ##
##  ------------------------------- ##
######################################

# Import Standard Libraries
import os
import sys
import time
from datetime import datetime, timedelta
import multiprocessing
import traceback
import warnings
import pickle
import stat
#from operator import itemgetter # No longer used

# Get root folder
MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.dirname(MODULE_PATH)

# Ulmo throws annoying warnings...
warnings.filterwarnings("ignore")

# Import 3rd Party Libraries

import requests
import urllib3
import json
import numpy
import pandas
import ulmo
from geopy.distance import great_circle
import matplotlib.pyplot as plt
#from matplotlib.legend_handler import HandlerLine2D # No longer used
import matplotlib.dates as dates
import matplotlib.ticker as ticker
from matplotlib import rcParams
import pylab

# Stop annoying urllib3 errors for EPQS tests
# import logging
# logging.getLogger("urllib3").setLevel(logging.ERROR)

# Import Custom Modules
try:
    from . import query_climdiv
    from . import process_manager
    from . import date_calcs
    from . import getElev
    from . import station_manager
    from . import get_forecast
    from .utilities import JLog
    from .utilities import web_wimp_scraper
    from . import netcdf_parse_all
except Exception:
    import query_climdiv
    import process_manager
    import date_calcs
    import getElev
    import station_manager
    import get_forecast
    # Add utilities folder to path directly
    PYTHON_SCRIPTS_FOLDER = os.path.join(ROOT, 'Python Scripts')
    TEST = os.path.exists(PYTHON_SCRIPTS_FOLDER)
    if TEST:
        sys.path.append(PYTHON_SCRIPTS_FOLDER)
        UTILITIES_FOLDER = os.path.join(PYTHON_SCRIPTS_FOLDER, 'utilities')
        sys.path.append(UTILITIES_FOLDER)
    else:
        ARC_FOLDER = os.path.join(ROOT, 'arc')
        sys.path.append(ARC_FOLDER)
        UTILITIES_FOLDER = os.path.join(ARC_FOLDER, 'utilities')
        sys.path.append(UTILITIES_FOLDER)
    import JLog
    import web_wimp_scraper
    import netcdf_parse_all



# FUNCTION DEFINITIONS

def get_json_multiple_ways(url):
    """Tries to pull JSON data from a URL using urllib3 first and then requests"""
    log = JLog.PrintLog()
    if 'https://epqs.nationalmap.gov/v1' in url:
        base_url = 'epqs.nationalmap.gov'
    # Common USGS Error Message
    temp_unavailable_message = 'The requested service is temporarily unavailable.  Please try later.'
    unavailable_error_count = 0
    # Try urllib3
    # Try Requests module
    try:
        log.print_status_message('Querying {}...'.format(base_url))
        content = requests.get(url, timeout=15)
        time.sleep(.5)
        while temp_unavailable_message in content.text:
            del content
            unavailable_error_count += 1
            log.Write('     USGS SERVER:  "{}"'.format(temp_unavailable_message))
            log.print_status_message('     Retrying query of {}...'.format(base_url))
            time.sleep(unavailable_error_count)
            content = requests.get(url)
            time.sleep(unavailable_error_count)
            if unavailable_error_count > 4:
                unavailable_error_count = 0
                break
        json_conversion = content.json()
        return json_conversion
    except Exception:
        requests_exception = traceback.format_exc()
    try:
        log.print_status_message('Querying {}...'.format(base_url))
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED')
        #http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        response = http.request('GET', url)
        time.sleep(1)
        string_data = str(response.data, 'utf-8')
        while temp_unavailable_message in string_data:
            del response
            unavailable_error_count += 1
            log.Write('     USGS SERVER:  "{}"'.format(temp_unavailable_message))
            log.print_status_message('     Retrying query of {}...'.format(base_url))
            time.sleep(unavailable_error_count)
            response = http.request('GET', url)
            sleep_duration = 3 + unavailable_error_count
            time.sleep(sleep_duration)
            string_data = str(response.data, 'utf-8')
            if unavailable_error_count > 4:
                unavailable_error_count = 0
                break
        json_conversion = json.loads(string_data)
        return json_conversion
    except Exception:
        pass

def test_usgs_epqs_servers():
    """
        ned.usgs.gov retired on 01 MAR 2023, NED-based nationalmap.gov API retired same day.

        Updated to use EPQS-based epqs.nationalmap.gov/v1 API on 02 MAR 2023.
    """

    """Tests if either one of the known USGS Elevation Point Query Service (EPQS) Servers are Online"""
    log = JLog.PrintLog()
    log.print_title('USGS Elevation Point Query Service (EPQS) Status Check')
    log.Wrap('Original - National Map Variant:')
    test_url_nationalmap = 'https://epqs.nationalmap.gov/v1/json?x=-121.5&y=38.5&wkid=4326&units=Feet&includeDate=false'
    log.Wrap('  -Test URL: {}'.format(test_url_nationalmap))
    log.Wrap('  -Attempting to connect (15-second timeout)')
    try:
        json_result = get_json_multiple_ways(test_url_nationalmap)
        log.Wrap('')
        elevation = json_result["value"]
        log.Wrap('')
        log.Wrap('    ###########################################')
        log.Wrap('    # --- National Map EPQS Server Online --- #')
        log.Wrap('    ###########################################')
        log.Wrap('')
        return 'nationalmap'
    except Exception:
        log.Wrap('')
        log.Wrap('    ############################################')
        log.Wrap('    # --- National Map EPQS Server Offline --- #')
        log.Wrap('    ############################################')
        log.Wrap('')
        raise Exception('The APT is unable to run if USGS Elevation Point Query Services are offline.')

def file_older_than(file_path, time_unit, time_value):
    """
    file_path = file to be tested (string)
    time_unit = seconds, minutes, hours, or days (string)
    time_value = number of selected time units (int or float)
    Tests the last modified date of a file against a given time unit and value
    """
    seconds = time.time() - os.stat(file_path)[stat.ST_MTIME]
    minutes = seconds/60
    hours = seconds/60/60
    days = seconds/60/60/24 # Not true on DST Change days but close enough
    if time_unit == 'seconds':
        test_value = seconds
    elif time_unit == 'minutes':
        test_value = minutes
    elif time_unit == 'hours':
        test_value = hours
    elif time_unit == 'days':
        test_value = days
    if test_value > time_value:
        return True
    else:
        return False

def time2String(total_seconds):
    if total_seconds < 61:
        seconds = str(int(total_seconds))
        output_string = '{} seconds'.format(seconds)
    elif total_seconds > 60 and total_seconds < 3601:
        minutes = int(total_seconds / 60)
        minutes_loss = (minutes * 60)
        seconds = int(total_seconds - minutes_loss)
        output_string = '{} minutes and {} seconds'.format(minutes, seconds)
    elif total_seconds > 3600:
        hours = int(total_seconds / 3600)
        hours_loss = (hours * 3600)
        minutes = int((total_seconds - hours_loss)/60)
        minutes_loss = (minutes * 60)
        seconds = int(total_seconds - hours_loss - minutes_loss)
        output_string = '{} hours, {} minutes, and {} seconds'.format(hours, minutes, seconds)
    return output_string

def value_list_to_water_year_table(dates, values):
    log = JLog.PrintLog()
    n = 0
    newrow = None
    list_of_arrays = []
    leap_day_rolling_totals = []
    log.Wrap('Collecting all rolling totals for each day of the year...')
    for row in dates:
        if '-10-01' in str(row):
            if newrow is not None:
                # convert list to array
                A = numpy.array(newrow)
                # Add array to list of arrays
                list_of_arrays.append(A)
                # create / empty newrow list
                newrow = []
            else:
                # Create newrow list
                newrow = []
        if '-02-29' in str(row):
            leap_day_rolling_totals.append(values[n])
        else:
            newrow.append(values[n])
        n += 1
    allDays = numpy.array(list_of_arrays)
#    numpy.set_printoptions(precision=2)
#    numpy.set_printoptions(suppress=True)
#    self.log.Wrap(allDays)
#    self.log.Wrap(allDays.shape)
#    # Save Numpy Array as CSV
#    allDays.tofile("C:/Temp/allDays.csv", ',','%f')
    return allDays


def calc_normal_values(dates, values):
    n = 0
    normal_low_values = []
    normal_high_values = []
    # Normal Year
    if len(dates) == (365):
        while n < (365):
            day = []
            for row in values:
                day.append(row[n])
            # Calculate Numpy Percentiles for High and Low normal
            normal_low_values.append(numpy.percentile(day, 30))
            normal_high_values.append(numpy.percentile(day, 70))
            n += 1
    # Leap Year
    if len(dates) == (366):
        while n < (365):
            if n == 151: # Leap day, Feb 29 in a Leap Year
                # Leap Year Processing - Estimate Feb 29th by Averaging percentiles of 2/28 and 3/1
                feb_28_rolling_totals = []
                mar_1_rolling_totals = []
                for row in values:
                    # Get day before and day after
                    feb_28_rolling_totals.append(row[150])
                    mar_1_rolling_totals.append(row[151])
                # Get before and after low and high values from values
                feb_28_normal_low = numpy.percentile(feb_28_rolling_totals, 30)
                feb_28_normal_high = numpy.percentile(feb_28_rolling_totals, 70)
                mar_1_normal_low = numpy.percentile(mar_1_rolling_totals, 30)
                mar_1_normal_high = numpy.percentile(mar_1_rolling_totals, 70)
                # Split the difference between the two dates
                Low = (feb_28_normal_low + mar_1_normal_low)/2
                High = (feb_28_normal_high + mar_1_normal_high)/2
                # Append the averaged data
                normal_low_values.append(Low)
                normal_high_values.append(High)
            # Even if the above executed (Leap Day), we'd still add n=151 as leap day was missing
            day = []
            for row in values:
                day.append(row[n])
            # Calculate Numpy Percentiles for High and Low normal
            normal_low_values.append(numpy.percentile(day, 30))
            normal_high_values.append(numpy.percentile(day, 70))
            n += 1
    # Convert lists to pandas series
    normal_low_series = pandas.Series(normal_low_values, dates)
    normal_high_series = pandas.Series(normal_high_values, dates)
    return normal_low_series, normal_high_series

# CLASS DEFINITIONS

class AnteProcess(object):
    def __init__(self, yMax=None):
        self.yMax = yMax

        self.searchDistance = 30 # Miles
        self.allStations = []
        # self.recentStations = []
        self.ghcn_station_list = None
        self.oldLatLong = None
        self.PDFs = []
        self.pdsidv_file = None
        self.cdf_instance = None
        # Create PrintLog object
        self.log = JLog.PrintLog()
        self.log.Wrap('Initializing anteProcess Class...')
        self.log.Wrap('')
        # Create WimpScraper Instance
        self.wimp_scraper = web_wimp_scraper.WimpScraper()
        self.web_wimp_rows = []
        # Watershed Analysis variables
        self.old_all_sampling_coordinates = None
        self.all_sampling_coordinate_elevations = None
        # Test USGS EPQS Servers
        self.epqs_variant = test_usgs_epqs_servers()

    def set_yMax(self, yMax):
        self.log.Wrap('Setting yMax to ' + str(yMax))
        self.yMax = yMax

    def setInputs(self, inputList, watershed_analysis, all_sampling_coordinates, gridded):
        # Set Inputs
        self.data_type = inputList[0]
        self.site_lat = inputList[1]
        self.site_long = inputList[2]
        year = inputList[3]
        month = inputList[4]
        day = inputList[5]
        self.image_name = inputList[6]
        self.image_source = inputList[7]
        self.save_folder = inputList[8]
        self.forecast_setting = inputList[9]
        self.watershed_analysis = watershed_analysis
        self.all_sampling_coordinates = all_sampling_coordinates
        self.gridded = gridded # True/False this analysis will be using gridded rainfall

        # JLG commented this out on 2023-04-24 to fix Oregon bug
        # if not self.allStations:
        #     # Check for previously Cached Station Data from same day
        #     pickle_folder = os.path.join(ROOT, 'cached')
        #     # Ensure pickle_folder exists
        #     try:
        #         os.makedirs(pickle_folder)
        #     except Exception:
        #         pass
        #     pickle_path = os.path.join(pickle_folder, 'station_classes.pickle')
        #     if self.data_type == 'PRCP' and self.gridded is False:
        #         self.log.Wrap('Checking for previously cached NCDC GHCN Weather Station Records...')
        #         stations_pickle_exists = os.path.exists(pickle_path)
        #         if stations_pickle_exists:
        #             self.log.Wrap('  Cached station data found. Testing...')
        #             expiration_hours = 12
        #             stale = file_older_than(file_path=pickle_path,
        #                                     time_unit='hours',
        #                                     time_value=expiration_hours)
        #             if stale:
        #                 self.log.Wrap('    Cached station data older than {} hours. Deleting...'.format(expiration_hours))
        #                 os.remove(pickle_path)
        #             else:
        #                 pickle_size = os.path.getsize(pickle_path)
        #                 if pickle_size < 15682622:
        #                     self.log.Wrap('    Cached station data corrupt. Deleting...')
        #                     os.remove(pickle_path)
        #         stations_pickle_exists = os.path.exists(pickle_path)
        #         if stations_pickle_exists:
        #             self.log.Wrap('Unserializing cached station data..."')
        #             try:
        #                 with open(pickle_path, 'rb') as handle:
        #                     self.allStations = pickle.load(handle)
        #             except:
        #                 self.log.Wrap('Unserialization failed. Deleting...')
        #                 self.allStations = []
        #                 os.remove(pickle_path)
        # Calculate Dates
        self.dates = date_calcs.DateCalc(year, month, day, self.gridded)

        if self.oldLatLong is None:
            self.oldLatLong = (self.site_lat, self.site_long)
            # Querying Elevation of Observation Point
            self.obs_elevation = round(getElev.main(self.site_lat, self.site_long, epqs_variant=self.epqs_variant), 3)
        else:
            if self.oldLatLong == (self.site_lat, self.site_long):
                self.log.Wrap('Same location. Keeping recent stations list.')
                # try:
                #     self.obs_elevation == 0
                # except Exception:
                #     # Querying Elevation of Observation Point'
                #     self.obs_elevation = round(getElev.main(self.site_lat, self.site_long, epqs_variant=self.epqs_variant), 3)
            else:
                self.oldLatLong = (self.site_lat, self.site_long)
                self.searchDistance = 30 # Miles
                # Querying Elevation of Observation Point'
                if not self.watershed_analysis:
                    self.log.Wrap('New location, starting new recent stations list.')
                    self.obs_elevation = round(getElev.main(self.site_lat, self.site_long, epqs_variant=self.epqs_variant), 3)
                    # self.recentStations = []
                    self.wimp_scraper = web_wimp_scraper.WimpScraper()
                else:
                    if self.old_all_sampling_coordinates is None: # First point of a watershed analysis
                        self.old_all_sampling_coordinates = self.all_sampling_coordinates
                        # self.recentStations = [] # Reset recent stations so it can do the wide sweep
                    else:
                        if self.old_all_sampling_coordinates == self.all_sampling_coordinates:
                            self.log.Wrap('Continuing Watershed Analysis - Keeping recent stations list.')
                            try:
                                dict_key = '{},{}'.format(self.site_lat, self.site_long)
                                self.obs_elevation = self.all_sampling_coordinate_elevations[dict_key]
                            except:
                                self.obs_elevation = round(getElev.main(self.site_lat, self.site_long, epqs_variant=self.epqs_variant), 3)
                        else:
                            self.log.Wrap('New Watershed Analysis - starting new recent stations list.')
                            # self.recentStations = []
                            self.all_sampling_coordinate_elevations = None
                            self.old_all_sampling_coordinates = self.all_sampling_coordinates


        if self.save_folder is not None:
            # Get main_ex version for folder path
            module_path = os.path.dirname(os.path.realpath(__file__))
            root_folder = os.path.dirname(module_path)
            version_files_folder = os.path.join(root_folder, 'v')
            main_version_file_path = os.path.join(version_files_folder, 'main_ex')
            with open(main_version_file_path, 'r') as version_file:
                for line in version_file:
                    version_string = line.replace('\n','')
                    version_list = version_string.split('.')
                    version_for_paths = 'v{}_{}_{}'.format(version_list[0], version_list[1], version_list[2])
                    break
            # Create PDF output Folder
            if self.data_type == 'PRCP':
                watershed_analysis = False
                version_folder = os.path.join(self.save_folder, version_for_paths)
                coord_string = '{}, {}'.format(self.site_lat, self.site_long)
                self.folderPath = os.path.join(version_folder, coord_string)
            if self.data_type == 'SNOW':
                watershed_analysis = False
                version_folder = os.path.join(self.save_folder, version_for_paths)
                snow_folder = os.path.join(version_folder, 'Snowfall')
                coord_string = '{}, {}'.format(self.site_lat, self.site_long)
                self.folderPath = os.path.join(snow_folder, coord_string)
            if self.data_type == 'SNWD':
                watershed_analysis = False
                version_folder = os.path.join(self.save_folder, version_for_paths)
                snow_depth_folder = os.path.join(version_folder, 'Snow Depth')
                coord_string = '{}, {}'.format(self.site_lat, self.site_long)
                self.folderPath = os.path.join(snow_depth_folder, coord_string)
            folder_exists = os.path.exists(self.folderPath)
            if not folder_exists:
                self.log.Wrap('Creating output directory ({})...'.format(self.folderPath))
                # Ensure self.folderPath exists
                try:
                    os.makedirs(self.folderPath)
                except Exception:
                    pass
            # Create CSV output Folder
            self.stationFolderPath = os.path.join(self.folderPath, "Station Data")
            folder_exists = os.path.exists(self.stationFolderPath)
            if not folder_exists:
                self.log.Wrap('Creating stationData output directory ({})...'.format(self.stationFolderPath))
                # Ensure self.stationFolderPath exists
                try:
                    os.makedirs(self.stationFolderPath)
                except Exception:
                    pass
        else:
            self.folderPath = None

        # Reset defaults
        self.stations = []

        if self.ghcn_station_list is None:
            # Get DataFrame of all available Stations
            pickle_folder = os.path.join(ROOT, 'cached')
            # Ensure pickle_folder exists
            try:
                os.makedirs(pickle_folder)
            except Exception:
                pass
            pickle_path = os.path.join(pickle_folder, 'stations.pickle')
            stations_pickle_exists = os.path.exists(pickle_path)
            if self.data_type == 'PRCP' and self.gridded is False:
                if stations_pickle_exists:
                    remove_pickle = False
                    # Call the file stale if it is older than 90 days, because
                    #  we want to save time but also catch potential new stations
                    #  or potentially those that get removed from the list.
                    stale = file_older_than(file_path=pickle_path,
                                            time_unit='days',
                                            time_value=90)
                    if stale:
                        remove_pickle = True
                    else:
                        pickle_size = os.path.getsize(pickle_path)
                        if pickle_size < 10682622:
                            remove_pickle = True
                    if remove_pickle is True:
                        os.remove(pickle_path)
                    else:
                        self.log.Wrap('Unserializing previously cached NCDC GHCN daily weather stations..."')
                        try:
                            with open(pickle_path, 'rb') as handle:
                                self.ghcn_station_list = pickle.load(handle)
                        except Exception:
                            self.log.Wrap('Unserializing failed.')
                            self.ghcn_station_list = None
            # Double-check it wasn't created above
            if self.ghcn_station_list is None and self.gridded is False:
                self.log.Wrap("Downloading list of NCDC GHCN daily weather stations...")
                self.ghcn_station_list = ulmo.ncdc.ghcn_daily.get_stations(elements=self.data_type,
                                                                           update=True,
                                                                           as_dataframe=True)
                self.log.Wrap("")
                # Pickling for later
                if self.data_type == 'PRCP':
                    # Store Data (serialize)
                    with open(pickle_path, 'wb') as handle:
                        pickle.dump(self.ghcn_station_list, handle, protocol=pickle.HIGHEST_PROTOCOL)
        if self.image_name is None:
            self.image_name = "N/A"
        if self.image_source is None:
            self.image_source = "N/A"
        self.site_loc = (self.site_lat, self.site_long)

# COMMANDS
        if self.gridded == False:
            # Get Stations
            if self.stations == []:
                self.getStations()
            else:
                # JLG commented out on 2023-04-24 to test the Oregon bug
                # commenting this out fixed the bug but slows things down
                # for station in self.recentStations:
                #     if station.data is None:
                #         station.run()
                #     station.updateValues(self.site_loc,
                #                          self.obs_elevation,
                #                          self.dates.normal_period_data_start_date,
                #                          self.dates.actual_data_end_date,
                #                          self.dates.antecedent_period_start_date)
                #     self.stations.append(station)
                if self.watershed_analysis:
                    # Sort stations by weighted difference of current sampling point (Recalculated immediately above)
                    sorted_stations = []
                    for station in self.stations:
                        sorted_stations.append([station.weightedDiff, station])
                    sorted_stations.sort(key=lambda x: x[0], reverse=False)
                    self.stations = []
                    for station in sorted_stations:
                        self.stations.append(station[1])

        # Create Final DF and Graph
        return self.createFinalDF()
    # End setInputs function

    def start_multiprocessing(self):
        """Creates queues and sub-processes"""
        self.log.print_section('MULTIPROCESSING START')
        self.log.Wrap('Preparing to use sub-processes to accelerate data acquisition...')
        # Kill any lingering child processes from previous runs
        for minion in multiprocessing.active_children():
            minion.terminate()
        # Set Path to Python Executable
        executable = sys.executable
        multiprocessing.set_executable(executable)
        # Set number of Sub-processes based on CPU_Count
#        num_minions = multiprocessing.cpu_count()
        num_minions = 4 # > 4 resulted in many failed FTP downloads that succeeded in-line later
        # Establish communication queues
        self.log.Wrap("Establishing Communication Queues...")
        tasks_queue = multiprocessing.Queue()
        results_queue = multiprocessing.Queue()
        # Create minions
        self.log.Wrap('Creating %d sub-processes...' % num_minions)
        minions = [process_manager.Minion(tasks_queue, results_queue) for i in range(num_minions)]
        # Start minions
        ### MANDATORY CODE TO DEAL WITH GLITCH ###
        sys.argv = ['']
        ### MANDATORY CODE TO DEAL WITH GLITCH ###
            # Glitch states the following:
            # File "C;\Python27\ArcGIS10.3\Lib\multiprocessing\forking.py",
            #  line 399, in get_preparation_data
            #  sys_argv=sys.argv,
            # AttributeError: 'module' object has no attribute 'argv'
        num = 0
        for minion in minions:
            num += 1
            minion.start()
            self.log.Wrap('Sub-process {} started'.format(num))
        self.log.print_separator_line()
        self.log.Wrap('')
        return tasks_queue, results_queue, minions
    # End of start_multiprocessing function

    def find_and_enqueue_stations(self, tasks_queue):
        """Locates and enqueus all stations within the selected search distance"""
        # Reset Station Numbering (Affects print display only)
        station_number_for_print = 0
        # self.recentStations = []
        # Find min and max ranges (Speed up search, Especially for HUC8 Watershed)
        min_lat = None
        max_lat = None
        min_lon = None
        max_lon = None
        if self.watershed_analysis:
            for sampling_coordinates in self.all_sampling_coordinates:
                if min_lat == None:
                    min_lat = sampling_coordinates[0]
                elif sampling_coordinates[0] < min_lat:
                    min_lat =sampling_coordinates[0]
                if max_lat == None:
                    max_lat = sampling_coordinates[0]
                elif sampling_coordinates[0] > max_lat:
                    max_lat = sampling_coordinates[0]
                if min_lon == None:
                    min_lon = sampling_coordinates[1]
                elif sampling_coordinates[1] < min_lon:
                    min_lon = sampling_coordinates[1]
                if max_lon == None:
                    max_lon = sampling_coordinates[1]
                elif sampling_coordinates[1] > max_lon:
                    max_lon = sampling_coordinates[1]
        else:
            min_lat = float(self.site_lat)
            max_lat = float(self.site_lat)
            min_lon = float(self.site_long)
            max_lon = float(self.site_long)
        # Add 3 to maximums and subtract 3 from the minimums to eliminate most stations quickly
        min_lat -= 4
        max_lat += 4
        min_lon -= 4
        max_lon += 4
        #  ALL STATIONS WITHIN searchDistance
        self.log.print_section('ENQUEUEING STATION DATA DOWNLOADS')
        self.log.Wrap("Searching for weather stations within "+str(self.searchDistance)+" miles...")
        constructor_class_list = []
        for index, row in self.ghcn_station_list.iterrows():
            # Eliminate Stations quickly using buffered min/max lat/lon
            ballpark = True
            if row['latitude'] < min_lat:
                ballpark = False
            elif row['latitude'] > max_lat:
                ballpark = False
            elif row['longitude'] < min_lon:
                ballpark = False
            elif row['longitude'] > max_lon:
                ballpark = False
            if self.searchDistance > 30:
                ballpark = True
            if ballpark:
                include_station = False
                location_tuple = (row['latitude'], row['longitude'])
                distance = great_circle(self.site_loc, location_tuple).miles
                if not self.watershed_analysis:
                    if distance < self.searchDistance:
                        include_station = True
                if self.watershed_analysis:
                    for sampling_coordinates in self.all_sampling_coordinates:
                        sampling_distance = great_circle(sampling_coordinates, location_tuple).miles
                        if sampling_distance < self.searchDistance:
                            include_station = True
                            break
                if include_station:
                    station_index = index
                    name = str(row['name'])
                    already = False
                    location = str(row['latitude']) + ", " + str(row['longitude'])
                    row_elev_meters = row['elevation']
                    elevation = row_elev_meters*3.28084
                    elevDiff = abs(self.obs_elevation - elevation)
                    weightedDiff = distance*((elevDiff/1000)+0.45)
                    # JLG commented out on 2023-04-24 to test the Oregon bug
                    # commenting this out fixed the bug but slows things down

                    # for item in self.allStations:
                    #     if item.name == name:
                    #         station_number_for_print += 1
                    #         self.log.Wrap('Station {} - {} - Data previously acquired'.format(station_number_for_print,
                    #                                                                           name))
                    #         already = item
                    #         already.updateValues(self.site_loc,
                    #                              self.obs_elevation,
                    #                              self.dates.normal_period_data_start_date,
                    #                              self.dates.actual_data_end_date,
                    #                              self.dates.antecedent_period_start_date)
                    #         self.stations.append(already)
                    #         # self.recentStations.append(already)
                    if already is False:
                        station_number_for_print += 1
                        self.log.Wrap('Station {} - {}'.format(station_number_for_print, name))
                        constructor_class = station_manager.Constructor(self.data_type,
                                                                        station_index,
                                                                        name,
                                                                        location,
                                                                        location_tuple,
                                                                        elevation,
                                                                        distance,
                                                                        elevDiff,
                                                                        weightedDiff,
                                                                        self.dates.normal_period_data_start_date,
                                                                        self.dates.actual_data_end_date,
                                                                        self.dates.observation_date,
                                                                        self.dates.antecedent_period_start_date)
                        constructor_class_list.append(constructor_class)
        enqueue_count = 0
        for constructor_class in constructor_class_list:
            tasks_queue.put(constructor_class)
            enqueue_count += 1
        self.log.print_separator_line()
        self.log.Write('')
        return enqueue_count
    # End of find_and_enqueue_stations function

    def finish_multiprocessing(self, tasks_queue, results_queue, minions, enqueue_count):
        """Maintains processing pool until all jobs are complete"""
        self.log.print_section('MULTIPROCESSING FINISH')
        count_copy = enqueue_count
        timer_list = []
        timer_list.append([datetime.now(), count_copy])
        self.log.Wrap('Waiting for sub-processes to download stations:')
        while count_copy > 0:
            # Keep # Minions at original num_minions
            for minion in minions:
                if not minion.is_alive():
                    self.log.Wrap('Sub-process died, creating a replacement...')
                    count_copy -= 1
                    minions.remove(minion)
                    new_minion = process_manager.Minion(tasks_queue, results_queue)
                    new_minion.start()
                    minions.append(new_minion)
            # Pull results_queue to keep queue buffer from overflowing
            try:
                result = results_queue.get(block=True, timeout=5)
                if result == "Maxed":
                    count_copy += 1
                else:
                    # Get another chance to download missing data while waiting
                    if result.data is None:
                        result.run()
                    self.stations.append(result)
                    # self.recentStations.append(result)
                    self.allStations.append(result)
                count_copy -= 1
                # Discern avg. pace and approximate time remaining
                if count_copy < enqueue_count:
                    try:
                        timer_list.append([datetime.now(), count_copy])
                        if len(timer_list) > 20:
                            timer_list.remove(timer_list[0])
                        time_taken = datetime.now() - timer_list[0][0]
                        tasks_complete = timer_list[0][1] - count_copy
                        seconds_per_task = time_taken/tasks_complete
                        seconds_remaining = count_copy * seconds_per_task
                        remaining_string = time2String(seconds_remaining)
                        if count_copy < 2:
                            msg = '{} station remaining.  Approximately {} remaining.'.format(count_copy, remaining_string)
                        else:
                            msg = '{} stations left.  Approximately {} remaining.'.format(count_copy, remaining_string)
                        self.log.print_status_message(msg)
                    except Exception:
                        pass
            except Exception:
                result = None
                # Discern avg. pace and approximate time remaining
                if count_copy < enqueue_count:
                    try:
                        time_taken = datetime.now() - timer_list[0][0]
                        tasks_complete = timer_list[0][1] - count_copy
                        seconds_per_task = time_taken/tasks_complete
                        seconds_remaining = count_copy * seconds_per_task
                        remaining_string = time2String(seconds_remaining)
                        if count_copy < 2:
                            msg = '{} station remaining.  Approximately {} remaining.'.format(count_copy, remaining_string)
                        else:
                            msg = '{} stations left.  Approximately {} remaining.'.format(count_copy, remaining_string)
                        self.log.print_status_message(msg)
                    except Exception:
                        pass
                time.sleep(1)
        # Add poison pill to queue so we can track when all processes are actually complete
            # This method is less glitchy than using a joinable queue
        self.log.Wrap('All jobs complete.  Killing sub-processes...')
        for minion in minions:
            if minion.is_alive():
                tasks_queue.put(None)
        # Waiting for poison pills to dissapear from queue, meaning the actual tasks_queue are complete
        self.log.Write('Waiting for sub-processes to close...')
        while True:
            size = tasks_queue.qsize()
            if size < 1:
                break
            else:
                msg = '{0} sub-processes remaining'.format(size)
                self.log.print_status_message(msg)
            time.sleep(1)
        self.log.Write('All sub-processes dead and accounted for.')
        self.log.print_separator_line()
        self.log.Write('')
    # End of finish_multiprocessing function

    def getStations(self):
        # Start Multiprocessing
        tasks_queue, results_queue, minions = self.start_multiprocessing()
        # Find an enqueue stations within the selected search distance
        enqueue_count = self.find_and_enqueue_stations(tasks_queue)
        # WebWimp Use this downtime to pre-load the WebWIMP Querry
                # Get WebWIMP Wet/Dry Season Determination
        if self.data_type == 'PRCP':
            # MAKING EARLY REQUESTS BELOW TO USE THIS DOWNTIME
            try:
                # Query PDSI
                palmer_value, palmer_class, palmer_color, self.pdsidv_file = query_climdiv.get_pdsidv(lat=float(self.site_lat),
                                                                                                      lon=float(self.site_long),
                                                                                                      year=self.dates.observation_year,
                                                                                                      month=self.dates.observation_month,
                                                                                                      pdsidv_file=self.pdsidv_file)
                # Querying WebWIMP to collect Wet / Dry season info...'
                wet_dry_season_result = self.wimp_scraper.get_season(lat=float(self.site_lat),
                                             lon=float(self.site_long),
                                             month=int(self.dates.observation_month),
                                             output_folder=self.folderPath,
                                             watershed_analysis=self.watershed_analysis)
                del palmer_value, palmer_class, palmer_color
                # Query all Elevations
                if self.watershed_analysis is True:
                    if self.all_sampling_coordinate_elevations is None:
                        self.all_sampling_coordinate_elevations = getElev.batch(self.all_sampling_coordinates, epqs_variant=self.epqs_variant)
            except Exception:
                self.log.Wrap(traceback.format_exc())
        # Maintain processing pool until all jobs are complete and collect results
        self.finish_multiprocessing(tasks_queue, results_queue, minions, enqueue_count)

        # Pickle All Stations for re-use the same day
        # JLG commented this out on 2023-04-24 to fix Oregon bug
        # if self.data_type == 'PRCP':
        #     self.log.Wrap('Attempting to pickle Station Records for future use within 12 hours...')
        #     pickle_folder = os.path.join(ROOT, 'cached')
        #     pickle_path = os.path.join(pickle_folder, 'station_classes.pickle')
        #     if os.path.exists(pickle_path) is True:
        #         try:
        #             os.remove(pickle_path)
        #         except Exception:
        #             pass
        #     # Store Data (serialize)
        #     try:
        #         with open(pickle_path, 'wb') as handle:
        #             pickle.dump(self.allStations, handle, protocol=pickle.HIGHEST_PROTOCOL)
        #     except Exception:
        #         pass

    def getBest(self, need_primary):
        lowestDiff = 10000
        best_station = None
        if len(self.stations) < 1:
            self.log.Wrap('No stations in station list...')
        else:
            if need_primary is True:
                self.log.Wrap('Searching for primary station...')
                min_antecedent_rows = int(90 * 0.75)
                huge_record_primary = None
                huge_lowest_diff = lowestDiff
                medium_record_primary = None
                medium_lowest_diff = lowestDiff
                minimum_record_primary = None
                minimum_lowest_diff = lowestDiff
                tolerable_difference_per_thousand = .75
                for station in self.stations:
                    if station.current_actual_rows >= min_antecedent_rows:
                        if station.actual_rows > 10000:
                            if station.weightedDiff < huge_lowest_diff:
                                huge_lowest_diff = station.weightedDiff
                                huge_record_primary = station
                        elif station.actual_rows > 8000:
                            if station.weightedDiff < medium_lowest_diff:
                                medium_lowest_diff = station.weightedDiff
                                medium_record_primary = station
                        elif station.actual_rows > 6000:
                            if station.weightedDiff < minimum_lowest_diff:
                                minimum_lowest_diff = station.weightedDiff
                                minimum_record_primary = station
                if not minimum_record_primary is None:
                    best_station = minimum_record_primary
                if not medium_record_primary is None:
                    if not minimum_record_primary is None:
                        record_test = medium_record_primary.weightedDiff < (minimum_record_primary.weightedDiff + (2*tolerable_difference_per_thousand))
                        if record_test:
                            best_station = medium_record_primary
                    else:
                        best_station = medium_record_primary
                if not huge_record_primary is None:
                    if not minimum_record_primary is None:
                        record_test = huge_record_primary.weightedDiff < (minimum_record_primary.weightedDiff + (4*tolerable_difference_per_thousand))
                        if record_test:
                            if not medium_record_primary is None:
                                if huge_record_primary.weightedDiff < (medium_record_primary.weightedDiff + (2*tolerable_difference_per_thousand)):
                                    best_station = huge_record_primary
                            else:
                                best_station = huge_record_primary
                    elif not medium_record_primary is None:
                        if huge_record_primary.weightedDiff < (medium_record_primary.weightedDiff + (2*tolerable_difference_per_thousand)):
                            best_station = huge_record_primary
                    else:
                        best_station = huge_record_primary
            else:
                for station in self.stations:
                    if station.weightedDiff < lowestDiff:
                        lowestDiff = station.weightedDiff
                        best_station = station
        if not best_station is None:
            self.stations.remove(best_station)
        return best_station

    def sortStations(self, primary_station):
        sorted_stations = []
        for station in self.stations:
            # loop through non-primary-stations and recalculate distance, etc.
            # based off of distance from primary station
            if station.name != primary_station.name:
                distance = great_circle(primary_station.location, station.location).miles
                distance = round(distance, 3)
                station.distance = distance
                elevDiff = round((primary_station.elevation - station.elevation), 3)
                elevDiff = abs(elevDiff)
                station.elevDiff = elevDiff
                weightedDiff = round(distance*((elevDiff/1000)+0.45), 3)
                station.weightedDiff = weightedDiff
                sorted_stations.append([station.weightedDiff, station])
        sorted_stations.sort(key=lambda x: x[0], reverse=False)
        # insert primary station at the top of the list
        sorted_stations.insert(0, [primary_station.weightedDiff, primary_station])
        self.stations = []
        self.log.Wrap('Looking for stations missing data...')
        for sort_list in sorted_stations:
            station = sort_list[1]
            if station.data is None:
                self.log.Wrap('  Station download failed for {}'.format(station.name))
                self.log.Wrap('    Retrying download...')
                station.run()
                if station.data is None:
                    self.log.Wrap('      Download failed again. Ignoring station.')
                else:
                    self.log.Wrap('      Download successful!')
            self.stations.append(station)

    def createFinalDF(self):
        # Start to Build Stations Table (continues during iteration below)
        if self.gridded is False:
            station_table_column_labels =[["Weather Station Name",
                                           "Coordinates",
                                           "Elevation (ft)",
                                           "Distance (mi)",
                                           r"Elevation $\Delta$",
                                           r"Weighted $\Delta$",
                                           "Days Normal",
                                           "Days Antecedent"]]
        if self.gridded is True:
            station_table_column_labels =[["",
                                           "Station Count Summary"]]

        station_table_values = [] # added by JLG

        # CREATE EMPTY DATAFRAME (self.finalDF)
        if self.gridded is False:
            if float(self.site_lat) < 50:
                maxSearchDistance = 60      # Maximum distance between observation point and station location
            else: # In AK, where stations are very rare
                maxSearchDistance = 300
            self.log.Wrap("")
            self.log.Wrap('Creating an empty dataframe from {} to {} to populate with weather station data...'.format(self.dates.normal_period_data_start_date, self.dates.actual_data_end_date))
            index = pandas.date_range(start=self.dates.normal_period_data_start_date,
                                      end=self.dates.actual_data_end_date,
                                      freq='D')
            self.finalDF = pandas.Series(index=index,
                                         dtype="object",
                                         name='value')

            # find the primary station after to order the precip selection
            need_primary = True
            primary_station = None
            while primary_station is None:
                primary_station = self.getBest(need_primary=need_primary)
                if primary_station is not None:
                    # Note that the primary station has been found
                    if need_primary is True:
                        need_primary = False
                else:
                    self.log.Wrap("No suitable primary station locations were found by the APT...")
                    self.log.Wrap("")
                    if float(self.site_lat) < 50:
                        self.searchDistance += 10 # Search distance increase interval
                    else:
                        self.searchDistance += 30 # In alaska it will probably go even higher.
                    if self.searchDistance <= maxSearchDistance:
                        # Clearing previous table data
                        station_table_values = []
                        # Clearing previous dataFrame in case a better fit is found.
                        self.log.Wrap('Creating an empty dataset to populate with weather data...')
                        self.log.Wrap("")
                        index = pandas.date_range(start=self.dates.normal_period_data_start_date,
                                                  end=self.dates.actual_data_end_date,
                                                  freq='D')
                        self.finalDF = pandas.Series(index=index,
                                                     dtype="object",
                                                     name='value')
                        self.log.Wrap("Widening search...")
                        num_stations_used = 0
                        self.getStations()
            self.sortStations(primary_station)

            # FILL self.finalDF
            # Fill in NaN using top station
            n = 0
            num_stations_used = 0 # start counting the number of stations used
            maxNumberOfStations = 15    # Maximum number of stations to use to complete record
            while self.finalDF.isnull().sum().sum() > 0 and num_stations_used < maxNumberOfStations and self.searchDistance <= maxSearchDistance:
            # number_of_stations = len(self.stations)
                for station in self.stations:
                    if num_stations_used < maxNumberOfStations and self.searchDistance <= maxSearchDistance and self.gridded==False:
                        n += 1
                        if n == 1:
                            self.log.Wrap(str(self.finalDF.isnull().sum().sum()) + ' null values.')
                        if self.searchDistance > 60:
                            need_primary = False
                        # Get baseline null value count
                        missing_before_normal = self.finalDF[self.dates.normal_period_data_start_date:self.dates.normal_period_end_date].isnull().sum().sum()
                        missing_before_antecedent = self.finalDF[self.dates.antecedent_period_start_date:self.dates.observation_date].isnull().sum().sum()
                        values = station.Values
                        self.log.Wrap('Attempting to replace null values with values from {}...'.format(station.name))
                        # Fill
                        try:
                            self.finalDF.fillna(values, inplace=True)
                        except ValueError:
                            self.log.Wrap('ERROR: No values found for {}. Station will be skipped.'.format(station.name))
                        missingAfter = self.finalDF.isnull().sum().sum()
                        self.log.Wrap(str(missingAfter) + ' null values remaining.')
                        missing_after_normal = self.finalDF[self.dates.normal_period_data_start_date:self.dates.normal_period_end_date].isnull().sum().sum()
                        missing_after_antecedent = self.finalDF[self.dates.antecedent_period_start_date:self.dates.observation_date].isnull().sum().sum()
                        num_rows_normal = missing_before_normal-missing_after_normal
                        num_rows_antecedent = missing_before_antecedent-missing_after_antecedent
                        num_rows = num_rows_normal + num_rows_antecedent
                        if num_rows > 0:
                            num_stations_used += 1
                            # BUILD STATIONS TABLE
                            vals = []
                            vals.append(station.name)
                            vals.append(station.location)
                            vals.append(station.elevation)
                            vals.append(station.distance)
                            vals.append(station.elevDiff)
                            vals.append(station.weightedDiff)
                            vals.append(num_rows_normal)
                            vals.append(num_rows_antecedent)
                            station_table_values.append(vals)
                            # SAVE RESULTS TO CSV IN OUTPUT DIRECTORY
                            if self.save_folder is not None:
                                # Generate output
                                try:
                                    station_csv_name = '{}_{}.csv'.format(station.name,self.dates.observation_date).replace('/','_') # Slashes keep getting added to file names somehow, causing failures here
                                    station_csv_path = os.path.join(self.stationFolderPath, station_csv_name)
                                    if os.path.isfile(station_csv_path) is False:
                                        self.log.Wrap('Saving station data to CSV in output folder...')
                                        station.Values.to_csv(station_csv_path)
                                except Exception:
                                    pass # Will add an announcement that station data save failed later)
                    else:
                        pass
                if self.finalDF.isnull().sum().sum() > 0:
                    self.log.Wrap("")
                    self.log.Wrap("No suitable station available to replace null values.")
                    if float(self.site_lat) < 50:
                        self.searchDistance += 10 # Search distance increase interval
                    else:
                        self.searchDistance += 30 # In alaska it will probably go even higher.
                    if self.finalDF.isnull().sum().sum() > 1:
                        if self.searchDistance <= maxSearchDistance:
                            # Clearing previous table data
                            station_table_values = []
                            # Clearing previous dataFrame in case a better fit is found.
                            self.log.Wrap('Creating an empty dataset to populate with weather data...')
                            self.log.Wrap("")
                            index = pandas.date_range(start=self.dates.normal_period_data_start_date,
                                                      end=self.dates.actual_data_end_date,
                                                      freq='D')
                            self.finalDF = pandas.Series(index=index,
                                                         dtype="object",
                                                         name='value')
                            self.log.Wrap("Widening search...")
                            num_stations_used = 0
                            self.getStations()
                            self.sortStations(primary_station)

                # Fill NaN using linear interpolation
                if self.finalDF.isnull().sum().sum() > 0:
                    #df.update(secondDF)
                    self.log.Wrap("")
                    self.log.Wrap('Attempting linear interpolation to fill null values...')
                    missing_before_normal = self.finalDF[self.dates.normal_period_data_start_date:self.dates.normal_period_end_date].isnull().sum().sum()
                    missing_before_antecedent = self.finalDF[self.dates.antecedent_period_start_date:self.dates.observation_date].isnull().sum().sum()
                    interp = self.finalDF.astype(float)
                    try:
                        interp.interpolate(method="time", inplace=True, limit=1)
                    except Exception:
                        interp.interpolate(inplace=True, limit=1)
                    self.finalDF.fillna(interp, inplace=True)
                    self.log.Wrap(str(self.finalDF.isnull().sum().sum()) + " null values remaining.")
                    if self.finalDF.isnull().sum().sum() > 0:
                        self.log.Wrap("Unfortunately, data gaps still persist after interpolating. Therefore, the APT was unable to complete your analysis.")
                    missing_after_normal = self.finalDF[self.dates.normal_period_data_start_date:self.dates.normal_period_end_date].isnull().sum().sum()
                    missing_after_antecedent = self.finalDF[self.dates.antecedent_period_start_date:self.dates.observation_date].isnull().sum().sum()
                    num_rows_normal = missing_before_normal - missing_after_normal
                    num_rows_antecedent = missing_before_antecedent - missing_after_antecedent
                    num_rows = num_rows_normal + num_rows_antecedent
                    if num_rows > 0:
                        # BUILD STATIONS TABLE by adding interpolation details to the stations
                        num_stations_used += 1
                        vals = []
                        vals.append("Linear Interpolation")
                        vals.append("N/A")
                        vals.append("N/A")
                        vals.append("N/A")
                        vals.append("N/A")
                        vals.append("N/A")
                        vals.append(num_rows_normal)
                        vals.append(num_rows_antecedent)
                        station_table_values.append(vals)

            self.searchDistance = 30 # Resetting this so future runs of the tool do not skip the above step.

            if self.finalDF.isnull().sum().sum() < 1:
                self.log.Wrap('No null values within self.finalDF')

            else:
                if self.data_type != 'PRCP':
                    self.log.Wrap('Since this is not for PRCP... filling null values with "0" to allow graph output...')
                    self.finalDF.fillna(0, inplace=True)
                    if self.finalDF.isnull().sum().sum() < 1:
                        self.log.Wrap('No null values within self.finalDF')
            self.log.print_separator_line()
            self.log.Wrap('')

            if self.finalDF.isnull().sum().sum() > 0:
                self.log.Wrap('Null values remain after interpolation... the APT cannot complete this analysis')
                self.log.Wrap('')
                raise

            # SAVE finalDF TO CSV IN OUTPUT DIRECTORY
            if self.save_folder is not None:
                # Ensure output folder exists
                try:
                    os.makedirs(self.stationFolderPath)
                except Exception:
                    pass
                # Generate output
                merged_stations_output_path = os.path.join(self.stationFolderPath, "merged_stations_{0}.csv".format(self.dates.observation_date))
                try:
                    if os.path.isfile(merged_stations_output_path) is False:
                        self.log.Wrap('Saving "merged_stations_{0}.csv" data to output folder...'.format(self.dates.observation_date))
                        self.finalDF.to_csv(merged_stations_output_path)
                except Exception:
                    pass
            # Converting to milimeters
            if self.data_type == 'PRCP':
    # #            self.log.Wrap('Converting PRCP values to milimeters...')
                if self.finalDF is not None:
                    self.finalDF = self.finalDF/10.0
                   # self.log.Wrap('self.finalDF conversion complete.')
    #            self.log.print_separator_line()
    #            self.log.Wrap('')
            # Converting from millimeters to inches
            units = 'in'
            units_long = 'Inches'
            if self.data_type == 'PRCP':
                self.log.Wrap('Converting PRCP values from millimeters to inches...')
                if self.finalDF is not None:
                    self.finalDF = self.finalDF * 0.03937008
                    self.log.Wrap('self.finalDF conversion complete.')
     #           self.log.print_separator_line()
     #           self.log.Wrap('')
            # Save converted finalDF to CSV in output directory
            if self.save_folder is not None:
                # Generate output
                converted_stations_output_path = os.path.join(self.stationFolderPath, "merged_stations_converted_to_{0}_{1}.csv".format(units,self.dates.observation_date))
                if os.path.isfile(converted_stations_output_path) is False:
                    self.log.Wrap('Saving "merged_stations_converted_to_{0}_{1}.csv" data to output folder...'.format(units,self.dates.observation_date))
                    try:
                        self.finalDF.to_csv(converted_stations_output_path)
                    except Exception:
                        pass
            self.log.print_separator_line()
        elif self.gridded is True:
            # Grid Section
            num_stations_used = 0
            # if self.cdf_instance is None:
            self.cdf_instance = netcdf_parse_all.get_point_history(float(self.site_lat),
                                                                   float(self.site_long),
                                                                   datetime.strptime(self.dates.normal_period_data_start_date, "%Y-%m-%d"),
                                                                   datetime.strptime(self.dates.actual_data_end_date, "%Y-%m-%d"))
            self.cdf_instance()
            self.gridFolderPath = os.path.join(self.folderPath, "Grid Data")
            if os.path.isdir(self.gridFolderPath) == True:
                pass
            else:
                os.mkdir(self.gridFolderPath)
            # Save entire TS to CSV in output directory
            outputName = 'gridded_data_{0}.csv'.format(self.dates.observation_date)
            outputName = os.path.join(self.gridFolderPath, outputName)
            if os.path.isfile(outputName) is True:
                os.remove(outputName)
                time.sleep(1)
            self.log.Wrap('Saving complete gridded precipitation time series to CSV in output folder...')
            pandas.concat([self.cdf_instance.entire_precip_ts, self.cdf_instance.entire_station_count_ts], axis=1).to_csv(outputName, header=False)
            self.log.Wrap('Entire TimeSeries rows = {}'.format(self.cdf_instance.entire_precip_ts.count()))
            self.finalDF = self.cdf_instance.entire_precip_ts[self.dates.normal_period_data_start_date:self.dates.actual_data_end_date]
            self.log.Wrap('FinalDF rows = {}'.format(self.finalDF.count()))
            currentValues = self.cdf_instance.entire_precip_ts[self.dates.antecedent_period_start_date:self.dates.current_water_year_end_date]
            self.log.Wrap('Current year rows = {}'.format(currentValues.count()))
            # convert the data into inches
            units = 'in'
            units_long = 'Inches'
            if self.data_type == 'PRCP':
                self.log.Wrap('Converting PRCP values to inches...')
                if self.finalDF is not None:
                    self.finalDF = self.finalDF * 0.03937008
                    self.log.Wrap('self.finalDF conversion complete.')
            station_count_data = numpy.float64(self.cdf_instance.entire_station_count_ts[self.dates.normal_period_data_start_date:self.dates.actual_data_end_date])
            vals = []
            vals.append("Minimum count of weather stations within 30 miles")
            vals.append(int(round(station_count_data.min(),0)))
            station_table_values.append(vals)
            vals = []
            vals.append("Mean count of weather stations within 30 miles")
            vals.append(int(round(station_count_data.mean(),0)))
            station_table_values.append(vals)
            vals = []
            vals.append("Median count of weather stations within 30 miles")
            vals.append(int(round(numpy.median(station_count_data),0)))
            station_table_values.append(vals)
            vals = []
            vals.append("Maximum count of weathers stations within 30 miles")
            vals.append(int(round(station_count_data.max(),0)))
            station_table_values.append(vals)
            # BUILD STATIONS TABLE
            # x = 1
            #row_labels3.append(row_options[0])
            #vals = []
            #vals.append('NOAA Gridded PRCP Alpha')
            #vals.append('N/A')
            #vals.append('N/A')
            #vals.append('N/A')
            #vals.append('N/A')
            #vals.append('N/A')
            #vals.append(self.finalDF.count())
            #vals.append(currentValues.count())
            #table_vals3.append(vals)
##            # SAVE finalDF TO CSV IN OUTPUT DIRECTORY
##            if self.saveFolder is not None:
##                try:
##                    outputName = '{}\\({}, {}) Trimmed AlphaGrid PRCP.csv'.format(self.stationFolderPath, self.cdf_instance.closest_lat, self.cdf_instance.closest_lon)
##                    if os.path.isfile(outputName) is True:
##                        os.remove(outputName)
##                        time.sleep(1)
##                    self.L.Wrap('Saving Trimmed AlphaGrid PRCP data to CSV in output folder...')
##                    self.finalDF.to_csv(outputName)
##                except Exception as F:
##                    self.L.Wrap(F)

        # Calculate rolling 30 day sum for the DataFrame
        self.log.Wrap('Calculating 30-day rolling totals...')
        try:
            longRolling30day = self.finalDF.rolling(window=30, center=False).sum()
        except Exception:
            longRolling30day = pandas.rolling_sum(arg=self.finalDF, window=30, center=False)
        if self.data_type == 'SNWD':
            longRolling30day = self.finalDF
        # Create version for calculating daily statistics
        statsRolling30day = longRolling30day[self.dates.normal_period_start_date:self.dates.normal_period_end_date]
        # Create version for graphing current water year
        rolling30day = longRolling30day[self.dates.graph_start_date:self.dates.graph_end_date]
        # get the max value
        rolling_30_day_max = rolling30day.max()

        #---Convert Normal Period 30-Day Rolling Totals to a 365x30 array---#
        # Create a list of dates encompassing the 30-water-year Normal Period
        normal_period_dates = pandas.date_range(self.dates.normal_period_start_date, self.dates.normal_period_end_date)
        # Convert to 365x30 table
        allDays = value_list_to_water_year_table(dates=normal_period_dates, values=statsRolling30day)

# Get current-year Normals (And those same normals replicated over the previous and following years for graphing)
        self.log.Wrap('Calculating Normal High and Normal Low values for each day of the year...')
        # Create a list of dates in the selected range
        current_water_year_dates = pandas.date_range(self.dates.current_water_year_start_date, self.dates.current_water_year_end_date)
        # Get all days Upper and Lower Normal values for the current water year
        current_normal_low_series, current_normal_high_series = calc_normal_values(dates=current_water_year_dates, values=allDays)
        # Create a list of dates for the prior water year
        prior_water_year_dates = pandas.date_range(self.dates.prior_water_year_start_date, self.dates.prior_water_year_end_date)
        # Get all days Upper and Lower Normal values for the current water year
        prior_normal_low_series, prior_normal_high_series = calc_normal_values(dates=prior_water_year_dates, values=allDays)
        # Create a list of dates for the following water year
        following_water_year_dates = pandas.date_range(self.dates.following_water_year_start_date, self.dates.following_water_year_end_date)
        # Get all days Upper and Lower Normal values for the current water year
        following_normal_low_series, following_normal_high_series = calc_normal_values(dates=following_water_year_dates, values=allDays)

        # Append current year to prior year to create final output
        normal_low_series = prior_normal_low_series.append(current_normal_low_series).append(following_normal_low_series)
        normal_high_series = prior_normal_high_series.append(current_normal_high_series.append(following_normal_high_series))

        # CREATE ANNOTATIONS
        first_point_y_rolling_total = None
        second_point_y_rolling_total = None
        third_point_y_rolling_total = None

        # Create a list of dates of the same Start/End range for figure labeling
        Dates = pandas.date_range(self.dates.graph_start_date, self.dates.graph_end_date)

        # get three points for annotation
        self.log.Wrap('Evaluating sample points...')
        for item in Dates:
            if self.dates.observation_date in str(item):
                first_point_datetime = item
        second_point_datetime = first_point_datetime - timedelta(days=30)
        third_point_datetime = second_point_datetime - timedelta(days=30)
        first_point_x_date_string = str(first_point_datetime)[:10]
        second_point_x_date_string = str(second_point_datetime)[:10]
        third_point_x_date_string = str(third_point_datetime)[:10]
        try:
            first_point_y_rolling_total = abs(round(rolling30day.loc[first_point_x_date_string], 6))
            if first_point_y_rolling_total > rolling_30_day_max * 0.85:
                first_point_xytext = (10, -25)
            else:
                first_point_xytext = (15, 30)
        except:
            self.log.Wrap(traceback.format_exc())
            pass
        try:
            second_point_y_rolling_total = abs(round(rolling30day.loc[second_point_x_date_string], 6))
            if second_point_y_rolling_total > rolling_30_day_max * 0.85:
                second_point_xytext = (10, -25)
            else:
                second_point_xytext = (15, 30)
        except:
            self.log.Wrap(traceback.format_exc())
            pass
        try:
            third_point_y_rolling_total = abs(round(rolling30day.loc[third_point_x_date_string], 6))
            if third_point_y_rolling_total > rolling_30_day_max * 0.85:
                third_point_xytext = (10, -25)
            else:
                third_point_xytext = (15, 30)
        except:
            self.log.Wrap(traceback.format_exc())
            pass

        # Define colors for cell color matrices
        light_green = (0.5, 0.8, 0.5)
        light_blue = (0.4, 0.5, 0.8)
        light_red = (0.8, 0.5, 0.5)
        light_grey = (0.85, 0.85, 0.85)
        white = (1, 1, 1)
        #black = (0, 0, 0)

        # Determine relationship to normal
        self.log.Wrap("Determining relationship between sample points and the normal range...")
        if self.data_type == 'PRCP':
            firstHigh = abs(round(normal_high_series.loc[first_point_x_date_string], 6))
            firstLow = abs(round(normal_low_series.loc[first_point_x_date_string], 6))
            secondHigh = abs(round(normal_high_series.loc[second_point_x_date_string], 6))
            secondLow = abs(round(normal_low_series.loc[second_point_x_date_string], 6))
            thirdHigh = abs(round(normal_high_series.loc[third_point_x_date_string], 6))
            thirdLow = abs(round(normal_low_series.loc[third_point_x_date_string], 6))
            score = 0
            if first_point_y_rolling_total > firstHigh:
                firstWetnessCondition = "Wet"
                firstConditionValue = 3
                firstMonthWeight = 3
                firstProduct = firstConditionValue * firstMonthWeight
                score += firstProduct
            elif first_point_y_rolling_total <= firstHigh and first_point_y_rolling_total >= firstLow:
                firstWetnessCondition = "Normal"
                firstConditionValue = 2
                firstMonthWeight = 3
                firstProduct = firstConditionValue * firstMonthWeight
                score += firstProduct
            elif first_point_y_rolling_total < firstLow:
                firstWetnessCondition = "Dry"
                firstConditionValue = 1
                firstMonthWeight = 3
                firstProduct = firstConditionValue * firstMonthWeight
                score += firstProduct
            if second_point_y_rolling_total > secondHigh:
                secondWetnessCondition = "Wet"
                secondConditionValue = 3
                secondMonthWeight = 2
                secondProduct = secondConditionValue * secondMonthWeight
                score += secondProduct
            elif second_point_y_rolling_total <= secondHigh and second_point_y_rolling_total >= secondLow:
                secondWetnessCondition = "Normal"
                secondConditionValue = 2
                secondMonthWeight = 2
                secondProduct = secondConditionValue * secondMonthWeight
                score += secondProduct
            elif second_point_y_rolling_total < secondLow:
                secondWetnessCondition = "Dry"
                secondConditionValue = 1
                secondMonthWeight = 2
                secondProduct = secondConditionValue * secondMonthWeight
                score += secondProduct
            if third_point_y_rolling_total > thirdHigh:
                thirdWetnessCondition = "Wet"
                thirdConditionValue = 3
                thirdMonthWeight = 1
                thirdProduct = thirdConditionValue * thirdMonthWeight
                score += thirdProduct
            elif third_point_y_rolling_total <= thirdHigh and third_point_y_rolling_total >= thirdLow:
                thirdWetnessCondition = "Normal"
                thirdConditionValue = 2
                thirdMonthWeight = 1
                thirdProduct = thirdConditionValue * thirdMonthWeight
                score += thirdProduct
            elif third_point_y_rolling_total < thirdLow:
                thirdWetnessCondition = "Dry"
                thirdConditionValue = 1
                thirdMonthWeight = 1
                thirdProduct = thirdConditionValue * thirdMonthWeight
                score += thirdProduct
            if score >= 6 and score <= 9:
                ante_calc_result = "Drier than Normal"
                final_cell_color = light_red
            if score >= 10 and score <= 14:
                ante_calc_result = 'Normal Conditions'
                final_cell_color = light_green
            if score >= 15:
                ante_calc_result = 'Wetter than Normal'
                final_cell_color = light_blue
            # Build Rain Table
            rain_colors = [
                [light_grey, light_grey, light_grey, light_grey, light_grey, light_grey, light_grey, light_grey],
                [white, white, white, white, white, white, white, white],
                [white, white, white, white, white, white, white, white],
                [white, white, white, white, white, white, white, white],
                [white, white, white, white, white, white, white, final_cell_color]
            ]
            rain_table_vals = [
                ['30 Days Ending',
                 r"30$^{th}$ %ile" + "  ({})".format(units),
                 r"70$^{th}$ %ile" + "  ({})".format(units),
                 "Observed ({})".format(units),
                 'Wetness Condition',
                 'Condition Value',
                 'Month Weight',
                 'Product'],
                [first_point_x_date_string,
                 firstLow,
                 firstHigh,
                 first_point_y_rolling_total,
                 firstWetnessCondition,
                 firstConditionValue,
                 firstMonthWeight,
                 firstProduct],
                [second_point_x_date_string,
                 secondLow,
                 secondHigh,
                 second_point_y_rolling_total,
                 secondWetnessCondition,
                 secondConditionValue,
                 secondMonthWeight,
                 secondProduct],
                [third_point_x_date_string,
                 thirdLow,
                 thirdHigh,
                 third_point_y_rolling_total,
                 thirdWetnessCondition,
                 thirdConditionValue,
                 thirdMonthWeight,
                 thirdProduct],
                ["Result",
                 "",
                 "",
                 "",
                 "",
                 "",
                 "",
                 '{} - {}'.format(ante_calc_result, str(score))]
            ]

        # Build Description Table

            # Truncate name
        tableName = self.image_name
        length = len(tableName)
        if length > 34:
            tableName = tableName[:33]+'...'
            length = 36
            # Truncate source
        tableSource = self.image_source
        sLength = len(tableSource)
        if sLength > 34:
            tableSource = tableSource[:33]+'...'
            sLength = 36

            # Create Column Labels
        description_table_values = [
            ["Coordinates", str(self.site_lat)+ ', ' + str(self.site_long)],
            ['Observation Date', self.dates.observation_date],
            ['Elevation (ft)', round(self.obs_elevation, 6)]
        ]
        description_table_colors = [
            [light_grey, white],
            [light_grey, white],
            [light_grey, white]
        ]
        self.log.print_separator_line()
        self.log.Wrap('')

        if not self.image_name == 'N/A':
            description_table_values.append(['Image or Event', tableName])
            description_table_colors.append([light_grey, white])

        if not self.image_source == 'N/A':
            description_table_values.append(['Source', tableSource])
            description_table_colors.append([light_grey, white])

        # GET FORECAST DATA (If enabled)
        if self.forecast_setting is True:
            # Get Forecast if current water year is still in progress
            if self.data_type == 'PRCP':
                if len(rolling30day) < 358:
                    self.log.Wrap("Requesting 7-Day Forecast Data from https://api.darksky.net...")
                    try:
                        days, mm = get_forecast.main(self.site_lat, self.site_long)
                    except Exception:
                        self.log.Wrap(traceback.format_exc())
                    self.log.Wrap('')

        # Get Palmer Drought Seveity Index
        if self.data_type == 'PRCP':
            try:
                palmer_value, palmer_class, palmer_color, self.pdsidv_file = query_climdiv.get_pdsidv(lat=float(self.site_lat),
                                                                                                      lon=float(self.site_long),
                                                                                                      year=self.dates.observation_year,
                                                                                                      month=self.dates.observation_month,
                                                                                                      pdsidv_file=self.pdsidv_file)
                description_table_values.append(["Drought Index (PDSI)", palmer_class])
                description_table_colors.append([light_grey, palmer_color])
            except Exception:
                palmer_class = 'Error'
                palmer_value = -99.99
                self.log.Wrap(traceback.format_exc())

        # Get WebWIMP Wet/Dry Season Determination
        if self.data_type == 'PRCP':
            # Querying WebWIMP to collect Wet / Dry season info...'
            try:
                # Querying WebWIMP to collect Wet / Dry season info...'
                wet_dry_season_result = self.wimp_scraper.get_season(lat=float(self.site_lat),
                                                                     lon=float(self.site_long),
                                                                     month=int(self.dates.observation_month),
                                                                     output_folder=self.folderPath,
                                                                     watershed_analysis=self.watershed_analysis)
                if not wet_dry_season_result == 'ERROR':
                    description_table_values.append([r"WebWIMP H$_2$O Balance", wet_dry_season_result])
                    if wet_dry_season_result == 'Wet Season':
                        description_table_colors.append([light_grey, white])
                    if wet_dry_season_result == 'Dry Season':
                        description_table_colors.append([light_grey, light_red])
            except Exception:
                wet_dry_season_result = 'Error'
                self.log.Wrap(traceback.format_exc())

        # Pickle values for graph_test if in Dev environment
        #if sys.executable == r'D:\Code\Python\WinPythonARC\WinPythonZero32\python-3.6.5\python.exe':
        if True:
            pickle_folder = os.path.join(ROOT, 'cached')
            pickle_path = os.path.join(pickle_folder, 'graph_demo_data.pickle')
            pickle_list = [Dates,
                           self.cdf_instance,
                           longRolling30day,
                           rolling30day,
                           self.dates,
                           self.dates.graph_start_date,
                           self.finalDF,
                           self.dates.graph_end_date,
                           self.forecast_setting,
                           normal_low_series,
                           normal_high_series,
                           self.yMax,
                           rolling_30_day_max,
                           first_point_y_rolling_total,
                           first_point_x_date_string,
                           first_point_xytext,
                           second_point_y_rolling_total,
                           second_point_x_date_string,
                           second_point_xytext,
                           third_point_y_rolling_total,
                           third_point_x_date_string,
                           third_point_xytext]
            # Store Data (serialize)
            with open(pickle_path, 'wb') as handle:
                pickle.dump(pickle_list, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # GRAPH
        self.log.print_section('GRAPH & TABLE GENERATION')
        self.log.Wrap('Constructing graph, plotting data, and configuring tables...')
        # Make graph tic marks face outward
        rcParams['xtick.direction'] = 'out'
        rcParams['ytick.direction'] = 'out'
        # Construct Figure
        plt.ion() # MAKES PLOT.SHOW() NON-BLOCKING
        fig = plt.figure(figsize=(17, 11))
        fig.set_facecolor('0.77')
        fig.set_dpi(140)
        # fig.text(0.51,0.31, fontsize=10, color="black")
        if self.data_type == 'PRCP':
        #    if num_stations_used < 14:
            ax1 = plt.subplot2grid((9, 10), (0, 0), colspan=10, rowspan=6)
            ax2 = plt.subplot2grid((9, 10), (6, 3), colspan=7, rowspan=2)
            ax3 = plt.subplot2grid((9, 10), (6, 0), colspan=3, rowspan=2)
            ax4 = plt.subplot2grid((9, 10), (8, 3), colspan=7, rowspan=1)
        #    if num_stations_used > 10:
        #        ax1 = plt.subplot2grid((9, 10), (0, 0), colspan=10, rowspan=5)
        #        ax2 = plt.subplot2grid((9, 10), (5, 3), colspan=7, rowspan=2)
        #        ax3 = plt.subplot2grid((9, 10), (5, 0), colspan=3, rowspan=2)
        #        ax4 = plt.subplot2grid((9, 10), (7, 3), colspan=7, rowspan=1)
            # Add Logo
            try:
                images_folder = os.path.join(ROOT, 'images')
                logo_file = os.path.join(images_folder, 'RD_2_0.png')
                logo = plt.imread(logo_file)
            except:
                images_folder = os.path.join(sys.prefix, 'images')
                logo_file = os.path.join(images_folder, 'RD_2_0.png')
                logo = plt.imread(logo_file)
            img = fig.figimage(X=logo, xo=118, yo=8)

        else:
            ax1 = plt.subplot2grid((9, 10), (0, 0), colspan=10, rowspan=7)
            ax2 = plt.subplot2grid((9, 10), (7, 3), colspan=7, rowspan=2)
            ax3 = plt.subplot2grid((9, 10), (7, 0), colspan=3, rowspan=2)

        # Configure ticks on main graph
        ax1.xaxis.set_major_locator(dates.MonthLocator())
        # 16 is a slight approximation since months differ in number of days.
        ax1.xaxis.set_minor_locator(dates.MonthLocator(bymonthday=16))
        ax1.xaxis.set_major_formatter(ticker.NullFormatter())
        ax1.xaxis.set_minor_formatter(dates.DateFormatter('%b\n%Y'))
        for tick in ax1.xaxis.get_minor_ticks():
            tick.tick1line.set_markersize(0)
            tick.tick2line.set_markersize(0)
            tick.label1.set_horizontalalignment('center')
        ax1.tick_params(axis='x', which='minor', bottom=False)

        # Remove axis from second subplot (For displaying tables)
        ax2.axis('off')
        ax3.axis('off')
        ax2.axis('tight')
        ax3.axis('tight')
        if self.data_type == 'PRCP':
            ax4.axis('off')
            ax4.axis('tight')

        # Create a truncated date range to allow for incomplete current water years
        print(Dates.shape)

        truncate = str(Dates[len(rolling30day)-1])[:10]
        truncDates = pandas.date_range(self.dates.graph_start_date, truncate)

        # Plot Data on Graph
        ax1.plot(truncDates.to_pydatetime(),
                 self.finalDF[self.dates.graph_start_date:self.dates.graph_end_date],
                 color='black',
                 linewidth=1,
                 drawstyle='steps-post',
                 label='Daily Total')

        # PLOT FORECAST DATA (If enabled)
        if self.forecast_setting is True:
            try:
                ax1.plot(days,
                         mm,
                         color='red',
                         linewidth=1.2,
                         drawstyle='steps-post',
                         label='Daily Total Forecast')
            except:
                pass

        # Plot Rolling 30-day total
        if self.data_type != 'SNWD':
            ax1.plot(truncDates.to_pydatetime(),
                     rolling30day,
                     linewidth=1.2,
                     label='30-Day Rolling Total',
                     color='blue')

        # Plot area between normal high and normal low 30-day rolling totals
        ax1.fill_between(Dates.to_pydatetime(),
                         normal_low_series[self.dates.graph_start_date:self.dates.graph_end_date],
                         normal_high_series[self.dates.graph_start_date:self.dates.graph_end_date],
                         color='orange',
                         label='30-Year Normal Range',
                         alpha=0.5)

        # Set the minimum Y value to 0 and the Max Y value to just above the max value
        if self.yMax == None:
            max30 = rolling_30_day_max
            max20 = normal_high_series[self.dates.graph_start_date:self.dates.graph_end_date].max()
            if max30 > max20:
                yMax = max30*1.03
            else:
                yMax = max20*1.03
            ax1.set_ylim(ymin=0, ymax=yMax)
        else:
            ax1.set_ylim(ymin=0, ymax=float(self.yMax))
            yMax = self.yMax

        # Force the Min and Max X Values to the Graph Dates
        graph_start_datetime = datetime.strptime(self.dates.graph_start_date, '%Y-%m-%d')
        graph_end_datetime = datetime.strptime(self.dates.graph_end_date, '%Y-%m-%d')
        ax1.set_xlim([graph_start_datetime, graph_end_datetime])

        # Configure Labels
        handles, labels = ax1.get_legend_handles_labels()
        ax1.legend(handles, labels)
        ax1.set_ylabel(u'Rainfall ({})'.format(units_long), fontsize=20)

        # Mark / Label Sampling Points
        if self.data_type == 'PRCP':
#            ax1.set_title("Antecedent Precipitation and 30-Year Normal Range from NOAA's Daily Global Historical Climatology Network",
#                          fontsize=20)
            if self.gridded is False:
                ax1.set_title("Antecedent Precipitation vs Normal Range based on NOAA's Daily Global Historical Climatology Network",
                              fontsize=20)
            elif self.gridded is True:
                ax1.set_title("Antecedent Precipitation vs Normal Range based on NOAA's nClimGrid-Daily Precipitation Data",
                              fontsize=20)
#            ax1.set_title('NOAA - National Climatic Data Center - Daily Global'
#                          ' Historical Climatology Network - Rainfall Data',
#                          fontsize=20)

            if first_point_y_rolling_total:
                first_point_label = first_point_x_date_string
                ax1.annotate(first_point_label,
                             xy=(pandas.Timestamp(first_point_x_date_string),
                                                  first_point_y_rolling_total),
                             xycoords='data',
                             xytext=first_point_xytext,
                             textcoords='offset points',
                             size=13,
                             # bbox=dict(boxstyle="round", fc="0.8"),
                             arrowprops=dict(arrowstyle="simple",
                                             fc="0.4", ec="none",
                                             connectionstyle="arc3,rad=0.5"),
                            )

            if second_point_y_rolling_total:
                second_point_label = second_point_x_date_string
                ax1.annotate(second_point_label,
                             xy=(pandas.Timestamp(second_point_x_date_string),
                                 second_point_y_rolling_total),
                             xycoords='data',
                             xytext=second_point_xytext,
                             textcoords='offset points',
                             size=13,
                             # bbox=dict(boxstyle="round", fc="0.8"),
                             arrowprops=dict(arrowstyle="simple",
                                             fc="0.4", ec="none",
                                             connectionstyle="arc3,rad=0.5"),
                            )

            if third_point_y_rolling_total:
                third_point_label = third_point_x_date_string
                ax1.annotate(third_point_label,
                             xy=(pandas.Timestamp(third_point_x_date_string),
                                                  third_point_y_rolling_total),
                             xycoords='data',
                             xytext=third_point_xytext,
                             textcoords='offset points',
                             size=13,
                             # bbox=dict(boxstyle="round", fc="0.8"),
                             arrowprops=dict(arrowstyle="simple",
                                             fc="0.4", ec="none",
                                             connectionstyle="arc3,rad=0.5"),
                            )

            # Plot Description Table
            description_table = ax3.table(cellText=description_table_values,
                                          colWidths=[0.4, 0.54],
                                          cellColours=description_table_colors,
                                          loc='center left')
            description_table.auto_set_font_size(False)
            description_table.set_fontsize(10)

            # Plot Rain Table
            the_table = ax2.table(cellText=rain_table_vals,
                                  cellColours=rain_colors,
                                  colWidths=[0.112, 0.111, 0.111, 0.120, 0.135, 0.114, 0.1, 0.18],
                                  loc='center')
            the_table.auto_set_font_size(False)
            the_table.set_fontsize(10)

            # Plot Stations Table
            if self.gridded is False:
                station_table_colors = [[light_grey, light_grey, light_grey, light_grey, light_grey, light_grey, light_grey, light_grey]]
                for row in station_table_values[:]:
                    station_table_colors.append([white, white, white, white, white, white, white, white])

                # combine the station table headers and values after sorting by distance from the location of interest
                station_table_values = station_table_column_labels + station_table_values

                stations_table = ax4.table(cellText=station_table_values,
                                           cellColours=station_table_colors,
                                           colWidths=[0.25, 0.15, 0.095, 0.097, 0.087, 0.087, 0.104, 0.132],
                                           loc='center')
                stations_table.auto_set_font_size(False)
                stations_table.set_fontsize(10)

            # Plot station count data from GHCN gridded dataset
            if self.gridded is True:
                station_table_colors = [[light_grey, light_grey]]
                for row in station_table_values[:]:
                    station_table_colors.append([white, white])

                # combine the station table headers and values after sorting by distance from the location of interest
                station_table_values = station_table_column_labels + station_table_values

                stations_table = ax4.table(cellText=station_table_values,
                                           cellColours=station_table_colors,
                                           colWidths=[0.4, 0.3],
                                           loc='center')
                stations_table.auto_set_font_size(False)
                stations_table.set_fontsize(10)

            # Determine bottom separation value by table rows
            if num_stations_used < 4:
                bValue = 0.01
            elif num_stations_used == 4:
                bValue = 0.02
            elif num_stations_used == 5:
                bValue = 0.03
            elif num_stations_used == 6:
                bValue = 0.035
            elif num_stations_used == 7:
                bValue = 0.04
            elif num_stations_used == 8:
                bValue = 0.050
            elif num_stations_used == 9:
                bValue = 0.055
            elif num_stations_used == 10:
                bValue = 0.059
            elif num_stations_used == 11:
                bValue = 0.068
            else:
                bValue = 0.08

            # Determine horizontal separation value by table rows
            if num_stations_used < 9:
                hValue = 0.00
            elif num_stations_used < 11:
                hValue = 0.17
            else:
                hValue = 0.8

            # Remove space between subplots
            plt.subplots_adjust(wspace=0.00,
                                hspace=hValue,
                                left=0.047,
                                bottom=bValue,
                                top=0.968,
                                right=0.99)

        ################################################################
        ############ START OF SNOW AND SNOW DEPTH SECTION ##############
        ################################################################

        if self.data_type == 'SNOW':
            ax1.set_title('NOAA - National Climatic Data Center - Daily Global'
                          ' Historical Climatology Network - Snowfall Data', fontsize=20)

        if self.data_type == 'SNWD':
            ax1.set_title('NOAA - National Climatic Data Center - Daily Global'
                          ' Historical Climatology Network - Snow Depth Data', fontsize=20)

        if self.data_type == 'SNOW' or self.data_type == 'SNWD':
            if first_point_y_rolling_total is not None:
                first_point_label = 'Observation Date'
                ax1.annotate(first_point_label, xy=(first_point_x_date_string, first_point_y_rolling_total), xycoords='data',
                             xytext=first_point_xytext,
                             textcoords='offset points',
                             size=15,
                             # bbox=dict(boxstyle="round", fc="0.8"),
                             arrowprops=dict(arrowstyle="simple",
                                             fc="0.4", ec="none",
                                             connectionstyle="arc3,rad=0.5"),
                            )

            # Plot Description Table
            description_table = ax3.table(cellText=description_table_values,
                                          colWidths=[0.4, 0.54],
                                          loc='center')
            description_table.auto_set_font_size(False)
            description_table.set_fontsize(10)


            # Plot Stations Table
            stations_table = ax2.table(cellText=station_table_values,
                                       colLabels=station_table_column_labels,
                                       colWidths=[0.25, 0.15, 0.095, 0.09, 0.09, 0.09, 0.11, 0.11],
                                       loc='center')
            stations_table.auto_set_font_size(False)
            stations_table.set_fontsize(10)

            # Remove extra white space around figure.
            fig.tight_layout()

            # Remove space between subplots
            plt.subplots_adjust(left=0.058,
                                bottom=0.02,
                                right=0.97,
                                top=0.968,
                                wspace=0.51,
                                hspace=0.51)

        ##########################################################
        ########## END OF SNOW AND SNOW DEPTH PORTION ############
        ##########################################################

        self.log.Wrap('Generating figure with graph and tables...')
        self.log.Wrap('')

        if self.save_folder is None:
            # Display Figure
            plt.show()
            time.sleep(1)
            if self.data_type != 'PRCP':
                ante_calc_result = 'N/A'
            return None, yMax, ante_calc_result, score, wet_dry_season_result, palmer_value, palmer_class
        else:
            # Save PDF
            if self.image_name != "N/A":
                imagePath = os.path.join(self.folderPath, '{}_{}.pdf'.format(self.dates.observation_date, self.image_name))
            else:
                imagePath = os.path.join(self.folderPath, '{}.pdf'.format(self.dates.observation_date))
            self.log.Wrap('Saving ' + imagePath)
            fig.savefig(imagePath, facecolor='0.77')

            # Closing figure in memory safe way
            self.log.Wrap('Closing figure...')
            pylab.close(fig)
            self.log.Wrap('')
            if self.data_type != 'PRCP':
                ante_calc_result = 'N/A'
            self.log.print_separator_line()
            self.log.Wrap('')
            return imagePath, yMax, ante_calc_result, score, wet_dry_season_result, palmer_value, palmer_class

if __name__ == '__main__':
    SAVE_FOLDER = os.path.join(ROOT, 'Outputs')
    INSTANCE = AnteProcess()
        # Input_List reference
#        self.data_type = inputList[0]
#        self.site_lat = inputList[1]
#        self.site_long = inputList[2]
#        year = inputList[3]
#        month = inputList[4]
#        day = inputList[5]
#        self.image_name = inputList[6]
#        self.image_source = inputList[7]
#        self.SAVE_FOLDER = inputList[8]
#        self.forecast_setting = inputList[9]
    # INPUT_LIST = ['PRCP',
    #               '38.5',
    #               '-121.5',
    #               2018,
    #               10,
    #               15,
    #               None,
    #               None,
    #               SAVE_FOLDER,
    #               False]
    # INPUT_LIST = ['PRCP',
    #               '62.235095',
    #               '-159.057434',
    #               2018,
    #               10,
    #               15,
    #               None,
    #               None,
    #               SAVE_FOLDER,
    #               False]
    INPUT_LIST = [['PRCP',
                  '33.2098',
                  '-87.5692',
                  2021,
                  10,
                  15,
                  None,
                  None,
                  SAVE_FOLDER,
                  False]]
    for i in INPUT_LIST:
        INSTANCE.setInputs(i, watershed_analysis=False, all_sampling_coordinates=None, gridded=False)
    input('Stall for debugging.  Press enter or click X to close')
