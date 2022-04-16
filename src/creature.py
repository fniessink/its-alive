"""Creature."""

from __future__ import annotations

import random

from map import Map


class Creature:
    def tick(self, old_map: Map[Creature], new_map: Map[Creature]) -> None:
        """Move the creature, if possible."""
        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])
        old_coordinate = old_map.coordinate(self)
        new_coordinate = old_coordinate.relative(dx, dy)
        if old_map.is_occupied(new_coordinate) or new_map.is_occupied(new_coordinate):
            new_map[old_coordinate] = self
        else:
            new_map[new_coordinate] = self
