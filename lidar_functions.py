# Created S '22 by Cara Piske for M.S. thesis in Hydrologic Sciences at the University of Nevada, Reno
# Advisor: Adrian Harpold
# supporting functions to allow for parallel processing of lidar tiles

# import supporting packages
import subprocess
import os
import json
import numpy as np
from osgeo import gdal, ogr, osr

json_path = 'piske_processing/PDAL_workflow/JSON/'


##########
# Change Formats
##########
json_full_path = json_path + 'las_to_laz.json'

def las_to_laz(full_input_path, full_output_path):
    json_full_path = json_path + 'las_to_laz.json'
    reader = '--readers.las.filename='+ full_input_path
    writer = '--writers.las.filename='+ full_output_path
    strata_cmd = ['pdal', 'pipeline', json_full_path, writer, reader]
    subprocess.run(strata_cmd)


##########
# Check Extents
##########
# full_paths - list of full paths of all tiles in a folder

def check_flight_extent(full_paths):
    min_x = 10000000
    min_y = 10000000
    max_x = 0
    max_y = 0
    for tiles in full_paths:
        pdal_info_command = ['pdal', 'info', tiles, '--metadata'] # set up pdal info command
        pdal_info_results = subprocess.run(pdal_info_command, stdout = subprocess.PIPE) # stout (standard out), PIPE indicates that a new pipe to the child should be created, execute command
        pdal_info_dict = json.loads(pdal_info_results.stdout.decode()) # save metadata to dictionary
        if min_x > pdal_info_dict['metadata']['minx']:
            min_x = pdal_info_dict['metadata']['minx']
        if min_y > pdal_info_dict['metadata']['miny']:
            min_y = pdal_info_dict['metadata']['miny']
        if max_x < pdal_info_dict['metadata']['maxx']:
            max_x = pdal_info_dict['metadata']['maxx']
        if max_y < pdal_info_dict['metadata']['maxy']:
            max_y = pdal_info_dict['metadata']['maxy']
    extents = [min_x, max_x, min_y, max_y, max_x - min_x, max_y - min_y]

    return(extents)

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
    
# run similar function except add in file tag. This is helpful for retiled files where there may be redundant llx_lly values 
def rename_llx_lly_repeats(full_path):
    
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
def copy_by_ext_ICB(full_path, output_path):
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
    
###########################################################
# Vertical Bias Corrections
############################################################

###########
# Calculate Vertical Bias from HAG measurements - where HAG input file is over a snow-off area (e.g. hwy89)
###########
# this function is useful where the input file is a direct measure of bias, for example the 2016 ASO flights over SCB
# where hwy 89 is used as for vbc, in this case points over hwy89 are extracted

# input_las - HAG, las file clipped to the road
# output_path - path to output files
# base_name - string, typically flight name
def calculate_vertical_bias_over_snowOff(input_las):
    # convert height only to txt file
    output_las_txt = input_las[:-3]+'csv'
    txt_cmd = ['pdal', 'translate', input_las, output_las_txt, '-w', 'writers.text', '--writers.text.format=csv','--writers.text.order=Z', '--writers.text.keep_unspecified=false']
    subprocess.run(txt_cmd)
    # calculate stats
    hag_arr = np.loadtxt(output_las_txt,skiprows=1)
    lowest_10th_per = np.nanpercentile(hag_arr, 10)
    mean_hag = np.nanmean(hag_arr)
    median_hag = np.nanmedian(hag_arr)
    stats = ["lowest_10th",lowest_10th_per, "mean",mean_hag, "median", median_hag]
    return(stats)


###########################################################
# Extract Vegetation Heigh Strata
############################################################

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

#######################################################
##########
# Create Command Template
##########
# Many other commands can be run in parallel, but it is beneficial to rasterize using a combined pipeline menthod
#   where we merge las files in one stage and write to a raster in the next
#   we can filter post-merging. This is helpful because it allows us to avoid discrepancies
#   between tile boundaries in the final rasterized product. It also allows us to merge las files
#   without having to write a large merged file or read in a merged file (saving disk memory)

# input_path - path to lidar files (e.g. '/path/to/HAG/')
def create_command_template(input_path):
    onlyfiles = [f for f in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, f))] # make a list of all filenames in directory
    input_list = [input_path + s for s in onlyfiles] # make a list of full filename paths in directory
    filename_dict = {} # initiate an empty dict to hold the readers
    tags = ['']*len(input_list) # initiate an empty list, size = number of files
    filenames = ['']*len(input_list) # repeat
    for i in range(len(input_list)): # for each file, create a dictionary element with the values matching json formatting for file merging
        filename_dict['filename_'+str(i)] = {'filename':input_list[i], 'tag':'A_'+str(i)}
        tags[i] = 'A_'+str(i) # add a tag to the reader stage
        filenames[i] = filename_dict[list(filename_dict)[i]] # Add all values to a list
    
    return(filenames, tags)

#######################################################
#########
# Raster to Array
#########
# input: path - full file path
# input: nd_value - num, no data value (i.e. -9999) 
def raster_to_array(path, nd_value):
    raster = gdal.Open(path) # open the file 
    raster_arr = raster.GetRasterBand(1).ReadAsArray() #read the first raster band (in this case we know we are only working with single bands) and read to a 2D array
    if raster_arr.dtype == 'int32':
        raster_arr = raster_arr.astype(float)
    raster_arr[raster_arr == nd_value] = np.nan # where the raster is equal to the provided no data value, set values to Nan
    raster_arr_flat = raster_arr.flatten() # flatten the array (row-wise)
    raster = None
    return raster_arr_flat