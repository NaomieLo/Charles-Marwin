# batterybar.py
from OpenGL.GL import *
import numpy as np
import ctypes
import glm
import shader  # your existing shader loader

class BatteryBar:
    def __init__(self):
        self.fill = 1.0  # battery life (1.0 = full, 0.0 = empty)

        self.shader = shader.Shader("battery_vert.glsl", "battery_frag.glsl")

        # Rectangle from (0, 0) to (1, 0.1) — top-left corner of screen
        self.vertices = np.array([
            0.0,  0.0,
            1.0,  0.0,
            1.0,  0.1,
            0.0,  0.1
        ], dtype=np.float32)

        self.indices = np.array([
            0, 1, 2,
            2, 3, 0
        ], dtype=np.uint32)

        # Setup VAO and VBO
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.EBO = glGenBuffers(1)

        glBindVertexArray(self.VAO)

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * ctypes.sizeof(ctypes.c_float), ctypes.c_void_p(0))

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def draw(self, screen_width, screen_height):
        glUseProgram(self.shader.pid)

        # Create orthographic projection
        projection = glm.ortho(0, screen_width, 0, screen_height)

        # Transform bar to correct screen position (top-left corner)
        model = glm.translate(glm.mat4(1.0), glm.vec3(20, screen_height - 40, 0))
        model = glm.scale(model, glm.vec3(200 * self.fill, 20, 1))

        # Send uniforms
        glUniformMatrix4fv(glGetUniformLocation(self.shader.pid, "projection"), 1, GL_FALSE, glm.value_ptr(projection))
        glUniformMatrix4fv(glGetUniformLocation(self.shader.pid, "model"), 1, GL_FALSE, glm.value_ptr(model))

        glBindVertexArray(self.VAO)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
