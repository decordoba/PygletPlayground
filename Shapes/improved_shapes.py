import pyglet
import math
import time
from PIL import Image


"""
Improvement over pyglet.shapes.
Summary of chages:
    * all angles changed to degrees (before, some in degrees and some in radians)
    * added getters and setters for some missing properties (i.e Arc [closed, radius, angle])
    * opacity and rotation passed in init
    * added shapes with borders
    * documentation slightly enhanced
"""


class Arc(pyglet.shapes.Arc):
    def __init__(self, x, y, radius, rotation=0, segments=None, angle=360, start_angle=0,
                 closed=False, color=(255, 255, 255), opacity=255, anchor_visible=False,
                 batch=None, group=None):
        """Create an Arc.

        The Arc's anchor point (x, y) defaults to it's center.

        :Parameters:
            `x` : float
                X coordinate of the circle.
            `y` : float
                Y coordinate of the circle.
            `radius` : float
                The desired radius.
            `rotation` : float
                The desired rotation (clockwise). It is recommended to use
                start_angle as the initial orientation, and rotation to
                change it later.
            `segments` : int
                You can optionally specify how many distinct line segments
                the arc should be made from. If not specified it will be
                automatically calculated using the formula:
                `max(14, int(radius / 1.25))`.
            `angle` : float
                The angle of the arc, in degrees (counter-clockwise).
                Defaults to 360, which is a full circle.
            `start_angle` : float
                The start angle of the arc, in degrees (counter-clockwise).
                Defaults to 0. To modify it after creation, use rotation.
            `closed` : bool
                If True, the ends of the arc will be connected with a line.
                Defaults to False.
            `color` : (int, int, int)
                The RGB color of the circle, specified as a tuple of
                three ints in the range of 0-255. Defaults to white.
            `opacity` : int
                The transparecy of the color, with a range of 0-255.
                Defaults to 255 (no transparency).
            `batch` : `~pyglet.graphics.Batch`
                Optional batch to add the circle to.
            `group` : `~pyglet.graphics.Group`
                Optional parent group of the circle.
        """
        self._anchor_visible = anchor_visible
        self._anchor_circle = None
        super().__init__(x, y, radius, segments=segments, angle=angle, start_angle=start_angle,
                         closed=True, color=color, batch=batch, group=group)
        self._closed = closed  # closed set to True, then overwritten, so extra vertex is created
        self.rotation = rotation
        self.opacity = opacity

    def delete(self):
        super().delete()
        if self._anchor_circle is not None:
            self._anchor_circle.delete()

    def draw(self):
        """Draw the shape at its current position.

        Using this method is not recommended. Instead, add the
        shape to a `pyglet.graphics.Batch` for efficient rendering.
        """
        super().draw()
        if self._anchor_circle is not None:
            self._anchor_circle.draw()

    def _update_position(self):
        # rewritten to allow flexibility with closed, to change angles to degrees, and to show/hide anchor
        if not self._visible:
            vertices = (0,) * self._segments * 4
        else:
            x = self._x + self._anchor_x
            y = self._y + self._anchor_y
            r = self._radius
            tau_segs = math.radians(self._angle) / self._segments
            start_angle = math.radians(self._start_angle - self._rotation)

            # calculate the outer points of the arc
            points = [(x + (r * math.cos((i * tau_segs) + start_angle)),
                       y + (r * math.sin((i * tau_segs) + start_angle))) for i in range(self._segments + 1)]

            # create a list of doubled-up points from the points
            vertices = []
            for i in range(len(points) - 1):
                line_points = points[i] + points[i + 1]
                vertices.extend(line_points)

            if self._closed:
                chord_points = points[-1] + points[0]
                vertices.extend(chord_points)
            else:
                chord_points = points[-1] + points[-1]
                vertices.extend(chord_points)

            # show/hide anchor
            if self._anchor_visible:
                if self._anchor_circle is None:
                    self._anchor_circle = Circle(0, 0, 2, opacity=0, batch=self._batch)
                    self._update_color()
                self._anchor_circle.anchor_position = (x, y)
                self._anchor_circle.visible = True
                print(self._anchor_circle.color, self._anchor_circle.opacity, self._anchor_circle.x, self._anchor_circle.y, self._anchor_circle.visible)
            elif self._anchor_circle is not None:
                self._anchor_circle.visible = False

        self._vertex_list.vertices[:] = vertices

    def _update_color(self):
        super()._update_color()
        if self._anchor_circle is not None:
            self._anchor_circle.color = (255 - c for c in self._rgb)
            self._anchor_circle.opacity = self._opacity

    @property
    def radius(self):
        """The radius of the arc.

        :type: float
        """
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value
        self._update_position()

    @property
    def closed(self):
        """Whether the arc is closed or not.

        :type: bool
        """
        return self._closed

    @closed.setter
    def closed(self, value):
        self._closed = value
        self._update_position()

    @property
    def angle(self):
        """The angle of the arc, in degrees.

        :type: float
        """
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value
        self._update_position()

    @property
    def start_angle(self):
        """The start_angle of the arc, in degrees.

        0 degress is right, 90 top, 180 left, etc.

        :type: float
        """
        return self._start_angle

    @start_angle.setter
    def start_angle(self, value):
        self._start_angle = value
        self._update_position()

    @property
    def anchor_visible(self):
        """Whether the anchor point is visible or not.

        :type: bool
        """
        return self._anchor_visible

    @anchor_visible.setter
    def anchor_visible(self, value):
        self._anchor_visible = value
        self._update_position()


class Circle(pyglet.shapes.Circle):
    def __init__(self, x, y, radius, rotation=0, segments=None, color=(255, 255, 255),
                 opacity=255, anchor_visible=False, batch=None, group=None):
        """Create a circle.

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
                three ints in the range of 0-255. Defaults to white.
            `opacity` : int
                The transparecy of the color, with a range of 0-255.
                Defaults to 255 (no transparency).
            `batch` : `~pyglet.graphics.Batch`
                Optional batch to add the circle to.
            `group` : `~pyglet.graphics.Group`
                Optional parent group of the circle.
        """
        self._rotation = rotation
        self._anchor_visible = anchor_visible
        self._anchor_circle = None
        super().__init__(x, y, radius, segments=segments,
                         color=color, batch=batch, group=group)
        self.opacity = opacity

    def delete(self):
        super().delete()
        if self._anchor_circle is not None:
            self._anchor_circle.delete()

    def draw(self):
        """Draw the shape at its current position.

        Using this method is not recommended. Instead, add the
        shape to a `pyglet.graphics.Batch` for efficient rendering.
        """
        super().draw()
        if self._anchor_circle is not None:
            self._anchor_circle.draw()

    def _update_position(self):
        # rewritten to add rotation, and to show/hide anchor
        if not self._visible:
            vertices = (0,) * self._segments * 6
        else:
            x = self._x + self._anchor_x
            y = self._y + self._anchor_y
            r = self._radius
            tau_segs = math.pi * 2 / self._segments
            start_angle = -math.radians(self._rotation)

            # calculate the outer points of the circle
            points = [(x + (r * math.cos((i * tau_segs) + start_angle)),
                       y + (r * math.sin((i * tau_segs) + start_angle))) for i in range(self._segments)]

            # create a list of triangles from the points
            vertices = []
            for i, point in enumerate(points):
                triangle = (x, y) + points[i - 1] + point
                vertices.extend(triangle)

            # show/hide anchor
            if self._anchor_visible:
                if self._anchor_circle is None:
                    self._anchor_circle = Circle(0, 0, 2, opacity=0, batch=self._batch)
                    self._update_color()
                self._anchor_circle.anchor_position = (x, y)
                self._anchor_circle.visible = True
                print(self._anchor_circle.color, self._anchor_circle.opacity, self._anchor_circle.x, self._anchor_circle.y, self._anchor_circle.visible)
            elif self._anchor_circle is not None:
                self._anchor_circle.visible = False

        self._vertex_list.vertices[:] = vertices

    def _update_color(self):
        super()._update_color()
        if self._anchor_circle is not None:
            self._anchor_circle.color = (255 - c for c in self._rgb)
            self._anchor_circle.opacity = self._opacity

    @property
    def rotation(self):
        """Clockwise rotation of the circle, in degrees.

        The circle will be rotated about its (anchor_x, anchor_y)
        position. The effect might be invisible unless segments is low.

        :type: float
        """
        return self._rotation

    @rotation.setter
    def rotation(self, rotation):
        self._rotation = rotation
        self._update_position()

    @property
    def anchor_visible(self):
        """Whether the anchor point is visible or not.

        :type: bool
        """
        return self._anchor_visible

    @anchor_visible.setter
    def anchor_visible(self, value):
        self._anchor_visible = value
        self._update_position()


class Sector(pyglet.shapes.Sector):
    def __init__(self, x, y, radius, rotation=0, segments=None, angle=360, start_angle=0,
                 color=(255, 255, 255), opacity=255, anchor_visible=False, batch=None, group=None):
        """Create a sector of a circle.

        The sector's anchor point (x, y) defaults to the center of the circle.

        :Parameters:
            `x` : float
                X coordinate of the sector.
            `y` : float
                Y coordinate of the sector.
            `radius` : float
                The desired radius.
            `rotation` : float
                The desired rotation (clockwise). It is recommended to use
                start_angle as the initial orientation, and rotation to
                change it later.
            `segments` : int
                You can optionally specify how many distinct triangles
                the sector should be made from. If not specified it will
                be automatically calculated based using the formula:
                `max(14, int(radius / 1.25))`.
            `angle` : float
                The angle of the sector, in degrees (counter-clockwise).
                Defaults to 360, which is a full circle.
            `start_angle` : float
                The start angle of the sector, in degrees (counter-clockwise).
                Defaults to 0.
            `color` : (int, int, int)
                The RGB color of the sector, specified as a tuple of
                three ints in the range of 0-255.
            `opacity` : int
                The transparecy of the color, with a range of 0-255.
                Defaults to 255 (no transparency).
            `batch` : `~pyglet.graphics.Batch`
                Optional batch to add the sector to.
            `group` : `~pyglet.graphics.Group`
                Optional parent group of the sector.
        """
        self._anchor_visible = anchor_visible
        self._anchor_circle = None
        super().__init__(x, y, radius, segments=segments, angle=angle,
                         start_angle=start_angle, color=color, batch=batch, group=group)
        self.rotation = rotation
        self.opacity = opacity

    def delete(self):
        super().delete()
        if self._anchor_circle is not None:
            self._anchor_circle.delete()

    def draw(self):
        """Draw the shape at its current position.

        Using this method is not recommended. Instead, add the
        shape to a `pyglet.graphics.Batch` for efficient rendering.
        """
        super().draw()
        if self._anchor_circle is not None:
            self._anchor_circle.draw()

    def _update_position(self):
        # rewritten to change angles to degrees, and to show/hide anchor
        if not self._visible:
            vertices = (0,) * self._segments * 6
        else:
            x = self._x + self._anchor_x
            y = self._y + self._anchor_y
            r = self._radius
            tau_segs = math.radians(self._angle) / self._segments
            start_angle = math.radians(self._start_angle - self._rotation)

            # calculate the outer points of the sector
            points = [(x + (r * math.cos((i * tau_segs) + start_angle)),
                       y + (r * math.sin((i * tau_segs) + start_angle))) for i in range(self._segments + 1)]

            # create a list of triangles from the points
            vertices = []
            for i, point in enumerate(points[1:], start=1):
                triangle = (x, y) + points[i - 1] + point
                vertices.extend(triangle)

            # show/hide anchor
            if self._anchor_visible:
                if self._anchor_circle is None:
                    self._anchor_circle = Circle(0, 0, 2, opacity=0, batch=self._batch)
                    self._update_color()
                self._anchor_circle.anchor_position = (x, y)
                self._anchor_circle.visible = True
                print(self._anchor_circle.color, self._anchor_circle.opacity, self._anchor_circle.x, self._anchor_circle.y, self._anchor_circle.visible)
            elif self._anchor_circle is not None:
                self._anchor_circle.visible = False

        self._vertex_list.vertices[:] = vertices

    def _update_color(self):
        super()._update_color()
        if self._anchor_circle is not None:
            self._anchor_circle.color = (255 - c for c in self._rgb)
            self._anchor_circle.opacity = self._opacity

    @property
    def angle(self):
        """The angle of the arc, in degrees.

        :type: float
        """
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value
        self._update_position()

    @property
    def start_angle(self):
        """The start_angle of the arc, in degrees.

        0 degress is right, 90 top, 180 left, etc.

        :type: float
        """
        return self._start_angle

    @start_angle.setter
    def start_angle(self, value):
        self._start_angle = value
        self._update_position()

    @property
    def anchor_visible(self):
        """Whether the anchor point is visible or not.

        :type: bool
        """
        return self._anchor_visible

    @anchor_visible.setter
    def anchor_visible(self, value):
        self._anchor_visible = value
        self._update_position()


class Line(pyglet.shapes.Line):
    def __init__(self, x, y, x2, y2, rotation=0, width=1, color=(255, 255, 255),
                 opacity=255, anchor_visible=False, batch=None, group=None):
        """Create a line.

        The line's anchor point defaults to the center of the line's
        width on the X axis, and the Y axis.

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
            `color` : (int, int, int)
                The RGB color of the line, specified as a tuple of
                three ints in the range of 0-255.
            `batch` : `~pyglet.graphics.Batch`
                Optional batch to add the line to.
            `group` : `~pyglet.graphics.Group`
                Optional parent group of the line.
        """
        self._anchor_visible = anchor_visible
        self._anchor_circle = None
        super().__init__(x, y, x2, y2, width=width, color=color, batch=batch, group=group)
        self.rotation = rotation
        self.opacity = opacity

    def _update_position(self):
        if not self._visible:
            self._vertex_list.vertices[:] = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        else:
            x1 = -self._anchor_y
            y1 = self._anchor_x - self._width / 2
            x = self._x
            y = self._y
            x2 = x1 + math.hypot(self._y2 - y, self._x2 - x)
            y2 = y1 + self._width

            r = math.atan2(self._y2 - y, self._x2 - x)
            cr = math.cos(r)
            sr = math.sin(r)
            ax = x1 * cr - y1 * sr + x
            ay = x1 * sr + y1 * cr + y
            bx = x2 * cr - y1 * sr + x
            by = x2 * sr + y1 * cr + y
            cx = x2 * cr - y2 * sr + x
            cy = x2 * sr + y2 * cr + y
            dx = x1 * cr - y2 * sr + x
            dy = x1 * sr + y2 * cr + y
            self._vertex_list.vertices[:] = (ax, ay, bx, by, cx, cy, ax, ay, cx, cy, dx, dy)

    def _update_color(self):
        self._vertex_list.colors[:] = [*self._rgb, int(self._opacity)] * 6

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


class RectangleWithBorder(pyglet.shapes.Rectangle):
    def __init__(self, x, y, width, height, border=1, color=(255, 255, 255), border_color=(0, 0, 0), batch=None, group=None):
        self._border_lines = []  # _update_position uses self._border_lines and is called in super.__init__, so initialize it to empty
        super().__init__(x, y, width, height, color=color, batch=batch, group=group)
        self._border = border
        self._brgb = border_color
        self._border_opacity = 255
        self._border_visible = True
        self._border_lines = [
            pyglet.shapes.Line(0, 0, 0, 0, width=self._border, color=self._brgb, batch=self._batch, group=self._group),
            pyglet.shapes.Line(0, 0, 0, 0, width=self._border, color=self._brgb, batch=self._batch, group=self._group),
            pyglet.shapes.Line(0, 0, 0, 0, width=self._border, color=self._brgb, batch=self._batch, group=self._group),
            pyglet.shapes.Line(0, 0, 0, 0, width=self._border, color=self._brgb, batch=self._batch, group=self._group)
        ]
        self._update_position()
        self._update_color()

    def delete(self):
        super().delete()
        for line in self._border_lines:
            line.delete()

    def draw(self):
        """Draw the shape at its current position.

        Using this method is not recommended. Instead, add the
        shape to a `pyglet.graphics.Batch` for efficient rendering.
        """
        super().draw()
        for line in self._border_lines:
            line.draw()

    def _update_position(self):
        super()._update_position()
        vertices = self._vertex_list.vertices[:][0:6] + self._vertex_list.vertices[:][10:12] + self._vertex_list.vertices[:][0:2]
        for i, line in enumerate(self._border_lines):
            line._visible = self._border_visible
            line.x = vertices[2 * i]
            line.y = vertices[2 * i + 1]
            line.x2 = vertices[2 * i + 2]
            line.y2 = vertices[2 * i + 3]
            line._width = self._border
            # correct for line width
            leg_x, leg_y = line.x - line.x2, line.y - line.y2
            hypotenuse = (leg_x ** 2 + leg_y ** 2) ** 0.5
            line.x += self._border / 2 * leg_x / hypotenuse
            line.x2 -= self._border / 2 * leg_x / hypotenuse
            line.y += self._border / 2 * leg_y / hypotenuse
            line.y2 -= self._border / 2 * leg_y / hypotenuse
            line._update_position()

    def _update_color(self):
        super()._update_color()
        for line in self._border_lines:
            line._rgb = self._brgb
            line._opacity = self._border_opacity
            line._update_color()

    @property
    def border(self):
        return self._border

    @border.setter
    def border(self, value):
        self._border = value
        self._update_position()

    @property
    def border_color(self):
        return self._brgb

    @border_color.setter
    def border_color(self, values):
        self._brgb = list(map(int, values))
        self._update_color()

    @property
    def border_opacity(self):
        return self._opacity

    @border_opacity.setter
    def border_opacity(self, value):
        self._border_opacity = value
        self._update_color()

    @property
    def border_visible(self):
        return self._border_visible

    @border_visible.setter
    def border_visible(self, value):
        self._border_visible = value
        self._update_position()


def save_window(window, filename="window.png"):
    """Save window as image."""
    buffer = (pyglet.gl.GLubyte * (4 * window.width * window.height))(0)
    pyglet.gl.glReadPixels(0, 0, window.width, window.height,
                           pyglet.gl.GL_RGBA, pyglet.gl.GL_UNSIGNED_BYTE, buffer)
    image = Image.frombytes(mode="RGBA", size=(window.width, window.height), data=buffer)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image.save(filename)


if __name__ == "__main__":
    options = ["Arc", "Circle", "Sector", "RectangleWithBorder"]
    while True:
        print(f"Choose an option [0 - {len(options) - 1}]:")
        for i, option in enumerate(options):
            print(f"{i}. {option}")
        txt = input(">> ")
        try:
            idx = int(txt)
            if idx >= 0 and idx < len(options):
                break
            print("Invalid number")
        except ValueError:
            print("Input is not a number")

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
                        print("Width:", self.shape.rotation)
                    except AttributeError:
                        print("Width:", None)
                if self.state == "h":
                    try:
                        self.shape.height += self.speed * factor
                        print("Height:", self.shape.rotation)
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
                if self.state.upper() == "N":
                    try:
                        self.shape.anchor_visible = not self.shape.anchor_visible
                        print("Anchor Visible:", self.shape.anchor_visible)
                    except AttributeError:
                        print("Anchor Visible:", None)
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
                    self.shape.anchor_x += self.speed * factor
                    print("Anchor X:", self.shape.anchor_x)
                if self.state == "Y":
                    self.shape.anchor_y += self.speed * factor
                    print("Anchor Y:", self.shape.anchor_y)
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
            elif text.upper() in ["Z"]:
                filename = input("Choose a name for your image (i.e. test1). Extension '.png' will be added.\n>> ")
                filename = "SavedImages/" + filename + ".png"
                save_window(window, filename)
                print(f"Saved to {filename}")
            elif text.upper() in ["I"]:
                print("Speed Increment:", self.speed_incr)
                print("Speed:", self.speed)
                print("State:", self.state)
                print("X:", self.shape.x)
                print("Y:", self.shape.y)
                print("Anchor X:", self.shape.anchor_x)
                print("Anchor Y:", self.shape.anchor_y)
                try:
                    print("Width:", self.shape.rotation)
                except AttributeError:
                    pass
                try:
                    print("Height:", self.shape.rotation)
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

    option = options[idx]
    print(f"Option chosen: {option}")
    window = pyglet.window.Window(1000, 1000, caption="option")
    batch = pyglet.graphics.Batch()
    background = pyglet.shapes.Rectangle(0, 0, window.width, window.height, color=(0, 0, 0), batch=batch)
    color_body = (255, 0, 0)
    color_line = (255, 255, 0)
    if option == "Arc":
        shape = Arc(window.width / 2, window.height / 2, 200, start_angle=90, angle=90, color=color_body, batch=batch)
    elif option == "Circle":
        shape = Circle(window.width / 2, window.height / 2, 200, segments=14, color=color_body, batch=batch)
    elif option == "Sector":
        shape = Sector(window.width / 2, window.height / 2, 200, start_angle=45, angle=270, color=color_body, batch=batch)
    elif option == "RectangleWithBorder":
        shape = RectangleWithBorder(window.width / 2, window.height / 2, 200, 200, color=color_body, border_color=color_line, batch=batch)
    else:
        raise Exception(f"Unknown shape {option}")
    handler = EventHandler(shape)
    window.push_handlers(handler)

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

    pyglet.app.run()
