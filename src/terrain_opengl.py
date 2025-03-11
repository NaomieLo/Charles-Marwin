import glfw
import numpy as np
import pyqtgraph.opengl as gl
from PyQt5 import QtCore, QtGui, QtWidgets
import matplotlib.pyplot as plt  
from matplotlib.colors import LinearSegmentedColormap
import pyvista as pv
import sys

class Terrain(object):
    def __init__(self, mesh_file):
        self.app = QtWidgets.QApplication(sys.argv)
        self.w = gl.GLViewWidget()
        self.w.setGeometry(0, 110, 1920, 1080)
        self. w.show()
        self.w.setWindowTitle("Test Terrain")
        self.w.setCameraPosition(distance=100, elevation=90, azimuth=0)

        grid =gl.GLGridItem()
        grid.scale(2,2,2)
        self.w.addItem(grid)

        self.load_mesh(mesh_file)

    # my first method of rendering data
        # self.nstep = 1
        # self.ypoints = range(-20, 22, self.nstep)
        # self.xpoints = range(-20, 22, self.nstep)
        # self.nfaces = len(self.ypoints)

        # verts = np.array([
        #     [x,y,0] for n, x in enumerate(self.xpoints) for n, y in enumerate(self.ypoints)
        #     ], dtype = np.float32)
        
        # faces = []
        # colors = []
        # for n in range(self.nfaces -1):
        #     yoff = n* self.nfaces
        #     for n in range(self.nfaces -1):
        #         faces.appends([n+yoff, yoff + n + self.nfaces, yoff + n + self.nfaces + 1])
        #         faces.append([n+yoff, yoff + n +1, yoff + n + self.nfaces + 1])
        #         colors.append([0,0,0,0])
        #         colors.append([0,0,0,0])
        
        # faces = np.array(faces)
        # colors = np.array(colors)
        # self.m1 = gl.GLMeshItem(
        #     vertexes = verts,
        #     faces = faces, faceColors = colors,
        #     smooth = False, drawEdges = True,
        # )
        # self.m1.setGLOptions('Additive')
        # self.w.addItem(self.m1)
    # def load_mesh(self, mesh_file):
    #     """ Load VTK terrain and apply elevation-based color mapping """
    #     mesh = pv.read(mesh_file)

    #     # If mesh is a StructuredGrid, convert to PolyData
    #     if isinstance(mesh, pv.StructuredGrid):
    #         mesh = mesh.extract_surface()

    #     verts = np.array(mesh.points, dtype=np.float32)
    #     faces = mesh.faces.reshape(-1, 4)[:, 1:]  # Convert faces to proper format

    #     print(f"Vertices shape: {verts.shape}")  # Debugging output
    #     print(f"Faces shape: {faces.shape}")  # Debugging output

    #     # Normalize elevation (Z values)
    #     z_min, z_max = np.min(verts[:, 2]), np.max(verts[:, 2])
    #     if z_max > z_min:
    #         norm_z = (verts[:, 2] - z_min) / (z_max - z_min)  # Normalize
    #     else:
    #         norm_z = np.zeros_like(verts[:, 2])

    #     # Apply colormap (terrain)
    #     colormap = plt.get_cmap("terrain")
    #     vertex_colors = colormap(norm_z)[:, :3]  # Convert to RGB

    #     # Assign colors per face (average vertex colors per face)
    #     face_colors = np.array([colormap(norm_z[face].mean())[:3] for face in faces])
    #     face_colors = np.hstack((face_colors, np.ones((face_colors.shape[0], 1))))  # Add alpha

    #     print(f"Face colors shape: {face_colors.shape}")  # Debugging output

    #     # Create mesh item
    #     if hasattr(self, 'm1'):
    #         self.w.removeItem(self.m1)  # Remove existing mesh before adding a new one
        
    #     self.m1 = gl.GLMeshItem(
    #         vertexes=verts,
    #         faces=faces,
    #         faceColors=face_colors,
    #         smooth=False,
    #         drawEdges=True
    #     )
    #     self.m1.setGLOptions('translucent')  
    #     self.w.addItem(self.m1)

    # Last version that worked
    # def load_mesh(self, mesh_file):
    #     """ Load VTK terrain and apply elevation-based color mapping efficiently """
    #     mesh = pv.read(mesh_file)

    #     # Convert StructuredGrid to PolyData
    #     if isinstance(mesh, pv.StructuredGrid):
    #         mesh = mesh.extract_surface()

    #     # Ensure the mesh is in PolyData format
    #     if not isinstance(mesh, pv.PolyData):
    #         raise ValueError("Mesh conversion failed. Ensure VTK file contains PolyData format.")

    #     # Convert to triangles (Mandatory for GLMeshItem)
    #     mesh = mesh.triangulate()

    #     # Extract full vertex and face data
    #     verts = np.array(mesh.points, dtype=np.float32)
    #     faces = mesh.faces.reshape(-1, 4)[:, 1:]  # Convert faces to proper format

    #     # Debugging: Print dataset size
    #     print(f"Total Vertices: {verts.shape[0]} - Sample: {verts[:5]}")  
    #     print(f"Total Faces: {faces.shape[0]} - Sample: {faces[:5]}")

    #     # Scale and fix elevation
    #     z_min, z_max = np.min(verts[:, 2]), np.max(verts[:, 2])
    #     if z_max == z_min:
    #         print("⚠ Warning: No elevation variation detected! Adjusting manually.")
    #         verts[:, 2] = np.random.uniform(0, 10, verts.shape[0])  # Temporary elevation variation
    #     else:
    #         verts[:, 2] = (verts[:, 2] - z_min) / (z_max - z_min) * 1000  # Scale for contrast

    #     # Center the terrain
    #     verts[:, 0] -= np.mean(verts[:, 0])  
    #     verts[:, 1] -= np.mean(verts[:, 1])  
    #     verts[:, 2] -= np.mean(verts[:, 2])  

    #     # Normalize elevation (Z values)
    #     norm_z = (verts[:, 2] - np.min(verts[:, 2])) / (np.max(verts[:, 2]) - np.min(verts[:, 2]))

    #     # Define custom colormap from light beige to dark red-brown
    #     colors = [(0.95, 0.8, 0.75),  # Light beige
    #             (0.8, 0.5, 0.4),    # Medium red-brown
    #             (0.5, 0.2, 0.15)]   # Dark reddish brown
    #     terrain_cmap = LinearSegmentedColormap.from_list("terrain_custom", colors, N=256)

    #     # Apply color mapping
    #     face_colors = terrain_cmap(norm_z[faces].mean(axis=1))[:, :3]
    #     face_colors = np.hstack((face_colors, np.ones((face_colors.shape[0], 1))))  # Add alpha

    #     print(f"Generated Face Colors: {face_colors.shape}")  # Debugging output

    #     # Create and display terrain mesh
    #     if hasattr(self, 'm1'):
    #         self.w.removeItem(self.m1)  # Remove existing mesh before adding a new one

    #     self.m1 = gl.GLMeshItem(
    #         vertexes=verts,
    #         faces=faces,
    #         faceColors=face_colors,
    #         smooth=False,
    #         drawEdges=True
    #     )
    #     self.m1.setGLOptions('opaque')  # Ensure it renders properly
    #     self.w.addItem(self.m1)

    #     # Adjust camera
    #     self.w.setCameraPosition(distance=20000, elevation=60, azimuth=30)




    # def load_mesh(self, mesh_file):
    #     mesh = pv.read(mesh_file)

    #     if isinstance(mesh, pv.StructuredGrid):
    #         mesh = mesh.extract_surface()

    #     verts = np.array(mesh.points, dtype=np.float32)
    #     faces = mesh.faces.reshape(-1,4)[:, 1:]

    #     if np.max(verts[:, 2]) >0:
    #         verts[:, 2] = verts[:, 2] / np.max(verts[:, 2])*10
            
    #     z_min, z_max = np.min(verts[:, 2]), np.max(verts[:, 2])
    #     if z_max > z_min:  
    #         norm_z = (verts[:, 2] - z_min) / (z_max - z_min)  # Normalize
    #     else:
    #         norm_z = np.zeros_like(verts[:, 2])

    #     # Map normalized elevation values to a colormap
    #     colormap = plt.get_cmap("terrain")  # Use "terrain" colormap (Matplotlib)
    #     vertex_colors = colormap(norm_z)[:, :3]  # Convert to RGB (Nx3)

    #     # Convert per-vertex colors to per-face colors
    #     face_colors = np.array([vertex_colors[face].mean(axis=0) for face in faces])  # Average color per face
    #     # Set solid color for debugging
    #     face_colors = np.ones((faces.shape[0], 4)) * [1, 1, 1, 1]  # White RGBA

    #     # Convert to RGBA (PyQtGraph requires Nx4 format)
    #     face_colors = np.hstack((face_colors, np.ones((face_colors.shape[0], 1))))  # Add alpha channel

    #     self.m1 = gl.GLMeshItem(
    #     vertexes=verts,
    #     faces=faces,
    #     faceColors=face_colors,
    #     smooth=False,
    #     drawEdges=True)
    #     self.m1.setGLOptions('additive')  # Better visibility
    #     self.w.addItem(self.m1)


    def load_mesh(self, mesh_file):
        """ Load VTK terrain and apply elevation-based color mapping efficiently """
        mesh = pv.read(mesh_file)

        # Convert StructuredGrid to PolyData
        if isinstance(mesh, pv.StructuredGrid):
            mesh = mesh.extract_surface()

        # Ensure the mesh is in PolyData format
        if not isinstance(mesh, pv.PolyData):
            raise ValueError("Mesh conversion failed. Ensure VTK file contains PolyData format.")

        # Convert to triangles (Mandatory for GLMeshItem)
        mesh = mesh.triangulate()

        # Extract full vertex and face data
        verts = np.array(mesh.points, dtype=np.float32)
        faces = mesh.faces.reshape(-1, 4)[:, 1:]  # Convert faces to proper format

        # Debugging: Check elevation
        has_variation = self.check_elevation_variation(verts)
        
        if not has_variation:
            print("⚠ WARNING: Elevation is flat! Adding artificial variation for testing.")
            verts[:, 2] += np.random.uniform(0, 10, verts.shape[0]) 

        # Shift elevation so the minimum is at 0
        verts[:, 2] -= np.min(verts[:, 2]) 

        # Normalize elevation
        elevation_scaled = verts[:, 2] / np.max(verts[:, 2])

        # Center terrain around (0,0,0)
        verts[:, 0] -= np.mean(verts[:, 0])  
        verts[:, 1] -= np.mean(verts[:, 1])  
        verts[:, 2] -= np.mean(verts[:, 2])  

        # Define improved colormap (light beige → dark brown)
        terrain_colors = LinearSegmentedColormap.from_list(
            "custom_terrain", ["#F4E0C2", "#C07C5A", "#8B4513"], N=256
        )

        # Apply color mapping
        face_colors = terrain_colors(elevation_scaled[faces].mean(axis=1))[:, :3]
        face_colors = np.hstack((face_colors, np.ones((face_colors.shape[0], 1)))) 

        print(f"Generated Face Colors: {face_colors.shape}")  # Debugging output

        # Create and display terrain mesh
        if hasattr(self, 'm1'):
            self.w.removeItem(self.m1)  
        self.m1 = gl.GLMeshItem(
            vertexes=verts,
            faces=faces,
            faceColors=face_colors,
            smooth=False,
            drawEdges=False  
        )
        self.m1.setGLOptions('opaque')  
        self.w.addItem(self.m1)

        # Adjust camera to ensure terrain is visible
        self.w.setCameraPosition(distance=10000, elevation=20, azimuth=30)



    def check_elevation_variation(self, verts):
        """Checks and prints min/max elevation to confirm variation."""
        z_min, z_max = np.min(verts[:, 2]), np.max(verts[:, 2])
        print(f" Min Elevation: {z_min}, Max Elevation: {z_max}")
        
        if z_max == z_min:
            print("⚠ WARNING: No elevation variation detected! Terrain might be flat.")
            return False
        return True
    
    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtWidgets.QApplication.instance().exec_()
    


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    file = "data//mesh_grid/terrain_mesh_section_0_1.vtk"
    t = Terrain(file)
    t.start()



# def main():
#     if not glfw.init():
#         return 
    
#     window = glfw.create_window(800, 600, "Test Window", None, None)

#     if not window:
#         glfw.terminate()
#         return

#     glfw.make_context_current(window)

#     while not glfw.window_should_close(window):
#         glfw.poll_events()
#         glfw.swap_buffers(window)

#     glfw.terminate()


# if __name__ == "__main__":
#     main()
