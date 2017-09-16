import pygame as pg
from pygame.math import Vector2 as V2
from random import randint, uniform, choice
from itertools import combinations

from Constants import *


def projection(a, b):
    other_length_sqrd = b[0] * b[0] + b[1] * b[1]
    projected_length_times_other_length = a.dot(b)
    return b * (projected_length_times_other_length / other_length_sqrd)


class Organism:
    heartbeat_period = 60

    def __init__(self, num_nodes=None, num_muscles=None):
        if num_nodes:
            self.num_nodes = num_nodes
        else:
            self.num_nodes = randint(3, 6)

        if num_muscles:
            self.num_muscles = num_muscles
        else:
            # bounded by # of sides + # of possible diagonals
            self.num_muscles = randint(self.num_nodes - 1, self.num_nodes - 1 + self.num_nodes * (self.num_nodes - 3) / 2)

        self.nodes = [Node() for _ in range(self.num_nodes)]
        self.muscles = [Muscle() for _ in range(self.num_muscles)]

        all_pairs = list(combinations(self.nodes, 2))
        all_test_sets = combinations(all_pairs, self.num_muscles)
        for test_set in all_test_sets:
            unique_nodes_present = []
            for pair in test_set:
                if pair[0] not in unique_nodes_present:
                    unique_nodes_present.append(pair[0])
                if pair[1] not in unique_nodes_present:
                    unique_nodes_present.append(pair[1])
            if len(unique_nodes_present) == self.num_nodes:
                for i in range(self.num_muscles):
                    self.muscles[i].connect(test_set[i][0])
                    self.muscles[i].connect(test_set[i][1])
                break

        for m in self.muscles:
            dist = m.node_a.pos.distance_to(m.node_b.pos)
            m.min_length = max(dist - 25, 5)
            m.max_length = dist + 25

        # 1 time unit = 1 frame = 1/60th second
        self.heartbeat = 0

    def apply_physics(self):
        # Gravity
        for node in self.nodes:
            node.apply_force(V2(0, -1))

        for muscle in self.muscles:
            if muscle.heartbeat_start <= self.heartbeat <= muscle.heartbeat_start + self.heartbeat_period // 2:
                muscle.contract()
            else:
                muscle.expand()

        for node in self.nodes:
            node.apply_velocity()

        # Ground Collision
        for node in self.nodes:
            if node.pos.y - node.radius <= 0:
                node.pos.y = node.radius
                node.vel.y = 0

        self.heartbeat = (self.heartbeat + 1) % self.heartbeat_period

    def draw_on(self, screen, offset):
        offset = V2(offset)
        for muscle in self.muscles:
            pg.draw.line(screen, black, (muscle.node_a.pos.x, screen.get_height() - muscle.node_a.pos.y) + offset,(muscle.node_b.pos.x, screen.get_height() - muscle.node_b.pos.y) + offset, muscle.width)
        for node in self.nodes:
            pg.draw.circle(screen, node.color, (int(node.pos.x + offset.x), int(screen.get_height() - node.pos.y + offset.y)), node.radius, 0)


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
            self.strength = uniform(0, 0.2)

        if heartbeat_start:
            self.heartbeat_start = heartbeat_start
        else:
            self.heartbeat_start = randint(0, Organism.heartbeat_period // 2 - 1)

        self.node_a, self.node_b = None, None

        self.width = max(int(self.strength ** 0.5 * 10), 1)

    def connect(self, node):
        if self.node_a:
            self.node_b = node
        else:
            self.node_a = node
        node.connections += 1

    def expand(self):
        if self.node_a.pos.distance_to(self.node_b.pos) == 0:
            return
        print("expand")
        if self.node_a.pos.distance_to(self.node_b.pos) <= self.max_length:
            force_a = (self.node_a.pos - self.node_b.pos).normalize() * self.strength / 2 * (self.max_length - self.node_a.pos.distance_to(self.node_b.pos)) / self.max_length
            self.node_a.apply_force(force_a)
            self.node_b.apply_force(-force_a)
        else:
            print("expand limit")
            displacement = self.node_a.pos - self.node_b.pos
            total_mass = self.node_a.mass + self.node_b.mass
            projection_a = projection(self.node_a.vel, displacement)
            projection_b = projection(self.node_b.vel, displacement)

            delta_v = projection_a - projection_b
            delta_s = displacement.normalize() * (displacement.length() - self.max_length)

            self.node_a.vel -= delta_v * (self.node_b.mass / total_mass)
            self.node_b.vel += delta_v * (self.node_a.mass / total_mass)
            self.node_a.pos -= delta_s * (self.node_b.mass / total_mass)
            self.node_b.pos += delta_s * (self.node_a.mass / total_mass)

    def contract(self):
        if self.node_a.pos.distance_to(self.node_b.pos) == 0:
            return
        print("contract")
        if self.node_b.pos.distance_to(self.node_a.pos) >= self.min_length:
            force_a = (self.node_b.pos - self.node_a.pos).normalize() * self.strength / 2 * (self.node_a.pos.distance_to(self.node_b.pos) - self.min_length) / self.min_length
            self.node_a.apply_force(force_a)
            self.node_b.apply_force(-force_a)
        else:
            print("contract limit")
            displacement = self.node_b.pos - self.node_a.pos
            total_mass = self.node_a.mass + self.node_b.mass
            projection_a = projection(self.node_a.vel, displacement)
            projection_b = projection(self.node_b.vel, displacement)

            delta_v = projection_a - projection_b
            delta_s = displacement.normalize() * (self.min_length - displacement.length())

            self.node_a.vel -= delta_v * (self.node_b.mass / total_mass)
            self.node_b.vel += delta_v * (self.node_a.mass / total_mass)
            self.node_a.pos -= delta_s * (self.node_b.mass / total_mass)
            self.node_b.pos += delta_s * (self.node_a.mass / total_mass)

