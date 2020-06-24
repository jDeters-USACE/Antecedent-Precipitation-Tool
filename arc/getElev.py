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
##            getElev.py            ##
##  ------------------------------- ##
##     Written by: Jason Deters     ##
##  ------------------------------- ##
## Last Edited on:  11-Apr-2018     ##
##  ------------------------------- ##
######################################

# Import Standard Libraries
import time
import os
import sys
import traceback

# Import 3rd Party Libraries
import json
import urllib3
import requests
from bs4 import BeautifulSoup

# Find module path
MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
# Find ROOT folder
ROOT = os.path.split(MODULE_PATH)[0]

# Import Custom Libraries
try:
    from .utilities import JLog
    from .utilities import selenium_operations
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
    import selenium_operations

L = JLog.PrintLog()

def get_json_multiple_ways(url=None):
    """Tries to pull JSON data from a URL using urllib3 first and then requests"""
    # Try urllib3
    try:
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED')
        response = http.request('GET', url)
        time.sleep(3)
        string_data = str(response.data, 'utf-8')
        json_conversion = json.loads(string_data)
        return json_conversion
    except Exception:
        urllib3_exception = traceback.format_exc()
    # Try Requests module
    try:
        content = requests.get(url)
        time.sleep(3)
        json_conversion = content.json()
        return json_conversion
    except Exception:
        requests_exception = traceback.format_exc()
        L.Write('    ---urllib3 Exception Traceback---')
        L.Write(urllib3_exception)
        L.Write('    ----------------------------------')
        L.Write('    ---Requests Exception Traceback---')
        L.Write(requests_exception)
        L.Write('    ----------------------------------')


def checkUSA(lat, lon):
    """Checks if a given Lat/Long is within the US boundary (To decide which elev service to use)"""
    # http://en.wikipedia.org/wiki/Extreme_points_of_the_United_States#Westernmost
    top = 49.3457868 # north lat
    left = -124.7844079 # west long
    right = -66.9513812 # east long
    bottom = 24.7433195 # south lat

    if bottom <= float(lat) <= top and left <= float(lon) <= right:
        inUSA = True
    else:
        inUSA = False
    return inUSA

def elevUSGS(lat, lon, units='Feet', batch=False):
    url = u'https://nationalmap.gov/epqs/pqs.php?x={}&y={}&output=json&units={}'.format(lon, lat, units)
    # Pre-set Elevation to USGS Server's fail code
    elevation = "-1000000"
    # Get JSON format text from url Body
    if not batch:
        L.Wrap('Request URL: {}'.format(url))
    # Attempting to use standard requests style OR urllib2 module
    for x in range(3):
        seconds = ((x+1)*3)
        try:
            json_result = get_json_multiple_ways(url)
            service = json_result['USGS_Elevation_Point_Query_Service']
            query = service['Elevation_Query']
            elevation = query['Elevation']
            return elevation
        except Exception:
            try:
                del content
            except:
                pass
            if x < 2:
                L.Wrap('  Attempt {} failed, trying again in 1 second...'.format((x+1)))
                time.sleep(1)
            else:
                L.Wrap('  Attempt {} failed.'.format((x+1)))
    # Try Selenium Requests Method if Requests fails
    L.Wrap('---Urllib3 and Requests Modules Failed----')
    L.Wrap('Attempting to collect the data through web-browser automation...')
    instance = selenium_operations.getJSON(url)
    json_result = instance()
    # Switch to manual entry if web requests are not working
    service = json_result['USGS_Elevation_Point_Query_Service']
    query = service['Elevation_Query']
    elevation = query['Elevation']
    return elevation

def main(lat, lon, units='Feet'):
    L.Wrap('Querying Elevation at Observation Point ({}, {})...'.format(lat, lon))
#    in_usa = checkUSA(lat, lon)
#    if in_usa is True:
#        L.Wrap('Point is within USA boundary. Using USGS Elevation Query Service...')
    elevation = elevUSGS(lat, lon)
    if elevation == "-1000000":
        L.Wrap('USGS Elevation Querry Failed. Using https://www.freemaptools.com/elevation-finder.htm...')
        elevation = selenium_operations.global_elev_query(lat, lon)
#    else:
#        L.Wrap('USGS Elevation Querry Failed. Using https://www.freemaptools.com/elevation-finder.htm...')
#        elevation = selenium_operations.global_elev_query(lat, lon)
    L.Wrap('-------------------------------')
    L.Wrap('Elevation = {} {}'.format(elevation, units))
    L.Wrap('-------------------------------')
    return float(elevation)

def batch(list_of_coords, units='Feet'):
    sampling_point_elevations = dict()
    L.print_section('Querying USGS Elevation Service for each Watershed Sampling Point')
    sp_num = 0
    for coords in list_of_coords:
        sp_num += 1
        lat = coords[0]
        lon = coords[1]
        elevation = elevUSGS(lat, lon, batch=True)
        if elevation == "-1000000":
            L.Wrap('USGS Elevation Querry Failed. Using https://www.freemaptools.com/elevation-finder.htm...')
            elevation = selenium_operations.global_elev_query(lat, lon)
        L.Wrap('Watershed Sampling Point {} - ({}, {}) - Elevation = {} {}'.format(sp_num, lat, lon, elevation, units))
        dict_key = '{},{}'.format(lat, lon)
        sampling_point_elevations[dict_key] = elevation
    L.print_separator_line()
    return sampling_point_elevations


if __name__ == '__main__':
    # Test within USA Rectangular Boundary
    L.Wrap("Within USA Rectangle Test:")
    L.Wrap('--------------------------')
    elev = main(29.446176, -95.164569)

    # Test batch
    L.Wrap('Batch Test')
    batch_list = [[38.5, -121.5], [36.5, -121.5]]
    test_dict = batch(batch_list)
    print(test_dict['38.5,-121.5'])

#    # Test outside USA Rectangular Boundary
#    L.Wrap("")
#    L.Wrap("Outside USA Rectangle Test:")
#    L.Wrap('---------------------------')
#    elev = main(7, -121.5)
#
#    # Test within USA Rectangular Boundary, but outside USA ACTUAL Boundary
#    L.Wrap("")
#    L.Wrap("Inside USA Rectangle, but outside Actual USA Boundary Test:")
#    L.Wrap('-----------------------------------------------------------')
#    elev = main(27.748181, -103.632760)

#https://nationalmap.gov/epqs/pqs.php?x=-153.321123&y=65.055219&output=json&units=Feet