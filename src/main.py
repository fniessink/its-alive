"""Main program."""

from collections.abc import Callable, Iterator
import random
import threading

from PIL import Image, ImageDraw

from organism import Organism
from map import Map


class MapSequenceListener:
    """Class listening for generation ticks."""
    def __init__(self, index: int) -> None:
        self._maps = []
        self._index = index

    def notify(self, map: Map[Organism], last: bool) -> None:
        if self._index % 10 != 0:
            return
        self._maps.append(map)
        if last:
            thread = threading.Thread(target=self._create_animated_gif)
            thread.start()

    def _create_animated_gif(self) -> None:
        """Create an animated gif from the maps."""
        images = [self._create_image(map) for map in self._maps]
        images[0].save(f"generation_{self._index:06}.gif", append_images=images[1:], save_all=True, duration=100, loop=0)

    @staticmethod
    def _create_image(map: Map[Organism]) -> Image:
        """Transform a map into an image."""
        image = Image.new("RGB", (map.size * 2, map.size * 2), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        for coordinate in map.coordinates():
            organism = map[coordinate]
            x, y = coordinate.x * 2, coordinate.y * 2
            draw.ellipse([(x-2, y-2), (x+2, y+2)], fill=organism.color())
        return image


class Generation:
    """Class representing a generation of organisms."""

    def __init__(self, map: Map[Organism], organisms: set[Organism], listener: MapSequenceListener = None, ticks=400) -> None:
        map.place_randomly(organisms)
        self._map = map
        self._ticks = ticks
        self._listener = listener

    def run(self) -> None:
        """Iterate over all organisms and make them do their thing."""
        map = self._map
        for _ in range(self._ticks):
            self._listener.notify(map, last=False)
            new_map = map.empty_copy()
            for organism in map.items():
                organism.tick(map, new_map)
            map = new_map
        self._map = map
        self._listener.notify(map, last=True)

    def survivors(self, evaluation_function: Callable) -> list[Organism]:
        """Return a subset of the organisms that survive, given the evaluation function."""
        return list(evaluation_function(self._map))


def left(map: Map[Organism]) -> Iterator[Organism]:
    """Return the organisms that are on the left."""
    boundary = map.size / 2
    for organism in map.items():
        if map.coordinate(organism).x < boundary:
            yield organism


def center(map: Map[Organism]) -> Iterator[Organism]:
    """Return the organisms that are in the center."""
    boundary1, boundary2 = map.size * 1 / 3, map.size * 2 / 3
    for organism in map.items():
        coordinate = map.coordinate(organism)
        if boundary1 < coordinate.x < boundary2 and boundary1 < coordinate.y < boundary2:
            yield organism


if __name__ == '__main__':
    population_size = 200
    organisms = set([Organism() for _ in range(population_size)])
    for index in range(100_000):
        map: Map[Organism] = Map(250)
        generation = Generation(map, organisms, MapSequenceListener(index))
        generation.run()
        survivors = generation.survivors(center)
        nr_survivors = len(survivors)
        print(f"Generation {index}: {nr_survivors} survivors")
        if nr_survivors < 2:
            print("Too few survivors left, giving up")
            break
        organisms = set()
        while len(organisms) < population_size:
            index1, index2 = random.randint(0, nr_survivors-1), random.randint(0, nr_survivors-1)
            organisms.add(survivors[index1].mate(survivors[index2]))
