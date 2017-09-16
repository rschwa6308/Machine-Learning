import pygame as pg
from pygame.math import Vector2 as V2
from random import randint, uniform, choice

from Constants import *


class Organism:
    def __init__(self):
        self.num_nodes = randint(3, 6)
        self.nodes = [Node() for _ in range(self.num_nodes)]

        # bounded by # of possible diagonals
        if self.num_nodes <= 4:
            self.num_muscles = randint(self.num_nodes * (self.num_nodes - 3) / 2, self.num_nodes - 1)
        else:
            self.num_muscles = randint(self.num_nodes - 1, self.num_nodes * (self.num_nodes - 3) / 2)
        self.muscles = [Muscle() for _ in range(self.num_muscles)]

        # # Connect all nodes into a chain (insures all nodes are connected)
        # for i in range(len(self.nodes) - 2):
        #     self.muscles[i].connect(self.nodes[i], self.nodes[i + 1])
        #
        # # Connect all remaining muscles to random nodes
        # for i in range(len(self.nodes) - 1, self.num_muscles):
        #     self.muscles[i].connect(choice(self.nodes), choice(self.nodes))
        for _ in range(2):
            for muscle in self.muscles:
                for node in sorted(self.nodes, key=lambda n: 0 if n.connections == 0 else randint(1, 1000)):
                    muscle.connect(node)

    def draw_on(self, screen, offset):
        offset = V2(offset)
        for muscle in self.muscles:
            pg.draw.line(screen, black, muscle.node_a.pos + offset, muscle.node_b.pos + offset, muscle.width)
        for node in self.nodes:
            pg.draw.circle(screen, node.color, (int(node.pos.x + offset.x), int(node.pos.y + offset.y)), node.radius, 0)


class Node:
    def __init__(self, mass=None, pos=None, friction=None):
        if mass:
            self.mass = mass
        else:
            self.mass = uniform(1, 5)

        if pos:
            self.pos = V2(pos)
        else:
            self.pos = V2(uniform(0, 200), uniform(0, 200))

        if friction:
            self.friction = friction
        else:
            self.friction = uniform(0, 1)

        self.connections = 0

        self.color = (int(self.friction * 255), 0, int((1 - self.friction) * 255))
        self.radius = int(10 * (self.mass ** (1/3)))


class Muscle:
    max_length_delta = 50

    def __init__(self, min_length=None, max_length=None, strength=None):
        if min_length:
            self.min_length = min_length
        else:
            self.min_length = uniform(10, 50)

        if max_length:
            self.max_length = max_length
        else:
            self.max_length = uniform(self.min_length, self.min_length + self.max_length_delta)

        if strength:
            self.strength = strength
        else:
            # 1 force unit = 1 mass unit * pixel / frame ^ 2
            self.strength = uniform(0, 1)

        self.node_a, self.node_b = None, None

        self.width = int(self.strength * 10)

    def connect(self, node):
        if self.node_a:
            self.node_b = node
        else:
            self.node_a = node
        node.connections += 1
