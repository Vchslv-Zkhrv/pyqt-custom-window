import sys

from PyQt6 import QtWidgets

import cwindow
from cwindow import modes


class Application(QtWidgets.QApplication):

    """main application class / главный класс приложения"""

    def __init__(self):
        QtWidgets.QApplication.__init__(self, sys.argv)
        self.window = cwindow.CWindow()
        self.window.gesture_mode = modes.GestureResizeModes.shrink_as_possible
        self.window.setMinimumSize(1080, 480)
        self.window.show()
        sys.exit(self.exec())


if __name__ == "__main__":
    app = Application()
