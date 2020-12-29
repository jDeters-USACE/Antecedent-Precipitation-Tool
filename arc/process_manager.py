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
##        process_manager.py        ##
##  ------------------------------- ##
##     Written by: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on: 2020-05-27    ##
##  ------------------------------- ##
######################################

""" This code provides the subprocess minions for the Antecedent Precipitation Tool """

import os
import sys
import multiprocessing
import traceback
import time
import warnings
multiprocessing.freeze_support()

# Find module path
MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
# Find ROOT folder
ROOT = os.path.split(MODULE_PATH)[0]

# Add Utilities dir to path
try:
    from .utilities import JLog
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

class Minion(multiprocessing.Process):
    """Multiprocessing worker class"""
    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.proc_name = None
        self.log = None
    def start_log(self):
        """Instantiates Logging class"""
        # Create PrintLog
        self.log = JLog.PrintLog()
        self.proc_name = self.name
    def run(self):
        warnings.filterwarnings("ignore")
#        f = open(os.devnull, 'w')
#        sys.stderr = f
        num_jobs = 0
        max_jobs = 100  # Max jobs before terminating
        sleep_time = 1
        while True:
            try:
                next_task = self.task_queue.get()
                sleep_time = 1
            except Exception:
                time.sleep(sleep_time)
                if sleep_time < 10:
                    sleep_time += .5
            if next_task is None:
                # Poison pill means shutdown
                break
            try:
                result = next_task()
            except Exception:
#                sys.stderr = sys.__stderr__
                self.start_log()
                self.log.Wrap('------------------------------------------')
                self.log.Wrap("EXCEPTION:")
                self.log.Wrap(traceback.format_exc())
                self.log.Wrap('------------------------------------------')
            self.result_queue.put(result)
            num_jobs += 1
            if num_jobs > max_jobs:
                self.result_queue.put("Maxed")
                break
        return
# End of Minion
