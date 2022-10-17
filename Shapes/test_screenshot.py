import pyglet
import random

from pyglet.graphics import Batch


window = pyglet.window.Window()

batch = pyglet.graphics.Batch()

background = pyglet.shapes.Rectangle(0, 0, window.width, window.height, color=(0, 0, 0), batch=batch)

label = pyglet.text.Label('Hello, world',
                          font_name='Times New Roman',
                          font_size=36,
                          x=window.width // 2, y=window.height // 2,
                          color=(255, 0, 0, 255),
                          anchor_x='center', anchor_y='center', batch=batch)


@window.event
def on_draw():
    window.clear()
    label.draw()


@window.event
def on_key_press(symbol, modifiers):
    print("Taking Screenshot...")
    pyglet.image.get_buffer_manager().get_color_buffer().save('screenshot.png')
    print("Done!")


def update(dt):
    label.x += random.randint(-10, 10)
    label.y += random.randint(-10, 10)


pyglet.clock.schedule_interval(update, 0.1)
pyglet.app.run()
