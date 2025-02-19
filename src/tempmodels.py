import sys
import shader
import ctypes
import numpy as np
import OpenGL.GL as gl
import pyassimp as ai
from pyglm import glm

null_ptr = ctypes.c_void_p

class Vertex(ctypes.Structure):
    _fields_ = [('position', glm.vec3), ('normal', glm.vec3), ('tex_coords', glm.vec2)]

class Texture(ctypes.Structure):
    _fields_ = [('tid', ctypes.c_int), ('type', ctypes.c_char_p)]

class Mesh():
    def __init__(self, _ver, _ind, _tex):
        self.vertices = _ver                            #[Vertex]
        self.indices = np.array(_ind, dtype=np.uint)    #[unsigned int]
        self.textures = _tex                            #[Texture]
        
        self.setup_mesh()
    
    def setup_mesh(self):
        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)
        self.ebo = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)

        gl.glBufferData(gl.GL_ARRAY_BUFFER, len(self.vertices) * ctypes.sizeof(Vertex), self.vertices, gl.GL_STATIC_DRAW)

        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, gl.GL_STATIC_DRAW)

        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, ctypes.sizeof(Vertex), null_ptr(0))
        gl.glEnableVertexAttribArray(1)
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, False, ctypes.sizeof(Vertex), Vertex.normal.offset)
        gl.glEnableVertexAttribArray(2)
        gl.glVertexAttribPointer(2, 2, gl.GL_FLOAT, False, ctypes.sizeof(Vertex), Vertex.tex_coords.offset)

        gl.glBindVertexArray(0)

    def draw(self, _shader):
        diffuse_nr = 1
        specular_nr = 1
        for _i in range(len(self.textures)):
            gl.glActiveTexture(gl.GL_TEXTURE0 + _i)
            _number = ""
            _name = self.textures[_i].type
            if _name == "texture_diffuse":
                diffuse_nr += 1
                _number = str(diffuse_nr)
            elif _name == "texture_specular":
                specular_nr += 1
                _number = str(specular_nr)
            _shader.setInt("material." + _name + _number, _i)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.textures[_i].tid)
        gl.glActiveTexture(gl.GL_TEXTURE0)

        gl.glBindVertexArray(self.vao)
        gl.glDrawElements(gl.GL_TRIANGLES, self.indices.size, gl.GL_UNSIGNED_INT, 0)
        gl.glBindVertexArray(0)

class Model():
    def __init__(self, _path):
        self.meshes = None
        self.directory = None

        self.load_model(_path)

    def draw(self, _shader):
        for _i in range(len(self.meshes)):
            self.meshes[_i].draw(_shader)

    def load_model(self, _path):
        ai.load(_path)
    
    def process_node(self, aiNode, aiScene):
        pass

    def process_mesh(self, aiMesh, aiScene):
        pass

    def load_material_textures(self, aiMaterial, aiTextureType, typeName):
        pass