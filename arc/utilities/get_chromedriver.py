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
##        get_chromedriver.py       ##
##  ------------------------------- ##
##      Copyright: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on:  2020-05-27   ##
##  ------------------------------- ##
######################################

"""
This module is used to:
1. Get the version of Chrome from Chrome.exe
2. Find the appropriate version of Chromedriver.exe for that version of Chrome
3. Check for that version of Chromedriver.exe
4. If it can't be located on the local machine;
    -Find the download URL for that version of Chromedriver.exe
    -Download the correct version of Chromedriver.exe to the local drive
5. Report the location of the appropriate version of Chromedriver.exe
"""

# Import Standard Libraries
import os
import sys
import shutil
import time
import stat

# Import Third-Party Libraries
import zipfile
import requests
import urllib3
from win32api import GetFileVersionInfo, LOWORD, HIWORD

# Import Custom Libraries
try:
    from . import JLog
except Exception:
    import JLog

MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
ROOT_PATH = os.path.dirname(os.path.dirname(MODULE_PATH))

def delete_read_only(file_path):
    """Deletes read-only files by changing their properties and retrying"""
    try:
        os.remove(file_path)
    except Exception:
        os.chmod(file_path, stat.S_IWRITE)
        os.remove(file_path)
# End of delete_read_only function

def sizeof_fmt(num, suffix='B'):
    for unit in [' ', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "{:6.2f} {}{}".format(num, unit, suffix)
        num /= 1024.0
    return "{:6.2f} {}{}".format(num, 'Y', suffix)

def get_chrome_version():
    """Gets the major, minor and build versions of the local Google Chrome installation"""
    log = JLog.PrintLog(Indent=2)
    log.Wrap('Checking Google Chrome version...')
    filename = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
    try:
        info = GetFileVersionInfo(filename, "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        version_numbers = [HIWORD(ms), LOWORD(ms), HIWORD(ls)]
        chrome_version = ".".join([str(i) for i in version_numbers])
        log.Wrap('Google Chrome version = {}'.format(chrome_version))
        return chrome_version
    except Exception:
        log.Wrap('Google Chrome version could not be determined.')
        chrome_version = '78.0.3904'
        log.Wrap(' Presumed version = {}'.format(chrome_version))
        return chrome_version
# End of get_chrome_version function

def get_chrome_driver_path():
    """Gets the expected file path of the appropriate version of Chromedriver.exe"""
    log = JLog.PrintLog(Indent=2)
    # Get Chrome Version
    chrome_version = get_chrome_version()
    # Locate Chrome Binary
    log.Wrap('Locating matching Chrome binary...')
    chrome_driver_folder = "{}\\webDrivers\\Chrome".format(ROOT_PATH)
    # The above tends to work even with the single-file executable, but this is here just to be safe
    folder_exists = os.path.exists(chrome_driver_folder)
    if not folder_exists:
        chrome_driver_folder = os.path.join(sys.prefix, 'webDrivers\\Chrome')
    chrome_driver_path = "{}\\{}\\chromedriver.exe".format(chrome_driver_folder, chrome_version)
    driver_exists = os.path.exists(chrome_driver_path)
    if driver_exists:
        driver_file_size = os.path.getsize(chrome_driver_path)
        if driver_file_size < 8036096:
            log.Wrap('Chrome binary corrupt (Less than 8036096 bytes), deleting...')
            delete_read_only(chrome_driver_path)
            driver_exists = False
    if not driver_exists:
        # Download chrome driver from Google
        download_chrome_driver(chrome_version, chrome_driver_path)
    log.Wrap('Chrome binary = {}'.format(chrome_driver_path))
    return chrome_driver_path
# End of get_chrome_driver_path function

def download_chrome_driver(chrome_version, chrome_driver_path):
    web_content = None
    http_file_size = None
    log = JLog.PrintLog(Indent=3)
    log.Wrap('Matching Chrome binary not found, acquiring directly from Google...')
    # Constructing LATEST_RELEASE URL
    latest_release_url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{}".format(chrome_version)
    log.Wrap('LATEST_RELEASE URL = {}'.format(latest_release_url))
    # Get data from LATEST_RELEASE URL using urllib3
    log.Wrap('Requesting data from LATEST_RELEASE URL...')
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED')
    response = http.request('GET', latest_release_url)
    download_url_suffix = str(response.data.split(b"\n")[0], 'utf-8')
    log.Wrap('Response = {}'.format(download_url_suffix))
    # Constructing DOWNLOAD URL
    download_url = "https://chromedriver.storage.googleapis.com/{}/chromedriver_win32.zip".format(download_url_suffix)
    log.Wrap('DOWNLOAD URL = {}'.format(download_url))
    # Ensure download directory exists
    download_directory = os.path.split(chrome_driver_path)[0]
    log.Wrap('Ensuring download directory ({}) exists...'.format(download_directory))
    try:
        os.makedirs(download_directory)
    except Exception:
        pass
    # Define temporary zip path
    chrome_zip_path = '{}\\chromedriver_win32.zip'.format(download_directory)
    # Download chrome binary
    log.Wrap('Starting requests session...')
    session = requests.Session()
    tries = 5
    while tries > 0:
        tries -= 1
        # Attempt to save web_content to a file
        try:
            # Initiate Get Request if not already open
            if web_content is None:
                web_content = session.get(download_url, stream=True)
            # Attempt to get file size from server if note already done
            try:
                if http_file_size is None:
                    http_file_size = int(web_content.headers['Content-length'])
                    minimum_bytes = http_file_size
                file_size_string = sizeof_fmt(http_file_size)
                file_size_message = ' - {}'.format(file_size_string)
            except Exception:
                file_size_message = ""
                minimum_bytes = 4759775
            log.Wrap("Downloading Chromedriver.exe{}".format(file_size_message))
            # Save operation - Open file, then iteratively write streaming web content
            with open(chrome_zip_path, 'wb') as local_file:
                shutil.copyfileobj(web_content.raw, local_file)
            driver_file_size = os.path.getsize(chrome_zip_path)
            if driver_file_size < minimum_bytes:
                log.Wrap(' Chrome binary corrupt, deleting...')
                log.Wrap('  Binary file size   = {} bytes'.format(driver_file_size))
                log.Wrap('  Expected file size > {} bytes'.format(minimum_bytes))
                delete_read_only(chrome_zip_path)
            else:
                with zipfile.ZipFile(chrome_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(download_directory)
                driver_exists = os.path.exists(chrome_driver_path)
                if driver_exists:
                    try:
                        os.remove(chrome_zip_path)
                    except Exception:
                        pass
                    tries = 0
        except Exception as F:
            log.Wrap(F)
            try:
                time.sleep(.1)
                os.remove(chrome_driver_path)
            except Exception:
                pass
            if tries > 0:
                log.Wrap('Download failed. Trying again in 5 seconds...')
                time.sleep(5)
                web_content = None
# End of download_chrome_driver function

if __name__ == '__main__':
    CHROME_DRIVER_PATH = get_chrome_driver_path()
    print(CHROME_DRIVER_PATH)
