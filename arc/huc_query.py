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
##           huc_query.py           ##
##  ------------------------------- ##
##      Copyright: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on: 2020-05-27    ##
##  ------------------------------- ##
######################################

"""
Identify the HUC of a given huc_digits in which the supplied coordinates lie.
If selected, generate random sampling points (# and minimum spacing determined by HUC Digits) 
"""

# Import Standard Libraries
import os
import sys
import random

# Import 3rd Party Libraries
import ogr
ogr.UseExceptions()

# Import Custom Libraries
MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.split(MODULE_PATH)[0]
try:
    from . import get_files
    from .utilities import JLog
except Exception:
    import get_files
    TEST = os.path.exists('{}\\Python Scripts'.format(ROOT))
    if TEST:
        sys.path.append('{}\\Python Scripts\\utilities'.format(ROOT))
    else:
        sys.path.append('{}\\arc\\utilities'.format(ROOT))
    import JLog


# Function Definitions

def ensure_dir(folder):
    """Ensures entire directory structure given exists"""
    try:
        os.makedirs(folder)
    except Exception:
        pass
# End of ensure_dir function

def findHorizontalUnits(csString):
    pLoc = csString.find('PROJCS')
    if pLoc == -1:
        startLoc = 0
    else:
        fLoc = csString.find('UNIT["')
        startLoc = len('UNIT["') + fLoc
    uLoc = csString.find('UNIT["',startLoc)
    midLoc = len('UNIT["') + uLoc
    endLoc = csString.find('"',midLoc)
    finalString = csString[midLoc:endLoc]
    return finalString

def huc_id_and_sample(lat, lon, huc_digits, sample=False, base_huc=None):
    """
    Identify the HUC of a given huc_digits in which the supplied coordinates lie.
    If selected, generate random sampling points (# and minimum spacing determined by HUC Digits) 
    """
    # Shapefile Query Adapted from
    # https://stackoverflow.com/questions/7861196/check-if-a-geopoint-with-latitude-and-longitude-is-within-a-shapefile/13433127#13433127
    log = JLog.PrintLog(Delete=False)
    lat = float(lat)
    lon = float(lon)
    log.Wrap("Identifying HUC{} Watershed".format(huc_digits))
    attribute_filter = None
    # Find module path
    module_folder = os.path.dirname(os.path.realpath(__file__))
    # Find ROOT folder
    root_folder = os.path.split(module_folder)[0]
    # Find WBD folder
    wbd_folder = u'{}\\GIS\\WBD'.format(root_folder)
    # Set HUC_Scale-Specific Values
    if huc_digits == 2:
        # Find Selected WBD shapefile
        shapefile = '{}\\HUC2.shp'.format(wbd_folder)
        field_name = "HUC2"
    elif huc_digits == 8:
        # Calc Shapefile and Field
        shapefile = u'{}\\GIS\\WBD\\{}\\Shape\\WBDHU{}.shp'.format(root_folder, str(base_huc)[:2], huc_digits)
        field_name = "HUC{}".format(huc_digits)
    elif huc_digits == 10:
        # Calc Shapefile and Field
        shapefile = u'{}\\GIS\\WBD\\{}\\Shape\\WBDHU{}.shp'.format(root_folder, str(base_huc)[:2], huc_digits)
        field_name = "HUC{}".format(huc_digits)
        # Get attribute filter
        attribute_filter = "HUC10 LIKE '{}%'".format(base_huc)
    elif huc_digits == 12:
        # Find Selected WBD_Shapefile and 
        shapefile = u'{}\\GIS\\WBD\\{}\\Shape\\WBDHU{}.shp'.format(root_folder, str(base_huc)[:2], huc_digits)
        field_name = "HUC{}".format(huc_digits)
        # Get attrigbute filter
        attribute_filter = "HUC12 LIKE '{}%'".format(base_huc)
    
    # Test for Shapefile
    log.Wrap('Checking for existing Watershed Boundary Data...')
    shapefile_exists = os.path.exists(shapefile)
    if shapefile_exists:
        log.Wrap('  Watershed Boundary Data found')
    else:
        get_huc2_package(str(base_huc)[:2])

    # Create list to store exploded points
    previously_selected_points = []
    coordinates_within_polygon = []

    # Open shapefile
    log.Wrap(' -Reading local HUC{} dataset'.format(huc_digits))
    ds_in = ogr.Open(shapefile)    #Get the contents of the shape file
    lyr_in = ds_in.GetLayer()    #Get the shape file's first layer

    # Put the title of the field you are interested in here
    idx_reg = lyr_in.GetLayerDefn().GetFieldIndex(field_name)

    #If the latitude/longitude we're going to use is not in the projection
    #of the shapefile, then we will get erroneous results.
    #The following assumes that the latitude longitude is in WGS84
    #This is identified by the number "4326", as in "EPSG:4326"
    #We will create a transformation between this and the shapefile's
    #project, whatever it may be
    geo_ref = lyr_in.GetSpatialRef()
    # Parse horizontal units from CS String
    horizontal_units = findHorizontalUnits(str(geo_ref))
    point_ref = ogr.osr.SpatialReference()
    point_ref.ImportFromEPSG(4326)
    ctran = ogr.osr.CoordinateTransformation(point_ref, geo_ref)
    rtran = ogr.osr.CoordinateTransformation(geo_ref, point_ref)

    # North_America_Albers_Equal_Area_Conic
    albers_ref = ogr.osr.SpatialReference()
    albers_ref.ImportFromEPSG(102008)
    transform_source_to_albers = ogr.osr.CoordinateTransformation(geo_ref, albers_ref)
    transform_albers_to_WGS = ogr.osr.CoordinateTransformation(albers_ref, point_ref)

    #Transform incoming longitude/latitude to the shapefile's projection
    [t_lon, t_lat, z] = ctran.TransformPoint(lon, lat)

    # Create a point
    pt = ogr.Geometry(ogr.wkbPoint)
    pt.SetPoint_2D(0, t_lon, t_lat)

    # For efficiency, filter by HUC8 First (If applicable)
    if attribute_filter is not None:
        log.Wrap(' -Filtering {} features by HUC{} ({})...'.format(field_name, len(base_huc), base_huc))
        lyr_in.SetAttributeFilter(attribute_filter)
        log.Wrap(' -Testing remaining {} features against selected coordinates...'.format(field_name))
        for feat_in in lyr_in:
            feat_in_geom = feat_in.geometry()
            contains_point = feat_in_geom.Contains(pt)
            if contains_point:
                selected_huc = feat_in
                selected_huc_geom = feat_in_geom
                break    

    # Pure SpatialFilter method, incredibly slow for HUC10 and HUC12 (Hangs)
    else:
        # Set up a spatial filter such that the only features we see when we
        # loop through "lyr_in" are those which overlap the point defined above
        log.Wrap(' -Filtering HUC{} features by spatial overlap with selected coordinates...'.format(huc_digits))  
        lyr_in.SetSpatialFilter(pt)
        # Loop through the overlapped features and display the field of interest
        for feat_in in lyr_in:
            selected_huc = feat_in
            selected_huc_geom = selected_huc.geometry()
            break

    # Get Area of selected HUC
    supported_units = ['meter', 'meters' 'foot', 'feet', 'us feet', 'us foot', 'us_foot', 'foot_us']
    if not horizontal_units.lower() in supported_units:
        # Transform geometry to Albers
        selected_huc_geom.Transform(transform_source_to_albers)
        # Update horizontal units
        geo_ref = selected_huc_geom.GetSpatialReference()
        horizontal_units = findHorizontalUnits(str(geo_ref))
    if horizontal_units.lower() in supported_units:
        # Calculate Area
        selected_huc_area = selected_huc_geom.GetArea()
        # Convert Area to Square Miles
        if horizontal_units.lower() in ['meter', 'meters']:
            huc_square_miles = selected_huc_area / 2590000
        elif horizontal_units.lower() in ['foot', 'feet', 'us feet', 'us foot', 'foot_us', 'us_foot']:
            huc_square_miles = selected_huc_area / 27880000
        huc_square_miles = round(huc_square_miles, 2)

    # Determine Sampling Distance and point spacing
    num_points = huc_square_miles / 18
    num_points = int(round(num_points, 0))    
    if num_points < 3:
        num_points = 3
    sampling_point_spacing_miles = round((huc_square_miles / 633.145), 2)
    if sampling_point_spacing_miles < 1:
        sampling_point_spacing_miles = 1
    if horizontal_units.lower() in ['meter', 'meters']:
        sampling_point_spacing = sampling_point_spacing_miles * 1609.34 # 1609.34 Meters = 1 Mi
    elif horizontal_units.lower() in ['foot', 'feet', 'us feet', 'us foot', 'foot_us', 'us_foot']:
        sampling_point_spacing = sampling_point_spacing_miles * 5280 # 5280 Feet = 1 Mi

    # Get the HUC Value of the selected watershed
    huc_string = selected_huc.GetFieldAsString(idx_reg)
    log.Wrap(' {}: {}'.format(field_name, huc_string))
    if sample is False:
        log.Wrap('')
    else:
        log.print_separator_line()

    #-----------------------RANDOM SAMPLING POINT GENERATOR SECTION---------------------#

    # Create Random Sampling Points at the selected spacing (If selected)
    if sample is True:
        # Calculate the Envelope (bounding box) of the selected HUC
        log.print_section('Random Sampling Point Generation Section')
        log.Wrap('Sampling Parameters:')
        log.Wrap(' -{} Points, including user-specified coordinates'.format(num_points))
        log.Wrap(' -All points fall Within the HUC{} ({})'.format(huc_digits, huc_string))
        log.Wrap(' -Each point at least {} mile(s) from all other sampling points'.format(sampling_point_spacing_miles))
        log.Wrap('Generating sampling points...')
        x_min, x_max, y_min, y_max = selected_huc_geom.GetEnvelope()
        # Add initially selected coordinates as the first sampling point
        previously_selected_points.append(pt)
        coordinates_within_polygon.append([lat, lon])
        num_points -= 1
        while num_points > 0:
            # Create a random X coordinate within the Envelope
            test_x = random.uniform(x_min, x_max)
            # Create a random Y coordinate within the Envelope
            test_y = random.uniform(y_min, y_max)
            # Create a blank Test Point (OGR Geometry of the type ogr.wkbPoint)
            test_pt = ogr.Geometry(ogr.wkbPoint)
            # Set the Test Point to the random X and Y coordinates
            test_pt.SetPoint_2D(0, test_x, test_y)
            # Test whether the within-envolope point is actually within the polygon
            inside = selected_huc_geom.Contains(test_pt)
            if inside:
                properly_spaced = True
                # Test against every previously selected point for optimal spacing
                for previous_point in previously_selected_points:
                    distance = test_pt.Distance(previous_point)
                    if distance < sampling_point_spacing:
                        properly_spaced = False
                # Test passed, add to all lists and reduce num_points needed
                if properly_spaced:
                    num_points -= 1
                    previously_selected_points.append(test_pt)
                    [wgs_lon, wgs_lat, z] = transform_albers_to_WGS.TransformPoint(test_x, test_y)
                    wgs_lat = round(wgs_lat, 6)
                    wgs_lon = round(wgs_lon, 6)
                    coordinates_within_polygon.append([wgs_lat, wgs_lon])
        log.Wrap('All {} sampling points generated successfully'.format(len(coordinates_within_polygon)))
        log.print_separator_line()
    return huc_string, coordinates_within_polygon, huc_square_miles

def huc8_id_and_sample(lat, lon):
    """Identifies the HUC8 within which the coordinates fall.
    Creates random sampling points within the selected HUC8 polygon"""
    # First Identify HUC2 (So we can download the relavent datasets)
    huc, sampling_points, huc_square_miles = huc_id_and_sample(lat=lat,
                                                               lon=lon,
                                                               huc_digits=2,
                                                               sample=False,
                                                               base_huc=None)
    # Itentify the HUC8 (Can directly use spatial filter on this dataset w/o hanging)
    huc, sampling_points, huc_square_miles = huc_id_and_sample(lat=lat,
                                                               lon=lon,
                                                               huc_digits=8,
                                                               sample=True,
                                                               base_huc=huc)
    return huc, sampling_points, huc_square_miles

def huc10_id_and_sample(lat, lon):
    """Identifies the HUC10 within which the coordinates fall.
    Creates random sampling points within the selected HUC10 polygon"""
    # First Identify HUC2 (So we can download the relavent datasets)
    huc, sampling_points, huc_square_miles = huc_id_and_sample(lat=lat,
                                                               lon=lon,
                                                               huc_digits=2,
                                                               sample=False,
                                                               base_huc=None)
    # Next Identify the HUC8 (Can directly use spatial filter on this dataset w/o Hanging)
    huc, sampling_points, huc_square_miles = huc_id_and_sample(lat=lat,
                                                               lon=lon,
                                                               huc_digits=8,
                                                               sample=False,
                                                               base_huc=huc)
    # Finally, use the HUC8 to narrow the HUC10s for individual testing (SpatialFilter Hangs)
    huc, sampling_points, huc_square_miles = huc_id_and_sample(lat=lat,
                                                               lon=lon,
                                                               huc_digits=10,
                                                               sample=True,
                                                               base_huc=huc)
    return huc, sampling_points, huc_square_miles

def huc12_id_and_sample(lat, lon):
    """Identifies the HUC12 within which the coordinates fall.
    Creates random sampling points within the selected HUC12 polygon"""
    # First Identify HUC2 (So we can download the relavent datasets)
    huc, sampling_points, huc_square_miles = huc_id_and_sample(lat=lat,
                                                               lon=lon,
                                                               huc_digits=2,
                                                               sample=False,
                                                               base_huc=None)
    # Then Identify the HUC8 (Can directly use spatial filter on this dataset w/o Hanging)
    huc, sampling_points, huc_square_miles = huc_id_and_sample(lat=lat,
                                                               lon=lon,
                                                               huc_digits=8,
                                                               sample=False,
                                                               base_huc=huc)
    # Next, use the HUC8 to narrow the HUC10s for individual testing (SpatialFilter Hangs)
    huc, sampling_points, huc_square_miles = huc_id_and_sample(lat=lat,
                                                               lon=lon,
                                                               huc_digits=10,
                                                               sample=False,
                                                               base_huc=huc)
    # Finally, use the HUC10 to narrow the HUC12s for individual testing (SpatialFilter Hangs)
    huc, sampling_points, huc_square_miles = huc_id_and_sample(lat=lat,
                                                               lon=lon,
                                                               huc_digits=12,
                                                               sample=True,
                                                               base_huc=huc)
    return huc, sampling_points, huc_square_miles

def id_and_sample(lat, lon, watershed_scale):
    """Runs the correct function to identify and randomly sample the HUC of the selected watershed_scale"""
    log = JLog.PrintLog(Delete=False)
    log.print_section('Watershed ({}) Identification Section'.format(watershed_scale))
    if watershed_scale == "HUC8":
        # Get HUC & Random Sampling Points
        huc, sampling_points, huc_square_miles = huc8_id_and_sample(lat=lat, lon=lon)
    elif watershed_scale == "HUC10":
        # Get HUC & Random Sampling Points
        huc, sampling_points, huc_square_miles = huc10_id_and_sample(lat=lat, lon=lon)
    elif watershed_scale == "HUC12":
        # Get HUC & Random Sampling Points
        huc, sampling_points, huc_square_miles = huc12_id_and_sample(lat=lat, lon=lon)
    return huc, sampling_points, huc_square_miles

def get_huc2_package(huc2):
    # Calculate url and paths
    file_url = 'https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/WBD/HU2/Shape/WBD_{}_HU2_Shape.zip'.format(huc2)
    module_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_folder)[0]
    local_file_path = u'{}\\GIS\\WBD\\WBD_{}_HU2_Shape.zip'.format(root_folder, huc2)
    extract_path = u'{}\\GIS\\WBD\\{}'.format(root_folder, huc2)
    # Download & Extract
    get_files.ensure_file_exists(file_url=file_url,
                                 local_file_path=local_file_path,
                                 extract_path=extract_path)



if __name__ == '__main__':
    import time
    start_time = time.clock()
    huc, sampling_points, huc_square_miles = id_and_sample(lat=38.4008283,
                                                           lon=-120.8286800,
                                                           watershed_scale="HUC8")
#    huc, sampling_points, huc_square_miles = id_and_sample(lat=40.4,
#                                                           lon=-80.4,
#                                                           watershed_scale="HUC8")
    print('HUC: '.format(huc))
    print('Square miles: {}'.format(huc_square_miles))
    print('Sampling Points:')
    for point in sampling_points:
        print(' {}'.format(point))
    duration = time.clock() - start_time
    print('Processing took {} seconds'.format(duration))

    DEVMODE = False
    if DEVMODE:
        HUC = None
        for HUC_DIGITS in [8, 10, 12]:
            print("")
            print("--------{}--------".format(HUC_DIGITS))
            HUC, POINTS_ON_SURFACE = huc_id_and_sample(lat=38.4008283,
                                                       lon=-120.8286800,
                                                       huc_digits=HUC_DIGITS,
                                                       sample=True,
                                                       base_huc=HUC)
            print(HUC)
            # Export Sampling Points to CSV (DEV ONLY)
            # Find module path, ROOT folder, and SCRATCH folder
            MODULE_FOLDER = os.path.dirname(os.path.realpath(__file__))
            ROOT_FOLDER = os.path.split(MODULE_FOLDER)[0]
            SCRATCH_FOLDER = u'{}\\Scratch'.format(ROOT_FOLDER)
            ensure_dir(SCRATCH_FOLDER)
            with open("{}\\{}points_test.csv".format(SCRATCH_FOLDER, HUC), 'w') as CSV:
                CSV.write('Lat,Lon\n')
                for POINT in POINTS_ON_SURFACE:
                    CSV.write('{},{}\n'.format(POINT[0], POINT[1]))
                    print('{},{}'.format(POINT[0], POINT[1]))
            print("------------------")
            print("")
    

