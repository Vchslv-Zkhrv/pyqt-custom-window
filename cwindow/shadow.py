from PyQt6 import QtCore, QtWidgets, QtGui



class WindowShadow(QtWidgets.QMainWindow):

    """
    translucent rectangle showing window target geometry /
    полупрозрачный прямоугольник, отображающий будущее расположение окна
    """

    def __init__(self, color: QtGui.QColor, rect: QtCore.QRect):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(rect)
        self.setCentralWidget(QtWidgets.QWidget())
        r, g, b, a = color.getRgb()
        self.centralWidget().setStyleSheet(
            f"background-color: rgba({r}, {g}, {b}, 0.5); border:none;")

class WindowEdgeShadow(WindowShadow):
    
    """
    WindowShadow creating when user drags window to the screen edge/
    WindowShadow, создающийся когда пользователь перемещает окно в край монитора
    """

    def __init__(self, screen: QtGui.QScreen,  color:QtGui.QColor, edge: QtCore.Qt.Edge):
        geo = screen.geometry()
        if edge == QtCore.Qt.Edge.BottomEdge:
            raise AttributeError("bottom edge doesn't supported")
        if edge == QtCore.Qt.Edge.TopEdge:
            pass
        if edge == QtCore.Qt.Edge.LeftEdge:
            geo.setWidth(int(geo.width()/2))
        if edge == QtCore.Qt.Edge.RightEdge:
            w = int(geo.width()/2)
            geo.setX(w)
            geo.setWidth(w)
        WindowShadow.__init__(self, color, geo)
