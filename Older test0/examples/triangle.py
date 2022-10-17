# Source 1: https://www.youtube.com/watch?v=Wyv5TnkFuxE
# Source 3: https://www.youtube.com/watch?v=chaIYg7_7KM

import pyglet


class MyWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pyglet.gl.glClearColor(0.5, 0.1, 0.2, 0.3)

    def on_draw(self):
        self.clear()
        # self.triangle.vertices.draw(GL_TRIANGLES)
        pyglet.gl.glLineWidth(5)
        self.vertices = pyglet.graphics.vertex_list(3, ("v3f", [-0.5, -0.5, 0.0,
                                                                0.5,  -0.5, 0.0,
                                                                 0.0,  0.5, 0.0]),
                                                        ("c3B", [100, 200, 220,
                                                                200, 100, 100,
                                                                100, 250, 100]))

        self.vertices.draw(pyglet.gl.GL_TRIANGLES)
    
    def on_resize(self, width, height):
        pyglet.gl.glViewport(0, 0, width, height)


window = MyWindow(1280, 720, "My Pyglet Window", resizable=True)
# window = pyglet.window.Window(1280, 720, "My Pyglet Window", resizable=True)

@window.event
def on_draw():
    window.clear()
    vertices = pyglet.graphics.vertex_list(3, ("v3f", [-50, -50, 0.0,
                                                                50,  -50, 0.0,
                                                                0.0,  50, 0.0]),
                                                        ("c3B", [100,    0, 0,
                                                                100, 0,  0,
                                                                100, 0,    0]))
    vertices.draw(pyglet.gl.GL_TRIANGLES)
pyglet.app.run()
