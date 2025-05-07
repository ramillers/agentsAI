import random
import pygame
import constantes

class StateBasedAgent:
    '''
    Agente baseado em estados:
    - Anda pelo ambiente evitando áreas já visitadas.
    - Coleta recurso, retorna à base e compartilha informação com o BDI.
    - Prioriza explorar áreas que nem ele nem o BDI conhecem.
    '''
    def __init__(self, env, x, y, grid, base_x, base_y, obstacles):
        self.env = env
        self.x, self.y = x, y
        self.name = "Baseado em estado"
        self.grid = grid
        self.base_x, self.base_y = base_x, base_y
        self.obstacles = obstacles
        self.color = constantes.STATEBASED_COLOR
        self.resources_collected = 0
        self.visited = set()
        self.shared_info = {}
        self.in_storm = False
        self.carrying = None
        self.target = None
        self.process = env.process(self.run())

    def move_to_unvisited(self):
        neighbors = [(self.x+dx, self.y+dy) for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]]
        random.shuffle(neighbors)
        bdi_knowledge = getattr(self.env, 'bdi_agent', None)
        known = bdi_knowledge.beliefs.keys() if bdi_knowledge else set()

        for nx, ny in neighbors:
            if (0 <= nx < constantes.GRID_WIDTH and
                0 <= ny < constantes.GRID_HEIGHT and
                (nx, ny) not in self.visited and
                (nx, ny) not in known and
                (nx, ny) not in [(o.x, o.y) for o in self.obstacles]):
                self.x, self.y = nx, ny
                self.visited.add((nx, ny))
                return

       # fallback aleatório
        for nx, ny in neighbors:
            if (0 <= nx < constantes.GRID_WIDTH and
                0 <= ny < constantes.GRID_HEIGHT and
                (nx, ny) not in [(o.x, o.y) for o in self.obstacles]):
                self.x, self.y = nx, ny
                return

    def collect_here(self):
        for res in self.grid:
            if not res.collected and (res.x, res.y) == (self.x, self.y) and self.carrying is None:
                res.collected = True
                self.resources_collected += res.value
                self.shared_info[(self.x, self.y)] = res.type
                self.carrying = res.type
                self.target = (self.base_x, self.base_y)
                self.plan = self.find_path((self.x, self.y), self.target)
                break

    def return_to_base(self):
        while (self.x, self.y) != (self.base_x, self.base_y):
            dx = self.base_x - self.x; dy = self.base_y - self.y
            self.x += 1 if dx > 0 else -1 if dx < 0 else 0
            self.y += 1 if dy > 0 else -1 if dy < 0 else 0
            yield self.env.timeout(1)

    def find_path(self, start, goal):
        from collections import deque
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

    def run(self):
        while True:
            if self.in_storm:
                yield from self.return_to_base()
                self.in_storm = False
            elif self.carrying:
                if (self.x, self.y) == (self.base_x, self.base_y):
                    from utils.resource_manager import register_delivery
                    register_delivery(self.id, 1)
                    self.carrying = None
                    self.target = None
                    self.plan = []
                elif self.plan:
                    nx, ny = self.plan.pop(0)
                    self.x, self.y = nx, ny
                else:
                    self.plan = self.find_path((self.x, self.y), (self.base_x, self.base_y))
            else:
                self.collect_here()
                if not self.carrying:
                    self.move_to_unvisited()
            yield self.env.timeout(1)

    def draw(self, screen):
        """Desenha como um quadrado distinto."""
        size = constantes.CELL_SIZE
        rect = pygame.Rect(
            self.x * size + 2,
            self.y * size + 2,
            size - 4,
            size - 4
        )
        pygame.draw.rect(screen, self.color, rect)
#Commit