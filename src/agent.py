# src/agent.py
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Tuple, Optional

import config
from world import World, Pos


@dataclass
class Agent:
    id: int
    pos: Pos

    age: int = 0
    alive: bool = True

    hunger: float = 30.0
    thirst: float = 30.0
    energy: float = 80.0

    def step_needs(self) -> None:
        self.age += 1
        self.hunger = min(config.MAX_NEED, self.hunger + config.HUNGER_INCREASE)
        self.thirst = min(config.MAX_NEED, self.thirst + config.THIRST_INCREASE)
        self.energy = max(0.0, self.energy - config.ENERGY_DECREASE)

        if self.hunger >= config.DEATH_THRESHOLD or self.thirst >= config.DEATH_THRESHOLD or self.energy <= 0:
            self.alive = False

    def choose_goal(self) -> str:
        # Logique simple (LLM plus tard)
        if self.thirst >= 70:
            return "water"
        if self.hunger >= 65:
            return "food"
        if self.energy <= 25:
            return "sleep"
        return "wander"

    def _move_towards(self, target: Pos, world: World) -> None:
        x, y = self.pos
        tx, ty = target

        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)

        # hasard léger pour éviter un “rail”
        if random.random() < 0.5:
            new_pos = (x + dx, y) if dx != 0 else (x, y + dy)
        else:
            new_pos = (x, y + dy) if dy != 0 else (x + dx, y)

        self.pos = world.clamp(new_pos)

    def _wander(self, world: World) -> None:
        x, y = self.pos
        self.pos = world.clamp((x + random.choice([-1, 0, 1]), y + random.choice([-1, 0, 1])))

    def act(self, world: World) -> None:
        if not self.alive:
            return

        goal = self.choose_goal()

        # Consommer si on est sur la case
        if goal == "food" and world.take_resource_at("food", self.pos):
            self.hunger = max(0.0, self.hunger - config.EAT_AMOUNT)
            self.energy = min(config.MAX_NEED, self.energy + 5.0)
            return

        if goal == "water" and world.take_resource_at("water", self.pos):
            self.thirst = max(0.0, self.thirst - config.DRINK_AMOUNT)
            self.energy = min(config.MAX_NEED, self.energy + 3.0)
            return

        if goal == "sleep":
            self.energy = min(config.MAX_NEED, self.energy + config.SLEEP_AMOUNT)
            # dormir consomme un peu
            self.hunger = min(config.MAX_NEED, self.hunger + 0.5)
            self.thirst = min(config.MAX_NEED, self.thirst + 0.8)
            return

        # Aller vers ressource si vue
        if goal in ("food", "water"):
            res = world.nearest_resource(goal, self.pos, config.VISION_RANGE)
            if res:
                self._move_towards(res.pos, world)
            else:
                self._wander(world)
        else:
            self._wander(world)