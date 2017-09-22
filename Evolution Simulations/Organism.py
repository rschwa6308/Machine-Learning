import pygame as pg
from pygame.math import Vector2 as V2
from random import randint, uniform, choice
from itertools import combinations
from math import copysign
from copy import copy, deepcopy

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
            self.num_nodes = randint(3, 7)

        if num_muscles:
            self.num_muscles = num_muscles
        else:
            # bounded by # of sides + # of possible diagonals
            self.num_muscles = randint(self.num_nodes - 1,
                                       self.num_nodes - 1 + self.num_nodes * (self.num_nodes - 3) / 2)

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
            m.desired_length = dist
            m.min_length = m.desired_length * 0.5
            m.max_length = m.desired_length * 1.5

        # Set on ground
        delta_y = min([node.pos.y for node in self.nodes])
        for node in self.nodes:
            node.pos.y -= delta_y

        # 1 time unit = 1 frame = 1/60th second
        self.heartbeat = 0

        self.starting_positions = {node: (node.pos.x, node.pos.y) for node in self.nodes}

    def apply_physics(self):
        g = 1
        # Gravity
        for node in self.nodes:
            node.apply_force(V2(0, -g))

        # Ground Collision
        for node in self.nodes:
            if node.pos.y - node.radius <= 0:
                node.pos.y = node.radius
                node.vel.y = 0
                # TODO: make friction force proportional to total normal force on node
                friction_force = V2(-copysign(node.friction * node.mass * g, node.vel.x), 0)
                node.apply_force(friction_force)

        for muscle in self.muscles:
            if muscle.heartbeat_start <= self.heartbeat <= muscle.heartbeat_start + self.heartbeat_period // 2:
                muscle.contract()
            else:
                muscle.expand()
                # muscle.passive()

        for node in self.nodes:
            node.apply_velocity()

        self.heartbeat = (self.heartbeat + 1) % self.heartbeat_period

    def draw_on(self, screen, offset):
        offset = V2(offset)
        for muscle in self.muscles:
            pg.draw.line(screen, black, (muscle.node_a.pos.x, screen.get_height() - muscle.node_a.pos.y) + offset,
                         (muscle.node_b.pos.x, screen.get_height() - muscle.node_b.pos.y) + offset, muscle.width)
        for node in self.nodes:
            pg.draw.circle(screen, node.color,
                           (int(node.pos.x + offset.x), int(screen.get_height() - node.pos.y + offset.y)), node.radius,
                           0)

    def reset_to_start(self):
        for node in self.nodes:
            node.pos = V2(self.starting_positions[node])
        for muscle in self.muscles:
            dist = muscle.node_a.pos.distance_to(muscle.node_b.pos)
            muscle.desired_length = dist

    def get_copy(self):
        new_organism = Organism(self.num_nodes, self.num_muscles)
        self.reset_to_start()
        node_map = {old_node: old_node.get_copy() for old_node in self.nodes}
        new_organism.muscles = [m.get_copy() for m in self.muscles]
        for i in range(self.num_muscles):
            old = self.muscles[i]
            new = new_organism.muscles[i]
            new.node_a = node_map[old.node_a]
            new.node_b = node_map[old.node_b]
        new_organism.nodes = node_map.values()
        new_organism.starting_positions = {node: (node.pos.x, node.pos.y) for node in new_organism.nodes}
        return new_organism

    def get_children(self, quanitiy):
        new_organisms = []
        for _ in range(quanitiy):
            new_organism = self.get_copy()

            new_organism.reset_to_start()
            for node in new_organism.nodes:
                node.pos.x += uniform(-5, 5)
                node.pos.y += uniform(-5, 5)
                node.friction = max(0, node.friction + uniform(-0.05, 0.05))

            for muscle in new_organism.muscles:
                muscle.max_length += uniform(-2, 2)
                muscle.min_length += uniform(-2, 2)
                muscle.strength = max(0, muscle.strength, uniform(-0.001, 0.001))
                muscle.speed = max(0, muscle.speed + uniform(-0.05, 0.05))
                muscle.heartbeat_start += randint(-2, 2)

            new_organism.starting_positions = {node: (node.pos.x, node.pos.y) for node in new_organism.nodes}

            new_organisms.append(new_organism)
        return new_organisms


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
        self.radius = int(8 * (self.mass ** (1 / 3)))

        self.vel = V2((0, 0))

    def get_copy(self):
        return Node(self.mass, (self.pos.x, self.pos.y), self.friction)

    def apply_force(self, force):
        self.vel += force / self.mass

    def apply_velocity(self):
        self.pos += self.vel


class Muscle:
    max_length_delta = 50

    def __init__(self, min_length=None, max_length=None, strength=None, speed=None, heartbeat_start=None):
        if min_length:
            self.min_length = min_length
        else:
            self.min_length = uniform(10, 50)

        if max_length:
            self.max_length = max_length
        else:
            self.max_length = uniform(self.min_length, self.min_length + self.max_length_delta)

        self.desired_length = (self.min_length + self.max_length) / 2

        if strength:
            self.strength = strength
        else:
            # 1 force unit = 1 mass unit * pixel / frame ^ 2
            self.strength = uniform(0, 0.3)

        if speed:
            self.speed = speed
        else:
            self.speed = uniform(0, 1)

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

    def get_copy(self):
        return Muscle(self.min_length, self.max_length, self.strength, self.speed, self.heartbeat_start)

    def passive(self):
        displacement = self.node_b.pos - self.node_a.pos
        # stretch_factor = displacement.length() / self.mid_length
        stretch_length = displacement.length() - self.desired_length
        force_a = displacement.normalize() * self.strength * stretch_length
        self.node_a.apply_force(force_a)
        self.node_b.apply_force(-force_a)

    def expand(self):
        if self.desired_length < self.max_length:
            self.desired_length += self.speed
        self.passive()

    def contract(self):
        if self.desired_length > self.min_length:
            self.desired_length -= self.speed
        self.passive()
