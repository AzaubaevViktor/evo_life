import time
from math import log

import pygame
from typing import Union, Dict, Tuple

from _types import TCoordinate, TColor
from cell import Cell
from world import World


class View:
    radius = 4
    GRAPH_SIZE = 300

    def __init__(self, model: World):
        self.model = model
        self._init_model()
        self.mouse: Union[TCoordinate, None] = None
        self.show_cell: Union[TCoordinate, None] = None
        self.play = True
        self.fps = 0

        self.stats = {}
        self.stats_count = 0
        self.log = False
        self._alpha = 1

        pygame.font.init()
        self.font = pygame.font.SysFont("monospaced", self.radius * 4)

        pygame.init()
        self.width = 2 * self.radius * self.model.w
        self.height = 2 * self.radius * self.model.h + 2 * 4 * self.radius + self.GRAPH_SIZE
        self.display = pygame.display.set_mode((
            self.width,
            self.height
        ))
        pygame.display.set_caption('Evolution Live')

    def _step(self):
        self.model.step()
        self._apply_stats(self.model.stats())

    def run(self):
        while True:
            start = time.time()
            self._events()

            self._draw()
            self._update()
            if self.play:
                self._step()
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
                        self._step()
                elif event.key == pygame.K_l:
                    self.log = not self.log
                elif event.key == pygame.K_o:
                    self._alpha *= 2
                elif event.key == pygame.K_PERIOD:
                    self._alpha /= 2

    def _init_model(self):
        self.model.clean()
        self.model.add_cell(2, 1, Cell.conway())
        self.model.add_cell(2, 2, Cell.conway())
        self.model.add_cell(2, 3, Cell.conway())
        self.stats_count = 0
        self.stats = {}

    def _update(self):
        pygame.display.update()
        self.display.fill((0, 0, 0))

    def _circle(self, coord: TCoordinate, radius: int, color: TColor, width: int = 1):
        pygame.draw.circle(self.display, color, coord, radius, width)

    def _calc_color(self, cell: Cell, other=None) -> TColor:
        birth = cell
        live = other
        if isinstance(cell, Cell):
            birth = cell.birth
            live = cell.live

        red = 0
        for i, r in enumerate(birth):
            red += (2 ** (7 - i)) * r

        green = 0
        for i, g in enumerate(live):
            green += (2 ** (7 - i)) * g

        return red, green, 255

    def _text(self, text, coord: TCoordinate, color: TColor):
        surface = self.font.render(text, False, color)
        self.display.blit(surface, coord)

    def _line(self, color: TColor, start: TCoordinate, end: TCoordinate, width: int = 1):
        pygame.draw.line(self.display, color, start, end, width)

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
        y = radius * 2 * self.model.h + radius * 4
        self._text("{:.0f}".format(self.fps), (0, y), (255, 255, 255))
        # show graphs
        height = self.GRAPH_SIZE

        ## calc ceofs for logariphm

        _beta = 1 / log(self._alpha + 1)
        _log = lambda x: log(self._alpha * x + 1) * _beta

        for x in range(1, 5):
            value = 0.5 ** x
            value = _log(value) if self.log else value
            y = -height * value + self.height

            self._line((100, 100, 100), (0, y), (self.width, y))

        if self.stats_count:
            coef = self.width / self.stats_count

            for color, values in self.stats.items():
                px = 0
                py = self.height
                for _x, value in enumerate(values):
                    x = coef * _x
                    if x == px:
                        continue

                    value = _log(value) if self.log else value
                    y = -height * value + self.height
                    self._line(color, (px, py), (x, y))
                    px = x
                    py = y

    def _apply_stats(self, stats: Dict[Tuple[Tuple, Tuple], int]):
        all = sum(stats.values())
        for k, v in stats.items():
            k = self._calc_color(*k)
            self.stats.setdefault(k, [0] * self.stats_count)
            self.stats[k].append(v / all)

        for k, v in self.stats.items():
            if len(v) != self.stats_count + 1:
                self.stats[k].append(0)

        self.stats_count += 1

    def _calc_fps(self, start, end):
        if end != start:
            self.fps = 1 / (end - start)
        else:
            self.fps = float("inf")
