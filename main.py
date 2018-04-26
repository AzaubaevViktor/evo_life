from random import choice, random
from typing import List, Union, Iterator, Tuple

import time

import pygame as pygame
import sys
from terminaltables import AsciiTable


TCoordinate = Tuple[int, int]
TColor = Tuple[int, int, int]


class Cell:
    MAX_ALIVE = 5
    MIN_ALIVE = 2
    EXPECT = 20

    def __init__(self, birth: List[int], live: List[int], raw=False):
        # 1..7 count
        # 0..6 index
        if raw:
            self.birth = birth
            self.live = live
        else:
            self.birth = [0 for x in range(self.MIN_ALIVE, self.MAX_ALIVE)]
            for index in birth:
                index = index - self.MIN_ALIVE
                if index < len(self.birth):
                    self.birth[index] = 1

            self.live = [0 for x in range(self.MIN_ALIVE, self.MAX_ALIVE)]
            for index in live:
                index = index - self.MIN_ALIVE
                if index < len(self.live):
                    self.live[index] = 1
        self.age = 0

    @classmethod
    def _is_birth(cls, birth: List[int], value: int):
        if value < cls.MIN_ALIVE or value >= cls.MAX_ALIVE:
            return False
        return birth[value - cls.MIN_ALIVE] == 1

    def is_birth(self, value: int) -> bool:
        return self._is_birth(self.birth, value)

    def is_alive(self, value: int) -> bool:
        if value < self.MIN_ALIVE or value >= self.MAX_ALIVE:
            return False
        return self.live[value - self.MIN_ALIVE] == 1

    def is_dead(self) -> bool:
        return self.age > self.EXPECT

    @classmethod
    def generate_new(cls, cells: List["Cell"], neight_count: int, mutation_coef: int=0.001) -> Union["Cell", None]:
        k = mutation_coef
        if len(cells) == 0:
            return None

        size = cls.MAX_ALIVE - cls.MIN_ALIVE

        birth = []
        for b in range(size):
            n = choice(cells).birth[b]
            if random() < k:
                n = 1 - n
            birth.append(n)

        if not cls._is_birth(birth, neight_count):
            return None

        live = []
        for l in range(size):
            n = choice(cells).live[l]
            if random() < k:
                n = 1 - n
            live.append(n)

        return Cell(birth, live, raw=True)

    def _gen_list(self, arr: List[int]):
        for i, b in enumerate(arr):
            if b:
                yield i + self.MIN_ALIVE

    def birth_list(self):
        return list(self._gen_list(self.birth))

    def live_list(self):
        return list(self._gen_list(self.live))

    def __str__(self):
        s = "".join(map(str, self.birth)) + "\n"
        s += "".join(map(str, self.live)) + '\n'
        s += "-------"
        return s

    @staticmethod
    def conway():
        return Cell([3], [2, 3])


class World:
    NEIGHT = (
        (-1, -1),
        (-1, 0),
        (-1, 1),
        (0, -1),
        (0, 1),
        (1, -1),
        (1, 0),
        (1, 1)
    )

    def __init__(self, width, height):
        self.w = width
        self.h = height

        self.cells = self._new_world()

        self.new_cells = None

    def add_cell(self, x: int, y: int, cell: Cell):
        self.cells[y][x] = cell

    def _new_world(self) -> List[List[Union[Cell, None]]]:
        return [
            [None for x in range(self.w)]
            for y in range(self.h)
        ]

    def _iter_by(self, cells) -> Iterator[Tuple[int, int, Cell]]:
        for y in range(self.h):
            for x in range(self.w):
                yield x, y, cells[y][x]

    def _neight(self, cx, cy) -> Iterator[Cell]:
        for dx, dy in self.NEIGHT:
            x = cx + dx
            y = cy + dy
            if not (0 <= x < self.w):
                x %= self.w
            if not (0 <= y < self.h):
                y %= self.h

            if self.cells[y][x] is not None:
                yield self.cells[y][x]

    def _neight_count(self, cx, cy) -> int:
        return len(tuple(self._neight(cx, cy)))

    def step(self):
        self.new_cells = self._new_world()
        for x, y, cell in self._iter_by(self.cells):
            neight = self._neight_count(x, y)
            if cell is None:
                cell = Cell.generate_new(list(self._neight(x, y)), neight)

                if (cell is not None) and (not cell.is_birth(neight)):
                    cell = None
            else:
                if not cell.is_alive(neight) or cell.is_dead():
                    cell = None

            self.new_cells[y][x] = cell
            if cell:
                cell.age += 1

        self.cells = self.new_cells

    def clean(self):
        self.cells = self._new_world()

    def print(self):
        for y in range(self.h):
            for x in range(self.w):
                cell = self.cells[y][x]
                if cell:
                    print("#", end="")
                else:
                    print("-", end="")
            print()
        # print(AsciiTable([[""]] + self.cells).table)

    def __iter__(self):
        yield from self._iter_by(self.cells)

    def __getitem__(self, item: Union[Tuple[int, int]]):
        return self.cells[item[1]][item[0]]


class View:
    radius = 4

    def __init__(self, model: World):
        self.model = model
        self._init_model()
        self.mouse: Union[TCoordinate, None] = None
        self.show_cell: Union[TCoordinate, None] = None
        self.play = True
        self.fps = 0

        pygame.font.init()
        self.font = pygame.font.SysFont("monospaced", self.radius * 4)

        pygame.init()
        self.display = pygame.display.set_mode((
            2 * self.radius * self.model.w,
            2 * self.radius * self.model.h + 100
        ))
        pygame.display.set_caption('Hello World!')

    def _step(self):
        self.model.step()

    def run(self):
        while True:
            start = time.time()
            self._events()

            self._draw()
            self._update()
            if self.play:
                self.model.step()
            end = time.time()
            self._calc_fps(start, end)

    def _events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse = event.pos
                self.show_cell = tuple(map(lambda x: int(x / self.radius / 2), self.mouse))
                if self.show_cell[0] > self.model.w:
                    self.show_cell = (-1, -1)
                if self.show_cell[1] > self.model.h:
                    self.show_cell = (-1, -1)
                self.mouse = None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.play = not self.play
                elif event.key == pygame.K_r:
                    self._init_model()
                elif event.key == pygame.K_s:
                    if not self.play:
                        self.model.step()

    def _init_model(self):
        self.model.clean()
        self.model.add_cell(2, 1, Cell.conway())
        self.model.add_cell(2, 2, Cell.conway())
        self.model.add_cell(2, 3, Cell.conway())

    def _update(self):
        pygame.display.update()
        self.display.fill((0, 0, 0))

    def _circle(self, coord: TCoordinate, radius: int, color: TColor, width: int=1):
        pygame.draw.circle(self.display, color, coord, radius, width)

    def _calc_color(self, cell: Cell) -> TColor:
        red = 0
        for i, r in enumerate(cell.birth):
            red += (2 ** (7 - i)) * r

        green = 0
        for i, g in enumerate(cell.live):
            green += (2 ** (7 - i)) * g

        return red, green, 255
    
    def _text(self, text, coord: TCoordinate, color: TColor):
        surface = self.font.render(text, False, color)
        self.display.blit(surface, coord)

    def _draw(self):
        # draw world
        radius = self.radius
        for x, y, cell in self.model:
            if cell:
                self._circle((radius + 2 * radius * x, radius + 2 * radius * y), radius, self._calc_color(cell))
        # draw info about cell
        if self.show_cell is not None:
            y = radius * 2 * self.model.h
            cell = self.model[self.show_cell]
            if cell:

                text = f"{self.show_cell}: birth: {cell.birth_list()}; live: {cell.live_list()}"
                color = self._calc_color(cell)
            else:
                text = f"{self.show_cell}: None"
                color = (255, 255, 255)

            self._text(text, (0, y), color)
        # show fps
        y = radius * 2 * self.model.h + 50
        self._text("{:.0f}".format(self.fps), (0, y), (255, 255, 255))

    def _calc_fps(self, start, end):
        if end != start:
            self.fps = 1 / (end - start)
        else:
            self.fps = float("inf")


w = World(100, 60)

view = View(w)

# while True:
#     w.print()
#     print()
#     w.step()
#     time.sleep(0.1)

view.run()
