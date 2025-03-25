import rasterio
import numpy as np
import pyvista as pv
import PySimpleGUI as sg
from rasterio.windows import Window
import os
from pyvistaqt import QtInteractor
from transformations import (
    unzip_dem, 
    dataset_info
)

def load_dem_to_pyvista(dem_path, window=None, decimation=1):
    """
    Load a DEM and convert it to a 3D terrain mesh for PyVista.
    
    Parameters:
        dem_path (str): Path to the DEM file.
        window (rasterio.windows.Window, optional): A window to read a subset of the data.
        decimation (int): Factor to downsample the data.
    
    Returns:
        pv.StructuredGrid: A PyVista structured grid representing the terrain.
    """
    with rasterio.open(dem_path) as data:
        # Read either a window of data or the full dataset.
        if window:
            array_2d = data.read(1, window=window)
            transform = data.window_transform(window)
        else:
            array_2d = data.read(1)
            transform = data.transform

        # Remove the first row and first column since valid values are from row 1 and col 1.
        array_2d = array_2d[1:, 1:]
        
        # Downsample the array if decimation > 1
        if decimation > 1:
            array_2d = array_2d[::decimation, ::decimation]

        # Compute the pixel resolution from the transform
        x_res, y_res = transform.a, -transform.e

        # New dimensions after removing the first row/column.
        height, width = array_2d.shape

        # Adjust X and Y coordinates: 
        # For X, skip the first column -> start at transform.c + x_res.
        x = transform.c + x_res * (np.arange(width) + 1)
        # For Y, skip the first row -> start at transform.f - y_res.
        y = transform.f - y_res * (np.arange(height) + 1)
        X, Y = np.meshgrid(x, y)

        # Convert the raster subset to a PyVista structured grid
        terrain = pv.StructuredGrid(X, Y, array_2d)
        return terrain

def section_mesh(dem_path, fraction=10, col_offset_frac=0, row_offset_frac=0):
    """
    Extract a section of the DEM that is 1/fraction of the full width and height.
    
    Parameters:
        dem_path (str): Path to the DEM file.
        fraction (int): The factor by which to divide the full dimensions.
        col_offset_frac (float): A value between 0 and 1 indicating the horizontal offset.
        row_offset_frac (float): A value between 0 and 1 indicating the vertical offset.
        
    Returns:
        pv.StructuredGrid: The PyVista mesh for the specified DEM section.
    """
    with rasterio.open(dem_path) as data:
        full_width, full_height = data.width, data.height
        
        # Calculate section dimensions (e.g., 1/40th if fraction=40; here you can adjust the fraction)
        section_width = full_width // fraction
        section_height = full_height // fraction

        # Determine the starting offsets (these are in the original DEM coordinate space).
        col_off = int((full_width - section_width) * col_offset_frac)
        row_off = int((full_height - section_height) * row_offset_frac)
        
        # Create the window for the section.
        window = Window(col_off, row_off, section_width, section_height)
    
    # Load the DEM subset as a mesh (removing its first row/col as above)
    terrain_section = load_dem_to_pyvista(dem_path, window=window, decimation=1)
    return terrain_section

def dem_to_mesh(dem_path):
    """
    Convert a DEM file into a PyVista StructuredGrid mesh.
    
    Parameters:
        dem_path (str): Path to the DEM file.
    
    Returns:
        pv.StructuredGrid: A PyVista mesh representing the terrain.
    """
    with rasterio.open(dem_path) as data:
        # Read the elevation values and the affine transform.
        elevation = data.read(1)
        transform = data.transform
        
        # Remove the first row and first column.
        elevation = elevation[1:, 1:]
        
        # Get dimensions of the sliced array.
        height, width = elevation.shape
        
        # Calculate pixel resolution.
        x_res = transform.a
        y_res = -transform.e
        
        # Adjust the starting coordinates to skip the first row/column.
        x_start = transform.c + x_res
        y_start = transform.f - y_res
        
        # Generate X and Y coordinate arrays.
        x = x_start + x_res * np.arange(width)
        y = y_start - y_res * np.arange(height)
        X, Y = np.meshgrid(x, y)
        
    # Create a PyVista StructuredGrid using the coordinate grids and elevation.
    terrain_mesh = pv.StructuredGrid(X, Y, elevation)
    return terrain_mesh

def save_mesh(mesh, save_folder, filename):
    """
    Save a PyVista mesh to the specified folder.
    
    Parameters:
        mesh (pv.DataSet): The PyVista mesh to save.
        save_folder (str): Folder where the mesh should be saved.
        filename (str): The name of the file (include appropriate extension, e.g., .vtk).
    """
    # Ensure the folder exists
    os.makedirs(save_folder, exist_ok=True)
    
    # Construct the full path and save the mesh
    save_path = os.path.join(save_folder, filename)
    mesh.save(save_path)
    print("Mesh saved to", save_path)

def visualize_terrain(dem_path):
    # Define a window to load (e.g., top-left quarter)
    with rasterio.open(dem_path) as data:
        width, height = data.width, data.height
    window = Window(0, 0, width // 20, height // 20)
    
    # Alternatively, choose a decimation factor (or combine both)
    decimation = 1  # Adjust as needed

    terrain = load_dem_to_pyvista(dem_path, window=window, decimation=decimation)

    plotter = pv.Plotter()
    plotter.add_mesh(terrain, cmap="terrain", show_edges=False)
    plotter.set_background("white")
    plotter.show()


def visualize_terrain_in_gui(dem_path):
    """Launches PyVista terrain visualization from PySimpleGUI"""
    sg.theme("DarkBlue")

    layout = [
        [sg.Text("Mars 3D Terrain Viewer", font=("Helvetica", 14))],
        [sg.Button("Render Terrain"), sg.Button("Exit")]
    ]

    window = sg.Window("Terrain Renderer", layout, finalize=True)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break  # Close PySimpleGUI
        elif event == "Render Terrain":
            visualize_terrain(dem_path)  # Open PyVista in a separate window

    window.close()


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(base_dir)
    dem_path = os.path.join(parent_dir, 'data/MarsMGSMOLA_MAP2_EQUI.tif')
    dem_path_zip = os.path.join(parent_dir, 'data/MarsMGSMOLA_MAP2_EQUI.tif.zip')

    # Step 1: Check if ZIP exists before extraction
    if os.path.exists(dem_path_zip):
        try:
            unzip_dem(dem_path_zip, dem_path)
        except Exception as e:
            print(f"Error during extraction: {e}")
            exit(1)
    elif os.path.exists(dem_path):
        print(f"DEM file already extracted: {dem_path}")
    else:
        print(f"Error: No valid DEM file found at {dem_path} or {dem_path_zip}")
        exit(1)

    # Step 2: Display dataset information
    try:
        dataset_info()
    except Exception as e:
        print(f"Error reading DEM data: {e}")
        exit(1)

    # Step 3: Start the PySimpleGUI window with terrain visualization
    visualize_terrain_in_gui(dem_path)

if __name__ == "__main__":
    #main()
    # For direct testing, here’s how to extract, save, and visualize one section:
    dem_file_path = "data/MarsMGSMOLA_MAP2_EQUI.tif"  # update if necessary
    # Extract the top-left section (1/40th of the full DEM)
    mesh_section = section_mesh(dem_file_path, fraction=10, col_offset_frac=0, row_offset_frac=0)
    
    # Specify where to save the mesh
    save_folder = "/Users/leannericard/Downloads/U3/Comp361/Charles-Marwin/data"
    filename = "terrain_mesh_section.vtk"
    save_mesh(mesh_section, save_folder, filename)
    
    # Optionally, visualize the mesh section
    mesh_section.plot(cmap="terrain")
