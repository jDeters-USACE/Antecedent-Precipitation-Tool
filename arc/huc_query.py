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
##           huc_query.py           ##
##  ------------------------------- ##
##      Writen by: Jason Deters     ##
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
from osgeo import ogr
ogr.UseExceptions()

# Import Custom Libraries
try:
    MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
except:
    MODULE_PATH = os.getcwd()
ROOT = os.path.split(MODULE_PATH)[0]

try:
    from . import get_files
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
    import get_files


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
    try:
        module_folder = os.path.dirname(os.path.realpath(__file__))
    except:
        module_folder = os.getcwd()
    # Find ROOT folder
    root_folder = os.path.split(module_folder)[0]
    # Find WBD folder
    gis_folder = os.path.join(root_folder, 'GIS')
    wbd_folder = os.path.join(gis_folder, 'WBD')
    # Set HUC_Scale-Specific Values
    if huc_digits == 2:
        # Find Selected WBD shapefile
        shapefile = os.path.join(wbd_folder, 'HUC2.shp')
        field_name = "HUC2"
    elif huc_digits == 8:
        # Calc Shapefile and Field
        base_huc_folder = os.path.join(wbd_folder, str(base_huc)[:2])
        shape_folder = os.path.join(base_huc_folder, "Shape")
        shapefile = os.path.join(shape_folder, 'WBDHU{}.shp'.format(huc_digits))
        field_name = "HUC{}".format(huc_digits)
    elif huc_digits == 10:
        # Calc Shapefile and Field
        base_huc_folder = os.path.join(wbd_folder, str(base_huc)[:2])
        shape_folder = os.path.join(base_huc_folder, "Shape")
        shapefile = os.path.join(shape_folder, 'WBDHU{}.shp'.format(huc_digits))
        field_name = "HUC{}".format(huc_digits)
        # Get attribute filter
        attribute_filter = "HUC10 LIKE '{}%'".format(base_huc)
    elif huc_digits == 12:
        # Find Selected WBD_Shapefile and 
        base_huc_folder = os.path.join(wbd_folder, str(base_huc)[:2])
        shape_folder = os.path.join(base_huc_folder, "Shape")
        shapefile = os.path.join(shape_folder, 'WBDHU{}.shp'.format(huc_digits))
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

    print(shapefile)
    print(ds_in)

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
#    geo_ref.SetAxisMappingStrategy(ogr.osr.OAMS_TRADITIONAL_GIS_ORDER)

    # Parse horizontal units from CS String
    horizontal_units = findHorizontalUnits(str(geo_ref))
    point_ref = ogr.osr.SpatialReference()
    
    # Following line added to address GDAL 3.0 changes
    point_ref.SetAxisMappingStrategy(ogr.osr.OAMS_TRADITIONAL_GIS_ORDER)

    point_ref.ImportFromEPSG(4326)
    ctran = ogr.osr.CoordinateTransformation(point_ref, geo_ref)
    rtran = ogr.osr.CoordinateTransformation(geo_ref, point_ref)

    # North_America_Albers_Equal_Area_Conic
    albers_ref = ogr.osr.SpatialReference()
    albers_ref.SetFromUserInput("ESRI:102008")
    transform_source_to_albers = ogr.osr.CoordinateTransformation(geo_ref, albers_ref)
    transform_albers_to_WGS = ogr.osr.CoordinateTransformation(albers_ref, point_ref)

    #Transform incoming longitude/latitude to the shapefile's projection
    [t_lon, t_lat, z] = ctran.TransformPoint(lat, lon)

    # Create a point
    pt = ogr.Geometry(ogr.wkbPoint)
    #pt.SetPoint_2D(0, t_lon, t_lat)

    # ogr seems to have changes lat/lon ordering
    pt.SetPoint_2D(0, t_lat, t_lon)

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
    supported_units = ['meter', 'meters', 'metre', 'foot', 'feet', 'us feet', 'us foot', 'us_foot', 'foot_us']
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
        if horizontal_units.lower() in ['meter', 'meters', 'metre']:
            huc_square_miles = selected_huc_area / 2590000
        elif horizontal_units.lower() in ['foot', 'feet', 'us feet', 'us foot', 'foot_us', 'us_foot']:
            huc_square_miles = selected_huc_area / 27880000
        huc_square_miles = round(huc_square_miles, 2)

    # Determine Sampling Distance and point spacing
#    if huc_square_miles < 5:
#        sampling_point_spacing_miles = 0.5
#    elif huc_square_miles < 50:
#        sampling_point_spacing_miles = 1
#    elif huc_square_miles < 100:
#        sampling_point_spacing_miles = 1.5
#    elif huc_square_miles < 200:
#        sampling_point_spacing_miles = 2
#    elif huc_square_miles < 500:
#        sampling_point_spacing_miles = 2.5
#    else:
#        sampling_point_spacing_miles = 2.5 + (huc_square_miles / 1000)
    sampling_point_spacing_miles = 3.75
    # Convert SPSM to SPS Linear Unit
    if horizontal_units.lower() in ['meter', 'meters', 'metre']:
        sampling_point_spacing = sampling_point_spacing_miles * 1609.34 # 1609.34 Meters = 1 Mi
    elif horizontal_units.lower() in ['foot', 'feet', 'us feet', 'us foot', 'foot_us', 'us_foot']:
        sampling_point_spacing = sampling_point_spacing_miles * 5280 # 5280 Feet = 1 Mi

    # Get the HUC Value of the selected watershed
    huc_string = selected_huc.GetFieldAsString(idx_reg)
    log.Wrap(' {}: {}'.format(field_name, huc_string))
    log.Wrap('Area: {} square miles'.format(huc_square_miles))
    log.Wrap('')

    #-----------------------RANDOM SAMPLING POINT GENERATOR SECTION---------------------#

    # Create Random Sampling Points at the selected spacing (If selected)
    if sample is True:
        # Calculate the Envelope (bounding box) of the selected HUC
        x_min, x_max, y_min, y_max = selected_huc_geom.GetEnvelope()

        # Announce Sampling Points
        log.print_section('Random Sampling Point Generation Section')
        log.Wrap('Sampling Protocol:')
        log.Wrap(' -Latitudes and Longitudes will be randomly generated watershed polygon extremes:')
        log.Wrap('    HUC{} ({}) Coordinate Extremes (Converted to Meters for testing):'.format(huc_digits, huc_string))
        log.Wrap('    Maximum Latitude:  {}'.format(y_max))
        log.Wrap('    Minimum Latitude:  {}'.format(y_min))
        log.Wrap('    Maximum Longitude: {}'.format(x_max))
        log.Wrap('    MInimum Longitude: {}'.format(x_min))
        log.Wrap(' -A point feature will be created for each random Latitude and Longitude.')
        log.Wrap(' -The point will be tested to see if it falls within the HUC{} ({})'.format(huc_digits, huc_string))
        log.Wrap(' -The point will be must also be at least {} mile(s) from any previously selected sampling points.'.format(sampling_point_spacing_miles))
        log.Wrap(' -If all criteria are met, the point will be added to the list of sampling points.')
        log.Wrap(' -When 1500 consecutive random test points fail these tests, the sampling procedure will be complete.')

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

        while num_points > 0:
            # Create a random X coordinate within the Envelope
            test_x = random.uniform(x_min, x_max)
            # Create a random Y coordinate within the Envelope
            test_y = random.uniform(y_min, y_max)
            points_tested += 1
            points_tested_since_last_success += 1
            test_x_round = round(test_x, 6)
            test_y_round = round(test_y, 6)
            if points_tested_since_last_success > 1500:
                if num_points < 998:
                    log.Wrap('Sampling complete (1500 consecutive points tested since the last suitable one was found. Sampling complete).')
                    break
                else:
                    log.Wrap('  {} points selected of {} test candidates generated.'.format(points_selected, points_tested))
                    points_tested_since_last_success = 0
                    log.Wrap('1500 points tested since the last suitable one was found.  Lowering minimum spacing by 0.5 mile.')
                    sampling_point_spacing_miles = round((sampling_point_spacing_miles - 0.5), 2)
                    if horizontal_units.lower() in ['meter', 'meters', 'metre']:
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
                    points_tested_since_last_success = 0
                    num_points -= 1
                    points_selected += 1
                    previously_selected_points.append(test_pt)
                    [wgs_lon, wgs_lat, z] = transform_albers_to_WGS.TransformPoint(test_x, test_y)
                    wgs_lat = round(wgs_lat, 6)
                    wgs_lon = round(wgs_lon, 6)
                    coordinates_within_polygon.append([wgs_lat, wgs_lon])
        log.Wrap('{} sampling points selected from {} randomly generated candidates'.format(points_selected, points_tested))
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
    try:
        module_folder = os.path.dirname(os.path.realpath(__file__))
    except:
        module_folder = os.getcwd()
    root_folder = os.path.split(module_folder)[0]
    gis_folder = os.path.join(root_folder, 'GIS')
    wbd_folder = os.path.join(gis_folder, 'WBD')
    local_file_path = os.path.join(wbd_folder, 'WBD_{}_HU2_Shape.zip'.format(huc2))
    extract_path = os.path.join(wbd_folder, huc2)
    # Download & Extract
    get_files.ensure_file_exists(file_url=file_url,
                                 local_file_path=local_file_path,
                                 extract_path=extract_path)



if __name__ == '__main__':
    from datetime import datetime
    start_time = datetime.now()
#    huc, sampling_points, huc_square_miles = id_and_sample(lat=40.5454,
#                                                           lon=-110.239,
#                                                           watershed_scale="HUC8")
#    huc, sampling_points, huc_square_miles = id_and_sample(lat=40.5454,
#                                                           lon=-110.239,
#                                                           watershed_scale="HUC10")
#    huc, sampling_points, huc_square_miles = id_and_sample(lat=40.5454,
#                                                           lon=-110.239,
#                                                           watershed_scale="HUC12")
#    huc, sampling_points, huc_square_miles = id_and_sample(lat=40.4,
#                                                           lon=-80.4,
#                                                           watershed_scale="HUC8")
#    huc, sampling_points, huc_square_miles = id_and_sample(lat=40.4,
#                                                           lon=-80.4,
#                                                           watershed_scale="HUC10")
#    huc, sampling_points, huc_square_miles = id_and_sample(lat=40.4,
#                                                           lon=-80.4,
#                                                           watershed_scale="HUC12")
#    huc, sampling_points, huc_square_miles = id_and_sample(lat=38.4008283,
#                                                           lon=-120.8286800,
#                                                           watershed_scale="HUC8")
#    huc, sampling_points, huc_square_miles = id_and_sample(lat=38.4008283,
#                                                           lon=-120.8286800,
#                                                           watershed_scale="HUC10")
#    huc, sampling_points, huc_square_miles = id_and_sample(lat=38.4008283,
#                                                           lon=-120.8286800,
#                                                           watershed_scale="HUC12")
#    # Print Output Values for verification
#    print('HUC: '.format(huc))
#    print('Square miles: {}'.format(huc_square_miles))
#    print('Sampling Points:')
#    for point in sampling_points:
#        print(' {}'.format(point))
#    duration = datetime.now() - start_time
#    print('Processing took {} seconds'.format(duration))



    huc = None
    for HUC_DIGITS in ["HUC8", "HUC10", "HUC12"]:
        print("")
        print("--------{}--------".format(HUC_DIGITS))
        huc, sampling_points, huc_square_miles = id_and_sample(lat=42.9169149,
                                                               lon=-81.7317756,
                                                               watershed_scale=HUC_DIGITS)
#        huc, sampling_points, huc_square_miles = id_and_sample(lat=38.4008283,
#                                                               lon=-120.8286800,
#                                                               watershed_scale=HUC_DIGITS)
#        huc, sampling_points, huc_square_miles = id_and_sample(lat=38.4008283,
#                                                               lon=-120.8286800,
#                                                               watershed_scale=HUC_DIGITS)
#        huc, sampling_points, huc_square_miles = id_and_sample(lat=38.4008283,
#                                                               lon=-120.8286800,
#                                                               watershed_scale=HUC_DIGITS)
        print(huc)
        # Export Sampling Points to CSV (DEV ONLY)
        # Find module path, ROOT folder, and SCRATCH folder
        try:
            MODULE_FOLDER = os.path.dirname(os.path.realpath(__file__))
        except:
            MODULE_FOLDER = os.getcwd()
        ROOT_FOLDER = os.path.split(MODULE_FOLDER)[0]
        SCRATCH_FOLDER = os.path.join(ROOT_FOLDER, 'Scratch')
        ensure_dir(SCRATCH_FOLDER)
        scratch_csv = os.path.join(SCRATCH_FOLDER, '{}_points_test.csv'.format(huc))
        with open(scratch_csv, 'w') as CSV:
            CSV.write('Lat,Lon\n')
            for POINT in sampling_points:
                CSV.write('{},{}\n'.format(POINT[0], POINT[1]))
                print('{},{}'.format(POINT[0], POINT[1]))
        print("------------------")
        print("")
    

