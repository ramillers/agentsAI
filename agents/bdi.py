import pygame
import constantes
from collections import deque

class BDIAgent:
    """
    Agrega dados de shared_info de todos os colegas, gera crenças,
    formula desejos, intenções e executa plano (coletar/entregar)."""
    def __init__(self, env, x, y, grid, base_x, base_y, obstacles):
        self.env = env
        self.x, self.y = x, y
        self.name = "BDI"
        self.grid = grid
        self.base_x, self.base_y = base_x, base_y
        self.obstacles = obstacles
        self.color = constantes.BDI_COLOR
        self.beliefs = {}
        self.desires = []
        self.intentions = None
        self.plan = []
        self.carrying = None
        self.in_storm = False
        self.process = env.process(self.run())

    def perceive(self):
        """Atualiza crenças a partir do painel de cada agente."""
        for ag in getattr(self.env, 'agents', []):
            if hasattr(ag, 'shared_info'):
                for pos, rtype in ag.shared_info.items():
                    self.beliefs[pos] = rtype

    def decide(self):
        """Define desejos, intenções e plano a partir das crenças."""
        # desejos: lista de (pos, valor)
        val_map = {'cristal': 10, 'metal': 20, 'estrutura': 50}
        self.desires = [(pos, val_map.get(rtype, 0)) for pos, rtype in self.beliefs.items()]
        self.desires.sort(key=lambda x: -x[1])
        # intenção: primeiro recurso ainda disponível
        self.intentions = None
        for pos, _ in self.desires:
            if any((not r.collected and (r.x, r.y) == pos) for r in self.grid):
                self.intentions = pos
                break
        # meta: volta à base se carregando, senão intenção
        goal = (self.base_x, self.base_y) if self.carrying else self.intentions
        if goal:
            self.plan = self.find_path((self.x, self.y), goal)

    def run(self):
        while True:
            # tempestade
            if self.in_storm:
                yield from self.return_to_base()
                self.in_storm = False
            # ciclo normal
            self.perceive()
            self.decide()
            # execução: entregar, coletar ou mover
            if self.carrying and (self.x, self.y) == (self.base_x, self.base_y):
                from utils.resource_manager import register_delivery
                register_delivery(self.id, 1)
                self.carrying = None
            elif not self.carrying and self.intentions == (self.x, self.y):
                for r in self.grid:
                    if not r.collected and (r.x, r.y) == self.intentions:
                        r.collected = True
                        self.carrying = r.type
                        break
            elif self.plan:
                nx, ny = self.plan.pop(0)
                self.x, self.y = nx, ny
            yield self.env.timeout(1)

    def find_path(self, start, goal):
        """BFS para encontrar caminho de start até goal."""
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
        """Retorna direto para a base durante tempestade."""
        while (self.x, self.y) != (self.base_x, self.base_y):
            dx = self.base_x - self.x; dy = self.base_y - self.y
            self.x += 1 if dx > 0 else -1 if dx < 0 else 0
            self.y += 1 if dy > 0 else -1 if dy < 0 else 0
            yield self.env.timeout(1)

    def draw(self, screen):
        """Desenha o BDI como um quadrado distinto."""
        size = constantes.CELL_SIZE
        rect = pygame.Rect(
            self.x * size + 2,
            self.y * size + 2,
            size - 4,
            size - 4
        )
        pygame.draw.rect(screen, self.color, rect)
