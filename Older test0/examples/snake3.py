import pyglet
import random


W = 20
H = 20
PX = 20

class Cell(object):
    def __init__(self, x, y, c):
        self.x = x
        self.y = y
        self.fix_pos()
        self.c = c
    
    def fix_pos(self):
        if self.x >= W:
            self.x -= W
        elif self.y >= H:
            self.y -= H
        elif self.x < 0:
            self.x += W
        elif self.y < 0:
            self.y += H
    
    def next(self, dir):
        if dir == "R":
            self.x += 1
        elif dir == "D":
            self.y -= 1
        elif dir == "L":
            self.x -= 1
        elif dir == "U":
            self.y += 1
        self.fix_pos()
    
    def random(self, exclude):
        empty = False
        while not empty:
            empty = True
            x = random.randint(0, W - 1)
            y = random.randint(0, H - 1)
            for cell in exclude:
                if cell.same(x, y):
                    empty = False
                    break
        self.x, self.y = x, y
    
    def same(self, x, y):
        return self. x == x and self.y == y
    
    def collide(self, other):
        return self.same(other.x, other.y)
    
    def copy(self):
        return Cell(self.x, self.y, self.c)
    
    def draw(self):
        x0 = self.x * PX + 1
        x1 = x0 + (PX - 2)
        y0 = self.y * PX + 1
        y1 = y0 + (PX - 2)
        positions = [x0, y0, x0, y1, x1, y1, x1, y0]
        colors = self.c * 4
        pyglet.graphics.vertex_list(
            4, ("v2f", positions), ("c3B", colors)).draw(pyglet.gl.GL_QUADS)


class Game(object):
    def __init__(self):
        self.window = pyglet.window.Window(W * PX, H * PX)
        self.snake = [Cell(10, 10, [0, 255, 0])]
        self.head = self.snake[0]
        self.head.c = [255, 255, 0]
        self.food = Cell(15, 15, [255, 0, 0])
        self.key_handler = pyglet.window.key.KeyStateHandler()
        self.dir = "R"
        self.growth = 1
        self.min_num_segments = 4

    def update(self, dt):
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
        
        tail = [self.snake[-1].copy() for i in range(self.growth)]
        for s0, s1 in zip(reversed(self.snake[1:]), reversed(self.snake[:-1])):
            s0.x = s1.x
            s0.y = s1.y
        self.head.move(self.dir)
        
        if self.head.collide(self.food):
            self.snake.append(tail)
            self.food.random(self.snake + [self.food.copy()])
        else:
            for s in self.snake[1:]:
                if self.head.collide(s):
                    self.snake = self.snake[:self.min_num_segments]
    
    def draw(self):
        pyglet.gl.glClearColor(0, 0, 0, 0)
        self.food.draw()
        for s in self.snake:
            s.draw()
    




