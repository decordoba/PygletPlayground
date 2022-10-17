import pyglet
import random
from . import resources
from . import utils
from . import asteroid
from . import config


def player_lives(num_lives, x=None, y=None, batch=None):
    """Load player lives."""
    player_lives = []
    x = x if x is not None else 785
    y = y if y is not None else 575
    for i in range(num_lives):
        new_sprite = pyglet.sprite.Sprite(img=resources.player_image, x=x - i * 30, y=y, batch=batch)
        new_sprite.scale = 0.5
        new_sprite.rotation = -90
        player_lives.append(new_sprite)
    return player_lives


def asteroids(num_asteroids, player_position, min_distance=150, batch=None):
    """Generate asteroids but not too close to player."""
    asteroids = []
    for _ in range(num_asteroids):
        asteroid_x, asteroid_y = player_position
        while utils.distance((asteroid_x, asteroid_y), player_position) < min_distance:
            asteroid_x = random.randint(0, config.WIDTH)
            asteroid_y = random.randint(0, config.HEIGHT)
        new_asteroid = asteroid.Asteroid(x=asteroid_x, y=asteroid_y, batch=batch)
        new_asteroid.rotation = random.randint(0, 360)
        new_asteroid.velocity_x = random.random()*40
        new_asteroid.velocity_y = random.random()*40
        asteroids.append(new_asteroid)
    return asteroids
