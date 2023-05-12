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
##         netcdf_parse_all.py      ##
##  ------------------------------- ##
##      Writen by: Jason Deters     ##
##      Edited by: Joseph Gutenson  ##
##      Edited by: Chase Hamilton   ##
##  ------------------------------- ##
##    Last Edited on: 2022-11-11    ##
##  ------------------------------- ##
######################################

# Import Standard Libraries
import math
import multiprocessing
from datetime import datetime, timedelta
from dateutil import relativedelta

# Import 3rd party libraries
import netCDF4
import numpy
from geopy.distance import great_circle
import pandas


RECENT_CHECK = False


def tunnel_fast(latvals, lonvals, lat0, lon0):
    '''
    Find closest point in a set of (lat,lon) points to specified point
    latvar - 2D latitude variable from an open netCDF dataset
    lonvar - 2D longitude variable from an open netCDF dataset
    lat0,lon0 - query point
    Returns iy,ix such that the square of the tunnel distance
    between (latval[it,ix],lonval[iy,ix]) and (lat0,lon0)
    is minimum.
    '''
    rad_factor = math.pi/180.0 # for trignometry, need angles in radians
    # Read latitude and longitude from file into numpy arrays
    latvals = latvals * rad_factor
    lonvals = lonvals * rad_factor
    #ny, nx = latvals.shape
    lat0_rad = lat0 * rad_factor
    lon0_rad = lon0 * rad_factor
    # Compute numpy arrays for all values, no loops
    clat,clon = numpy.cos(latvals),numpy.cos(lonvals)
    slat,slon = numpy.sin(latvals),numpy.sin(lonvals)
    delX = numpy.cos(lat0_rad)*numpy.cos(lon0_rad) - clat*clon
    delY = numpy.cos(lat0_rad)*numpy.sin(lon0_rad) - clat*slon
    delZ = numpy.sin(lat0_rad) - slat;
    dist_sq = delX**2 + delY**2 + delZ**2
    minindex_1d = dist_sq.argmin()  # 1D index of minimum element
    iy_min, ix_min = numpy.unravel_index(minindex_1d, latvals.shape)
    x = numpy.unravel_index(minindex_1d, latvals.shape)
    return iy_min, ix_min

###
#    Deprecated in favor of the numpy implementation below
#
###
#def get_closest_coordinates(dataset, lat, lon):
#    print('Finding closest coordinates...')
#    start_time = datetime.now()
#    latvals = dataset.variables['lat'][:]
#    lonvals = dataset.variables['lon'][:]
#    test_coords = (lat, lon)
#    lowest_distance = 9999999
#    for dataset_lat in latvals:
#        for dataset_lon in lonvals:
#            dataset_coords = (dataset_lat, dataset_lon)
#            distance = great_circle(test_coords, dataset_coords).miles
#            if distance < lowest_distance:
#                lowest_distance = distance
#                closest_lat = dataset_lat
#                closest_lon = dataset_lon
#    time_taken = datetime.now() - start_time # No longer used
#    print('Found closest coordinates in {} seconds'.format(time_taken))
#    print('Closest = {}, {}'.format(closest_lat, closest_lon))
#    return closest_lat, closest_lon
###

def get_closest_coordinates_numpy(dataset, lat0, lon0):
    print('Creating complete list of coordinates...')
    lat_variable = dataset.variables['lat']
    lon_variable = dataset.variables['lon']
    lat_degree_vals = lat_variable[:]
    lon_degree_vals = lon_variable[:]
    lat_array_list = []
    lon_array_list = []
    for dataset_lat in lat_degree_vals:
        for dataset_lon in lon_degree_vals:
            lat_array_list.append(dataset_lat)
            lon_array_list.append(dataset_lon)
    lat_degree_vals_numpy = numpy.array(lat_array_list)
    lon_degree_vals_numpy = numpy.array(lon_array_list)
    print('Locating closest coordinate pair...')
    rad_factor = math.pi/180.0 # for trignometry, need angles in radians

    # Read latitude from file into numpy arrays
    latvals = lat_degree_vals_numpy * rad_factor
    lat0_rad = lat0 * rad_factor

    # Find nearest grid cell centroid using Haversine Distance
    r = 6371 #radius of the earth in km
    dlat = rad_factor * (lat_degree_vals_numpy - lat0)
    dlon = rad_factor * (lon_degree_vals_numpy - lon0)
    a = numpy.sin(dlat/2)**2 + numpy.cos(lat0_rad) * numpy.cos(latvals) * numpy.sin(dlon/2)**2
    c = 2 * numpy.arctan2(numpy.sqrt(a), numpy.sqrt(1-a))
    distance = c * r # in units of km
    distance_min = numpy.amin(distance)*0.621371
    minindex_1d = distance.argmin()  # 1D index of minimum element
    closest_lat = lat_degree_vals_numpy[minindex_1d]
    closest_lon = lon_degree_vals_numpy[minindex_1d]

    # Convert to positions
    n = 0
    for lat_degree_val in lat_degree_vals:
        if lat_degree_val == closest_lat:
            lat_index = n
        n += 1
    n = 0
    for lon_degree_val in lon_degree_vals:
        if lon_degree_val == closest_lon:
            lon_index = n
        n += 1
    return closest_lat, lat_index, closest_lon, lon_index, distance_min, lat_array_list, lon_array_list


### Check if connectivity exists to the NOAA THREDDS server
### Only check once every three minutes, to make sure we're not overloading them

def check_thredds_status():
    global RECENT_CHECK

    if RECENT_CHECK:
        if datetime.now() - RECENT_CHECK[0] < timedelta(minutes=3):
            return RECENT_CHECK[1]

    try:
        netCDF4.Dataset("https://www.ncei.noaa.gov/thredds/dodsC/nclimgrid-daily/1990/ncdd-199001-grd-scaled.nc")
        good = True
    except:
        good = False

    RECENT_CHECK = (datetime.now(), good)
    return good


def get_nc_files(prcp_netcdf_folder, station_count_netcdf_folder, normal_period_data_start_date, actual_data_end_date):
    nc_dates_and_files = []
    # create a unique list of month-day pairs to use when downloading gridded data
    months = []
    query_dates = []
    while normal_period_data_start_date <= actual_data_end_date:
        if [normal_period_data_start_date.year, normal_period_data_start_date.month] not in query_dates:
            months.append(normal_period_data_start_date.month)
            query_dates.append([normal_period_data_start_date.year,normal_period_data_start_date.month])
        normal_period_data_start_date += timedelta(days=1)

    # loop through the days to create the inputs that will feed workers in the multiprocessing step
    for query_date in query_dates:
        year = str(query_date[0])
        month = str(query_date[1])
        month = month.zfill(2)
        date = '{0}{1}'.format(year,month)

        station_count_file = 'ncddsupp-{0}-obcounts.nc'.format(date)
        station_count_file_path = '{0}/{1}/{2}'.format(station_count_netcdf_folder,year,station_count_file)

        # create the paths to the precip netcdfs
        currentMonth = datetime.now().month
        currentYear = datetime.now().year
        currentDay = datetime.now().day
        currentYearMonth = datetime(currentYear, currentMonth, 1)
        testYearMonth = datetime(int(year), int(month), 1)
        # if the month is within two months of the current month, file name will be different
        delta = relativedelta.relativedelta(currentYearMonth, testYearMonth)
        delta_months = delta.months + (delta.years * 12)
        # if within 2 months, the preliminary grid may still apply
        if delta_months <= 2:
            prcp_file = 'ncdd-{0}-grd-prelim.nc'.format(date)
        else:
            prcp_file = 'ncdd-{0}-grd-scaled.nc'.format(date)
        prcp_file_path = '{0}/{1}/{2}'.format(prcp_netcdf_folder,year,prcp_file)
        nc_dates_and_files.append([date, prcp_file_path, station_count_file_path])

    nc_dates_and_files.sort(key=lambda x: x[0], reverse=False)
    return nc_dates_and_files


def nc_file_worker(args):

    # Split input tuple into constituents
    nc_file = args[0]
    lat_index = args[1]
    lon_index = args[2]

    # Get precip file date from nc_file list
    file_date = nc_file[0]

    # Instantiate empty values
    total_rows = 0
    data_rows = 0
    blank_rows = 0

    prcp_values = []
    timestamps = []
    station_count_values = []

    # Open precip dataset
    # assume if there is an issue opening the precip dataset it's because
    # the file is still preliminary
    # if the error persists, it must be something with the THREDDS server
    try:
        prcp_dataset = netCDF4.Dataset(nc_file[1], 'r')
    except:
        try:
            nc_file_path = nc_file[1]
            nc_file_path = nc_file_path[:-9]
            nc_file_path = "{0}prelim.nc".format(nc_file_path)
            prcp_dataset = netCDF4.Dataset(nc_file_path, 'r')
        except:
            print("It appears the nClimGrid-Daily THREDDS data service is experiecing issues, please try again...\n")
            print("If the problems persists, please contact the nClimGrid-Daily team at ncei.grids@noaa.gov\n")

    prcp = prcp_dataset.variables['prcp']
    timevar = prcp_dataset.variables['time']
    timeunits = timevar.units
    times = timevar[:]

    # Open station count dataset
    station_count_dataset = netCDF4.Dataset(nc_file[2], 'r')
    station_count = station_count_dataset.variables['cntp']

    # Pull relevant data subset from precip & station count datasets
    prcp_vals = prcp[:, lat_index, lon_index]
    station_count_vals = station_count[:, lat_index, lon_index]

    # Process data and update variables
    for x_time in range(len(times)):
        total_rows += 1
        prcp_val = prcp_vals[x_time]

        if str(prcp_val) != '--':
            data_rows += 1
            prcp_values.append(prcp_val)

            time_val = netCDF4.num2date(times[x_time], timeunits)
            timestamp = pandas.Timestamp(str(time_val))

            timestamps.append(timestamp)

        else:
            blank_rows += 1

        station_count_val = station_count_vals[x_time]
        station_count_values.append(station_count_val)

    # Clean up NetCDF file connections
    prcp_dataset.close()
    del(prcp_dataset)
    station_count_dataset.close()
    del(station_count_dataset)

    return (file_date, prcp_values, timestamps, station_count_values, total_rows, data_rows, blank_rows)


class get_point_history(object):

    def __init__(self, lat, lon, normal_period_data_start_date, actual_data_end_date):
        self.lat = lat
        self.lon = lon
        self.closest_lat = None
        self.closest_lon = None
        self.lat_index = None
        self.lon_index = None
        self.nc_files = None
        self.csv_export_path = None
        self.prcp_data = []
        self.timestamps = []
        self.prcp_values = []
        self.station_count_values = []
        self.total_rows = 0
        self.blank_rows = 0
        self.data_rows = 0
        self.entire_precip_ts = None
        self.entire_station_count_ts = None
        self.distance = 0
        self.normal_period_data_start_date = normal_period_data_start_date
        self.actual_data_end_date = actual_data_end_date

    def __call__(self):
        print('Getting complete PRCP history for ({}, {})...'.format(self.lat, self.lon))
        netcdf_precip_folder = r'https://www.ncei.noaa.gov/thredds/dodsC/nclimgrid-daily'
        netcdf_station_count_folder = r'https://www.ncei.noaa.gov/thredds/dodsC/nclimgrid-daily-auxiliary'
        self.nc_files = get_nc_files(netcdf_precip_folder, netcdf_station_count_folder, self.normal_period_data_start_date, self.actual_data_end_date)

        # Open first dataset and get variables / basic info
        nc_file = self.nc_files[0]

        try:
            prcp_dataset = netCDF4.Dataset(nc_file[1], 'r')

            (self.closest_lat, self.lat_index, self.closest_lon, self.lon_index,
             self.distance, lat_array_list, lon_array_list) = get_closest_coordinates_numpy(prcp_dataset, self.lat, self.lon)

        except Exception as F:
            pass

        # Create list of all tasks
        process_queue = []

        for nc_file in self.nc_files:
            process_queue.append((nc_file, self.lat_index, self.lon_index))

        process_number = min(multiprocessing.cpu_count() - 2, 12)
        chunksize = process_number

        # Create empty results dictionary
        mp_results = {}

        # Chunk and loop through chunks, necessary to not run into blocking issues on Windows
        print("Downloading gridded time series data...\n")

        for i in range(0, len(process_queue), chunksize):
            chunk_start = datetime.now()

            start_index = i
            end_index = min(i + chunksize, len(process_queue))

            partial_queue = process_queue[start_index:end_index]

            mp_pool = multiprocessing.Pool(processes=process_number)

            for result in mp_pool.map(nc_file_worker, partial_queue):
                file_date, prcp_values, timestamps, station_count_values, total_rows, data_rows, blank_rows = result
                mp_results[file_date] = (prcp_values, timestamps, station_count_values, total_rows, data_rows, blank_rows)

                self.prcp_values += prcp_values
                self.timestamps += timestamps
                self.station_count_values += station_count_values
                self.total_rows += total_rows
                self.data_rows += data_rows
                self.blank_rows += blank_rows

            mp_pool.close()
            mp_pool.join()

            start_date = partial_queue[0][0][0]
            start_date = start_date[:4] + "-" + start_date[4:]
            end_date = partial_queue[-1][0][0]
            end_date = end_date[:4] + "-" + end_date[4:]

            print("{} through {}: {}".format(start_date, end_date, datetime.now() - chunk_start))

        # remove "masked" returns from station count results
        self.station_count_values = [x for x in self.station_count_values if x >= 0]
        # self.station_count_values.remove("masked")
        print(self.station_count_values)

        print('----------')
        print('')
        print('All datasets processed.')
        print('Converting data to TimeSeries format...')
        self.entire_precip_ts = pandas.Series(data=self.prcp_values,
                                       index=self.timestamps,
                                       dtype="float64",
                                       name='value')
        self.entire_station_count_ts = pandas.Series(data=self.station_count_values,
                                       index=self.timestamps,
                                       dtype="float64",
                                       name='value')
        print('Conversion complete.')
        print('')
        print('-'*119)
        print('Total rows = {}'.format(self.total_rows))
        print('Rows with data = {}'.format(self.data_rows))
        print('Blank rows = {}'.format(self.blank_rows))
        print('-'*119)
        return


if __name__ == '__main__':
    COORD_LIST = []
    COORD_LIST.append([35., -90.])
    #list_of_instances = []
    for COORDS in COORD_LIST:
        instance = get_point_history(COORDS[0], COORDS[1])
        instance()
        #list_of_instances.append(instance)
