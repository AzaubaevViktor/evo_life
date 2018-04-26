from random import choice, random
from typing import List, Union


class Cell:
    MAX_ALIVE = 5
    MIN_ALIVE = 2
    EXPECT = 100
    PENALTY_MULT = 20

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
        penalty = sum(self.birth) + sum(self.live)
        penalty *= self.PENALTY_MULT
        return self.age > self.EXPECT - penalty

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
