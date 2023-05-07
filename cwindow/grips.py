from PyQt6 import QtWidgets, QtCore, QtGui


class SideGrip(QtWidgets.QWidget):

    """Grips that allows to resize frameless window"""

    def __init__(
            self,
            parent: QtWidgets.QMainWindow,
            edge: QtCore.Qt.Edge):

        QtWidgets.QWidget.__init__(self, parent)

        if edge == QtCore.Qt.Edge.LeftEdge:
            self.setCursor(QtCore.Qt.CursorShape.SizeHorCursor)
            self.resize_func = self.resize_left
        elif edge == QtCore.Qt.Edge.TopEdge:
            self.setCursor(QtCore.Qt.CursorShape.SizeVerCursor)
            self.resize_func = self.resize_top
        elif edge == QtCore.Qt.Edge.RightEdge:
            self.setCursor(QtCore.Qt.CursorShape.SizeHorCursor)
            self.resize_func = self.resize_right
        else:
            self.setCursor(QtCore.Qt.CursorShape.SizeVerCursor)
            self.resize_func = self.resize_bottom

        self.mouse_pos = None

    def resize_left(self, delta: QtCore.QPoint):
        window = self.window()
        width = max(window.minimumWidth(), window.width() - delta.x())
        geo = window.geometry()
        geo.setLeft(geo.right() - width)
        window.setGeometry(geo)

    def resize_top(self, delta: QtCore.QPoint):
        window = self.window()
        height = max(window.minimumHeight(), window.height() - delta.y())
        geo = window.geometry()
        geo.setTop(geo.bottom() - height)
        window.setGeometry(geo)

    def resize_right(self, delta: QtCore.QPoint):
        window = self.window()
        width = max(window.minimumWidth(), window.width() + delta.x())
        window.resize(width, window.height())

    def resize_bottom(self, delta: QtCore.QPoint):
        window = self.window()
        height = max(window.minimumHeight(), window.height() + delta.y())
        window.resize(window.width(), height)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.mouse_pos = event.pos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self.mouse_pos is not None:
            delta = event.pos() - self.mouse_pos
            self.resize_func(delta)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        self.mouse_pos = None
