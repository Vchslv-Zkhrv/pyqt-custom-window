# pyqt-custom-window

__CWindow__ is a QMainWindow subclass with custom titlebar.

It's still removable, resizable and supports some Windows gestures. You can place any widgets to the titlebar and set him custom style and size.

## Installation

Clone or fork this repository.

## Usage

You can see usage example in setup.py.

### Setup

Exactly the same as with a regular window.

```python
import sys
from PyQt6 import QtWidgets
from cwindow import CWindow

app = QtWidgtets.QApplication(sys.argv)
window = CWindow()

window.setMinimumSize(720, 480)

window.show()
sys.exit(app.exec())
```
