import pygame
from collections import deque
import constantes

class GoalBasedAgent:
    """
    Agente baseado em objetivos. Recebe objetivos do BDI via shared_info
    quando está na base, segue até o objetivo e coleta. Não pondera valor.
    """
    def __init__(self, env, x, y, grid, base_x, base_y, obstacles):
        self.env = env
        self.x, self.y = x, y
        self.grid = grid
        self.base_x, self.base_y = base_x, base_y
        self.obstacles = obstacles
        self.color = constantes.STRUCTURE_COLOR
        self.resources_collected = 0
        self.shared_info = {} # Atualizado pelo BDI na base
        self.plan = []
        self.target = None
        self.in_storm = False
        self.carrying = None
        self.process = env.process(self.run())

    def find_path(self, start, goal):
        q = deque([start])
        visited = {start: None}
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]
        while q:
            cx, cy = q.popleft()
            if (cx,cy) == goal:
                break
            for dx, dy in dirs:
                nx, ny = cx + dx, cy + dy
                if (
                    0 <= nx < constantes.GRID_WIDTH and
                    0 <= ny < constantes.GRID_HEIGHT and
                    (nx,ny) not in visited and
                    (nx,ny) not in [(o.x, o.y) for o in self.obstacles]
                ):
                    visited[(nx,ny)] = (cx,cy)
                    q.append((nx,ny))
        path, node = [], goal
        while node and node != start:
            path.append(node)
            node = visited[node]
        path.reverse()
        return path

    def run(self):
        while True:
            if self.in_storm:
                yield from self.return_to_base()
                self.in_storm = False
            else:
                if self.carrying:
                    goal = (self.base_x, self.base_y)
                else:
                    if (self.x, self.y) == (self.base_x, self.base_y) and self.shared_info:
                        # Pega o primeiro objetivo disponível do BDI
                        for pos, rtype in self.shared_info.items():
                            self.target = pos
                            break
                        self.shared_info.clear()  # limpa após pegar o alvo
                    goal = self.target

                if goal and (goal != self.target or not self.plan):
                    self.plan = self.find_path((self.x, self.y), goal)
                    self.target = goal

                if goal and (self.x, self.y) == goal:
                    if self.carrying:
                        self.deliver()
                    else:
                        self.collect_here()
                elif self.plan:
                    nx, ny = self.plan.pop(0)
                    self.x, self.y = nx, ny

            yield self.env.timeout(1)

    def collect_here(self):
        for res in self.grid:
            if not res.collected and (res.x, res.y) == (self.x, self.y):
                res.collected = True
                self.resources_collected += res.value
                self.shared_info[(self.x, self.y)] = res.type
                break

    def return_to_base(self):
        while (self.x, self.y) != (self.base_x, self.base_y):
            dx = self.base_x - self.x; dy = self.base_y - self.y
            self.x += 1 if dx > 0 else -1 if dx < 0 else 0
            self.y += 1 if dy > 0 else -1 if dy < 0 else 0
            yield self.env.timeout(1)

    def deliver(self):
        from utils.resource_manager import register_delivery
        register_delivery(self.id, 1)  # registra 1 unidade entregue
        self.carrying = None

    def draw(self, screen):
        """
        Desenha o agente como um círculo usando sua cor e posição.
        """
        size = constantes.CELL_SIZE
        center = (self.x * size + size // 2, self.y * size + size // 2)
        pygame.draw.circle(screen, self.color, center, size // 2 - 2)

    #Commit