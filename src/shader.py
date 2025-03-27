import OpenGL.GL as gl
import os

class Shader():
    def __init__(self, vertex_path, fragment_path):
        self.vertex = self.compile_shader(gl.GL_VERTEX_SHADER, self.load_shader_source(vertex_path))
        self.fragment = self.compile_shader(gl.GL_FRAGMENT_SHADER, self.load_shader_source(fragment_path))

        self.pid = gl.glCreateProgram()
        gl.glAttachShader(self.pid, self.vertex)
        gl.glAttachShader(self.pid, self.fragment)
        gl.glLinkProgram(self.pid)

        gl.glDeleteShader(self.vertex)
        gl.glDeleteShader(self.fragment)
    
    def use(self):
        gl.glUseProgram(self.pid)

    def set_bool(self, name, value):
        gl.glUniform1i(gl.glGetUniformLocation(self.pid, name), int(value))
    
    def set_int(self, name, value):
        gl.glUniform1i(gl.glGetUniformLocation(self.pid, name), value)
    
    def set_float(self, name, value):
        gl.glUniform1f(gl.glGetUniformLocation(self.pid, name), value)
    
    # Function to load shader source
    def load_shader_source(self, file_path):
        abs_path = os.path.join(os.path.dirname(__file__), file_path)
        with open(abs_path, 'r') as file:
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