from Organism import *


def display(screen, organism):
    screen.fill(white)

    organism.draw_on(screen, (screen.get_width() / 2, 0))

    pg.display.update()


screen = pg.display.set_mode((1000, 800))

bob = Organism(3, 3)

clock = pg.time.Clock()
fps = 60
done = False
while not done:
    clock.tick(fps)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 4:
                fps += 1
                print(fps)
            elif event.button == 5:
                if fps > 1:
                    fps -= 1
                print(fps)

    display(screen, bob)

    bob.apply_physics()


pg.quit()