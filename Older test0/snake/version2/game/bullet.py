import pyglet
from . import resources
from . import physical_object

class Bullet(physical_object.PhysicalObject):
    """Bullets fired by the player."""

    def __init__(self, *args, **kwargs):
        super(Bullet, self).__init__(img=resources.bullet_image, *args, **kwargs)
        pyglet.clock.schedule_once(self.die, 0.5)
        self.is_bullet = True

    def die(self, dt):
        self.dead = True
