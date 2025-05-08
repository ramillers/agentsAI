import pygame
from collections import deque
import constantes
from utils.resource_manager import register_delivery
from agents.reactive import ReactiveAgent

class CooperativeAgent:
    """
    Fica na base. Só sai quando o BDI informar um alvo cooperativo (estrutura/diamante).
    Vai com outro agente cooperar, baseado em utilidade (valor/distância).
    """

    def __init__(self, env, x, y, grid, base_x, base_y, obstacles):
        self.env = env
        self.x, self.y = x, y
        self.name = "Agente Cooperativo"
        self.grid = grid
        self.base_x, self.base_y = base_x, base_y
        self.obstacles = obstacles
        self.color = constantes.COOPERATIVE_COLOR
        self.resources_collected = 0
        self.shared_info = {}
        self.plan = []
        self.target = None
        self.collecteds = []
        self.waiting = False
        self.in_storm = False
        self.process = env.process(self.run())


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
                        if tipo in ['estrutura']
                    ]
                    print(f"ESTRUTURAS DO COOPERATIVO: {coop_targets}")
                    #O cooperativo só esta indo na primeira estrutura encontrada
                    if coop_targets:
                        for position in coop_targets:
                            if position not in self.collecteds:
                                self.target = position
                                self.plan = self.find_path((self.x, self.y), self.target)
                                self.waiting = True

                                print(f"[COOP] Aguardando parceiro para {self.target}")
                            #O COOPERATIVO NÃO VOLTA

                # Se estiver esperando e parceiro chegou com mesmo alvo, prossegue
                if self.waiting and self.has_partner():
                    print(f"[COOP] Indo com parceiro para {self.target}")
                    self.waiting = False
                    self.collecteds.append(self.target)

            # Se já tem plano e não está esperando, signfica que já tem alguem pra ir com ele
            if self.plan and not self.waiting: #Se tem um plano e não está esperando
                nx, ny = self.plan.pop(0)
                self.x, self.y = nx, ny
                #Anda anda até chegar no recurso, depois tem que voltar

                # Ao chegar no destino, tenta coletar
                if (self.x, self.y) == self.target: #AQUI
                    for res in self.grid:
                        if not res.collected and (res.x, res.y) == self.target: #Se n ele pode coletar outros no caminho
                            res.collected = True
                            self.resources_collected += res.value
                            register_delivery(self.name, res.type)
                            print(f"[COOP] Recurso {res.type} coletado em {self.target}")
                            self.return_to_base()
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
            if ag is not self and not isinstance(ag, ReactiveAgent) and ag.name != "BDI":
                if (ag.x, ag.y) == (self.base_x, self.base_y) and not ag.plan:
                    ag.coperating = True
                    ag.plan = self.plan
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
            #Vou usar essa função

    def draw(self, screen): 
        """
        Desenha o agente como um quadrado na tela do pygame.
        """
        size = constantes.CELL_SIZE
        rect = pygame.Rect(
            self.x * size + 2,
            self.y * size + 2,
            size - 4,
            size - 4
        )
        pygame.draw.rect(screen, self.color, rect)