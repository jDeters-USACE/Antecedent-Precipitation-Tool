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
##          get_items.py            ##
##  ------------------------------- ##
##     Written by: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on: 2020-06-11    ##
##  ------------------------------- ##
######################################

# Import Standard Libraries
import os
import sys
import requests
import time
import zipfile

# Find module path
MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
# Find ROOT folder
ROOT = os.path.split(MODULE_PATH)[0]

# Import Custom Libraries
try:
    # Frozen Application Method
    from .utilities import JLog
except Exception:
    # Development Environment Method
    TEST = os.path.exists('{}\\Python Scripts'.format(ROOT))
    if TEST:
        sys.path.append('{}\\Python Scripts\\utilities'.format(ROOT))
    else:
        sys.path.append('{}\\arc\\utilities'.format(ROOT))
    import JLog

def check_local_version(version_local_path):
    """Checks local version number"""
    log = JLog.PrintLog()
    local_version = 0
    # Query ProcDate
    with open(version_local_path, 'r') as version_file:
        for line in version_file:
            local_version = float(line)
            break
    return(local_version)

def check_web_version(version_url):
    """Uses requests to check the first line of a text file at a URL"""
    response = requests.get(version_url)
    time.sleep(.1)
    web_version = float(response.text)
    return web_version

def extract_to_folder(zip_file, output_folder, pwd=None):
#    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
#        if pwd is None:
#            zip_ref.extractall(output_folder)
#        else:
#            zip_ref.extractall(output_folder, pwd=pwd.encode())
    with zipfile.ZipFile(zip_file) as zip:
        for zip_info in zip.infolist():
            if pwd is None:
                try:
                    zip.extract(zip_info, output_folder)
                except Exception:
                    pass
            else:
                try:
                    zip.extract(zip_info, output_folder, pwd=pwd.encode())
                except Exception:
                    pass


def sizeof_fmt(num, suffix='B'):
    for unit in [' ', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "{:6.2f} {}{}".format(num, unit, suffix)
        num /= 1024.0
    return "{:6.2f} {}{}".format(num, 'Y', suffix)


def ensure_file_exists(file_url, local_file_path, local_check_file=None,
                       version_url=None, version_local_path=None, minimum_size=None,
                       extract_path=None, extract_pwd=None):
    """Checks for file and version, downloads if necessary"""
    download = False
    local_version = 0
    log = JLog.PrintLog()
    download_dir, file_name = os.path.split(local_file_path)
    # Check for local file
    log.Wrap('  Checking for {}...'.format(file_name))
    local_file_exists = os.path.exists(local_file_path)
    if not local_file_exists:
        log.Wrap('   File not found.')
        download = True
    else:
        log.Wrap('    File located.')
        if minimum_size is not None:
            log.Wrap('  Testing local file...')
            local_file_size = os.path.getsize(local_file_path)
            if local_file_size < minimum_size:
                log.Wrap('    Local file corrupt. Deleting...')
                os.remove(local_file_path)
                download = True
            else:
                log.Wrap('    Passed')
    # Check Web Version
    if version_url is not None:
        version_dir, version_name = os.path.split(version_local_path)
        log.Wrap('  Checking {} web version...'.format(version_name))
        web_version = check_web_version(version_url)
        log.Wrap('    Web version = {}'.format(web_version))
        # If Local File exists Check Local Version
        version_local_file_exists = os.path.exists(version_local_path)
        if version_local_file_exists:
            log.Wrap('  Checking {} local version...'.format(version_name))
            local_version = check_local_version(version_local_path)
            log.Wrap('    Local version = {}'.format(local_version))
        if download is False:
            # Compare local and web versions
            if web_version > local_version:
                log.Wrap('  Newer version available.')
                # If web newer, delete local and set download to True
                os.remove(local_file_path)
                download = True
    if download is True:
        # Ensure download directory exists
        try:
            os.makedirs(download_dir)
        except Exception:
            pass
        dl_start = time.clock()
        # Streaming with requests module
        num_bytes = 0
        count = 0
        with requests.get(file_url, stream=True) as r:
            r.raise_for_status()
            with open(local_file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        num_bytes += 8192
                        count += 1
                        if count > 25:
                            formatted_bytes = sizeof_fmt(num_bytes)
                            log.print_status_message('    Downloading file... ({})'.format(formatted_bytes))
                            count = 0
        formatted_bytes = sizeof_fmt(num_bytes)
        log.Wrap('    File Downloaded ({})'.format(formatted_bytes))
        sys.stdout.flush()
        time.sleep(.1)
        # Extract compressed package if selected
        if extract_path is None:
            extracted = ''
        else:
            extracted = 'and Extracting '
            log.Wrap('    Extracting package to target directory...')
            extract_to_folder(zip_file=local_file_path,
                              output_folder=extract_path,
                              pwd=extract_pwd)
            log.Wrap('     Extraction complete. Deleting zip file...')
            # Remove zip file after extraction
            os.remove(local_file_path)
        # Write new Version file
        log.Wrap('  Updating local version file...')
        if version_url is not None:
            with open(version_local_path, 'w') as version_file:
                version_file.write('{}'.format(web_version))
        log.Time(dl_start, 'Downloading {}{}'.format(extracted, file_name))
        log.Wrap('')
    return

def get_only_newer_version(file_url, local_file_path, local_check_file=None,
                           version_url=None, version_local_path=None, minimum_size=None,
                           extract_path=None, extract_pwd=None):
    """Checks for file and version, downloads if necessary"""
    download = False
    local_version = 0
    log = JLog.PrintLog()
    download_dir, file_name = os.path.split(local_file_path)
    log.print_section('Checking for updates to {}'.format(file_name))
    # Check Web Version
    if version_url is not None:
        version_dir, version_name = os.path.split(version_local_path)
        log.Wrap('  Checking latest version on web...'.format(version_name))
        web_version = check_web_version(version_url)
        log.Wrap('    Web version = {}'.format(web_version))
        # If Local File exists Check Local Version
        version_local_file_exists = os.path.exists(version_local_path)
        if version_local_file_exists:
            log.Wrap('  Checking {} local version...'.format(version_name))
            local_version = check_local_version(version_local_path)
            log.Wrap('    Local version = {}'.format(local_version))
        if download is False:
            # Compare local and web versions
            if web_version > local_version:
                log.Wrap('  Newer version available.')
                # If web newer, delete local and set download to True
                try:
                    os.remove(local_file_path)
                except Exception:
                    pass
                download = True
    if download is True:
        # Ensure download directory exists
        try:
            os.makedirs(download_dir)
        except Exception:
            pass
        dl_start = time.clock()
        # Streaming with requests module
        num_bytes = 0
        count = 0
        with requests.get(file_url, stream=True) as r:
            r.raise_for_status()
            with open(local_file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        num_bytes += 8192
                        count += 1
                        if count > 25:
                            formatted_bytes = sizeof_fmt(num_bytes)
                            log.print_status_message('    Downloading file... ({})'.format(formatted_bytes))
                            count = 0
        formatted_bytes = sizeof_fmt(num_bytes)
        log.Wrap('    File Downloaded ({})'.format(formatted_bytes))
        sys.stdout.flush()
        time.sleep(.1)
        # Extract compressed package if selected
        if extract_path is None:
            extracted = ''
        else:
            extracted = 'and Extracting '
            log.Wrap('    Extracting package to target directory...')
            extract_to_folder(zip_file=local_file_path,
                              output_folder=extract_path,
                              pwd=extract_pwd)
            log.Wrap('     Extraction complete. Deleting zip file...')
            # Remove zip file after extraction
            os.remove(local_file_path)
        # Write new Version file
        log.Wrap('  Updating local version file...')
        if version_url is not None:
            with open(version_local_path, 'w') as version_file:
                version_file.write('{}'.format(web_version))
        log.Time(dl_start, 'Downloading {}{}'.format(extracted, file_name))
        log.Wrap('')
    return


#if __name__ == '__main__':
#    LOCAL_VERSION = check_local_version(version_local_path=r'D:\Code\Python\WinPythonARC_dev_EPA_dl_dl\core\arc_ex_version.txt')
#    print(LOCAL_VERSION)

#    ensure_file_exists(file_url='https://www.spk.usace.army.mil/Portals/12/documents/regulatory/upload/APT/WBD/HUC8_Albers.zip',
#                       local_file_path=r'C:\Users\L2RCSJ9D\Desktop\delete\apt\WBD\zip\HUC8_Albers.zip',
#                       version_url='https://www.spk.usace.army.mil/Portals/12/documents/regulatory/upload/APT/WBD/WBD.txt',
#                       version_local_path=r'C:\Users\L2RCSJ9D\Desktop\delete\apt\versions\WBD.txt',
#                       extract_path=r'C:\Users\L2RCSJ9D\Desktop\delete\apt\WBD')

#    ensure_file_exists(file_url='https://www.spk.usace.army.mil/Portals/12/documents/regulatory/upload/APT/WBD/HUC8_Albers.zip',
#                       local_file_path=r'C:\Users\L2RCSJ9D\Desktop\delete\apt\WBD\zip\HUC10_Albers.zip.001',
#                       version_url='https://www.spk.usace.army.mil/Portals/12/documents/regulatory/upload/APT/WBD/WBD.txt',
#                       version_local_path=r'C:\Users\L2RCSJ9D\Desktop\delete\apt\versions\WBD.txt',
#                       extract_path=r'C:\Users\L2RCSJ9D\Desktop\delete\apt\WBD')

#    ensure_file_exists(file_url='https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/WBD/HU2/Shape/WBD_01_HU2_Shape.zip',
#                       local_file_path=r'C:\Users\L2RCSJ9D\Desktop\delete\apt\WBD\zip\WBD_01_HU2_Shape.zip',
#                       extract_path=r'C:\Users\L2RCSJ9D\Desktop\delete\apt\WBD')

#    version = check_web_version('https://raw.githubusercontent.com/jDeters-USACE/Test_REpo/master/Release/version')
#    print('version = {}'.format(version))
