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
##     MasterTileIndexGenerator.py  ##
##  ------------------------------- ##
##     Written by: Jason Deters     ##
##  ------------------------------- ##
##    Last Edited on: 10-26-2017    ##
##  ------------------------------- ##
######################################

# Import Standard Libraries
import os
import sys
import shutil
import time
import multiprocessing
import traceback
import textwrap
import stat
import re
import subprocess

# Import Custom Libraries
import osConvenience
import versionproof
import JLog


if __name__ != '__main__':
    # Import arcpy
    import arcpy
    # Check out any necessary licenses
    arcpy.CheckOutExtension("3D")
    # Enable Overwritting Geoprocessing Outputs
    arcpy.env.overwriteOutput = True

#-------------------------- Function Definitions --------------------------#

def SetToPythonW():
    versions = ['10', '10.1', '10.2', '10.3', '10.4', '10.5', '10.6', '10.7', '10.8', '10.9']
    log_path = u'C:\\Temp\\LiDAR Index Generator\\Generator_Log.txt'
    L = JLog.PrintLog(Indent=9, Log=log_path, Delete=False)
    L.Wrap(" ")
    L.Wrap("----------Start of SetPyOrPyW.SetToPythonW()-----------")
    L.Wrap(str(time.ctime()))
    for ver in versions:
        path = "C:/Python27/ArcGIS" + ver + "/pythonw.exe"
        test = os.path.exists(path)
        if test:
            latest_path = path
            latest_version = ver
    L.Wrap("ArcGIS " + latest_version + " installed on the system...")
    L.Wrap("Setting multiprocessing executable to pythonw.exe")
    multiprocessing.set_executable(latest_path)
    L.Wrap(latest_path)
    L.Wrap("-----------End of SetPyOrPyW.SetToPythonW()------------")
    L.Wrap(" ")
    return latest_path


def SetToPython():
    versions = ['10', '10.1', '10.2', '10.3', '10.4', '10.5', '10.6', '10.7', '10.8', '10.9']
    log_path = u'C:\\Temp\\LiDAR Index Generator\\Generator_Log.txt'
    L = JLog.PrintLog(Indent=9, Log=log_path, Delete=False)
    L.Wrap(" ")
    L.Wrap("----------Start of SetPyOrPyW.SetToPython()-----------")
    L.Wrap(str(time.ctime()))
    for ver in versions:
        path = "C:/Python27/ArcGIS" + ver + "/python.exe"
        test = os.path.exists(path)
        if test:
            latest_path = path
            latest_version = ver
    L.Wrap("ArcGIS " + latest_version + " installed on the system...")
    L.Wrap("Setting multiprocessing executable to pythonw.exe")
    multiprocessing.set_executable(latest_path)
    L.Wrap(latest_path)
    L.Wrap("-----------End of SetPyOrPyW.SetToPython()------------")
    L.Wrap(" ")
    return latest_path

def ensure_dir(folder):
    """Ensures entire directory structure given exists"""
    try:
        os.makedirs(folder)
    except WindowsError:
        pass
# End of ensure_dir function

def deleteReadOnly(filePath):
    for x in range(10):
        try:
            os.remove(filePath)
            break
        except Exception:
            test = os.path.exists(filePath)
            if test is False:
                break
            try:
                os.chmod(filePath, stat.S_IWRITE)
                os.remove(filePath)
                break
            except Exception:
                if x == 9:
                    raise
            time.sleep(x)

def time2String(totalSeconds):
    if totalSeconds < 61:
        Seconds = str(int(totalSeconds))
        outputStr = '{} seconds'.format(Seconds)
    elif totalSeconds > 60 and totalSeconds < 3601:
        Minutes = int(totalSeconds / 60)
        minutesLoss = (Minutes * 60)
        Seconds = int(totalSeconds - minutesLoss)
        outputStr = '{} minutes and {} seconds'.format(Minutes, Seconds)
    elif totalSeconds > 3600:
        Hours = int(totalSeconds / 3600)
        hoursLoss = (Hours * 3600)
        Minutes = int((totalSeconds - hoursLoss)/60)
        minutesLoss = (Minutes * 60)
        Seconds = int(totalSeconds - hoursLoss - minutesLoss)
        outputStr = '{} hours, {} minutes, and {} seconds'.format(Hours, Minutes, Seconds)
    return outputStr

def arcDelete(File):
    tries = 5
    while tries > 0:
        tries -= 1
        try:
            arcpy.Delete_management(File)
            break
        except Exception:
            Test = arcpy.Exists(File)
            if test is False:
                break
            time.sleep(5)
            if tries < 1:
                raise

def append_pfi_tile_to_master(pfi_tile, LiDAR_Model_Integration_Folder, coordinate_system, PFI_No_Summarize, PFI_Summarize):
    """Appends PFI file for a LiDAR Tile to the Master PFI feature class"""
    deleted = False
    log_path = 'C:\\Temp\\LiDAR Index Generator\\Generator_Log.txt'
    L = JLog.PrintLog(Log=log_path, Delete=False)
    try:
        pfi_tile_name = os.path.split(pfi_tile)[1]
        if '_no.shp' in pfi_tile:
            if os.path.exists(PFI_No_Summarize) is False:
                L.Wrap('Creating PFI_No_Summarize.shp...')
                arcpy.CreateFeatureclass_management(out_path=LiDAR_Model_Integration_Folder,
                                                    out_name="PFI_No_Summarize",
                                                    geometry_type="POLYGON",
                                                    template=pfi_tile,
                                                    has_m="DISABLED",
                                                    has_z="DISABLED",
                                                    spatial_reference=coordinate_system,
                                                    config_keyword="",
                                                    spatial_grid_1="0",
                                                    spatial_grid_2="0",
                                                    spatial_grid_3="0")
            L.Wrap('Appending {} to PFI_No_Summarize.shp...'.format(pfi_tile_name))
            fields = ['SHAPE@', 'FileName', 'Pt_Count', 'Pt_Spacing', 'Z_Min', 'Z_Max']
            with arcpy.da.SearchCursor(pfi_tile, fields) as cursor:
                new_rows = []
                for row in cursor:
                    shape = row[0]
                    filename = row[1]
                    pt_count = row[2]
                    pt_spacing = row[3]
                    z_min = row[4]
                    z_max = row[5]
                    new_row = [shape, filename, pt_count, pt_spacing, z_min, z_max]
                    new_rows.append(new_row)
            if os.path.exists(PFI_No_Summarize) is True:
                for append_attempt in range(5):
                    append_attempt += 1
                    try:
                        with arcpy.da.InsertCursor(PFI_No_Summarize, fields) as cursor:
                            for new_row in new_rows:
                                cursor.insertRow(new_row)
                        try:
                            arcDelete(pfi_tile)
                        except Exception:
                            pass
                        break
                    except Exception:
                        L.Wrap('    Attempt {} failed.  Trying agian in 5 seconds...'.format(append_attempt))
                        time.sleep(5)
        else:
            if os.path.exists(PFI_Summarize) is False:
                L.Wrap('Creating PFI_Summarize.shp...')
                arcpy.CreateFeatureclass_management(out_path=LiDAR_Model_Integration_Folder,
                                                    out_name="PFI_Summarize",
                                                    geometry_type="POLYGON",
                                                    template=pfi_tile,
                                                    has_m="DISABLED",
                                                    has_z="DISABLED",
                                                    spatial_reference=coordinate_system,
                                                    config_keyword="",
                                                    spatial_grid_1="0",
                                                    spatial_grid_2="0",
                                                    spatial_grid_3="0")
            L.Wrap('Appending {} to PFI_Summarize.shp...'.format(pfi_tile_name))
            fields = ['SHAPE@', 'FileName', 'Class', 'Pt_Count', 'Pt_Spacing', 'Z_Min', 'Z_Max']
            with arcpy.da.SearchCursor(pfi_tile, fields) as cursor:
                new_rows = []
                for row in cursor:
                    shape = row[0]
                    filename = row[1]
                    class_field = row[2]
                    pt_count = row[3]
                    pt_spacing = row[4]
                    z_min = row[5]
                    z_max = row[6]
                    new_row = [shape, filename, class_field, pt_count, pt_spacing, z_min, z_max]
                    new_rows.append(new_row)
            if os.path.exists(PFI_Summarize) is True:
                for append_attempt in range(5):
                    append_attempt += 1
                    try:
                        with arcpy.da.InsertCursor(PFI_Summarize, fields) as cursor:
                            for new_row in new_rows:
                                cursor.insertRow(new_row)
                        try:
                            arcDelete(pfi_tile)
                        except Exception:
                            pass
                        break
                    except Exception:
                        L.Wrap('    Attempt {} failed.  Trying agian in 5 seconds...'.format(append_attempt))
                        time.sleep(5)
        if not new_rows:
            L.Wrap("   PFI corrupt. Deleting...")
            arcDelete(pfi_tile)
            deleted = True
        return deleted
    except Exception:
        L.Wrap('-------------------------------------------------------')
        L.Wrap('EXCEPTION:')
        L.Wrap(traceback.format_exc())
        L.Wrap('-------------------------------------------------------')
# End Append PFI to 

class Minion(multiprocessing.Process):
    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.proc_name = self.name
    def startLog(self):
        # Create PrintLog
        log_path = 'C:\\Temp\\LiDAR Index Generator\\Minion Errors.txt'
        self.L = JLog.PrintLog(Log=log_path, Delete=False)
    def run(self):
        self.startLog()
        num_jobs = 0
        max_jobs = 20  # Max jobs before terminating (Reduces glitches)
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
                next_task()
            except Exception:
                self.L.Wrap('------------------------------------------')
                self.L.Wrap("EXCEPTION:")
                self.L.Wrap(traceback.format_exc())
                self.L.Wrap('------------------------------------------')
            self.result_queue.put(next_task)
            num_jobs += 1
            if num_jobs > max_jobs:
                self.result_queue.put("Maxed")
                break
        return
# End of Minion


class pfiMaker(object):
    def __init__(self, summarize, las_path, laz_path, pfi_path, coordinate_system, temp_las_file):
        self.summarize = summarize
        self.las_path = las_path
        self.laz_path = laz_path
        self.pfi_path = pfi_path
        self.coordinate_system = coordinate_system
        self.Created = None
        self.Failed = None
        self.temp_las_file = temp_las_file
    def startLog(self):
        # Create PrintLog
        log_path = u'C:\\Temp\\LiDAR Index Generator\\PFI_Maker_Errors.txt'
        self.L = JLog.PrintLog(Log=log_path, Delete=False)
    def __call__(self):
        try:
            import lasZipWrapper
            spatial_reference = arcpy.CreateSpatialReference_management(self.coordinate_system)
            test = os.path.exists(self.pfi_path)
            if test is False:
                test = os.path.exists(self.las_path)
                if test is False:
                    temp_las_folder = os.path.split(self.las_path)[0]
                    lasZipWrapper.one_file(self.laz_path, temp_las_folder)
                if self.summarize is True:
                    arcpy.PointFileInformation_3d(input=self.las_path,
                                                  out_feature_class=self.pfi_path,
                                                  in_file_type="LAS",
                                                  file_suffix=".LAS",
                                                  input_coordinate_system=spatial_reference,
                                                  folder_recursion="RECURSION",
                                                  extrude_geometry="NO_EXTRUSION",
                                                  decimal_separator="DECIMAL_POINT",
                                                  summarize_by_class_code="SUMMARIZE",
                                                  improve_las_point_spacing="NO_LAS_SPACING")
                elif self.summarize is False:
                    arcpy.PointFileInformation_3d(input=self.las_path,
                                                  out_feature_class=self.pfi_path,
                                                  in_file_type="LAS",
                                                  file_suffix=".LAS",
                                                  input_coordinate_system=spatial_reference,
                                                  folder_recursion="RECURSION",
                                                  extrude_geometry="NO_EXTRUSION",
                                                  decimal_separator="DECIMAL_POINT",
                                                  summarize_by_class_code="NO_SUMMARIZE",
                                                  improve_las_point_spacing="LAS_SPACING")
                self.Created = self.pfi_path
        except Exception:
            self.Failed = self.pfi_path
            self.startLog()
            self.L.Wrap('-------------------------------------------------------')
            self.L.Wrap('EXCEPTION:')
            self.L.Wrap(self.pfi_path)
            self.L.Wrap('TRACEBACK:')
            self.L.Wrap(traceback.format_exc())
            self.L.Wrap('-------------------------------------------------------')
        return
    def __str__(self):
        return '{}'.format(self.pfi_path)


class DA(object):
    def __init__(self,
                 Dataset_Name,
                 Dataset_Abbreviation,
                 Main_Dataset_Folder,
                 coordinate_system,
                 FirstReturn,
                 CreateNewIndices):
        self.Dataset_Name = Dataset_Name
        self.Dataset_Abbreviation = Dataset_Abbreviation
        self.Main_Dataset_Folder = Main_Dataset_Folder
        self.coordinate_system = coordinate_system
        self.FirstReturn = FirstReturn
        self.CreateNewIndices = CreateNewIndices
    def __call__(self):
        log_path = u'C:\\Temp\\LiDAR Index Generator\\Generator_Log.txt'
        L = JLog.PrintLog(Indent=0, Log=log_path)
        EntireTime = time.clock()
        TileIndexStartTime = time.clock()
        #------------------------------Script Arguments----------------------------#
        # Collect Script Arguments
        DatasetName = self.Dataset_Name
        DatasetAbbreviation = self.Dataset_Abbreviation
        DatasetFolder = self.Main_Dataset_Folder
        coordinate_system = self.coordinate_system
        FirstReturn = self.FirstReturn
        CreateNewIndices = self.CreateNewIndices
        # Announce Script Arguments
        L.Wrap("                         --" + "-"*len(DatasetAbbreviation) + "--")
        L.Wrap("Dataset Abbreviation =   | " + DatasetAbbreviation + " |")
        L.Wrap("                         --" + "-"*len(DatasetAbbreviation) + "--")
        L.Wrap('')
        L.Wrap('Dataset Name = {}'.format(self.Dataset_Name))
        #------------------------------Local Variables-----------------------------#
        # Define Local Variables
        Files2Delete = []
        Files_2_os_remove = []
        Files2Shutil_rmtree = []
        las_folder = '{}\\LAS'.format(DatasetFolder)
        laz_folder = '{}\\LAZ'.format(DatasetFolder)
        temp_folder = u'C:\\Temp\\LiDAR Index Generator'
        dataset_temp_folder = '{}\\{}'.format(temp_folder, DatasetAbbreviation)
        pfi_temp_folder_sum = u'C:\\Temp\\LiDAR Index Generator\\{}\\PFIs\\sum'.format(DatasetAbbreviation)
        pfi_temp_folder_no_sum = u'C:\\Temp\\LiDAR Index Generator\\{}\\PFIs\\no_sum'.format(DatasetAbbreviation)
        las_temp_folder = u'C:\\Temp\\LiDAR Index Generator\\{}\\LAS'.format(DatasetAbbreviation)
        LiDAR_Model_Integration_Folder = (DatasetFolder + r"\LiDAR Model Integration Folder")
        PFI_No_Summarize = LiDAR_Model_Integration_Folder + r"\PFI_No_Summarize.shp"
        PFI_No_Summarize_Valid = LiDAR_Model_Integration_Folder + r"\PFI_No_Summarize_Valid.shp"
        PFI_Summarize = LiDAR_Model_Integration_Folder + r"\PFI_Summarize.shp"
        PFI_Merge = LiDAR_Model_Integration_Folder + r"\PFI_Merge.shp"
        PFI_Class_2 = LiDAR_Model_Integration_Folder + r"\PFI_Class_2.shp"
        Tile_Index_Name = DatasetAbbreviation + r"_Tile_Index.shp"
        Tile_Index = (LiDAR_Model_Integration_Folder + "\\" + DatasetAbbreviation + r"_Tile_Index.shp")

        #---------------------------Testing Tile_Index-----------------------------#
        L.Wrap(" ")
        L.Wrap("#---------------------------Testing Tile_Index-----------------------------#")
        # Create Lidar 2.0 Model Integration Folder
        L.Wrap("Checking for 'LiDAR Model Integration Folder'...")
        if arcpy.Exists(LiDAR_Model_Integration_Folder) == False:
            L.Wrap("Creating 'LiDAR Model Integration Folder'")
            arcpy.CreateFolder_management(DatasetFolder, "LiDAR Model Integration Folder")
            L.Wrap("Successfully Created: " + LiDAR_Model_Integration_Folder)
            L.Wrap(" ")
        # Check if Tile_Index, with features, exists, otherwise delete & Create
        if CreateNewIndices == True:
            L.Wrap("Checking for Tile_Index...")
            if arcpy.Exists(Tile_Index) == True:
                L.Wrap("Deleting Tile Index...")
                arcDelete(Tile_Index)
        L.Wrap("Checking for Tile Index...")
        if arcpy.Exists(Tile_Index) == True:
            L.Wrap("Tile_Index already exists... Testing...")
            try:
                Test = [row[0] for row in arcpy.da.SearchCursor(Tile_Index, "FirstRetrn")]
                L.Wrap("Test passed.")
            except:
                L.Wrap("Tile index currupt. Deleting....")
                arcDelete(Tile_Index)
        if arcpy.Exists(Tile_Index) == False:
            Attempt = 1
            while Attempt < 10:
                L.Wrap(" ")
                L.Write("                         #############")
                L.Write("                         # Attempt "+str(Attempt)+" #")
                L.Write("                         #############")
                Attempt = Attempt + 1
                try:
                    #----------------------------Analyzing Dataset-----------------------------#
                    L.Wrap(" ")
                    L.Wrap("#----------------------------Analyzing Dataset-----------------------------#")
                    sum_files2enqueue = []
                    no_sum_files2enqueue = []
                    enqueCount = 0
                    buildingPFI_No_Summarize = False
                    build_pfi_summarize = False
                    # Check if PFI_No_Summarize.shp already exists, with features
                    L.Wrap("Checking for PFI_No_Summarize.shp...")
                    if arcpy.Exists(PFI_No_Summarize) is True:
                        L.Wrap("PFI_No_Summarize found. Testing it...")
                        Count = len([row[0] for row in arcpy.da.SearchCursor(PFI_No_Summarize, "FID")])
                        if Count == 0:
                            L.Wrap("Test failed... deleting PFI_No_Summarize...")
                            arcDelete(PFI_No_Summarize)
                        if Count > 0:
                            L.Wrap("PFI_No_Summarize already exists. Moving forward using the existing file...")
                    PFI_No_Summarize_Exists = arcpy.Exists(PFI_No_Summarize)
                    # Check completeness of current PFI_No_Summarize
                    PFI_No_Summarize_Filenames = []
                    if PFI_No_Summarize_Exists:
                        fields = ['FileName']
                        with arcpy.da.SearchCursor(PFI_No_Summarize, fields) as cursor:
                            for row in cursor:
                                filename = row[0]
                                PFI_No_Summarize_Filenames.append(filename)
                    # Check if PFI_Summarize.shp already exists
                    L.Wrap("Checking for PFI_Summarize.shp...")
                    if arcpy.Exists(PFI_Summarize) is True:
                        L.Wrap("PFI_Summarize.shp found. Testing it...")
                        Count = len([row[0] for row in arcpy.da.SearchCursor(PFI_Summarize, "FID")])
                        if Count == 0:
                            L.Wrap("test failed... deleting PFI_Summarize...")
                            arcDelete(PFI_Summarize)
                            L.Wrap("PFI_Summarize deleted")
                        if Count > 0:
                            L.Wrap("PFI_Summarize already exists. Moving forward using the existing file...")
                    PFI_Summarize_Exists = arcpy.Exists(PFI_Summarize)
                    # Check completeness of current PFI_Summarize
                    PFI_Summarize_Filenames = []
                    if PFI_Summarize_Exists:
                        fields = ['FileName']
                        with arcpy.da.SearchCursor(PFI_Summarize, fields) as cursor:
                            for row in cursor:
                                filename = row[0]
                                PFI_Summarize_Filenames.append(filename)
                    # Create pfi_temp_folders
                    osConvenience.ensure_dir(pfi_temp_folder_no_sum)
                    osConvenience.ensure_dir(pfi_temp_folder_sum)
                    # Create las_temp_folder
                    osConvenience.ensure_dir(las_temp_folder)
                    # Create PFI_No_Summarize.shp
                    try:
                        las_files = filter(lambda x: x.lower().endswith(('.las')), os.listdir(las_folder))
                    except WindowsError:
                        las_files = []
                        pass
                    try:
                        laz_files = filter(lambda x: x.lower().endswith(('.laz')), os.listdir(laz_folder))
                    except WindowsError:
                        laz_files = []
                        pass
                    if las_files:
                        file_count = len(las_files)
                    else:
                        file_count = len(laz_files)
                    pfiFilesNoSummarize = []
                    pfiFiles = []
                    temp_las_files = []
                    multiprocess = False
                    msg = ''
                    L.Wrap('Creating PFI_Maker class instances...')
                    for num in range(file_count):
                        temp_las_file = None
                        msg = '{} Files enqueued so far...'.format(enqueCount)
                        L.statusMsg(msg)
                        try:
                            las_name = las_files[num]
                            tile_name = os.path.splitext(las_name)[0]
                            las_path = '{}\\{}.las'.format(las_folder, tile_name)
                        except Exception:
                            laz_name = laz_files[num]
                            tile_name = os.path.splitext(laz_name)[0]
                            las_name = '{}.las'.format(tile_name)
                            las_path = '{}\\{}.las'.format(las_temp_folder, tile_name)
                            temp_las_file = las_path
                        laz_path = '{}\\{}.laz'.format(laz_folder, tile_name)
                        if not las_name in PFI_No_Summarize_Filenames:
                            no_sum_pfi_path = '{}\\{}_no.shp'.format(pfi_temp_folder_no_sum, tile_name)
                            pfiFilesNoSummarize.append(no_sum_pfi_path)
                            if os.path.exists(no_sum_pfi_path) is False:
                                enqueCount += 1
                                a = pfiMaker(False, las_path, laz_path, no_sum_pfi_path, coordinate_system, temp_las_file)
                                no_sum_files2enqueue.append(a)
                                multiprocess = True
                                if not temp_las_file is None:
                                    temp_las_files.append(temp_las_file)
                            else:
                                no_sum_pfi_name = os.path.split(no_sum_pfi_path)[1]
                                # Appending to PFI_No_Summarize.shp
                                deleted = append_pfi_tile_to_master(no_sum_pfi_path, LiDAR_Model_Integration_Folder, coordinate_system, PFI_No_Summarize, PFI_Summarize)
                                if deleted:
                                    # If existing version got deleted for beign corrupt, add it to queue normally
                                    enqueCount += 1
                                    a = pfiMaker(False, las_path, laz_path, no_sum_pfi_path, coordinate_system, temp_las_file)
                                    no_sum_files2enqueue.append(a)
                                    multiprocess = True
                                    if not temp_las_file is None:
                                        temp_las_files.append(temp_las_file)
                        if not las_name in PFI_Summarize_Filenames:
                            pfi_path = '{}\\{}.shp'.format(pfi_temp_folder_sum, tile_name)
                            pfiFiles.append(pfi_path)
                            if os.path.exists(pfi_path) is False:
                                enqueCount += 1
                                a = pfiMaker(True, las_path, laz_path, pfi_path, coordinate_system, temp_las_file)
                                sum_files2enqueue.append(a)
                                multiprocess = True
                                if not temp_las_file is None:
                                    temp_las_files.append(temp_las_file)
                            else:
                                pfi_name = os.path.split(pfi_path)[1]
                                # Appending to PFI_Summarize.shp
                                deleted = append_pfi_tile_to_master(pfi_path, LiDAR_Model_Integration_Folder, coordinate_system, PFI_No_Summarize, PFI_Summarize)
                                if deleted:
                                    # If existing PFI got deleted for being corrupt, add it to queue normally
                                    enqueCount += 1
                                    a = pfiMaker(True, las_path, laz_path, pfi_path, coordinate_system, temp_las_file)
                                    sum_files2enqueue.append(a)
                                    multiprocess = True
                                    if not temp_las_file is None:
                                        temp_las_files.append(temp_las_file)
                    L.Wrap('{0} Files enqueued          '.format(enqueCount))
                    L.Wrap('-------------------------------------------------------')
                    L.Wrap('')
                    if multiprocess:
                        try:
                            #---------------------------MULTIPROCESSING START-----------------------------#
                            L.Wrap('#---------------------------MULTIPROCESSING START-----------------------------#')
                            # Set Set Path to Python Executable
                            executable = os.path.split(sys.executable)[1]
                            if executable == 'pythonw.exe':
                                SetToPython()
                            elif executable == 'ArcMap.exe':
                                SetToPython()
                            elif executable == 'python.exe':
                                SetToPythonW()
                            # Establish communication queues
                            L.Wrap("Establishing Communication Queues")
                            tasks = multiprocessing.Queue()
                            results = multiprocessing.Queue()
                            # Create minions
                            num_minions = multiprocessing.cpu_count() - 1
                            L.Wrap('Creating %d minions' % num_minions)
                            import MasterTileIndexGenerator
                            minions = [MasterTileIndexGenerator.Minion(tasks, results)for i in
                                       xrange(num_minions)]
                            # Start minions
                            ### MANDATORY CODE TO DEAL WITH ArcGIS 10.3.1 GLITCH ###
                            sys.argv = ['']
                            ### MANDATORY CODE TO DEAL WITH ArcGIS 10.3.1 GLITCH ###
                                # Glitch states the following:
                                # File "C;\Python27\ArcGIS10.3\Lib\multiprocessing\forking.py", line 399, in get_preparation_data
                                #     sys_argv=sys.argv,
                                # AttributeError: 'module' object has no attribute 'argv'
                            U = 1
                            for w in minions:
                                L.Wrap("Starting Minion {0}".format(U))
                                U = U + 1
                                w.start()
                            L.Wrap('')
                            #----------------------------- CLASS INSTANCE ENQUEUEING--------------------------------#
                            L.Wrap('#----------------------------- CLASS INSTANCE ENQUEUEING--------------------------------#')
                            L.Wrap('Adding class instances to task queue...')
                            no_sum_num = 0
                            sum_num = 0
                            batch_num = 8
                            no_sum_out = False
                            sum_out = False
                            total_instances = len(no_sum_files2enqueue) + len(sum_files2enqueue)
                            # Sorting files so LAS tiles are processed in the same order
                            no_sum_files2enqueue.sort(key=lambda x: x.las_path, reverse=False)
                            sum_files2enqueue.sort(key=lambda x: x.las_path, reverse=False)
                            # enqueueing
                            for queue_num in range(total_instances):
                                if not no_sum_out:
                                    try:
                                        for waste_variable in range(8):
                                            tasks.put(no_sum_files2enqueue[no_sum_num])
                                            no_sum_num += 1
                                    except:
                                        no_sum_out = True
                                if not sum_out:
                                    try:
                                        for waste_variable in range(8):
                                            tasks.put(sum_files2enqueue[sum_num])
                                            sum_num += 1
                                    except:
                                        sum_out = True
                            L.Wrap('{} PFI_Maker class instances added to queue.'.format(total_instances))
                            L.Wrap('')
                            #----------------------------MULTIPROCESSING FINISH---------------------------#
                            L.Wrap('#----------------------------MULTIPROCESSING FINISH---------------------------#')
                            L.Wrap('Waiting for minions to complete all jobs...')
                            multiStart = time.clock()
                            countCopy = enqueCount
                            timerList = []
                            timerList.append([time.clock(), countCopy])
                            resultList = []
                            Done = False
                            while countCopy > 0:
                                # Keep # Minions at num_minions
                                for w in minions:
                                    if not w.is_alive():
                                        L.Write('{} died on the job. Creating new one to pick up the slack...'.format(w.name))
                                        countCopy -= 1
                                        minions.remove(w)
                                        newMinion = MasterTileIndexGenerator.Minion(tasks, results)
                                        newMinion.start()
                                        minions.append(newMinion)
                                # Pull results to keep queue buffer from overflowing
                                try:
                                    multiprocessing_result = results.get(block=True, timeout=1)
                                    countCopy -= 1
                                    if multiprocessing_result == "Maxed":
                                        countCopy += 1
                                    else:
                                        resultList.append(multiprocessing_result)
                                        try:
                                            # Append multiprocessing_result to applicable final PFI file
                                            if not multiprocessing_result.Created is None:
                                                pfi_tile = multiprocessing_result.Created
                                                append_pfi_tile_to_master(pfi_tile,
                                                                          LiDAR_Model_Integration_Folder,
                                                                          coordinate_system,
                                                                          PFI_No_Summarize,
                                                                          PFI_Summarize)
                                        except Exception:
                                            L.Wrap('-------------------------------------------------------')
                                            L.Wrap('EXCEPTION:')
                                            L.Wrap(traceback.format_exc())
                                            L.Wrap('-------------------------------------------------------')
                                        try:
                                            # Delete Temporary LAS File from local drive (If created)
                                            if not multiprocessing_result.temp_las_file is None:
                                                temp_las_files.remove(multiprocessing_result.temp_las_file)
                                                if not multiprocessing_result.temp_las_file in temp_las_files:
                                                    try:
                                                        deleteReadOnly(multiprocessing_result.temp_las_file)
                                                    except Exception:
                                                        L.Wrap('-------------------------------------------------------')
                                                        L.Wrap('EXCEPTION:')
                                                        L.Wrap(traceback.format_exc())
                                                        L.Wrap('-------------------------------------------------------')
                                                    # Delete LASX file that was automatically generated as well
                                                    temp_lasx_file = multiprocessing_result.temp_las_file.replace(".las", ".lasx")
                                                    try:
                                                        deleteReadOnly(temp_lasx_file)
                                                    except Exception:
                                                        L.Wrap('-------------------------------------------------------')
                                                        L.Wrap('EXCEPTION:')
                                                        L.Wrap(traceback.format_exc())
                                                        L.Wrap('-------------------------------------------------------')
                                        except Exception:
                                            L.Wrap('-------------------------------------------------------')
                                            L.Wrap('EXCEPTION:')
                                            L.Wrap(traceback.format_exc())
                                            L.Wrap('-------------------------------------------------------')
                                    if countCopy < enqueCount:
                                        timerList.append([time.clock(), countCopy])
                                        if len(timerList) > 600:
                                            timerList.remove(timerList[0])
                                        timeTaken = time.clock() - timerList[0][0]
                                        tasksComplete = timerList[0][1] - countCopy
                                        secondsPerTask = timeTaken/tasksComplete
                                        secondsRemaining = countCopy * secondsPerTask
                                        remainingString = time2String(secondsRemaining)
                                        msg = '{} jobs left. Approx. {} remaining.'.format(countCopy, remainingString)
                                        missing_spaces = " " * (119 - len(msg))
                                        msg = '{}{}'.format(msg, missing_spaces)
                                        L.statusMsg(msg)
                                except Exception:
                                    multiprocessing_result = None
                                    if countCopy < enqueCount:
                                        timerList.append([time.clock(), countCopy])
                                        if len(timerList) > 600:
                                            timerList.remove(timerList[0])
                                        timeTaken = time.clock() - timerList[0][0]
                                        tasksComplete = timerList[0][1] - countCopy
                                        secondsPerTask = timeTaken/tasksComplete
                                        secondsRemaining = countCopy * secondsPerTask
                                        remainingString = time2String(secondsRemaining)
                                        msg = '{} jobs left. Approx. {} remaining.'.format(countCopy, remainingString)
                                        missing_spaces = " " * (119 - len(msg))
                                        msg = '{}{}'.format(msg, missing_spaces)
                                        L.statusMsg(msg)
                                    time.sleep(1)
                            # Add poison pill to queue so we can track when all processes are actually complete
                                 # This method is less glitchy than using a joinable queue
                            L.Wrap('All jobs complete.  Killing minions...')
                            for minion in minions:
                                if minion.is_alive():
                                    tasks.put(None)
                            # Waiting for poison pills to dissapear from queue, meaning the actual tasks are complete
                            L.Write('Waiting for minions to die...')
                            kill_time = time.clock()
                            while True:
                                size = tasks.qsize()
                                if size < 1:
                                    break
                                current_time = time.clock()
                                wait_time = current_time - kill_time
                                if wait_time > 30:
                                    break
                                else:
                                    msg = '{} Minions remaining'.format(size)
                                    L.statusMsg(msg)
                                time.sleep(1)
                            L.Write('All minions dead and accounted for.')
                            L.print_seperator_line()
                            L.Write('')
                            #--------------------------------Get Results----------------------------------#
                            L.Wrap('#--------------------------------Get Results----------------------------------#')
                            createdFiles = []
                            failedFiles = []
                            L.Wrap('Getting results...')
                            for specific_result in resultList:
                                if specific_result.Created is not None:
                                    createdFiles.append(specific_result.Created)
                                if specific_result.Failed is not None:
                                    failedFiles.append(specific_result.Failed)
                            L.Wrap('')
                            #--------------------------------Print Results--------------------------------#
                            L.Wrap('#--------------------------------Print Results--------------------------------#')
                            if len(failedFiles) > 0:
                                L.Wrap('')
                                L.Wrap('Files that failed processing:')
                                for f in failedFiles:
                                    L.Wrap(f)
                                L.Wrap('-------------------------------------------------------')
                            L.Wrap('')
                            L.Wrap('Total files enqueued = {}'.format(enqueCount))
                            L.Wrap('Total files created = {}'.format(len(createdFiles)))
                            L.Wrap('Total files that could not be created = {}'.format(len(failedFiles)))
                            L.Wrap('-------------------------------------------------------')
                            L.Time(multiStart, 'Waiting for PFI Multiprocessing')
                            L.Wrap('')
                        except:
                            for m in multiprocessing.active_children():
                                m.terminate()
                            L.Wrap('-------------------------------------------------------')
                            L.Wrap('EXCEPTION:')
                            L.Wrap(traceback.format_exc())
                            L.Wrap('-------------------------------------------------------')
                            raise
                    #-----------------------------Resume Single Process work----------------------#
                    L.Wrap('#-----------------------------Single Process work----------------------#')
                    # Check if PFI_No_Summarize_Valid exists and, if so, delete
                    L.Wrap(" ")
                    L.Wrap("Checking for PFI_No_Summarize_Valid.shp...")
                    if arcpy.Exists(PFI_No_Summarize_Valid) == True:
                        L.Wrap("PFI_Class_2 already exists. Deleting it to avoid"
                               " any errors that may have resulted from previous pro"
                               "cesses that failed to complete...")
                        arcDelete(PFI_No_Summarize_Valid)
                    # Create PFI_No_Summarize_Valid.shp
                    StartTime = time.clock()
                    L.Wrap("Creating PFI_No_Summarize_Valid.shp by executing arcpy.Select_analy"
                           "sis() with the following SQL conditions:")
                    L.Wrap('-Condition 1: "Pt_Spacing" < 100 (Eliminates Junk Tiles)')
                    L.Wrap('-Condition 2: "Pt_Count" > 1     (Eliminates Junk Tiles)')
                    arcpy.Select_analysis(in_features=PFI_No_Summarize,
                                          out_feature_class=PFI_No_Summarize_Valid,
                                          where_clause=""""Pt_Count" > 1 AND "Pt_Spacing" < 100""")
                    Files2Delete.append(PFI_No_Summarize_Valid)
                    L.Time(StartTime, "PFI_No_Summarize_Valid.shp")
                    # Check if PFI_Class_2.shp already exists and, if so, delete
                    L.Wrap(" ")
                    L.Wrap("Checking for PFI_Class_2.shp...")
                    if arcpy.Exists(PFI_Class_2) == True:
                        L.Wrap("PFI_Class_2 already exists. Deleting it to avoid"
                               " any errors that may have resulted from previous pro"
                               "cesses that failed to complete...")
                        arcDelete(PFI_Class_2)
                    # Create PFI_Class_2.shp
                    StartTime = time.clock()
                    L.Wrap("Creating PFI_Class_2.shp by executing arcpy.Select_analy"
                           "sis() with the following SQL conditions:")
                    L.Wrap('-Condition 1: "Class" = 2"')
                    L.Wrap('-Condition 2: "Pt_Spacing" < 100 (Eliminates Junk Tiles)')
                    L.Wrap('-Condition 3: "Pt_Count" > 1     (Eliminates Junk Tiles)')
                    arcpy.Select_analysis(in_features=PFI_Summarize,
                                          out_feature_class=PFI_Class_2,
                                          where_clause=""""Class" = 2 AND "Pt_Spacing" < 100 AND "Pt_Count" > 1""")
                    Files2Delete.append(PFI_Class_2)
                    # Add Class2APS field to PFI_Class_2
                    Check = arcpy.Exists(PFI_Class_2)
                    L.Wrap("Adding Class2APS field to PFI_Class_2...")
                    Check = arcpy.Exists(PFI_Class_2)
                    arcpy.AddField_management(PFI_Class_2, "Class2APS", "DOUBLE")
                    # Calculate Class2APS field in PFI_Class_2
                    L.Wrap("Calculating Class2APS field in PFI_Class_2...")
                    Check = arcpy.Exists(PFI_Class_2)
                    arcpy.CalculateField_management(in_table=PFI_Class_2,
                                                    field="Class2APS",
                                                    expression="!Pt_Spacing!",
                                                    expression_type="PYTHON",
                                                    code_block="#")
                    # Delete Pt_Spacing field from PFI_Class_2 to avoid any potential conflict
                    L.Wrap("Deleting 'Pt_Spacing' field from PFI_Class_2 before merging...")
                    Check = arcpy.Exists(PFI_Class_2)
                    arcpy.DeleteField_management(PFI_Class_2, "Pt_Spacing")
                    L.Time(StartTime, "PFI_Class_2")
                    # Check if PFI_Merge.shp already exists and, if so, delete
                    L.Wrap(" ")
                    L.Wrap("Checking for PFI_Merge...")
                    if arcpy.Exists(PFI_Merge) == True:
                        L.Wrap("PFI_Merge already exists. Deleting it to avoid any erro"
                               "rs that may have resulted from previous processes that "
                               "failed to complete...")
                        arcDelete(PFI_Merge)
                    # Create PFI_Merge.shp by merging PFI_Class_2 and PFI_No_Summarize_Valid
                    L.Wrap("Creating PFI_Merge.shp by merging PFI_No_Summarize_Valid and PFI_Class_2...")
                    StartTime = time.clock()
                    PFI_MergeList = [PFI_No_Summarize_Valid, PFI_Class_2]
                    for dataset in PFI_MergeList:
                        Check = arcpy.Exists(dataset)
                    arcpy.Merge_management(inputs=PFI_MergeList,
                                           output=PFI_Merge)
                    Check = arcpy.Exists(PFI_Merge)
                    Files2Delete.append(PFI_Merge)
                    L.Time(StartTime, "PFI_Merge")
                    # Create and edit tile index (Makes 5 attempts since it tends to fail)
                    #----------------------------Create Tile Index-----------------------------#
                    L.Wrap(" ")
                    L.Wrap("#----------------------------Create Tile Index-----------------------------#")

                    # Dissolve PFI_Merge by FileName to create new Tile_Index
                    StartTime = time.clock()
                    L.Wrap(str(time.ctime()))
                    L.Wrap("Creating Tile index by Dissolving PFI_Merge by FileName...")
                    Check = arcpy.Exists(PFI_Merge)
                    arcpy.Dissolve_management(in_features=PFI_Merge,
                                              out_feature_class=Tile_Index,
                                              dissolve_field="FileName",
                                              statistics_fields="Pt_Spacing MAX;Class2APS MAX",
                                              multi_part="MULTI_PART",
                                              unsplit_lines="DISSOLVE_LINES")
                    L.Time(StartTime, Tile_Index_Name)
                    #-------------------------Editing Tile Index Fields------------------------#
                    L.Wrap(" ")
                    L.Wrap("#-------------------------Editing Tile Index Fields------------------------#")
                    StartTime = time.clock()
                    L.Wrap("Making the following modifications to the Tile Index:")
                    Check = arcpy.Exists(Tile_Index)
                    # Add DataCode field
                    L.Wrap("Adding DataCode field")
                    arcpy.AddField_management(in_table=Tile_Index,
                                              field_name="DataCode",
                                              field_type="TEXT",
                                              field_precision="#",
                                              field_scale="#",
                                              field_length="254",
                                              field_alias="#",
                                              field_is_nullable="NULLABLE",
                                              field_is_required="NON_REQUIRED",
                                              field_domain="#")
                    Check = arcpy.Exists(Tile_Index)
                    # Calculate DataCode field
                    L.Wrap("Calculating DataCode field")
                    arcpy.CalculateField_management(in_table=Tile_Index,
                                                    field="DataCode",
                                                    expression=('"' + DatasetAbbreviation + '"'),
                                                    expression_type="PYTHON",
                                                    code_block="#")
                    Check = arcpy.Exists(Tile_Index)
                    # Add File_Name field
                    L.Wrap("Adding File_Name field")
                    arcpy.AddField_management(in_table=Tile_Index,
                                              field_name="File_Name",
                                              field_type="TEXT",
                                              field_precision="#",
                                              field_scale="#",
                                              field_length="254",
                                              field_alias="#",
                                              field_is_nullable="NULLABLE",
                                              field_is_required="NON_REQUIRED",
                                              field_domain="#")
                    Check = arcpy.Exists(Tile_Index)
                    # Calculate FileName field
                    L.Wrap("Calculating FileName field")
                    arcpy.CalculateField_management(in_table=Tile_Index,
                                                    field="File_Name",
                                                    expression="!FileName!",
                                                    expression_type="PYTHON",
                                                    code_block="#")
                    Check = arcpy.Exists(Tile_Index)
                    # Remove FileName field
                    L.Wrap("Removing FileName field")
                    arcpy.DeleteField_management(Tile_Index, "FileName")
                    Check = arcpy.Exists(Tile_Index)
                    # Add All_APS field
                    L.Wrap("Adding All_APS field")
                    arcpy.AddField_management(Tile_Index, "All_APS", "DOUBLE")
                    Check = arcpy.Exists(Tile_Index)
                    # Calculate All_APS field
                    L.Wrap("Calculating All_APS field")
                    arcpy.CalculateField_management(in_table=Tile_Index,
                                                    field="All_APS",
                                                    expression="!MAX_Pt_Spa!",
                                                    expression_type="PYTHON",
                                                    code_block="#")
                    Check = arcpy.Exists(Tile_Index)
                    # Remove MAX_Pt_Spa field
                    L.Wrap("Removing MAX_Pt_Spa field")
                    arcpy.DeleteField_management(Tile_Index, "MAX_Pt_Spa")
                    Check = arcpy.Exists(Tile_Index)
                    # Add Class2APS field
                    L.Wrap("Adding Class2APS field")
                    arcpy.AddField_management(Tile_Index, "Class2APS", "DOUBLE")
                    Check = arcpy.Exists(Tile_Index)
                    # Calculate Class2APS field
                    L.Wrap("Calculating Class2APS field")
                    arcpy.CalculateField_management(in_table=Tile_Index,
                                                    field="Class2APS",
                                                    expression="!MAX_Class2!",
                                                    expression_type="PYTHON",
                                                    code_block="#")
                    Check = arcpy.Exists(Tile_Index)
                    # Delete MAX_Class2 field
                    L.Wrap("Removing MAX_Class2 field")
                    arcpy.DeleteField_management(Tile_Index, "MAX_Class2")
                    Check = arcpy.Exists(Tile_Index)
                    # Add DataName field
                    L.Wrap("Adding DataName field")
                    arcpy.AddField_management(in_table=Tile_Index,
                                              field_name="DataName",
                                              field_type="TEXT",
                                              field_precision="#",
                                              field_scale="#",
                                              field_length="254",
                                              field_alias="#",
                                              field_is_nullable="NULLABLE",
                                              field_is_required="NON_REQUIRED",
                                              field_domain="#")
                    Check = arcpy.Exists(Tile_Index)
                    # Calculate DataName field
                    L.Wrap("Calculating DataName field")
                    arcpy.CalculateField_management(in_table=Tile_Index,
                                                    field="DataName",
                                                    expression=('"' + DatasetName + '"'),
                                                    expression_type="PYTHON",
                                                    code_block="#")

                    Check = arcpy.Exists(Tile_Index)
                    # Add LAS_Folder field to
                    L.Wrap("Adding LAS_Folder field")
                    arcpy.AddField_management(in_table=Tile_Index,
                                              field_name="LAS_Folder",
                                              field_type="TEXT",
                                              field_precision="#",
                                              field_scale="#",
                                              field_length="254",
                                              field_alias="#",
                                              field_is_nullable="NULLABLE",
                                              field_is_required="NON_REQUIRED",
                                              field_domain="#")
                    Check = arcpy.Exists(Tile_Index)
                    # Calculate LAS_Folder field
                    L.Wrap("Calculating LAS_Folder field")
##                        # qLAZFolder step is a glitch work-around:
##                        #   After switching from VBA to Python, the CalculateField
##                        #   function kept dropping one of the leading '\' characters
##                        #   from the final output table.
##                    qLAZFolder = 'r"' + laz_folder + '"'
                    arcpy.CalculateField_management(in_table=Tile_Index,
                                                    field="LAS_Folder",
                                                    expression=('r"' + laz_folder + '"'),
                                                    expression_type="PYTHON",
                                                    code_block="#")
                    Check = arcpy.Exists(Tile_Index)
                    # Change file extension to .laz
                    arcpy.CalculateField_management(Tile_Index,
                                                    "File_Name",
                                                    """!File_Name!.replace('.las','.laz')""",
                                                    "PYTHON",)
                    Check = arcpy.Exists(Tile_Index)
                    # Add SpatialRef field
                    L.Wrap("Adding SpatialRef field")
                    arcpy.AddField_management(in_table=Tile_Index,
                                              field_name="SpatialRef",
                                              field_type="TEXT",
                                              field_precision="#",
                                              field_scale="#",
                                              field_length="254",
                                              field_alias="#",
                                              field_is_nullable="NULLABLE",
                                              field_is_required="NON_REQUIRED",
                                              field_domain="#")
                    Check = arcpy.Exists(Tile_Index)
                    # Calculate SpatialRef field
                    L.Wrap("Calculating SpatialRef field")
##                        # qTile_Index step is a glitch work-around:
##                        #   After switching from VBA to Python, the CalculateField
##                        #   function kept dropping one of the leading '\' characters
##                        #   from the final output table.
##                    qTile_Index = 'r"' + Tile_Index + '"'
                    arcpy.CalculateField_management(in_table=Tile_Index,
                                                    field="SpatialRef",
                                                    expression=('r"' + Tile_Index + '"'),
                                                    expression_type="PYTHON",
                                                    code_block="#")
                    Check = arcpy.Exists(Tile_Index)
                    # Add FirstReturn field
                    L.Wrap("Adding FirstRetrn field")
                    arcpy.AddField_management(in_table=Tile_Index,
                                              field_name="FirstRetrn",
                                              field_type="TEXT",
                                              field_precision="#",
                                              field_scale="#",
                                              field_length="10",
                                              field_alias="#",
                                              field_is_nullable="NULLABLE",
                                              field_is_required="NON_REQUIRED",
                                              field_domain="#")
                    Check = arcpy.Exists(Tile_Index)
                    # Calculate FirstReturn field
                    L.Wrap("Calculating FirstReturn field")
                    arcpy.CalculateField_management(in_table=Tile_Index,
                                                    field="FirstRetrn",
                                                    expression=('"' + FirstReturn + '"'),
                                                    expression_type="PYTHON",
                                                    code_block="#")
                    L.Time(StartTime, "Updating Tile Index Fields")
                    del Check
                    break
                except Exception as F:
                    L.Wrap("EXCEPTION:")
                    Fail = arcpy.GetMessages(2)
                    L.Wrap("-----ArcPy Exception Output-----")
                    L.Wrap(Fail)
                    L.Wrap("-----ArcPy Exception Output-----")
                    L.Wrap("")
                    L.Wrap('--------TRACEBACK OUTPUT--------')
                    L.Wrap(traceback.format_exc())
                    L.Wrap('--------TRACEBACK OUTPUT--------')
                    L.Wrap('')
                    L.Wrap("Attempting to delete Tile_Index...")
                    try:
                        arcDelete(Tile_Index)
                    except Exception:
                        pass
                    if Attempt > 5:
                        raise
            L.Time(TileIndexStartTime, ("In total, creating " + Tile_Index_Name))
        #---------Make and populate LAZ Folder if it doens't exist already---------#
        if arcpy.Exists(las_folder) == True:
            L.Wrap("Compressing all LAS files into LAZ files in the laz_folder...")
            lasZipWrapper.Convert2LAZ(DatasetFolder)
            # Removing LAS Folder to save space
            Files2Shutil_rmtree.append(las_folder)
        #------------------------------Memory Clean-Up-----------------------------#
        StartTime = time.clock()
        L.Wrap(" ")
        L.Wrap("#------------------------------Memory Clean-Up-----------------------------#")
        # arcpy.Delete_management(Files in Files2Delete list)
        L.Wrap("Removing items in Files2Delete...")
        UniqueFiles2Delete = set(Files2Delete)
        for thing in UniqueFiles2Delete:
            Attempt = 0
            while Attempt < 5:
                Attempt = Attempt + 1
                try:
                    L.Wrap("Deleting " + thing)
                    arcDelete(thing)
                    break
                except Exception as F:
                    L.Wrap("EXCEPTION!!!")
                    L.Wrap(str(F))
                    L.Wrap("Attempt " + str(Attempt) + " failed.")
                    if Attempt < 5:
                        L.Wrap("Waiting 5 seconds and trying again...")
                        time.sleep(5)
                    else:
                        L.Wrap("No attempts remaining")
                        raise
        # shutil.rmtree(Files in Files2Shutil_rmtree)
        L.Wrap("Removing items in Files2Shutil_rmtree...")
        UniqueFiles2Shutil_rmtree = set(Files2Shutil_rmtree)
        for thing in UniqueFiles2Shutil_rmtree:
            Attempt = 0
            while Attempt < 5:
                Attempt = Attempt + 1
                try:
                    L.Wrap("Deleting " + thing)
                    shutil.rmtree(thing)
                    break
                except Exception as F:
                    L.Wrap("EXCEPTION!!!")
                    L.Wrap(str(F))
                    L.Wrap("Attempt " + str(Attempt) + " failed.")
                    if Attempt < 5:
                        L.Wrap("Waiting 5 seconds and trying again...")
                        time.sleep(5)
                    else:
                        L.Wrap("No attempts remaining")
                        raise
        # os.Remove(Files in Files_2_os_remove)
        L.Wrap("Removing items in Files_2_os_remove...")
        UniqueFiles_2_os_remove = set(Files_2_os_remove)
        for thing in UniqueFiles_2_os_remove:
            Attempt = 0
            while Attempt < 5:
                Attempt = Attempt + 1
                try:
                    L.Wrap("Deleting " + thing)
                    os.remove(thing)
                    break
                except Exception as F:
                    L.Wrap("EXCEPTION!!!")
                    L.Wrap(str(F))
                    L.Wrap("Attempt " + str(Attempt) + " failed.")
                    if Attempt < 5:
                        L.Wrap("Waiting 5 seconds and trying again...")
                        time.sleep(5)
                    else:
                        L.Wrap("No attempts remaining")
                        raise
        try:
            shutil.rmtree(dataset_temp_folder)
        except Exception:
            pass
        L.Time(StartTime, "Memory Clean-Up")
        L.Wrap(" ")
        L.Time(EntireTime, (str(time.ctime())+" - Entire DA Class for "+DatasetAbbreviation))
        L.Wrap(" ")
        return '%s\LiDAR Model Integration Folder\%s_Tile_Index.shp' % (self.Main_Dataset_Folder, self.Dataset_Abbreviation)
    def __str__(self):
        return '%s Tile Index' % (self.Dataset_Name)
# End of DatasetAssimilator


###############################################################################
###############################################################################
#################### ---- if __name__ == '__main__': ---- #####################
###############################################################################
###############################################################################



if __name__ == '__main__':
    MODULE_PATH = os.path.realpath(__file__)
    VP_INSTANCE = versionproof.RunScriptInArcMapPython32(MODULE_PATH)
    CORRECT_VERSION = VP_INSTANCE.ensure_correct_version()
    if CORRECT_VERSION:
        log_path = u'C:\\Temp\\LiDAR Index Generator\\Generator_Log.txt'
        L = JLog.PrintLog(Indent=0, Log=log_path, Delete=True)
        #-------------------------------Title Block----------------------------------#
        L.Wrap(" ")
        L.Wrap("###############################################################################")
        L.Wrap("##---------------------------------------------------------------------------##")
        L.Wrap("## ---------------------- Master Tile Index Generator ---------------------- ##")
        L.Wrap("##---------------------------------------------------------------------------##")
        L.Wrap("###############################################################################")

        #----------------------------Requesting Inputs--------------------------------#
        L.Wrap(" ")
        L.Wrap("#----------------------------Requesting Inputs--------------------------------#")
        # Request Input - Create Tile Indices from Scratch?
        CNI = raw_input("Create New Tile Indices from Scratch?")
        if CNI == "Y" or CNI == "y" or CNI == "Yes" or CNI == "yes" or CNI == "YES":
            CreateNewIndices = True
        if CNI == "N" or CNI == "n" or CNI == "No" or CNI == "no" or CNI == "NO" or CNI == "":
            CreateNewIndices = False
        L.Wrap("CreateNewIndices = " + str(CreateNewIndices))
        NUM_2_SKIP = raw_input('Dataset # to start on? (Press ENTER to start on first dataset)')
        try:
            NUM_2_SKIP = int(NUM_2_SKIP)
            L.Wrap('Starting from dataset {}'.format(NUM_2_SKIP))
            if NUM_2_SKIP > 0:
                NUM_2_SKIP -= 1
        except:
            L.Wrap('Non integer input received.  Starting from first dataset...')
            NUM_2_SKIP = 0
        #--------------------------------Import Libraries-----------------------------#
        L.Wrap(" ")
        L.Wrap("#--------------------------------Import Libraries-----------------------------#")

        ENTIRE_TIME = time.clock()
        # Import arcpy
        arcpyLoadStartTime = time.clock()
        L.Wrap("Importing arcpy...")
        import arcpy
        arcpyLoadTime = int(time.clock() - arcpyLoadStartTime)
        L.Wrap("arcpy loaded in " + str(arcpyLoadTime) + " seconds")
        # Check out any necessary licenses
        arcpy.CheckOutExtension("3D")
        # Enable Overwritting Geoprocessing Outputs
        arcpy.env.overwriteOutput = True
        import lasZipWrapper
        import RemoveGDBLocks

        #-------------------------------Local Variables-------------------------------#
        # Define Local Variables
        module_folder = os.path.dirname(os.path.realpath(__file__))
        DatasetsTable = '{}\\Datasets.gdb\\Datasets'.format(module_folder)
        Indices = []
        CE = []

        #----------------Creating DA instances for Datasets from Table----------------#
        L.Wrap(" ")
        L.Wrap("#----------------Creating DA instances for Datasets from Table----------------#")
        L.Wrap(" ")
        L.Wrap(" ")
        # Create Search Cursor for Datasets table
        L.Wrap("Creating Search Cursor using Master Datasets Table")
        Search = arcpy.da.SearchCursor(DatasetsTable, "*")
        # Iterrate on every row of the table
        L.Wrap("Iterating through Cursor Rows...")
        num_rows = 0
        for row in Search:
            num_rows += 1
            # Define Iteration Variables
            ID = str(row[0])
            Dataset_Name = row[1]
            Dataset_Abbreviation = row[2]
            Main_Dataset_Folder = row[3]
            coordinate_system = row[4]
            FirstReturn = row[5]
            # Creating Instance of DA and add it to the list of classes to execute (CE)
            L.Wrap("(Row {}) - Creating DA instance for {}".format(num_rows, Dataset_Name))
            a = DA(Dataset_Name,
                   Dataset_Abbreviation,
                   Main_Dataset_Folder,
                   coordinate_system,
                   FirstReturn,
                   CreateNewIndices)
            CE.append(a)
        L.Wrap(" ")
        L.Wrap("DA instances created for all datasets.")
        #----------------------------Collecting Results-------------------------------#
        L.Wrap(" ")
        L.Wrap("###############################################################################")
        L.Wrap("# --------------------------- Collecting Results ---------------------------- #")
        L.Wrap("###############################################################################")
        L.Wrap(" ")
        N = 1
        D = len(CE)
        dataset_number = 0
        for ClassInstance in reversed(CE):
            if not NUM_2_SKIP > dataset_number:
                L.Wrap(" ")
                middle = "# --------- Class " + str(N) + " of " + str(D) + " --------- #"
                L.Wrap("#" * len(middle))
                L.Wrap(middle)
                L.Wrap("#" * len(middle))
                L.Wrap(" ")
                L.Wrap(str(time.ctime()))
                L.Wrap(" ")
                N = N + 1
                INSTANCE = ClassInstance()
                Indices.append(INSTANCE)
            dataset_number += 1
        del N
        del D
        #-----------------Backup and Remove Previous Master Tile Index----------------#
        L.Wrap(" ")
        L.Wrap("###############################################################################")
        L.Wrap("# --------------- Backup and Remove Previous Master Tile Index -------------- #")
        L.Wrap("###############################################################################")
        L.Wrap(" ")
        # Define Local Variables
        BackupTime = time.clock()
        YMD = time.strftime("%Y_%m_%d", time.gmtime())
        module_folder = os.path.dirname(os.path.realpath(__file__))
        Master_Tile_Index_Folder = "{}\\Master Tile Index".format(module_folder)
        Master_Tile_Index_Backup_Folder = Master_Tile_Index_Folder + "\Backups"
        Master_Tile_Index_Backup_Date_Folder = Master_Tile_Index_Backup_Folder + "\\" + YMD
        Merged_Tile_Indices = "in_memory/Merged_Tile_Indices"
        ge_export_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(module_folder))))
        ge_export_folder = '{}\\GE Tools Package\\Data\\Other Datasets\\Data\\LiDAR\\Data'.format(ge_export_root)
        LiDAR_Availability = '{}\\LiDAR_Availability.kmz'.format(ge_export_folder)
        MasterGDB_Name = "SPK_LiDAR_Tile_Index"
        MasterGDB = Master_Tile_Index_Folder + "\\" + MasterGDB_Name + ".gdb"
        MasterGDB_Backup = Master_Tile_Index_Backup_Date_Folder + "\\" + MasterGDB_Name + ".gdb"
        MasterFeatureClassName = "SPK_LiDAR_Tool_Tile_Index"
        Master_Tile_Index = MasterGDB + "\\" + MasterFeatureClassName
        Tile_Index_Template_Layer_File = '{}\\Template Files\\LiDAR_Tiles_By_APS.lyr'.format(module_folder)
        # Determine Whether to Create a Backup Copy of the MasterGDB
        L.Wrap("Checking whether or not MaasterGDB exists...")
        if arcpy.Exists(MasterGDB) == True:
            # Check for Master Tile Index Backup Folder
            L.Wrap("Checking for Master_Tile_Index_backup_Folder...")
            if arcpy.Exists(Master_Tile_Index_Backup_Folder) == False:
                L.Wrap("Master_Tile_Index_Backup_Folder does not exist... creating...")
                # Create Master Tile Index Backup Folder
                arcpy.CreateFolder_management(out_folder_path=Master_Tile_Index_Folder,
                                              out_name="Backups")
            # Check for Master Tile Index Backup Date folder
            L.Wrap("Checking for Master_Tile_Index_Backup_Date_Folder...")
            if arcpy.Exists(Master_Tile_Index_Backup_Date_Folder) == True:
                L.Wrap("Deleting Master_Tile_Index_Backup_Date_Folder...")
                arcpy.Delete_management(in_data=Master_Tile_Index_Backup_Date_Folder,
                                        data_type="Workspace")
                L.Wrap("Master_Tile_Index_Backup_Date_Folder deleted")
            L.Wrap("Checking for Master_Tile_Index_Backup_Date_Folder...")
            if arcpy.Exists(Master_Tile_Index_Backup_Date_Folder) == False:
                L.Wrap("Master_Tile_Index_Backup_Date_Folder does not exist... creating...")
                # Create Master Tile Index Backup Date folder
                arcpy.CreateFolder_management(out_folder_path=Master_Tile_Index_Backup_Folder,
                                              out_name=YMD)
            # Copy MasterGDB to Master_Tile_Index_Backup_Date_Folder
            try:
                L.Wrap("Attempting to copy MasterGDB into Master_Tile_Index_Backup_Date_Folder...")
                shutil.copytree(MasterGDB, MasterGDB_Backup)
                L.Wrap("Backup created.")
            except Exception as exception:
                L.Wrap("shutil.copytree(MasterGDB, MasterGDB_Backup) failed...")
                L.Wrap(str(exception))
                pass
            # Remove GDB Locks that Arc May have left erroniously
            L.Wrap("Removing any Read/Write locks on MasterGDB...")
            RemoveGDBLocks.main(MasterGDB)
            # Delete MasterGDB
            L.Wrap("Deleting MasterGDB...")
            arcpy.Delete_management(in_data=MasterGDB, data_type="Workspace")
            L.Wrap("MasterGDB deleted.")
        L.Wrap("Checking if Master_Tile_Index already exists...")
        Exists = arcpy.Exists(Master_Tile_Index)
        if Exists == True:
            L.Wrap("Master_Tile_Index exists... deleting it...")
            arcDelete(Master_Tile_Index)
            L.Wrap("Master_Tile_Index deleted.")
        if Exists == False:
            L.Wrap("No previous version exists... moving on...")
        del Exists
        L.Time(BackupTime, "Backing up and then removing the previous index")
        #----------------Updating SPK_LiDAR_Tool_Master_Tile_Index----------------#
        L.Wrap(" ")
        L.Wrap("###############################################################################")
        L.Wrap("# ---------------- Updating SPK_LiDAR_Tool_Master_Tile_Index ---------------- #")
        L.Wrap("###############################################################################")
        L.Wrap(" ")
        # Merge all dataset tile indices into a single Master Tile Index shapefile
        StartTime = time.clock()
        L.Wrap("Merging all dataset tile indices into Merged_Tile_Indices...")
        arcpy.Merge_management(inputs=Indices, output=Merged_Tile_Indices)
        L.Time(StartTime, "Creating Merged_Tile_Indices")
        # Create new MasterGDB
        StartTime = time.clock()
        L.Wrap("Creating new version of MasterGDB...")
        arcpy.CreateFileGDB_management(Master_Tile_Index_Folder, MasterGDB_Name, "10.0")
        L.Time(StartTime, "Creating MasterGDB")
        # Re-project Merged_Tile_Indices into GDB in neutral projection
        StartTime = time.clock()
        L.Wrap("Re-Projecting Merged_Tile_Indices into Master Tile Index in WGS_1984_Web_Mercator_Auxiliary_Sphere...")
        arcpy.Project_management(in_dataset=Merged_Tile_Indices,
                                 out_dataset=Master_Tile_Index,
                                 out_coor_system="PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',"
                                 "GEOGCS['GCS_WGS_1984',"
                                 "DATUM['D_WGS_1984',"
                                 "SPHEROID['WGS_1984',6378137.0,298.257223563]],"
                                 "PRIMEM['Greenwich',0.0],"
                                 "UNIT['Degree',0.0174532925199433]],"
                                 "PROJECTION['Mercator_Auxiliary_Sphere'],"
                                 "PARAMETER['False_Easting',0.0],"
                                 "PARAMETER['False_Northing',0.0],"
                                 "PARAMETER['Central_Meridian',0.0],"
                                 "PARAMETER['Standard_Parallel_1',0.0],"
                                 "PARAMETER['Auxiliary_Sphere_Type',0.0],"
                                 "UNIT['Meter',1.0]]")
        L.Time(StartTime, "Master Tile Index")
        # Compact MasterGDB
        StartTime = time.clock()
        L.Wrap("Compacting MasterGDB...")
        arcpy.Compact_management(in_workspace=MasterGDB)
        L.Time(StartTime, "Compacting MasterGDB")
        # Compress MasterGDB
        StartTime = time.clock()
        L.Wrap("Compressing MasterGDB...")
        arcpy.CompressFileGeodatabaseData_management(in_data=MasterGDB, lossless="true")
        L.Time(StartTime, "Compressing MasterGDB")
        #----------------Exporting Master_Tile_Index to Google Earth----------------#
        if os.path.exists(ge_export_folder) is True:
            L.Wrap(" ")
            L.Wrap("###############################################################################")
            L.Wrap("# --------------- Exporting Master_Tile_Index to Google Earth --------------- #")
            L.Wrap("###############################################################################")
            L.Wrap(" ")
            StartTime = time.clock()
            # Check for / Remove LiDAR_availability
            L.Wrap("Attempting to remove previous vesion of " + LiDAR_Availability+"...")
            try:
                os.remove(LiDAR_Availability)
            except Exception as F:
                L.Wrap(str(F))
            # Create Layer because the KML Conversion tool breaks when you use a filepath
            L.Wrap("Creating Layer object to work with KML Conversion tool")
            Master_Tile_Index_Layer = arcpy.MakeFeatureLayer_management(Master_Tile_Index)
            # Import Symbology
            L.Wrap("Importing symbology from template layer")
            arcpy.ApplySymbologyFromLayer_management(in_layer=Master_Tile_Index_Layer,
                                                     in_symbology_layer=Tile_Index_Template_Layer_File)
            # Export to KMZ
            StartTime = time.clock()
            L.Wrap("Exporting DissolvedLayer to KMZ...")
            arcpy.LayerToKML_conversion(layer=Master_Tile_Index_Layer,
                                        out_kmz_file=LiDAR_Availability,
                                        layer_output_scale="0",
                                        is_composite="true",
                                        boundary_box_extent="#",
                                        image_size="5000",
                                        dpi_of_client="96",
                                        ignore_zvalue="CLAMPED_TO_GROUND")
            L.Time(StartTime, "LayerToKML")
            del Master_Tile_Index_Layer
        #------------------------------Memory Clean-Up--------------------------------#
        L.Wrap(" ")
        L.Wrap("###############################################################################")
        L.Wrap("# ----------------------------- Memory Clean-up ----------------------------- #")
        L.Wrap("###############################################################################")
        L.Wrap(" ")
        # arcDelete(Files in Files2Delete list)
        UniqueFiles2Delete = set(Files2Delete)
        for thing in UniqueFiles2Delete:
            Attempt = 0
            while Attempt < 5:
                Attempt = Attempt + 1
                try:
                    L.Wrap("Deleting " + thing)
                    arcpy.Delete_management(thing)
                    break
                except Exception as F:
                    L.Wrap("EXCEPTION!!!")
                    L.Wrap(str(F))
                    L.Wrap("Attempt " + str(Attempt) + " failed.")
                    if Attempt < 5:
                        L.Wrap("Waiting 5 seconds and trying again...")
                        time.sleep(5)
                    else:
                        L.Wrap("No attempts remaining")
                        raise
        # Delete Main Generator Temp Folder
        if NUM_2_SKIP == 0:
            L.Wrap('Deleting "C:\Temp\LiDAR Index Generator" (Temp folder)')
            temp_folder = u'C:\\Temp\\LiDAR Index Generator'
            for root, directories, file_names in os.walk(unicode(temp_folder), topdown=False):
                for file_name in file_names:
                    file_path = os.path.join(root, file_name)
                    try:
                        os_convenience.delete_read_only(file_path)
                    except Exception:
                        self.start_log()
                        self.log.Wrap('-------------------------------------------------------')
                        self.log.Wrap('EXCEPTION:')
                        self.log.Wrap(traceback.format_exc())
                        self.log.Wrap('-------------------------------------------------------')
                        self.log.Wrap('')
                for dir_name in directories:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        shutil.rmtree(dir_path)
                    except Exception:
                        self.start_log()
                        self.log.Wrap('-------------------------------------------------------')
                        self.log.Wrap('EXCEPTION:')
                        self.log.Wrap(traceback.format_exc())
                        self.log.Wrap('-------------------------------------------------------')
                        self.log.Wrap('')
        # Success Announcement
        L.Wrap(" ")
        L.Time(ENTIRE_TIME, "Successfull completion of all scheduled processes")
        # Hold window open for inspection
        Stall = raw_input("Press enter to exit")
