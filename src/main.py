import rasterio
import numpy as np
from pyproj import CRS, Transformer
import math
import random
import os

from transformations import (
    rowcol_to_xy,
    setup_transformer,
    setup_reverse_transformer,
    xy_to_latlong,
    latlong_to_xy,
    xy_to_rowcol,
    test_random_transformations,
    unzip_dem, 
    dataset_info
)

def main():
    base_dir=os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(base_dir)
    dem_path = 'data/MarsMGSMOLA_MAP2_EQUI.tif'
    dem_path_zip = 'data/MarsMGSMOLA_MAP2_EQUI.tif.zip'
    
    dem_path = os.path.join(parent_dir,dem_path)
    dem_path_zip = os.path.join(parent_dir,dem_path_zip)

    # Step 1: Unzip the DEM file if necessary
    try:
        unzip_dem(dem_path_zip, dem_path)
    except Exception as e:
        print(f"Error during extraction: {e}")
        exit(1)
    
    # Step 2: Display dataset information
    try:
        dataset_info()
    except Exception as e:
        print(f"Error reading DEM data: {e}")
        exit(1)


    with rasterio.open(dem_path) as data:
        array_2d = data.read(1)
        profile = data.profile
        affine_transform = data.transform  
        crs = data.crs
    
        inverse_affine = ~affine_transform

        transformer = setup_transformer(crs)
        inverse_transformer = setup_reverse_transformer(crs)

    #test_random_transformations(num_tests=1000)

    
    




if __name__ == "__main__":
    main()