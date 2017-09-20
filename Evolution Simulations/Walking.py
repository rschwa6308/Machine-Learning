from Organism import *


def display(screen, organism):
    screen.fill(white)

    organism.draw_on(screen, (screen.get_width() / 2, 0))

    pg.display.update()


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
        org.fittness = get_walking_distance(org, 5)
    return sorted(organisms, key=lambda o: o.fittness)[::-1]


if __name__ == "__main__":
    orgnanisms = [Organism() for _ in range(100)]
    for i in range(len(orgnanisms)):
        orgnanisms[i].name = "organism {}".format(str(i))
    sorted_organisms = get_sorted(orgnanisms)
    for o in sorted_organisms:
        print(o.name, o.fittness)
