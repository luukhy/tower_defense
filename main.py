import sys

from PyQt6 import QtCore, QtWidgets, uic
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QGraphicsScene

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

        # towers
        self.towers = []

        # timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)  # ~60 FPS

    def update_game(self):
        pass

    def set_meteoro_tiles_occupied(self, meteoro_pos: tuple):
        for row in range(meteoro_pos[1], meteoro_pos[1] + 3):
            for col in range(meteoro_pos[0], meteoro_pos[0] + 3):
                if 0 >= row > GRID_SIZE[1] and 0 >= col > GRID_SIZE[0]:
                    continue
                tile = self.map.grid[row][col]
                tile.set_walkability(False)
                tile.set_emptiness(False)

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
