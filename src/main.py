"""Main program."""

from collections.abc import Callable, Iterator
import threading

from PIL import Image, ImageDraw

from creature import Creature
from map import Map


class MapSequenceListener:
    """Class listening for generation ticks."""
    def __init__(self) -> None:
        self._maps = []

    def add_map(self, map: Map[Creature]) -> None:
        self._maps.append(map)

    def finish(self) -> None:
        print("Starting thread")
        thread = threading.Thread(target=self._create_animated_gif)
        thread.start()

    def _create_animated_gif(self) -> None:
        """Create an animated gif from the maps."""
        images = [self._create_image(map) for map in self._maps]
        images[0].save("generation.gif", append_images=images[1:], save_all=True, duration=100, loop=0)

    @staticmethod
    def _create_image(map: Map[Creature]) -> Image:
        """Transform a map into an image."""
        image = Image.new("RGB", (map.size, map.size), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.point([(coordinate.x, coordinate.y) for coordinate in map.coordinates()], fill=(0, 0, 0))
        return image


class Generation:
    """Class representing a generation of creatures."""

    def __init__(self, map: Map[Creature], creatures: set[Creature], listener: MapSequenceListener, ticks=1000) -> None:
        map.place_randomly(creatures)
        self._map = map
        self._ticks = ticks
        self._listener = listener

    def run(self) -> None:
        """Iterate over all creatures and make them do their thing."""
        map = self._map
        for _ in range(self._ticks):
            new_map = map.empty_copy()
            for creature in map.items():
                creature.tick(map, new_map)
            map = new_map
            self._listener.add_map(map)
        self._map = new_map
        self._listener.finish()

    def survivors(self, evaluation_function: Callable) -> set[Creature]:
        """Return a subset of the creatures that survive, given the evaluation function."""
        return set(evaluation_function(self._map))


def has_neighbors(map: Map[Creature], min_neighbors=0, max_neighbors=3) -> Iterator[Creature]:
    """Return the creatures that have a neighbor."""
    for creature in map.items():
        if min_neighbors < len(list(map.neighbors(creature))) < max_neighbors:
            yield creature


if __name__ == '__main__':
    map: Map[Creature] = Map(200)
    creatures = set([Creature() for _ in range(250)])
    generation = Generation(map, creatures, MapSequenceListener())
    generation.run()
