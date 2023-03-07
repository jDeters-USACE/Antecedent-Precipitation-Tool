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
##             JLog.py              ##
##  ------------------------------- ##
##     Written by: Jason Deters     ##
##      Edited by: Chase Hamilton   ##
##  ------------------------------- ##
##    Last Edited on:  2022-11-10   ##
##  ------------------------------- ##
######################################

# Import Standard Libraries
import os
import sys
import traceback
import textwrap
import stat
import struct
import subprocess

from datetime import datetime


# Function Definitions

def ensure_dir(folder):
    """Ensures entire directory structure given exists"""
    try:
        os.makedirs(folder)
    except Exception:
        pass
# End of ensure_dir function


def deleteReadOnly(filePath):
    try:
        os.remove(filePath)
    except WindowsError:
        try:
            os.chmod(filePath, stat.S_IWRITE)
            os.remove(filePath)
        except WindowsError:
            pass


#-------------------------------------Class Definitions-----------------------------------#

# Define Local Variables
UTILITIES_FOLDER = os.path.dirname(os.path.realpath(__file__))
ARC_FOLDER = os.path.dirname(UTILITIES_FOLDER)
ROOT_FOLDER = os.path.dirname(ARC_FOLDER)

class PrintLog(object):
    """Handles the printing and logging of various types of inputs"""
    def __init__(self,
                 Delete=False,
                 Log=None,
                 Indent=0,
                 Width=119,
                 LogOnly=False):
        if Log is None:
            log_folder = os.path.join(ROOT_FOLDER, 'Logs')
            Log = os.path.join(log_folder, 'Antecedent_LOG.txt')
        self.Wrapper = textwrap.TextWrapper()
        self.Log = Log
        self.SetIndent(Indent)
        self.SetWidth(Width)
        self.LogOnly = LogOnly
        self.executable_name = os.path.split(sys.executable)[1]
        self.prevMsgLen = None
        self.get_terminal_size_windows()
        if self.Log is not None:
            # Get folder portion of log file path
            logPath = os.path.split(Log)[0]
            # Ensure log file folder exists
            ensure_dir(logPath)
            if Delete is True:
                # Attempt to delete log file
                try:
                    deleteReadOnly(self.Log)
                except Exception:
                    pass

    def SetIndent(self, Spaces):
        if type(Spaces) == int:
            InitialIndent = " " * Spaces
            SubIndent = " " * (Spaces+2)
        if type(Spaces) == str:
            InitialIndent = Spaces
            SubIndent = Spaces + "  "
        self.Wrapper.initial_indent = InitialIndent
        self.Wrapper.subsequent_indent = SubIndent
        return

    def SetWidth(self, Width):
        self.Wrapper.width = Width
        return

    def SetLogOnly(self, Boolean):
        self.LogOnly = Boolean
        return

    def write_error_log(self):
        log_folder = os.path.join(ROOT_FOLDER, 'Logs')
        error_log_path = os.path.join(log_folder, 'APT_Error_Log.txt')
        with open(error_log_path, 'w') as error_log:
            error_log.write(' \n')
            error_log.write('Please email this document to APT-Report-Issue@usace.army.mil to assist with your Error Report\n')
            error_log.write(' \n')
            with open(self.Log, 'r') as log_file:
                for line in log_file:
                    error_log.write(line)
                    sys.stdout.flush()
        return error_log_path


    def Write(self, message):
        # Ensure we completely overwrite any '\r' lines
        if self.prevMsgLen is not None:
            while len(message) < 118:
                message = u'{0} '.format(message)
            self.prevMsgLen = None
        if self.Log is not None:
            tries = 5
            while tries > 0:
                try:
                    with open(self.Log, "a") as f:
                        # Write message to Log
                        f.write(u"{0}\n".format(message))
                        tries = 0
                    if self.LogOnly == True:
                        sys.stdout.flush()
                        return
                except:
                    tries -= 1
                    if tries == 0:
                        self.Wrap('-------------------------------------------------------')
                        self.Wrap('EXCEPTION:')
                        self.Wrap(traceback.format_exc())
                        self.Wrap('-------------------------------------------------------')
        # Print message in Python Window, if open
        try:
            print(message)
        except Exception:
            self.Wrap('-------------------------------------------------------')
            self.Wrap('EXCEPTION:')
            self.Wrap(traceback.format_exc())
            self.Wrap('-------------------------------------------------------')
        sys.stdout.flush()
        return

    def Wrap(self, message):
        # Local Variable definitions
        ListOfSplitLinesLists = []
        # Skip wrapping for " " Messages
        if message == " ":
            self.Write(message)
            return
        if message == "":
            self.Write(message)
            return
        # Convert message from types that cause errors with .splitlines()
        if str(type(message)).startswith("<type 'exceptions."):
            message = str(message)
        if type(message) == type(None):
            message = str(message)
        if type(message) == bool:
            message = str(message)
        if type(message) == int:
            message = str(message)
        if type(message) == float:
            message = str(message)
        # Determine how to handle message
        if (type(message) != list and type(message) != tuple):
            # Split lines indicated by /n into a list of separate strings
            SplitLinesList = message.splitlines()
            # Append new list of lines into the ListOfSplitLinesLists
            ListOfSplitLinesLists.append(SplitLinesList)
        else:
            # Iterate over a list object
            for item in message:
                # Split lines indicated by /n into a list of separate strings
                SplitLinesList = item.splitlines()
                # Append new list of lines into the ListOfSplitLinesLists
                ListOfSplitLinesLists.append(SplitLinesList)
                del SplitLinesList
        # Iterate over a list of lists (ListOfSplitLines)
        for SplitLinesList in ListOfSplitLinesLists:
            # Iterate over the sub-list
            for Line in SplitLinesList:
                # Wrap all individual lines, which creates a new list
                WrappedLinesList = self.Wrapper.wrap(Line)
                for WrappedLine in WrappedLinesList:
                    self.Write(WrappedLine)
        return

    def Time(self, StartTime, Task):
        elapsed_time = (datetime.now() - StartTime).seconds
        
        if elapsed_time < 61:
            seconds = str(int(elapsed_time))
            time_str = "{} took {} seconds to complete".format(Task, seconds)
        
        if elapsed_time > 60:
            minutes = int(elapsed_time / 60)
            seconds = int(elapsed_time - (minutes * 60))
            time_str = "{} took {} minutes and {} seconds to complete".format(Task,
                                                                              minutes,
                                                                              seconds)
        if elapsed_time > 3600:
            hours = int(elapsed_time / 3600)
            minutes = int((elapsed_time - (hours * 3600)) / 60)
            seconds = int((elapsed_time - (hours * 3600) - (minutes * 60)))
            time_str = "{} took {} hours, {} minutes, and {} seconds to complete".format(Task,
                                                                                         hours,
                                                                                         minutes,
                                                                                         seconds)
        if elapsed_time > 86400:
            days = int(elapsed_time / 86400)
            used_seconds = days * 86400
            hours = int((elapsed_time - used_seconds) / 3600)
            used_seconds += (hours * 3600)
            minutes = int((elapsed_time - used_seconds) / 60)
            used_seconds += (minutes * 60)
            seconds = int(elapsed_time - used_seconds)
            time_str = "{} took {} days, {} hours, {} minutes, and {} seconds to complete".format(Task,
                                                                                                  days,
                                                                                                  hours,
                                                                                                  minutes,
                                                                                                  seconds)
        self.Wrap(time_str)
        self.print_separator_line()
        return

    def send_log(self):
        """
        If Outlook Installed:
        Drafts and email with the current error log as an attachment directed to me

        If Outlook Not Installed:
        Opens the Error Log and requests that users transmit it with their error report.
        """
        recipient = 'APT-Report-Issue@usace.army.mil'
        subject = 'Antecedent Precipitation Tool Error Log'
        attachmentPath = self.Log
        outlookpath2doc = None
        for root, directories, filenames in os.walk('C:\\Program Files (x86)\\Microsoft Office'):
            for f in filenames:
                if 'OUTLOOK.EXE' in f:
                    fileName = os.path.join(root, f)
                    outlookpath2doc = '"{}"'.format(fileName)
        if outlookpath2doc is not None:
            outlookpath2doc = r'"C:\Program Files (x86)\Microsoft Office\Office15\OUTLOOK.EXE"'
            compose = '/c ipm.note'
            recipients = '/m "{}&subject={}"'.format(recipient, subject)
            attachment = '/a "' + attachmentPath + '"'
            command = ' '.join([outlookpath2doc, compose, recipients, attachment])
            subprocess.Popen(command, shell=False, stdout=subprocess.PIPE)
        else:
            self.send_log_no_outlook()

    def send_log_no_outlook(self):
        """Opens Error Log and asks the user to transmit it with their error report"""
        print("Microsoft Outlook not found on this machine. Cannot create message automatically.")
        print(' -Opening error log for user to transmit manually...')
        error_log_path = self.write_error_log()
        subprocess.Popen(error_log_path, shell=True)
        print(' -Please email this error log to "APT-Report-Issue@usace.army.mil" to assist with your error report.')
        print(' ')
        print('Ready for new input.')
        print(' ')

    def print_title(self, title):
        if self.print_length < 81:
            outer_spaces = 0
            spaces = ''
            remainder = self.print_length
        else:
            outer_spaces = 0
            spaces = ' ' * outer_spaces
            remainder = self.print_length - (outer_spaces * 2)
        # Calculate character lengths
        test_line = '{}####  {}  ####{}'.format(spaces, title, spaces)
        characters_needed = self.print_length - len(test_line)
        numLeftDashes = int(characters_needed/2)
        numRightDashes = int(characters_needed - numLeftDashes)
        leftDashes = '-' * numLeftDashes
        rightDashes = '-' * numRightDashes
        # Construct Title and Top/Bottom Lines
        topOrBottom = '{}{}'.format(spaces, "#" * remainder)
        titleLine = '{}#### {} {} {} ####'.format(spaces, leftDashes, title, rightDashes)
        # Print Title Block
        self.Write("")
        self.Write(topOrBottom)
        self.Write(titleLine)
        self.Write(topOrBottom)
        return
    def print_section(self, section):
        # Calculate character lengths
        test_line = ' # {} #'.format(section)
        characters_needed = self.print_length - len(test_line)
        numLeftDashes = int(characters_needed/2)
        if (numLeftDashes * 2) == characters_needed:
            numRightDashes = numLeftDashes
        else:
            numRightDashes = numLeftDashes + 1
        leftDashes = '-' * numLeftDashes
        rightDashes = '-' * numRightDashes
        # Construct Section Line
        sectionLine = '#{} {} {}#'.format(leftDashes, section, rightDashes)
        # Print Section Heading
        self.Write("")
        self.Write(sectionLine)
        return
    def print_separator_line(self):
        # Calculate character lengths
        Dashes = '-' * self.print_length
        # Print separator
        self.Write(Dashes)
        return
    def print_status_message(self, message):
        if self.executable_name != 'pythonw.exe':
            try:
                needed_chars = self.print_length - len(message)
                if needed_chars > 0:
                    message = message + (" "*needed_chars)
                self.prevMsgLen = len(message)
                print(message, end="\r")
                sys.stdout.flush()
            except Exception:
                pass
    def deleteLog(self):
        deleteReadOnly(self.Log)
        return
    def get_terminal_size_windows(self):
        try:
            from ctypes import windll, create_string_buffer
            # stdin handle is -10
            # stdout handle is -11
            # stderr handle is -12
            h = windll.kernel32.GetStdHandle(-12)
            csbi = create_string_buffer(22)
            res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
            if res:
                (bufx, bufy, curx, cury, wattr,
                 left, top, right, bottom,
                 maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
                self.terminal_size_x = right - left + 1
                self.terminal_size_y = sizey = bottom - top + 1
            self.print_length = self.terminal_size_x - 1
        except:
            self.print_length = 119
        return
# End of PrintLog Class

if __name__ == '__main__':
    log = PrintLog()
    