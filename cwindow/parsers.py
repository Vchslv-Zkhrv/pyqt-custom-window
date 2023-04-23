from PyQt6 import QtCore, QtWidgets, QtGui


class EventParser(QtWidgets.QWidget):

    """
    Parses QMouseEvent:
    point - absolute event position;
    relative_pos - event position relative to window width and height;
    side - indicates that event happend near the screen edge or corner;
    shadow_rect - geometry for WindowShadow.show_ method.
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

    def __init__(self, window: QtWidgets.QMainWindow, event: QtGui.QMouseEvent):
        QtWidgets.QWidget.__init__(self)
        self._window = window
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

        geo = self.screen().geometry()
        x2 = w2 = int(geo.width()/2)
        y2 = h2 = int(geo.height()/2)

        if self.side == QtCore.Qt.Edge.BottomEdge:
            self.shadow_rect = None
            return

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

        self.shadow_rect = geo

    def _get_event_relative_pos(self):
        dpos = self.event.pos()
        rx = dpos.x() / self._window.width()
        ry = dpos.y() / self._window.height()
        self.relative_pos = (rx, ry)
