from random import random

from Organism import *


def display(screen, organism):
    screen.fill(white)

    organism.draw_on(screen, (screen.get_width() / 2, 0))

    pg.display.update()


class Generation:
    def __init__(self, organisms):
        self.organisms = organisms
        self.size = len(self.organisms)

    def run_tests(self):
        for organism in self.organisms:
            organism.fitness = get_walking_distance(organism, 5)

    def sort(self):
        self.organisms.sort(key=lambda o: o.fitness, reverse=True)

    def get_best(self):
        return self.organisms[0]

    def get_median(self):
        return self.organisms[self.size // 2]

    def get_worst(self):
        return self.organisms[-1]

    def get_next_generation(self):
        self.run_tests()
        self.sort()

        new_organisms = []
        for rank in range(self.size):
            probability = (-1.0 / self.size) * rank + 1       # linear decline
            if random() < probability:
                new_organisms.extend(self.organisms[rank].get_children(2))
        print(len(new_organisms))

        size_delta = len(new_organisms) - self.size
        if size_delta < 0:
            for organism in self.organisms[:size_delta]:            # best organisms produce additional children
                new_organisms.extend(organism.get_children(1))
        elif size_delta > 0:
            new_organisms = new_organisms[:self.size]               # worst organisms' children are killed
            #TODO FIX THIS LINE ^^^ its doubling population size

        return Generation(new_organisms)


def get_walking_distance(organism, time_limit):
    clock = pg.time.Clock()
    fps = 60
    tick_limit = fps * time_limit
    tick = 0
    while tick <= tick_limit:
        # clock.tick(fps)
        organism.apply_physics()
        tick += 1

    return max(organism.nodes, key=lambda n: n.pos.x).pos.x


def get_sorted(organisms):
    for org in organisms:
        org.fitness = get_walking_distance(org, 5)
    return sorted(organisms, key=lambda o: o.fitness)[::-1]


if __name__ == "__main__":
    population_size = 1000
    starting_organisms = [Organism() for _ in range(population_size)]
    population = Generation(starting_organisms)

    for i in range(1, 100):
        population = population.get_next_generation()
        print(population.size)
        print("Population {0}: best = {1}    median = {2}    worst = {3}".format(i, population.get_best().fitness, population.get_median().fitness, population.get_worst().fitness))
