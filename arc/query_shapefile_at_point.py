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
##    query_shapefile_at_point.py   ##
##  ------------------------------- ##
##      Written by: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on: 2020-06-11    ##
##  ------------------------------- ##
######################################

# Originally sourced from
# https://stackoverflow.com/questions/7861196/check-if-a-geopoint-with-latitude-and-longitude-is-within-a-shapefile/13433127#13433127

# Import Standard Libraries
import os

# Import 3rd Party Libraries
import ogr
ogr.UseExceptions()

def check(lon, lat, shapefile, field_name):
    # Load shapefile driver
    ogr_shapefile_driver = ogr.GetDriverByName('ESRI Shapefile')
    # Get shapefile contents
    shapefile_contents = ogr_shapefile_driver.Open(shapefile, 0)
    # Get first layer in shapefile_contents
    shapefile_layer = shapefile_contents.GetLayer(0)
    # Get field index value for supplied field_name
    selected_field_index_value = shapefile_layer.GetLayerDefn().GetFieldIndex(field_name)

    #If the latitude/longitude we're going to use is not in the projection
    #of the shapefile, then we will get erroneous results.
    #The following assumes that the latitude longitude is in WGS84
    #This is identified by the number "4326", as in "EPSG:4326"
    #We will create a transformation between this and the shapefile's
    #project, whatever it may be
    geo_ref = shapefile_layer.GetSpatialRef()
    point_ref = ogr.osr.SpatialReference()
    point_ref.ImportFromEPSG(4326)
    ctran = ogr.osr.CoordinateTransformation(point_ref, geo_ref)

    #Transform incoming longitude/latitude to the shapefile's projection
    [lon, lat, z] = ctran.TransformPoint(lon, lat)

    #Create a point
    pt = ogr.Geometry(ogr.wkbPoint)
    pt.SetPoint_2D(0, lon, lat)

    #Set up a spatial filter such that the only features we see when we
    #loop through "shapefile_layer" are those which overlap the point defined above
    shapefile_layer.SetSpatialFilter(pt)

    #Loop through the overlapped features and display the field of interest
    for feat_in in shapefile_layer:
        feature_intersecting_point = feat_in.GetFieldAsString(selected_field_index_value)
        return feature_intersecting_point

#Take command-line input and do all this
#check(float(sys.argv[1]),float(sys.argv[2]))

if __name__ == '__main__':
    # Find module path
    MODULE_FOLDER = os.path.dirname(os.path.realpath(__file__))
    # Find ROOT folder
    ROOT_FOLDER = os.path.split(MODULE_FOLDER)[0]
    # Find clim_div folder
    CLIM_DIV_FOLDER = u'{}\\GIS\\climdiv'.format(ROOT_FOLDER)
    CLIM_DIV_SHAPEFILE = '{}\\GIS.OFFICIAL_CLIM_DIVISIONS.shp'.format(CLIM_DIV_FOLDER)
    FEATURE_ATTRIBUTE_TO_QUERY = "CLIMDIV"
    CLIMDIV = check(lat=36.5,
                    lon=-121.5,
                    shapefile=CLIM_DIV_SHAPEFILE,
                    field_name=FEATURE_ATTRIBUTE_TO_QUERY)
    print(CLIMDIV)
