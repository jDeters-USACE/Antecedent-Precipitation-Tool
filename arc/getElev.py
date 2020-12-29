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

def get_json_multiple_ways(url):
    """Tries to pull JSON data from a URL using urllib3 first and then requests"""
    log = JLog.PrintLog()
    if 'https://nationalmap.gov/epqs' in url:
        base_url = 'https://nationalmap.gov/epqs'
    elif 'https://ned.usgs.gov/epqs' in url:
        base_url = 'https://ned.usgs.gov/epqs'
    # Common USGS Error Message
    temp_unavailable_message = 'The requested service is temporarily unavailable.  Please try later.'
    unavailable_error_count = 0
    # Try urllib3
    # Try Requests module
    try:
        log.print_status_message('Querying {}...'.format(base_url))
        content = requests.get(url, timeout=15)
        time.sleep(.5)
        while temp_unavailable_message in content.text:
            del content
            unavailable_error_count += 1
            log.Write('     USGS SERVER:  "{}"'.format(temp_unavailable_message))
            log.print_status_message('     Retrying query of {}...'.format(base_url))
            time.sleep(unavailable_error_count)
            content = requests.get(url)
            time.sleep(unavailable_error_count)
            if unavailable_error_count > 4:
                unavailable_error_count = 0
                break
        json_conversion = content.json()
        return json_conversion
    except Exception:
        requests_exception = traceback.format_exc()
    try:
        log.print_status_message('Querying {}...'.format(base_url))
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED')
        response = http.request('GET', url)
        time.sleep(1)
        string_data = str(response.data, 'utf-8')
        while temp_unavailable_message in string_data:
            del response
            unavailable_error_count += 1
            log.Write('     USGS SERVER:  "{}"'.format(temp_unavailable_message))
            log.print_status_message('     Retrying query of {}...'.format(base_url))
            time.sleep(unavailable_error_count)
            response = http.request('GET', url)
            sleep_duration = 3 + unavailable_error_count
            time.sleep(sleep_duration)
            string_data = str(response.data, 'utf-8')
            if unavailable_error_count > 4:
                unavailable_error_count = 0
                break
        json_conversion = json.loads(string_data)
        return json_conversion
    except Exception:
        L.Write('    ---Requests Exception Traceback---')
        L.Write(requests_exception)
        L.Write('    ----------------------------------')
        urllib3_exception = traceback.format_exc()
        L.Write('    ---urllib3 Exception Traceback---')
        L.Write(urllib3_exception)
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

def elevUSGS_nationalmap(lat, lon, units='Feet', batch=False):
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

def elevUSGS_ned(lat, lon, units='Feet', batch=False):
    url = u'https://ned.usgs.gov/epqs/pqs.php?x={}&y={}&units={}&output=json'.format(lon, lat, units)
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

def main(lat, lon, units='Feet', epqs_variant='nationalmap'):
    L.Wrap('Querying Elevation at Observation Point ({}, {})...'.format(lat, lon))
#    in_usa = checkUSA(lat, lon)
#    if in_usa is True:
#        L.Wrap('Point is within USA boundary. Using USGS Elevation Query Service...')
    if epqs_variant == 'nationalmap':
        elevation = elevUSGS_nationalmap(lat, lon)
    elif epqs_variant == 'ned':
        elevation = elevUSGS_ned(lat, lon)
    if elevation == "-1000000":
        L.Wrap('USGS Elevation Querry Failed. Using https://www.freemaptools.com/elevation-finder.htm...')
        elevation = selenium_operations.global_elev_query(lat, lon)
    L.Wrap('-------------------------------')
    L.Wrap('Elevation = {} {}'.format(elevation, units))
    L.Wrap('-------------------------------')
    return float(elevation)

def batch(list_of_coords, units='Feet', epqs_variant='nationalmap'):
    sampling_point_elevations = dict()
    L.print_section('Querying USGS Elevation Service for each Watershed Sampling Point')
    sp_num = 0
    for coords in list_of_coords:
        sp_num += 1
        lat = coords[0]
        lon = coords[1]
        if epqs_variant == 'nationalmap':
            elevation = elevUSGS_nationalmap(lat, lon, batch=True)
        elif epqs_variant == 'ned':
            elevation = elevUSGS_ned(lat, lon, batch=True)
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
    batch_list = [[38.5, -121.5],
                 [38.512024, -121.85663],
                 [38.571309, -121.466601],
                 [38.514189, -121.396986],
                 [38.305416, -121.752758],
                 [38.425778, -121.532817],
                 [38.631153, -121.749137],
                 [38.376917, -121.612664],
                 [38.335298, -122.04697],
                 [38.63407, -122.065706],
                 [38.142966, -121.730625],
                 [38.542088, -121.203454],
                 [38.060273, -121.741327],
                 [38.735047, -121.694238],
                 [38.57745, -121.620299],
                 [38.471649, -121.94944],
                 [38.562792, -122.004397],
                 [38.605449, -121.98951],
                 [38.193847, -121.668168],
                 [38.399478, -121.858778],
                 [38.591784, -121.524331],
                 [38.507899, -121.358888],
                 [38.599221, -121.821016],
                 [38.317145, -121.681206],
                 [38.514709, -121.22082],
                 [38.105685, -121.78534],
                 [38.61529, -121.592906],
                 [38.587815, -121.674077],
                 [38.334092, -122.0078],
                 [38.168111, -121.780984],
                 [38.467505, -121.902848],
                 [38.210155, -121.786728],
                 [38.367962, -122.003479],
                 [38.769371, -121.728745],
                 [38.341788, -121.532221],
                 [38.272567, -121.546393],
                 [38.404386, -121.595936],
                 [38.171484, -121.713082],
                 [38.06758, -121.686661],
                 [38.451716, -121.436812],
                 [38.593532, -121.759726],
                 [38.495494, -121.931338],
                 [38.50655, -121.766059],
                 [38.692543, -122.086156],
                 [38.412162, -121.67741],
                 [38.577833, -121.965081],
                 [38.414271, -121.920104],
                 [38.797826, -121.701433],
                 [38.668811, -121.691171],
                 [38.37065, -121.957751],
                 [38.441833, -121.332749],
                 [38.427668, -121.875828],
                 [38.35858, -121.667456],
                 [38.546716, -121.850837],
                 [38.662205, -121.869923],
                 [38.303392, -121.934311],
                 [38.24233, -121.557077],
                 [38.136003, -121.771312],
                 [38.44654, -121.699953],
                 [38.385869, -121.797751],
                 [38.092827, -121.740964],
                 [38.574348, -121.903483],
                 [38.611522, -122.122915],
                 [38.41825, -121.638275],
                 [38.55278, -121.346289],
                 [38.657731, -121.828199],
                 [38.54989, -121.435088],
                 [38.275138, -121.851317]]
    test_dict = batch(batch_list)

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