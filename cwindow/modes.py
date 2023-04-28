from abc import ABC
from dataclasses import dataclass

"""
module with modes managing CWindow working
"""


class CMode(ABC):
    """
    Main mode class
    """


class GestureResizeMode(CMode):
    """
    superclass for mode classes managing window reaction to resize gestures
    """


class Always(GestureResizeMode):
    """
    CWindow always applies the shadow geometry, ignoring the min and max size properties
    """


class Acceptable(GestureResizeMode):
    """
    CWindow.window_shadow ignores screen areas that violate the min and max size properties
    """


class Never(GestureResizeMode):
    """
    CWindow don't use resize gestures
    """


@dataclass
class GestureModes():
    always = Always
    acceptable = Acceptable
    never = Never
