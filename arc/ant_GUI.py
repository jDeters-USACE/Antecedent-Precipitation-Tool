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
##            ant_GUI.py            ##
##  ------------------------------- ##
##     Written by: Jason Deters     ##
##      Edited by: Joseph Gutenson  ##
##      Edited by: Chase Hamilton   ##
##  ------------------------------- ##
##    Last Edited on:  2022-11-10   ##
##  ------------------------------- ##
######################################

"""
Graphical user interface for the Antecedent Precipitation Tool
"""

import pickle



# Import Standard Libraries
import tkinter
import tkinter.ttk
import tkinter.filedialog
import os
import sys
import subprocess
from datetime import datetime, timedelta
import ftplib

# Import 3rd-Party Libraries
import PyPDF2
import requests

# Find module path
MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
# Find ROOT folder
ROOT = os.path.split(MODULE_PATH)[0]

# Import Custom Libraries
try:
    from . import anteProcess
    from . import huc_query
    from . import custom_watershed_query
    from . import check_usa
    from . import watershed_summary
    from . import help_window
    from . import get_all
    from . import netcdf_parse_all
    from .utilities import JLog
except Exception:
    # Old unfrozen version backwards compatibility step
    import anteProcess
    import huc_query
    import custom_watershed_query
    import check_usa
    import watershed_summary
    import help_window
    import get_all
    import netcdf_parse_all
    from utilities import JLog

"""
    # Add utilities folder to path directly
    PYTHON_SCRIPTS_FOLDER = os.path.join(ROOT, 'Python Scripts')
    TEST = os.path.exists(PYTHON_SCRIPTS_FOLDER)
    if TEST:
        sys.path.append(PYTHON_SCRIPTS_FOLDER)
        UTILITIES_FOLDER = os.path.join(PYTHON_SCRIPTS_FOLDER, 'utilities')
        sys.path.append(UTILITIES_FOLDER)
    else:
        ARC_FOLDER = os.path.join(ROOT, 'arc')
        sys.path.append(ARC_FOLDER)
        UTILITIES_FOLDER = os.path.join(ARC_FOLDER, 'utilities')
        sys.path.append(UTILITIES_FOLDER)
    import JLog
"""

# Version stuff
get_all.ensure_version_file()
VERSION_FILES_FOLDER = os.path.join(ROOT, 'v')
VERSION_FILE_PATH = os.path.join(VERSION_FILES_FOLDER, 'main_ex')
with open(VERSION_FILE_PATH, 'r') as VERSION_FILE:
    for line in VERSION_FILE:
        VERSION_STRING = line.replace('\n','')
        VERSION_LIST = VERSION_STRING.split('.')
        VERSION_FOR_PATHS = 'v{}_{}_{}'.format(VERSION_LIST[0], VERSION_LIST[1], VERSION_LIST[2])
        break

def click_help_button():
    help_app = help_window.HelpWindow()
    help_app.run()

class AntGUI(object):
    """GUI for the Antecedent Precipitation Tool"""

    def __init__(self):
        self.row = 0
        self.separators = []
        self.date_separators = []
        self.date_labels = []
        self.date_entry_boxes = []
        self.custom_watershed_fields_active = False
        # Define class attributes
        self.rain_instance = None
        self.snow_instance = None
        self.snow_depth_instance = None
        self.input_list_list_prcp = []
        self.input_list_list_snow = []
        self.input_list_list_snwd = []
        self.show = False
        # Define Local Variables
        root_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

        # Create PrintLog
        self.L = JLog.PrintLog(Delete=True)
        # Announce GUI
        self.L.Wrap("Launching Graphical User Interface...")
        self.L.Wrap('')
        self.L.Wrap('')
        self.L.Wrap('Ready for Input!')
        self.L.Wrap('')

        # Create UI Object
        self.master = tkinter.Tk()
        # Add Title
        self.master.title('Antecedent Precipitation Tool')
        self.master.maxsize(500, 1500)
        self.master.resizable(1, 1)

        # Set GUI Window Icon and Create Folder Image Object
        try:
            graph_icon_file = root_folder + '/images/Graph.ico'
            self.master.wm_iconbitmap(graph_icon_file)
            folder_icon_path = root_folder + '/images/folder.gif'
            self.folder_image = tkinter.PhotoImage(file=folder_icon_path)
            plus_icon_path = root_folder + '/images/Plus.gif'
            self.PLUS_IMAGE = tkinter.PhotoImage(file=plus_icon_path)
            minus_icon_path = root_folder + '/images/Minus.gif'
            self.minus_image = tkinter.PhotoImage(file=minus_icon_path)
            question_icon_path = root_folder + '/images/Question.gif'
            self.question_image = tkinter.PhotoImage(file=question_icon_path)
            waterfall_path = root_folder + '/images/Traverse_80%_503.gif'
            waterfall_path = root_folder + '/images/Traverse_67%_1000.gif'
            waterfall_path = root_folder + '/images/Traverse_40%_503.gif'
            self.waterfall = tkinter.PhotoImage(file=waterfall_path)
        except Exception:
            images_folder = os.path.join(sys.prefix, 'images')
            graph_icon_file = os.path.join(images_folder, 'Graph.ico')
            self.master.wm_iconbitmap(graph_icon_file)
            folder_icon_path = os.path.join(images_folder, 'folder.gif')
            self.folder_image = tkinter.PhotoImage(file=folder_icon_path)
            plus_icon_path = os.path.join(images_folder, 'Plus.gif')
            self.PLUS_IMAGE = tkinter.PhotoImage(file=plus_icon_path)
            minus_icon_path = os.path.join(images_folder, 'Minus.gif')
            self.minus_image = tkinter.PhotoImage(file=minus_icon_path)
            question_icon_path = os.path.join(images_folder, 'Question.gif')
            self.question_image = tkinter.PhotoImage(file=question_icon_path)
            waterfall_path = os.path.join(images_folder, 'Traverse_40%_503.gif')
            self.waterfall = tkinter.PhotoImage(file=waterfall_path)

        self.background_label = tkinter.Label(self.master, image=self.waterfall)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        #---GRIDDED PRECIPITATION---#

        self.gridded = False
        self.grid_selection = tkinter.Checkbutton(self.master, text='Use Gridded Precipitation?',
                                                 offvalue=0, onvalue=1, command=self.set_grid_input,)
        self.grid_selection.grid(row=self.row, column=0, sticky='nw', columnspan=1)
        self.grid_selection.deselect()

        #---HELP BUTTON---#
        self.help_button = tkinter.ttk.Button(self.master, text='Help / More Info', image=self.question_image, command=click_help_button)
        #self.help_button = tkinter.Button(self.master, text='?', command=click_help_button, font='Helvetica 12 bold', fg="orange")
        self.help_button.grid(row=self.row, column=2, sticky='ne', columnspan=1)
        self.row += 1

        #---SEPARATOR---#
        self.line_style = tkinter.ttk.Style()
        self.line_style.configure("Line.TSeparator", background="#000000")
        separator = tkinter.ttk.Separator(self.master, orient="horizontal", style="Line.TSeparator")
        separator.grid(row=self.row, sticky='ew', columnspan=3, pady=3, padx=4)
        self.separators.append(separator)
        self.row += 1

        #---LAT, LON, SCOPE LABELS---#
        self.label_latitude = tkinter.ttk.Label(self.master, text="Latitude (DD):")
        self.label_longitude = tkinter.ttk.Label(self.master, text="Longitude (-DD):")
#        self.label_watershed_scope = tkinter.ttk.Label(self.master, text="Geographic Scope")
        self.label_watershed_scope = tkinter.ttk.Label(self.master, text="Scope")
        self.label_latitude.grid(row=self.row, column=0, sticky='ws', padx=4, pady=0)
        self.label_longitude.grid(row=self.row, column=1, sticky='ws', padx=3, pady=0)
        self.label_watershed_scope.grid(row=self.row, column=2, sticky='ws', padx=3, pady=1)
        self.row += 1

        #---LAT, LON, SCOPE ENTRIES---#
        self.ENTRY_LATITUDE = tkinter.ttk.Entry(self.master, width=15)
        self.ENTRY_LONGITUDE = tkinter.ttk.Entry(self.master, width=15)
        self.watershed_scope_string_var = tkinter.StringVar()
        self.watershed_scope_string_var.set('Single Point')
        options = ['Single Point',
                   'Single Point', # It was not showing up in the list, but did when duplicated for some reason
                   'HUC12',
                   'HUC10',
                   'HUC8',
                   'Custom Polygon']
        self.watershed_scope_menu = tkinter.ttk.OptionMenu(self.master,
                                                           self.watershed_scope_string_var,
                                                           *(options),
                                                           command=self.watershed_selection)
        self.ENTRY_LATITUDE.grid(row=self.row, column=0, padx=3, sticky='w')
        self.ENTRY_LONGITUDE.grid(row=self.row, column=1, padx=3, sticky='w')
        self.watershed_scope_menu.grid(row=self.row, column=2, sticky='w', padx=3)
        self.row += 1

        #---SEPARATOR---#
        separator = tkinter.ttk.Separator(self.master, orient="horizontal", style="Line.TSeparator")
        separator.grid(row=self.row, sticky='ew', columnspan=3, pady=3, padx=4)
        self.separators.append(separator)
        self.row += 1

        #---DATES FRAME---#
        self.dates_frame = tkinter.ttk.Frame(self.master)
        self.dates_frame.grid(row=self.row, column=0, sticky="nsew", padx=0, pady=0, columnspan=3)
        self.background_label2 = tkinter.Label(self.dates_frame, image=self.waterfall)
        self.background_label2.place(x=0, y=0, relwidth=1, relheight=1)
        self.row += 1
        self.plus_button = tkinter.ttk.Button(self.dates_frame, command=self.add_date, image=self.PLUS_IMAGE)
        self.minus_button = tkinter.ttk.Button(self.dates_frame, image=self.minus_image, command=self.minus_function)

        #---SEPARATOR---#
        separator = tkinter.ttk.Separator(self.master, orient="horizontal", style="Line.TSeparator")
        separator.grid(row=98, sticky='ew', columnspan=3, pady=0, padx=0)
        self.separators.append(separator)
        self.row += 1

        #---BOTTOM ROW BUTTONS---#
        self.BUTTON_CALCULATE = tkinter.ttk.Button(self.master, text='Calculate', command=self.calculate_and_graph)
        self.batch_style_string_var = tkinter.StringVar()
        self.batch_style_string_var.set('Switch to Date Range')
        self.BUTTON_BATCH = tkinter.ttk.Button(self.master, textvariable=self.batch_style_string_var, command=self.switch_batch_style)
        self.BUTTON_QUIT = tkinter.ttk.Button(self.master, text='Quit', command=self.quit_command)
        self.BUTTON_CALCULATE.grid(row=99, column=0, padx=5, pady=5, columnspan=2, sticky='w')
        self.BUTTON_BATCH.grid(row=99, column=1, padx=1, pady=5, sticky='w')
        self.BUTTON_QUIT.grid(row=99, column=2, padx=1, pady=5, sticky='e')

        # Create Watershed Label/Buttons
        self.LABEL_CUSTOM_WATERSHED_NAME = tkinter.ttk.Label(self.master, text='Custom Watershed Name:')
        self.ENTRY_CUSTOM_WATERSHED_NAME = tkinter.ttk.Entry(self.master)
        self.LABEL_CUSTOM_WATERSHED_FILE = tkinter.ttk.Label(self.master, text='Custom Watershed Shapefile:')
        self.ENTRY_CUSTOM_WATERSHED_FILE = tkinter.ttk.Entry(self.master)
        self.BUTTON_BROWSE_SHAPEFILE = tkinter.ttk.Button(self.master, text='Browse', command=self.ask_shapefile, image=self.folder_image)

# Reverse compatibility ITEMS (For the non-compiled version)
        self.BUTTON_BROWSE_DIR = tkinter.ttk.Button(self.master, text='Browse', command=self.ask_directory, image=self.folder_image)
        self.ENTRY_OUTPUT_FOLDER = tkinter.ttk.Entry(self.master)
        default_save_folder = os.path.join(ROOT,'Outputs')
        self.ENTRY_OUTPUT_FOLDER.insert(0, default_save_folder)
        self.ENTRY_IMAGE_NAME = tkinter.ttk.Entry(self.master)
        self.ENTRY_IMAGE_SOURCE = tkinter.ttk.Entry(self.master)
        self.RADIO_VARIABLE_PARAMETER = tkinter.StringVar()
        self.RADIO_VARIABLE_PARAMETER.set('Rain')  # initialize
        self.RADIO_BUTTON_PARAMETER_RAIN = tkinter.ttk.Radiobutton(self.master, text='Rain', variable=self.RADIO_VARIABLE_PARAMETER, value='Rain')
        self.RADIO_BUTTON_PARAMETER_SNOW = tkinter.ttk.Radiobutton(self.master, text='Snow', variable=self.RADIO_VARIABLE_PARAMETER, value='Snow')
        self.RADIO_BUTTON_PARAMETER_SNOW_DEPTH = tkinter.ttk.Radiobutton(self.master, text='Snow Depth', variable=self.RADIO_VARIABLE_PARAMETER, value='Snow Depth')
        self.RADIO_VARIABLE_Y_AXIS = tkinter.StringVar()
        self.RADIO_VARIABLE_Y_AXIS.set(False)  # initialize
        self.RADIO_BUTTON_Y_AXIS_VARIABLE = tkinter.ttk.Radiobutton(self.master, text='Variable', variable=self.RADIO_VARIABLE_Y_AXIS, value=False)
        self.RADIO_BUTTON_Y_AXIS_CONSTANT = tkinter.ttk.Radiobutton(self.master, text='Constant', variable=self.RADIO_VARIABLE_Y_AXIS, value=True)
        self.RADIO_VARIABLE_FORECAST = tkinter.StringVar()
        self.RADIO_VARIABLE_FORECAST.set(False)  # initialize
        self.RADIO_BUTTON_FORECAST_INCLUDE = tkinter.ttk.Radiobutton(self.master, text='Include Forecast', variable=self.RADIO_VARIABLE_FORECAST, value=True)
        self.RADIO_BUTTON_FORECAST_EXCLUDE = tkinter.ttk.Radiobutton(self.master, text="Don't Include Forecast", variable=self.RADIO_VARIABLE_FORECAST, value=False)
        self.STRING_VARIABLE_LABEL_FOR_SHOW_OPTIONS_BUTTON = tkinter.StringVar()
        self.STRING_VARIABLE_LABEL_FOR_SHOW_OPTIONS_BUTTON.set('Show Options')
# Reverse compatibility ITEMS (For the non-compiled version)

        # Create all elements and grid_forget then recreate starting style
        self.setup_unique_dates()
        self.setup_date_range()
        self.setup_csv_input()
        self.wipe_date_elements()
        self.setup_unique_dates()

        # Configure rows/columns
        self.master.geometry("+800+400")
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        # a trick to activate the window (on Windows 7 & 10)
        self.master.deiconify()
    # End of __init__ method

    def run(self):
        """Starts the GUI's TKinter mainloop"""
        # start mainloop
        self.master.mainloop()
    # End of run method

    def switch_batch_style(self):
        current_style = self.batch_style_string_var.get()
        if current_style == 'Switch to Date Range':
            self.wipe_date_elements()
            self.setup_date_range()
            self.batch_style_string_var.set('Switch to CSV Input')
        elif current_style == 'Switch to CSV Input':
            self.wipe_date_elements()
            self.setup_csv_input()
            self.batch_style_string_var.set('Switch to Unique Dates')
        elif current_style == 'Switch to Unique Dates':
            self.wipe_date_elements()
            self.setup_unique_dates()
            self.batch_style_string_var.set('Switch to Date Range')
        # Configure rows/columns
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

    def setup_unique_dates(self):
        # Add Upper Label
        self.upper_label_unique = tkinter.ttk.Label(self.dates_frame, text='Run a single date or click "+" to add more')
        self.upper_label_unique.grid(row=0, column=0, columnspan=7, sticky='ew', padx=60)
        self.upper_label_separator = tkinter.ttk.Separator(self.dates_frame, orient="horizontal", style="Line.TSeparator")
        self.upper_label_separator.grid(row=1, sticky='ew', columnspan=7, pady=3)
        # Add Format labels
        self.date_format_label = tkinter.ttk.Label(self.dates_frame, text='YYYY-MM-DD')
        self.date_format_label.grid(row=2, column=1, sticky='e')
        self.day_format_label = tkinter.ttk.Label(self.dates_frame, text='#')
        self.day_format_label.grid(row=2, column=0, sticky='w', padx=35)
        self.top_row_separator = tkinter.ttk.Separator(self.dates_frame, orient="horizontal", style="Line.TSeparator")
        self.top_row_separator.grid(row=3, sticky='ew', columnspan=7, pady=3)
        # Add first day
        self.add_date()

    def add_date(self):
        # Calc Rows
        obs_num = len(self.date_labels)
        if obs_num == 0:
            # Calc spacing
            obs_num_str = ' YYYY-MM-DD:'
            obs_row = obs_num + 4
        else:
            obs_row = (obs_num * 2) + 4
            # Minus Button
            self.minus_button.grid_forget()
            self.minus_button.grid(row=obs_row, column=4, sticky='e', padx=1)
        obs_num_str = '{}'.format((obs_num + 1))
        sep_row = obs_row + 1
        # Label
#        date_label = tkinter.ttk.Label(self.dates_frame, text='Observation Date{}(YYYY-MM-DD):  '.format(obs_num_str))
        date_label = tkinter.ttk.Label(self.dates_frame, text='{}'.format(obs_num_str))
        date_label.grid(row=obs_row, column=0, sticky='w', padx=35)
        self.date_labels.append(date_label)
        # Entry
        date_entry = DateEntry(self.dates_frame, font=('Helvetica', 10, 'normal'), border=0)
        date_entry.grid(row=obs_row, column=1, sticky='e')
        self.date_entry_boxes.append(date_entry)
        # Plus Button
        self.plus_button.grid_forget()
        self.plus_button.grid(row=obs_row, column=5, sticky='e', padx=1)
        #---SEPARATOR---#
        date_separator = tkinter.ttk.Separator(self.dates_frame, orient="horizontal", style="Line.TSeparator")
        date_separator.grid(row=sep_row, sticky='ew', columnspan=7, pady=3)
        self.date_separators.append(date_separator)
        # Focus on new element
        date_entry.entry_year.focus()

    def minus_function(self):
        num_rows = len(self.date_entry_boxes)
        if num_rows < 2:
            print('Cannot remove the only Date Entry Box!')
            print('')
            return
        else:
            # Get elements
            date_label = self.date_labels[-1]
            date_entry = self.date_entry_boxes[-1]
            date_separator = self.date_separators[-1]
            # Forget Positions
            date_label.grid_forget()
            date_entry.grid_forget()
            date_separator.grid_forget()
            # Remove from lists
            self.date_labels.remove(date_label)
            self.date_entry_boxes.remove(date_entry)
            self.date_separators.remove(date_separator)
            # Plus Button
            obs_num = len(self.date_entry_boxes)
            if obs_num == 0:
                obs_row = obs_num + 2
            else:
                obs_row = (obs_num * 2) + 2
            sep_row = obs_row + 1
            self.plus_button.grid_forget()
            self.plus_button.grid(row=obs_row, column=5, sticky='e', padx=1)
            if obs_num > 1:
                # Minus Button
                self.minus_button.grid_forget()
                self.minus_button.grid(row=obs_row, column=4, sticky='e', padx=1)
            else:
                self.minus_button.grid_forget()

    def setup_date_range(self):
        # Upper Label
        self.upper_label_range = tkinter.ttk.Label(self.dates_frame, text='Get daily results between a Start Date and End Date')
        self.upper_label_range.grid(row=0, column=0, columnspan=3, sticky='nesw', padx=20)
        date_separator = tkinter.ttk.Separator(self.dates_frame, orient="horizontal", style="Line.TSeparator")
        date_separator.grid(row=1, sticky='ew', columnspan=5, pady=3)
        self.date_separators.append(date_separator)
        #---START DATE---#
        date_label = tkinter.ttk.Label(self.dates_frame, text='Start Date (YYYY-MM-DD):')
        date_label.grid(row=2, column=0, sticky='e')
        self.date_labels.append(date_label)
        date_entry = DateEntry(self.dates_frame, font=('Helvetica', 10, 'normal'), border=0)
        date_entry.grid(row=2, column=1, sticky='w')
        self.date_entry_boxes.append(date_entry)
        date_separator = tkinter.ttk.Separator(self.dates_frame, orient="horizontal", style="Line.TSeparator")
        date_separator.grid(row=1, sticky='ew', columnspan=5, pady=3)
        self.date_separators.append(date_separator)
        #---END DATE---#
        date_label = tkinter.ttk.Label(self.dates_frame, text='End Date (YYYY-MM-DD):')
        date_label.grid(row=4, column=0, sticky='e')
        self.date_labels.append(date_label)
        date_entry = DateEntry(self.dates_frame, font=('Helvetica', 10, 'normal'), border=0)
        date_entry.grid(row=4, column=1, sticky='w')
        self.date_entry_boxes.append(date_entry)
        date_separator = tkinter.ttk.Separator(self.dates_frame, orient="horizontal", style="Line.TSeparator")
        date_separator.grid(row=1, sticky='ew', columnspan=5, pady=3)
        self.date_separators.append(date_separator)

    def setup_csv_input(self):
        # Create/Grid
        self.upper_label_csv = tkinter.ttk.Label(self.dates_frame, text='Use a CSV file to run many dates at once')
        self.upper_label_csv.grid(row=0, column=0, columnspan=5, sticky='nesw', padx=45)
        date_separator = tkinter.ttk.Separator(self.dates_frame, orient="horizontal", style="Line.TSeparator")
        date_separator.grid(row=1, sticky='ew', columnspan=5, pady=3)
        self.date_separators.append(date_separator)
        # Create CSV Label/Entry/Button
        self.label_csv_file_path = tkinter.ttk.Label(self.dates_frame, text='CSV File Path:')
        self.entry_csv_file_path = tkinter.ttk.Entry(self.dates_frame)
        self.button_browse_csv_file_path = tkinter.ttk.Button(self.dates_frame, text='Browse', command=self.ask_csv_file, image=self.folder_image)
        # Grid CSV Label/Entry/Button
        self.label_csv_file_path.grid(row=2, sticky='sw', padx=5, pady=3, columnspan=5)
        self.entry_csv_file_path.grid(row=3, padx=5, sticky='ew', columnspan=6)
        self.button_browse_csv_file_path.grid(row=3, column=6, padx=4, pady=1)
        date_separator = tkinter.ttk.Separator(self.dates_frame, orient="horizontal", style="Line.TSeparator")
        date_separator.grid(row=4, sticky='ew', columnspan=5, pady=3)
        self.date_separators.append(date_separator)

    def wipe_date_elements(self):
        # Unique Elements
        self.upper_label_unique.grid_forget()
        self.plus_button.grid_forget()
        self.minus_button.grid_forget()
        self.upper_label_separator.grid_forget()
        self.date_format_label.grid_forget()
        self.day_format_label.grid_forget()
        self.top_row_separator.grid_forget()
        # Range Elements
        self.upper_label_range.grid_forget()
        # CSV Elements
        self.upper_label_csv.grid_forget()
        self.label_csv_file_path.grid_forget()
        self.entry_csv_file_path.grid_forget()
        self.button_browse_csv_file_path.grid_forget()
        # Sweep through Date Elements and Remove (Hopefully separately helps)
        to_remove = []
        for date_label in self.date_labels:
            date_label.grid_forget()
            to_remove.append(date_label)
        for item in to_remove:
            try:
                self.date_labels.remove(item)
            except Exception:
                pass
        to_remove = []
        for date_entry in self.date_entry_boxes:
            date_entry.grid_forget()
            to_remove.append(date_entry)
        for item in to_remove:
            try:
                self.date_entry_boxes.remove(item)
            except Exception:
                pass
        to_remove = []
        for date_separator in self.date_separators:
            date_separator.grid_forget()
            to_remove.append(date_separator)
        for item in to_remove:
            try:
                self.date_separators.remove(item)
            except Exception:
                pass

    def watershed_selection(self, event):
        """Acts on the self.watershed_scope_menu drop-down selection"""
        watershed_scale = self.watershed_scope_string_var.get()
        if watershed_scale == 'Custom Polygon':
            # Grid Custom Watershed Entry Box
            self.LABEL_CUSTOM_WATERSHED_NAME.grid(row=94, sticky='sw', padx=5, pady=3, columnspan=3)
            self.ENTRY_CUSTOM_WATERSHED_NAME.grid(row=95, padx=5, sticky='ew', columnspan=3)
            self.LABEL_CUSTOM_WATERSHED_FILE.grid(row=96, sticky='sw', padx=5, pady=3, columnspan=3)
            self.ENTRY_CUSTOM_WATERSHED_FILE.grid(row=97, padx=5, sticky='ew', columnspan=3)
            self.BUTTON_BROWSE_SHAPEFILE.grid(row=97, column=2, padx=4, pady=1, sticky='e')
        else:
            # Remove Custom Watershed Label and Entry Box
            self.LABEL_CUSTOM_WATERSHED_NAME.grid_forget()
            self.ENTRY_CUSTOM_WATERSHED_NAME.grid_forget()
            self.LABEL_CUSTOM_WATERSHED_FILE.grid_forget()
            self.ENTRY_CUSTOM_WATERSHED_FILE.grid_forget()
            self.BUTTON_BROWSE_SHAPEFILE.grid_forget()
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

    def set_grid_input(self):
        self.gridded = not self.gridded

        if self.gridded:
            if netcdf_parse_all.check_thredds_status():
                self.grid_selection.select()
            else:
                error_message = "Unable to retrieve data from www.ncei.noaa.gov/thredds.\n" + \
                                "Gridded data is currently unavailable.\n" + \
                                "\n" + \
                                "If gridded data support is needed, please wait a few minutes and try again.\n" + \
                                "\n" + \
                                "If this error persists, please let us know at:\n" + \
                                "APT-Report-Issue@usace.army.mil"

                tkinter.messagebox.showinfo(title="Warning",
                                        message=error_message)

                self.gridded = False
                self.grid_selection.deselect()

        else:
            self.grid_selection.deselect()


    def send_log(self):
        """
        Drafts and email with the current error log as an attachment directed to me
        """
        self.L.send_log()
    # End of send_log method

    def quit_command(self):
        """
        Closes the program.
        """
        self.master.destroy()
    # End of quit_command method

    def ask_directory(self):
        """Returns a selected directoryname."""
        # defining options for opening a directory
        dir_opt = options = {}
        options['initialdir'] = 'C:\\'
        options['mustexist'] = False
        options['parent'] = self.master
        options['title'] = 'Select a folder within which PDFs will be exported'
        selected_directory = tkinter.filedialog.askdirectory(**dir_opt)
        self.ENTRY_OUTPUT_FOLDER.delete(0, 'end')
        self.ENTRY_OUTPUT_FOLDER.insert(10, selected_directory)
        return
    # End ask_directory method

    def ask_csv_file(self):
        """Returns a selected CSV file."""
        # Find module path, root folder, batch folder, batch template path
        module_path = os.path.dirname(os.path.realpath(__file__))
        root = os.path.split(module_path)[0]
        batch_folder = os.path.join(root, 'Batch')
        default_template_path = os.path.join(batch_folder, 'APT Batch Template.csv')
        # Test for presence of Batch Template CSV
        template_exists = os.path.exists(default_template_path)
        if not template_exists:
            try:
                # Ensure Batch Folder Exists
                try:
                    os.makedirs(batch_folder)
                except Exception:
                    pass
                with open(default_template_path, 'w') as CSV:
                    CSV.write('Year (yyyy),Month (m or mm),Day (d or dd)\n')
            except Exception:
                pass
#        initial_folder = os.path.join(sys.prefix, 'Batch_Files')
        # Find module path, root folder, batch folder, batch template path
        module_path = os.path.dirname(os.path.realpath(__file__))
        root = os.path.split(module_path)[0]
        batch_folder = os.path.join(root, 'Batch')
        default_template_path = os.path.join(batch_folder, 'APT Batch Template.csv')
        # define options for opening a file
        file_opt = options = {}
        options['defaultextension'] = '.csv'
        options['filetypes'] = [('CSV file', '.csv'), ('all files', '.*')]
        options['initialdir'] = batch_folder
        options['initialfile'] = 'APT Batch Template.csv'
        options['parent'] = self.master
        options['title'] = "Locate the batch CSV file for this project"
        # get filename
        filename = tkinter.filedialog.askopenfilename(**file_opt)
        self.entry_csv_file_path.delete(0, 'end')
        self.entry_csv_file_path.insert(0, filename)
    # End askfile method

    def ask_shapefile(self):
        """Returns a selected Shapefile"""
#        initial_folder = os.path.join(sys.prefix, 'Batch_Files')
        # Find module path, root folder, batch folder, batch template path
        module_path = os.path.dirname(os.path.realpath(__file__))
        root = os.path.split(module_path)[0]
        # define options for opening a file
        file_opt = options = {}
        options['defaultextension'] = '.shp'
        options['filetypes'] = [('Shapefile', '.shp')]
        options['initialdir'] = 'C:\\'
        options['parent'] = self.master
        options['title'] = "Locate the Custom Watershed Shapefile you want to analyze"
        # get filename
        filename = tkinter.filedialog.askopenfilename(**file_opt)
        self.ENTRY_CUSTOM_WATERSHED_FILE.delete(0, 'end')
        self.ENTRY_CUSTOM_WATERSHED_FILE.insert(10, filename)
        return
    # End askfile method

    def test_noaa_server(self):
        # Test whether https://www1.ncdc.noaa.gov/pub/data/ghcn/daily is accessible
        if self.ncdc_working is False:
            try:
                self.L.print_title("NOAA Server Status Check")
                self.L.Wrap('Server Base URL = https://www1.ncdc.noaa.gov/pub/data/ghcn/daily')
                self.L.Wrap("Testing if NOAA's Server is currently accessible...")
                test_url = "https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt"
                for i in range(5):
                    if i < 1:
                        self.L.Wrap('  Attempting to download: {}'.format(test_url))
                    else:
                        self.L.Wrap('  Attempt {} of 5 - Downloading: {}'.format((i+1), test_url))
                    test_connection = requests.get(test_url, timeout=15)
                    if i > 0:
                        wait = i * 2
                        self.L.Wrap('    -Giving the server {} extra seconds to respond'.format(wait))
                        time.sleep(i)
                    if test_connection.status_code > 299:
                        self.L.Wrap('    -Download failed!')
                        self.ncdc_working = False
                    else:
                        self.ncdc_working = True
                        del test_connection
                        break
            except Exception:
                self.ncdc_working = False
        # Try FTP
        if self.ncdc_working is False:
            self.L.Wrap("NOAA'S HTTP SERVER IS UNAVAILABLE - ATTEMPTING TO USE FTP SERVER AS A WORKAROUND...")
            self.L.Wrap('Server Base URL = ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily')
            self.L.Wrap("Testing if NOAA's Server is currently accessible...")
            test_url = "ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt"
            for i in range(5):
                test_url = "ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt"
                if i < 1:
                    self.L.Wrap('  Attempting to download: {}'.format(test_url))
                else:
                    self.L.Wrap('  Attempt {} of 5 - Downloading: {}'.format((i+1), test_url))
                    module_path = os.path.dirname(os.path.realpath(__file__))
                    root_folder = os.path.split(module_path)[0]
                    local_file_name = 'readme.txt'
                    local_file_path = os.path.join(root_folder, local_file_name)
                    # Delete the old file if it exists so this test works properly
                    try:
                        os.remove(local_file_path)
                    except Exception:
                        pass
                    test_url = "ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily"
                    strip_ftp = test_url[6:]
                    first_slash = strip_ftp.find('/')
                    ftp_address = strip_ftp[:first_slash]
                    ftp_folder = strip_ftp[(first_slash+1):]
                    try:
                        self.L.Wrap('   -Creating FTP Instance for {}...'.format(ftp_address))
                        ftp = ftplib.FTP(ftp_address)
                        self.L.Wrap('   -Logging in to FTP Instance...')
                        ftp.login()
                        self.L.Wrap('   -Navigating to selected folder ({})...'.format(ftp_folder))
                        ftp.cwd(ftp_folder)
                        self.L.Wrap('   -Downloading via File Transfer Protocol...')
                        ftp.retrbinary("RETR {}".format(local_file_name), open(local_file_path, 'wb').write)
                        ftp.quit()
                        del ftp
                        # Check DLY file size and switch to http if < 2 KB
                        self.L.Wrap('   -Testing file...')
                        dly_size = os.path.getsize(local_file_path)
                        if dly_size < 300: # 241 is what the 403 Forbidden error has been producing during Gov't Shutdown
                            self.L.Wrap('     -403 Forbidden error received.')
                            self.ncdc_working = False
                            try:
                                os.remove(local_file_path)
                            except Exception:
                                pass
                        else:
                            self.ncdc_working = True
                            try:
                                os.remove(local_file_path)
                            except Exception:
                                pass
                            break
                    except Exception:
                        try:
                            ftp.quit()
                            del ftp
                        except Exception:
                            pass
        if self.ncdc_working is False:
            self.L.Wrap('                   ###################')
            self.L.Wrap("  NOAA's Server is ###---OFFLINE---###")
            self.L.Wrap('                   ###################')
            self.L.Wrap('  Request terminated, as weather data is currently inaccessbile.')
            self.L.Wrap('NOTE: If you continue to receive this error, please click the "Report Issue" button to submit an error report.')
            self.L.print_separator_line()
            self.L.Wrap('')
            self.L.Wrap('Click "Calculate" to retry, or click the "?" in the top right and then "Report Issue" to send an error log to the developer.')
        else:
            self.L.Wrap("  NOAA's Servers ONLINE.  Proceeding with request...")
            self.L.print_separator_line()
            self.L.Wrap('')
    # End test_noaa_server method


    def calculate_and_graph(self):
        """
        Runs the main function with currently selected values.
            -Will run as batch if batch processes have already been entered
        """
        self.ncdc_working = False
        # Test whether NOAA's servers are online and accessible
        if self.gridded is False:
            self.test_noaa_server()
        if self.ncdc_working is True and self.gridded is False:
            try:
                current_style = self.batch_style_string_var.get()
                if current_style == 'Switch to Date Range': # Means it is currently on Unique
                    self.get_inputs_unique()
                elif current_style == 'Switch to CSV Input': # Means it is currently on Range
                    self.get_inputs_range()
                elif current_style == 'Switch to Unique Dates': #Means it is currently on CSV
                    self.get_inputs_csv()
            except Exception:
                print('The APT cannot complete this analysis.\n')
                print('The following error occurred. Please close the APT and reboot.\n')
                # self.L.Wrap(traceback.format_exc())
                raise
        if self.ncdc_working is False and self.gridded is True:
            self.L.print_title("Analyzing NOAA Gridded Dataset")
            try:
                current_style = self.batch_style_string_var.get()
                if current_style == 'Switch to Date Range': # Means it is currently on Unique
                    self.get_inputs_unique()
                elif current_style == 'Switch to CSV Input': # Means it is currently on Range
                    self.get_inputs_range()
                elif current_style == 'Switch to Unique Dates': #Means it is currently on CSV
                    self.get_inputs_csv()
            except Exception:
                print('The APT cannot complete this analysis.\n')
                print('The following error occurred. Please close the APT and reboot.\n')
                # self.L.Wrap(traceback.format_exc())
                raise

                # python = sys.executable
                # os.execl(python, python, * sys.argv)
                # self.master.mainloop()

    # End of calculate_and_graph method


    def get_inputs_unique(self):
        latitude = self.ENTRY_LATITUDE.get()
        longitude = self.ENTRY_LONGITUDE.get()
        image_name = self.ENTRY_IMAGE_NAME.get() # DISABLED
        image_source = self.ENTRY_IMAGE_SOURCE.get() # DISABLED
        save_folder = self.ENTRY_OUTPUT_FOLDER.get() # DISABLED
        watershed_scale = self.watershed_scope_string_var.get()
        custom_watershed_name = self.ENTRY_CUSTOM_WATERSHED_NAME.get()
        custom_watershed_file = self.ENTRY_CUSTOM_WATERSHED_FILE.get()
        radio = self.RADIO_VARIABLE_PARAMETER.get() # DISABLED
        fixed_y_max = self.RADIO_VARIABLE_Y_AXIS.get() # DISABLED
        forecast_enabled = self.RADIO_VARIABLE_FORECAST.get() # DISABLED
        # Iterate through dates list
        for date_entry in self.date_entry_boxes:
            params = []
            observation_year, observation_month, observation_day = date_entry.get()
            params.append(latitude)
            params.append(longitude)
            params.append(observation_year)
            params.append(observation_month)
            params.append(observation_day)
            params.append(image_name)
            params.append(image_source)
            params.append(save_folder)
            params.append(custom_watershed_name)
            params.append(custom_watershed_file)
            params.append(watershed_scale)
            params.append(radio)
            params.append(fixed_y_max)
            params.append(forecast_enabled)
            if watershed_scale == 'Single Point':
                self.calculate_or_add_batch(True, params)
            else:
                self.calculate_or_add_batch(False, params)
        if watershed_scale == 'Single Point':
            self.calculate_or_add_batch(False, params)
    # End get_inputs_unique method

    def get_inputs_range(self):
        latitude = self.ENTRY_LATITUDE.get()
        longitude = self.ENTRY_LONGITUDE.get()
        image_name = self.ENTRY_IMAGE_NAME.get() # DISABLED
        image_source = self.ENTRY_IMAGE_SOURCE.get() # DISABLED
        save_folder = self.ENTRY_OUTPUT_FOLDER.get() # DISABLED
        watershed_scale = self.watershed_scope_string_var.get()
        custom_watershed_name = self.ENTRY_CUSTOM_WATERSHED_NAME.get()
        custom_watershed_file = self.ENTRY_CUSTOM_WATERSHED_FILE.get()
        radio = self.RADIO_VARIABLE_PARAMETER.get() # DISABLED
        fixed_y_max = self.RADIO_VARIABLE_Y_AXIS.get() # DISABLED
        forecast_enabled = self.RADIO_VARIABLE_FORECAST.get() # DISABLED
        # Get Start and End dates
        start_year, start_month, start_day = self.date_entry_boxes[0].get()
        end_year, end_month, end_day = self.date_entry_boxes[1].get()
        # Convert to Datetimes
        try:
            # Get start_datetime
            if len(str(start_day)) == 1:
                start_day = '0'+str(start_day)
            else:
                start_day = str(start_day)
            if len(str(start_month)) == 1:
                start_month = '0'+str(start_month)
            else:
                start_month = str(start_month)
            start_date = str(start_year)+'-'+start_month+'-'+start_day
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            # Get end_datetime
            if len(str(end_day)) == 1:
                end_day = '0'+str(end_day)
            else:
                end_day = str(end_day)
            if len(str(end_month)) == 1:
                end_month = '0'+str(end_month)
            else:
                end_month = str(end_month)
            end_date = str(end_year)+'-'+end_month+'-'+end_day
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        except Exception as error:
            self.L.Wrap('')
            self.L.Wrap('{}!'.format(str(error).upper()))
            self.L.Wrap('')
            return
        test_datetime = start_datetime
        while test_datetime <= end_datetime:
            params = []
            # Get date values
            observation_day = test_datetime.strftime('%d')
            observation_month = test_datetime.strftime('%m')
            observation_year = test_datetime.strftime('%Y')
            params.append(latitude)
            params.append(longitude)
            params.append(observation_year)
            params.append(observation_month)
            params.append(observation_day)
            params.append(image_name)
            params.append(image_source)
            params.append(save_folder)
            params.append(custom_watershed_name)
            params.append(custom_watershed_file)
            params.append(watershed_scale)
            params.append(radio)
            params.append(fixed_y_max)
            params.append(forecast_enabled)
            if watershed_scale == 'Single Point':
                self.calculate_or_add_batch(True, params)
            else:
                self.calculate_or_add_batch(False, params)

            self.calculate_or_add_batch(True, params)
            # Advance 1 day
            test_datetime = test_datetime + timedelta(days=1)
        # Submit final request
        if watershed_scale == 'Single Point':
            self.calculate_or_add_batch(False, params)

    def get_inputs_csv(self):
        """Reads batch inputs from CSV and runs them"""
        # Get Non-CSV inputs
        latitude = self.ENTRY_LATITUDE.get()
        longitude = self.ENTRY_LONGITUDE.get()
        image_name = self.ENTRY_IMAGE_NAME.get() # DISABLED
        image_source = self.ENTRY_IMAGE_SOURCE.get() # DISABLED
        save_folder = self.ENTRY_OUTPUT_FOLDER.get() # DISABLED
        radio = self.RADIO_VARIABLE_PARAMETER.get() # DISABLED
        fixed_y_max = self.RADIO_VARIABLE_Y_AXIS.get() # DISABLED
        forecast_enabled = self.RADIO_VARIABLE_FORECAST.get() # DISABLED
        watershed_scale = self.watershed_scope_string_var.get()
        custom_watershed_name = self.ENTRY_CUSTOM_WATERSHED_NAME.get()
        custom_watershed_file = self.ENTRY_CUSTOM_WATERSHED_FILE.get()
        # Get CSV file Path
        batch_csv_file = self.entry_csv_file_path.get()
        if batch_csv_file == '':
            self.L.Wrap('')
            self.L.Wrap('No CSV file provided!')
            self.L.Wrap('')
            return
        extension = os.path.splitext(batch_csv_file)[1].lower()
        if not extension == '.csv':
            self.L.Wrap('')
            self.L.Wrap('Selected file must be in CSV format!')
            self.L.Wrap('')
            return
        exists = os.path.exists(batch_csv_file)
        if not exists:
            self.L.Wrap('')
            self.L.Wrap('Selected CSV file does not exist!')
            self.L.Wrap('')
            return
        # Collect CSV Lines as Lists
        first_line = True
        self.L.Wrap('Reading CSV File...')
        csv_lines_list = []
        with open(batch_csv_file, 'r') as lines:
            for line in lines:
                self.L.Write('{}  '.format(line.replace('\n', '')))
                if first_line:
                    first_line = False
                else:
                    # Parse CSV Line Values
                    csv_inputs = line.replace('\n', '').split(',')
                    # Append to CSV Lines List
                    csv_lines_list.append(csv_inputs)
        for line in csv_lines_list:
            params = []
            observation_year = line[0]
            observation_month = line[1]
            observation_day = line[2]
            # Process parameters list
            params.append(latitude)
            params.append(longitude)
            params.append(observation_year)
            params.append(observation_month)
            params.append(observation_day)
            params.append(image_name)
            params.append(image_source)
            params.append(save_folder)
            params.append(custom_watershed_name)
            params.append(custom_watershed_file)
            params.append(watershed_scale)
            params.append(radio)
            params.append(fixed_y_max)
            params.append(forecast_enabled)
            if watershed_scale == 'Single Point':
                self.calculate_or_add_batch(True, params)
            else:
                self.calculate_or_add_batch(False, params)
        if watershed_scale == 'Single Point':
            self.calculate_or_add_batch(False, params)
    # End batch_from_csv method



    def test_parameters(self,
                        latitude,
                        longitude,
                        observation_year,
                        observation_month,
                        observation_day,
                        image_name,
                        image_source,
                        save_folder,
                        custom_watershed_name,
                        custom_watershed_file,
                        fixed_y_max,
                        forecast_enabled):
        """Test whether or not all parameters are valid"""
        parameters_valid = True
        try:
            float(latitude)
        except Exception:
            self.L.Wrap('Latitude must be in decimal degree format!')
            parameters_valid = False
        try:
            float(longitude)
        except Exception:
            self.L.Wrap('Longitude must be in decimal degree format!')
            parameters_valid = False
        # Ensure location is within USA boundary
        in_usa = check_usa.main(latitude, longitude)
        if not in_usa:
            self.L.Wrap('Coordinates must be within the United States!')
            parameters_valid = False
        try:
            observation_year = int(observation_year)
            if observation_year < 1900:
                if str(observation_year) != '50' and str(observation_year) != '30':
                    self.L.Wrap('Year must be greater than 1900!')
                    parameters_valid = False
        except Exception:
            self.L.Wrap('Year must be a number!')
            parameters_valid = False
        try:
            observation_month = int(observation_month)
            if observation_month > 12:
                self.L.Wrap('Month cannot exceed 12!')
                parameters_valid = False
            if observation_month < 1:
                self.L.Wrap('Month cannot be less than 1!')
                parameters_valid = False
        except Exception:
            self.L.Wrap('Month must be a number!')
            parameters_valid = False
        try:
            observation_day = int(observation_day)
            if observation_day > 31:
                self.L.Wrap('Day cannot exceed 31')
                parameters_valid = False
            if observation_day < 1:
                self.L.Wrap('Day cannot be less than 1!')
        except Exception:
            self.L.Wrap('Day must be a number!')
            parameters_valid = False
        # Discern Watershed Scale
        watershed_scale = self.watershed_scope_string_var.get()
        # Test if shapefile exists
        if custom_watershed_file != '':
            watershed_file_exists = os.path.exists(custom_watershed_file)
            if not watershed_file_exists:
                self.L.Wrap('SUPPLIED CUSTOM WATERSHED FILE NOT FOUND!')
                parameters_valid = False
            watershed_extension = os.path.splitext(custom_watershed_file)[1]
            if watershed_extension.lower() == '.shp':
                prj_file = custom_watershed_file[:-4] + '.prj'
                prj_exists = os.path.exists(prj_file)
                if not prj_exists:
                    self.L.Wrap('SUPPLIED CUSTOM WATERSHED FILE LACKS REQUIRED PROJECTION (.prj) FILE!')
                    parameters_valid = False
            if custom_watershed_name == '':
                custom_watershed_name = os.path.splitext(os.path.split(custom_watershed_file)[1])[0]
        else:
            custom_watershed_file = None
            if watershed_scale == 'Custom Polygon':
                self.L.Wrap('"CUSTOM POLYGON" SELECTED BY NOT PROVIDED!')
                parameters_valid = False
        # Test for actual date
        if parameters_valid:
            try:
                # RECTIFY INPUTS
                if len(str(observation_day)) == 1:
                    observation_day = '0'+str(observation_day)
                else:
                    observation_day = str(observation_day)
                if len(str(observation_month)) == 1:
                    observation_month = '0'+str(observation_month)
                else:
                    observation_month = str(observation_month)
                observation_date = str(observation_year)+'-'+observation_month+'-'+observation_day
                observation_datetime = datetime.strptime(observation_date, '%Y-%m-%d')
            except Exception as error:
                self.L.Wrap('')
                self.L.Wrap('{}!'.format(str(error).upper()))
                parameters_valid = False
        if parameters_valid:
            # Ensure date is no later than 2 days prior to current date
            two_days_prior_datetime = datetime.today()- timedelta(days=2)
            if observation_datetime > two_days_prior_datetime:
                observation_date = two_days_prior_datetime.strftime('%Y-%m-%d')
                self.L.Wrap('Date cannot exceed two days ago due to data availability')
                self.L.Wrap('  Observation date updated to: {}'.format(observation_date))
                observation_day = two_days_prior_datetime.strftime('%d')
                observation_month = two_days_prior_datetime.strftime('%m')
                observation_year = int(two_days_prior_datetime.strftime('%Y'))
                observation_datetime = two_days_prior_datetime
        return parameters_valid




    def calculate_or_add_batch(self, batch, params):
        """
        If batch is False
        --Executes main business logic of the Antecedent Precipitation Tool
        If batch is True
        --Adds current field values to batch list
        """
        start_time = datetime.now()
        # Get Paramaters
        latitude = params[0]
        longitude = params[1]
        observation_year = params[2]
        observation_month = params[3]
        observation_day = params[4]
        image_name = params[5]
        image_source = params[6]
        save_folder = params[7]
        custom_watershed_name = params[8]
        custom_watershed_file = params[9]
        watershed_scale = params[10]
        radio = params[11]
        fixed_y_max = params[12]
        forecast_enabled = params[13]
        # Remove Spaces and Line Breaks from numeric fields (They were showing up when copying from Excel for some reason)
        latitude = latitude.replace(' ', '').replace('\n', '')
        longitude = longitude.replace(' ', '').replace('\n', '')
        observation_year = observation_year.replace(' ', '').replace('\n', '')
        observation_month = observation_month.replace(' ', '').replace('\n', '')
        observation_day = observation_day.replace(' ', '').replace('\n', '')
        # Test whether or not all parameters are valid
        parameters_valid = True
        try:
            float(latitude)
        except Exception:
            self.L.Wrap('Latitude must be in decimal degree format!')
            parameters_valid = False
        try:
            float(longitude)
        except Exception:
            self.L.Wrap('Longitude must be in decimal degree format!')
            parameters_valid = False
        # Ensure location is within USA boundary
        in_usa = check_usa.main(latitude, longitude)
        if not in_usa:
            self.L.Wrap('Coordinates must be within the United States!')
            parameters_valid = False
        try:
            observation_year = int(observation_year)
            if observation_year < 1900:
                if str(observation_year) != '50' and str(observation_year) != '30':
                    self.L.Wrap('Year must be greater than 1900!')
                    parameters_valid = False
        except Exception:
            self.L.Wrap('Year must be a number!')
            parameters_valid = False
        try:
            observation_month = int(observation_month)
            if observation_month > 12:
                self.L.Wrap('Month cannot exceed 12!')
                parameters_valid = False
            if observation_month < 1:
                self.L.Wrap('Month cannot be less than 1!')
                parameters_valid = False
        except Exception:
            self.L.Wrap('Month must be a number!')
            parameters_valid = False
        try:
            observation_day = int(observation_day)
            if observation_day > 31:
                self.L.Wrap('Day cannot exceed 31')
                parameters_valid = False
            if observation_day < 1:
                self.L.Wrap('Day cannot be less than 1!')
        except Exception:
            self.L.Wrap('Day must be a number!')
            parameters_valid = False
        # Test if shapefile exists
        if custom_watershed_file != '':
            watershed_file_exists = os.path.exists(custom_watershed_file)
            if not watershed_file_exists:
                self.L.Wrap('SUPPLIED CUSTOM WATERSHED FILE NOT FOUND!')
                parameters_valid = False
            watershed_extension = os.path.splitext(custom_watershed_file)[1]
            if watershed_extension.lower() == '.shp':
                prj_file = custom_watershed_file[:-4] + '.prj'
                prj_exists = os.path.exists(prj_file)
                if not prj_exists:
                    self.L.Wrap('SUPPLIED CUSTOM WATERSHED FILE LACKS REQUIRED PROJECTION (.prj) FILE!')
                    parameters_valid = False
            if custom_watershed_name == '':
                custom_watershed_name = os.path.splitext(os.path.split(custom_watershed_file)[1])[0]
        else:
            custom_watershed_file = None
            if watershed_scale == 'Custom Polygon':
                self.L.Wrap('"CUSTOM POLYGON" SELECTED BY NOT PROVIDED!')
                parameters_valid = False
        # Test for actual date
        if parameters_valid:
            try:
                # RECTIFY INPUTS
                if len(str(observation_day)) == 1:
                    observation_day = '0'+str(observation_day)
                else:
                    observation_day = str(observation_day)
                if len(str(observation_month)) == 1:
                    observation_month = '0'+str(observation_month)
                else:
                    observation_month = str(observation_month)
                observation_date = str(observation_year)+'-'+observation_month+'-'+observation_day
                observation_datetime = datetime.strptime(observation_date, '%Y-%m-%d')
            except Exception as error:
                self.L.Wrap('')
                self.L.Wrap('{}!'.format(str(error).upper()))
                parameters_valid = False
        # Ensure date is no later than 2 days prior to current date
        if parameters_valid:
            two_days_prior_datetime = datetime.today()- timedelta(days=2)
            if observation_datetime > two_days_prior_datetime:
                observation_date = two_days_prior_datetime.strftime('%Y-%m-%d')
                self.L.Wrap('Date cannot exceed two days ago due to data availability')
                self.L.Wrap('  Observation date updated to: {}'.format(observation_date))
                observation_day = two_days_prior_datetime.strftime('%d')
                observation_month = two_days_prior_datetime.strftime('%m')
                observation_year = int(two_days_prior_datetime.strftime('%Y'))
                observation_datetime = two_days_prior_datetime
        # Terminate function of parameters invalid
        if not parameters_valid:
            return
        if image_name == '':
            image_name = None
        if image_source == '':
            image_source = None
        if save_folder == "":
            save_folder = None
        if fixed_y_max == "1":
            fixed_y_max = True
        if forecast_enabled == "1":
            forecast_enabled = True
        # Set data_variable specific variables
        if radio == 'Rain':
            if self.rain_instance is None:
                self.L.Wrap("Creating Rain anteProcess.AnteProcess() instance...")
                self.rain_instance = anteProcess.AnteProcess()
            input_list_list = self.input_list_list_prcp
            ante_instance = self.rain_instance
            data_variable = 'PRCP'
        elif radio == 'Snow':
            if self.snow_instance is None:
                self.L.Wrap("Creating Snow anteProcess.AnteProcess() instance...")
                self.snow_instance = anteProcess.AnteProcess()
            input_list_list = self.input_list_list_snow
            ante_instance = self.snow_instance
            data_variable = 'SNOW'
        elif radio == 'Snow Depth':
            if self.snow_depth_instance is None:
                self.L.Wrap("Creating Snow Depth anteProcess.AnteProcess() instance...")
                self.snow_depth_instance = anteProcess.AnteProcess()
            input_list_list = self.input_list_list_snwd
            ante_instance = self.snow_depth_instance
            data_variable = 'SNWD'
        # Create Batch or Execute Function
        input_list = [data_variable,
                      latitude,
                      longitude,
                      observation_year,
                      observation_month,
                      observation_day,
                      image_name,
                      image_source]
        test = input_list in input_list_list
        if test is False:
            if batch is True or input_list_list:
                input_list_list.append(input_list)
                self.L.Wrap(radio+' Batch '+str(len(input_list_list))+' - '+str(input_list))
        else:
            if batch is True:
                self.L.Wrap('The selected inputs have already been added to the batch list.')
            self.L.Wrap("")
        if batch is False:
#-WATERSHED START
            if radio == 'Rain':
                # WATERSHED PROCESSING SECTION
                if watershed_scale != 'Single Point':
                    # Announce Watershed Processing
                    self.L.print_title('WATERSHED IDENTIFICATION AND RANDOM SAMPLING')
                    # Clear the Batch Queue (If necessary) [We currently don't support batch watershed runs]
                    if len(input_list_list) > 1:
                        # Let user know the batch processes are being cleared
                        self.L.Wrap('Manual batch processing lists are not supported for Watershed Scales other than "Single Point"')
                        self.L.Wrap('  Clearing Batch Process Queue to prepare for Watershed Random Sampling Points...')
                        input_list_list = []
                    self.L.Wrap('Selected Watershed Scale: {}'.format(watershed_scale))
                    self.L.Wrap('Identifying and sampling watershed...')
                    if watershed_scale != 'Custom Polygon':
                        # Get HUC & Random Sampling Points
                        huc, sampling_points, huc_square_miles = huc_query.id_and_sample(lat=latitude,
                                                                                         lon=longitude,
                                                                                         watershed_scale=watershed_scale)
                    else:
                        # Get Random Sampling points and square miles
                        sampling_points, huc_square_miles = custom_watershed_query.shapefile_sample(lat=latitude,
                                                                                                    lon=longitude,
                                                                                                    shapefile=custom_watershed_file)
                    # Add each sampling point to batch process
                    self.L.print_section('Batch Process Queueing')
                    self.L.Wrap('Adding Random Sampling Points for the watershed to the Batch Process Queue...')
                    if watershed_scale != 'Custom Polygon':
                        self.L.Wrap('{} ({}) - Watershed Sampling Points:'.format(watershed_scale, huc))
                    else:
                        self.L.Wrap('{} ({}) - Watershed Sampling Points:'.format(watershed_scale, custom_watershed_name))
                    for sampling_point in sampling_points:
                        # Create input list for sampling point
                        input_list = [data_variable,
                                      sampling_point[0],
                                      sampling_point[1],
                                      observation_year,
                                      observation_month,
                                      observation_day,
                                      image_name,
                                      image_source]
                        # Add sampling point to input_list_list
                        input_list_list.append(input_list)
                        # Announce the addition of this sampling point
                        self.L.Wrap(' Sampling Point {} - {}'.format(str(len(input_list_list)),
                                                                     str(input_list)))
                    self.L.print_separator_line()
#-WATERSHED END
            ### - INDIVIDUAL PROCESS OR BATCH ITERATION - ###
            current_input_list_list = list(input_list_list)

            if not len(input_list_list) > 1:
                self.L.print_title("SINGLE POINT ANALYSIS")
                run_list = input_list + [save_folder, forecast_enabled]

                with open('temp.pickle', 'wb') as picklefile:
                    pickle.dump((run_list, ante_instance, self.gridded), picklefile)

                self.L.Wrap('Running: '+str(run_list))
                result_pdf, run_y_max, condition, ante_score, wet_dry_season, palmer_value, palmer_class = ante_instance.setInputs(run_list, watershed_analysis=False, all_sampling_coordinates=None, gridded=self.gridded)
                if result_pdf is not None:
                    # Open folder containing outputs
                    version_folder = os.path.join(save_folder, VERSION_FOR_PATHS)
                    coord_string = '{}, {}'.format(input_list[1], input_list[2])
                    output_folder = os.path.join(version_folder, coord_string)
                    subprocess.Popen('explorer "{}"'.format(output_folder))
                    # Open PDF in new process
                    self.L.Wrap('Opening PDF in a new process...')
                    subprocess.Popen(result_pdf, shell=True)
                del run_list
            else:
                pdf_list = []
                highest_y_max = 0
                # Ensure batches are saved to a folder (Force Desktop if empty)
                if save_folder is None:
                    save_folder = os.path.join(ROOT, 'Outputs')
                    self.L.Wrap('Setting Output Folder to default location: {}...'.format(save_folder))
                # Test for common naming
                img_event_name = current_input_list_list[0][6]
                for specific_input_list in current_input_list_list:
                    if img_event_name != specific_input_list[6]:
                        img_event_name = ''
                        break
                if img_event_name != '':
                    img_event_name = '{} '.format(img_event_name)
                # Calculate output_folder
                if radio == 'Rain':
                    if watershed_scale == 'Single Point':
                        watershed_analysis = False
                        version_folder = os.path.join(save_folder, VERSION_FOR_PATHS)
                        coord_string = '{}, {}'.format(input_list[1], input_list[2])
                        output_folder = os.path.join(version_folder, coord_string)
                        # Define PDF Outputs
                        final_path_variable = os.path.join(output_folder, '({}, {}) Batch Result.pdf'.format(latitude, longitude))
                        final_path_fixed = os.path.join(output_folder, '({}, {}) Batch Result - Fixed.pdf'.format(latitude, longitude))
                        # Define CSV Output
                        csv_path = os.path.join(output_folder, '({}, {}) Batch Result.csv'.format(latitude, longitude))
                    elif watershed_scale == 'Custom Polygon':
                        watershed_analysis = True
                        version_folder = os.path.join(save_folder, VERSION_FOR_PATHS)
                        general_watershed_folder = os.path.join(version_folder, '~Watershed')
                        watershed_scale_folder = os.path.join(general_watershed_folder, watershed_scale)
                        output_folder = os.path.join(watershed_scale_folder, custom_watershed_name)
                        watershed_analysis = True
                        # Define PDF Outputs
                        final_path_variable = os.path.join(output_folder, '{} - {} - Batch Result.pdf'.format(observation_date, custom_watershed_name))
                        watershed_summary_path = os.path.join(output_folder, '{} - {} - Summary Page.pdf'.format(observation_date, custom_watershed_name))
                        final_path_fixed = os.path.join(output_folder, '{} - {} - Batch Result - Fixed Scale.pdf'.format(observation_date, custom_watershed_name))
                        # Define CSV Output
                        csv_path = os.path.join(output_folder, '{} - {} - Sampling Results.csv'.format(observation_date, custom_watershed_name))
                    else:
                        version_folder = os.path.join(save_folder, VERSION_FOR_PATHS)
                        general_watershed_folder = os.path.join(version_folder, '~Watershed')
                        watershed_scale_folder = os.path.join(general_watershed_folder, watershed_scale)
                        output_folder = os.path.join(watershed_scale_folder, huc)
                        watershed_analysis = True
                        # Define PDF Outputs
                        final_path_variable = os.path.join(output_folder, '{} - {} - Batch Result.pdf'.format(observation_date, huc))
                        watershed_summary_path = os.path.join(output_folder, '{} - {} - Summary Page.pdf'.format(observation_date, huc))
                        final_path_fixed = os.path.join(output_folder, '{} - {} - Batch Result - Fixed Scale.pdf'.format(observation_date, huc))
                        # Define CSV Output
                        csv_path = os.path.join(output_folder, '{} - {} - Sampling Results.csv'.format(observation_date, huc))
                elif radio == 'Snow':
                    watershed_analysis = False
                    version_folder = os.path.join(save_folder, VERSION_FOR_PATHS)
                    snow_folder = os.path.join(version_folder, 'Snowfall')
                    coord_string = '{}, {}'.format(input_list[1], input_list[2])
                    output_folder = os.path.join(snow_folder, coord_string)
                    # Define PDF Outputs
                    final_path_variable = os.path.join(output_folder, '({}, {}) Batch Result.pdf'.format(latitude, longitude))
                    final_path_fixed = os.path.join(output_folder, '({}, {}) Batch Result - Fixed.pdf'.format(latitude, longitude))
                    # Define CSV Output
                    csv_path = os.path.join(output_folder, '({}, {}) Batch Result.csv'.format(latitude, longitude))
                elif radio == 'Snow Depth':
                    watershed_analysis = False
                    version_folder = os.path.join(save_folder, VERSION_FOR_PATHS)
                    snow_depth_folder = os.path.join(version_folder, 'Snow Depth')
                    coord_string = '{}, {}'.format(input_list[1], input_list[2])
                    output_folder = os.path.join(snow_depth_folder, coord_string)
                    # Define PDF Outputs
                    final_path_variable = os.path.join(output_folder, '({}, {}) Batch Result.pdf'.format(latitude, longitude))
                    final_path_fixed = os.path.join(output_folder, '({}, {}) Batch Result - Fixed.pdf'.format(latitude, longitude))
                    # Define CSV Output
                    csv_path = os.path.join(output_folder, '({}, {}) Batch Result.csv'.format(latitude, longitude))
                # Add save_folder and Forecast setting to input lists
                for count, specific_input_list in enumerate(current_input_list_list):
                    current_input_list_list[count] = specific_input_list + [save_folder, forecast_enabled]


                # Create csv_writer
                csv_writer = JLog.PrintLog(Delete=True,
                                           Log=csv_path,
                                           Indent=0,
                                           Width=400,
                                           LogOnly=True)
                # Write first line of CSV
                if watershed_scale == 'Single Point':
                    csv_writer.Wrap('Latitude,Longitude,Date,PDSI Value,PDSI Class,Season,Antecedent Precip Score,Antecedent Precip Condition')
                else:
                    csv_writer.Wrap('Latitude,Longitude,Date,PDSI Value,PDSI Class,Season,Antecedent Precip Score,Antecedent Precip Condition')
                # Create watershed_summary results_list
                watershed_results_list = []
                # Set PDF Counter and Part Counter to 0
                pdf_count = 0
                part_count = 0
                parts_2_delete = []
                total_pdfs = len(current_input_list_list)
                run_count = 0
                for current_input_list in current_input_list_list:
                    run_count += 1
                    if watershed_scale == 'Single Point':
                        sampling_points = None
                        self.L.print_title("Single Point Batch Analysis - Date {} of {}".format(run_count, total_pdfs))
                    else:
                        self.L.print_title("{} WATERSHED ANALYSIS - SAMPLING POINT {} of {}".format(watershed_scale, run_count, total_pdfs))
                    self.L.Wrap('')
                    self.L.Wrap('Running: '+str(current_input_list))
                    self.L.Wrap('')
                    result_pdf, run_y_max, condition, ante_score, wet_dry_season, palmer_value, palmer_class = ante_instance.setInputs(current_input_list, watershed_analysis=watershed_analysis, all_sampling_coordinates=sampling_points, gridded=self.gridded)
                    if run_y_max > highest_y_max:
                        highest_y_max = run_y_max
                    if result_pdf is not None:
                        if total_pdfs > 1:
                            pdf_list.append(result_pdf)
                            # CHECK TO SEE IF INCREMENTAL MERGING IS NECESSARY
                            pdf_count += 1
                            if len(pdf_list) > 365:
                                if (total_pdfs - pdf_count) > 25:
                                    part_count += 1
                                    # Merging current PDFs to avoid crash when too many PDFs are merged at once
                                    self.L.Wrap('')
                                    self.L.Wrap('Merging PDFs to temp file to avoid crash at the end from merging too many files at once...')
                                    self.L.Wrap('')
                                    # Determine available temp file name
                                    final_path_variable_part = '{} - Part {}.pdf'.format(final_path_variable[:-4],
                                                                                         part_count)
                                    # Merge current PDFs
                                    merger = PyPDF2.PdfFileMerger()
                                    for doc in pdf_list:
                                        merger.append(PyPDF2.PdfFileReader(doc), "rb")
                                    merger.write(final_path_variable_part)
                                    # Clear pdf_list
                                    pdf_list = []
                                    # Add Merged PDF to the newly cleared PDF list
                                    pdf_list.append(final_path_variable_part)
                                    del merger
                                    # Remember to delete these partial files later
                                    parts_2_delete.append(final_path_variable_part)
                            # Create all_items list for CSV writing
                            all_items = current_input_list + [palmer_value, palmer_class, wet_dry_season, condition, ante_score]
                            if watershed_scale == 'Single Point':
                                # Write results to CSV
                                csv_writer.Wrap('{},{},{}-{}-{},{},{},{},{},{}'.format(current_input_list[1], # Latitude
                                                                                             current_input_list[2], # Longitude
                                                                                             all_items[3], # Observation Year
                                                                                             all_items[4], # Observation Month
                                                                                             all_items[5], # Observation Day
                                                                                             all_items[10], # PDSI Value
                                                                                             all_items[11], # PDSI Class
                                                                                             all_items[12], # Season
                                                                                             all_items[14], # Antecedent Precip Score
                                                                                             all_items[13])) # Antecedent Precip Condition
                            else:
                                watershed_results_list.append((ante_score, condition, wet_dry_season, palmer_class))
                                csv_writer.Wrap('{},{},{}-{}-{},{},{},{},{},{}'.format(current_input_list[1], # Latitude
                                                                                       current_input_list[2], # Longitude
                                                                                       all_items[3], # Observation Year
                                                                                       all_items[4], # Observation Month
                                                                                       all_items[5], # Observation Day
                                                                                       all_items[10], # PDSI Value
                                                                                       all_items[11], # PDSI Class
                                                                                       all_items[12], # Season
                                                                                       all_items[14], # Antecedent Precip Score
                                                                                       all_items[13])) # Antecedent Precip Condition
                        else:
                            # Open PDF in new process
                            self.L.Wrap('Opening PDF in a new process...')
                            subprocess.Popen(result_pdf, shell=True)
                            # Open Output Folder
                            subprocess.Popen('explorer "{}"'.format(output_folder))
                if watershed_scale != 'Single Point':
                    if watershed_scale == 'Custom Polygon':
                        huc = custom_watershed_name
                    generated = watershed_summary.create_summary(site_lat=latitude,
                                                                 site_long=longitude,
                                                                 observation_date=observation_date,
                                                                 geographic_scope=watershed_scale,
                                                                 huc=huc,
                                                                 huc_size=huc_square_miles,
                                                                 results_list=watershed_results_list,
                                                                 watershed_summary_path=watershed_summary_path,
                                                                 grid_selection=self.gridded)
                    if generated:
                        pdf_list = [watershed_summary_path] + pdf_list
                        parts_2_delete.append(watershed_summary_path)
                if pdf_list: # Testing list for content
                    merger = PyPDF2.PdfFileMerger()
                    for doc in pdf_list:
                        merger.append(PyPDF2.PdfFileReader(doc), "rb")
                    merger.write(final_path_variable)
                    # Open Excel Results
                    self.L.Wrap('Opening Batch Results CSV in new process...')
                    subprocess.Popen(csv_path, shell=True)
                    # Open finalPDF
                    self.L.Wrap('Opening finalPDF in new process...')
                    subprocess.Popen(final_path_variable, shell=True)
                    # Open folder containing outputs
                    subprocess.Popen('explorer "{}"'.format(output_folder))
                    del merger
                    if fixed_y_max is True:
                        # Re-run batch with fixed yMax value
                        ante_instance.set_yMax(highest_y_max)
                        # Set PDF Counter and Part Counter to 0
                        pdf_count = 0
                        part_count = 0
                        # Clear pdf_list
                        pdf_list = []
                        for current_input_list in current_input_list_list:
                            self.L.Wrap('')
                            self.L.Wrap('Re-running with fixed yMax value: '+str(current_input_list))
                            self.L.Wrap('')
                            result_pdf, run_y_max, condition, ante_score, wet_dry_season, palmer_value, palmer_class = ante_instance.setInputs(current_input_list, watershed_analysis=False, all_sampling_coordinates=None, grid=self.gridded)
                            pdf_list.append(result_pdf)
                            # CHECK TO SEE IF INCREMENTAL MERGING IS NECESSARY
                            pdf_count += 1
                            if len(pdf_list) > 365:
                                if (total_pdfs - pdf_count) > 25:
                                    part_count += 1
                                    # Merging current PDFs to avoid crash when too many PDFs are merged at once
                                    self.L.Wrap('')
                                    self.L.Wrap('Merging PDFs to temp file to avoid crash at the end from merging too many files at once...')
                                    self.L.Wrap('')
                                    # Determine available temp file name
                                    final_path_fixed_part = '{} - Part {}.pdf'.format(final_path_fixed[:-4],
                                                                                      part_count)
                                    # Merge current PDFs
                                    merger = PyPDF2.PdfFileMerger()
                                    for doc in pdf_list:
                                        merger.append(PyPDF2.PdfFileReader(doc), "rb")
                                    merger.write(final_path_fixed_part)
                                    # Clear pdf_list
                                    pdf_list = []
                                    # Add temp file to pdf_list
                                    pdf_list.append(final_path_fixed_part)
                                    del merger
                                    # Remember to delete these partial files later
                                    parts_2_delete.append(final_path_fixed_part)
                        ante_instance.set_yMax(None)
                        if pdf_list:
                            merger = PyPDF2.PdfFileMerger()
                            for doc in pdf_list:
                                merger.append(PyPDF2.PdfFileReader(doc), "rb")
                            merger.write(final_path_fixed)
                            # Open finalPDF
                            self.L.Wrap('Opening finalPDF in new process...')
                            subprocess.Popen(final_path_fixed, shell=True)
                            del merger
                    # Attempt to delete partial files
                    self.L.Wrap('Attempting to delete temporary files...')
                    if parts_2_delete:
                        for part in parts_2_delete:
                            try:
                                os.remove(part)
                            except Exception:
                                pass
                if radio == 'Rain':
                    self.input_list_list_prcp = []
                elif radio == 'Snow':
                    self.input_list_list_snow = []
                elif radio == 'Snow Depth':
                    self.input_list_list_snwd = []
            self.L.Wrap('')
            self.L.Time(StartTime=start_time,
                        Task="All tasks")
            self.L.Wrap('')
            self.L.Wrap('Ready for new input.')

            # reset the input lists
            self.input_list_list_prcp = []
            self.input_list_list_snow = []
            self.input_list_list_snwd = []
            # reset the GUI
            # self.master.mainloop()
    # End calculate_or_add_batch function


class DateEntry(tkinter.Frame):
    """Date entry box"""
    def __init__(self, master, frame_look={}, **look):
        self.gridded = False
        self.recheck = False
        args = dict(relief=tkinter.SUNKEN, border=1)
        args.update(frame_look)
        tkinter.Frame.__init__(self, master, **args)

        args.update(look)

        self.ignore_key_list = ['Shift_L', 'Shift_R', 'Left', 'Right']

        self.year_testable = False
        self.month_testable = False
        self.day_testable = False

        self.two_days_prior_datetime = datetime.today() - timedelta(days=2)
        self.two_days_prior_string = self.two_days_prior_datetime.strftime('%Y-%m-%d')
        self.two_days_prior_year = int(self.two_days_prior_datetime.strftime('%Y'))

        self.three_days_prior_datetime = datetime.today() - timedelta(days=3)
        self.three_days_prior_string = self.three_days_prior_datetime.strftime('%Y-%m-%d')
        self.three_days_prior_year = int(self.three_days_prior_datetime.strftime('%Y'))

        #---SEPARATOR STYLE---#
        self.line_style = tkinter.ttk.Style()
        self.line_style.configure("Line.TSeparator", background="#000000")

        self.entry_year = tkinter.ttk.Entry(self, width=4)
        self.label_yr_mo = tkinter.ttk.Separator(self, orient="horizontal", style="Line.TSeparator")
        self.entry_month = tkinter.ttk.Entry(self, width=2)
        self.label_mo_dd = tkinter.ttk.Separator(self, orient="horizontal", style="Line.TSeparator")
        self.entry_day = tkinter.ttk.Entry(self, width=2)

        self.entry_year.grid(row=0, column=0, sticky='w')
        self.label_yr_mo.grid(row=0, column=1, sticky='ew', padx=2)
        self.entry_month.grid(row=0, column=2, sticky='w')
        self.label_mo_dd.grid(row=0, column=3, sticky='ew', padx=2)
        self.entry_day.grid(row=0, column=4, sticky='w')

        self.entry_year.bind('<KeyRelease>', self._entry_year_check)
        self.entry_month.bind('<KeyRelease>', self._entry_month_check)
        self.entry_day.bind('<KeyRelease>', self.entry_day_check)

    def _backspace(self, entry):
        entry_text = entry.get()
        entry.delete(0, 'end')
        entry.insert(0, entry_text[:-1])
        self._test_date()

    def _test_date(self):
        self.date_problem = False
        year = self._year_eval()
        month = self._month_eval()
        day = self._day_eval()
        if self.year_testable and self.month_testable and self.day_testable:
            # Test for actual date
            try:
                # RECTIFY INPUTS
                if len(str(day)) == 1:
                    day = '0'+str(day)
                else:
                    day = str(day)
                if len(str(month)) == 1:
                    month = '0'+str(month)
                else:
                    month = str(month)
                date_string = str(year)+'-'+month+'-'+day
                entry_datetime = datetime.strptime(date_string, '%Y-%m-%d')
                # Ensure date is no later than 2 days prior to current date
                if self.gridded is False:
                    if entry_datetime > self.two_days_prior_datetime:
                        print('')
                        print('INPUT ERROR - GHCN Data is two days old - Please change to: ({})'.format(self.two_days_prior_string))
                        self.date_problem = True
                # Ensure date is no later than 3 days prior to current date
                if self.gridded is True:
                    if entry_datetime > self.three_days_prior_datetime:
                        print('')
                        print('INPUT ERROR - GHCN Data is three days old - Please change to: ({})'.format(self.three_days_prior_string))
                        self.date_problem = True
            except Exception as error:
                self.date_problem = True
                print('')
                print('{}!'.format(str(error).upper()))
        if self.year_problem:
            self.config({"background":"red"})
        elif self.month_problem:
            self.config({"background":"red"})
        elif self.day_problem:
            self.config({"background":"red"})
        elif self.date_problem:
            self.config({"background":"red"})
        else:
            self.config({"background":"white"})

    def _year_eval(self):
        self.year_problem = False
        entry_text = self.entry_year.get()
        if len(entry_text) > 3:
            int_year = int(entry_text)

            if not self.gridded:
                if int_year < 1910:
                    self.year_problem = True
                    print(' ')
                    print('Year cannot be less than 1910 for a station based analysis!')
                elif int_year > self.two_days_prior_year:
                    self.year_problem = True
                    print(' ')
                    print('Year cannot be greater than {}!'.format(self.two_days_prior_year))
            else:
                if int_year < 1983:
                    self.year_problem = True
                    print(' ')
                    print('Year cannot be less than 1983 for a grid based analysis!')
                elif int_year > self.three_days_prior_year:
                    self.year_problem = True
                    print(' ')
                    print('Year cannot be greater than {}!'.format(self.three_days_prior_year))

        return entry_text

    def _month_eval(self):
        self.month_problem = False
        entry_text = self.entry_month.get()
        if len(entry_text) > 0:
            int_month = int(entry_text)
            if int_month > 12:
                self.month_problem = True
                print(' ')
                print('Month cannot be more than 12!')
        return entry_text

    def _day_eval(self):
        self.day_problem = False
        entry_text = self.entry_day.get()
        if len(entry_text) > 1:
            int_day = int(entry_text)
            if int_day > 31:
                self.day_problem = True
                print('')
                print('Day cannot be more than 31!')
        return entry_text


    def _entry_year_check(self, e):
        self.year_testable = True
        self.year_problem = False
        entry_text = self.entry_year.get()
        if len(entry_text) == 0:
            return
        # Deal with non-numeric characters
        try:
            if not entry_text[-1].isdigit():
                self._backspace(self.entry_year)
        except Exception:
            pass
        if len(entry_text) > 4:
            self._backspace(self.entry_year)
            self.entry_month.focus()
            self.year_testable = True
        if len(entry_text) > 3:
            if e.keysym == 'Left':
                pass
            elif e.keysym == 'Right':
                if self.entry_year.index(tkinter.INSERT) > 3:
                    self.entry_month.focus()
                    self.year_testable = True
            else:
                self.entry_month.focus()
                self.year_testable = True
        if not e.keysym in self.ignore_key_list:
            self.year_testable = True
        if self.year_testable:
            self._test_date()


    def _entry_month_check(self, e):
        self.month_testable = False
        entry_text = self.entry_month.get()
        if len(entry_text) == 0:
            if e.keysym == 'Left':
                if self.entry_month.index(tkinter.INSERT) < 1:
                    self.entry_year.focus()
            if e.keysym == 'BackSpace':
                if self.entry_month.index(tkinter.INSERT) < 1:
                    self.entry_year.focus()
            return
        # Overwriting
        if len(entry_text) > 2:
            self._backspace(self.entry_month)
            self.entry_day.focus()
            self.month_testable = True
        # Non-digits
        if not entry_text[-1].isdigit():
            self._backspace(self.entry_month)
        if e.keysym == 'Left':
            if self.entry_month.index(tkinter.INSERT) < 1:
                self.entry_year.focus()
                self.entry_year.icursor(4)
                self.month_testable = True
        if len(entry_text) > 1:
            self.entry_day.focus()
            self.month_testable = True
        if not e.keysym in self.ignore_key_list:
            self.month_testable = True
        if self.month_testable:
            self._test_date()

    def entry_day_check(self, e):
        self.day_testable = False
        entry_text = self.entry_day.get()
        if len(entry_text) == 0:
            if e.keysym == 'Left':
                if self.entry_day.index(tkinter.INSERT) < 1:
                    self.entry_month.focus()
            if e.keysym == 'BackSpace':
                if self.entry_day.index(tkinter.INSERT) < 1:
                    self.entry_month.focus()
            return
        # Overwriting
        if len(entry_text) > 2:
            self._backspace(self.entry_day)
            self.day_testable = True
        # Non-Digits
        if not entry_text[-1].isdigit():
            self._backspace(self.entry_day)
        # Jumping Left
        if e.keysym == 'Left':
            if self.entry_day.index(tkinter.INSERT) < 1:
                self.entry_month.focus()
                self.day_testable = True
        if not e.keysym in self.ignore_key_list:
            self.day_testable = True
        if self.day_testable:
            self._test_date()


    def get(self):
        return self.entry_year.get(), self.entry_month.get(), self.entry_day.get()

    def set(self, year, month, day):
        self.entry_year.delete(0, 'end')
        self.entry_year.insert(0, year)
        self.entry_month.delete(0, 'end')
        self.entry_month.insert(0, month)
        self.entry_day.delete(0, 'end')
        self.entry_day.insert(0, day)


if __name__ == '__main__':
    APP = AntGUI()
    APP.run()
