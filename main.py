from random import choice, random
from typing import List, Union, Iterator, Tuple

from terminaltables import AsciiTable


class Cell:
    def __init__(self, birth: List[int], live: List[int]):
        # 1..7 count
        # 0..6 index
        self.birth = birth
        self.live = live

    def is_birth(self, value):
        if value == 0 or value == 8:
            return False
        return self.birth[value - 1] == 1

    def is_alive(self, value):
        if value == 0 or value == 8:
            return False
        return self.live[value - 1] == 1

    @staticmethod
    def generate_new(cells: List["Cell"], mutation_coef: int=0.01) -> Union["Cell", None]:
        k = mutation_coef
        if len(cells) == 0:
            return None

        birth = []
        for b in range(7):
            n = choice(cells).birth[b]
            if random() < k:
                n = 1 - n
            birth.append(n)

        live = []
        for l in range(7):
            n = choice(cells).live[l]
            if random() < k:
                n = 1 - n
            live.append(n)

        return Cell(birth, live)

    def __str__(self):
        s = "".join(map(str, self.birth)) + "\n"
        s += "".join(map(str, self.live)) + '\n'
        s += "-------"
        return s

    @staticmethod
    def conway():
        return Cell([0, 0, 1, 0, 0, 0, 0], [0, 1, 1, 0, 0, 0, 0])


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
        for y in range(self.w):
            for x in range(self.h):
                yield x, y, cells[y][x]

    def _neight(self, cx, cy) -> Iterator[Cell]:
        for dx, dy in self.NEIGHT:
            x = cx + dx
            y = cy + dy
            if not (0 <= x < self.w):
                continue
            if not (0 <= y < self.h):
                continue

            if self.cells[y][x] is not None:
                yield self.cells[y][x]

    def _neight_count(self, cx, cy) -> int:
        return len(tuple(self._neight(cx, cy)))

    def step(self):
        self.new_cells = self._new_world()
        for x, y, cell in self._iter_by(self.cells):
            neight = self._neight_count(x, y)
            if cell is None:
                cell = Cell.generate_new(list(self._neight(x, y)))

                if (cell is not None) and (not cell.is_birth(neight)):
                    cell = None
            else:
                if not cell.is_alive(neight):
                    cell = None

            self.new_cells[y][x] = cell

        self.cells = self.new_cells

    def print(self):
        print(AsciiTable([[""]] + self.cells).table)


w = World(4, 4)
w.add_cell(2, 1, Cell.conway())
w.add_cell(2, 2, Cell.conway())
w.add_cell(2, 3, Cell.conway())
w.print()
w.step()
w.print()
