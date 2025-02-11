import sys
import shader
import ctypes
import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut
import glfw
import numpy as np
import tkinter as tk
from pyopengltk import OpenGLFrame


class UI():
    def __init__(self):
        self.vao = None

    def main(self):
        null_ptr = ctypes.c_void_p

        # initialize window & context
        glfw.init()
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        window = glfw.create_window(600, 600, "Charles Marwin", None, None)
        glfw.make_context_current(window)
        gl.glViewport(0,0,600,600)

        # BUILDING THE SHADER
        # compile shaders
        proj_shader = shader.Shader("vertex_shader.glsl", "fragment_shader.glsl")

        # triangle data
        vertices = np.array([
            -0.5, -0.5, 0.0,  1.0, 0.0, 0.0,
            0.5, -0.5, 0.0,   0.0, 1.0, 0.0,
            0.0, 0.5, 0.0,    0.0, 0.0, 1.0
        ], dtype=np.float32)

        # vertex buffer & array object
        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)

        vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 6 * 4, null_ptr(0))
        gl.glEnableVertexAttribArray(0)

        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, False, 6 * 4, null_ptr(3 * 4))
        gl.glEnableVertexAttribArray(1)

        # runtime loop
        while not (glfw.window_should_close(window)):
            # input
            if (glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS):
                glfw.set_window_should_close(window,True)

            # rendering
            proj_shader.use()
            proj_shader.set_float("someUniform", 1.0)

            gl.glClearColor(0.2, 0.3, 0.3, 1.0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            gl.glBindVertexArray(self.vao)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)

            # events & buffer swap
            glfw.swap_buffers(window)
            glfw.poll_events()
        
        glfw.terminate()

ui_instance = UI()
ui_instance.main()