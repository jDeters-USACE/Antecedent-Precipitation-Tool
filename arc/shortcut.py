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
##           shortcut.py            ##
##  ------------------------------- ##
##     Written by: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on: 2020-06-21    ##
##  ------------------------------- ##
######################################

"""Creates a desktop shortcut for the Antecedent Precipitation Tool"""

import os
import time
import winshell


def create_shortcut_unfrozen():
    """Creates a desktop shortcut for the Antecedent Precipitation Tool"""
    # Define Shortcut Variables
    python_path = 'C:\\Antecedent Precipitation Tool\\WinPythonZero32\\python-3.6.5\\python.exe'
    desktop_path = str(winshell.desktop()) # get desktop path
    icon = "C:\\Antecedent Precipitation Tool\\images\\Graph.ico"
    launch_script = '"C:\\Antecedent Precipitation Tool\\Python Scripts\\ant_GUI.py"'
    shortcut_path = os.path.join(desktop_path, 'Antecedent Precipitation Tool.lnk')
    description = 'Launches the Antecedent Precipitation Tool, written by Jason C. Deters'
    # Create shortcut
    shortcut_exists = os.path.exists(shortcut_path)
    if not shortcut_exists:
        print('Creating Desktop shortcut for the Antecedent Precipitation Tool...')
    else:
        print('Validating Desktop shortcut...')
    winshell.CreateShortcut(Path=shortcut_path,
                            Target=python_path,
                            Arguments=launch_script,
                            StartIn=desktop_path,
                            Icon=(icon, 0),
                            Description=description)
    print('')
    print('All Elements installed successfully!    Closing window in 5 seconds')
    time.sleep(5)


def create_shortcut_frozen():
    """Creates a desktop shortcut for the Antecedent Precipitation Tool"""
    # Define Shortcut Variables
    module_path = os.path.dirname(os.path.realpath(__file__))
    root_folder = os.path.split(module_path)[0]
    frozen_exe_path = '{}\\main_ex.exe'.format(root_folder)
    desktop_path = str(winshell.desktop()) # get desktop path
    icon = "{}\\images\\Graph.ico".format(root_folder)
    shortcut_path = os.path.join(desktop_path, 'Antecedent Precipitation Tool.lnk')
    description = 'Launches the Antecedent Precipitation Tool, written by Jason C. Deters'
    # Create shortcut
    shortcut_exists = os.path.exists(shortcut_path)
    if not shortcut_exists:
        print('Creating Desktop shortcut for the Antecedent Precipitation Tool...')
    else:
        print('Validating Desktop shortcut...')
        print('')
        print('')
        print('')
        print('')
        print('')
    winshell.CreateShortcut(Path=shortcut_path,
                            Target=frozen_exe_path,
                            StartIn=desktop_path,
                            Icon=(icon, 0),
                            Description=description)
    print('')




if __name__ == '__main__':
    create_shortcut_frozen()
