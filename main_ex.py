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
##   Antecedent Precipitation Tool  ##
##  ------------------------------- ##
##     Written by: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on: 2020-06-22    ##
##  ------------------------------- ##
######################################

# Import Standard Libraries
import multiprocessing
multiprocessing.freeze_support()

# Import Custom Libraries
import arc

TITLE = r"""
     ++++  +++  ++++                     +++  ++++  +++                     _                    _            _
     hNNN +NNNy hNNm                    yNNN+ mNNd oNNN+        /\         | |                  | |          | |
     hMMMhhMMMmymMMN                    hMMMhyNMMmyhMMM+       /  \   _ __ | |_ ___  ___ ___  __| | ___ _ __ | |_
     sNMMMMMMMMMMMMd   syyo syyy  yyys  sNMMMMMMMMMMMMm       / /\ \ | '_ \| __/ _ \/ __/ _ \/ _` |/ _ \ '_ \| __|
      +mMMMMMMMMMMs    NMMh mMMMo+MMMN   +dMMMMMMMMMMh       / ____ \| | | | ||  __/ (_|  __/ (_| |  __/ | | | |_
       dMMMm++MMMM+    NMMNNMMMMNNMMMN    yMMMMo+dMMMs     _/_/_   \_\_| |_|\__\___|\___\___|\__,_|\___|_| |_|\__|
       dMMMm  MMMM+    yNMMMMMMMMMMMmy    yMMMM+ dMMMs    |  __ \             (_)     (_) |      | | (_)
       dMMMm  MMMM+     sMMMMMMMMMMm+     yMMMM+ dMMMs    | |__) | __ ___  ___ _ _ __  _| |_ __ _| |_ _  ___  _ __
       dMMMmooMMMMyyyyyyhMMMMMMMMMMmyyyyyydMMMMsodMMMs    |  ___/ '__/ _ \/ __| | '_ \| | __/ _` | __| |/ _ \| '_ \
       dMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMs    | |   | | |  __/ (__| | |_) | | || (_| | |_| | (_) | | | |
       dMMMMMMMMMMMMMMMMMMMNhysshmMMMMMMMMMMMMMMMMMMMs    |_|___|_|_ \___|\___|_| .__/|_|\__\__,_|\__|_|\___/|_| |_|
       dMMMNyyMMMMMMyymMMMh+      hMMMNyyMMMMMMhymMMMs     |__   __|        | | | |
       dMMMm  MMMMMM  dMMN         NMMN  NMMMMM+ dMMMs        | | ___   ___ | | |_|
       dMMMm  MMMMMM+ dMMm         mMMN  NMMMMM+ dMMMs        | |/ _ \ / _ \| |        -Written by:
     +dMMMMm++MMMMMMddNMMm         mMMMddMMMMMMo+dMMMNh       | | (_) | (_) | |         Jason C. Deters,
     hMMMMMMNNMMMMMMMMMMMm         mMMMMMMMMMMMNNNMMMMMo      |_|\___/ \___/|_|         U.S. Army Corps of Engineers
     hMMMMMMMMMMMMMMMMMMMNhhhhhhhhhNMMMMMMMMMMMMMMMMMMMo
     ymmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm+
"""

def ula_window():
    # Launch ULA
    APP = arc.ula_window.UlaWindow()
    APP.run()

def main():
    print(TITLE)
    # Launch GUI
    APP = arc.ant_GUI.AntGUI()
    APP.run()

if __name__ == '__main__':
    # arc.get_all.get_latest_release()
    # arc.get_all.ensure_antecdent_precipitation_tool_exe()
    arc.get_all.ensure_images()
    arc.get_all.ensure_wbd_folder()
    arc.get_all.ensure_us_shp_folder()
    arc.get_all.ensure_climdiv_folder()
    arc.get_all.ensure_WIMP()
    arc.get_all.ensure_binaries()
    arc.shortcut.create_shortcut_frozen()
    ula_window()
    main()
