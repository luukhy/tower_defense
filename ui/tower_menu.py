from PyQt6 import uic
from PyQt6.QtCore import QEasingCurve, QEvent, QPoint, QPropertyAnimation, pyqtSignal
from PyQt6.QtWidgets import QWidget


class SlidingTowerMenu(QWidget):
    tower_selected = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

        uic.loadUi("res/ui/tower_menu.ui", self)

        self.expanded_width = self.width()
        self.collapsed_width = 50

        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.MenuTowerIcon.installEventFilter(self)

        self.buttonBasic.clicked.connect(lambda: self.tower_selected.emit("basic"))
        self.buttonSniper.clicked.connect(lambda: self.tower_selected.emit("sniper"))

        self.update_position()

    def eventFilter(self, source, event):
        if source == self.MenuTowerIcon and event.type() == QEvent.Type.Enter:
            self.open_menu()

        return super().eventFilter(source, event)

    def open_menu(self):
        target_x = self.parent().width() - self.expanded_width
        self.animation.setEndValue(QPoint(target_x, 0))
        self.animation.start()

    def leaveEvent(self, event):
        target_x = self.parent().width() - self.collapsed_width
        self.animation.setEndValue(QPoint(target_x, 0))
        self.animation.start()
        super().leaveEvent(event)

    def update_position(self):
        self.resize(self.expanded_width, self.parent().height())
        if self.underMouse():
            self.move(self.parent().width() - self.expanded_width, 0)
        else:
            self.move(self.parent().width() - self.collapsed_width, 0)
