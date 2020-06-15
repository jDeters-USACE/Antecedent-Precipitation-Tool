
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
    TEST = os.path.exists('{}\\Python Scripts'.format(ROOT))
    if TEST:
        sys.path.append('{}\\Python Scripts\\utilities'.format(ROOT))
    else:
        sys.path.append('{}\\arc\\utilities'.format(ROOT))
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
