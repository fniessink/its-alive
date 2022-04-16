"""Map class."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from random import randint

from typing import Generic, TypeVar


class Coordinate:
    """Coordinates in a square 2D world without edges."""

    def __init__(self, x: int, y: int, size: int = 0) -> None:
        self.x = x
        self.y = y
        self._size = size

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def relative(self, dx: int, dy: int) -> Coordinate:
        """Return the coordinate relative to this one."""
        return self.__class__((self.x + dx) % self._size, (self.y + dy) % self._size, self._size)

    def neighbors(self) -> Iterator[Coordinate]:
        """Return the neighboring coordinates."""
        delta = (-1, 0, 1)
        for dx in delta:
            for dy in delta:
                if dx == 0 and dy == 0:
                    continue
                yield self.relative(dx, dy)


T = TypeVar("T")


class Map(Generic[T]):
    """Map of the world."""

    def __init__(self, size: int) -> None:
        self.size = size
        self._coordinates: dict[Coordinate, T] = {}

    def __str__(self):
        result = []
        for x in range(self.size):
            for y in range(self.size):
                result.append("x" if self.is_occupied(Coordinate(x, y)) else " ")
            result.append("\n")
        return "".join(result)

    def __setitem__(self, coordinate: Coordinate, item: T) -> None:
        """Put the item on the coordinate. Raises KeyError if coordinate is occupied."""
        if coordinate in self._coordinates:
            raise KeyError(f"Coordinate {coordinate} already occupied")
        self._coordinates[coordinate] = item

    def __getitem__(self, coordinate: Coordinate) -> T:
        """Return the item on the coordinate. Raises KeyError if no item is on the coordinate."""
        return self._coordinates[coordinate]

    def empty_copy(self) -> Map[T]:
        """Return an empty copy of the map."""
        return self.__class__(self.size)

    def place_randomly(self, items: set[T]) -> None:
        """Place the items randomly on the map."""
        for item in items:
            self._coordinates[self.random_coordinate()] = item

    def is_occupied(self, coordinate: Coordinate) -> bool:
        """Return whether the coordinate is occupied."""
        return coordinate in self._coordinates

    def items(self) -> Sequence[T]:
        """Return all the items on the map."""
        return list(self._coordinates.values())

    def neighbors(self, item: T) -> Iterator[T]:
        """Return the neighbors of the item, if any."""
        for coordinate in self.coordinate(item).neighbors():
            if self.is_occupied(coordinate):
                yield self[coordinate]

    def coordinates(self):
        """Return all coordinates with items."""
        return self._coordinates.keys()

    def coordinate(self, item: T) -> Coordinate:
        """Return the coordinate of the item."""
        for coordinate, i in self._coordinates.items():
            if item == i:
                return coordinate
        raise LookupError(f"Could not find the coordinates of {item}")

    def random_coordinate(self) -> Coordinate:
        """Return a random, non-occupied coordinate."""
        size = self.size
        while self.is_occupied(coordinate := Coordinate(randint(0, size - 1), randint(0, size - 1), size)):
            pass
        return coordinate
