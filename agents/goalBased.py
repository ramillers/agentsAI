import pygame
from collections import deque
import constantes

class GoalBasedAgent:
    """
    Seleciona de forma gulosa o recurso de maior valor/distância, planeja um caminho
    (BFS) até ele e depois retorna à base, registrando no painel todas as detecções e coletas.
    """
    def __init__(self, env, x, y, grid, base_x, base_y, obstacles):
        self.env = env
        self.x, self.y = x, y
        self.grid = grid
        self.base_x, self.base_y = base_x, base_y
        self.obstacles = obstacles
        self.color = constantes.GOALBASED_COLOR
        self.resources_collected = 0
        self.shared_info = {}
        self.plan = []
        self.target = None
        self.in_storm = False
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
                # detecta todos os recursos não coletados
                seen = [(res.x, res.y, res.type) for res in self.grid if not res.collected]
                for x0, y0, t in seen:
                    self.shared_info[(x0, y0)] = t
                # decide meta
                if hasattr(self, 'carrying') and self.carrying:
                    goal = (self.base_x, self.base_y)
                else:
                    vals = {'cristal': 10, 'metal': 20, 'estrutura': 50}
                    seen.sort(key=lambda e: (-vals[e[2]], abs(e[0]-self.x) + abs(e[1]-self.y)))
                    goal = (seen[0][0], seen[0][1]) if seen else None
                # monta plano
                if goal and (goal != self.target or not self.plan):
                    self.plan = self.find_path((self.x, self.y), goal)
                    self.target = goal
                # executa próxima ação
                if goal and (self.x, self.y) == goal:
                    if hasattr(self, 'carrying') and self.carrying:
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
        rect = pygame.Rect(
            self.x * size + 2,
            self.y * size + 2,
            size - 4,
            size - 4
        )
        pygame.draw.rect(screen, self.color, rect)
