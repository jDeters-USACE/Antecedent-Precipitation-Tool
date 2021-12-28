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
##  ------------------------------- ##
##    Last Edited on: 2021-12-28    ##
##  ------------------------------- ##
######################################

# Import Standard Libraries
import os
import math
import time

# Import 3rd Party Libraries
import netCDF4
import numpy
from geopy.distance import great_circle
import pandas

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


def get_closest_coordinates(dataset, lat, lon):
    print('Finding closest coordinates...')
    start_time = time.clock()
    latvals = dataset.variables['lat'][:]
    lonvals = dataset.variables['lon'][:]
    test_coords = (lat, lon)
    lowest_distance = 9999999
    for dataset_lat in latvals:
        for dataset_lon in lonvals:
            dataset_coords = (dataset_lat, dataset_lon)
            distance = great_circle(test_coords, dataset_coords).miles
            if distance < lowest_distance:
                lowest_distance = distance
                closest_lat = dataset_lat
                closest_lon = dataset_lon
    time_taken = time.clock() - start_time
    print('Found closest coordinates in {} seconds'.format(time_taken))
    print('Closest = {}, {}'.format(closest_lat, closest_lon))
    return closest_lat, closest_lon

#LAT, LON = get_closest_coordinates(DATASET, 38.5, -121.5)

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
    calc_start = time.clock()
    rad_factor = math.pi/180.0 # for trignometry, need angles in radians
    # Read latitude and longitude from file into numpy arrays
    latvals = lat_degree_vals_numpy * rad_factor
    lonvals = lon_degree_vals_numpy * rad_factor
    #ny, nx = latvals.shape
    lat0_rad = lat0 * rad_factor
    lon0_rad = lon0 * rad_factor
    # Compute numpy arrays for all values, no loops
    clat,clon = numpy.cos(latvals), numpy.cos(lonvals)
    slat,slon = numpy.sin(latvals), numpy.sin(lonvals)
    delX = numpy.cos(lat0_rad)*numpy.cos(lon0_rad) - clat*clon
    delY = numpy.cos(lat0_rad)*numpy.sin(lon0_rad) - clat*slon
    delZ = numpy.sin(lat0_rad) - slat;
    dist_sq = delX**2 + delY**2 + delZ**2
    minindex_1d = dist_sq.argmin()  # 1D index of minimum element
    closest_lat = lat_degree_vals_numpy[minindex_1d]
    closest_lon = lon_degree_vals_numpy[minindex_1d]
    time_taken = time.clock() - calc_start
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
    return closest_lat, lat_index, closest_lon, lon_index

def get_nc_files():
    # netcdf_folder = r'\\coe-spknv001sac.spk.ds.usace.army.mil\EGIS_GEOMATICS\Regulatory\BaseData\Climatology\nclimdivd\nclimdivd-alpha-nc'
    netcdf_folder = r'D:\2020_APT_SON\Gridded_Rainfall'
    nc_dates_and_files = []
    for root, directories, file_names in os.walk(netcdf_folder):
        for file_name in file_names:
            pre = file_name[:5]
            post = file_name[11:]
            date = file_name[5:11]
            file_path = os.path.join(root, file_name)
            nc_dates_and_files.append([date, file_path])
            # if pre == 'prcp-':
            #     if post == '-grd-scaled.nc':
            #         file_path = os.path.join(root, file_name)
            #         nc_dates_and_files.append([date, file_path])
    nc_dates_and_files.sort(key=lambda x: x[0], reverse=False)
    nc_files = []
    for nc_date_and_file in nc_dates_and_files:
        nc_files.append(nc_date_and_file[1])
    return nc_files

class get_point_history(object):

    def __init__(self, lat, lon):
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
        self.total_rows = 0
        self.blank_rows = 0
        self.data_rows = 0
        self.entire_ts = None

    def __call__(self):
        print('Getting complete PRCP history for ({}, {})...'.format(self.lat, self.lon))
        self.nc_files = get_nc_files()
        num_datasets = len(self.nc_files)
        current_dataset = 0
        for nc_file in self.nc_files:
            current_dataset += 1
            try:
                # Open dataset and get variables / basic info
                dataset = netCDF4.Dataset(nc_file, 'r')
                prcp = dataset.variables['prcp']
                timevar = dataset.variables['time']
                timeunits = timevar.units
                times = timevar[:]
                # Find closest Lat/Lon and set export path
                if self.closest_lat is None or self.closest_lon is None:
                    self.closest_lat, self.lat_index, self.closest_lon, self.lon_index = get_closest_coordinates_numpy(dataset, self.lat, self.lon)
                    print('Closest coordinates in dataset = {}, {}'.format(self.closest_lat, self.closest_lon))
                    query_coords = (self.lat, self.lon)
                    grid_coords = (self.closest_lat, self.closest_lon)
                    distance = great_circle(query_coords, grid_coords).miles
                    print('Distance to center of grid = {} miles'.format(distance))
                    print('Reading values from {} netCDF datasets...'.format(num_datasets))
                # Collect/print/write relevant values
                for x_time in range(len(times)):
                    prcp_val = prcp[x_time, self.lat_index, self.lon_index]
                    self.total_rows += 1
                    if str(prcp_val) != '--':
                        self.data_rows += 1
                        self.prcp_values.append(prcp_val)
                        time_val = netCDF4.num2date(times[x_time], timeunits)
                        t_stamp = pandas.Timestamp(time_val)
                        self.timestamps.append(t_stamp)
                    else:
                        self.blank_rows += 1
            except Exception as F:
                print('----------')
                print('----EXCEPTION!!!------')
                print('----------')
                print('Error processing dataset {} of {}'.format(current_dataset, num_datasets))
                dataset_name = os.path.split(nc_file)[1]
                print('Dataset name = {}'.format(dataset_name))
                print(str(F))
                print('----------')
                print('----EXCEPTION!!!------')
        print('----------')
        print('')
        print('All datasets processed.')
        # Convert to pandas dataframe
        print('Converting data to TimeSeries format...')
        self.entire_ts = pandas.Series(data=self.prcp_values,
                                       index=self.timestamps,
                                       dtype="object",
                                       name='value')
        print('Conversion complete.')
        # Print and log summary stats
        print('')
        print('-'*119)
        print('Total rows = {}'.format(self.total_rows))
        print('Rows with data = {}'.format(self.data_rows))
        print('Blank rows = {}'.format(self.blank_rows))
        print('-'*119)
        return


if __name__ == '__main__':
    COORD_LIST = []
    COORD_LIST.append([36.5, -121.5])
##    COORD_LIST.append([39.1122, -119.7603])
##    COORD_LIST.append([46.925686, -117.683027])
##    COORD_LIST.append([46.925718, -117.682981])
##    COORD_LIST.append([37.197776, -117.813483])
##    COORD_LIST.append([35.1919, -80.6567])
##    COORD_LIST.append([49.354, -95.0625]) # Complete History
##    COORD_LIST.append([38.790289, -120.798243]) # Kelsey
##    COORD_LIST.append([38.5, -121.5]) # Empty in previous tests, complete 03/12/2018
##    COORD_LIST.append([36.5, -121.5]) # Sparse Stations
    list_of_instances = []
    for COORDS in COORD_LIST:
        instance = get_point_history(COORDS[0], COORDS[1])
        instance()
        list_of_instances.append(instance)
    raw_input("STALLING...")
