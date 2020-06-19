# Import Built-In Libraries
import os
import sys
import time
import subprocess

# FUNCTION DEFINITIONS

def check_output(command,console):
    """This function allows me the main process to receive the output from an external .exe process without queues"""
    if console == True:
        process = subprocess.Popen(command, close_fds=True, creationflags = subprocess.CREATE_NEW_CONSOLE)
        return
    else:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        output,error = process.communicate()
        returncode = process.poll()
        return returncode,output
# End of check_output


# CLASS DEFINITIONS

class cmdString(object):
    """This function simplifies the programmatic generation/execution of command line processes"""

    def __init__(self):
        self.command = []
        self.command_string = ""

    def AddStringInQuotes(self,String):
        """Retains '"' around directories to protect from space breaks in the CMD interpreter"""
        self.command.append('"'+String+'"')
        return

    def AddString(self,String):
        self.command.append(String)
        return

    def Batch(self):
        # Determine number of commands in command list
        command_length = len(self.command)
        # Create command string for printing / debugging
        self.command_string = str(self.command[0])
        # Remove quotes from first item in command list
        self.command[0] = self.command[0].strip('"')
        for i in range(1, command_length):
            # Keep self.command_string updated (for printing/debugging)
            self.command_string = self.command_string + ' ' + str(self.command[i])
            # Remove quotes from command list item
            self.command[i] = self.command[i].strip('"')
        # Print the string version of the command list
        print('Command line string to be executed:')
        print(self.command_string)
        print(' ')
        bat = r"C:\Temp\CMD.bat"
        B = JLog.PrintLog(Delete=True,Log=bat,Width=1000)
        B.Write(self.command_string)
        returncode,output = check_output(bat, True)

    def Execute(self):
        # Determine number of commands in command list
        command_length = len(self.command)
        # Create command string for printing / debugging
        self.command_string = str(self.command[0])
        # Remove quotes from first item in command list
        self.command[0] = self.command[0].strip('"')
        for i in range(1, command_length):
            # Keep self.command_string updated (for printing/debugging)
            self.command_string = self.command_string + ' ' + str(self.command[i])
            # Remove quotes from command list item
            self.command[i] = self.command[i].strip('"')
        # Print the string version of the command list
        print('Command line string to be executed:')
        print(self.command_string)
        print(' ')
        # Run command
        print(str(time.ctime())+" - Executing command...")
        returncode,output = check_output(self.command, False)
        # Report output
        print('Command line output:')
        print(output)
        # Check return code
        if returncode != 0:
            print('Error: Execution failed.')
        return

    def ExecuteConsole(self):
        # Determine number of commands in command list
        command_length = len(self.command)
        # Create command string for printing / debugging
        self.command_string = str(self.command[0])
        # Remove quotes from first item in command list
        self.command[0] = self.command[0].strip('"')
        for i in range(1, command_length):
            # Keep self.command_string updated (for printing/debugging)
            self.command_string = self.command_string + ' ' + str(self.command[i])
            # Remove quotes from command list item
            self.command[i] = self.command[i].strip('"')
        # Print the string version of the command list
        print('Command line string to be executed:')
        print(self.command_string)
        print(' ')
        # Run command
        print(str(time.ctime())+" - Executing command...")
        check_output(self.command, True)
        return
# end of cmdString class

# Function definitions
def usepip(name,pypath,packagePath,extraCMD=None):
    print(' ')
    print('Installing '+name+'...')
    e = cmdString()
    e.AddStringInQuotes(pypath)
    e.AddString('-m')
    e.AddString('pip')
    e.AddString('install')
    if extraCMD is not None:
        if type(extraCMD) == list:
            for item in extraCMD:
                e.AddString(item)
        else:
            e.AddString(extraCMD)
    e.AddStringInQuotes(packagePath)
    e.Execute()
    del e
    return
