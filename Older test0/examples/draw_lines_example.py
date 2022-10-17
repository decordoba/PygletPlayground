import pyglet
import random
import colorsys


def get_color_by_idx(i):
    h = (i % 20) / 19
    s = 0.8
    v = 0.8
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))


# create window
window = pyglet.window.Window()

# set drawing config
pyglet.gl.glLineWidth(5)
pyglet.gl.glClearColor(0, 0, 0, 0)

# create global variables
positions = []
lines = []
colors = []

@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == pyglet.window.mouse.LEFT:
        print('The left mouse button was pressed in x: {} y: {}'.format(x, y))
        pt = [x, y, 0]
        colorsys.hsv_to_rgb(359,100,100)
        color = get_color_by_idx(len(positions))
        if len(positions) > 0:
            lines.extend(positions[-1] + pt)
            colors.extend(color + color)
        positions.append(pt)


@window.event
def on_draw():
    global lines, colors, positions
    window.clear()
    a = pyglet.graphics.vertex_list(3,
                                ("v3f", [-50, -50, 0, 50,  -50, 0, 0,  50, 0]),
                                ("c3B", [100, 200, 220, 200, 100, 100, 100, 250, 100]))
    a.draw(pyglet.gl.GL_TRIANGLES)
    if len(positions) == 1:
        pyglet.graphics.vertex_list(1, ("v3i", positions[0])).draw(pyglet.gl.GL_POINTS)
    elif len(positions) > 1:
        print(lines)
        pyglet.graphics.vertex_list(len(lines) // 3, ("v3i", lines), ("c3B", colors)).draw(pyglet.gl.GL_LINES)

pyglet.app.run()