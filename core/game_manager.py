"""This module contains a definition of a Game Manager class"""

import time

from PyQt6 import QtCore
from PyQt6.QtCore import QObject, pyqtSignal

from core.wave_manager import WaveManager
from entities.meteoro import Meteoro
from entities.tower import BasicTower, SniperTower
from world.game_map import GRID_SIZE, TILE_SIZE, GameMap

TOWER_CLASSES = {"basic": BasicTower, "sniper": SniperTower}


class GameManager(QObject):
    tower_clicked = pyqtSignal(object)

    def __init__(self, scene):
        super().__init__()
        self.scene = scene

        # map setup
        self.game_map = GameMap()
        self.game_map.add_to_scene(self.scene)

        # meteoro setup
        self.meteoro_pos = (1, 1)  # (y_pos, x_pos)
        # self.meteoro = Meteoro(self.meteoro_pos[1], self.meteoro_pos[0], TILE_SIZE)
        # self.scene.addItem(self.meteoro)
        # self.set_meteoro_tiles_occupied(self.meteoro_pos)

        self.wave_manager = WaveManager(
            self.game_map, target_x=self.meteoro_pos[1], target_y=self.meteoro_pos[0]
        )

        self.current_wave = 1
        self.dinos = self.wave_manager.spawn_wave(wave=self.current_wave)

        for dino in self.dinos:
            self.scene.addItem(dino)

        self.towers = []
        self.projectiles = []

        self.last_frame_time = time.time()

        self.selected_tower_type = "basic"
        self.selected_tower_on_map = None

        self.money = 200

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)  # ~60 FPS

        self.game_over = False

    def update_game(self):
        current_time = time.time()
        dt = current_time - self.last_frame_time
        self.last_frame_time = current_time

        if dt > 0.1:
            dt = 0.1

        self.update_dinos(dt)
        self.update_towers(dt)
        self.update_projectiles(dt)

    def set_build_mode(self, tower_type: str):
        """Called by the UI buttons to change what we build next."""
        self.selected_tower_type = tower_type
        print(f"Build mode changed to: {tower_type}")

    def set_meteoro_tiles_occupied(self, meteoro_pos: tuple):
        for row in range(meteoro_pos[1], meteoro_pos[1] + 3):
            for col in range(meteoro_pos[0], meteoro_pos[0] + 3):
                if not (0 <= row < GRID_SIZE[1] and 0 <= col < GRID_SIZE[0]):
                    continue
                tile = self.game_map.grid[row][col]
                tile.is_empty = False

    def update_dinos(self, dt):
        if self.game_over:
            return

        for dino in self.dinos[:]:
            reached_end = dino.move_logic(dt)

            if reached_end:
                print("Dino hit the Base! Ouch!")

                hit_tower = self.get_tower_at(dino.grid_x, dino.grid_y)
                hit_tower.take_damage(dino.damage)
                if hit_tower.hp <= 0:
                    self.scene.removeItem(hit_tower)
                    self.dinos.remove(hit_tower)
                self.scene.removeItem(dino)
                self.dinos.remove(dino)
                continue

            if dino.hp <= 0:
                self.money += dino.reward
                print(f"Dino killed! +${dino.reward}. Total: ${self.money}")
                self.scene.removeItem(dino)
                self.dinos.remove(dino)

        if len(self.dinos) == 0:
            self.current_wave += 1
            print(
                f"Fala {self.current_wave - 1} pokonana. Start fali {self.current_wave}..."
            )

            new_wave = self.wave_manager.spawn_wave(wave=self.current_wave)

            if not new_wave:
                print("WYGRANA")
                self.game_over = True
                return

            self.dinos = new_wave
            for dino in self.dinos:
                self.scene.addItem(dino)

    def update_towers(self, dt):
        for tower in self.towers:
            new_bullet = tower.update_logic(dt, self.dinos)
            if new_bullet:
                print("new buller")
                self.projectiles.append(new_bullet)
                self.scene.addItem(new_bullet)

    def update_projectiles(self, dt):
        for proj in self.projectiles[:]:
            exploded = proj.update_logic(dt, self.dinos)

            if exploded:
                self.scene.removeItem(proj)
                self.projectiles.remove(proj)

    def handle_map_click(self, x, y):
        grid_x = x // TILE_SIZE
        grid_y = y // TILE_SIZE

        if not (
            0 <= grid_x < self.game_map.grid_size[0]
            and 0 <= grid_y < self.game_map.grid_size[1]
        ):
            return

        clicked_tile = self.game_map.grid[grid_y][grid_x]

        if not clicked_tile.is_empty:
            self.select_tower(grid_x, grid_y)
            return

        tower_built = self.build_tower(clicked_tile)
        if tower_built:
            self.update_dino_path(grid_x, grid_y)

    def select_tower(self, grid_x, grid_y):
        clicked_tower = self.get_tower_at(grid_x, grid_y)

        # toggle logic
        if self.selected_tower_on_map == clicked_tower and clicked_tower is not None:
            self.selected_tower_on_map.is_selected = False
            self.selected_tower_on_map.range_circle.hide()
            self.selected_tower_on_map = None
            self.tower_clicked.emit(None)
            return

        # deselect
        if self.selected_tower_on_map:
            self.selected_tower_on_map.is_selected = False
            self.selected_tower_on_map.range_circle.hide()
            self.selected_tower_on_map = None

        # select new
        if clicked_tower:
            self.selected_tower_on_map = clicked_tower
            self.selected_tower_on_map.is_selected = True
            self.selected_tower_on_map.range_circle.show()

            self.tower_clicked.emit(clicked_tower)
            print(
                f"Selected Tower! DMG: {clicked_tower.damage}, Range: {clicked_tower.range}"
            )
            return

        self.tower_clicked.emit(None)

    def update_dino_path(self, grid_x, grid_y):
        for dino in self.dinos:
            curr_x, curr_y = dino.get_curr_pos_grid()
            new_waypoints = self.game_map.get_path_a_star(
                curr_x, curr_y, grid_x, grid_y
            )
            dino.update_path(new_waypoints)

    def build_tower(self, clicked_tile) -> bool:
        grid_x = clicked_tile.grid_x
        grid_y = clicked_tile.grid_y

        tower_class = TOWER_CLASSES.get(self.selected_tower_type)

        if not tower_class:
            print("Error: Unknown tower type selected!")
            return False

        if self.money < tower_class.cost:
            print(
                f"Not enough money! Need ${tower_class.cost}, but you only have ${self.money}."
            )
            return False

        self.money -= tower_class.cost
        print(f"Spent ${tower_class.cost}. Remaining money: ${self.money}")

        clicked_tile.is_empty = False
        self.game_map.grid[grid_y][grid_x + 1].is_empty = False

        new_tower = tower_class(grid_y, grid_x, TILE_SIZE)

        self.towers.append(new_tower)
        self.scene.addItem(new_tower)
        print(f"Built a {self.selected_tower_type} tower at ({grid_x}, {grid_y})!")
        return True

    def get_tower_at(self, grid_x, grid_y):
        for tower in self.towers:
            if tower.grid_y == grid_y and (
                tower.grid_x == grid_x or tower.grid_x + 1 == grid_x
            ):
                return tower
        return None
