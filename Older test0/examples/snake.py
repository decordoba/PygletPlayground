import pyglet
import random


w = 20
h = 20
pix_per_cell = 20


class Pos(object):
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.correct_pos()

    def move(self, dir):
        if dir == "R":
            self.x += 1
        elif dir == "U":
            self.y += 1
        elif dir == "L":
            self.x -= 1
        elif dir == "D":
            self.y -= 1
        self.correct_pos()

    def correct_pos(self):
        if self.x >= w:
            self.x -= w
        if self.y >= h:
            self.y -= h
        if self.x < 0:
            self.x += w
        if self.y < 0:
            self.y += h

    def copy(self):
        return Pos(x=self.x, y=self.y, color=self.color)

    def set_to_pos(self, other):
        self.x = other.x
        self.y = other.y

    def in_same_pos(self, other):
        return self.x == other.x and self.y == other.y

    def draw(self):
        x0 = self.x * pix_per_cell
        x1 = x0 + (pix_per_cell - 2)
        x0 += 1
        y0 = self.y * pix_per_cell
        y1 = y0 + (pix_per_cell - 2)
        y0 += 1
        positions = [x0, y0, x0, y1, x1, y1, x1, y0]
        colors = self.color * 4
        pyglet.graphics.vertex_list(
            4, ("v2f", positions), ("c3B", colors)).draw(pyglet.gl.GL_QUADS)


class SnakePos(Pos):
    def __init__(self, x, y, id=None):
        super(SnakePos, self).__init__(x, y, color=[0, 255, 0])
        self.id = id

    def copy(self):
        snake_pos = super(SnakePos, self).copy()
        snake_pos.id = self.id + 1
        return snake_pos


class Snake(object):
    def __init__(self, num_segments, x_head, y_head):
        self.snake = [SnakePos(x_head - i, y_head, id=i)
                      for i in range(num_segments)]
        self.snake[0].color = [255, 255, 0]
        self.key_handler = pyglet.window.key.KeyStateHandler()
        self.dir = "R"
        self.food = FoodPos(0, 0)
        self.food.move_to_empty_pos(self.snake)
        self.num_segments = num_segments

    def food_eaten(self):
        return self.food.in_same_pos(self.snake[0])

    def death(self):
        for segment in self.snake[1:]:
            if self.snake[0].in_same_pos(segment):
                return True
        return False

    def reset(self):
        self.snake = self.snake[:self.num_segments]

    def update(self, dt):
        # move player
        new_dir = ""
        if self.key_handler[pyglet.window.key.LEFT]:
            new_dir = "L"
        elif self.key_handler[pyglet.window.key.RIGHT]:
            new_dir = "R"
        elif self.key_handler[pyglet.window.key.UP]:
            new_dir = "U"
        elif self.key_handler[pyglet.window.key.DOWN]:
            new_dir = "D"

        if new_dir != "" and not (self.dir in ["L", "R"] and new_dir in ["L", "R"]) and not (self.dir in ["U", "D"] and new_dir in ["U", "D"]):
            self.dir = new_dir

        food_eaten = False
        if self.food_eaten():
            self.snake.append(self.snake[-1].copy())
            food_eaten = True

        if self.death():
            self.reset()

        for prev_segment, next_segment in zip(reversed(self.snake[:-1]), reversed(self.snake[1:])):
            next_segment.set_to_pos(prev_segment)
        self.snake[0].move(self.dir)

        if food_eaten:
            self.food.move_to_empty_pos(self.snake)

    def draw(self):
        for segment in self.snake:
            segment.draw()
        self.food.draw()


class FoodPos(Pos):
    def __init__(self, x, y):
        super(FoodPos, self).__init__(x, y, color=[255, 0, 0])

    def move_to_empty_pos(self, pos_list):
        empty_pos = False
        while not empty_pos:
            self.x = random.randint(0, w - 1)
            self.y = random.randint(0, h - 1)
            empty_pos = True
            for pos in pos_list:
                if self.in_same_pos(pos):
                    empty_pos = False
                    break


# create window
window = pyglet.window.Window(w * pix_per_cell, h * pix_per_cell)

# set drawing config
pyglet.gl.glClearColor(0, 0, 0, 0)

# create objects
snake = Snake(4, x_head=10, y_head=10)
window.push_handlers(snake.key_handler)


@window.event
def on_draw():
    window.clear()
    snake.draw()


pyglet.clock.schedule_interval(snake.update, 1/32)
pyglet.app.run()
