import random
import sys
import time

from PyQt6 import QtCore, QtWidgets, uic
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QGraphicsScene

from dino import Dino
from game_map import GRID_SIZE, MAP_SIZE, TILE_SIZE, GameMap
from meteoro import Meteoro
from tower import Tower


class DinoDefense(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("main_window.ui", self)

        self.scene = QGraphicsScene(0, 0, MAP_SIZE[0], MAP_SIZE[1])

        self.graphicsView.setScene(self.scene)
        self.graphicsView.setStyleSheet("border: none;")
        self.graphicsView.tile_clicked_signal.connect(self.handle_map_click)

        # map setup
        self.map = GameMap()
        self.map.add_to_scene(self.scene)

        # meteoro setup
        self.meteoro_pos = (18, 18)  # (y_pos, x_pos)
        self.meteoro = Meteoro(self.meteoro_pos[1], self.meteoro_pos[0], TILE_SIZE)
        self.scene.addItem(self.meteoro)
        self.set_meteoro_tiles_occupied(self.meteoro_pos)

        # dinos
        dinos_init_config = {"num_dinos": 30, "first_wave_type": "triceratops"}
        self.dinos = []
        self.initiate_dinos(dinos_init_config)
        self.add_dinos_to_scene()

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

        for dino in self.dinos[:]:
            reached_end = dino.move_logic(dt)

            if reached_end:
                print("Dino hit the Base!")
                self.scene.removeItem(dino)
                self.dinos.remove(dino)
        pass

    def initiate_dinos(self, config):
        dinos_num = config["num_dinos"]
        dinos_type = config["first_wave_type"]
        dinos_pos = self.generate_dinos_pos(dinos_num)

        target_x = self.meteoro_pos[1]
        target_y = self.meteoro_pos[0]

        for pos in dinos_pos:
            start_x = pos["x"]
            start_y = pos["y"]

            path = self.map.get_path_a_star(start_x, start_y, target_x, target_y)

            if path:
                new_dino = Dino(
                    grid_y=start_y, grid_x=start_x, dino_type=dinos_type, waypoints=path
                )
                self.dinos.append(new_dino)
            else:
                print(f"Skipped dino at {start_x}, {start_y}: No path to base!")

    def add_dinos_to_scene(self):
        for dino in self.dinos:
            self.scene.addItem(dino)

    def generate_dinos_pos(self, dinos_num):
        walkable_tiles = self.map.get_walkable_tiles()
        if dinos_num > len(walkable_tiles):
            dinos_num = len(walkable_tiles)

        random_idx = set()
        while len(random_idx) < dinos_num:
            random_id = random.randint(0, len(walkable_tiles) - 1)
            random_idx.add(random_id)

        pos = []
        for id in random_idx:
            tile = walkable_tiles[id]
            pos.append({"x": tile.x_grid, "y": tile.y_grid})
        return pos

    def set_meteoro_tiles_occupied(self, meteoro_pos: tuple):
        for row in range(meteoro_pos[1], meteoro_pos[1] + 3):
            for col in range(meteoro_pos[0], meteoro_pos[0] + 3):
                if not (0 <= row < GRID_SIZE[1] and 0 <= col < GRID_SIZE[0]):
                    continue
                tile = self.map.grid[row][col]
                tile.is_empty = False

    def update_dinos(self):
        pass

    def handle_map_click(self, x, y):
        col = x // TILE_SIZE
        row = y // TILE_SIZE

        if 0 <= col < GRID_SIZE[0] and 0 <= row < GRID_SIZE[1]:
            clicked_tile = self.map.grid[row][col]

            if clicked_tile.is_empty:
                print(f"Building tower at {row}, {col}!")

                clicked_tile.is_empty = False
                new_tower = Tower(row, col, TILE_SIZE)
                self.towers.append(new_tower)
                self.scene.addItem(new_tower)
            else:
                print("Cannot build here!")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DinoDefense()
    window.show()
    sys.exit(app.exec())
