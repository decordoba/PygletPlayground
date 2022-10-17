import pyglet
import random
import math
from functools import partial

NICKNAMES = {
    (0, 0, 0): "BLACK ",
    (255, 0, 0): "RED   ",
    (0, 255, 0): "GREEN ",
    (0, 0, 255): "BLUE  ",
    (255, 255, 0): "YELLOW",
    (255, 0, 255): "PURPLE",
    (0, 255, 255): "CYAN  ",
    (255, 255, 255): "WHITE "
}

class Vector2D(object):
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y
    
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

    def __truediv__(self, other):
        if type(other) in [int, float]:
            return Vector2D(self.x / other, self.y / other)
        if type(other) is Vector2D:
            return Vector2D(self.x / other.x, self.y / other.y)
        if type(other) is list:
            new_list = []
            for i in range(0, len(other), 2):
                new_list.append(self.x / other[i])
                new_list.append(self.y / other[i + 1])
            return new_list

    def __rtruediv__(self, other):
        if type(other) in [int, float]:
            return Vector2D(other / self.x, other / self.y)
        if type(other) is Vector2D:
            return Vector2D(other.x / self.x, other.y / self.y)
        if type(other) is list:
            new_list = []
            for i in range(0, len(other), 2):
                new_list.append(other[i] / self.x)
                new_list.append(other[i + 1] / self.y)
            return new_list

    def __abs__(self):
        return Vector2D(abs(self.x), abs(self.y))
    
    def __int__(self):
        return Vector2D(int(self.x), int(self.y))

    def __str__(self):
        return "x: {}, y: {}".format(self.x, self.y)

    def __repr__(self):
        return "x: {}\ny: {}".format(self.x, self.y)

    def dist(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
    
    def same(self, other):
        return self.x == other.x and self.y == other.y

    def copy(self):
        return Vector2D(self.x, self.y)
    
    def shift(self):
        self.x, self.y = self.y, self.x
        return self

    def is_zero(self):
        return self.x == 0 and self.y == 0
    
    def cast(self, data_type):
        self.x = data_type(self.x)
        self.y = data_type(self.y)
        return self

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
        return cls(x=vector2d.x, y=vector2d.y)
    
    def set_from_vector2d_if_none(self, vector2d):
        if self.x is None or self.y is None:
            self.__init__(x=vector2d.x, y=vector2d.y)

    def set_from_list_if_none(self, lst):
        if self.x is None or self.y is None:
            self.__init__(x=lst[0], y=lst[1])
    
    def get_as_list(self):
        return [self.x, self.y]


class GameObject(object):
    def __init__(self, name, visual_objects, move_logic=None, collide_logic=None, peripherals_logic=None):
        self.name = name
        # contains vertices, anchor, etc. that will be drawn
        self.visual_objects = visual_objects if type(visual_objects) is list else [visual_objects]
        # contains movement logic: how position changes every dt
        # may use/change vertices and anchor from visual_object
        self.has_move_logic = move_logic is not None
        self.move_logic = move_logic if self.has_move_logic else MoveLogic()
        # controls what to do on a collision with screen edges, etc.
        # may use/change vertices and anchor from visual_object
        # may use/change values from move_logic
        self.has_collide_logic = collide_logic is not None
        self.collide_logic = collide_logic if self.has_collide_logic else self.move_logic
        # controlls what to do when peripherals changes are received
        # may use/change vertices and anchor from visual_object
        # may use/change values from move_logic
        # may use/change values from collide_logic
        self.has_peripherals_logic = peripherals_logic is not None
        self.peripherals_logic = peripherals_logic if self.has_peripherals_logic else self.move_logic

    def update(self, dt, peripherals_input=None):
        self.move_logic.update(self.visual_objects,
                               self.collide_logic,
                               self.peripherals_logic, dt,
                               peripherals_input=peripherals_input)
    
    def draw(self):
        for visual_object in self.visual_objects:
            visual_object.draw()


class Polygon(object):
    def __init__(self, anchor, vertices, colors, vertices_indices=None, primitive=pyglet.gl.GL_TRIANGLES,
                 batch=None, group=None, initial_rotation=0, absolute_vertices=False,
                 show_anchor=False):
        """Assume v2f vertices and c3B colors.
        
        anchor: position that is moved / used as center for rotation
                type Vector2D or list
        vertices: offsets from anchor with vertices of polygon
                  type list with len = num_vertices*2 like [x0, y0, x1, y1...]
        colors: color for each vertex or solid color for all vertices
                type list with len = num_vertices*3 or len = 3 (for RGB)
        primitive: used to tell pyglet how to draw polygon
                   type int
        initial_rotation: vertices are rotated this much on start, angle in radians
                          type float
        absolute_vertices: if False, vertices are offset from anchor
                           type bool
        show_anchor: whether to print anchor in complimentary color
                     type bool
        """
        # internal variables
        self.move_total = Vector2D(0, 0)
        self.rotate_total = 0
        # variables for how and where to draw
        self.anchor = anchor if type(anchor) is not list else Vector2D.set_from_list(anchor)
        self.vertices = vertices if absolute_vertices else vertices + self.anchor
        self.vertices_format = "v2f"
        self.rotate_by_angle(initial_rotation)
        self.vertices_indices = vertices_indices
        num_vertices = int(len(self.vertices) // 2)
        self.colors_format = 3 if len(colors) == 3 or len(colors) / num_vertices == 3 else None
        self.colors_format = 4 if len(colors) == 4 or len(colors) / num_vertices == 4 else self.colors_format
        self.colors = colors if len(colors) != self.colors_format else colors * num_vertices
        self.colors_format = "c3B" if self.colors_format == 3 else ("c4B" if self.colors_format == 4 else None)
        self.primitive = primitive
        self.batch = batch
        self.group = group
        # variables for debugging
        self.show_anchor = show_anchor
        self.nickname = tuple(self.colors[:3])
        self.nickname = NICKNAMES[self.nickname] if self.nickname in NICKNAMES else str(self.nickname)
        # internal variables
        self.reset_calculations()
        self.num_vertices = num_vertices
        self.initial_anchor = self.anchor.copy()
        self.initial_vertices = self.vertices.copy()
        self.initial_colors = self.colors.copy()
        self.initial_vertices_indices = None if self.vertices_indices is None else self.vertices_indices.copy()
        self.previous_anchor = self.anchor.copy()
        self.previous_vertices = self.vertices.copy()
        # initialize polygon
        self.initialize_vertex_list()

    def restart(self):
        """Set object to original values."""
        self.anchor = self.initial_anchor.copy()
        self.vertices = self.initial_vertices.copy()
        self.colors = self.initial_colors.copy()

    def record_current_state(self):
        """Remember vertices and anchor of object, reset cumulative variables."""
        self.previous_anchor = self.anchor.copy()
        self.previous_vertices = self.vertices.copy()
        self.move_total = Vector2D(0, 0)
        self.rotate_total = 0

    def initialize_vertex_list(self):
        """Declare vertex_list, after this vertices will be refreshed but vertex_list will not."""
        if self.batch is None:
            if self.vertices_indices is None:
                self.vertex_list = pyglet.graphics.vertex_list(self.num_vertices,
                                                               (self.vertices_format, self.vertices),
                                                               (self.colors_format, self.colors))
            else:
                self.vertex_list = pyglet.graphics.vertex_list_indexed(self.num_vertices,
                                                                       self.vertices_indices,
                                                                       (self.vertices_format, self.vertices),
                                                                       (self.colors_format, self.colors))
        else:
            if self.vertices_indices is None:
                self.vertex_list = self.batch.add(self.num_vertices, self.primitive, self.group,
                                                  (self.vertices_format, self.vertices),
                                                  (self.colors_format, self.colors))
            else:
                self.vertex_list = self.batch.add_indexed(self.num_vertices, self.primitive, self.group,
                                                          self.vertices_indices,
                                                          (self.vertices_format, self.vertices),
                                                          (self.colors_format, self.colors))

    def draw(self):
        """Update vertex list if necessary and draw the polygon."""
        if self.refresh_vertex_list:
            self.vertex_list.vertices = self.vertices
            self.refresh_vertex_list = False
        if self.batch is None:
            self.vertex_list.draw(self.primitive)
        # draw anchor, this is for debugging purposes and is not optimized, only works if batch is not given
        if self.show_anchor:
            complimentary_color = [255 - c for c in self.colors[:3]] * 2
            cross = [
                (self.anchor.x + 3, self.anchor.y + 3,
                 self.anchor.x - 3, self.anchor.y - 3),
                (self.anchor.x + 3, self.anchor.y - 3,
                 self.anchor.x - 3, self.anchor.y + 3)
            ]
            for segment in cross:
                pyglet.graphics.vertex_list(2,
                                            ("v2f", segment),
                                            ("c3B", complimentary_color)).draw(pyglet.gl.GL_LINES)

    def move_by_offset(self, offset):
        """Move anchor and vertices by offset. Remember previous anchor."""
        self.vertices += offset
        self.anchor += offset
        self.move_total += offset
        self.min_vertex += offset
        self.max_vertex += offset
        self.reset_calculations(has_rotated=False)
    
    def move_anchor(self, anchor):
        """Move anchor to an absolute location, and all vertices accordingly."""
        self.move_by_offset(anchor - self.anchor)

    def rotate_by_angle(self, angle):
        """Rotate all vertices around anchor by angle in radians."""
        for i in range(0, len(self.vertices), 2):
            vx, vy = self.anchor.rotate_around_raw(self.vertices[i], self.vertices[i + 1], angle)
            self.vertices[i], self.vertices[i + 1] = vx, vy
        self.rotate_total += angle
        self.reset_calculations(has_rotated=True)
    
    def reset_calculations(self, has_rotated=True):
        """Set vertex list and anything related to vertices being drawn/calculated to None."""
        self.refresh_vertex_list = True
        if has_rotated:
            self.min_vertex = None
            self.max_vertex = None
    
    def get_min_max_vertices(self):
        """Get min and max vertex for x and y."""
        if self.min_vertex is None or self.max_vertex is None:
            xs = [0] * int(len(self.vertices) // 2)
            ys = [0] * len(xs)
            for i, val in enumerate(self.vertices):
                if i % 2 == 0:
                    xs[i // 2] = val
                else:
                    ys[i // 2] = val
            self.min_vertex = Vector2D(min(xs), min(ys))
            self.max_vertex = Vector2D(max(xs), max(ys))
        return self.min_vertex, self.max_vertex


class RegularPolygon(Polygon):
    def __init__(self, anchor, num_vertices, colors, radius=1, side=None, use_vertices_indices=True, **kwargs):
        def calculate_vertices(anchor, num_vertices, radius=1, side=None, use_vertices_indices=True):
            angle = 2 * math.pi / num_vertices
            angle0 = - math.pi / 2 - angle / 2
            angles = [angle0 + i * angle for i in range(num_vertices)]
            radius = radius if side is None else side / 2 / math.sin(angle / 2)  # overwrite radius
            vertices = []
            for a in angles:
                vertices.append(math.cos(a) * radius + anchor.x)  # x
                vertices.append(math.sin(a) * radius + anchor.y)  # y
            if use_vertices_indices:
                vertices = [anchor.x, anchor.y] + vertices
                vertices_indices = []
                for i in range(num_vertices):
                    vertices_indices += [0, i + 1, i + 2]
                vertices_indices[-1] = 1
            else:
                vertices_indices = None
            return vertices, vertices_indices
        anchor = anchor if type(anchor) is not list else Vector2D.set_from_list(anchor)
        vertices, vertices_indices = calculate_vertices(anchor, num_vertices, radius, side,
                                                        use_vertices_indices=use_vertices_indices)
        super(RegularPolygon, self).__init__(anchor, vertices, colors,
                                             vertices_indices=vertices_indices,
                                             absolute_vertices=True, **kwargs)


class MoveLogic(object):
    def __init__(self, velocity=None, acceleration=None, rotation_velocity=0,
                 rotation_acceleration=0):
        """Move and rotate drawable object according to speed and acceleration.

        velocity: increment of position in every move operation
                  type Vector2D or list (px/s)
        acceleration: increment of velocity in every accelerate operation
                      type Vector2D or list (px/s^2)
        rotation_velocity: rotate object in every rotate operation
                           type float (rad/s)
        rotation_acceleration: increment rotation speed in time
                               type float (rad/s^2)
        """
        # movement variables
        self.velocity = velocity if velocity is not None else Vector2D(0, 0)
        self.velocity = self.velocity if type(self.velocity) is not list else Vector2D.set_from_list(self.velocity)
        self.acceleration = acceleration if acceleration is not None else Vector2D(0, 0)
        self.acceleration = self.acceleration if type(self.acceleration) is not list else Vector2D.set_from_list(self.acceleration)
        self.rotation_velocity = rotation_velocity
        self.rotation_acceleration = rotation_acceleration
        # internal variables
        self.initial_velocity = self.velocity.copy()
        self.initial_acceleration = self.acceleration.copy()
        self.initial_rotation_velocity = self.rotation_velocity
        self.initial_rotation_acceleration = self.rotation_acceleration
        self.dt = 0

    def restart(self):
        """Set logic to original values."""
        self.velocity = self.initial_velocity.copy()
        self.acceleration = self.initial_acceleration.copy()
        self.rotation_velocity = self.initial_rotation_velocity
        self.rotation_acceleration = self.initial_rotation_acceleration

    def update(self, objs, collide_logic, peripherals_logic, dt, peripherals_input=None):
        """Update internal state of drawable object."""
        # record object at the beginning of the update
        for obj in objs:
            obj.record_current_state()
        # handle keys and mouse actions by user if they exist
        has_changed = False
        if peripherals_input is not None:
            has_changed = peripherals_logic.handle_peripherals_input(objs, self, dt, peripherals_input)
        # rotate and move object
        has_rotated = self.rotate(objs, dt)
        has_moved = self.move(objs, dt)
        # handle collisions if there were changes, and accelerate movement and rotation 
        if has_rotated or has_moved or has_changed:
            dt_factor_move, dt_factor_rotate = collide_logic.after_movement(objs, self, dt)
            self.accelerate_rotation(dt, dt_factor_rotate)
            self.accelerate(dt, dt_factor_move)
        else:
            self.accelerate(dt)
            self.accelerate_rotation(dt)

    def move(self, objs, dt):
        """Move vertex in vx, vy direction, remember movement distance."""
        if not self.velocity.is_zero():
            for obj in objs:
                obj.move_by_offset(self.velocity * dt + 0.5 * self.acceleration * dt * dt)
            return True
        return False

    def rotate(self, objs, dt):
        """Rotate by angle, accelerate rotation afterwards."""
        if self.rotation_velocity != 0:
            for obj in objs:
                obj.rotate_by_angle(self.rotation_velocity * dt)
            return True
        return False

    def accelerate(self, dt, acceleration_correction=Vector2D(1, 1)):
        """Change velocity depending on acceleration."""
        if not self.acceleration.is_zero():
            self.velocity += self.acceleration * acceleration_correction * dt

    def accelerate_rotation(self, dt, acceleration_correction=1):
        """Change rotation_velocity depending on rotation_acceleration."""
        if self.rotation_acceleration != 0:
            self.rotation_velocity += self.rotation_acceleration * acceleration_correction * dt

    def after_movement(self, objs, move_logic, dt):
        """How the object and move_logic change after each dt move step, here no changes."""
        # implement other behaviors in a collider_logic object
        return Vector2D(1, 1), 1  # return dt_factor_move and dt_factor_rotate
    
    def handle_peripherals_input(self, objs, move_logic, dt, peripherals_input):
        """What to do when keys/mouse are used."""
        # implement other behaviors in a peripherals_logic object
        return False


class AbsoluteMoveLogic(MoveLogic):
    def __init__(self, *args, modify_increment_after_step=False, verbose=True, **kwargs):
        """Move based on absolute values, ignore dt for move. Used mostly for debugging."""
        super(AbsoluteMoveLogic, self).__init__(*args, **kwargs)
        self.modify_increment_after_step = modify_increment_after_step
        self.verbose = verbose
        self.options = ["px", "py", "vx", "vy", "ax", "ay", "rv", "ra", "s0", "go", "id"]

    def move(self, objs, dt):
        """Move vertex vx, vy pixels, ignore dt."""
        if self.modify_increment_after_step:
            # modify x and y increments in next move.
            idx = 0
            if self.verbose:
                print("Object State:" +
                      "  Objects: {}, Id: {}".format(len(objs), idx) +
                      "  Position: {}".format(objs[idx].anchor) +
                      "  Velocity: {}".format(self.velocity) +
                      "  Acceleration: {}".format(self.acceleration) +
                      "  Rotation: v: {} a: {}".format(self.rotation_velocity, self.rotation_acceleration) +
                      "Options:" +
                      "  {}".format(self.options))

            changes = input(">> ")
            if len(changes) > 1:
                for change in changes.split():
                    op = change[0:2].lower()
                    if op in self.options:
                        try:
                            if len(change[2:]):
                                value = 0
                            else:
                                value = float(change[2:])
                        except ValueError:
                            continue
                        if op == "px":
                            objs[idx].move_anchor(Vector2D(value, objs[idx].anchor.y))
                        elif op == "py":
                            objs[idx].move_anchor(Vector2D(objs[idx].anchor.x, value))
                        elif op == "vx":
                            self.velocity.x = value
                        elif op == "vy":
                            self.velocity.y = value
                        elif op == "ax":
                            self.acceleration.x = value
                        elif op == "ay":
                            self.acceleration.y = value
                        elif op == "rv":
                            self.rotation_velocity = value
                        elif op == "ra":
                            self.rotation_acceleration = value
                        elif op == "s0":
                            objs[idx].restart()
                        elif op == "go":
                            self.modify_increment_after_step = False
                        elif op == "id":
                            new_idx = int(value)
                            idx = new_idx if new_idx < len(objs) else idx
        if not self.velocity.is_zero():
            for obj in objs:
                obj.move_by_offset(self.velocity)
            return True
        return False


class DiscreteMoveLogic(MoveLogic):
    def __init__(self, steps, *args, **kwargs):
        """Initialize the length of the steps."""
        super(DiscreteMoveLogic, self).__init__(*args, **kwargs)
        self.steps = steps if type(steps) is not list else Vector2D.set_from_list(steps)
        self.remaining_movement = Vector2D(0, 0)  # how much object moved after step but not yet a new step

    def move(self, objs, dt):
        """Move vertex in vx, vy direction, only update object if it has moved one step."""
        if not self.velocity.is_zero():
            movement = self.velocity * dt + 0.5 * self.acceleration * dt * dt + self.remaining_movement
            num_steps = movement / self.steps
            num_steps.cast(int)  # cast to remove decimals, get int num of steps
            last_movement = self.steps * num_steps
            self.remaining_movement = movement - last_movement
            if not last_movement.same(Vector2D(0, 0)):
                for obj in objs:
                    obj.move_by_offset(last_movement)
                return True
        return False


class DiscreteFollowMoveLogic(DiscreteMoveLogic):
    def move(self, objs, dt):
        """Move vertex in vx, vy direction, only update object if it has moved one step."""
        if not self.velocity.is_zero():
            movement = self.velocity * dt + 0.5 * self.acceleration * dt * dt + self.remaining_movement
            num_steps = movement / self.steps
            num_steps.cast(int)  # cast to remove decimals, get int num of steps
            last_movement = self.steps * num_steps
            self.remaining_movement = movement - last_movement
            if not last_movement.same(Vector2D(0, 0)):
                for i in range(len(objs) - 1, 0, -1):
                    follower = objs[i]
                    followee = objs[i - 1]
                    follower.move_anchor(followee.anchor)
                objs[0].move_by_offset(last_movement)                
            return True
        return False


class CollideLogic(object):
    def __init__(self, right_edge, top_edge, left_edge=0, bottom_edge=0, anchor_collide=False,
                 collide_combination_method="separate"):
        self.right_edge = right_edge
        self.top_edge = top_edge
        self.left_edge = left_edge
        self.bottom_edge = bottom_edge
        assert top_edge > bottom_edge, "Bottom edge must be smaller than top edge"
        assert right_edge > left_edge, "Left edge must be smaller than right edge"
        self.anchor_collide = anchor_collide  # if true, collide checks anchor, else checks vertices
        self.collide_combination_method = collide_combination_method  # options: edges, mean, separate
        self.separate_object_collisions = self.collide_combination_method == "separate"

    def get_min_max_vertices(self, objs):
        min_corners, max_corners = [], []
        if self.anchor_collide:
            for obj in objs:
                min_corners.append(obj.anchor)
                max_corners.append(obj.anchor)
        else:
            i = 0
            for obj in objs:
                min_corner, max_corner = obj.get_min_max_vertices()
                i += 1
                min_corners.append(min_corner)
                max_corners.append(max_corner)
        if self.collide_combination_method == "edges":
            self.min_corner = min_corners[0].copy()
            self.max_corner = max_corners[0].copy()
            for min_corner, max_corner in zip(min_corners, max_corners):
                self.min_corner.x = min(self.min_corner.x, min_corner.x)
                self.min_corner.y = min(self.min_corner.y, min_corner.y)
                self.max_corner.x = max(self.max_corner.x, max_corner.x)
                self.max_corner.y = max(self.max_corner.y, max_corner.y)
        elif self.collide_combination_method == "mean":
            self.min_corner = Vector2D(0, 0)
            self.max_corner = Vector2D(0, 0)
            for min_corner, max_corner in zip(min_corners, max_corners):
                self.min_corner += min_corner
                self.max_corner += max_corner
            self.min_corner /= len(min_corners)
            self.max_corner /= len(max_corners)
        else:
            self.min_corner = min_corners[0]
            self.max_corner = max_corners[0]

    def after_movement(self, objs, move_logic, dt):
        if not self.separate_object_collisions:
            self.get_min_max_vertices(objs)
        dt_factor_move = Vector2D(1, 1)
        dt_factor_rotate = 1
        for obj in objs:
            if self.separate_object_collisions:
                self.get_min_max_vertices([obj])
            if self.max_corner.x > self.right_edge:
                dt_factor_move.x = self.handle_object_collision(obj, move_logic, dt, diff=self.max_corner.x - self.right_edge, x_not_y=True)
            elif self.min_corner.x < self.left_edge:
                dt_factor_move.x = self.handle_object_collision(obj, move_logic, dt, diff=self.min_corner.x - self.left_edge, x_not_y=True)
            if self.max_corner.y > self.top_edge:
                dt_factor_move.y = self.handle_object_collision(obj, move_logic, dt, diff=self.max_corner.y - self.top_edge, x_not_y=False)
            elif self.min_corner.y < self.bottom_edge:
                dt_factor_move.y = self.handle_object_collision(obj, move_logic, dt, diff=self.min_corner.y - self.bottom_edge, x_not_y=False)
        return dt_factor_move, dt_factor_rotate
    
    def handle_object_collision(self, obj, move_logic, dt, diff, x_not_y=True):
        diff_vector = Vector2D(0, 0)
        if x_not_y:
            diff_vector.x = -diff
        else:
            diff_vector.y = -diff
        obj.move_by_offset(diff_vector)
        if x_not_y:
            move_logic.velocity.x = 0
        else:
            move_logic.velocity.y = 0
        return 1  # return dt_factor for x or y


class BounceLogic(CollideLogic):
    def handle_object_collision(self, obj, move_logic, dt, diff, x_not_y=True):
        d, v = self.calculate_bounce(obj, move_logic, dt, diff, x_not_y=x_not_y)
        diff_vector = Vector2D(0, 0)
        if x_not_y:
            diff_vector.x = d
        else:
            diff_vector.y = d
        obj.move_by_offset(diff_vector)
        if x_not_y:
            move_logic.velocity.x = v
        else:
            move_logic.velocity.y = v
        return 0
    
    def calculate_bounce(self, obj, move_logic, dt, diff, x_not_y):
        """For object, calculate distance and new velocity after bounce."""
        if x_not_y:
            a = move_logic.acceleration.x
            v = move_logic.velocity.x
            o = obj.move_total.x
        else:
            a = move_logic.acceleration.y
            v = move_logic.velocity.y
            o = obj.move_total.y
        # calculate times
        t0, t1 = self.solve_x(0.5 * a, v, diff - o)
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
    
    def solve_x(self, a, b, c):
        """Solve x for ax^2 + bx + c = 0."""
        if a == 0:
            return -c / b, -c / b
        sqrt_b2_4ac = math.sqrt(b * b - 4 * a * c)
        return (-b + sqrt_b2_4ac) / 2 / a, (-b - sqrt_b2_4ac) / 2 / a


class WarpLogic(CollideLogic):
    def __init__(self, *args, **kwargs):
        super(WarpLogic, self).__init__(*args, **kwargs)
        self.screen_width = self.right_edge - self.left_edge
        self.screen_height = self.top_edge - self.bottom_edge

    def handle_object_collision(self, obj, move_logic, dt, diff, x_not_y=True):
        diff_vector = Vector2D(0, 0)
        factor = -1 if diff > 0 else 1
        if x_not_y:
            translation = self.screen_width - self.max_corner.x + self.min_corner.x
            translation = math.ceil(abs(diff) / translation) * translation  # compensate when diff > translation
            diff_vector.x = factor * translation
        else:
            translation = self.screen_height - self.max_corner.y + self.min_corner.y
            translation = math.ceil(abs(diff) / translation) * translation  # compensate when diff > translation
            diff_vector.y = factor * translation
        obj.move_by_offset(diff_vector)
        return 1


class CollideLogicTetris(CollideLogic):
    def handle_object_collision(self, obj, move_logic, dt, diff, x_not_y=True):
        diff_vector = Vector2D(0, 0)
        if x_not_y:
            diff_vector.x = -diff
        else:
            diff_vector.y = -diff
        obj.move_by_offset(diff_vector)
        if x_not_y:
            move_logic.velocity.x = 0
        else:
            move_logic.velocity.y = 0
        return 1  # return dt_factor for x or y


class PeripheralsLogic(object):
    def __init__(self, increase_on_key=Vector2D(1, 1), absolute_increase=True, erase_used_keys=False):
        self.increase_on_key = increase_on_key if type(increase_on_key) is not list else Vector2D.set_from_list(increase_on_key)
        self.absolute_increase = absolute_increase
        self.erase_used_keys = erase_used_keys
        self.apply_increase_if_no_keys = False
        self.locked = False

    def handle_peripherals_input(self, objs, move_logic, dt, peripherals_input):
        has_changed = False
        if self.absolute_increase:
            keys = peripherals_input.keys_started
            if self.erase_used_keys:
                peripherals_input.reset_keys_started()
        else:
            keys = peripherals_input.keys_pressed
            if self.erase_used_keys:
                peripherals_input.reset_keys_pressed()
        if len(keys) > 0 or self.apply_increase_if_no_keys:
            increase = self.parse_keys(objs, dt, keys)
            if not self.locked:
                self.apply_increase(objs, move_logic, increase)
                has_changed = True
        return has_changed

    def parse_keys(self, objs, dt, keys):
        increase = Vector2D(0, 0)
        factor = 1 if self.absolute_increase else dt
        keys_used = ""
        for key in keys:
            if key == "L" and key not in keys_used:
                increase.x -= self.increase_on_key.x * factor
                keys_used += key
            elif key == "R":
                increase.x += self.increase_on_key.x * factor
                keys_used += key
            elif key == "D":
                increase.y -= self.increase_on_key.y * factor
                keys_used += key
            elif key == "U":
                increase.y += self.increase_on_key.y * factor
                keys_used += key
        return increase

    def apply_increase(self, objs, move_logic, increase):
        print("Increase applied: {}".format(increase))


class PeripheralsLogicVelocityIncrease(PeripheralsLogic):
    def apply_increase(self, objs, move_logic, increase):
        move_logic.velocity += increase


class PeripheralsLogicPositionIncrease(PeripheralsLogic):
    def apply_increase(self, objs, move_logic, increase):
        for obj in objs:
            obj.move_by_offset(increase)

class PeripheralsLogicOneDirection(PeripheralsLogic):
    def __init__(self, *args, direction="", allow_reverse=False, **kwargs):
        super(PeripheralsLogicOneDirection, self).__init__(*args, **kwargs)
        self.direction = direction
        self.prev_direction = self.direction
        self.allow_reverse = allow_reverse
        self.keys_next_update = ""
        self.apply_increase_if_no_keys = True

    def update_locked(self, objs):
        self.locked = False

    def parse_keys(self, objs, dt, keys):
        # update self.locked
        self.update_locked(objs)
        # get object direction (if locked, object direction is prev_direction)
        direction = self.direction if not self.locked else self.prev_direction
        # get valid directions to turn
        if direction in ["L", "R"]:
            valid_directions = "UD"
            if self.allow_reverse:
                valid_directions += "R" if direction == "L" else "L"
        elif direction in ["U", "D"]:
            valid_directions = "LR"
            if self.allow_reverse:
                valid_directions += "U" if direction == "D" else "D"
        else:
            valid_directions = "UDLR"
        # if locked, read keys that can be added to self.keys_next_update and exit
        if self.locked:
            for key in keys:
                if key not in valid_directions and key not in self.keys_next_update:
                    self.keys_next_update += key
            return None
        # if unlocked, record whether input keys are actions that can be done now (keys_used) or not
        keys_prev_update = "".join([c for c in self.keys_next_update if c in valid_directions])
        self.keys_next_update = ""
        keys_used = ""
        for key in keys_prev_update + keys:
            if key in self.keys_next_update or key in keys_used:
                continue
            if key not in valid_directions:
                self.keys_next_update += key
            else:
                keys_used += key
        # if no keys with valid actions chosen, ignore any next actions
        if len(keys_used) == 0:
            keys_used = self.direction
            self.keys_next_update = ""
        return self.get_increase_from_keys_used(keys_used)


    def get_increase_from_keys_used(self, keys_used):
        increase = Vector2D(0, 0)
        for key in keys_used:
            if key == "L":
                increase += Vector2D(-1, 0)
            elif key == "R":
                increase += Vector2D(1, 0)
            elif key == "D":
                increase += Vector2D(0, -1)
            elif key == "U":
                increase += Vector2D(0, 1)
        self.prev_direction = self.direction
        if len(keys_used) == 1 and not increase.is_zero():
            self.direction = key
        elif len(keys_used) == 0:
            self.direction = ""
        elif (increase.x != 0 and increase.y != 0) or increase.is_zero():
            increase = self.get_increase_from_keys_used(self.direction)
        elif increase.x < 0:
            self.direction = "L"
        elif increase.x > 0:
            self.direction = "R"
        elif increase.y < 0:
            self.direction = "D"
        elif increase.y > 0:
            self.direction = "U"
        else:
            self.direction = ""
        return increase

    def apply_increase(self, objs, move_logic, increase):
        move_logic.velocity = self.increase_on_key * increase


class PeripheralsLogicOneDirectionDiscrete(PeripheralsLogicOneDirection):
    def is_opposite_direction(self, direction):
        return ((direction == "L" and self.direction == "R") or
               (direction == "R" and self.direction == "L") or 
               (direction == "U" and self.direction == "D") or 
               (direction == "D" and self.direction == "U"))

    def update_locked(self, objs):
        """Unlock when all anchors are different to self.anchors_when_locked."""
        if self.locked == True:
            locked = False
            for obj, anchor_when_locked in zip(objs, self.anchors_when_locked):
                locked |= anchor_when_locked.same(obj.anchor)
            self.locked = locked

    def apply_increase(self, objs, move_logic, increase):
        if self.prev_direction != self.direction:
            move_logic.remaining_movement = abs(move_logic.remaining_movement) / move_logic.steps
            if not self.is_opposite_direction(self.prev_direction):
                move_logic.remaining_movement.shift()
            move_logic.remaining_movement = move_logic.remaining_movement * move_logic.steps * increase
            self.locked = True
            self.anchors_when_locked = [obj.anchor.copy() for obj in objs]
        super(PeripheralsLogicOneDirectionDiscrete, self).apply_increase(objs, move_logic, increase)


class PeripheralsLogicSnake(PeripheralsLogicOneDirectionDiscrete):
    def __init__(self, snake, *args, **kwargs):
        self.snake = snake
        super(PeripheralsLogicSnake, self).__init__(*args, **kwargs)


class PeripheralsLogicTetris(PeripheralsLogic):
    def __init__(self, *args, default_increase=Vector2D(0, 0), **kwargs):
        super(PeripheralsLogicTetris, self).__init__(*args, **kwargs)
        self.default_increase = default_increase if type(default_increase) is not list else Vector2D.set_from_list(default_increase)
        self.apply_increase_if_no_keys = True

    def parse_keys(self, objs, dt, keys):
        valid_keys = "LRUD"
        keys_used = ""
        for key in keys:
            if key in keys_used:
                continue
            if key in valid_keys:
                keys_used += key
        return self.get_increase_from_keys_used(keys_used)

    def get_increase_from_keys_used(self, keys_used):
        horizontal_increase = 0
        vertical_increase = 0
        rotate = False
        for key in keys_used:
            if key == "L":
                horizontal_increase += -1
            elif key == "R":
                horizontal_increase += 1
            elif key == "D":
                vertical_increase += -1
            elif key == "U":
                rotate = True
        return horizontal_increase, vertical_increase, rotate

    def apply_increase(self, objs, move_logic, increase):
        horizontal_increase, vertical_increase, rotate = increase
        vertical_increase = self.default_increase.y if vertical_increase == 0 else self.increase_on_key.y * vertical_increase
        horizontal_increase = self.default_increase.x if horizontal_increase == 0 else self.increase_on_key.x * horizontal_increase
        move_logic.velocity = Vector2D(horizontal_increase, vertical_increase)
        # if rotate:


class PeripheralsInput(object):
    def __init__(self):
        self.reset_keys_pressed()
        self.reset_keys_started()
        self.reset_keys_released()

    def reset_keys_started(self):
        self.keys_started = ""

    def reset_keys_pressed(self):
        self.keys_pressed = ""

    def reset_keys_released(self):
        self.keys_released = ""
    
    def __str__(self):
        return ("STARTED:  '{}'\n".format(self.keys_started) +
                "PRESSED:  '{}'\n".format(self.keys_pressed) + 
                "RELEASED: '{}'".format(self.keys_released))


class GameWindow(pyglet.window.Window):
    def __init__(self, objects=None, batches=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # setup draw
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        pyglet.gl.glClearColor(0, 0, 0, 1)
        # setup objects and batches
        objects = [] if objects is None else objects
        self.object_names = [o.name for o in objects]
        self.objects = {o.name: o for o in objects}
        self.batches = [] if batches is None else batches
        self.batches = [self.batches] if type(self.batches) is not list else self.batches
        # setup key handlers
        self.key_handler = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.key_handler)
        self.peripherals_input = PeripheralsInput()
    
    def add_object(self, new_object):
        """Add object to objects, or replace if name already exists."""
        self.objects[new_object.name] = new_object
    
    def remove_object(self, object_name):
        """Remove object by name."""
        if object_name in self.objects:
            del self.objects[object_name]
    
    def update(self, dt):
        # check keys being pressed now
        if self.key_handler[pyglet.window.key.LEFT]:
            self.peripherals_input.keys_pressed += "L"
        if self.key_handler[pyglet.window.key.RIGHT]:
            self.peripherals_input.keys_pressed += "R"
        if self.key_handler[pyglet.window.key.UP]:
            self.peripherals_input.keys_pressed += "U"
        if self.key_handler[pyglet.window.key.DOWN]:
            self.peripherals_input.keys_pressed += "D"
        # update objects
        for name in self.objects:
            if self.objects[name].has_peripherals_logic:
                self.objects[name].update(dt, self.peripherals_input)
            else:
                self.objects[name].update(dt)
        # reset keys
        self.peripherals_input.reset_keys_started()
        self.peripherals_input.reset_keys_pressed()
        self.peripherals_input.reset_keys_released()

    def on_draw(self):
        self.clear()
        # draw every refresh
        for name in self.object_names:
            self.objects[name].draw()
        for batch in self.batches:
            batch.draw()
    
    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.LEFT:
            self.peripherals_input.keys_started += "L"
        if symbol == pyglet.window.key.RIGHT:
            self.peripherals_input.keys_started += "R"
        if symbol == pyglet.window.key.UP:
            self.peripherals_input.keys_started += "U"
        if symbol == pyglet.window.key.DOWN:
            self.peripherals_input.keys_started += "D"
        if symbol == pyglet.window.key.ESCAPE:
            self.close()

    def on_key_release(self, symbol, modifiers):
        if symbol == pyglet.window.key.LEFT:
            self.peripherals_input.keys_released += "L"
        if symbol == pyglet.window.key.RIGHT:
            self.peripherals_input.keys_released += "R"
        if symbol == pyglet.window.key.UP:
            self.peripherals_input.keys_released += "U"
        if symbol == pyglet.window.key.DOWN:
            self.peripherals_input.keys_released += "D"


class Game(object):
    def __init__(self, w=20, h=20, px_w=20, px_h=20, title="My game", resizable=False, **kwargs):
        self.w = w
        self.h = h
        self.px_w = px_w
        self.px_h = px_h
        assert self.px_h == self.px_w
        self.refresh_raw_dimensions()

        batches = [pyglet.graphics.Batch(), pyglet.graphics.Batch()]
        batch_background = batches[0]
        batch_foreground = batches[1]

        self.food = [
            GameObject("food",
                       RegularPolygon([self.px_w * 10.5, self.px_h * 10.5], 4, [255, 0, 0], side=self.px_w, batch=batch_foreground))
        ]
        self.snake = [
            GameObject("snake0",
                       # [
                       #     RegularPolygon([self.px_w * 4.5, self.px_h * 4.5], 4, [255, 255, 0], side=self.px_w, batch=batch_background),
                       #     RegularPolygon([self.px_w * 5.5, self.px_h * 4.5], 4, [0, 255, 255], side=self.px_w, batch=batch_background),
                       #     RegularPolygon([self.px_w * 5.5, self.px_h * 5.5], 4, [0, 0, 255], side=self.px_w, batch=batch_background),
                       #     RegularPolygon([self.px_w * 6.5, self.px_h * 5.5], 4, [0, 255, 0], side=self.px_w, batch=batch_background)
                       # ],
                       [
                           RegularPolygon([self.px_w * 4.5, self.px_h * 4.5], 4, [0, 255, 0], side=self.px_w, batch=batch_background),
                           RegularPolygon([self.px_w * 3.5, self.px_h * 4.5], 4, [0, 255, 0], side=self.px_w, batch=batch_background),
                           RegularPolygon([self.px_w * 2.5, self.px_h * 4.5], 4, [0, 255, 0], side=self.px_w, batch=batch_background)
                       ],
                       DiscreteFollowMoveLogic(steps=[self.px_w, self.px_h]),
                       WarpLogic(right_edge=self.raw_w + 0.5 * self.px_w, top_edge=self.raw_h + 0.5 * self.px_h,
                                 left_edge=-0.5 * self.px_w, bottom_edge=-0.5 * self.px_h, anchor_collide=False),
                       PeripheralsLogicOneDirectionDiscrete(increase_on_key=[self.px_w * 4, self.px_h * 4], absolute_increase=True, allow_reverse=False, direction="R"))
        ]
        self.tetris = [
            GameObject("tetris",
                       [
                           RegularPolygon([self.px_w * 4.5, self.px_h * 4.5], 4, [255, 255, 0], side=self.px_w, batch=batch_background),
                           RegularPolygon([self.px_w * 5.5, self.px_h * 4.5], 4, [0, 255, 255], side=self.px_w, batch=batch_background),
                           RegularPolygon([self.px_w * 5.5, self.px_h * 5.5], 4, [0, 0, 255], side=self.px_w, batch=batch_background),
                           RegularPolygon([self.px_w * 6.5, self.px_h * 5.5], 4, [255, 0, 255], side=self.px_w, batch=batch_background)
                       ],
                       DiscreteMoveLogic(steps=[self.px_w, self.px_h]),
                       CollideLogic(right_edge=self.raw_w, top_edge=self.raw_h, anchor_collide=False, collide_combination_method="edges"),
                       PeripheralsLogicTetris(increase_on_key=[self.px_w * 12, self.px_h * 12], default_increase=[0, -self.px_h * 4], absolute_increase=False))
        ]
        self.objects = self.food + self.snake + self.tetris

        self.window = GameWindow(self.objects, batches, self.raw_w, self.raw_h, title, resizable, **kwargs)
        self.key_handler = pyglet.window.key.KeyStateHandler()
    
    def refresh_raw_dimensions(self):
        self.raw_w = self.w * self.px_w
        self.raw_h = self.h * self.px_h

    def update(self, dt):
        self.window.update(dt)


if __name__ == "__main__":
    # config = pyglet.gl.Config(double_buffer=False)
    game = Game(resizable=False, title="Tetris", h=22, w=10, px_w=40, px_h=40)
    pyglet.clock.schedule_interval(game.update, 1/120)
    pyglet.app.run()
