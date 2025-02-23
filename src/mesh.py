import ctypes
import numpy as np
from PIL import Image
from OpenGL.GL import *

class Material:
    def __init__(self, filename):
        self.mats = self.loadMaterials(filename); #print(self.mats)

    def loadMaterials(self, filename):
        mats = {}
        flag = ""

        with open(filename, 'r') as f:
            line = f.readline().rstrip('\n')
            while line:
                words = line.split(" ")
                if words[0] == "newmtl":
                    flag = words[1]
                elif words[0] == "map_Kd":
                    mats.update({flag:words[1]})
                    flag = ""
                line = f.readline()
        
        return mats

    def size(self):
        return len(self.mats)

class Mesh:
    def __init__(self, filename):
        # x, y, z, s, t, nx, ny, nz
        self.materials = None
        self.obj_data = []
        vertices = self.loadMesh(filename); #print(vertices)
        vertices = np.ravel(np.array(vertices, dtype=np.float32))

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        matkeys = self.materials.mats.keys()

        # bind materials to texture buffer
        self.textures = []
        self.tindex = {}
        x = 0
        for i in matkeys:
            self.textures.append(glGenTextures(1))
            self.tindex[i] = x
            temptex = self.textures[x]
            glBindTexture(GL_TEXTURE_2D, temptex)

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

            if self.materials.mats[i] != None:
                img = Image.open(self.materials.mats[i])
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img.tobytes())
                glGenerateMipmap(GL_TEXTURE_2D)
                img.close()
            x += 1

        # vertices
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        # position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(0))
        # texture
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(3 * 4))
    
    def draw(self):
        glBindVertexArray(self.vao)
        offset = 0
        for obj in self.obj_data:
            glBindTexture(GL_TEXTURE_2D, self.textures[self.tindex[obj[0]]])
            glDrawArrays(GL_TRIANGLES, offset, obj[1])
            offset += obj[1]


    def loadMesh(self, filename):
        #raw, unassembled data
        v = []
        vt = []

        #intermediate, assembled object
        temp_vertices = []
        mat = None
        
        #final, complete object
        vertices = []

        #open the obj file and read the data
        with open(filename,'r') as f:
            line = f.readline().rstrip('\n')
            while line:
                words = line.split(" ")
                if words[0] == "o":
                    #new object
                    if len(temp_vertices) > 0: 
                        vertices.append(temp_vertices)
                        self.obj_data.append([mat,len(temp_vertices)//5])
                    temp_vertices = []
                    mat = None
                elif words[0] == "mtllib":
                    #set material library
                    self.materials = Material(words[1])
                elif words[0] == "v":
                    #vertex
                    v.append(self.read_vertex_data(words))
                elif words[0] == "vt":
                    #texture coord
                    vt.append(self.read_texcoord_data(words))
                elif words[0] == "f":
                    #face, three or more vertices in v/vt/vn form
                    self.read_face_data(words, v, vt, temp_vertices)
                elif words[0] == "usemtl":
                    #material binding to current obj
                    mat = words[1]
                line = f.readline().rstrip('\n')
        vertices.append(temp_vertices)
        self.obj_data.append([mat,len(temp_vertices)//5])
        return vertices
    
    def read_vertex_data(self, words):
        return[
            float(words[1]),
            float(words[2]),
            float(words[3])
        ]
    
    def read_texcoord_data(self, words):
        return[
            float(words[1]),
            float(words[2])
        ]
    
    def read_face_data(self, words, v, vt, container):
        triangle_count = len(words) - 3
        for i in range(triangle_count):
            self.make_corner(words[1], v, vt, container)
            self.make_corner(words[2 + i], v, vt, container)
            self.make_corner(words[3 + i], v, vt, container)

    def make_corner(self, corner_description, v, vt, container):
        v_vt_vn = corner_description.split("/")
        for element in v[int(v_vt_vn[0]) - 1]:
            container.append(element)
        for element in vt[int(v_vt_vn[1]) - 1]:
            container.append(element)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))