# recursos.py

import random
import pygame
import constantes

class Resource:
    def __init__(self, id, type, x, y):
        self.id = id
        self.type = type
        self.x = x
        self.y = y
        self.required_agents = constantes.REQUIRED_AGENTS[type]
        self.value = constantes.RESOURCE_VALUES[type]
        self.collected = False

    def draw(self, screen):
        cell = constantes.cell_size
        px = self.x * cell + cell // 2
        py = self.y * cell + cell // 2
        color = {
            'cristal': constantes.CRYSTAL_COLOR,
            'metal': constantes.METAL_COLOR,
            'estrutura': constantes.STRUCTURE_COLOR
        }.get(self.type, (255, 255, 255))
        pygame.draw.circle(screen, color, (px, py), cell // 2 - 2)

class Obstacle:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

    def draw(self, screen):
        cell = constantes.CELL_SIZE
        px = self.x * cell + cell // 2
        py = self.y * cell + cell // 2
        color = {
            'cristal': constantes.CRYSTAL_COLOR,
            'metal':   constantes.METAL_COLOR,
            'estrutura': constantes.STRUCTURE_COLOR
        }[self.type]
        radius = cell // 4    # era `cell // 2 - 2`
        pygame.draw.circle(screen, color, (px, py), radius)


def create_resources():
    resources = []
    positions = set()
    id_counter = 1
    for kind, count in [
        ('cristal', constantes.NUM_CRYSTALS),
        ('metal', constantes.NUM_METAL),
        ('estrutura', constantes.NUM_STRUCTURES)
    ]:
        for _ in range(count):
            while True:
                x = random.randrange(constantes.grid_width)
                y = random.randrange(constantes.grid_height)
                if (x, y) != constantes.BASE_POS and (x, y) not in positions:
                    positions.add((x, y))
                    break
            resources.append(Resource(id_counter, kind, x, y))
            id_counter += 1
    return resources


def create_obstacles():
    # Se desejar obstáculos estáticos, instancie aqui; senão, retorna lista vazia
    return []
