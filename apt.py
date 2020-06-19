# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
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
##   Antecedent Precipitation Tool  ##
##  ------------------------------- ##
##     Written by: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on: 2020-06-16    ##
##  ------------------------------- ##
######################################

# Import Standard Libraries
import multiprocessing

# Import Custom Libraries
import arc

TITLE = """

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

def main():
    print(TITLE)
    # Launch GUI
    APP = arc.ant_GUI.Main()
    APP.run()

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
