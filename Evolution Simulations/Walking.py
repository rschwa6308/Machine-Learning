import multiprocessing as mp
import numpy as np
import matplotlib.pyplot as plt
import pandas
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

    def get_species_distribution(self):
        species_list = [org.get_species() for org in self.organisms]
        return dict(sorted([(species, species_list.count(species)) for species in set(species_list)], key=lambda x: x[1], reverse=True))

    def get_next_generation(self):
        new_organisms = []
        for rank in range(self.size):
            probability = (-1.0 / self.size) * rank + 1       # linear decline
            if random() < probability:
                new_organisms.extend(self.organisms[rank].get_children(2))
                # new_organisms.append(self.organisms[rank].get_copy())

        size_delta = len(new_organisms) - self.size
        if size_delta < 0:
            for organism in self.organisms[:-size_delta]:            # best organisms produce additional children
                new_organisms.extend(organism.get_children(1))
        elif size_delta > 0:
            new_organisms = new_organisms[:self.size]               # worst organisms' children are killed

        return Generation(new_organisms)


def get_walking_distance(organism, time_limit):
    # organism.reset_to_start()
    avg = sum([node.pos.x for node in organism.nodes]) / organism.num_nodes
    for node in organism.nodes:
        node.pos.x -= avg
    clock = pg.time.Clock()
    fps = 60
    tick_limit = fps * time_limit
    tick = 0
    while tick <= tick_limit:
        # clock.tick(fps)
        try:
            organism.apply_physics()
        except:
            return 0
        tick += 1
    avg = sum([node.pos.x for node in organism.nodes]) / organism.num_nodes
    if abs(avg) < 1e+10:
        return avg
    return 0


def watch(organism, screen=None):
    if not screen:
        screen = pg.display.set_mode((1000, 500))

    organism.reset_to_start()
    avg = sum([node.pos.x for node in organism.nodes]) / organism.num_nodes
    for node in organism.nodes:
        node.pos.x -= avg

    cam_x = 0
    cam_x_vel = 0
    clock = pg.time.Clock()
    fps = 60
    tick = 0
    max_tick = 60 * 10
    while tick < max_tick:
        clock.tick(fps)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.display.quit()
                return
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    pg.display.quit()
                    return
                elif event.key == pg.K_LEFT:
                    cam_x_vel -= 6
                elif event.key == pg.K_RIGHT:
                    cam_x_vel += 6
            if event.type == pg.KEYUP:
                if event.key == pg.K_LEFT:
                    cam_x_vel = 0
                elif event.key == pg.K_RIGHT:
                    cam_x_vel = 0
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 4:
                    fps += 1
                elif event.button == 5:
                    fps = max(1, fps - 1)

        avg_pos =  sum([node.pos.x for node in organism.nodes]) / organism.num_nodes
        if avg_pos >= screen.get_width() - 200:
            cam_x = int(avg_pos) - screen.get_width() + 200

        cam_x += cam_x_vel
        screen.fill((255, 255, 255))
        for i in range(-1 + cam_x // 100, screen.get_width() // 100 + 1 + cam_x // 100):
            pg.draw.line(screen, (0, 0, 0), (i * 100 - cam_x, 0), (i * 100 - cam_x, screen.get_height()), 2)
        organism.draw_on(screen, (100 - cam_x, 0))
        pg.display.update()

        organism.apply_physics()
        tick += 1

    pg.display.quit()


def display_graphs(history, census, species_distribution, i):
    history_data = pandas.DataFrame(history, columns=["best", "median", "worst"])
    current_data = pandas.DataFrame(census)
    species_data = pandas.Series(list(species_distribution.values()), index=list(species_distribution.keys()), name="")

    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 5))
    history_data.plot(ax=axes[0])
    axes[0].set_title("History")
    current_data.hist(bins=30, ax=axes[1])
    axes[1].set_title("Generation {0} Distances".format(i))
    species_data.plot.pie(ax=axes[2])
    axes[2].set_title("Generation {0} Species".format(i))
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    population_size = 500
    starting_organisms = [Organism() for _ in range(population_size)]
    population = Generation(starting_organisms)

    history = []

    for i in range(0, 100000000000000):
        population.run_tests()
        population.sort()

        best, median, worst = population.get_best(), population.get_median(), population.get_worst()
        species_distribution = population.get_species_distribution()

        print("Generation {0}: best = {1}    median = {2}    worst = {3}    species = {4}".format(
            i, round(best.fitness, 3), round(median.fitness, 3), round(worst.fitness, 3), species_distribution)
        )

        history.append([best.fitness, median.fitness, worst.fitness])
        census = [org.fitness for org in population.organisms]

        graph_process = mp.Process(target=display_graphs, args=(history, census, species_distribution, i))
        graph_process.start()

        watch(best)
        graph_process.terminate()
        population = population.get_next_generation()
