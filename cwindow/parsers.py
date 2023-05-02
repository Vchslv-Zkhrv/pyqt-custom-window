from dataclasses import dataclass

from PyQt6 import QtCore, QtWidgets, QtGui


@dataclass
class ScreenAreas():
    entire: QtCore.QRect
    top: QtCore.QRect
    right: QtCore.QRect
    bottom: QtCore.QRect
    left: QtCore.QRect
    topright: QtCore.QRect
    topleft: QtCore.QRect
    bottomright: QtCore.QRect
    bottomleft: QtCore.QRect


class ScreenParser(QtWidgets.QWidget):

    """
    Parsers QScreen:
    areas - QRect objects marks screen parts;
    """

    _screen: QtGui.QScreen

    areas: ScreenAreas

    def __init__(self, screen: QtGui.QScreen):
        QtWidgets.QWidget.__init__(self)
        self._screen = screen
        self._parse_screen()

    def _parse_screen(self):
        def geo(): return self._screen.geometry()
        x2 = w2 = int(geo().width()/2)
        y2 = h2 = int(geo().height()/2)

        self.areas = ScreenAreas(
            geo(),
            geo(),
            geo(),
            geo(),
            geo(),
            geo(),
            geo(),
            geo(),
            geo())

        self.areas.left.setWidth(w2)

        self.areas.right.setX(x2)
        self.areas.right.setWidth(w2)

        self.areas.bottom.setY(y2)
        self.areas.bottom.setHeight(h2)

        self.areas.top.setHeight(h2)

        self.areas.topright.setX(x2)
        self.areas.topright.setWidth(w2)
        self.areas.topright.setHeight(h2)

        self.areas.topleft.setWidth(w2)
        self.areas.topleft.setHeight(h2)

        self.areas.bottomright.setX(x2)
        self.areas.bottomright.setY(y2)
        self.areas.bottomright.setHeight(h2)
        self.areas.bottomright.setWidth(w2)

        self.areas.bottomleft.setY(y2)
        self.areas.bottomleft.setWidth(w2)
        self.areas.bottomleft.setHeight(h2)


class EventParser(QtWidgets.QWidget):

    """
    Parses QMouseEvent:
    point - absolute event position;
    relative_pos - event position relative to window width and height;
    side - indicates that event happend near the screen edge or corner;
    shadow_rect - geometry for WindowShadow.show_ method;
    """

    event: QtGui.QMouseEvent

    top: bool = False
    left: bool = False
    bottom: bool = False
    right: bool = False

    point: QtCore.QPoint
    relative_pos: tuple[float, float]
    side: QtCore.Qt.Edge | QtCore.Qt.Corner = None
    shadow_rect: QtCore.QRect

    def __init__(self, titlebar: QtWidgets.QFrame, event: QtGui.QMouseEvent):
        QtWidgets.QWidget.__init__(self)
        self._window = titlebar.window()
        self._screen: ScreenParser = titlebar._screen
        self.event = event
        self.parse_event()

    def _drop_to_defaults(self):
        self.top = False
        self.left = False
        self.bottom = False
        self.right = False
        self.point = None
        self.side = None
        self.rect = None

    def parse_event(self):
        self._drop_to_defaults()
        self._get_event_absolute_pos()
        self._get_event_relative_pos()
        self._get_event_edges()
        self._translate_edges_to_qt()
        self._get_shadow_rect()

    def _get_event_absolute_pos(self):
        pos = self.event.pos()
        x, y = pos.x(), pos.y()
        opos = self._window.pos()
        x += opos.x()
        y += opos.y()
        self.point = QtCore.QPoint(x, y)

    def _get_event_edges(self):
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

    def _translate_edges_to_qt(self):
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

    def _get_shadow_rect(self):
        if self.side == QtCore.Qt.Edge.BottomEdge:
            self.shadow_rect = self._screen.areas.bottom
        elif self.side == QtCore.Qt.Edge.LeftEdge:
            self.shadow_rect = self._screen.areas.left
        elif self.side == QtCore.Qt.Edge.RightEdge:
            self.shadow_rect = self._screen.areas.right
        elif self.side == QtCore.Qt.Corner.TopLeftCorner:
            self.shadow_rect = self._screen.areas.topleft
        elif self.side == QtCore.Qt.Corner.TopRightCorner:
            self.shadow_rect = self._screen.areas.topright
        elif self.side == QtCore.Qt.Corner.BottomLeftCorner:
            self.shadow_rect = self._screen.areas.bottomleft
        elif self.side == QtCore.Qt.Corner.BottomRightCorner:
            self.shadow_rect = self._screen.areas.bottomright
        else:
            self.shadow_rect = self._screen.areas.entire

    def _get_event_relative_pos(self):
        dpos = self.event.pos()
        rx = dpos.x() / self._window.width()
        ry = dpos.y() / self._window.height()
        self.relative_pos = (rx, ry)
