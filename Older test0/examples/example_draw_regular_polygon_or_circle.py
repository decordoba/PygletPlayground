import pyglet
import math


def circle(x, y, r, p, c, b):
    """Adds a vertex list of circle polygon to batch and returns it.
    
    x, y is center circle,
    r is radius,
    p is number of points in circle excluding center,
    c is color tuple / 2 colors tuple,
    b is batch
    """
    angle_triangle = math.pi * 2 / p
    points = x, y  # center
    for i in range(p):
        n = angle_triangle * i
        points += int(r * math.cos(n)) + x, int(r * math.sin(n)) + y
    return b.add(p + 1, pyglet.gl.GL_TRIANGLE_FAN, None, ('v2i', points), ('c3B', (c)))


# Constants
WIN = 800, 800, 'TEST', False, 'tool' # x, y, caption, resizable, style
CENTER = WIN[0] // 2, WIN[1] // 2
RADIUS = 300
MAGENTA = (255, 0, 255)
WHITE = (255, 255, 255)
SPEED = 0.5 # in seconds

# Variables
win = pyglet.window.Window(*WIN)
batch = pyglet.graphics.Batch()
points = 3  # excluding center, start with triangle

def on_step(dt):
    """ Logic performed every frame. """
    global batch, points
    batch = pyglet.graphics.Batch()
    # points += 1 # 2, 3, 4...
    # print(points + 1)  # total number of points
    circle(CENTER[0], CENTER[1], RADIUS, points, WHITE+MAGENTA*(points), batch)

@win.event
def on_draw():
    """ Drawing perfomed every frame. """
    win.clear()
    batch.draw()

@win.event
def on_mouse_press(x, y, button, modifiers):
    global points, WIN
    if x > WIN[0] / 2:
        print("More points in circle:", points)
        points += 1
    else:
        print("Less points in circle:", points)
        points -= 1


pyglet.clock.schedule_interval(on_step, SPEED)
pyglet.app.run()