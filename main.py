import sys

from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QGraphicsScene

from core.game_manager import GameManager
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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DinoDefense()
    window.show()
    sys.exit(app.exec())
