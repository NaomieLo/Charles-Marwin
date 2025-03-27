import sys
import os
import numpy as np
import pyvista as pv
import pyqtgraph.opengl as gl
from PyQt5 import QtWidgets, QtCore, QtGui
from matplotlib.colors import LinearSegmentedColormap


class TerrainViewer:
    def __init__(self, mesh_file, highlight_regions=None):
        self.highlight_regions = highlight_regions or []

        self.app = QtWidgets.QApplication(sys.argv)
        self.w = gl.GLViewWidget()
        self.w.setWindowTitle("Terrain Test Viewer")
        self.w.setGeometry(0, 110, 1000, 800)
        self.w.show()

        self.load_mesh(mesh_file)
    
    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_W:
            self.opts['center'].setZ(self.opts['center'].z() - 100)
        elif key == QtCore.Qt.Key_S:
            self.opts['center'].setZ(self.opts['center'].z() + 100)
        elif key == QtCore.Qt.Key_A:
            self.opts['center'].setX(self.opts['center'].x() - 100)
        elif key == QtCore.Qt.Key_D:
            self.opts['center'].setX(self.opts['center'].x() + 100)
        elif key == QtCore.Qt.Key_Q:
            self.opts['center'].setY(self.opts['center'].y() + 100)
        elif key == QtCore.Qt.Key_E:
            self.opts['center'].setY(self.opts['center'].y() - 100)
        self.update()
    

    def load_mesh(self, mesh_file):
        abs_path = os.path.join(os.path.dirname(__file__), mesh_file)
        mesh = pv.read(abs_path)

        if isinstance(mesh, pv.StructuredGrid):
            mesh = mesh.extract_surface()
        if not isinstance(mesh, pv.PolyData):
            raise ValueError("Mesh must be PolyData.")

        mesh = mesh.triangulate()
        verts = np.array(mesh.points, dtype=np.float32)
        faces = mesh.faces.reshape(-1, 4)[:, 1:]

        # Elevation coloring
        verts[:, 2] -= np.min(verts[:, 2])
        elevation_scaled = verts[:, 2] / np.max(verts[:, 2])

        colormap = LinearSegmentedColormap.from_list(
            "custom_terrain", ["#F4E0C2", "#C07C5A", "#8B4513"], N=256
        )
        base_colors = colormap(elevation_scaled)[:, :3]
        override_color = np.array([0.4, 0.8, 1.0])

        # Highlight override
        for i, (x, y, z) in enumerate(verts):
            for min_x, min_y, max_x, max_y in self.highlight_regions:
                if min_x <= x <= max_x and min_y <= y <= max_y:
                    base_colors[i] = override_color
                    break

        # Center terrain
        verts -= np.mean(verts, axis=0)

        # Create and show mesh
        self.m1 = gl.GLMeshItem(
            vertexes=verts,
            faces=faces,
            vertexColors=base_colors,
            smooth=False,
            drawEdges=False
        )
        self.m1.setGLOptions('opaque')
        self.w.addItem(self.m1)

        # self.w.setCameraPosition(distance=10000, elevation=20, azimuth=30)
        min_x= highlight_regions[0][0]
        min_y= highlight_regions[0][1]
        max_x= highlight_regions[0][2] 
        max_y= highlight_regions[0][3]

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        center_z = 0  # We'll use the terrain midpoint or elevation mean

        self.w.setCameraPosition(
            pos=QtGui.QVector3D(center_x, center_y, center_z),
            distance=10000,
            elevation=30,
            azimuth=45
        )

        # Print bounds for reference
        bounds = mesh.bounds
        print(f"Terrain bounds:\nX: {bounds[0]:.2f} → {bounds[1]:.2f}\n"
              f"Y: {bounds[2]:.2f} → {bounds[3]:.2f}\n"
              f"Z: {bounds[4]:.2f} → {bounds[5]:.2f}")

    def start(self):
        QtWidgets.QApplication.instance().exec_()


if __name__ == "__main__":
    # Example highlight region
    highlight_regions = [
        (1000000, 5000000, 1100000, 5100000)
    ]

    # terrain_path = "../data/mesh_grid/terrain_mesh_section_3_5_to_5_6.vtk"
    terrain_path = "../data/mesh_grid/terrain_mesh_section.vtk"
    viewer = TerrainViewer(terrain_path, highlight_regions)
    viewer.start()
