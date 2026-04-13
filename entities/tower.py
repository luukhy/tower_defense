import math
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QPen, QPixmap
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsPixmapItem, QGraphicsRectItem

from entities.projectile import Projectile

resources_path = Path("res/textures")

towers_textures = {
    "basic": resources_path / Path("tower_default.png"),
    "sniper": resources_path / Path("tower_2.png"),
}


class BaseTower(QGraphicsPixmapItem):
    """Base class for all towers. Handles rendering and default logic."""

    def __init__(self, grid_y, grid_x, tile_size, texture_key="basic"):
        super().__init__()
        self.tile_size = tile_size

        tex_path = towers_textures.get(texture_key, towers_textures["basic"])
        self.texture = QPixmap(str(tex_path))

        if self.texture.isNull():
            print(f"Warning: Missing tower texture at {str(tex_path)}")

        self.grid_y = grid_y
        self.grid_x = grid_x

        self.exact_x = grid_x * tile_size
        self.exact_y = grid_y * tile_size

        offset_y = self.texture.height() - tile_size

        self.setPos(self.exact_x, self.exact_y - offset_y)
        self.setPixmap(self.texture)
        self.setZValue(self.grid_y)

        self.hp = 100
        self.max_hp = self.hp
        self.range = 0.0
        self.fire_rate = 1.0
        self.damage = 0
        self.aoe_radius = 0.0
        self.time_since_last_shot = 0.0

        self.center_x = self.exact_x + self.texture.width() / 2
        self.center_y = self.exact_y + tile_size / 2

        self.is_selected = False

        self.target_mode = "Closest"

        self.bar_width = self.texture.width()
        self.bar_height = 5

        # black bg
        self.border_hp_bar = QGraphicsRectItem(
            self.exact_x - 2,
            self.exact_y - 2,
            self.bar_width + 4,
            self.bar_height + 4,
            self,
        )
        self.border_hp_bar.setBrush(QBrush(QColor(0, 0, 0)))
        self.border_hp_bar.setPen(QPen(Qt.PenStyle.NoPen))

        # red bg
        self.bg_hp_bar = QGraphicsRectItem(
            self.exact_x, self.exact_y, self.bar_width, self.bar_height, self
        )
        self.bg_hp_bar.setBrush(QBrush(QColor(200, 0, 0)))
        self.bg_hp_bar.setPen(QPen(Qt.PenStyle.NoPen))

        # green fg
        self.fg_hp_bar = QGraphicsRectItem(
            self.exact_x, self.exact_y, self.bar_width, self.bar_height, self
        )
        self.fg_hp_bar.setBrush(QBrush(QColor(0, 200, 0)))
        self.fg_hp_bar.setPen(QPen(Qt.PenStyle.NoPen))

        # hide health bar when at full hp
        self.bg_hp_bar.hide()
        self.border_hp_bar.hide()
        self.fg_hp_bar.hide()

    def setup_range_circle(self):
        self.local_center_x = self.texture.width() / 2
        self.local_center_y = self.texture.height() - self.tile_size / 2

        diameter = self.range * 2
        top_left_x = self.local_center_x - self.range
        top_left_y = self.local_center_y - self.range

        self.range_circle = QGraphicsEllipseItem(
            top_left_x, top_left_y, diameter, diameter, self
        )

        self.range_circle.setBrush(QColor(150, 150, 150, 100))
        self.range_circle.setPen(QPen(QColor(255, 255, 255, 150)))
        self.range_circle.setZValue(-1)

        self.setAcceptHoverEvents(True)
        self.range_circle.hide()

    def hoverEnterEvent(self, event):
        self.range_circle.show()

    def hoverLeaveEvent(self, event):
        if not self.is_selected:
            self.range_circle.hide()

    def update_logic(self, dt: float, dinos: list):
        self.time_since_last_shot += dt

        if self.time_since_last_shot >= self.fire_rate:
            target = self.find_target(dinos)

            if target:
                self.time_since_last_shot = 0.0
                return self.shoot(target)

        return None

    def find_target(self, dinos: list):
        """Finds a target based on the current target_mode."""
        valid_targets = []

        for dino in dinos:
            dx = dino.exact_x - self.center_x
            dy = dino.exact_y - self.center_y
            dist = math.sqrt(dx**2 + dy**2)

            if dist <= self.range:
                valid_targets.append((dino, dist))

        if not valid_targets:
            return None

        if self.target_mode == "Closest":
            valid_targets.sort(key=lambda x: x[1])

        elif self.target_mode == "Most HP":
            valid_targets.sort(key=lambda x: x[0].hp, reverse=True)

        elif self.target_mode == "Least HP":
            valid_targets.sort(key=lambda x: x[0].hp)

        return valid_targets[0][0]

    def shoot(self, target):
        spawn_x = self.center_x
        spawn_y = self.center_y - (self.texture.height() / 2)

        target_ground_x = target.exact_x + 20
        target_ground_y = target.exact_y + 20

        new_bullet = Projectile(
            start_x=spawn_x,
            start_y=spawn_y,
            target_x=target_ground_x,
            target_y=target_ground_y,
            damage=self.damage,
            aoe_radius=self.aoe_radius,
            speed=self.projectile_speed,
        )
        return new_bullet

    def take_damage(self, damage):
        if self.hp < 0:
            self.hp = 0

        # show the bar only after it take damage
        self.bg_hp_bar.show()
        self.fg_hp_bar.show()
        self.border_hp_bar.show()

        health_ratio = self.hp / self.max_hp
        new_width = self.bar_width * health_ratio

        self.fg_hp_bar.setRect(0, -10, new_width, self.bar_height)


class BasicTower(BaseTower):
    cost = 50

    def __init__(self, grid_y, grid_x, tile_size):
        super().__init__(grid_y, grid_x, tile_size, texture_key="basic")

        self.hp = 100
        self.max_hp = self.hp
        self.range = 240.0
        self.fire_rate = 0.5
        self.damage = 25
        self.aoe_radius = tile_size
        self.projectile_speed = 300

        self.setup_range_circle()


class SniperTower(BaseTower):
    cost = 120

    def __init__(self, grid_y, grid_x, tile_size):
        super().__init__(grid_y, grid_x, tile_size, texture_key="sniper")

        self.hp = 50
        self.max_hp = self.hp
        self.range = 500.0
        self.fire_rate = 2.0
        self.damage = 100
        self.aoe_radius = tile_size
        self.projectile_speed = 1000

        self.setup_range_circle()

    def find_target(self, dinos: list):
        """Ignores distance, targets the Dino with the most hp"""
        best_target = None
        highest_hp = 0

        for dino in dinos:
            dx = dino.exact_x - self.center_x
            dy = dino.exact_y - self.center_y
            dist = math.sqrt(dx**2 + dy**2)

            if dist <= self.range:
                if dino.hp > highest_hp:
                    highest_hp = dino.hp
                    best_target = dino

        return best_target
