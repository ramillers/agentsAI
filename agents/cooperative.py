import pygame
from collections import deque
import constantes

class CooperativeAgent:
    """
    Fica na base. Só sai quando o BDI informar um alvo cooperativo (estrutura/diamante).
    Vai com outro agente cooperar, baseado em utilidade (valor/distância).
    """

    def __init__(self, env, x, y, grid, base_x, base_y, obstacles):
        self.env = env
        self.x, self.y = x, y
        self.grid = grid
        self.base_x, self.base_y = base_x, base_y
        self.obstacles = obstacles
        self.color = constantes.STRUCTURE_COLOR
        self.resources_collected = 0
        self.shared_info = {}
        self.plan = []
        self.target = None
        self.waiting = False
        self.in_storm = False
        self.process = env.process(self.run())

    def utility(self, pos):
        """Calcula utilidade com base em valor/distância."""
        dist = abs(pos[0] - self.x) + abs(pos[1] - self.y)
        val_map = {'estrutura': 50, 'diamante': 100}
        tipo = self.shared_info.get(pos, 'estrutura')
        valor = val_map.get(tipo, 0)
        return valor / (dist + 1)

    def run(self):
        while True:
            if self.in_storm:
                yield from self.return_to_base()
                self.in_storm = False
                continue

            # Sempre começa na base
            if (self.x, self.y) == (self.base_x, self.base_y):
                # Se ainda não tem alvo, busca alvos cooperativos no shared_info
                if not self.target:
                    coop_targets = [
                        pos for pos, tipo in self.shared_info.items()
                        if tipo in ['estrutura', 'diamante']
                    ]
                    if coop_targets:
                        scored = [(pos, self.utility(pos)) for pos in coop_targets]
                        scored.sort(key=lambda x: -x[1])
                        self.target = scored[0][0]
                        self.plan = self.find_path((self.x, self.y), self.target)
                        self.waiting = True
                        print(f"[COOP] Aguardando parceiro para {self.target}")

                # Se estiver esperando e parceiro chegou com mesmo alvo, prossegue
                if self.waiting and self.has_partner():
                    print(f"[COOP] Indo com parceiro para {self.target}")
                    self.waiting = False

            # Se já tem plano e não está esperando, segue
            if self.plan and not self.waiting:
                nx, ny = self.plan.pop(0)
                self.x, self.y = nx, ny

                # Ao chegar no destino, tenta coletar
                if (self.x, self.y) == self.target:
                    for res in self.grid:
                        if not res.collected and (res.x, res.y) == self.target:
                            res.collected = True
                            self.resources_collected += res.value
                            print(f"[COOP] Recurso {res.type} coletado em {self.target}")
                            break
                    # Limpa dados
                    self.target = None
                    self.plan = []
                    self.waiting = False

            # Se o recurso foi pego por outro antes, limpa o alvo
            if self.target:
                found = any(not res.collected and (res.x, res.y) == self.target for res in self.grid)
                if not found:
                    print(f"[COOP] Recurso em {self.target} indisponível. Resetando.")
                    self.target = None
                    self.plan = []
                    self.waiting = False

            yield self.env.timeout(1)

    def has_partner(self):
        """Verifica se outro agente cooperativo está na base com o mesmo alvo."""
        for ag in self.env.agents:
            if ag is not self and isinstance(ag, CooperativeAgent):
                if (ag.x, ag.y) == (self.base_x, self.base_y) and ag.target == self.target:
                    return True
        return False

    def find_path(self, start, goal):
        """Busca caminho usando BFS."""
        queue = deque([start])
        visited = {start: None}
        dirs = [(1,0), (-1,0), (0,1), (0,-1)]
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
        """Retorna à base durante tempestade."""
        while (self.x, self.y) != (self.base_x, self.base_y):
            dx = self.base_x - self.x
            dy = self.base_y - self.y
            self.x += 1 if dx > 0 else -1 if dx < 0 else 0
            self.y += 1 if dy > 0 else -1 if dy < 0 else 0
            yield self.env.timeout(1)

    def draw(self, screen):
        """Desenha o agente como círculo."""
        size = constantes.CELL_SIZE
        center = (self.x * size + size // 2, self.y * size + size // 2)
        pygame.draw.circle(screen, self.color, center, size // 2 - 2)

#Commit