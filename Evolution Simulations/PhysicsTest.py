from Organism import *


def display(screen, organism):
    screen.fill(white)

    organism.draw_on(screen, (screen.get_width() / 2, 0))

    pg.display.update()


screen = pg.display.set_mode((1000, 800))

bob = Organism()

clock = pg.time.Clock()
done = False
while not done:
    clock.tick(60)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True

    display(screen, bob)

    bob.apply_physics()


pg.quit()