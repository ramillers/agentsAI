import pygame
import agents.constantes as constantes
from collections import deque

class BDIAgent:
    """
    Agrega dados de shared_info de todos os colegas, gera crenças,
    formula desejos, intenções e executa plano (coletar/entregar)."""
    def __init__(self, env, x, y, base_x, base_y):
        self.env = env
        self.x, self.y = x, y
        self.base_x, self.base_y = base_x, base_y
        self.color = constantes.BASE_COLOR
        self.beliefs = {} # Informações acumuladas de todos
        self.desires = [] # Painel que pode ser consultado pelos outros
        self.in_storm = False
        self.process = env.process(self.run())


    def update_beliefs_from_agents(self):
        """Agrega informações dos agentes que estão na base."""
        for ag in getattr(self.env, 'agents', []):
            if ag is not self and hasattr(ag, 'shared_info'):
                if (ag.x, ag.y) == (self.base_x, self.base_y):
                    for pos, rtype in ag.shared_info.items():
                        self.beliefs[pos] = rtype

    def broadcast_to_agents(self):
        """Atualiza os painéis (shared_info) de todos os colegas que estão na base."""
        for ag in getattr(self.env, 'agents', []):
            if ag is not self and hasattr(ag, 'shared_info'):
                if (ag.x, ag.y) == (self.base_x, self.base_y):
                    ag.shared_info.update(self.beliefs)
   

    def run(self):
        while True:
            # Não se move, não coleta, apenas gerencia informações
            self.update_beliefs_from_agents()
            self.broadcast_to_agents()
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
#Commit