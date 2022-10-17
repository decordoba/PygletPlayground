# Source 1: https://www.youtube.com/watch?v=Wyv5TnkFuxE
# Source 3: https://www.youtube.com/watch?v=chaIYg7_7KM

import pyglet
from pyglet.gl import *
import OpenGL  # pip install PyOpenGL
import ctypes


class Triangle(object):
    def __init__(self):
        self.vertices = pyglet.graphics.vertex_list(3, ("v3f", [-0.5, -0.5, 0.0,
                                                                0.5,  -0.5, 0.0,
                                                                 0.0,  0.5, 0.0]),
                                                        ("c3B", [100, 200, 220,
                                                                200, 100, 100,
                                                                100, 250, 100]))


# class Triangle2(object):
#     def __init__(self):
#         self.triangle = [-0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
#                           0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
#                           0.0,  0.5, 0.0, 0.0, 0.0, 1.0]
    
#         self.vertex_shader_source = """
#         #version 330
#         in layout(location = 0) vec3 position;
#         in layout(location = 1) vec3 color;

#         out vec3 newColor;
#         void main()
#         {
#             gl_Position = vec4(position, 1.0f);
#             newColor = color;
#         }
#         """

#         self.fragment_shader_source = """
#         #version 330
#         in vec3 newColor;

#         out vec4 outColor;
#         void main()
#         {
#             outColor = vec4(newColor, 1.0f);
#         }
#         """

#         shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShaders(self.vertex_shader_source, GL_VERTEX_SHADER),
#                                                   OpenGL.GL.shaders.compileShaders(self.fragment_shader_source, GL_FRAGMENT_SHADER))
        
        
#         glUseProgram(shader)

#         vbo = GLuint(0)  # vertex buffer object
#         glGenBuffers(1, vbo)

#         glBindBuffer(GL_ARRAY_BUFFER, vbo)
#         glBufferData(GL_ARRAY_BUFFER, 72, (GLFloat * len(self.triangle))(*self.triangle), GL_STATIC_DRAW)

#         # positions
#         glVertesAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
#         glEnableVertexAttribArray(0)

#         # colors
#         glVertesAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
#         glEnableVertexAttribArray(1)


# class Triangle3(object):
#     def __init__(self):
#         self.triangle = [-0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
#                           0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
#                           0.0,  0.5, 0.0, 0.0, 0.0, 1.0]
    
#         self.vertex_shader_source = """
#         #version 330
#         in layout(location = 0) vec3 position;
#         in layout(location = 1) vec3 color;

#         out vec3 newColor;
#         void main()
#         {
#             gl_Position = vec4(position, 1.0f);
#             newColor = color;
#         }
#         """

#         self.fragment_shader_source = """
#         #version 330
#         in vec3 newColor;

#         out vec4 outColor;
#         void main()
#         {
#             outColor = vec4(newColor, 1.0f);
#         }
#         """

#         shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShaders(self.vertex_shader_source, GL_VERTEX_SHADER),
#                                                   OpenGL.GL.shaders.compileShaders(self.fragment_shader_source, GL_FRAGMENT_SHADER))
        
        
#         glUseProgram(shader)

#         vbo = GLuint(0)  # vertex buffer object
#         glGenBuffers(1, vbo)

#         glBindBuffer(GL_ARRAY_BUFFER, vbo)
#         glBufferData(GL_ARRAY_BUFFER, 72, (GLFloat * len(self.triangle))(*self.triangle), GL_STATIC_DRAW)

#         # positions
#         glVertesAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
#         glEnableVertexAttribArray(0)

#         # colors
#         glVertesAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
#         glEnableVertexAttribArray(1)


class Quad(object):
    def __init__(self):
        self.vertices = pyglet.graphics.vertex_list_indexed(4, [0, 1, 2,
                                                                2, 3, 0],
                                                               ("v3f", [-0.5, -0.5, 0.0,
                                                                         0.5, -0.5, 0.0,
                                                                         0.5,  0.5, 0.0,
                                                                        -0.5,  0.5, 0.0]),
                                                               ("c3f", [1, 0, 0,
                                                                        0, 1, 0,
                                                                        0, 0, 1,
                                                                        1, 1, 1]))

class Quad2(object):
    def __init__(self):
        self.index = [0, 1, 2, 2, 3, 0]
        self.vertex = [-0.5, -0.5, 0.0, 0.5, -0.5, 0.0, 0.5, 0.5, 0.0, -0.5, 0.5, 0.0]
        self.color = [1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1]
        self.vertices = pyglet.graphics.vertex_list_indexed(len(self.vertex) // 3, self.index, ("v3f", self.vertex), ("c3f", self.color))


class Quad3(object):
    def __init__(self):
        self.index = [0, 1, 2, 2, 3, 0]
        self.vertex = [-0.5, -0.5, 0.0, 0.5, -0.5, 0.0, 0.5, 0.5, 0.0, -0.5, 0.5, 0.0]
        self.color = [1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1]
    
    def render(self):
        self.vertices = pyglet.graphics.draw_indexed(4, GL_TRIANGLES, self.index, ("v3f", self.vertex), ("c3f", self.color))


class MyWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(400, 300)
        glClearColor(0.5, 0.1, 0.2, 0.3)

        self.triangle = Triangle()
        # self.triangle2 = Triangle2()
        # self.triangle3 = Triangle3()
        self.quad = Quad()
        self.quad2 = Quad2()
        self.quad3 = Quad3()
    
    def on_draw(self):
        self.clear()
        # self.triangle.vertices.draw(GL_TRIANGLES)
        pyglet.gl.glLineWidth(5)
        self.quad.vertices.draw(GL_TRIANGLES)
        # self.quad2.vertices.draw(GL_TRIANGLES)
        # self.quad3.render()
        # glDrawArrays(GL_TRIANGLES, 0, 3)  # triangle2
    
    def on_resize(self, width, height):
        glViewport(0, 0, width, height)


if __name__ == "__main__":
    window = MyWindow(1280, 720, "My Pyglet Window", resizable=True)
    window.on_draw()
    pyglet.app.run()
