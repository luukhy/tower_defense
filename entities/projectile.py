import math

from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import QGraphicsEllipseItem


class Projectile(QGraphicsEllipseItem):
    def __init__(
        self,
        start_x: float,
        start_y: float,
        target_x: float,
        target_y: float,
        damage: int,
        aoe_radius: float,
        speed: float = 300.0,
    ):
        super().__init__(-5, -5, 10, 10)
        self.setBrush(QBrush(QColor(50, 50, 50)))
        self.setZValue(1000)

        self.exact_x = start_x
        self.exact_y = start_y
        self.setPos(self.exact_x, self.exact_y)

        self.dest_x = target_x
        self.dest_y = target_y

        self.damage = damage
        self.speed = speed

        self.aoe_radius = max(aoe_radius, 15.0)

    def update_logic(self, dt: float, dinos: list) -> bool:
        """Moves the bullet to the target coordinates. Returns True when it explodes."""

        dx = self.dest_x - self.exact_x
        dy = self.dest_y - self.exact_y
        distance = math.sqrt(dx**2 + dy**2)

        step = self.speed * dt

        if distance <= step:
            self.explode(dinos)
            return True

        else:
            self.exact_x += (dx / distance) * step
            self.exact_y += (dy / distance) * step
            self.setPos(self.exact_x, self.exact_y)
            return False

    def explode(self, dinos: list):
        """Checks which dinos are caught in the blast radius."""
        for dino in dinos:
            dino_cx = dino.exact_x + 20
            dino_cy = dino.exact_y + 20

            dist = math.sqrt(
                (dino_cx - self.dest_x) ** 2 + (dino_cy - self.dest_y) ** 2
            )

            if dist <= self.aoe_radius:
                dino.take_damage(self.damage)
                print(dino.hp)
