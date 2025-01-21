import rasterio
import numpy as np
from pyproj import CRS, Transformer
import math
import random
import os
import zipfile

base_dir=os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
dem_path = 'data/MarsMGSMOLA_MAP2_EQUI.tif'
dem_path_zip = 'data/MarsMGSMOLA_MAP2_EQUI.tif.zip'

dem_path = os.path.join(parent_dir,dem_path)
dem_path_zip = os.path.join(parent_dir,dem_path_zip)

def unzip_dem(zip_file_path, extract_to_path):
    #If .tif file already exists
    if os.path.exists(extract_to_path):
        return
    
    #Check zip files exists
    if not os.path.exists(zip_file_path):
        raise FileNotFoundError(f"The zip file '{zip_file_path}' does not exist.")
    
    #Extract .zip
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        tif_file = zip_ref.namelist()[0]
        zip_ref.extract(tif_file, path=os.path.dirname(extract_to_path))
        
        print(f"Extracted '{tif_file}' to '{extract_to_path}'.")

#FOR FORWARD TRANSFORMATION
def setup_transformer(crs):
    #This is the CRS given in the dataset
    source_crs = CRS.from_wkt(str(crs))
    
    #This is the CRS we are trying to obtain
    target_crs = CRS.from_proj4(
        "+proj=latlong +a=3396190 +b=3396190 +R=3396190 +unit=degrees +no_defs"
    )

    #Create the transformer
    transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
    return transformer

def rowcol_to_xy(row, col, affine_transformation):
    #Apply affine transformation from the DEM data
    x, y = affine_transformation * (col, row)
    return x, y

def xy_to_latlong(x, y, transformer):
    longitude, latitude = transformer.transform(x, y)
    return latitude, longitude

#FOR BACKWARD TRANSFORMATION
def setup_reverse_transformer(crs):
    #Switch target and source for reverse transformer
    target_crs = CRS.from_proj4(
        "+proj=latlong +a=3396190 +b=3396190 +R=3396190 +unit=degrees +no_defs"
    )
    source_crs = CRS.from_wkt(str(crs))

    inverse_transformer = Transformer.from_crs(target_crs, source_crs, always_xy=True)

    return inverse_transformer

def latlong_to_xy(latitude, longitude, inverse_transformer):
    radius_of_mars = 3396190
    x, y = inverse_transformer.transform(longitude, latitude)
    circumference = 2 * math.pi * radius_of_mars
    x = x % circumference  #normalize X to [0, circumference)
    return x, y

def xy_to_rowcol(x, y, inverse_affine, epsilon=1e-4):
    col_float, row_float = inverse_affine * (x, y)
    
    #Adjust rounding for precision
    row = int(math.floor(row_float + 0.5 + epsilon))
    col = int(math.floor(col_float + 0.5 + epsilon))

    return row, col 


def dataset_info():
    with rasterio.open(dem_path) as data:
        array_2d = data.read(1)
        profile = data.profile
        affine_transformation = data.transform   
        crs = data.crs
         
    print(array_2d.shape)
    print(array_2d)
    print("Min:", np.nanmin(array_2d))
    print("Max:", np.nanmax(array_2d))
    print("Mean:", np.nanmean(array_2d))

    print("DEM shape:", data.shape)
    print("------")
    print("CRS:", crs)
    print("------")
    print("Transform:", affine_transformation)
    print("------")
    print("Profile:", profile)

def test_random_transformations(num_tests):
    with rasterio.open(dem_path) as data:
        affine_transformation = data.transform  
        crs = data.crs
        dem_shape = data.shape

        #Invert the affine transformation
        inverse_affine = ~affine_transformation

    transformer = setup_transformer(crs)
    inverse_transformer = setup_reverse_transformer(crs)

    success_count = 0
    failure_count = 0

    for i in range(num_tests):
        # Randomly select row and col within valid range
        row = random.randint(1, dem_shape[0] - 1)
        col = random.randint(1, dem_shape[1] - 1)
        
        #Forward
        x, y = rowcol_to_xy(row, col, affine_transformation)
        lat, long = xy_to_latlong(x, y, transformer)

        #Backwards
        inv_x, inv_y = latlong_to_xy(lat, long, inverse_transformer)
        inv_row, inv_col = xy_to_rowcol(inv_x, inv_y, inverse_affine)

        # Validation
        if inv_row == row and inv_col == col:
            success_count += 1
        else:
            failure_count += 1

    print("----Results------")
    print(f"Total Tests: {num_tests}")
    print(f"Successful Transformations: {success_count}")
    print(f"Failed Transformations: {failure_count}")




