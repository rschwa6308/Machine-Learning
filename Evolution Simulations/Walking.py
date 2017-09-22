from random import random

from Organism import *


def display(screen, organisms):
    screen.fill(white)

    for i in range(len(organisms)):
        organisms[i].draw_on(screen, (100 + 300 * i, -200))

    pg.display.update()


class Generation:
    def __init__(self, organisms):
        self.organisms = organisms
        self.size = len(self.organisms)

    def run_tests(self):
        for organism in self.organisms:
            organism.reset_to_start()
            organism.fitness = get_walking_distance(organism, 10)
            organism.reset_to_start()

    def sort(self):
        self.organisms.sort(key=lambda o: o.fitness, reverse=True)

    def get_best(self):
        return self.organisms[0]

    def get_median(self):
        return self.organisms[self.size // 2]

    def get_worst(self):
        return self.organisms[-1]

    def get_next_generation(self):
        new_organisms = []
        for rank in range(self.size):
            probability = (-1.0 / self.size) * rank + 1       # linear decline
            if random() < probability:
                new_organisms.extend(self.organisms[rank].get_children(2))
                # new_organisms.extend(self.organisms[rank].get_children(1))
                # new_organisms.append(self.organisms[rank].get_copy())

        size_delta = len(new_organisms) - self.size
        if size_delta < 0:
            for organism in self.organisms[:-size_delta]:            # best organisms produce additional children
                new_organisms.extend(organism.get_children(1))
        elif size_delta > 0:
            new_organisms = new_organisms[:self.size]               # worst organisms' children are killed

        return Generation(new_organisms)


def get_walking_distance(organism, time_limit):
    avg = sum([node.pos.x for node in organism.nodes]) / organism.num_nodes
    for node in organism.nodes:
        node.pos.x -= avg
    clock = pg.time.Clock()
    fps = 60
    tick_limit = fps * time_limit
    tick = 0
    while tick <= tick_limit:
        # clock.tick(fps)
        organism.apply_physics()
        tick += 1

    return sum([node.pos.x for node in organism.nodes]) / organism.num_nodes


def watch(screen, organism):
    avg = sum([node.pos.x for node in organism.nodes]) / organism.num_nodes
    for node in organism.nodes:
        node.pos.x -= avg

    cam_x = 0
    cam_x_vel = 0
    clock = pg.time.Clock()
    tick = 0
    max_tick = 60 * 10
    while tick < max_tick:
        clock.tick(60)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    screen.fill((255, 255, 255))
                    pg.display.update()
                    return
                elif event.key == pg.K_LEFT:
                    cam_x_vel -= 1
                elif event.key == pg.K_RIGHT:
                    cam_x_vel += 1
            if event.type == pg.KEYUP:
                if event.key == pg.K_LEFT:
                    cam_x_vel = 0
                elif event.key == pg.K_RIGHT:
                    cam_x_vel = 0
        cam_x += cam_x_vel
        screen.fill((255, 255, 255))
        for i in range(-10, 10):
            pg.draw.line(screen, (0, 0, 0), (i * 100 - cam_x, 0), (i * 100 - cam_x, screen.get_height()), 2)
        organism.draw_on(screen, (100 - cam_x, 0))
        pg.display.update()
        organism.apply_physics()
        tick += 1
    screen.fill((255, 255, 255))
    pg.display.update()


if __name__ == "__main__":
    screen = pg.display.set_mode((1000, 500))

    population_size = 500
    starting_organisms = [Organism() for _ in range(population_size)]
    for o in starting_organisms:
        print(o.num_nodes)
    population = Generation(starting_organisms)

    for i in range(1, 100000000000000):
        population.run_tests()
        population.sort()
        best, median, worst = population.get_best(), population.get_median(), population.get_worst()
        print("Population {0}: best = {1}    median = {2}    worst = {3}".format(i, best.fitness, median.fitness, worst.fitness))
        # display(screen, [best, median, worst])
        watch(screen, best)
        population = population.get_next_generation()
