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
##           get_all.py             ##
##  ------------------------------- ##
##     Written by: Jason Deters     ##
##     Edited by: Joseph Gutenson   ##
##  ------------------------------- ##
##    Last Edited on: 2023-04-26    ##
##  ------------------------------- ##
######################################

import os
from pathlib import Path

try:
    from . import get_files
except Exception:
    import get_files

MODULE_FOLDER = os.path.dirname(os.path.realpath(__file__))
ROOT_FOLDER = os.path.split(MODULE_FOLDER)[0]

def ensure_main_exe():
    # Calculate Paths
    local_file_path = os.path.join(ROOT_FOLDER, 'main_ex.exe')
    file_url = 'https://github.com/erdc/Antecedent-Precipitation-Tool/raw/master/update/main_ex.exe'
    version_folder = os.path.join(ROOT_FOLDER, 'v')
    local_version_file = os.path.join(version_folder, 'main_ex')
    web_version_url = 'https://raw.githubusercontent.com/erdc/Antecedent-Precipitation-Tool/master/v/main_ex'
    get_files.get_only_newer_version(file_url=file_url,
                                     local_file_path=local_file_path,
                                     version_url=web_version_url,
                                     version_local_path=local_version_file)

def ensure_antecdent_precipitation_tool_exe():
    local_file_path = os.path.join(ROOT_FOLDER, 'Antecedent Precipitation Tool.exe')
    file_url = 'https://github.com/erdc/Antecedent-Precipitation-Tool/raw/master/update/Antecedent%20Precipitation%20Tool.exe'
    version_folder = os.path.join(ROOT_FOLDER, 'v')
    local_version_file = os.path.join(version_folder, 'apt')
    web_version_url = 'https://raw.githubusercontent.com/erdc/Antecedent-Precipitation-Tool/master/v/apt'
    get_files.get_only_newer_version(file_url=file_url,
                                     local_file_path=local_file_path,
                                     version_url=web_version_url,
                                     version_local_path=local_version_file)


def get_latest_release():
    local_file_path = os.path.join(str(Path(ROOT_FOLDER).parents[0]), 'Antecedent.Precipitation.Tool.7z')
    file_url = 'https://github.com/erdc/Antecedent-Precipitation-Tool/releases/latest/download/Antecedent.Precipitation.Tool.7z'
    version_folder = os.path.join(ROOT_FOLDER, 'v')
    local_version_file = os.path.join(version_folder, 'release')
    web_version_url = "https://raw.githubusercontent.com/erdc/Antecedent-Precipitation-Tool/master/v/apt"
    extraction_path = str(Path(ROOT_FOLDER).parents[0])
    get_files.get_only_newer_version(file_url=file_url,
                                    local_file_path=local_file_path,
                                    version_url=web_version_url,
                                    version_local_path=local_version_file,
                                    extract_path=extraction_path)

def attempt_repair():
    local_file_path = os.path.join(ROOT_FOLDER, 'APT Repair Package.zip')
    file_url = r'https://github.com/jDeters-USACE/Antecedent-Precipitation-Tool/releases/download/v1.0/Antecedent Precipitation Tool.zip'
    local_file_exists = os.path.exists(local_file_path)
    if local_file_exists:
        try:
            os.remove(local_file_path)
        except Exception:
            pass
    get_files.ensure_file_exists(file_url=file_url,
                                 local_file_path=local_file_path,
                                 extract_path=ROOT_FOLDER)


def ensure_version_file():
    local_file_path = os.path.join(ROOT_FOLDER, 'version')
    file_url = 'https://github.com/erdc/Antecedent-Precipitation-Tool/raw/master/version'
    get_files.ensure_file_exists(file_url=file_url,
                                 local_file_path=local_file_path)

def ensure_wbd_folder():
    file_url = 'https://github.com/jDeters-USACE/Antecedent-Precipitation-Tool/releases/download/v1.0/WBD.zip'
    gis_folder = os.path.join(ROOT_FOLDER, 'GIS')
    local_file_path = os.path.join(gis_folder, "WBD.zip")
    wbd_folder = os.path.join(gis_folder, "WBD")
    wbd_Exists = os.path.exists(wbd_folder)
    version_folder = os.path.join(ROOT_FOLDER, 'v')
    local_version_file = os.path.join(version_folder, 'wbd')
    web_version_url = 'https://github.com/erdc/Antecedent-Precipitation-Tool/raw/master/v/wbd'
    get_files.get_only_newer_version(file_url=file_url,
                                     local_file_path=local_file_path,
                                     local_check_file=wbd_folder,
                                     version_url=web_version_url,
                                     version_local_path=local_version_file,
                                     extract_path=wbd_folder)

def ensure_us_shp_folder():
    gis_folder = os.path.join(ROOT_FOLDER, 'GIS')
    us_shp_folder = os.path.join(gis_folder, "us_shp")
    us_shp_folder_exists = os.path.exists(us_shp_folder)
    if not us_shp_folder_exists:
        local_file_path = os.path.join(gis_folder, "us_shp.zip")
        try:
            os.remove(local_file_path)
        except Exception:
            pass
        try:
            file_url = 'https://github.com/erdc/Antecedent-Precipitation-Tool/releases/download/v1.0.21/us_shp.zip'
            get_files.ensure_file_exists(file_url=file_url,
                                    local_file_path=local_file_path,
                                    extract_path=us_shp_folder)
        except:
            file_url = 'https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_us_nation_5m.zip'
            get_files.ensure_file_exists(file_url=file_url,
                                    local_file_path=local_file_path,
                                    extract_path=us_shp_folder)


def ensure_climdiv_folder():
    gis_folder = os.path.join(ROOT_FOLDER, 'GIS')
    climdiv_folder = os.path.join(gis_folder, "climdiv")
    climdiv_folder_exists = os.path.exists(climdiv_folder)
    if not climdiv_folder_exists:
        local_file_path = os.path.join(gis_folder, "climdiv.zip")
        try:
            os.remove(local_file_path)
        except Exception:
            pass
        file_url = 'https://github.com/jDeters-USACE/Antecedent-Precipitation-Tool/releases/download/v1.0.3/climdiv.zip'
        get_files.ensure_file_exists(file_url=file_url,
                                    local_file_path=local_file_path,
                                    extract_path=gis_folder)

def ensure_WIMP():
    wimp_folder = os.path.join(ROOT_FOLDER, 'cached')
    wimp_path = os.path.join(wimp_folder, 'wimp_dict.pickle')
    wimp_path_exists = os.path.exists(wimp_path)
    if not wimp_path_exists:
        local_file_path = os.path.join(wimp_folder, 'WebWimpcache.zip')
        try:
            os.remove(local_file_path)
        except Exception:
            pass
        file_url = 'https://github.com/erdc/Antecedent-Precipitation-Tool/raw/master/cached/WebWIMPcache.zip'
        get_files.ensure_file_exists(file_url=file_url,
                                     local_file_path=local_file_path,
                                     extract_path=wimp_folder)


def ensure_libiomp5md():
    local_file_path = os.path.join(ROOT_FOLDER, 'libiomp5md.dll')
    url = 'https://github.com/jDeters-USACE/Antecedent-Precipitation-Tool/releases/download/v1.0/libiomp5md.dll'
    get_files.ensure_file_exists(file_url=url,
                                 local_file_path=local_file_path)

def ensure_mkl_avx2():
    local_file_path = os.path.join(ROOT_FOLDER, 'mkl_avx2.dll')
    url = 'https://github.com/jDeters-USACE/Antecedent-Precipitation-Tool/releases/download/v1.0/mkl_avx2.dll'
    get_files.ensure_file_exists(file_url=url,
                                 local_file_path=local_file_path)

def ensure_mkl_core():
    local_file_path = os.path.join(ROOT_FOLDER, 'mkl_core.dll')
    url = 'https://github.com/jDeters-USACE/Antecedent-Precipitation-Tool/releases/download/v1.0/mkl_core.dll'
    get_files.ensure_file_exists(file_url=url,
                                 local_file_path=local_file_path)

def ensure_mkl_intel_thread():
    local_file_path = os.path.join(ROOT_FOLDER, 'mkl_intel_thread.dll')
    url = 'https://github.com/jDeters-USACE/Antecedent-Precipitation-Tool/releases/download/v1.0/mkl_intel_thread.dll'
    get_files.ensure_file_exists(file_url=url,
                                 local_file_path=local_file_path)

def ensure_mkl_p4m3():
    local_file_path = os.path.join(ROOT_FOLDER, 'mkl_p4m3.dll')
    url = 'https://github.com/jDeters-USACE/Antecedent-Precipitation-Tool/releases/download/v1.0/mkl_p4m3.dll'
    get_files.ensure_file_exists(file_url=url,
                                 local_file_path=local_file_path)

def ensure_mkl_vml_p4():
    local_file_path = os.path.join(ROOT_FOLDER, 'mkl_vml_p4.dll')
    url = 'https://github.com/jDeters-USACE/Antecedent-Precipitation-Tool/releases/download/v1.0/mkl_vml_p4.dll'
    get_files.ensure_file_exists(file_url=url,
                                 local_file_path=local_file_path)

def ensure_mkl_avx():
    local_file_path = os.path.join(ROOT_FOLDER, 'mkl_avx.dll')
    url = 'https://github.com/jDeters-USACE/Antecedent-Precipitation-Tool/releases/download/v1.0/mkl_avx.dll'
    get_files.ensure_file_exists(file_url=url,
                                 local_file_path=local_file_path)

def ensure_mkl_p4():
    local_file_path = os.path.join(ROOT_FOLDER, 'mkl_p4.dll')
    url = 'https://github.com/jDeters-USACE/Antecedent-Precipitation-Tool/releases/download/v1.0/mkl_p4.dll'
    get_files.ensure_file_exists(file_url=url,
                                 local_file_path=local_file_path)


def ensure_binaries():
    ensure_libiomp5md()
    #ensure_mkl_avx2()
    #ensure_mkl_core()
    #ensure_mkl_intel_thread()
    #ensure_mkl_p4m3()
    #ensure_mkl_vml_p4()
    #ensure_mkl_avx()
    #ensure_mkl_p4()


def ensure_images():
    """Ensure the existence of all items from the image folder"""
    images_folder = os.path.join(ROOT_FOLDER, 'images')
    local_file_path = os.path.join(images_folder, 'Graph.ico')
    get_files.ensure_file_exists(file_url='https://github.com/erdc/Antecedent-Precipitation-Tool/raw/master/images/Graph.ico',
                                 local_file_path=local_file_path)
    local_file_path = os.path.join(images_folder, 'Minus.gif')
    get_files.ensure_file_exists(file_url='https://github.com/erdc/Antecedent-Precipitation-Tool/raw/master/images/Minus.gif',
                                 local_file_path=local_file_path)
    local_file_path = os.path.join(images_folder, 'Plus.gif')
    get_files.ensure_file_exists(file_url='https://github.com/erdc/Antecedent-Precipitation-Tool/raw/master/images/Plus.gif',
                                 local_file_path=local_file_path)
    local_file_path = os.path.join(images_folder, 'Question.gif')
    get_files.ensure_file_exists(file_url='https://github.com/erdc/Antecedent-Precipitation-Tool/raw/master/images/Question.gif',
                                 local_file_path=local_file_path)
    local_file_path = os.path.join(images_folder, 'RD_2_0.png')
    get_files.ensure_file_exists(file_url='https://github.com/erdc/Antecedent-Precipitation-Tool/raw/master/images/RD_2_0.png',
                                 local_file_path=local_file_path)
    local_file_path = os.path.join(images_folder, 'Traverse_40%_503.gif')
    get_files.ensure_file_exists(file_url='https://github.com/erdc/Antecedent-Precipitation-Tool/raw/master/images/Traverse_40%25_503.gif',
                                 local_file_path=local_file_path)
    local_file_path = os.path.join(images_folder, 'Traverse_80%_1920.png')
    get_files.ensure_file_exists(file_url='https://github.com/erdc/Antecedent-Precipitation-Tool/raw/master/images/Traverse_80%25_1920.png',
                                 local_file_path=local_file_path)
    local_file_path = os.path.join(images_folder, 'folder.gif')
    get_files.ensure_file_exists(file_url='https://github.com/erdc/Antecedent-Precipitation-Tool/raw/master/images/folder.gif',
                                 local_file_path=local_file_path)


def main():
    ensure_main_exe()
    ensure_images()


if __name__ == '__main__':
    ensure_images()
    ensure_wbd_folder()
    ensure_us_shp_folder()
    ensure_climdiv_folder()
    ensure_WIMP()
