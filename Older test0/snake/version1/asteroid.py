import pyglet
import random
import math


WIDTH = 800
HEIGHT = 600


def center_image(image):
    """Sets an image"s anchor point to its center."""
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2


def asteroids(num_asteroids, player_position, batch=None):
    """Generate asteroids but not too close to player."""
    asteroids = []
    for _ in range(num_asteroids):
        asteroid_x, asteroid_y = player_position
        while distance((asteroid_x, asteroid_y), player_position) < 100:
            asteroid_x = random.randint(0, WIDTH)
            asteroid_y = random.randint(0, HEIGHT)
        new_asteroid = Asteroid(x=asteroid_x, y=asteroid_y, batch=batch)
        new_asteroid.rotation = random.randint(0, 360)
        new_asteroid.velocity_x = random.random()*40
        new_asteroid.velocity_y = random.random()*40
        asteroids.append(new_asteroid)
    return asteroids


def distance(point_1=(0, 0), point_2=(0, 0)):
    """Returns the distance between two points"""
    return math.sqrt((point_1[0] - point_2[0]) ** 2 + (point_1[1] - point_2[1]) ** 2)


def player_lives(num_icons, batch=None):
    player_lives = []
    for i in range(num_icons):
        new_sprite = pyglet.sprite.Sprite(img=player_image, x=785-i*30, y=575, batch=batch)
        new_sprite.scale = 0.5
        new_sprite.rotation = -90
        player_lives.append(new_sprite)
    return player_lives


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

class PhysicalObject(pyglet.sprite.Sprite):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.velocity_x, self.velocity_y = 0.0, 0.0
        self.dead = False
        self.new_objects = []
        self.reacts_to_bullets = True
        self.is_bullet = False

    def check_bounds(self):
        min_x = -self.image.width / 2
        min_y = -self.image.height / 2
        max_x = WIDTH + self.image.width / 2
        max_y = HEIGHT + self.image.height / 2
        if self.x < min_x:
            self.x = max_x
        elif self.x > max_x:
            self.x = min_x
        if self.y < min_y:
            self.y = max_y
        elif self.y > max_y:
            self.y = min_y
    
    def collides_with(self, other_object):
        if not self.reacts_to_bullets and other_object.is_bullet:
            return False
        if self.is_bullet and not other_object.reacts_to_bullets:
            return False

        collision_distance = self.image.width/2 + other_object.image.width/2
        actual_distance = distance(self.position, other_object.position)

        return (actual_distance <= collision_distance)
    
    def handle_collision_with(self, other_object):
        if other_object.__class__ == self.__class__:
            self.dead = False
        else:
            self.dead = True

    def update(self, dt):
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.check_bounds()


class Bullet(PhysicalObject):
    """Bullets fired by the player"""

    def __init__(self, *args, **kwargs):
        super(Bullet, self).__init__(img=bullet_image, *args, **kwargs)
        pyglet.clock.schedule_once(self.die, 0.5)
        self.is_bullet = True

    def die(self, dt):
        self.dead = True


class Asteroid(PhysicalObject):
    def __init__(self, *args, **kwargs):
        super(Asteroid, self).__init__(img=asteroid_image, *args, **kwargs)
        self.rotate_speed = random.random() * 100.0 - 50.0

    def handle_collision_with(self, other_object):
        super(Asteroid, self).handle_collision_with(other_object)
        if self.dead and self.scale > 0.25:
            num_asteroids = random.randint(2, 3)
            for i in range(num_asteroids):
                new_asteroid = Asteroid(x=self.x, y=self.y, batch=self.batch)
                new_asteroid.rotation = random.randint(0, 360)
                new_asteroid.velocity_x = (random.random() * 70 + self.velocity_x)
                new_asteroid.velocity_y = (random.random() * 70 + self.velocity_y)
                new_asteroid.scale = self.scale * 0.5
                self.new_objects.append(new_asteroid)
    
    def update(self, dt):
        super(Asteroid, self).update(dt)
        self.rotation += self.rotate_speed * dt


class Player(PhysicalObject):

    def __init__(self, *args, **kwargs):
        super(Player, self).__init__(img=player_image, *args, **kwargs)

        self.thrust = 300.0
        self.rotate_speed = 200.0

        self.keys = dict(left=False, right=False, up=False, down=False)
        self.key_handler = pyglet.window.key.KeyStateHandler()

        self.engine_sprite = pyglet.sprite.Sprite(img=engine_image, *args, **kwargs)
        self.engine_sprite.visible = False

        self.bullet_speed = 700.0
        self.reacts_to_bullets = False
    
    def fire(self):
        angle_radians = -math.radians(self.rotation)
        ship_radius = self.image.width/2
        bullet_x = self.x + math.cos(angle_radians) * ship_radius
        bullet_y = self.y + math.sin(angle_radians) * ship_radius
        new_bullet = Bullet(x=bullet_x, y=bullet_y, batch=self.batch)
        bullet_vx = self.velocity_x + math.cos(angle_radians) * self.bullet_speed
        bullet_vy = self.velocity_y + math.sin(angle_radians) * self.bullet_speed
        new_bullet.velocity_x = bullet_vx
        new_bullet.velocity_y = bullet_vy
        new_bullet.rotation = self.rotation
        self.new_objects.append(new_bullet)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            self.fire()

    # def on_key_press(self, symbol, modifiers):
    #     if symbol == pyglet.window.key.UP:
    #         self.keys["up"] = True
    #     elif symbol == pyglet.window.key.DOWN:
    #         self.keys["down"] = True
    #     elif symbol == pyglet.window.key.LEFT:
    #         self.keys["left"] = True
    #     elif symbol == pyglet.window.key.RIGHT:
    #         self.keys["right"] = True

    # def on_key_release(self, symbol, modifiers):
    #     if symbol == pyglet.window.key.UP:
    #         self.keys["up"] = False
    #     elif symbol == pyglet.window.key.DOWN:
    #         self.keys["down"] = False
    #     elif symbol == pyglet.window.key.LEFT:
    #         self.keys["left"] = False
    #     elif symbol == pyglet.window.key.RIGHT:
    #         self.keys["right"] = False

    def update(self, dt):
        super(Player, self).update(dt)

        # move player
        if self.key_handler[pyglet.window.key.LEFT]:
            self.rotation -= self.rotate_speed * dt
        elif self.key_handler[pyglet.window.key.RIGHT]:
            self.rotation += self.rotate_speed * dt
        elif self.key_handler[pyglet.window.key.UP]:
            angle_radians = -math.radians(self.rotation)
            force_x = math.cos(angle_radians) * self.thrust * dt
            force_y = math.sin(angle_radians) * self.thrust * dt
            self.velocity_x += force_x
            self.velocity_y += force_y
        elif self.key_handler[pyglet.window.key.DOWN]:
            angle_radians = -math.radians(self.rotation)
            force_x = math.cos(angle_radians) * self.thrust * dt
            force_y = math.sin(angle_radians) * self.thrust * dt
            self.velocity_x -= force_x
            self.velocity_y -= force_y

        # draw fire engine
        if self.key_handler[pyglet.window.key.UP] or self.key_handler[pyglet.window.key.DOWN]:
            self.engine_sprite.rotation = self.rotation
            self.engine_sprite.x = self.x
            self.engine_sprite.y = self.y
            self.engine_sprite.visible = True
        else:
            self.engine_sprite.visible = False

    def delete(self):
        self.engine_sprite.delete()
        super(Player, self).delete()


# create instance of window
game_window = pyglet.window.Window(width=WIDTH, height=HEIGHT)

# set resources path
pyglet.resource.path = ["../resources"]
pyglet.resource.reindex()

# import images
player_image = pyglet.resource.image("spaceship.png")
engine_image = pyglet.resource.image("flame.png")
bullet_image = pyglet.resource.image("missile.png")
asteroid_image = pyglet.resource.image("asteroid.png")

# set anchor point in images to their center
center_image(player_image)
center_image(bullet_image)
center_image(asteroid_image)
center_image(engine_image)

# create main object batch (all objects in a batch are refreshed at the same time)
main_batch = pyglet.graphics.Batch()

# create labels
score_label = pyglet.text.Label(text="Score: 0", x=10, y=575, batch=main_batch)
level_label = pyglet.text.Label(text="My Amazing Game", x=400, y=575, anchor_x="center", batch=main_batch)

# draw player lives
player_lives = player_lives(3, batch=main_batch)

# create player and asteroids
player_ship = Player(x=400, y=300, batch=main_batch)
game_window.push_handlers(player_ship)
game_window.push_handlers(player_ship.key_handler)
# player_ship = pyglet.sprite.Sprite(img=player_image, x=400, y=300, batch=main_batch)
asteroids = asteroids(3, player_ship.position, batch=main_batch)
game_objects = [player_ship] + asteroids

@game_window.event
def on_draw():
    game_window.clear()
    # level_label.draw()
    # score_label.draw()
    # player_ship.draw()
    # for asteroid in asteroids:
    #     asteroid.draw()
    main_batch.draw()


if __name__ == "__main__":
    # update game twice every frame (assuming 60 frames/s)
    pyglet.clock.schedule_interval(update, 1/120.0)
    # run game
    pyglet.app.run()