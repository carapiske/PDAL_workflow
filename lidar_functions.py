# Created S '22 by Cara Piske for M.S. thesis in Hydrologic Sciences at the University of Nevada, Reno
# Advisor: Adrian Harpold
# supporting functions to allow for parallel processing of lidar tiles

# import supporting packages
import subprocess
import os
import json
json_path = 'piske_processing/PDAL_workflow/JSON/'

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
    
# run similar function except add in file size. This is helpful for retiled files where there may be redundant llx_lly values and it's helpful to know when to target 
# files for visualization 
# file structure will be count (*10^5)_llx_lly
def rename_llx_lly_b(full_path):
    
    pdal_info_command = ['pdal', 'info', full_path, '--metadata'] # set up pdal info command
    pdal_info_results = subprocess.run(pdal_info_command, stdout = subprocess.PIPE) # stout (standard out), PIPE indicates that a new pipe to the child should be created, execute command
    pdal_info_dict = json.loads(pdal_info_results.stdout.decode()) # save metadata to dictionary
    pathname = os.path.dirname(os.path.realpath(full_path)) # isolate only pathname (i.e. 'folder1/folder2/SCB/flight1/lid_files/')
    new_name = os.path.join(pathname, str(round(pdal_info_dict['metadata']['minx'])) +"_"+ str(round(pdal_info_dict['metadata']['miny']))+full_path[-4:])    
    if os.path.exists(new_name):
        lidar_folder = pathname
        onlyfiles = [f for f in os.listdir(lidar_folder) if os.path.isfile(os.path.join(lidar_folder, f))]
        full_paths = [os.path.join(lidar_folder, s) for s in onlyfiles] 
        full_str = ','.join(full_paths)
        num_occurences = full_str.count(new_name[:-4])
        new_name_b = new_name[:-4]+'_'+str(num_occurences)+new_name[-4:]
        os.rename(full_path, new_name_b)
    else:
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

# input_lid 'folder1/folder2/folder3a/filename.laz' and output_lid 'folder1/folder2/folder3b/filename.laz'
# if files are held in a different file structure, code must be changed to accomodate change
# input - full path to a lid file [str]
# output_path - path to folder with ICB tiles (e.g. 'path/to/folder/') [str]
def copy_lid_by_ext_ICB(full_path, output_path):
    pdal_info_command = ['pdal', 'info', full_path, '--metadata'] # set up pdal command
    pdal_info_results = subprocess.run(pdal_info_command, stdout = subprocess.PIPE) # stout (standard out), PIPE indicates that a new pipe to the child should be created, execute command
    pdal_info_dict = json.loads(pdal_info_results.stdout.decode()) # save metadata to dict
    # extract llx,lly of tile
    minx = pdal_info_dict['metadata']['minx']
    miny = pdal_info_dict['metadata']['miny']
    maxx = pdal_info_dict['metadata']['maxx']
    maxy = pdal_info_dict['metadata']['maxy']
    # if file origin is within bounds of ICB extents, copy the file
    if (minx <= 288000 and maxx >= 265000):
        if (maxy >= 4165000 and miny<= 4180000):
            input_lid = full_path
            output_lid = output_path + os.path.basename(full_path)
            pdal_copy_cmd = ['pdal','translate', input_lid, output_lid]
            subprocess.run(pdal_copy_cmd)

#########################################################

##########
# GROUND FILTER
#########

# filter 
def ground_filter_preClassified(full_input_path, full_output_path):
    json_full_path = json_path + 'ground_filter_preClassified.json'
    range_cmd = ['pdal', 'translate', full_input_path,  full_output_path, '--json',json_full_path]
    subprocess.run(range_cmd)

########################################################

##########
# HAG DEM
##########
def ground_filter_rasterize(full_output_path):
    json_full_path = json_path + 'DEM_from_las.json'
    #reader = '--filters.merge.inputs='+ full_input_list
    writer = '--writers.gdal.filename='+ full_output_path
    strata_cmd = ['pdal', 'pipeline', json_full_path, writer]
    subprocess.run(strata_cmd)




########################################################

##########
# HAG DEM
##########

# filter points by heigh above rasterized dem
# input - full path to lidar file ('path/to/lidar/file/filename.laz') [str]
# output - full path to lidar file ('path/to/lidar/file/filename.laz') [str]

def HAG_dem(full_input_path, full_output_path):
    json_full_path = json_path + 'HAG_dem.json'
    strata_cmd = ['pdal', 'translate', full_input_path,  full_output_path, '--json',json_full_path]
    subprocess.run(strata_cmd)
    
##########
# HAG DEM Range Filtered
##########
# Filter snow-off lidar into vegetation strata defined by Kost et al., 2019

# input - full path to lidar file ('path/to/lidar/file/filename.laz') [str]
# output - full path to lidar file ('path/to/lidar/file/filename.laz') [str]
def filter_pts_neg0pt15_0pt15(full_input_path, full_output_path):
    json_full_path = json_path + 'filter_pts_neg0pt15_0pt15.json'
    reader = '--readers.las.filename='+ full_input_path
    writer = '--writers.gdal.filename='+ full_output_path
    strata_cmd = ['pdal', 'pipeline', json_full_path, writer, reader]
    subprocess.run(strata_cmd)

def filter_pts_0pt15_2(full_input_path, full_output_path):
    json_full_path = json_path + 'filter_pts_0pt15_2.json'
    reader = '--readers.las.filename='+ full_input_path
    writer = '--writers.gdal.filename='+ full_output_path
    strata_cmd = ['pdal', 'pipeline', json_full_path, writer, reader]
    subprocess.run(strata_cmd)

def filter_pts_2(full_input_path, full_output_path):
    json_full_path = json_path + 'filter_pts_2.json'
    reader = '--readers.las.filename='+ full_input_path
    writer = '--writers.gdal.filename='+ full_output_path
    strata_cmd = ['pdal', 'pipeline', json_full_path, writer, reader]
    subprocess.run(strata_cmd)

def filter_pts_2_ground(full_input_path, full_output_path):
    json_full_path = json_path + 'filter_pts_2_ground.json'
    reader = '--readers.las.filename='+ full_input_path
    writer = '--writers.gdal.filename='+ full_output_path
    strata_cmd = ['pdal', 'pipeline', json_full_path, writer, reader]
    subprocess.run(strata_cmd)
    
def filter_pts_2_nonground(full_input_path, full_output_path):
    json_full_path = json_path + 'filter_pts_2_nonground.json'
    reader = '--readers.las.filename='+ full_input_path
    writer = '--writers.gdal.filename='+ full_output_path
    strata_cmd = ['pdal', 'pipeline', json_full_path, writer, reader]
    subprocess.run(strata_cmd)
########################################################

##########
# Correct Lidar Files
##########

# Correct lidar files by a target value calculated from taking the difference between two snow-off sections in a target region
# using the PDAL assign filter

# input: full_input_path - full path to input lidar file [str]
# input: full_output_path - full path to output lidar file [str]
def correct_by_targetVal_rasterize(full_input_path, full_output_path):
    json_full_path = json_path + 'correct_by_targetVal_rasterize.json'
    reader = '--readers.las.filename='+ full_input_path
    writer = '--writers.gdal.filename='+ full_output_path
    correct_cmd = ['pdal', 'pipeline', json_full_path, writer, reader]
    subprocess.run(correct_cmd)

def correct_by_targetVal(full_input_path, full_output_path, target_assign):
    input_lid = full_input_path
    output_lid = full_output_path
    filters_assign = '--filters.assign.value=Z='+target_assign
    assign_cmd = ['pdal', 'translate', input_lid, output_lid, 'assign' ,filters_assign]
    subprocess.run(assign_cmd)


########################################################
##########
# Rasterize
##########
def rasterize_mean(full_input_lid, full_output_tif):
    json_full_path = json_path + 'rasterize_mean.json'
    writer = '--writers.gdal.filename='+full_output_tif
    reader = '--readers.las.filename='+full_input_lid
    rasterize_command = ['pdal', 'pipeline',json_full_path, writer, reader]
    subprocess.run(rasterize_command)

def rasterize_count(full_input_lid, full_output_tif):
    json_full_path = json_path + 'rasterize_count.json'
    writer = '--writers.gdal.filename='+full_output_tif
    reader = '--readers.las.filename='+full_input_lid
    rasterize_command = ['pdal', 'pipeline', json_full_path, writer, reader]
    subprocess.run(rasterize_command)

