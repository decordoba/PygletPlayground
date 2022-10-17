import pyglet
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
        """Calculate vertices before rotation and translation and save them into _vertices (i.e. [x1, y1, x2, y2...])."""
        raise NotImplementedError

    def _get_consecutive_outer_vertices(self):
        """Return a list with the vertices in order that mark the boundary of the polygon (i.e. [x1, y1, x2, y2...])."""
        raise NotImplementedError

    def is_position_inside_shape(self, x, y):
        """Return true if point (x, y) is inside shape (including edge)."""
        points = self._get_consecutive_outer_vertices()
        edges_crossed = 0
        vertices_crossed = set()
        for i in range(0, len(points), 2):
            x1, y1 = points[i - 2, i - 1]
            x2, y2 = points[i, i + 1]
            if (x > x1 and x > x2) or (y1 < y and y2 < y) or (y1 > y and y2 > y):  # remove dots higher, lower or right of segment's box
                pass
            elif (x < x1 and x < x2):  # dot is to the left of segment's box
                if y1 != y and y2 != y:  # y1 and y2 are above and below dot
                    edges_crossed += 1
                elif y1 == y and y2 != y:  # look into vertices crossed, only count them once
                    if (x1, y1) not in vertices_crossed:  # ignore already counted vertices
                        edges_crossed += 1
                        vertices_crossed.add((x1, y1))
                elif y2 == y and y1 != y:  # look into vertices crossed, only count them once
                    if (x2, y2) not in vertices_crossed:  # ignore already counted vertices
                        edges_crossed += 1
                        vertices_crossed.add((x2, y2))
                else:
            else:  # dot is in segment's box, we need to check with math
                if x1 == x2:
                    pass
                m = (y1 - y2) / (x2 - x1)
                n = y1 - m * x1
                x_intersection = (y - n) / m
                if (y - n) / m > x:
                    edges_crossed += 1
                elif
                
        return edges_crossed % 2 == 1

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
                r = math.hypot(x, y)
                if r == 0:  # dot in anchor, no need to rotate
                    continue
                angle = math.atan2(y, x) + rotation
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
                 anchor_visible=False, closed=False, batch=None, group=None):
        """Create a circle, or a sector if angle is less than 360.

        The circle's anchor point (x, y) defaults to the center of the circle.

        :Parameters:
            `x` : float
                X coordinate of the circle.
            `y` : float
                Y coordinate of the circle.
            `radius` : float
                The desired radius.
            `angle` : float
                The angle of the sector, in degrees. Defaults to 360,
                a full circle.
            `start_angle` : float
                The start angle of the sector, in degrees. Defaults to 0.
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
                Whether to show anchor points or not.
            `closed` : bool
                If True, the ends of the sector will be connected.
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
        self._segments = segments or max(14, int(radius / 1.25))
        self._closed = closed
        self._rotation = rotation
        self._rgb = color
        self._opacity = opacity
        self._anchor_rotation_visible = anchor_visible
        self._anchor_position_visible = anchor_visible

        self._batch = batch or Batch()
        self._group = pyglet.shapes._ShapeGroup(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, group)

        self._vertex_list = self._batch.add((self._segments + 1) * 3, GL_TRIANGLES, self._group, 'v2f', 'c4B')
        self._update_position()
        self._update_color()

    def _calculate_vertices(self):
        r = self._radius
        start_angle = math.radians(self._start_angle)
        tau_segs = math.radians(self._angle) / self._segments

        # calculate the outer points of the circle
        # the extra segment (+1) is to close sector if needed
        points = [[r * math.cos(i * tau_segs + start_angle),
                   r * math.sin(i * tau_segs + start_angle)] for i in range(self._segments + 1)]

        # create a list of triangles from the points
        self._vertices = []
        for i in range(len(points) - 1):
            self._vertices.extend(points[i] + [0, 0] + points[i + 1])
        if self._closed:
            self._vertices.extend(points[-1] + [0, 0] + points[0])
        else:
            self._vertices.extend(points[-1] + points[-1] + points[-1])

    def _update_color(self):
        self._vertex_list.colors[:] = [*self._rgb, int(self._opacity)] * (self._segments + 1) * 3
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
        """The start_angle of the sector (0 = right, 90 = top, etc.).

        :type: float
        """
        return self._start_angle

    @start_angle.setter
    def start_angle(self, value):
        self._start_angle = value
        self._update_position()

    @property
    def closed(self):
        """Whether the sector is closed or not.
        This will not be noticable in a full circle.

        :type: bool
        """
        return self._closed

    @closed.setter
    def closed(self, value):
        self._closed = value
        self._update_position()


class RegularPolygon(Circle):
    def __init__(self, x, y, num_sides, side=None, radius=None, rotation=0, angle=360, start_angle=0,
                 color=(255, 255, 255), opacity=255, anchor_visible=False, closed=False, batch=None, group=None):
        """Create a regular polygon, or a sector if angle is less than 360.

        The polygon's anchor point (x, y) defaults to the center of the polygon.

        :Parameters:
            `x` : float
                X coordinate of the circle.
            `y` : float
                Y coordinate of the circle.
            `num_sides` : int
                The number of sides of the polygon.
            `side` : float
                The size of the side. If not specified, use radius.
            `radius` : float
                The radius of the polygon. If side is passed, it is ignored.
            `angle` : float
                The angle of the sector, in degrees. Defaults to 360,
                a full circle.
            `start_angle` : float
                The start angle of the sector, in degrees. Defaults to 0.
            `rotation` : float
                The desired rotation (clockwise). For a circle, the
                effect is invisible unless few segments are used.
            `color` : (int, int, int)
                The RGB color of the circle, specified as a tuple of
                three ints in the range of 0-255.
            `opacity` : int
                The transparecy of the color, with a range of 0-255.
                Defaults to 255 (no transparency).
            `anchor_visible` : bool
                Whether to show anchor points or not.
            `closed` : bool
                If True, the ends of the sector will be connected.
            `batch` : `~pyglet.graphics.Batch`
                Optional batch to add the circle to.
            `group` : `~pyglet.graphics.Group`
                Optional parent group of the circle.
        """
        assert side is not None or radius is not None, "Either side or radius are required"
        factor = math.sin(math.radians(360) / num_sides / 2)
        radius = side / 2 / factor if side is not None else radius
        self._side = radius * factor * 2 if side is None else side
        super().__init__(x, y, radius, rotation=rotation, angle=angle, start_angle=start_angle, segments=num_sides,
                         color=color, opacity=opacity, anchor_visible=anchor_visible, closed=closed, batch=batch, group=group)

    def _calculate_vertices(self):
        self._radius = self._side / 2 / math.sin(math.radians(360) / self._segments / 2)
        super()._calculate_vertices()

    @property
    def side(self):
        """The side of the polygon.

        :type: float
        """
        return self._side

    @side.setter
    def side(self, value):
        self._side = value
        self._update_position()


    @property
    def radius(self):
        """The radius of the polygon.

        :type: float
        """
        return self._radius

    @radius.setter
    def radius(self, value):
        self._side = value * 2 * math.sin(math.radians(360) / self._segments / 2)
        self._update_position()


class Ellipse(_AdvancedShapeBase):
    def __init__(self, x, y, a, b, angle=360, start_angle=0, rotation=0, segments=None, color=(255, 255, 255), opacity=255,
                 anchor_visible=False, closed=False, batch=None, group=None):
        """Create an ellipse, or an ellipse sector if angle is less than 360.

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
            `angle` : float
                The angle of the sector, in degrees. Defaults to 360,
                a full circle.
            `start_angle` : float
                The start angle of the sector, in degrees. Defaults to 0.
            `rotation` : float
                The desired rotation (clockwise).
            `segments` : int
                You can optionally specify how many distinct triangles
                the ellipse should be made from. If not specified it will
                be automatically calculated based using the formula:
                `max(14, int(max(a, b) / 1.25))`.
            `color` : (int, int, int)
                The RGB color of the ellipse, specified as a tuple of
                three ints in the range of 0-255.
            `opacity` : int
                The transparecy of the color, with a range of 0-255.
                Defaults to 255 (no transparency).
            `anchor_visible` : bool
                Whether to show anchor points or not.
            `closed` : bool
                If True, the ends of the sector will be connected.
            `batch` : `~pyglet.graphics.Batch`
                Optional batch to add the circle to.
            `group` : `~pyglet.graphics.Group`
                Optional parent group of the circle.
        """
        self._x = x
        self._y = y
        self._angle = angle
        self._start_angle = start_angle
        self._a = a
        self._b = b
        self._segments = segments or max(14, int(max(a, b) / 1.25))
        self._closed = closed
        self._rotation = rotation
        self._rgb = color
        self._opacity = opacity
        self._anchor_rotation_visible = anchor_visible
        self._anchor_position_visible = anchor_visible

        self._batch = batch or Batch()
        self._group = pyglet.shapes._ShapeGroup(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, group)

        self._vertex_list = self._batch.add((self._segments + 1) * 3, GL_TRIANGLES, self._group, 'v2f', 'c4B')
        self._update_position()
        self._update_color()

    def _calculate_vertices(self):
        start_angle = math.radians(self._start_angle)
        tau_segs = math.radians(self._angle) / self._segments

        # calculate the outer points of the ellipse
        # the extra segment (+1) is to close sector if needed
        points = [[self._a * math.cos(i * tau_segs + start_angle),
                   self._b * math.sin(i * tau_segs + start_angle)] for i in range(self._segments + 1)]

        # create a list of triangles from the points
        self._vertices = []
        for i in range(len(points) - 1):
            self._vertices.extend(points[i] + [0, 0] + points[i + 1])
        if self._closed:
            self._vertices.extend(points[-1] + [0, 0] + points[0])
        else:
            self._vertices.extend(points[-1] + points[-1] + points[-1])

    def _update_color(self):
        self._vertex_list.colors[:] = [*self._rgb, int(self._opacity)] * (self._segments + 1) * 3
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

    @property
    def angle(self):
        """The angle of the sector in degrees (360 = full ellipse).

        :type: float
        """
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value
        self._update_position()

    @property
    def start_angle(self):
        """The start_angle of the sector (0 = right, 90 = top, etc.).

        :type: float
        """
        return self._start_angle

    @start_angle.setter
    def start_angle(self, value):
        self._start_angle = value
        self._update_position()

    @property
    def closed(self):
        """Whether the sector is closed or not.
        This will not be noticable in a full ellipse.

        :type: bool
        """
        return self._closed

    @closed.setter
    def closed(self, value):
        self._closed = value
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
                Whether to show anchor points or not.
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
                Whether to show anchor points or not.
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


class Star(_AdvancedShapeBase):
    def __init__(self, x, y, outer_radius, inner_radius, num_spikes, rotation=0, angle=360, start_angle=0,
                 color=(255, 255, 255), opacity=255, anchor_visible=False, closed=False, outer_first=True, batch=None, group=None):
        """Create a star, or a star sector.

        The star's anchor point (x, y) defaults to the center of the star.

        :Parameters:
            `x` : float
                The X coordinate of the star.
            `y` : float
                The Y coordinate of the star.
            `outer_radius` : float
                The desired outer radius of the star.
            `inner_radius` : float
                The desired inner radius of the star.
            `num_spikes` : float
                The desired number of spikes of the star.
            `angle` : float
                The angle of the sector, in degrees. Defaults to 360,
                a full circle.
            `start_angle` : float
                The start angle of the sector, in degrees. Defaults to 0.
            `rotation` : float
                The desired rotation (clockwise).
            `color` : (int, int, int)
                The RGB color of the star, specified as a tuple of
                three ints in the range of 0-255.
            `opacity` : int
                The transparecy of the color, with a range of 0-255.
                Defaults to 255 (no transparency).
            `anchor_visible` : bool
                Whether to show anchor points or not.
            `closed` : bool
                If True, the ends of the sector will be connected.
            `outer_first` : bool
                If True, the sector breaks in a point, else it breaks in the angle.
            `batch` : `~pyglet.graphics.Batch`
                Optional batch to add the star to.
            `group` : `~pyglet.graphics.Group`
                Optional parent group of the star.
        """
        self._x = x
        self._y = y
        self._angle = angle
        self._start_angle = start_angle
        self._outer_radius = outer_radius
        self._inner_radius = inner_radius
        self._num_spikes = num_spikes
        self._closed = closed
        self._outer_first = outer_first
        self._rotation = rotation
        self._rgb = color
        self._opacity = opacity
        self._anchor_rotation_visible = anchor_visible
        self._anchor_position_visible = anchor_visible

        self._batch = batch or Batch()
        self._group = pyglet.shapes._ShapeGroup(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, group)

        self._vertex_list = self._batch.add(int((self._num_spikes + 0.5) * 6), GL_TRIANGLES, self._group, 'v2f', 'c4B')
        self._update_position()
        self._update_color()

    def _calculate_vertices(self):
        r1 = self._outer_radius if self._outer_first else self._inner_radius
        r2 = self._inner_radius if self._outer_first else self._outer_radius

        # get angle covered by each line (= half a spike)
        d_theta = math.radians(self._angle) / self._num_spikes / 2
        start_angle = math.radians(self._start_angle)

        # calculate alternating points on inner and outer circles
        points = []
        for i in range(self._num_spikes):
            points.append([r1 * math.cos(2 * i * d_theta + start_angle), r1 * math.sin(2 * i * d_theta + start_angle)])
            points.append([r2 * math.cos((2 * i + 1) * d_theta + start_angle), r2 * math.sin((2 * i + 1) * d_theta + start_angle)])
        points.append([r1 * math.cos(2 * self._num_spikes * d_theta + start_angle), r1 * math.sin(2 * self._num_spikes * d_theta + start_angle)])

        # create a list of triangles from the points
        self._vertices = []
        for i in range(len(points) - 1):
            self._vertices.extend(points[i] + [0, 0] + points[i + 1])
        if self._closed:
            self._vertices.extend(points[-1] + [0, 0] + points[0])
        else:
            self._vertices.extend(points[-1] + points[-1] + points[-1])

    def _update_color(self):
        self._vertex_list.colors[:] = [*self._rgb, int(self._opacity)] * int((self._num_spikes + 0.5) * 6)
        super()._update_color()

    @property
    def outer_radius(self):
        """The outer radius of the star."""
        return self._outer_radius

    @outer_radius.setter
    def outer_radius(self, value):
        self._outer_radius = value
        self._update_position()

    @property
    def inner_radius(self):
        """The inner radius of the star."""
        return self._inner_radius

    @inner_radius.setter
    def inner_radius(self, value):
        self._inner_radius = value
        self._update_position()

    @property
    def num_spikes(self):
        """Number of spikes of the star."""
        return self._num_spikes

    @num_spikes.setter
    def num_spikes(self, value):
        self._num_spikes = value
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
        """The start_angle of the sector (0 = right, 90 = top, etc.).

        :type: float
        """
        return self._start_angle

    @start_angle.setter
    def start_angle(self, value):
        self._start_angle = value
        self._update_position()

    @property
    def closed(self):
        """Whether the sector is closed or not.
        This will not be noticable in a full circle.

        :type: bool
        """
        return self._closed

    @closed.setter
    def closed(self, value):
        self._closed = value
        self._update_position()


class Line(_AdvancedShapeBase):
    def __init__(self, x, y, x2, y2, width=1, rotation=0, color=(255, 255, 255), opacity=255,
                 anchor_visible=False, relative_points=False, center_line=True, batch=None, group=None):
        """Create a line.

        The line's anchor point defaults to the center of the line's width
        or the center of one of the sides (depending on center_line).

        :Parameters:
            `x` : float
                The first X coordinate of the line.
            `y` : float
                The first Y coordinate of the line.
            `x2` : float
                The second X coordinate of the line.
            `y2` : float
                The second Y coordinate of the line.
            `width` : float
                The desired width of the line.
            `rotation` : float
                The desired rotation (clockwise).
            `color` : (int, int, int)
                The RGB color of the line, specified as a tuple of
                three ints in the range of 0-255.
            `opacity` : int
                The transparecy of the color, with a range of 0-255.
                Defaults to 255 (no transparency).
            `anchor_visible` : bool
                Whether to show anchor points or not.
            `relative_points` : bool
                if True, (x2, y3) values are read as an
                offset from (x, y). Else, read as absolute coordinates.
            `center_line` : bool
                Whether the line's width is centered or is in the bottom.
            `batch` : `~pyglet.graphics.Batch`
                Optional batch to add the line to.
            `group` : `~pyglet.graphics.Group`
                Optional parent group of the line.
        """
        self._x = x
        self._y = y
        self._x2 = x2
        self._y2 = y2
        if not relative_points:
            self._x2 -= self._x
            self._y2 -= self._y
        self._width = width
        self._center_line = center_line
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
        line_lenght = math.hypot(self._y2, self._x2)
        line_width = self._width

        angle = math.atan2(self._y2, self._x2)
        cr = math.cos(angle)
        sr = math.sin(angle)
        offset_x = - line_lenght * cr / 2 + (line_width * sr / 2 if self._center_line else 0)
        offset_y = - line_lenght * sr / 2 - (line_width * cr / 2 if self._center_line else 0)
        ax = offset_x
        ay = offset_y
        bx = line_lenght * cr
        by = line_lenght * sr
        dx = - line_width * sr
        dy = line_width * cr
        cx = bx + dx + offset_x
        cy = by + dy + offset_y
        bx += offset_x
        by += offset_y
        dx += offset_x
        dy += offset_y
        self._vertices = [ax, ay, bx, by, cx, cy, ax, ay, cx, cy, dx, dy]

    def _update_color(self):
        self._vertex_list.colors[:] = [*self._rgb, int(self._opacity)] * 6
        super()._update_color

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
    def position(self):
        """The (x, y, x2, y2) coordinates of the line, as a tuple.

        :Parameters:
            `x` : int or float
                X coordinate of the line.
            `y` : int or float
                Y coordinate of the line.
            `x2` : int or float
                X2 coordinate of the line.
            `y2` : int or float
                Y2 coordinate of the line.
        """
        return self._x, self._y, self._x2, self._y2

    @position.setter
    def position(self, values):
        self._x, self._y, self._x2, self._y2 = values
        self._update_position()

    @property
    def width(self):
        """Width of the line.

        :type: int or float
        """
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        self._update_position()

    @property
    def center_line(self):
        """Whether center or side of the line's width is drawn following line (x, y) - (x2, y2).

        :type: int or float
        """
        return self._center_line

    @center_line.setter
    def center_line(self, value):
        self._center_line = value
        self._update_position()


class LineBasic(_AdvancedShapeBase):
    def __init__(self, x, y, x2, y2, rotation=0, color=(255, 255, 255), opacity=255,
                 anchor_visible=False, relative_points=False, batch=None, group=None):
        """Create a 1 px width line, with unchangeable width.

        The line's anchor point defaults to the center of the line.

        Why not use Line with width=1? For some angles it looks cleaner than Line.

        :Parameters:
            `x` : float
                The first X coordinate of the line.
            `y` : float
                The first Y coordinate of the line.
            `x2` : float
                The second X coordinate of the line.
            `y2` : float
                The second Y coordinate of the line.
            `rotation` : float
                The desired rotation (clockwise).
            `color` : (int, int, int)
                The RGB color of the line, specified as a tuple of
                three ints in the range of 0-255.
            `opacity` : int
                The transparecy of the color, with a range of 0-255.
                Defaults to 255 (no transparency).
            `anchor_visible` : bool
                Whether to show anchor points or not.
            `relative_points` : bool
                if True, (x2, y3) values are read as an
                offset from (x, y). Else, read as absolute coordinates.
            `batch` : `~pyglet.graphics.Batch`
                Optional batch to add the line to.
            `group` : `~pyglet.graphics.Group`
                Optional parent group of the line.
        """
        self._x = x
        self._y = y
        self._x2 = x2
        self._y2 = y2
        if not relative_points:
            self._x2 -= self._x
            self._y2 -= self._y
        self._rotation = rotation
        self._rgb = color
        self._opacity = opacity
        self._anchor_rotation_visible = anchor_visible
        self._anchor_position_visible = anchor_visible

        self._batch = batch or Batch()
        self._group = pyglet.shapes._ShapeGroup(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, group)
        self._vertex_list = self._batch.add(2, GL_LINES, self._group, 'v2f', 'c4B')
        self._update_position()
        self._update_color()

    def _calculate_vertices(self):
        self._vertices = [-self._x2 / 2, -self._y2 / 2, self._x2 / 2, self._y2 / 2]

    def _update_color(self):
        self._vertex_list.colors[:] = [*self._rgb, int(self._opacity)] * 2
        super()._update_color

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
    def position(self):
        """The (x, y, x2, y2) coordinates of the line, as a tuple.

        :Parameters:
            `x` : int or float
                X coordinate of the line.
            `y` : int or float
                Y coordinate of the line.
            `x2` : int or float
                X2 coordinate of the line.
            `y2` : int or float
                Y2 coordinate of the line.
        """
        return self._x, self._y, self._x2, self._y2

    @position.setter
    def position(self, values):
        self._x, self._y, self._x2, self._y2 = values
        self._update_position()


if __name__ == "__main__":
    import time
    class EventHandler:
        def __init__(self, shape, shape2=None, speed=10):
            self.state = None
            self.last_trigger = time.time()
            self.speed = speed
            self.speed_incr = 1
            self.shape = shape
            self.shape2 = shape2
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
                        if self.shape2:
                            self.shape2.width += self.speed * factor
                        print("Width:", self.shape.width)
                    except AttributeError:
                        print("Width:", None)
                if self.state == "h":
                    try:
                        self.shape.height += self.speed * factor
                        if self.shape2:
                            self.shape2.height += self.speed * factor
                        print("Height:", self.shape.height)
                    except AttributeError:
                        print("Height:", None)
                if self.state == "r":
                    try:
                        self.shape.rotation += self.speed * factor
                        if self.shape2:
                            self.shape2.rotation += self.speed * factor
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
                    if self.shape2:
                        self.shape2.anchor_rotation_visible = not self.shape2.anchor_rotation_visible
                    print("Anchor Rotation Visible:", self.shape.anchor_rotation_visible)
                if self.state == "N":
                    self.shape.anchor_position_visible = not self.shape.anchor_position_visible
                    if self.shape2:
                        self.shape2.anchor_position_visible = not self.shape2.anchor_position_visible
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
                    if self.shape2:
                        self.shape2.x += self.speed * factor
                    print("X:", self.shape.x)
                if self.state == "y":
                    self.shape.y += self.speed * factor
                    if self.shape2:
                        self.shape2.y += self.speed * factor
                    print("Y:", self.shape.y)
                if self.state == "X":
                    self.shape.anchor_rotation_x += self.speed * factor
                    if self.shape2:
                        self.shape2.anchor_rotation_x += self.speed * factor
                    print("Anchor Rotation X:", self.shape.anchor_rotation_x)
                if self.state == "Y":
                    self.shape.anchor_rotation_y += self.speed * factor
                    if self.shape2:
                        self.shape2.anchor_rotation_y += self.speed * factor
                    print("Anchor Rotation Y:", self.shape.anchor_rotation_y)
                if self.state == "K":
                    self.shape.anchor_position_x += self.speed * factor
                    if self.shape2:
                        self.shape2.anchor_position_x += self.speed * factor
                    print("Anchor Position X:", self.shape.anchor_position_x)
                if self.state == "l":
                    try:
                        self.shape.center_line = not self.shape.center_line
                        if self.shape2:
                            self.shape2.center_line = not self.shape2.center_line
                        print("Line centered:", self.shape.center_line)
                    except AttributeError:
                        print("Line centered:", self.shape.center_line)
                if self.state == "L":
                    self.shape.anchor_position_y += self.speed * factor
                    if self.shape2:
                        self.shape2.anchor_position_y += self.speed * factor
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
            elif text.upper() in ["V"]:
                print("Vertices:", self.shape._vertices)
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
    # shape = Circle(window.width / 2, window.height / 2, 200, segments=6, color=color_body, batch=batch)
    # shape = RegularPolygon(window.width / 2, window.height / 2, 5, side=30, color=color_body, batch=batch)
    # shape = Line(window.width / 2, window.height / 2, 150, 150, relative_points=True, color=color_body, batch=batch)
    # shape2 = LineBasic(window.width / 2 + 10, window.height / 2, 150, 150, relative_points=True, color=color_body, batch=batch)
    shape = Ellipse(window.width / 2, window.height / 2, 100, 150, segments=None, color=color_body, batch=batch)
    # shape = Star(window.width / 2, window.height / 2, 150, 100, num_spikes=10, color=color_body, batch=batch)
    # shape = Rectangle(window.width / 2, window.height / 2, 100, 200, color=color_body, batch=batch)
    # shape = Triangle(middle_x, middle_y, middle_x + 100, middle_y + 200, middle_x + 300, middle_y - 100, color=color_body, batch=batch)
    shape._verbose = True
    handler = EventHandler(shape, None)
    window.push_handlers(handler)

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

    pyglet.app.run()
