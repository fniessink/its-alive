"""Main program."""

from collections.abc import Callable
import math
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
        for wall in map.walls:
            draw.line((wall[0][0]*2, wall[0][1] * 2, wall[1][0] * 2, wall[1][1] * 2), fill=(255, 255, 255))
        for coordinate in map.coordinates():
            organism = map[coordinate]
            x, y = coordinate.x * 2, coordinate.y * 2
            draw.ellipse([(x-2, y-2), (x+2, y+2)], fill=organism.color())
        return image


class Generation:
    """Class representing a generation of organisms."""

    def __init__(self, map: Map[Organism], organisms: set[Organism], ticks: int, listener: MapSequenceListener = None) -> None:
        map.place_randomly(organisms)
        self._map = map
        self._ticks = ticks
        self._listener = listener

    def run(self) -> None:
        """Iterate over all organisms and make them do their thing."""
        map = self._map
        for _ in range(self._ticks):
            if self._listener:
                self._listener.notify(map, last=False)
            new_map = map.empty_copy()
            for organism in map.items():
                organism.tick(map, new_map)
            map = new_map
        self._map = map
        if self._listener:
            self._listener.notify(map, last=True)

    def evaluated(self, evaluation_function: Callable) -> tuple[list[Organism], list[float], float]:
        """Return the organisms ordered by the evaluation function."""
        return evaluation_function(self._map)


def center(map: Map[Organism]) -> tuple[list[Organism], list[float], float]:
    """Return the organisms that are closest to the center."""
    center_x = center_y = map.size / 2

    def distance_to_center(organism: Organism) -> float:
        return (center_x - map.coordinate(organism).x)**2 + (center_y - map.coordinate(organism).y)**2

    # Include the index in the decorated list because organisms are not sortable
    decorated = [(distance_to_center(organism), index, organism) for index, organism in enumerate(map.items())]
    decorated.sort()
    decorated = decorated[:len(decorated) // 2]  # Keep the best half
    distances = [item[0] for item in decorated]
    max_distance = max(distances)
    weights = [max_distance - distance for distance in distances]
    organisms = [item[2] for item in decorated]
    return organisms, weights, sum(distances) / len(distances)


if __name__ == '__main__':
    population_size = 200
    ticks = 300
    organisms = set([Organism(ticks) for _ in range(population_size)])
    for index in range(100_000):
        map: Map[Organism] = Map(200)
        listener = MapSequenceListener(index) if index % 100 == 0 else None
        generation = Generation(map, organisms, ticks, listener)
        generation.run()
        evaluated_organisms, weights, score = generation.evaluated(center)
        print(f"Generation {index}: {round(score, 1)}")
        organisms = set()
        while len(organisms) < population_size:
            parent1, parent2 = random.choices(evaluated_organisms, weights=weights, k=2)
            organisms.add(parent1.mate(parent2))
