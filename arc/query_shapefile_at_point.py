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
from osgeo import ogr
ogr.UseExceptions()

def check(lat, lon, shapefile, field_name):
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

    # Following line added to address GDAL 3.0 changes
    point_ref.SetAxisMappingStrategy(ogr.osr.OAMS_TRADITIONAL_GIS_ORDER)
    
    point_ref.ImportFromEPSG(4326)
    ctran = ogr.osr.CoordinateTransformation(point_ref, geo_ref)

    #Transform incoming longitude/latitude to the shapefile's projection
    [lon, lat, z] = ctran.TransformPoint(lat, lon)

    #Create a point
    pt = ogr.Geometry(ogr.wkbPoint)
    #pt.SetPoint_2D(0, lon, lat)

    # ogr seems to have changes lat/lon ordering
    pt.SetPoint_2D(0, lat, lon)

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
    GIS_FOLDER = os.path.join(ROOT_FOLDER, 'GIS')
    CLIM_DIV_FOLDER = os.path.join(GIS_FOLDER, 'climdiv')
    CLIM_DIV_SHAPEFILE = os.path.join(CLIM_DIV_FOLDER, 'GIS.OFFICIAL_CLIM_DIVISIONS.shp')
    FEATURE_ATTRIBUTE_TO_QUERY = "CLIMDIV"
    CLIMDIV = check(lat=36.5,
                    lon=-121.5,
                    shapefile=CLIM_DIV_SHAPEFILE,
                    field_name=FEATURE_ATTRIBUTE_TO_QUERY)
    print(CLIMDIV)
