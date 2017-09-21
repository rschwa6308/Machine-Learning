from Organism import *


def display(screen, organism):
    screen.fill(white)

    organism.draw_on(screen, (screen.get_width() / 2, 0))

    pg.display.update()


screen = pg.display.set_mode((1000, 800))

bob = Organism(6)
##bob.nodes = [Node(5, (-100, 20), 1.0), Node(1, (0, 100), 0.1), Node(5, (100, 20), 0.1)]
##bob.muscles = [Muscle(100, 150, 0.1), Muscle(100, 150, 0.1), Muscle(100, 150, 0.1)]
##for i in range(len(bob.muscles)):
##    bob.muscles[i].connect(bob.nodes[i])
##    bob.muscles[i].connect(bob.nodes[(i + 1)%len(bob.muscles)])

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
                bob = Organism(6)

    display(screen, bob)

    bob.apply_physics()


pg.quit()
