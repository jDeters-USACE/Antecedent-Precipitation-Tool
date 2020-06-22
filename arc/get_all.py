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

MODULE_FOLDER = os.path.dirname(os.path.realpath(__file__))
ROOT_FOLDER = os.path.split(MODULE_FOLDER)[0]

def ensure_main_exe():
    # Calculate Paths
    local_file_path = os.path.join(ROOT_FOLDER, 'main_ex.exe')
    file_url = 'https://github.com/jDeters-USACE/Antecedent-Precipitation-Tool/raw/master/update/main_ex.exe'
    version_folder = os.path.join(ROOT_FOLDER, 'v')
    local_version_file = os.path.join(version_folder, 'main_ex')
    web_version_url = 'https://raw.githubusercontent.com/jDeters-USACE/Antecedent-Precipitation-Tool/master/v/main_ex'
    get_files.get_only_newer_version(file_url=file_url,
                                     local_file_path=local_file_path,
                                     version_url=web_version_url,
                                     version_local_path=local_version_file)

def ensure_antecdent_precipitation_tool_exe():
    local_file_path = os.path.join(ROOT_FOLDER, 'Antecedent Precipitation Tool.exe')
    file_url = 'https://github.com/jDeters-USACE/Antecedent-Precipitation-Tool/raw/master/update/Antecedent%20Precipitation%20Tool.exe'
    version_folder = os.path.join(ROOT_FOLDER, 'v')
    local_version_file = os.path.join(version_folder, 'apt')
    web_version_url = 'https://raw.githubusercontent.com/jDeters-USACE/Antecedent-Precipitation-Tool/master/v/apt'
    get_files.get_only_newer_version(file_url=file_url,
                                     local_file_path=local_file_path,
                                     version_url=web_version_url,
                                     version_local_path=local_version_file)

def ensure_images():
    """Ensure the existence of all items from the image folder"""
    images_folder = os.path.join(ROOT_FOLDER, 'images')
    local_file_path = os.path.join(images_folder, 'Graph.ico')
    get_files.ensure_file_exists(file_url='https://github.com/jDeters-USACE/Antecedent-Precipitation-Tool/raw/master/images/Graph.ico',
                                 local_file_path=local_file_path)
    local_file_path = os.path.join(images_folder, 'Minus.gif')
    get_files.ensure_file_exists(file_url='https://github.com/jDeters-USACE/Antecedent-Precipitation-Tool/raw/master/images/Minus.gif',
                                 local_file_path=local_file_path)
    local_file_path = os.path.join(images_folder, 'Plus.gif')
    get_files.ensure_file_exists(file_url='https://github.com/jDeters-USACE/Antecedent-Precipitation-Tool/raw/master/images/Plus.gif',
                                 local_file_path=local_file_path)
    local_file_path = os.path.join(images_folder, 'Question.gif')
    get_files.ensure_file_exists(file_url='https://github.com/jDeters-USACE/Antecedent-Precipitation-Tool/raw/master/images/Question.gif',
                                 local_file_path=local_file_path)
    local_file_path = os.path.join(images_folder, 'RD_1_0.png')
    get_files.ensure_file_exists(file_url='https://github.com/jDeters-USACE/Antecedent-Precipitation-Tool/raw/master/images/RD_1_0.png',
                                 local_file_path=local_file_path)
    local_file_path = os.path.join(images_folder, 'Traverse_40%_503.gif')
    get_files.ensure_file_exists(file_url='https://github.com/jDeters-USACE/Antecedent-Precipitation-Tool/raw/master/images/Traverse_40%25_503.gif',
                                 local_file_path=local_file_path)
    local_file_path = os.path.join(images_folder, 'Traverse_80%_1920.png')
    get_files.ensure_file_exists(file_url='https://github.com/jDeters-USACE/Antecedent-Precipitation-Tool/raw/master/images/Traverse_80%25_1920.png',
                                 local_file_path=local_file_path)
    local_file_path = os.path.join(images_folder, 'folder.gif')
    get_files.ensure_file_exists(file_url='https://github.com/jDeters-USACE/Antecedent-Precipitation-Tool/raw/master/images/folder.gif',
                                 local_file_path=local_file_path)


def main():
    ensure_main_exe()
    ensure_images()


if __name__ == '__main__':
    ensure_images()
