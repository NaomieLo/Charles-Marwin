import sys
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
        self.shader_program = None
        self.vao = None

    # Function to load shader source
    def load_shader_source(self, file_path):
        with open(file_path, 'r') as file:
            return file.read()
        
    # Function to compile a shader
    def compile_shader(self, shader_type, source):
        shader = gl.glCreateShader(shader_type)
        gl.glShaderSource(shader, source)
        gl.glCompileShader(shader)

        # Check for errors
        if not gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS):
            error = gl.glGetShaderInfoLog(shader)
            raise RuntimeError(f"Shader compilation failed: {error.decode()}")

        return shader

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
        vertex_shader = self.compile_shader(gl.GL_VERTEX_SHADER, self.load_shader_source("vertex_shader.glsl"))
        fragment_shader = self.compile_shader(gl.GL_FRAGMENT_SHADER, self.load_shader_source("fragment_shader.glsl"))
        # shader program
        self.shader_program = gl.glCreateProgram()
        gl.glAttachShader(self.shader_program, vertex_shader)
        gl.glAttachShader(self.shader_program, fragment_shader)
        gl.glLinkProgram(self.shader_program)
        # cleanup
        gl.glDeleteShader(vertex_shader)
        gl.glDeleteShader(fragment_shader)

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
            gl.glClearColor(0.2, 0.3, 0.3, 1.0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            gl.glUseProgram(self.shader_program)
            gl.glBindVertexArray(self.vao)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)

            # events & buffer swap
            glfw.swap_buffers(window)
            glfw.poll_events()
        
        glfw.terminate()

ui_instance = UI()
ui_instance.main()