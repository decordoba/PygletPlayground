import pyglet


class MyWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pyglet.gl.glClearColor(0.5, 0.1, 0.2, 0.3)

    def on_draw(self):
        self.clear()
        pyglet.gl.glLineWidth(5)
        self.vertices = pyglet.graphics.vertex_list(3,
                                                   ("v2f", [100, 100, 300, 100, 200, 200]),
                                                   ("c3B", [100, 200, 220, 200, 100, 100, 100, 250, 100]))
        self.vertices.draw(pyglet.gl.GL_TRIANGLES)

    # def on_resize(self, width, height):
    #     pyglet.gl.glViewport(0, 0, width, height)


window = MyWindow(400, 400, "My Window", resizable=True)
pyglet.app.run()
