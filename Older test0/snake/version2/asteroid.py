import pyglet
import random
import math
from game import config
from game import load
from game import player


def update(dt):
    # handle collisions (kill objects)
    for i in range(len(game_objects)):
        for j in range(i + 1, len(game_objects)):
            obj_1 = game_objects[i]
            obj_2 = game_objects[j]
            if not obj_1.dead and not obj_2.dead and obj_1.collides_with(obj_2):
                obj_1.handle_collision_with(obj_2)
                obj_2.handle_collision_with(obj_1)

    # update position and what is drawn, track new objects
    to_add = []
    for obj in game_objects:
        obj.update(dt)
        to_add.extend(obj.new_objects)
        obj.new_objects = []
        
    # add new objects
    game_objects.extend(to_add)

    # remove dead objects
    for to_remove in [obj for obj in game_objects if obj.dead]:
        to_remove.delete()
        game_objects.remove(to_remove)


if __name__ == "__main__":
    # create instance of window
    game_window = pyglet.window.Window(width=config.WIDTH, height=config.HEIGHT)

    # create main object batch (all objects in a batch are refreshed at the same time)
    main_batch = pyglet.graphics.Batch()

    # define function that will refresh screen 
    @game_window.event
    def on_draw():
        game_window.clear()
        main_batch.draw()

    # create score and title labels, and player's lives
    title_height = config.HEIGHT - 25
    score_label = pyglet.text.Label(text="Score: 0", x=10, y=title_height, batch=main_batch)
    level_label = pyglet.text.Label(text="Asteroids", x=config.WIDTH / 2, y=title_height, anchor_x="center", batch=main_batch)
    player_lives = load.player_lives(3, x=config.WIDTH - 15, y=title_height, batch=main_batch)

    # create player and asteroids
    player_ship = player.Player(x=400, y=300, batch=main_batch)
    game_window.push_handlers(player_ship)
    game_window.push_handlers(player_ship.key_handler)
    asteroids = load.asteroids(3, player_ship.position, batch=main_batch)
    game_objects = [player_ship] + asteroids

    # update game twice every frame (assuming 60 frames/s)
    pyglet.clock.schedule_interval(update, 1/120.0)
    # run game
    pyglet.app.run()