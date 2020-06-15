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
##     custom_watershed_query.py    ##
##  ------------------------------- ##
##      Copyright: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on: 2020-05-27    ##
##  ------------------------------- ##
######################################


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
    from .utilities import JLog
except Exception:
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
    horizontal_units = findHorizontalUnits(str(geo_ref))
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
    if not horizontal_units.lower() in supported_units:
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
    num_points = huc_square_miles / 20
    num_points = int(round(num_points, 0))    
    sampling_point_spacing_miles = round((huc_square_miles / 633.145), 2)
    if sampling_point_spacing_miles < 1:
        sampling_point_spacing_miles = 1
    if horizontal_units.lower() in ['meter', 'meters']:
        sampling_point_spacing = sampling_point_spacing_miles * 1609.34 # 1609.34 Meters = 1 Mi
    elif horizontal_units.lower() in ['foot', 'feet', 'us feet', 'us foot', 'foot_us', 'us_foot']:
        sampling_point_spacing = sampling_point_spacing_miles * 5280 # 5280 Feet = 1 Mi

    #-----------------------RANDOM SAMPLING POINT GENERATOR SECTION---------------------#

    # Create Random Sampling Points at the selected spacing (If selected)
    # Calculate the Envelope (bounding box) of the selected HUC
    log.print_section('Random Sampling Point Generation Section')
    log.Wrap('Sampling Parameters:')
    log.Wrap(' -{} Points, including user-specified coordinates'.format(num_points))
    log.Wrap(' -All points fall Within the Custom Watershed provided')
    log.Wrap(' -Each point at least {} mile(s) from all other sampling points'.format(sampling_point_spacing_miles))
    log.Wrap('Generating sampling points...')
    x_min, x_max, y_min, y_max = selected_feature_geometry.GetEnvelope()
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
                num_points -= 1
                previously_selected_points.append(test_pt)
                [wgs_lon, wgs_lat, z] = transform_albers_to_wgs.TransformPoint(test_x, test_y)
                wgs_lat = round(wgs_lat, 6)
                wgs_lon = round(wgs_lon, 6)
                coordinates_within_polygon.append([wgs_lat, wgs_lon])
    log.Wrap('All {} sampling points generated successfully'.format(len(coordinates_within_polygon)))
    log.print_separator_line()
    return coordinates_within_polygon, huc_square_miles




if __name__ == '__main__':
    import time
    start_time = time.clock()
    sampling_points, huc_square_miles = shapefile_sample(lat=38.325033,
                                                         lon=-121.356081,
                                                         shapefile=r"c:\Users\L2RCSJ9D\Desktop\delete\~anteTest\Cosumnes_Drainage_Area2.shp")
    print(huc_square_miles)
    for point in sampling_points:
        print(point)
#    print(huc)
#    for point in sampling_points:
#        print(point)
    duration = time.clock() - start_time
    print('DevOnly: Processing took {} seconds'.format(duration))

    

