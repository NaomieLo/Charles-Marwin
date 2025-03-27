import glfw
import ctypes
import numpy as np
from OpenGL.GL import *
import pyqtgraph.opengl as gl
from PyQt5 import QtCore, QtGui, QtWidgets
import matplotlib.pyplot as plt  # Used for color mapping
from matplotlib.colors import LinearSegmentedColormap
import pyvista as pv
import sys
import os


class Terrain(object):
    def __init__(self, mesh_file):
        self.app = QtWidgets.QApplication(sys.argv)
        self.load_mesh(mesh_file)


    def load_mesh(self, mesh_file):
        """ Load VTK terrain and apply elevation-based color mapping efficiently """
        abs_path = os.path.join(os.path.dirname(__file__), mesh_file)
        mesh = pv.read(abs_path)

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
        indices = mesh.faces.reshape(-1, 4)[:, 1:]  # Convert faces to proper format
        self.obj_count = len(indices)
        indices = np.ravel(np.array(indices, dtype=np.uint32))
    
        # Debugging: Check elevation
        # has_variation = self.check_elevation_variation(verts)
        
        # if not has_variation:
        #     print("⚠ WARNING: Elevation is flat! Adding artificial variation for testing.")
        #     verts[:, 2] += np.random.uniform(0, 10, verts.shape[0])  # Add small height differences

        # Shift elevation so the minimum is at 0
        verts[:, 2] -= np.min(verts[:, 2])  # Ensures minimum elevation is now 0

        # Normalize elevation values between 0 and 1
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
        colors = terrain_colors(elevation_scaled)[:, :3]
        # print(f"Generated Face Colors: {face_colors.shape}")  # Debugging output

        # format vertices
        vertices = np.ravel(np.concatenate((verts,colors), axis=1, dtype=np.float32))
    
        # Create buffers
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(0))
        # color
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(3 * 4))

        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    def draw(self):
        glBindVertexArray(self.vao)
        # glDrawArrays(GL_TRIANGLES,0,self.test_num)
        glDrawElements(GL_TRIANGLES, self.obj_count, GL_UNSIGNED_INT, ctypes.c_void_p(0))
        glBindVertexArray(0)

    def check_elevation_variation(self, verts):
        """Checks and prints min/max elevation to confirm variation."""
        z_min, z_max = np.min(verts[:, 2]), np.max(verts[:, 2])
        print(f"🟢 Min Elevation: {z_min}, Max Elevation: {z_max}")
        
        if z_max == z_min:
            print("⚠ WARNING: No elevation variation detected! Terrain might be flat.")
            return False
        return True
    
    # def start(self):
    #     if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #         QtWidgets.QApplication.instance().exec_()
    


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    file = "data/terrain_mesh_section.vtk"
    t = Terrain(file)



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
