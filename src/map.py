"""Map class."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from random import randint

from typing import Generic, TypeVar


@dataclass(slots=True)
class Coordinate:
    """Coordinates in a square 2D world without edges."""

    x: int
    y: int
    _hash: int = 0

    def __post_init__(self) -> None:
        self._hash = hash((self.x, self.y))

    def __eq__(self, other) -> bool:
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self) -> int:
        return self._hash

    def relative(self, dx: int, dy: int) -> Coordinate:
        """Return the coordinate relative to this one."""
        return self.__class__((self.x + dx), (self.y + dy))


T = TypeVar("T")


class Map(Generic[T]):
    """Map of the world."""

    def __init__(self, size: int) -> None:
        self.size = size
        self._coordinates: dict[Coordinate, T] = {}
        self._items: dict[T, Coordinate] = {}

    def __setitem__(self, coordinate: Coordinate, item: T) -> None:
        """Put the item on the coordinate. Raises KeyError if coordinate is occupied."""
        if coordinate in self._coordinates:
            raise KeyError(f"Coordinate {coordinate} already occupied")
        self._coordinates[coordinate] = item
        self._items[item] = coordinate

    def __getitem__(self, coordinate: Coordinate) -> T:
        """Return the item on the coordinate. Raises KeyError if no item is on the coordinate."""
        return self._coordinates[coordinate]

    def empty_copy(self) -> Map[T]:
        """Return an empty copy of the map."""
        return self.__class__(self.size)

    def place_randomly(self, items: set[T]) -> None:
        """Place the items randomly on the map."""
        for item in items:
            self[self.random_coordinate()] = item

    def is_occupied(self, coordinate: Coordinate) -> bool:
        """Return whether the coordinate is occupied."""
        x, y, size = coordinate.x, coordinate.y, self.size
        return x < 0 or y < 0 or x >= size or y >= self.size or coordinate in self._coordinates

    def items(self) -> Sequence[T]:
        """Return all the items on the map."""
        return list(self._coordinates.values())

    def coordinates(self):
        """Return all coordinates with items."""
        return self._coordinates.keys()

    def coordinate(self, item: T) -> Coordinate:
        """Return the coordinate of the item."""
        return self._items[item]

    def random_coordinate(self) -> Coordinate:
        """Return a random, non-occupied coordinate."""
        size = self.size
        while self.is_occupied(coordinate := Coordinate(randint(0, size - 1), randint(0, size - 1))):
            pass
        return coordinate
