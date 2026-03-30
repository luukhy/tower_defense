from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QPixmap
from PyQt6.QtWidgets import QGraphicsView

ZOOM_MAX = 10
ZOOM_MIN = -3
ZOOM_IN_FACTOR = 1.15


class MapView(QGraphicsView):
    tile_clicked_signal = QtCore.pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        custom_cursor = QCursor(QPixmap("res/textures/cursor.png"))
        self.viewport().setCursor(custom_cursor)

        self.zoom = 0
        self.zoom_max = ZOOM_MAX
        self.zoom_min = ZOOM_MIN

        self._is_panning = False
        self._pan_start_pos = None

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
        if event.button() == Qt.MouseButton.RightButton:
            self._is_panning = True
            self._pan_start_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        elif event.button() == QtCore.Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            self.tile_clicked_signal.emit(int(scene_pos.x()), int(scene_pos.y()))

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_panning:
            delta = event.pos() - self._pan_start_pos

            # we move the scorll bars to move the map even if they are off
            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()
            h_bar.setValue(h_bar.value() - delta.x())
            v_bar.setValue(v_bar.value() - delta.y())

            self._pan_start_pos = event.pos()
            event.accept()

        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Stops the panning."""
        if event.button() == Qt.MouseButton.RightButton:
            self._is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)  # Reset the cursor
            event.accept()

        else:
            super().mouseReleaseEvent(event)
