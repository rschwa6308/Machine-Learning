import pygame as pg
from time import time, sleep
from random import randint

from Colors import *
from Images import *


class Bird:
    cooldown = 0.2
    rect_buffer = 2         # Higher rect_buffer gives higher collision tolerance (more forgiving)

    def __init__(self, y_pos):
        self.y_pos = y_pos
        self.y_vel = 0
        self.jump_timestamp = 0.0
        self.image = bird_image
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def get_rect(self):
        return pg.Rect(50 + self.rect_buffer, self.y_pos + self.rect_buffer, self.width - self.rect_buffer * 2,
                       self.height - self.rect_buffer * 2)


class Pipe:
    pipe_width = 75
    gap = 200

    def __init__(self, x_pos, screen_height):
        self.x_pos = x_pos
        self.y_pos = randint(self.gap, screen_height - self.gap)
        self.rect_top = pg.Rect(0, 0, self.pipe_width, self.y_pos - self.gap / 2)
        self.rect_bottom = pg.Rect(0, self.y_pos + self.gap / 2, self.pipe_width,
                                   screen_height - (self.y_pos + self.gap / 2))
        self.image = pg.Surface((self.pipe_width, screen_height))
        self.image.fill(bg_color)
        pg.draw.rect(self.image, pipe_color, self.rect_top, 0)
        pg.draw.rect(self.image, pipe_color, self.rect_bottom, 0)

    def get_rect_top(self):
        self.rect_top.x = self.x_pos
        return self.rect_top

    def get_rect_bottom(self):
        self.rect_bottom.x = self.x_pos
        return self.rect_bottom


def display(screen, pipes, bird, score):
    # Clear previous frame
    screen.fill(bg_color)

    # Draw Pipes
    for pipe in pipes:
        screen.blit(pipe.image, (pipe.x_pos, 0))

    # Render Score Text
    img = score_font.render("Score: " + str(score), True, black)
    screen.blit(img, (20, 20))

    # Draw Bird
    screen.blit(bird.image, (50, bird.y_pos))

    pg.display.update()


def main():
    width, height = 1000, 800
    pipe_spacing = 300

    # Instantiate game objects
    pipes = [Pipe(300 + pipe_spacing * n, height) for n in range(int(width / pipe_spacing) + 1)]
    bird = Bird(height / 2)
    score = 0

    # Initialize display
    screen = pg.display.set_mode((width, height))
    pg.display.set_caption("Flappy Bird")

    # Main Game Loop
    clock = pg.time.Clock()
    done = False
    while not done:
        clock.tick(60)

        display(screen, pipes, bird, score)

        # Listen for user input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                done = True
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if time() - bird.jump_timestamp > bird.cooldown:
                        bird.jump_timestamp = time()
                        bird.y_vel = -7

        # Exert Gravity (with terminal velocity)
        if bird.y_vel < 20:
            bird.y_vel += 0.3

        # Apply Velocity
        bird.y_pos += bird.y_vel

        # Move Pipes
        for pipe in pipes:
            if pipe.x_pos + pipe.pipe_width < 0:
                pipes.remove(pipe)
                pipes.append(Pipe(pipes[-1].x_pos + pipe_spacing, height))
                del pipe
            else:
                pipe.x_pos -= 2

        for pipe in pipes:
            # Increment Score
            if pipe.x_pos == 50:
                score += 1

            # Pipe - Bird Collision
            bird_rect = bird.get_rect()
            if pipe.get_rect_top().colliderect(bird_rect):
                sleep(2)
                pg.quit()
                done = True
            elif pipe.get_rect_bottom().colliderect(bird_rect):
                sleep(2)
                pg.quit()
                done = True

        if bird.y_pos + bird.height > height:
            sleep(2)
            pg.quit()
            done = True


if __name__ == "__main__":
    main()
