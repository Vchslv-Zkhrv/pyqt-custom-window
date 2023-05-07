from PyQt6 import QtCore, QtGui, QtWidgets

from .grips import SideGrip
from .shadow import WindowShadow
from .parsers import EventParser, ScreenParser
from . import modes


class CWindow(QtWidgets.QMainWindow):

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

    title_bar: QtWidgets.QFrame
    content: QtWidgets.QFrame

    gesture_mode: modes.GestureResizeMode = modes.GestureResizeModes.shrink_as_possible
    gesture_sides: modes.SidesUsingMode = modes.SideUsingModes.whole
    gesture_orientation_mode: modes.ScreenOrientationModes \
        = modes.ScreenOrientationModes.no_difference

    _press_event: EventParser
    _release_event: EventParser

    def __init__(self, parent=None):

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

        self._is_pressed = False
        # _is_gestured indicates that window was resized with moving to screen edge gesture
        self._is_gestured = False
        self._shadow = WindowShadow(self.shadow_color)
        self._normal_size = self.size()
        self._screen = ScreenParser(self.screen())

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
        self.corner_grips = [QtWidgets.QSizeGrip(self) for _ in range(4)]
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

    def _use_shadow_geometry(self):

        """hides shadow and sets it's geometry to itself"""

        if not self._is_gestured:
            # saves window old size to restore it later
            self._normal_size = self.window().size()
        self._shadow.hide()
        self._is_gestured = True
        geo = self._shadow.geometry()
        self.setGeometry(geo)

    def _move_normal(self):

        """common way to move the window"""

        # calculates delta between pressed and released points
        pos1 = self._release_event.point
        pos0 = self._press_event.point
        dx = pos1.x() - pos0.x()
        dy = pos1.y() - pos0.y()
        posW = self.window().pos()
        self.move(dx + posW.x(), dy + posW.y())

    def _fix_x_delta_after_resize(self):

        """
        makes screen edge gesture exiting more intuitive
        """
        # window position after moving and resizing
        pos = self.pos()

        # if window was moved right
        if self._release_event.point.x() > self._press_event.point.x():
            x = self._press_event.event.pos().x()
            # delta x = window width * relative cursor position when it was pressed
            x -= int(self.width() * self._press_event.relative_pos[0])
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
            dx = int(self.width()*rdx)
            pos.setX(pos.x() + dx)

        self.move(pos)

    def _restore_normal_size(self):
        """
        Restores normal window size after gestures
        """
        width = self.width()
        self.resize(self._normal_size)
        if width > self._normal_size.width():
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

    def _titlebar_mouse_pressed(self, a0: QtGui.QMouseEvent) -> None:
        self._is_pressed = True
        self._press_event = EventParser(self, a0)
        self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)

    def _is_fullscreen_gesture(self, event: EventParser) -> bool:
        portrait: bool = self.screen().isPortrait(self.screen().orientation())
        return (
            self.gesture_orientation_mode != modes.ScreenOrientationModes.use_special
            and event.side == QtCore.Qt.Edge.TopEdge
        ) or (
            self.gesture_orientation_mode == modes.ScreenOrientationModes.use_special
            and (
                not portrait and event.side == QtCore.Qt.Edge.TopEdge or
                portrait and event.side in (
                    QtCore.Qt.Edge.LeftEdge,
                    QtCore.Qt.Edge.RightEdge
                )
            )
        )

    def _skip_shadow(self, event: EventParser) -> bool:

        portrait: bool = self.screen().isPortrait(self.screen().orientation())
        fullscreen = self._is_fullscreen_gesture(event)

        return (
            # if function is disallowed
            self.gesture_mode == modes.GestureResizeModes.never
        ) or (
            # if window can use shadow only for acceptable areas
            self.gesture_mode == modes.GestureResizeModes.acceptable and
            (
                # looking for acceptable sides
                event.screen_area.height() < self.minimumHeight() or
                event.screen_area.width() < self.minimumWidth())
        ) or (
            # if corners are blocked
            self.gesture_sides == modes.SideUsingModes.ignore_corners and
            isinstance(event.side, QtCore.Qt.Corner)
        ) or (
            # if "ignore_portrait", only fullscreen gesture is allowed
            self.gesture_orientation_mode == modes.ScreenOrientationModes.ignore_portrait and
            portrait and
            not fullscreen
        ) or (
            # if "use_special" dissalowed
            self.gesture_orientation_mode != modes.ScreenOrientationModes.use_special and
            event.side == QtCore.Qt.Edge.BottomEdge
        ) or (
            # if "use_special" used
            self.gesture_orientation_mode == modes.ScreenOrientationModes.use_special and
            not portrait and
            event.side == QtCore.Qt.Edge.BottomEdge

        ) or (
            # if "fullscreen_only"
            self.gesture_sides == modes.SideUsingModes.fullscreen_only and
            not fullscreen
        )

    def _get_appropriate_area(self, event: EventParser) -> QtCore.QRect:
        """
        implements "shrink_as_possibple" option
        """
        # input
        area = event.screen_area
        ah, aw, ax, ay = area.height(), area.width(), area.x(), area.y()
        mh, mw = self.minimumHeight(), self.minimumWidth()
        dx, dy = 0, 0
        # if event screen area violates minimimum height
        if ah < mh:
            area.setHeight(mh)
            if ay > 1:
                dy = mh - ah
        # if event screen area violates minimimum width
        if aw < mw:
            area.setWidth(mw)
            if ax > 1:
                dx = mw - aw
        # move backwards if area is off screen
        if event.right:
            dx = -dx
        if event.bottom:
            dy = -dy
        # set new position
        area.setX(ax + dx)
        area.setY(ay + dy)
        # output
        return area

    def _show_shadow(self, event: EventParser):
        """
        shows window shadow using user settings
        """
        # skip (or not to skip) the shadow
        if self._skip_shadow(event):
            return
        # resize the shadow
        if self.gesture_mode == modes.GestureResizeModes.shrink_as_possible:
            area = self._get_appropriate_area(event)
        else:
            area = event.screen_area
        # draw the shadow
        self._shadow.show_(area)

    def _titlebar_mouse_moved(self, a0: QtGui.QMouseEvent) -> None:
        if self._is_pressed:
            # if pressed, checks that user moved window to the screen edge
            # and shows the shadow to indicate target window geometry
            parser = EventParser(self, a0)
            if parser.side and parser.screen_area:
                self._show_shadow(parser)
            else:
                self._shadow.hide()

    def _titlebar_mouse_released(self, a0: QtGui.QMouseEvent) -> None:
        # saves event info
        self._release_event = EventParser(self, a0)
        # launches custom window moving implementation
        if self._is_pressed:
            self._move_via_gesture()
        # drop defaults
        self._is_pressed = False
        self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)


class TitleBar(QtWidgets.QFrame):

    """
    Custom window title bar. Provides moving for frameless window
    """

    def __init__(
            self,
            cwindow: CWindow,
            height: int):

        QtWidgets.QFrame.__init__(self, cwindow)
        self.setFixedHeight(height)
        self.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Fixed)
            )
        self.cwindow = cwindow

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.cwindow._titlebar_mouse_pressed(a0)
        return super().mousePressEvent(a0)

    def mouseMoveEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.cwindow._titlebar_mouse_moved(a0)
        return super().mouseMoveEvent(a0)

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.cwindow._titlebar_mouse_released(a0)
        return super().mouseReleaseEvent(a0)
