# src/config.py

# Fenêtre
WINDOW_W = 1000
WINDOW_H = 700
FPS = 60

# Monde (grille)
CELL_SIZE = 20
GRID_W = WINDOW_W // CELL_SIZE
GRID_H = WINDOW_H // CELL_SIZE

# Simulation
TICKS_PER_SECOND = 10  # logique (faim/soif) indépendamment des FPS

# Agents
START_AGENTS = 12

HUNGER_INCREASE = 1.2
THIRST_INCREASE = 1.6
ENERGY_DECREASE = 0.6

EAT_AMOUNT = 35.0
DRINK_AMOUNT = 45.0
SLEEP_AMOUNT = 30.0

MAX_NEED = 100.0
DEATH_THRESHOLD = 100.0

# Ressources
FOOD_SPAWN_CHANCE = 0.20   # chance par tick logique
WATER_SPAWN_CHANCE = 0.20

MAX_FOOD = 50
MAX_WATER = 50

# “Vision” simple: distance Manhattan max pour détecter une ressource
VISION_RANGE = 12