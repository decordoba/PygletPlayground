import pyglet


class GameWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.px, self.py = 10, 10
        self.vx, self.vy = 15, 60
        self.ax, self.ay = 0, -5

    def update(self, dt):
        self.px, self.py = self.px + self.vx * dt, self.py + self.vy * dt
        self.vx, self.vy = self.vx + self.ax * dt, self.vy + self.ay * dt

    def on_draw(self):
        # clear screen with semitransparent layer
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        pyglet.gl.glClearColor(0, 0, 0, 0.01)
        self.clear()

        # pyglet.text.Label(text="This is Some Random Text", x=10, y=195).draw()
        # pyglet.text.Label(text="This is Some Random Text", x=10, y=100).draw()
        # pyglet.text.Label(text="This is Some Random Text", x=10, y=5).draw()
        # pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
        #              ('v2f', (0,   0,        # point0
        #                       0,   200,      # point1
        #                       200, 200,      # point2
        #                       200, 0)        # point3
        #              ),
        #              ('c4B', (255, 0, 0, 200, # color for point0
        #                       0, 255, 0, 200, # color for point1
        #                       0, 0, 255, 200, # color for point2
        #                       0, 0,   0, 200) # color for point3
        #              )
        #             ) # end draw()
        
        # calculate and draw polygon
        relative_vertices = [[20, 20], [20, -20], [-20, -20], [-20, 20]]
        vertices = []
        for v in relative_vertices:
            vertices.append(self.px + v[0])
            vertices.append(self.py + v[1])
        colors = [255, 0, 0] * len(relative_vertices)
        pyglet.graphics.vertex_list(len(relative_vertices), ("v2f", vertices), ("c3B", colors)).draw(pyglet.gl.GL_POLYGON)


if __name__ == "__main__":
    config = pyglet.gl.Config(double_buffer=False)
    window = GameWindow(400, 400, config=config)
    pyglet.clock.schedule_interval(window.update, 1/120)
    pyglet.app.run()
