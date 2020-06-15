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
##         get_all.py               ##
##  ------------------------------- ##
##      Copyright: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on: 2020-05-27    ##
##  ------------------------------- ##
######################################

import os

try:
    from . import get_files
except Exception:
    import get_files

def ensure_wbd_exists():
    module_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_folder)[0]
    wbd_folder = u'{}\\GIS\\WBD'.format(root_folder)
    shapefile = '{}\\HUC2.shp'.format(wbd_folder)
    exists = os.path.exists(shapefile)
    if not exists:
        file_url = 'https://www.spk.usace.army.mil/Portals/12/documents/regulatory/upload/APT/WBD/HUC2.zip'
        local_file_path = u'{}\\GIS\\HUC2.zip'.format(root_folder)
        get_files.ensure_file_exists(file_url=file_url,
                                    local_file_path=local_file_path,
                                    extract_path=wbd_folder)

def ensure_climdiv_exists():
    module_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_folder)[0]
    climdiv_folder = u'{}\\GIS\\climdiv'.format(root_folder)
    shapefile = '{}\\GIS.OFFICIAL_CLIM_DIVISIONS.shp'.format(climdiv_folder)
    exists = os.path.exists(shapefile)
    if not exists:
        file_url = 'https://www.spk.usace.army.mil/Portals/12/documents/regulatory/upload/APT/climdiv/GIS.OFFICIAL_CLIM_DIVISIONS.zip'
        local_file_path = u'{}\\GIS\\GIS.OFFICIAL_CLIM_DIVISIONS.zip'.format(root_folder)
        get_files.ensure_file_exists(file_url=file_url,
                                    local_file_path=local_file_path,
                                    extract_path=climdiv_folder)

def ensure_us_shp_exists():
    module_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_folder)[0]
    us_shp_folder = u'{}\\GIS\\us_shp'.format(root_folder)
    shapefile = '{}\\cb_2018_us_nation_5m.shp'.format(us_shp_folder)
    exists = os.path.exists(shapefile)
    if not exists:
        file_url = 'https://www.spk.usace.army.mil/Portals/12/documents/regulatory/upload/APT/us_shp/cb_2018_us_nation_5m.zip'
        local_file_path = u'{}\\GIS\\cb_2018_us_nation_5m.zip'.format(root_folder)
        get_files.ensure_file_exists(file_url=file_url,
                                    local_file_path=local_file_path,
                                    extract_path=us_shp_folder)

def ensure_wimp_pickle():
    module_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_folder)[0]
    us_shp_folder = u'{}\\cached'.format(root_folder)
    pickle_file = '{}\\wimp_dict.pickle'.format(us_shp_folder)
    exists = os.path.exists(pickle_file)
    if not exists:
        file_url = 'https://www.spk.usace.army.mil/Portals/12/documents/regulatory/upload/APT/cached/wimp_dict.zip'
        local_file_path = u'{}\\cached\\wimp_dict.zip'.format(root_folder)
        get_files.ensure_file_exists(file_url=file_url,
                                    local_file_path=local_file_path,
                                    extract_path=us_shp_folder)

def ensure_package():
    module_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_folder)[0]
    local_file_path = '{}\\versions\\math_&_graphing_packages.zip'.format(root_folder)
    try:
        os.remove(local_file_path)
    except Exception:
        pass
    file_url = 'https://www.spk.usace.army.mil/Portals/12/documents/regulatory/upload/APT/package/math_&_graphing_packages.zip?ver=2020-06-15'
    local_version_file = '{}\\versions\\package_version.txt'.format(root_folder)
    web_version_url = 'https://raw.githubusercontent.com/jDeters-USACE/Antecedent-Rainfall-Calculator/master/versions/package_version.txt'
    get_files.get_only_newer_version(file_url=file_url,
                                     local_file_path=local_file_path,
                                     version_url=web_version_url,
                                     version_local_path=local_version_file,
                                     extract_path=root_folder)

def ensure_arc_exe():
    # Calculate Paths
    module_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_folder)[0]
    local_file_path = '{}\\arc_ex.exe'.format(root_folder)
    file_url = 'https://github.com/jDeters-USACE/Antecedent-Rainfall-Calculator/raw/master/update/arc_ex.exe'
    local_version_file = '{}\\versions\\arc_ex_version.txt'.format(root_folder)
    web_version_url = 'https://raw.githubusercontent.com/jDeters-USACE/Antecedent-Rainfall-Calculator/master/versions/arc_ex_version.txt'
    get_files.get_only_newer_version(file_url=file_url,
                                     local_file_path=local_file_path,
                                     version_url=web_version_url,
                                     version_local_path=local_version_file)

def ensure_antecdent_precipitation_tool_exe():
    module_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_folder)[0]
    local_file_path = '{}\\Antecedent Precipitation Tool.exe'.format(root_folder)
    file_url = 'https://github.com/jDeters-USACE/Antecedent-Rainfall-Calculator/raw/master/update/Antecedent%20Precipitation%20Tool.exe'
    local_version_file = local_version_file = '{}\\versions\\dl_version.txt'.format(root_folder)
    web_version_url = 'https://raw.githubusercontent.com/jDeters-USACE/Antecedent-Rainfall-Calculator/master/versions/dl_version.txt'
    get_files.get_only_newer_version(file_url=file_url,
                                     local_file_path=local_file_path,
                                     version_url=web_version_url,
                                     version_local_path=local_version_file)

def ensure_rd_1_0_png():
    module_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_folder)[0]
    local_file_path = '{}\\images\\RD_1_0.png'.format(root_folder)
    file_url = 'https://github.com/jDeters-USACE/Antecedent-Rainfall-Calculator/raw/master/images/RD_1_0.png'
    exists = os.path.exists(local_file_path)
    if not exists:
        get_files.ensure_file_exists(file_url=file_url,
                                     local_file_path=local_file_path)

def ensure_traverse_80():
    module_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_folder)[0]
    local_file_path = '{}\\images\\Traverse_80%_1920.png'.format(root_folder)
    file_url = 'https://github.com/jDeters-USACE/Antecedent-Rainfall-Calculator/raw/master/images/Traverse_80%25_1920.png'
    exists = os.path.exists(local_file_path)
    if not exists:
        get_files.ensure_file_exists(file_url=file_url,
                                     local_file_path=local_file_path)

def ensure_traverse_40():
    module_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_folder)[0]
    local_file_path = '{}\\images\\Traverse_40%_503.gif'.format(root_folder)
    file_url = 'https://github.com/jDeters-USACE/Antecedent-Rainfall-Calculator/raw/master/images/Traverse_40%25_503.gif'
    exists = os.path.exists(local_file_path)
    if not exists:
        get_files.ensure_file_exists(file_url=file_url,
                                     local_file_path=local_file_path)
def ensure_minus():
    module_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_folder)[0]
    local_file_path = '{}\\images\\Minus.gif'.format(root_folder)
    file_url = 'https://github.com/jDeters-USACE/Antecedent-Rainfall-Calculator/raw/master/images/Minus.gif'
    exists = os.path.exists(local_file_path)
    if not exists:
        get_files.ensure_file_exists(file_url=file_url,
                                     local_file_path=local_file_path)

def ensure_plus():
    module_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_folder)[0]
    local_file_path = '{}\\images\\Plus.gif'.format(root_folder)
    file_url = 'https://github.com/jDeters-USACE/Antecedent-Rainfall-Calculator/raw/master/images/Plus.gif'
    exists = os.path.exists(local_file_path)
    if not exists:
        get_files.ensure_file_exists(file_url=file_url,
                                     local_file_path=local_file_path)

def ensure_question():
    module_folder = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_folder)[0]
    local_file_path = '{}\\images\\Question.gif'.format(root_folder)
    file_url = 'https://github.com/jDeters-USACE/Antecedent-Rainfall-Calculator/raw/master/images/Question.gif'
    exists = os.path.exists(local_file_path)
    if not exists:
        get_files.ensure_file_exists(file_url=file_url,
                                     local_file_path=local_file_path)


def ensure_images():
    ensure_rd_1_0_png()
    ensure_traverse_80()
    ensure_traverse_40()
    ensure_minus()
    ensure_plus()
    ensure_question()


def main():
    ensure_package()
    ensure_arc_exe()
    ensure_wbd_exists()
    ensure_climdiv_exists()
    ensure_us_shp_exists()
    ensure_wimp_pickle()


if __name__ == '__main__':
    ensure_antecdent_precipitation_tool_exe()
