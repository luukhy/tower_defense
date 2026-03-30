import math
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QPen, QPixmap, QTransform
from PyQt6.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem

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

        self.max_hp = 100.0
        self.hp = self.max_hp
        self.reward = 15

        # health bar
        self.bar_width = self.texture.width()
        self.bar_height = 5

        x_pos = 0
        y_pos = -10

        # black bg
        self.border_hp_bar = QGraphicsRectItem(
            x_pos - 2, y_pos - 2, self.bar_width + 4, self.bar_height + 4, self
        )
        self.border_hp_bar.setBrush(QBrush(QColor(0, 0, 0)))
        self.border_hp_bar.setPen(QPen(Qt.PenStyle.NoPen))

        # red bg
        self.bg_hp_bar = QGraphicsRectItem(
            x_pos, y_pos, self.bar_width, self.bar_height, self
        )
        self.bg_hp_bar.setBrush(QBrush(QColor(200, 0, 0)))
        self.bg_hp_bar.setPen(QPen(Qt.PenStyle.NoPen))

        # green fg
        self.fg_hp_bar = QGraphicsRectItem(
            x_pos, y_pos, self.bar_width, self.bar_height, self
        )
        self.fg_hp_bar.setBrush(QBrush(QColor(0, 200, 0)))
        self.fg_hp_bar.setPen(QPen(Qt.PenStyle.NoPen))

        # hide health bar when at full hp
        self.bg_hp_bar.hide()
        self.border_hp_bar.hide()
        self.fg_hp_bar.hide()

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

    def take_damage(self, amount: float):
        self.hp -= amount

        if self.hp < 0:
            self.hp = 0

        # show the bar only after they take damage
        self.bg_hp_bar.show()
        self.fg_hp_bar.show()
        self.border_hp_bar.show()

        health_ratio = self.hp / self.max_hp
        new_width = self.bar_width * health_ratio

        self.fg_hp_bar.setRect(0, -10, new_width, self.bar_height)

    def update_path(self, waypoints):
        self.waypoints = list(waypoints)

    def get_curr_pos(self):
        return (self.exact_x, self.exact_y)

    def get_curr_pos_grid(self):
        return (self.grid_x, self.grid_y)
