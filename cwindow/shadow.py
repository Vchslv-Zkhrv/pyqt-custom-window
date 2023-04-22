from PyQt6 import QtCore, QtWidgets, QtGui

shadow_color = QtGui.QColor(0, 0, 0, 100)


class WindowShadow(QtWidgets.QMainWindow):

    """
    translucent rectangle showing window target geometry /
    полупрозрачный прямоугольник, отображающий будущее расположение окна
    """

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCentralWidget(QtWidgets.QWidget())
        r, g, b, a = shadow_color.getRgb()
        self.centralWidget().setStyleSheet(
            f"background-color: rgba({r}, {g}, {b}, {a}); border:none;")

    def show_(self, rect: QtCore.QRect):
        self.setGeometry(rect)
        self.show()
