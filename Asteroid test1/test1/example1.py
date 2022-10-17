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
    # calculate collisions (all objects against all objects) after new state
    for i in range(len(game_objects)):
        for j in range(i+1, len(game_objects)):
            obj_1 = game_objects[i]
            obj_2 = game_objects[j]
            
            if not obj_1.dead and not obj_2.dead:
                if obj_1.collides_with(obj_2):
                    obj_1.handle_collision_with(obj_2)
                    obj_2.handle_collision_with(obj_1)

    # update state of objects after dt, and track objects added after dt
    to_add = []
    for i, obj in enumerate(game_objects):
        obj.update(dt)
        to_add.extend(obj.new_objects)
        obj.new_objects = []

    # kill objects if dead is set to True
    for to_remove in [obj for obj in game_objects if obj.dead]:
        to_remove.delete()
        game_objects.remove(to_remove)
    
    # add added object to list objects to update
    game_objects.extend(to_add)


if __name__ == '__main__':
    main_batch = pyglet.graphics.Batch()

    score_label = pyglet.text.Label(text="Score: 0", x=10, y=575, batch=main_batch)
    level_label = pyglet.text.Label(text="My Amazing Game", x=400, y=575, anchor_x="center", batch=main_batch)
    lives = load.player_lives(3, batch=main_batch)

    player_ship = Player(x=400, y=300, batch=main_batch)
    asteroids = load.asteroids(3, player_ship.position, batch=main_batch)

    game_objects = [player_ship] + asteroids
    game_window.push_handlers(player_ship.key_handler)  # tell pyglet event handlers
    game_window.push_handlers(player_ship)  # tell pyglet event handlers

    pyglet.clock.schedule_interval(update, 1 / 120.0)
    pyglet.app.run()
