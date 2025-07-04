# Configuração da grade
GRID_WIDTH = 40
GRID_HEIGHT = 30
CELL_SIZE = 20
# Aliases (compatibilidade com nomes anteriores)
grid_width = GRID_WIDTH
grid_height = GRID_HEIGHT
cell_size = CELL_SIZE

# Posição da base (centro)
BASE_POS = (GRID_WIDTH // 2, GRID_HEIGHT // 2)

# Cores (RGB)
STORM_BG_COLOR = (70, 70, 100)    # Cor de fundo durante tempestade (azul escuro/acinzentado)
NORMAL_BG_COLOR = (0, 0, 0)       # fundo escuro
BASE_COLOR = (200, 200, 200)      # base clara
CRYSTAL_COLOR = (0, 255, 255)     # cristal (ciano)
METAL_COLOR = (255, 215, 0)       # metal (dourado)
STRUCTURE_COLOR = (255, 0, 255)   # estrutura (magenta)
OBSTACLE_COLOR = (100, 100, 100)  # obstáculos

BDI_COLOR = (88, 72, 148)
COOPERATIVE_COLOR = (51, 30, 247)
GOALBASED_COLOR = (69, 89, 58)
REACTIVE_COLOR = (133, 252, 82)
STATEBASED_COLOR = (254, 51, 29)

# Quantidade de recursos
NUM_CRYSTALS = 25
NUM_METAL = 25
NUM_STRUCTURES = 15
# Tamanho da base (em células, deve ser ímpar para centralizar)
BASE_SIZE = 3

TEMPO_EXPERIMENTO = 60 #Em segundos

# Valores e agentes necessários por tipo
RESOURCE_VALUES = {
    'cristal': 10,
    'metal': 20,
    'estrutura': 50
}
REQUIRED_AGENTS = {
    'cristal': 1,
    'metal': 1,
    'estrutura': 2
}

# Valores da legenda
LEGEND_WIDTH = 200  # Largura da área da legenda
LEGEND_BG_COLOR = (240, 240, 240)  # Cor de fundo da legenda
LEGEND_TEXT_COLOR = (0, 0, 0)  # Cor do texto
LEGEND_MARGIN = 10  # Margem interna
LEGEND_LINE_HEIGHT = 30  # Espaço entre linhas
