import pygame
from collections import deque
import constantes
from utils.resource_manager import register_delivery

class GoalBasedAgent:
    """
    Agente baseado em objetivos. Recebe objetivos do BDI via shared_info
    quando está na base, segue até o objetivo e coleta. Não pondera valor.
    """
    def __init__(self, env, x, y, grid, base_x, base_y, obstacles):
        self.env = env
        self.x, self.y = x, y
        self.name = "Baseado em Objetivo"
        self.grid = grid
        self.base_x, self.base_y = base_x, base_y
        self.obstacles = obstacles
        self.color = constantes.GOALBASED_COLOR
        self.resources_collected = 0
        self.shared_info = {} # Atualizado pelo BDI na base
        self.plan = []
        self.target = None
        self.in_storm = False
        self.carrying = None
        self.failed_targets = set()  # Conjunto de targets que falharam
        self.process = env.process(self.run())

    def is_resource_available(self, pos):
        """Verifica se o recurso na posição está disponível"""
        return any(not res.collected and (res.x, res.y) == pos for res in self.grid)

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
                if (0 <= nx < constantes.GRID_WIDTH and
                    0 <= ny < constantes.GRID_HEIGHT and
                    (nx,ny) not in visited and
                    (nx,ny) not in [(o.x, o.y) for o in self.obstacles]):
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
                    if (self.x, self.y) == (self.base_x, self.base_y):
                        # Filtra targets válidos (disponíveis e não falhados anteriormente)
                        valid_targets = {
                            pos: rtype for pos, rtype in self.shared_info.items()
                            if pos not in self.failed_targets and self.is_resource_available(pos)
                        }
                        
                        if valid_targets:
                            self.target = next(iter(valid_targets.keys()))
                            self.shared_info.clear()
                        else:
                            self.target = None
                    
                    goal = self.target

                if goal:
                    if (self.x, self.y) == goal:
                        if self.carrying:
                            self.deliver()
                        else:
                            self.collect_here()
                            if not self.carrying:  # Se não coletou
                                self.failed_targets.add(goal)  # Marca como falhado
                                self.target = None
                    elif not self.plan:
                        self.plan = self.find_path((self.x, self.y), goal)
                    
                    if self.plan:
                        nx, ny = self.plan.pop(0)
                        self.x, self.y = nx, ny
                
                yield self.env.timeout(1)

    def collect_here(self):
        """Tenta coletar o recurso na posição atual"""
        for res in self.grid:
            if not res.collected and (res.x, res.y) == (self.x, self.y):
                res.collected = True
                self.carrying = res.type
                self.resources_collected += res.value
                register_delivery(self.name, constantes.RESOURCE_VALUES[self.carrying])
                
                # Remove de failed_targets se estava lá
                self.failed_targets.discard((self.x, self.y))
                return True
        
        # Se chegou aqui, não encontrou recurso
        return False

    def return_to_base(self):
        """Retorna diretamente à base durante tempestades"""
        while (self.x, self.y) != (self.base_x, self.base_y):
            dx = self.base_x - self.x
            dy = self.base_y - self.y
            self.x += 1 if dx > 0 else -1 if dx < 0 else 0
            self.y += 1 if dy > 0 else -1 if dy < 0 else 0
            yield self.env.timeout(1)

    def deliver(self):
        """Entrega o recurso na base"""
        from utils.resource_manager import register_delivery
        register_delivery(self.id, 1)
        self.carrying = None

    def draw(self, screen):
        """Desenha o agente na tela"""
        size = constantes.CELL_SIZE
        rect = pygame.Rect(
            self.x * size + 2,
            self.y * size + 2,
            size - 4,
            size - 4
        )
        pygame.draw.rect(screen, self.color, rect)