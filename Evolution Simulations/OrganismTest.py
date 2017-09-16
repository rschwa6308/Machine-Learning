from Organism import *


def refresh(screen):
    org_a = Organism()
    org_b = Organism()
    org_c = Organism()

    screen.fill(white)

    org_a.draw_on(screen, (100, 400))
    org_b.draw_on(screen, (400, 400))
    org_c.draw_on(screen, (700, 400))

    pg.display.update()

screen = pg.display.set_mode((1000, 800))

refresh(screen)

clock = pg.time.Clock()
done = False
while not done:
    clock.tick(60)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                refresh(screen)

pg.quit()