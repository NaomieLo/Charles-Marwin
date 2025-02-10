import PySimpleGUI as sg
import OpenGL.GL as gl
import tkinter as tk
from pyopengltk import OpenGLFrame

# OpenGL rendering class
class OpenGLCanvas(OpenGLFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def initgl(self):
        """ Initialize OpenGL settings. """
        gl.glEnable(gl.GL_DEPTH_TEST)

    def redraw(self):
        """ Render a simple triangle """
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()

        gl.glBegin(gl.GL_TRIANGLES)
        gl.glColor3f(1, 0, 0)
        gl.glVertex3f(-0.5, -0.5, 0)
        gl.glColor3f(0, 1, 0)
        gl.glVertex3f(0.5, -0.5, 0)
        gl.glColor3f(0, 0, 1)
        gl.glVertex3f(0, 0.5, 0)
        gl.glEnd()

        self.tkSwapBuffers()


# PySimpleGUI layout
layout = [
    [sg.Text("Work in Progress")],
    [sg.Canvas(key="-CANVAS-",size=(400,400),expand_x=True,expand_y=True)],
    [sg.Button("Exit")]
]

# Create PySimpleGUI window
window = sg.Window("OpenGL in PySimpleGUI", layout, finalize=True,size=(600,600))

# Get the Tkinter Canvas element from PySimpleGUI
canvas_elem = window["-CANVAS-"].Widget

# Create and attach OpenGL Canvas to the Tkinter Canvas
opengl_canvas = OpenGLCanvas(canvas_elem)
opengl_canvas.pack(fill=tk.BOTH, expand=tk.YES)

# Enable continuous rendering
opengl_canvas.animate = 1  
opengl_canvas.after(10, opengl_canvas.update)

# Main event loop
while True:
    event, values = window.read(timeout=10)
    if event in (sg.WINDOW_CLOSED, "Exit"):
        break

window.close()
