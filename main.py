import sys

from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QGraphicsScene

from core.game_manager import GameManager
from ui.stats_menu import SlidingStatsMenu
from ui.tower_menu import SlidingTowerMenu
from world.game_map import MAP_SIZE


class DinoDefense(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("res/ui/main_window.ui", self)

        self.scene = QGraphicsScene(0, 0, MAP_SIZE[0], MAP_SIZE[1])
        self.graphicsView.setScene(self.scene)
        self.graphicsView.setStyleSheet("border: none;")

        self.game_manager = GameManager(self.scene)

        self.graphicsView.tile_clicked_signal.connect(
            self.game_manager.handle_map_click
        )

        self.tower_menu = SlidingTowerMenu(self.centralwidget)
        self.tower_menu.tower_selected.connect(self.game_manager.set_build_mode)

        self.stats_menu = SlidingStatsMenu(self.centralwidget)
        self.game_manager.tower_clicked.connect(self.stats_menu.update_stats)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "tower_menu"):
            self.tower_menu.update_position()
        if hasattr(self, "stats_menu"):
            self.stats_menu.update_position()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DinoDefense()
    window.show()
    sys.exit(app.exec())
