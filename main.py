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

# --------- Função para controlar tempestades ---------
def storm_controller(env, agents):
    while True:
        yield env.timeout(STORM_INTERVAL)
        print("[STORM] Tempestade iniciada! Agentes voltam à base.")
        for ag in agents:
            ag.in_storm = True
        # tempestade dura um tempo, depois termina automaticamente
        yield env.timeout(STORM_DURATION)
        print("[STORM] Tempestade encerrada. Agentes retornam à coleta.")

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

# --------- Iniciar Pygame ---------
pygame.init()
screen = pygame.display.set_mode((constantes.GRID_WIDTH * constantes.CELL_SIZE,
                                   constantes.GRID_HEIGHT * constantes.CELL_SIZE))
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
    screen.fill(constantes.BG_COLOR)

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

    pygame.display.flip()
    clock.tick(FPS)

# Ao fechar, exibir métricas finais
print("\n=== Métricas de Coleta ===")
for ag in agents:
    delivered = register_delivery(ag.id, None, query_only=True)
    print(f"Agente {ag.id} ({type(ag).__name__}): entregou {delivered} unidades")

pygame.quit()
sys.exit()
