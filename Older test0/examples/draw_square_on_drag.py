import pyglet


# rectangle class
class Rect:

    def __init__(self, x, y, w, h):
        self.set(x, y, w, h)

    def draw(self):
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, self._quad)

    def set(self, x=None, y=None, w=None, h=None):
        self._x = self._x if x is None else x
        self._y = self._y if y is None else y
        self._w = self._w if w is None else w
        self._h = self._h if h is None else h
        self._quad = ('v2f', (self._x, self._y,
                              self._x + self._w, self._y,
                              self._x + self._w, self._y + self._h,
                              self._x, self._y + self._h))

    def __repr__(self):
        return f"Rect(x={self._x}, y={self._y}, w={self._w}, h={self._h})"


# main function
def main():
    r1 = Rect(10, 10, 100, 100)
    window = pyglet.window.Window()

    @window.event
    def on_draw():
        window.clear()
        r1.draw()

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        r1.set(x=x, y=y)
        print(r1)

    @window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        r1.set(x=x, y=y)
        print(r1)

    pyglet.app.run()

if __name__ == '__main__':
    main()
