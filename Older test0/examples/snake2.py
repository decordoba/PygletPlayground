import pyglet


W, H = 20, 20
CW, CH = 20, 20
OW, OH = CW - 1, CH - 1

class Pos(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.fix_pos()

    def fix_pos(self):
        while self.x < 0:
            self.x += W
        while self.x >= W:
            self.x -= W
        while self.y < 0:
            self.y += H
        while self.y >= H:
            self.y -= H

    def move(self, dir):
        pos = self.next(dir)
        if not self.same(pos):
            self.changed = True
            self.x, self.y = pos.x, pos.y
            self.fix_pos()

    def next(self, dir):
        x, y = self.x, self.y
        if dir == "U":
            y += 1
        elif dir == "D":
            y -= 1
        elif dir == "R":
            x += 1
        elif dir == "L":
            x -= 1
        return Pos(x, y)
    
    def same(self, other):
        return (self.x, self.y) == (other.x, other.y)
    
    def random(self, exclude):
        empty_cell = False
        while not empty_cell:
            empty_cell = True
            self.x, self.y = random.randint(0, CW - 1), random.randint(0, CH - 1)
            for cell in exclude:
                if self.same(cell):
                    empty_cell = False
                    break
    
    def copy(self):
        return Pos(self.x, self.y)

class Cell(Pos):
    def __init__(self, x, y, c):
        super(Cell, self).__init__(x, y)
        self.c = c
        self.changed = True    

    def get_vertices(self):
        if self.changed:
            self.vertices = [
                (self.x * CW) + OW,
                (self.y * CH) + OH,
                (self.x * CW) + OW,
                (self.y * CH) + OH,
                (self.x * CW) + OW,
                (self.y * CH) + OH,
                (self.x * CW) + OW,
                (self.y * CH) + OH
            ]
            self.colors = list(self.c) * 4
            self.changed = False

    def draw(self):
        self.get_vertices()
        pyglet.graphics.vertex_list(4,
                                    ("v2f", self.vertices),
                                    ("c3B", self.colors))
    
    def copy(self):
        cell = super(Cell, self).copy()
        cell.c = self.c
        self.changed = True



class Game(object):
    def __init__(self):
        self.food = Cell(15, 15, [255, 0, 0])
        self.snake = [Cell(10 - i, 10, [0 if i > 0 else 255, 255, 0]) for i in range(4)]
        self.head = self.snake[0]
        self.dir = "R"
        self.key_handler = pyglet.window.key.KeyStateHandler()
    
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
        
        if self.head.next(self.dir).same(self.food):
            self.food.random(self.snake + [self.food])
            self.snake.append(self.snake[-1].copy())
        
        for 





