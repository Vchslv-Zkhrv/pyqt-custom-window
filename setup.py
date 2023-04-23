import sys

from PyQt6 import QtWidgets

import cwindow


class Application(QtWidgets.QApplication):

    """main application class / главный класс приложения"""

    def __init__(self):
        QtWidgets.QApplication.__init__(self, sys.argv)
        self.window = cwindow.Window()
        self.window.setMinimumSize(480, 360)
        self.window.show()
        sys.exit(self.exec())


if __name__ == "__main__":
    app = Application()
