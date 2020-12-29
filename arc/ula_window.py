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


import os
import sys
import time
import tkinter
import tkinter.ttk
import subprocess

# Custom Libraries
try:
    from arc import shortcut
    from arc import get_all
except Exception:
    import shortcut
    import get_all


USACE_ULA_TEXT = """This software was developed by United States Army Corps of Engineers (USACE)
employees in the course of their official duties.  USACE used copyrighted,
open source code to develop this software, as such this software 
(per 17 USC § 101) is considered "joint work."  Pursuant to 17 USC § 105,
portions of the software developed by USACE employees in the course of their
official duties are not subject to copyright protection and are in the public
domain.

USACE assumes no responsibility whatsoever for the use of this software by
other parties, and makes no guarantees, expressed or implied, about its
quality, reliability, or any other characteristic. 

The software is provided "as is," without warranty of any kind, express or
implied, including but not limited to the warranties of merchantability,
fitness for a particular purpose, and noninfringement.  In no event shall the
authors or U.S. Government be liable for any claim, damages or other
liability, whether in an action of contract, tort or otherwise, arising from,
out of or in connection with the software or the use or other dealings in the
software.

Public domain portions of this software can be redistributed and/or modified
freely, provided that any derivative works bear some notice that they are
derived from it, and any modified versions bear some notice that they have
been modified. 

Copyrighted portions of the software are annotated within the source code.
Open Source Licenses, included in the source code, apply to the applicable
copyrighted portions.  Copyrighted portions of the software are not in the
public domain."""


class Main(object):
    """GUI for the ULA of the  Antecedent Precipitation Tool"""

    def __init__(self):
        # Find Root Folder
        module_path = os.path.dirname(os.path.realpath(__file__))
        root_folder = os.path.split(module_path)[0]

        # Create Master Frame
        self.master=tkinter.Tk()
        self.master.geometry("712x460+431+132")
        self.master.minsize(712, 440)
        self.master.maxsize(1370, 749)
        self.master.resizable(1, 1)
        self.master.title("User Licence Agreement - Antecedent Precipitation Tool")

        # Set Window Icon
        try:
            images_folder = os.path.join(root_folder, 'images')
            graph_icon_file = os.path.join(images_folder, 'Graph.ico')
            self.master.wm_iconbitmap(graph_icon_file)
        except Exception:
            images_folder = os.path.join(sys.prefix, 'images')
            graph_icon_file = os.path.join(images_folder, 'Graph.ico')
            self.master.wm_iconbitmap(graph_icon_file)


        self.label_1=tkinter.ttk.Label(self.master,
                               text="Please review and accept the user licence agreement to proceed",
                               font='Helvetica 12 bold')
        self.label_1.grid(row=0, column=0, padx=0, pady=0)

        self.text_frame = tkinter.ttk.Frame(self.master)
        self.text_frame.grid(row=1, column=0, sticky="new", padx=30, columnspan=1)


        self.agreement_text = tkinter.Text(self.text_frame, height=20, width=79) # creating a textbox for getting address
        self.scrollbar = tkinter.ttk.Scrollbar(self.text_frame)  # making a scrolbar with entry test text field
        self.agreement_text.config(yscrollcommand=self.scrollbar.set)  # setting scrolbar to y-axis
        self.scrollbar.config(command=self.agreement_text.yview)  # setting the scrolbar to entry test textbox
        self.agreement_text.insert('end', USACE_ULA_TEXT) # Inserting the License 
        self.agreement_text.config(state='disabled')
        self.agreement_text.grid(column=0, row=0, sticky='W') # set entry to Specific column of bottom frame grid
        self.scrollbar.grid(column=1, row=0, sticky='nsw') # set self.scrollbar to Specific column of bottom frame grid



        # Create Secondary Frame for bottom buttons.
        self.f1 = tkinter.ttk.Frame(self.master)
        self.f1.grid(row=3, column=0, sticky="nsew", pady=2, columnspan=2, rowspan=2)

        self.var1 = tkinter.IntVar()

        self.checkbox = tkinter.ttk.Checkbutton(self.f1,
                                        text="I have read and accept the terms of the license agreement",
                                        variable=self.var1,
                                        command=self.checkboxChecked)

        self.checkbox.grid(row=1, column=0, padx=25, pady=10)

        # Create Secondary Frame for Buttons
        self.f2 = tkinter.ttk.Frame(self.master)
        self.f2.grid(row=5, column=0, sticky="nsew")

        self.button_accept = tkinter.ttk.Button(self.f2,
                                        text="Submit",
                                        state='disabled',
                                        command=self.click_accept_button)
        self.button_cancel = tkinter.ttk.Button(self.f2,
                                        text="Cancel",
                                        command=self.click_cancel_button)
        self.button_accept.grid(row=0, column=0, pady=10, padx=140)
        self.button_cancel.grid(row=0, column=1, pady=10, padx=140)

        # Configure rows and columns
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        # a trick to activate the window (on windows 7 & 10)
        self.master.deiconify()

    def checkboxChecked(self):
        if self.var1.get()==1:
            self.button_accept.config(state='normal')
        else:
            self.button_accept.config(state='disabled')

    def click_accept_button(self):
        self.master.destroy() # Close ULA window
        self.write_ula_accepted_file()
        print('Checking for a newer version of the APT...')
        get_all.main()
        print('Checking for all required images...')
        get_all.ensure_images()
        print('Checking for Watershed Boundary Dataset - HUC2.shp...')
        get_all.ensure_wbd_folder()
        print('Checking for U.S. Boundary dataset...')
        get_all.ensure_us_shp_folder()
        print('Checking for NOAA Climate Divisions dataset...')
        get_all.ensure_climdiv_folder()
        print('Checking for latest nationwide cache of the Web-based Watershed Interactive Modeling Program (WebWIMP) results...')
        get_all.ensure_WIMP()
        print('Checking for all additional binaries required for exectuion...')
        get_all.ensure_binaries()
        print("All checks completed successfully.")
        print("")
        print('Launching APT...')
        module_folder = os.path.dirname(os.path.realpath(__file__))
        root_folder = os.path.split(module_folder)[0]
        main_exe_path = '"{}\\main_ex.exe"'.format(root_folder)
        test = subprocess.Popen(main_exe_path, shell=True)
        time.sleep(2)
        x = test.poll()
        if x == 4294967295:
            print('The APT is malfunctioning, likely due to a failed update.')
            print('  Attempting to repair the directory...')
            get_all.attempt_repair()
            print('Repair package installed successfully.  Attempting to run main EXE again...')
            test = subprocess.Popen(main_exe_path, shell=True)
            time.sleep(2)
            x = test.poll()
            if x == 4294967295:
                print('Repair was unsuccessful.  Please email APT-Report-Issue@usace.army.mil')
                print('  to apprise them of the current situation.  If you try the tool again')
                print('  later, updates will likely have been made to correct the issue.')
                time.sleep(1)
                print('Closign in 5 seconds...')
                time.sleep(5)
        sys.exit()

    def click_cancel_button(self):
        self.master.destroy() # Close ULA window
        return False
    
    def write_ula_accepted_file(self):
        # Define path for the ula_accepted_file
        module_path = os.path.dirname(os.path.realpath(__file__))
        root_folder = os.path.split(module_path)[0]
        ula_accepted_file = os.path.join(root_folder, 'ula_accepted')
        try:
            # Get network information
            process = subprocess.Popen("ipconfig.exe",
                                       shell=True,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       universal_newlines=True)
            output, error = process.communicate()
            # Test if user is on USACE network
            internal_user = 'usace.army.mil' in output
            if internal_user:
                # Create a ula_accepted file to stop the ULA window from opening in the future
                with open(ula_accepted_file, 'w') as accept_file:
                    accept_file.write('True')
        except Exception:
            pass # Because this step doesn't really matter

    def run(self):
        # Find "ula_accepted.txt"
        module_path = os.path.dirname(os.path.realpath(__file__))
        root_folder = os.path.split(module_path)[0]
        ula_accepted_file = os.path.join(root_folder, 'ula_accepted')
        ula_accepted_file_exists = os.path.exists(ula_accepted_file)
        if ula_accepted_file_exists:
            self.click_accept_button()
        else:
            self.master.mainloop()

if __name__ == '__main__':
    APP = Main()
    APP.run()
