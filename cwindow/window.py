from PyQt6 import QtCore, QtGui, QtWidgets

from .grips import SideGrip
from .shadow import WindowShadow


class EventRectParser(QtWidgets.QWidget):

    """
    gets event and makes rect for WindowShadow
    """

    event: QtGui.QMouseEvent

    top: bool = False
    left: bool = False
    bottom: bool = False
    right: bool = False

    point: QtCore.QPoint
    side: QtCore.Qt.Edge | QtCore.Qt.Corner = None
    rect: QtCore.QRect

    def __init__(self, window: QtWidgets.QMainWindow):
        self._window = window
        QtWidgets.QWidget.__init__(self)

    def _drop_to_defaults(self):
        self.top = False
        self.left = False
        self.bottom = False
        self.right = False
        self.point = None
        self.side = None
        self.rect = None

    def parse_event(self, event: QtGui.QMouseEvent):
        self._drop_to_defaults()
        self.event = event
        self._get_event_absolute_pos()
        self._get_event_edges(event)
        self._translate_edges_to_qt()

    def _get_event_absolute_pos(self):
        pos = self.event.pos()
        x, y = pos.x(), pos.y()
        opos = self._window.pos()
        x += opos.x()
        y += opos.y()
        self.point = QtCore.QPoint(x, y)

    def _get_event_edges(self, a0: QtGui.QMouseEvent) -> None:
        pos = self.point
        x, y = pos.x(), pos.y()
        geo = self.screen().geometry()
        top, left, right, bottom = 5, 5, geo.right()-5, geo.bottom()-5
        if x < left:
            self.left = True
        if x > right:
            self.right = True
        if y < top:
            self.top = True
        if y > bottom:
            self.bottom = True

    def _translate_edges_to_qt(self) -> None:
        if self.right and self.top:
            self.side = QtCore.Qt.Corner.TopRightCorner
        elif self.right and self.bottom:
            self.side = QtCore.Qt.Corner.BottomRightCorner
        elif self.left and self.top:
            self.side = QtCore.Qt.Corner.TopLeftCorner
        elif self.left and self.bottom:
            self.side = QtCore.Qt.Corner.BottomLeftCorner
        elif self.right:
            self.side = QtCore.Qt.Edge.RightEdge
        elif self.left:
            self.side = QtCore.Qt.Edge.LeftEdge
        elif self.top:
            self.side = QtCore.Qt.Edge.TopEdge
        elif self.bottom:
            self.side = QtCore.Qt.Edge.BottomEdge

    def get_shadow_rect(self) -> QtCore.QRect | None:

        print(self.side)

        geo = self.screen().geometry()
        x2 = w2 = int(geo.width()/2)
        y2 = h2 = int(geo.height()/2)

        if self.side == QtCore.Qt.Edge.BottomEdge:
            return None

        if self.side == QtCore.Qt.Edge.LeftEdge:
            geo.setWidth(w2)
        if self.side == QtCore.Qt.Edge.RightEdge:
            geo.setX(x2)
            geo.setWidth(w2)
        if self.side == QtCore.Qt.Corner.TopLeftCorner:
            geo.setWidth(w2)
            geo.setHeight(h2)
        if self.side == QtCore.Qt.Corner.TopRightCorner:
            geo.setX(x2)
            geo.setWidth(w2)
            geo.setHeight(h2)
        if self.side == QtCore.Qt.Corner.BottomLeftCorner:
            geo.setY(y2)
            geo.setWidth(w2)
            geo.setHeight(h2)
        if self.side == QtCore.Qt.Corner.BottomRightCorner:
            geo.setX(x2)
            geo.setY(y2)
            geo.setWidth(w2)
            geo.setHeight(h2)

        return geo


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
        self._press_pos = None
        self._shadow = WindowShadow()
        self._parser = EventRectParser(parent)
        self.window_normal_size = parent.size()
        self._is_gestured = False

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self._is_pressed = True
        self._parser.parse_event(a0)
        self._press_pos = self._parser.point
        self.window().setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
        return super().mousePressEvent(a0)

    def _show_shadow(self):
        rect = self._parser.get_shadow_rect()
        if rect:
            self._shadow.show_(rect)

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if self._is_pressed:
            self._parser.parse_event(a0)
            if self._parser.side:
                self._show_shadow()
            else:
                self._shadow.hide()
        return super().mouseMoveEvent(a0)

    def _move_via_gesture(self, a0: QtGui.QMouseEvent):
        if self._shadow.isVisible():
            if not self._is_gestured:
                self.window_normal_size = self.window().size()
            self._shadow.hide()
            self._is_gestured = True
            self.window().setGeometry(self._shadow.geometry())
        else:
            if self._is_gestured:
                self.window().resize(self.window_normal_size)
            self._parser.parse_event(a0)
            pos1 = self._parser.point
            pos0 = self._press_pos
            dx = pos1.x() - pos0.x()
            dy = pos1.y() - pos0.y()
            opos = self.window().pos()
            self.window().move(dx + opos.x(), dy + opos.y())
            self._is_gestured = False

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.window().setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        if self._is_pressed:
            self._move_via_gesture(a0)
        self._is_pressed = False
        self._start_pos = None
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
