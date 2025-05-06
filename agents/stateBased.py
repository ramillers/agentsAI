import random
import pygame
import constantes

class StateBasedAgent:
    """
    Explora o grid marcando células visitadas, coleta recursos e registra em shared_info.
    """
    def __init__(self, env, x, y, grid, base_x, base_y, obstacles):
        self.env = env
        self.x, self.y = x, y
        self.grid = grid
        self.base_x, self.base_y = base_x, base_y
        self.obstacles = obstacles
        self.color = constantes.STATEBASED_COLOR
        self.resources_collected = 0
        self.visited = set()
        self.shared_info = {}
        self.in_storm = False
        self.carrying = None
        self.process = env.process(self.run())

    def move_to_unvisited(self):
        neighbors = [(self.x+dx, self.y+dy) for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]]
        random.shuffle(neighbors)
        for nx, ny in neighbors:
            if (0 <= nx < constantes.GRID_WIDTH and
                0 <= ny < constantes.GRID_HEIGHT and
                (nx, ny) not in self.visited and
                (nx, ny) not in [(o.x, o.y) for o in self.obstacles]):
                self.x, self.y = nx, ny
                self.visited.add((nx, ny))
                return
        # fallback aleatório
        self.x, self.y = random.choice(neighbors)

    def collect_here(self):
        for res in self.grid:
            if not res.collected and (res.x, res.y) == (self.x, self.y) and self.carrying is None:
                res.collected = True
                self.resources_collected += res.value
                self.shared_info[(self.x, self.y)] = res.type
                self.carrying = res.type
                break

    def return_to_base(self):
        while (self.x, self.y) != (self.base_x, self.base_y):
            dx = self.base_x - self.x; dy = self.base_y - self.y
            self.x += 1 if dx > 0 else -1 if dx < 0 else 0
            self.y += 1 if dy > 0 else -1 if dy < 0 else 0
            yield self.env.timeout(1)

    def run(self):
        while True:
            if self.in_storm:
                yield from self.return_to_base()
                self.in_storm = False
            else:
                # coleta ou explora
                if any((not r.collected and (r.x, r.y) == (self.x, self.y)) for r in self.grid) and self.carrying is None:
                    self.collect_here()
                else:
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
