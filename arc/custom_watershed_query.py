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
##     custom_watershed_query.py    ##
##  ------------------------------- ##
##      Copyright: Jason Deters     ##
##      Edited by: Joseph Gutenson  ##
##  ------------------------------- ##
##    Last Edited on: 2021-12-16    ##
##  ------------------------------- ##
######################################


# Import Standard Libraries
from datetime import datetime
import os
import sys
import random

# Import 3rd Party Libraries
from osgeo import ogr
ogr.UseExceptions()

# Import Custom Libraries
MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.split(MODULE_PATH)[0]
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

def shapefile_sample(lat, lon, shapefile):
    """
    Identify the HUC of a given huc_digits in which the supplied coordinates lie.
    If selected, generate random sampling points (# and minimum spacing determined by HUC Digits)
    """
    # Shapefile Query Adapted from
    # https://stackoverflow.com/questions/7861196/check-if-a-geopoint-with-latitude-and-longitude-is-within-a-shapefile/13433127#13433127
    log = JLog.PrintLog(Delete=False)
    lat = float(lat)
    lon = float(lon)
    log.Wrap("Analyzing Custom Watershed Shapefile")
    log.Wrap('Shapefile Path = {}'.format(shapefile))
    # Find module path
    module_folder = os.path.dirname(os.path.realpath(__file__))
    # Find ROOT folder
    root_folder = os.path.split(module_folder)[0]

    # Create list to store exploded points
    previously_selected_points = []
    coordinates_within_polygon = []

    # Open shapefile
    log.Wrap(' -Reading Shapefile...')
    ds_in = ogr.Open(shapefile)    #Get the contents of the shape file
    lyr_in = ds_in.GetLayer()    #Get the shape file's first layer

    #If the latitude/longitude we're going to use is not in the projection
    #of the shapefile, then we will get erroneous results.
    #The following assumes that the latitude longitude is in WGS84
    #This is identified by the number "4326", as in "EPSG:4326"
    #We will create a transformation between this and the shapefile's
    #project, whatever it may be
    geo_ref = lyr_in.GetSpatialRef()
    # Parse horizontal units from CS String
    original_horizontal_units = findHorizontalUnits(str(geo_ref))
    point_ref = ogr.osr.SpatialReference()
    point_ref.ImportFromEPSG(4326)
    ctran = ogr.osr.CoordinateTransformation(point_ref, geo_ref)
    rtran = ogr.osr.CoordinateTransformation(geo_ref, point_ref)

    # North_America_Albers_Equal_Area_Conic
    albers_ref = ogr.osr.SpatialReference()
    albers_ref.ImportFromEPSG(102008)
    transform_source_to_albers = ogr.osr.CoordinateTransformation(geo_ref, albers_ref)
    transform_albers_to_wgs = ogr.osr.CoordinateTransformation(albers_ref, point_ref)

    #Transform incoming longitude/latitude to the shapefile's projection
    [t_lon, t_lat, z] = ctran.TransformPoint(lon, lat)

    # Create a point
    pt = ogr.Geometry(ogr.wkbPoint)
    pt.SetPoint_2D(0, t_lon, t_lat)

    # Set up a spatial filter such that the only features we see when we
    # loop through "lyr_in" are those which overlap the point defined above
    log.Wrap(' -Filtering HUC8 features by spatial overlap with selected coordinates...')
    lyr_in.SetSpatialFilter(pt)
    # Loop through the overlapped features and display the field of interest
    for feat_in in lyr_in:
        selected_feature = feat_in
        selected_feature_geometry = selected_feature.geometry()
        break

    # Get Area of selected HUC
    supported_units = ['meter', 'meters' 'foot', 'feet', 'us feet', 'us foot', 'us_foot', 'foot_us']
    if not original_horizontal_units.lower() in supported_units:
        # Transform geometry to Albers
        selected_feature_geometry.Transform(transform_source_to_albers)
        # Update horizontal units
        geo_ref = selected_feature_geometry.GetSpatialReference()
        horizontal_units = findHorizontalUnits(str(geo_ref))
    if horizontal_units.lower() in supported_units:
        # Calculate Area
        selected_huc_area = selected_feature_geometry.GetArea()
        # Convert Area to Square Miles
        if horizontal_units.lower() in ['meter', 'meters']:
            huc_square_miles = selected_huc_area / 2590000
        elif horizontal_units.lower() in ['foot', 'feet', 'us feet', 'us foot', 'foot_us', 'us_foot']:
            huc_square_miles = selected_huc_area / 27880000
        huc_square_miles = round(huc_square_miles, 2)

    # Determine Sampling Distance and point spacing
    sampling_point_spacing_miles = round((huc_square_miles / 633.145), 2)
    sampling_point_spacing_miles = 3.75
    if sampling_point_spacing_miles < 1:
        sampling_point_spacing_miles = 1
    if horizontal_units.lower() in ['meter', 'meters']:
        sampling_point_spacing = sampling_point_spacing_miles * 1609.34 # 1609.34 Meters = 1 Mi
    elif horizontal_units.lower() in ['foot', 'feet', 'us feet', 'us foot', 'foot_us', 'us_foot']:
        sampling_point_spacing = sampling_point_spacing_miles * 5280 # 5280 Feet = 1 Mi

    #-----------------------RANDOM SAMPLING POINT GENERATOR SECTION---------------------#

    # Calculate the Envelope (bounding box) of the selected HUC
    x_min, x_max, y_min, y_max = selected_feature_geometry.GetEnvelope()

    # Announce Sampling Points
    log.print_section('Random Sampling Point Generation Section')
    log.Wrap('Sampling Protocol:')
    log.Wrap(' -Latitudes and Longitudes will be randomly generated watershed polygon extremes:')
    log.Wrap('   -Custom Watershed Coordinate Extremes (Converted to Meters for testing):')
    log.Wrap('      -Maximum Latitude:  {}'.format(y_max))
    log.Wrap('      -Minimum Latitude:  {}'.format(y_min))
    log.Wrap('      -Maximum Longitude: {}'.format(x_max))
    log.Wrap('      -MInimum Longitude: {}'.format(x_min))
    log.Wrap(' -An OGR point geometry will be created to test each random Latitude and Longitude.')
    log.Wrap('   -The point must fall Within the Custom Watershed provided')
    log.Wrap('   -The point must also be at least {} mile(s) from any previously selected sampling points.'.format(sampling_point_spacing_miles))
    log.Wrap(' -If both criteria are met, the point will be added to the list of sampling points.')
    log.Wrap(' -When 3000 consecutive random test points fail these tests, the sampling procedure will be complete.')

    # Announce protocol commencement
    log.Wrap('')
    log.Wrap('Generating potential sampling points and testing the above conditions...')

    # Add initially selected coordinates as the first sampling point
    previously_selected_points.append(pt)
    coordinates_within_polygon.append([lat, lon])
    points_selected = 1 # Starting with observation point
    points_tested = 1 # Starting with observation point
    points_tested_since_last_success = 0

    # Setting this to use existing structure since it is now based on 1500-attempt timeout
    num_points = 999
    num_points -= 1 # Subtracting for adding observation point

    while num_points > 0:
        # Create a random X coordinate within the Envelope
        test_x = random.uniform(x_min, x_max)
        # Create a random Y coordinate within the Envelope
        test_y = random.uniform(y_min, y_max)
        points_tested += 1
        points_tested_since_last_success += 1
        test_x_round = round(test_x, 6)
        test_y_round = round(test_y, 6)
        if points_tested_since_last_success > 3000:
            if num_points < 997:
                log.Wrap('Sampling complete (3000 consecutive points tested since the last suitable one was found).')
                break
            else:
                log.Wrap('  {} points selected of {} test candidates generated.'.format(points_selected, points_tested))
                points_tested_since_last_success = 0
                log.Wrap('3000 points tested since the last suitable one was found.  Lowering minimum spacing by 0.5 mile.')
                sampling_point_spacing_miles = round((sampling_point_spacing_miles - 0.5), 2)
                if horizontal_units.lower() in ['meter', 'meters']:
                    sampling_point_spacing = sampling_point_spacing_miles * 1609.34 # 1609.34 Meters = 1 Mi
                elif horizontal_units.lower() in ['foot', 'feet', 'us feet', 'us foot', 'foot_us', 'us_foot']:
                    sampling_point_spacing = sampling_point_spacing_miles * 5280 # 5280 Feet = 1 Mi
                log.Wrap(' -Now each point must be at least {} miles(s) from all other sampling points'.format(sampling_point_spacing_miles))
        log.print_status_message('  {} points selected of {} test candidates generated. Testing ({}, {})'.format(points_selected, points_tested, test_y_round, test_x_round))
        # Create a blank Test Point (OGR Geometry of the type ogr.wkbPoint)
        test_pt = ogr.Geometry(ogr.wkbPoint)
        # Set the Test Point to the random X and Y coordinates
        test_pt.SetPoint_2D(0, test_x, test_y)
        # Test whether the within-envolope point is actually within the polygon
        inside = selected_feature_geometry.Contains(test_pt)
        if inside:
            properly_spaced = True
            # Test against every previously selected point for optimal spacing
            for previous_point in previously_selected_points:
                distance = test_pt.Distance(previous_point)
                if distance < sampling_point_spacing:
                    properly_spaced = False
            # Test passed, add to all lists and reduce num_points needed
            if properly_spaced:
                points_tested_since_last_success = 0
                num_points -= 1
                points_selected += 1
                previously_selected_points.append(test_pt)
                if not original_horizontal_units.lower() in supported_units:
                    [wgs_lon, wgs_lat, z] = transform_albers_to_wgs.TransformPoint(test_x, test_y)
                else:
                    [wgs_lon, wgs_lat, z] = rtran.TransformPoint(test_x, test_y)
                wgs_lat = round(wgs_lat, 6)
                wgs_lon = round(wgs_lon, 6)
                coordinates_within_polygon.append([wgs_lat, wgs_lon])
    log.Wrap('{} sampling points selected from {} randomly generated candidates'.format(points_selected, points_tested))
    log.print_separator_line()
    return coordinates_within_polygon, huc_square_miles




if __name__ == '__main__':
    start_time = datetime.now()
    SCRATCH_FOLDER = os.path.join(ROOT, 'Scratch')
    WATERSHED_FOLDER = os.path.join(SCRATCH_FOLDER, 'Cosumnes River Watershed (ESRI)')
    SHAPEFILE = os.path.join(WATERSHED_FOLDER, 'Cosumnes_River_Watershed.shp')
    sampling_points, huc_square_miles = shapefile_sample(lat=38.3315574,
                                                         lon=-121.3622894,
                                                         shapefile=SHAPEFILE)
    print(huc_square_miles)
    for point in sampling_points:
        print(point)
#    print(huc)
#    for point in sampling_points:
#        print(point)
    duration = datetime.now() - start_time
    print('DevOnly: Processing took {} seconds'.format(duration))
