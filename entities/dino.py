import math
from pathlib import Path

from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtWidgets import QGraphicsPixmapItem

from world.game_map import TILE_SIZE

texture_path = Path("res/textures")

dino_textures = {
    "triceratops": texture_path / Path("triceratops.png"),
    "t_rex": texture_path / Path("t_rex.png"),
}


def sign(x):
    return (x > 0) - (x < 0)


class Dino(QGraphicsPixmapItem):
    def __init__(
        self,
        grid_y: int,
        grid_x: int,
        dino_type: str,
        waypoints: list[tuple[float, float]],
        tile_size: int = TILE_SIZE,
    ):
        super().__init__()

        # texture
        tex_path = dino_textures.get(dino_type)
        self.texture = QPixmap(str(tex_path))

        if self.texture.isNull():
            print(f"Warning: Missing dino texture at {str(tex_path)}")
        self.setPixmap(self.texture)

        # grid coords
        self.grid_y = grid_y
        self.grid_x = grid_x

        # the exact logical position of the Dino - float values for smooth movement
        self.exact_x = float(grid_x * tile_size)
        self.exact_y = float(grid_y * tile_size)
        self.direction = 0

        # visual offset handling
        self.offset_y = self.texture.height() - tile_size

        self.setPos(self.exact_x, self.exact_y - self.offset_y)

        self.setZValue(self.exact_y + tile_size)

        self.waypoints = list(waypoints)

        self.speed = 40.0  # px/s
        self.hp = 100

    def move_logic(self, dt: float) -> bool:
        """Called every frame. Returns True if reached the end, False otherwise."""

        prev_dir = self.direction
        if not self.waypoints:
            return True

        target_x, target_y = self.waypoints[0]

        dx = target_x - self.exact_x
        dy = target_y - self.exact_y
        distance = math.sqrt(dx**2 + dy**2)

        step = self.speed * dt

        if distance <= step:
            self.exact_x = target_x
            self.exact_y = target_y
            self.waypoints.pop(0)
        else:
            self.exact_x += (dx / distance) * step
            self.exact_y += (dy / distance) * step

        self.grid_x = int(self.exact_x // TILE_SIZE)

        self.grid_y = int(self.exact_y // TILE_SIZE)

        curr_dir = sign(dx)
        if curr_dir != prev_dir:
            transform = QTransform().scale(1, -1)
            self.texture = self.texture.transformed(transform)
        self.setPos(int(self.exact_x), int(self.exact_y) - self.offset_y)

        self.setZValue(self.exact_y + 40)

        return False

    def update_path(self, waypoints):
        self.waypoints = list(waypoints)

    def get_curr_pos(self):
        return (self.exact_x, self.exact_y)

    def get_curr_pos_grid(self):
        return (self.grid_x, self.grid_y)
