# Created S '22 by Cara Piske for M.S. thesis in Hydrologic Sciences at the University of Nevada, Reno
# Advisor: Adrian Harpold
# supporting functions to allow for parallel processing of lidar tiles

# import supporting packages
import subprocess
import os
import json
json_path = 

##########
# RENAME
##########


# Many files come with inconsistent naming (including unsupported characters...)
# Rename all files to maintain consistency

# Rename a file with the lower left x and y defined as the corner point of the bounding box (add resolution/2 to get the center point of the box) 
# input - full lidar file path (i.e. 'folder1/folder2/SCB/flight1/lid_files/filename.laz'), [str]

def rename_llx_lly(full_path):
    
    pdal_info_command = ['pdal', 'info', full_path, '--metadata'] # set up pdal info command
    pdal_info_results = subprocess.run(pdal_info_command, stdout = subprocess.PIPE) # stout (standard out), PIPE indicates that a new pipe to the child should be created, execute command
    pdal_info_dict = json.loads(pdal_info_results.stdout.decode()) # save metadata to dictionary
    
    pathname = os.path.dirname(os.path.realpath(full_path)) # isolate only pathname (i.e. 'folder1/folder2/SCB/flight1/lid_files/')
    new_name = os.path.join(pathname, str(round(pdal_info_dict['metadata']['minx'])) +"_"+ str(round(pdal_info_dict['metadata']['miny']))+full_path[-4:])    
    os.rename(full_path, new_name) # rename file
    

# Rename a file with additional metadata at the beginning of the filename
# Flight organization, watershed, date of flight (i.e. ASO_ICB_20140423)
# Additional text will be taken from the flight directory name, could hardcode additional string instead of using folder name; redefine function as add_str_to_filename(full_path, add_str): and comment out the "add_str" lines of function

# input - full lidar file path (i.e. 'folder1/folder2/flight1/filename.laz'), [str]

def add_str_to_filename(full_path):
    filename = os.path.basename(full_path) # isolate only filename (i.e 'filename.laz')
    pathname = os.path.dirname(os.path.realpath(full_path)) # isolate only path name (i.e. 'lidar/lidar_files')
    
    add_str = os.path.normpath(pathname) # split up the path name (i.e. full path)
    add_str = [i for i in add_str.split(os.sep) if (i.startswith('ASO_') or i.startswith('NCALM_') or i.startswith('WSI_'))] # (i.e. 'ASO_SCB_2016')
    rename = os.path.join(pathname, add_str[0]+ '_' + filename)
    os.rename(full_path, rename) # rename file

#######################################################################
    
    
    
##########
# TILE INDEX
########## 
    
# save the tile index of a file to a new folder

# input - full lidar/sqlite file patsh (i.e. 'lidar/lidar_files/filename.laz'), [str, str]
def create_tindex(input_path, output_path):
    boundary_cmd = ['pdal', 'tindex', 'create', '--tindex', output_path, '--filespec', input_path, '-f', 'SQLite']
    subprocess.run(boundary_cmd)

####################################################


##########
# COPY FILES TO NEW LOCATION
##########
    
    
# copy file based on llx and lly into output filename. Note that this function relies on the assumption that files follow the structure 

# input_las 'folder1/folder2/folder3a/filename.laz' and output_las 'folder1/folder2/folder3b/filename.laz'
# if files are held in a different file structure, code must be changed to accomodate change
# input - full path to a las file [str]

def copy_las_by_ext_ICB(full_path):
    pdal_info_command = ['pdal', 'info', full_path, '--metadata'] # set up pdal command
    pdal_info_results = subprocess.run(pdal_info_command, stdout = subprocess.PIPE) # stout (standard out), PIPE indicates that a new pipe to the child should be created, execute command
    pdal_info_dict = json.loads(pdal_info_results.stdout.decode()) # save metadata to dict
    # extract llx,lly of tile
    minx = round(pdal_info_dict['metadata']['minx'])
    miny = round(pdal_info_dict['metadata']['miny'])
    # if file origin is within bounds of ICB extents, copy the file
    if (minx <= 288000 and minx >= 265000):
        if (miny >= 4165000 and miny<= 4180000):
            input_las = full_path
            output_las =             output_las = os.path.join(os.path.dirname(os.path.realpath(os.path.dirname(os.path.realpath(full_path)))), 'retile_ICB', os.path.basename(full_path))
            pdal_copy_cmd = ['pdal','translate', input_las, output_las]
            subprocess.run(pdal_copy_cmd)

#########################################################

##########
# GROUND FILTER
#########

# filter 
def ground_filter(full_input_path, full_output_path):
    range_cmd = ['pdal', 'translate', full_input_path,  full_output_path, '--json','/Volumes/cpiske/lidar_processing/python_scripts/PDAL_workflow/JSON/ground_filter_preClassified.json']
    subprocess.run(range_cmd)

def rasterize_mean(full_input_las, full_output_tif):
    writer = '--writers.gdal.filename='+full_output_tif
    reader = '--readers.las.filename='+full_input_las
    rasterize_command = ['pdal', 'pipeline', '/Volumes/cpiske/lidar_processing/python_scripts/PDAL_workflow/JSON/las_to_tif_mean.json', writer, reader]
    subprocess.run(rasterize_command)

def rasterize_count(full_input_las, full_output_tif):
    writer = '--writers.gdal.filename='+full_output_tif
    reader = '--readers.las.filename='+full_input_las
    rasterize_command = ['pdal', 'pipeline', '/Volumes/cpiske/lidar_processing/python_scripts/PDAL_workflow/JSON/las_to_tif_count.json', writer, reader]
    subprocess.run(rasterize_command)

def HAG_dem(full_input_path, full_output_path):
    HAG_cmd = ['pdal', 'translate',full_input_path, full_output_path, '--json', '/Volumes/cpiske/lidar_processing/python_scripts/PDAL_workflow/JSON/heigh_above_ground_vegStrata.json']
    subprocess.run(HAG_cmd)

def filter_pts_neg0pt15_0pt15(full_input_path, full_output_path):
    strata_cmd = ['pdal', 'translate', full_input_path,  full_output_path, '--json','/Volumes/cpiske/lidar_processing/python_scripts/PDAL_workflow/JSON/filter_range_neg0pt15_0pt15.json']
    subprocess.run(strata_cmd)
