import pyglet


batch2 = pyglet.graphics.Batch()


class RectangleContour(pyglet.shapes.Rectangle):
    def __init__(self, x, y, width, height, border=1, color=(255, 255, 255), border_color=(0, 0, 0), batch=None, group=None):
        self.lines = []  # _update_position uses self.lines and is called in super.__init__, so initialize it to empty
        super().__init__(x, y, width, height, color=color, batch=batch, group=group)
        self._border = border
        self._brgb = border_color
        self._border_opacity = 255
        self._border_visible = True
        self.lines = [
            pyglet.shapes.Line(0, 0, 0, 0, width=self._border, color=self._brgb, batch=self._batch, group=self._group),
            pyglet.shapes.Line(0, 0, 0, 0, width=self._border, color=self._brgb, batch=self._batch, group=self._group),
            pyglet.shapes.Line(0, 0, 0, 0, width=self._border, color=self._brgb, batch=self._batch, group=self._group),
            pyglet.shapes.Line(0, 0, 0, 0, width=self._border, color=self._brgb, batch=self._batch, group=self._group)
        ]

    def _update_position(self):
        super()._update_position()
        vertices = self._vertex_list.vertices[:][0:6] + self._vertex_list.vertices[:][10:12] + self._vertex_list.vertices[:][0:2]
        for i, line in enumerate(self.lines):
            line._visible = self._border_visible
            line.x = vertices[2 * i]
            line.y = vertices[2 * i + 1]
            line.x2 = vertices[2 * i + 2]
            line.y2 = vertices[2 * i + 3]
            # correct for line width
            leg_x, leg_y = line.x - line.x2, line.y - line.y2
            hypotenuse = (leg_x ** 2 + leg_y ** 2) ** 0.5
            line.x += self._border / 2 * leg_x / hypotenuse
            line.x2 -= self._border / 2 * leg_x / hypotenuse
            line.y += self._border / 2 * leg_y / hypotenuse
            line.y2 -= self._border / 2 * leg_y / hypotenuse
            line._update_position()

    def _update_color(self):
        for line in self.lines:
            line._rgb = self._brgb
            line._opacity = self._border_opacity
            line._update_color()
        return super()._update_color()

    @property
    def border_color(self):
        return self._brgb

    @border_color.setter
    def border_color(self, values):
        self._brgb = list(map(int, values))
        self._update_color()

    @property
    def border_color(self):
        return self._brgb

    @border_color.setter
    def border_color(self, values):
        self._brgb = list(map(int, values))
        self._update_color()

    @property
    def border_opacity(self):
        return self._opacity

    @border_opacity.setter
    def border_opacity(self, value):
        self._border_opacity = value
        self._update_color()

    @property
    def border_visible(self):
        return self._border_visible

    @border_visible.setter
    def border_visible(self, value):
        self._border_visible = value
        self._update_position()


batch1 = pyglet.graphics.Batch()
batch3 = pyglet.graphics.Batch()
window = pyglet.window.Window(1000, 1000, caption="Test1")


side = 400
center = (window.width / 2, window.height / 2)
offset = (side / 2 + 50, side / 2 + 10)
dot_radius = 2

# Rectangle with center as anchor
s1 = pyglet.shapes.Rectangle(center[0], center[1], side, side, color=(55, 55, 255), batch=batch1)  # blue
s2 = pyglet.shapes.Rectangle(center[0], center[1], side, side, color=(255, 55, 55), batch=batch1)  # red
s3 = pyglet.shapes.Rectangle(center[0], center[1], side, side, color=(55, 255, 55), batch=batch1)  # green
# s4 = pyglet.shapes.Rectangle(center[0], center[1], side, side, color=(255, 55, 255), batch=batch2)  # pink
s4 = RectangleContour(center[0], center[1], side, side, border=3, color=(255, 55, 255), border_color=(255, 255, 255), batch=batch2)  # pink with border
s1.opacity = 100
s2.opacity = 100
s3.opacity = 100
s4.opacity = 100
dot = pyglet.shapes.Circle(center[0], center[1], radius=dot_radius, color=(255, 0, 0), batch=batch1)

# changing anchor centers anchor in (x, y) coordinates (therefore, it moves the shape)
s1.anchor_position = (offset[0], offset[1])
s2.anchor_position = (offset[0], offset[1])
s3.anchor_position = (offset[0], offset[1])
s4.anchor_position = (offset[0], offset[1])

# s2.rotation = 90
# s3.rotation = 180
# s4.rotation = 270


def update(dt):
    # s1.rotation += dt * 90

    s2.rotation += dt * 90
    s3.rotation += dt * 135
    s4.rotation -= dt * 45
    pass


@window.event
def on_draw():
    window.clear()
    batch1.draw()
    batch2.draw()


if __name__ == "__main__":
    pyglet.clock.schedule_interval(update, 1 / 120.0)
    pyglet.app.run()
