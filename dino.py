from pathlib import Path

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QGraphicsPixmapItem

resources_path = Path("res")

dino_textures = {"default": resources_path / Path("tower.png")}


class Dino(QGraphicsPixmapItem):
    def __init__(self, grid_y, grid_x, tile_size, type):
        super().__init__()
        tex_path = dino_textures["default"]
        self.texture = QPixmap(str(tex_path))

        if self.texture.isNull():
            print(f"Warning: Missing dino texture at {str(tex_path)}")

        self.grid_y = grid_y
        self.grid_x = grid_x

        pos_x = grid_x * tile_size
        pos_y = grid_y * tile_size

        offset_y = self.texture.height() - tile_size
        self.setPos(pos_x, pos_y - offset_y)
        self.setPixmap(self.texture)

        self.setZValue(self.grid_y)
