#pathname = 'lidar_processing/PDAL_testFiles_tutorials/test_las/SCB/retile/NCALM_2014_buff100/'
#glob.iglob(r'lidar_processing/PDAL_testFiles_tutorials/test_las/SCB/retile/NCALM_2014_buff100/*.laz')
import subprocess
import os
import json
def rename_retiles(full_path):
    import json
    pdal_info_command = ['pdal', 'info', full_path, '--metadata']
    pdal_info_results = subprocess.run(pdal_info_command, stdout = subprocess.PIPE) # stout (standard out), PIPE indicates that a new pipe to the child should be created
    pdal_info_dict = json.loads(pdal_info_results.stdout.decode())
    pathname = os.path.dirname(os.path.realpath(full_path)) + '/'
    name = pathname +str(round(pdal_info_dict['metadata']['minx'])) +"_"+ str(round(pdal_info_dict['metadata']['miny']))+full_path[-4:]
    os.rename(full_path, name)

# input - full folder path
# input_str - file data appended to front of filename i.e. /ASO_SCB_
def rename_llx_lly(full_path, input_str):
    pdal_info_command = ['pdal', 'info', full_path, '--metadata']
    pdal_info_results = subprocess.run(pdal_info_command, stdout = subprocess.PIPE) # stout (standard out), PIPE indicates that a new pipe to the child should be created
    pdal_info_dict = json.loads(pdal_info_results.stdout.decode())
    pathname = os.path.dirname(os.path.realpath(full_path))
    name = pathname + input_str +pathname[-15:-7]+'_'+ str(round(pdal_info_dict['metadata']['minx'])) +"_"+ str(round(pdal_info_dict['metadata']['miny']))+full_path[-4:]
    os.rename(full_path, name)