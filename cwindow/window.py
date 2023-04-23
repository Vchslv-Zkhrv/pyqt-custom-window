from PyQt6 import QtCore, QtGui, QtWidgets

from .grips import SideGrip
from .shadow import WindowShadow
from .parsers import EventParser


class TitleBar(QtWidgets.QFrame):

    """
    Custom window title bar. Provides window moving
    """

    def __init__(
            self,
            parent: QtWidgets.QMainWindow,
            height: int):

        QtWidgets.QFrame.__init__(self, parent)
        self.setFixedHeight(height)
        self.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Fixed)
            )

        self._is_pressed = False
        self._is_gestured = False
        self._shadow = WindowShadow()
        self.window_normal_size = parent.size()

        self._press_event: EventParser
        self._release_event: EventParser

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self._is_pressed = True
        self._press_event = EventParser(self.window(), a0)
        self.window().setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
        return super().mousePressEvent(a0)

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if self._is_pressed:
            parser = EventParser(self.window(), a0)
            if parser.side and parser.shadow_rect:
                self._shadow.show_(parser.shadow_rect)
            else:
                self._shadow.hide()
        return super().mouseMoveEvent(a0)

    def _use_shadow_geometry(self):
        if not self._is_gestured:
            self.window_normal_size = self.window().size()
        self._shadow.hide()
        self._is_gestured = True
        self.window().setGeometry(self._shadow.geometry())

    def _move_normal(self):
        pos1 = self._release_event.point
        pos0 = self._press_event.point
        posW = self.window().pos()
        dx = pos1.x() - pos0.x()
        dy = pos1.y() - pos0.y()
        self.window().move(dx + posW.x(), dy + posW.y())

    def _fix_x_delta_after_resize(self):
        pos = self.window().pos()
        if self._release_event.point.x() > self._press_event.point.x():
            x = self._press_event.event.pos().x()
            x -= int(self.window().width() * self._press_event.relative_pos[0])
            pos.setX(x)
        else:
            self._release_event.parse_event()
            rdx = abs(self._press_event.relative_pos[0] - self._release_event.relative_pos[0])
            dx = int(self.window().width()*rdx)
            pos.setX(pos.x() + dx)
        self.window().move(pos)

    def _restore_normal_size(self):
        width = self.window().width()
        self.window().resize(self.window_normal_size)
        if width > self.window_normal_size.width():
            self._fix_x_delta_after_resize()

    def _move_via_gesture(self):
        if self._shadow.isVisible():
            self._use_shadow_geometry()
            return
        self._move_normal()
        if self._is_gestured:
            self._restore_normal_size()
            self._is_gestured = False

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self._release_event = EventParser(self.window(), a0)
        self.window().setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        if self._is_pressed:
            self._move_via_gesture()
        self._is_pressed = False
        return super().mouseReleaseEvent(a0)


class Window(QtWidgets.QMainWindow):

    """
    Framless window with re-implemented title bar
    """

    _grip_size = 12
    _titlebar_height = 44

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

        self.setCentralWidget(QtWidgets.QWidget())
        layout = QtWidgets.QVBoxLayout(self.centralWidget())
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.title_bar = TitleBar(self, self._titlebar_height)
        layout.addWidget(self.title_bar)

        self.content = QtWidgets.QFrame(self)
        self.content.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Expanding)
            )
        layout.addWidget(self.content)

        self.side_grips = [
            SideGrip(self, QtCore.Qt.Edge.LeftEdge),
            SideGrip(self, QtCore.Qt.Edge.TopEdge),
            SideGrip(self, QtCore.Qt.Edge.RightEdge),
            SideGrip(self, QtCore.Qt.Edge.BottomEdge),
        ]
        self.corner_grips = [QtWidgets.QSizeGrip(self) for i in range(4)]
        for grip in self.corner_grips:
            grip.setStyleSheet("background-color: rgba(0,0,0,0)")

    def setStyleSheet(self, styleSheet: str) -> None:
        self.centralWidget().setStyleSheet(styleSheet)
        super().setStyleSheet(styleSheet)

    @property
    def grip_size(self):
        return self._grip_size

    def set_grip_size(self, size):
        if size == self._grip_size:
            return
        self._grip_size = max(2, size)
        self.update_grips()

    def update_grips(self):

        self.setContentsMargins(*[self.grip_size] * 4)
        out_rect = self.rect()
        # an "inner" rect used for reference to set the geometries of size grips
        in_rect = out_rect.adjusted(
            self.grip_size,
            self.grip_size,
            -self.grip_size,
            -self.grip_size)

        # top left
        self.corner_grips[0].setGeometry(
            QtCore.QRect(out_rect.topLeft(), in_rect.topLeft()))

        # top right
        self.corner_grips[1].setGeometry(
            QtCore.QRect(out_rect.topRight(), in_rect.topRight()).normalized())

        # bottom right
        self.corner_grips[2].setGeometry(
            QtCore.QRect(in_rect.bottomRight(), out_rect.bottomRight()))

        # bottom left
        self.corner_grips[3].setGeometry(
            QtCore.QRect(out_rect.bottomLeft(), in_rect.bottomLeft()).normalized())

        # left edge
        self.side_grips[0].setGeometry(
            0, in_rect.top(), self.grip_size, in_rect.height())

        # top edge
        self.side_grips[1].setGeometry(
            in_rect.left(), 0, in_rect.width(), self.grip_size)

        # right edge
        self.side_grips[2].setGeometry(
            in_rect.left() + in_rect.width(),
            in_rect.top(),
            self.grip_size,
            in_rect.height())

        # bottom edge
        self.side_grips[3].setGeometry(
            self.grip_size,
            in_rect.top() + in_rect.height(),
            in_rect.width(),
            self.grip_size)

    def _update_cw_geometry(self):
        rect = self.geometry()
        rect.setX(0)
        rect.setY(0)
        self.centralWidget().setGeometry(rect)

    def resizeEvent(self, event):
        QtWidgets.QMainWindow.resizeEvent(self, event)
        self.update_grips()
        self._update_cw_geometry()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        super().paintEvent(a0)
        self._update_cw_geometry()

    def moveEvent(self, a0: QtGui.QMoveEvent) -> None:
        super().moveEvent(a0)
        self._update_cw_geometry()
