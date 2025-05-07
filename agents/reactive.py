import random
import constantes

class ReactiveAgent:
    """
    Agente puramente reativo: anda aleatoriamente, coleta cristais e registra
    no painel local (shared_info) todos os recursos vistos na vizinhança.
    """
    def __init__(self, env, x, y, grid, base_x, base_y, obstacles):
        self.env = env
        self.x, self.y = x, y
        self.name = "Reativo"
        self.grid = grid                # lista de Resource
        self.base_x, self.base_y = base_x, base_y
        self.obstacles = obstacles
        self.color = constantes.REACTIVE_COLOR
        self.resources_collected = 0
        self.shared_info = {}           # painel local
        self.in_storm = False
        # dispara o processo de simulação
        self.process = env.process(self.run())

    def move_randomly(self):
        dx, dy = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        nx = max(0, min(self.x+dx, constantes.grid_width-1))
        ny = max(0, min(self.y+dy, constantes.grid_height-1))
        if (nx,ny) not in [(o.x, o.y) for o in self.obstacles]:
            self.x, self.y = nx, ny

    def collect_if_crystal(self):
        for res in self.grid:
            if not res.collected and res.type=='cristal' and res.x==self.x and res.y==self.y:
                res.collected = True
                self.resources_collected += res.value
                # registra coleta no painel
                self.shared_info[(self.x, self.y)] = res.type
                break

    def return_to_base(self):
        # movimento direto em linha reta
        while (self.x, self.y) != (self.base_x, self.base_y):
            dx = self.base_x - self.x
            dy = self.base_y - self.y
            self.x += 1 if dx>0 else -1 if dx<0 else 0
            self.y += 1 if dy>0 else -1 if dy<0 else 0
            yield self.env.timeout(1)

    def run(self):
        while True:
            if self.in_storm:
                # tempestade: volta imediatamente
                yield from self.return_to_base()
                self.in_storm = False
            else:
                # antes de mover, registra vizinhança
                for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                    nx, ny = self.x+dx, self.y+dy
                    for res in self.grid:
                        if (not res.collected and 
                            (res.x,res.y)==(nx,ny)):
                            self.shared_info[(nx,ny)] = res.type
                # movimenta e tenta coletar
                self.move_randomly()
                self.collect_if_crystal()
                yield self.env.timeout(1)

    def draw(self, screen):
        """
        Desenha o agente como um círculo usando sua cor e posição.
        """
        import pygame
        size = constantes.cell_size
        rect = pygame.Rect(
            self.x * size + 2,
            self.y * size + 2,
            size - 4,
            size - 4
        )
        pygame.draw.rect(screen, self.color, rect)
