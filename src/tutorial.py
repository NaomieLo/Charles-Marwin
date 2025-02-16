import shader
import ctypes
import OpenGL.GL as gl
import glfw
import numpy as np
from PIL import Image
from pyglm import glm

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

        window = glfw.create_window(600, 600, "Tutorial", None, None)
        glfw.make_context_current(window)
        gl.glViewport(0,0,600,600)
        gl.glEnable(gl.GL_DEPTH_TEST)

        # projection matrices
        model = glm.rotate(glm.mat4(1.0), glm.radians(-55.0), glm.vec3(1.0, 0.0, 0.0))
        view = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, -3.0))
        projection = glm.perspective(glm.radians(45.0), 600 / 600, 0.1, 100.0)

        # BUILDING THE SHADER
        # compile shaders
        proj_shader = shader.Shader("vertex_shader.glsl", "fragment_shader.glsl")

        # model data
        vertices = np.array([
                -0.5, -0.5, -0.5,  0.0, 0.0,
                0.5, -0.5, -0.5,  1.0, 0.0,
                0.5,  0.5, -0.5,  1.0, 1.0,
                0.5,  0.5, -0.5,  1.0, 1.0,
                -0.5,  0.5, -0.5,  0.0, 1.0,
                -0.5, -0.5, -0.5,  0.0, 0.0,

                -0.5, -0.5,  0.5,  0.0, 0.0,
                0.5, -0.5,  0.5,  1.0, 0.0,
                0.5,  0.5,  0.5,  1.0, 1.0,
                0.5,  0.5,  0.5,  1.0, 1.0,
                -0.5,  0.5,  0.5,  0.0, 1.0,
                -0.5, -0.5,  0.5,  0.0, 0.0,

                -0.5,  0.5,  0.5,  1.0, 0.0,
                -0.5,  0.5, -0.5,  1.0, 1.0,
                -0.5, -0.5, -0.5,  0.0, 1.0,
                -0.5, -0.5, -0.5,  0.0, 1.0,
                -0.5, -0.5,  0.5,  0.0, 0.0,
                -0.5,  0.5,  0.5,  1.0, 0.0,

                0.5,  0.5,  0.5,  1.0, 0.0,
                0.5,  0.5, -0.5,  1.0, 1.0,
                0.5, -0.5, -0.5,  0.0, 1.0,
                0.5, -0.5, -0.5,  0.0, 1.0,
                0.5, -0.5,  0.5,  0.0, 0.0,
                0.5,  0.5,  0.5,  1.0, 0.0,

                -0.5, -0.5, -0.5,  0.0, 1.0,
                0.5, -0.5, -0.5,  1.0, 1.0,
                0.5, -0.5,  0.5,  1.0, 0.0,
                0.5, -0.5,  0.5,  1.0, 0.0,
                -0.5, -0.5,  0.5,  0.0, 0.0,
                -0.5, -0.5, -0.5,  0.0, 1.0,

                -0.5,  0.5, -0.5,  0.0, 1.0,
                0.5,  0.5, -0.5,  1.0, 1.0,
                0.5,  0.5,  0.5,  1.0, 0.0,
                0.5,  0.5,  0.5,  1.0, 0.0,
                -0.5,  0.5,  0.5,  0.0, 0.0,
                -0.5,  0.5, -0.5,  0.0, 1.0
        ], dtype=np.float32)

        # multicubes
        cube_pos = [
            glm.vec3( 0.0,  0.0,  0.0), 
            glm.vec3( 2.0,  5.0, -15.0), 
            glm.vec3(-1.5, -2.2, -2.5),  
            glm.vec3(-3.8, -2.0, -12.3),  
            glm.vec3( 2.4, -0.4, -3.5),  
            glm.vec3(-1.7,  3.0, -7.5),  
            glm.vec3( 1.3, -2.0, -2.5),  
            glm.vec3( 1.5,  2.0, -2.5), 
            glm.vec3( 1.5,  0.2, -1.5), 
            glm.vec3(-1.3,  1.0, -1.5)  
        ]

        # generate & configure texture
        texture = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture)

        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_MIRRORED_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_MIRRORED_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        img = Image.open("container.jpg")
        img_width = img.width
        img_height = img.height
        img_data = img.tobytes()

        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, img_width, img_height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, img_data)
        gl.glGenerateMipmap

        # vertex buffer & array object
        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)

        vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 5 * 4, null_ptr(0))
        gl.glEnableVertexAttribArray(0)

        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, False, 5 * 4, null_ptr(3 * 4))
        gl.glEnableVertexAttribArray(1)

        # runtime loop
        while not (glfw.window_should_close(window)):
            # input
            if (glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS):
                glfw.set_window_should_close(window,True)

            # rendering
            proj_shader.use()
            proj_shader.set_float("someUniform", 1.0)

            #model = glm.rotate(glm.mat4(1.0), glfw.get_time()*glm.radians(-55.0), glm.vec3(0.5, 1.0, 0.0))
            
            #gl.glUniformMatrix4fv(gl.glGetUniformLocation(proj_shader.pid, "model"), 1, False, glm.value_ptr(model))
            gl.glUniformMatrix4fv(gl.glGetUniformLocation(proj_shader.pid, "view"), 1, False, glm.value_ptr(view))
            gl.glUniformMatrix4fv(gl.glGetUniformLocation(proj_shader.pid, "projection"), 1, False, glm.value_ptr(projection))

            gl.glClearColor(0.2, 0.3, 0.3, 1.0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
            gl.glBindVertexArray(self.vao)
            for _i in range(10):
                temp_model = glm.translate(glm.mat4(1.0), cube_pos[_i])
                model = glm.rotate(temp_model, glfw.get_time()*glm.radians(20.0 * _i), glm.vec3(1.0, 0.3, 0.5))
                gl.glUniformMatrix4fv(gl.glGetUniformLocation(proj_shader.pid, "model"), 1, False, glm.value_ptr(model))
                gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)

            # events & buffer swap
            glfw.swap_buffers(window)
            glfw.poll_events()
        
        glfw.terminate()

ui_instance = UI()
ui_instance.main()