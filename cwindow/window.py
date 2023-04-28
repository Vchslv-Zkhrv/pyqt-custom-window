from PyQt6 import QtCore, QtGui, QtWidgets

from .grips import SideGrip
from .shadow import WindowShadow
from .parsers import EventParser, ScreenParser


class TitleBar(QtWidgets.QFrame):

    """
    Custom window title bar. Provides moving for frameless window
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
        # _is_gestured indicates that window was resized with moving to screen edge gesture
        self._is_gestured = False
        self._shadow = WindowShadow(parent.shadow_color)
        self.window_normal_size = parent.size()
        self._screen = ScreenParser(self.screen())

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self._is_pressed = True
        self._press_event = EventParser(self, a0)
        self.window().setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
        return super().mousePressEvent(a0)

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        if self._is_pressed:
            # if pressed, checks that user moved window to the screen edge 
            # and shows the shadow to indicate target window geometry
            parser = EventParser(self, a0)
            if parser.side and parser.shadow_rect:
                self._shadow.show_(parser.shadow_rect)
            else:
                self._shadow.hide()
        return super().mouseMoveEvent(a0)

    def _use_shadow_geometry(self):

        """hides shadow and sets it's geometry to window"""

        if not self._is_gestured:
            # saves window old size to restore it later
            self.window_normal_size = self.window().size()
        self._shadow.hide()
        self._is_gestured = True
        self.window().setGeometry(self._shadow.geometry())

    def _move_normal(self):

        """common way to move the window"""

        # calculates delta between pressed and released points
        pos1 = self._release_event.point
        pos0 = self._press_event.point
        dx = pos1.x() - pos0.x()
        dy = pos1.y() - pos0.y()
        posW = self.window().pos()
        self.window().move(dx + posW.x(), dy + posW.y())

    def _fix_x_delta_after_resize(self):

        """
        makes screen edge gesture exiting more intuitive
        """
        # window position after moving and resizing
        pos = self.window().pos()

        # if window was moved right
        if self._release_event.point.x() > self._press_event.point.x():
            x = self._press_event.event.pos().x()
            # delta x = window width * relative cursor position when it was pressed
            x -= int(self.window().width() * self._press_event.relative_pos[0])
            pos.setX(x)

        # if window was moved left
        else:
            # up to this point, the _release_event characteristics
            # have been computed relative to the old window geometry.
            # Updates them
            self._release_event.parse_event()
            # rdx = relative delta x = difference between
            # cursor relative position to the old window geometry and the new one
            rdx = abs(self._press_event.relative_pos[0] - self._release_event.relative_pos[0])
            # delta x = window width * rdx
            dx = int(self.window().width()*rdx)
            pos.setX(pos.x() + dx)

        self.window().move(pos)

    def _restore_normal_size(self):
        """
        Restores normal window size after gestures
        """
        width = self.window().width()
        self.window().resize(self.window_normal_size)
        if width > self.window_normal_size.width():
            self._fix_x_delta_after_resize()

    def _move_via_gesture(self):
        """
        window moving implementation
        """

        # if user wants to resize window with screen edge gesture
        if self._shadow.isVisible():
            self._use_shadow_geometry()
            return

        # straight moving
        self._move_normal()
        if self._is_gestured:
            self._restore_normal_size()
            self._is_gestured = False

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        # saves event info
        self._release_event = EventParser(self, a0)
        # launches custom window moving implementation
        if self._is_pressed:
            self._move_via_gesture()
        # drop defaults
        self._is_pressed = False
        self.window().setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        return super().mouseReleaseEvent(a0)


class Window(QtWidgets.QMainWindow):

    """
    Framless window with customazible title bar.
    """

    # window layout:

    #  visible part:
    # ┌─────────────────────────┬╌╌╌╌╌
    # │        title_bar        │    | = titlebar_height (default 44px) 
    # ├─────────────────────────┼╌╌╌╌╌
    # │                         │
    # │                         │
    # │         content         │
    # │                         │
    # │                         │
    # │                         │
    # └─────────────────────────┘

    #  corner and side grips:
    # ┌─┬─────────┬─┬─────────┬─┬╌╌╌╌╌
    # ├─┘         └─┘         └─┼╌╌╌╌╌ = grip_sze (defaul 12px)  
    # │                         │
    # │                         │
    # ├─┐                     ┌─┤
    # ├─┘                     └─┤
    # │                         │
    # │                         │
    # ├─┐         ┌─┐         ┌─┤
    # └─┴─────────┴─┴─────────┴─┘

    grip_size = 12
    titlebar_height = 44
    shadow_color = QtGui.QColor(0, 0, 0, 100)

    title_bar: TitleBar
    content: QtWidgets.QFrame

    def __init__(self, parent = None):

        QtWidgets.QMainWindow.__init__(self, parent)
        # FramelessWindowHint makes window lose gesture functionality
        # and disallows system hotkeys
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

        self.setCentralWidget(QtWidgets.QWidget())
        layout = QtWidgets.QVBoxLayout(self.centralWidget())
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.title_bar = TitleBar(self, self.titlebar_height)
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

    def set_grip_size(self, size):
        if size == self.grip_size:
            return
        self.grip_size = max(2, size)
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
