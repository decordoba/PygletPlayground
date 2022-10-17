import pyglet
import math
from . import resources
from . import physical_object
from . import bullet


class Player(physical_object.PhysicalObject):

    def __init__(self, *args, **kwargs):
        super(Player, self).__init__(img=resources.player_image, *args, **kwargs)

        self.thrust = 300.0
        self.rotate_speed = 200.0

        self.keys = dict(left=False, right=False, up=False, down=False)
        self.key_handler = pyglet.window.key.KeyStateHandler()

        self.engine_sprite = pyglet.sprite.Sprite(img=resources.engine_image, *args, **kwargs)
        self.engine_sprite.visible = False

        self.bullet_speed = 700.0
        self.reacts_to_bullets = False
    
    def fire(self):
        angle_radians = -math.radians(self.rotation)
        ship_radius = self.image.width/2
        bullet_x = self.x + math.cos(angle_radians) * ship_radius
        bullet_y = self.y + math.sin(angle_radians) * ship_radius
        new_bullet = bullet.Bullet(x=bullet_x, y=bullet_y, batch=self.batch)
        bullet_vx = self.velocity_x + math.cos(angle_radians) * self.bullet_speed
        bullet_vy = self.velocity_y + math.sin(angle_radians) * self.bullet_speed
        new_bullet.velocity_x = bullet_vx
        new_bullet.velocity_y = bullet_vy
        new_bullet.rotation = self.rotation
        self.new_objects.append(new_bullet)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            self.fire()

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