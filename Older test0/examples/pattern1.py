import pyglet
import random
import math
from functools import partial


class Vector2D(object):
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y
    
    def add(self, vector2d):
        self.x += vector2d.x
        self.y += vector2d.y

    def substract(self, vector2d):
        self.x -= vector2d.x
        self.y -= vector2d.y

    def multiply(self, variable):
        if type(variable) is Vector2D:
            self.x *= variable.x
            self.y *= variable.y
        else:
            self.x *= variable
            self.y *= variable

    def divide(self, variable):
        if type(variable) is Vector2D:
            self.x /= variable.x
            self.y /= variable.y
        else:
            self.x /= variable
            self.y /= variable

    def __mul__(self, other):
        if type(other) in [int, float]:
            return Vector2D(self.x * other, self.y * other)
        if type(other) is Vector2D:
            return Vector2D(self.x * other.x, self.y * other.y)
        if type(other) is list:
            new_list = []
            for i in range(0, len(other), 2):
                new_list.append(other[i] * self.x)
                new_list.append(other[i + 1] * self.y)
            return new_list

    def __rmul__(self, other):
        return self.__mul__(other)

    def __add__(self, other):
        if type(other) in [int, float]:
            return Vector2D(self.x + other, self.y + other)
        if type(other) is Vector2D:
            return Vector2D(self.x + other.x, self.y + other.y)
        if type(other) is list:
            new_list = []
            for i in range(0, len(other), 2):
                new_list.append(other[i] + self.x)
                new_list.append(other[i + 1] + self.y)
            return new_list

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if type(other) in [int, float]:
            return Vector2D(self.x - other, self.y - other)
        if type(other) is Vector2D:
            return Vector2D(self.x - other.x, self.y - other.y)
        if type(other) is list:
            new_list = []
            for i in range(0, len(other), 2):
                new_list.append(self.x - other[i])
                new_list.append(self.y - other[i + 1])
            return new_list

    def __rsub__(self, other):
        if type(other) in [int, float]:
            return Vector2D(other - self.x, other - self.y)
        if type(other) is Vector2D:
            return Vector2D(other.x - self.x, other.y - self.y)
        if type(other) is list:
            new_list = []
            for i in range(0, len(other), 2):
                new_list.append(other[i] - self.x)
                new_list.append(other[i + 1] - self.y)
            return new_list

    def __str__(self):
        return "x: {}, y: {}".format(self.x, self.y)

    def dist(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
    
    def same(self, other):
        return self.x == other.x and self.y == other.y

    def copy(self):
        return Vector2D(self.x, self.y)

    def is_zero(self):
        return self.x == 0 and self.y == 0

    def rotate_around_raw(self, x, y, angle):
        """Return point rotated around self by angle."""
        new_x = self.x + math.cos(angle) * (x - self.x) - math.sin(angle) * (y - self.y)
        new_y = self.y + math.sin(angle) * (x - self.x) + math.cos(angle) * (y - self.y)
        return new_x, new_y

    def rotate_around(self, point, angle):
        """Return point rotated around self by angle."""
        return Vector2D(*self.rotate_around_raw(point.x, point.y, angle))

    @classmethod
    def set_from_list(cls, lst):
        return cls(x=lst[0], y=lst[1])

    @classmethod
    def set_from_vector2d(cls, vector2d):
        if vector2d is None:
            vector2d = Vector2D()
        cls(x=vector2d.x, y=vector2d.y)
    
    def set_from_vector2d_if_none(self, vector2d):
        if self.x is None or self.y is None:
            self.__init__(x=vector2d.x, y=vector2d.y)

    def set_from_list_if_none(self, lst):
        if self.x is None or self.y is None:
            self.__init__(x=lst[0], y=lst[1])
    
    def get_as_list(self):
        return [self.x, self.y]


class Polygon(object):
    def __init__(self, name, anchor, vertices, colors, velocity=None,
                 acceleration=None, rotation_velocity=0, rotation_acceleration=0,
                 primitive=pyglet.gl.GL_POLYGON,
                 absolute_vertices=False, show_anchor=False):
        """Assume v2f vertices and c3B colors.
        
        name: name of polygon, serves as id.
              type string
        anchor: position that is moved / used as center for rotation
                type Vector2D
        vertices: offsets from anchor with vertices of polygon
                  type list with len = num_vertices*2 like [x0, y0, x1, y1...]
        colors: color for each vertex or solid color for all vertices
                type list with len = num_vertices*3 or len = 3 (for RGB)
        velocity: increment of position in every move operation
                  type Vector2D
        acceleration: increment of velocity in every accelerate operation
                      type Vector2D
        primitive: used to tell pyglet how to draw polygon
                   type int
        position_fix_function: function to correct position after movement
                               type function
        absolute_vertices: if False, vertices are offset from anchor
                           type bool
        show_anchor: whether to print anchor in complimentary color
                     type bool
        """
        # variables for how and where to draw
        self.anchor = anchor
        self.vertices = vertices if absolute_vertices else vertices + self.anchor
        self.num_vertices = int(len(self.vertices) // 2)
        self.colors = colors if len(colors) != 3 else colors * self.num_vertices
        assert len(self.vertices) / 2 == len(self.colors) / 3, "Vertices and colors don't match"
        self.primitive = primitive
        # variables for how to move/rotate
        self.velocity = velocity if velocity is not None else Vector2D(0, 0)
        self.acceleration = acceleration if acceleration is not None else Vector2D(0, 0)
        self.rotation_velocity = rotation_velocity
        self.rotation_acceleration = rotation_acceleration
        # variables for debugging
        self.name = name
        self.show_anchor = show_anchor
        # internal variables
        self.vertex_list = None
    
    def draw(self):
        """Update vertex list if necessary and draw the polygon."""
        if self.vertex_list is None:
            self.vertex_list = pyglet.graphics.vertex_list(self.num_vertices,
                                                           ("v2f", self.vertices),
                                                           ("c3B", self.colors))
        self.vertex_list.draw(self.primitive)
        # draw anchor, this is for debugging purposes and is not optimized
        if self.show_anchor:
            complimentary_color = [255 - c for c in self.colors[:3]] * 2
            cross = [
                (self.anchor.x + 3, self.anchor.y + 3, self.anchor.x - 3, self.anchor.y - 3),
                (self.anchor.x + 3, self.anchor.y - 3, self.anchor.x - 3, self.anchor.y + 3)
            ]
            for segment in cross:
                pyglet.graphics.vertex_list(2, ("v2f", segment), ("c3B", complimentary_color)).draw(pyglet.gl.GL_LINES)

    def move_by_offset(self, offset):
        for i, _ in enumerate(self.vertices):
            if i % 2 == 0:
                self.vertices[i] += offset.x
            else:
                self.vertices[i] += offset.y
        self.prev_anchor = self.anchor.copy()
        self.anchor += offset
    
    def move_anchor(self, anchor):
        self.move_by_offset(anchor - self.anchor)

    def move(self, dt):
        """Move vertex in vx, vy direction, accelerate velocity afterwards."""
        # move
        dt_factor = Vector2D(1, 1)
        if not self.velocity.is_zero():
            self.offset = self.velocity * dt + 0.5 * self.acceleration * dt * dt
            self.move_by_offset(self.offset)
            # controls what to do after moving (i.e. warp position, bounce...)
            dt_factor = self.after_movement(dt)
            Vector2D(1, 1) if dt_factor is None else dt_factor
            self.vertex_list = None
        # accelerate
        self.accelerate(dt, dt_factor)
    
    def rotate(self, dt):
        """Rotate by angle, accelerate rotation afterwards."""
        # rotate
        if self.rotation_velocity != 0:
            for i in range(0, len(self.vertices), 2):
                self.vertices[i], self.vertices[i + 1] = self.anchor.rotate_around_raw(self.vertices[i],
                                                                                       self.vertices[i + 1],
                                                                                       self.rotation_velocity * dt)
            self.vertex_list = None
        # accelerate
        self.accelerate_rotation(dt)

    def accelerate(self, dt, acceleration_correction=Vector2D(1, 1)):
        """Change velocity depending on acceleration."""
        if not self.acceleration.is_zero():
            self.velocity.add(self.acceleration * acceleration_correction * dt)

    def accelerate_rotation(self, dt):
        """Change rotation_velocity depending on rotation_acceleration."""
        if self.rotation_acceleration != 0:
            self.rotation_velocity += self.rotation_acceleration * dt

    def after_movement(self, dt):
        """What the polygon does after moving, here it does nothing (please, override)."""
        return Vector2D(1, 1)
    
    def update(self, dt):
        """Update internal state of polygon."""
        self.rotate(dt)
        self.move(dt)


class RegularPolygon(Polygon):
    def __init__(self, name, anchor, num_vertices, colors, radius=1, **kwargs):
        def calculate_vertices(anchor, num_vertices, radius=1):
            angle = 2 * math.pi / num_vertices
            angle0 = - math.pi / 2 - angle / 2
            angles = [angle0 + i * angle for i in range(num_vertices)]
            vertices = []
            for a in angles:
                vertices.append(math.cos(a) * radius + anchor.x)  # x
                vertices.append(math.sin(a) * radius + anchor.y)  # y
            return vertices

        vertices = calculate_vertices(anchor, num_vertices, radius)
        super(RegularPolygon, self).__init__(name, anchor, vertices, colors,
                                             absolute_vertices=True, **kwargs)


class BouncingRegularPolygon(RegularPolygon):
    def __init__(self, right_edge, top_edge, left_edge=0, bottom_edge=0, anchor_bounce=False, *args, **kwargs):
        super(BouncingRegularPolygon, self).__init__(*args, **kwargs)
        self.right_edge = right_edge
        self.top_edge = top_edge
        self.left_edge = left_edge
        self.bottom_edge = bottom_edge
        self.anchor_bounce = anchor_bounce

    def after_movement(self, dt):
        min_x, max_x = self.anchor.x, self.anchor.x
        min_y, max_y = self.anchor.y, self.anchor.y
        dt_factor = Vector2D(1, 1)
        if not self.anchor_bounce:
            xs = [x for i, x in enumerate(self.vertices) if i % 2 == 0]
            ys = [y for i, y in enumerate(self.vertices) if i % 2 == 1]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
        if max_x > self.right_edge:
            d, v = self.calculate_bounce(dt, max_x - self.right_edge, x_not_y=True)
            self.move_by_offset(Vector2D(d, 0))
            self.velocity.x = v
            dt_factor.x = 0
        elif min_x < self.left_edge:
            d, v = self.calculate_bounce(dt, min_x - self.left_edge, x_not_y=True)
            self.move_by_offset(Vector2D(d, 0))
            self.velocity.x = v
            dt_factor.x = 0
        if max_y > self.top_edge:
            d, v = self.calculate_bounce(dt, max_y - self.top_edge, x_not_y=False)
            self.move_by_offset(Vector2D(0, d))
            self.velocity.y = v
            dt_factor.y = 0
        elif min_y < self.bottom_edge:
            d, v = self.calculate_bounce(dt, min_y - self.bottom_edge, x_not_y=False)
            self.move_by_offset(Vector2D(0, d))
            self.velocity.y = v
            dt_factor.y = 0
        return dt_factor
    
    def calculate_bounce(self, dt, diff, x_not_y):
        if x_not_y:
            a = self.acceleration.x
            v = self.velocity.x
            o = self.offset.x
        else:
            a = self.acceleration.y
            v = self.velocity.y
            o = self.offset.y
        # calculate times
        t0, t1 = solve_x(0.5 * a, v, diff - o)
        dt0 = t1 if t1 > 0 else (t0 if t0 > 0 else None)
        dt1 = dt - dt0
        # calculate position and velocity on bounce
        p0 = v * dt0 + 0.5 * a * dt0 * dt0
        v += a * dt0
        v = -v
        # calculate position and velocity at end of dt
        p1 = v * dt1 + 0.5 * a * dt1 * dt1
        v += a * dt1
        # calculate new offset
        d = p0 + p1 - o
        return d, v

def solve_x(a, b, c):
    """Solve x for ax^2 + bx + c = 0."""
    sqrt_b2_4ac = math.sqrt(b * b - 4 * a * c)
    t0, t1 = (-b + sqrt_b2_4ac) / 2 / a, (-b - sqrt_b2_4ac) / 2 / a
    return t0, t1


class WarpingPolygon(RegularPolygon):
    def __init__(self, right_edge, top_edge, left_edge=0, bottom_edge=0, anchor_warp=True, *args, **kwargs):
        super(WarpingPolygon, self).__init__(*args, **kwargs)
        self.right_edge = right_edge
        self.top_edge = top_edge
        self.left_edge = left_edge
        self.bottom_edge = bottom_edge
        self.screen_width = self.right_edge - self.left_edge
        self.screen_height = self.top_edge - self.bottom_edge
        self.anchor_warp = anchor_warp
    
    def after_movement(self, dt):
        min_x, max_x = self.anchor.x, self.anchor.x
        min_y, max_y = self.anchor.y, self.anchor.y
        dt_factor = Vector2D(1, 1)
        if not self.anchor_warp:
            xs = [x for i, x in enumerate(self.vertices) if i % 2 == 0]
            ys = [y for i, y in enumerate(self.vertices) if i % 2 == 1]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
        diff_x = self.screen_width + max_x - min_x
        diff_y = self.screen_height + max_y - min_y
        if min_x > self.right_edge:
            self.move_by_offset(Vector2D(-diff_x, 0))
        elif max_x < self.left_edge:
            self.move_by_offset(Vector2D(diff_x, 0))
        if min_y > self.top_edge:
            self.move_by_offset(Vector2D(0, -diff_y))
        elif max_y < self.bottom_edge:
            self.move_by_offset(Vector2D(0, diff_y))
        return dt_factor


class GameWindow(pyglet.window.Window):
    def __init__(self, objects=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pyglet.gl.glClearColor(0, 0, 0, 0)
        # setup draw
        objects = [] if objects is None else objects
        self.object_names = [o.name for o in objects]
        self.objects = {o.name: o for o in objects}
    
    def add_object(self, new_object):
        """Add object to objects, or replace if name already exists."""
        self.objects[new_object.name] = new_object
    
    def remove_object(self, object_name):
        if object_name in self.objects:
            del self.objects[object_name]
    
    def update(self, dt):
        for name in self.objects:
            self.objects[name].update(dt)

    def on_draw(self):
        self.clear()
        # draw every refresh
        for name in self.object_names:
            self.objects[name].draw()


class Game(object):
    def __init__(self, w=20, h=20, px_w=20, px_h=20, title="My game", resizable=False):
        self.w = w
        self.h = h
        self.px_w = px_w
        self.px_h = px_h
        self.refresh_raw_dimensions()

        objects = [
            BouncingRegularPolygon(name="d0",
                    anchor=Vector2D(self.raw_w / 2, self.raw_h / 2),
                    num_vertices=8,
                    radius=30,
                    colors=[0, 0, 255],
                    acceleration=Vector2D(-30, -30),
                    right_edge=self.raw_w,
                    top_edge=self.raw_h),
            BouncingRegularPolygon(name="d1",
                    anchor=Vector2D(self.raw_w / 2, self.raw_h / 2),
                    num_vertices=8,
                    radius=30,
                    colors=[0, 0, 255],
                    acceleration=Vector2D(-30, 30),
                    right_edge=self.raw_w,
                    top_edge=self.raw_h),
            BouncingRegularPolygon(name="d2",
                    anchor=Vector2D(self.raw_w / 2, self.raw_h / 2),
                    num_vertices=8,
                    radius=30,
                    colors=[0, 0, 255],
                    acceleration=Vector2D(30, -30),
                    right_edge=self.raw_w,
                    top_edge=self.raw_h),
            BouncingRegularPolygon(name="d3",
                    anchor=Vector2D(self.raw_w / 2, self.raw_h / 2),
                    num_vertices=8,
                    radius=30,
                    colors=[0, 0, 255],
                    acceleration=Vector2D(30, 30),
                    right_edge=self.raw_w,
                    top_edge=self.raw_h),
            BouncingRegularPolygon(name="n0",
                    anchor=Vector2D(self.raw_w / 2, self.raw_h / 2),
                    num_vertices=8,
                    radius=30,
                    colors=[255, 255, 0],
                    acceleration=Vector2D(-60, -30),
                    right_edge=self.raw_w,
                    top_edge=self.raw_h),
            BouncingRegularPolygon(name="n1",
                    anchor=Vector2D(self.raw_w / 2, self.raw_h / 2),
                    num_vertices=8,
                    radius=30,
                    colors=[255, 255, 0],
                    acceleration=Vector2D(-30, -60),
                    right_edge=self.raw_w,
                    top_edge=self.raw_h),
            BouncingRegularPolygon(name="n2",
                    anchor=Vector2D(self.raw_w / 2, self.raw_h / 2),
                    num_vertices=8,
                    radius=30,
                    colors=[255, 255, 0],
                    acceleration=Vector2D(30, 60),
                    right_edge=self.raw_w,
                    top_edge=self.raw_h),
            BouncingRegularPolygon(name="n3",
                    anchor=Vector2D(self.raw_w / 2, self.raw_h / 2),
                    num_vertices=8,
                    radius=30,
                    colors=[255, 255, 0],
                    acceleration=Vector2D(60, 30),
                    right_edge=self.raw_w,
                    top_edge=self.raw_h),
            BouncingRegularPolygon(name="n4",
                    anchor=Vector2D(self.raw_w / 2, self.raw_h / 2),
                    num_vertices=8,
                    radius=30,
                    colors=[255, 255, 0],
                    acceleration=Vector2D(60, -30),
                    right_edge=self.raw_w,
                    top_edge=self.raw_h),
            BouncingRegularPolygon(name="n5",
                    anchor=Vector2D(self.raw_w / 2, self.raw_h / 2),
                    num_vertices=8,
                    radius=30,
                    colors=[255, 255, 0],
                    acceleration=Vector2D(30, -60),
                    right_edge=self.raw_w,
                    top_edge=self.raw_h),
            BouncingRegularPolygon(name="n6",
                    anchor=Vector2D(self.raw_w / 2, self.raw_h / 2),
                    num_vertices=8,
                    radius=30,
                    colors=[255, 255, 0],
                    acceleration=Vector2D(-30, 60),
                    right_edge=self.raw_w,
                    top_edge=self.raw_h),
            BouncingRegularPolygon(name="n7",
                    anchor=Vector2D(self.raw_w / 2, self.raw_h / 2),
                    num_vertices=8,
                    radius=30,
                    colors=[255, 255, 0],
                    acceleration=Vector2D(-60, 30),
                    right_edge=self.raw_w,
                    top_edge=self.raw_h),
            BouncingRegularPolygon(name="octagon1",
                    anchor=Vector2D(self.raw_w / 2, self.raw_h / 2),
                    num_vertices=8,
                    radius=30,
                    colors=[255, 0, 0],
                    acceleration=Vector2D(-60, 0),
                    right_edge=self.raw_w,
                    top_edge=self.raw_h),
            BouncingRegularPolygon(name="octagon2",
                    anchor=Vector2D(self.raw_w / 2, self.raw_h / 2),
                    num_vertices=8,
                    radius=30,
                    colors=[255, 0, 0],
                    acceleration=Vector2D(60, 0),
                    right_edge=self.raw_w,
                    top_edge=self.raw_h),
            BouncingRegularPolygon(name="octagon3",
                    anchor=Vector2D(self.raw_w / 2, self.raw_h / 2),
                    num_vertices=8,
                    radius=30,
                    colors=[255, 0, 0],
                    acceleration=Vector2D(0, -60),
                    right_edge=self.raw_w,
                    top_edge=self.raw_h),
            BouncingRegularPolygon(name="octagon4",
                    anchor=Vector2D(self.raw_w / 2, self.raw_h / 2),
                    num_vertices=8,
                    radius=30,
                    colors=[255, 0, 0],
                    acceleration=Vector2D(0, 60),
                    right_edge=self.raw_w,
                    top_edge=self.raw_h),
            # Polygon(name="arrow",
            #         anchor=Vector2D(self.raw_w / 2, self.raw_h / 2),
            #         vertices=[0, 0, 2 * self.px_w, self.px_h, 1.5 * self.px_w, 0, 2 * self.px_w, -self.px_h],
            #         colors=[128, 0, 255],
            #         velocity=Vector2D(0.0, 0.0),
            #         rotation_acceleration=0,
            #         rotation_velocity=math.pi),
            RegularPolygon(name="ball",
                                   anchor=Vector2D(self.raw_w / 3, self.raw_h / 3),
                                   num_vertices=50,
                                   radius=15,
                                   colors=[0, 255, 0],
                                   velocity=Vector2D(200, -600)),
        ]

        self.window = GameWindow(objects, self.px_w * self.w, self.px_h * self.h, title, resizable)
    
    def refresh_raw_dimensions(self):
        self.raw_w = self.w * self.px_w
        self.raw_h = self.h * self.px_h

    def update(self, dt):
        self.window.update(dt)


if __name__ == "__main__":
    game = Game(resizable=False)
    pyglet.clock.schedule_interval(game.update, 1/240)
    pyglet.app.run()
