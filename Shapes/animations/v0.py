import pyglet
from pyglet import shapes
from pyglet.gl import GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
from pyglet.gl import GL_TRIANGLES, GL_LINES
from pyglet.graphics import Batch

import math


class _AdvancedShapeBase(pyglet.shapes._ShapeBase):
    """Base class for Advanced Shapes."""

    _rotation = 0
    _anchor_rotation_visible = False
    _anchor_rotation_circle = None
    _anchor_position_visible = False
    _anchor_position_circle = None
    _anchor_position_x = 0
    _anchor_position_y = 0
    _vertices = []
    _frozen_vertices = None
    _verbose = False  # used to print debug messages

    def __del__(self):
        super().__del__()
        if self._anchor_rotation_circle is not None:
            self._anchor_rotation_circle.__del__()
        if self._anchor_position_circle is not None:
            self._anchor_position_circle.__del__()

    def draw(self):
        super().draw()
        if self._anchor_rotation_circle is not None:
            self._anchor_rotation_circle.draw()
        if self._anchor_position_circle is not None:
            self._anchor_position_circle.draw()

    def delete(self):
        super().delete()
        if self._anchor_rotation_circle is not None:
            self._anchor_rotation_circle.delete()
        if self._anchor_position_circle is not None:
            self._anchor_position_circle.delete()

    def _update_anchor_position(self):
        if self._anchor_rotation_visible:
            if self._anchor_rotation_circle is None:
                self._anchor_rotation_circle = Circle(0, 0, 2, opacity=0, batch=self._batch)
                self._update_anchor_color()
            self._anchor_rotation_circle.position = (self._x + self._anchor_x - self._anchor_position_x,
                                                     self._y + self._anchor_y - self._anchor_position_y)
            self._anchor_rotation_circle.visible = True
        elif self._anchor_rotation_circle is not None:
            self._anchor_rotation_circle.visible = False
        if self._anchor_position_visible:
            if self._anchor_position_circle is None:
                self._anchor_position_circle = Circle(0, 0, 2, opacity=0, batch=self._batch)
                self._update_anchor_color()
            self._anchor_position_circle.position = (self._x, self._y)
            self._anchor_position_circle.visible = True
        elif self._anchor_position_circle is not None:
            self._anchor_position_circle.visible = False

    def _update_anchor_color(self):
        if self._anchor_rotation_circle is not None:
            self._anchor_rotation_circle._rgb = (255 - c for c in self._rgb)
            self._anchor_rotation_circle._opacity = self._opacity
            self._anchor_rotation_circle._update_color()
        if self._anchor_position_circle is not None:
            self._anchor_position_circle._rgb = (255 - c for c in self._rgb)
            self._anchor_position_circle._opacity = self._opacity
            self._anchor_position_circle._update_color()

    def _update_position(self):
        if not self._visible:
            self._vertices = (0,) * len(self._vertices)
        else:
            self._get_vertices()
            self._rotate_vertices()
            self._translate_vertices()
        self._vertex_list.vertices[:] = tuple(self._vertices)
        self._update_anchor_position()

    def _update_color(self):
        self._update_anchor_color()

    def _calculate_vertices(self):
        """Calculate vertices before rotation and translation. Requires filling list _vertices."""
        raise NotImplementedError

    def _get_vertices(self):
        if self._frozen_vertices is None:
            self._calculate_vertices()
        else:
            self._vertices = self._frozen_vertices.copy()

    def _rotate_vertices(self):
        if self._rotation % 360 != 0:
            rotation = math.radians(self._rotation)
            for i in range(0, len(self._vertices), 2):
                x, y = self._vertices[i] - self._anchor_x, self._vertices[i + 1] - self._anchor_y
                r = math.sqrt(x * x + y * y)
                if r == 0:  # dot in anchor, no need to rotate
                    continue
                angle = math.asin(y / r)
                if x < 0:
                    angle = math.radians(180) - angle
                angle += rotation
                self._vertices[i] = math.cos(angle) * r + self._anchor_x
                self._vertices[i + 1] = math.sin(angle) * r + self._anchor_y

    def _translate_vertices(self):
        for i in range(0, len(self._vertices), 2):
            self._vertices[i] += self._x - self._anchor_position_x
            self._vertices[i + 1] += self._y - self._anchor_position_y

    def freeze_rotation(self):
        """Store vertices after rotation and set rotation back to 0, so vertices can be rotated again from a different anchor point.

        When a shape is frozen, changing shape attributes (width, height, radius...) has no effect until shape is unfrozen.
        Only rotation, position and color changes will be displayed.
        """
        self._get_vertices()
        self._rotate_vertices()
        self._frozen_vertices = self._vertices.copy()
        self._rotation = 0
        self._anchor_x = 0
        self._anchor_y = 0
        self._update_position()

    def unfreeze_rotation(self):
        """Forget frozen vertices and set rotation back to 0."""
        self._frozen_vertices = None
        self._rotation = 0
        self._anchor_x = 0
        self._anchor_y = 0
        self._update_position()

    @property
    def anchor_visible(self):
        """True if anchor rotation point (center of rotation) is drawn. Same as self.anchor_rotation_visible.

        :type: bool
        """
        return self._anchor_rotation_visible

    @anchor_visible.setter
    def anchor_visible(self, value):
        self._anchor_rotation_visible = value
        self._update_position()

    @property
    def anchor_position_visible(self):
        """True if anchor position point (marks (x, y) position of shape) is drawn.

        :type: bool
        """
        return self._anchor_position_visible

    @anchor_position_visible.setter
    def anchor_position_visible(self, value):
        self._anchor_position_visible = value
        self._update_position()

    @property
    def anchor_rotation_visible(self):
        """True if anchor rotation point (center of rotation) is drawn. Same as self.anchor_visible.

        :type: bool
        """
        return self.anchor_visible

    @anchor_rotation_visible.setter
    def anchor_rotation_visible(self, value):
        self.anchor_visible = value

    @property
    def rotation(self):
        """Rotation of the shape in degrees.

        :type: int or float
        """
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self._update_position()

    @property
    def anchor_position_x(self):
        """The X coordinate of the anchor position point.

        :type: int or float
        """
        return self._anchor_position_x

    @anchor_position_x.setter
    def anchor_position_x(self, value):
        self._anchor_position_x = value
        self._update_position()

    @property
    def anchor_position_y(self):
        """The Y coordinate of the anchor position point.

        :type: int or float
        """
        return self._anchor_position_y

    @anchor_position_y.setter
    def anchor_position_y(self, value):
        self._anchor_position_y = value
        self._update_position()

    @property
    def anchor_position_position(self):
        """The (x, y) coordinates of the anchor position point, as a tuple.

        :Parameters:
            `x` : int or float
                X coordinate of the anchor position point.
            `y` : int or float
                Y coordinate of the anchor position point.
        """
        return self._anchor_position_x, self._anchor_position_y

    @anchor_position_position.setter
    def anchor_position_position(self, values):
        self._anchor_position_x, self._anchor_position_y = values
        self._update_position()

    @property
    def anchor_rotation_x(self):
        """The X coordinate of the anchor rotation point.

        :type: int or float
        """
        return self.anchor_x

    @anchor_rotation_x.setter
    def anchor_rotation_x(self, value):
        self.anchor_x = value

    @property
    def anchor_rotation_y(self):
        """The Y coordinate of the anchor rotation point.

        :type: int or float
        """
        return self.anchor_y

    @anchor_rotation_y.setter
    def anchor_rotation_y(self, value):
        self.anchor_y = value

    @property
    def anchor_rotation_position(self):
        """The (x, y) coordinates of the anchor rotation point, as a tuple.

        :Parameters:
            `x` : int or float
                X coordinate of the anchor rotation point.
            `y` : int or float
                Y coordinate of the anchor rotation point.
        """
        return self.anchor_position

    @anchor_rotation_position.setter
    def anchor_rotation_position(self, values):
        self.anchor_position = values


class Circle(_AdvancedShapeBase):
    def __init__(self, x, y, radius, rotation=0, angle=360, start_angle=0, segments=None, color=(255, 255, 255), opacity=255,
                 anchor_visible=False, batch=None, group=None):
        """Create a circle, or a sector if angle is less than 360.

        The circle's anchor point (x, y) defaults to the center of the circle.

        :Parameters:
            `x` : float
                X coordinate of the circle.
            `y` : float
                Y coordinate of the circle.
            `radius` : float
                The desired radius.
            `rotation` : float
                The desired rotation (clockwise). For a circle, the
                effect is invisible unless few segments are used.
            `segments` : int
                You can optionally specify how many distinct triangles
                the circle should be made from. If not specified it will
                be automatically calculated based using the formula:
                `max(14, int(radius / 1.25))`.
            `color` : (int, int, int)
                The RGB color of the circle, specified as a tuple of
                three ints in the range of 0-255.
            `opacity` : int
                The transparecy of the color, with a range of 0-255.
                Defaults to 255 (no transparency).
            `anchor_visible` : bool
                whether to show anchor point or not.
            `batch` : `~pyglet.graphics.Batch`
                Optional batch to add the circle to.
            `group` : `~pyglet.graphics.Group`
                Optional parent group of the circle.
        """
        self._x = x
        self._y = y
        self._angle = angle
        self._start_angle = start_angle
        self._radius = radius
        self._rotation = rotation
        self._segments = segments or max(14, int(radius / 1.25))
        self._rgb = color
        self._opacity = opacity
        self._anchor_rotation_visible = anchor_visible
        self._anchor_position_visible = anchor_visible

        self._batch = batch or Batch()
        self._group = pyglet.shapes._ShapeGroup(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, group)

        self._vertex_list = self._batch.add(self._segments * 3, GL_TRIANGLES, self._group, 'v2f', 'c4B')
        self._update_position()
        self._update_color()

    def _calculate_vertices(self):
        r = self._radius
        start_angle = math.radians(self._start_angle)
        tau_segs = math.radians(self._angle) / self._segments

        # calculate the outer points of the circle
        points = [[r * math.cos(i * tau_segs + start_angle),
                   r * math.sin(i * tau_segs + start_angle)] for i in range(self._segments)]

        # create a list of triangles from the points
        self._vertices = []
        for i, point in enumerate(points):
            self._vertices.extend([0, 0] + points[i - 1] + point)

    def _update_color(self):
        self._vertex_list.colors[:] = [*self._rgb, int(self._opacity)] * self._segments * 3
        super()._update_color()

    @property
    def radius(self):
        """The radius of the circle.

        :type: float
        """
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value
        self._update_position()

    @property
    def angle(self):
        """The angle of the sector in degrees (360 = full circle).

        :type: float
        """
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value
        self._update_position()

    @property
    def start_angle(self):
        """The start_angle of the circle ().

        :type: float
        """
        return self._start_angle

    @start_angle.setter
    def start_angle(self, value):
        self._start_angle = value
        self._update_position()


class Ellipse(_AdvancedShapeBase):
    def __init__(self, x, y, a, b, rotation=0, segments=None, color=(255, 255, 255), opacity=255,
                 anchor_visible=False, batch=None, group=None):
        """Create an ellipse.

        The ellipse's anchor point (x, y) defaults to the center of the ellipse.

        :Parameters:
            `x` : float
                X coordinate of the ellipse.
            `y` : float
                Y coordinate of the ellipse.
            `a` : float
                Semi-major axes of the ellipse.
            `b`: float
                Semi-minor axes of the ellipse.
            `color` : (int, int, int)
                The RGB color of the ellipse. specify as a tuple of
                three ints in the range of 0~255.
            `batch` : `~pyglet.graphics.Batch`
                Optional batch to add the circle to.
            `group` : `~pyglet.graphics.Group`
                Optional parent group of the circle.
        """
        self._x = x
        self._y = y
        self._a = a
        self._b = b
        self._rotation = rotation
        self._segments = segments or max(14, int(max(a, b) / 1.25))
        self._rgb = color
        self._opacity = opacity

        self._batch = batch or Batch()
        self._group = pyglet.shapes._ShapeGroup(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, group)

        self._vertex_list = self._batch.add(self._segments * 3, GL_TRIANGLES, self._group, 'v2f', 'c4B')
        self._update_position()
        self._update_color()

    def _calculate_vertices(self):
        tau_segs = math.pi * 2 / self._segments

        # calculate the outer points of the ellipse
        points = [[self._a * math.cos(i * tau_segs),
                   self._b * math.sin(i * tau_segs)] for i in range(self._segments)]

        # create a list of lines from the points
        self._vertices = []
        for i, point in enumerate(points):
            self._vertices.extend([0, 0] + points[i - 1] + point)

    def _update_color(self):
        self._vertex_list.colors[:] = [*self._rgb, int(self._opacity)] * self._segments * 3
        super()._update_color()

    @property
    def a(self):
        """The semi-major axes of the ellipse.

        :type: float
        """
        return self._a

    @a.setter
    def a(self, value):
        self._a = value
        self._update_position()

    @property
    def b(self):
        """The semi-minor axes of the ellipse.

        :type: float
        """
        return self._b

    @b.setter
    def b(self, value):
        self._b = value
        self._update_position()


class Rectangle(_AdvancedShapeBase):
    def __init__(self, x, y, width, height, rotation=0, color=(255, 255, 255), opacity=255,
                 anchor_visible=False, batch=None, group=None):
        """Create a rectangle or square.

        The rectangle's anchor point defaults to the (x, y) coordinates,
        which are in the center of the rectangle.

        :Parameters:
            `x` : float
                The X coordinate of the rectangle.
            `y` : float
                The Y coordinate of the rectangle.
            `width` : float
                The width of the rectangle.
            `height` : float
                The height of the rectangle.
            `rotation` : float
                The desired rotation (clockwise).
            `color` : (int, int, int)
                The RGB color of the rectangle, specified as
                a tuple of three ints in the range of 0-255.
            `opacity` : int
                The transparecy of the color, with a range of 0-255.
                Defaults to 255 (no transparency).
            `anchor_visible` : bool
                whether to show anchor point or not.
            `batch` : `~pyglet.graphics.Batch`
                Optional batch to add the rectangle to.
            `group` : `~pyglet.graphics.Group`
                Optional parent group of the rectangle.
        """
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._rotation = rotation
        self._rgb = color
        self._opacity = opacity
        self._anchor_rotation_visible = anchor_visible
        self._anchor_position_visible = anchor_visible

        self._batch = batch or Batch()
        self._group = pyglet.shapes._ShapeGroup(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, group)
        self._vertex_list = self._batch.add(6, GL_TRIANGLES, self._group, 'v2f', 'c4B')
        self._update_position()
        self._update_color()

    def _calculate_vertices(self):
        x1 = -self._width / 2
        x2 = self._width / 2
        y1 = -self._height / 2
        y2 = self._height / 2
        self._vertices = [x1, y1, x2, y1, x2, y2, x1, y1, x1, y2, x2, y2]

    def _update_color(self):
        self._vertex_list.colors[:] = [*self._rgb, int(self._opacity)] * 6
        super()._update_color()

    @property
    def width(self):
        """The width of the rectangle.

        :type: float
        """
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        self._update_position()

    @property
    def height(self):
        """The height of the rectangle.

        :type: float
        """
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        self._update_position()


class Triangle(_AdvancedShapeBase):
    def __init__(self, x, y, x2, y2, x3, y3, rotation=0, color=(255, 255, 255), opacity=255,
                 anchor_visible=False, relative_points=False, batch=None, group=None):
        """Create a triangle.

        The triangle's anchor point defaults to the first vertex point.

        :Parameters:
            `x` : float
                The first X coordinate of the triangle.
            `y` : float
                The first Y coordinate of the triangle.
            `x2` : float
                The second X coordinate of the triangle.
            `y2` : float
                The second Y coordinate of the triangle.
            `x3` : float
                The third X coordinate of the triangle.
            `y3` : float
                The third Y coordinate of the triangle.
            `rotation` : float
                The desired rotation (clockwise).
            `color` : (int, int, int)
                The RGB color of the triangle, specified as
                a tuple of three ints in the range of 0-255.
            `opacity` : int
                The transparecy of the color, with a range of 0-255.
                Defaults to 255 (no transparency).
            `anchor_visible` : bool
                whether to show anchor point or not.
            `relative_points` : bool
                if True, (x2, y3) and (x3, y3) values are read as an
                offset from (x, y). Else, read as absolute coordinates.
            `batch` : `~pyglet.graphics.Batch`
                Optional batch to add the triangle to.
            `group` : `~pyglet.graphics.Group`
                Optional parent group of the triangle.
        """
        self._x = x
        self._y = y
        self._x2 = x2
        self._y2 = y2
        self._x3 = x3
        self._y3 = y3
        if not relative_points:
            self._x2 -= self._x
            self._y2 -= self._y
            self._x3 -= self._x
            self._y3 -= self._y
        self._rotation = rotation
        self._rgb = color
        self._opacity = opacity
        self._anchor_rotation_visible = anchor_visible
        self._anchor_position_visible = anchor_visible

        self._batch = batch or Batch()
        self._group = pyglet.shapes._ShapeGroup(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, group)
        self._vertex_list = self._batch.add(3, GL_TRIANGLES, self._group, 'v2f', 'c4B')
        self._update_position()
        self._update_color()

    def _calculate_vertices(self):
        self._vertices = [0, 0, self._x2, self._y2, self._x3, self._y3]

    def _update_color(self):
        self._vertex_list.colors[:] = [*self._rgb, int(self._opacity)] * 3
        super()._update_color()

    def set_vertices(self, x1=None, y1=None, x2=None, y2=None, x3=None, y3=None, relative_points=False):
        """Update any vertices in the triangle. If relative_points, (x2, y2) and (x3, y3) are an offset of (x, y)."""
        self._x = x1 if x1 is not None else self._x
        self._y = y1 if y1 is not None else self._y
        offset_x = self._x if not relative_points else 0
        offset_y = self._y if not relative_points else 0
        self._x2 = x2 - offset_x if x2 is not None else self._x2
        self._y2 = y2 - offset_y if y2 is not None else self._y2
        self._x3 = x3 - offset_x if x3 is not None else self._x3
        self._y3 = y3 - offset_y if y3 is not None else self._y3
        self._update_position()

    @property
    def x1(self):
        """First X coordinate of the shape. Same as self.x.

        :type: int or float
        """
        return self._x

    @x1.setter
    def x1(self, value):
        self._x = value
        self._update_position()

    @property
    def x2(self):
        """Second X coordinate of the shape.

        :type: int or float
        """
        return self._x2

    @x2.setter
    def x2(self, value):
        self._x2 = value
        self._update_position()

    @property
    def y2(self):
        """Second Y coordinate of the shape.

        :type: int or float
        """
        return self._y2

    @y2.setter
    def y2(self, value):
        self._y2 = value
        self._update_position()

    @property
    def x3(self):
        """Third X coordinate of the shape.

        :type: int or float
        """
        return self._x3

    @x3.setter
    def x3(self, value):
        self._x3 = value
        self._update_position()

    @property
    def y3(self):
        """Third Y coordinate of the shape.

        :type: int or float
        """
        return self._y3

    @y3.setter
    def y3(self, value):
        self._y3 = value
        self._update_position()

    @property
    def position(self):
        """The (x, y, x2, y2, x3, y3) coordinates of the triangle, as a tuple.

        :Parameters:
            `x` : int or float
                X coordinate of the triangle.
            `y` : int or float
                Y coordinate of the triangle.
            `x2` : int or float
                X2 coordinate of the triangle.
            `y2` : int or float
                Y2 coordinate of the triangle.
            `x3` : int or float
                X3 coordinate of the triangle.
            `y3` : int or float
                Y3 coordinate of the triangle.
        """
        self.set_vertices()
        return self._x, self._y, self._x2 + self._x, self._y2 + self._y, self._x3 + self._x, self._y3 + self._y

    @position.setter
    def position(self, values):
        x, y, x2, y2, x3, y3 = values
        self.set_vertices(x, y, x2, y2, x3, y3, relative_points=False)


if __name__ == "__main__":
    import time
    class EventHandler:
        def __init__(self, shape, speed=10):
            self.state = None
            self.last_trigger = time.time()
            self.speed = speed
            self.speed_incr = 1
            self.shape = shape
            self._colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255), (0, 0, 0)]
            self.color_idx = 0
            self.border_color_idx = -1

        def on_text(self, text):
            t = time.time()
            if self.last_trigger is not None and t - self.last_trigger < 0.0:
                return
            self.last_trigger = t
            if text in ["+", "=", "-", "_"]:
                factor = -1 if text in ["-", "_"] else 1
                if self.state == ".":
                    self.speed_incr += factor
                    print("Speed Increment:", self.speed_incr)
                if self.state == ",":
                    self.speed += self.speed_incr * factor
                    print("Speed:", self.speed)
                if self.state == "w":
                    try:
                        self.shape.width += self.speed * factor
                        print("Width:", self.shape.width)
                    except AttributeError:
                        print("Width:", None)
                if self.state == "h":
                    try:
                        self.shape.height += self.speed * factor
                        print("Height:", self.shape.height)
                    except AttributeError:
                        print("Height:", None)
                if self.state == "r":
                    try:
                        self.shape.rotation += self.speed * factor
                        print("Rotation:", self.shape.rotation)
                    except AttributeError:
                        print("Rotation:", None)
                if self.state == "R":
                    try:
                        self.shape.radius += self.speed * factor
                        print("Radius:", self.shape.radius)
                    except AttributeError:
                        print("Radius:", None)
                if self.state == "f":
                    self.shape.freeze_rotation()
                    print("Rotation freeze")
                if self.state == "F":
                    self.shape.unfreeze_rotation()
                    print("Rotation unfreeze")
                if self.state == "e":
                    try:
                        self.shape.a += self.speed * factor
                        print("A:", self.shape.a)
                    except AttributeError:
                        print("A:", None)
                if self.state == "E":
                    try:
                        self.shape.b += self.speed * factor
                        print("B:", self.shape.b)
                    except AttributeError:
                        print("B:", None)
                if self.state == "a":
                    try:
                        self.shape.angle += self.speed * factor
                        print("Angle:", self.shape.angle)
                    except AttributeError:
                        print("Angle:", None)
                if self.state == "A":
                    try:
                        self.shape.start_angle += self.speed * factor
                        print("Start Angle:", self.shape.start_angle)
                    except AttributeError:
                        print("Start Angle:", None)
                if self.state == "n":
                    self.shape.anchor_rotation_visible = not self.shape.anchor_rotation_visible
                    print("Anchor Rotation Visible:", self.shape.anchor_rotation_visible)
                if self.state == "N":
                    self.shape.anchor_position_visible = not self.shape.anchor_position_visible
                    print("Anchor Position Visible:", self.shape.anchor_position_visible)
                if self.state == "b":
                    try:
                        self.shape.border += self.speed * factor
                        print("Border:", self.shape.border)
                    except AttributeError:
                        print("Border:", None)
                if self.state == "B":
                    self.border_color_idx = (self.border_color_idx + factor) % len(self._colors)
                    try:
                        self.shape.border_color  # will fail if property does not exist
                        self.shape.border_color = self._colors[self.border_color_idx]
                        print("Border Color:", self.shape.border_color)
                    except AttributeError:
                        print("Border Color:", None)
                if self.state == "C":
                    try:
                        self.shape.closed = not self.shape.closed
                        print("Closed:", self.shape.closed)
                    except AttributeError:
                        print("Closed:", None)
                if self.state == "x":
                    self.shape.x += self.speed * factor
                    print("X:", self.shape.x)
                if self.state == "y":
                    self.shape.y += self.speed * factor
                    print("Y:", self.shape.y)
                if self.state == "X":
                    self.shape.anchor_rotation_x += self.speed * factor
                    print("Anchor Rotation X:", self.shape.anchor_rotation_x)
                if self.state == "Y":
                    self.shape.anchor_rotation_y += self.speed * factor
                    print("Anchor Rotation Y:", self.shape.anchor_rotation_y)
                if self.state == "K":
                    self.shape.anchor_position_x += self.speed * factor
                    print("Anchor Position X:", self.shape.anchor_position_x)
                if self.state == "L":
                    self.shape.anchor_position_y += self.speed * factor
                    print("Anchor Position Y:", self.shape.anchor_position_y)
                if self.state.upper() == "O":
                    self.shape.opacity += self.speed * factor
                    self.shape.opacity = min(max(self.shape.opacity, 0), 255)
                    print("Opacity:", self.shape.opacity)
                if self.state == "c":
                    self.color_idx = (self.color_idx + factor) % len(self._colors)
                    self.shape.color = self._colors[self.color_idx]
                    print("Color:", self.shape.color)
            elif text.upper() in ["Q"]:
                self.state = None
                print("State:", None)
            elif text.upper() in ["I"]:
                print("Speed Increment:", self.speed_incr)
                print("Speed:", self.speed)
                print("State:", self.state)
                print("X:", self.shape.x)
                print("Y:", self.shape.y)
                print("Anchor Rotation X:", self.shape.anchor_rotation_x)
                print("Anchor Rotation Y:", self.shape.anchor_rotation_y)
                print("Anchor Position X:", self.shape.anchor_position_x)
                print("Anchor Position Y:", self.shape.anchor_position_y)
                try:
                    print("Width:", self.shape.width)
                except AttributeError:
                    pass
                try:
                    print("Height:", self.shape.height)
                except AttributeError:
                    pass
                try:
                    print("Rotation:", self.shape.rotation)
                except AttributeError:
                    pass
                try:
                    print("Radius:", self.shape.radius)
                except AttributeError:
                    pass
                try:
                    print("Angle:", self.shape.angle)
                except AttributeError:
                    pass
                try:
                    print("Start Angle:", self.shape.start_angle)
                except AttributeError:
                    pass
                print("Color:", self.shape.color)
                print("Opacity:", self.shape.opacity)
                try:
                    print("Border:", self.shape.border)
                except AttributeError:
                    print("Border:", None)
                try:
                    print("Border Color:", self.shape.border_color)
                except AttributeError:
                    print("Border Color:", None)
                try:
                    print("Closed:", self.shape.closed)
                except AttributeError:
                    print("Closed:", None)
            else:
                self.state = text
                print("State:", self.state)

    window = pyglet.window.Window(1000, 1000, caption="option")
    batch = pyglet.graphics.Batch()
    background = pyglet.shapes.Rectangle(0, 0, window.width, window.height, color=(0, 0, 0), batch=batch)
    color_body = (255, 0, 0)
    color_line = (255, 255, 0)
    middle_x, middle_y = window.width / 2, window.height / 2
    shape = Circle(window.width / 2, window.height / 2, 400, segments=6, angle=0, color=color_body, batch=batch)
    # shape = Ellipse(window.width / 2, window.height / 2, 100, 150, segments=12, color=color_body, batch=batch)
    # shape = Rectangle(window.width / 2, window.height / 2, 100, 200, color=color_body, batch=batch)
    # shape = Triangle(middle_x, middle_y, middle_x + 100, middle_y + 200, middle_x + 300, middle_y - 100, color=color_body, batch=batch)
    shape._verbose = True
    handler = EventHandler(shape)
    window.push_handlers(handler)

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

    def update(dt):
        shape.angle += dt * 160
        a = shape.angle % 2160
        g = a * 255 / 1080 if a < 1080 else (2160 - a) * 255 / 1080
        c = shape.color
        shape.color = (c[0], g, c[2])

    pyglet.clock.schedule_interval(update, 1 / 120.0)
    pyglet.app.run()
