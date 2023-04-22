from PyQt6 import QtCore, QtWidgets, QtGui


class WindowShadow(QtWidgets.QMainWindow):

    """
    translucent rectangle showing window target geometry /
    полупрозрачный прямоугольник, отображающий будущее расположение окна
    """

    def __init__(self, color: QtGui.QColor):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCentralWidget(QtWidgets.QWidget())
        r, g, b, a = color.getRgb()
        self.centralWidget().setStyleSheet(
            f"background-color: rgba({r}, {g}, {b}, 0.5); border:none;")

    def show_(self, rect: QtCore.QRect):
        self.setGeometry(rect)
        self.show()
