# src/world.py
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Tuple, Optional

import config

Pos = Tuple[int, int]


@dataclass
class Resource:
    kind: str  # "food" or "water"
    pos: Pos


class World:
    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h
        self.tick = 0
        self.food: List[Resource] = []
        self.water: List[Resource] = []

    def in_bounds(self, pos: Pos) -> bool:
        x, y = pos
        return 0 <= x < self.w and 0 <= y < self.h

    def clamp(self, pos: Pos) -> Pos:
        x, y = pos
        x = max(0, min(self.w - 1, x))
        y = max(0, min(self.h - 1, y))
        return (x, y)

    def random_free_pos(self, occupied: set[Pos]) -> Optional[Pos]:
        for _ in range(80):
            p = (random.randrange(self.w), random.randrange(self.h))
            if p not in occupied:
                return p
        return None

    def spawn_resources(self, occupied: set[Pos]) -> None:
        # On évite de spawn sur agent/ressources
        occupied_all = set(occupied) | {r.pos for r in self.food} | {r.pos for r in self.water}

        if len(self.food) < config.MAX_FOOD and random.random() < config.FOOD_SPAWN_CHANCE:
            p = self.random_free_pos(occupied_all)
            if p:
                self.food.append(Resource("food", p))
                occupied_all.add(p)

        if len(self.water) < config.MAX_WATER and random.random() < config.WATER_SPAWN_CHANCE:
            p = self.random_free_pos(occupied_all)
            if p:
                self.water.append(Resource("water", p))
                occupied_all.add(p)

    def take_resource_at(self, kind: str, pos: Pos) -> bool:
        arr = self.food if kind == "food" else self.water
        for i, r in enumerate(arr):
            if r.pos == pos:
                arr.pop(i)
                return True
        return False

    def nearest_resource(self, kind: str, from_pos: Pos, max_range: int) -> Optional[Resource]:
        arr = self.food if kind == "food" else self.water
        if not arr:
            return None

        fx, fy = from_pos
        best = None
        best_d = 10**9
        for r in arr:
            x, y = r.pos
            d = abs(x - fx) + abs(y - fy)
            if d <= max_range and d < best_d:
                best = r
                best_d = d
        return best

    def update(self, occupied: set[Pos]) -> None:
        self.tick += 1
        self.spawn_resources(occupied)