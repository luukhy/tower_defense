from PyQt6 import uic
from PyQt6.QtCore import QEasingCurve, QEvent, QPoint, QPropertyAnimation
from PyQt6.QtWidgets import QWidget


class SlidingStatsMenu(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi("res/ui/tower_stats.ui", self)

        self.expanded_width = self.width()
        self.collapsed_width = 50

        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        if hasattr(self, "MenuTowerIcon"):
            self.MenuTowerIcon.installEventFilter(self)

        self.current_tower = None

        if hasattr(self, "comboTargeting"):
            self.comboTargeting.currentTextChanged.connect(self.on_targeting_changed)

        self.update_position()

    def update_stats(self, tower):
        """Fills in the labels with the selected tower's stats."""
        self.current_tower = tower

        if tower:
            tower_name = tower.__class__.__name__
            self.labelTitle.setText(f"{tower_name}")
            self.labelDamage.setText(f"Damage: {tower.damage}")
            self.labelRange.setText(f"Range: {tower.range}px")
            self.labelFireRate.setText(f"Fire Rate: {tower.fire_rate}s")

            if hasattr(self, "comboTargeting"):
                self.comboTargeting.blockSignals(True)
                self.comboTargeting.setCurrentText(tower.target_mode)
                self.comboTargeting.blockSignals(False)

            self.open_menu()
        else:
            self.close_menu()

    def on_targeting_changed(self, new_mode: str):
        if self.current_tower:
            self.current_tower.target_mode = new_mode
        else:
            print("ERROR: Tried to change targeting, but no tower is selected!")

    def eventFilter(self, source, event):
        if (
            hasattr(self, "MenuTowerIcon")
            and source == self.MenuTowerIcon
            and event.type() == QEvent.Type.Enter
        ):
            self.open_menu()
        return super().eventFilter(source, event)

    def open_menu(self):
        self.animation.setEndValue(QPoint(0, 0))
        self.animation.start()

    def leaveEvent(self, event):
        if hasattr(self, "comboTargeting") and self.comboTargeting.view().isVisible():
            event.ignore()
            return

        self.close_menu()
        super().leaveEvent(event)

    def close_menu(self):
        target_x = -(self.expanded_width - self.collapsed_width)
        self.animation.setEndValue(QPoint(target_x, 0))
        self.animation.start()

    def update_position(self):
        self.resize(self.expanded_width, self.parent().height())
        if self.underMouse():
            self.move(0, 0)
        else:
            self.move(-(self.expanded_width - self.collapsed_width), 0)
