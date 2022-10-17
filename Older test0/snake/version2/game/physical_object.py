import pyglet
from . import utils
from . import config


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
        max_x = config.WIDTH + self.image.width / 2
        max_y = config.HEIGHT + self.image.height / 2
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
        actual_distance = utils.distance(self.position, other_object.position)

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