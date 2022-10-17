"""
@author: Daniel
First approach to engine
"""
import math
import pyglet


class EngineWindow(pyglet.window.Window):

    def __init__(self, width: int, height: int, batch=None, interval=1 / 30, *args, **kwargs):
        """Initailize window, and objects inside.

        Choose window attributes: width, height, caption, resizable, style, fullscreen, visible, vsync.
        """
        super().__init__(width, height, *args, **kwargs)

        self.t = 0
        self.paused = False
        self.batch = batch

        self.interval = interval

        self.objects = []

    def add_objects(self, objects):
        """Extend objects."""
        objects = [objects] if type(objects) is not list else objects
        self.objects.extend(objects)

    def remove_objects_by_index(self, indices):
        """Remove all objects with chosen object indices."""
        new_objects = []
        removed_objects = []
        indices = [indices] if type(indices) is int else indices
        for i, obj in enumerate(self.objects):
            if i in indices:
                removed_objects.append(obj)
            else:
                new_objects.append(obj)
        self.objects = new_objects
        for obj in removed_objects:
            obj.delete()

    def remove_objects_by_name(self, names):
        """Remove all objects with chosen object names."""
        new_objects = []
        removed_objects = []
        names = [names] if type(names) is int else names
        for obj in self.objects:
            if obj.name in names:
                removed_objects.append(obj)
            else:
                new_objects.append(obj)
        self.objects = new_objects
        for obj in removed_objects:
            obj.delete()

    def on_draw(self):
        """Clear the screen and draw objects in self.batch."""
        self.clear()
        if self.batch is not None:
            self.batch.draw()
        else:
            for obj in self.objects:
                obj.draw()

    def update(self, dt):
        """Animate objects."""
        if not self.paused:
            self.t += dt
            for obj in self.objects:
                obj.update(dt, self)

    def run(self):
        """Start run."""
        pyglet.clock.schedule_interval(self.update, self.interval)
        pyglet.app.run()

    def toggle_pause(self):
        """Pause/unpause update."""
        self.paused = not self.paused


class EngineObject():

    def __init__(self, name=None, category=None, shapes=None, motion=None, init_fn=None, hitboxes_square=None, hitboxes_circle=None):
        """Initialize engine object.

        Every object can have:
            * a unique name
            * a category (this should be an enum)
            * a list of shapes that will be drawn (if only one, there is no need to pass a list)
            * a motion function with logic on how every shape will be transformed on update
                def motion(shape, dt, window, object)
            * hitboxes
        """
        self.name = name
        self.category = category
        self.shapes = shapes if type(shapes) is list else ([shapes] if type(shapes) is not None else [])
        self.motion = motion
        self.hitboxes_square = hitboxes_square if hitboxes_square is not None else []
        self.hitboxes_circle = hitboxes_circle if hitboxes_circle is not None else []
        assert type(self.motion) is not list or len(self.motion) == len(self.shapes)
        if init_fn is not None:
            init_fn(self)

    def draw(self):
        """Draw shapes."""
        for shape in self.shapes:
            shape.draw()

    def update(self, dt, window):
        """Update properties shapes."""
        if self.motion is not None:
            if type(self.motion) is not list:
                for shape in self.shapes:
                    self.motion(shape, dt, window, self)
            else:
                for shape, motion in zip(self.shapes, self.motion):
                    if motion is not None:
                        motion(shape, dt, window, self)

    def delete(self):
        """Delete shapes."""
        for shape in self.shapes:
            shape.delete()

    def get_anchor(self):
        """Return anchor position, by default it is the anchor of the first shape."""
        return self.shapes[0].anchor_position


def main():
    """Main function."""
    batch = pyglet.graphics.Batch()

    window = EngineWindow(720, 480, batch=batch, caption="EngineWindowDemo")

    circle = pyglet.shapes.Circle(360, 240, 100, color=(255, 225, 255), batch=batch)
    circle.opacity = 127
    def circle_motion(shape, dt, window, object):
        shape.radius = 175 + math.sin(window.t * 1.17) * 50
    circle_object = EngineObject(shapes=circle, motion=circle_motion)

    ball = pyglet.shapes.Circle(360, 240, 30, color=(255, 0, 255), batch=batch)
    def ball_motion_warp(shape, dt, window, object):
        shape.x += object.vx * dt + 0.5 * object.ax * dt * dt
        shape.y += object.vy * dt + 0.5 * object.ay * dt * dt
        object.vx += object.ax * dt
        object.vy += object.ay * dt
        shape.x = shape.x % window.width
        shape.y = shape.y % window.height
    def ball_motion_bounce(shape, dt, window, object):
        shape.x += object.vx * dt + 0.5 * object.ax * dt * dt
        shape.y += object.vy * dt + 0.5 * object.ay * dt * dt
        object.vx += object.ax * dt
        object.vy += object.ay * dt
        if shape.x < 0:
            object.vx = abs(object.vx)
        if shape.x >= window.width:
            object.vx = -abs(object.vx)
        if shape.y < 0:
            object.vy = abs(object.vy)
        if shape.y >= window.height:
            object.vy = -abs(object.vy)
    ball_object = EngineObject(shapes=ball, motion=ball_motion_bounce)
    ball_object.vx = 300
    ball_object.vy = 0
    ball_object.ax = 0
    ball_object.ay = -1000

    window.add_objects([circle_object, ball_object])

    # Rectangle with center as anchor
    square = pyglet.shapes.Rectangle(360, 240, 200, 200, color=(55, 55, 255), batch=batch)
    square.anchor_x = 100
    square.anchor_y = 100

    # Large transparent rectangle
    rectangle = pyglet.shapes.Rectangle(0, 190, 720, 100, color=(255, 22, 20), batch=batch)
    rectangle.opacity = 64

    line = pyglet.shapes.Line(0, 0, 0, 480, width=4, color=(200, 20, 20), batch=batch)

    triangle = pyglet.shapes.Triangle(10, 10, 190, 10, 100, 150, color=(55, 255, 255), batch=batch)
    triangle.opacity = 175

    arc = pyglet.shapes.Arc(50, 300, radius=40, segments=25, angle=4, color=(255, 255, 255), batch=batch)

    star = pyglet.shapes.Star(600, 375, 50, 30, 5, color=(255, 255, 0), batch=batch)

    ellipse = pyglet.shapes.Ellipse(600, 150, a=50, b=30, color=(55, 255, 55), batch=batch)

    sector = pyglet.shapes.Sector(125, 400, 60, angle=0.9, color=(55, 255, 55), batch=batch)

    def square_motion(shape, dt, window, object):
        shape.rotation += dt * 15

    def rectangle_motion(shape, dt, window, object):
        shape.y = 200 + math.sin(window.t) * 190

    def line_motion(shape, dt, window, object):
        shape.position = (360 + math.sin(window.t * 0.81) * 360, 0,
                          360 + math.sin(window.t * 1.34) * 360, 480,)

    def arc_motion(shape, dt, window, object):
        shape.rotation = window.t * 30

    def star_motion(shape, dt, window, object):
        shape.rotation += dt * 50

    def ellipse_motion(shape, dt, window, object):
        shape.b = abs(math.sin(window.t) * 100)

    def sector_motion(shape, dt, window, object):
        # only way to modify angle in sector shape
        shape._angle = window.t % math.tau
        shape._update_position()

    objects = [
        EngineObject(shapes=square, motion=square_motion),
        EngineObject(shapes=rectangle, motion=rectangle_motion),
        EngineObject(shapes=line, motion=line_motion),
        EngineObject(shapes=arc, motion=arc_motion),
        EngineObject(shapes=star, motion=star_motion),
        EngineObject(shapes=ellipse, motion=ellipse_motion),
        EngineObject(shapes=sector, motion=sector_motion),
        EngineObject(shapes=triangle, motion=None),
    ]

    window.add_objects(objects)

    window.run()


if __name__ == "__main__":
    main()
