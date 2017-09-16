import pygame as pg
from pygame.math import Vector2 as V2
from random import randint, uniform, choice

from Constants import *


class Organism:
    def __init__(self):
        self.num_nodes = randint(3, 6)
        self.nodes = [Node() for _ in range(self.num_nodes)]

        # bounded by # of sides + # of possible diagonals
        self.num_muscles = randint(self.num_nodes - 1, self.num_nodes - 1 + self.num_nodes * (self.num_nodes - 3) / 2)
        self.muscles = [Muscle() for _ in range(self.num_muscles)]

        # Connect all nodes into a chain (insures all nodes are connected)
        for i in range(self.num_nodes - 1):
            self.muscles[i].connect(self.nodes[i])
            self.muscles[i].connect(self.nodes[i + 1])

        # Connect all remaining muscles to random nodes
        for muscle in self.muscles[self.num_nodes - 1:]:
            nodes_not_connected_to = [n for n in self.nodes if n is not muscle.node_a and n is not muscle.node_b]
            muscle.connect(choice(nodes_not_connected_to))
            muscle.connect(choice(nodes_not_connected_to))

        for m in self.muscles:
            dist = m.node_a.pos.distance_to(m.node_b.pos)
            m.min_length = dist - 25
            m.max_length = dist + 25

        # 1 time unit = 1 frame = 1/60th second
        self.heartbeat = 0
        self.heartbeat_period = 60

    def apply_physics(self):
        for muscle in self.muscles:
            if self.heartbeat < muscle.heartbeat_start:
                muscle.contract()
            else:
                muscle.expand()

        for node in self.nodes:
            node.apply_velocity()
        self.heartbeat = (self.heartbeat + 1) % self.heartbeat_period

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
        self.radius = int(8 * (self.mass ** (1/3)))

        self.vel = V2((0, 0))

    def apply_force(self, force):
        self.vel += force / self.mass

    def apply_velocity(self):
        self.pos += self.vel


class Muscle:
    max_length_delta = 50

    def __init__(self, min_length=None, max_length=None, strength=None, heartbeat_start=None):
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

        if heartbeat_start:
            self.heartbeat_start = heartbeat_start
        else:
            self.heartbeat_start = randint(0, 60)

        self.node_a, self.node_b = None, None

        self.width = max(int(self.strength ** 0.5 * 10), 1)

    def connect(self, node):
        if self.node_a:
            self.node_b = node
        else:
            self.node_a = node
        node.connections += 1

    def expand(self):
        if self.min_length <= self.node_b.pos.distance_to(self.node_a.pos) <= self.max_length:
            force_a = (self.node_b.pos - self.node_a.pos).normalize() * self.strength / 2
            self.node_a.apply_force(force_a)
            self.node_b.apply_force(-force_a)
        else:
            other = self.node_b.pos - self.node_a.pos
            other_length_sqrd = other[0] * other[0] + other[1] * other[1]
            projected_length_times_other_length = self.node_a.vel.dot(other)
            proj = other * (projected_length_times_other_length / other_length_sqrd)

            v = self.node_a.vel - proj
            print(v)

    def contract(self):
        if self.min_length <= self.node_a.pos.distance_to(self.node_b.pos) <= self.max_length:
            force_a = (self.node_a.pos - self.node_b.pos).normalize() * self.strength / 2
            self.node_a.apply_force(force_a)
            self.node_b.apply_force(-force_a)
