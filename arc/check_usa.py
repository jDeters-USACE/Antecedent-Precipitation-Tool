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
##          check_usa.py            ##
##  ------------------------------- ##
##     Copyright: Jason Deters      ##
##  ------------------------------- ##
##    Last Edited on: 2020-05-27    ##
##  ------------------------------- ##
######################################

"""Script facilitates testing a point against a shapefile of the USA boundary"""

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


def main(lat, lon):
    """Tests latitude and longitude against a shapefile of the USA boundary"""
    lat = float(lat)
    lon = float(lon)
    in_usa = False
    # Find module path
    module_folder = os.path.dirname(os.path.realpath(__file__))
    # Find ROOT folder
    root_folder = os.path.split(module_folder)[0]
    # Find USA Boundary Shapefile
    gis_folder = os.path.join(root_folder, 'GIS')
    usa_shapefile_folder = os.path.join(gis_folder, 'us_shp')
    usa_shapefile_path = os.path.join(usa_shapefile_folder, 'cb_2018_us_nation_5m.shp')

    # Get the contents of the USA Boundary Shapefile
    ds_in = ogr.Open(usa_shapefile_path)
    # Get the shapefile's first layer
    lyr_in = ds_in.GetLayer()

    #If the latitude/longitude we're going to use is not in the projection
    #of the shapefile, then we will get erroneous results.
    #The following assumes that the latitude longitude is in WGS84
    #This is identified by the number "4326", as in "EPSG:4326"
    #We will create a transformation between this and the shapefile's
    #project, whatever it may be
    geo_ref = lyr_in.GetSpatialRef()
    point_ref = ogr.osr.SpatialReference()
    point_ref.ImportFromEPSG(4326)
    ctran = ogr.osr.CoordinateTransformation(point_ref, geo_ref)
    rtran = ogr.osr.CoordinateTransformation(geo_ref, point_ref)

    #Transform incoming longitude/latitude to the shapefile's projection
    [t_lon, t_lat, z] = ctran.TransformPoint(lon, lat)

    # Create a point
    pt = ogr.Geometry(ogr.wkbPoint)
    pt.SetPoint_2D(0, t_lon, t_lat)

    # Check if point is within boundary
    for feat_in in lyr_in:
        feat_in_geom = feat_in.geometry()
        contains_point = feat_in_geom.Contains(pt)
        if contains_point:
            in_usa = True
            return in_usa
    
    # Return result if not caught above
    return in_usa 


if __name__ == '__main__':
    # CA
    LAT = 38.544418
    LON = -120.812989
    print("California")
    main(lat=LAT, lon=LON)
    # AK
    LAT = 67.261448
    LON = -153.100011
    print('Alaska')
    main(lat=LAT, lon=LON)
    # HUC12 Test
    LAT = 38.4008283
    LON = -120.8286800
    print('HUC Sample Point')
    main(lat=LAT, lon=LON)
