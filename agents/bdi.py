import pygame
import constantes as constantes
from collections import deque

class BDIAgent:
    """
    Agrega dados de shared_info de todos os colegas, gera crenças,
    formula desejos, intenções e executa plano (coletar/entregar)."""
    def __init__(self, env, x, y, base_x, base_y, grid):
        self.env = env
        self.x, self.y = x, y
        self.name = "BDI"
        self.base_x, self.base_y = base_x, base_y
        self.grid = grid  # Lista de recursos reais
        self.color = constantes.BDI_COLOR
        self.beliefs = {} # Informações acumuladas de todos
        self.desires = [] # Painel que pode ser consultado pelos outros
        self.in_storm = False
        self.process = env.process(self.run())

    def validate_beliefs(self):
        """Remove crenças sobre recursos já coletados ou inexistentes"""
        to_remove = []
        for pos, rtype in self.beliefs.items():
            resource_exists = False
            for res in self.grid:
                if not res.collected and (res.x, res.y) == pos and res.type == rtype:
                    resource_exists = True
                    break
            
            if not resource_exists:
                to_remove.append(pos)
        
        for pos in to_remove:
            self.beliefs.pop(pos)



    def update_beliefs_from_agents(self):
        """Agrega informações válidas dos agentes"""
        temp_beliefs = {}
        for ag in getattr(self.env, 'agents', []):
            if ag is not self and hasattr(ag, 'shared_info'):
                if (ag.x, ag.y) == (self.base_x, self.base_y):
                    # Filtra apenas recursos não coletados
                    for pos, rtype in ag.shared_info.items():
                        if any(not res.collected and (res.x, res.y) == pos for res in self.grid):
                            temp_beliefs[pos] = rtype
        self.beliefs = temp_beliefs

    def broadcast_to_agents(self):
        """Atualiza os painéis (shared_info) de todos os colegas que estão na base."""
        for ag in getattr(self.env, 'agents', []):
            if ag is not self and hasattr(ag, 'shared_info'):
                if (ag.x, ag.y) == (self.base_x, self.base_y):
                    ag.shared_info.update(self.beliefs)
   

    def run(self):
        while True:
            self.validate_beliefs()  # Valida antes de atualizar
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