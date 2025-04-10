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
from batterybar import BatteryBar

null_ptr = ctypes.c_void_p

class UI():
    def __init__(self):
        self.shader = None; self.shader2 = None; self.cam_pos = None; self.robot_pos = None; self.robot_ang = None

        self.delta_time = 0.0; self.last_frame = 0.0; self.robot_speed = 0; self.robot_mesh = None

        self.cam_front = glm.vec3(0.0, 0.0, -1.0); self.cam_up = glm.vec3(0.0, 1.0, 0.0)

        self.robot_forward = glm.vec3(0.0, 0.0, -1.0)

        self.yaw = -90.0; self.pitch = 0.0; self.lastX = 400.0; self.lastY = 300.0; self.first_mouse = True

        self.battery = 1.0  # Initialize battery value
        self.battery_bar = None  # Placeholder, will be set in main()

    def set_mesh(self, path):
        self.robot_mesh = path

    def set_pos(self, a, b, c):
        x = a*self.terrain.x_ratio; y = b; z = c*self.terrain.z_ratio
        self.robot_pos.x = x; self.cam_pos.x = x
        self.robot_pos.y = y; self.cam_pos.y = y + 2
        self.robot_pos.z = z; self.cam_pos.z = z + 6

    def move_forward(self):
        self.robot_pos += self.robot_speed * self.robot_forward
        self.cam_pos += self.robot_speed * self.robot_forward

    def move_backward(self):
        self.robot_pos -= self.robot_speed * self.robot_forward
        self.cam_pos -= self.robot_speed * self.robot_forward

    def turn_clockwise(self):
        self.robot_ang -= self.robot_speed * 30.0
    
    def turn_counterclockwise(self):
        self.robot_ang += self.robot_speed * 30.0
    
    def process_input(self, window):
        self.robot_speed = 2.5 * self.delta_time
        if (glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS):
            glfw.set_window_should_close(self.window,True)
        if (glfw.get_key(window, glfw.KEY_W) == glfw.PRESS):
             self.move_forward()
        if (glfw.get_key(window, glfw.KEY_S) == glfw.PRESS):
             self.move_backward()
        if (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS):
             self.turn_counterclockwise()
        if (glfw.get_key(window, glfw.KEY_D) == glfw.PRESS):
             self.turn_clockwise()
        
        direction = glm.vec3(0.0)
        direction.x = math.sin(glm.radians(self.robot_ang))
        direction.z = math.cos(glm.radians(self.robot_ang))
        self.robot_forward = glm.normalize(direction)

    def mouse_callback(self, window, xpos, ypos):
        if self.first_mouse:
            self.lastX = xpos; self.lastY = ypos; self.first_mouse = False

        xoffset = xpos - self.lastX
        yoffset = self.lastY - ypos
        self.lastX = xpos
        self.lastY = ypos

        sensitivity = 0.1
        xoffset *= sensitivity
        yoffset *= sensitivity

        self.yaw += xoffset
        self.pitch += yoffset

        if (self.pitch > 89.0): self.pitch = 89.0
        if (self.pitch < -89.0): self.pitch = -89.0

        direction = glm.vec3(0.0)
        direction.x = math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        direction.y = math.sin(glm.radians(self.pitch))
        direction.z = math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        self.cam_front = glm.normalize(direction)

    
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
        self.window = glfw.create_window(1000, 800, "Charles Marwin", None, None)
        glfw.make_context_current(self.window)
        glViewport(0,0,800,600)
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        #glfw.set_cursor_pos_callback(window,self.mouse_callback)

        # Compile Shader
        self.shader = shader.Shader("src/vertex_shader.glsl", "src/fragment_shader.glsl")
        self.shader2 = shader.Shader("src/vertex_shader_color.glsl", "src/fragment_shader_color.glsl")

        # Models and views
        self.cam_pos = glm.vec3(0.0, 2.0, 6.0)
        self.robot_pos = glm.vec3(0.0, 0.0, 0.0)
        self.robot_ang = 180.0

        self.robot = mesh.Mesh(self.robot_mesh)
        self.terrain = terraingen.Terrain("src/data/terrain_mesh_section.vtk")

        self.battery_bar = BatteryBar()

        #print(terrain.obj_count)

        self.tmodel = glm.rotate(glm.mat4(1.0), glm.radians(-90), glm.vec3(1.0, 0.0, 0.0))
        self.tmodel = glm.translate(self.tmodel, glm.vec3(0.0, -0.666376*self.terrain.y_offset, 50.0))
        self.tmodel = glm.scale(self.tmodel, glm.vec3(1.0, 1.0, 1.0))
        self.projection = glm.perspective(glm.radians(45.0), 800 / 600, 0.1, 2000000.0)
        
    def terminate(self):
        glfw.terminate()

    def update_frame(self):
        # Update deltatime
        current_frame = glfw.get_time()
        self.delta_time = current_frame - self.last_frame
        self.last_frame = current_frame

        # Process input
        self.process_input(self.window)

        #Render stuff here
        self.shader2.use()
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        view = glm.lookAt(self.cam_pos, self.robot_pos, self.cam_up)
        #view = glm.rotate(view_pos, glm.radians(45), glm.vec3(1.0, 0.0, 0.0))

        glUniformMatrix4fv(glGetUniformLocation(self.shader2.pid, "model"), 1, False, glm.value_ptr(self.tmodel))
        glUniformMatrix4fv(glGetUniformLocation(self.shader2.pid, "view"), 1, False, glm.value_ptr(view))
        glUniformMatrix4fv(glGetUniformLocation(self.shader2.pid, "projection"), 1, False, glm.value_ptr(self.projection))

        self.terrain.draw()

        self.shader.use() # NOTICE: If only one shader is in use, can place this in setup.

        rmodel = glm.rotate(glm.translate(glm.mat4(1), self.robot_pos), glm.radians(self.robot_ang), glm.vec3(0.0, 1.0, 0.0))
        rmodel = glm.scale(rmodel, glm.vec3(0.3, 0.3, 0.3))

        glUniformMatrix4fv(glGetUniformLocation(self.shader.pid, "model"), 1, False, glm.value_ptr(rmodel))
        glUniformMatrix4fv(glGetUniformLocation(self.shader.pid, "view"), 1, False, glm.value_ptr(view))
        glUniformMatrix4fv(glGetUniformLocation(self.shader.pid, "projection"), 1, False, glm.value_ptr(self.projection))

        self.robot.draw()

        #print(str(self.robot_pos.x)+", "+str(self.robot_pos.y)+", "+str(self.robot_pos.z))

        # Update and draw battery bar
        self.battery -= self.delta_time * 0.002
        self.battery = max(0.0, self.battery)
        self.battery_bar.fill = self.battery
        
        glDisable(GL_DEPTH_TEST)
        self.battery_bar.draw(800, 600)
        glEnable(GL_DEPTH_TEST)

        # events & buffer swap
        glfw.swap_buffers(self.window)
        glfw.poll_events()


if __name__ == "__main__":
    ui_instance = UI()
    ui_instance.set_mesh("src/models/perseverance/ImageToStl.com_25042_perseverance.obj")
    ui_instance.main()