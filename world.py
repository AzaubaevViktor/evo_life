from typing import List, Union, Iterator, Tuple

from cell import Cell


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

    def stats(self):
        types = {}
        for x, y, cell in self:
            if cell is None:
                continue
            key = tuple(cell.birth), tuple(cell.live)

            types.setdefault(key, 0)
            types[key] += 1
        return types

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
