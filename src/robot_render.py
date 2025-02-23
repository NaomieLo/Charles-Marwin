import shader
import mesh
import ctypes
#import OpenGL.GL as gl
from OpenGL.GL import *
import glfw
import numpy as np
from PIL import Image
from pyglm import glm

null_ptr = ctypes.c_void_p

class UI():
    def __init__(self):
        self.vao = None
        self.vbo = None
        self.ebo = None
        self.shader = None
    
    def main(self):
        # ======================= #
        #          SETUP          #
        # ======================= #

        # Initialize GLFW
        glfw.init()
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        # Initialize GL Context
        window = glfw.create_window(800, 600, "Charles Marwin", None, None)
        glfw.make_context_current(window)
        glViewport(0,0,800,600)
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 1.0)

        # Compile Shader
        self.shader = shader.Shader("vertex_shader.glsl", "fragment_shader.glsl")

        # Vertex Array initialization
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # Vertex Buffer initialization
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        #glBufferData(GL_ARRAY_BUFFER, ___, ___, GL_STATIC_DRAW)
        #glVertexAttribPointer(_index, _size, _type, _normalized, _stride, _offset)
        #glEnableVertexAttribArray(_index)

        # Element Buffer initialization
        # NOTICE: If object files do not support vertex indexing, the EBO is unnecessary.
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)

        #cube test
        cube = mesh.Mesh("models/perseverance/ImageToStl.com_25042_perseverance.obj")
        model = glm.rotate(glm.mat4(1.0), glm.radians(0.0), glm.vec3(1.0, 1.0, 1.0))
        view = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0))
        projection = glm.perspective(glm.radians(45.0), 800 / 600, 0.1, 100.0)
        #

        # ======================= #
        #       RENDER LOOP       #
        # ======================= #
        while not (glfw.window_should_close(window)):
            # Press ESC to exit
            if (glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS):
                glfw.set_window_should_close(window,True)

            # Render stuff here
            self.shader.use() # NOTICE: If only one shader is in use, can place this in setup.
            self.shader.set_float("someUniform", 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glUniformMatrix4fv(glGetUniformLocation(self.shader.pid, "model"), 1, False, glm.value_ptr(model))
            glUniformMatrix4fv(glGetUniformLocation(self.shader.pid, "view"), 1, False, glm.value_ptr(view))
            glUniformMatrix4fv(glGetUniformLocation(self.shader.pid, "projection"), 1, False, glm.value_ptr(projection))

            cube.draw()

            # events & buffer swap
            glfw.swap_buffers(window)
            glfw.poll_events()

        glfw.terminate()

ui_instance = UI()
ui_instance.main()