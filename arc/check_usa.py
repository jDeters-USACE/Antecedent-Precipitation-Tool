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
    TEST = os.path.exists('{}\\Python Scripts'.format(ROOT))
    if TEST:
        sys.path.append('{}\\Python Scripts\\utilities'.format(ROOT))
    else:
        sys.path.append('{}\\arc\\utilities'.format(ROOT))
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
    usa_shapefile_path = '{}\\GIS\\us_shp\\cb_2018_us_nation_5m.shp'.format(ROOT)

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
