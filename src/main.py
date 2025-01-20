import rasterio
import numpy as np
from pyproj import CRS, Transformer
import math
import random

from transformations import (
    rowcol_to_xy,
    setup_transformer,
    setup_reverse_transformer,
    xy_to_latlong,
    latlong_to_xy,
    xy_to_rowcol,
    test_random_transformations
)

def main():
    dem_path = 'data/NASAdem/MarsMGSMOLA_MAP2_EQUI.tif'
    with rasterio.open(dem_path) as data:
        array_2d = data.read(1)
        profile = data.profile
        affine_transform = data.transform  
        crs = data.crs
    
        inverse_affine = ~affine_transform

        transformer = setup_transformer(crs)
        inverse_transformer = setup_reverse_transformer(crs)

    test_random_transformations(num_tests=1000)



if __name__ == "__main__":
    main()
