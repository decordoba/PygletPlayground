import pyglet
import random

import resources
import load
from player import Player


game_window = pyglet.window.Window(800, 600)


@game_window.event
def on_draw():
    game_window.clear()

    main_batch.draw()
    # level_label.draw()
    # score_label.draw()

    # for asteroid in asteroids:
    #     asteroid.draw()
    # player_ship.draw()


def update(dt):
    for obj in game_objects:
        obj.update(dt)


if __name__ == '__main__':
    main_batch = pyglet.graphics.Batch()

    score_label = pyglet.text.Label(text="Score: 0", x=10, y=575, batch=main_batch)
    level_label = pyglet.text.Label(text="My Amazing Game", x=400, y=575, anchor_x="center", batch=main_batch)
    lives = load.player_lives(3, batch=main_batch)

    player_ship = Player(img=resources.player_image, x=400, y=300, batch=main_batch)
    asteroids = load.asteroids(3, player_ship.position, batch=main_batch)

    game_objects = [player_ship] + asteroids
    game_window.push_handlers(player_ship)  # tell pyglet that player_ship is an event handler

    pyglet.clock.schedule_interval(update, 1 / 120.0)
    pyglet.app.run()
