from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QCursor, QPixmap

ZOOM_MAX = 10
ZOOM_MIN = -3
ZOOM_IN_FACTOR = 1.15


class MapView(QtWidgets.QGraphicsView):
    tile_clicked_signal = QtCore.pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTransformationAnchor(
            QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        custom_cursor = QCursor(QPixmap("res/textures/cursor.png"))
        self.viewport().setCursor(custom_cursor)

        self.zoom = 0
        self.zoom_max = ZOOM_MAX
        self.zoom_min = ZOOM_MIN

    def wheelEvent(self, event):
        zoom_in_factor = ZOOM_IN_FACTOR
        zoom_out_factor = 1.0 / zoom_in_factor

        # scrolling up
        if event.angleDelta().y() > 0:
            if self.zoom < self.zoom_max:
                self.scale(zoom_in_factor, zoom_in_factor)
                self.zoom += 1

        # scrolling down
        else:
            if self.zoom > self.zoom_min:
                self.scale(zoom_out_factor, zoom_out_factor)
                self.zoom -= 1

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.pos())

            self.tile_clicked_signal.emit(int(scene_pos.x()), int(scene_pos.y()))

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        custom_cursor = QCursor(QPixmap("res/textures/cursor.png"))
        self.viewport().setCursor(custom_cursor)
