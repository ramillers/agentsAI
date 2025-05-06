# agents/cooperative.py

import pygame
import random
from collections import deque
import constantes

class CooperativeAgent:
    """
    Agente utilitário que coopera para coletar recursos do tipo 'estrutura', registrando
    posições no shared_info e usando utilidade para decidir onde atuar.
    """
    def __init__(self, env, x, y, grid, base_x, base_y, obstacles):
        self.env = env
        self.x, self.y = x, y
        self.grid = grid
        self.base_x, self.base_y = base_x, base_y
        self.obstacles = obstacles
        self.color = constantes.COOPERATIVE_COLOR
        self.resources_collected = 0
        self.shared_info = {}
        self.plan = []
        self.target = None
        self.in_storm = False
        self.process = env.process(self.run())

    def utility(self, tx, ty, free_agents):
        dist = abs(tx - self.x) + abs(ty - self.y)
        return 50 / (dist + 1) * (1 if free_agents >= 1 else 0)

    def run(self):
        while True:
            if self.in_storm:
                yield from self.return_to_base()
                self.in_storm = False
            else:
                # Atualiza shared_info com estruturas disponíveis
                E_positions = [(r.x, r.y) for r in self.grid
                               if not r.collected and r.type == 'estrutura']
                for pos in E_positions:
                    self.shared_info[pos] = 'estrutura'

                # Conta agentes livres
                free_agents = sum(1 for a in self.env.agents
                                  if a.id != getattr(self, 'id', None) and getattr(a, 'carrying', None) is None)

                # Seleciona alvo por utilidade
                target = None
                if free_agents and E_positions:
                    utilities = [(pos, self.utility(pos[0], pos[1], free_agents)) for pos in E_positions]
                    target, _ = max(utilities, key=lambda item: item[1])

                # Planeja caminho se necessário
                if target and (target != self.target or not self.plan):
                    self.plan = self.find_path((self.x, self.y), target)
                    self.target = target

                # Executa ação
                if target and (self.x, self.y) == target and free_agents >= 1:
                    # Coleta cooperativa
                    for res in self.grid:
                        if not res.collected and (res.x, res.y) == target:
                            res.collected = True
                            self.resources_collected += res.value
                            self.shared_info[target] = res.type
                            break
                elif self.plan:
                    nx, ny = self.plan.pop(0)
                    self.x, self.y = nx, ny
                else:
                    # Movimento aleatório
                    dx, dy = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
                    self.x = max(0, min(self.x + dx, constantes.GRID_WIDTH - 1))
                    self.y = max(0, min(self.y + dy, constantes.GRID_HEIGHT - 1))

                yield self.env.timeout(1)

    def find_path(self, start, goal):
        queue = deque([start])
        visited = {start: None}
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]
        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == goal:
                break
            for dx, dy in dirs:
                nx, ny = cx + dx, cy + dy
                if (0 <= nx < constantes.GRID_WIDTH and
                    0 <= ny < constantes.GRID_HEIGHT and
                    (nx, ny) not in visited and
                    (nx, ny) not in [(o.x, o.y) for o in self.obstacles]):
                    visited[(nx, ny)] = (cx, cy)
                    queue.append((nx, ny))
        path, node = [], goal
        while node and node != start:
            path.append(node)
            node = visited[node]
        path.reverse()
        return path

    def return_to_base(self):
        while (self.x, self.y) != (self.base_x, self.base_y):
            dx = self.base_x - self.x; dy = self.base_y - self.y
            self.x += 1 if dx > 0 else -1 if dx < 0 else 0
            self.y += 1 if dy > 0 else -1 if dy < 0 else 0
            yield self.env.timeout(1)

    def draw(self, screen): 
        """
        Desenha o agente como um círculo na tela do pygame.
        """
        size = constantes.CELL_SIZE
        rect = pygame.Rect(
            self.x * size + 2,
            self.y * size + 2,
            size - 4,
            size - 4
        )
        pygame.draw.rect(screen, self.color, rect)