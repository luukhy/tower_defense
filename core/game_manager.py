"""This module contains a definition of a Game Manager class"""

import time

from PyQt6 import QtCore

from core.wave_manager import WaveManager
from entities.meteoro import Meteoro
from entities.tower import Tower
from world.game_map import GRID_SIZE, TILE_SIZE, GameMap


class GameManager:
    def __init__(self, scene):

        self.scene = scene

        # map setup
        self.game_map = GameMap()
        self.game_map.add_to_scene(self.scene)

        # meteoro setup
        self.meteoro_pos = (18, 18)  # (y_pos, x_pos)
        self.meteoro = Meteoro(self.meteoro_pos[1], self.meteoro_pos[0], TILE_SIZE)
        self.scene.addItem(self.meteoro)
        self.set_meteoro_tiles_occupied(self.meteoro_pos)

        # dinos
        self.wave_manager = WaveManager(
            self.game_map, target_x=self.meteoro_pos[1], target_y=self.meteoro_pos[0]
        )

        self.dinos = self.wave_manager.spawn_wave(wave=1)

        for dino in self.dinos:
            self.scene.addItem(dino)

        # towers
        self.towers = []

        # timer
        self.last_frame_time = time.time()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)  # ~60 FPS

    def update_game(self):
        current_time = time.time()
        dt = current_time - self.last_frame_time
        self.last_frame_time = current_time

        if dt > 0.1:
            dt = 0.1

        self.update_dinos(dt)
        self.update_towers(dt)

    def set_meteoro_tiles_occupied(self, meteoro_pos: tuple):
        for row in range(meteoro_pos[1], meteoro_pos[1] + 3):
            for col in range(meteoro_pos[0], meteoro_pos[0] + 3):
                if not (0 <= row < GRID_SIZE[1] and 0 <= col < GRID_SIZE[0]):
                    continue
                tile = self.game_map.grid[row][col]
                tile.is_empty = False

    def update_dinos(self, dt):
        for dino in self.dinos[:]:
            reached_end = dino.move_logic(dt)

            if reached_end:
                print("Dino hit the Base!")
                self.scene.removeItem(dino)
                self.dinos.remove(dino)

    def update_towers(dt):
        pass

    def handle_map_click(self, x, y):
        col = x // TILE_SIZE
        row = y // TILE_SIZE

        if 0 <= col < GRID_SIZE[0] and 0 <= row < GRID_SIZE[1]:
            clicked_tile = self.game_map.grid[row][col]

            if clicked_tile.is_empty:
                print(f"Building tower at {row}, {col}!")

                clicked_tile.is_empty = False
                new_tower = Tower(row, col, TILE_SIZE)
                self.towers.append(new_tower)
                self.scene.addItem(new_tower)
                for dino in self.dinos:
                    curr_x, curr_y = dino.get_curr_pos_grid()
                    new_waypoints = self.game_map.get_path_a_star(
                        curr_x, curr_y, col, row
                    )
                    dino.update_path(new_waypoints)
            else:
                print("Cannot build here!")
