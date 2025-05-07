import sys
import random
import pygame
import simpy

import constantes
import recursos
from utils.resource_manager import register_delivery
from agents.reactive import ReactiveAgent
from agents.stateBased import StateBasedAgent
from agents.goalBased import GoalBasedAgent
from agents.cooperative import CooperativeAgent
from agents.bdi import BDIAgent

# --------- Configurações iniciais ---------
FPS = 10
STORM_INTERVAL = 50  # passos até próxima tempestade
STORM_DURATION = 10  # duração da tempestade em passos
env = simpy.Environment()
env.is_storm = False  # Estado inicial sem tempestade

# --------- Função para controlar tempestades ---------
def storm_controller(env, agents):
    while True:
        yield env.timeout(STORM_INTERVAL)
        print("[STORM] Tempestade iniciada! Agentes voltam à base.")
        # Ativa tempestade para todos os agentes E no ambiente
        for ag in agents:
            ag.in_storm = True
        env.is_storm = True  # Novo atributo para controlar o estado global
        
        yield env.timeout(STORM_DURATION)
        print("[STORM] Tempestade encerrada. Agentes retornam à coleta.")
        # Desativa tempestade
        for ag in agents:
            ag.in_storm = False
        env.is_storm = False

# --------- Inicialização do ambiente SimPy ---------
env = simpy.Environment()

# --------- Criar recursos e obstáculos ---------
all_resources = recursos.create_resources()
obstacles = recursos.create_obstacles()

# Mostrar recursos no terminal
print("Recursos disponíveis:")
for res in all_resources:
    print(f"  ID={res.id}, tipo={res.type}, posição=({res.x},{res.y}), requer={res.required_agents}")

# --------- Criar agentes na base ---------
base_x, base_y = constantes.BASE_POS
agents = []

agent_classes = [ReactiveAgent, StateBasedAgent, GoalBasedAgent, CooperativeAgent, BDIAgent]
for idx, cls in enumerate(agent_classes, start=1):
    ag = cls(env, base_x, base_y, all_resources, base_x, base_y, obstacles)
    ag.id = idx
    agents.append(ag)
    print(f"Agente {idx}: {cls.__name__} criado na base ({base_x},{base_y})")

# --- Vincular agentes ao ambiente para uso interno (shared_info) ---
env.agents = agents

# Registrar tempestade
env.process(storm_controller(env, agents))

# Desenha legenda
def draw_legend(screen, agents):
    # Calcula a posição inicial da legenda
    legend_x = constantes.GRID_WIDTH * constantes.CELL_SIZE
    legend_width = constantes.LEGEND_WIDTH
    
    # Desenha o fundo da legenda
    pygame.draw.rect(screen, constantes.LEGEND_BG_COLOR, 
                    (legend_x, 0, legend_width, constantes.GRID_HEIGHT * constantes.CELL_SIZE))
    
    # Prepara a fonte
    font = pygame.font.SysFont('Arial', 16)
    y_pos = constantes.LEGEND_MARGIN
    
    # Título
    title = font.render("Legenda:", True, constantes.LEGEND_TEXT_COLOR)
    screen.blit(title, (legend_x + constantes.LEGEND_MARGIN, y_pos))
    y_pos += constantes.LEGEND_LINE_HEIGHT
    
    # Agentes
    agent_title = font.render("Agentes:", True, constantes.LEGEND_TEXT_COLOR)
    screen.blit(agent_title, (legend_x + constantes.LEGEND_MARGIN, y_pos))
    y_pos += constantes.LEGEND_LINE_HEIGHT
    
    for agent in agents:
        # Quadrado de cor
        pygame.draw.rect(screen, agent.color, 
                        (legend_x + constantes.LEGEND_MARGIN, y_pos, 20, 20))
        
        # Nome do agente
        agent_name = font.render(agent.name, True, constantes.LEGEND_TEXT_COLOR)
        screen.blit(agent_name, (legend_x + constantes.LEGEND_MARGIN + 25, y_pos + 2))
        y_pos += constantes.LEGEND_LINE_HEIGHT
    
    # Recursos
    y_pos += constantes.LEGEND_LINE_HEIGHT  # Espaço extra
    resources_title = font.render("Recursos:", True, constantes.LEGEND_TEXT_COLOR)
    screen.blit(resources_title, (legend_x + constantes.LEGEND_MARGIN, y_pos))
    y_pos += constantes.LEGEND_LINE_HEIGHT
    
    # Adicione aqui os tipos de recursos com suas cores
    resource_types = [
        ("Cristal Energético", constantes.CRYSTAL_COLOR),
        ("Bloco de Metal", constantes.METAL_COLOR),
        ("Estrutura Antiga", constantes.STRUCTURE_COLOR)
    ]
    
    for name, color in resource_types:
        
        pygame.draw.rect(screen, color, 
                        (legend_x + constantes.LEGEND_MARGIN, y_pos, 20, 20))
        res_name = font.render(name, True, constantes.LEGEND_TEXT_COLOR)
        screen.blit(res_name, (legend_x + constantes.LEGEND_MARGIN + 25, y_pos + 2))
        y_pos += constantes.LEGEND_LINE_HEIGHT
    
    # # Obstáculos
    # y_pos += constantes.LEGEND_LINE_HEIGHT  # Espaço extra
    # obs_title = font.render("Obstáculos:", True, constantes.LEGEND_TEXT_COLOR)
    # screen.blit(obs_title, (legend_x + constantes.LEGEND_MARGIN, y_pos))
    # y_pos += constantes.LEGEND_LINE_HEIGHT
    
    # pygame.draw.rect(screen, constantes.OBSTACLE_COLOR, 
    #                 (legend_x + constantes.LEGEND_MARGIN, y_pos, 20, 20))
    # obs_name = font.render("Montanhas/Rios", True, constantes.LEGEND_TEXT_COLOR)
    # screen.blit(obs_name, (legend_x + constantes.LEGEND_MARGIN + 25, y_pos + 2))


# --------- Iniciar Pygame ---------
pygame.init()

total_width = constantes.GRID_WIDTH * constantes.CELL_SIZE + constantes.LEGEND_WIDTH
screen = pygame.display.set_mode((total_width, constantes.GRID_HEIGHT * constantes.CELL_SIZE))

clock = pygame.time.Clock()

# --------- Loop principal ---------
running = True
while running:
    # Processamento do SimPy (um passo)
    env.step()

    # Eventos Pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Preencher fundo
    bg_color = constantes.STORM_BG_COLOR if getattr(env, 'is_storm', False) else constantes.NORMAL_BG_COLOR
    screen.fill(bg_color)

    # Desenhar recursos ainda não coletados
    for res in all_resources:
        if not res.collected:
            res.draw(screen)

    # Desenhar base
    half = constantes.BASE_SIZE // 2
    rect = pygame.Rect(
        (base_x - half) * constantes.CELL_SIZE,
        (base_y - half) * constantes.CELL_SIZE,
        constantes.BASE_SIZE * constantes.CELL_SIZE,
        constantes.BASE_SIZE * constantes.CELL_SIZE
    )
    pygame.draw.rect(screen, constantes.BASE_COLOR, rect)

    # Desenhar e atualizar agentes
    for ag in agents:
        ag.draw(screen)
    

    # Desenhar legenda
    draw_legend(screen, agents)

    pygame.display.flip()
    clock.tick(FPS)

# Ao fechar, exibir métricas finais
print("\n=== Métricas de Coleta ===")
for ag in agents:
    delivered = register_delivery(ag.id, None, query_only=True)
    print(f"Agente {ag.id} ({type(ag).__name__}): entregou {delivered} unidades")

pygame.quit()
sys.exit()