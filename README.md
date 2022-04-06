# Lidar Processing Workflow
This code processes raw lidar point clouds in order to calculate snow depth using PDAL. <br>
Lidar data were provided by the Airborne Snow Observatory (ASO), the National Center for Airborne Laser Mapping (NCALM), and Watershed Sciences Inc. (WSI). <br>

The goal of this project is to process snow depth to the one-meter spatial scale while maintaining conservative under-canopy estimates. Therefore, little interpolation occurs under-canopy. We follow these protocols in order to obtain a 1-m rasterized product (as opposed to the 3-m rasterized product provided by ASO on the NSIDC data portal). NCALM and WSI flights were obtained through OpenTopography.<br>

Here is the directory structure used to process files:
The *base structure* for flights = source_watershed_yyyymmdd (e.g. ASO_SCB_20160326)
The *base structure tile* for tiles = source_watershed_yyyymmdd_llx_lly (e.g. ASO_SCB_20160326_728000_4360000.laz)

```bash
All Flights
├── watershed (e.g. SCB, MRB)
│   ├── lidar_files (e.g. Sagehen_lidar, Merced_lidar)
│   │   ├── flight_source (e.g. ASO, NCALM, WSI)
│   │	│  	├── flight - source_watershed_yyyymmdd (e.g. ASO_SCB_20160326)
│   │	│  	│	├── corrected_lid: corrected for vertial bias (base structure tile.las/.laz)
│   │	│  	│	├── corrected_tif: corrected for vertial bias (base structure tile.tif)
│   │	│  	│	├── HAG: height above ground DEM (base structure tile.laz/.las)
│   │	│  	│	├── hwy89_vertical_bias
│   │	│  	│	│	├── clipped: merged file clipped to control area polygon, .laz/.las and .csv
│   │	│  	│	│	├── target_lid: files that overlap the control area, merged files (e.g. source_watershed_yyyymmdd_hwy89_merge.laz)
│   │	│  	│	├── laz: raw lidar files, from source
│   │	│  	│	├── NAD83_NAD83_epoch2010: reprojected tiles - base structure tile.las/.laz
│   │	│  	│	├── retile: lidar files tiled from 1000mx1000m - base structure tile.las/.laz
│   │	│  	│	├── tindex: tile indices or boundaries (tile filename.sqlite)
│   │	│  	│	│	├── original: boundary of original file 
│   │	│  	│	│	├── tiles: boundary of retiled files 
│   │	│  	│	├── VDATUM_processing: txt document containing VDATUM processing inputs - base structure tile.las/.laz
Snow-off Flights
│   │	│  	│	├── DEM_ground: rasterized ground_filtered files - base structure tile.tif
│   │	│  	│	├── ground_filtered: points filtered by Classification 2 (ground) - base structure tile.las/.laz
│   │	│  	│	├── veg_strata: HAG files filtered by Z values - base structure
│   │	│  	│	│	├── base structure_vegStrat_0pt15_2: Z values [0.15,2)
│   │	│  	│	│	│	├── lid: filtered lidar files, base structure tile.las/.laz
│   │	│  	│	│	│	├── tif: filtered lidar files rasterized by count, base structure tile.tif, merged files.tif
│   │	│  	│	│	├── vegStrat_gt2: Z values [2,inf)
│   │	│  	│	│	├── vegStrat_gt2_ground: Z values [2,inf), Classification 2
│   │	│  	│	│	├── vegStrat_gt2_nonground: Z values [2,inf), Classification not 2
│   │	│  	│	│	├── vegStrat_neg0pt15_0pt15: Z values [-0.15,0.15)
│   │	│  	│	│	├── base structure_open_strata1_2: first two strata classes, filtered from rasters based on Kost. et al., 2019 classification for open pixels
│   │	│  	│	│	├── base structure_open: open_strata1_2 filtered based on 3rd boundary from Kost. et al., 2019 
│   │	│  	│	│	├── base structure_tall_strata1_2: first two strata classes filtered from rasters based on Kost. et al., 2019 classification for pixels with tall veg
│   │	│  	│	│	├── base structure_tall: tall_strata1_2 filtered based on 3rd boundary from Kost. et al., 2019 


**retile_uo: use original tiles instead of retiled files
**strata classes (rasters) filtered in two stages to ensure GDAL captures logical expression
```

See PDAL documentation for more information about the structure of pipelines. Here, instead of using python PDAL bindings, we run processes using the subprocess module. We use a combination of functions that call json files and processes that directly call PDAL functions depending on the process.

Parallelization is initiated using multiple processes. Because the modules require functions to be called from imported packages, see lidar_functions.py for functions. Typically these functions execute pipelines using json files which allows us to alter json files in the script without altering the lidar_functions packages


# Raster Processing Workflow

Separate scripts were created for raster and LAS files. 
This script processes raster files created from the rasterization of LAS files. The goal is to run pixel-pixel calculations to retreive snow depth based on canopy structure classifications. 
