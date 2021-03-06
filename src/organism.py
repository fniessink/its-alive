"""Organism."""

from __future__ import annotations

import numpy as np

from map import Map
from neural_network import NeuralNetwork


class Organism:
    def __init__(self, ticks: int, brain: NeuralNetwork = None) -> None:
        self._max_age = ticks
        self._brain = brain or NeuralNetwork([4, 5, 5, 2], output='sigmoid')
        self._age = 0
        self._blocked = 0

    def tick(self, old_map: Map[Organism], new_map: Map[Organism]) -> None:
        """Move, if possible."""
        old_coordinate = old_map.coordinate(self)
        input_x = old_coordinate.x / old_map.size
        input_y = old_coordinate.y / old_map.size
        input_age = self._age / self._max_age
        input = [self._blocked, input_x, input_y, input_age]
        output_x, output_y = self._brain.predict(np.array([input]))[0]
        dx = int(output_x * 2 + 0.5) - 1  # int(float + 0.5) is faster than round(float)
        dy = int(output_y * 2 + 0.5) - 1
        new_coordinate = old_coordinate.relative(dx, dy)
        if old_coordinate != new_coordinate and (old_map.is_occupied(new_coordinate) or new_map.is_occupied(new_coordinate)):
            new_map[old_coordinate] = self
            self._blocked = 1
        else:
            new_map[new_coordinate] = self
            self._blocked = 0
        self._age += 1

    def mate(self, other) -> Organism:
        return self.__class__(self._max_age, self._brain.mate(other._brain))

    def color(self) -> tuple[int, int, int]:
        """Return a color based on the layers."""
        rgb = [(round(self._brain.layers[index][0][0] + 2) * 100) for index in range(3)]
        return (15, 15, 15) if sum(rgb) < 15 else tuple(rgb)
