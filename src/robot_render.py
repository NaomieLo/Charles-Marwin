import shader
import mesh
import learnOpenGL as terraingen
import ctypes
#import OpenGL.GL as gl
from OpenGL.GL import *
import glfw
import math
import numpy as np
from PIL import Image
from pyglm import glm

null_ptr = ctypes.c_void_p
cam_front = glm.vec3(0.0, 0.0, -1.0)
cam_up = glm.vec3(0.0, 1.0, 0.0)

class UI():
    def __init__(self):
        self.shader = None
        self.shader2 = None
        self.cam_pos = None

        self.delta_time = 0.0
        self.last_frame = 0.0
    
    def process_input(self, window):
        cam_speed = 200.5 * self.delta_time
        if (glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS):
                glfw.set_window_should_close(window,True)
        if (glfw.get_key(window, glfw.KEY_W) == glfw.PRESS):
             self.cam_pos += cam_speed * cam_front
        if (glfw.get_key(window, glfw.KEY_S) == glfw.PRESS):
             self.cam_pos -= cam_speed * cam_front
        if (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS):
             self.cam_pos -= cam_speed * glm.normalize(glm.cross(cam_front, cam_up))
        if (glfw.get_key(window, glfw.KEY_D) == glfw.PRESS):
             self.cam_pos += cam_speed * glm.normalize(glm.cross(cam_front, cam_up))
        if (glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS):
             self.cam_pos += cam_speed * cam_up
        if (glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS):
             self.cam_pos -= cam_speed * cam_up
    
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
        self.shader2 = shader.Shader("vertex_shader_color.glsl", "fragment_shader_color.glsl")

        # Models and views
        self.cam_pos = glm.vec3(0.0, 0.0, 1740.0)

        #robot = mesh.Mesh("models/perseverance/ImageToStl.com_25042_perseverance.obj")
        terrain = terraingen.Terrain("data/terrain_mesh_section.vtk")

        #print(terrain.obj_count)

        rmodel = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, 0.0))
        tmodel = glm.rotate(glm.mat4(1.0), glm.radians(0), glm.vec3(0.0, 1.0, 0.0))
        projection = glm.perspective(glm.radians(45.0), 800 / 600, 0.1, 100.0)

        # ======================= #
        #       RENDER LOOP       #
        # ======================= #
        while not (glfw.window_should_close(window)):
          # Update deltatime
          current_frame = glfw.get_time()
          self.delta_time = current_frame - self.last_frame
          self.last_frame = current_frame

          # Process input
          self.process_input(window)

          #Render stuff here
          self.shader2.use()
            
          glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
          view = glm.lookAt(self.cam_pos, self.cam_pos + cam_front, cam_up)

          glUniformMatrix4fv(glGetUniformLocation(self.shader2.pid, "model"), 1, False, glm.value_ptr(tmodel))
          glUniformMatrix4fv(glGetUniformLocation(self.shader2.pid, "view"), 1, False, glm.value_ptr(view))
          glUniformMatrix4fv(glGetUniformLocation(self.shader2.pid, "projection"), 1, False, glm.value_ptr(projection))

          terrain.draw()

          # self.shader.use() # NOTICE: If only one shader is in use, can place this in setup.
          # self.shader.set_float("someUniform", 1.0)
          # #glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
          # #model = glm.rotate(glm.mat4(1.0), glfw.get_time()*glm.radians(10.0), glm.vec3(0.0, 1.0, 0.0))

          # glUniformMatrix4fv(glGetUniformLocation(self.shader.pid, "model"), 1, False, glm.value_ptr(rmodel))
          # glUniformMatrix4fv(glGetUniformLocation(self.shader.pid, "view"), 1, False, glm.value_ptr(view))
          # glUniformMatrix4fv(glGetUniformLocation(self.shader.pid, "projection"), 1, False, glm.value_ptr(projection))

          # robot.draw()

          # events & buffer swap
          glfw.swap_buffers(window)
          glfw.poll_events()

        glfw.terminate()

ui_instance = UI()
ui_instance.main()