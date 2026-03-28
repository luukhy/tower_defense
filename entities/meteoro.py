from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QGraphicsPixmapItem

stages_textures = [
    "res/textures/meteoro_stage_0.png",
    "res/textures/meteoro_stage_1.png",
]


class Meteoro(QGraphicsPixmapItem):
    def __init__(self, grid_x: int, grid_y: int, tile_size: int):
        super().__init__()
        # TODO: get rid of the hardcoded sclaing factors
        self.texture = QPixmap(stages_textures[1]).scaled(240, 240)
        self.setPixmap(self.texture)
        self.grid_pos = (grid_y, grid_x)
        self.setPos(grid_x * tile_size, grid_y * tile_size)
        self.setZValue(1)

        self.hp = 1000
        self.stage = 0
