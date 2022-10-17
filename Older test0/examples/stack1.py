import pyglet


class Polygon(object):
    def __init__(self, vertices, color, velocity=0, acceleration=-600):
        self.vertices = vertices
        self.y_idx = 1
        self.num_vertices = int(len(self.vertices) // 2)
        self.colors = color * self.num_vertices
        self.velocity = velocity
        self.acceleration = acceleration
        self.bottom_edge = 0
    
    def draw(self):
        self.vertex_list = pyglet.graphics.vertex_list(self.num_vertices,
                                                       ("v2f", self.vertices),
                                                       ("c3B", self.colors))
        self.vertex_list.draw(pyglet.gl.GL_POLYGON)

    def move_by_offset(self, offset):
        for i in range(1, len(self.vertices), 2):
            self.vertices[i] += offset  # only modify y values

    def bounce(self, dt):
        if self.vertices[self.y_idx] < self.bottom_edge:
            self.velocity = abs(self.velocity)
            return True
        return False

    def update1(self, dt):
        # move
        self.move_by_offset(self.velocity * dt)
        # check if bounce
        self.bounce(dt)
        # accelerate
        self.velocity += self.acceleration * dt

    def update2(self, dt):
        # move
        self.move_by_offset(self.velocity * dt)
        # accelerate
        self.velocity += self.acceleration * dt
        # check if bounce
        self.bounce(dt)

    def update3(self, dt):
        # move
        self.move_by_offset(self.velocity * dt)
        # check if bounce
        bounced = self.bounce(dt)
        if not bounced:
            # accelerate (only if no bounce happened)
            self.velocity += self.acceleration * dt
    
    def update(self, dt):
        # self.update1(dt)
        # self.update2(dt)
        self.update3(dt)


class GameWindow(pyglet.window.Window):
    def __init__(self, objects=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.objects = objects
    
    def update(self, dt):
        for obj in self.objects:
            obj.update(dt)

    def on_draw(self):
        self.clear()
        for obj in self.objects:
            obj.draw()


class Game(object):
    def __init__(self, w=400, h=400, title="My game", resizable=False):
        self.w = w
        self.h = h
        objects = [
            # square
            Polygon(vertices=[w/2-20, h/2, w/2-20, h/2+40, w/2+20, h/2+40, w/2+20, h/2],
                    color=[0, 128, 32],  # green
                    velocity=0,
                    acceleration=-6000),
            # arrow
            Polygon(vertices=[w/2, h/2, w/2+40, h/2+20, w/2+30, h/2, w/2+40, h/2-20],
                    color=[255, 255, 0], # yellow
                    velocity=0,
                    acceleration=0)
        ]
        self.window = GameWindow(objects, self.w, self.h, title, resizable)

    def update(self, dt):
        self.window.update(dt)


if __name__ == "__main__":
    game = Game(resizable=False)
    pyglet.clock.schedule_interval(game.update, 1/120)
    pyglet.app.run()
