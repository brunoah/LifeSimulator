# src/main.py
from __future__ import annotations

import random
import pygame

import config
from world import World
from agent import Agent


def cell_to_px(pos):
    x, y = pos
    return x * config.CELL_SIZE, y * config.CELL_SIZE


def draw_need_bar(screen, x, y, w, h, value):
    # valeur 0..100
    value = max(0.0, min(100.0, value))
    fill = int(w * (value / 100.0))
    pygame.draw.rect(screen, (30, 30, 30), (x, y, w, h), 1)
    pygame.draw.rect(screen, (200, 200, 200), (x, y, fill, h))

def draw_legend(screen, font):

    legend_x = config.WINDOW_W - 180
    legend_y = 10

    pygame.draw.rect(screen, (10,10,12), (legend_x, legend_y, 170, 120))
    pygame.draw.rect(screen, (60,60,70), (legend_x, legend_y, 170, 120), 1)

    title = font.render("Légende", True, (230,230,230))
    screen.blit(title, (legend_x + 10, legend_y + 8))

    items = [
        ((240,200,80), "Agent"),
        ((255,120,120), "Agent Sélectionné"),
        ((80,220,120), "Nourriture"),
        ((80,140,240), "Eau")
    ]

    for i, (color, text) in enumerate(items):

        y = legend_y + 30 + i * 20

        pygame.draw.rect(screen, color, (legend_x + 10, y, 12, 12))

        label = font.render(text, True, (230,230,230))
        screen.blit(label, (legend_x + 30, y - 2))

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.WINDOW_W, config.WINDOW_H))
    pygame.display.set_caption("LifeSimulator - v0 (2D)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 16)

    world = World(config.GRID_W, config.GRID_H)

    agents: list[Agent] = []
    for i in range(config.START_AGENTS):
        pos = (random.randrange(world.w), random.randrange(world.h))
        agents.append(Agent(id=i + 1, pos=pos))

    # ressources initiales
    for _ in range(25):
        world.food.append(type("R", (), {"kind": "food", "pos": (random.randrange(world.w), random.randrange(world.h))})())
        world.water.append(type("R", (), {"kind": "water", "pos": (random.randrange(world.w), random.randrange(world.h))})())

    # Timer logique (ticks indépendants du rendu)
    logic_accum = 0.0
    logic_dt = 1.0 / config.TICKS_PER_SECOND

    running = True
    selected_id = 1

    while running:
        dt = clock.tick(config.FPS) / 1000.0
        logic_accum += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_RIGHT:
                    selected_id += 1
                if event.key == pygame.K_LEFT:
                    selected_id -= 1
                selected_id = max(1, min(config.START_AGENTS, selected_id))

        # --- logique simulation ---
        while logic_accum >= logic_dt:
            logic_accum -= logic_dt

            occupied = {a.pos for a in agents if a.alive}
            world.update(occupied)

            for a in agents:
                if not a.alive:
                    continue
                a.step_needs()
                a.act(world)

        # --- rendu ---
        screen.fill((18, 18, 22))

        # ressources: carrés
        for f in world.food:
            px, py = cell_to_px(f.pos)
            pygame.draw.rect(screen, (80, 220, 120), (px, py, config.CELL_SIZE, config.CELL_SIZE))
        for w in world.water:
            px, py = cell_to_px(w.pos)
            pygame.draw.rect(screen, (80, 140, 240), (px, py, config.CELL_SIZE, config.CELL_SIZE))

        # agents: cercles
        for a in agents:
            if not a.alive:
                continue
            px, py = cell_to_px(a.pos)
            cx = px + config.CELL_SIZE // 2
            cy = py + config.CELL_SIZE // 2

            color = (240, 200, 80)
            if a.id == selected_id:
                color = (255, 120, 120)

            pygame.draw.circle(screen, color, (cx, cy), config.CELL_SIZE // 2 - 2)

        # HUD agent sélectionné
        sel = next((a for a in agents if a.id == selected_id), None)
        hud_x, hud_y = 10, 10
        pygame.draw.rect(screen, (10, 10, 12), (hud_x, hud_y, 330, 120))
        pygame.draw.rect(screen, (60, 60, 70), (hud_x, hud_y, 330, 120), 1)

        if sel:
            t1 = font.render(f"Selected: A{sel.id}  Alive={sel.alive}  Age={sel.age}", True, (230, 230, 230))
            screen.blit(t1, (hud_x + 10, hud_y + 10))

            screen.blit(font.render("Hunger", True, (230, 230, 230)), (hud_x + 10, hud_y + 35))
            draw_need_bar(screen, hud_x + 80, hud_y + 38, 230, 10, sel.hunger)

            screen.blit(font.render("Thirst", True, (230, 230, 230)), (hud_x + 10, hud_y + 55))
            draw_need_bar(screen, hud_x + 80, hud_y + 58, 230, 10, sel.thirst)

            screen.blit(font.render("Energy", True, (230, 230, 230)), (hud_x + 10, hud_y + 75))
            draw_need_bar(screen, hud_x + 80, hud_y + 78, 230, 10, sel.energy)

            alive_count = sum(1 for a in agents if a.alive)
            screen.blit(font.render(f"Alive agents: {alive_count}", True, (230, 230, 230)), (hud_x + 10, hud_y + 95))

        draw_legend(screen, font)    

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()