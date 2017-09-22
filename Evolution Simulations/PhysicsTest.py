from Organism import *


def display(screen, organism):
    screen.fill(white)

    organism.draw_on(screen, (screen.get_width() / 2, 0))

    pg.display.update()


screen = pg.display.set_mode((1000, 800))

bob = Organism(4, 6)


clock = pg.time.Clock()
fps = 60
done = False
while not done:
    clock.tick(fps)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 4:
                fps += 1
                print(fps)
            elif event.button == 5:
                if fps > 1:
                    fps -= 1
                print(fps)
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                bob = bob.get_children(1)[0]
            if event.key == pg.K_r:
                bob = Organism(4, 6)

    display(screen, bob)

    bob.apply_physics()


pg.quit()
