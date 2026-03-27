from pathlib import Path

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QGraphicsPixmapItem

from game_map import TILE_SIZE

texture_path = Path("res/textures")

dino_textures = {"triceratops": texture_path / Path("triceratops.png")}


class Dino(QGraphicsPixmapItem):
    def __init__(self, grid_y, grid_x, type: str, tile_size=TILE_SIZE):
        super().__init__()
        tex_path = dino_textures[type]
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
